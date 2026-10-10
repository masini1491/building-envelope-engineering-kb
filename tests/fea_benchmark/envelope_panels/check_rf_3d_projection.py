"""CCX 2.21 C3D20 expanded RF -> original S8R RF projection audit.

Matches the source-defined force branch of map3dto1d2d.f for a bounded,
ordinary quadratic S8R panel. This is not external support-reaction recovery.
"""
from __future__ import annotations

import math
import re
from pathlib import Path

from audit_rf_projection import rf_block
from check_expanded_frd import read_expanded_frd
from check_pressure_equilibrium import parse_deck

# One-based source node8(:,j) maps to the zero-based C3D20 element slots.
# For quadratic shell corners use three layers, for midside nodes two.
NODE8_GROUPS = (
    (0, 16, 4), (1, 17, 5), (2, 18, 6), (3, 19, 7),
    (8, 12), (9, 13), (10, 14), (11, 15),
)


def read_final_expanded_rf(path: Path, expected: set[int]) -> dict[int, tuple[float, float, float]]:
    """Read final ASCII FRD FORC dataset on every expanded solid node."""
    raw = path.read_bytes()
    if not raw or b"\0" in raw:
        raise ValueError("MISSING_OR_BINARY_RF_FRD")
    try:
        lines = raw.decode("ascii").splitlines()
    except UnicodeDecodeError as exc:
        raise ValueError("NONASCII_RF_FRD") from exc
    time = None
    mode = False
    sets: list[tuple[float, dict[int, tuple[float, float, float]]]] = []
    current = {}
    for line in lines:
        label = line.strip()
        if label.startswith("100CL"):
            if mode:
                raise ValueError("TRUNCATED_FRD_FORC")
            try:
                time = float(line[12:24])
            except ValueError as exc:
                raise ValueError("MALFORMED_FRD_RF_TIME") from exc
            if not math.isfinite(time):
                raise ValueError("NONFINITE_FRD_RF_TIME")
        elif re.match(r"^-4\s+FORC\b", label):
            if mode or time is None:
                raise ValueError("INVALID_FRD_FORC_HEADER")
            mode = True
            current = {}
        elif mode and label == "-3":
            sets.append((time, current))
            mode = False
        elif mode and line.startswith(" -1"):
            if len(line) < 49:
                raise ValueError("MALFORMED_FRD_RF_VECTOR")
            try:
                node = int(line[3:13])
                value = tuple(float(line[13 + 12 * i:25 + 12 * i]) for i in range(3))
            except ValueError as exc:
                raise ValueError("MALFORMED_FRD_RF_VECTOR") from exc
            if node <= 0 or node in current or not all(math.isfinite(v) for v in value):
                raise ValueError("DUPLICATE_OR_NONFINITE_FRD_RF")
            current[node] = value
    if mode:
        raise ValueError("TRUNCATED_FRD_FORC")
    if not sets or abs(sets[-1][0] - 1.0) > 1e-7:
        raise ValueError("MISSING_FINAL_EXPANDED_RF")
    result = sets[-1][1]
    if set(result) != expected:
        raise ValueError(f"EXPANDED_RF_COVERAGE_MISMATCH expected={len(expected)} found={len(result)}")
    return result


def project_expanded_rf(original_elements, expanded_elements, forces):
    """Reproduce map3dto1d2d force mode: each 3D force is summed only once.

    Restriction: each expanded node must belong to exactly one original
    S8R shell node group. This fails closed for unaccounted variants.
    """
    if not original_elements or set(expanded_elements) != set(range(1, len(original_elements) + 1)):
        raise ValueError("EXPANDED_ELEMENT_COVERAGE_MISMATCH")
    incidence: dict[int, int] = {}
    associations: dict[int, int] = {}
    for eid, original in enumerate(original_elements, 1):
        expanded = expanded_elements[eid]
        if len(original) != 8 or len(expanded) != 20 or len(set(expanded)) != 20:
            raise ValueError("BAD_S8R_OR_C3D20_CONNECTIVITY")
        for orig, slots in zip(original, NODE8_GROUPS):
            incidence[orig] = incidence.get(orig, 0) + 1
            for slot in slots:
                expanded_nid = expanded[slot]
                if expanded_nid in associations and associations[expanded_nid] != orig:
                    raise ValueError("SHARED_EXPANDED_NODE_HAS_AMBIGUOUS_ORIGINAL")
                associations[expanded_nid] = orig
    if set(associations) != set(forces) or not all(len(f) == 3 and all(math.isfinite(v) for v in f) for f in forces.values()):
        raise ValueError("INCOMPLETE_OR_NONFINITE_EXPANDED_RF")
    projected = {node: [0.0, 0.0, 0.0] for node in incidence}
    for expanded_nid, orig in associations.items():
        for i in range(3):
            projected[orig][i] += forces[expanded_nid][i]
    # iforce=1 resets inum(node2d)=-1; unlike field interpolation,
    # repeated-element incidence is NOT an averaging divisor.
    return {node: tuple(vec) for node, vec in projected.items()}, incidence


def reconcile(deck: Path, frd: Path, dat: Path):
    nodes, elements, _, _ = parse_deck(deck)
    coordinates, expanded, displacement = read_expanded_frd(frd)
    if set(coordinates) != set(displacement):
        raise ValueError("INCOMPLETE_EXPANDED_U")
    force = read_final_expanded_rf(frd, set(coordinates))
    mapped, incidence = project_expanded_rf(elements, expanded, force)
    if set(mapped) != set(nodes):
        raise ValueError("INCOMPLETE_MAPPED_RF_COVERAGE")
    original = rf_block(dat.read_text(errors="replace"), "NALL", set(nodes))
    max_difference = max(abs(mapped[node][i] - original[node][i]) for node in nodes for i in range(3))
    max_value = max(abs(v) for vec in original.values() for v in vec)
    # Both outputs round values for human-readable FRD/.dat; 0.0002 is a
    # serialization-tolerance scope, not a force-equilibrium tolerance.
    relative = max_difference / max(1.0, max_value)
    if relative > 0.0002:
        raise ValueError(f"SOURCE_RF_PROJECTION_MISMATCH relative={relative:.8g}")
    summed_3d = tuple(sum(x[i] for x in force.values()) for i in range(3))
    summed_original = tuple(sum(x[i] for x in original.values()) for i in range(3))
    return dict(expanded_nodes=len(force), original_nodes=len(nodes),
                incidence_types=tuple(sorted(set(incidence.values()))),
                max_nodal_component_relative_rounding_gap=relative,
                summed_expanded_internal_rf=summed_3d,
                summed_original_internal_rf=summed_original)


def main():
    for material in ("glass", "aluminum"):
        for n in (4, 8, 16):
            folder = Path(f"{material}_large_{n}")
            evidence = reconcile(folder / "panel.inp", folder / "panel.frd", folder / "panel.dat")
            print(f"{material} n={n} {evidence}")
            print("SOURCE_RF_PROJECTION_MATCH_ONLY; NO_EXTERNAL_REACTION_BALANCE_ADMISSION")
    print("CCX_3D_RF_MAPPING_DIAGNOSTIC_COMPLETE; GLOBAL_BALANCE_NOT_ADMITTED")


if __name__ == "__main__":
    main()
