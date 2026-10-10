"""A/B test of CCX RF output selection on identical physical NLGEOM decks.

Two independent solver runs differ ONLY by requesting NALL RF output.
This establishes output-selection invariance, not external-force equilibrium.
"""
from __future__ import annotations

import math
from pathlib import Path

from check_pressure_equilibrium import parse_deck, read_edge_rf
from check_follower_pressure import displacement_block


def verify_pair(a_deck: Path, a_dat: Path, b_deck: Path, b_dat: Path):
    original = a_deck.read_text(encoding="utf-8")
    changed = b_deck.read_text(encoding="utf-8")
    marker = "*NODE PRINT,NSET=NALL\nU,RF\n"
    if original.count(marker) != 1 or changed != original.replace(marker, "*NODE PRINT,NSET=NALL\nU\n"):
        raise ValueError("NOT_ISOLATED_NALL_RF_OUTPUT_CHANGE")
    nodes, elements, edge, q = parse_deck(a_deck)
    nodes_b, elements_b, edge_b, q_b = parse_deck(b_deck)
    if (nodes, elements, edge, q) != (nodes_b, elements_b, edge_b, q_b):
        raise ValueError("PHYSICAL_DECK_DRIFT")
    a_rf = read_edge_rf(a_dat, edge)
    b_rf = read_edge_rf(b_dat, edge)
    a_u = displacement_block(a_dat.read_text(errors="replace"), set(nodes))
    b_u = displacement_block(b_dat.read_text(errors="replace"), set(nodes))
    max_rf = max(abs(v) for v in a_rf)
    rf_gap = max(abs(a-b) for a,b in zip(a_rf,b_rf))
    max_u = max(abs(v) for xyz in a_u.values() for v in xyz)
    u_gap = max(abs(a_u[n][i]-b_u[n][i]) for n in nodes for i in range(3))
    if not all(math.isfinite(v) for v in (max_rf,rf_gap,max_u,u_gap)):
        raise ValueError("NONFINITE_AB_EVIDENCE")
    # DAT print precision, not physical equilibrium tolerance.
    if rf_gap > 1e-7 * max(1.0,max_rf) or u_gap > 1e-7 * max(1.0,max_u):
        raise ValueError(f"NALL_RF_OUTPUT_AFFECTS_RESULT rf_gap={rf_gap} u_gap={u_gap}")
    return {"nodes":len(nodes),"elements":len(elements),"edge_rf_z_a":a_rf[2],
            "edge_rf_z_b":b_rf[2],"max_rf_gap":rf_gap,"max_u_gap":u_gap,
            "interpretation":"OUTPUT_SELECTION_INVARIANCE_ONLY"}


def main():
    for material in ("glass","aluminum"):
        for n in (4,8,16):
            a=Path(f"{material}_large_{n}")
            b=Path(f"{material}_large_{n}_no_nall_rf")
            result=verify_pair(a/"panel.inp",a/"panel.dat",b/"panel.inp",b/"panel.dat")
            print(f"{material} n={n} {result}")
    print("NALL_RF_OUTPUT_SELECTION_AB_PASS; GLOBAL_BALANCE_NOT_ADMITTED")


if __name__=="__main__":
    main()
