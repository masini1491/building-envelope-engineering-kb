"""Negative controls for S8R contact observation, not a physical PASS oracle."""
import tempfile,unittest
from pathlib import Path
from check_u_rib_contact_observations import observe_dat,contact_print,observe
RF="""forces (fx,fy,fz) for set PLATE_EDGE_RF and time 0.1000000E+01

 1 0. 0. -10.

 forces (fx,fy,fz) for set RIB_END_RF and time 0.1000000E+01

 2 0. 0. -20.

 forces (fx,fy,fz) for set CENTER_RF and time 0.1000000E+01

 3 0. 0. 30.
"""
CONTACT="""statistics for slave set RIB_BASE_UNDERSIDE, master set PLATE_TOP and time 0.1000000E+01

 total surface force (fx,fy,fz) and moment about the origin (mx,my,mz)

 0. 0. 10. 0. -2000. 0.

 center of gravity and mean normal

 200. 0. 1.5 0. 0. -1.

 moment about the center of gravity(mx,my,mz)

 0. 0. 0.

 area,  normal force (+ = tension) and shear force (size)

 34. -10. 0.
"""
class ObservationsTests(unittest.TestCase):
    def test_raw_not_admitted(self):
        data=observe_dat(RF+CONTACT,"toward")
        self.assertEqual(data["raw_rf3_sum_n"],0.)
        self.assertEqual(data["contact_print"]["contact_area_mm2"],34.)
        self.assertEqual(data["contact_print"]["slave_total_force_n"][2],10.)
        self.assertEqual(data["raw_rf_is_complete_mpc_balance"],"UNPROVEN")
        self.assertEqual(data["engineering_acceptance"],"NOT_ADMITTED")
    def test_unlinked(self):
        self.assertIsNone(observe_dat(RF,"unlinked")["contact_print"])
        with self.assertRaises(ValueError):observe_dat(RF+CONTACT,"unlinked")
    def test_reject_bad_time_missing_surface_nonfinite(self):
        with self.assertRaises(ValueError):observe_dat(RF,"toward")
        with self.assertRaises(ValueError):observe_dat(RF.replace("0.1000000E+01","0.5000000E+00"),"unlinked")
        with self.assertRaises(ValueError):contact_print(CONTACT.replace("34. -10.","-34. -10."))
        with self.assertRaises(ValueError):observe_dat(RF.replace("30.","NaN"),"unlinked")
    def test_reject_duplicate_nodes(self):
        duplicated=RF.replace("3 0. 0. 30.","3 0. 0. 30.\n 3 0. 0. 30.")
        with self.assertRaises(ValueError):observe_dat(duplicated,"unlinked")
    def test_fortran_number_and_unknown_case(self):
        value=observe_dat(RF.replace("30.","3.000000+01"),"unlinked")
        self.assertEqual(value["raw_rf3_sum_n"],0.)
        with self.assertRaises(ValueError):observe_dat(RF,"other")
    def test_require_real_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):observe(Path(d))
if __name__=="__main__":unittest.main()
