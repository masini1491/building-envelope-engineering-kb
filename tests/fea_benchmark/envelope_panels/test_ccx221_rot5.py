"""Bounded source-pinned DOF5 input-generation negative controls."""
import hashlib,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from generate_ccx221_rot5 import generate,PINS
from verify_ccx221_rot5 import scalar,observe
class Tests(unittest.TestCase):
    def test_negative_observations(self):
        with self.assertRaisesRegex(ValueError,'FINAL_ENERGY_MISSING'):scalar('','total internal energy for set PLATE and time')
        with self.assertRaisesRegex(ValueError,'NONFINITE'):scalar('total internal energy for set PLATE and time 1.0\n\n nan\n','total internal energy for set PLATE and time')
    def test_pinned_input_and_noncontact_scope(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);src=root/'source'
            for n in (8,16):
                x=src/f'u_s8r_rf_projection_n{n}_toward';x.mkdir(parents=True)
                # Fixture pins tested against the SHA256 of the pinned artifact.
                x.joinpath('panel.inp').write_text('not an authentic source deck')
            with self.assertRaisesRegex(ValueError,'PROVENANCE'):generate(src,root/'out')
    def test_missing_observation(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises((ValueError,FileNotFoundError)):observe(Path(d))
if __name__=='__main__':unittest.main()
