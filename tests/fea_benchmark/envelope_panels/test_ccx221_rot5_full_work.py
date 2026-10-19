"""MPC elimination controls; deterministic, independent of solver artifacts."""
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from verify_ccx221_rot5_full_work import parse_work,eliminate
SAMPLE="""KB_WORK_EVENT 1 10 1 5 4 1
KB_WORK_FN 1 3 -1 6
KB_WORK_MPC 1 MEANROT
KB_WORK_TERM 1 1 1 3 1
KB_WORK_TERM 1 2 4 1 -2
KB_WORK_TERM 1 3 4 2 1
KB_WORK_END
"""
CASCADE="""KB_WORK_EVENT 1 10 1 5 4 2
KB_WORK_FN 1 3 -1 6
KB_WORK_MPC 1 OTHER
KB_WORK_TERM 1 1 1 3 1
KB_WORK_TERM 1 2 2 3 -1
KB_WORK_MPC 2 MEANROT
KB_WORK_TERM 2 1 2 3 1
KB_WORK_TERM 2 2 4 1 -2
KB_WORK_TERM 2 3 4 2 1
KB_WORK_END
"""
class Tests(unittest.TestCase):
    def reject(self,txt,code):
        with self.assertRaisesRegex(ValueError,'CCX221_FULL_WORK_'+code):
            eliminate(parse_work(txt))
    def test_analytic_signed_couple(self):
        f,m=eliminate(parse_work(SAMPLE))
        self.assertEqual(m,{1:6.})
        self.assertEqual(f[(4,1)],12.)
        self.assertEqual(f[(4,2)],-6.)
    def test_cascaded_mpc(self):
        f,m=eliminate(parse_work(CASCADE))
        self.assertEqual(m,{1:6.,2:6.})
        self.assertEqual(f[(4,1)],12.)
    def test_rotational_dependent_skipped(self):
        txt=CASCADE.replace('1 5 4 2','1 5 7 2').replace('1 1 1 3 1','1 1 1 5 1').replace('1 2 2 3 -1','1 2 2 5 -1')
        f,m=eliminate(parse_work(txt))
        self.assertNotIn(1,m)
    def test_duplicate_mpc_term(self):
        self.reject(SAMPLE.replace('1 3 4 2 1','1 3 4 1 1'),'DUPLICATE_TERM')
    def test_invalid_dependent_coefficient(self):
        self.reject(SAMPLE.replace('1 1 1 3 1','1 1 1 3 0'),'INVALID_DEPENDENT_COEF')
    def test_nonfinite(self):
        self.reject(SAMPLE.replace('4 1 -2','4 1 nan'),'NONFINITE')
    def test_missing_terminator(self):
        self.reject(SAMPLE.replace('KB_WORK_END\n',''),'MPC_COVERAGE')
    def test_out_of_order_term(self):
        self.reject(SAMPLE.replace('1 2 4 1 -2','1 8 4 1 -2'),'TERM_OWNER')
    def test_extra_after_end(self):
        self.reject(SAMPLE+'KB_WORK_MPC 2 OTHER\n','RECORD_SEQUENCE')
if __name__=='__main__':unittest.main()
