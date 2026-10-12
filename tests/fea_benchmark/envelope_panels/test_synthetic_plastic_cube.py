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

    def test_partial_unload_oracle_and_both_step_decks(self):
        from synthetic_plastic_cube import E, CASES
        peak = analytic("plastic")
        final = analytic("unload")
        self.assertAlmostEqual(peak["peeq"], final["peeq"])
        self.assertAlmostEqual(final["stress_mpa"], peak["stress_mpa"]
                               - E*(CASES["plastic"]-CASES["unload"]))
        self.assertGreater(final["stress_mpa"], 0.)
        self.assertEqual(deck("unload").count("*STEP"), 2)
        self.assertEqual(deck("unload").count("*EL FILE"), 2)
        self.assertIn("RIGHT,1,1,0.00400000", deck("unload"))
        self.assertIn("RIGHT,1,1,0.00300000", deck("unload"))

    def test_parser_selects_exact_step_time_and_rejects_missing_step(self):
        from synthetic_plastic_cube import STRESS_LABELS, NODES
        def row(node, vec):
            return " -1" + f"{node:10d}" + "".join(f"{x:12.5E}" for x in vec)
        def field(time, name, labels, data):
            return (["       100CL" + f"{time:12.5E}", f" -4 {name} {len(labels)}"]
                    + [f" -5 {lab}" for lab in labels]
                    + [row(n, data) for n in sorted(NODES)] + [" -3"])
        lines = []
        for time, sigma, peeq in ((1., 102.5, .0025),(2.,32.5,.0025)):
            lines += field(time, "STRESS", STRESS_LABELS, (sigma,0.,0.,0.,0.,0.))
            lines += field(time, "PE", ("PE",), (peeq,))
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"cube.frd"
            f.write_text("\n".join(lines)+"\n")
            self.assertEqual(parse(f,1.)["STRESS"][1][0],102.5)
            self.assertEqual(parse(f,2.)["STRESS"][1][0],32.5)
            with self.assertRaisesRegex(ValueError,"MISSING_OR_DUPLICATED"):
                parse(f,3.)
            f.write_text("\n".join(lines[:-11])+"\n")
            with self.assertRaises(ValueError):parse(f,2.)

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
