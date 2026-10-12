"""Stage 62: bounded rib-end SPRING1 translational direction sensitivity.

Compare DOF1 / DOF2 against existing same-CI DOF3 and free rib-end controls
at identical k = 10000 N/mm per spring. This is NOT rotational stiffness,
a fastener stiffness, a directional load capacity or six-DOF support design.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

from check_rib_end_spring import (
    MESHES, _case as stage61_case, make_deck as stage61_deck,
)
from check_rib_end_transfer import (
    _dat_vectors, _completed, pressure_work_proxy, case as stage60_case,
)

K_PER_NODE=10000
DIRECTIONS=(1,2)
DOF_LABELS={1:"X",2:"Y",3:"Z"}
SCOPE="SYNTHETIC_CENTER_RIB_END_TRANSLATIONAL_DIRECTION_AB"


def make_deck(n:int,dof:int):
    if type(n) is not int or n not in MESHES or type(dof) is not int or dof not in DIRECTIONS:
        raise ValueError("RIB_DIRECTION_SCOPE_REJECTED")
    original,web_nodes,end_nodes,web=stage61_deck(n,K_PER_NODE)
    old=f"*SPRING,ELSET=RIB_END_Z_SPRING\n3\n{K_PER_NODE:.1f}\n"
    new=f"*SPRING,ELSET=RIB_END_{DOF_LABELS[dof]}_SPRING\n{dof}\n{K_PER_NODE:.1f}\n"
    if original.count(old)!=1 or original.count("RIB_END_Z_SPRING")!=2:
        raise ValueError("RIB_DIRECTION_STAGE61_ANCHOR_DRIFT")
    deck=original.replace("RIB_END_Z_SPRING",f"RIB_END_{DOF_LABELS[dof]}_SPRING").replace(old.replace("RIB_END_Z_SPRING",f"RIB_END_{DOF_LABELS[dof]}_SPRING"),new)
    from_head="synthetic-stage61-rib_end_zspring_10000-ribheight-8-mesh-"
    to_head=f"synthetic-stage62-rib_end_{DOF_LABELS[dof].lower()}spring_10000-ribheight-8-mesh-"
    if deck.count(from_head)!=1:
        raise ValueError("RIB_DIRECTION_STAGE61_HEADER_DRIFT")
    deck=deck.replace(from_head,to_head)
    if (deck.count(f"*SPRING,ELSET=RIB_END_{DOF_LABELS[dof]}_SPRING\n{dof}\n10000.0\n")!=1
            or "RIB_END_Z_SPRING" in deck or "RIB_END,1,6,0." in deck
            or deck.count("*DLOAD\nWEB,P,0.0001")!=1
            or "*CLOAD" in deck or "*PLASTIC" in deck):
        raise ValueError("RIB_DIRECTION_DECK_SCOPE_ESCALATION")
    return deck,web_nodes,end_nodes,web


def generate(directory:Path,n:int,dof:int)->None:
    if directory.is_symlink() or directory.exists():
        raise ValueError("RIB_DIRECTION_DESTINATION_MUST_BE_NEW")
    deck,*_=make_deck(n,dof)
    directory.mkdir(parents=True)
    (directory/"panel.inp").write_text(deck,encoding="utf-8")


def _case(directory:Path,n:int,dof:int)->dict:
    deck,web_nodes,end_nodes,web=make_deck(n,dof)
    files={ext:directory/f"panel.{ext}" for ext in ("inp","dat","sta","frd")}
    for ext,p in files.items():
        max_bytes=64_000_000 if ext=="frd" else 10_000_000
        if p.is_symlink() or not p.is_file() or not 0<p.stat().st_size<=max_bytes:
            raise ValueError("RIB_DIRECTION_REQUIRED_ARTIFACT_MISSING:"+ext)
    if files["inp"].read_bytes()!=deck.encode("utf-8"):
        raise ValueError("RIB_DIRECTION_INPUT_PROVENANCE_FAILURE")
    _completed(files["sta"])
    web_u=_dat_vectors(files["dat"],"WEB_NODES","U")
    end_u=_dat_vectors(files["dat"],"RIB_END_SPRING_NODES","U")
    if set(web_u)!=web_nodes or set(end_u)!=end_nodes:
        raise ValueError("RIB_DIRECTION_OUTPUT_NODE_COVERAGE")
    work=pressure_work_proxy(web,web_u,n)
    index=dof-1
    u=[end_u[node][index] for node in sorted(end_nodes)]
    if any(type(x) not in (int,float) or not math.isfinite(x) for x in u):
        raise ValueError("RIB_DIRECTION_NODAL_NONFINITE")
    energy=math.fsum(.5*K_PER_NODE*x*x for x in u)
    force=math.fsum(K_PER_NODE*x for x in u)
    if not math.isfinite(energy) or not math.isfinite(force) or energy<0:
        raise ValueError("RIB_DIRECTION_DERIVED_ENERGY_NONFINITE")
    return {
        "web_work_conjugate_mean_u3_mm":work,
        "dof":dof,"axis":DOF_LABELS[dof],
        "per_node_spring_stiffness_n_per_mm":K_PER_NODE,
        "spring_count":len(end_nodes),
        "derived_spring_energy_n_mm":energy,
        "derived_signed_force_n":force,
        "derived_force_is_independent_ccx_reaction":"NO_K_TIMES_U_ONLY",
        "displacement_signal_can_be_zero_by_symmetry":True,
        "sha256":{ext:hashlib.sha256(p.read_bytes()).hexdigest()
                  for ext,p in files.items()},
    }


def assess(values:dict[tuple[int,int],float])->dict:
    expected={(n,d) for n in MESHES for d in (0,1,2,3)}
    if (not isinstance(values,dict) or set(values)!=expected or
            any(type(x) not in (float,int) or not math.isfinite(x) or x<=0
                for x in values.values())):
        raise ValueError("RIB_DIRECTION_OBSERVATION_MATRIX_INVALID")
    changes={}
    mesh={}
    for n in MESHES:
        free=values[n,0]
        if values[n,3]>=free:
            raise ValueError("RIB_DIRECTION_KNOWN_Z_CONTROL_FAILED")
        changes[str(n)]={}
        for d in (1,2,3):
            ratio=values[n,d]/free
            # Small-displacement, NLGEOM follower pressure: a 0.5% *screen*
            # against spurious compliance increase, not a nonlinear theorem.
            if ratio>1.005:
                raise ValueError("RIB_DIRECTION_COMPLIANCE_INCREASE:"+str(d))
            changes[str(n)][DOF_LABELS[d]]={
                "ratio_to_free":ratio,"signed_relative_effect":1-ratio,
                "material_effect_significance":"NOT_ASSERTED"}
    for d in (0,1,2,3):
        delta=abs(values[16,d]-values[8,d])/values[16,d]
        if delta>.15:
            raise ValueError("RIB_DIRECTION_MESH_CHANGE_TOO_LARGE:"+str(d))
        mesh[str(d)]=delta
    return {
        "scope":SCOPE,
        "web_work_conjugate_displacement_mm_by_mesh":{
            str(n):{str(d):values[n,d] for d in (0,1,2,3)} for n in MESHES},
        "relative_directional_effects":changes,
        "two_mesh_relative_change":mesh,
        "per_node_spring_stiffness_n_per_mm":K_PER_NODE,
        "spring_axis_dofs":[1,2,3],
        "independent_exact_directional_shell_oracle":"NOT_ESTABLISHED",
        "small_load_linear_positive_semidefinite_stiffness_screen":True,
        "nonlinear_follower_pressure_monotonicity_theorem":"NOT_CLAIMED",
        "rotational_support_stiffness":"NOT_MODELED",
        "connector_or_fastener":"NOT_MODELED",
        "global_six_component_balance":"NOT_ADMITTED",
        "engineering_acceptance":"NOT_ADMITTED",
    }


def check(root:Path)->dict:
    cases={}
    values={}
    for n in MESHES:
        base=stage60_case(root/f"rib_end_rib_end_free_n{n}",n,"rib_end_free")
        cases[f"n{n}_dof0"]={
            "same_workflow_control":"STAGE60_REVALIDATED",
            "sha256":base["sha256"]}
        values[n,0]=base["web_work_conjugate_mean_u3_mm"]
        z=stage61_case(root/f"rib_spring_k{K_PER_NODE}_n{n}",n,K_PER_NODE)
        cases[f"n{n}_dof3"]={
            "same_workflow_control":"STAGE61_REVALIDATED",
            "artifact_sha256":z["artifact_sha256"]}
        values[n,3]=z["web_work_conjugate_mean_u3_mm"]
        for dof in DIRECTIONS:
            result=_case(root/f"rib_direction_dof{dof}_n{n}",n,dof)
            cases[f"n{n}_dof{dof}"]=result
            values[n,dof]=result["web_work_conjugate_mean_u3_mm"]
    outcome=assess(values)
    outcome["cases"]=cases
    return outcome


if __name__=="__main__":
    if len(sys.argv)==5 and sys.argv[1]=="--generate":
        generate(Path(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]))
        print("RIB_DIRECTION_SYNTHETIC_DECK_GENERATED_NO_SOLVER")
    elif len(sys.argv)==2:
        print(json.dumps(check(Path(sys.argv[1])),sort_keys=True,allow_nan=False))
        print("RIB_DIRECTION_TRANSLATION_SCREEN_PASS; NO_ENGINEERING_ADMISSION")
    else:
        raise SystemExit("USAGE: check_rib_end_direction.py ROOT | --generate DIR N DOF")
