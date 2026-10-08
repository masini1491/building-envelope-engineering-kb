"""Fail-closed synthetic material panel benchmark, not glass/aluminum strength."""
from pathlib import Path
import math,re
from generate import CONFIG,A
def read(material,load,n):
    directory=Path(f"{material}_{load}_{n}")
    text=(directory/"panel.dat").read_text(errors="replace")
    lines=(directory/"panel.sta").read_text(errors="replace").splitlines()
    times=[]
    for line in lines:
        parts=line.split()
        if len(parts)==7 and parts[0]=="1":
            try: times.append(float(parts[4]))
            except ValueError: pass
    if not times or abs(times[-1]-1)>1e-7:raise SystemExit("INCOMPLETE_STEP")
    pattern=r"displacements \(vx,vy,vz\) for set CENTER and time\s+([\d.E+-]+)\s+(\d+)\s+([\d.E+-]+)\s+([\d.E+-]+)\s+([\d.E+-]+)"
    hits=list(re.finditer(pattern,text,re.I))
    if not hits or abs(float(hits[-1].group(1))-1)>1e-7:raise SystemExit("MISSING_FINAL_CENTER")
    z=float(hits[-1].group(5))
    if not math.isfinite(z):raise SystemExit("NONFINITE_CENTER")
    print(f"{material} {load} n={n} center_z={z:.8f}")
    return abs(z)
for material,c in CONFIG.items():
    small=[read(material,"small",n) for n in (4,8,16)]
    large=[read(material,"large",n) for n in (4,8,16)]
    D=c["E"]*c["t"]**3/(12*(1-c["nu"]**2))
    reference=c["coefficient"]*c["q_small"]*A**4/D
    print(f"{material} INDEPENDENT_LINEAR_PLATE_REFERENCE={reference:.8f}")
    if abs(small[-1]-reference)/reference>.05:raise SystemExit(f"{material} SMALL_LOAD_ANALYTICAL_MISMATCH")
    if abs(small[-1]-small[-2])>=abs(small[-2]-small[0]):raise SystemExit(f"{material} SMALL_REFINEMENT_FAIL")
    if abs(large[-1]-large[-2])>=abs(large[-2]-large[0]):raise SystemExit(f"{material} LARGE_REFINEMENT_FAIL")
    if not large[-1]<small[-1]*(c["q_large"]/c["q_small"])*.95:
        raise SystemExit(f"{material} NONLINEAR_STIFFENING_NOT_DEMONSTRATED")
print("SYNTHETIC_GLASS_AND_ALUMINUM_PANEL_BOUNDED_PASS; NO STRENGTH ADMISSION")
