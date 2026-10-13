"""Stage 65 bounded deck/geometry and model-boundary tests."""
import tempfile
import unittest
from pathlib import Path
from check_rib_spring_height import (
    MESHES,WINDOWS,K_PER_NODE,window_nodes,geometry_matrix,
    make_deck,generate,assess,observed
)
class HeightWindowTests(unittest.TestCase):
    def test_two_windows_geometry(self):
        for n in MESHES:
            seen=[]
            for window in WINDOWS:
                base,web,end_nodes,els,coords,selected=window_nodes(n,window)
                self.assertEqual(len(selected),8)
                m=geometry_matrix(coords,selected)
                self.assertEqual(m["k00_n_per_mm"],8*K_PER_NODE)
                self.assertAlmostEqual(m["condensed_rotational_coefficient_n_mm_per_rad"],100000.)
                self.assertTrue(m["matrix_determinant"]>0)
                seen.append(selected)
            self.assertFalse(seen[0]&seen[1])
            self.assertEqual(seen[0]|seen[1],end_nodes)
    def test_deck_is_subset_only(self):
        for n in MESHES:
            for window in WINDOWS:
                deck,*_=make_deck(n,window)
                self.assertEqual(deck.count("*ELEMENT,TYPE=SPRING1,ELSET="),1)
                self.assertEqual(deck.count("*SPRING,ELSET=RIB_END_X_SPRING"),1)
                self.assertEqual(deck.count("*DLOAD\nWEB,P,0.0001"),1)
                self.assertNotIn("*CLOAD",deck)
                self.assertNotIn("*PLASTIC",deck)
                with tempfile.TemporaryDirectory() as d:
                    p=Path(d)/"fresh"
                    generate(p,n,window)
                    self.assertEqual((p/"panel.inp").read_text(),deck)
                    with self.assertRaises(ValueError):generate(p,n,window)
                    with self.assertRaisesRegex(ValueError,"ARTIFACT_MISSING"):
                        observed(p,n,window)
    def test_assessment_bounds_and_no_high_low_order_assumption(self):
        mats={}
        for w in WINDOWS:
            _,_,_,_,coords,selected=window_nodes(8,w)
            mats[w]=geometry_matrix(coords,selected)
        rows={}
        for n in MESHES:
            rows[n,"free"]=4e-5
            rows[n,"full"]=3e-5
            rows[n,"low"]=3.8e-5
            rows[n,"high"]=3.6e-5
        result=assess(rows,mats)
        self.assertEqual(result["engineering_acceptance"],"NOT_ADMITTED")
        rows[8,"low"],rows[8,"high"]=rows[8,"high"],rows[8,"low"]
        self.assertEqual(assess(rows,mats)["order_between_low_and_high"],"NOT_ASSUMED")
        with self.assertRaisesRegex(ValueError,"OUTSIDE_FULL_FREE_BOUNDS"):
            assess({**rows,(16,"low"):2e-5},mats)
        with self.assertRaisesRegex(ValueError,"OBSERVATION_MATRIX_INVALID"):
            assess({**rows,(16,"high"):float("nan")},mats)
    def test_fail_closed(self):
        for n,w in ((4,"low"),(16,"middle"),(True,"low"),(8,1)):
            with self.assertRaises(ValueError): make_deck(n,w)
if __name__=="__main__": unittest.main()
