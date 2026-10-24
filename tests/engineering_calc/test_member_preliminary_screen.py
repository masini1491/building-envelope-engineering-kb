import unittest
from scripts.engineering_calc.member_preliminary_screen import (
    MemberScreenInputError, screen_preliminary_member_options,
)

def sample(**changes):
    args=dict(
        member_role="mullion", span_m_range=[2., 2.],
        span_source="verified drawing", tributary_width_m_range=[1., 1.],
        tributary_width_source="verified layout",
        elastic_modulus_mpa_range=[70000., 70000.], elastic_modulus_source="supplied material",
        wind_cases=[
            dict(name="push", direction="positive", pressure_magnitude_kpa_range=[1.,1.], pressure_source="wind input"),
            dict(name="suction", direction="negative", pressure_magnitude_kpa_range=[2.,2.], pressure_source="wind input"),
        ],
        options=[dict(name="section A",support_model="simply_supported",support_source="ideal beam assumption",
                      section_property_source="section calculation",inertia_mm4_range=[1000000.,1000000.],
                      section_modulus_positive_mm3_range=[10000.,10000.],
                      section_modulus_negative_mm3_range=[20000.,20000.])],
    )
    args.update(changes)
    return screen_preliminary_member_options(**args)

class MemberScreenTests(unittest.TestCase):
    def test_simple_span_against_hand_formula_and_opposite_fibres(self):
        result=sample()
        positive,negative=result.options[0].cases
        self.assertAlmostEqual(positive.line_load_n_per_mm.maximum, 1.)
        self.assertAlmostEqual(positive.max_shear_n.maximum, 1000.)
        self.assertAlmostEqual(positive.max_moment_n_mm.maximum, 500000.)
        self.assertAlmostEqual(positive.max_deflection_mm.maximum, 5*1*2000**4/(384*70000*1e6))
        self.assertAlmostEqual(positive.extreme_fiber_stress_mpa.maximum,50.)
        self.assertAlmostEqual(negative.max_moment_n_mm.maximum,1000000.)
        self.assertAlmostEqual(negative.extreme_fiber_stress_mpa.maximum,50.)
        self.assertEqual(result.acceptance_status,"NOT_ADMITTED")
        self.assertIn("LOCAL_BUCKLING", result.unevaluated_modes)

    def test_cantilever_against_hand_formula(self):
        opt=sample()["none"] if False else dict(name="section B",support_model="cantilever",
                      support_source="ideal fixity", section_property_source="measured",
                      inertia_mm4_range=[1e6,1e6],
                      section_modulus_positive_mm3_range=[1e4,1e4],
                      section_modulus_negative_mm3_range=[2e4,2e4])
        v=sample(options=[opt]).options[0].cases[0]
        self.assertAlmostEqual(v.max_shear_n.maximum,2000.)
        self.assertAlmostEqual(v.max_moment_n_mm.maximum,2000000.)
        self.assertAlmostEqual(v.max_deflection_mm.maximum,1*2000**4/(8*70000*1e6))

    def test_interval_monotonicity_and_limit(self):
        args=dict(span_m_range=[2., 3.],tributary_width_m_range=[1.,2.],
                  elastic_modulus_mpa_range=[60000.,70000.],
                  deflection_limit_mm=5.,deflection_limit_source="project criterion")
        result=sample(**args)
        positive=result.options[0].cases[0]
        self.assertAlmostEqual(positive.max_moment_n_mm.minimum, 500000.)
        self.assertAlmostEqual(positive.max_moment_n_mm.maximum, 2*3000**2/8)
        self.assertLess(positive.max_deflection_mm.minimum,positive.max_deflection_mm.maximum)
        self.assertEqual(positive.deflection_limit_comparison,"MIXED_MODEL_SCENARIOS_AGAINST_SUPPLIED_LIMIT")

    def test_invalid_input_rejected(self):
        cases=[
            dict(span_m_range=[2,-1]),dict(span_m_range=[2,1]),dict(span_m_range=[0,1]),
            dict(elastic_modulus_mpa_range=[0,70000]),
            dict(elastic_modulus_mpa_range=[float("inf"),70000]),
            dict(member_role="generic"),dict(wind_cases=[]),
            dict(wind_cases=[dict(name="p",direction="positive",pressure_magnitude_kpa_range=[0,0],pressure_source="x")]),
            dict(options=[dict(name="x",support_model="semi_rigid")]),
            dict(span_source=""),dict(deflection_limit_mm=5),
        ]
        for bad in cases:
            with self.subTest(bad=bad), self.assertRaises(MemberScreenInputError):
                sample(**bad)

if __name__=="__main__":
    unittest.main()
