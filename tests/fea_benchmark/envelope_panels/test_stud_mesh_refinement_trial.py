"""Synthetic-only regression for the Hot-2 n24 model and fail-closed screen."""
import copy
import math
import tempfile
import unittest
from pathlib import Path

from stud_mesh_refinement_trial import (
    CASES, DIRECTIONS, MESHES, deck, generate, n24_positive,
)
from stud_signed_pressure_trial import deck as hot1_deck, POSITIVE_CARD, NEGATIVE_CARD
from stud_solid_trial import STATIONS, model_nodes
from verify_stud_solid_trial import sets
from verify_pressure_contact_trial import nominal_pressure_equivalents
from pressure_contact_trial import APPLIED_TOTAL_Z_N
from verify_stud_mesh_refinement_trial import sample, compare, verify


def observation(n, case, direction, scale=1.):
    sign=DIRECTIONS[direction];k=CASES[case]
    groups={
      "STUD_PLATE":[101,102,103,104],
      "STUD_RIB":[201,202,203,204],
      "CENTER_RF":[301,302]
    }
    f=[scale*sign*z for z in (0.4,0.5,0.5,0.4)] if k else [0.]*4
    plate={node:(0.,0.,(v/k if k else 0.)) for node,v in zip(groups["STUD_PLATE"],f)}
    rib={node:(0.,0.,0.) for node in groups["STUD_RIB"]}
    center={node:(0.,0.,sign*scale*.01) for node in groups["CENTER_RF"]}
    support=-sum(f)
    plate_rf=(-sign*APPLIED_TOTAL_Z_N+sign*nominal_pressure_equivalents(n)["edge_pressure_n"]-support)
    return [groups,plate,rib,center,plate_rf,support]


def result(n,case,direction,scale=1.):
    return sample(n,case,direction,*observation(n,case,direction,scale))


class Hot2Tests(unittest.TestCase):
    def test_reused_hot1_input_exact(self):
        for n in (8,16):
            for case in CASES:
                for sign in DIRECTIONS:
                    self.assertEqual(deck(n,case,sign),hot1_deck(n,case,sign))
    def test_n24_pressure_only_sign_change(self):
        for case in CASES:
            plus=deck(24,case,"positive")
            neg=deck(24,case,"negative")
            self.assertEqual(plus.count(POSITIVE_CARD),1)
            self.assertEqual(neg.count(NEGATIVE_CARD),1)
            self.assertEqual(neg.replace(NEGATIVE_CARD,POSITIVE_CARD),plus)
            self.assertNotIn("*CONTACT PAIR",plus)
    def test_n24_stations_are_unique_and_independent(self):
        for case in CASES:
            src=deck(24,case,"positive")
            groups=sets(src)
            nodes,bodies,last=model_nodes(src)
            self.assertEqual(len(groups["STUD_PLATE"]),4)
            self.assertEqual(len(groups["STUD_RIB"]),4)
            self.assertEqual(len(set(groups["STUD_PLATE"]+groups["STUD_RIB"])),8)
            for x,p,r in zip(STATIONS,groups["STUD_PLATE"],groups["STUD_RIB"]):
                self.assertEqual(nodes[p],(x,0.,1.5))
                self.assertEqual(nodes[r],(x,0.,1.5))
                self.assertIn(p,bodies["PLATE"])
                self.assertIn(r,bodies["RIB"])
    def test_n24_link_definition(self):
        for name,k in CASES.items():
            s=n24_positive(name)
            self.assertEqual(s.count("*ELEMENT,TYPE=SPRING2"),int(k>0))
            if k:
                self.assertIn(f"\n{k:.8f}\n",s)
    def test_scope_rejects_unknown(self):
        for n,case,direction in ((32,"soft","positive"),(True,"soft","positive"),
                                 (24,"actual_weld","positive"),(24,"soft","lateral")):
            with self.assertRaisesRegex(ValueError,"STUD_REFINEMENT_INPUT_SCOPE"):
                deck(n,case,direction)
    def test_fresh_target_only(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"new"
            generate(root,24,"unlinked","positive")
            self.assertEqual((root/"panel.inp").read_text(),deck(24,"unlinked","positive"))
            with self.assertRaisesRegex(ValueError,"FRESH_DIRECTORY"):
                generate(root,24,"unlinked","positive")
    def test_mock_positive_negative_balance(self):
        for n in MESHES:
            for c in CASES:
                for direction in DIRECTIONS:
                    a=result(n,c,direction)
                    self.assertLess(abs(a["rib_balance_residual_n"]),1e-12)
                    self.assertLess(abs(a["global_z_balance_residual_n"]),1e-12)
    def test_bad_rib_reaction_fails(self):
        args=observation(24,"soft","negative");args[-1]+=.1
        with self.assertRaisesRegex(ValueError,"RIB_ACTION_REACTION"):
            sample(24,"soft","negative",*args)
    def test_bad_global_balance_fails(self):
        args=observation(24,"stiff","positive");args[-2]+=.1
        with self.assertRaisesRegex(ValueError,"GLOBAL_BALANCE"):
            sample(24,"stiff","positive",*args)
    def test_wrong_negative_transfer_sign_fails(self):
        args=observation(24,"soft","negative")
        args[1]={i:(0.,0.,abs(u[2])) for i,u in args[1].items()}
        with self.assertRaisesRegex(ValueError,"STATION_WRONG_DIRECTION"):
            sample(24,"soft","negative",*args)
    def test_center_sign_fails(self):
        args=observation(24,"soft","negative")
        args[3]={i:(0.,0.,abs(u[2])) for i,u in args[3].items()}
        with self.assertRaisesRegex(ValueError,"CENTER_SIGN"):
            sample(24,"soft","negative",*args)
    def test_unlinked_rib_fails(self):
        args=observation(24,"unlinked","positive");args[-1]=.2
        with self.assertRaisesRegex(ValueError,"UNLINKED"):
            sample(24,"unlinked","positive",*args)
    def test_symmetry_fails(self):
        args=observation(24,"soft","positive")
        args[1][101]=(0.,0.,.099)
        with self.assertRaisesRegex(ValueError,"SYMMETRY"):
            sample(24,"soft","positive",*args)
    def test_nonfinite_fails(self):
        args=observation(24,"soft","positive")
        args[1][101]=(0.,0.,float("nan"))
        with self.assertRaisesRegex(ValueError,"STATION_NONFINITE"):
            sample(24,"soft","positive",*args)
    def test_three_mesh_comparisons_and_no_design(self):
        all_rows=[result(n,c,d,1.+.003*math.sqrt(8/n)) for n in MESHES for c in CASES for d in DIRECTIONS]
        x=compare(all_rows)
        self.assertEqual(x["case_count"],18)
        self.assertEqual(len(x["comparisons"]),12)
        self.assertTrue(x["last_refinement_passes_declared_5_percent_screen"])
        self.assertEqual(x["local_connector_force_convergence"],"NOT_ESTABLISHED")
        self.assertEqual(x["engineering_acceptance"],"NOT_ADMITTED")
    def test_drifting_refinement_screen_is_not_pass(self):
        all_rows=[result(n,c,d,n/8.) for n in MESHES for c in CASES for d in DIRECTIONS]
        x=compare(all_rows)
        self.assertFalse(x["last_refinement_passes_declared_5_percent_screen"])
        self.assertEqual(x["last_refinement_status"],"MESH_SENSITIVITY_NOT_WITHIN_SCREEN")
    def test_duplicate_and_missing_cases(self):
        xs=[result(n,c,d) for n in MESHES for c in CASES for d in DIRECTIONS]
        copied=copy.deepcopy(xs)
        copied[1]=copy.deepcopy(copied[0])
        with self.assertRaisesRegex(ValueError,"DUPLICATE_CASE"):
            compare(copied)
        with self.assertRaisesRegex(ValueError,"CASE_COUNT"):
            compare(xs[:-1])
    def test_no_solver_data_does_not_pass(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_FILE"):
            verify("/nonexistent-c3d20r-refinement")


if __name__=="__main__":unittest.main()
