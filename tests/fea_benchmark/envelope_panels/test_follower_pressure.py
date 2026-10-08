"""Unit checks for independent S8 gradient, follower quadrature, and parsing guards."""
import math
import unittest

from check_follower_pressure import (cross, displacement_block, gradients,
                                     integrate_follower_mid_surface)
from check_pressure_equilibrium import shape


class FollowerTests(unittest.TestCase):
    @staticmethod
    def flat_element():
        xy = [(0, 0), (10, 0), (10, 20), (0, 20),
              (5, 0), (10, 10), (5, 20), (0, 10)]
        return {i+1:(float(x),float(y),0.0) for i,(x,y) in enumerate(xy)}, [tuple(range(1,9))]

    def test_gradient_partitions_and_finite_differences(self):
        for xi, eta in ((0, 0), (-0.6, 0.4), (0.7, -0.8)):
            dx, dy = gradients(xi, eta)
            self.assertAlmostEqual(sum(dx), 0, places=12)
            self.assertAlmostEqual(sum(dy), 0, places=12)
            h = 1e-6
            for i in range(8):
                self.assertAlmostEqual(dx[i], (shape(xi+h, eta)[i]-shape(xi-h, eta)[i])/(2*h), places=8)
                self.assertAlmostEqual(dy[i], (shape(xi, eta+h)[i]-shape(xi, eta-h)[i])/(2*h), places=8)

    def test_flat_and_uniform_tilt_exact_resultants(self):
        nodes, elements = self.flat_element()
        for slope_x, slope_y in ((0,0),(0.1,-0.2)):
            disp = {k: (0,0,slope_x*p[0]+slope_y*p[1]) for k,p in nodes.items()}
            loads,total = integrate_follower_mid_surface(nodes,elements,disp,0.25)
            self.assertAlmostEqual(total[0], -50*slope_x, places=8)
            self.assertAlmostEqual(total[1], -50*slope_y, places=8)
            self.assertAlmostEqual(total[2], 50, places=8)
            for c in range(3):
                self.assertAlmostEqual(sum(f[c] for f in loads.values()),total[c],places=8)

    def test_area_change_affects_loads(self):
        nodes, elements = self.flat_element()
        disp = {k:(0.1*p[0], -0.1*p[1], 0) for k,p in nodes.items()}
        _, f=integrate_follower_mid_surface(nodes,elements,disp,0.25)
        self.assertAlmostEqual(f[2], 49.5, places=8)

    def test_parse_missing_duplicate_nonfinite(self):
        expected={1,2}
        header="displacements (vx,vy,vz) for set NALL and time  0.1000000E+01\n\n"
        good=header+"1 0 0 0\n2 0 0 1\n\n"
        self.assertEqual(displacement_block(good,expected)[2],(0.0,0.0,1.0))
        for bad,pattern in ((header+"1 0 0 0\n", "NALL_COVERAGE_MISMATCH"),
                            (header+"1 0 0 0\n1 0 0 1\n2 0 0 1\n", "DUPLICATE_OR_NONFINITE_NALL"),
                            (header+"1 0 0 NaN\n2 0 0 0\n", "MISSING_NALL_DISPLACEMENTS")):
            with self.assertRaisesRegex(ValueError,pattern):
                displacement_block(bad,expected)

    def test_fail_on_folded_surface(self):
        nodes,elements=self.flat_element()
        disp={k:(-2*p[0],0,0) for k,p in nodes.items()}
        with self.assertRaisesRegex(ValueError,"FOLDED_OR_INVALID_MID_SURFACE"):
            integrate_follower_mid_surface(nodes,elements,disp,1)


if __name__ == '__main__':
    unittest.main()
