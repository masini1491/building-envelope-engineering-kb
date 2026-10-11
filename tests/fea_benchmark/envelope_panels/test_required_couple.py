"""Stage 21 fail-closed synthetic tests: theoretical missing couple, not measured RM."""
import unittest

from check_required_couple import required_unobserved_couple


class RequiredCoupleTests(unittest.TestCase):
    @staticmethod
    def sample():
        positions = {1:(1., 0., 0.), 2:(0., 0., 0.)}
        applied = {1:(0., 0., 10.), 2:(0., 0., 0.)}
        internal = {1:(0., 0., 0.), 2:(0., 0., 0.)}
        return positions, applied, internal, {(1,2)}, (0., 0., 10.)

    def test_balanced_translation_arm_still_not_full_admission(self):
        result = required_unobserved_couple(*self.sample(), (0., -10., 0.))
        self.assertEqual(result["reconstructed_translation_support_N"], (0., 0., -10.))
        self.assertEqual(result["translation_support_r_cross_F_Nmm"], (0., 10., 0.))
        self.assertEqual(result["required_unobserved_couple_if_equilibrium_Nmm"], (0., 0., 0.))
        self.assertEqual(result["six_component_balance"], "NOT_ADMITTED")

    def test_required_couple_not_measured_reaction(self):
        result = required_unobserved_couple(*self.sample(), (3., -10., 0.))
        self.assertEqual(result["required_unobserved_couple_if_equilibrium_Nmm"], (-3., 0., 0.))
        self.assertEqual(result["original_shell_rotational_reaction"], "UNOBSERVED")
        self.assertEqual(result["MPC_constraint_couple"], "UNOBSERVED")

    def test_origin_shift_keeps_required_couple_when_force_closed(self):
        p, load, internal, support, applied = self.sample()
        # Both pressure and support arms shift by the same origin.
        result = required_unobserved_couple(
            p, load, internal, support, applied, (0., 0., 0.), origin=(1., 0., 0.))
        self.assertEqual(result["required_unobserved_couple_if_equilibrium_Nmm"], (0., 0., 0.))

    def test_unbalanced_translations_rejected_before_moment_diagnostic(self):
        p, load, internal, support, applied = self.sample()
        internal[1] = (0., 0., -1.)
        with self.assertRaisesRegex(ValueError, "CARTESIAN_RESULTANT_BALANCE_FAIL"):
            required_unobserved_couple(p, load, internal, support, applied, (0., -10., 0.))

    def test_missing_support_position_and_constraint_rejected(self):
        p, load, internal, support, applied = self.sample()
        with self.assertRaisesRegex(ValueError, "POSITION_COVERAGE_MISMATCH"):
            required_unobserved_couple({1:p[1]}, load, internal, support, applied, (0., -10., 0.))
        with self.assertRaisesRegex(ValueError, "INVALID_CONSTRAINT_COVERAGE"):
            required_unobserved_couple(p, load, internal, {(7,2)}, applied, (0., -10., 0.))

    def test_invalid_pressure_moment_and_node_position_rejected(self):
        p, load, internal, support, applied = self.sample()
        for m in ((0., 0.), (0., float("nan"), 0.), (float("inf"), 0., 0.)):
            with self.subTest(m=m), self.assertRaisesRegex(ValueError, "INVALID_PRESSURE_MOMENT"):
                required_unobserved_couple(p, load, internal, support, applied, m)
        p[1] = (0., float("nan"), 0.)
        with self.assertRaisesRegex(ValueError, "INVALID_MOMENT_VECTOR"):
            required_unobserved_couple(p, load, internal, support, applied, (0., -10., 0.))


if __name__ == "__main__":
    unittest.main()
