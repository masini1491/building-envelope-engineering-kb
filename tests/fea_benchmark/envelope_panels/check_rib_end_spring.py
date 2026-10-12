"""Stage 61: synthetic rib-end DOF-3 ground springs in CalculiX SPRING1.

Preserves Stage-60 geometry, web pressure and external plate clamping. Only
per-node translational stiffness at the 16 elevated rib-end nodes is varied.
Linear-elastic compliance monotonicity is a small-load screening oracle; not
a nonlinear follower-pressure theorem, fastener capacity or full balance.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

from check_rib_end_transfer import (
    MESHES, _dat_vectors, _geometry, _lists, _completed,
    build as stage60_build, case as stage60_case,
    pressure_work_proxy,
)

STIFFNESS_PER_NODE_N_MM=(1000,10000)
MODEL_LABEL="SYNTHETIC_RIB_END_Z_ONLY_SPRING_TO_GROUND"


def make_deck(n:int,k:int)->tuple[str,set[int],set[int],list[tuple[int,...]]]:
    if type(n) is not int or n not in MESHES or type(k) is not int or k not in STIFFNESS_PER_NODE_N_MM:
        raise ValueError("RIB_SPRING_VARIANT_OUTSIDE_SCOPE")
    original,web_nodes,end_nodes,web=stage60_build(n,"rib_end_free")
    if (len(end_nodes)!=16 or len(web)!=n*n or
            any(node in web_nodes for node in end_nodes)):
        raise ValueError("RIB_SPRING_BASE_GEOMETRY_CHANGED")
    anchor="*MATERIAL,NAME=SYNTHETIC_ELASTIC\n"
    if original.count(anchor)!=1:
        raise ValueError("RIB_SPRING_MATERIAL_ANCHOR_MISSING")
    start=n*n+n*4+1
    spring_elements="*ELEMENT,TYPE=SPRING1,ELSET=RIB_END_Z_SPRING\n"
    spring_elements+="\n".join(f"{start+i},{nid}" for i,nid in enumerate(sorted(end_nodes)))+"\n"
    deck=original.replace(anchor,spring_elements+anchor,1)
    anchor="*NSET,NSET=WEB_NODES\n"
    if deck.count(anchor)!=1:
        raise ValueError("RIB_SPRING_NODESET_ANCHOR_MISSING")
    deck=deck.replace(anchor,"*NSET,NSET=RIB_END_SPRING_NODES\n"+
                      _lists(end_nodes)+"\n"+anchor,1)
    boundary="*STEP,NLGEOM\n"
    if deck.count(boundary)!=1:
        raise ValueError("RIB_SPRING_STEP_ANCHOR_MISSING")
    deck=deck.replace(boundary,
        "*SPRING,ELSET=RIB_END_Z_SPRING\n3\n"+f"{float(k):.1f}"+"\n"+boundary,1)
    web_print="*NODE PRINT,NSET=WEB_NODES\nU\n"
    if deck.count(web_print)!=1:
        raise ValueError("RIB_SPRING_PRINT_ANCHOR_MISSING")
    deck=deck.replace(web_print,
                      web_print+"*NODE PRINT,NSET=RIB_END_SPRING_NODES\nU\n",1)
    if deck.count("synthetic-stage60-rib_end_free-ribheight-8-mesh-")!=1:
        raise ValueError("RIB_SPRING_HEADER_NOT_CANONICAL")
    deck=deck.replace("synthetic-stage60-rib_end_free-ribheight-8-mesh-",
                      f"synthetic-stage61-rib_end_zspring_{k}-ribheight-8-mesh-",1)
    if (deck.count("*ELEMENT,TYPE=SPRING1,ELSET=RIB_END_Z_SPRING")!=1
            or deck.count("*SPRING,ELSET=RIB_END_Z_SPRING")!=1
            or deck.count("ROOT,1,6,0.")!=1
            or deck.count("RIB_END,1,6,0.")!=0
            or deck.count("*DLOAD\nWEB,P,0.0001")!=1
            or "*CLOAD" in deck or "*PLASTIC" in deck):
        raise ValueError("RIB_SPRING_DECK_SCOPE_ESCALATION")
    return deck,web_nodes,end_nodes,web


def generate(folder:Path,n:int,k:int)->None:
    if folder.exists() or folder.is_symlink():
        raise ValueError("RIB_SPRING_WORKSPACE_MUST_BE_NEW")
    deck,*_=make_deck(n,k)
    folder.mkdir(parents=True)
    (folder/"panel.inp").write_text(deck,encoding="utf-8")


def _artifact_files(folder:Path)->dict[str,Path]:
    files={ext:folder/f"panel.{ext}" for ext in ("inp","dat","sta","frd")}
    for ext,path in files.items():
        max_size=64_000_000 if ext=="frd" else 10_000_000
        if (path.is_symlink() or not path.is_file()
                or not 0<path.stat().st_size<=max_size):
            raise ValueError("RIB_SPRING_ARTIFACT_MISSING_OR_UNBOUNDED:"+ext)
    return files


def _case(folder:Path,n:int,k:int)->dict:
    deck,web_nodes,end_nodes,web=make_deck(n,k)
    files=_artifact_files(folder)
    if files["inp"].read_bytes()!=deck.encode("utf-8"):
        raise ValueError("RIB_SPRING_DECK_PROVENANCE_MISMATCH")
    _completed(files["sta"])
    web_u=_dat_vectors(files["dat"],"WEB_NODES","U")
    end_u=_dat_vectors(files["dat"],"RIB_END_SPRING_NODES","U")
    if set(web_u)!=web_nodes or set(end_u)!=end_nodes:
        raise ValueError("RIB_SPRING_PRINTED_NODES_INCOMPLETE")
    w=pressure_work_proxy(web,web_u,n)
    displacements=[end_u[nid][2] for nid in sorted(end_nodes)]
    if any(not math.isfinite(u) for u in displacements):
        raise ValueError("RIB_SPRING_DISPLACEMENT_NONFINITE")
    raw_kinematic_force=math.fsum(k*u for u in displacements)
    spring_energy=math.fsum(k*u*u/2 for u in displacements)
    if not (spring_energy>1e-16 and math.isfinite(raw_kinematic_force)):
        raise ValueError("RIB_SPRING_RESPONSE_SIGNAL_MISSING")
    return {"web_work_conjugate_mean_u3_mm":w,
            "spring_nodal_stiffness_n_per_mm":k,
            "spring_node_count":len(end_nodes),
            "derived_spring_z_force_sum_n":raw_kinematic_force,
            "derived_spring_energy_n_mm":spring_energy,
            "spring_force_independently_measured":"NO_K_TIMES_U_ONLY",
            "artifact_sha256":{
                ext:hashlib.sha256(path.read_bytes()).hexdigest()
                for ext,path in files.items()}}


def assess(values:dict[tuple[int,int],float])->dict:
    expected={(n,k) for n in MESHES for k in (0,*STIFFNESS_PER_NODE_N_MM)}
    if (not isinstance(values,dict) or set(values)!=expected or
        any(type(v) not in (float,int) or not math.isfinite(v) or v<=0
            for v in values.values())):
        raise ValueError("RIB_SPRING_OBSERVATION_MATRIX_INVALID")
    delta={}
    for n in MESHES:
        base,lo,hi=(values[n,k] for k in (0,*STIFFNESS_PER_NODE_N_MM))
        if not base>lo>hi:
            raise ValueError("RIB_SPRING_COMPLIANCE_NOT_MONOTONIC:"+str(n))
        delta[n]={"baseline_to_low_ratio":lo/base,
                  "low_to_high_ratio":hi/lo,
                  "high_to_baseline_ratio":hi/base}
    mesh_error={}
    for k in (0,*STIFFNESS_PER_NODE_N_MM):
        mesh_error[str(k)]=abs(values[16,k]-values[8,k])/values[16,k]
        if mesh_error[str(k)]>.15:
            raise ValueError("RIB_SPRING_MESH_DIFFERENCE_EXCESSIVE:"+str(k))
    return {"scope":MODEL_LABEL,
            "work_conjugate_web_displacement_mm":{
                str(n):{str(k):values[n,k] for k in (0,*STIFFNESS_PER_NODE_N_MM)}
                for n in MESHES},
            "stiffness_ratio_observations":delta,
            "two_mesh_relative_change":mesh_error,
            "spring_stiffness_per_node_n_mm":list(STIFFNESS_PER_NODE_N_MM),
            "ground_spring_degree_of_freedom":3,
            "physical_screen":"SMALL_LOAD_LINEAR_ELASTIC_POSITIVE_SEMIDEFINITE_SPRING_STIFFNESS_TREND",
            "nlgeom_follower_pressure_exact_monotonicity":"NOT_CLAIMED",
            "rotational_stiffness":"NOT_MODELED",
            "direct_spring_force_validation":"NOT_ESTABLISHED_K_TIMES_U_ONLY",
            "actual_connector_or_fastener":"NOT_MODELED",
            "global_six_component_balance":"NOT_ADMITTED",
            "engineering_acceptance":"NOT_ADMITTED"}


def check(root:Path)->dict:
    cases={}
    work={}
    for n in MESHES:
        # The existing Stage 60 workflow produces exact same-revision free
        # endpoint evidence before the Stage 61 runs. Re-check its full deck,
        # solver-step and printed-field provenance via the Stage 60 checker.
        baseline=stage60_case(root/f"rib_end_rib_end_free_n{n}",n,"rib_end_free")
        cases[f"n{n}_k0_baseline"]={
            "origin":"SAME_WORKFLOW_STAGE60_EXACT_DECK_REVALIDATED",
            "web_work_conjugate_mean_u3_mm":baseline["web_work_conjugate_mean_u3_mm"],
            "artifact_sha256":baseline["sha256"]}
        work[n,0]=baseline["web_work_conjugate_mean_u3_mm"]
        for k in STIFFNESS_PER_NODE_N_MM:
            value=_case(root/f"rib_spring_k{k}_n{n}",n,k)
            cases[f"n{n}_k{k}"]=value
            work[n,k]=value["web_work_conjugate_mean_u3_mm"]
    output=assess(work)
    output["cases"]=cases
    return output


if __name__=="__main__":
    if len(sys.argv)==5 and sys.argv[1]=="--generate":
        generate(Path(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]))
        print("RIB_END_SPRING_DECK_GENERATED_NO_SOLVER")
    elif len(sys.argv)==2:
        print(json.dumps(check(Path(sys.argv[1])),sort_keys=True,allow_nan=False))
        print("RIB_END_SPRING_STIFFNESS_TREND_PASS; NO_DESIGN_ADMISSION")
    else:
        raise SystemExit("USAGE: check_rib_end_spring.py ROOT | --generate DIR N STIFFNESS")
