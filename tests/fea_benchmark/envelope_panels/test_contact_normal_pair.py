"""Deterministic synthetic contact oracle and negative cases, no solver impersonation."""
import math
import tempfile
import unittest
from pathlib import Path
from check_contact_normal_pair import CASES,deck,generate,oracle,field,completed

def values(case):
    f=1. if case=="compression" else 0.
    g=-.00001 if case=="compression" else .002
    return ({i:(0.,0.,f/4) for i in range(1,5)},
            {i:(0.,0.,-f/4) for i in range(13,17)},
            {i:(0.,0.,0.) for i in range(5,9)},
            {i:(0.,0.,g) for i in range(9,13)})

class ContactNormalTests(unittest.TestCase):
    def test_isolated_two_cube_decks(self):
        for c in CASES:
            s=deck(c)
            self.assertEqual(s.count("*ELEMENT,TYPE=C3D8"),2)
            self.assertEqual(s.count("*CONTACT PAIR"),1)
            self.assertIn("1,S2",s)
            self.assertIn("2,S1",s)
            self.assertNotIn("*FRICTION",s)
            self.assertIn(f"DRIVEN,3,3,{CASES[c]:.8f}",s)
        self.assertNotEqual(deck("compression"),deck("opening"))
    def test_oracle_valid_synthetic_samples(self):
        for c in CASES:
            self.assertEqual(oracle(c,*values(c))["engineering_acceptance"],"NOT_ADMITTED")
    def test_reject_fabricated_no_compression_contact(self):
        a=list(values("compression"))
        a[0]={i:(0.,0.,0.) for i in a[0]}
        a[1]={i:(0.,0.,0.) for i in a[1]}
        with self.assertRaises(ValueError): oracle("compression",*a)
    def test_reject_fake_tensile_transfer(self):
        a=list(values("opening"))
        a[0][1]=(0.,0.,-.25)
        a[1][13]=(0.,0.,.25)
        with self.assertRaises(ValueError): oracle("opening",*a)
    def test_reject_corrupt_interface_geometry(self):
        a=list(values("opening"))
        a[3][9]=(0.,0.,0.)
        with self.assertRaises(ValueError): oracle("opening",*a)
    def test_reject_bad_balance_nodes_nan(self):
        a=list(values("compression"))
        a[0][1]=(0.,0.,-3.)
        with self.assertRaises(ValueError): oracle("compression",*a)
        a=list(values("compression"))
        del a[2][5]
        with self.assertRaises(ValueError): oracle("compression",*a)
        a=list(values("compression"))
        a[2][5]=(0.,0.,math.nan)
        with self.assertRaises(ValueError): oracle("compression",*a)
    def test_parser_and_completion(self):
        s=" displacements (global) for set UPPER_FACE and time 1.0\n\n9 0 0 .002\n"
        self.assertAlmostEqual(field(s,"displacements","UPPER_FACE")[9][2],.002)
        with self.assertRaises(ValueError): field(s+"9 0 0 .002\n","displacements","UPPER_FACE")
        with self.assertRaises(ValueError): field("","forces","BASE")
        with self.assertRaises(ValueError): completed("1 1 1 1 .5 1 1")
    def test_generation_guard(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"sample"
            generate(p,"compression")
            self.assertEqual((p/"panel.inp").read_text(),deck("compression"))
            with self.assertRaises(ValueError): generate(p,"opening")
            with self.assertRaises(ValueError): deck("unknown")
if __name__=="__main__": unittest.main()
