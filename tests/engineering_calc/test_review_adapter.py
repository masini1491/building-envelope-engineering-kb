import json
import unittest
from scripts.engineering_calc.beam import BeamElement, simple_span_udl, solve_beam
from scripts.engineering_calc.beam_extrema import beam_extrema
from scripts.engineering_calc.review import run_review

class EngineeringCalcAdapterTests(unittest.TestCase):
    def test_simple_span_extrema_match_closed_form(self):
        els=[BeamElement(0,1,70000,1000000,udl=-2)]
        result=solve_beam(node_positions=[0,1000],elements=els,vertical_restraints=[0,1])
        _,glob=beam_extrema(node_positions=[0,1000],elements=els,result=result)
        closed=simple_span_udl(span=1000,line_load=2,elastic_modulus=70000,inertia=1000000)
        self.assertAlmostEqual(glob.max_abs_shear,closed.shear_max)
        self.assertAlmostEqual(glob.max_abs_moment,closed.moment_max)
        self.assertAlmostEqual(glob.max_abs_deflection,closed.deflection_max)
        self.assertAlmostEqual(glob.max_abs_moment_x,500)
        self.assertAlmostEqual(glob.max_abs_deflection_x,500)

    def test_cantilever_extrema(self):
        els=[BeamElement(0,1,70000,1000000,udl=-1)]
        result=solve_beam(node_positions=[0,1000],elements=els,vertical_restraints=[0],rotational_restraints=[0])
        _,glob=beam_extrema(node_positions=[0,1000],elements=els,result=result)
        self.assertAlmostEqual(glob.max_abs_moment,500000)
        self.assertAlmostEqual(glob.max_abs_deflection,1000**4/(8*70000*1000000))
        self.assertAlmostEqual(glob.max_abs_deflection_x,1000)

    def test_two_span_extrema(self):
        els=[BeamElement(0,1,70000,1000000,udl=-1),BeamElement(1,2,70000,1000000,udl=-1)]
        result=solve_beam(node_positions=[0,1000,2000],elements=els,vertical_restraints=[0,1,2])
        ex,glob=beam_extrema(node_positions=[0,1000,2000],elements=els,result=result)
        self.assertAlmostEqual(glob.max_abs_moment,125000)
        self.assertAlmostEqual(ex[0].max_abs_moment,125000)
        self.assertAlmostEqual(ex[1].max_abs_moment,125000)

    def test_adapter_beam_match(self):
        p={"check_type":"beam","units":{"length":"mm","force":"N","moment":"N*mm","elastic_modulus":"MPa","inertia":"mm^4","line_load":"N/mm"},"inputs":{"node_positions":[0,1000],"elements":[{"start":0,"end":1,"elastic_modulus":70000,"inertia":1000000,"udl":-2}],"vertical_restraints":[0,1]},"reported_results":{"reactions.0":1000,"reactions.1":1000,"global.max_abs_moment":250000}}
        r=run_review(p); self.assertEqual(r["calculation_status"],"COMPUTED"); self.assertEqual(r["comparison_status"],"MATCH")

    def test_adapter_mismatch_and_units_gate(self):
        p={"check_type":"required_inertia","units":{"inertia":"mm^4","deflection":"mm"},"inputs":{"i_trial":100,"delta_trial":12,"delta_allow":8},"reported_results":{"required_inertia":140}}
        self.assertEqual(run_review(p)["comparison_status"],"MISMATCH")
        p.pop("units"); self.assertEqual(run_review(p)["calculation_status"],"INCOMPLETE_INPUT")

    def test_adapter_routes_existing_helpers(self):
        cases=[
          {"check_type":"required_section_modulus","units":{"moment":"N*mm","stress":"MPa"},"inputs":{"moment_max":1200,"allowable_stress":60},"reported_results":{"required_section_modulus":20}},
          {"check_type":"demand_capacity","units":{"force":"N"},"inputs":{"demand":80,"capacity":100},"reported_results":{"utilization":0.8}},
          {"check_type":"projected_bearing_stress","units":{"force":"N","length":"mm"},"inputs":{"force":1000,"diameter":10,"thickness":2},"reported_results":{"projected_bearing_stress":50}},
          {"check_type":"fastener_group","units":{"length":"mm","force":"N"},"inputs":{"points":[[-1,0],[1,0]],"fx":100},"reported_results":{"governing_resultant":50}},
          {"check_type":"audit_force_balance","units":{"force":"N"},"inputs":{"applied_forces":[-1000],"reactions":[500,500]},"reported_results":{"residual":0}}
        ]
        for p in cases:
            with self.subTest(check_type=p["check_type"]):
                r=run_review(p); self.assertEqual(r["calculation_status"],"COMPUTED"); self.assertEqual(r["comparison_status"],"MATCH")

    def test_unsupported_model_and_json_output(self):
        r=run_review({"check_type":"weld_group","units":{"force":"N"},"inputs":{}})
        self.assertEqual(r["calculation_status"],"UNSUPPORTED_MODEL"); json.dumps(r)

if __name__=="__main__": unittest.main()
