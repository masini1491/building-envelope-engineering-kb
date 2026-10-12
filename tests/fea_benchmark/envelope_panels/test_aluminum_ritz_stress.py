"""Analytical polynomials + fail-closed selected stress field checks."""
import math
import unittest
from check_aluminum_ritz_stress import reference,compare,_solve3
from check_aluminum_ritz import expected_input,ritz_center_mm


class Tests(unittest.TestCase):
    def config(self):
        return expected_input("thicker_square",16)

    def test_three_term_square_reference_and_material_scaling(self):
        cfg=self.config()
        r=reference(cfg)
        self.assertAlmostEqual(r["center_deflection_mm"],0.000072472855221608,places=12)
        self.assertAlmostEqual(r["center_surface_bending_stress_mpa"]["SXX"],0.0153156861215,places=9)
        self.assertAlmostEqual(r["center_surface_bending_stress_mpa"]["SXX"],
                               r["center_surface_bending_stress_mpa"]["SYY"],places=12)
        self.assertLess(r["center_deflection_mm"],ritz_center_mm(cfg))
        doubled={**cfg,"pressure_n_mm2":2*cfg["pressure_n_mm2"]}
        rr=reference(doubled)
        self.assertAlmostEqual(rr["center_deflection_mm"],2*r["center_deflection_mm"],places=12)
        self.assertAlmostEqual(rr["center_surface_bending_stress_mpa"]["SXX"],
                               2*r["center_surface_bending_stress_mpa"]["SXX"],places=9)

    def test_rectangular_is_not_artificially_symmetric(self):
        r=reference(expected_input("rectangular_higher_pressure",16))
        self.assertGreater(r["center_surface_bending_stress_mpa"]["SYY"],
                           r["center_surface_bending_stress_mpa"]["SXX"])

    def make_fields(self, cfg):
        r=reference(cfg)
        sx=r["center_surface_bending_stress_mpa"]["SXX"]
        sy=r["center_surface_bending_stress_mpa"]["SYY"]
        a,b,t=cfg["width_mm"],cfg["height_mm"],cfg["thickness_mm"]
        return ({1:(a/2,b/2,t/2),2:(a/2,b/2,-t/2)},
                {1:(sx,sy,0,0,0,0),2:(-sx,-sy,0,0,0,0)},
                r["center_deflection_mm"])

    def test_center_field_and_failure_modes(self):
        cfg=self.config();xyz,s,w=self.make_fields(cfg)
        result=compare(cfg,xyz,s,w)
        self.assertEqual(result["engineering_acceptance"],"NOT_ADMITTED")
        self.assertEqual(result["integration_point_stress_extreme"],"NOT_OBSERVED")
        with self.assertRaisesRegex(ValueError,"COVERAGE"):
            compare(cfg,{1:xyz[1]},{1:s[1]},w)
        with self.assertRaisesRegex(ValueError,"BENDING_STRESS"):
            compare(cfg,xyz,{1:tuple(1.6*v for v in s[1]),2:s[2]},w)
        with self.assertRaisesRegex(ValueError,"DEFLECTION"):
            compare(cfg,xyz,s,1.25*w)
        with self.assertRaisesRegex(ValueError,"MEMBRANE"):
            sx=reference(cfg)["center_surface_bending_stress_mpa"]["SXX"]
            top=list(s[1]);bottom=list(s[2])
            top[0]+=sx*.4;bottom[0]+=sx*.4
            with self.assertRaisesRegex(ValueError,"MEMBRANE"):
                compare(cfg,xyz,{1:tuple(top),2:tuple(bottom)},w)

    def test_reject_invalid_math_inputs(self):
        cfg=self.config()
        for key,value in (("poisson_ratio",.5),("pressure_n_mm2",float("nan")),
                          ("width_mm",0),("thickness_mm",100)):
            with self.subTest(key=key),self.assertRaises(ValueError):
                reference({**cfg,key:value})
        with self.assertRaisesRegex(ValueError,"SINGULAR"):
            _solve3([[0,0,0]]*3,[1,2,3])


if __name__=="__main__":
    unittest.main()
