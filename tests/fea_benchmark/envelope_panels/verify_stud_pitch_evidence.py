"""Bounded C3D20R 3/4/5 stud-position sensitivity; NOT engineering acceptance.

The baseline four-station run is independently SHA-pinned; no raw RF or stud
force is inferred from contact pressure. Count and pitch change together.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from zipfile import ZipFile

from stud_pitch_trial import TRIALS, PROFILES, MESHES, make
from stud_solid_trial import CASES
from verify_stud_solid_trial import field, sets
from verify_c3d20r_u_contact import status
from check_u_rib_contact_observations import rf
from verify_pressure_contact_trial import nominal_pressure_equivalents

BASELINE_SHA256 = '03cda477016e945c5f76a5b88a0548a08027c62ec777e4d5e7afec4c6b0e7f7a'
RAW_SHA256 = 'c249bb93622b66cd25aab87fa503c3b179ebde1ead2e632c47dd2f1ef0149279'
FORCE_TOL_N = 0.002


def fail(s):
    raise ValueError('STUD_PITCH_' + s)


def pinned(path, sha):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size < 32000000:
        fail('PINNED_FILE')
    with path.open('rb') as f:
        if hashlib.file_digest(f, 'sha256').hexdigest() != sha:
            fail('SHA256_MISMATCH')
    return ZipFile(path)


def baseline_report(z):
    report = json.loads(z.read('stud-report.json'))
    if report.get('scope') != 'SYNTHETIC_C3D20R_FOUR_STATION_Z_SPRING_ONLY':
        fail('BASELINE_SCOPE')
    out = {}
    for case in report.get('cases', []):
        n = case['mesh']
        kind = case['case']
        if n not in MESHES or kind not in CASES or (n,kind) in out:
            fail('BASELINE_CASE_COVERAGE')
        if not math.isfinite(case['center_u3_mm']) or case['center_u3_mm'] <= 0:
            fail('BASELINE_BAD_VALUE')
        out[n,kind] = case
    if len(out) != 6:
        fail('BASELINE_CASE_COVERAGE')
    return out


def analyze_case(contents, n, profile, kind):
    label = f'pitch_{n}_{profile}_{kind}/panel.'
    expected, links = make(n, profile, kind)
    try:
        inp = contents.read(label+'inp')
        dat = contents.read(label+'dat').decode('utf-8', errors='replace')
        sta = contents.read(label+'sta').decode('utf-8', errors='replace')
        frd = contents.getinfo(label+'frd')
    except KeyError:
        fail('MISSING_RAW_CASE_FILE')
    if inp != expected.encode('utf-8'):
        fail('INPUT_PROVENANCE')
    if frd.file_size <= 0 or frd.file_size > 64000000:
        fail('FRD_MISSING_OR_OVERSIZE')
    status(sta)
    groups = sets(expected)
    p = field(dat, 'STUD_PLATE', groups['STUD_PLATE'])
    r = field(dat, 'STUD_RIB', groups['STUD_RIB'])
    center = field(dat, 'CENTER_RF', groups['CENTER_RF'])
    if set(p) != set(groups['STUD_PLATE']) or set(r) != set(groups['STUD_RIB']) or set(center) != set(groups['CENTER_RF']):
        fail('NODE_COVERAGE')
    forces = [CASES[kind]*(p[a][2]-r[b][2]) for a,b in links]
    if len(forces) != len(PROFILES[profile]) or not all(map(math.isfinite,forces)):
        fail('FORCES')
    if min(forces) <= 0:
        fail('NEGATIVE_OR_INACTIVE_FORCE')
    if any(abs(forces[i]-forces[-1-i]) > FORCE_TOL_N for i in range(len(forces)//2)):
        fail('SYMMETRY')
    total = math.fsum(forces)
    rib_rf = rf(dat,'RIB_END_RF',expected_nodes=groups['RIB_END_RF'])['sum_rf3_n']
    residual = math.fsum((total,rib_rf))
    if abs(residual) > FORCE_TOL_N:
        fail('RIB_BALANCE')
    plate_rf = rf(dat,'PLATE_EDGE_RF',expected_nodes=groups['PLATE_EDGE_RF'])['sum_rf3_n']
    global_residual = math.fsum((plate_rf,rib_rf,-nominal_pressure_equivalents(n)['edge_pressure_n'],36.0))
    if abs(global_residual) > FORCE_TOL_N:
        fail('GLOBAL_BALANCE')
    u3 = math.fsum(v[2] for v in center.values())/len(center)
    if not math.isfinite(u3) or u3 <= 0:
        fail('DISPLACEMENT')
    return {
        'mesh':n,'case':kind,'profile':profile,
        'station_positions_mm':PROFILES[profile],'station_count':len(links),
        'pitch_mm':PROFILES[profile][1]-PROFILES[profile][0],
        'synthetic_stiffness_each_n_per_mm':CASES[kind],
        'center_u3_mm':u3,'four_or_variable_station_link_forces_n':forces,
        'max_link_force_n':max(forces),'sum_link_force_n':total,
        'rib_end_rf3_n':rib_rf,'rib_action_reaction_residual_n':residual,
        'nominal_global_z_residual_n':global_residual
    }


def verify(pitch_zip, four_station_zip):
    with pinned(pitch_zip,RAW_SHA256) as new, pinned(four_station_zip,BASELINE_SHA256) as old:
        reference=baseline_report(old)
        fresh={(n,profile,kind): analyze_case(new,n,profile,kind)
               for n in MESHES for profile in TRIALS for kind in ('soft','stiff')}
        rows=[]
        for n in MESHES:
            for kind in ('soft','stiff'):
                b = reference[n,kind]
                third = fresh[n,'three_450',kind]
                fifth = fresh[n,'five_225',kind]
                four = b['center_u3_mm']
                unlinked = reference[n,'unlinked']['center_u3_mm']
                if not all(0 < x < unlinked for x in
                           (third['center_u3_mm'],four,fifth['center_u3_mm'])):
                    fail('CONNECTION_COMPLIANCE')
                # Nonmonotonic trends are a diagnostic: never fake a pass
                # by requiring a monotonic count/pitch relation.
                rows.append({
                    'mesh':n,'stiffness_each_n_per_mm':CASES[kind],
                    'unlinked_center_u3_mm':unlinked,
                    'station_counts':[3,4,5],
                    'pitches_mm':[450.,300.,225.],
                    'center_u3_mm':[third['center_u3_mm'],four,fifth['center_u3_mm']],
                    'middle_station_present':[True,False,True],
                    'isolated_pitch_effect':'NOT_IDENTIFIABLE_COUNT_AND_CENTER_POSITION_COVARY'
                })
    return {
        'scope':'SYNTHETIC_C3D20R_STATION_COUNT_AND_SPACING_SENSITIVITY_ONLY',
        'sources_sha256':{'new_3_and_5':RAW_SHA256,'four_station':BASELINE_SHA256},
        'new_cases':list(fresh.values()),'controlled_comparisons':rows,
        'max_rib_balance_residual_n':max(abs(x['rib_action_reaction_residual_n']) for x in fresh.values()),
        'max_global_balance_residual_n':max(abs(x['nominal_global_z_residual_n']) for x in fresh.values()),
        'spring_force':'DERIVED_FROM_K_TIMES_DELTA_U',
        'native_spring_force':'NOT_INDEPENDENTLY_MEASURED',
        'real_stud_stiffness_capacity_failure':'NOT_ADMITTED',
        'stud_pitch_only_effect':'NOT_ISOLATED',
        'face_contact':'NOT_MODELED',
        'engineering_acceptance':'NOT_ADMITTED'
    }


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('pitch_zip');p.add_argument('four_station_zip')
    a=p.parse_args()
    print(json.dumps(verify(a.pitch_zip,a.four_station_zip),sort_keys=True,indent=2,allow_nan=False))
