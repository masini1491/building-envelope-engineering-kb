"""Fail-closed signed-pressure positive/negative tests without private sources."""
import unittest

from pressure_contact_trial import APPLIED_TOTAL_Z_N
from stud_signed_pressure_trial import deck, CASES, DIRECTIONS, POSITIVE_CARD, NEGATIVE_CARD
from stud_solid_trial import deck as baseline
from verify_pressure_contact_trial import nominal_pressure_equivalents
from verify_stud_signed_pressure_trial import check_observations, verify


def observation(sign, n=8, case='soft'):
    k = CASES[case]
    nodes = {"STUD_PLATE": [11, 12, 13, 14],
             "STUD_RIB": [21, 22, 23, 24],
             "CENTER_RF": [31, 32]}
    forces = [sign * v for v in (0.4, 0.5, 0.5, 0.4)] if k else [0.0] * 4
    plate = {i: (0., 0., (v / k if k else 0.0)) for i, v in zip(nodes["STUD_PLATE"], forces)}
    rib = {i: (0., 0., 0.) for i in nodes["STUD_RIB"]}
    center = {i: (0., 0., sign * .001) for i in nodes["CENTER_RF"]}
    rib_rf = -sum(forces)
    plate_rf = (-sign * APPLIED_TOTAL_Z_N +
                sign * nominal_pressure_equivalents(n)["edge_pressure_n"] - rib_rf)
    return (nodes, plate, rib, center, plate_rf, rib_rf)


class SignedDeck(unittest.TestCase):
    def test_positive_is_original_byte_exact(self):
        for n in (8,16):
            for case in CASES:
                self.assertEqual(deck(n, case, "positive"), baseline(n, case))
    def test_negative_changes_only_signed_pressure(self):
        for n in (8,16):
            for case in CASES:
                plus = deck(n, case, "positive")
                minus = deck(n, case, "negative")
                self.assertEqual(plus.count(POSITIVE_CARD), 1)
                self.assertEqual(minus.count(NEGATIVE_CARD), 1)
                self.assertEqual(minus.replace(NEGATIVE_CARD, POSITIVE_CARD), plus)
                self.assertNotIn("*CONTACT PAIR", minus)
    def test_no_other_mesh_or_case_or_sign(self):
        for n,case,direction in ((24,'soft','positive'),(True,'soft','positive'),
                                 (8,'weld','positive'),(8,'soft','shear')):
            with self.subTest(n=n,case=case,direction=direction):
                with self.assertRaisesRegex(ValueError,'STUD_SIGNED_SCOPE'):
                    deck(n,case,direction)


class SignedOracle(unittest.TestCase):
    def run_oracle(self, sign, n, case):
        observations = observation(sign,n,case)
        return check_observations(n,case,"positive" if sign == 1 else "negative",*observations)
    def test_both_signs_meshes_cases(self):
        for n in (8,16):
            for case in CASES:
                for sign in (-1,1):
                    with self.subTest(n=n,case=case,sign=sign):
                        result=self.run_oracle(sign,n,case)
                        self.assertLess(abs(result["rib_action_reaction_residual_n"]),1e-9)
                        self.assertLess(abs(result["corrected_global_z_residual_n"]),1e-9)
                        self.assertEqual(result["center_mean_u3_mm"] > 0, sign > 0)
    def test_unlinked_rib_transfer_fails(self):
        parts = list(observation(1,8,'unlinked'));parts[-1]=0.03
        with self.assertRaisesRegex(ValueError,'UNLINKED_TRANSFER'):
            check_observations(8,'unlinked','positive',*parts)
    def test_reversed_negative_link_sign_fails(self):
        parts=list(observation(-1,8,'soft'))
        fake={i:(0.,0.,abs(v[2])) for i,v in parts[1].items()}
        parts[1]=fake
        with self.assertRaisesRegex(ValueError,'SIGNED_TRANSFER_DIRECTION'):
            check_observations(8,'soft','negative',*parts)
    def test_unbalanced_rib_fails(self):
        parts=list(observation(1,8,'stiff'));parts[-1]+=0.01
        with self.assertRaisesRegex(ValueError,'RIB_ACTION_REACTION'):
            check_observations(8,'stiff','positive',*parts)
    def test_missing_pressure_correction_fails(self):
        parts=list(observation(1,8,'soft'));parts[-2]+=1.
        with self.assertRaisesRegex(ValueError,'GLOBAL_Z_BALANCE'):
            check_observations(8,'soft','positive',*parts)
    def test_symmetry_break_fails(self):
        parts=list(observation(1,8,'soft'))
        parts[1][11]=(0.,0.,.15)
        with self.assertRaisesRegex(ValueError,'STATION_SYMMETRY'):
            check_observations(8,'soft','positive',*parts)
    def test_center_sign_break_fails(self):
        parts=list(observation(-1,8,'soft'))
        parts[3]={i:(0.,0.,abs(v[2])) for i,v in parts[3].items()}
        with self.assertRaisesRegex(ValueError,'CENTER_DIRECTION'):
            check_observations(8,'soft','negative',*parts)
    def test_nonfinite_force_fails(self):
        parts=list(observation(1,8,'soft'))
        parts[1][11]=(0.,0.,float("nan"))
        with self.assertRaisesRegex(ValueError,'NONFINITE_STATION'):
            check_observations(8,'soft','positive',*parts)
    def test_missing_solver_evidence_fails(self):
        with self.assertRaisesRegex(ValueError,'MISSING_SOLVER_EVIDENCE'):
            verify('/no/such/synthetic/solver-output')


if __name__=="__main__":
    unittest.main()
