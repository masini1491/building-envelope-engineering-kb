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
from .glazing_condensation import CondensationInputError, screen_center_glass_condensation
from .member_preliminary_screen import MemberScreenInputError, screen_preliminary_member_options
from .member_multispan_screen import MultispanInputError, screen_multispan_options
from .wind_pressure import (
    WindPressureInputError,
    WindPressureUnsupportedError,
    calculate_roof_design_pressure,
    calculate_wall_design_pressure,
)

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


def _wind_pressure(p, inp):
    required_strings = [
        "region",
        "terrain_category",
        "enclosure",
        "governing_wind_source",
    ]
    values = {}
    for key in required_strings:
        value = inp.get(key)
        if not isinstance(value, str) or not value.strip():
            raise IncompleteInputError(f"inputs.{key} is required")
        values[key] = value.strip()

    if "building_category" not in inp:
        raise IncompleteInputError("inputs.building_category is required")
    values["building_category"] = inp["building_category"]
    values["district"] = inp.get("district")
    surface = str(inp.get("surface", "wall")).strip().lower()
    if surface not in {"wall", "roof"}:
        raise IncompleteInputError("inputs.surface must be wall or roof")

    h_m = _num(inp, "h_m")
    basis = inp.get("positive_internal_pressure_basis", "q(h)")
    if not isinstance(basis, str):
        raise IncompleteInputError("inputs.positive_internal_pressure_basis must be a string")
    opening_top = (_num(inp, "opening_top_height_m")
                   if inp.get("opening_top_height_m") is not None else None)
    try:
        if surface == "roof":
            apply_parapet = inp.get("apply_parapet_zone3_as_zone2", False)
            if not isinstance(apply_parapet, bool):
                raise IncompleteInputError(
                    "inputs.apply_parapet_zone3_as_zone2 must be boolean"
                )
            parapet_all_sides = inp.get("parapet_all_sides", False)
            if not isinstance(parapet_all_sides, bool):
                raise IncompleteInputError("inputs.parapet_all_sides must be boolean")
            parapet_height = None
            if "parapet_height_m" in inp and inp.get("parapet_height_m") is not None:
                parapet_height = _num(inp, "parapet_height_m")
            computed = calculate_roof_design_pressure(
                region=values["region"],
                district=values["district"],
                building_category=values["building_category"],
                terrain_category=values["terrain_category"],
                kzt=_num(inp, "kzt"),
                enclosure=values["enclosure"],
                h_m=h_m,
                roof_slope_deg=_num(inp, "roof_slope_deg"),
                effective_area_m2=_num(inp, "effective_area_m2"),
                least_horizontal_dimension_m=_num(inp, "least_horizontal_dimension_m"),
                governing_wind_source=values["governing_wind_source"],
                positive_internal_pressure_basis=basis,
                opening_top_height_m=opening_top,
                apply_parapet_zone3_as_zone2=apply_parapet,
                parapet_all_sides=parapet_all_sides,
                parapet_height_m=parapet_height,
            )
        else:
            z_value = None
            if "z_m" in inp and inp.get("z_m") is not None:
                z_value = _num(inp, "z_m")
            apply_reduction = inp.get("apply_low_slope_wall_reduction", False)
            if not isinstance(apply_reduction, bool):
                raise IncompleteInputError(
                    "inputs.apply_low_slope_wall_reduction must be boolean"
                )
            roof_slope = None
            if "roof_slope_deg" in inp and inp.get("roof_slope_deg") is not None:
                roof_slope = _num(inp, "roof_slope_deg")
            computed = calculate_wall_design_pressure(
                region=values["region"],
                district=values["district"],
                building_category=values["building_category"],
                terrain_category=values["terrain_category"],
                kzt=_num(inp, "kzt"),
                enclosure=values["enclosure"],
                h_m=h_m,
                z_m=z_value,
                effective_area_m2=_num(inp, "effective_area_m2"),
                least_horizontal_dimension_m=_num(inp, "least_horizontal_dimension_m"),
                governing_wind_source=values["governing_wind_source"],
                positive_internal_pressure_basis=basis,
                opening_top_height_m=opening_top,
                roof_slope_deg=roof_slope,
                apply_low_slope_wall_reduction=apply_reduction,
            )
    except WindPressureUnsupportedError as exc:
        raise UnsupportedModelError(str(exc)) from exc
    except WindPressureInputError as exc:
        raise IncompleteInputError(str(exc)) from exc

    flat = {
        "qh_kpa": computed["velocity_pressure"]["qh"]["q_kpa"],
        "corner_a_m": computed["corner_zone"]["a_m"],
    }
    qz = computed["velocity_pressure"].get("qz")
    if qz is not None:
        flat["qz_kpa"] = qz["q_kpa"]
    for zone, pressures in computed["pressures"].items():
        if "positive_kpa" in pressures:
            flat[f"{zone}.positive_kpa"] = pressures["positive_kpa"]
        if "negative_kpa" in pressures:
            flat[f"{zone}.negative_kpa"] = pressures["negative_kpa"]
    return _final(p, "wind_pressure", computed, flat)

def _glazing_condensation(p, inp):
    for field in (
        "indoor_temperature_c", "outdoor_temperature_c",
        "indoor_relative_humidity_pct", "glazing_u_value_w_m2k",
        "interior_surface_resistance_m2k_w",
    ):
        if isinstance(inp.get(field), bool):
            raise IncompleteInputError(f"inputs.{field} must be numeric, not boolean")
    try:
        result = screen_center_glass_condensation(
            indoor_temperature_c=_num(inp, "indoor_temperature_c"),
            outdoor_temperature_c=_num(inp, "outdoor_temperature_c"),
            indoor_relative_humidity_pct=_num(inp, "indoor_relative_humidity_pct"),
            glazing_u_value_w_m2k=_num(inp, "glazing_u_value_w_m2k"),
            interior_surface_resistance_m2k_w=_num(
                inp, "interior_surface_resistance_m2k_w"
            ),
        )
    except CondensationInputError as exc:
        raise IncompleteInputError(str(exc)) from exc
    computed = asdict(result)
    flat = {
        "interior_surface_temperature_c": result.interior_surface_temperature_c,
        "indoor_dew_point_c": result.indoor_dew_point_c,
    }
    if result.temperature_factor_frsi is not None:
        flat["temperature_factor_frsi"] = result.temperature_factor_frsi
    return _final(p, "glazing_condensation", computed, flat)



# This check_type is strictly unit-locked; ranges must already be converted.
_MEMBER_UNITS = {
    "span": "m", "tributary_width": "m", "elastic_modulus": "MPa",
    "wind_pressure": "kPa", "inertia": "mm^4", "section_modulus": "mm^3",
}
_MEMBER_FIELDS = {
    "member_role", "span_m_range", "span_source",
    "tributary_width_m_range", "tributary_width_source",
    "elastic_modulus_mpa_range", "elastic_modulus_source",
    "wind_cases", "options", "deflection_limit_mm", "deflection_limit_source",
}
_MEMBER_WIND_FIELDS = {"name", "direction", "pressure_magnitude_kpa_range", "pressure_source"}
_MEMBER_OPTION_FIELDS = {
    "name", "support_model", "support_source", "section_property_source",
    "inertia_mm4_range", "section_modulus_positive_mm3_range",
    "section_modulus_negative_mm3_range",
}


def _member_preliminary(p, inp):
    """Route caller-bounded idealized member demand through the canonical screen.

    The adapter does not derive project loads, material values, code criteria,
    member capacities or applicability. A computed response is NOT acceptance.
    """
    units = _map(p["units"], "units")
    if set(units) != set(_MEMBER_UNITS):
        raise IncompleteInputError("member_preliminary_screen requires exactly: " +
                                   ", ".join(sorted(_MEMBER_UNITS)))
    for key, expected in _MEMBER_UNITS.items():
        if units[key] != expected:
            raise IncompleteInputError(f"units.{key} must be {expected}")
    unknown = set(inp) - _MEMBER_FIELDS
    if unknown:
        raise IncompleteInputError("unsupported member input fields: " + ", ".join(sorted(map(str, unknown))))
    for name, allowed in (("wind_cases", _MEMBER_WIND_FIELDS),
                          ("options", _MEMBER_OPTION_FIELDS)):
        items = inp.get(name)
        if not isinstance(items, list) or not items:
            raise IncompleteInputError(f"inputs.{name} must be a nonempty array")
        for index, raw in enumerate(items):
            item = _map(raw, f"inputs.{name}[{index}]")
            excess = set(item) - allowed
            if excess:
                raise IncompleteInputError(f"inputs.{name}[{index}] has unsupported fields")
    if inp.get("member_role") not in ("mullion", "transom"):
        raise UnsupportedModelError("member_role supports only mullion / transom")
    for raw in inp["options"]:
        if raw.get("support_model") not in ("simply_supported", "cantilever"):
            raise UnsupportedModelError("only ideal simply_supported / cantilever models are admitted")
    for raw in inp["wind_cases"]:
        if raw.get("direction") not in ("positive", "negative"):
            raise IncompleteInputError("wind_cases.direction must be positive or negative")
    try:
        result = screen_preliminary_member_options(**inp)
    except MemberScreenInputError as exc:
        raise IncompleteInputError(str(exc)) from exc
    computed = asdict(result)
    flat = {}
    for i, option in enumerate(result.options):
        for j, case in enumerate(option.cases):
            for attr in ("line_load_n_per_mm", "max_shear_n", "max_moment_n_mm",
                         "max_deflection_mm", "extreme_fiber_stress_mpa"):
                bounds = getattr(case, attr)
                flat[f"options.{i}.cases.{j}.{attr}.minimum"] = bounds.minimum
                flat[f"options.{i}.cases.{j}.{attr}.maximum"] = bounds.maximum
    return _final(p, "member_preliminary_screen", computed, flat)




_MULTISPAN_UNITS = {
    "span": "m", "tributary_width": "m", "elastic_modulus": "MPa",
    "wind_pressure": "kPa", "inertia": "mm^4", "section_modulus": "mm^3",
}
_MULTISPAN_FIELDS = {
    "member_role", "span_lengths_m", "span_source", "tributary_widths_m",
    "tributary_width_source", "wind_cases", "options",
    "deflection_limit_mm", "deflection_limit_source",
}


def _member_multispan(p, inp):
    units = _map(p["units"], "units")
    if units != _MULTISPAN_UNITS:
        raise IncompleteInputError("member_multispan_screen requires exact units: " + str(_MULTISPAN_UNITS))
    if set(inp) - _MULTISPAN_FIELDS:
        raise IncompleteInputError("unsupported member_multispan_screen fields")
    options = inp.get("options")
    if not isinstance(options, list) or not options:
        raise IncompleteInputError("inputs.options must be a nonempty array")
    for option in options:
        opt = _map(option, "option")
        if opt.get("support_model") not in ("continuous_pinned_supports", "continuous_fixed_ends"):
            raise UnsupportedModelError("unsupported multi-span support model / incomplete support condition")
    try:
        result = screen_multispan_options(**inp)
    except MultispanInputError as exc:
        raise IncompleteInputError(str(exc)) from exc
    computed = asdict(result)
    flat = {}
    for i, option in enumerate(result.options):
        for j, case in enumerate(option.cases):
            for key in ("maximum_absolute_shear_n", "maximum_absolute_moment_n_mm",
                        "maximum_absolute_deflection_mm", "maximum_absolute_bending_stress_mpa",
                        "positive_moment_max_n_mm", "negative_moment_magnitude_max_n_mm"):
                flat[f"options.{i}.cases.{j}.{key}"] = getattr(case, key)
            for k, reaction in enumerate(case.reactions_n):
                flat[f"options.{i}.cases.{j}.reactions_n.{k}"] = reaction
    return _final(p, "member_multispan_screen", computed, flat)


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
        if check=="beam": return _beam(p,inp)
        if check=="wind_pressure": return _wind_pressure(p,inp)
        if check=="glazing_condensation": return _glazing_condensation(p,inp)
        if check=="member_preliminary_screen": return _member_preliminary(p,inp)
        if check=="member_multispan_screen": return _member_multispan(p,inp)
        return _simple(p,inp,check)
    except UnsupportedModelError as e: status="UNSUPPORTED_MODEL"; flag=f"UNSUPPORTED_MODEL:{e}"
    except (IncompleteInputError,TypeError,ValueError) as e: status="INCOMPLETE_INPUT"; flag=f"INCOMPLETE_INPUT:{e}"
    return {"calculation_status":status,"comparison_status":"INCOMPLETE","check_type":payload.get("check_type") if isinstance(payload,Mapping) else None,"computed":{},"comparisons":{},"review_flags":[flag]}

def main(argv=None):
    ap=argparse.ArgumentParser(); ap.add_argument("input",nargs="?"); ap.add_argument("--indent",type=int,default=2); a=ap.parse_args(argv)
    try: data=json.loads(Path(a.input).read_text(encoding="utf-8") if a.input else sys.stdin.read()); out=run_review(data)
    except (OSError,json.JSONDecodeError) as e: out={"calculation_status":"INCOMPLETE_INPUT","comparison_status":"INCOMPLETE","check_type":None,"computed":{},"comparisons":{},"review_flags":[f"INCOMPLETE_INPUT:{e}"]}
    json.dump(out,sys.stdout,ensure_ascii=False,indent=a.indent,sort_keys=True); sys.stdout.write("\n"); return 0 if out["calculation_status"]=="COMPUTED" else 2
if __name__=="__main__": raise SystemExit(main())
