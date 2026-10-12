"""Stage 57: fixed synthetic U-fold S8R cantilever, no design admission.

Three connected midsurface strips, two mesh densities, unit-consistent end
line loading. An independent Euler-Bernoulli thin-wall reference is screening,
not a universal shell field solution or manufactured folded-panel capacity.
"""
from __future__ import annotations
import hashlib
import json
import math
import re
import sys
from pathlib import Path

L, B, FLANGE, T, E, NU, FORCE = 300.0, 40.0, 20.0, 1.5, 69000.0, 0.33, 1.0
SECTIONS = (4, 8, 4)
MESHES = (8, 16)


def beam_reference() -> dict:
    zbar = FLANGE ** 2 / (B + 2 * FLANGE)
    iy = T * (B * zbar ** 2 + 2 * ((FLANGE - zbar) ** 3 + zbar ** 3) / 3)
    delta = FORCE * L ** 3 / (3 * E * iy)
    if not all(math.isfinite(v) and v > 0 for v in (zbar, iy, delta)):
        raise ValueError("BEAM_REFERENCE_NONPHYSICAL")
    return {"neutral_axis_z_mm": zbar, "mid_surface_iy_mm4": iy,
            "cantilever_tip_deflection_mm": delta,
            "root_bending_moment_demand_n_mm": FORCE * L,
            "reference_type": "THIN_WALL_EULER_BERNOULLI_CANTILEVER_APPROXIMATION"}


def _outline(j: int) -> tuple[float, float]:
    if j <= 8:
        return (-B / 2, FLANGE * (1 - j / 8))
    if j <= 24:
        return (-B / 2 + B * (j - 8) / 16, 0.0)
    return (B / 2, FLANGE * (j - 24) / 8)


def build(n: int) -> tuple[str, dict[int, float], set[int], set[int]]:
    if type(n) is not int or n not in MESHES:
        raise ValueError("UNSUPPORTED_U_FOLD_MESH")
    m = sum(SECTIONS)
    nodes = {}
    coords = {}
    def node(i: int, j: int) -> int:
        key = (i, j)
        if key not in nodes:
            nid = len(nodes) + 1
            y, z = _outline(j)
            nodes[key] = nid
            coords[nid] = (L * i / (2 * n), y, z)
        return nodes[key]

    elements = []
    for i in range(n):
        for j in range(m):
            a, b = 2 * i, 2 * j
            positions = ((a,b),(a+2,b),(a+2,b+2),(a,b+2),
                         (a+1,b),(a+2,b+1),(a+1,b+2),(a,b+1))
            elements.append(tuple(node(*p) for p in positions))
    root = {node(0,j) for j in range(2*m+1)}
    tip = {node(2*n,j) for j in range(2*m+1)}
    line_weights = {j:0.0 for j in range(2*m+1)}
    for j in range(0,2*m,2):
        y0,z0 = _outline(j)
        y1,z1 = _outline(j+2)
        segment = math.hypot(y1-y0,z1-z0)
        for k,share in ((j,1/6),(j+1,2/3),(j+2,1/6)):
            line_weights[k] += FORCE * segment / (B+2*FLANGE) * share
    loads = {node(2*n,j):weight for j,weight in line_weights.items()}
    if (len(elements)!=n*m or len(root)!=2*m+1 or len(tip)!=2*m+1
            or root & tip or not math.isclose(sum(loads.values()),FORCE,rel_tol=1e-13)):
        raise ValueError("U_FOLD_MESH_OR_LOAD_NOT_CLOSED")
    # Distinct normals along the folded path are allowed; the longitudinal
    # quadratic shell-edge nodes at the corners are shared, never tied by MPC.
    lines = ["*HEADING",f"synthetic-U-fold-stage57-n{n}-cantilever",
             "*NODE"]
    lines += [f"{i},{x:.8f},{y:.8f},{z:.8f}" for i,(x,y,z) in sorted(coords.items())]
    lines += ["*ELEMENT,TYPE=S8R,ELSET=FOLD"]
    lines += [f"{i},"+",".join(map(str,el)) for i,el in enumerate(elements,1)]
    lines += ["*MATERIAL,NAME=SYNTHETIC_ELASTIC","*ELASTIC",f"{E},{NU}",
              "*SHELL SECTION,ELSET=FOLD,MATERIAL=SYNTHETIC_ELASTIC",str(T)]
    for name,group in (("ROOT",root),("TIP",tip)):
        ids=sorted(group)
        lines += [f"*NSET,NSET={name}"]
        lines += [",".join(map(str,ids[k:k+12])) for k in range(0,len(ids),12)]
    lines += ["*BOUNDARY","ROOT,1,6,0.","*STEP,NLGEOM","*STATIC",
              "0.05,1.,0.00001,0.1","*CLOAD"]
    lines += [f"{nid},3,{-v:.12f}" for nid,v in sorted(loads.items())]
    lines += ["*NODE FILE,OUTPUT=3D","U,RF","*NODE PRINT,NSET=TIP",
              "U","*NODE PRINT,NSET=ROOT","RF","*END STEP"]
    return "\n".join(lines)+"\n",loads,root,tip


def generate(root: Path, n: int) -> None:
    if root.is_symlink() or root.exists():
        raise ValueError("U_FOLD_WORKSPACE_MUST_BE_NEW")
    deck, _, _, _ = build(n)
    root.mkdir(parents=True)
    (root/"panel.inp").write_text(deck,encoding="utf-8")


def _dat_vectors(path: Path, name: str, kind: str) -> dict[int, tuple[float,float,float]]:
    contents = path.read_text(encoding="utf-8",errors="replace")
    title = "displacements \\(vx,vy,vz\\)" if kind=="U" else "forces \\(fx,fy,fz\\)"
    matches = list(re.finditer(title+r" for set "+name+
                 r" and time\s+([+.\dEe-]+)",contents,re.I))
    if not matches or abs(float(matches[-1].group(1))-1)>1e-7:
        raise ValueError("U_FOLD_FINAL_DAT_FIELD_MISSING:"+name)
    tail=contents[matches[-1].end():]
    number=r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?"
    pattern=re.compile(r"\s*(\d+)\s+("+number+r")\s+("+number+r")\s+("+number+r")\s*")
    data={}
    for line in tail.splitlines():
        if not line.strip():
            if data: break
            continue
        m=pattern.fullmatch(line)
        if m is None:
            if data: break
            continue
        nid=int(m.group(1))
        value=tuple(float(m.group(i)) for i in (2,3,4))
        if nid in data or not all(math.isfinite(v) for v in value):
            raise ValueError("U_FOLD_DUPLICATE_OR_NONFINITE_DAT")
        data[nid]=value
    if not data:
        raise ValueError("U_FOLD_FIELD_EMPTY")
    return data


def _completed(path: Path) -> None:
    times=[]
    for row in path.read_text(encoding="ascii").splitlines():
        parts=row.split()
        if len(parts)==7 and parts[0]=="1":
            times.append(float(parts[4]))
    if not times or not math.isfinite(times[-1]) or abs(times[-1]-1)>1e-7:
        raise ValueError("U_FOLD_INCOMPLETE_SOLVE")


def _case(folder:Path,n:int) -> dict:
    deck,loads,root,tip=build(n)
    paths={ext:folder/("panel."+ext) for ext in ("inp","dat","sta","frd")}
    for key,p in paths.items():
        maximum=64_000_000 if key=="frd" else 10_000_000
        if p.is_symlink() or not p.is_file() or not 0<p.stat().st_size<=maximum:
            raise ValueError("U_FOLD_ARTIFACT_MISSING_OR_UNBOUNDED:"+key)
    if paths["inp"].read_bytes()!=deck.encode("utf-8"):
        raise ValueError("U_FOLD_DECK_PROVENANCE_MISMATCH")
    _completed(paths["sta"])
    u=_dat_vectors(paths["dat"],"TIP","U")
    rf=_dat_vectors(paths["dat"],"ROOT","RF")
    if set(u)!=tip or set(rf)!=root:
        raise ValueError("U_FOLD_DAT_NODE_COVERAGE_MISMATCH")
    tip_z=-sum(loads[nid]*u[nid][2] for nid in tip)/FORCE
    root_rfz=sum(v[2] for v in rf.values())
    if (not math.isfinite(tip_z) or tip_z<=0 or
            abs(root_rfz-FORCE)/FORCE>0.02):
        raise ValueError("U_FOLD_TRANSLATION_OR_FORCE_REJECTED")
    return {"tip_mean_displacement_mm":tip_z,
            "root_z_force_n":root_rfz,
            "artifact_sha256":{k:hashlib.sha256(p.read_bytes()).hexdigest()
                               for k,p in paths.items()}}


def assess(observed:dict[int,float]) -> dict:
    if (not isinstance(observed,dict) or set(observed)!=set(MESHES) or
            any(type(v) not in (int,float) or not math.isfinite(v) or v<=0
                for v in observed.values())):
        raise ValueError("U_FOLD_MESH_VALUES_INVALID")
    expected=beam_reference()
    analytic=expected["cantilever_tip_deflection_mm"]
    difference=abs(observed[16]-analytic)/analytic
    mesh_difference=abs(observed[16]-observed[8])/analytic
    if difference>0.25:
        raise ValueError("U_FOLD_BEAM_ORACLE_DISAGREEMENT:"+repr(observed))
    if mesh_difference>0.15:
        raise ValueError("U_FOLD_MESH_CHANGE_TOO_LARGE:"+repr(observed))
    if max(observed.values())>=0.05*T:
        raise ValueError("U_FOLD_LARGE_DEFLECTION_OUTSIDE_SCOPE")
    return {**expected,"observed_by_mesh_mm":observed,
            "fine_mesh_reference_relative_difference":difference,
            "two_mesh_relative_change":mesh_difference,
            "screening_thresholds":{"beam":0.25,"two_mesh_change":0.15},
            "mesh_convergence_order":"NOT_ESTABLISHED",
            "six_component_global_balance":"NOT_ADMITTED",
            "material_capacity":"NOT_ADMITTED",
            "attachment_contact":"NOT_MODELED",
            "engineering_acceptance":"NOT_ADMITTED"}


def check(root:Path)->dict:
    cases={n:_case(root/f"u_fold_{n}",n) for n in MESHES}
    summary=assess({n:v["tip_mean_displacement_mm"] for n,v in cases.items()})
    summary["cases"]=cases
    return summary


if __name__=="__main__":
    if len(sys.argv)==4 and sys.argv[1]=="--generate":
        generate(Path(sys.argv[2]),int(sys.argv[3]))
        print("SYNTHETIC_U_FOLD_DECK_GENERATED; NO SOLVER EXECUTION")
    elif len(sys.argv)==2:
        print(json.dumps(check(Path(sys.argv[1])),sort_keys=True,allow_nan=False))
        print("U_FOLD_EULER_BERNOULLI_SCREENING_PASS; DESIGN_NOT_ADMITTED")
    else:
        raise SystemExit("USAGE: check_u_fold_cantilever.py ROOT | --generate DIR MESH")
