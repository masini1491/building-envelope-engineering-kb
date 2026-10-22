"""Research-only bridge between tensile failure screen and synthetic C3D20R loads.

Only a SHA-pinned, previously validated 16-case C3D20R evidence artifact
may supply model forces. A signed local-axis k*delta-U has NOT been verified
as a real welded-stud axial tensile demand. Even a small numerical ratio is
NOT a design utilization check, nor proof of loading / connection validity.

The tool never uploads specimen data or puts real specimen data in its source.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from zipfile import ZipFile

from stud_tensile_strength_screen import calculate, load_input

PINNED_SYNTHETIC_REPORT_ZIP_SHA256 = '8207996dc19ab5674c1bc0b218d5048c13fbe4fe8e9f087b1ce06884a38326d1'
PINNED_SOLVER_ARTIFACT_SHA256 = {
    'four': '03cda477016e945c5f76a5b88a0548a08027c62ec777e4d5e7afec4c6b0e7f7a',
    'five': 'c249bb93622b66cd25aab87fa503c3b179ebde1ead2e632c47dd2f1ef0149279',
    'moved': '445414375571a6d74aaf3e90859868b4ad3c6f57b5e1e51d21edb4750e858d02',
}
PROFILES = {
    'four_inner_out': ((150., 450., 750., 1050.), (150., 375., 825., 1050.)),
    'five_inner_out': ((150., 375., 600., 825., 1050.), (150., 300., 600., 900., 1050.)),
}
STUDY_SCOPE = 'SYNTHETIC_C3D20R_FIXED_COUNT_LOCATION_COMPARATOR_NOT_DESIGN'
FORCE_TOL_N = 0.002


def reject(code):
    raise ValueError('STUD_STRENGTH_DEMAND_' + code)


def finite_number(value, code):
    if type(value) not in (int, float) or not math.isfinite(value):
        reject(code)
    return float(value)


def load_verified_research_zip(filename: Path):
    filename = Path(filename)
    if (filename.is_symlink() or not filename.is_file() or
            not 0 < filename.stat().st_size <= 1_000_000):
        reject('ARTIFACT_FILE_BOUNDARY')
    with filename.open('rb') as handle:
        digest = hashlib.file_digest(handle, 'sha256').hexdigest()
    if digest != PINNED_SYNTHETIC_REPORT_ZIP_SHA256:
        reject('ARTIFACT_SHA256')
    with ZipFile(filename) as archive:
        members = archive.infolist()
        if len(members) != 1 or members[0].filename != 'report.json' or not 0 < members[0].file_size <= 100_000:
            reject('ARTIFACT_CONTENT')
        content = archive.read('report.json')
    def no_duplicates(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                reject('DUPLICATE_JSON_KEY')
            result[key] = value
        return result
    def no_nonfinite(_):
        reject('NONFINITE_JSON')
    return json.loads(content, object_pairs_hook=no_duplicates, parse_constant=no_nonfinite)


def validate_synthetic_study(study):
    if (not isinstance(study, dict) or study.get('scope') != STUDY_SCOPE or
            study.get('sha256') != PINNED_SOLVER_ARTIFACT_SHA256 or
            study.get('engineering_acceptance') != 'NOT_ADMITTED' or
            study.get('synthetic_connector_model') != 'BILATERAL_Z_SPRING_ONLY' or
            study.get('true_stud_and_weld_stiffness_capacity') != 'NOT_ADMITTED' or
            study.get('same_stud_count_and_k') is not True):
        reject('STUDY_PROVENANCE_OR_ADMISSION')
    rows = study.get('cases')
    if not isinstance(rows, list) or len(rows) != 8:
        reject('STUDY_COVERAGE')
    indexed = set()
    best = None
    for case in rows:
        if not isinstance(case, dict):
            reject('CASE_STRUCTURE')
        n, layout, typ, k = (case.get('mesh'), case.get('layout'),
                             case.get('case'), case.get('k_per_station_n_per_mm'))
        if (type(n) is not int or n not in (8, 16) or layout not in PROFILES or
                typ not in ('soft', 'stiff') or
                type(k) not in (float, int) or k != {'soft': 50., 'stiff': 500.}[typ]):
            reject('CASE_IDENTITY')
        key = (n, layout, typ)
        if key in indexed:
            reject('DUPLICATE_CASE')
        indexed.add(key)
        original_sites, shifted_sites = PROFILES[layout]
        if (case.get('station_count') != len(original_sites) or
                tuple(case.get('moved_positions_mm', ())) != shifted_sites or
                case.get('causal_scope') != 'CONTROLLED_INTERIOR_LOCATION_ONLY_SYNTHETIC'):
            reject('STATION_GEOMETRY')
        for phase, sites in [('baseline', original_sites), ('moved', shifted_sites)]:
            result = case.get(phase)
            if not isinstance(result, dict):
                reject('MISSING_PHASE')
            raw_forces = result.get('station_forces_n')
            if not isinstance(raw_forces, list) or len(raw_forces) != len(sites):
                reject('STATION_FORCE_COVERAGE')
            forces = [finite_number(x, 'NONFINITE_FORCE') for x in raw_forces]
            if min(forces) <= 0:
                reject('NONPOSITIVE_SYNTHETIC_FORCE')
            total = math.fsum(forces)
            if (abs(total-finite_number(result.get('sum_station_force_n'), 'FORCE_SUM')) > 1e-7 or
                abs(max(forces)-finite_number(result.get('peak_station_force_n'), 'FORCE_PEAK')) > 1e-7 or
                abs(total+finite_number(result.get('rib_end_rf3_n'), 'RIB_REACTION')) > FORCE_TOL_N or
                abs(finite_number(result.get('rib_reaction_residual_n'), 'RIB_BALANCE')) > FORCE_TOL_N or
                abs(finite_number(result.get('nominal_global_z_residual_n'), 'GLOBAL_BALANCE')) > FORCE_TOL_N):
                reject('STATION_FORCE_BALANCE')
            for ix, load in enumerate(forces):
                candidate = {'mesh': n, 'layout': layout, 'stiffness_n_per_mm': k,
                             'phase': phase, 'position_mm': sites[ix], 'load_n': load}
                if best is None or load > best['load_n']:
                    best = candidate
        before = finite_number(case['baseline'].get('center_u3_mm'), 'CENTER_U3')
        after = finite_number(case['moved'].get('center_u3_mm'), 'CENTER_U3')
        if before <= 0 or after <= 0:
            reject('CENTER_U3')
        delta = finite_number(case.get('center_u3_change_mm'), 'DISPLACEMENT_CHANGE')
        pct = finite_number(case.get('center_u3_relative_change_percent'), 'PERCENT_CHANGE')
        if abs(delta-(after-before))>1e-9 or abs(pct-100*delta/before)>1e-5:
            reject('DISPLACEMENT_CHANGE')
    expected={(n,l,t) for n in (8,16) for l in PROFILES for t in ('soft','stiff')}
    if indexed!=expected or best is None:
        reject('STUDY_COVERAGE')
    return best


def compare_raw_strength_to_synthetic_study(raw_strength, verified_study):
    strength=calculate(raw_strength)
    best=validate_synthetic_study(verified_study)
    candidate_n=finite_number(strength['candidate_allowable_load_n'], 'STRENGTH_CANDIDATE')
    ratio=best['load_n']/candidate_n
    if not math.isfinite(ratio):
        reject('NUMERIC_RATIO')
    return {
        'scope': 'STUD_TENSILE_CANDIDATE_VS_UNCALIBRATED_C3D20R_RESEARCH_ONLY',
        'test_count': strength['sample_count'],
        'failure_mode_counts': strength['failure_mode_counts'],
        'tensile_candidate_method': strength['method'],
        'candidate_allowable_n_NOT_APPROVED': candidate_n,
        'source_authenticity': strength['source_authenticity'],
        'synthetic_model_research_provenance': 'SHA256_PINNED_VERIFIED_REPORT',
        'research_only_peak_synthetic_axis_force_n': best['load_n'],
        'research_only_peak_case': {k: v for k,v in best.items() if k!='load_n'},
        'research_only_magnitude_ratio_NOT_UTILIZATION': ratio,
        'ratio_is_design_check': False,
        'tensile_force_direction_at_link': 'NOT_ESTABLISHED',
        'realistic_design_load_case': 'NOT_ESTABLISHED',
        'physical_link_stiffness': 'NOT_ESTABLISHED',
        'allowable_capacity_authority': 'ENGINEER_SELECTED_NOT_CODE_QUALIFIED',
        'engineering_acceptance': 'NOT_ADMITTED',
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('private_strength_input_json', type=Path)
    parser.add_argument('pinned_synthetic_report_artifact_zip', type=Path)
    args=parser.parse_args()
    source=load_input(args.private_strength_input_json)
    study=load_verified_research_zip(args.pinned_synthetic_report_artifact_zip)
    print(json.dumps(compare_raw_strength_to_synthetic_study(source,study),
                     ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False))


if __name__=='__main__':
    main()
