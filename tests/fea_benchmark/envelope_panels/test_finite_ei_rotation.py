"""Stage 64 synthetic B31 / root-lever oracle tests."""
import unittest
from check_finite_ei_rotation import analytical,build,assess,CASES,MESHES
class Tests(unittest.TestCase):
    def test_theory(self):
        a=analytical()
        self.assertAlmostEqual(a["second_moment_mm4"],10000/12)
        self.assertAlmostEqual(a["root_rotational_stiffness_n_mm_per_rad"],1000000)
        self.assertAlmostEqual(a["euler_bernoulli_tip_bending_mm"],.005797101449275362)
        self.assertAlmostEqual(a["finite_root_rotation_tip_increment_mm"],.01)
    def test_deck(self):
        for n in MESHES:
            for case in CASES:
                s=build(n,case)
                self.assertEqual(s.count("*ELEMENT,TYPE=B31"),1)
                self.assertEqual(s.count("*STEP"),1)
                self.assertEqual(s.count("*RIGID BODY"),int(case=="root_spring"))
                self.assertEqual(s.count("*ELEMENT,TYPE=SPRING1"),int(case=="root_spring"))
                self.assertNotIn("*PLASTIC",s)
                self.assertNotIn("S8R",s)
    def test_fail_closed(self):
        for n in (0,1,16,True):
            with self.assertRaises(ValueError): build(n,"clamped")
        with self.assertRaises(ValueError): build(4,"fiction")
    def test_assess(self):
        b=analytical()["euler_bernoulli_tip_bending_mm"]
        d=analytical()["finite_root_rotation_tip_increment_mm"]
        cases={(n,c):{"tip_downward_mm":b+(d if c=="root_spring" else 0)} for n in MESHES for c in CASES}
        self.assertEqual(assess(cases)["engineering_capacity"],"NOT_ADMITTED")
        cases[4,"root_spring"]["tip_downward_mm"]=b-0.1
        with self.assertRaises(ValueError): assess(cases)
if __name__=="__main__": unittest.main()
