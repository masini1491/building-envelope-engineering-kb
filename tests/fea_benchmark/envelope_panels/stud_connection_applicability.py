"""Screen *declared* test-specimen relevance to the C3D20R Z-link surrogate.

This matches nominal metadata, not physical equivalence. It never emits
private geometry or curves and never calibrates spring k or stud capacity.
"""
import argparse
import json
import math
from pathlib import Path

from stud_connection_evidence_gate import (
    SCOPE, FIELDS, assess as evidence_screen, load as load_evidence,
)

MODEL = 'C3D20R_SYNTHETIC_Z_SPRING'
TARGET_KEYS = {'scope', 'model', 'interface', 'direction'}
Z_DIRECTIONS = frozenset(('Z_TENSION', 'Z_COMPRESSION'))


def fail(code):
    raise ValueError('STUD_APPLICABILITY_' + code)


def validate_target(target):
    if not isinstance(target, dict) or set(target) != TARGET_KEYS:
        fail('TARGET_SCHEMA')
    if target['scope'] != SCOPE or target['model'] != MODEL:
        fail('TARGET_SCOPE')
    if target['direction'] not in Z_DIRECTIONS:
        fail('MODEL_Z_ONLY')
    body = target['interface']
    if not isinstance(body, dict) or set(body) != set(FIELDS):
        fail('TARGET_INTERFACE_SCHEMA')
    missing = []
    for field in FIELDS:
        value = body[field]
        if value is None:
            missing.append('interface.' + field)
        elif field.endswith('_mm'):
            if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
                fail('TARGET_DIMENSION')
        elif type(value) is not str or not 0 < len(value.strip()) <= 64:
            fail('TARGET_STRING')
    return missing


def compare(target, specimen):
    missing_target = validate_target(target)
    screen = evidence_screen(specimen)
    missing_evidence = list(screen['missing_fields'])
    mismatched = []
    # Equality is literal nominal metadata identity, *not* a dimensional
    # tolerance, weld procedure qualification, or mechanical equivalence.
    for field in FIELDS:
        reference = target['interface'][field]
        claimed = specimen['interface'][field]
        if reference is not None and claimed is not None and reference != claimed:
            mismatched.append('interface.' + field)
    if specimen['direction'] != 'UNKNOWN' and specimen['direction'] != target['direction']:
        mismatched.append('direction')
    if mismatched:
        status = 'DECLARED_SPECIMEN_MODEL_MISMATCH'
    elif missing_target:
        status = 'TARGET_INCOMPLETE'
    elif screen['readiness'] != 'METADATA_AND_CURVE_SCREEN_ONLY':
        status = 'SPECIMEN_EVIDENCE_INCOMPLETE'
    else:
        status = 'NOMINAL_METADATA_MATCH_ONLY'
    return {
        'scope': SCOPE,
        'model': MODEL,
        'screen': status,
        'target_missing_fields': sorted(missing_target),
        'evidence_missing_fields': sorted(missing_evidence),
        'mismatched_fields': sorted(mismatched),
        'specimen_evidence_readiness': screen['readiness'],
        'source_authenticity': 'NOT_VERIFIED',
        'test_fixture_boundary_equivalence': 'NOT_ESTABLISHED',
        'joint_process_equivalence': 'NOT_ESTABLISHED',
        'actual_stud_z_stiffness_n_per_mm': 'NOT_ESTABLISHED',
        'tension_compression_shear_interchangeability': 'NOT_ESTABLISHED',
        'engineering_acceptance': 'NOT_ADMITTED',
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('target_json', type=Path)
    p.add_argument('specimen_evidence_json', type=Path)
    a = p.parse_args()
    report = compare(load_evidence(a.target_json), load_evidence(a.specimen_evidence_json))
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
