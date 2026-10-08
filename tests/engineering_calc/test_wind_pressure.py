import unittest
import math

from scripts.engineering_calc.review import run_review
from scripts.engineering_calc.wind_pressure import (
    WindPressureInputError,
    WindPressureUnsupportedError,
    calculate_roof_design_pressure,
    calculate_wall_design_pressure,
    figure_3_1_roof_gcp,
    figure_3_1_wall_gcp,
    figure_3_2_wall_gcp,
    figure_3_2_roof_suction_with_parapet,
    low_rise_corner_width,
    resolve_basic_wind_speed,
    resolve_importance_factor,
    resolve_terrain,
    velocity_pressure,
)


class TaiwanWindPressureTests(unittest.TestCase):
    def test_basic_wind_speed_resolver_matches_103_code_zones(self):
        cases = [
            (("臺北市", None), 42.5),
            (("新北市", "板橋區"), 37.5),
            (("新北市", "淡水區"), 42.5),
            (("臺中市", "梧棲區"), 32.5),
            (("南投縣", "鹿谷鄉"), 22.5),
            (("屏東縣", "恆春鎮"), 47.5),
            (("花蓮縣", "吉安鄉"), 47.5),
            (("澎湖縣", None), 33.0),
            (("連江縣", None), 42.0),
        ]
        for args, expected in cases:
            with self.subTest(args=args):
                self.assertEqual(resolve_basic_wind_speed(*args), expected)

    def test_admin_name_aliases_are_normalized(self):
        self.assertEqual(resolve_basic_wind_speed("台北市"), 42.5)
        self.assertEqual(resolve_basic_wind_speed("桃園縣"), 37.5)
        self.assertEqual(resolve_basic_wind_speed("台中市", "梧棲區"), 32.5)

    def test_unknown_district_fails_closed(self):
        with self.assertRaises(WindPressureInputError):
            resolve_basic_wind_speed("新北市", "不存在區")

    def test_importance_factor_and_terrain(self):
        self.assertEqual(resolve_importance_factor(3), 1.1)
        self.assertEqual(resolve_importance_factor(4), 0.9)
        self.assertEqual(resolve_importance_factor(5), 1.0)
        self.assertEqual(resolve_terrain("B"), (0.25, 400.0))

    def test_velocity_pressure_known_case(self):
        result = velocity_pressure(
            50.0,
            terrain_category="B",
            kzt=1.0,
            importance_factor=1.1,
            v10_mps=42.5,
        )
        self.assertAlmostEqual(result["k"], 0.9807571055057415)
        self.assertAlmostEqual(result["q_kgf_m2"], 128.61035708411356)
        self.assertAlmostEqual(result["q_kpa"], 1.2612367582989223)

    def test_velocity_pressure_uses_five_metre_floor(self):
        at_two = velocity_pressure(
            2.0,
            terrain_category="C",
            kzt=1.0,
            importance_factor=1.0,
            v10_mps=32.5,
        )
        at_five = velocity_pressure(
            5.0,
            terrain_category="C",
            kzt=1.0,
            importance_factor=1.0,
            v10_mps=32.5,
        )
        self.assertEqual(at_two["height_for_k_m"], 5.0)
        self.assertAlmostEqual(at_two["k"], at_five["k"])
        self.assertAlmostEqual(at_two["q_kpa"], at_five["q_kpa"])

    def test_high_rise_roof_parapet_suction_coefficients(self):
        low = figure_3_2_roof_suction_with_parapet(1.0)
        high = figure_3_2_roof_suction_with_parapet(50.0)
        middle = figure_3_2_roof_suction_with_parapet(math.sqrt(50.0))
        self.assertAlmostEqual(low["zone1_negative"], -2.92)
        self.assertAlmostEqual(low["zone2_negative"], -4.79)
        self.assertAlmostEqual(high["zone1_negative"], -1.87)
        self.assertAlmostEqual(high["zone2_negative"], -3.33)
        self.assertAlmostEqual(middle["zone1_negative"], (-2.92 - 1.87) / 2)
        self.assertEqual(low["zone3_negative"], low["zone2_negative"])
        self.assertIsNone(low["positive_all_zones"])

    def test_zone3_direct_official_figure_endpoints_and_semilog_midpoint(self):
        for area, expected in ((0.5, -6.67), (1.0, -6.67),
                               (math.sqrt(50.0), (-6.67 - 4.79) / 2),
                               (50.0, -4.79), (100.0, -4.79)):
            with self.subTest(area=area):
                args = dict(
                    region="臺北市", district=None, building_category=3,
                    terrain_category="B", kzt=1.0, enclosure="enclosed",
                    h_m=50.0, roof_slope_deg=5.0, effective_area_m2=area,
                    least_horizontal_dimension_m=20.0, governing_wind_source="code",
                )
                result = calculate_roof_design_pressure(**args)
                self.assertAlmostEqual(
                    result["coefficients"]["gcp"]["zone3_negative"], expected, places=8
                )
                self.assertFalse(result["applicability"]["parapet_zone3_as_zone2_applied"])
                self.assertAlmostEqual(
                    result["pressures"]["zone3"]["negative_kpa"],
                    result["velocity_pressure"]["qh"]["q_kpa"] * (expected - 0.375),
                )
                self.assertNotIn("positive_kpa", result["pressures"]["zone3"])

    def test_high_rise_roof_requires_qualified_parapet(self):
        args = dict(
            region="臺北市", district=None, building_category=3,
            terrain_category="B", kzt=1.0, enclosure="enclosed",
            h_m=50.0, roof_slope_deg=5.0, effective_area_m2=1.0,
            least_horizontal_dimension_m=20.0, governing_wind_source="code",
        )
        direct = calculate_roof_design_pressure(**args)
        self.assertEqual(direct["applicability"]["status"], "SUPPORTED_SUCTION_ONLY")
        self.assertAlmostEqual(direct["coefficients"]["gcp"]["zone3_negative"], -6.67)
        self.assertNotIn("positive_kpa", direct["pressures"]["zone3"])
        with self.assertRaises(WindPressureInputError):
            calculate_roof_design_pressure(
                **args, apply_parapet_zone3_as_zone2=True,
                parapet_all_sides=True, parapet_height_m=0.9
            )
        result = calculate_roof_design_pressure(
            **args, apply_parapet_zone3_as_zone2=True,
            parapet_all_sides=True, parapet_height_m=1.2
        )
        self.assertEqual(
            result["applicability"]["status"], "SUPPORTED_SUCTION_ONLY"
        )
        qh = result["velocity_pressure"]["qh"]["q_kpa"]
        self.assertAlmostEqual(
            result["pressures"]["zone1"]["negative_kpa"], qh * (-2.92 - 0.375)
        )
        self.assertEqual(
            result["pressures"]["zone3"]["negative_kpa"],
            result["pressures"]["zone2"]["negative_kpa"]
        )
        self.assertNotIn("positive_kpa", result["pressures"]["zone1"])
        self.assertAlmostEqual(result["corner_zone"]["a_m"], 2.0)

    def test_high_rise_roof_steep_slope_routes_figure_3_1(self):
        result = calculate_roof_design_pressure(
            region="臺北市", district=None, building_category=3,
            terrain_category="B", kzt=1.0, enclosure="enclosed",
            h_m=50.0, roof_slope_deg=20.0, effective_area_m2=1.0,
            least_horizontal_dimension_m=20.0, governing_wind_source="code",
        )
        self.assertEqual(result["applicability"]["route"],
                         "FIGURE_3_1_C_D_BY_FIGURE_3_2_NOTE_5")
        self.assertEqual(result["reference"]["figure"], "3.1(c)")
        self.assertIn("positive_kpa", result["pressures"]["zone3"])

    def test_high_rise_roof_adapter_does_not_invent_positive_suction_values(self):
        payload = dict(
            check_type="wind_pressure",
            units={"pressure":"kPa", "length":"m", "area":"m2"},
            inputs={
                "surface":"roof", "region":"臺北市", "building_category":3,
                "terrain_category":"B", "kzt":1.0,
                "enclosure":"enclosed", "h_m":50.0, "roof_slope_deg":5.0,
                "effective_area_m2":1.0,
                "least_horizontal_dimension_m":20.0,
                "governing_wind_source":"code",
                "apply_parapet_zone3_as_zone2":True,
                "parapet_all_sides":True,
                "parapet_height_m":1.2,
            },
            reported_results={"zone1.positive_kpa":1.0},
        )
        response = run_review(payload)
        self.assertEqual(response["calculation_status"], "COMPUTED")
        self.assertEqual(response["comparison_status"], "INCOMPLETE")
        self.assertIn("UNSUPPORTED_REPORTED_KEY:zone1.positive_kpa",
                      response["review_flags"])

    def test_figure_3_2_regression_unchanged(self):
        low = figure_3_2_wall_gcp(1.0)
        self.assertEqual(low["selection_method"], "LOW_AREA_PLATEAU")
        self.assertAlmostEqual(low["positive_zone4_zone5"], 1.8747)
        self.assertAlmostEqual(low["zone4_negative"], -1.8747)
        self.assertAlmostEqual(low["zone5_negative"], -3.7494)

        middle = figure_3_2_wall_gcp(10.0)
        self.assertEqual(middle["selection_method"], "SEMILOG_INTERPOLATION")
        self.assertAlmostEqual(middle["positive_zone4_zone5"], 1.56225)
        self.assertAlmostEqual(middle["zone4_negative"], -1.6664)
        self.assertAlmostEqual(middle["zone5_negative"], -2.9162)

        high = figure_3_2_wall_gcp(50.0)
        self.assertEqual(high["selection_method"], "HIGH_AREA_PLATEAU")
        self.assertAlmostEqual(high["positive_zone4_zone5"], 1.2498)
        self.assertAlmostEqual(high["zone4_negative"], -1.4581)
        self.assertAlmostEqual(high["zone5_negative"], -2.083)

    def test_figure_3_1_wall_endpoints_and_optional_reduction(self):
        low = figure_3_1_wall_gcp(1.0)
        self.assertEqual(low["figure"], "3.1(a)")
        self.assertAlmostEqual(low["positive_zone4_zone5"], 2.083)
        self.assertAlmostEqual(low["zone4_negative"], -2.2913)
        self.assertAlmostEqual(low["zone5_negative"], -2.9162)
        self.assertFalse(low["low_slope_reduction_applied"])

        high = figure_3_1_wall_gcp(50.0)
        self.assertAlmostEqual(high["positive_zone4_zone5"], 1.4581)
        self.assertAlmostEqual(high["zone4_negative"], -1.6664)
        self.assertAlmostEqual(high["zone5_negative"], -1.6664)

        reduced = figure_3_1_wall_gcp(
            1.0,
            apply_low_slope_reduction=True,
            roof_slope_deg=10.0,
        )
        self.assertAlmostEqual(reduced["positive_zone4_zone5"], 2.083 * 0.9)
        self.assertAlmostEqual(reduced["zone5_negative"], -2.9162 * 0.9)
        with self.assertRaises(WindPressureInputError):
            figure_3_1_wall_gcp(
                1.0,
                apply_low_slope_reduction=True,
                roof_slope_deg=10.1,
            )

    def test_figure_3_1_roof_slope_boundaries(self):
        low = figure_3_1_roof_gcp(1.0, 7.0)
        self.assertEqual(low["figure"], "3.1(b)")
        self.assertAlmostEqual(low["positive_all_zones"], 0.6249)
        self.assertAlmostEqual(low["zone1_negative"], -2.083)
        self.assertAlmostEqual(low["zone2_negative"], -3.7494)
        self.assertAlmostEqual(low["zone3_negative"], -5.8324)

        middle = figure_3_1_roof_gcp(1.0, 7.0001)
        self.assertEqual(middle["figure"], "3.1(c)")
        self.assertAlmostEqual(middle["positive_all_zones"], 1.0415)
        self.assertAlmostEqual(middle["zone1_negative"], -1.8747)
        self.assertAlmostEqual(middle["zone2_negative"], -3.5411)
        self.assertAlmostEqual(middle["zone3_negative"], -5.4158)

        middle_max = figure_3_1_roof_gcp(10.0, 27.0)
        self.assertEqual(middle_max["figure"], "3.1(c)")
        self.assertAlmostEqual(middle_max["positive_all_zones"], 0.6249)
        self.assertAlmostEqual(middle_max["zone1_negative"], -1.6664)
        self.assertAlmostEqual(middle_max["zone2_negative"], -2.4996)
        self.assertAlmostEqual(middle_max["zone3_negative"], -4.166)

        steep = figure_3_1_roof_gcp(1.0, 27.0001)
        self.assertEqual(steep["figure"], "3.1(d)")
        self.assertAlmostEqual(steep["positive_all_zones"], 1.8747)
        self.assertAlmostEqual(steep["zone1_negative"], -2.083)
        self.assertAlmostEqual(steep["zone2_negative"], -2.4996)
        self.assertAlmostEqual(steep["zone3_negative"], -2.4996)

        steep_high = figure_3_1_roof_gcp(10.0, 45.0)
        self.assertAlmostEqual(steep_high["positive_all_zones"], 1.6664)
        self.assertAlmostEqual(steep_high["zone1_negative"], -1.6664)
        self.assertAlmostEqual(steep_high["zone2_negative"], -2.083)
        self.assertAlmostEqual(steep_high["zone3_negative"], -2.083)

        with self.assertRaises(WindPressureUnsupportedError):
            figure_3_1_roof_gcp(1.0, 45.1)

    def test_figure_3_1_roof_semilog_midpoint(self):
        result = figure_3_1_roof_gcp(10 ** 0.5, 5.0)
        self.assertEqual(result["selection_method"], "SEMILOG_INTERPOLATION")
        self.assertAlmostEqual(result["positive_all_zones"], (0.6249 + 0.4166) / 2)
        self.assertAlmostEqual(result["zone2_negative"], (-3.7494 - 2.2913) / 2)

    def test_figure_3_1_c_positive_semilog_matches_official_curve_direction(self):
        result = figure_3_1_roof_gcp(10 ** 0.5, 20.0)
        self.assertEqual(result["figure"], "3.1(c)")
        self.assertAlmostEqual(result["positive_all_zones"], (1.0415 + 0.6249) / 2)
        self.assertGreater(
            figure_3_1_roof_gcp(1.0, 20.0)["positive_all_zones"],
            figure_3_1_roof_gcp(10.0, 20.0)["positive_all_zones"],
        )

    def test_low_slope_parapet_zone3_relief_is_explicit_and_bounded(self):
        baseline = calculate_roof_design_pressure(
            region="臺北市",
            district=None,
            building_category=3,
            terrain_category="B",
            kzt=1.0,
            enclosure="enclosed",
            h_m=15.0,
            roof_slope_deg=5.0,
            effective_area_m2=1.0,
            least_horizontal_dimension_m=20.0,
            governing_wind_source="code",
        )
        relieved = calculate_roof_design_pressure(
            region="臺北市",
            district=None,
            building_category=3,
            terrain_category="B",
            kzt=1.0,
            enclosure="enclosed",
            h_m=15.0,
            roof_slope_deg=5.0,
            effective_area_m2=1.0,
            least_horizontal_dimension_m=20.0,
            governing_wind_source="code",
            apply_parapet_zone3_as_zone2=True,
            parapet_all_sides=True,
            parapet_height_m=0.9,
        )
        self.assertNotAlmostEqual(
            baseline["pressures"]["zone3"]["negative_kpa"],
            baseline["pressures"]["zone2"]["negative_kpa"],
        )
        self.assertAlmostEqual(
            relieved["pressures"]["zone3"]["negative_kpa"],
            relieved["pressures"]["zone2"]["negative_kpa"],
        )
        self.assertTrue(
            relieved["applicability"]["parapet_zone3_as_zone2_applied"]
        )

        with self.assertRaises(WindPressureInputError):
            calculate_roof_design_pressure(
                region="臺北市",
                district=None,
                building_category=3,
                terrain_category="B",
                kzt=1.0,
                enclosure="enclosed",
                h_m=15.0,
                roof_slope_deg=8.0,
                effective_area_m2=1.0,
                least_horizontal_dimension_m=20.0,
                governing_wind_source="code",
                apply_parapet_zone3_as_zone2=True,
                parapet_all_sides=True,
                parapet_height_m=0.9,
            )
        with self.assertRaises(WindPressureInputError):
            calculate_roof_design_pressure(
                region="臺北市",
                district=None,
                building_category=3,
                terrain_category="B",
                kzt=1.0,
                enclosure="enclosed",
                h_m=15.0,
                roof_slope_deg=5.0,
                effective_area_m2=1.0,
                least_horizontal_dimension_m=20.0,
                governing_wind_source="code",
                apply_parapet_zone3_as_zone2=True,
                parapet_all_sides=True,
                parapet_height_m=0.89,
            )

    def test_low_rise_corner_width_rule(self):
        self.assertAlmostEqual(low_rise_corner_width(15.0, 20.0), 2.0)
        self.assertAlmostEqual(low_rise_corner_width(2.0, 10.0), 0.9)
        self.assertAlmostEqual(low_rise_corner_width(30.0, 30.0), 3.0)

    def test_high_rise_wall_regression_is_reproducible(self):
        result = calculate_wall_design_pressure(
            region="臺北市",
            district=None,
            building_category=3,
            terrain_category="B",
            kzt=1.0,
            enclosure="enclosed",
            h_m=50.0,
            z_m=50.0,
            effective_area_m2=1.1,
            least_horizontal_dimension_m=20.0,
            governing_wind_source="code",
        )
        self.assertEqual(result["applicability"]["route"], "FIGURE_3_2_HIGH_RISE_WALL")
        self.assertAlmostEqual(
            result["velocity_pressure"]["qz"]["q_kpa"],
            1.2612367582989223,
        )
        self.assertAlmostEqual(
            result["pressures"]["zone4"]["positive_kpa"],
            2.8374043351450857,
        )
        self.assertAlmostEqual(
            result["pressures"]["zone4"]["negative_kpa"],
            -2.8374043351450857,
        )
        self.assertAlmostEqual(
            result["pressures"]["zone5"]["negative_kpa"],
            -5.201844885928076,
        )

    def test_low_rise_wall_uses_qh_and_does_not_require_z(self):
        result = calculate_wall_design_pressure(
            region="臺北市",
            district=None,
            building_category=3,
            terrain_category="B",
            kzt=1.0,
            enclosure="enclosed",
            h_m=15.0,
            z_m=None,
            effective_area_m2=1.0,
            least_horizontal_dimension_m=20.0,
            governing_wind_source="code",
        )
        self.assertEqual(result["reference"]["figure"], "3.1(a)")
        self.assertEqual(result["applicability"]["route"], "FIGURE_3_1_A_LOW_RISE_WALL")
        self.assertIsNone(result["velocity_pressure"]["qz"])
        self.assertAlmostEqual(result["velocity_pressure"]["qh"]["q_kpa"], 0.6908078228750106)
        self.assertAlmostEqual(result["pressures"]["zone4"]["positive_kpa"], 1.6980056286267762)
        self.assertAlmostEqual(result["pressures"]["zone4"]["negative_kpa"], -1.8419008981316412)
        self.assertAlmostEqual(result["pressures"]["zone5"]["negative_kpa"], -2.2735867066462347)
        self.assertEqual(result["corner_zone"]["a_m"], 2.0)

    def test_low_rise_roof_pressure_routes_all_three_zones(self):
        result = calculate_roof_design_pressure(
            region="臺北市",
            district=None,
            building_category=3,
            terrain_category="B",
            kzt=1.0,
            enclosure="enclosed",
            h_m=15.0,
            roof_slope_deg=5.0,
            effective_area_m2=1.0,
            least_horizontal_dimension_m=20.0,
            governing_wind_source="code",
        )
        self.assertEqual(result["reference"]["figure"], "3.1(b)")
        self.assertAlmostEqual(result["pressures"]["zone1"]["positive_kpa"], 0.6907387420927231)
        self.assertAlmostEqual(result["pressures"]["zone1"]["negative_kpa"], -1.6980056286267762)
        self.assertAlmostEqual(result["pressures"]["zone2"]["negative_kpa"], -2.849167784665694)
        self.assertAlmostEqual(result["pressures"]["zone3"]["negative_kpa"], -4.288120479714341)

    def test_h_equal_18_routes_to_low_rise(self):
        result = calculate_wall_design_pressure(
            region="臺北市",
            district=None,
            building_category=5,
            terrain_category="B",
            kzt=1.0,
            enclosure="enclosed",
            h_m=18.0,
            z_m=None,
            effective_area_m2=1.0,
            least_horizontal_dimension_m=20.0,
            governing_wind_source="code",
        )
        self.assertEqual(result["reference"]["figure"], "3.1(a)")

    def test_partially_enclosed_standardizes_internal_pressure_on_qh(self):
        result = calculate_wall_design_pressure(
            region="基隆市",
            district=None,
            building_category=5,
            terrain_category="B",
            kzt=1.0,
            enclosure="partially_enclosed",
            h_m=50.0,
            z_m=40.0,
            effective_area_m2=10.0,
            least_horizontal_dimension_m=20.0,
            governing_wind_source="code",
        )
        self.assertEqual(
            result["applicability"]["partially_enclosed_internal_velocity_pressure_basis"],
            "q(h)",
        )
        self.assertAlmostEqual(
            result["velocity_pressure"]["qi"]["q_kpa"],
            result["velocity_pressure"]["qh"]["q_kpa"],
        )

    def test_review_adapter_routes_high_and_low_rise(self):
        high = run_review(
            {
                "check_type": "wind_pressure",
                "units": {"pressure": "kPa"},
                "inputs": {
                    "surface": "wall",
                    "region": "臺北市",
                    "building_category": 3,
                    "terrain_category": "B",
                    "kzt": 1.0,
                    "enclosure": "enclosed",
                    "h_m": 50.0,
                    "z_m": 50.0,
                    "effective_area_m2": 1.1,
                    "least_horizontal_dimension_m": 20.0,
                    "governing_wind_source": "code",
                },
                "reported_results": {
                    "zone4.positive_kpa": 2.8374043351450857,
                    "zone5.negative_kpa": -5.201844885928076,
                },
            }
        )
        self.assertEqual(high["calculation_status"], "COMPUTED")
        self.assertEqual(high["comparison_status"], "MATCH")

        roof = run_review(
            {
                "check_type": "wind_pressure",
                "units": {"pressure": "kPa"},
                "inputs": {
                    "surface": "roof",
                    "region": "臺北市",
                    "building_category": 3,
                    "terrain_category": "B",
                    "kzt": 1.0,
                    "enclosure": "enclosed",
                    "h_m": 15.0,
                    "roof_slope_deg": 5.0,
                    "effective_area_m2": 1.0,
                    "least_horizontal_dimension_m": 20.0,
                    "governing_wind_source": "code",
                },
                "reported_results": {
                    "zone3.negative_kpa": -4.288120479714341,
                },
            }
        )
        self.assertEqual(roof["calculation_status"], "COMPUTED")
        self.assertEqual(roof["comparison_status"], "MATCH")
        self.assertEqual(roof["computed"]["reference"]["figure"], "3.1(b)")

        parapet_roof = run_review(
            {
                "check_type": "wind_pressure",
                "units": {"pressure": "kPa"},
                "inputs": {
                    "surface": "roof",
                    "region": "臺北市",
                    "building_category": 3,
                    "terrain_category": "B",
                    "kzt": 1.0,
                    "enclosure": "enclosed",
                    "h_m": 15.0,
                    "roof_slope_deg": 5.0,
                    "effective_area_m2": 1.0,
                    "least_horizontal_dimension_m": 20.0,
                    "governing_wind_source": "code",
                    "apply_parapet_zone3_as_zone2": True,
                    "parapet_all_sides": True,
                    "parapet_height_m": 0.9,
                },
            }
        )
        self.assertEqual(parapet_roof["calculation_status"], "COMPUTED")
        self.assertAlmostEqual(
            parapet_roof["computed"]["pressures"]["zone3"]["negative_kpa"],
            parapet_roof["computed"]["pressures"]["zone2"]["negative_kpa"],
        )

    def test_review_adapter_incomplete_and_unsupported(self):
        incomplete = run_review(
            {
                "check_type": "wind_pressure",
                "units": {"pressure": "kPa"},
                "inputs": {},
            }
        )
        self.assertEqual(incomplete["calculation_status"], "INCOMPLETE_INPUT")

        unsupported_open = run_review(
            {
                "check_type": "wind_pressure",
                "units": {"pressure": "kPa"},
                "inputs": {
                    "surface": "roof",
                    "region": "臺北市",
                    "building_category": 5,
                    "terrain_category": "B",
                    "kzt": 1.0,
                    "enclosure": "open",
                    "h_m": 15.0,
                    "roof_slope_deg": 5.0,
                    "effective_area_m2": 10.0,
                    "least_horizontal_dimension_m": 20.0,
                    "governing_wind_source": "code",
                },
            }
        )
        self.assertEqual(unsupported_open["calculation_status"], "UNSUPPORTED_MODEL")

        unsupported_slope = run_review(
            {
                "check_type": "wind_pressure",
                "units": {"pressure": "kPa"},
                "inputs": {
                    "surface": "roof",
                    "region": "臺北市",
                    "building_category": 5,
                    "terrain_category": "B",
                    "kzt": 1.0,
                    "enclosure": "enclosed",
                    "h_m": 15.0,
                    "roof_slope_deg": 46.0,
                    "effective_area_m2": 10.0,
                    "least_horizontal_dimension_m": 20.0,
                    "governing_wind_source": "code",
                },
            }
        )
        self.assertEqual(unsupported_slope["calculation_status"], "UNSUPPORTED_MODEL")

    def test_wind_tunnel_governing_still_fails_closed(self):
        with self.assertRaises(WindPressureUnsupportedError):
            calculate_wall_design_pressure(
                region="臺北市",
                district=None,
                building_category=5,
                terrain_category="B",
                kzt=1.0,
                enclosure="enclosed",
                h_m=15.0,
                z_m=None,
                effective_area_m2=10.0,
                least_horizontal_dimension_m=20.0,
                governing_wind_source="wind_tunnel",
            )


if __name__ == "__main__":
    unittest.main()
