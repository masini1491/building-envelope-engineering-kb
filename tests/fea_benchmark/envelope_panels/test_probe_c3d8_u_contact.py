"""Deterministic scope and volume guards for bounded C3D8 comparator."""
import unittest
from probe_c3d8_u_contact import deck,model
class SolidControl(unittest.TestCase):
    def test_geometry(self):
        for n in (8,16):
            nodes,els,plate,base,ps,rs,cent=model(n,"toward")
            self.assertEqual(len(els),n*n+14*n)
            self.assertEqual(len(base),6*n)
            self.assertEqual(max(z for x,y,z in nodes.values()),51.5)
            self.assertTrue(set(ps).isdisjoint(rs))
            self.assertTrue(set(cent).isdisjoint(ps))
            volume=0.
            for body,c in els.values():
                x0,y0,z0=nodes[c[0]];x1,y1,z1=nodes[c[6]]
                self.assertGreater(min(x1-x0,y1-y0,z1-z0),0.)
                volume+=(x1-x0)*(y1-y0)*(z1-z0)
            self.assertAlmostEqual(volume,1200*300*3+1200*(50*3+2*3*47),places=4)
    def test_decks(self):
        for n in (8,16):
            for case in ("toward","away","unlinked"):
                with self.subTest(n=n,case=case):
                    s=deck(n,case)
                    self.assertEqual(s.count("*CONTACT PAIR"),case!="unlinked")
                    self.assertEqual(s.count("*ELEMENT,TYPE=C3D8"),2)
                    self.assertNotIn("*ELEMENT,TYPE=S8R",s)
                    self.assertNotIn("SPRING2",s)
                    self.assertIn("CENTER_RF,3,3,-0.02000000" if case=="away" else "CENTER_RF,3,3,0.02000000",s)
        for n,case in ((4,"toward"),(True,"toward"),(8,"unknown")):
            with self.assertRaises(ValueError):deck(n,case)
if __name__=="__main__":unittest.main()
