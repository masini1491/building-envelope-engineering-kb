"""Bounded synthetic rib/plate thickness sensitivity, not curtain-wall design.

Stage 59 pristine 2 mm specimens remain untouched and reused from same CI.
Add only 3 mm plates AND 3 mm ribs with original 0/4/8-mm heights,
fixed material, pressure, perfect bonded midsurface seam and fixed edges.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from pathlib import Path

from check_center_rib_plate import (A, B, E, NU, P, NODES_MESH,
                                    RIB_HEIGHTS, build as original_build)
from check_aluminum_ritz import ritz_center_mm, center_z
from check_u_fold_cantilever import _completed

THICKNESSES = (2.0, 3.0)
THICKNESS_ADDED = 3.0
_MAX_MESH_DIFF = .15  # Stage 59 research-only screen; not engineering tolerance.
_MAX_FLAT_RITZ_DIFF = .20  # Stage 59 research-only screen.


def _allowed(n: int, h: int, t: float) -> None:
    if type(n) is not int or n not in NODES_MESH:
        raise ValueError('RIB_THICKNESS_MESH_NOT_SUPPORTED')
    if type(h) is not int or h not in RIB_HEIGHTS:
        raise ValueError('RIB_THICKNESS_HEIGHT_NOT_SUPPORTED')
    if type(t) not in (float, int) or float(t) not in THICKNESSES:
        raise ValueError('RIB_THICKNESS_NOT_SUPPORTED')


def build(n: int, h: int, t: float) -> str:
    _allowed(n, h, t)
    original, center, outer, counts = original_build(n, h)
    # Exact Stage 59 bytes for control reuse. Never mutate the original code.
    if t == 2.0:
        return original
    pattern = r'(\*SHELL SECTION,ELSET=(?:WEB|RIB),MATERIAL=SYNTHETIC_ELASTIC\n)2(?:\.0)?(\n)'
    new, substitutions = re.subn(pattern, lambda m: m.group(1)+'3.0'+m.group(2), original)
    if substitutions != (2 if h else 1):
        raise ValueError('RIB_THICKNESS_MATERIAL_SECTION_DRIFT')
    old_header = f'synthetic-stage59-clamped-web-ribheight-{h}-mesh-{n}'
    if new.count(old_header) != 1:
        raise ValueError('RIB_THICKNESS_SOURCE_HEADER_DRIFT')
    new = new.replace(old_header, f'synthetic-thickness3-clamped-web-ribheight-{h}-mesh-{n}', 1)
    if (new.count('*DLOAD\nWEB,P,0.0001') != 1 or '*CLOAD' in new
            or '*EQUATION' in new or '*PLASTIC' in new
            or new.count('ROOT,1,6,0.') != 1
            or new.count('*STEP,NLGEOM') != 1):
        raise ValueError('RIB_THICKNESS_SCOPE_ESCALATION')
    return new


def generate(folder: Path, n: int, h: int, t: float) -> None:
    _allowed(n, h, t)
    if t != THICKNESS_ADDED:
        raise ValueError('RIB_THICKNESS_CONTROL_GENERATION_FORBIDDEN')
    if folder.is_symlink() or folder.exists():
        raise ValueError('RIB_THICKNESS_FOLDER_MUST_BE_NEW')
    s = build(n, h, t)
    folder.mkdir(parents=True)
    (folder/'panel.inp').write_text(s, encoding='utf-8')


def _case(folder: Path, n: int, h: int, t: float) -> dict:
    expected = build(n, h, t)
    files = {k:folder/f'panel.{k}' for k in ('inp', 'dat', 'sta', 'frd')}
    for k,f in files.items():
        limit = 64_000_000 if k == 'frd' else 10_000_000
        if f.is_symlink() or not f.is_file() or not 0 < f.stat().st_size <= limit:
            raise ValueError('RIB_THICKNESS_ARTIFACT_MISSING:'+k)
    if files['inp'].read_bytes() != expected.encode('utf-8'):
        raise ValueError('RIB_THICKNESS_DECK_PROVENANCE_MISMATCH')
    _completed(files['sta'])
    u = center_z(files['dat'])
    if not math.isfinite(u) or not 0 < u < .05*float(t):
        raise ValueError('RIB_THICKNESS_DISPLACEMENT_OUT_OF_SCOPE')
    return dict(center_mm=u, thickness_mm=t, height_mm=h, mesh=n,
                sha256={k:hashlib.sha256(f.read_bytes()).hexdigest() for k,f in files.items()})


def assess(observed: dict[tuple[float,int,int],float]) -> dict:
    keys = {(t,n,h) for t in THICKNESSES for n in NODES_MESH for h in RIB_HEIGHTS}
    if (not isinstance(observed,dict) or set(observed) != keys
            or any(type(v) not in (float,int) or not math.isfinite(v) or v <= 0
                   for v in observed.values())):
        raise ValueError('RIB_THICKNESS_MATRIX_INVALID')
    reference = {}
    mesh_diff = {}
    for t in THICKNESSES:
        c = dict(width_mm=A,height_mm=B,thickness_mm=t,
                 youngs_modulus_mpa=E,poisson_ratio=NU,pressure_n_mm2=P)
        flat = ritz_center_mm(c)
        diff = abs(observed[t,16,0]-flat)/flat
        if diff > _MAX_FLAT_RITZ_DIFF:
            raise ValueError('RIB_THICKNESS_FLAT_RITZ_MISMATCH')
        reference[str(t)] = dict(ritz_center_mm=flat,relative_difference=diff)
        for n in NODES_MESH:
            if not (observed[t,n,0] > observed[t,n,4] > observed[t,n,8]):
                raise ValueError('RIB_THICKNESS_HEIGHT_ORDER_FAILED')
        for h in RIB_HEIGHTS:
            d = abs(observed[t,16,h]-observed[t,8,h])/observed[t,16,h]
            if d > _MAX_MESH_DIFF:
                raise ValueError('RIB_THICKNESS_MESH_DIFFERENCE_FAILED')
            mesh_diff[f't{t}_h{h}'] = d
    for n in NODES_MESH:
        for h in RIB_HEIGHTS:
            if not observed[3.0,n,h] < observed[2.0,n,h]:
                raise ValueError('RIB_THICKNESS_STIFFENING_NOT_OBSERVED')
    kirchhoff_ratio = (2.0/3.0)**3
    solver_ratio = observed[3.0,16,0]/observed[2.0,16,0]
    # Ratios compare the same fixed pressure/geometries. Independent classical
    # plate scaling is a *small-deflection* screen, not exact NLGEOM behavior.
    if abs(solver_ratio-kirchhoff_ratio)/kirchhoff_ratio > .20:
        raise ValueError('RIB_THICKNESS_FLAT_SCALING_REFERENCE_MISMATCH')
    return {
        'scope':'SYNTHETIC_CENTER_RIB_TWO_DISCRETE_THICKNESSES_ONLY',
        'plate_width_mm':A, 'plate_height_mm':B,
        'pressure_n_mm2':P, 'youngs_modulus_mpa':E, 'poisson_ratio':NU,
        'center_displacement_mm':{str(t):{str(n):{str(h):observed[t,n,h] for h in RIB_HEIGHTS}
                                  for n in NODES_MESH} for t in THICKNESSES},
        'flat_ritz_by_thickness':reference,
        'flat_plate_Kirchhoff_t_cubed_ratio':kirchhoff_ratio,
        'flat_plate_solver_t3_over_t2_ratio':solver_ratio,
        'two_mesh_differences':mesh_diff,
        'rib_web_connection':'IDEAL_SHARED_S8R_NODES',
        'rigid_rotation_or_fastener_force':'NOT_ADMITTED',
        'pressure_balance_six_components':'NOT_ADMITTED',
        'material_capacity':'NOT_ADMITTED',
        'engineering_acceptance':'NOT_ADMITTED',
    }


def check(root: Path) -> dict:
    cases={}
    for t in THICKNESSES:
        for n in NODES_MESH:
            for h in RIB_HEIGHTS:
                folder = root/(f'center_rib_h{h}_n{n}' if t==2.0 else f'rib_thickness_3_h{h}_n{n}')
                cases[t,n,h] = _case(folder,n,h,t)
    result = assess({key:value['center_mm'] for key,value in cases.items()})
    result['cases'] = {f't{t}_n{n}_h{h}':case for (t,n,h),case in cases.items()}
    return result


if __name__ == '__main__':
    if len(sys.argv)==6 and sys.argv[1]=='--generate':
        generate(Path(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),float(sys.argv[5]))
        print('RIB_THICKNESS_SYNTHETIC_DECK_GENERATED_NO_DESIGN')
    elif len(sys.argv)==2:
        print(json.dumps(check(Path(sys.argv[1])),allow_nan=False,sort_keys=True))
        print('RIB_THICKNESS_BOUNDED_SENSITIVITY_PASS; NO_CAPACITY_OR_FASTENER')
    else:
        raise SystemExit('USAGE: check_rib_thickness_sweep.py ROOT | --generate DIR N H T')
