"""Read actual CCX 2.21 expanded C3D20 geometry and final 3D U from ASCII FRD.

The full expanded connectivity and every used node's final displacement must
exist in the real solver output. No S8R midsurface reconstruction fallback.
This is only a load-resultant diagnostic, never a global-equilibrium admission.
"""
from __future__ import annotations

import math
import re
from pathlib import Path

# CCX 2.21 src/frd.c writes solid node ids in this FRD permutation.
CCX_TO_FRD = tuple(range(12)) + (16, 17, 18, 19, 12, 13, 14, 15)


def _frd_vec(line: str):
    """Read fixed-width -1 record including adjacent negative E fields."""
    if not line.startswith(' -1') or len(line) < 49:
        raise ValueError('MALFORMED_FRD_VECTOR')
    try:
        node = int(line[3:13])
        vec = tuple(float(line[13 + 12 * i:25 + 12 * i]) for i in range(3))
    except ValueError as exc:
        raise ValueError('MALFORMED_FRD_VECTOR') from exc
    if node <= 0 or not all(math.isfinite(x) for x in vec):
        raise ValueError('NONFINITE_OR_BAD_FRD_VECTOR')
    return node, vec


def _finish_element(element_id, kind, frd_nodes, elements):
    if element_id is None:
        return
    if kind != 4 or len(frd_nodes) != 20 or len(set(frd_nodes)) != 20 or min(frd_nodes) <= 0:
        raise ValueError('NOT_EXPANDED_C3D20_ELEMENT')
    if element_id in elements:
        raise ValueError('DUPLICATE_FRD_ELEMENT')
    ccx = [0] * 20
    for frd_slot, ccx_slot in enumerate(CCX_TO_FRD):
        ccx[ccx_slot] = frd_nodes[frd_slot]
    elements[element_id] = tuple(ccx)


def read_expanded_frd(path: Path):
    """Return FRD reference coordinates, CCX C3D20 connectivity and final U."""
    raw = path.read_bytes()
    if not raw or b'\x00' in raw:
        raise ValueError('MISSING_OR_BINARY_FRD')
    try:
        lines = raw.decode('ascii').splitlines()
    except UnicodeDecodeError as exc:
        raise ValueError('NONASCII_FRD') from exc
    coordinates, elements, displacements = {}, {}, {}
    mode = None
    element_id, kind, frd_nodes = None, None, []
    time = None
    displacements_at = []
    for line in lines:
        stripped = line.strip()
        if re.match(r'^2C\s', stripped):
            mode = 'coordinates'
            continue
        if re.match(r'^3C\s', stripped):
            mode = 'elements'
            continue
        if stripped.startswith('100CL'):
            mode = None
            try:
                time = float(line[12:24])
            except ValueError as exc:
                raise ValueError('MALFORMED_FRD_TIME') from exc
            if not math.isfinite(time):
                raise ValueError('NONFINITE_FRD_TIME')
            continue
        if re.match(r'^-4\s+DISP\b', stripped):
            if time is None:
                raise ValueError('DISP_WITHOUT_TIME')
            mode = 'displacements'
            displacements = {}
            continue
        if stripped == '-3':
            if mode == 'elements':
                _finish_element(element_id, kind, frd_nodes, elements)
                element_id, kind, frd_nodes = None, None, []
            elif mode == 'displacements':
                displacements_at.append((time, displacements))
            mode = None
            continue
        if mode == 'coordinates' and line.startswith(' -1'):
            nid, xyz = _frd_vec(line)
            if nid in coordinates:
                raise ValueError('DUPLICATE_FRD_COORDINATE')
            coordinates[nid] = xyz
        elif mode == 'elements' and line.startswith(' -1'):
            _finish_element(element_id, kind, frd_nodes, elements)
            cols = line.split()
            if len(cols) < 3:
                raise ValueError('MALFORMED_FRD_ELEMENT_HEADER')
            element_id, kind = int(cols[1]), int(cols[2])
            if element_id <= 0:
                raise ValueError('BAD_FRD_ELEMENT_ID')
            frd_nodes = []
        elif mode == 'elements' and line.startswith(' -2'):
            if element_id is None:
                raise ValueError('ORPHAN_FRD_CONNECTIVITY')
            frd_nodes.extend(int(x) for x in line[3:].split())
        elif mode == 'displacements' and line.startswith(' -1'):
            nid, u = _frd_vec(line)
            if nid in displacements:
                raise ValueError('DUPLICATE_FRD_DISPLACEMENT')
            displacements[nid] = u
    if mode is not None:
        raise ValueError('TRUNCATED_FRD_BLOCK')
    if not coordinates or not elements or not displacements_at:
        raise ValueError('MISSING_FRD_COORDINATES_TOPOLOGY_OR_DISP')
    last_time, displacement = displacements_at[-1]
    if abs(last_time - 1.0) > 1e-7:
        raise ValueError('MISSING_FINAL_FRD_TIME')
    required = {nid for element in elements.values() for nid in element}
    if not required <= set(coordinates) or not required <= set(displacement):
        raise ValueError(f'EXPANDED_FACE_COVERAGE_UNRESOLVED coords={len(required & coordinates.keys())}/{len(required)} '
                         f'U={len(required & displacement.keys())}/{len(required)}')
    return coordinates, elements, displacement


def diagnose(deck: Path, frd: Path):
    from check_expanded_face import integrate_p1_expanded_face
    from check_pressure_equilibrium import parse_deck
    nodes, original_elements, _, pressure = parse_deck(deck)
    coordinates, expanded, displacement = read_expanded_frd(frd)
    if set(expanded) != set(range(1, len(original_elements) + 1)):
        raise ValueError('FRD_ELEMENT_ID_COVERAGE_MISMATCH')
    if not any(node not in nodes for node in coordinates):
        raise ValueError('NO_EXPANDED_NODES_FOUND')
    total = [0.0, 0.0, 0.0]
    for eid in sorted(expanded):
        node_ids = expanded[eid]
        current_xyz = [tuple(coordinates[n][i] + displacement[n][i] for i in range(3)) for n in node_ids]
        _, force = integrate_p1_expanded_face(current_xyz, pressure)
        for axis in range(3):
            total[axis] += force[axis]
    if not all(math.isfinite(x) for x in total) or total[2] <= 0:
        raise ValueError('INVALID_EXPANDED_P1_RESULTANT')
    return dict(elements=len(expanded), original_nodes=len(nodes), frd_nodes=len(coordinates),
                pressure=pressure, p1_resultant=tuple(total))


def main():
    for material in ('glass', 'aluminum'):
        for n in (4, 8, 16):
            folder = Path(f'{material}_large_{n}')
            evidence = diagnose(folder / 'panel.inp', folder / 'panel.frd')
            print(f'{material} n={n} {evidence}')
            print('CCX_FRD_EXPANDED_P1_LOAD_DIAGNOSTIC_ONLY; GLOBAL_BALANCE_NOT_ADMITTED')
    print('CCX_FRD_P1_GEOMETRY_COVERAGE_COMPLETE; NO_STRENGTH_OR_GLOBAL_BALANCE_CLAIM')


if __name__ == '__main__':
    main()
