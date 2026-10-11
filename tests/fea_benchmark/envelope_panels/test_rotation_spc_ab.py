"""Stage 23 isolated deck A/B failure-path unit tests."""
import unittest
from check_rotation_spc_ab import make_pair, ORIGINAL, VARIANT

class RotationABTests(unittest.TestCase):
    def test_single_isolated_edge_change(self):
        source = "synthetic aluminum clamped plate, n=4, large\n*BOUNDARY\nEDGE,1,6,0.\n*STEP,NLGEOM\n"
        variant = make_pair(source)
        self.assertEqual(variant,source.replace(ORIGINAL,VARIANT))
        self.assertEqual(variant.replace(VARIANT,ORIGINAL),source)

    def test_multiple_constraints_fail(self):
        with self.assertRaisesRegex(ValueError,"UNSUPPORTED_ROTATION_AB_BASE"):
            make_pair("*BOUNDARY\nEDGE,1,6,0.\nEDGE,1,6,0.\n")

    def test_missing_constraints_fail(self):
        with self.assertRaisesRegex(ValueError,"UNSUPPORTED_ROTATION_AB_BASE"):
            make_pair("*BOUNDARY\nEDGE,1,5,0.\n")

    def test_missing_boundary_keyword_fails(self):
        with self.assertRaisesRegex(ValueError,"UNSUPPORTED_ROTATION_AB_BASE"):
            make_pair("EDGE,1,6,0.\n")

if __name__=="__main__":
    unittest.main()
