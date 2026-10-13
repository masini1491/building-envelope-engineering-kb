"""Stage 67 exact derived loads, height distribution and mesh screen tests."""
import copy
import unittest
from check_rib_force_peak_distribution import (
    K_PER_NODE, end_profile, compare_meshes
)

def synthetic_case(n, window):
    zz=range(1,5) if window=="low" else range(5,9)
    sides={}
    for side, sign in (("x0",-1.),("x100",1.)):
        rows=[]
        for z in zz:
            ux=sign*z*1e-6*(1 if n==8 else 1.04)
            force=K_PER_NODE*ux
            rows.append({"node_id":z+(100 if side=="x100" else 0),
                         "z_mm":float(z), "u_x_mm":ux,
                         "k_times_u_x_n":force,
                         "z_times_k_u_n_mm":z*force,
                         "half_k_u_squared_n_mm":.5*K_PER_NODE*ux*ux})
        sides[side]={
            "selected_nodes":rows,
            "derived_sum_absolute_k_u_n":sum(abs(r["k_times_u_x_n"]) for r in rows),
            "derived_signed_k_u_n":sum(r["k_times_u_x_n"] for r in rows),
            "derived_sum_absolute_z_k_u_n_mm":sum(abs(r["z_times_k_u_n_mm"]) for r in rows),
            "derived_signed_z_k_u_n_mm":sum(r["z_times_k_u_n_mm"] for r in rows),
            "derived_spring_energy_n_mm":sum(r["half_k_u_squared_n_mm"] for r in rows),
            "largest_abs_individual_k_u_n":max(abs(r["k_times_u_x_n"]) for r in rows),
        }
    return {"spring_height_window":window,"per_end":sides}

def cases():
    return {f"n{n}_{w}":synthetic_case(n,w)
            for n in (8,16) for w in ("low","high")}

class Stage67Tests(unittest.TestCase):
    def test_profiles(self):
        for w in ("low","high"):
            p=end_profile(synthetic_case(16,w),"x0",w)
            self.assertEqual(len(p["height_distribution"]),4)
            self.assertEqual(p["peak_at_height_mm"],4 if w=="low" else 8)
            self.assertAlmostEqual(sum(x["force_fraction"] for x in p["height_distribution"]),1.)
            self.assertEqual(p["not_measured_connector_reaction_or_capacity"],True)
    def test_compare_mesh_screen(self):
        v=compare_meshes(cases())
        self.assertEqual(v["engineering_acceptance"],"NOT_ADMITTED")
        self.assertEqual(v["independent_spring_reaction"],"NOT_MEASURED_K_TIMES_U_ONLY")
        self.assertLess(v["cases_by_window_and_end"]["high"]["x0"]
            ["global_metric_mesh_relative_differences"]["peak_individual_abs_k_u_n"],.15)
    def test_reject_bad_force_identity(self):
        bad=synthetic_case(16,"low")
        bad["per_end"]["x0"]["selected_nodes"][0]["k_times_u_x_n"]*=2
        with self.assertRaisesRegex(ValueError,"ARITHMETIC_IDENTITY"):
            end_profile(bad,"x0","low")
    def test_reject_duplicate_height_and_missing_node(self):
        bad=synthetic_case(16,"high")
        bad["per_end"]["x0"]["selected_nodes"][0]["z_mm"]=6.
        first=bad["per_end"]["x0"]["selected_nodes"][0]
        first["z_times_k_u_n_mm"]=6.*first["k_times_u_x_n"]
        with self.assertRaisesRegex(ValueError,"NONFINITE_OR_DUPLICATED"):
            end_profile(bad,"x0","high")
        bad=synthetic_case(16,"high")
        bad["per_end"]["x0"]["selected_nodes"].pop()
        with self.assertRaisesRegex(ValueError,"FOUR_SPRING"):
            end_profile(bad,"x0","high")
    def test_reject_mesh_drift_and_missing_case(self):
        bad=cases()
        bad["n8_low"]=copy.deepcopy(bad["n8_low"])
        for side in ("x0","x100"):
            rows=bad["n8_low"]["per_end"][side]["selected_nodes"]
            for row in rows:
                row["u_x_mm"]*=2
                row["k_times_u_x_n"]*=2
                row["z_times_k_u_n_mm"]*=2
                row["half_k_u_squared_n_mm"]*=4
            end=bad["n8_low"]["per_end"][side]
            for key in ("derived_sum_absolute_k_u_n","derived_signed_k_u_n",
                        "derived_sum_absolute_z_k_u_n_mm","derived_signed_z_k_u_n_mm",
                        "largest_abs_individual_k_u_n"):
                end[key]*=2
            end["derived_spring_energy_n_mm"]*=4
        with self.assertRaisesRegex(ValueError,"MESH_SCREEN"):
            compare_meshes(bad)
        with self.assertRaisesRegex(ValueError,"REQUIRED_CASE_COVERAGE"):
            compare_meshes({k:v for k,v in cases().items() if k!="n8_low"})
    def test_reject_false_symmetry(self):
        bad=cases()
        right=bad["n16_low"]["per_end"]["x100"]
        for row in right["selected_nodes"]:
            row["u_x_mm"]*=1.1
            row["k_times_u_x_n"]*=1.1
            row["z_times_k_u_n_mm"]*=1.1
            row["half_k_u_squared_n_mm"]*=1.21
        for key in ("derived_sum_absolute_k_u_n","derived_signed_k_u_n",
                    "derived_sum_absolute_z_k_u_n_mm","derived_signed_z_k_u_n_mm",
                    "largest_abs_individual_k_u_n"):
            right[key]*=1.1
        right["derived_spring_energy_n_mm"]*=1.21
        with self.assertRaisesRegex(ValueError,"SYMMETRIC_GROUP_ENVELOPE_MISMATCH"):
            compare_meshes(bad)

if __name__=="__main__":
    unittest.main()
