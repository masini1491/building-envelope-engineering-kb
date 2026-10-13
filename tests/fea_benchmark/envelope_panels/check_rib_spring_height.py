"""Stage 65: S8R rib-end X-spring height-window sensitivity, synthetic only.

Low (z=1..4 mm) and high (z=5..8 mm) spring windows each contain
8 identical DOF1 SPRING1 ground springs. Compare against same-CI Stage 60
free and Stage 62 all-height X-spring controls. The independent 2x2 geometry
matrix is an EXACT discrete translational-spring kinematic identity, NOT an
independent S8R shell-field oracle, actual bracket, or pure DOF4-6 spring.
"""
from __future__ import annotations
import hashlib
import json
import math
import sys
from pathlib import Path

from check_rib_end_direction import (
    K_PER_NODE, make_deck as stage62_x_deck, _case as stage62_x_case,
)
from check_rib_end_transfer import (
    MESHES, _geometry, _dat_vectors, _completed, pressure_work_proxy,
    case as stage60_free_case,
)

WINDOWS=("low","high")
SCOPE="SYNTHETIC_S8R_RIB_END_X_SPRING_HEIGHT_WINDOW"
MAX_MESH_RELATIVE_DIFFERENCE=.15
COMPLIANCE_SCREEN_MARGIN=.005


def window_nodes(n:int,window:str):
    if type(n) is not int or n not in MESHES or window not in WINDOWS:
        raise ValueError("STAGE65_CASE_OUTSIDE_SCOPE")
    original, web_nodes, end_nodes, web=stage62_x_deck(n,1)
    coords, web2, web_nodes2, endpoints2=_geometry(original,n)
    if web!=web2 or web_nodes!=web_nodes2 or end_nodes!=endpoints2:
        raise ValueError("STAGE65_STAGE62_GEOMETRY_DRIFT")
    selected={nid for nid in end_nodes
              if (0<coords[nid][2]<=4 if window=="low"
                  else 4<coords[nid][2]<=8)}
    if (len(selected)!=8 or len(end_nodes)!=16
            or len({coords[nid][2] for nid in selected})!=4
            or any(sum(abs(coords[nid][0]-x)<1e-8 for nid in selected)!=4
                   for x in (0,100))
            or set(coords[nid][2] for nid in selected)!=(set((1.,2.,3.,4.))
                if window=="low" else set((5.,6.,7.,8.)))):
        raise ValueError("STAGE65_HEIGHT_WINDOW_NODE_COVERAGE")
    return original, web_nodes, end_nodes, web, coords, selected


def geometry_matrix(coords:dict, selected:set[int]):
    # u_x(z) = u_0 + z*theta is a hypothetical rigid-section field.
    # Actual shell displacement need not obey that assumption.
    zz=[coords[nid][2] for nid in selected]
    k0=K_PER_NODE*len(zz)
    k1=K_PER_NODE*math.fsum(zz)
    k2=K_PER_NODE*math.fsum(z*z for z in zz)
    schur=k2-k1*k1/k0
    det=k0*k2-k1*k1
    if (len(zz)!=8 or not all(math.isfinite(q) for q in (k0,k1,k2,schur,det))
            or min(k0,schur,det)<=0):
        raise ValueError("STAGE65_GEOMETRIC_MATRIX_INVALID")
    return {"k00_n_per_mm":k0,"k01_n":k1,"k11_n_mm":k2,
            "condensed_rotational_coefficient_n_mm_per_rad":schur,
            "matrix_determinant":det,
            "kinematic_model":"RIGID_SECTION_ASSUMPTION_ONLY_NOT_S8R_FIELD",
            "translation_rotation_coupling":"NONZERO"}


def make_deck(n:int,window:str):
    original,web_nodes,end_nodes,web,coords,selected=window_nodes(n,window)
    begin="*ELEMENT,TYPE=SPRING1,ELSET=RIB_END_X_SPRING\n"
    original_ids=sorted(end_nodes)
    start=n*n+n*4+1
    old=begin+"".join(f"{start+i},{nid}\n" for i,nid in enumerate(original_ids))
    new=begin+"".join(f"{start+i},{nid}\n" for i,nid in enumerate(sorted(selected)))
    if original.count(old)!=1:
        raise ValueError("STAGE65_STAGE62_SPRING_ELEMENT_DRIFT")
    deck=original.replace(old,new,1)
    header="synthetic-stage62-rib_end_xspring_10000-ribheight-8-mesh-"
    if deck.count(header)!=1:
        raise ValueError("STAGE65_STAGE62_HEADER_DRIFT")
    deck=deck.replace(header,f"synthetic-stage65-xspring_{window}-ribheight-8-mesh-",1)
    if (deck.count(begin)!=1 or deck.count("*SPRING,ELSET=RIB_END_X_SPRING\n1\n10000.0\n")!=1
            or deck.count("*DLOAD\nWEB,P,0.0001")!=1 or "*CLOAD" in deck
            or "*PLASTIC" in deck or "RIB_END,1,6,0." in deck
            or deck.count("*NODE PRINT,NSET=RIB_END_SPRING_NODES\nU\n")!=1
            or deck.count("*ELEMENT,TYPE=SPRING1,ELSET=")!=1):
        raise ValueError("STAGE65_DECK_SCOPE_ESCALATION")
    return deck,web_nodes,end_nodes,web,coords,selected


def generate(folder:Path,n:int,window:str):
    folder=Path(folder)
    if folder.is_symlink() or folder.exists():
        raise ValueError("STAGE65_WORKSPACE_MUST_BE_NEW")
    deck,*_=make_deck(n,window)
    folder.mkdir(parents=True)
    (folder/"panel.inp").write_text(deck,encoding="utf-8")


def observed(folder:Path,n:int,window:str):
    deck,web_nodes,end_nodes,web,coords,selected=make_deck(n,window)
    files={ext:Path(folder)/("panel."+ext) for ext in ("inp","dat","sta","frd")}
    for ext,f in files.items():
        limit=64_000_000 if ext=="frd" else 10_000_000
        if f.is_symlink() or not f.is_file() or not 0<f.stat().st_size<=limit:
            raise ValueError("STAGE65_REQUIRED_SOLVER_ARTIFACT_MISSING:"+ext)
    if files["inp"].read_bytes()!=deck.encode("utf-8"):
        raise ValueError("STAGE65_DECK_PROVENANCE_MISMATCH")
    _completed(files["sta"])
    wu=_dat_vectors(files["dat"],"WEB_NODES","U")
    eu=_dat_vectors(files["dat"],"RIB_END_SPRING_NODES","U")
    if set(wu)!=web_nodes or set(eu)!=end_nodes:
        raise ValueError("STAGE65_SOLVER_FIELD_COVERAGE")
    work=pressure_work_proxy(web,wu,n)
    xx=[eu[nid][0] for nid in sorted(selected)]
    if any(not math.isfinite(x) for x in xx):
        raise ValueError("STAGE65_SPRING_UX_NONFINITE")
    energy=math.fsum(.5*K_PER_NODE*x*x for x in xx)
    if not energy>1e-15:
        raise ValueError("STAGE65_SPRING_PARTICIPATION_ABSENT")
    derived_f=K_PER_NODE*math.fsum(xx)
    derived_m=K_PER_NODE*math.fsum(coords[nid][2]*eu[nid][0] for nid in sorted(selected))
    if not all(math.isfinite(x) for x in (derived_f,derived_m)):
        raise ValueError("STAGE65_DERIVED_FORCE_MOMENT_NONFINITE")
    return {"web_work_conjugate_mean_u3_mm":work,
            "geometry_matrix":geometry_matrix(coords,selected),
            "spring_node_count":len(selected),
            "spring_energy_derived_n_mm":energy,
            "derived_spring_horizontal_force_n":derived_f,
            "derived_spring_z_weighted_x_force_n_mm":derived_m,
            "independent_shell_rotation_or_reaction":"NOT_OBSERVED",
            "derived_force_is_independent_ccx_reaction":"NO_K_TIMES_U_ONLY",
            "sha256":{ext:hashlib.sha256(f.read_bytes()).hexdigest() for ext,f in files.items()}}


def assess(values:dict[tuple[int,str],float],
           matrices:dict[str,dict]):
    modes=("free","full",*WINDOWS)
    if (not isinstance(values,dict) or set(values)!={(n,s) for n in MESHES for s in modes}
            or any(type(x) not in (int,float) or not math.isfinite(x) or x<=0 for x in values.values())
            or set(matrices)!=set(WINDOWS)):
        raise ValueError("STAGE65_OBSERVATION_MATRIX_INVALID")
    low,high=(matrices[w] for w in WINDOWS)
    if (abs(low["k00_n_per_mm"]-80000)>1e-8
            or abs(high["k00_n_per_mm"]-80000)>1e-8
            or abs(low["k01_n"]-200000)>1e-8
            or abs(high["k01_n"]-520000)>1e-8
            or abs(low["k11_n_mm"]-600000)>1e-8
            or abs(high["k11_n_mm"]-3480000)>1e-8
            or abs(low["condensed_rotational_coefficient_n_mm_per_rad"]-100000)>1e-8
            or abs(high["condensed_rotational_coefficient_n_mm_per_rad"]-100000)>1e-8):
        raise ValueError("STAGE65_INDEPENDENT_GEOMETRIC_ORACLE_MISMATCH")
    results={}
    for n in MESHES:
        free,full=(values[n,s] for s in ("free","full"))
        if full>free*(1+COMPLIANCE_SCREEN_MARGIN):
            raise ValueError("STAGE65_STAGE62_FULL_SPRING_ORDER_FAILURE")
        for w in WINDOWS:
            v=values[n,w]
            if (v>free*(1+COMPLIANCE_SCREEN_MARGIN)
                    or v<full*(1-COMPLIANCE_SCREEN_MARGIN)):
                raise ValueError("STAGE65_SUBSET_COMPLIANCE_OUTSIDE_FULL_FREE_BOUNDS:"+w)
        results[str(n)]={s:values[n,s] for s in modes}
    mesh={}
    for s in modes:
        delta=abs(values[16,s]-values[8,s])/values[16,s]
        if delta>MAX_MESH_RELATIVE_DIFFERENCE:
            raise ValueError("STAGE65_TWO_MESH_SCREEN_EXCEEDED:"+s)
        mesh[s]=delta
    return {"scope":SCOPE,"web_displacement_by_mesh_mm":results,
            "derived_geometric_kinematic_matrices":matrices,
            "equal_condensed_rotational_coefficient_does_not_mean_equal_shell_response":True,
            "order_between_low_and_high":"NOT_ASSUMED",
            "exact_independent_s8r_field_oracle":"NOT_ESTABLISHED",
            "full_six_component_balance":"NOT_ADMITTED",
            "local_connection_capacity":"NOT_ADMITTED",
            "engineering_acceptance":"NOT_ADMITTED",
            "two_mesh_relative_change":mesh}


def check(root:Path):
    root=Path(root)
    values={}
    cases={}
    matrix={}
    for n in MESHES:
        b=stage60_free_case(root/f"rib_end_rib_end_free_n{n}",n,"rib_end_free")
        f=stage62_x_case(root/f"rib_direction_dof1_n{n}",n,1)
        values[n,"free"]=b["web_work_conjugate_mean_u3_mm"]
        values[n,"full"]=f["web_work_conjugate_mean_u3_mm"]
        cases[f"n{n}_free"]={"origin":"SAME_CI_STAGE60_RECHECK","sha256":b["sha256"]}
        cases[f"n{n}_full"]={"origin":"SAME_CI_STAGE62_RECHECK","sha256":f["sha256"]}
        for w in WINDOWS:
            v=observed(root/f"rib_height_{w}_n{n}",n,w)
            cases[f"n{n}_{w}"]=v
            values[n,w]=v["web_work_conjugate_mean_u3_mm"]
            if w in matrix and v["geometry_matrix"]!=matrix[w]:
                raise ValueError("STAGE65_GEOMETRIC_MATRIX_MESH_DRIFT")
            matrix[w]=v["geometry_matrix"]
    out=assess(values,matrix)
    out["cases"]=cases
    return out


if __name__=="__main__":
    if len(sys.argv)==5 and sys.argv[1]=="--generate":
        generate(Path(sys.argv[2]),int(sys.argv[3]),sys.argv[4])
        print("STAGE65_SYNTHETIC_INPUT_GENERATED_NO_SOLVER")
    elif len(sys.argv)==2:
        print(json.dumps(check(Path(sys.argv[1])),sort_keys=True,allow_nan=False))
        print("STAGE65_S8R_SPRING_HEIGHT_SCREEN_PASS; NO_ROTATIONAL_CONNECTION_ADMISSION")
    else:
        raise SystemExit("USAGE: check_rib_spring_height.py ROOT | --generate DIR N low|high")
