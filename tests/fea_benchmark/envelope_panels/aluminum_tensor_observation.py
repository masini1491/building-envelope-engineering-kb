"""Final CCX 2.21 FRD tensor observations for bounded aluminum S8R research.

*EL FILE S,E are nodal-averaged/extrapolated values on the expanded solid
mesh, NOT integration-point stresses or independently validated design values.
FRD six-component order: XX,YY,ZZ,XY,YZ,ZX (not DAT EL PRINT ordering).
"""
from __future__ import annotations

import math
import re
from pathlib import Path

from check_expanded_frd import read_expanded_frd

_LABELS = {
    "STRESS": ("SXX", "SYY", "SZZ", "SXY", "SYZ", "SZX"),
    "TOSTRAIN": ("EXX", "EYY", "EZZ", "EXY", "EYZ", "EZX"),
}


def _read_tensor_line(line: str) -> tuple[int, tuple[float, ...]]:
    if not line.startswith(" -1") or len(line) < 85:
        raise ValueError("INVALID_FRD_TENSOR_ROW")
    try:
        node = int(line[3:13])
        values = tuple(float(line[13 + 12*i:25 + 12*i]) for i in range(6))
    except ValueError as exc:
        raise ValueError("INVALID_FRD_TENSOR_ROW") from exc
    if node <= 0 or not all(math.isfinite(v) for v in values):
        raise ValueError("INVALID_FRD_TENSOR_VALUE")
    return node, values


def read_final_tensors(frd: Path, expected_nodes: set[int]) -> dict[str, dict[int, tuple[float, ...]]]:
    if not expected_nodes or any(type(n) is not int or n <= 0 for n in expected_nodes):
        raise ValueError("TENSOR_EXPECTED_NODES_INVALID")
    raw = frd.read_bytes()
    if not raw or b"\x00" in raw:
        raise ValueError("TENSOR_FRD_MISSING_OR_BINARY")
    try:
        lines = raw.decode("ascii").splitlines()
    except UnicodeDecodeError as exc:
        raise ValueError("TENSOR_FRD_NONASCII") from exc

    records: dict[str, list[tuple[float, dict[int, tuple[float, ...]]]]] = {
        kind: [] for kind in _LABELS
    }
    time: float | None = None
    kind: str | None = None
    current: dict[int, tuple[float, ...]] = {}
    component_labels: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("100CL"):
            if kind is not None:
                raise ValueError("TRUNCATED_TENSOR_DATASET")
            try:
                time = float(line[12:24])
            except ValueError as exc:
                raise ValueError("INVALID_TENSOR_TIME") from exc
            if not math.isfinite(time):
                raise ValueError("INVALID_TENSOR_TIME")
            continue
        match = re.match(r"^-4\s+(STRESS|TOSTRAIN)\b", stripped)
        if match:
            if kind is not None or time is None:
                raise ValueError("INVALID_TENSOR_HEADER")
            kind = match.group(1)
            header_fields = stripped.split()
            if len(header_fields) < 3 or header_fields[2] != "6":
                raise ValueError("TENSOR_COMPONENT_COUNT_MISMATCH")
            current = {}
            component_labels = []
            continue
        if kind is not None and stripped == "-3":
            # If component descriptors are present, require expected
            # order. A different ordering cannot silently reuse this parser.
            if tuple(component_labels) != _LABELS[kind]:
                raise ValueError("TENSOR_COMPONENT_ORDER_MISMATCH")
            if not current:
                raise ValueError("EMPTY_TENSOR_DATASET")
            records[kind].append((time, current))
            kind = None
            continue
        if kind is not None and stripped.startswith("-5"):
            desc = re.match(r"^-5\s+([A-Z][A-Z0-9]*)\b", stripped)
            if not desc:
                raise ValueError("INVALID_TENSOR_COMPONENT_HEADER")
            component_labels.append(desc.group(1))
            if len(component_labels) > 6:
                raise ValueError("TOO_MANY_TENSOR_COMPONENTS")
            continue
        if kind is not None and stripped.startswith("-2"):
            raise ValueError("UNSUPPORTED_TENSOR_CONTINUATION")
        if kind is not None and line.startswith(" -1"):
            node, value = _read_tensor_line(line)
            if node in current:
                raise ValueError("DUPLICATE_TENSOR_NODE")
            current[node] = value
    if kind is not None:
        raise ValueError("TRUNCATED_TENSOR_DATASET")
    output: dict[str, dict[int, tuple[float, ...]]] = {}
    for label in _LABELS:
        if not records[label]:
            raise ValueError("MISSING_FRD_TENSOR:" + label)
        latest_time, values = records[label][-1]
        if abs(latest_time - 1.0) > 1e-7:
            raise ValueError("MISSING_FINAL_TENSOR_TIME:" + label)
        if set(values) != expected_nodes:
            raise ValueError("INCOMPLETE_TENSOR_NODE_COVERAGE:" + label)
        if len(records[label]) >= 2 and abs(records[label][-2][0] - latest_time) < 1e-7:
            raise ValueError("DUPLICATE_FINAL_TENSOR_DATASET:" + label)
        output[label] = values
    return output


def summarize_tensors(frd: Path) -> dict:
    # Reuse the existing exact C3D20 geometry + U coverage verifier; do not
    # synthesize an expanded-node set from the original shell mid-surface.
    coordinates, expanded_elements, displacement = read_expanded_frd(frd)
    if set(coordinates) != set(displacement) or not expanded_elements:
        raise ValueError("TENSOR_EXPANDED_GEOMETRY_MISSING")
    fields = read_final_tensors(frd, set(coordinates))
    result = {}
    for label, result_key, units in (
        ("STRESS", "stress", "MPa"),
        ("TOSTRAIN", "strain", "dimensionless"),
    ):
        tensor = fields[label]
        # Maximum ABSOLUTE tensor component at solver-produced expanded
        # nodal points only. Neither integration-point extreme nor strength.
        nid, comp = max(
            ((node, j) for node in tensor for j in range(6)),
            key=lambda pair: (abs(tensor[pair[0]][pair[1]]), -pair[0], -pair[1]),
        )
        result[result_key] = {
            "evidence_type": "CCX_FRD_EXTRAPOLATED_AVERAGED_EXPANDED_NODE_TENSOR",
            "field": label,
            "tensor_component_order": list(_LABELS[label]),
            "components_per_node": 6,
            "expanded_nodes_covered": len(tensor),
            "units": units,
            "max_abs_component": abs(tensor[nid][comp]),
            "max_abs_component_signed_value": tensor[nid][comp],
            "max_abs_component_label": _LABELS[label][comp],
            "max_abs_component_expanded_node_id": nid,
            "integration_point_extreme": "NOT_OBSERVED",
            "independent_numerical_oracle": "NOT_ESTABLISHED",
            "design_capacity": "NOT_COMPUTED",
        }
    return result
