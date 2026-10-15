"""Independent geometry-only guards; no stiffness or CCX admission."""
from __future__ import annotations

import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from u_rib_stud_geometry import geometry, load


def fixture(**patch):
    model = dict(
        units="mm", panel_thickness_mm=3.0,
        rib_base_width_mm=50.0, rib_height_mm=50.0,
        rib_thickness_mm=3.0, rib_length_mm=1200.0,
        stud_pitch_mm=300.0, first_stud_edge_offset_mm=150.0,
        last_stud_min_edge_offset_mm=150.0,
        stud_layout="single_center_row",
    )
    return {**model, **patch}


def polygon_integrals(vertices):
    # Independent Green-theorem area, centroid and about-centroid I across z.
    twice_area = mx = mz = origin_i = 0.
    for (x, z), (xx, zz) in zip(vertices, vertices[1:] + vertices[:1]):
        cross = x*zz - xx*z
        twice_area += cross
        mx += (x+xx)*cross
        mz += (z+zz)*cross
        origin_i += (z*z+z*zz+zz*zz)*cross
    area = twice_area/2
    return area, mx/(6*area), mz/(6*area), origin_i/12 - (mz/(6*area))**2*area


class GeometryTests(unittest.TestCase):
    def test_typical_dimensions_and_center_stud_positions(self):
        result = geometry(fixture())
        s = result["section"]
        self.assertEqual(s["geometric_area_mm2"], 432.)
        self.assertEqual(s["nominal_extruded_section_volume_mm3"], 518400.)
        self.assertEqual(result["stud_centers"]["positions_along_length_mm"], [150., 450., 750., 1050.])
        self.assertEqual(result["stud_centers"]["actual_last_stud_edge_distance_mm"], 150.)
        self.assertEqual(result["stud_centers"]["number_of_rows"], 1)
        self.assertEqual(result["engineering_acceptance"], "NOT_ADMITTED")
        self.assertEqual(result["finite_element_deck"], "NOT_GENERATED")
        self.assertEqual(result["connection_transfer"], "NOT_ESTABLISHED")

    def test_independent_polygon_area_centroid_and_inertia(self):
        for values in [fixture(), fixture(rib_base_width_mm=65, rib_height_mm=80, rib_thickness_mm=4),
                       fixture(rib_base_width_mm=40, rib_height_mm=25, rib_thickness_mm=2)]:
            s = geometry(values)["section"]
            a, x, z, inertia = polygon_integrals(s["cross_section_outline_transverse_normal_mm"])
            self.assertAlmostEqual(a, s["geometric_area_mm2"], places=8)
            self.assertAlmostEqual(x, s["centroid_transverse_from_midline_mm"], places=8)
            self.assertAlmostEqual(z, s["centroid_normal_from_panel_interface_mm"], places=8)
            self.assertAlmostEqual(inertia, s["geometric_I_about_transverse_centroid_mm4"], places=6)

    def test_stud_window_not_a_forced_symmetric_margin(self):
        result = geometry(fixture(rib_length_mm=1000))
        self.assertEqual(result["stud_centers"]["positions_along_length_mm"], [150., 450., 750.])
        self.assertEqual(result["stud_centers"]["actual_last_stud_edge_distance_mm"], 250.)

    def test_variable_profile_and_panel_thickness_are_independent(self):
        a = geometry(fixture())
        b = geometry(fixture(rib_height_mm=70, rib_base_width_mm=65, rib_thickness_mm=4))
        c = geometry(fixture(panel_thickness_mm=5))
        self.assertNotEqual(a["section"]["geometric_area_mm2"], b["section"]["geometric_area_mm2"])
        self.assertEqual(a["section"], c["section"])
        self.assertNotEqual(a["inputs"]["panel_thickness_mm"], c["inputs"]["panel_thickness_mm"])

    def test_rejects_unadmitted_layout_and_extra_keys(self):
        for variant in [fixture(stud_layout="two_rows"), fixture(units="inch"),
                        {**fixture(), "stud_diameter_mm": 6},
                        {k:v for k,v in fixture().items() if k!="rib_height_mm"}]:
            with self.subTest(case=variant), self.assertRaises(ValueError):
                geometry(variant)

    def test_rejects_bad_numeric_types_and_degenerate_section(self):
        for patch in [dict(rib_base_width_mm=6), dict(rib_height_mm=3),
                      dict(rib_thickness_mm=True), dict(rib_length_mm=float("nan")),
                      dict(stud_pitch_mm="300"), dict(panel_thickness_mm=float("inf"))]:
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                geometry(fixture(**patch))

    def test_rejects_impossible_stud_window(self):
        with self.assertRaisesRegex(ValueError, "NO_VALID_STUD_WINDOW"):
            geometry(fixture(rib_length_mm=300, first_stud_edge_offset_mm=200,
                             last_stud_min_edge_offset_mm=200))

    def test_explicit_synthetic_example_file(self):
        example = Path(__file__).parent / "fixtures" / "u_rib_stud_50x50_t3_synthetic.json"
        result = load(example)
        self.assertEqual(result["stud_centers"]["positions_along_length_mm"], [150., 450., 750., 1050.])
        self.assertEqual(result["engineering_acceptance"], "NOT_ADMITTED")

    def test_bounded_json_loader_and_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as d:
            file = Path(d)/"input.json"
            file.write_text(json.dumps(fixture()),encoding="utf-8")
            self.assertEqual(load(file)["stud_centers"]["count"], 4)
            file.write_text('{"units":"mm","units":"mm"}',encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "DUPLICATE_INPUT_KEY"):load(file)
            file.write_text(json.dumps(fixture()).replace("300.0", "NaN"),encoding="utf-8")
            with self.assertRaises(ValueError):load(file)

    def test_cli_uses_explicit_file_and_emits_only_geometry(self):
        with tempfile.TemporaryDirectory() as d:
            file=Path(d)/"input.json"
            file.write_text(json.dumps(fixture()),encoding="utf-8")
            run=subprocess.run([sys.executable, str(Path(__file__).with_name("u_rib_stud_geometry.py")),
                                "--input",str(file)],capture_output=True,text=True,check=True)
            x=json.loads(run.stdout)
            self.assertEqual(x["stud_centers"]["count"],4)
            self.assertEqual(x["engineering_acceptance"],"NOT_ADMITTED")
            self.assertNotIn("stress", x)


if __name__ == "__main__":
    unittest.main()
