import unittest
from stud_position_trial import make,LAYOUTS
from stud_pitch_trial import make as baseline
class PositionTests(unittest.TestCase):
 def test_pairs_and_only_link_mutation(self):
  for n in (8,16):
   for layout,(parent,positions) in LAYOUTS.items():
    for k in ('soft','stiff'):
     a,p=make(n,layout,k);b,q=baseline(n,parent,k)
     self.assertEqual(len(p),len(q))
     self.assertEqual(len(set(sum((list(z) for z in p),[]))),2*len(p))
     self.assertEqual(a.split('*NSET,NSET=STUD_PLATE\n')[0],b.split('*NSET,NSET=STUD_PLATE\n')[0])
     self.assertEqual(a.split('*MATERIAL,NAME=SYNTH\n')[1],b.split('*MATERIAL,NAME=SYNTH\n')[1])
     self.assertNotEqual(p,q)
 def test_invalid_scope(self):
  for n,l,c in ((24,'four_inner_out','soft'),(True,'four_inner_out','soft'),(8,'unknown','soft'),(8,'four_inner_out','actual')):
   with self.assertRaisesRegex(ValueError,'STUD_POSITION_SCOPE'):make(n,l,c)
 def test_fixed_end_and_center(self):
  for layout,(parent,x) in LAYOUTS.items():
   self.assertEqual((x[0],x[-1]),(150.,1050.))
   self.assertEqual(600. in x,parent=='five_225')
   self.assertTrue(all(x[i]+x[-1-i]==1200 for i in range(len(x))))
if __name__=='__main__':unittest.main()
