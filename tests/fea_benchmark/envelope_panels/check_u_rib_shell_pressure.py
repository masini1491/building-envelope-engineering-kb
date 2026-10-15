"""Research-only uniform pressure on separate plate/open-U S8R shells.

Preserves the exact prior synthetic geometry, four studs, and ideal supports.
Only the center -1 N CLOAD is replaced by small uniform plate pressure.
No real wind design, physical connection stiffness, contact, or capacity.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

from check_u_rib_shell_links import (
    LENGTH, PANEL_WIDTH, E, NU, MESHES, CASES, STUD_STIFFNESS,
    deck as point_deck, mesh, _configuration,
)
from check_u_fold_cantilever import _completed, _dat_vectors

PRESSURE_N_MM2 = 0.000001  # synthetic 0.001 kPa; not a design wind pressure
NOMINAL_RESULTANT_N = PRESSURE_N_MM2 * LENGTH * PANEL_WIDTH
SCOPE = 'SYNTHETIC_OPEN_U_SHELL_FOUR_STUDS_PLATE_UNIFORM_PRESSURE_ONLY'


def pressure_deck(n: int, case: str) -> str:
    """Change the load, not shell topology or attachment semantics."""
    src = point_deck(n, case)
    parts = src.splitlines()
    center = mesh(n)['center']
    expected = f'{center},3,-1.00000000'
    try:
        i = parts.index('*CLOAD')
    except ValueError as exc:
        raise ValueError('U_PRESSURE_POINT_LOAD_ANCHOR_ABSENT') from exc
    if parts.count('*CLOAD') != 1 or parts[i+1] != expected:
        raise ValueError('U_PRESSURE_POINT_LOAD_CONTRACT_CHANGED')
    parts[i:i+2] = ['*DLOAD', f'PLATE,P,{PRESSURE_N_MM2:.9f}']
    out = '\n'.join(parts) + '\n'
    if (out.count('*DLOAD') != 1 or '*CLOAD' in out or
        out.count('*ELEMENT,TYPE=S8R') != 2 or
        out.count('*ELEMENT,TYPE=SPRING2') != (case != 'unlinked') or
        any(s in out for s in ('*EQUATION','*CONTACT','*PLASTIC','NLGEOM','*RIGID BODY'))):
        raise ValueError('U_PRESSURE_MODEL_SCOPE_BREACH')
    return out


def _basis(k: int) -> dict[int, float]:
    return {2*k: 1.0, 2*k+2: -2.0, 2*k+4: 1.0}


def _derivative(poly: dict[int,float], n: int = 1) -> dict[int,float]:
    for _ in range(n):
        poly = {e-1: v*e for e,v in poly.items() if e >= 1}
    return poly


def _integral(a: dict[int,float], b: dict[int,float]) -> float:
    return math.fsum(2*v*w/(i+j+1) for i,v in a.items()
                     for j,w in b.items() if (i+j)%2 == 0)


def pressure_ritz_center(terms: int = 6) -> float:
    """Independent six-mode linear Kirchhoff--Ritz uniform-load approximation.

    One y mode, multiple x modes; no CalculiX fields or measured stiffness.
    """
    if type(terms) is not int or terms not in (1, 4, 6):
        raise ValueError('U_PRESSURE_UNSUPPORTED_RITZ_TERMS')
    a, b = LENGTH, PANEL_WIDTH
    d = E*3.0**3/(12*(1-NU**2))
    jac = a*b/4
    y = _basis(0)
    y00 = _integral(y,y)
    y11 = _integral(_derivative(y),_derivative(y))
    y22 = _integral(_derivative(y,2),_derivative(y,2))
    y20 = _integral(y,_derivative(y,2))
    modes = [_basis(k) for k in range(terms)]
    matrix = [[0.0]*terms for _ in range(terms)]
    rhs = [PRESSURE_N_MM2*jac*_integral(x,{0:1.})*_integral(y,{0:1.}) for x in modes]
    for i,x in enumerate(modes):
        for j,z in enumerate(modes):
            matrix[i][j] = d*jac*(
                16/a**4 * _integral(_derivative(x,2),_derivative(z,2))*y00
                +16/b**4 * _integral(x,z)*y22
                +16*NU/(a*a*b*b)*(_integral(_derivative(x,2),z)+_integral(x,_derivative(z,2)))*y20
                +32*(1-NU)/(a*a*b*b)*_integral(_derivative(x),_derivative(z))*y11
            )
    for i in range(terms):
        pivot = max(range(i,terms),key=lambda row:abs(matrix[row][i]))
        if abs(matrix[pivot][i]) < 1e-12:
            raise ValueError('U_PRESSURE_RITZ_SINGULAR')
        matrix[i],matrix[pivot] = matrix[pivot],matrix[i]
        rhs[i],rhs[pivot] = rhs[pivot],rhs[i]
        for row in range(i+1,terms):
            f = matrix[row][i]/matrix[i][i]
            for j in range(i,terms):matrix[row][j] -= f*matrix[i][j]
            rhs[row] -= f*rhs[i]
    solution = [0.]*terms
    for i in range(terms-1,-1,-1):
        solution[i] = (rhs[i]-math.fsum(matrix[i][j]*solution[j] for j in range(i+1,terms)))/matrix[i][i]
    result = solution[0] # higher x basis vanish at longitudinal center
    if not 0. < result < .05 or not math.isfinite(result):
        raise ValueError('U_PRESSURE_RITZ_NONPHYSICAL')
    return result


def compare(observed: dict[tuple[int,str], float]) -> dict:
    if (not isinstance(observed,dict) or
        set(observed) != {(n,c) for n in MESHES for c in CASES} or
        any(type(v) not in (int,float) or not math.isfinite(v) or not 0 < v < .15
            for v in observed.values())):
        raise ValueError('U_PRESSURE_INVALID_OBSERVATION_MATRIX')
    for n in MESHES:
        if not observed[n,'unlinked'] > observed[n,'soft'] > observed[n,'stiff']:
            raise ValueError('U_PRESSURE_BOUNDED_COMPLIANCE_ORDER_NOT_OBSERVED')
    reference = pressure_ritz_center(6)
    rel_error = abs(observed[16,'unlinked']-reference)/reference
    if rel_error > .30:
        raise ValueError('U_PRESSURE_INDEPENDENT_PLATE_ORACLE_DISAGREEMENT')
    mesh_changes = {case:abs(observed[16,case]-observed[8,case])/observed[16,case]
                    for case in CASES}
    if any(x > .25 for x in mesh_changes.values()):
        raise ValueError('U_PRESSURE_TWO_MESH_CHANGE_TOO_LARGE')
    return {
        'scope':SCOPE,
        'synthetic_uniform_pressure_n_mm2':PRESSURE_N_MM2,
        'nominal_pressure_area_mm2':LENGTH*PANEL_WIDTH,
        'nominal_uniform_pressure_resultant_n':NOMINAL_RESULTANT_N,
        'independent_six_mode_plate_ritz_center_mm':reference,
        'unlinked_fine_mesh_oracle_relative_difference':rel_error,
        'center_deflection_mm':{str(n):{case:observed[n,case] for case in CASES} for n in MESHES},
        'two_mesh_relative_change':mesh_changes,
        'synthetic_dof3_stud_spring_n_per_mm':STUD_STIFFNESS,
        'support_model':'SYNTHETIC_PLATE_FOUR_EDGE_AND_RIB_END_CLAMPS',
        'real_wind_pressure_admission':'NOT_ADMITTED',
        'real_contact_shear_slip_and_stud_capacity':'NOT_ADMITTED',
        'connection_force_independently_observed':'NO_DERIVED_K_TIMES_RELATIVE_U_ONLY',
        'general_six_component_balance':'NOT_ADMITTED',
        'engineering_acceptance':'NOT_ADMITTED',
    }


def observed_case(root: Path, n: int, case: str) -> dict:
    folder = root/f'u_pressure_n{n}_{case}'
    paths = {e:folder/('panel.'+e) for e in ('inp','sta','dat','frd')}
    for ext,p in paths.items():
        limit = 64_000_000 if ext=='frd' else 10_000_000
        if p.is_symlink() or not p.is_file() or not 0 < p.stat().st_size <= limit:
            raise ValueError('U_PRESSURE_MISSING_ARTIFACT:'+ext)
    if paths['inp'].read_bytes() != pressure_deck(n,case).encode('utf-8'):
        raise ValueError('U_PRESSURE_DECK_SHA_PROVENANCE_MISMATCH')
    _completed(paths['sta'])
    topo = mesh(n)
    center = _dat_vectors(paths['dat'],'PLATE_CENTER','U')
    p_stud = _dat_vectors(paths['dat'],'P_STUD','U')
    r_stud = _dat_vectors(paths['dat'],'R_STUD','U')
    if (set(center) != {topo['center']} or set(p_stud) != set(topo['panel_studs']) or
        set(r_stud) != set(topo['rib_studs'])):
        raise ValueError('U_PRESSURE_INCOMPLETE_OUTPUT_NODES')
    v = -center[topo['center']][2]
    if not math.isfinite(v) or not 0 < v < .15:
        raise ValueError('U_PRESSURE_CENTER_DEFLECTION_INVALID')
    x = _configuration()['stud_centers']['positions_along_length_mm']
    derived = {str(xi):STUD_STIFFNESS[case]*(p_stud[a][2]-r_stud[b][2])
               for xi,a,b in zip(x,topo['panel_studs'],topo['rib_studs'])}
    if case == 'unlinked' and any(abs(f)>1e-14 for f in derived.values()):
        raise ValueError('U_PRESSURE_UNLINKED_TRANSFER_NOT_ZERO')
    return {'center_deflection_mm':v,
            'derived_synthetic_spring_force_n_not_stud_demand':derived,
            'input_and_solver_artifact_sha256':{e:hashlib.sha256(p.read_bytes()).hexdigest()
                                                for e,p in paths.items()}}


def assess(root: Path) -> dict:
    cases = {(n,c):observed_case(root,n,c) for n in MESHES for c in CASES}
    report = compare({key:value['center_deflection_mm'] for key,value in cases.items()})
    report['cases'] = {f'n{n}_{c}':v for (n,c),v in cases.items()}
    return report


def generate(folder:Path,n:int,case:str) -> None:
    if folder.exists() or folder.is_symlink():
        raise ValueError('U_PRESSURE_FRESH_WORKSPACE_REQUIRED')
    source = pressure_deck(n,case)
    folder.mkdir(parents=True)
    (folder/'panel.inp').write_text(source,encoding='utf-8')


if __name__=='__main__':
    if len(sys.argv)==5 and sys.argv[1]=='--generate':
        generate(Path(sys.argv[2]),int(sys.argv[3]),sys.argv[4])
        print('U_PRESSURE_SYNTHETIC_S8R_DECK_GENERATED; NO_DESIGN')
    elif len(sys.argv)==2:
        print(json.dumps(assess(Path(sys.argv[1])),sort_keys=True,allow_nan=False))
        print('U_PRESSURE_SYNTHETIC_RITZ_AND_MESH_SCREEN_PASS; NO_DESIGN_ADMISSION')
    else:
        raise SystemExit('USAGE: check_u_rib_shell_pressure.py ROOT | --generate DIR MESH CASE')
