"""Fail-closed limited pressure-plate benchmark checks."""
from pathlib import Path
import math,re
E=210000.0; nu=.3; a=100.; t=1.; q_small=.0001; q_large=.5
D=E*t**3/(12*(1-nu**2))
analytic=.00406*q_small*a**4/D
def read(n,case):
    d=Path(f"{case}_{n}")
    dat=(d/"plate.dat").read_text(errors="replace")
    sta=(d/"plate.sta").read_text(errors="replace")
    records=[]
    for line in sta.splitlines():
        fields=line.split()
        if len(fields)==7 and fields[0]=="1":
            try: records.append(float(fields[4]))
            except ValueError: continue
    if not records or abs(records[-1]-1.0)>1e-7: raise SystemExit("INCOMPLETE_STEP")
    pattern=r"displacements \(vx,vy,vz\) for set CENTER and time\s+([\d.E+-]+)\s+(\d+)\s+([\d.E+-]+)\s+([\d.E+-]+)\s+([\d.E+-]+)"
    hits=list(re.finditer(pattern,dat,re.I))
    if not hits: raise SystemExit("CENTER_MISSING")
    m=hits[-1]
    if abs(float(m.group(1))-1)>1e-6:raise SystemExit("FINAL_TIME_MISSING")
    z=float(m.group(5))
    if not math.isfinite(z):raise SystemExit("NONFINITE_DEFLECTION")
    print(f"{case} mesh {n}: center z={z:.8g}")
    return abs(z)
small=[read(n,"small") for n in (4,8,16)]
large=[read(n,"large") for n in (4,8,16)]
print(f"KIRCHHOFF_SMALL_PLATE_ORACLE={analytic:.8g}")
if not abs(small[-1]-analytic)/analytic < .16:raise SystemExit("SMALL_PLATE_ANALYTIC_MISMATCH")
if not abs(small[-1]-small[-2])<abs(small[-2]-small[0]):raise SystemExit("SMALL_PLATE_REFINEMENT_FAILED")
if not abs(large[-1]-large[-2])<abs(large[-2]-large[0]):raise SystemExit("LARGE_PLATE_REFINEMENT_FAILED")
if not large[-1]<small[-1]*(q_large/q_small)*.8:raise SystemExit("NLGEOM_MEMBRANE_STIFFENING_NOT_OBSERVED")
print("PRESSURE_PLATE_LIMITED_BENCHMARK_PASS; not glass or metal panel design")
