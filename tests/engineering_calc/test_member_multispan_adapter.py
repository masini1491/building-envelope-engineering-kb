import unittest
from scripts.engineering_calc.review import run_review

def sample():
    return dict(check_type="member_multispan_screen",
      units={"span":"m","tributary_width":"m","elastic_modulus":"MPa","wind_pressure":"kPa","inertia":"mm^4","section_modulus":"mm^3"},
      inputs=dict(member_role="mullion",span_lengths_m=[2,2],span_source="synthetic",tributary_widths_m=[1,1],tributary_width_source="synthetic",
        wind_cases=[dict(name="uniform",signed_pressure_kpa_by_span=[-1,-1],pressure_source="synthetic")],
        options=[dict(name="A",support_model="continuous_pinned_supports",support_source="idealized",continuity_source="synthetic",
          material_source="synthetic",section_property_source="synthetic",elastic_modulus_mpa=70000,
          inertia_mm4_by_span=[1000000,1000000],section_modulus_positive_mm3_by_span=[10000,10000],
          section_modulus_negative_mm3_by_span=[20000,20000])]))

class MultispanTests(unittest.TestCase):
    def test_equal_span_known_solution(self):
        x=run_review(sample())
        self.assertEqual(x["calculation_status"],"COMPUTED",x["review_flags"])
        case=x["computed"]["options"][0]["cases"][0]
        self.assertAlmostEqual(case["maximum_absolute_moment_n_mm"],500000,places=5)
        self.assertAlmostEqual(sum(case["reactions_n"]),4000,places=5)
        self.assertEqual(x["computed"]["engineering_acceptance"],"NOT_ADMITTED")

    def test_wrong_support_and_units_rejected(self):
        a=sample(); a["inputs"]["options"][0]["support_model"]="semi_rigid"
        self.assertEqual(run_review(a)["calculation_status"],"UNSUPPORTED_MODEL")
        a=sample(); a["units"]["span"]="mm"
        self.assertEqual(run_review(a)["calculation_status"],"INCOMPLETE_INPUT")

    def test_reported_comparison(self):
        a=sample(); a["reported_results"]={"options.0.cases.0.maximum_absolute_moment_n_mm":500000}
        self.assertEqual(run_review(a)["comparison_status"],"MATCH")
        a["reported_results"]["options.0.cases.0.maximum_absolute_moment_n_mm"]=1
        self.assertEqual(run_review(a)["comparison_status"],"MISMATCH")

if __name__=="__main__":
    unittest.main()
