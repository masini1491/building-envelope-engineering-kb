"""Fail-closed aluminum sheet / U-rib stud-weld connection input readiness.

This does not calibrate a spring, approve a weld, or validate external source
truth. A passing shape/curve screen is NEVER engineering admission.
Input is read locally; output contains no source identifiers, private values,
or raw force/displacement points.
"""
import argparse
import json
import math
from pathlib import Path

SCOPE = 'ALUMINUM_PANEL_TO_U_RIB_STUD_CONNECTION'
CLASSES = {'NO_EVIDENCE', 'MANUFACTURER_DECLARATION', 'LAB_TEST'}
DIRECTIONS = {'UNKNOWN', 'Z_TENSION', 'Z_COMPRESSION', 'IN_PLANE_SHEAR'}
FIELDS = ('panel_alloy_temper', 'rib_alloy_temper', 'panel_thickness_mm',
          'rib_thickness_mm', 'stud_diameter_mm', 'joining_process')
REQUIRED = {'scope', 'source_class', 'source_sha256', 'interface',
            'direction', 'specimen_count', 'force_slip_pairs'}


def fail(code):
    raise ValueError('STUD_EVIDENCE_' + code)


def load(path):
    p = Path(path)
    if p.is_symlink() or not p.is_file() or not 0 < p.stat().st_size <= 16384:
        fail('FILE_BOUNDARY')
    def no_duplicates(pairs):
        out = {}
        for k, v in pairs:
            if k in out:fail('DUPLICATE_KEY')
            out[k] = v
        return out
    def no_constant(_):fail('NONFINITE_JSON')
    return json.loads(p.read_text(encoding='utf-8'), object_pairs_hook=no_duplicates,
                      parse_constant=no_constant)


def numeric_positive(value):
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        fail('INVALID_POSITIVE_VALUE')
    return float(value)


def assess(candidate):
    if not isinstance(candidate, dict) or set(candidate) != REQUIRED:
        fail('SCHEMA')
    if candidate['scope'] != SCOPE or candidate['source_class'] not in CLASSES:
        fail('SCOPE')
    source = candidate['source_sha256']
    if source is not None and (type(source) is not str or len(source) != 64 or
                               any(c not in '0123456789abcdef' for c in source)):
        fail('SOURCE_DIGEST_FORMAT')
    interface = candidate['interface']
    if not isinstance(interface, dict) or set(interface) != set(FIELDS):
        fail('INTERFACE_SCHEMA')
    missing = []
    for key in FIELDS:
        value = interface[key]
        if value is None:
            missing.append('interface.' + key)
        elif key.endswith('_mm'):
            numeric_positive(value)
        elif type(value) is not str or not 0 < len(value.strip()) <= 64:
            fail('INTERFACE_TEXT')
    direction = candidate['direction']
    if direction not in DIRECTIONS:fail('DIRECTION')
    if direction == 'UNKNOWN':missing.append('direction')
    count = candidate['specimen_count']
    if count is None:
        missing.append('specimen_count')
    elif type(count) is not int or count < 1 or count > 1000:
        fail('SPECIMEN_COUNT')
    pairs = candidate['force_slip_pairs']
    if not isinstance(pairs, list) or len(pairs) > 1000:
        fail('CURVE_SCHEMA')
    if pairs:
        if len(pairs) < 3:fail('CURVE_TOO_SHORT')
        previous_x = -1.
        previous_force = -1.
        for i, pair in enumerate(pairs):
            if not isinstance(pair, list) or len(pair) != 2:
                fail('CURVE_ROW')
            slip, force = pair
            if any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in pair):
                fail('CURVE_NUMBER')
            if i == 0 and (slip != 0 or force != 0):fail('CURVE_ORIGIN')
            if i > 0 and (slip <= previous_x or force < previous_force):
                fail('CURVE_ORDER')
            previous_x, previous_force = float(slip), float(force)
        if pairs[-1][1] <= 0:fail('CURVE_NO_TRANSFER')
    else:
        missing.append('force_slip_pairs')
    if source is None:missing.append('source_sha256')
    if candidate['source_class'] == 'NO_EVIDENCE' and (source is not None or pairs):
        fail('SOURCE_CLASS_CONFLICT')
    if candidate['source_class'] == 'LAB_TEST' and count is not None and count < 2:
        missing.append('multi_specimen_repeatability')
    # No self-asserted evidence, nor a visually linear force-slip curve,
    # can establish source authenticity, a design-range tangent, or capacity.
    return {
        'scope':SCOPE,
        'source_class':candidate['source_class'],
        'readiness':'MISSING_INPUT' if missing else 'METADATA_AND_CURVE_SCREEN_ONLY',
        'missing_fields':sorted(missing),
        'curve_rows_screened':len(pairs),
        'physical_connection_stiffness_n_per_mm':'NOT_ESTABLISHED',
        'tension_compression_shear_equivalence':'NOT_ESTABLISHED',
        'source_authenticity':'NOT_VERIFIED',
        'engineering_acceptance':'NOT_ADMITTED',
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input_json')
    args=p.parse_args()
    print(json.dumps(assess(load(args.input_json)),sort_keys=True,indent=2))


if __name__=='__main__':main()
