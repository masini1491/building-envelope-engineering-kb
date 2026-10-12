"""Stage 58 web-only DLOAD identity, theory and fail-closed test coverage."""
import math
import tempfile
import unittest
from pathlib import Path

from check_u_fold_cantilever import L, B, MESHES, SECTIONS
from check_u_fold_web_pressure import (
    PRESSURE_N_MM2, assess, build_pressure, generate, pressure_reference,
)


class UFoldWebPressureTest(unittest.TestCase):
    def test_independent_uniform_beam_reference(self):
        result = pressure_reference()
        self.assertAlmostEqual(result["nominal_total_force_n"], 1.2, places=12)
        self.assertAlmostEqual(result["nominal_root_moment_demand_n_mm"],
                               180.0, places=12)
        self.assertAlmostEqual(result["cantilever_tip_deflection_mm"],
                               0.011739130434782608, places=12)
        self.assertEqual(result["engineering_acceptance"], "NOT_ADMITTED")

    def test_only_web_receives_pressure(self):
        for n in MESHES:
            with self.subTest(mesh=n):
                deck, root, tip = build_pressure(n)
                self.assertEqual(len(root), 49)
                self.assertEqual(len(tip), 49)
                self.assertTrue(root.isdisjoint(tip))
                self.assertNotIn("*CLOAD", deck)
                self.assertIn("*DLOAD\nWEB,P,0.0001\n", deck)
                self.assertEqual(deck.count("*ELEMENT,TYPE=S8R,ELSET=FOLD"), 1)
                self.assertIn("*SHELL SECTION,ELSET=FOLD", deck)
                block = deck.split("*ELSET,ELSET=WEB\n")[1].split("*MATERIAL")[0]
                ids = [int(k) for line in block.splitlines()
                       for k in line.split(",")]
                m = sum(SECTIONS)
                expected = [i*m+j+1 for i in range(n)
                            for j in range(SECTIONS[0],
                                           SECTIONS[0]+SECTIONS[1])]
                self.assertEqual(ids, expected)
                with tempfile.TemporaryDirectory() as d:
                    root_path = Path(d) / "fixture"
                    generate(root_path, n)
                    self.assertEqual((root_path/"panel.inp").read_text(), deck)
                    with self.assertRaisesRegex(ValueError, "WORKSPACE_MUST_BE_NEW"):
                        generate(root_path, n)

    def test_invalid_mesh_and_pressure_observation(self):
        with self.assertRaisesRegex(ValueError, "MESH_NOT_ADMITTED"):
            build_pressure(12)
        reference = pressure_reference()["cantilever_tip_deflection_mm"]
        good = assess({8: 1.04 * reference, 16: 1.02 * reference})
        self.assertEqual(good["material_capacity"], "NOT_ADMITTED")
        self.assertEqual(good["mesh_convergence_order"], "NOT_ESTABLISHED")
        bad = [
            {8: 1.03 * reference, 16: 1.30 * reference},
            {8: 0.70 * reference, 16: reference},
            {8: reference, 16: math.inf},
            {8: reference, 16: 0.0},
            {8: reference},
            {8: True, 16: reference},
        ]
        for item in bad:
            with self.subTest(data=item), self.assertRaises(ValueError):
                assess(item)


if __name__ == "__main__":
    unittest.main()
