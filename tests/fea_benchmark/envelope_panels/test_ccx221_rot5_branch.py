"""Negative controls for observed DOF5 contact-resultant replay."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from verify_ccx221_rot5_branch import final_contact,replay
P="statistics for slave set RIB_BASE_UNDERSIDE, master set PLATE_TOP and time 0.1000000E+01\n"
R="total surface force (fx,fy,fz) and moment about the origin (mx,my,mz)\n\n1 2 3 4 5 6\n"
class Tests(unittest.TestCase):
    def test_valid_pair(self):
        self.assertEqual(final_contact(P+R+P+R)[2],3)
    def test_missing_pair(self):
        with self.assertRaisesRegex(ValueError,"FINAL_DUPLICATE_COVERAGE"):final_contact(P+R)
    def test_bad_dimension(self):
        with self.assertRaisesRegex(ValueError,"FORCE_DIMENSION"):final_contact(P+R.replace("1 2 3 4 5 6","1 2 3 4 5")+P+R)
    def test_nan(self):
        with self.assertRaisesRegex(ValueError,"NONFINITE"):final_contact(P+R.replace("1 2 3 4 5 6","1 2 nan 4 5 6")+P+R)
    def test_duplicate_drift(self):
        with self.assertRaisesRegex(ValueError,"FINAL_DUPLICATE_DRIFT"):final_contact(P+R+P+R.replace("1 2 3 4 5 6","1 2 4 4 5 6"))
    def test_absent_artifact(self):
        with self.assertRaises(FileNotFoundError):replay(Path("/does/not/exist"))
if __name__=="__main__":unittest.main()
