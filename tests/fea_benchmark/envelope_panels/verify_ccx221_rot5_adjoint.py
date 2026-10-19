"""Inverse kinematic MPC virtual-work audit for CalculiX 2.21 DOF5.

Computes the displacement tangent from frozen MPC coefficients, then pairs
it with the ORIGINAL uneliminated fn. This is distinct from force elimination
and does not require fmpc. Not a physical dual, external work or support moment.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import zipfile
from verify_ccx221_rot5_full_work import (
    SOURCE_SHA, MANIFEST_SHA, CASES, parse_work, parse_old_dual,
    input_mode, owner_angle_map, eliminate,
)


def fail(code):
    raise ValueError('CCX221_ADJOINT_' + code)


def make_kinematic_tangent(work, spc_seeds):
    """MPC back-substitution from independently specified SPC tangent.

    Assign d(unknown independent translational DOFs)/dtheta=0; dependent
    coordinates come from the exact linearized MPC equations. Traversal is
    inverse of elimination order; repeated dependent nodes are rejected.
    """
    v = {}
    if not spc_seeds:
        fail('EMPTY_SEEDS')
    for key, value in spc_seeds.items():
        if len(key) != 2 or key[0] < 1 or key[1] not in (1, 2, 3):
            fail('SEED_OWNER')
        if not math.isfinite(value):
            fail('NONFINITE_SEED')
        v[key] = value
    dependent = set()
    active = []
    for index in reversed(tuple(work['mpcs'])):
        entry = work['mpcs'][index]
        if entry['tag'] == 'FLUID':
            continue
        terms = entry['terms']
        if not terms:
            fail('EMPTY_MPC')
        n, d, c = terms[0]
        if d > 3:  # Same physically scoped suppression as resultsforc.c
            continue
        if any(dd > 3 for _, dd, _ in terms) or not math.isfinite(c) or c == 0:
            fail('INVALID_TRANSLATION_MPC')
        key = (n, d)
        if key in v or key in dependent:
            fail('DEPENDENT_COLLISION')
        v[key] = -math.fsum(a * v.get((node, direction), 0.0)
                             for node, direction, a in terms[1:]) / c
        if not math.isfinite(v[key]):
            fail('NONFINITE_TANGENT')
        dependent.add(key)
        active.append(terms)
    # Check the full constraints, not only the selected SPC projection.
    max_abs_residual = max(
        (abs(math.fsum(a * v.get((node, direction), 0.0)
                       for node, direction, a in terms)) for terms in active),
        default=0.0,
    )
    if max_abs_residual > 1e-10:
        fail('CONSTRAINT_RESIDUAL')
    return v, max_abs_residual


def audit_case(work, seeds):
    v, residual = make_kinematic_tangent(work, seeds)
    raw_work = math.fsum(fn * v.get(key, 0.0) for key, (fn, _) in work['fn'].items())
    reduced, _ = eliminate(work)
    reduced_work = math.fsum(reduced.get(key, 0.0) * gradient
                             for key, gradient in seeds.items())
    delta = raw_work - reduced_work
    scale = max(1.0, abs(raw_work), abs(reduced_work))
    if abs(delta) > (1e-11 * scale):
        fail('TRANSPOSE_WORK_MISMATCH')
    return {
        'raw_fn_virtual_work_nmm': raw_work,
        'reduced_spc_virtual_work_nmm': reduced_work,
        'raw_minus_reduced_nmm': delta,
        'max_mpc_tangent_residual': residual,
        'active_tangent_coordinates': sum(vv != 0 for vv in v.values()),
        'nonzero_original_fn': len(work['fn']),
        'constraint_physical_dual': 'NOT_ESTABLISHED',
    }


def audit_zip(source_zip: Path, trace_zip: Path):
    if hashlib.sha256(source_zip.read_bytes()).hexdigest() != SOURCE_SHA:
        fail('SOURCE_PIN')
    report = {}
    with zipfile.ZipFile(source_zip) as source, zipfile.ZipFile(trace_zip) as trace:
        manifest_raw = source.read('manifest.json')
        if hashlib.sha256(manifest_raw).hexdigest() != MANIFEST_SHA:
            fail('MANIFEST_PIN')
        manifest = json.loads(manifest_raw)['cases']
        for key in CASES:
            inp = source.read(key + '/panel.inp')
            if hashlib.sha256(inp).hexdigest() != manifest[key]['input_sha256']:
                fail('INPUT_PIN')
            angles, weights = input_mode(inp.decode('ascii'))
            prefix = 'rot-dual/' + key + '/'
            work = parse_work(trace.read(prefix + 'kb_rot_full_work.tsv').decode('ascii'))
            _, spc = parse_old_dual(trace.read(prefix + 'kb_rot_dual.tsv').decode('ascii'))
            owners = owner_angle_map(
                trace.read(prefix + 'kb_rot_owner.tsv').decode('ascii'), angles, spc
            )
            seeds = {owners[node]: weights[node] for node in sorted(owners)}
            report[key] = audit_case(work, seeds)
    return {
        'status': 'INTERNAL_MPC_TRANSPOSE_VIRTUAL_WORK_CROSSCHECK_ONLY',
        'source_sha256': SOURCE_SHA,
        'trace_artifact_sha256': hashlib.sha256(trace_zip.read_bytes()).hexdigest(),
        'cases': report,
        'independent_external_spc_dual': 'NOT_ESTABLISHED',
        'physical_support_moment': 'NOT_ESTABLISHED',
        'contact': 'NOT_ADMITTED',
        'engineering_acceptance': 'NOT_ADMITTED',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source_zip', type=Path)
    parser.add_argument('trace_zip', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit_zip(args.source_zip, args.trace_zip),
                     indent=2, sort_keys=True, allow_nan=False))
