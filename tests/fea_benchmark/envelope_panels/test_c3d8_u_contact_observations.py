"""Scope / negative input checks for C3D8 control."""
import tempfile,unittest
from pathlib import Path
from check_c3d8_u_contact_observations import evaluate,observe
class SolidObservations(unittest.TestCase):
    def test_requires_real_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):observe(d)
    def test_out_of_scope(self):
        with tempfile.TemporaryDirectory() as d:
            for n,c in ((4,"toward"),(8,"unknown"),(True,"away")):
                with self.assertRaises(ValueError):evaluate(d,n,c)
if __name__=="__main__":unittest.main()
