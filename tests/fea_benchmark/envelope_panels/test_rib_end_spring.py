"""Stage 61 bounded SPRING1 input, signed energy and fail-closed checks."""
import math
import tempfile
import unittest
from pathlib import Path

from check_rib_end_spring import (
    MESHES, STIFFNESS_PER_NODE_N_MM, assess, generate, make_deck,
)

class RibEndSpringTests(unittest.TestCase):
    def test_deck_identity_and_16_springs(self):
        for n in MESHES:
            for k in STIFFNESS_PER_NODE_N_MM:
                with self.subTest(n=n,k=k):
                    deck,web_nodes,end_nodes,web=make_deck(n,k)
                    self.assertEqual(len(end_nodes),16)
                    self.assertEqual(len(web),n*n)
                    self.assertTrue(web_nodes.isdisjoint(end_nodes))
                    self.assertIn("*ELEMENT,TYPE=SPRING1,ELSET=RIB_END_Z_SPRING\n",deck)
                    self.assertIn("*SPRING,ELSET=RIB_END_Z_SPRING\n3\n"+f"{float(k):.1f}\n",deck)
                    self.assertEqual(deck.count("*DLOAD\nWEB,P,0.0001"),1)
                    self.assertEqual(deck.count("ROOT,1,6,0."),1)
                    self.assertNotIn("RIB_END,1,6,0.",deck)
                    self.assertNotIn("*CLOAD",deck)
                    self.assertNotIn("*PLASTIC",deck)
                    spring_block=deck.split("*ELEMENT,TYPE=SPRING1,ELSET=RIB_END_Z_SPRING\n",1)[1]
                    spring_block=spring_block.split("*MATERIAL",1)[0]
                    lines=spring_block.splitlines()
                    self.assertEqual(len(lines),16)
                    self.assertEqual({int(x.split(",")[1]) for x in lines},end_nodes)
                    self.assertEqual(len({int(x.split(",")[0]) for x in lines}),16)
                    with tempfile.TemporaryDirectory() as t:
                        path=Path(t)/"case"
                        generate(path,n,k)
                        self.assertEqual((path/"panel.inp").read_text(),deck)
                        with self.assertRaisesRegex(ValueError,"WORKSPACE_MUST_BE_NEW"):
                            generate(path,n,k)

    def test_linear_oracle_regression(self):
        vals={(8,0):4.00e-5,(8,1000):3.90e-5,(8,10000):3.10e-5,
              (16,0):4.05e-5,(16,1000):3.95e-5,(16,10000):3.15e-5}
        r=assess(vals)
        self.assertEqual(r["engineering_acceptance"],"NOT_ADMITTED")
        self.assertEqual(r["rotational_stiffness"],"NOT_MODELED")
        self.assertEqual(r["global_six_component_balance"],"NOT_ADMITTED")
        for mutation,needle in [
            ({(16,10000):4e-5},"COMPLIANCE_NOT_MONOTONIC"),
            ({(8,10000):1e-5},"MESH_DIFFERENCE_EXCESSIVE"),
            ({(8,1000):float("nan")},"MATRIX_INVALID")]:
            changed={**vals,**mutation}
            with self.subTest(mutation=mutation),self.assertRaisesRegex(ValueError,needle):
                assess(changed)

    def test_invalid_scope(self):
        for n,k in ((4,1000),(16,0),(16,2000),(True,10000),(8,1000.0)):
            with self.subTest(n=n,k=k),self.assertRaises(ValueError):
                make_deck(n,k)

if __name__=="__main__":
    unittest.main()
