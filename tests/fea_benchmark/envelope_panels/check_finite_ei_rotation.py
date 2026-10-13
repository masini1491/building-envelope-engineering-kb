"""Stage 64 research candidate: finite-EI B31 cantilever with synthetic root lever.

Two bounding cases use identical finite-EI B31 main beams: a fully clamped
root, and a translation-fixed root joined to two high-E B31 arm elements and
DOF3 SPRING1. The arm approximation is elastic and NOT a rigid-body MPC.
Euler-Bernoulli provides an independent small-deflection reference. CCX B31
includes formulation effects; this is a tolerance-bounded SCREENING, not an
exact analytical equivalence or manufactured connection.
Only N-mm-MPa synthetic elastic values. No S8R, strength or capacity admission.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from pathlib import Path

L, E, NU, SIDE, P = 100.0, 69000.0, .33, 10.0, 1.0
A = 50.0
K_PER_LEVER = 200.0
E_ARM = E*10000.0  # deliberately synthetic finite-stiffness transfer beams
MESHES = (4, 8)
CASES = ("clamped", "root_spring")
LEFT, RIGHT = 901, 902
ROOT, TIP = 1, -1
MAX_RELATIVE_BENDING_ERROR = .12
MAX_RELATIVE_SPRING_INCREMENT_ERROR = .10
MAX_MESH_DIFFERENCE = .12

def analytical():
    iy=SIDE**4/12
    kt=2*K_PER_LEVER*A*A
    beam=P*L**3/(3*E*iy)
    spring=P*L**2/kt
    return {"length_mm":L,"youngs_mpa":E,"second_moment_mm4":iy,
            "root_rotational_stiffness_n_mm_per_rad":kt,
            "euler_bernoulli_tip_bending_mm":beam,
            "finite_root_rotation_rad":P*L/kt,
            "finite_root_rotation_tip_increment_mm":spring,
            "finite_root_rotation_total_tip_mm":beam+spring,
            "theory":"EULER_BERNOULLI_REFERENCE_NOT_AN_EXACT_CCX_B31_IDENTITY",
            "engineering_capacity":"NOT_ADMITTED"}

def build(mesh, case):
    if type(mesh) is not int or mesh not in MESHES:
        raise ValueError("STAGE64_MESH_OUTSIDE_SCOPE")
    if case not in CASES:
        raise ValueError("STAGE64_CASE_OUTSIDE_SCOPE")
    tip=mesh+1
    lines=["*HEADING",f"stage64-synthetic-finite-EI-{case}-n{mesh}",
           "*NODE"]
    lines += [f"{i+1},{L*i/mesh:.8f},0.,0." for i in range(mesh+1)]
    if case=="root_spring":
        lines += [f"{LEFT},{-A:.8f},0.,0.",
                  f"{RIGHT},{A:.8f},0.,0."]
    lines += ["*ELEMENT,TYPE=B31,ELSET=FINITE_BEAM"]
    lines += [f"{i},{i},{i+1}" for i in range(1,mesh+1)]
    lines += ["*MATERIAL,NAME=SYNTHETIC_ELASTIC","*ELASTIC",f"{E:.8f},{NU:.8f}",
              "*BEAM SECTION,ELSET=FINITE_BEAM,MATERIAL=SYNTHETIC_ELASTIC,SECTION=RECT",
              f"{SIDE:.8f},{SIDE:.8f}","0.,1.,0."]
    lines += ["*NSET,NSET=BEAM_TIP",str(tip),
              "*NSET,NSET=BEAM_ROOT","1"]
    if case=="clamped":
        lines += ["*BOUNDARY","1,1,6,0."]
    else:
        # Independent side members physically share node 1 with the main B31.
        # This establishes a finite-EI moment-transfer route by beam elements,
        # rather than assuming a rigid-body MPC ties B31 root rotation.
        lines += ["*ELEMENT,TYPE=B31,ELSET=FINITE_STIFF_LEVERS",
                  f"{mesh+1},{LEFT},1",f"{mesh+2},1,{RIGHT}",
                  "*MATERIAL,NAME=SYNTHETIC_LEVER_ELASTIC","*ELASTIC",
                  f"{E_ARM:.8f},{NU:.8f}",
                  "*BEAM SECTION,ELSET=FINITE_STIFF_LEVERS,MATERIAL=SYNTHETIC_LEVER_ELASTIC,SECTION=RECT",
                  f"{SIDE:.8f},{SIDE:.8f}","0.,1.,0.",
                  "*NSET,NSET=LEVERS",f"{LEFT},{RIGHT}",
                  "*ELEMENT,TYPE=SPRING1,ELSET=LEVER_SPRINGS",
                  f"{mesh+3},{LEFT}",f"{mesh+4},{RIGHT}",
                  "*SPRING,ELSET=LEVER_SPRINGS","3",f"{K_PER_LEVER:.8f}",
                  "*BOUNDARY",
                  "1,1,4,0.","1,6,6,0."]
    lines += ["*STEP","*STATIC","0.05,1.,0.00001,0.1",
              "*CLOAD",f"{tip},3,{-P:.8f}",
              "*NODE FILE,OUTPUT=3D","U,RF",
              "*NODE PRINT,NSET=BEAM_TIP","U",
              "*NODE PRINT,NSET=BEAM_ROOT","U"]
    if case=="root_spring":
        lines += ["*NODE PRINT,NSET=LEVERS","U"]
    lines += ["*END STEP"]
    return "\n".join(lines)+"\n"

def generate(root,mesh,case):
    root=Path(root)
    if root.is_symlink() or root.exists():
        raise ValueError("STAGE64_NEW_WORKSPACE_REQUIRED")
    payload=build(mesh,case)
    root.mkdir(parents=True)
    (root/"panel.inp").write_text(payload,encoding="utf-8")

def dat_vector(path,name):
    s=path.read_text(encoding="utf-8",errors="replace")
    hits=list(re.finditer(r"displacements \(vx,vy,vz\) for set "+name+
                         r" and time\s+([+.\dEe-]+)",s,re.I))
    if not hits or abs(float(hits[-1].group(1))-1)>1e-7:
        raise ValueError("STAGE64_FINAL_DAT_FIELD_MISSING:"+name)
    number=r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?"
    pat=re.compile(r"\s*(\d+)\s+("+number+r")\s+("+number+r")\s+("+number+r")\s*")
    rows={}
    for line in s[hits[-1].end():].splitlines():
        if not line.strip():
            if rows: break
            continue
        m=pat.fullmatch(line)
        if m is None:
            if rows: break
            continue
        node=int(m.group(1))
        v=tuple(float(m.group(i)) for i in (2,3,4))
        if node in rows or not all(map(math.isfinite,v)):
            raise ValueError("STAGE64_DAT_INVALID_VECTOR")
        rows[node]=v
    if not rows: raise ValueError("STAGE64_DAT_EMPTY")
    return rows

def observed(root,mesh,case):
    root=Path(root)
    files={ext:root/("panel."+ext) for ext in ("inp","dat","sta","frd")}
    for ext,f in files.items():
        cap=64000000 if ext=="frd" else 10000000
        if f.is_symlink() or not f.is_file() or not 0<f.stat().st_size<=cap:
            raise ValueError("STAGE64_SOLVER_ARTIFACT_MISSING:"+ext)
    if files["inp"].read_bytes()!=build(mesh,case).encode("utf-8"):
        raise ValueError("STAGE64_INPUT_PROVENANCE_MISMATCH")
    from check_u_fold_cantilever import _completed
    _completed(files["sta"])
    tip=dat_vector(files["dat"],"BEAM_TIP")
    base=dat_vector(files["dat"],"BEAM_ROOT")
    if set(tip)!={mesh+1} or set(base)!={1}:
        raise ValueError("STAGE64_BEAM_FIELD_COVERAGE")
    d=-tip[mesh+1][2]
    if not math.isfinite(d) or d<=0 or d>1.0:
        raise ValueError("STAGE64_TIP_RESPONSE_NONPHYSICAL_OR_UNBOUNDED")
    result={"case":case,"mesh":mesh,"tip_downward_mm":d,
            "beam_root_uz_mm":base[1][2],
            "artifact_sha256":{ext:hashlib.sha256(f.read_bytes()).hexdigest() for ext,f in files.items()},
            "engineering_capacity":"NOT_ADMITTED"}
    if case=="root_spring":
        arms=dat_vector(files["dat"],"LEVERS")
        if set(arms)!={LEFT,RIGHT}: raise ValueError("STAGE64_LEVER_FIELD_COVERAGE")
        if max(abs(arms[LEFT][2]),abs(arms[RIGHT][2]))<1e-9:
            raise ValueError("STAGE64_LEVER_NOT_PARTICIPATING")
        slope=(arms[RIGHT][2]-arms[LEFT][2])/(2*A)
        total=K_PER_LEVER*(arms[LEFT][2]+arms[RIGHT][2])
        moment=A*K_PER_LEVER*(arms[RIGHT][2]-arms[LEFT][2])
        if abs(total)>max(.002,.01*P):
            raise ValueError("STAGE64_LEVER_FORCE_BALANCE")
        if abs(moment+P*L)>max(.5,.01*P*L):
            raise ValueError("STAGE64_LEVER_MOMENT_BALANCE")
        if abs(-slope-analytical()["finite_root_rotation_rad"])>1e-5:
            raise ValueError("STAGE64_ROOT_ROTATION_ORACLE_MISMATCH")
        result.update({"lever_slope_rad":slope,"lever_to_beam_elastic_modulus_ratio":E_ARM/E,
                       "k_u_total_n":total,
                       "x_k_u_total_n_mm":moment,
                       "independent_lever_reaction":"NOT_OBSERVED_K_U_DERIVED_ONLY"})
    return result

def assess(cases):
    if set(cases)!={(mesh,case) for mesh in MESHES for case in CASES}:
        raise ValueError("STAGE64_CASE_COVERAGE")
    theory=analytical()
    comparison={}
    for mesh in MESHES:
        fixed=cases[mesh,"clamped"]["tip_downward_mm"]
        sprung=cases[mesh,"root_spring"]["tip_downward_mm"]
        increment=sprung-fixed
        if not 0<fixed<sprung:
            raise ValueError("STAGE64_SPRING_COMPLIANCE_ORDER")
        err_fixed=abs(fixed-theory["euler_bernoulli_tip_bending_mm"])/theory["euler_bernoulli_tip_bending_mm"]
        err_spring=abs(increment-theory["finite_root_rotation_tip_increment_mm"])/theory["finite_root_rotation_tip_increment_mm"]
        if err_fixed>MAX_RELATIVE_BENDING_ERROR:
            raise ValueError("STAGE64_FINITE_EI_BENDING_SCREEN_FAILURE")
        if err_spring>MAX_RELATIVE_SPRING_INCREMENT_ERROR:
            raise ValueError("STAGE64_ROOT_SPRING_INCREMENT_SCREEN_FAILURE")
        comparison[str(mesh)]={"clamped_mm":fixed,"sprung_mm":sprung,
                               "additional_root_rotation_mm":increment,
                               "bending_relative_error":err_fixed,"increment_relative_error":err_spring}
    for case in CASES:
        x=cases[4,case]["tip_downward_mm"]
        y=cases[8,case]["tip_downward_mm"]
        if abs(x-y)/y>MAX_MESH_DIFFERENCE:
            raise ValueError("STAGE64_MESH_SCREEN_FAILURE:"+case)
    return {"scope":"SYNTHETIC_B31_FINITE_EI_ROOT_ROTATION_SCREEN_ONLY",
            "theory":theory,"comparison":comparison,
            "independent_reaction_moment":"NOT_ADMITTED",
            "S8R_SHELL_CONNECTOR":"NOT_ADMITTED",
            "general_six_component_balance":"NOT_ADMITTED",
            "engineering_capacity":"NOT_ADMITTED"}

def check(root):
    root=Path(root)
    cases={(n,c):observed(root/f"finite_ei_{c}_n{n}",n,c)
           for n in MESHES for c in CASES}
    output=assess(cases)
    output["cases"]={f"n{n}_{c}":x for (n,c),x in cases.items()}
    return output

if __name__=="__main__":
    if len(sys.argv)==5 and sys.argv[1]=="--generate":
        generate(Path(sys.argv[2]),int(sys.argv[3]),sys.argv[4])
        print("STAGE64_SYNTHETIC_DECK_ONLY")
    elif len(sys.argv)==2:
        print(json.dumps(check(Path(sys.argv[1])),sort_keys=True,allow_nan=False))
        print("STAGE64_FINITE_EI_ROTATIONAL_COMPLIANCE_SCREEN_PASS; NO_DESIGN_ADMISSION")
    else:
        raise SystemExit("USAGE: check_finite_ei_rotation.py ROOT | --generate DIR N clamped|root_spring")
