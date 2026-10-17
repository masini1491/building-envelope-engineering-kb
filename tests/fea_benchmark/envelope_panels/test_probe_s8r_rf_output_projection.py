"""Output-only A/B contract; does not simulate CalculiX execution."""
import tempfile,unittest
from pathlib import Path
from probe_s8r_rf_output_projection import deck,generate,observe
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
if __name__=="__main__":unittest.main()
