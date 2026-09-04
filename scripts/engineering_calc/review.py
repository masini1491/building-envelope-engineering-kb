"""AI-facing JSON adapter for deterministic engineering calculation review.

Execution bridge only: engineering methodology, units, supports, material properties,
allowables and project criteria remain external traceable inputs.
"""
from dataclasses import asdict, is_dataclass
from math import isfinite
from typing import Any, Mapping
import argparse, json, sys
from pathlib import Path
from .beam import BeamElement, solve_beam
from .beam_extrema import beam_extrema
from .compare import compare_values
from .fastener_group import elastic_in_plane_group
from .section_required import required_inertia, required_section_modulus, utilization
from .connection import demand_capacity, projected_bearing_stress, shear_tension_demand, thread_engagement_ratio
from .audit import audit_product, audit_force_balance

class IncompleteInputError(ValueError): pass
class UnsupportedModelError(ValueError): pass

def _map(v,name):
    if not isinstance(v,Mapping): raise IncompleteInputError(f"{name} must be an object")
    return v

def _num(m,key):
    if key not in m: raise IncompleteInputError(f"inputs.{key} is required")
    try: v=float(m[key])
    except (TypeError,ValueError) as e: raise IncompleteInputError(f"inputs.{key} must be numeric") from e
    if not isfinite(v): raise IncompleteInputError(f"inputs.{key} must be finite")
    return v

def _units(p):
    u=_map(p.get("units"),"units")
    if not u or any(not isinstance(k,str) or not k.strip() or not isinstance(v,str) or not v.strip() for k,v in u.items()):
        raise IncompleteInputError("units must contain explicit non-empty unit strings")

def _tol(p):
    t=_map(p.get("tolerance") or {},"tolerance")
    try: a=float(t.get("abs",1e-9)); r=float(t.get("rel",1e-6))
    except (TypeError,ValueError) as e: raise IncompleteInputError("tolerance must be numeric") from e
    if a<0 or r<0 or not isfinite(a) or not isfinite(r): raise IncompleteInputError("tolerance must be finite and non-negative")
    return a,r

def _reported(p):
    raw=p.get("reported_results") or {}; raw=_map(raw,"reported_results"); out={}
    for k,v in raw.items():
        if not isinstance(k,str) or not k: raise IncompleteInputError("reported_results keys must be strings")
        try: out[k]=float(v)
        except (TypeError,ValueError) as e: raise IncompleteInputError(f"reported_results.{k} must be numeric") from e
        if not isfinite(out[k]): raise IncompleteInputError(f"reported_results.{k} must be finite")
    return out

def _final(p,check,computed,flat):
    reported=_reported(p); a,r=_tol(p); comparisons={}; flags=[]; statuses=[]
    for key,value in reported.items():
        if key not in flat: flags.append(f"UNSUPPORTED_REPORTED_KEY:{key}"); continue
        c=compare_values(value,flat[key],abs_tol=a,rel_tol=r); comparisons[key]=asdict(c); statuses.append(c.status)
    if flags: status="INCOMPLETE"
    elif not reported: status="NOT_PROVIDED"
    elif any(x=="MISMATCH" for x in statuses): status="MISMATCH"
    else: status="MATCH"
    return {"calculation_status":"COMPUTED","comparison_status":status,"check_type":check,"computed":computed,"comparisons":comparisons,"review_flags":flags}

def _beam(p,inp):
    pos=inp.get("node_positions"); raw=inp.get("elements"); vr=inp.get("vertical_restraints")
    if not isinstance(pos,list) or len(pos)<2: raise IncompleteInputError("inputs.node_positions requires at least two values")
    if not isinstance(raw,list) or not raw: raise IncompleteInputError("inputs.elements requires at least one element")
    if not isinstance(vr,list): raise IncompleteInputError("inputs.vertical_restraints must be an array")
    try:
        pos=[float(x) for x in pos]
        els=[BeamElement(int(e["start"]),int(e["end"]),float(e["elastic_modulus"]),float(e["inertia"]),float(e.get("udl",0))) for e in raw]
        nf={int(k):float(v) for k,v in (inp.get("nodal_forces") or {}).items()}; nm={int(k):float(v) for k,v in (inp.get("nodal_moments") or {}).items()}
        result=solve_beam(node_positions=pos,elements=els,vertical_restraints=[int(x) for x in vr],rotational_restraints=[int(x) for x in inp.get("rotational_restraints",[])],nodal_forces=nf,nodal_moments=nm)
        ex,glob=beam_extrema(node_positions=pos,elements=els,result=result)
    except (KeyError,TypeError,ValueError) as e:
        if "singular" in str(e) or "no free degrees" in str(e): raise UnsupportedModelError(str(e)) from e
        raise IncompleteInputError(str(e)) from e
    computed={"displacements":list(result.displacements),"rotations":list(result.rotations),"reactions":list(result.reactions),"reaction_moments":list(result.reaction_moments),"element_end_forces":[asdict(x) for x in result.element_end_forces],"element_extrema":[asdict(x) for x in ex],"global_extrema":asdict(glob)}
    flat={f"reactions.{i}":v for i,v in enumerate(result.reactions) if v is not None}
    flat.update({"global.max_abs_shear":glob.max_abs_shear,"global.max_abs_moment":glob.max_abs_moment,"global.max_abs_deflection":glob.max_abs_deflection})
    return _final(p,"beam",computed,flat)

def _simple(p,inp,check):
    if check=="required_inertia": computed={"required_inertia":required_inertia(_num(inp,"i_trial"),_num(inp,"delta_trial"),_num(inp,"delta_allow"))}
    elif check=="required_section_modulus": computed={"required_section_modulus":required_section_modulus(_num(inp,"moment_max"),_num(inp,"allowable_stress"))}
    elif check=="section_property_utilization": computed={"utilization":utilization(_num(inp,"required"),_num(inp,"actual"))}
    elif check=="demand_capacity": computed=asdict(demand_capacity(demand=_num(inp,"demand"),capacity=_num(inp,"capacity")))
    elif check=="projected_bearing_stress": computed={"projected_bearing_stress":projected_bearing_stress(force=_num(inp,"force"),diameter=_num(inp,"diameter"),thickness=_num(inp,"thickness"))}
    elif check=="shear_tension_demand": computed=asdict(shear_tension_demand(shear_x=float(inp.get("shear_x",0)),shear_y=float(inp.get("shear_y",0)),tension=float(inp.get("tension",0)),shear_capacity=inp.get("shear_capacity"),tension_capacity=inp.get("tension_capacity")))
    elif check=="thread_engagement": computed=asdict(thread_engagement_ratio(actual_engagement=_num(inp,"actual_engagement"),required_engagement=_num(inp,"required_engagement")))
    elif check=="fastener_group":
        pts=inp.get("points")
        if not isinstance(pts,list) or not pts: raise IncompleteInputError("inputs.points requires [x,y] pairs")
        res=elastic_in_plane_group([(float(x),float(y)) for x,y in pts],fx=float(inp.get("fx",0)),fy=float(inp.get("fy",0)),mz=float(inp.get("mz",0))); computed=asdict(res); flat={"governing_resultant":res.demands[res.governing_index].resultant,"governing_index":float(res.governing_index)}; return _final(p,check,computed,flat)
    elif check=="audit_product":
        res=audit_product(factors=[float(x) for x in inp.get("factors",[])],reported=_num(inp,"reported"),abs_tol=_tol(p)[0],rel_tol=_tol(p)[1]); computed={"recomputed":res.recomputed,"status":res.comparison.status}
    elif check=="audit_force_balance":
        res=audit_force_balance(applied_forces=[float(x) for x in inp.get("applied_forces",[])],reactions=[float(x) for x in inp.get("reactions",[])],abs_tol=_tol(p)[0],rel_tol=_tol(p)[1]); computed={"applied_sum":res.applied_sum,"reaction_sum":res.reaction_sum,"residual":res.residual,"status":res.comparison.status}
    else: raise UnsupportedModelError(f"unsupported check_type: {check!r}")
    flat={k:float(v) for k,v in computed.items() if isinstance(v,(int,float)) and not isinstance(v,bool)}
    return _final(p,check,computed,flat)

def run_review(payload):
    try:
        p=_map(payload,"payload"); _units(p); inp=_map(p.get("inputs"),"inputs"); check=p.get("check_type")
        if not isinstance(check,str) or not check: raise IncompleteInputError("check_type must be a non-empty string")
        return _beam(p,inp) if check=="beam" else _simple(p,inp,check)
    except UnsupportedModelError as e: status="UNSUPPORTED_MODEL"; flag=f"UNSUPPORTED_MODEL:{e}"
    except (IncompleteInputError,TypeError,ValueError) as e: status="INCOMPLETE_INPUT"; flag=f"INCOMPLETE_INPUT:{e}"
    return {"calculation_status":status,"comparison_status":"INCOMPLETE","check_type":payload.get("check_type") if isinstance(payload,Mapping) else None,"computed":{},"comparisons":{},"review_flags":[flag]}

def main(argv=None):
    ap=argparse.ArgumentParser(); ap.add_argument("input",nargs="?"); ap.add_argument("--indent",type=int,default=2); a=ap.parse_args(argv)
    try: data=json.loads(Path(a.input).read_text(encoding="utf-8") if a.input else sys.stdin.read()); out=run_review(data)
    except (OSError,json.JSONDecodeError) as e: out={"calculation_status":"INCOMPLETE_INPUT","comparison_status":"INCOMPLETE","check_type":None,"computed":{},"comparisons":{},"review_flags":[f"INCOMPLETE_INPUT:{e}"]}
    json.dump(out,sys.stdout,ensure_ascii=False,indent=a.indent,sort_keys=True); sys.stdout.write("\n"); return 0 if out["calculation_status"]=="COMPUTED" else 2
if __name__=="__main__": raise SystemExit(main())
