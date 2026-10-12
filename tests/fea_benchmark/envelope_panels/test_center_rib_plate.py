"""Bounded regression for centered synthetic shell rib; never a capacity check."""
import math
import tempfile
import unittest
from pathlib import Path

from check_center_rib_plate import (
    A, B, E, NU, P, T, NODES_MESH, RIB_HEIGHTS,
    assess, build, generate, independent_ritz,
)


class CenterRibStudyTests(unittest.TestCase):
    def test_independent_energy_reference(self):
        refs = [independent_ritz(h) for h in RIB_HEIGHTS]
        self.assertAlmostEqual(refs[0]["flat_ritz_center_mm"],
                               0.00025749110714824876, places=13)
        self.assertTrue(refs[0]["plate_plus_rib_energy_center_mm"] >
                        refs[1]["plate_plus_rib_energy_center_mm"] >
                        refs[2]["plate_plus_rib_energy_center_mm"])
        self.assertEqual(refs[0]["rib_only_synthetic_iy_mm4"], 0.0)
        self.assertAlmostEqual(refs[1]["rib_only_synthetic_iy_mm4"],
                               2.0 * 4**3 / 3, places=12)
        self.assertEqual(refs[2]["engineering_acceptance"], "NOT_ADMITTED")
        self.assertEqual(refs[2]["exact_folded_or_stiffened_shell_field"],
                         "NOT_ESTABLISHED")

    def test_web_shell_load_and_rib_geometry(self):
        for n in NODES_MESH:
            for height in RIB_HEIGHTS:
                with self.subTest(mesh=n, height=height):
                    deck, center, root, counts = build(n, height)
                    self.assertEqual(counts["web"], n*n)
                    self.assertEqual(counts["rib"], 4*n if height else 0)
                    self.assertEqual(len(root), 8*n)
                    self.assertNotIn(center, root)
                    self.assertEqual(deck.count("*DLOAD\nWEB,P,0.0001"), 1)
                    self.assertEqual(deck.count("*STEP,NLGEOM"), 1)
                    self.assertEqual(deck.count("*MATERIAL,NAME=SYNTHETIC_ELASTIC"), 1)
                    self.assertIn("ROOT,1,6,0.", deck)
                    self.assertNotIn("*CLOAD", deck)
                    self.assertNotIn("*PLASTIC", deck)
                    self.assertNotIn("*INCLUDE", deck)
                    self.assertEqual(deck.count("*ELEMENT,TYPE=S8R,ELSET=WEB"), 1)
                    self.assertEqual(deck.count("*ELEMENT,TYPE=S8R,ELSET=RIB"),
                                     1 if height else 0)
                    nodes = deck.split("*NODE\n")[1].split("*ELEMENT", 1)[0].splitlines()
                    coords = {
                        int(parts[0]): tuple(float(x) for x in parts[1:])
                        for line in nodes if (parts := line.split(","))
                    }
                    seam_nodes = [
                        nid for nid, (_, y, z) in coords.items()
                        if abs(y - B/2) < 1e-9 and abs(z) < 1e-9
                    ]
                    self.assertEqual(len(seam_nodes), 2*n+1)
                    self.assertEqual(max(x[2] for x in coords.values()), float(height))
                    if height:
                        rib_block = deck.split("*ELEMENT,TYPE=S8R,ELSET=RIB\n",1)[1]
                        rib_block = rib_block.split("*MATERIAL",1)[0]
                        used = {int(k) for line in rib_block.splitlines()
                                for k in line.split(",")[1:]}
                        self.assertTrue(set(seam_nodes).issubset(used))
                    with tempfile.TemporaryDirectory() as d:
                        p = Path(d)/"candidate"
                        generate(p,n,height)
                        self.assertEqual((p/"panel.inp").read_text(),deck)
                        with self.assertRaisesRegex(ValueError,"WORKSPACE_MUST_BE_NEW"):
                            generate(p,n,height)

    def test_assess_requires_stiffness_order_without_design_escalation(self):
        baseline=independent_ritz(0)["flat_ritz_center_mm"]
        data={(8,0):.91*baseline,(8,4):.72*baseline,(8,8):.45*baseline,
              (16,0):.95*baseline,(16,4):.74*baseline,(16,8):.46*baseline}
        result=assess(data)
        self.assertTrue(result["rib_stiffness_order_observed"])
        self.assertEqual(result["engineering_acceptance"],"NOT_ADMITTED")
        self.assertEqual(result["independent_stiffener_field_oracle"],
                         "NOT_ESTABLISHED")
        other={**data,(16,8):data[16,4]*1.01}
        with self.assertRaisesRegex(ValueError,"RIB_STIFFNESS_ORDER_NOT_OBSERVED"):
            assess(other)
        with self.assertRaisesRegex(ValueError,"RIB_STUDY_OBSERVATION_MATRIX_INVALID"):
            assess({**data,(16,4):math.nan})
        with self.assertRaisesRegex(ValueError,"RIB_TWO_MESH_DIFFERENCE_TOO_LARGE"):
            assess({**data,(8,8):.24*baseline})

    def test_reject_unadmitted_mesh_height(self):
        for n,h in ((4,4),(16,12),(True,8),(8,-1)):
            with self.subTest(mesh=n,height=h),self.assertRaises(ValueError):
                build(n,h)
        with self.assertRaises(ValueError):
            independent_ritz(5)


if __name__ == "__main__":
    unittest.main()
