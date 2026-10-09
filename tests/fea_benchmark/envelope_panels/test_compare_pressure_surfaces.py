"""Numerical comparison must not be mistaken for equilibrium admission."""
import unittest

from compare_pressure_surfaces import compare


class ComparisonTests(unittest.TestCase):
    def test_mixed_pressure_resultant_is_not_equilibrium(self):
        mid = {"midsurface_total": (0, 0, 5980), "inferred_support": (0, 0, -5961)}
        expanded = {"p1_resultant": (0, 0, 5960)}
        actual = compare(mid, expanded)
        self.assertAlmostEqual(actual["p1_minus_mid_z_relative"], -20 / 5960)
        self.assertAlmostEqual(actual["mixed_z_relative"], -1 / 5960)
        self.assertNotIn("PASS", actual)

    def test_bad_inputs_fail_closed(self):
        mid = {"midsurface_total": (0, 0, 5980), "inferred_support": (0, 0, -5961)}
        for z in (0, -1, float("nan")):
            with self.assertRaisesRegex(ValueError, "NONPOSITIVE_PRESSURE_RESULTANT|INCOMPLETE_OR_NONFINITE_COMPARISON"):
                compare(mid, {"p1_resultant": (0, 0, z)})
        with self.assertRaisesRegex(ValueError, "INCOMPLETE_OR_NONFINITE_COMPARISON"):
            compare({"midsurface_total": (0, 0, 5980), "inferred_support": (0, float("inf"), -5961)},
                    {"p1_resultant": (0, 0, 5960)})


if __name__ == "__main__":
    unittest.main()
