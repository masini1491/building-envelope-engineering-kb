"""Fail-closed isolated plate-and-rib thickness research tests."""
import math
import tempfile
import unittest
from pathlib import Path
from check_rib_thickness_sweep import build, generate, assess, THICKNESSES, NODES_MESH, RIB_HEIGHTS
from check_center_rib_plate import build as original, A, B, E, NU, P
from check_aluminum_ritz import ritz_center_mm

def fixture():
    data={}
    for t in THICKNESSES:
        ref=ritz_center_mm(dict(width_mm=A,height_mm=B,thickness_mm=t,
             youngs_modulus_mpa=E,poisson_ratio=NU,pressure_n_mm2=P))
        for n in NODES_MESH:
            for h,factor in ((0,1.),(4,.77),(8,.49)):
                data[t,n,h]=ref*(.94 if n==8 else .97)*factor
    return data

class Tests(unittest.TestCase):
    def test_preserves_controls(self):
        for n in NODES_MESH:
            for h in RIB_HEIGHTS:
                self.assertEqual(build(n,h,2.0),original(n,h)[0])
    def test_sections_and_geometry(self):
        for n in NODES_MESH:
            for h in RIB_HEIGHTS:
                source=build(n,h,2.0)
                revised=build(n,h,3.0)
                self.assertEqual(revised.count('SYNTHETIC_ELASTIC\n3.0\n'),2 if h else 1)
                self.assertEqual(source.count('SYNTHETIC_ELASTIC\n2.0\n'),2 if h else 1)
                self.assertEqual(revised.count('WEB,P,0.0001'),1)
                self.assertIn('ROOT,1,6,0.',revised)
                self.assertNotIn('*EQUATION',revised)
                self.assertNotIn('*PLASTIC',revised)
    def test_fresh_generation(self):
        with tempfile.TemporaryDirectory() as root:
            folder=Path(root)/'case'
            generate(folder,8,4,3.0)
            self.assertEqual((folder/'panel.inp').read_text(),build(8,4,3.0))
            with self.assertRaisesRegex(ValueError,'MUST_BE_NEW'):generate(folder,8,4,3.)
            with self.assertRaisesRegex(ValueError,'CONTROL_GENERATION'):
                generate(Path(root)/'control',8,4,2.)
    def test_bad_parameters(self):
        for n,h,t in ((4,4,3.),(8,12,3.),(True,4,3.),(8,4,True),(8,4,2.5),(8,4,float('nan'))):
            with self.subTest(n=n,h=h,t=t),self.assertRaises(ValueError):build(n,h,t)
    def test_oracle_and_boundaries(self):
        x=assess(fixture())
        self.assertEqual(x['engineering_acceptance'],'NOT_ADMITTED')
        self.assertEqual(x['rigid_rotation_or_fastener_force'],'NOT_ADMITTED')
        self.assertAlmostEqual(x['flat_plate_Kirchhoff_t_cubed_ratio'],8/27)
    def test_bad_physics(self):
        x=fixture()
        cases=({**x,(3.,16,8):math.nan},
               {**x,(3.,16,8):x[3.,16,4]*1.02},
               {**x,(3.,16,4):x[2.,16,4]*1.02},
               {**x,(3.,8,8):x[3.,16,8]*2},
               {**x,(3.,16,0):x[3.,16,0]*1.5})
        for case in cases:
            with self.assertRaises(ValueError):assess(case)

if __name__=='__main__':unittest.main()
