"""Stage 24 force-to-couple partition synthetic oracles and failure guards."""
import unittest
from check_expanded_moment_partition import partition_moment

class PartitionTests(unittest.TestCase):
    def input(self):
        original=[tuple(range(1,9))]
        expanded={1:tuple(range(21,41))}
        shell={i:(0.,0.,0.) for i in range(1,9)}
        positions={i:(0.,0.,0.) for i in range(21,41)}
        force={i:(0.,0.,0.) for i in range(21,41)}
        return original,expanded,shell,positions,force

    def test_pure_couple_hidden_by_force_projection(self):
        o,e,s,p,f=self.input()
        # expanded slots 0,16 both map to original shell node 1.
        p[21]=(0.,0.,1.);p[37]=(0.,0.,-1.)
        f[21]=(2.,0.,0.);f[37]=(-2.,0.,0.)
        x=partition_moment(o,e,s,p,f)
        self.assertEqual(x["projected_shell_force_moment_Nmm"],(0.,0.,0.))
        self.assertEqual(x["expanded_relative_geometric_couple_Nmm"],(0.,4.,0.))
        self.assertEqual(x["expanded_total_moment_Nmm"],(0.,4.,0.))
        self.assertEqual(x["rotational_reaction"],"UNOBSERVED")

    def test_shell_arm_and_layer_couple_recombine(self):
        o,e,s,p,f=self.input()
        s[1]=(10.,0.,0.);p[21]=(10.,0.,2.);f[21]=(0.,3.,0.)
        x=partition_moment(o,e,s,p,f)
        self.assertEqual(x["projected_shell_force_moment_Nmm"],(0.,0.,30.))
        self.assertEqual(x["expanded_relative_geometric_couple_Nmm"],(-6.,0.,0.))
        self.assertEqual(x["expanded_total_moment_Nmm"],(-6.,0.,30.))

    def test_incomplete_expanded_positions_fail(self):
        o,e,s,p,f=self.input();del p[21]
        with self.assertRaisesRegex(ValueError,"COVERAGE_MISMATCH"):
            partition_moment(o,e,s,p,f)

    def test_incomplete_shell_position_fail(self):
        o,e,s,p,f=self.input();del s[1]
        with self.assertRaisesRegex(ValueError,"COVERAGE_MISMATCH"):
            partition_moment(o,e,s,p,f)

    def test_nonfinite_force_fails(self):
        o,e,s,p,f=self.input();f[21]=(float('nan'),0.,0.)
        with self.assertRaisesRegex(ValueError,"NONFINITE"):
            partition_moment(o,e,s,p,f)

if __name__=="__main__":
    unittest.main()
