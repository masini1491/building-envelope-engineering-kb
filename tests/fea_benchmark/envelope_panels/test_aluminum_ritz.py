import math
import tempfile
import unittest
from pathlib import Path
from check_aluminum_ritz import CASES,expected_input,ritz_center_mm,assess,deck_material

class Tests(unittest.TestCase):
    def test_polynomial_integral_square(self):
        c=expected_input("thicker_square",16)
        D=c["youngs_modulus_mpa"]*c["thickness_mm"]**3/(12*(1-c["poisson_ratio"]**2))
        coeff=ritz_center_mm(c)*D/(c["pressure_n_mm2"]*c["width_mm"]**4)
        self.assertAlmostEqual(coeff,0.0013292100694444443,places=13)
        self.assertGreater(coeff,0.00126)
    def test_two_cases_and_mesh(self):
        self.assertNotEqual(CASES["thicker_square"]["width_mm"]/CASES["thicker_square"]["height_mm"],
                            CASES["rectangular_higher_pressure"]["width_mm"]/CASES["rectangular_higher_pressure"]["height_mm"])
        for case in CASES:
            c=expected_input(case,4);w=ritz_center_mm(c)
            result=assess(c,{4:w*.9,8:w*.98,16:w*.99})
            self.assertEqual(result["engineering_acceptance"],"NOT_ADMITTED")
    def test_fail_closed(self):
        c=expected_input("thicker_square",4);w=ritz_center_mm(c)
        for v in ({4:w,8:w,16:w},{4:w*.9,8:w*.99,16:w*1.3},{4:w,8:w},{4:w,8:math.nan,16:w}):
            with self.subTest(v=v),self.assertRaises(ValueError):assess(c,v)
    def test_material(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"a.inp"
            p.write_text("*ELASTIC\n70000,0.32\n*SHELL SECTION\n2.5\n")
            self.assertEqual(deck_material(p),(70000.,.32,2.5))
            p.write_text("*ELASTIC\nnan,0.32\n*SHELL SECTION\n2.5\n")
            with self.assertRaises(ValueError):deck_material(p)
if __name__=="__main__":unittest.main()
