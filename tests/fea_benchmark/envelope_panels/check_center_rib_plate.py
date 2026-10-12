"""Stage 59 synthetic four-clamped-edge plate and centered bonded S8R rib.

Small-deflection, unit-consistent research ONLY. A center-rib energy / flat
Kirchhoff--Ritz approximation is qualitative; it is not an exact shell field
or an aluminum member design capacity.
"""
from __future__ import annotations
import hashlib
import json
import math
import re
import sys
from pathlib import Path

A = B = 100.0
T, E, NU, P = 2.0, 69000.0, 0.33, 0.0001
NODES_MESH = (8, 16)
RIB_HEIGHTS = (0, 4, 8)
RIB_VERTICAL_ELEMENTS = 4


def independent_ritz(height: int) -> dict:
    """One clamped Kirchhoff-plate Ritz term + simple midline beam energy.

    The rib-only inertia about the plate midsurface is a deliberately
    simplified kinematic assumption, not a precise composite section model.
    """
    if type(height) is not int or height not in RIB_HEIGHTS:
        raise ValueError("RIB_HEIGHT_OUTSIDE_SYNTHETIC_SCOPE")
    i0,i1,i2,ix,il = 256/315,256/105,128/5,-256/105,16/15
    d = E*T**3/(12*(1-NU**2))
    jac = A*B/4
    kp = jac*(16*i2*i0*(A**-4+B**-4)+
              32*(NU*ix**2+(1-NU)*i1**2)/(A*A*B*B))
    qgen = P*jac*il**2
    ib = T*height**3/3
    kb = E*ib*1024/(5*A**3)
    plate = qgen/(d*kp)
    combined = qgen/(d*kp+kb)
    if not all(math.isfinite(v) and v>=0 for v in (ib,kb,plate,combined)):
        raise ValueError("RIB_ANALYTICAL_NONFINITE")
    return {
        "flat_ritz_center_mm":plate,
        "plate_plus_rib_energy_center_mm":combined,
        "rib_only_synthetic_iy_mm4":ib,
        "reference":"ONE_TERM_CLAMPED_KIRCHHOFF_PLATE_PLUS_CENTER_BEAM_ENERGY_APPROXIMATION",
        "exact_folded_or_stiffened_shell_field":"NOT_ESTABLISHED",
        "engineering_acceptance":"NOT_ADMITTED",
    }


def _node_xy(i:int,j:int,n:int)->tuple[float,float,float]:
    return A*i/(2*n), B*j/(2*n), 0.


def build(n:int,height:int)->tuple[str,int,set[int],dict[str,int]]:
    if type(n) is not int or n not in NODES_MESH:
        raise ValueError("RIB_MESH_NOT_ADMITTED")
    if type(height) is not int or height not in RIB_HEIGHTS:
        raise ValueError("RIB_HEIGHT_NOT_ADMITTED")
    coords:dict[int,tuple[float,float,float]]={}
    plate:dict[tuple[int,int],int]={}
    def plate_node(i:int,j:int)->int:
        key=(i,j)
        if key not in plate:
            nid=len(coords)+1
            plate[key]=nid
            coords[nid]=_node_xy(i,j,n)
        return plate[key]
    web=[]
    for j in range(n):
        for i in range(n):
            u,v=2*i,2*j
            web.append(tuple(plate_node(*ij) for ij in
                ((u,v),(u+2,v),(u+2,v+2),(u,v+2),
                 (u+1,v),(u+2,v+1),(u+1,v+2),(u,v+1))))
    outer={nid for (i,j),nid in plate.items()
           if i in (0,2*n) or j in (0,2*n)}
    center=plate_node(n,n)
    expected_root=8*n
    if len(web)!=n*n or len(outer)!=expected_root:
        raise ValueError("RIB_WEB_MESH_INCOMPLETE")
    rib=[]
    rib_nodes={}
    def rib_node(i:int,k:int)->int:
        if k==0:
            return plate_node(i,n)
        key=(i,k)
        if key not in rib_nodes:
            nid=len(coords)+1
            rib_nodes[key]=nid
            coords[nid]=(A*i/(2*n),B/2,height*k/(2*RIB_VERTICAL_ELEMENTS))
        return rib_nodes[key]
    if height:
        for i in range(n):
            for k in range(RIB_VERTICAL_ELEMENTS):
                u,v=2*i,2*k
                rib.append(tuple(rib_node(*ij) for ij in
                     ((u,v),(u+2,v),(u+2,v+2),(u,v+2),
                      (u+1,v),(u+2,v+1),(u+1,v+2),(u,v+1))))
        if len(rib)!=n*RIB_VERTICAL_ELEMENTS or len(outer)!=expected_root:
            raise ValueError("RIB_SHELL_TOPOLOGY_NOT_CLOSED")
        # RIB z=0 nodes share exact integer node IDs with plate midline.
        if any(rib_node(i,0)!=plate_node(i,n) for i in range(2*n+1)):
            raise ValueError("RIB_ATTACHMENT_IDENTITY_INVALID")
    lines=["*HEADING",f"synthetic-stage59-clamped-web-ribheight-{height}-mesh-{n}","*NODE"]
    lines += [f"{i},{x:.8f},{y:.8f},{z:.8f}" for i,(x,y,z) in sorted(coords.items())]
    lines += ["*ELEMENT,TYPE=S8R,ELSET=WEB"]
    lines += [f"{j},"+",".join(map(str,e)) for j,e in enumerate(web,1)]
    if rib:
        lines += ["*ELEMENT,TYPE=S8R,ELSET=RIB"]
        lines += [f"{j+n*n},"+",".join(map(str,e)) for j,e in enumerate(rib,1)]
    lines += ["*MATERIAL,NAME=SYNTHETIC_ELASTIC","*ELASTIC",f"{E},{NU}",
              "*SHELL SECTION,ELSET=WEB,MATERIAL=SYNTHETIC_ELASTIC",str(T)]
    if rib:
        lines += ["*SHELL SECTION,ELSET=RIB,MATERIAL=SYNTHETIC_ELASTIC",str(T)]
    lines += ["*NSET,NSET=ROOT"]
    ordered=sorted(outer)
    lines += [",".join(map(str,ordered[i:i+12])) for i in range(0,len(ordered),12)]
    lines += ["*NSET,NSET=CENTER",str(center),"*BOUNDARY","ROOT,1,6,0.",
              "*STEP,NLGEOM","*STATIC","0.05,1.,0.00001,0.1",
              "*DLOAD",f"WEB,P,{P}","*NODE FILE,OUTPUT=3D","U,RF",
              "*NODE PRINT,NSET=CENTER","U","*NODE PRINT,NSET=ROOT","RF","*END STEP"]
    return "\n".join(lines)+"\n",center,outer,{"web":len(web),"rib":len(rib)}


def generate(folder:Path,n:int,height:int)->None:
    if folder.exists() or folder.is_symlink():
        raise ValueError("RIB_WORKSPACE_MUST_BE_NEW")
    deck,*_=build(n,height)
    folder.mkdir(parents=True)
    (folder/"panel.inp").write_text(deck,encoding="utf-8")


def _observed(folder:Path,n:int,height:int)->dict:
    from check_aluminum_ritz import center_z
    from check_u_fold_cantilever import _completed
    deck,center,outer,count=build(n,height)
    files={suffix:folder/f"panel.{suffix}" for suffix in ("inp","dat","sta","frd")}
    for suffix,p in files.items():
        size=64_000_000 if suffix=="frd" else 10_000_000
        if p.is_symlink() or not p.is_file() or not 0<p.stat().st_size<=size:
            raise ValueError("RIB_SOLVER_ARTIFACT_MISSING:"+suffix)
    if files["inp"].read_bytes()!=deck.encode("utf-8"):
        raise ValueError("RIB_DECK_PROVENANCE_MISMATCH")
    _completed(files["sta"])
    disp=center_z(files["dat"])
    if not math.isfinite(disp) or not 0<disp<.05*T:
        raise ValueError("RIB_CENTER_FIELD_INVALID")
    return {"center_deflection_mm":disp,
            "mesh":n,"rib_height_mm":height,
            "element_counts":count,
            "artifact_sha256":{suffix:hashlib.sha256(p.read_bytes()).hexdigest()
                               for suffix,p in files.items()}}


def assess(observed:dict[tuple[int,int],float])->dict:
    if (not isinstance(observed,dict) or
        set(observed)!={(n,h) for n in NODES_MESH for h in RIB_HEIGHTS} or
        any(type(v) not in (float,int) or not math.isfinite(v) or v<=0
            for v in observed.values())):
        raise ValueError("RIB_STUDY_OBSERVATION_MATRIX_INVALID")
    for n in NODES_MESH:
        if not observed[n,0]>observed[n,4]>observed[n,8]:
            raise ValueError("RIB_STIFFNESS_ORDER_NOT_OBSERVED:"+repr(observed))
    flat_ref=independent_ritz(0)["flat_ritz_center_mm"]
    err=abs(observed[16,0]-flat_ref)/flat_ref
    if err>.20:
        raise ValueError("FLAT_PLATE_RITZ_REFERENCE_DISAGREEMENT")
    differences={}
    for h in RIB_HEIGHTS:
        d=abs(observed[16,h]-observed[8,h])/observed[16,h]
        if d>.15:
            raise ValueError("RIB_TWO_MESH_DIFFERENCE_TOO_LARGE:"+str(h))
        differences[h]=d
    return {"scope":"SYNTHETIC_FOUR_EDGE_CLAMPED_WEB_WITH_CENTER_RIB",
            "observed_center_mm":{str(n):{str(h):observed[n,h] for h in RIB_HEIGHTS}
                                  for n in NODES_MESH},
            "independent_plate_and_beam_energy":{str(h):independent_ritz(h)
                                                for h in RIB_HEIGHTS},
            "flat_ritz_relative_difference":err,
            "two_mesh_relative_difference":differences,
            "rib_stiffness_order_observed":True,
            "independent_stiffener_field_oracle":"NOT_ESTABLISHED",
            "rib_attachment_model":"SHARED_SHELL_MIDSURFACE_NODES_NOT_FASTENER",
            "global_six_component_balance":"NOT_ADMITTED",
            "material_capacity":"NOT_ADMITTED",
            "engineering_acceptance":"NOT_ADMITTED"}


def check(root:Path)->dict:
    cases={(n,h):_observed(root/f"center_rib_h{h}_n{n}",n,h)
           for n in NODES_MESH for h in RIB_HEIGHTS}
    summary=assess({key:value["center_deflection_mm"] for key,value in cases.items()})
    summary["cases"]={f"n{n}_h{h}":case for (n,h),case in cases.items()}
    return summary


if __name__=="__main__":
    if len(sys.argv)==5 and sys.argv[1]=="--generate":
        generate(Path(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]))
        print("CENTER_RIB_STUDY_DECK_GENERATED_NO_SOLVER")
    elif len(sys.argv)==2:
        print(json.dumps(check(Path(sys.argv[1])),sort_keys=True,allow_nan=False))
        print("CENTER_RIB_LOAD_TRANSFER_SCREEN_PASS; NO_DESIGN_ADMISSION")
    else:
        raise SystemExit("USAGE: check_center_rib_plate.py ROOT | --generate DIR N HEIGHT")
