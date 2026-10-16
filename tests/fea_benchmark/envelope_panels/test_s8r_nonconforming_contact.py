"""Nonconforming S8R surface contract and negative checks."""
import math,tempfile,unittest
from pathlib import Path
from check_s8r_nonconforming_contact import PAIRS,CASES,faces,deck,generate,compare,check
class NonconformingS8RTests(unittest.TestCase):
    def test_geometry(self):
        for a,b in PAIRS:
            coords,groups=faces(a,b)
            self.assertEqual(len(groups[0][2]),a*a)
            self.assertEqual(len(groups[1][2]),b*b)
            self.assertFalse(set(groups[0][1]) & set(groups[1][1]))
            self.assertNotEqual({coords[k][:2] for k in groups[0][1]}, {coords[k][:2] for k in groups[1][1]})
    def test_decks(self):
        for a,b in PAIRS:
            for case in CASES:
                s=deck(a,b,case)
                self.assertEqual(s.count("*ELEMENT,TYPE=S8R"),2)
                self.assertEqual(s.count("*CONTACT PAIR"),int(case!="disconnected"))
                self.assertNotIn("*PLASTIC",s)
                self.assertNotIn("SPRING2",s)
                self.assertNotIn("*FRICTION",s)
                self.assertTrue(all(len(row.split(","))<=16 for row in s.splitlines()))
    def test_reject_bad_pairs_and_cases(self):
        for a,b in ((1,1),(2,2),(3,1),(True,2),(1,2.0)):
            with self.assertRaises(ValueError):faces(a,b)
        with self.assertRaises(ValueError):deck(1,2,"fake")
    def test_reject_invalid_results(self):
        good={(p,c):{"lower_rf3_n":(3.91 if c=="approach" else 0.),"upper_rf3_n":(-3.91 if c=="approach" else 0.)} for p in PAIRS for c in CASES}
        self.assertEqual(len(compare(good,3.91)),2)
        for key,field,value in [(((1,2),"opening"),"upper_rf3_n",.2),(((2,1),"approach"),"upper_rf3_n",-.2)]:
            wrong={k:dict(v) for k,v in good.items()}
            wrong[key][field]=value
            with self.assertRaises(ValueError):compare(wrong,3.91)
        with self.assertRaises(ValueError):compare(good,math.nan)
    def test_fresh_workspace_and_missing_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"new";generate(p,1,2,"approach")
            self.assertEqual((p/"panel.inp").read_text(),deck(1,2,"approach"))
            with self.assertRaises(ValueError):generate(p,1,2,"opening")
            with self.assertRaises(ValueError):check(d)
if __name__=="__main__":unittest.main()
