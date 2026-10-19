"""Input-only scope gate negative controls."""
import pathlib
import sys
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from verify_ccx221_rot5_load_scope import classify
BASE='''*NODE
1,0,0,0
*ELEMENT,TYPE=S8R,ELSET=P
1,1,1,1,1,1,1,1,1
*STEP
*STATIC
*BOUNDARY
1,1,1,0
*BOUNDARY
1,5,5,0
*END STEP
'''
class Scope(unittest.TestCase):
    def test_base(self):
        self.assertEqual(classify(BASE)['explicit_load_cards'],0)
    def test_comments_not_load(self):
        self.assertEqual(classify(BASE+'** *CLOAD\n')['explicit_load_cards'],0)
    def test_cload(self):
        with self.assertRaisesRegex(ValueError,'FORBIDDEN_CLOAD'):
            classify(BASE.replace('*END STEP','*CLOAD\n1,3,5\n*END STEP'))
    def test_dload(self):
        with self.assertRaisesRegex(ValueError,'FORBIDDEN_DLOAD'):
            classify(BASE.replace('*END STEP','*DLOAD\n1,P,5\n*END STEP'))
    def test_unknown_card(self):
        with self.assertRaisesRegex(ValueError,'UNRECOGNIZED'):
            classify(BASE+'*SOME FUTURE LOAD\n')
    def test_missing_step(self):
        with self.assertRaisesRegex(ValueError,'STEP_COUNT'):
            classify(BASE.replace('*STEP','**STEP'))
    def test_missing_boundary(self):
        with self.assertRaisesRegex(ValueError,'BOUNDARY_COUNT'):
            classify(BASE.replace('*BOUNDARY\n1,5,5,0\n',''))
    def test_dynamic(self):
        with self.assertRaisesRegex(ValueError,'FORBIDDEN_DYNAMIC'):
            classify(BASE.replace('*STATIC','*DYNAMIC'))
    def test_option(self):
        with self.assertRaisesRegex(ValueError,'UNSUPPORTED_OPTION'):
            classify(BASE.replace('*BOUNDARY','*BOUNDARY,AMPLITUDE=A',1))
if __name__=='__main__': unittest.main()
