"""Analytic force-couple, coordinate change and negative CCX print controls."""
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
from verify_ccx221_contact_moment import couple_oracle,cross,parse_dat,geometric_audit,verify_files

BLOCK='''statistics for slave set RIB_BASE_UNDERSIDE, master set PLATE_TOP and time  0.1000000E+01

   total surface force (fx,fy,fz) and moment about the origin (mx,my,mz)

    1.223131E-04 -3.796829E-05  1.440875E+01 -2.488363E-01 -8.644839E+03 -1.648774E-02

   center of gravity and mean normal

    5.996268E+02  8.052388E-01  1.519682E+00  1.091918E-05 -3.844319E-06 -1.000000E+00

   moment about the center of gravity(mx,my,mz)

   -1.185138E+01 -4.966360E+00  6.377556E-03
'''

class MomentTests(unittest.TestCase):
    def bad(self,t,code):
        with self.assertRaisesRegex(ValueError,"CCX221_MOMENT_"+code):
            geometric_audit(parse_dat(t)[0])
    def test_analytic_couple(self):
        v=couple_oracle()
        self.assertEqual(v["forces_net_n"],(0.,0.,0.))
        self.assertAlmostEqual(v["moment_nmm"][1],48.)
        self.assertAlmostEqual(v["moment_after_origin_shift_nmm"][1],48.)
        for x in v["virtual_work_derivatives_nmm"].values():self.assertAlmostEqual(x,48.)
    def test_arbitrary_origin_shift(self):
        r,f,o=(2.,3.,4.),(5.,-7.,11.),(19.,-21.,13.)
        a=cross(r,f);b=cross(tuple(x-y for x,y in zip(r,o)),f);c=cross(o,f)
        for i in range(3):self.assertAlmostEqual(a[i],b[i]+c[i])
    def test_repeated_records(self):
        a,n=parse_dat(BLOCK+"\n"+BLOCK)
        self.assertEqual(n,2)
        self.assertEqual(len(geometric_audit(a)["center_shift_components"]),3)
    def test_invalid_origin_moment(self):
        self.bad((BLOCK+BLOCK).replace("-8.644839E+03","-8.600000E+03"),"MOMENT_ORIGIN_TRANSFORM")
    def test_invalid_center_moment(self):
        self.bad((BLOCK+BLOCK).replace("-4.966360E+00","-5.966360E+00"),"MOMENT_ORIGIN_TRANSFORM")
    def test_duplicate_drift(self):
        self.bad(BLOCK+BLOCK.replace("-4.966360E+00","-5.966360E+00"),"DUPLICATE_FINAL_STATISTICS_INCONSISTENT")
    def test_absence(self):
        self.bad("unknown\n","NO_CONTACT_STATISTICS")
    def test_nonfinite(self):
        self.bad((BLOCK+BLOCK).replace("1.440875E+01","NaN"),"ROW_FORMAT")
    def test_precision(self):
        self.bad((BLOCK+BLOCK).replace("1.440875E+01","1.44E+01"),"ROW_FORMAT")
    def test_missing_cg(self):
        self.bad((BLOCK+BLOCK).replace("center of gravity and mean normal","missing"),"HEADER_MISSING")
    def test_invalid_oracle_input(self):
        with self.assertRaisesRegex(ValueError,"CCX221_MOMENT_BAD_COUPLE_INPUT"):couple_oracle(a_mm=0)
    def test_artifact_pin(self):
        with self.assertRaisesRegex(ValueError,"CCX221_MOMENT_DAT_PROVENANCE"):
            verify_files({8:Path(__file__),16:Path(__file__)})

if __name__=="__main__":unittest.main()
