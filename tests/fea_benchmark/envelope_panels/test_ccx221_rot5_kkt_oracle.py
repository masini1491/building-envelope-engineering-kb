"""Independent external-work oracle tests; not CalculiX acceptance tests."""
from fractions import Fraction as F
import unittest
from verify_ccx221_rot5_kkt_oracle import (
    exact_constraint_work, reference_48, reference_inhomogeneous, reference_rectangular_mpc, solve)

class TestVirtualWork(unittest.TestCase):
    def test_force_couple_48_nmm(self):
        r=reference_48()
        self.assertEqual(r['dual_power'],F(48))
        self.assertEqual(r['applied_power'],F(48))
        self.assertEqual(r['energy_power'],F(48))
        self.assertEqual(r['external_power'],0)
        self.assertEqual(r['lam'],[F(24,100),F(-24,100)])
    def test_rectangular_mpc_exact_analytic_solution(self):
        r=reference_rectangular_mpc()
        self.assertEqual(r['u'][2],F(19,10500))
        self.assertEqual(r['tangent'],[F(-900,7),F(500,7),F(-200,7)])
        self.assertEqual(r['external_power'],F(-200,7))
        self.assertEqual(r['energy_power'],F(456,7))
        self.assertEqual(r['dual_power'],F(656,7))
        self.assertEqual(r['dual_power'],r['applied_power'])
    def test_rectangular_mpc_rejects_redundant_constraint(self):
        with self.assertRaisesRegex(ValueError,'KKT_SINGULAR'):
            exact_constraint_work([[1,0,0],[0,1,0],[0,0,1]],
                                  [[1,0,-1],[2,0,-2]],
                                  [0,0,0],[0,0],[1,2])
    def test_rectangular_mpc_constraint_sign_change_is_invariant(self):
        r=reference_rectangular_mpc()
        a=F(100);theta=F(1,50000)
        flip=exact_constraint_work([[F(120),0,0],[0,F(240),0],[0,0,F(60)]],
                                  [[-1,0,1],[0,1,-1]],
                                  [F(0),F(0),F(1)],
                                  [a*theta,a*theta],[a,a])
        self.assertEqual(flip['dual_power'],r['dual_power'])
        self.assertEqual(flip['external_power'],r['external_power'])
    def test_negative_rotation_reverses_couple(self):
        k=F(120); theta=-F(1,50000);a=F(100)
        r=exact_constraint_work([[k,0],[0,k]],[[1,0],[0,1]],[0,0],
                                [-a*theta,a*theta],[-a,a])
        self.assertEqual(r['dual_power'],-F(48))
    def test_inhomogeneous_spc_and_external_power_not_conflated(self):
        r=reference_inhomogeneous()
        self.assertEqual(r['external_power'],F(2))
        self.assertEqual(r['energy_power']-r['dual_power'],F(2))
        self.assertEqual(r['applied_power'],r['dual_power'])
        self.assertNotEqual(r['energy_power'],r['dual_power'])
    def test_spc_gradient_omission_detected(self):
        r=reference_inhomogeneous()
        wrong_gradient=[F(-100),F(100),F(0)]
        self.assertNotEqual(-sum((l*v for l,v in zip(r['lam'],wrong_gradient)),F(0)),r['dual_power'])
    def test_sign_inversion_detected(self):
        r=reference_48()
        bad=sum((l*x for l,x in zip(r['lam'],[F(-100),F(100)])),F(0))
        self.assertEqual(bad,-F(48))
        self.assertNotEqual(bad,r['dual_power'])
    def test_singular_matrix_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'KKT_SINGULAR'):
            solve([[1,1],[2,2]],[1,2])
    def test_dimension_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'KKT_SHAPE'):
            exact_constraint_work([[1]],[[1,0]],[0],[1],[1])
    def test_asymmetric_stiffness_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'KKT_ASYMMETRIC'):
            exact_constraint_work([[1,1],[0,1]],[[1,0],[0,1]],[0,0],[0,0],[1,1])
    def test_external_load_contributes_to_generalized_force(self):
        k=F(120); theta=F(1,50000); a=F(100)
        f=[F(1),F(-1)]
        r=exact_constraint_work([[k,0],[0,k]],[[1,0],[0,1]],f,
                                [-a*theta,a*theta],[-a,a])
        self.assertEqual(r['external_power'],-F(200))
        self.assertEqual(r['dual_power'],F(248))

if __name__=='__main__':unittest.main()
