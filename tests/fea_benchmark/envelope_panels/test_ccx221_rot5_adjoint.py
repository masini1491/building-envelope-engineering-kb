"""Deterministic tests of the inverse-kinematic virtual-work crosscheck."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from verify_ccx221_rot5_adjoint import (audit_case, make_kinematic_tangent)


class TestAdjoint(unittest.TestCase):
    def test_synthetic_coupled_mpc(self):
        work = {
            'fn': {(1, 1): (4.0, -1), (2, 1): (-1.0, 7)},
            'mpcs': {1: {'tag': 'OTHER', 'terms': [(1, 1, 1.0), (2, 1, -2.0)]}},
        }
        result = audit_case(work, {(2, 1): 3.0})
        self.assertAlmostEqual(result['raw_fn_virtual_work_nmm'], 21.0)
        self.assertAlmostEqual(result['raw_minus_reduced_nmm'], 0.0)
        self.assertEqual(result['max_mpc_tangent_residual'], 0.0)
    def test_cascaded_mpc(self):
        work = {
            'fn': {(1, 1): (2.0, -1), (2, 1): (3.0, -3)},
            'mpcs': {
                1: {'tag': 'OTHER', 'terms': [(1, 1, 1.0), (2, 1, -1.0)]},
                2: {'tag': 'OTHER', 'terms': [(2, 1, 1.0), (3, 1, -2.0)]},
            },
        }
        result = audit_case(work, {(3, 1): 1.0})
        self.assertEqual(result['raw_fn_virtual_work_nmm'], 10.0)
    def test_reverse_mode(self):
        work = {'fn': {(1, 1): (4., 0)},
                'mpcs': {1: {'tag': 'OTHER', 'terms': [(1, 1, 1.), (2, 1, -2.)]}}}
        result = audit_case(work, {(2, 1): -3.})
        self.assertEqual(result['raw_fn_virtual_work_nmm'], -24.)
    def test_reject_empty_seeds(self):
        with self.assertRaisesRegex(ValueError, 'ADJOINT_EMPTY_SEEDS'):
            make_kinematic_tangent({'mpcs': {}}, {})
    def test_reject_duplicated_dependent_seed(self):
        work = {'mpcs': {1: {'tag': 'OTHER', 'terms': [(1, 1, 1.), (2, 1, 1.)]}}}
        with self.assertRaisesRegex(ValueError, 'ADJOINT_DEPENDENT_COLLISION'):
            make_kinematic_tangent(work, {(1, 1): 1.})
    def test_reject_invalid_coefficient(self):
        work = {'mpcs': {1: {'tag': 'OTHER', 'terms': [(1, 1, 0.), (2, 1, 1.)]}}}
        with self.assertRaisesRegex(ValueError, 'ADJOINT_INVALID_TRANSLATION_MPC'):
            make_kinematic_tangent(work, {(2, 1): 1.})
    def test_reject_nonfinite_seed(self):
        with self.assertRaisesRegex(ValueError, 'ADJOINT_NONFINITE_SEED'):
            make_kinematic_tangent({'mpcs': {}}, {(1, 1): float('nan')})
    def test_rotational_dependent_skipped(self):
        work = {'fn': {(1, 1): (3., 1)}, 'mpcs': {1: {'tag': 'OTHER',
                'terms': [(1, 5, 1.), (2, 1, 1.)]}}}
        v, residual = make_kinematic_tangent(work, {(2, 1): 1.})
        self.assertEqual(v[(2, 1)], 1.)
        self.assertEqual(residual, 0.)
    def test_reject_nonphysical_direction(self):
        with self.assertRaisesRegex(ValueError, 'ADJOINT_SEED_OWNER'):
            make_kinematic_tangent({'mpcs': {}}, {(1, 5): 1.})


if __name__ == '__main__':
    unittest.main()
