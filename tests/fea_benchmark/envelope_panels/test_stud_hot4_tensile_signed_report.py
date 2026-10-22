"""Hot 4 synthetic regression. No proprietary measurements."""
import copy
import unittest
from stud_hot4_tensile_signed_report import compare
from stud_engineering_intake_report import fixture
from stud_tensile_strength_screen import METHOD

def strength():
    return dict(method=METHOD,failure_loads=[70,80,90],load_unit="N",
                safety_factor=3,failure_modes=["STUD_FRACTURE","WELD_FAILURE","STUD_FRACTURE"],
                source_sha256="a"*64)

def study():
    cases=[]
    for n in (8,16,24):
        for name,k in (("unlinked",0),("soft",50),("stiff",500)):
            for direction,sign in (("positive",1),("negative",-1)):
                forces=[sign*v for v in ((0,0,0,0) if k==0 else (.2,.3,.3,.2))]
                cases.append(dict(mesh=n,case=name,direction=direction,
                    nominal_signed_pressure_n_per_mm2=sign*.0001,
                    synthetic_k_n_per_mm=k,stud_positions_mm=[150,450,750,1050],
                    signed_forces_n=forces,max_signed_force_magnitude_n=max(map(abs,forces)),
                    total_signed_force_n=sum(forces),rib_end_observed_rf3_n=-sum(forces),
                    rib_balance_residual_n=0,global_z_balance_residual_n=0,
                    center_mean_u3_mm=sign*.01))
    return dict(scope="SYNTHETIC_C3D20R_FIXED_FOUR_STATION_SIGNED_MESH_STUDY_NOT_DESIGN",
        engineering_acceptance="NOT_ADMITTED",case_count=18,
        local_connector_force_convergence="NOT_ESTABLISHED",
        mesh_independent_true_stud_force="NOT_ESTABLISHED",cases=cases)

class TestHot4(unittest.TestCase):
    def test_signed_pair(self):
        result=compare(fixture(),strength(),study())
        self.assertEqual(result["calculation_status"],"COMPUTED_RESEARCH_ONLY")
        self.assertEqual(len(result["directional_research_rows"]),2)
        self.assertFalse(result["ratio_is_design_check"])
        self.assertEqual(result["engineering_acceptance"],"NOT_ADMITTED")
    def test_no_solver(self):
        self.assertEqual(compare(fixture(),strength(),None)["calculation_status"],"EVIDENCE_REQUIRED")
    def test_unsupported_pressure(self):
        req=fixture()
        req["load"]["signed_pressure_n_mm2"]=.004
        self.assertEqual(compare(req,strength(),study())["calculation_status"],"UNSUPPORTED_MODEL")
    def test_wrong_safety_factor(self):
        data=strength()
        data["safety_factor"]=0
        with self.assertRaisesRegex(ValueError,"SAFETY_FACTOR"):
            compare(fixture(),data,study())
    def test_forged_admission(self):
        data=study()
        data["engineering_acceptance"]="PASS"
        with self.assertRaisesRegex(ValueError,"UPSTREAM_SCOPE"):
            compare(fixture(),strength(),data)
    def test_missing_solver_case(self):
        data=study()
        data["cases"].pop()
        with self.assertRaisesRegex(ValueError,"UPSTREAM_COVERAGE"):
            compare(fixture(),strength(),data)
    def test_duplicate_solver_case(self):
        data=study()
        data["cases"][1]=copy.deepcopy(data["cases"][0])
        with self.assertRaisesRegex(ValueError,"UPSTREAM_CASE_ID"):
            compare(fixture(),strength(),data)
    def test_wrong_synthetic_stiffness(self):
        data=study()
        data["cases"][0]["synthetic_k_n_per_mm"]=999
        with self.assertRaisesRegex(ValueError,"UPSTREAM_CASE_PARAMETERS"):
            compare(fixture(),strength(),data)
    def test_rib_reaction_imbalanced(self):
        data=study()
        data["cases"][0]["rib_end_observed_rf3_n"]=10
        with self.assertRaisesRegex(ValueError,"UPSTREAM_FORCE_BALANCE"):
            compare(fixture(),strength(),data)
    def test_bad_force_nan(self):
        data=study()
        data["cases"][0]["signed_forces_n"][0]=float("nan")
        with self.assertRaisesRegex(ValueError,"UPSTREAM_STATION_FORCES"):
            compare(fixture(),strength(),data)
    def test_negative_sign_reversed(self):
        data=study()
        for row in data["cases"]:
            if row["mesh"]==24 and row["case"]=="soft" and row["direction"]=="negative":
                row["signed_forces_n"]=[.2,.3,.3,.2]
                row["total_signed_force_n"]=1
                row["rib_end_observed_rf3_n"]=-1
        with self.assertRaisesRegex(ValueError,"UPSTREAM_SIGN_REVERSAL"):
            compare(fixture(),strength(),data)
    def test_unlinked_still_not_admitted(self):
        result=compare(fixture(case="unlinked"),strength(),study())
        self.assertEqual(result["engineering_acceptance"],"NOT_ADMITTED")
        self.assertTrue(all(r["arithmetic_magnitude_ratio_NOT_UTILIZATION"]==0 for r in result["directional_research_rows"]))

if __name__=="__main__":
    unittest.main()
