import unittest

from scripts.engineering_calc.glazing_condensation import (
    CondensationInputError,
    screen_center_glass_condensation,
)


class GlazingCondensationTests(unittest.TestCase):
    def test_known_one_dimensional_temperature_and_frsi(self):
        result = screen_center_glass_condensation(
            indoor_temperature_c=20,
            outdoor_temperature_c=0,
            indoor_relative_humidity_pct=50,
            glazing_u_value_w_m2k=2,
            interior_surface_resistance_m2k_w=0.13,
        )
        self.assertAlmostEqual(result.interior_surface_temperature_c, 14.8)
        self.assertAlmostEqual(result.temperature_factor_frsi, 0.74)
        self.assertAlmostEqual(result.indoor_dew_point_c, 9.255, delta=0.02)
        self.assertEqual(result.surface_condensation_status, "NO_CONDENSATION_IN_THIS_1D_MODEL")

    def test_condensation_when_surface_below_dew_point(self):
        result = screen_center_glass_condensation(
            indoor_temperature_c=20,
            outdoor_temperature_c=0,
            indoor_relative_humidity_pct=90,
            glazing_u_value_w_m2k=2,
            interior_surface_resistance_m2k_w=0.13,
        )
        self.assertEqual(result.surface_condensation_status, "POSSIBLE_SURFACE_CONDENSATION")

    def test_equal_indoor_and_outdoor_temperature_undefined_frsi(self):
        result = screen_center_glass_condensation(
            indoor_temperature_c=20,
            outdoor_temperature_c=20,
            indoor_relative_humidity_pct=50,
            glazing_u_value_w_m2k=2,
            interior_surface_resistance_m2k_w=0.13,
        )
        self.assertIsNone(result.temperature_factor_frsi)
        self.assertAlmostEqual(result.interior_surface_temperature_c, 20)

    def test_invalid_inputs_fail_closed(self):
        good = dict(
            indoor_temperature_c=20,
            outdoor_temperature_c=0,
            indoor_relative_humidity_pct=50,
            glazing_u_value_w_m2k=2,
            interior_surface_resistance_m2k_w=0.13,
        )
        for field, invalid in (
            ("indoor_relative_humidity_pct", 0),
            ("indoor_relative_humidity_pct", 101),
            ("glazing_u_value_w_m2k", 0),
            ("interior_surface_resistance_m2k_w", -0.1),
            ("glazing_u_value_w_m2k", float("nan")),
            ("glazing_u_value_w_m2k", True),
            ("glazing_u_value_w_m2k", 100),
        ):
            with self.subTest(field=field, invalid=invalid):
                with self.assertRaises(CondensationInputError):
                    screen_center_glass_condensation(**{**good, field: invalid})

    def test_scope_is_explicit(self):
        result = screen_center_glass_condensation(
            indoor_temperature_c=20,
            outdoor_temperature_c=5,
            indoor_relative_humidity_pct=65,
            glazing_u_value_w_m2k=1.2,
            interior_surface_resistance_m2k_w=0.13,
        )
        self.assertEqual(result.assessment_scope, "CENTER_OF_GLAZING_SURFACE_ONLY")
        self.assertEqual(result.compliance_status, "SCREENING_ONLY_NOT_ISO_COMPLIANCE")
