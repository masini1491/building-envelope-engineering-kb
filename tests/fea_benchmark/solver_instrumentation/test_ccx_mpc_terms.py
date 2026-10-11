"""Stage 26 MEANROT MPC trace fail-closed synthetic tests."""
import unittest
import tempfile
from pathlib import Path
from ccx_mpc_terms import append_patch,parse_terms

class Tests(unittest.TestCase):
    def test_patch_gate(self):
        raw='MPC_TRACE_V1\n    return;\n\n}\n'
        changed=append_patch(raw)
        self.assertIn('MPC_TERMS_FILE',changed)
        with self.assertRaisesRegex(ValueError,'ALREADY_STAGE26'):
            append_patch(changed)
        with self.assertRaisesRegex(ValueError,'STAGE25_SOURCE'):
            append_patch('not stage25')
    def test_trace_valid(self):
        data='CALL,1,8\nTERM,1,3,1,100,1,2.5,4.0\nTERM,1,3,2,200,1,-2.5,4.0\nEND,1,2\n'
        with tempfile.TemporaryDirectory() as p:
            f=Path(p)/'t';f.write_text(data)
            result=parse_terms(f)
            self.assertEqual((result['calls'],result['final_mpc_count'],result['final_term_count']),(1,1,2))
    def test_missing_final_terms(self):
        with tempfile.TemporaryDirectory() as p:
            f=Path(p)/'t';f.write_text('CALL,1,8\nEND,1,0\n')
            with self.assertRaisesRegex(ValueError,'FINAL_MEANROT'):
                parse_terms(f)
    def test_invalid_value(self):
        with tempfile.TemporaryDirectory() as p:
            f=Path(p)/'t';f.write_text('CALL,1,8\nTERM,1,3,1,100,1,nan,4.0\nEND,1,1\n')
            with self.assertRaisesRegex(ValueError,'INVALID_TERM_RECORD'):
                parse_terms(f)
    def test_truncated_call(self):
        with tempfile.TemporaryDirectory() as p:
            f=Path(p)/'t';f.write_text('CALL,1,8\n')
            with self.assertRaisesRegex(ValueError,'TRUNCATED'):
                parse_terms(f)
if __name__=='__main__':unittest.main()
