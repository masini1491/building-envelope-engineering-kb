"""Synthetic connector rib reaction crosscheck: source-free negative tests."""
import unittest
from verify_stud_solid_independent_balance import check_pair, final_field, input_guard

class RibIndependentTest(unittest.TestCase):
    def test_clean_unlinked(self):
        self.assertEqual(check_pair([0.,0.,0.,0.],0.,'unlinked'),(0.,0.))
    def test_link_force_and_reaction(self):
        total,resid=check_pair([.35,.45,.45,.35],-1.6,'soft')
        self.assertAlmostEqual(total,1.6);self.assertAlmostEqual(resid,0.)
    def test_wrong_reaction(self):
        with self.assertRaisesRegex(ValueError,'RIB_ACTION_REACTION'):
            check_pair([.35,.45,.45,.35],-1.55,'soft')
    def test_unsymmetric(self):
        with self.assertRaisesRegex(ValueError,'STATION_SYMMETRY'):
            check_pair([.35,.45,.45,.36],-1.61,'soft')
    def test_wrong_direction(self):
        with self.assertRaisesRegex(ValueError,'TRANSFER_DIRECTION'):
            check_pair([-.35,.45,.45,.35],-.9,'soft')
    def test_false_unlinked(self):
        with self.assertRaisesRegex(ValueError,'RIB_ACTION_REACTION|UNLINKED_FORCE'):
            check_pair([0.,0.,0.,0.],.02,'unlinked')
    def test_final_field(self):
        text='forces (fx,fy,fz) for set RIB_END_RF and time  0.1000000E+01\n\n  99 0.000000E+00 0.000000E+00 -1.000000E+00\n\n'
        self.assertEqual(final_field(text,'forces','RIB_END_RF')[99][2],-1.)
        with self.assertRaisesRegex(ValueError,'FINAL_FIELD'):
            final_field(text.replace('0.1000000E+01','0.5000000E+00'),'forces','RIB_END_RF')
    def test_direct_rib_load_rejected(self):
        sets={'STUD_PLATE':[1,2,3,4],'STUD_RIB':[5,6,7,8],'RIB_END_RF':[9]}
        bad='*DLOAD\nPLATE,P1,0.00010000\nRIB_END_RF,1,3,0.\n*CLOAD\n9,3,1.0\n'
        with self.assertRaisesRegex(ValueError,'EXTERNAL_RIB_LOAD_OR_CONTACT'):
            input_guard(bad,'unlinked',sets)

if __name__=='__main__':unittest.main()
