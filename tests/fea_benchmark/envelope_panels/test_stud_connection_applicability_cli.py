"""Command-line contract checks for the public synthetic stud applicability screen.

No project or vendor records; all fixtures use non-identifying dummy values.
Run the actual Python executable rather than calling compare() directly.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from stud_connection_evidence_gate import FIELDS, SCOPE
from stud_connection_applicability import MODEL

CLI = Path(__file__).with_name('stud_connection_applicability.py')


def dummy_interface():
    return {
        'panel_alloy_temper': 'DUMMY-PANEL',
        'rib_alloy_temper': 'DUMMY-RIB',
        'panel_thickness_mm': 3.0,
        'rib_thickness_mm': 3.0,
        'stud_diameter_mm': 4.0,
        'joining_process': 'DUMMY-JOIN',
    }


def target():
    return {'scope': SCOPE, 'model': MODEL, 'interface': dummy_interface(),
            'direction': 'Z_TENSION'}


def specimen():
    return {'scope': SCOPE, 'source_class': 'LAB_TEST',
            'source_sha256': 'a' * 64, 'interface': dummy_interface(),
            'direction': 'Z_TENSION', 'specimen_count': 3,
            'force_slip_pairs': [[0.0, 0.0], [0.123456, 1.234567],
                                 [0.234567, 2.345678]]}


class TestCLI(unittest.TestCase):
    def run_cli(self, tgt=None, spc=None, *, raw_target=None, raw_specimen=None):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            a, b = path / 'model.json', path / 'specimen.json'
            a.write_text(raw_target if raw_target is not None else json.dumps(
                target() if tgt is None else tgt), encoding='utf-8')
            b.write_text(raw_specimen if raw_specimen is not None else json.dumps(
                specimen() if spc is None else spc), encoding='utf-8')
            return subprocess.run([sys.executable, '-B', str(CLI), str(a), str(b)],
                                  capture_output=True, text=True, timeout=10)

    def test_nominal_match_uses_real_cli(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['screen'], 'NOMINAL_METADATA_MATCH_ONLY')
        self.assertEqual(report['engineering_acceptance'], 'NOT_ADMITTED')
        self.assertEqual(report['actual_stud_z_stiffness_n_per_mm'], 'NOT_ESTABLISHED')
        self.assertEqual(report['source_authenticity'], 'NOT_VERIFIED')

    def test_nominal_match_does_not_expose_inputs(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        for private_fragment in ('DUMMY-PANEL', 'DUMMY-RIB', 'DUMMY-JOIN',
                                 '0.123456', '1.234567', '0.234567', '2.345678',
                                 'a' * 64):
            with self.subTest(fragment=private_fragment[:14]):
                self.assertNotIn(private_fragment, result.stdout)

    def test_shear_specimen_is_flagged_not_equated_to_z(self):
        s = specimen()
        s['direction'] = 'IN_PLANE_SHEAR'
        result = self.run_cli(spc=s)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['screen'], 'DECLARED_SPECIMEN_MODEL_MISMATCH')
        self.assertIn('direction', report['mismatched_fields'])
        self.assertEqual(report['engineering_acceptance'], 'NOT_ADMITTED')

    def test_diameter_mismatch_is_flagged(self):
        s = specimen()
        s['interface']['stud_diameter_mm'] = 5
        result = self.run_cli(spc=s)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertIn('interface.stud_diameter_mm', report['mismatched_fields'])

    def test_missing_curve_is_not_admitted(self):
        s = specimen()
        s['force_slip_pairs'] = []
        result = self.run_cli(spc=s)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['screen'], 'SPECIMEN_EVIDENCE_INCOMPLETE')
        self.assertIn('force_slip_pairs', report['evidence_missing_fields'])
        self.assertEqual(report['actual_stud_z_stiffness_n_per_mm'], 'NOT_ESTABLISHED')

    def test_target_wrong_shape_returns_error(self):
        result = self.run_cli(raw_target='{"scope":"WRONG"}')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('STUD_APPLICABILITY_TARGET_SCHEMA', result.stderr)
        self.assertNotIn('"engineering_acceptance":', result.stdout)

    def test_duplicate_target_key_returns_error(self):
        result = self.run_cli(raw_target='{"scope":"one","scope":"two"}')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('STUD_EVIDENCE_DUPLICATE_KEY', result.stderr)

    def test_nonfinite_target_returns_error(self):
        raw = json.dumps(target()).replace('"panel_thickness_mm": 3.0',
                                           '"panel_thickness_mm": NaN')
        result = self.run_cli(raw_target=raw)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('STUD_EVIDENCE_NONFINITE_JSON', result.stderr)

    def test_bad_curve_returns_error(self):
        s = specimen()
        s['force_slip_pairs'] = [[0, 0], [0.1, 2], [0.2, 1]]
        result = self.run_cli(spc=s)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('STUD_EVIDENCE_CURVE_ORDER', result.stderr)

    def test_no_source_conflict_returns_error(self):
        s = specimen()
        s['source_class'] = 'NO_EVIDENCE'
        result = self.run_cli(spc=s)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('STUD_EVIDENCE_SOURCE_CLASS_CONFLICT', result.stderr)


if __name__ == '__main__':
    unittest.main()
