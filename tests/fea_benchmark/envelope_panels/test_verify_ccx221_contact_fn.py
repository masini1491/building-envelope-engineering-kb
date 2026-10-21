"""Fail-closed synthetic tests for the contact fn-only output verifier."""
import unittest
from verify_ccx221_contact_fn import parse_trace, original_nodes, sta_increments


def block(nk=2, mt=4, inc=1, fn3=(1.,-1.), owners=(0,0)):
    lines=[f'KB_OUTPUT_FN_BEGIN 1 {inc} {nk} {mt}']
    for node in range(1,nk+1):
        for dof in range(mt):
            lines.append(f'KB_OUTPUT_FN {node} {dof} {fn3[node-1] if dof==3 else 0} {owners[node-1] if dof==3 else 0}')
    lines.append('KB_OUTPUT_FN_END')
    return lines

class OutputFnTests(unittest.TestCase):
    def test_original_and_expanded_distinguished(self):
        rows=parse_trace(block(),1)
        self.assertEqual(rows[0]['original_fn3_n'],1.)
        self.assertEqual(rows[0]['expanded_fn3_n'],-1.)
        self.assertEqual(rows[0]['all_fn3_n'],0.)
    def test_active_owner_is_observation_only(self):
        rows=parse_trace(block(owners=(1,-2)),1)
        self.assertEqual((rows[0]['active_dof3_count'],rows[0]['inactive_dof3_count']), (1,1))
    def test_multiple_increment_owners_may_change(self):
        rows=parse_trace(block(owners=(1,-1))+block(inc=2,owners=(0,-2)),1)
        self.assertEqual(len(rows),2)
    def test_wrong_increment_rejected(self):
        with self.assertRaisesRegex(ValueError,'WRONG_INCREMENT'):
            parse_trace(block(inc=2),1)
    def test_wrong_node_order_rejected(self):
        trace=block(); trace[1]=trace[1].replace('KB_OUTPUT_FN 1 0','KB_OUTPUT_FN 2 0')
        with self.assertRaisesRegex(ValueError,'BAD_ROW_INDEX'):
            parse_trace(trace,1)
    def test_nonfinite_rejected(self):
        trace=block();trace[4]=trace[4].replace(' 1.0 ', ' nan ')
        with self.assertRaisesRegex(ValueError,'BAD_ROW_INDEX_OR_FORCE'):
            parse_trace(trace,1)
    def test_truncated_rejected(self):
        with self.assertRaisesRegex(ValueError,'TRUNCATED'):
            parse_trace(block()[:5],1)
    def test_missing_end_rejected(self):
        with self.assertRaisesRegex(ValueError,'BAD_END'):
            parse_trace(block()[:-1],1)
    def test_node_coverage(self):
        good='*HEADING\n*NODE\n1,0,0,0\n2,1,0,0\n*ELEMENT,TYPE=S8R\n'
        self.assertEqual(original_nodes(good),2)
        with self.assertRaisesRegex(ValueError,'NODE_COVERAGE'):
            original_nodes(good.replace('2,1,0,0','3,1,0,0'))
    def test_incomplete_sta_rejected(self):
        with self.assertRaisesRegex(ValueError,'INCOMPLETE_STA'):
            sta_increments('1 1 1 4 0.1 0.1 0.1')
if __name__=='__main__':unittest.main()
