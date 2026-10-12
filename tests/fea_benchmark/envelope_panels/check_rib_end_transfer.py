"""Stage 60: bounded extra rib-end support vs free rib-end, same plate.

Independent conceptual oracle: in linear elasticity, imposing additional
homogeneous kinematic constraints cannot increase work-conjugate compliance
under the same dead load. In the small-displacement S8R NLGEOM follower-load
fixture, this is a bounded screen, not a general nonlinear theorem.
No manufactured connection, fastener, reaction moment or capacity admission.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

from check_center_rib_plate import A, B, P, T, build as base_build
from check_u_fold_cantilever import _completed, _dat_vectors

MESHES=(8,16)
HEIGHT=8
SUPPORTS=("rib_end_free","rib_end_fixed")
MAX_PAIR_MESH_DIFFERENCE=.15


def _geometry(deck:str,n:int)->tuple[dict[int,tuple[float,float,float]],
                                     list[tuple[int,...]],set[int],set[int]]:
    try:
        region=deck.split("*NODE\n",1)[1].split("*ELEMENT,TYPE=S8R,ELSET=WEB\n",1)
        head=region[0].splitlines()
        raw_web=region[1].split("*ELEMENT,TYPE=S8R,ELSET=RIB\n",1)[0].splitlines()
        nodes={}
        for line in head:
            parts=line.split(",")
            if len(parts)!=4:
                raise ValueError("END_TRANSFER_NODE_RECORD_MALFORMED")
            nid=int(parts[0])
            xyz=tuple(float(x) for x in parts[1:])
            if nid in nodes or not all(math.isfinite(x) for x in xyz):
                raise ValueError("END_TRANSFER_NODE_DUPLICATE_OR_NONFINITE")
            nodes[nid]=xyz
        web=[]
        for line in raw_web:
            parts=[int(q) for q in line.split(",")]
            if len(parts)!=9:
                raise ValueError("END_TRANSFER_WEB_ELEMENT_MALFORMED")
            web.append(tuple(parts[1:]))
    except (IndexError,ValueError) as exc:
        raise ValueError("END_TRANSFER_SOURCE_DECK_UNPARSABLE") from exc
    web_nodes={v for el in web for v in el}
    endpoints={nid for nid,(x,y,z) in nodes.items()
               if (abs(x)<1e-9 or abs(x-A)<1e-9)
               and abs(y-B/2)<1e-9 and z>1e-9}
    if (len(web)!=n*n or len(web_nodes)!=3*n*n+4*n+1
            or len(endpoints)!=16 or
            any(len(set(el))!=8 or not set(el)<=web_nodes for el in web)
            or any(nid in web_nodes for nid in endpoints)):
        raise ValueError("END_TRANSFER_MESH_COVERAGE_INVALID")
    return nodes,web,web_nodes,endpoints


def build(n:int,support:str)->tuple[str,set[int],set[int],list[tuple[int,...]]]:
    if type(n) is not int or n not in MESHES or support not in SUPPORTS:
        raise ValueError("END_TRANSFER_VARIANT_NOT_ADMITTED")
    deck,center,root,counts=base_build(n,HEIGHT)
    if counts!={"web":n*n,"rib":n*4}:
        raise ValueError("END_TRANSFER_STAGE59_SOURCE_DRIFT")
    nodes,web,web_nodes,endpoints=_geometry(deck,n)
    prefix="*NSET,NSET=CENTER\n"
    extra="*NSET,NSET=WEB_NODES\n"+_lists(web_nodes)+ "\n"
    if deck.count(prefix)!=1:
        raise ValueError("END_TRANSFER_CENTER_ANCHOR_MISSING")
    deck=deck.replace(prefix,extra+prefix,1)
    if support=="rib_end_fixed":
        deck=deck.replace(prefix,"*NSET,NSET=RIB_END\n"+
                          _lists(endpoints)+"\n"+prefix,1)
        if deck.count("ROOT,1,6,0.\n")!=1:
            raise ValueError("END_TRANSFER_ROOT_BOUNDARY_DRIFT")
        deck=deck.replace("ROOT,1,6,0.\n","ROOT,1,6,0.\nRIB_END,1,6,0.\n",1)
        deck=deck.replace("*NODE PRINT,NSET=ROOT\nRF\n",
                          "*NODE PRINT,NSET=ROOT\nRF\n*NODE PRINT,NSET=RIB_END\nRF\n",1)
    anchor="*NODE PRINT,NSET=CENTER\nU\n"
    if deck.count(anchor)!=1:
        raise ValueError("END_TRANSFER_CENTER_PRINT_DRIFT")
    deck=deck.replace(anchor,anchor+"*NODE PRINT,NSET=WEB_NODES\nU\n",1)
    deck=deck.replace("synthetic-stage59-clamped-web-ribheight-8-mesh-",
                      "synthetic-stage60-"+support+"-ribheight-8-mesh-",1)
    if (deck.count("*DLOAD\nWEB,P,0.0001")!=1
            or deck.count("*NODE PRINT,NSET=WEB_NODES\nU\n")!=1
            or deck.count("RIB_END,1,6,0.")!=int(support=="rib_end_fixed")
            or "*CLOAD" in deck or "*PLASTIC" in deck):
        raise ValueError("END_TRANSFER_DECK_SCOPE_ESCALATION")
    return deck,web_nodes,endpoints,web


def _lists(values:set[int])->str:
    ordered=sorted(values)
    return "\n".join(",".join(map(str,ordered[i:i+12]))
                     for i in range(0,len(ordered),12))


def generate(folder:Path,n:int,support:str)->None:
    if folder.exists() or folder.is_symlink():
        raise ValueError("END_TRANSFER_WORKSPACE_MUST_BE_NEW")
    deck,*_=build(n,support)
    folder.mkdir(parents=True)
    (folder/"panel.inp").write_text(deck,encoding="utf-8")


def pressure_work_proxy(web:list[tuple[int,...]],
                        displacement:dict[int,tuple[float,float,float]],
                        n:int)->float:
    """S8R shape-function area integration on original flat loaded web.

    Shape-function mean: each corner -1/12, each midside +1/3.
    This is p times area-average U3 (divided by nominal total load).
    """
    if len(web)!=n*n or set(displacement)!={j for e in web for j in e}:
        raise ValueError("END_TRANSFER_WORK_FIELD_COVERAGE")
    contributions=[]
    for el in web:
        values=[displacement[v][2] for v in el]
        if any(len(displacement[v])!=3 or
               any(type(x) not in (int,float) or not math.isfinite(x)
                   for x in displacement[v])
               for v in el):
            raise ValueError("END_TRANSFER_WORK_NONFINITE")
        avg=-math.fsum(values[:4])/12+math.fsum(values[4:])/3
        contributions.append(avg)
    ubar=math.fsum(contributions)/len(contributions)
    if not math.isfinite(ubar) or not 0<ubar<.05*T:
        raise ValueError("END_TRANSFER_WORK_DIRECTION_OR_SCOPE")
    return ubar


def case(folder:Path,n:int,support:str)->dict:
    deck,web_nodes,endpoints,web=build(n,support)
    files={ext:folder/("panel."+ext) for ext in ("inp","dat","sta","frd")}
    for ext,f in files.items():
        limit=64_000_000 if ext=="frd" else 10_000_000
        if f.is_symlink() or not f.is_file() or not 0<f.stat().st_size<=limit:
            raise ValueError("END_TRANSFER_ARTIFACT_MISSING:"+ext)
    if files["inp"].read_bytes()!=deck.encode("utf-8"):
        raise ValueError("END_TRANSFER_DECK_HASH_IDENTITY_MISMATCH")
    _completed(files["sta"])
    u=_dat_vectors(files["dat"],"WEB_NODES","U")
    if set(u)!=web_nodes:
        raise ValueError("END_TRANSFER_DAT_NODE_COVERAGE")
    avg=pressure_work_proxy(web,u,n)
    root=_dat_vectors(files["dat"],"ROOT","RF")
    if len(root)!=8*n:
        raise ValueError("END_TRANSFER_ROOT_COVERAGE")
    end_rf=None
    if support=="rib_end_fixed":
        end=_dat_vectors(files["dat"],"RIB_END","RF")
        if set(end)!=endpoints:
            raise ValueError("END_TRANSFER_END_REACTION_COVERAGE")
        end_rf={"signed_sum_z_n":math.fsum(x[2] for x in end.values()),
                "sum_absolute_z_n":math.fsum(abs(x[2]) for x in end.values())}
        if not end_rf["sum_absolute_z_n"]>1e-7:
            raise ValueError("END_TRANSFER_END_REACTION_SIGNAL_NOT_OBSERVED")
    return {"web_work_conjugate_mean_u3_mm":avg,
            "end_rf_raw":end_rf,
            "root_rf_raw_z_n":math.fsum(x[2] for x in root.values()),
            "all_raw_rf_are_independent_support_reactions":"NOT_ESTABLISHED",
            "pressure_following_global_balance":"NOT_ADMITTED",
            "sha256":{k:hashlib.sha256(f.read_bytes()).hexdigest()
                      for k,f in files.items()}}


def assess(observed:dict[tuple[int,str],float])->dict:
    expected={(n,s) for n in MESHES for s in SUPPORTS}
    if (not isinstance(observed,dict) or set(observed)!=expected or
        any(type(v) not in (int,float) or not math.isfinite(v) or v<=0
            for v in observed.values())):
        raise ValueError("END_TRANSFER_MATRIX_INVALID")
    ratios={}
    mesh_error={}
    for n in MESHES:
        loose=observed[n,"rib_end_free"]
        rigid=observed[n,"rib_end_fixed"]
        if not rigid<loose:
            raise ValueError("END_TRANSFER_ADDITIONAL_CONSTRAINT_DID_NOT_REDUCE_WORK")
        ratios[n]=rigid/loose
    for s in SUPPORTS:
        a,b=(observed[n,s] for n in MESHES)
        change=abs(b-a)/b
        if change>MAX_PAIR_MESH_DIFFERENCE:
            raise ValueError("END_TRANSFER_MESH_CHANGE_EXCESSIVE:"+s)
        mesh_error[s]=change
    return {"scope":"SYNTHETIC_CENTER_RIB_END_SUPPORT_KINEMATIC_AB",
            "work_conjugate_mean_u3_by_mesh":{str(n):{s:observed[n,s]
                                                    for s in SUPPORTS}
                                            for n in MESHES},
            "fixed_to_free_compliance_proxy_ratios":ratios,
            "two_mesh_relative_difference":mesh_error,
            "physical_oracle":"LINEAR_ELASTIC_RESTRICTED_KINEMATIC_SPACE_NONINCREASING_LOAD_WORK",
            "nlgeom_follower_pressure_oracle_is_exact":"NO_SMALL_LOAD_SCREENING_ONLY",
            "center_node_deflection_theorem":"NOT_CLAIMED",
            "rib_end_support_type":"IDEAL_EXTRA_FIXED_RIB_END_NOT_REAL_FASTENER",
            "complete_six_component_balance":"NOT_ADMITTED",
            "engineering_acceptance":"NOT_ADMITTED"}


def check(root:Path)->dict:
    cases={(n,s):case(root/f"rib_end_{s}_n{n}",n,s)
           for n in MESHES for s in SUPPORTS}
    result=assess({k:v["web_work_conjugate_mean_u3_mm"]
                   for k,v in cases.items()})
    result["cases"]={f"n{n}_{s}":v for (n,s),v in cases.items()}
    return result


if __name__=="__main__":
    if len(sys.argv)==5 and sys.argv[1]=="--generate":
        generate(Path(sys.argv[2]),int(sys.argv[3]),sys.argv[4])
        print("END_TRANSFER_SYNTHETIC_DECK_GENERATED_NO_SOLVER")
    elif len(sys.argv)==2:
        print(json.dumps(check(Path(sys.argv[1])),sort_keys=True,allow_nan=False))
        print("END_TRANSFER_KINEMATIC_CONSTRAINT_SCREEN_PASS; ENGINEERING_NOT_ADMITTED")
    else:
        raise SystemExit("USAGE: check_rib_end_transfer.py ROOT | --generate DIR N SUPPORT")
