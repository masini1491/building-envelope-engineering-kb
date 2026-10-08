"""Independent circular-arc comparison and mesh sequence gate for 90° NLGEOM shell."""
from __future__ import annotations
import math
import re
from pathlib import Path

ANGLE=1.57
LENGTH=100.0
EXPECTED_X=LENGTH*(math.sin(ANGLE)/ANGLE-1)
EXPECTED_Z=-LENGTH*(1-math.cos(ANGLE))/ANGLE

def extract(directory):
    path=Path(directory)
    lines=(path/"shell90.frd").read_text(errors="replace").splitlines()
    geo={}
    disp={}
    active=None
    for line in lines:
        if line.startswith("    2C"):
            active="geo"
        elif line.startswith(" -4  DISP"):
            active="disp"
            disp={}
        elif line.startswith(" -3"):
            active=None
        elif line.startswith(" -1") and active in ("geo","disp"):
            try:
                node=int(line[3:13])
                xyz=tuple(float(line[i:i+12]) for i in (13,25,37))
            except ValueError as exc:
                raise SystemExit("FRD_PARSE_ERROR") from exc
            (geo if active=="geo" else disp)[node]=xyz
    tips=[n for n,(x,y,z) in geo.items() if abs(x-LENGTH)<1e-6]
    if len(tips)<3 or any(n not in disp for n in tips):
        raise SystemExit("MISSING_TIP_DISPLACEMENT")
    sta=(path/"shell90.sta").read_text(errors="replace").splitlines()
    valid=[]
    for line in sta:
        fields=line.split()
        if len(fields)==7 and fields[0]=="1":
            try: valid.append((float(fields[4]),fields[2]))
            except ValueError: pass
    if not valid or abs(valid[-1][0]-1)>1e-7 or "U" in valid[-1][1]:
        raise SystemExit("SHELL_NOT_CONVERGED_FULL_STEP")
    x=sum(disp[n][0] for n in tips)/len(tips)
    z=sum(disp[n][2] for n in tips)/len(tips)
    if not math.isfinite(x) or not math.isfinite(z):
        raise SystemExit("NONFINITE_RESULT")
    text=(path/"shell90.dat").read_text(errors="replace")
    pattern=re.compile(r"statistics for surface set SFIX and time\s+([0-9.E+-]+).*?total surface force \(fx,fy,fz\) and moment about the origin\(mx,my,mz\)\s+([0-9.E+\-\s]+?)\s+center of gravity", re.S|re.I)
    matches=list(pattern.finditer(text))
    if not matches: raise SystemExit("MISSING_REACTION_MOMENT")
    vals=[float(v) for v in matches[-1].group(2).split()]
    if len(vals)!=6: raise SystemExit("BAD_REACTION_MOMENT")
    # At a pure imposed end-rotation the ideal net support force is zero.
    # Check CGX/CCX reported support traction force stays small relative to
    # characteristic bending force abs(M)/L; do not claim exact equilibrium.
    force_norm=math.sqrt(sum(v*v for v in vals[:3]))
    if force_norm > 0.05 * abs(vals[4])/LENGTH:
        raise SystemExit("SUPPORT_PARASITIC_FORCE_TOO_LARGE")
    if abs(vals[3]) > 0.02*abs(vals[4]) or abs(vals[5]) > 0.02*abs(vals[4]):
        raise SystemExit("SUPPORT_PARASITIC_MOMENT_TOO_LARGE")
    return (x,z,vals[4],len(geo))

# Independent Euler-Bernoulli bending idealization, per unit strip width:
# EI = E*b*t^3/12. The 90-degree pure-bending moment is EI*theta/L.
# This is an approximate thin-strip theory, not an exact 3D shell solution.
E=210000.0
WIDTH=10.0
THICKNESS=1.0
EXPECTED_ABS_MY=E*WIDTH*THICKNESS**3/12 * ANGLE/LENGTH
if not math.isfinite(EXPECTED_ABS_MY):
    raise SystemExit("INVALID_ANALYTIC_MOMENT")

results=[]
for subdivisions in (20,40,80):
    result=extract(f"mesh_{subdivisions}")
    results.append(result)
    print(f"MESH {subdivisions}: UX={result[0]:.6f} UZ={result[1]:.6f} MY={result[2]:.6f} nodes={result[3]}")
coarse,medium,fine=results
print(f"INDEPENDENT_ARC: UX={EXPECTED_X:.6f} UZ={EXPECTED_Z:.6f}")
print(f"INDEPENDENT_EULER_BERNOULLI_MOMENT_ABS: MY={EXPECTED_ABS_MY:.6f} Nmm")
if abs(abs(fine[2])-EXPECTED_ABS_MY)>35.0:
    raise SystemExit("ANALYTICAL_REACTION_MOMENT_TOLERANCE_FAILED")
if not (abs(fine[2]-medium[2]) < abs(medium[2]-coarse[2])):
    raise SystemExit("REACTION_MOMENT_REFINEMENT_NOT_CONTRACTING")

if abs(fine[0]-EXPECTED_X)>0.6 or abs(fine[1]-EXPECTED_Z)>0.7:
    raise SystemExit("ANALYTICAL_DISPLACEMENT_TOLERANCE_FAILED")
if not (abs(fine[0]-medium[0])<abs(medium[0]-coarse[0]) and
        abs(fine[1]-medium[1])<abs(medium[1]-coarse[1])):
    raise SystemExit("DISPLACEMENT_MESH_TREND_FAILED")
if abs(fine[0]-medium[0])>0.15 or abs(fine[1]-medium[1])>0.15:
    raise SystemExit("DISPLACEMENT_FINE_MESH_DIFFERENCE_TOO_LARGE")
if not (abs(fine[2]-medium[2])<abs(medium[2]-coarse[2])):
    raise SystemExit("REACTION_MOMENT_MESH_TREND_FAILED")
print("BOUNDED_SHELL90_GEOMETRIC_BENCHMARK_PASS (not glass/metal panel design)")
