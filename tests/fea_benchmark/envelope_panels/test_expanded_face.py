"""Independent analytic and failure-path tests for exact P1-face geometry inputs."""

import unittest

from check_expanded_face import GAUSS, P1_FACE_SLOTS, _s8, integrate_p1_expanded_face


def expanded_block(width=10.0, height=20.0, thickness=2.0, slope_x=0.0, slope_y=0.0):
    """Synthetic C3D20R node positions, not CCX-expanded runtime output."""
    xy = [(0, 0), (width, 0), (width, height), (0, height),
          (0, 0), (width, 0), (width, height), (0, height),
          (width / 2, 0), (width, height / 2), (width / 2, height), (0, height / 2),
          (width / 2, 0), (width, height / 2), (width / 2, height), (0, height / 2),
          (0, 0), (width, 0), (width, height), (0, height)]
    z_layer = [-thickness / 2] * 4 + [thickness / 2] * 4 + \
              [-thickness / 2] * 4 + [thickness / 2] * 4 + [0] * 4
    return [(x, y, z + slope_x * x + slope_y * y) for (x, y), z in zip(xy, z_layer)]


class ExpandedFaceTests(unittest.TestCase):
    def test_face_index_source_and_shape_partition(self):
        self.assertEqual(P1_FACE_SLOTS, (4, 3, 2, 1, 11, 10, 9, 12))
        for xi in GAUSS:
            for eta in GAUSS:
                n, dx, dy = _s8(xi, eta)
                self.assertAlmostEqual(sum(n), 1.0)
                self.assertAlmostEqual(sum(dx), 0.0)
                self.assertAlmostEqual(sum(dy), 0.0)

    def test_planar_face_load_and_non_face_zero(self):
        nodal, total = integrate_p1_expanded_face(expanded_block(), 0.25)
        for actual, expected in zip(total, (0, 0, 50)):
            self.assertAlmostEqual(actual, expected, places=8)
        for index in range(20):
            if index + 1 not in P1_FACE_SLOTS:
                self.assertEqual(nodal[index], (0.0, 0.0, 0.0))
        self.assertAlmostEqual(sum(p[2] for p in nodal), 50, places=8)

    def test_tilted_face_resultant_and_thickness_independence(self):
        for thick in (0.5, 2.0, 7.0):
            nodal, total = integrate_p1_expanded_face(
                expanded_block(thickness=thick, slope_x=0.1, slope_y=-0.2), 0.25)
            for actual, expected in zip(total, (-5, 10, 50)):
                self.assertAlmostEqual(actual, expected, places=8)
            for c in range(3):
                self.assertAlmostEqual(sum(v[c] for v in nodal), total[c], places=8)

    def test_strict_missing_nonfinite_and_bad_pressure(self):
        coords = expanded_block()
        for bad in (coords[:-1], coords + [coords[-1]]):
            with self.assertRaisesRegex(ValueError, "INVALID_EXPANDED_FACE_INPUT"):
                integrate_p1_expanded_face(bad, 0.25)
        with self.assertRaisesRegex(ValueError, "INVALID_EXPANDED_FACE_INPUT"):
            integrate_p1_expanded_face(coords, float("nan"))
        coords[3] = (float("nan"), 20, -1)
        with self.assertRaisesRegex(ValueError, "INVALID_EXPANDED_FACE_COORDINATES"):
            integrate_p1_expanded_face(coords, 0.25)

    def test_degenerate_and_inverted_face_guards(self):
        coords = expanded_block()
        coords[3] = coords[2]
        with self.assertRaisesRegex(ValueError, "DEGENERATE_P1_FACE"):
            integrate_p1_expanded_face(coords, 0.25)
        coords = expanded_block()
        coords[10] = (5.0, -300.0, -1.0)
        with self.assertRaisesRegex(ValueError, "FOLDED_OR_DEGENERATE_P1_FACE"):
            integrate_p1_expanded_face(coords, 0.25)


if __name__ == "__main__":
    unittest.main()
