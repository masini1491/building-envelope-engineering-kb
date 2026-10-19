import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
from check_ccx221_spc_ledger import validate

P=("KB_SPC_EVENT P 1 10 1.0 10 3\n"
   "KB_SPC P 1 1 1 -2 0 0\n"
   "KB_SPC_ROT_UNMAPPED P 2 1 4\n"
   "KB_SPC P 3 2 3 -4 0.02 0\n")
Q=("KB_SPC_EVENT Q 1 10 1.0 10 3\n"
   "KB_SPC Q 1 1 1 -2 0 1\n"
   "KB_SPC_ROT_UNMAPPED Q 2 1 4\n"
   "KB_SPC Q 3 2 3 -4 0.02 -1\n")
BASE=P+Q
class TestSPC(unittest.TestCase):
    def test_baseline(self):
        x=validate(BASE);self.assertEqual(x['spc_count'],3)
        self.assertEqual(x['unmapped_rotational_count'],1)
    def bad(self,s,code):
        with self.assertRaisesRegex(ValueError,code):validate(s)
    def test_negative(self):
        cases=[(BASE.replace('KB_SPC Q 1 1 1 -2 0 1','KB_SPC Q 1 1 1 -2 0 nan'),'NONFINITE'),
               (BASE.replace('KB_SPC Q 3 2 3 -4 0.02 -1\n',''),'ENTRY_COVERAGE'),
               (BASE.replace('KB_SPC Q 3 2 3 -4 0.02 -1','KB_SPC Q 1 2 3 -4 0.02 -1'),'DUPLICATE_OR_RANGE'),
               (BASE.replace('KB_SPC_ROT_UNMAPPED Q 2 1 4','KB_SPC_INVALID Q 2 1 4'),'INVALID_NODE_OR_DIRECTION'),
               (BASE.replace('KB_SPC_ROT_UNMAPPED P 2 1 4','KB_SPC P 2 1 4 -3 0 0'),'TRANSLATION_RANGE'),
               (BASE.replace('KB_SPC_ROT_UNMAPPED P 2 1 4\n',''),'ENTRY_COVERAGE'),
               (BASE.replace('KB_SPC_EVENT Q 1 10 1.0 10 3','KB_SPC_EVENT Q 1 10 0.9 10 3'),'EVENT_TIME'),
               (BASE.replace('KB_SPC Q 3 2 3 -4 0.02 -1','KB_SPC Q 3 3 3 -4 0.02 -1'),'PRE_POST_OWNER_MISMATCH'),
               (BASE+'KB_SPC Q 3 2 3 -4 0.02 -1\n','DUPLICATE_OR_RANGE'),
               (BASE.replace('KB_SPC_ROT_UNMAPPED Q 2 1 4','KB_SPC_ROT_UNMAPPED Q 2 1 8'),'ROTATION_RANGE')]
        for t,c in cases:
            with self.subTest(c=c):self.bad(t,c)
if __name__=='__main__':unittest.main()
