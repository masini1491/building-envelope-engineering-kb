"""Fail-closed test suite for isolated GPL diagnostic insertion."""
import tempfile
from pathlib import Path
import unittest
from ccx_mpc_probe import patch, read_trace

class DiagnosticTests(unittest.TestCase):
    def test_patch_is_only_appendix(self):
        source='#include "CalculiX.h"\nfn[0]=0;\n    return;\n\n}\n'
        result=patch(source)
        self.assertIn('MPC_TRACE_V1',result)
        self.assertIn('fn[0]=0;',result)
        self.assertEqual(result.count('return;'),1)

    def test_double_and_unknown_source_blocked(self):
        with self.assertRaisesRegex(ValueError,'UNRECOGNIZED'):
            patch('wrong version')
        source='#include "CalculiX.h"\n    return;\n\n}\n'
        with self.assertRaisesRegex(ValueError,'ALREADY_INSTRUMENTED'):
            patch(patch(source))

    def test_valid_meanrot_trace(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'trace'
            p.write_text('MPC_TRACE_V1,1,30,12,1.5\nMPC_TRACE_V1,2,30,12,0.25\n')
            result=read_trace(p)
            self.assertEqual(result['maximum_observed_MEANROT_count'],12)

    def test_no_meanrot_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'trace'
            p.write_text('MPC_TRACE_V1,1,10,0,0\n')
            with self.assertRaisesRegex(ValueError,'MEANROT_MPC_NOT_OBSERVED'):
                read_trace(p)

    def test_corrupt_and_nonfinite_refuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'trace'
            for content in ('MPC_TRACE_V1,2,12,4,1\n','MPC_TRACE_V1,1,12,4,nan\n'):
                p.write_text(content)
                with self.subTest(content=content),self.assertRaisesRegex(ValueError,'INVALID_MPC_TRACE_VALUE'):
                    read_trace(p)

if __name__ == "__main__":
    unittest.main()
