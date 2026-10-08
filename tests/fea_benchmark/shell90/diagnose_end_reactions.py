"""Diagnose section-vs-nodal end reactions; this does NOT certify global equilibrium."""
from __future__ import annotations
import math
import re
from pathlib import Path

def check(directory):
    dat=(Path(directory)/"shell90.dat").read_text(errors="replace")
    def section(tag):
        pattern=rf"statistics for surface set {tag} and time\s+([0-9.E+-]+)\s+total surface force \(fx,fy,fz\) and moment about the origin\(mx,my,mz\)\s+([^\n]+)"
        matches=list(re.finditer(pattern,dat,re.I))
        if not matches or abs(float(matches[-1].group(1))-1.0)>1e-7:
            raise SystemExit(f"MISSING_FINAL_SECTION_{tag}")
        vals=tuple(float(v) for v in matches[-1].group(2).split())
        if len(vals)!=6 or not all(math.isfinite(x) for x in vals):
            raise SystemExit(f"BAD_SECTION_{tag}")
        return vals
    def node_reactions(tag):
        pattern=rf"forces \(fx,fy,fz\) for set {tag} and time\s+([0-9.E+-]+)\s+((?:\s*\d+\s+[0-9.E+\-]+\s+[0-9.E+\-]+\s+[0-9.E+\-]+\s*\n)+)"
        matches=list(re.finditer(pattern,dat,re.I))
        if not matches or abs(float(matches[-1].group(1))-1.0)>1e-7:
            raise SystemExit(f"MISSING_FINAL_NODAL_{tag}")
        values=[]
        for line in matches[-1].group(2).strip().splitlines():
            nums=line.split()
            if len(nums)!=4: raise SystemExit("BAD_NODE_REACTION")
            values.append(tuple(float(v) for v in nums[1:]))
        if not values: raise SystemExit("EMPTY_NODE_REACTIONS")
        return tuple(sum(v[i] for v in values) for i in range(3))
    fix,rot=section("SFIX"),section("SROT")
    nfix,nrot=node_reactions("NFIX"),node_reactions("NROT")
    print(f"{directory} SECTION_FIX_6={fix} SECTION_ROT_6={rot}")
    print(f"{directory} NODE_FIX_RF123={nfix} NODE_ROT_RF123={nrot}")
    print(f"{directory} SECTION_SUM_6={tuple(fix[i]+rot[i] for i in range(6))}")
    print("FULL_GLOBAL_EQUILIBRIUM_NOT_ADMITTED: node print RF gives only reported translational components; section resultant is not identical to constrained nodal rotational reactions")
    return fix,rot,nfix,nrot

for n in (20,40,80):
    check(f"mesh_{n}")
print("TWO_END_REACTION_DIAGNOSTIC_COMPLETE_NOT_GLOBAL_BALANCE_PASS")
