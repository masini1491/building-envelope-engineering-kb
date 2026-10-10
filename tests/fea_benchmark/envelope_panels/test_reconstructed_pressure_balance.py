"""Positive and fail-closed coverage for bounded reconstructed Cartesian equilibrium."""
import unittest

from check_reconstructed_pressure_balance import (
    constrained_translations, reconstruct_projected_pressure,
    assess_reconstructed_translational_balance)
from test_expanded_face import expanded_block


class ReconstructedBalanceTests(unittest.TestCase):
    @staticmethod
    def known_geometry():
        nodes = {1:(0.,0.,0.), 2:(10.,0.,0.), 3:(10.,10.,0.), 4:(0.,10.,0.)}
        return nodes, set(nodes)

    def test_fixture_boundary_whitelist(self):
        nodes, edge = self.known_geometry()
        glass = ("synthetic glass simple plate\n*BOUNDARY\nEDGE,3,3,0.\n"
                 "1,1,2,0.\n2,2,2,0.\n*STEP,NLGEOM\n")
        constraints = constrained_translations(glass,nodes,edge,"glass")
        self.assertEqual(constraints, {(1,2),(2,2),(3,2),(4,2),(1,0),(1,1),(2,1)})
        aluminum = "synthetic aluminum clamped plate\n*BOUNDARY\nEDGE,1,6,0.\n*STEP,NLGEOM\n"
        self.assertEqual(len(constrained_translations(aluminum,nodes,edge,"aluminum")), 12)
        with self.assertRaisesRegex(ValueError,"UNSUPPORTED_BOUNDARY_CONFIGURATION"):
            constrained_translations(glass.replace("2,2,2,0.","2,1,2,0."),nodes,edge,"glass")
        with self.assertRaisesRegex(ValueError,"FIXTURE_MATERIAL_MISMATCH"):
            constrained_translations(glass,nodes,edge,"aluminum")

    def test_flat_p1_load_projection(self):
        expanded = {1:tuple(range(21,41))}
        coords = {i+21:xyz for i,xyz in enumerate(expanded_block())}
        disps = {i:(0.,0.,0.) for i in coords}
        mapped,total = reconstruct_projected_pressure(
            [tuple(range(1,9))],expanded,coords,disps,0.25)
        self.assertAlmostEqual(total[2],50.0,places=8)
        self.assertEqual(set(mapped),set(range(1,9)))
        self.assertAlmostEqual(sum(v[2] for v in mapped.values()),50.0,places=8)
        with self.assertRaisesRegex(ValueError,"EXPANDED_COORDINATE_COVERAGE_MISMATCH"):
            reconstruct_projected_pressure(
                [tuple(range(1,9))],expanded,coords,
                {k:v for k,v in disps.items() if k != 21},0.25)

    @staticmethod
    def balanced_case():
        load={1:(0.,0.,25.),2:(0.,0.,75.)}
        internal={1:(0.,0.,-75.),2:(0.,0.,75.)}
        return load,internal,{(1,2)},(0.,0.,100.)

    def test_free_dof_and_support_balance(self):
        result=assess_reconstructed_translational_balance(*self.balanced_case())
        self.assertAlmostEqual(result["reconstructed_support"][2],-100.)
        self.assertEqual(result["relative_global_residual"],0.)
        self.assertEqual(result["relative_max_free_residual"],0.)

    def test_free_dof_perturbation_blocks(self):
        load,internal,constrained,total=self.balanced_case()
        internal[2]=(0.,0.,76.)
        with self.assertRaisesRegex(ValueError,"FREE_TRANSLATION_RESIDUAL_FAIL"):
            assess_reconstructed_translational_balance(load,internal,constrained,total)

    def test_constraint_perturbation_blocks(self):
        load,internal,constrained,total=self.balanced_case()
        internal[1]=(0.,0.,-74.)
        with self.assertRaisesRegex(ValueError,"CARTESIAN_RESULTANT_BALANCE_FAIL"):
            assess_reconstructed_translational_balance(load,internal,constrained,total)

    def test_incomplete_and_nonfinite_data_blocks(self):
        load,internal,constrained,total=self.balanced_case()
        with self.assertRaisesRegex(ValueError,"NALL_INTERNAL_PRESSURE_COVERAGE_MISMATCH"):
            assess_reconstructed_translational_balance(load,{1:internal[1]},constrained,total)
        with self.assertRaisesRegex(ValueError,"INCONSISTENT_PRESSURE_RESULTANT"):
            assess_reconstructed_translational_balance(load,internal,constrained,(0.,0.,101.))
        with self.assertRaisesRegex(ValueError,"NONFINITE_NODE_FORCE"):
            assess_reconstructed_translational_balance(
                load,{1:internal[1],2:(0.,0.,float("nan"))},constrained,total)
        with self.assertRaisesRegex(ValueError,"INCOMPLETE_OR_INVALID_CONSTRAINT_COVERAGE"):
            assess_reconstructed_translational_balance(load,internal,{(3,2)},total)


if __name__=="__main__":
    unittest.main()
