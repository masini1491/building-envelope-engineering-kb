"""Independent small-deflection pressure/reaction gate and nonlinear load diagnostic.

N-mm units, initial-planform area exactly 10000 mm2.
Large-deformation follower pressure is deliberately not admitted by q*A0.
"""
from pathlib import Path
import math,re
from generate import CONFIG,A

def last_block(source, label, set_name):
    pat=rf"{label} \([^)]*\) for set {set_name} and time\s+([\d.Ee+-]+)\s+((?:\s*\d+\s+[\d.Ee+-]+\s+[\d.Ee+-]+\s+[\d.Ee+-]+\s*\n)+)"
    matches=list(re.finditer(pat,source,re.I))
    if not matches:raise SystemExit(f"MISSING_RESULT_{label}_{set_name}")
    match=matches[-1]
    if abs(float(match.group(1))-1)>1e-7:raise SystemExit("MISSING_FINAL_TIME")
    lines=[]
    for line in match.group(2).strip().splitlines():
        tokens=line.split()
        if len(tokens)!=4:raise SystemExit("MALFORMED_RESULT")
        values=tuple(float(x) for x in tokens[1:])
        if not all(math.isfinite(x) for x in values):raise SystemExit("NONFINITE_RESULT")
        lines.append(values)
    if not lines:raise SystemExit("EMPTY_RESULTS")
    return [sum(row[i] for row in lines) for i in range(3)],len(lines)

for material,c in CONFIG.items():
    for n in (4,8,16):
        for load in ("small","large"):
            source=Path(f"{material}_{load}_{n}/panel.dat").read_text(errors="replace")
            reaction,count=last_block(source,"forces","EDGE")
            q=c["q_"+load]
            reference=q*A*A
            rel_z=abs(abs(reaction[2])-reference)/reference
            transverse=math.hypot(reaction[0],reaction[1])/reference
            print(f"{material} {load} mesh={n} edge_nodes={count} RF={reaction} initial_planform_force={reference:.6f} rel_z_initial={rel_z:.6g}")
            if load=="small":
                if rel_z>0.03:raise SystemExit("SMALL_LOAD_FORCE_BALANCE_FAILURE")
                if transverse>0.03:raise SystemExit("SMALL_LOAD_TRANSVERSE_REACTION_FAILURE")
            else:
                print("LARGE_LOAD_INITIAL_AREA_COMPARISON_IS_DIAGNOSTIC_ONLY")
print("SMALL_LOAD_BOUNDARY_REACTION_CHECK_PASS; NONLINEAR_FOLLOWER_LOAD_BALANCE_NOT_ADMITTED")
