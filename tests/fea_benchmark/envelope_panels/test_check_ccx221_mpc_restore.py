"""Synthetic replay + negative controls for the S8R MPC diagnostic verifier."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from check_ccx221_mpc_restore import audit, parse

P = ('KB_EVENT P 1 1 1 3 4 2\n'
     'KB_FN P 1 3 -1 5\n'
     'KB_FN P 2 3 -2 3\n'
     'KB_FN P 3 3 -3 -8\n')
Q = ('KB_EVENT Q 1 1 1 3 4 2\n'
     'KB_FN Q 1 3 -1 5\n'
     'KB_FN Q 2 3 -2 -7\n'
     'KB_FN Q 3 3 -3 -8\n'
     'KB_MPC 1 KNOT1 5\n'
     'KB_TERM 1 1 1 3 1\n'
     'KB_TERM 1 2 2 3 2\n'
     'KB_MPC 2 MEANROTBS -7\n'
     'KB_TERM 2 1 2 3 1\n'
     'KB_TERM 2 2 3 3 -1\n')
DAT = (' forces (fx,fy,fz) for set ALL_ORIGINAL_RF and time  0.1000000E+01\n'
       ' 1 0 0 5\n 2 0 0 -7\n 3 0 0 -8\n\n')

class CheckMpcRestore(unittest.TestCase):
    def test_synthetic_cascade(self):
        out=audit(P+Q,DAT)
        self.assertEqual(out['increment_count'],1)
        self.assertAlmostEqual(out['final']['net_mpc_fn3_change_n'],-10)
        self.assertAlmostEqual(out['raw_dat_all_original_rf3_sum_n'],-10)
        self.assertAlmostEqual(out['final']['mpc_type_contributions']['KNOT1']['net_f3_n'],0)
        self.assertAlmostEqual(out['final']['mpc_type_contributions']['MEANROTBS']['net_f3_n'],-10)
        self.assertEqual(out['engineering_acceptance'],'NOT_ADMITTED')

    def test_negative_controls(self):
        cases=[
           (P+Q.replace('KB_MPC 1 KNOT1 5','KB_MPC 1 KNOT1 nan'),DAT,'NONFINITE'),
           (P+Q.replace('KB_FN Q 1 3 -1 5','KB_FN Q 1 3 -1 8'),DAT,'REPLAY_OUTPUT'),
           (P+Q.replace('KB_MPC 2 MEANROTBS -7','KB_MPC 2 MEANROTBS -6'),DAT,'MULTIPLIER'),
           (P+Q.replace('KB_TERM 1 1 1 3 1\n',''),DAT,'TERM_COVERAGE'),
           (P+Q.replace('KB_TERM 1 2 2 3 2','KB_TERM 1 1 2 3 2'),DAT,'TERM_DUP'),
           (P+Q.replace('KB_EVENT Q 1 1 1 3 4 2','KB_EVENT Q 1 2 1 3 4 2'),DAT,'PAIR'),
           (P+Q.replace('KB_MPC 1 KNOT1 5','KB_MPC 1 KNOT1 5\nKB_MPC 1 KNOT1 5'),DAT,'MPC_COVERAGE'),
           (P+Q,DAT.replace(' 3 0 0 -8',' 3 0 0 0'),'ORIGINAL_RF_PROJECTION'),
           (P+Q,'', 'DAT_NO_ORIGINAL_RF'),
           (P+Q.replace('KB_TERM 2 1 2 3 1','KB_TERM 2 1 2 3 0'),DAT,'TERM_COVERAGE'),
        ]
        for data,dat,code in cases:
            with self.subTest(code=code):
                with self.assertRaisesRegex(ValueError,'CCX221_MPC_RESTORE_'+code):audit(data,dat)

if __name__=='__main__':unittest.main()
