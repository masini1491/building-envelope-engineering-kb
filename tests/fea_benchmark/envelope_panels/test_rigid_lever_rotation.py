"""Stage 63 bounded algebraic oracle and input-scope tests."""
import tempfile
import unittest
from pathlib import Path
from check_rigid_lever_rotation import CASES,SPRINGS,oracle,finite_ei_theory_only,deck,generate,check

class TestStage63(unittest.TestCase):
    def test_rotation(self):
        a=oracle("rotation")
        self.assertAlmostEqual(a["reference_uz_mm"],0)
        self.assertAlmostEqual(a["slope_rad"],.0001)
        self.assertAlmostEqual(a["k2_n_mm"],1e6)
        self.assertAlmostEqual(sum(a["k_u_n"]),0)
        self.assertAlmostEqual(sum(x*f for (x,k),f in zip(SPRINGS["rotation"],a["k_u_n"])),100)
    def test_distribution(self):
        a=oracle("distribution")
        self.assertAlmostEqual(a["k0_n_per_mm"],1600)
        self.assertAlmostEqual(a["k1_n"],10000)
        self.assertAlmostEqual(a["k2_n_mm"],1100000)
        self.assertAlmostEqual(a["reference_uz_mm"],1000000/1660000000)
        self.assertAlmostEqual(a["slope_rad"],6000/1660000000)
        self.assertAlmostEqual(sum(a["k_u_n"]),1)
        self.assertAlmostEqual(sum(x*f for (x,k),f in zip(SPRINGS["distribution"],a["k_u_n"])),10)
    def test_theory_is_not_solver(self):
        a=finite_ei_theory_only()
        self.assertAlmostEqual(a["combined_tip_mm"],.014830917874396136)
        self.assertEqual(a["ccx_match"],"NOT_ADMITTED_FINITE_EI")
    def test_decks(self):
        for case in CASES:
            s=deck(case)
            self.assertEqual(s.count("*RIGID BODY"),1)
            self.assertEqual(s.count("*ELEMENT,TYPE=SPRING1"),len(SPRINGS[case]))
            self.assertEqual(s.count("*SPRING,ELSET="),len(SPRINGS[case]))
            self.assertNotIn("*PLASTIC",s)
            self.assertNotIn("*ELEMENT,TYPE=SPRING2",s)
            self.assertNotIn("*EQUATION",s)
            self.assertIn("101,1,1,0.",s)
            self.assertIn("101,3,3,0.",s)
            self.assertEqual(s.count("*STEP"),1)
    def test_fail_closed(self):
        for candidate in ("", "B31", "S8R"):
            with self.assertRaises(ValueError): deck(candidate)
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/"new"
            generate(folder,"rotation")
            with self.assertRaises(ValueError): generate(folder,"rotation")
            with self.assertRaisesRegex(ValueError,"ARTIFACT_MISSING"): check(folder,"rotation")
if __name__=="__main__":
    unittest.main()
