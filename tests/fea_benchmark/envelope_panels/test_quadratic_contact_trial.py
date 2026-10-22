"""Source-scoped quadratic element and support invariants."""
import unittest
from quadratic_contact_trial import deck, EDGES
from probe_c3d8_u_contact import model

class QuadraticDeckTrial(unittest.TestCase):
    def test_all_cases(self):
        for n in (8,16):
            for case in ('toward','away','unlinked','clearance'):
                with self.subTest(n=n,case=case):
                    s=deck(n,case)
                    old,elems,plate,base,ps,rs,center=model(n,case)
                    self.assertEqual(s.count('*ELEMENT,TYPE=C3D20R'),2)
                    self.assertNotIn('*ELEMENT,TYPE=C3D8',s)
                    self.assertEqual(s.count('*CONTACT PAIR'),int(case!='unlinked'))
                    self.assertEqual(s.count('*SURFACE,NAME='),0 if case=='unlinked' else 2)
                    self.assertEqual(s.count('CENTER_RF,3,3,'),1)
                    self.assertEqual(s.count('*ELEMENT,TYPE=C3D20R,ELSET=PLATE'),1)
                    self.assertEqual(s.count('*ELEMENT,TYPE=C3D20R,ELSET=RIB'),1)
                    self.assertIn('Synthetic explicit C3D20R open-U',s)
    def test_scope(self):
        for n,case in ((4,'toward'),(True,'toward'),(8,'unknown')):
            with self.assertRaises(ValueError):deck(n,case)
    def test_straight_midpoints_and_continuations(self):
        n=8;s=deck(n,'toward');lines=s.splitlines()
        mids={};i=lines.index('*NODE')+1
        while not lines[i].startswith('*'):
            row=lines[i].split(',');mids[int(row[0])]=tuple(map(float,row[1:]));i+=1
        originals,elements,*_=model(n,'toward')
        self.assertGreater(len(mids),len(originals))
        for k in ('*ELEMENT,TYPE=C3D20R,ELSET=PLATE','*ELEMENT,TYPE=C3D20R,ELSET=RIB'):
            i=lines.index(k)+1
            while i<len(lines) and not lines[i].startswith('*'):
                self.assertTrue(lines[i].endswith(','));v=lines[i][:-1].split(',')
                self.assertEqual(len(v),16);a=list(map(int,v))
                b=list(map(int,lines[i+1].split(',')));self.assertEqual(len(b),5)
                c=a[1:]+b; self.assertEqual(len(c),20)
                self.assertEqual(c[:8],list(elements[a[0]][1]))
                for k,(p,q) in enumerate(EDGES):
                    xyz=tuple((originals[c[p]][j]+originals[c[q]][j])/2 for j in range(3))
                    self.assertEqual(mids[c[8+k]],xyz)
                i+=2
if __name__=='__main__':unittest.main()
