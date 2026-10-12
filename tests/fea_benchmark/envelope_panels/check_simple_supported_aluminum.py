"""Fixture-only ideal simply-supported aluminum S8R/Navier plate study.

Does not enable user-supplied supports, actual attachments or design capacity.
"""
from __future__ import annotations
import hashlib
import json
import math
import sys
from pathlib import Path

MESHES=(4,8,16)
E,NU,T,A,B,Q=69000.,.33,2.,100.,100.,.0001


def navier_center(a=A,b=B,t=T,e=E,nu=NU,q=Q,order=61):
    if (type(order) is not int or order not in (41,61) or
        any(type(x) not in (float,int) or not math.isfinite(x)
            for x in (a,b,t,e,nu,q)) or min(a,b,t,e,q)<=0 or
        not 0<nu<.49 or min(a,b)/t<15):
        raise ValueError("NAVIER_PARAMETERS_OUTSIDE_SCOPE")
    d=e*t**3/(12*(1-nu**2))
    terms=((-1)**((m-1)//2+(n-1)//2)/
           (m*n*((m/a)**2+(n/b)**2)**2)
           for m in range(1,order+1,2) for n in range(1,order+1,2))
    w=16*q*math.fsum(terms)/(math.pi**6*d)
    if not math.isfinite(w) or w<=0:
        raise ValueError("NAVIER_NONPHYSICAL")
    return w


def assess(clamped,simple):
    if (not isinstance(clamped,dict) or not isinstance(simple,dict)
        or set(clamped)!=set(MESHES) or set(simple)!=set(MESHES)
        or any(type(x) not in (float,int) or not math.isfinite(x) or x<=0
               for x in (*clamped.values(),*simple.values()))):
        raise ValueError("SUPPORT_FIELD_INVALID")
    analytic=navier_center()
    if abs(analytic-navier_center(order=41))/analytic>1e-6:
        raise ValueError("NAVIER_SERIES_UNSTABLE")
    if any(simple[n]<=clamped[n] for n in MESHES):
        raise ValueError("SUPPORT_RESPONSE_NOT_DISTINCT")
    if not (simple[4]<simple[8]<simple[16]):
        raise ValueError("SIMPLE_MESH_NONMONOTONIC")
    coarse=abs(simple[8]-simple[4]);fine=abs(simple[16]-simple[8])
    if not 0<fine<coarse:
        raise ValueError("SIMPLE_MESH_CHANGE_NOT_CONTRACTING")
    error=abs(simple[16]-analytic)/analytic
    if error>0.12:
        raise ValueError("NAVIER_FINE_MESH_DISAGREEMENT")
    if max(simple.values())>=.05*T:
        raise ValueError("NOT_SMALL_DEFLECTION")
    return dict(reference_type="CLASSICAL_NAVIER_DOUBLE_SINE_KIRCHHOFF_APPROXIMATION",
                center_reference_mm=analytic,clamped_center_by_mesh_mm=clamped,
                simple_center_by_mesh_mm=simple,fine_mesh_relative_error=error,
                research_screening_tolerance=.12,mesh_changes_contract=True,
                physical_support_boundary="IDEAL_TRANSVERSE_PINNED_EDGES_MINIMAL_INPLANE_PINS",
                attachment_contact="NOT_MODELED",rotational_reaction="NOT_OBSERVED",
                engineering_acceptance="NOT_ADMITTED",
                aluminum_design_manual_capacity="NOT_COMPUTED",
                general_global_balance="NOT_ADMITTED")


def make_fixture(folder:Path,n:int)->None:
    from generate import build
    from check_pressure_equilibrium import parse_deck
    if type(n) is not int or n not in MESHES:
        raise ValueError("SIMPLE_FIXTURE_MESH_REJECTED")
    if folder.is_symlink() or folder.exists():
        raise ValueError("SIMPLE_FIXTURE_DESTINATION_MUST_BE_NEW")
    build("aluminum",n,"small",folder)
    inp=folder/"panel.inp"
    nodes,elements,edge,q=parse_deck(inp)
    if len(elements)!=n*n or abs(q-Q)>1e-12:
        raise ValueError("SIMPLE_FIXTURE_GENERATION_DRIFT")
    def corner(x,y):
        matches=[nid for nid,pt in nodes.items() if pt==(x,y,0.)]
        if len(matches)!=1 or matches[0] not in edge:
            raise ValueError("SIMPLE_FIXTURE_PIN_NODE_MISSING")
        return matches[0]
    left=corner(0.,0.);right=corner(A,0.)
    txt=inp.read_text(encoding="utf-8")
    old_heading=f"synthetic aluminum clamped plate, n={n}, small"
    if txt.count(old_heading)!=1 or txt.count("EDGE,1,6,0.")!=1:
        raise ValueError("SIMPLE_FIXTURE_SOURCE_DRIFT")
    boundary=f"EDGE,3,3,0.\\n{left},1,2,0.\\n{right},2,2,0."
    # This is a fixture transformation, never an arbitrary user input deck.
    txt=txt.replace(old_heading,f"synthetic aluminum simple plate, n={n}, small")
    txt=txt.replace("EDGE,1,6,0.",boundary)
    inp.write_text(txt,encoding="utf-8")


def _read_case(root:Path,n:int,support:str):
    from check_pressure_equilibrium import parse_deck,reconcile
    from check_aluminum_ritz import center_z,deck_material
    from run_synthetic_panel import _completed_step
    folder=root/f"aluminum_{'small' if support=='clamped' else 'simple_small'}_{n}"
    inp,dat,sta=(folder/f"panel.{s}" for s in ("inp","dat","sta"))
    for p in (inp,dat,sta):
        if p.is_symlink() or not p.is_file() or not 0<p.stat().st_size<=10000000:
            raise ValueError("SUPPORT_ARTIFACT_MISSING")
    raw=inp.read_text(encoding="utf-8")
    label=f"synthetic aluminum {'clamped' if support=='clamped' else 'simple'} plate, n={n}, small"
    if label not in raw or "*STEP,NLGEOM" not in raw:
        raise ValueError("SUPPORT_DECK_IDENTITY_MISMATCH")
    if support=="clamped":
        if "EDGE,1,6,0." not in raw or "EDGE,3,3,0." in raw:
            raise ValueError("SUPPORT_CLAMPED_BOUNDARY_MISMATCH")
    elif ("EDGE,3,3,0." not in raw or "EDGE,1,6,0." in raw
          or ",1,2,0." not in raw or ",2,2,0." not in raw):
        raise ValueError("SUPPORT_SIMPLE_BOUNDARY_MISMATCH")
    nodes,elements,edge,q=parse_deck(inp)
    if (len(elements)!=n*n or len(edge)!=8*n or abs(q-Q)>1e-12 or
        deck_material(inp)!=(E,NU,T) or
        min(x for x,y,z in nodes.values())!=0 or
        min(y for x,y,z in nodes.values())!=0 or
        abs(max(x for x,y,z in nodes.values())-A)>1e-6 or
        abs(max(y for x,y,z in nodes.values())-B)>1e-6):
        raise ValueError("SUPPORT_MODEL_GEOMETRY_OR_MATERIAL_MISMATCH")
    _completed_step(sta)
    reconcile(inp,dat,tolerance=1e-4)
    return {"w":center_z(dat),
            "input_sha256":hashlib.sha256(inp.read_bytes()).hexdigest(),
            "dat_sha256":hashlib.sha256(dat.read_bytes()).hexdigest()},nodes,elements,q


def check(root:Path):
    c,s,hashes={},{},{}
    for n in MESHES:
        cv,cn,ce,cq=_read_case(root,n,"clamped")
        sv,sn,se,sq=_read_case(root,n,"simple")
        if cn!=sn or ce!=se or cq!=sq or cv["input_sha256"]==sv["input_sha256"]:
            raise ValueError("SUPPORT_PAIR_TOPOLOGY_OR_BOUNDARY_NOT_DISTINCT")
        c[n]=cv["w"];s[n]=sv["w"]
        hashes[n]={"clamped":{k:v for k,v in cv.items() if k.endswith("sha256")},
                   "simple":{k:v for k,v in sv.items() if k.endswith("sha256")}}
    result=assess(c,s)
    result["artifact_provenance_by_mesh"]=hashes
    return result


if __name__=="__main__":
    if len(sys.argv)==4 and sys.argv[1]=="--generate":
        make_fixture(Path(sys.argv[2]),int(sys.argv[3]))
        print("IDEAL_SIMPLE_SUPPORT_FIXTURE_GENERATED_NO_SOLVER_EXECUTION")
    elif len(sys.argv)==2:
        print(json.dumps(check(Path(sys.argv[1])),sort_keys=True,allow_nan=False))
        print("IDEAL_SUPPORT_NAVIER_RESEARCH_PASS; ENGINEERING_NOT_ADMITTED")
    else:
        raise SystemExit("USAGE: check_simple_supported_aluminum.py ROOT | --generate DIR N")
