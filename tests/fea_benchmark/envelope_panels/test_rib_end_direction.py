"""Stage 62 translational directional spring identity and limits."""
import math
import tempfile
import unittest
from pathlib import Path

from check_rib_end_direction import MESHES,DIRECTIONS,K_PER_NODE,make_deck,generate,assess
from check_rib_end_spring import make_deck as stage61_make_deck


class DirectionalSpringTests(unittest.TestCase):
    def test_only_direction_and_label_change(self):
        for n in MESHES:
            base,base_web,base_end,base_el=stage61_make_deck(n,K_PER_NODE)
            for dof in DIRECTIONS:
                with self.subTest(n=n,dof=dof):
                    actual,web,end,elements=make_deck(n,dof)
                    self.assertEqual(web,base_web)
                    self.assertEqual(end,base_end)
                    self.assertEqual(elements,base_el)
                    self.assertEqual(len(end),16)
                    self.assertIn(f"*SPRING,ELSET=RIB_END_{'X' if dof==1 else 'Y'}_SPRING\n{dof}\n10000.0\n",actual)
                    self.assertNotIn("RIB_END_Z_SPRING",actual)
                    self.assertIn("*DLOAD\nWEB,P,0.0001",actual)
                    self.assertNotIn("RIB_END,1,6,0.",actual)
                    self.assertNotIn("*CLOAD",actual)
                    self.assertNotIn("*PLASTIC",actual)
                    with tempfile.TemporaryDirectory() as d:
                        p=Path(d)/"fixture"
                        generate(p,n,dof)
                        self.assertEqual((p/"panel.inp").read_text(),actual)
                        with self.assertRaisesRegex(ValueError,"DESTINATION_MUST_BE_NEW"):
                            generate(p,n,dof)

    def test_tie_aware_screen(self):
        x={(8,0):4e-5,(8,1):4e-5,(8,2):4e-5,(8,3):3.95e-5,
           (16,0):4.05e-5,(16,1):4.049e-5,(16,2):4.05e-5,(16,3):4e-5}
        r=assess(x)
        self.assertEqual(r["rotational_support_stiffness"],"NOT_MODELED")
        self.assertEqual(r["engineering_acceptance"],"NOT_ADMITTED")
        self.assertEqual(r["relative_directional_effects"]["8"]["Y"]["signed_relative_effect"],0)
        with self.assertRaisesRegex(ValueError,"COMPLIANCE_INCREASE"):
            assess({**x,(16,1):4.2e-5})
        with self.assertRaisesRegex(ValueError,"KNOWN_Z_CONTROL"):
            assess({**x,(16,3):4.06e-5})
        with self.assertRaisesRegex(ValueError,"MESH_CHANGE_TOO_LARGE"):
            assess({**x,(8,2):2.0e-5})
        with self.assertRaisesRegex(ValueError,"MATRIX_INVALID"):
            assess({**x,(16,2):float("nan")})

    def test_reject_nontranslational_stiffness(self):
        for n,dof in ((4,1),(16,3),(16,4),(16,0),(True,2),(8,2.0)):
            with self.subTest(n=n,dof=dof),self.assertRaises(ValueError):
                make_deck(n,dof)


if __name__=="__main__":
    unittest.main()
