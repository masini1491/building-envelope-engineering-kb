import unittest

from scripts.engineering_calc.review import run_review
from scripts.engineering_calc.wind_pressure import (
    WindPressureInputError,
    WindPressureUnsupportedError,
    calculate_wall_design_pressure,
    figure_3_2_wall_gcp,
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

    def test_figure_3_2_plateaus_and_semilog_interpolation(self):
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

    def test_full_enclosed_wall_case_is_reproducible(self):
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
        self.assertEqual(result["corner_zone"]["a_m"], 2.0)
        self.assertEqual(
            result["display_pressures"]["zone5"]["negative_kpa"],
            -5.2,
        )

    def test_partially_enclosed_v1_standardizes_internal_pressure_on_qh(self):
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

    def test_review_adapter_routes_wind_pressure_and_compares_reported_values(self):
        payload = {
            "check_type": "wind_pressure",
            "units": {
                "length": "m",
                "area": "m^2",
                "velocity": "m/s",
                "pressure": "kPa",
            },
            "inputs": {
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
        result = run_review(payload)
        self.assertEqual(result["calculation_status"], "COMPUTED")
        self.assertEqual(result["comparison_status"], "MATCH")
        self.assertEqual(result["check_type"], "wind_pressure")

    def test_review_adapter_preserves_incomplete_vs_unsupported(self):
        incomplete = run_review(
            {
                "check_type": "wind_pressure",
                "units": {"pressure": "kPa"},
                "inputs": {},
            }
        )
        self.assertEqual(incomplete["calculation_status"], "INCOMPLETE_INPUT")

        unsupported = run_review(
            {
                "check_type": "wind_pressure",
                "units": {"length": "m", "area": "m^2", "pressure": "kPa"},
                "inputs": {
                    "region": "臺北市",
                    "building_category": 5,
                    "terrain_category": "B",
                    "kzt": 1.0,
                    "enclosure": "open",
                    "h_m": 50.0,
                    "z_m": 50.0,
                    "effective_area_m2": 10.0,
                    "least_horizontal_dimension_m": 20.0,
                    "governing_wind_source": "code",
                },
            }
        )
        self.assertEqual(unsupported["calculation_status"], "UNSUPPORTED_MODEL")

    def test_v1_scope_fails_closed(self):
        common = dict(
            region="臺北市",
            district=None,
            building_category=5,
            terrain_category="B",
            kzt=1.0,
            h_m=50.0,
            z_m=50.0,
            effective_area_m2=10.0,
            least_horizontal_dimension_m=20.0,
            governing_wind_source="code",
        )
        with self.assertRaises(WindPressureUnsupportedError):
            calculate_wall_design_pressure(enclosure="open", **common)

        low_building = dict(common)
        low_building.update(h_m=18.0, z_m=18.0)
        with self.assertRaises(WindPressureUnsupportedError):
            calculate_wall_design_pressure(enclosure="enclosed", **low_building)

        tunnel = dict(common)
        tunnel["governing_wind_source"] = "wind_tunnel"
        with self.assertRaises(WindPressureUnsupportedError):
            calculate_wall_design_pressure(enclosure="enclosed", **tunnel)


if __name__ == "__main__":
    unittest.main()
