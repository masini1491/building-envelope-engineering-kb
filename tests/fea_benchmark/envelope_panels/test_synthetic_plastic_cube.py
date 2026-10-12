"""Synthetic C3D8 constitutive interface negative-path regression."""
import math
import tempfile
import unittest
from pathlib import Path
from synthetic_plastic_cube import analytic, deck, _values, parse, check

class SyntheticPlasticTests(unittest.TestCase):
    def test_exact_yield_branches(self):
        a, b = analytic("elastic"), analytic("plastic")
        self.assertEqual(a["stress_mpa"], 56)
        self.assertEqual(a["peeq"], 0.)
        self.assertAlmostEqual(b["peeq"], (70000*.004-100)/(70000+1000))
        self.assertAlmostEqual(b["stress_mpa"], 100+1000*b["peeq"])
        self.assertLess(b["stress_mpa"], 70000*.004)

    def test_no_aluminum_material_constants(self):
        for case in ("elastic", "plastic"):
            s = deck(case)
            self.assertIn("ARTIFICIAL_BILINEAR", s)
            self.assertIn("*PLASTIC,HARDENING=ISOTROPIC", s)
            self.assertIn("*EL FILE\nS,PEEQ,NOE", s)
            self.assertNotIn("3003", s)
            self.assertNotIn("3004", s)
        with self.assertRaises(ValueError):deck("3004-O")

    def test_invalid_nodal_output_rejected(self):
        row=lambda node,val: " -1"+f"{node:10d}"+"".join(f"{v:12.5E}" for v in val)
        self.assertEqual(_values(row(1,[1.]*6),6)[0],1)
        for invalid in (row(9,[1.]*6),row(1,[math.nan]*6)," -1 1 2 3"):
            with self.assertRaises(ValueError):_values(invalid,6)

    def test_ccx_221_pe_descriptor_is_not_literally_peeq(self):
        # Exact observed CCX 2.21 descriptor: *EL FILE PEEQ -> -4 PE, -5 PE.
        self.assertIn("*EL FILE\nS,PEEQ,NOE", deck("plastic"))
        import inspect
        import synthetic_plastic_cube
        self.assertIn('tuple(labels) != ("PE",)', inspect.getsource(synthetic_plastic_cube.parse))

    def test_missing_and_malformed_frd_rejected(self):
        with tempfile.TemporaryDirectory() as p:
            path=Path(p)/"cube.frd"
            with self.assertRaises(ValueError):parse(path)
            path.write_text("invalid")
            with self.assertRaises(ValueError):parse(path)

    def test_no_solver_result_cannot_claim_pass(self):
        with tempfile.TemporaryDirectory() as p:
            root=Path(p)
            (root/"cube.inp").write_text(deck("plastic"))
            with self.assertRaises(ValueError):check("plastic",root)

if __name__=="__main__":unittest.main()
