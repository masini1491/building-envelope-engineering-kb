"""Bounded unit checks for all-original S8R reaction diagnostic; no CCX claims."""
import tempfile,unittest
from pathlib import Path
from probe_s8r_all_original_rf import deck,generate,analyze_text,observe
from check_u_rib_base_contact import selected_faces
class AllOriginalRFTests(unittest.TestCase):
    def test_exact_deck_insertion_and_geometry(self):
        for n in (8,16):
            with self.subTest(n=n):
                s=deck(n)
                topo,_,_=selected_faces(n)
                self.assertEqual(s.count("*NODE PRINT,NSET=ALL_ORIGINAL_RF"),1)
                self.assertEqual(s.count("*NSET,NSET=ALL_ORIGINAL_RF"),1)
                self.assertEqual(s.count("*CONTACT PAIR"),1)
                self.assertEqual(s.count("*ELEMENT,TYPE=S8R"),2)
                self.assertEqual(len(topo["coords"]),len(set(topo["coords"])))
                self.assertNotIn("*CLOAD",s)
        for n in (0,4,True,8.0):
            with self.assertRaises(ValueError):deck(n)
    def test_fresh_generation_and_missing_solver_artifacts(self):
        with tempfile.TemporaryDirectory() as root:
            folder=Path(root)/"u_s8r_all_original_rf_n8_toward"
            generate(folder,8)
            self.assertEqual((folder/"panel.inp").read_bytes(),deck(8).encode())
            with self.assertRaisesRegex(ValueError,"WORKSPACE_NOT_FRESH"):generate(folder,8)
            with self.assertRaisesRegex(ValueError,"MISSING_dat"):observe(root)
    def test_missing_all_nodes_fails_closed(self):
        for n in (8,16):
            with self.assertRaises(ValueError):analyze_text("",n)
if __name__=="__main__":unittest.main()
