"""Quadratic-face fixed-load oracle: bounded synthetic negative and positive checks."""
import unittest
from verify_pressure_contact_trial import nominal_pressure_equivalents

class QuadraticPressureEquivalentTest(unittest.TestCase):
    def test_both_meshes(self):
        for n,edge,center in ((8,3.1875,-0.1875),(16,1.546875,-0.046875)):
            with self.subTest(mesh=n):
                x=nominal_pressure_equivalents(n)
                self.assertAlmostEqual(x['edge_pressure_n'],edge)
                self.assertAlmostEqual(x['center_pressure_n'],center)

    def test_reject_unadmitted_meshes(self):
        for n in (0,1,4,24,True,8.0):
            with self.subTest(mesh=n),self.assertRaisesRegex(ValueError,'PRESSURE_SCOPE'):
                nominal_pressure_equivalents(n)

    def test_original_failure_is_not_accepted(self):
        for n,raw in ((8,-32.99989715788786),(16,-34.499840267737035)):
            x=nominal_pressure_equivalents(n)
            # Center is a free node: do NOT include it as an SPC reaction.
            corrected=raw-x['center_pressure_n']-x['edge_pressure_n']+36
            self.assertLess(abs(corrected),0.002)
            self.assertGreater(abs(raw+36),0.9)

if __name__=='__main__':unittest.main()
