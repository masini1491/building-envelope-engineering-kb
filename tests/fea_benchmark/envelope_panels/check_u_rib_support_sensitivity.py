"""Synthetic S8R plate support-sensitivity screen with unchanged open-U/studs.

Only the PLATE boundary differs from the previous four-edge clamp pressure
cases. It is NOT an actual curtain-wall clip, stud force or contact analysis.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

from check_u_rib_shell_links import LENGTH, PANEL_WIDTH, E, NU, MESHES, CASES, mesh
from check_u_rib_shell_pressure import (
    PRESSURE_N_MM2, NOMINAL_RESULTANT_N, pressure_deck,
    assess as clamped_assess,
)
from check_u_fold_cantilever import _completed, _dat_vectors

SCOPE = 'SYNTHETIC_PLATE_FOUR_EDGE_TRANSVERSE_SIMPLE_SUPPORT_WITH_OPEN_U_RIB_STUD_SPRINGS'
THICKNESS_MM = 3.0
REFERENCE_TERMS = 79  # odd m,n <= 79; bounded, converged Fourier screen


def _corners(n: int) -> tuple[int, int]:
    topology = mesh(n)
    coords = topology['coords']
    lookup = {tuple(point): number for number, point in coords.items()}
    left = lookup.get((0.0, -PANEL_WIDTH/2, 0.0))
    right = lookup.get((LENGTH, -PANEL_WIDTH/2, 0.0))
    if (not isinstance(left, int) or not isinstance(right, int) or left == right or
        left not in topology['clamped_plate'] or right not in topology['clamped_plate'] or
        left in topology['clamped_rib_end'] or right in topology['clamped_rib_end']):
        raise ValueError('U_SUPPORT_CORNER_ANCHORS_NOT_ESTABLISHED')
    return left, right


def simply_supported_deck(n: int, case: str) -> str:
    """Exact single-span boundary replacement, no change of load or elements."""
    source = pressure_deck(n, case)
    old = ('*BOUNDARY\nPLATE_CLAMP,1,6,0.\n'
           'RIB_END_CLAMP,1,6,0.\n*STEP')
    if source.count(old) != 1:
        raise ValueError('U_SUPPORT_BOUNDARY_CONTRACT_DRIFT')
    a, b = _corners(n)
    replacement = (
        f'*NSET,NSET=PLATE_INPLANE_A\n{a}\n'
        f'*NSET,NSET=PLATE_INPLANE_B\n{b}\n'
        '*BOUNDARY\n'
        'PLATE_CLAMP,3,3,0.\n'  # all plate edge nodes have U3=0; rotations free
        'PLATE_INPLANE_A,1,2,0.\n'  # remove in-plane translations
        'PLATE_INPLANE_B,2,2,0.\n'  # remove remaining in-plane rigid rotation
        'RIB_END_CLAMP,1,6,0.\n*STEP'
    )
    result = source.replace(old, replacement, 1)
    if (result.count('*DLOAD') != 1 or result.count('*ELEMENT,TYPE=S8R') != 2 or
        result.count('*ELEMENT,TYPE=SPRING2') != (case != 'unlinked') or
        any(key in result for key in ('*CONTACT', '*CLOAD', '*EQUATION', 'NLGEOM', '*PLASTIC')) or
        result.count('*NSET,NSET=PLATE_INPLANE_A') != 1 or
        result.count('*NSET,NSET=PLATE_INPLANE_B') != 1 or
        'PLATE_CLAMP,1,6,0.' in result):
        raise ValueError('U_SUPPORT_MODEL_SCOPE_ESCALATION')
    return result


def four_edges_simply_supported_series(max_odd: int = REFERENCE_TERMS) -> float:
    """Independent Navier sine-series Kirchhoff plate center displacement.

    A truly simply supported, homogeneous thin rectangle under uniform pressure:
    w = sum_odd_mn 16*q*sin(m*pi*x/a)*sin(n*pi*y/b)
            / (pi^6 * D * m*n*(m^2/a^2+n^2/b^2)^2).
    Finite sums are screening, not manufactured system predictions.
    """
    if type(max_odd) is not int or max_odd not in (19, 39, 79):
        raise ValueError('U_SUPPORT_FOURIER_ORDER_OUTSIDE_SCOPE')
    a, b = LENGTH, PANEL_WIDTH
    D = E*THICKNESS_MM**3/(12*(1-NU**2))
    terms = [((-1 if ((m-1)//2+(n-1)//2)%2 else 1) /
              (m*n*(m*m/(a*a)+n*n/(b*b))**2))
             for m in range(1,max_odd+1,2) for n in range(1,max_odd+1,2)]
    val = 16 * PRESSURE_N_MM2 * math.fsum(terms) / (math.pi**6 * D)
    if not math.isfinite(val) or not 0 < val < THICKNESS_MM*.05:
        raise ValueError('U_SUPPORT_FOURIER_REFERENCE_INVALID')
    return val


def compare(clamped: dict[tuple[int,str],float], simple: dict[tuple[int,str],float]) -> dict:
    wanted = {(n, c) for n in MESHES for c in CASES}
    for label, values in (('clamped',clamped),('simple',simple)):
        if (not isinstance(values,dict) or set(values) != wanted or
            any(type(v) not in (int,float) or not math.isfinite(v) or not 0 < v < .15
                for v in values.values())):
            raise ValueError('U_SUPPORT_INVALID_MATRIX:'+label)
    ref = four_edges_simply_supported_series()
    convergence = abs(ref-four_edges_simply_supported_series(39))/ref
    if convergence > .003:
        raise ValueError('U_SUPPORT_FOURIER_TRUNCATION_NOT_STABLE')
    error = abs(simple[16,'unlinked']-ref)/ref
    if error > .25:
        raise ValueError('U_SUPPORT_SIMPLE_PLATE_FOURIER_DISAGREEMENT')
    change = {}
    for n in MESHES:
        if not simple[n,'unlinked'] > simple[n,'soft'] > simple[n,'stiff']:
            raise ValueError('U_SUPPORT_STUD_STIFFNESS_TREND_INVALID')
        for case in CASES:
            if not simple[n,case] > clamped[n,case]:
                raise ValueError('U_SUPPORT_RELAXATION_NOT_OBSERVED')
    for case in CASES:
        delta = abs(simple[16,case]-simple[8,case])/simple[16,case]
        if delta > .25:
            raise ValueError('U_SUPPORT_MESH_CHANGE_TOO_LARGE')
        change[case]=delta
    return {
        'scope':SCOPE,
        'pressure_n_mm2':PRESSURE_N_MM2,
        'nominal_applied_resultant_n':NOMINAL_RESULTANT_N,
        'plate_four_edge_conditions_compared':['all_dofs_clamped','u3_only_edge_restraint'],
        'extra_inplane_pin':'one plate corner U1/U2 and another corner U2',
        'rib_end_condition_in_both':'SYNTHETIC_FIXED_RIB_ENDS',
        'simple_support_center_fourier_reference_mm':ref,
        'fourier_39_to_79_relative_change':convergence,
        'unlinked_fine_mesh_fourier_relative_error':error,
        'center_deflection_mm':{
            str(n):{c:{'clamped':clamped[n,c],'simple':simple[n,c],
                        'simple_to_clamped_ratio':simple[n,c]/clamped[n,c]}
                    for c in CASES} for n in MESHES},
        'two_mesh_simple_relative_change':change,
        'real_thermal_boundary_clip_rotation':'NOT_MODELED',
        'real_stud_contact_slip_and_stiffness':'NOT_ADMITTED',
        'independent_stud_connector_force':'NOT_ESTABLISHED',
        'real_design_wind_pressure':'NOT_ADMITTED',
        'engineering_acceptance':'NOT_ADMITTED',
    }


def verify(root: Path,n:int,case:str) -> dict:
    folder=root/f'u_support_simple_n{n}_{case}'
    paths={s:folder/('panel.'+s) for s in ('inp','sta','dat','frd')}
    for ext,p in paths.items():
        ceiling=64_000_000 if ext=='frd' else 10_000_000
        if p.is_symlink() or not p.is_file() or not 0<p.stat().st_size<=ceiling:
            raise ValueError('U_SUPPORT_ARTIFACT_ABSENT:'+ext)
    if paths['inp'].read_bytes()!=simply_supported_deck(n,case).encode('utf-8'):
        raise ValueError('U_SUPPORT_DECK_PROVENANCE_CHANGED')
    _completed(paths['sta'])
    topo=mesh(n)
    center=_dat_vectors(paths['dat'],'PLATE_CENTER','U')
    pstud=_dat_vectors(paths['dat'],'P_STUD','U')
    rstud=_dat_vectors(paths['dat'],'R_STUD','U')
    if (set(center)!={topo['center']} or set(pstud)!=set(topo['panel_studs']) or
        set(rstud)!=set(topo['rib_studs'])):
        raise ValueError('U_SUPPORT_OUTPUT_NODE_COVERAGE_MISSING')
    displacement=center[topo['center']][2]
    if not math.isfinite(displacement) or not 0<displacement<.15:
        raise ValueError('U_SUPPORT_CENTER_DEFLECTION_INVALID')
    return {'center_deflection_mm':displacement,
            'sha256':{s:hashlib.sha256(p.read_bytes()).hexdigest() for s,p in paths.items()}}


def assess(root:Path)->dict:
    existing=clamped_assess(root)  # revalidates all six same-run prior-stage cases
    clamped={(n,c):existing['cases'][f'n{n}_{c}']['center_deflection_mm']
             for n in MESHES for c in CASES}
    fresh={(n,c):verify(root,n,c) for n in MESHES for c in CASES}
    report=compare(clamped,{key:value['center_deflection_mm'] for key,value in fresh.items()})
    report['same_run_clamped_artifact_sha256']={
        k:existing['cases'][k]['input_and_solver_artifact_sha256']
        for k in sorted(existing['cases'])}
    report['simple_case_artifact_sha256']={f'n{n}_{c}':case['sha256']
                                          for (n,c),case in fresh.items()}
    return report


def generate(folder:Path,n:int,case:str)->None:
    if folder.exists() or folder.is_symlink():
        raise ValueError('U_SUPPORT_MUST_USE_FRESH_WORKSPACE')
    inp=simply_supported_deck(n,case)
    folder.mkdir(parents=True)
    (folder/'panel.inp').write_text(inp,encoding='utf-8')


if __name__=='__main__':
    if len(sys.argv)==5 and sys.argv[1]=='--generate':
        generate(Path(sys.argv[2]),int(sys.argv[3]),sys.argv[4]);print('U_SUPPORT_SYNTHETIC_DECK_GENERATED')
    elif len(sys.argv)==2:
        print(json.dumps(assess(Path(sys.argv[1])),sort_keys=True,allow_nan=False))
        print('U_SUPPORT_FOURIER_AND_DISCRETE_LINK_SCREEN_PASS; NOT_DESIGN_ADMITTED')
    else:
        raise SystemExit('USAGE: check_u_rib_support_sensitivity.py ROOT | --generate DIR MESH CASE')
