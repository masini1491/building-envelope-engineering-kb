"""Fixture-only negative tests for nominal C3D20R stud evidence relevance."""
import json
import unittest
from stud_connection_applicability import MODEL, compare, validate_target
from stud_connection_evidence_gate import FIELDS, SCOPE

def interface():
    return dict(panel_alloy_temper='SYNTHETIC-PANEL',
                rib_alloy_temper='SYNTHETIC-RIB',
                panel_thickness_mm=3.0, rib_thickness_mm=3.0,
                stud_diameter_mm=4.0, joining_process='SYNTHETIC-PROCESS')
def target():
    return dict(scope=SCOPE, model=MODEL, interface=interface(),direction='Z_TENSION')
def specimen():
    return dict(scope=SCOPE, source_class='LAB_TEST',
                source_sha256='a'*64, interface=interface(),
                direction='Z_TENSION', specimen_count=3,
                force_slip_pairs=[[0,0],[.1,1],[.2,2]])

class ApplicabilityTests(unittest.TestCase):
    def test_nominal_match_not_admission(self):
        r=compare(target(),specimen())
        self.assertEqual(r['screen'],'NOMINAL_METADATA_MATCH_ONLY')
        self.assertEqual(r['actual_stud_z_stiffness_n_per_mm'],'NOT_ESTABLISHED')
        self.assertEqual(r['engineering_acceptance'],'NOT_ADMITTED')
        self.assertEqual(r['test_fixture_boundary_equivalence'],'NOT_ESTABLISHED')
        self.assertNotIn('SYNTHETIC-',json.dumps(r))
    def test_panel_thickness_mismatch(self):
        v=specimen();v['interface']['panel_thickness_mm']=6
        self.assertIn('interface.panel_thickness_mm',compare(target(),v)['mismatched_fields'])
    def test_rib_thickness_mismatch(self):
        v=specimen();v['interface']['rib_thickness_mm']=4
        self.assertIn('interface.rib_thickness_mm',compare(target(),v)['mismatched_fields'])
    def test_diameter_mismatch(self):
        v=specimen();v['interface']['stud_diameter_mm']=10
        self.assertIn('interface.stud_diameter_mm',compare(target(),v)['mismatched_fields'])
    def test_alloy_mismatch(self):
        v=specimen();v['interface']['rib_alloy_temper']='OTHER'
        self.assertIn('interface.rib_alloy_temper',compare(target(),v)['mismatched_fields'])
    def test_joining_process_mismatch(self):
        v=specimen();v['interface']['joining_process']='OTHER'
        self.assertIn('interface.joining_process',compare(target(),v)['mismatched_fields'])
    def test_shear_vs_axial(self):
        v=specimen();v['direction']='IN_PLANE_SHEAR'
        self.assertEqual(compare(target(),v)['mismatched_fields'],['direction'])
    def test_compression_vs_tension(self):
        v=specimen();v['direction']='Z_COMPRESSION'
        self.assertEqual(compare(target(),v)['screen'],'DECLARED_SPECIMEN_MODEL_MISMATCH')
    def test_shear_target_not_admitted(self):
        v=target();v['direction']='IN_PLANE_SHEAR'
        with self.assertRaisesRegex(ValueError,'MODEL_Z_ONLY'):validate_target(v)
    def test_partial_target(self):
        v=target();v['interface']['stud_diameter_mm']=None
        self.assertEqual(compare(v,specimen())['screen'],'TARGET_INCOMPLETE')
    def test_partial_evidence(self):
        v=specimen();v['source_sha256']=None
        self.assertEqual(compare(target(),v)['screen'],'SPECIMEN_EVIDENCE_INCOMPLETE')
    def test_single_specimen(self):
        v=specimen();v['specimen_count']=1
        self.assertIn('multi_specimen_repeatability',compare(target(),v)['evidence_missing_fields'])
    def test_no_evidence_conflict(self):
        v=specimen();v['source_class']='NO_EVIDENCE'
        with self.assertRaisesRegex(ValueError,'SOURCE_CLASS_CONFLICT'):compare(target(),v)
    def test_corrupted_curve(self):
        v=specimen();v['force_slip_pairs']=[[0,0],[.1,2],[.2,1]]
        with self.assertRaisesRegex(ValueError,'CURVE_ORDER'):compare(target(),v)
    def test_nan_target(self):
        v=target();v['interface']['panel_thickness_mm']=float('nan')
        with self.assertRaisesRegex(ValueError,'TARGET_DIMENSION'):compare(v,specimen())
    def test_extra_authority_field(self):
        v=target();v['approved_stiffness_n_mm']=500
        with self.assertRaisesRegex(ValueError,'TARGET_SCHEMA'):compare(v,specimen())
if __name__=='__main__':unittest.main()
