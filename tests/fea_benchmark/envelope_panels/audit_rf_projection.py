"""CCX 2.21 RF print projection audit: original NALL vs EDGE.

RF in .dat is an internal nodal force projection (resultsforc + map3dto1d2d),
NOT a support-only reaction. No MPC correction or global balance admission.
"""
from __future__ import annotations

import math
import re
from pathlib import Path

from check_pressure_equilibrium import parse_deck, read_edge_rf


def rf_block(source: str, set_name: str, expected: set[int]):
    pattern = (rf"forces \(fx,fy,fz\) for set {re.escape(set_name)} and time\s+([\d.Ee+-]+)\s+"
               rf"((?:\s*\d+\s+[\d.Ee+-]+\s+[\d.Ee+-]+\s+[\d.Ee+-]+\s*\n)+)")
    matches = list(re.finditer(pattern, source, re.I))
    if not matches or abs(float(matches[-1].group(1)) - 1.0) > 1e-7:
        raise ValueError(f"MISSING_FINAL_{set_name}_RF")
    result = {}
    for line in matches[-1].group(2).splitlines():
        values = line.split()
        if len(values) != 4:
            raise ValueError("MALFORMED_RF_ROW")
        node = int(values[0])
        xyz = tuple(float(x) for x in values[1:])
        if node in result or not all(math.isfinite(v) for v in xyz):
            raise ValueError("DUPLICATE_OR_NONFINITE_RF")
        result[node] = xyz
    if set(result) != expected:
        raise ValueError(f"INCOMPLETE_{set_name}_RF_COVERAGE")
    return result


def audit(deck: Path, output: Path):
    nodes, _, edge, _ = parse_deck(deck)
    raw = output.read_text(errors="replace")
    all_rf = rf_block(raw, "NALL", set(nodes))
    edge_rf = rf_block(raw, "EDGE", edge)
    edge_from_all = tuple(sum(all_rf[n][i] for n in edge) for i in range(3))
    edge_from_edge = tuple(sum(edge_rf[n][i] for n in edge) for i in range(3))
    max_component = max(1., *(abs(x) for x in edge_from_edge))
    for n in edge:
        for i in range(3):
            if abs(all_rf[n][i] - edge_rf[n][i]) > 2e-6 * max(1., abs(edge_rf[n][i])):
                raise ValueError("EDGE_NALL_RF_PROJECTION_MISMATCH")
    if any(abs(a - b) > 2e-6 * max_component for a,b in zip(edge_from_all, edge_from_edge)):
        raise ValueError("EDGE_NALL_RF_SUM_MISMATCH")
    all_sum = tuple(sum(x[i] for x in all_rf.values()) for i in range(3))
    interior_sum = tuple(all_sum[i] - edge_from_all[i] for i in range(3))
    return dict(nall_count=len(all_rf), edge_count=len(edge),
                nall_internal_force_sum=all_sum, edge_internal_force_sum=edge_from_edge,
                interior_internal_force_sum=interior_sum)


def main():
    for material in ("glass", "aluminum"):
        for n in (4, 8, 16):
            folder = Path(f"{material}_large_{n}")
            data = audit(folder / "panel.inp", folder / "panel.dat")
            print(f"{material} n={n} {data}")
            print("CCX_RF_IS_PROJECTED_INTERNAL_FORCE_NOT_SUPPORT_ONLY; GLOBAL_BALANCE_NOT_ADMITTED")
    print("NALL_EDGE_RF_PROJECTION_AUDIT_COMPLETE; NO_EQUILIBRIUM_PASS")


if __name__ == "__main__":
    main()
