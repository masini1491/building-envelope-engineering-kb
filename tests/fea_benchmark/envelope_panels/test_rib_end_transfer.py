"""Bounded synthetic rib-end support and quadratic shell work checks."""
import math
import tempfile
import unittest
from pathlib import Path

from check_rib_end_transfer import (
    MESHES, SUPPORTS, assess, build, generate, pressure_work_proxy,
)


class RibEndTransferTests(unittest.TestCase):
    def test_exact_variant_pair_only_boundary_changes(self):
        for n in MESHES:
            a,web_a,tip_a,elements_a=build(n,"rib_end_free")
            b,web_b,tip_b,elements_b=build(n,"rib_end_fixed")
            self.assertEqual(web_a,web_b)
            self.assertEqual(tip_a,tip_b)
            self.assertEqual(elements_a,elements_b)
            self.assertEqual(len(tip_a),16)
            self.assertEqual(len(elements_a),n*n)
            self.assertEqual(len(web_a),3*n*n+4*n+1)
            self.assertIn("RIB_END,1,6,0.",b)
            self.assertNotIn("RIB_END,1,6,0.",a)
            for deck in (a,b):
                self.assertIn("*DLOAD\nWEB,P,0.0001",deck)
                self.assertEqual(deck.count("*NODE PRINT,NSET=WEB_NODES\nU\n"),1)
                self.assertNotIn("*CLOAD",deck)
                self.assertNotIn("*PLASTIC",deck)
                self.assertIn("*STEP,NLGEOM",deck)
                self.assertEqual(deck.count("*SHELL SECTION"),2)
            with tempfile.TemporaryDirectory() as t:
                for s in SUPPORTS:
                    f=Path(t)/s
                    generate(f,n,s)
                    self.assertEqual((f/"panel.inp").read_text(),build(n,s)[0])
                    with self.assertRaisesRegex(ValueError,"WORKSPACE_MUST_BE_NEW"):
                        generate(f,n,s)

    def test_s8r_integral_weights_for_constant_and_quadratic_fields(self):
        n=8
        _,nodes,_,web=build(n,"rib_end_free")
        constant={v:(0.,0.,.02) for v in nodes}
        self.assertAlmostEqual(pressure_work_proxy(web,constant,n),.02,places=13)
        # Node-only arbitrary values with sparse high midside fields.
        changed={i:(0.,0.,.001) for i in nodes}
        self.assertAlmostEqual(pressure_work_proxy(web,changed,n),.001,places=13)
        with self.assertRaisesRegex(ValueError,"WORK_FIELD_COVERAGE"):
            pressure_work_proxy(web,dict(list(changed.items())[1:]),n)
        with self.assertRaisesRegex(ValueError,"WORK_NONFINITE"):
            broken={**changed,next(iter(nodes)):(0.,0.,float("nan"))}
            pressure_work_proxy(web,broken,n)

    def test_compliance_oracle_is_fail_closed(self):
        good={(8,"rib_end_free"):.0030,(8,"rib_end_fixed"):.0024,
              (16,"rib_end_free"):.0031,(16,"rib_end_fixed"):.00245}
        result=assess(good)
        self.assertEqual(result["engineering_acceptance"],"NOT_ADMITTED")
        self.assertEqual(result["center_node_deflection_theorem"],"NOT_CLAIMED")
        wrong={**good,(16,"rib_end_fixed"):.0032}
        with self.assertRaisesRegex(ValueError,"DID_NOT_REDUCE"):
            assess(wrong)
        with self.assertRaisesRegex(ValueError,"MESH_CHANGE"):
            assess({**good,(8,"rib_end_fixed"):.0010})
        with self.assertRaisesRegex(ValueError,"MATRIX_INVALID"):
            assess({**good,(16,"rib_end_free"):float("nan")})

    def test_reject_invalid_scope(self):
        for n,s in ((4,"rib_end_free"),(16,"sliding"),(True,"rib_end_fixed")):
            with self.subTest(mesh=n,support=s),self.assertRaises(ValueError):
                build(n,s)


if __name__=="__main__":
    unittest.main()
