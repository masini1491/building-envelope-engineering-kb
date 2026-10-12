"""Strict boundaries for declared alloy choice; no manufacturer-property inference."""
import json
import tempfile
import unittest
from pathlib import Path

from aluminum_research_input import load
from prepare_aluminum_material_input import prepare, read_selection, main


def selection(grade="3004-O"):
    return dict(
        alloy_temper=grade, manufacturer="CS Aluminum",
        property_evidence_status="USER_DECLARED_UNVERIFIED",
        width_mm=120.0, height_mm=80.0, thickness_mm=2.5,
        youngs_modulus_mpa=70000.0, poisson_ratio=0.32,
        pressure_n_mm2=0.0002, mesh=8,
        support="four_edges_clamped", units="N-mm-MPa",
    )


class Tests(unittest.TestCase):
    def test_three_distinct_choices_keep_exact_explicit_inputs(self):
        for grade in ("3003-H14", "3004-H12", "3004-O"):
            with self.subTest(grade=grade):
                raw = selection(grade)
                prepared = prepare(raw)
                self.assertEqual(prepared["youngs_modulus_mpa"], raw["youngs_modulus_mpa"])
                self.assertEqual(prepared["poisson_ratio"], raw["poisson_ratio"])
                self.assertEqual(prepared["pressure_n_mm2"], raw["pressure_n_mm2"])
                self.assertIn(grade, prepared["material_provenance"])
                self.assertIn("UNVERIFIED", prepared["material_provenance"])
                self.assertNotIn("yield", json.dumps(prepared).lower())
                self.assertEqual(len(prepared), 10)

    def test_reject_missing_properties_implicit_grade_or_strength(self):
        for key, value in (("youngs_modulus_mpa", None),
                           ("poisson_ratio", None),
                           ("alloy_temper", "3004-H14"),
                           ("manufacturer", "Other"),
                           ("property_evidence_status", "VERIFIED_PRIMARY"),
                           ("width_mm", 20), ("support", "simple")):
            raw = selection()
            if value is None:
                raw.pop(key)
            else:
                raw[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                prepare(raw)
        raw = selection()
        raw["yield_strength_mpa"] = 145
        with self.assertRaises(ValueError):
            prepare(raw)

    def test_json_rejects_nan_duplicates_and_keeps_private_references_out(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "selection.json"
            result = Path(d) / "generated.json"
            p.write_text(json.dumps(selection()), encoding="utf-8")
            prepared = read_selection(p)
            result.write_text(json.dumps(prepared), encoding="utf-8")
            self.assertEqual(load(result), prepared)
            self.assertNotIn("source_filename", result.read_text())
            p.write_text('{"mesh":4,"mesh":8}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "DUPLICATE"):
                read_selection(p)
            p.write_text('{"poisson_ratio":NaN}', encoding="utf-8")
            with self.assertRaises(ValueError):
                read_selection(p)


if __name__ == "__main__":
    unittest.main()
