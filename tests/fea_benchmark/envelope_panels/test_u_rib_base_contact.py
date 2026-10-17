"""Actual-shape synthetic U-base contact deck and negative controls."""
import tempfile,unittest
from pathlib import Path
from check_u_rib_base_contact import CASES,MESHES,selected_faces,deck,generate,validate,check
class UBaseContactTests(unittest.TestCase):
    def test_geometry_surface_selection(self):
        for n in MESHES:
            topo,plate,rib=selected_faces(n)
            self.assertEqual(len(plate),n*8)
            self.assertEqual(len(rib),2*n)
            self.assertEqual(len(topo["panel_studs"]),4)
            self.assertEqual(len(topo["rib_studs"]),4)
    def test_deck_cases(self):
        for n in MESHES:
            for case in CASES:
                with self.subTest(n=n,case=case):
                    s=deck(n,case)
                    self.assertEqual(s.count("*ELEMENT,TYPE=S8R"),2)
                    self.assertEqual(s.count("*CONTACT PAIR"),int(case!="unlinked"))
                    self.assertEqual(s.count("*SURFACE,NAME=RIB_BASE_UNDERSIDE"),int(case!="unlinked"))
                    self.assertNotIn("SPRING2",s)
                    self.assertNotIn("*FRICTION",s)
                    self.assertTrue(all(len(line.split(","))<=16 for line in s.splitlines()))
    def test_bad_scope(self):
        for n in (0,4,True,8.0):
            with self.assertRaises(ValueError):selected_faces(n)
        with self.assertRaises(ValueError):deck(8,"fake")
    def test_reactions_fail_closed(self):
        def case(rib,center):
            return {"rib_end_rf3_n":rib,"driven_center_rf3_n":center}
        good={(n,c):case(-.02,1.5) if c=="toward" else case(0.,-1.) if c=="away" else case(0.,1.)
              for n in MESHES for c in CASES}
        self.assertEqual(validate(good)["engineering_acceptance"],"NOT_ADMITTED")
        broken={k:dict(v) for k,v in good.items()}
        broken[8,"toward"]["rib_end_rf3_n"]=0.
        with self.assertRaises(ValueError):validate(broken)
        broken={k:dict(v) for k,v in good.items()}
        broken[16,"away"]["rib_end_rf3_n"]=.1
        with self.assertRaises(ValueError):validate(broken)
    def test_generation_and_evidence_required(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"case";generate(p,8,"toward")
            self.assertEqual((p/"panel.inp").read_text(),deck(8,"toward"))
            with self.assertRaises(ValueError):generate(p,8,"toward")
            with self.assertRaises(ValueError):check(td)
if __name__=="__main__":unittest.main()
