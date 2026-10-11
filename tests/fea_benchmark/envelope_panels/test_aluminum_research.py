import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from aluminum_research_input import validate,load
from run_aluminum_research import run
from generate import build

def example():
    return dict(width_mm=100.,height_mm=100.,thickness_mm=2.,
                youngs_modulus_mpa=69000.,poisson_ratio=.33,
                pressure_n_mm2=.6,mesh=4,support="four_edges_clamped",
                units="N-mm-MPa",material_provenance="explicit research-only values")

class Tests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate(example())["mesh"],4)
    def test_rejected_values(self):
        for key,val in (("mesh",True),("width_mm",10.),("pressure_n_mm2",float("nan")),
                        ("support","simply_supported"),("units","kN-m"),("material_provenance","")):
            data=example();data[key]=val
            with self.subTest(key=key),self.assertRaises(ValueError):validate(data)
    def test_bad_json_and_duplicate(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"in.json";p.write_text('{"mesh":4,"mesh":8}')
            with self.assertRaisesRegex(ValueError,"DUPLICATE_INPUT_KEY"):load(p)
            p.write_text('{"width_mm":NaN}')
            with self.assertRaises(ValueError):load(p)
    def test_parametric_generator_exact_fixture(self):
        with tempfile.TemporaryDirectory() as d:
            build("aluminum",4,"large",Path(d),research=example())
            s=(Path(d)/"panel.inp").read_text()
            self.assertIn("PLATE,P,0.6",s)
            self.assertIn("EDGE,1,6,0.",s)
            self.assertIn("synthetic aluminum clamped plate",s)
    def test_opt_in_required_and_empty_workspace(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);inp=root/"in.json";inp.write_text(json.dumps(example()))
            work=root/"run";work.mkdir()
            self.assertEqual(run(input_json=inp,workspace=work,executable="fake")["execution_status"],"NOT_EXECUTED_OPT_IN_REQUIRED")
            self.assertFalse(list(work.iterdir()))
            (work/"previous").write_text("x")
            with self.assertRaisesRegex(ValueError,"WORKSPACE_MUST_BE_EXISTING_EMPTY_DIRECTORY"):
                run(input_json=inp,workspace=work,executable="fake",execute=True)
    def test_missing_solver_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);inp=root/"in.json";inp.write_text(json.dumps(example()))
            work=root/"run";work.mkdir()
            with self.assertRaises(ValueError):
                run(input_json=inp,workspace=work,executable=str(root/"nonexistent"),execute=True)

if __name__=="__main__":unittest.main()
