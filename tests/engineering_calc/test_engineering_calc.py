import math
import unittest

from scripts.engineering_calc.beam import simple_span_udl
from scripts.engineering_calc.compare import compare_values
from scripts.engineering_calc.fastener_group import elastic_in_plane_group
from scripts.engineering_calc.section_required import required_inertia, required_section_modulus
from scripts.engineering_calc.units import cm4_to_mm4, kn_m_to_n_mm, kpa_m_to_n_per_mm


class EngineeringCalcTests(unittest.TestCase):
    def test_units(self):
        self.assertEqual(cm4_to_mm4(1), 10_000)
        self.assertEqual(kn_m_to_n_mm(1), 1_000_000)
        self.assertEqual(kpa_m_to_n_per_mm(2.5), 2.5)

    def test_compare(self):
        self.assertEqual(compare_values(10.0, 10.000001, rel_tol=1e-6).status, "MATCH")
        self.assertEqual(compare_values(10.0, 11.0, rel_tol=1e-6).status, "MISMATCH")

    def test_required_properties(self):
        self.assertEqual(required_inertia(100.0, 12.0, 8.0), 150.0)
        self.assertEqual(required_section_modulus(1200.0, 60.0), 20.0)
        with self.assertRaises(ValueError):
            required_section_modulus(1200.0, 0.0)

    def test_simple_span_udl_known_formulas(self):
        result = simple_span_udl(span=1000.0, line_load=2.0, elastic_modulus=70_000.0, inertia=1_000_000.0)
        self.assertAlmostEqual(result.reaction_each, 1000.0)
        self.assertAlmostEqual(result.moment_max, 250_000.0)
        expected_delta = 5 * 2.0 * 1000.0**4 / (384 * 70_000.0 * 1_000_000.0)
        self.assertAlmostEqual(result.deflection_max, expected_delta)

    def test_fastener_group_direct_force(self):
        result = elastic_in_plane_group([(-1, 0), (1, 0)], fx=100.0)
        self.assertEqual(len(result.demands), 2)
        self.assertAlmostEqual(result.demands[0].fx, 50.0)
        self.assertAlmostEqual(result.demands[1].fx, 50.0)

    def test_fastener_group_pure_moment(self):
        result = elastic_in_plane_group([(-1, -1), (1, -1), (1, 1), (-1, 1)], mz=8.0)
        for demand in result.demands:
            self.assertAlmostEqual(demand.resultant, math.sqrt(2.0))


if __name__ == "__main__":
    unittest.main()
