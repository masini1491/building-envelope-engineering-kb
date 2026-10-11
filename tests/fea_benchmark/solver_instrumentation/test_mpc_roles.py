"""Synthetic guards for isolated Stage 28 role trace."""
import tempfile
import unittest
from pathlib import Path
from ccx_mpc_role_probe import patch
from check_mpc_roles import parse_roles,compare

class RoleTests(unittest.TestCase):
    valid=("ROLE_TERM,3,1,10,1,0,4,1\n"
           "ROLE_TERM,3,2,20,1,1,4,1\n"
           "ROLE_TERM,3,3,21,2,2,4,1\n"
           "ROLE_END,3,3,20,21,4,1\n")
    terms=("CALL,1,3\nTERM,1,3,1,10,1,1.5,4\n"
           "TERM,1,3,2,20,1,-2,4\n"
           "TERM,1,3,3,21,2,1,4\nEND,1,3\n")
    def test_valid(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/"roles";b=Path(d)/"terms"
            a.write_text(self.valid);b.write_text(self.terms)
            result=compare(a,b)
            self.assertEqual((result["regular_terms"],result["angle_axis_terms"],result["inhomogeneous_terms"]),(1,1,1))
    def test_missing_end(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/"roles";a.write_text(self.valid.split("ROLE_END")[0])
            with self.assertRaisesRegex(ValueError,"ROLE_TRACE_INCOMPLETE"):parse_roles(a)
    def test_missing_helper(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/"roles";a.write_text(self.valid.replace(",10,1,0,",",10,1,1,"))
            with self.assertRaisesRegex(ValueError,"HELPER_ROLE_MULTIPLICITY"):parse_roles(a)
    def test_wrong_term_node(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/"roles";b=Path(d)/"terms"
            a.write_text(self.valid);b.write_text(self.terms.replace("3,1,10,1","3,1,11,1"))
            with self.assertRaisesRegex(ValueError,"TERM_NODE_DOF_IDENTITY"):compare(a,b)
    def test_unknown_source(self):
        with self.assertRaisesRegex(ValueError,"UNRECOGNIZED"):patch("unknown source")

if __name__=="__main__":unittest.main()
