"""Synthetic S8R input scope and negative tests; not solver substitution."""
import unittest,tempfile
from pathlib import Path
from check_s8r_normal_contact import CASES,MESHES,deck,topology,generate,check
class S8RContactTests(unittest.TestCase):
    def test_decks(self):
        for n in MESHES:
            for c in CASES:
                with self.subTest(n=n,c=c):
                    s=deck(n,c)
                    self.assertEqual(s.count("*ELEMENT,TYPE=S8R"),2)
                    self.assertEqual(s.count("*CONTACT PAIR"),int(c!="disconnected"))
                    self.assertNotIn("*PLASTIC",s)
                    self.assertNotIn("SPRING2",s)
                    self.assertNotIn("*FRICTION",s)
                    if c!="disconnected":
                        self.assertIn("SPOS",s);self.assertIn("SNEG",s)
    def test_disjoint_geometry(self):
        for n in MESHES:
            coordinates,bodies=topology(n)
            self.assertEqual(len(bodies[0][2]),n*n)
            self.assertEqual(len(bodies[1][2]),n*n)
            self.assertFalse(set(bodies[0][1])&set(bodies[1][1]))
    def test_fail_closed_inputs(self):
        for n in (0,3,True,1.0):
            with self.assertRaises(ValueError):topology(n)
        with self.assertRaises(ValueError):deck(1,"other")
    def test_generation_guard(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"sample";generate(p,1,"approach")
            self.assertEqual((p/"panel.inp").read_text(),deck(1,"approach"))
            with self.assertRaises(ValueError):generate(p,1,"opening")
    def test_missing_solver_results_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):check(td)
if __name__=="__main__":unittest.main()
