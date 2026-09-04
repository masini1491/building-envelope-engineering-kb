import math
import unittest

from scripts.engineering_calc.audit import audit_force_balance, audit_product
from scripts.engineering_calc.beam import BeamElement, simple_span_udl, solve_beam
from scripts.engineering_calc.connection import (
    demand_capacity,
    projected_bearing_stress,
    shear_tension_demand,
    thread_engagement_ratio,
)


class EngineeringCalcExpansionTests(unittest.TestCase):
    def test_simple_span_udl_known_formulas(self):
        result = simple_span_udl(
            span=1000.0,
            line_load=2.0,
            elastic_modulus=70_000.0,
            inertia=1_000_000.0,
        )
        self.assertAlmostEqual(result.reaction_each, 1000.0)
        self.assertAlmostEqual(result.moment_max, 250_000.0)

    def test_general_beam_simple_span_udl_reactions_and_end_moments(self):
        result = solve_beam(
            node_positions=[0.0, 1000.0],
            elements=[BeamElement(0, 1, 70_000.0, 1_000_000.0, udl=-2.0)],
            vertical_restraints=[0, 1],
        )
        self.assertAlmostEqual(result.reactions[0], 1000.0)
        self.assertAlmostEqual(result.reactions[1], 1000.0)
        self.assertAlmostEqual(result.element_end_forces[0].start_moment, 0.0, places=7)
        self.assertAlmostEqual(result.element_end_forces[0].end_moment, 0.0, places=7)

    def test_general_beam_two_span_continuous_symmetry_and_equilibrium(self):
        result = solve_beam(
            node_positions=[0.0, 1000.0, 2000.0],
            elements=[
                BeamElement(0, 1, 70_000.0, 1_000_000.0, udl=-1.0),
                BeamElement(1, 2, 70_000.0, 1_000_000.0, udl=-1.0),
            ],
            vertical_restraints=[0, 1, 2],
        )
        r0, r1, r2 = result.reactions
        self.assertAlmostEqual(r0, r2)
        self.assertAlmostEqual(r0 + r1 + r2, 2000.0)
        self.assertAlmostEqual(result.element_end_forces[0].end_moment, -125000.0)
        self.assertAlmostEqual(result.element_end_forces[1].start_moment, 125000.0)

    def test_general_beam_point_load_at_node(self):
        result = solve_beam(
            node_positions=[0.0, 500.0, 1000.0],
            elements=[
                BeamElement(0, 1, 70_000.0, 1_000_000.0),
                BeamElement(1, 2, 70_000.0, 1_000_000.0),
            ],
            vertical_restraints=[0, 2],
            nodal_forces={1: -1000.0},
        )
        self.assertAlmostEqual(result.reactions[0], 500.0)
        self.assertAlmostEqual(result.reactions[2], 500.0)
        expected_midspan = -1000.0 * 1000.0**3 / (48.0 * 70_000.0 * 1_000_000.0)
        self.assertAlmostEqual(result.displacements[1], expected_midspan)

    def test_general_beam_cantilever_udl(self):
        result = solve_beam(
            node_positions=[0.0, 1000.0],
            elements=[BeamElement(0, 1, 70_000.0, 1_000_000.0, udl=-1.0)],
            vertical_restraints=[0],
            rotational_restraints=[0],
        )
        self.assertAlmostEqual(result.reactions[0], 1000.0)
        self.assertAlmostEqual(result.reaction_moments[0], 500_000.0)

    def test_general_beam_detects_unstable_model(self):
        with self.assertRaises(ValueError):
            solve_beam(
                node_positions=[0.0, 1000.0],
                elements=[BeamElement(0, 1, 70_000.0, 1_000_000.0)],
                vertical_restraints=[],
            )

    def test_connection_arithmetic(self):
        result = demand_capacity(demand=80.0, capacity=100.0)
        self.assertAlmostEqual(result.utilization, 0.8)
        self.assertEqual(result.status, "PASS")
        self.assertAlmostEqual(projected_bearing_stress(force=1000.0, diameter=10.0, thickness=2.0), 50.0)

        demand = shear_tension_demand(
            shear_x=3.0,
            shear_y=4.0,
            tension=6.0,
            shear_capacity=10.0,
            tension_capacity=12.0,
        )
        self.assertAlmostEqual(demand.shear, 5.0)
        self.assertAlmostEqual(demand.shear_utilization, 0.5)
        self.assertAlmostEqual(demand.tension_utilization, 0.5)

        engagement = thread_engagement_ratio(actual_engagement=12.0, required_engagement=10.0)
        self.assertAlmostEqual(engagement.utilization, 10 / 12)
        self.assertEqual(engagement.status, "PASS")

    def test_audit_product_and_force_balance(self):
        product = audit_product(factors=[4.0, 0.7, 1.12], reported=3.136)
        self.assertEqual(product.comparison.status, "MATCH")

        mismatch = audit_product(factors=[4.0, 0.7, 1.12], reported=3.388)
        self.assertEqual(mismatch.comparison.status, "MISMATCH")

        balance = audit_force_balance(applied_forces=[-1000.0], reactions=[500.0, 500.0])
        self.assertEqual(balance.comparison.status, "MATCH")
        self.assertAlmostEqual(balance.residual, 0.0)


if __name__ == "__main__":
    unittest.main()
