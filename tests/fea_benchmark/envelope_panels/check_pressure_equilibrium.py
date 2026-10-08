"""Independent small-pressure S8R nodal-load integration and CCX RF reconciliation.

Only planar, straight-edged, axis-aligned rectangular S8R shells with a uniform
*DLOAD P and global Cartesian constraints are supported. No capacity admission.
"""
from __future__ import annotations

import math
import re
from pathlib import Path

GAUSS = (-math.sqrt(3.0 / 5.0), 0.0, math.sqrt(3.0 / 5.0))
WEIGHTS = (5.0 / 9.0, 8.0 / 9.0, 5.0 / 9.0)
TOL = 1e-7


def shape(xi: float, eta: float) -> tuple[float, ...]:
    return (
        -0.25 * (1 - xi) * (1 - eta) * (1 + xi + eta),
        -0.25 * (1 + xi) * (1 - eta) * (1 - xi + eta),
        -0.25 * (1 + xi) * (1 + eta) * (1 - xi - eta),
        -0.25 * (1 - xi) * (1 + eta) * (1 + xi - eta),
        0.5 * (1 - xi * xi) * (1 - eta),
        0.5 * (1 + xi) * (1 - eta * eta),
        0.5 * (1 - xi * xi) * (1 + eta),
        0.5 * (1 - xi) * (1 - eta * eta),
    )


def parse_deck(path: Path):
    nodes: dict[int, tuple[float, float, float]] = {}
    elements: list[tuple[int, ...]] = []
    edge: list[int] = []
    pressure: list[float] = []
    section = ""
    nset = ""
    saw_nlgeom = False
    boundaries: list[tuple[str, int, int, float]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("**"):
            continue
        if line.startswith("*"):
            upper = line.upper().replace(" ", "")
            if upper.startswith(("*MPC", "*EQUATION", "*TRANSFORM", "*CLOAD", "*DSLOAD")):
                raise ValueError("UNSUPPORTED_CONSTRAINT_OR_LOAD")
            if upper.startswith("*NODE,") or upper == "*NODE":
                section = "nodes"
            elif upper.startswith("*ELEMENT,"):
                if "TYPE=S8R" not in upper or "ELSET=PLATE" not in upper:
                    raise ValueError("UNSUPPORTED_ELEMENT")
                section = "elements"
            elif upper.startswith("*NSET,"):
                nset = "EDGE" if "NSET=EDGE" in upper else "other"
                section = "nset"
            elif upper.startswith("*DLOAD"):
                section = "dload"
            elif upper.startswith("*BOUNDARY"):
                section = "boundary"
            elif upper.startswith("*STEP"):
                saw_nlgeom = "NLGEOM" in upper
                section = ""
            else:
                section = ""
            continue
        fields = [x.strip() for x in line.split(",") if x.strip()]
        if section == "nodes":
            if len(fields) != 4:
                raise ValueError("BAD_NODE")
            nid = int(fields[0])
            if nid in nodes:
                raise ValueError("DUPLICATE_NODE")
            nodes[nid] = tuple(float(x) for x in fields[1:])
        elif section == "elements":
            if len(fields) != 9:
                raise ValueError("BAD_S8R_CONNECTIVITY")
            elements.append(tuple(int(x) for x in fields[1:]))
        elif section == "nset" and nset == "EDGE":
            edge.extend(int(x) for x in fields)
        elif section == "dload":
            if len(fields) != 3 or fields[0].upper() != "PLATE" or fields[1].upper() != "P":
                raise ValueError("UNSUPPORTED_PRESSURE")
            pressure.append(float(fields[2]))
        elif section == "boundary":
            if len(fields) != 4:
                raise ValueError("UNSUPPORTED_BOUNDARY")
            boundaries.append((fields[0], int(fields[1]), int(fields[2]), float(fields[3])))
    if not saw_nlgeom or not nodes or not elements or not edge or len(set(edge)) != len(edge) or len(pressure) != 1:
        raise ValueError("INCOMPLETE_DECK")
    q = pressure[0]
    if not math.isfinite(q) or q <= 0 or not all(math.isfinite(c) for xyz in nodes.values() for c in xyz):
        raise ValueError("NONFINITE_OR_INVALID_INPUT")
    if not boundaries or not any(b[0] == "EDGE" and b[1] <= 3 <= b[2] and b[3] == 0 for b in boundaries):
        raise ValueError("UNSUPPORTED_EDGE_CONSTRAINT")
    if any(nid not in nodes for nid in edge):
        raise ValueError("UNKNOWN_EDGE_NODE")
    if any(abs(xyz[2]) > TOL for xyz in nodes.values()):
        raise ValueError("NONPLANAR_MODEL")
    return nodes, elements, set(edge), q


def integrate_loads(nodes, elements, q):
    applied = {nid: 0.0 for nid in nodes}
    total_area = 0.0
    for element in elements:
        if len(set(element)) != 8 or any(nid not in nodes for nid in element):
            raise ValueError("BAD_S8R_CONNECTIVITY")
        p = [nodes[nid] for nid in element]
        x0, y0, _ = p[0]
        x1, _, _ = p[1]
        _, y3, _ = p[3]
        dx, dy = x1 - x0, y3 - y0
        if dx <= 0 or dy <= 0:
            raise ValueError("UNSUPPORTED_ELEMENT_ORIENTATION")
        expected = (
            (x0, y0), (x1, y0), (x1, y3), (x0, y3),
            ((x0 + x1) / 2, y0), (x1, (y0 + y3) / 2),
            ((x0 + x1) / 2, y3), (x0, (y0 + y3) / 2),
        )
        if any(abs(p[i][axis] - expected[i][axis]) > TOL for i in range(8) for axis in (0, 1)):
            raise ValueError("NONRECTANGULAR_OR_DISTORTED_S8R")
        jacobian = dx * dy / 4.0
        total_area += dx * dy
        for i, xi in enumerate(GAUSS):
            for j, eta in enumerate(GAUSS):
                vals = shape(xi, eta)
                for nid, ni in zip(element, vals):
                    applied[nid] += q * jacobian * WEIGHTS[i] * WEIGHTS[j] * ni
    if not math.isclose(sum(applied.values()), q * total_area, abs_tol=1e-9, rel_tol=1e-10):
        raise ValueError("LOAD_INTEGRATION_NOT_CLOSED")
    return applied, q * total_area


def read_edge_rf(path: Path, edge: set[int]):
    source = path.read_text(errors="replace")
    pattern = (r"forces \(fx,fy,fz\) for set EDGE and time\s+([\d.Ee+-]+)\s+"
               r"((?:\s*\d+\s+[\d.Ee+-]+\s+[\d.Ee+-]+\s+[\d.Ee+-]+\s*\n)+)")
    matches = list(re.finditer(pattern, source, re.I))
    if not matches:
        raise ValueError("MISSING_EDGE_RF")
    match = matches[-1]
    if abs(float(match.group(1)) - 1.0) > TOL:
        raise ValueError("MISSING_FINAL_TIME")
    read: dict[int, tuple[float, float, float]] = {}
    for line in match.group(2).strip().splitlines():
        fields = line.split()
        if len(fields) != 4:
            raise ValueError("MALFORMED_EDGE_RF")
        nid = int(fields[0])
        values = tuple(float(x) for x in fields[1:])
        if nid in read or not all(math.isfinite(x) for x in values):
            raise ValueError("DUPLICATE_OR_NONFINITE_RF")
        read[nid] = values
    if set(read) != edge:
        raise ValueError("INCOMPLETE_EDGE_RF")
    return [sum(values[axis] for values in read.values()) for axis in range(3)]


def reconcile(inp: Path, dat: Path, tolerance: float = 1e-4):
    nodes, elements, edge, q = parse_deck(inp)
    applied, resultant = integrate_loads(nodes, elements, q)
    if resultant <= 0 or not math.isfinite(resultant):
        raise ValueError("INVALID_PRESSURE_RESULTANT")
    external_edge = sum(applied[nid] for nid in edge)
    raw_rf = read_edge_rf(dat, edge)
    corrected_support_z = raw_rf[2] - external_edge
    residual = abs(corrected_support_z + resultant) / resultant
    in_plane = math.hypot(raw_rf[0], raw_rf[1]) / resultant
    if residual > tolerance or in_plane > tolerance:
        raise ValueError(f"SMALL_LOAD_BALANCE_FAIL residual={residual:.7g} in_plane={in_plane:.7g}")
    return resultant, external_edge, raw_rf, corrected_support_z, residual


def main():
    for material in ("glass", "aluminum"):
        for n in (4, 8, 16):
            folder = Path(f"{material}_small_{n}")
            resultant, edge_load, raw_rf, support, residual = reconcile(folder / "panel.inp", folder / "panel.dat")
            if abs(resultant - 1.0) > 1e-9:
                raise ValueError("UNEXPECTED_SMALL_LOAD_REFERENCE")
            print(f"{material} n={n} total_pressure={resultant:.9f} edge_applied={edge_load:.9f} "
                  f"raw_RFz={raw_rf[2]:.9f} corrected_support_RFz={support:.9f} "
                  f"relative_balance_residual={residual:.8g} SMALL_LOAD_BALANCE_PASS")
    print("S8R_SMALL_PRESSURE_BALANCE_BOUNDED_PASS; LARGE_NLGEOM_GLOBAL_BALANCE_NOT_ADMITTED")


if __name__ == "__main__":
    main()
