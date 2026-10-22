"""Synthetic-only fail-closed bridge negative and CLI tests; never real SGS data."""
from __future__ import annotations
import copy
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from stud_tensile_strength_screen import METHOD
from stud_strength_demand_bridge import (
    PINNED_SOLVER_ARTIFACT_SHA256, PROFILES, STUDY_SCOPE,
    compare_raw_strength_to_synthetic_study, load_verified_research_zip,
    validate_synthetic_study,
)


def dummy_tensile():
    return {'method': METHOD, 'failure_loads': [90., 105., 111., 120.],
            'load_unit': 'kgf', 'safety_factor': 3.,
            'failure_modes': ['STUD_FRACTURE', 'WELD_FAILURE',
                              'STUD_FRACTURE', 'STUD_FRACTURE'],
            'source_sha256': 'a' * 64}


def dummy_study():
    rows=[]
    for n in (8,16):
        for layout, (old_sites, new_sites) in PROFILES.items():
            for kind, k in [('soft',50.),('stiff',500.)]:
                m=len(old_sites)
                forces=[.2 + .001*i for i in range(m)]
                total=math.fsum(forces)
                row={'mesh': n, 'layout': layout, 'case': kind,
                     'station_count': m, 'k_per_station_n_per_mm':k,
                     'moved_positions_mm':list(new_sites),
                     'causal_scope': 'CONTROLLED_INTERIOR_LOCATION_ONLY_SYNTHETIC'}
                for phase in ('baseline','moved'):
                    row[phase]={'station_forces_n':forces.copy(),
                        'sum_station_force_n':total,'peak_station_force_n':max(forces),
                        'rib_end_rf3_n':-total,'rib_reaction_residual_n':0.,
                        'nominal_global_z_residual_n':0.,
                        'center_u3_mm':.012 if phase=='baseline' else .013}
                row['center_u3_change_mm']=.001
                row['center_u3_relative_change_percent']=100*(.001/.012)
                rows.append(row)
    return {'scope':STUDY_SCOPE,'sha256':PINNED_SOLVER_ARTIFACT_SHA256.copy(),
            'engineering_acceptance':'NOT_ADMITTED',
            'synthetic_connector_model':'BILATERAL_Z_SPRING_ONLY',
            'true_stud_and_weld_stiffness_capacity':'NOT_ADMITTED',
            'same_stud_count_and_k':True,'cases':rows}


class Bridge(unittest.TestCase):
    def test_selected_strength_and_peak(self):
        o=compare_raw_strength_to_synthetic_study(dummy_tensile(),dummy_study())
        self.assertEqual(o['test_count'],4)
        self.assertEqual(o['failure_mode_counts']['WELD_FAILURE'],1)
        self.assertAlmostEqual(o['research_only_peak_synthetic_axis_force_n'],.204)
        self.assertEqual(o['engineering_acceptance'],'NOT_ADMITTED')
        self.assertFalse(o['ratio_is_design_check'])
        self.assertEqual(o['tensile_force_direction_at_link'],'NOT_ESTABLISHED')
        self.assertEqual(o['physical_link_stiffness'],'NOT_ESTABLISHED')
        self.assertNotIn('a'*64,json.dumps(o))
    def test_sign_does_not_become_tension(self):
        o=compare_raw_strength_to_synthetic_study(dummy_tensile(),dummy_study())
        self.assertNotIn('PASS',json.dumps(o))
        self.assertNotIn('tensile_utilization',o)
        self.assertFalse(o['ratio_is_design_check'])
    def test_missing_study_case_rejected(self):
        x=dummy_study();x['cases'].pop()
        with self.assertRaisesRegex(ValueError,'STUDY_COVERAGE'):
            validate_synthetic_study(x)
    def test_duplicate_study_case_rejected(self):
        x=dummy_study();x['cases'][1]=copy.deepcopy(x['cases'][0])
        with self.assertRaisesRegex(ValueError,'DUPLICATE_CASE'):
            validate_synthetic_study(x)
    def test_changed_source_sha_rejected(self):
        x=dummy_study();x['sha256']['moved']='b'*64
        with self.assertRaisesRegex(ValueError,'STUDY_PROVENANCE'):
            validate_synthetic_study(x)
    def test_forged_engineering_approval_rejected(self):
        x=dummy_study();x['engineering_acceptance']='PASS'
        with self.assertRaisesRegex(ValueError,'STUDY_PROVENANCE'):
            validate_synthetic_study(x)
    def test_changed_model_rejected(self):
        x=dummy_study();x['synthetic_connector_model']='CALIBRATED'
        with self.assertRaisesRegex(ValueError,'STUDY_PROVENANCE'):
            validate_synthetic_study(x)
    def test_changed_force_detected_by_rib_reaction(self):
        x=dummy_study();x['cases'][0]['moved']['station_forces_n'][0]+=.1
        with self.assertRaisesRegex(ValueError,'STATION_FORCE_BALANCE'):
            validate_synthetic_study(x)
    def test_nonfinite_synthetic_force_rejected(self):
        x=dummy_study();x['cases'][0]['baseline']['station_forces_n'][0]=float('nan')
        with self.assertRaisesRegex(ValueError,'NONFINITE_FORCE'):
            validate_synthetic_study(x)
    def test_negative_force_rejected(self):
        x=dummy_study();x['cases'][0]['baseline']['station_forces_n'][0]=-.1
        with self.assertRaisesRegex(ValueError,'NONPOSITIVE_SYNTHETIC_FORCE'):
            validate_synthetic_study(x)
    def test_wrong_station_count_rejected(self):
        x=dummy_study();x['cases'][0]['station_count']=5
        with self.assertRaisesRegex(ValueError,'STATION_GEOMETRY'):
            validate_synthetic_study(x)
    def test_wrong_stiffness_rejected(self):
        x=dummy_study();x['cases'][0]['k_per_station_n_per_mm']=100.
        with self.assertRaisesRegex(ValueError,'CASE_IDENTITY'):
            validate_synthetic_study(x)
    def test_changed_displacement_rejected(self):
        x=dummy_study();x['cases'][0]['center_u3_relative_change_percent']+=10
        with self.assertRaisesRegex(ValueError,'DISPLACEMENT_CHANGE'):
            validate_synthetic_study(x)
    def test_bad_tensile_input_rejected(self):
        x=dummy_tensile();x['safety_factor']=0
        with self.assertRaisesRegex(ValueError,'STUD_TENSILE_SCREEN_SAFETY_FACTOR'):
            compare_raw_strength_to_synthetic_study(x,dummy_study())
    def test_artifact_hash_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            f=Path(t)/'fake.zip';f.write_bytes(b'not a real zip')
            with self.assertRaisesRegex(ValueError,'ARTIFACT_SHA256'):
                load_verified_research_zip(f)
    def test_missing_zip_rejected(self):
        with self.assertRaisesRegex(ValueError,'ARTIFACT_FILE_BOUNDARY'):
            load_verified_research_zip('/no/such/file.zip')


if __name__=='__main__':unittest.main()
