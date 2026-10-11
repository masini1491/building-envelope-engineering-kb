"""Bounded user-parameter aluminum S8R research input; no capacity admission."""
from __future__ import annotations
import json
import math
from pathlib import Path

_KEYS={"width_mm","height_mm","thickness_mm","youngs_modulus_mpa",
       "poisson_ratio","pressure_n_mm2","mesh","support","units",
       "material_provenance"}

def validate(value:dict)->dict:
    if not isinstance(value,dict) or set(value)!=_KEYS:
        raise ValueError("ALUMINUM_INPUT_SCHEMA_MISMATCH")
    if value["units"]!="N-mm-MPa" or value["support"]!="four_edges_clamped":
        raise ValueError("UNSUPPORTED_UNITS_OR_SUPPORT")
    if not isinstance(value["material_provenance"],str) or not 1<=len(value["material_provenance"].strip())<=200:
        raise ValueError("MATERIAL_EVIDENCE_LABEL_REQUIRED")
    if type(value["mesh"]) is not int or value["mesh"] not in (4,8,16):
        raise ValueError("UNSUPPORTED_MESH")
    limits={"width_mm":(50,1000),"height_mm":(50,1000),"thickness_mm":(0.5,12),
            "youngs_modulus_mpa":(10000,100000),"poisson_ratio":(0.01,0.49),
            "pressure_n_mm2":(0.00001,0.6)}
    for key,(low,high) in limits.items():
        x=value[key]
        if type(x) not in (float,int) or not math.isfinite(x) or not low<=x<=high:
            raise ValueError("PARAMETER_OUTSIDE_RESEARCH_BOUND:"+key)
    if min(value["width_mm"],value["height_mm"])/value["thickness_mm"]<15:
        raise ValueError("SHELL_THINNESS_SCOPE_REJECTED")
    return dict(value)

def load(path:Path)->dict:
    if path.is_symlink() or not path.is_file() or not 0<path.stat().st_size<=4096:
        raise ValueError("INPUT_JSON_NOT_REGULAR_BOUNDED")
    def reject_constant(v):raise ValueError("NONFINITE_JSON")
    def reject_duplicate(pairs):
        out={}
        for k,v in pairs:
            if k in out:raise ValueError("DUPLICATE_INPUT_KEY")
            out[k]=v
        return out
    return validate(json.loads(path.read_text(encoding="utf-8"),parse_constant=reject_constant,
                               object_pairs_hook=reject_duplicate))
