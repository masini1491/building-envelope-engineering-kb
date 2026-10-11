"""Bounded independent Kirchhoff/Rayleigh-Ritz *approximation* for aluminum CCX research."""
from __future__ import annotations
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from aluminum_research_input import load
from check_pressure_equilibrium import parse_deck

MESHES=(4,8,16)
# Exact polynomial integrals, phi(s)=(1-s*s)**2 over [-1,1].
I0=256/315
I1=256/105
I2=128/5
IX=-256/105
IL=16/15
CASES={
    "thicker_square":dict(width_mm=100.0,height_mm=100.0,thickness_mm=3.0,youngs_modulus_mpa=69000.0,poisson_ratio=0.33,pressure_n_mm2=0.0001),
    "rectangular_higher_pressure":dict(width_mm=120.0,height_mm=80.0,thickness_mm=2.5,youngs_modulus_mpa=70000.0,poisson_ratio=0.32,pressure_n_mm2=0.0002)
}

def expected_input(case,mesh):
    if case not in CASES or mesh not in MESHES:
        raise ValueError("UNSUPPORTED_RITZ_FIXTURE")
    return dict(**CASES[case],mesh=mesh,support="four_edges_clamped",
                units="N-mm-MPa",material_provenance="explicit synthetic Ritz research fixture")

def ritz_center_mm(c):
    """One polynomial Ritz term for fully clamped small-deflection Kirchhoff plate."""
    a,b=c["width_mm"],c["height_mm"]
    e,nu,t,q=c["youngs_modulus_mpa"],c["poisson_ratio"],c["thickness_mm"],c["pressure_n_mm2"]
    D=e*t**3/(12*(1-nu**2))
    jac=a*b/4
    # U=D W^2 K/2, Q=q W L, w=W phi(2x/a)phi(2y/b).
    K=jac*(16*I2*I0*(a**-4+b**-4)+32*(nu*IX**2+(1-nu)*I1**2)/(a*a*b*b))
    L=jac*IL**2
    w=q*L/(D*K)
    if not math.isfinite(w) or w<=0:raise ValueError("INVALID_RITZ_REFERENCE")
    return w

def assess(c,values):
    if set(values)!=set(MESHES):raise ValueError("INCOMPLETE_MESH_TRIPLET")
    w=[values[n] for n in MESHES]
    if any(not math.isfinite(x) or x<=0 for x in w):
        raise ValueError("NONPOSITIVE_OR_NONFINITE_DEFLECTION")
    if max(w)>=0.05*c["thickness_mm"]:raise ValueError("NOT_SMALL_DEFLECTION")
    ref=ritz_center_mm(c)
    error=abs(w[-1]-ref)/ref
    if error>0.20:raise ValueError("ONE_TERM_RITZ_DISAGREEMENT")
    coarse=abs(w[1]-w[0]);fine=abs(w[2]-w[1])
    if not (coarse>0 and fine<coarse):raise ValueError("MESH_REFINEMENT_NOT_CONTRACTING")
    return dict(reference_type="ONE_TERM_KIRCHHOFF_RITZ_APPROXIMATION",
                reference_mm=ref,center_by_mesh_mm=values,
                relative_reference_difference=error,
                coarse_change_mm=coarse,fine_change_mm=fine,
                mesh_contraction_observed=True,engineering_acceptance="NOT_ADMITTED",
                general_global_balance="NOT_ADMITTED")

def center_z(path):
    data=path.read_text(encoding="utf-8",errors="replace")
    pat=(r"displacements \(vx,vy,vz\) for set CENTER and time\s+"
         r"([\d.Ee+-]+)\s+(\d+)\s+([\d.Ee+-]+)\s+([\d.Ee+-]+)\s+([\d.Ee+-]+)")
    hits=list(re.finditer(pat,data,re.I))
    if not hits or abs(float(hits[-1].group(1))-1)>1e-7:
        raise ValueError("MISSING_FINAL_CENTER")
    value=abs(float(hits[-1].group(5)))
    if not math.isfinite(value):raise ValueError("NONFINITE_CENTER")
    return value

def deck_material(inp):
    lines=[x.strip() for x in inp.read_text(encoding="utf-8").splitlines()]
    if lines.count("*ELASTIC")!=1 or sum(x.startswith("*SHELL SECTION") for x in lines)!=1:
        raise ValueError("UNEXPECTED_MATERIAL_OR_SECTION")
    i=lines.index("*ELASTIC")
    j=next(i for i,x in enumerate(lines) if x.startswith("*SHELL SECTION"))
    e,nu=(float(x) for x in lines[i+1].split(","))
    t=float(lines[j+1])
    if not all(math.isfinite(x) for x in (e,nu,t)):
        raise ValueError("NONFINITE_DECK_MATERIAL")
    return e,nu,t

def check_fixture(root,case):
    center={}
    for n in MESHES:
        config=load(root/f"input_{n}.json")
        if config!=expected_input(case,n):raise ValueError("FIXTURE_INPUT_DRIFT")
        report=json.loads((root/f"output_{n}.json").read_text(encoding="utf-8"))
        if (report.get("execution_status")!="ALUMINUM_PARAMETRIC_RESEARCH_EVIDENCE_PASS"
            or report.get("engineering_acceptance")!="NOT_ADMITTED"
            or report.get("inputs")!=config):
            raise ValueError("SOLVER_EVIDENCE_INVALID")
        inp=root/f"mesh_{n}"/"panel.inp"
        dat=root/f"mesh_{n}"/"panel.dat"
        if report.get("artifact_provenance",{}).get("input_sha256")!=hashlib.sha256(inp.read_bytes()).hexdigest():
            raise ValueError("DECK_PROVENANCE_MISMATCH")
        nodes,elements,edge,q=parse_deck(inp)
        if (len(elements)!=n*n or not edge
            or abs(max(x for x,y,z in nodes.values())-config["width_mm"])>1e-6
            or abs(max(y for x,y,z in nodes.values())-config["height_mm"])>1e-6
            or abs(q-config["pressure_n_mm2"])>1e-12):
            raise ValueError("DECK_GEOMETRY_PRESSURE_MISMATCH")
        e,nu,t=deck_material(inp)
        if (abs(e-config["youngs_modulus_mpa"])>1e-8
            or abs(nu-config["poisson_ratio"])>1e-12
            or abs(t-config["thickness_mm"])>1e-10):
            raise ValueError("DECK_MATERIAL_MISMATCH")
        center[n]=center_z(dat)
    return assess(expected_input(case,16),center)

if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("USAGE: check_aluminum_ritz.py DIR CASE")
    print(json.dumps(check_fixture(Path(sys.argv[1]),sys.argv[2]),allow_nan=False,sort_keys=True))
    print("ALUMINUM_SMALL_LOAD_RITZ_MESH_EVIDENCE_PASS; NO ADM CAPACITY ADMISSION")
