"""Fail-closed source and connection stiffness evidence boundary tests."""
import json
import tempfile
import unittest
from pathlib import Path
from stud_connection_evidence_gate import assess, load, SCOPE, FIELDS


def fixture():
    return {
        'scope':SCOPE, 'source_class':'NO_EVIDENCE', 'source_sha256':None,
        'interface':{k:None for k in FIELDS},'direction':'UNKNOWN',
        'specimen_count':None,'force_slip_pairs':[],
    }


class EvidenceGateTest(unittest.TestCase):
    def test_empty_stays_not_admitted(self):
        v=assess(fixture())
        self.assertEqual(v['readiness'],'MISSING_INPUT')
        self.assertEqual(v['engineering_acceptance'],'NOT_ADMITTED')
        self.assertIn('interface.stud_diameter_mm',v['missing_fields'])
    def test_declared_curve_is_not_calibrated(self):
        x=fixture()
        x.update(source_class='MANUFACTURER_DECLARATION',source_sha256='a'*64,
                 direction='Z_TENSION',specimen_count=3,
                 force_slip_pairs=[[0,0],[.1,1],[.2,2]])
        for k in FIELDS:
            x['interface'][k]=3.0 if k.endswith('_mm') else 'SYNTHETIC'
        v=assess(x)
        self.assertEqual(v['readiness'],'METADATA_AND_CURVE_SCREEN_ONLY')
        self.assertEqual(v['physical_connection_stiffness_n_per_mm'],'NOT_ESTABLISHED')
        self.assertEqual(v['source_authenticity'],'NOT_VERIFIED')
        self.assertNotIn('SYNTHETIC',json.dumps(v))
        self.assertNotIn('0.1',json.dumps(v))
    def test_duplicate_json_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.json';p.write_text('{"scope":"a","scope":"b"}')
            with self.assertRaisesRegex(ValueError,'DUPLICATE_KEY'):load(p)
    def test_nonfinite_json_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.json';p.write_text('{"x":NaN}')
            with self.assertRaisesRegex(ValueError,'NONFINITE_JSON'):load(p)
    def test_source_class_conflict_rejected(self):
        x=fixture();x['force_slip_pairs']=[[0,0],[.1,1],[.2,2]]
        with self.assertRaisesRegex(ValueError,'SOURCE_CLASS_CONFLICT'):assess(x)
    def test_nonmonotonic_curve_rejected(self):
        x=fixture();x['source_class']='LAB_TEST';x['force_slip_pairs']=[[0,0],[.1,2],[.2,1]]
        with self.assertRaisesRegex(ValueError,'CURVE_ORDER'):assess(x)
    def test_zero_and_negative_stiffness_not_inferred(self):
        x=fixture();x['source_class']='LAB_TEST';x['force_slip_pairs']=[[0,0],[.1,0],[.2,0]]
        with self.assertRaisesRegex(ValueError,'CURVE_NO_TRANSFER'):assess(x)
    def test_bad_dimensions_rejected(self):
        x=fixture();x['interface']['stud_diameter_mm']=-1
        with self.assertRaisesRegex(ValueError,'INVALID_POSITIVE_VALUE'):assess(x)
    def test_negative_count_rejected(self):
        x=fixture();x['specimen_count']=-2
        with self.assertRaisesRegex(ValueError,'SPECIMEN_COUNT'):assess(x)
    def test_invalid_direction_rejected(self):
        x=fixture();x['direction']='BENDING_PLUS_SHEAR'
        with self.assertRaisesRegex(ValueError,'DIRECTION'):assess(x)
    def test_reject_unknown_schema_keys(self):
        x=fixture();x['design_stiffness_n_mm']=123
        with self.assertRaisesRegex(ValueError,'SCHEMA'):assess(x)
    def test_invalid_digest_rejected(self):
        x=fixture();x['source_sha256']='not-a-hash'
        with self.assertRaisesRegex(ValueError,'SOURCE_DIGEST_FORMAT'):assess(x)


if __name__=='__main__':unittest.main()
