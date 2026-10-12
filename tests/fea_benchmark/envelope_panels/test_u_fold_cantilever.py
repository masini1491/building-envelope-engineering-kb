"""Independent synthetic section values and fail-closed U-fold fixture checks."""
import math
import tempfile
import unittest
from pathlib import Path
from check_u_fold_cantilever import build,beam_reference,generate,assess,_dat_vectors,_outline,L,B,FLANGE,FORCE

class TestUFold(unittest.TestCase):
    def test_reference_section_and_tip(self):
        r=beam_reference()
        self.assertAlmostEqual(r["neutral_axis_z_mm"],5.0,places=12)
        self.assertAlmostEqual(r["mid_surface_iy_mm4"],5000.,places=8)
        self.assertAlmostEqual(r["cantilever_tip_deflection_mm"],
                               0.02608695652173913,places=11)
        self.assertEqual(r["root_bending_moment_demand_n_mm"],FORCE*L)

    def test_u_profile_corner_geometry(self):
        self.assertEqual(_outline(0),(-B/2,FLANGE))
        self.assertEqual(_outline(8),(-B/2,0.0))
        self.assertEqual(_outline(24),(0.0,0.0))
        self.assertEqual(_outline(40),(B/2,0.0))
        self.assertEqual(_outline(48),(B/2,FLANGE))

    def test_exact_mesh_and_load_closure(self):
        for n in (8,16):
            deck,weights,root,tip=build(n)
            self.assertEqual(len(weights),33)
            self.assertEqual(len(root),33)
            self.assertEqual(len(tip),33)
            self.assertAlmostEqual(sum(weights.values()),FORCE,places=12)
            self.assertEqual(deck.count("*ELEMENT,TYPE=S8R,ELSET=FOLD"),1)
            self.assertEqual(deck.count("ROOT,1,6,0."),1)
            self.assertIn("*STEP,NLGEOM",deck)
            self.assertNotIn("*PLASTIC",deck)
            self.assertNotIn("*INCLUDE",deck)
            with tempfile.TemporaryDirectory() as d:
                target=Path(d)/"case"
                generate(target,n)
                self.assertEqual((target/"panel.inp").read_text(),deck)
                with self.assertRaisesRegex(ValueError,"WORKSPACE_MUST_BE_NEW"):
                    generate(target,n)

    def test_observed_gate(self):
        w=beam_reference()["cantilever_tip_deflection_mm"]
        good=assess({8:1.07*w,16:1.03*w})
        self.assertEqual(good["engineering_acceptance"],"NOT_ADMITTED")
        for case in ({8:.6*w,16:1.3*w},{8:w,16:math.inf},
                     {8:w,16:0.},{8:w},{8:w,16:True}):
            with self.subTest(case=case),self.assertRaises(ValueError):
                assess(case)

    def test_dat_field_requires_matching_nodes(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"panel.dat"
            p.write_text("displacements (vx,vy,vz) for set TIP and time 1.000000E+00\n"
                         " 101 0 0 -1.25E-02\n 102 0 0 -1.25E-02\n\n")
            self.assertEqual(set(_dat_vectors(p,"TIP","U")),{101,102})
            with self.assertRaisesRegex(ValueError,"MISSING"):
                _dat_vectors(p,"ROOT","RF")

if __name__=="__main__":
    unittest.main()
