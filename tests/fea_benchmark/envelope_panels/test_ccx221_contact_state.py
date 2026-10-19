"""Negative controls for exact ZIP contact CDIS/CSTR/CELS replay."""
import os, tempfile, unittest
from pathlib import Path
from check_ccx221_contact_state import analyze, final_rows, final_scalar, num, LABELS
ORIG=Path(os.environ.get("CCX221_ORIGINAL_ZIP","/mnt/data/ccx221-rot5-original20.zip"))
PRESS=Path(os.environ.get("CCX221_PRESSURE_ZIP","/mnt/data/ccx221-rot5-cdis-cstr.zip"))
class ContactState(unittest.TestCase):
    def test_real_pinned_eight_cases(self):
        r=analyze(ORIG,PRESS)
        self.assertEqual(r["count_cases"],8)
        self.assertEqual(r["engineering_acceptance"],"NOT_ADMITTED")
        self.assertEqual(r["results"]["n16/contact/plus1"]["count"],19)
        self.assertEqual(r["results"]["n16/contact/plus2"]["count"],22)
        self.assertFalse(r["results"]["n16/contact/plus2"]["original_and_new_solver_output_equal_in_checked_fields"])
        self.assertEqual(r["results"]["n16/contact/plus1"]["positive_pressure_count"],19)
        self.assertGreater(r["results"]["n16/contact/plus1"]["positive_pressure_zero_reported_energy_count"],0)
    def test_invalid_float(self):
        with self.assertRaisesRegex(ValueError,"NUMBER_FORMAT"):num("nan")
    def test_missing_final_pressure(self):
        with self.assertRaisesRegex(ValueError,"COVERAGE"):final_rows("",LABELS["pressure"])
    def test_pressure_field_missing(self):
        t=LABELS["pressure"]+" for all contact elements and time 0.1000000E+01\n\n100 1 0.2 0.0\n\n"
        with self.assertRaisesRegex(ValueError,"ROW_FIELDS"):final_rows(t,LABELS["pressure"])
    def test_invalid_energy_scalar(self):
        with self.assertRaisesRegex(ValueError,"NUMBER_FORMAT"):
            final_scalar("total contact spring energy for time 0.1000000E+01\n\nNaN\n","total contact spring energy")
    def test_artifact_sha_reject(self):
        with tempfile.TemporaryDirectory() as d:
            x=Path(d)/"fake.zip";x.write_bytes(b"not the pinned artifact")
            with self.assertRaisesRegex(ValueError,"ARTIFACT_PROVENANCE"):analyze(x,PRESS)
if __name__=="__main__":unittest.main()
