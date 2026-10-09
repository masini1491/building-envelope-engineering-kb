"""Side-by-side CCX expanded P1 and midsurface pressure diagnostics.

The inferred EDGE support subtracts *midsurface* nodal loads; combining it
with expanded P1 forces is a mixed-model diagnostic, NOT global equilibrium.
"""
from __future__ import annotations

import math
from pathlib import Path

from check_expanded_frd import diagnose as expanded_diagnose
from check_follower_pressure import diagnose as midsurface_diagnose


def compare(midsurface, expanded):
    mid = midsurface["midsurface_total"]
    support = midsurface["inferred_support"]
    p1 = expanded["p1_resultant"]
    if any(len(vec) != 3 or not all(math.isfinite(v) for v in vec) for vec in (mid, support, p1)):
        raise ValueError("INCOMPLETE_OR_NONFINITE_COMPARISON")
    if p1[2] <= 0 or mid[2] <= 0:
        raise ValueError("NONPOSITIVE_PRESSURE_RESULTANT")
    difference = tuple(p1[i] - mid[i] for i in range(3))
    mixed_residual = tuple(p1[i] + support[i] for i in range(3))
    return {"p1_minus_mid": difference, "p1_plus_mid_inferred_support": mixed_residual,
            "p1_minus_mid_z_relative": difference[2] / p1[2],
            "mixed_z_relative": mixed_residual[2] / p1[2]}


def main():
    for material in ("glass", "aluminum"):
        for n in (4, 8, 16):
            folder = Path(f"{material}_large_{n}")
            mid = midsurface_diagnose(folder / "panel.inp", folder / "panel.dat")
            face = expanded_diagnose(folder / "panel.inp", folder / "panel.frd")
            print(f"{material} n={n} {compare(mid, face)}")
            print("MIXED_PRESSURE_REACTION_DIAGNOSTIC_ONLY; GLOBAL_BALANCE_NOT_ADMITTED")
    print("MIDSURFACE_VS_EXPANDED_FACE_COMPARISON_COMPLETE; NO_EQUILIBRIUM_PASS")


if __name__ == "__main__":
    main()
