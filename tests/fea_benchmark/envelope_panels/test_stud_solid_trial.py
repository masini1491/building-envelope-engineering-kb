"""Synthetic four-position C3D20R link mapping validation."""
import unittest
from stud_solid_trial import add_studs,deck,STATIONS,CASES
from pressure_contact_trial import deck as baseline

class StudTrial(unittest.TestCase):
    def test_exact_mesh_pairs(self):
        for n in (8,16):
            inp=baseline(n,'unlinked')
            for case in CASES:
                out,pairs=add_studs(inp,n,case)
                self.assertEqual(len(pairs),4)
                self.assertEqual(len(set(sum((list(p) for p in pairs),[]))),8)
                self.assertEqual(out.count('*ELEMENT,TYPE=SPRING2'),int(case!='unlinked'))
                self.assertEqual(out.count('PLATE,P1,0.00010000'),1)
                self.assertNotIn('*CONTACT PAIR',out)
                self.assertEqual(deck(n,case),out)
    def test_scope(self):
        for n,c in ((4,'soft'),(24,'soft'),(True,'soft'),(8,'real')):
            with self.assertRaisesRegex(ValueError,'STUD_SOLID_SCOPE'):
                deck(n,c)
    def test_no_contact(self):
        with self.assertRaisesRegex(ValueError,'BASE_DECK_CONTRACT'):
            add_studs(baseline(8,'toward'),8,'soft')
    def test_pressure_mutation(self):
        with self.assertRaisesRegex(ValueError,'BASE_DECK_CONTRACT'):
            add_studs(baseline(8,'unlinked').replace('0.00010000','0.00020000'),8,'soft')
    def test_station_geometry(self):
        self.assertEqual(STATIONS,(150.,450.,750.,1050.))
    def test_synthetic_k(self):
        self.assertEqual(CASES,{'unlinked':0.,'soft':50.,'stiff':500.})
if __name__=='__main__':unittest.main()
