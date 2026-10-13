"""Stage 68 force output-scope and analytic boundary tests."""
import tempfile
import unittest
from pathlib import Path
from check_spring_rf_observation import (
    CASES,P,K,EXPECTED_U2,SUPPORT_LOAD,deck,generate,_near,crosscheck,field
)
class SpringRFTests(unittest.TestCase):
    def test_analytic_load_deflection(self):
        self.assertAlmostEqual(EXPECTED_U2,.005)
        self.assertAlmostEqual(K*EXPECTED_U2,P)
    def test_isolated_decks(self):
        for c in CASES:
            s=deck(c)
            self.assertEqual(s.count("*ELEMENT,TYPE=SPRING2"),1)
            self.assertEqual(s.count("*NODE PRINT"),2)
            self.assertNotIn("*RIGID BODY",s)
            self.assertNotIn("*EQUATION",s)
            self.assertEqual(s.count("*CLOAD"),1)
            with tempfile.TemporaryDirectory() as t:
                d=Path(t)/"fixture"
                generate(d,c)
                self.assertEqual((d/"panel.inp").read_text(),s)
                with self.assertRaises(ValueError):generate(d,c)
    def test_scope_gate(self):
        with self.assertRaises(ValueError):deck("rotational")
        with self.assertRaises(ValueError):field(Path("unused"),"stress","FIXED")
    def test_external_force_decomposition(self):
        a={"observed_fixed_rf3_n":-P,"observed_loaded_rf3_n":P,
           "observed_uz2_mm":EXPECTED_U2,"inferred_mechanical_fixed_reaction_n":-P}
        b={**a,"inferred_mechanical_fixed_reaction_n":-P-SUPPORT_LOAD["loaded_spc"]}
        result=crosscheck({"clean_spc":a,"loaded_spc":b})
        self.assertEqual(result["mpc_reaction"],"NOT_ADMITTED_NOT_TESTED")
        with self.assertRaisesRegex(ValueError,"CONTAMINATION"):
            crosscheck({"clean_spc":a,"loaded_spc":a})
    def test_failclosed_field_parser(self):
        with tempfile.TemporaryDirectory() as t:
            file=Path(t)/"out.dat"
            file.write_text("forces (fx,fy,fz) for set FIXED and time 1.000000E+00\n\n 1 0. 0. -1.25\n\n")
            self.assertAlmostEqual(field(file,"forces","FIXED")[1][2],-P)
            with self.assertRaisesRegex(ValueError,"FIELD_NOT_FOUND"):
                field(file,"forces","LOADED")
if __name__=="__main__":
    unittest.main()
