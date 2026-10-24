import unittest
from scripts.engineering_calc.review import run_review

def payload():
    return {
        "check_type": "member_preliminary_screen",
        "units": {"span": "m", "tributary_width": "m", "elastic_modulus": "MPa",
                  "wind_pressure": "kPa", "inertia": "mm^4", "section_modulus": "mm^3"},
        "inputs": {
            "member_role": "mullion",
            "span_m_range": [2, 2], "span_source": "example only",
            "tributary_width_m_range": [1, 1], "tributary_width_source": "example only",
            "elastic_modulus_mpa_range": [70000, 70000],
            "elastic_modulus_source": "example only",
            "wind_cases": [
                {"name": "pressure", "direction": "positive",
                 "pressure_magnitude_kpa_range": [1, 1], "pressure_source": "example only"},
                {"name": "suction", "direction": "negative",
                 "pressure_magnitude_kpa_range": [2, 2], "pressure_source": "example only"},
            ],
            "options": [
                {"name": "A", "support_model": "simply_supported",
                 "support_source": "ideal assumption", "section_property_source": "example only",
                 "inertia_mm4_range": [1e6, 1e6],
                 "section_modulus_positive_mm3_range": [1e4, 1e4],
                 "section_modulus_negative_mm3_range": [2e4, 2e4]},
                {"name": "B", "support_model": "cantilever",
                 "support_source": "ideal assumption", "section_property_source": "example only",
                 "inertia_mm4_range": [2e6, 2e6],
                 "section_modulus_positive_mm3_range": [2e4, 2e4],
                 "section_modulus_negative_mm3_range": [2e4, 2e4]},
            ],
            "deflection_limit_mm": 10,
            "deflection_limit_source": "example criterion only",
        },
        "reported_results": {
            "options.0.cases.0.max_moment_n_mm.maximum": 500000,
            "options.0.cases.1.extreme_fiber_stress_mpa.maximum": 50,
        },
    }

class MemberPreliminaryAdapterTests(unittest.TestCase):
    def test_multiple_options_and_directions(self):
        r = run_review(payload())
        self.assertEqual(r["calculation_status"], "COMPUTED")
        self.assertEqual(r["comparison_status"], "MATCH")
        self.assertEqual(len(r["computed"]["options"]), 2)
        self.assertEqual(r["computed"]["acceptance_status"], "NOT_ADMITTED")
        self.assertIn("LOCAL_BUCKLING", r["computed"]["unevaluated_modes"])
        self.assertAlmostEqual(r["computed"]["options"][0]["cases"][0]
                               ["max_moment_n_mm"]["maximum"], 500000)

    def test_reported_numeric_mismatch(self):
        p = payload()
        p["reported_results"]["options.0.cases.0.max_moment_n_mm.maximum"] = 1
        self.assertEqual(run_review(p)["comparison_status"], "MISMATCH")

    def test_no_reported_is_not_provided(self):
        p = payload()
        p.pop("reported_results")
        self.assertEqual(run_review(p)["comparison_status"], "NOT_PROVIDED")

    def test_bad_units_fail_closed(self):
        for units in ({"span": "mm"}, {"span": "m"}, {**payload()["units"], "force": "N"},
                      {**payload()["units"], "wind_pressure": "Pa"}):
            p = payload()
            p["units"] = units
            self.assertEqual(run_review(p)["calculation_status"], "INCOMPLETE_INPUT")

    def test_unsupported_support_model(self):
        p = payload()
        p["inputs"]["options"][0]["support_model"] = "semi_rigid"
        self.assertEqual(run_review(p)["calculation_status"], "UNSUPPORTED_MODEL")

    def test_missing_provenance_and_invalid_ranges(self):
        for field, value in (("span_source", ""), ("span_m_range", [3, 2]),
                             ("elastic_modulus_mpa_range", [float("nan"), 70000])):
            p = payload()
            p["inputs"][field] = value
            self.assertEqual(run_review(p)["calculation_status"], "INCOMPLETE_INPUT")

    def test_unknown_fields_and_reported_keys(self):
        p = payload()
        p["inputs"]["unrecognized_allowable_strength"] = 100
        self.assertEqual(run_review(p)["calculation_status"], "INCOMPLETE_INPUT")
        p = payload()
        p["inputs"]["options"][0]["adm_capacity"] = 200
        self.assertEqual(run_review(p)["calculation_status"], "INCOMPLETE_INPUT")
        p = payload()
        p["reported_results"] = {"acceptance_status": 1}
        self.assertEqual(run_review(p)["comparison_status"], "INCOMPLETE")

if __name__ == "__main__":
    unittest.main()
