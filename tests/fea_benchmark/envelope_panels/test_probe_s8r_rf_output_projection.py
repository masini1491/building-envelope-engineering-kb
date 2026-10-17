"""Output-only A/B contract; does not simulate CalculiX execution."""
import tempfile,unittest
from pathlib import Path
from probe_s8r_rf_output_projection import deck,generate,observe,final_frd_forc
from probe_s8r_all_original_rf import deck as baseline
class ProjectionTests(unittest.TestCase):
    def test_only_node_file_rf_changes(self):
        for n in (8,16):
            old=baseline(n)
            new=deck(n)
            self.assertEqual(new.replace("*NODE FILE,OUTPUT=3D\nU,RF\n","*NODE FILE,OUTPUT=3D\nU\n"),old)
            self.assertEqual(new.count("*CONTACT PAIR"),1)
        for n in (True,0,4,8.0):
            with self.assertRaises(ValueError):deck(n)
    def test_missing_solver_artifacts_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            name=Path(d)/"u_s8r_rf_projection_n8_toward"
            generate(name,8)
            self.assertEqual((name/"panel.inp").read_bytes(),deck(8).encode())
            with self.assertRaises(ValueError):generate(name,8)
            with self.assertRaises(ValueError):observe(d)

    def test_frd_final_reported_node_force_block(self):
        base=("  100CL  110 1.00000E+00         2                     0   10           1\\n"
              " -4  FORC        4    1\\n -5  F1\\n -5  F2\\n -5  F3\\n"
              + " -1" + f"{347:10d}{0.:12.5E}{0.:12.5E}{1.5:12.5E}" + "\\n"
              + " -1" + f"{348:10d}{0.:12.5E}{0.:12.5E}{-2.5:12.5E}" + "\\n -3\\n")
        # Escape sequences above are intentionally decoded into actual FRD newlines.
        raw=base.replace(chr(92) + "n", chr(10)).encode("ascii")
        result=final_frd_forc(raw,346)
        self.assertEqual(result["frd_final_force_record_count"],2)
        self.assertAlmostEqual(result["frd_final_reported_nodes_rf3_sum_n"],-1.)
        self.assertFalse(result["frd_is_complete_solver_force_oracle"])
        with self.assertRaisesRegex(ValueError,"S8R_FRD_FORCE_NODE_ID_OR_VALUE"):
            final_frd_forc(raw.replace(b"       347",b"       346",1),346)
        with self.assertRaisesRegex(ValueError,"S8R_FRD_FORCE_STEP_INVALID"):
            final_frd_forc(raw.replace(b"1.00000E+00",b"9.00000E-01",1),346)
        with self.assertRaisesRegex(ValueError,"S8R_FRD_FORCE_RECORD_COUNT"):
            final_frd_forc(raw[:-4],346)
        # Replace the complete 12-character FRD numeric field; preserving
        # only the non-space substring shifts subsequent fixed-width columns.
        original_value=f"{1.5:12.5E}".encode("ascii")
        self.assertEqual(len(original_value),12)
        for nonfinite in (float("nan"),float("inf"),float("-inf")):
            malformed=f"{nonfinite:12.5E}".encode("ascii")
            self.assertEqual(len(malformed),12)
            with self.subTest(nonfinite=nonfinite):
                with self.assertRaisesRegex(ValueError,"S8R_FRD_FORCE_NODE_ID_OR_VALUE"):
                    final_frd_forc(raw.replace(original_value,malformed,1),346)
        with self.assertRaisesRegex(ValueError,"S8R_FRD_FORCE_NODE_ID_OR_VALUE"):
            final_frd_forc(raw.replace(f"{348:10d}".encode("ascii"),
                                       f"{347:10d}".encode("ascii"),1),346)
        with self.assertRaisesRegex(ValueError,"S8R_FRD_FORCE_RECORD_COUNT"):
            final_frd_forc(raw.replace(b"1.00000E+00         2",
                                       b"1.00000E+00         3",1),346)
        with self.assertRaisesRegex(ValueError,"S8R_FRD_FORCE_RECORD_INVALID"):
            # A short terminal F3 slice ("1.5") is parseable without a width guard.
            final_frd_forc(raw.replace(original_value+b"\n",
                                       b"        1.5\n",1),346)
        with self.assertRaisesRegex(ValueError,"S8R_FRD_FORCE_RECORD_MISSING"):
            final_frd_forc(raw.replace(b" -4  FORC",b" -4  VOID",1),346)
if __name__=="__main__":unittest.main()
