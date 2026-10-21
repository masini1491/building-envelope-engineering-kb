"""Fixed end stations, 3/4/5 count synthetic link deck checks."""
import unittest
from stud_pitch_trial import PROFILES,MESHES,make
from stud_solid_trial import add_studs
from pressure_contact_trial import deck

class PitchTrial(unittest.TestCase):
    def test_both_meshes_all_profiles(self):
        for n in MESHES:
            for profile,x in PROFILES.items():
                for case in ('soft','stiff'):
                    inp,pairs=make(n,profile,case)
                    self.assertEqual(len(pairs),len(x))
                    self.assertEqual(len({v for pair in pairs for v in pair}),2*len(x))
                    self.assertEqual(inp.count('*ELEMENT,TYPE=SPRING2'),1)
                    self.assertEqual(inp.count('*DLOAD\nPLATE,P1,0.00010000'),1)
                    self.assertNotIn('*CONTACT PAIR',inp)
    def test_canonical_four_bytes(self):
        for n in MESHES:
            for case in ('soft','stiff'):
                self.assertEqual(make(n,'four_300',case),add_studs(deck(n,'unlinked'),n,case))
    def test_no_unrelated_physics_change(self):
        original,_=make(8,'four_300','soft')
        for profile in ('three_450','five_225'):
            modified,_=make(8,profile,'soft')
            self.assertEqual(modified.split('*NSET,NSET=STUD_PLATE\n')[0],original.split('*NSET,NSET=STUD_PLATE\n')[0])
            self.assertEqual(modified.split('*MATERIAL,NAME=SYNTH\n')[1],original.split('*MATERIAL,NAME=SYNTH\n')[1])
    def test_bad_scope(self):
        base=deck(8,'unlinked')
        for n,prof,k in ((24,'three_450','soft'),(True,'three_450','soft'),(8,'bad','soft'),(8,'three_450','real')):
            with self.assertRaisesRegex(ValueError,'STUD_PITCH_SCOPE'):
                make(n,prof,k)
    def test_endpoints_and_spacing(self):
        for k,p in PROFILES.items():
            self.assertEqual((p[0],p[-1]),(150.,1050.))
            dx=[p[i+1]-p[i] for i in range(len(p)-1)]
            self.assertTrue(all(abs(v-dx[0])<1e-9 for v in dx))

if __name__=='__main__':unittest.main()
