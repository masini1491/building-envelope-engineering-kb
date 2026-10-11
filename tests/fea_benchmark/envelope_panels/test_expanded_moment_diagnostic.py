"""Synthetic checks for geometric torque; no rotational/MPC admission."""
import unittest

from check_expanded_moment_diagnostic import force_and_geometric_moment


class ExpandedMomentDiagnosticTests(unittest.TestCase):
    def test_pure_couple_is_lost_by_shell_force_sum(self):
        # Two expanded nodes can map to the SAME original shell node.
        # Their projected translational force sums to zero; torque does not.
        p = {101: (0., 0., 1.), 102: (0., 0., -1.)}
        f = {101: (2., 0., 0.), 102: (-2., 0., 0.)}
        total, torque = force_and_geometric_moment(p, f)
        self.assertEqual(total, (0., 0., 0.))
        self.assertEqual(torque, (0., 4., 0.))

    def test_known_force_and_moment(self):
        p = {1: (2., 0., 0.)}
        f = {1: (0., 3., 0.)}
        self.assertEqual(force_and_geometric_moment(p, f), ((0., 3., 0.), (0., 0., 6.)))

    def test_origin_shift_is_not_invariant_when_resultant_nonzero(self):
        p, f = {1: (2., 0., 0.)}, {1: (0., 3., 0.)}
        self.assertEqual(force_and_geometric_moment(p, f, (1., 0., 0.))[1], (0., 0., 3.))

    def test_missing_or_extra_expanded_nodes_rejected(self):
        p, f = {1: (0., 0., 0.)}, {2: (1., 0., 0.)}
        with self.assertRaisesRegex(ValueError, "COVERAGE_MISMATCH"):
            force_and_geometric_moment(p, f)
        with self.assertRaisesRegex(ValueError, "COVERAGE_MISMATCH"):
            force_and_geometric_moment({}, {})

    def test_nonfinite_and_invalid_components_rejected(self):
        p = {1: (0., 0., 0.)}
        for force in [(1., 2.), (1., float('nan'), 0.), (float('inf'), 0., 0.), ("1", 0., 0.)]:
            with self.subTest(force=force), self.assertRaisesRegex(ValueError, "INVALID_MOMENT_VECTOR"):
                force_and_geometric_moment(p, {1: force})
        with self.assertRaisesRegex(ValueError, "INVALID_MOMENT_VECTOR"):
            force_and_geometric_moment(p, {1: (0., 0., 1.)}, origin=(0.,))


if __name__ == "__main__":
    unittest.main()
