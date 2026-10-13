"""Stage 63 isolated synthetic rigid-lever support oracle.

All model elements are translational SPRING1 DOF3. Rigid-body reference and
rotation nodes do not belong to any spring. This is the rigid-beam (EI -> inf)
limit, NOT finite-EI Euler-Bernoulli, S8R shell coupling, a true rotational
spring element, an independent support reaction, or connector/design capacity.
Units: N, mm, N/mm, N*mm.
"""
from __future__ import annotations
import hashlib
import json
import math
import re
import sys
from pathlib import Path

CASES=("rotation","distribution")
SPRINGS={
    "rotation":((-50.,200.),(50.,200.)),
    # Three principal supports, two added offsets. The offsets ADD both
    # translation and geometric rotation stiffness; they are NOT pure k_theta.
    "distribution":((-50.,100.),(0.,200.),(50.,300.),(-10.,500.),(10.,500.))}
LOADS={"rotation":((1,-50.,-1.),(2,50.,1.)),
       "distribution":((6,10.,1.),)}
REF=100
ROT=101

def oracle(case):
    if case not in CASES: raise ValueError("STAGE63_CASE_NOT_ADMITTED")
    springs=SPRINGS[case]
    k0=math.fsum(k for x,k in springs)
    k1=math.fsum(k*x for x,k in springs)
    k2=math.fsum(k*x*x for x,k in springs)
    p=math.fsum(f for n,x,f in LOADS[case])
    q=math.fsum(x*f for n,x,f in LOADS[case])
    det=k0*k2-k1*k1
    if det<=0 or not all(map(math.isfinite,(k0,k1,k2,p,q,det))):
        raise ValueError("STAGE63_ORACLE_SINGULAR")
    w=(k2*p-k1*q)/det
    s=(k0*q-k1*p)/det  # uz=w+x*s; physical theta_y=-s
    return {"case":case,"force_n":p,"x_fz_n_mm":q,
            "k0_n_per_mm":k0,"k1_n":k1,"k2_n_mm":k2,
            "reference_uz_mm":w,"slope_rad":s,"theta_y_rad":-s,
            "k_u_n":[k*(w+x*s) for x,k in springs],
            "energy_n_mm":.5*math.fsum(k*(w+x*s)**2 for x,k in springs),
            "pure_rotation_spring":"NOT_CLAIMED",
            "finite_EI_bending":"NOT_SOLVED",
            "engineering_capacity":"NOT_ADMITTED"}

def finite_ei_theory_only():
    L,E,I,P,kt=100.,69000.,1000.,1.,1e6
    a=P*L**3/(3*E*I)
    b=P*L**2/kt
    return {"beam_bending_mm":a,"rotation_mm":b,
            "combined_tip_mm":a+b,"ccx_match":"NOT_ADMITTED_FINITE_EI"}

def deck(case):
    if case not in CASES: raise ValueError("STAGE63_CASE_NOT_ADMITTED")
    springs=SPRINGS[case]
    nodes=[f"{i},{x:.8f},0.,0." for i,(x,k) in enumerate(springs,1)]
    aux=6 if case=="distribution" else 3
    nodes.append(f"{aux},{10 if case=='distribution' else 100}.,0.,0.")
    # Non-collinear dummy rigid body node avoids undefined rigid-body axis.
    nodes += ["99,0.,1.,0.","100,0.,0.,0.","101,0.,0.,0."]
    body=list(range(1,len(springs)+1))+[aux,99]
    lines=["*HEADING",f"stage63-synthetic-rigid-lever-{case}",
           "*NODE",*nodes,"*NSET,NSET=RIGID_LEVER",",".join(map(str,body)),
           "*NSET,NSET=SUPPORT_NODES",",".join(str(i) for i in range(1,len(springs)+1)),
           "*NSET,NSET=REFERENCE","100",
           "*RIGID BODY,NSET=RIGID_LEVER,REF NODE=100,ROT NODE=101"]
    for i,(x,k) in enumerate(springs,1):
        lines += [f"*ELEMENT,TYPE=SPRING1,ELSET=SPRING_{i}",
                  f"{i},{i}",f"*SPRING,ELSET=SPRING_{i}","3",f"{k:.8f}"]
    lines += ["*BOUNDARY","100,1,2,0.","101,1,1,0.","101,3,3,0.",
              "*STEP","*STATIC","0.1,1.,0.00001,0.1","*CLOAD"]
    lines += [f"{n},3,{f:.8f}" for n,x,f in LOADS[case]]
    lines += ["*NODE PRINT,NSET=SUPPORT_NODES","U",
              "*NODE PRINT,NSET=REFERENCE","U","*END STEP"]
    return "\n".join(lines)+"\n"

def generate(folder,case):
    folder=Path(folder)
    if case not in CASES or folder.is_symlink() or folder.exists():
        raise ValueError("STAGE63_NEW_WORKSPACE_REQUIRED")
    folder.mkdir(parents=True)
    (folder/"panel.inp").write_text(deck(case),encoding="utf-8")

def _dat(path,name):
    contents=path.read_text(encoding="utf-8",errors="replace")
    matches=list(re.finditer(r"displacements \(vx,vy,vz\) for set "+name+
                            r" and time\s+([+.\dEe-]+)",contents,re.I))
    if not matches or abs(float(matches[-1].group(1))-1)>1e-7:
        raise ValueError("STAGE63_FINAL_DAT_FIELD_MISSING:"+name)
    number=r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?"
    pattern=re.compile(r"\s*(\d+)\s+("+number+r")\s+("+number+r")\s+("+number+r")\s*")
    data={}
    for line in contents[matches[-1].end():].splitlines():
        if not line.strip():
            if data: break
            continue
        match=pattern.fullmatch(line)
        if match is None:
            if data: break
            continue
        nid=int(match.group(1))
        xyz=tuple(float(match.group(i)) for i in (2,3,4))
        if nid in data or not all(map(math.isfinite,xyz)):
            raise ValueError("STAGE63_DAT_DUPLICATE_OR_NONFINITE")
        data[nid]=xyz
    if not data: raise ValueError("STAGE63_DAT_EMPTY")
    return data

def check(folder,case):
    if case not in CASES: raise ValueError("STAGE63_CASE_NOT_ADMITTED")
    folder=Path(folder)
    files={ext:folder/("panel."+ext) for ext in ("inp","dat","sta","frd")}
    for ext,f in files.items():
        cap=64000000 if ext=="frd" else 10000000
        if f.is_symlink() or not f.is_file() or not 0<f.stat().st_size<=cap:
            raise ValueError("STAGE63_REQUIRED_SOLVER_ARTIFACT_MISSING:"+ext)
    if files["inp"].read_bytes()!=deck(case).encode("utf-8"):
        raise ValueError("STAGE63_EXACT_DECK_MISMATCH")
    from check_u_fold_cantilever import _completed
    _completed(files["sta"])
    data=_dat(files["dat"],"SUPPORT_NODES")
    ref=_dat(files["dat"],"REFERENCE")
    springs=SPRINGS[case]
    if set(data)!=set(range(1,len(springs)+1)) or set(ref)!={REF}:
        raise ValueError("STAGE63_SOLVER_FIELD_COVERAGE")
    expected=oracle(case)
    for i,(x,k) in enumerate(springs,1):
        want=expected["reference_uz_mm"]+x*expected["slope_rad"]
        got=data[i][2]
        if abs(got-want)>max(5e-7,.03*abs(want)):
            raise ValueError(f"STAGE63_SOLVER_ORACLE_MISMATCH:{case}:{i}:{got}:{want}")
    if abs(ref[REF][2]-expected["reference_uz_mm"])>max(5e-7,.03*abs(expected["reference_uz_mm"])):
        raise ValueError("STAGE63_REFERENCE_MISMATCH")
    # Derived k*u only. This is NOT independently observed CCX spring reaction.
    forces=[k*data[i][2] for i,(x,k) in enumerate(springs,1)]
    total=math.fsum(forces)
    moment=math.fsum(x*f for (x,k),f in zip(springs,forces))
    if abs(total-expected["force_n"])>max(.005,.03*abs(expected["force_n"])):
        raise ValueError("STAGE63_KU_FORCE_MISMATCH")
    if abs(moment-expected["x_fz_n_mm"])>max(.05,.03*abs(expected["x_fz_n_mm"])):
        raise ValueError("STAGE63_KU_MOMENT_MISMATCH")
    return {"case":case,"observed_support_uz_mm":{str(i):data[i][2] for i in data},
            "observed_reference_uz_mm":ref[REF][2],
            "oracle":expected,"derived_k_u_force_n":total,"derived_x_k_u_n_mm":moment,
            "independent_support_reaction":"NO_K_U_DERIVED_ONLY",
            "S8R_shell_and_rotational_spring":"NOT_ADMITTED",
            "engineering_capacity":"NOT_ADMITTED",
            "sha256":{ext:hashlib.sha256(f.read_bytes()).hexdigest() for ext,f in files.items()}}

if __name__=="__main__":
    if len(sys.argv)==4 and sys.argv[1]=="--generate":
        generate(Path(sys.argv[2]),sys.argv[3])
        print("STAGE63_DECK_GENERATED_NO_SOLVER")
    elif len(sys.argv)==2:
        root=Path(sys.argv[1])
        output={"cases":{c:check(root/("rigid_lever_"+c),c) for c in CASES},
                "finite_EI_theory_only":finite_ei_theory_only(),
                "engineering_capacity":"NOT_ADMITTED"}
        print(json.dumps(output,sort_keys=True,allow_nan=False))
        print("STAGE63_RIGID_LEVER_ORACLE_PASS; NO_CONNECTOR_ADMISSION")
    else:
        raise SystemExit("USAGE: check_rigid_lever_rotation.py ROOT | --generate DIR rotation|distribution")
