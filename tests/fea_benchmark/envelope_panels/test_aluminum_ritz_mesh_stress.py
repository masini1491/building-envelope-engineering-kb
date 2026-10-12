"""Unit checks for additional case/mesh stress trend without simulated CCX."""
import math
import unittest
from check_aluminum_ritz_mesh_stress import contraction_by_mesh, check_case

class Tests(unittest.TestCase):
    def test_contraction(self):
        x=contraction_by_mesh({4:0.010,8:0.015,16:0.017})
        self.assertTrue(x["change_contraction_observed"])
        self.assertEqual(x["engineering_acceptance"],"NOT_ADMITTED")
        self.assertEqual(x["independent_exact_field_solution"],"NOT_ESTABLISHED")
        self.assertAlmostEqual(x["coarse_change_mpa"],0.005)
        self.assertAlmostEqual(x["fine_change_mpa"],0.002)

    def test_reject_nonconvergence(self):
        cases=({4:0.01,8:0.011,16:0.02},
               {4:0.01,8:0.01,16:0.01},
               {4:0.01,8:0.015},
               {4:0.01,8:0.015,16:math.inf},
               {4:0.01,8:0.015,16:0.0},
               {4:0.01,8:0.015,16:True})
        for item in cases:
            with self.subTest(item=item), self.assertRaises(ValueError):
                contraction_by_mesh(item)

    def test_bad_fixture_label(self):
        with self.assertRaisesRegex(ValueError,"UNSUPPORTED_MESH_STRESS_CASE"):
            check_case(None,"uncited_case")

if __name__ == "__main__":
    unittest.main()
