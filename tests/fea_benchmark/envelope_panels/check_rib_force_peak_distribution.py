"""Stage 67: bounded spring-group force peaks, height distribution, mesh screen.

Post-process SAME-CI Stage65/66 real CalculiX displacements; no additional
model, deck, shell stress, connector reaction, or capacity calculation.
The k*u and z*k*u terms are independently re-summed from Stage66-recorded
nodewise data, but are NOT independent observed support forces or moments.
"""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path

from check_rib_local_groups import check as stage66_check
from check_rib_spring_height import WINDOWS, MESHES, K_PER_NODE

SCOPE="SYNTHETIC_S8R_RIB_SPRING_DERIVED_PEAK_HEIGHT_DISTRIBUTION"
MESH_RELATIVE_SCREEN=.15
IDENTITY_RELATIVE_TOL=1e-8
IDENTITY_ABSOLUTE_TOL=1e-10


def _close(observed:float, expected:float) -> bool:
    return abs(observed-expected)<=max(
        IDENTITY_ABSOLUTE_TOL,IDENTITY_RELATIVE_TOL*max(abs(observed),abs(expected))
    )


def end_profile(case:dict,side:str,window:str) -> dict:
    if side not in ("x0","x100") or window not in WINDOWS:
        raise ValueError("STAGE67_PROFILE_SCOPE_REJECTED")
    if case.get("spring_height_window")!=window:
        raise ValueError("STAGE67_PROFILE_WINDOW_MISMATCH")
    grouped=case.get("per_end",{})
    if not isinstance(grouped,dict) or set(grouped)!={"x0","x100"}:
        raise ValueError("STAGE67_TWO_END_COVERAGE")
    end=grouped[side]
    nodes=end.get("selected_nodes")
    heights=list(range(1,5)) if window=="low" else list(range(5,9))
    if not isinstance(nodes,list) or len(nodes)!=4:
        raise ValueError("STAGE67_FOUR_SPRING_COVERAGE")
    rows=[]
    seen_nodes=set()
    seen_heights=set()
    for v in nodes:
        if not isinstance(v,dict):
            raise ValueError("STAGE67_SPRING_ROW_MALFORMED")
        nid=v.get("node_id")
        z=v.get("z_mm")
        u=v.get("u_x_mm")
        f=v.get("k_times_u_x_n")
        m=v.get("z_times_k_u_n_mm")
        e=v.get("half_k_u_squared_n_mm")
        if (type(nid) is not int or nid<=0 or nid in seen_nodes
                or type(z) not in (float,int)
                or type(u) not in (float,int)
                or type(f) not in (float,int)
                or type(m) not in (float,int)
                or type(e) not in (float,int)
                or not all(math.isfinite(t) for t in (z,u,f,m,e))
                or z in seen_heights or z not in heights):
            raise ValueError("STAGE67_NONFINITE_OR_DUPLICATED_HEIGHT_OR_NODE")
        seen_nodes.add(nid)
        seen_heights.add(z)
        if (not _close(f,K_PER_NODE*u)
                or not _close(m,z*f)
                or not _close(e,.5*K_PER_NODE*u*u)
                or e<0):
            raise ValueError("STAGE67_INDEPENDENT_ARITHMETIC_IDENTITY_FAILED")
        rows.append({"z_mm":int(z),"node_id":nid,
                     "u_x_mm":u,"signed_k_u_n":f,"abs_k_u_n":abs(f),
                     "signed_z_k_u_n_mm":m,"spring_energy_n_mm":e})
    if set(seen_heights)!=set(heights):
        raise ValueError("STAGE67_HEIGHT_COVERAGE_INCOMPLETE")
    rows.sort(key=lambda x:x["z_mm"])
    total=math.fsum(r["abs_k_u_n"] for r in rows)
    signed=math.fsum(r["signed_k_u_n"] for r in rows)
    weighted=math.fsum(r["z_mm"]*r["abs_k_u_n"] for r in rows)
    moment=math.fsum(r["signed_z_k_u_n_mm"] for r in rows)
    energy=math.fsum(r["spring_energy_n_mm"] for r in rows)
    if not all(math.isfinite(t) for t in (total,signed,weighted,moment,energy)) or total<=0 or weighted<=0 or energy<=0:
        raise ValueError("STAGE67_ZERO_OR_INVALID_LOCAL_DISTRIBUTION")
    if not all(_close(value,expected) for value,expected in (
        (total,end["derived_sum_absolute_k_u_n"]),
        (signed,end["derived_signed_k_u_n"]),
        (weighted,end["derived_sum_absolute_z_k_u_n_mm"]),
        (moment,end["derived_signed_z_k_u_n_mm"]),
        (energy,end["derived_spring_energy_n_mm"]))):
        raise ValueError("STAGE67_STAGE66_GROUP_SUM_INCONSISTENT")
    peak=max(rows,key=lambda v:v["abs_k_u_n"])
    if not _close(peak["abs_k_u_n"],end["largest_abs_individual_k_u_n"]):
        raise ValueError("STAGE67_STAGE66_PEAK_IDENTITY")
    distribution=[{**row,"force_fraction":row["abs_k_u_n"]/total}
                  for row in rows]
    if not _close(math.fsum(r["force_fraction"] for r in distribution),1.0):
        raise ValueError("STAGE67_FRACTION_NORMALIZATION")
    return {
        "side":side,"window":window,
        "force_magnitude_sum_n":total,
        "signed_force_sum_n":signed,
        "height_weighted_force_magnitude_n_mm":weighted,
        "signed_z_k_u_sum_n_mm":moment,
        "force_magnitude_centroid_z_mm":weighted/total,
        "peak_individual_abs_k_u_n":peak["abs_k_u_n"],
        "peak_node_id":peak["node_id"],
        "peak_at_height_mm":peak["z_mm"],
        "peak_fraction_of_end_sum":peak["abs_k_u_n"]/total,
        "derived_spring_energy_n_mm":energy,
        "height_distribution":distribution,
        "not_measured_connector_reaction_or_capacity":True,
    }


def compare_meshes(cases:dict) -> dict:
    expected={f"n{n}_{w}" for n in MESHES for w in WINDOWS}
    if not isinstance(cases,dict) or set(cases)!=expected:
        raise ValueError("STAGE67_REQUIRED_CASE_COVERAGE")
    result={}
    for w in WINDOWS:
        result[w]={}
        for side in ("x0","x100"):
            coarse=end_profile(cases[f"n8_{w}"],side,w)
            fine=end_profile(cases[f"n16_{w}"],side,w)
            values={}
            for key in ("force_magnitude_sum_n",
                        "height_weighted_force_magnitude_n_mm",
                        "force_magnitude_centroid_z_mm",
                        "peak_individual_abs_k_u_n"):
                v8=coarse[key];v16=fine[key]
                if v16<=0 or not math.isfinite(v16):
                    raise ValueError("STAGE67_INVALID_FINE_MESH_VALUE:"+key)
                difference=abs(v16-v8)/v16
                if difference>MESH_RELATIVE_SCREEN:
                    raise ValueError("STAGE67_MESH_SCREEN_FAILED:"+w+":"+side+":"+key)
                values[key]=difference
            local={}
            for a,b in zip(coarse["height_distribution"],fine["height_distribution"]):
                z=a["z_mm"]
                if z!=b["z_mm"] or b["abs_k_u_n"]<=0:
                    raise ValueError("STAGE67_LOCAL_HEIGHT_IDENTITY_OR_ZERO")
                delta=abs(b["abs_k_u_n"]-a["abs_k_u_n"])/b["abs_k_u_n"]
                if delta>MESH_RELATIVE_SCREEN:
                    raise ValueError("STAGE67_POINTWISE_HEIGHT_SCREEN_FAILED:"+w+":"+side+":"+str(z))
                local[str(z)]=delta
            if coarse["peak_at_height_mm"]!=fine["peak_at_height_mm"]:
                raise ValueError("STAGE67_DISCRETE_PEAK_HEIGHT_CHANGED:"+w+":"+side)
            result[w][side]={
                "coarse_n8":coarse,
                "fine_n16":fine,
                "global_metric_mesh_relative_differences":values,
                "same_height_abs_k_u_mesh_relative_differences":local,
                "screen_limit":MESH_RELATIVE_SCREEN,
                "mesh_convergence_order":"NOT_ESTABLISHED_TWO_MESH_SCREEN_ONLY",
            }
    for w in WINDOWS:
        left=result[w]["x0"]["fine_n16"]
        right=result[w]["x100"]["fine_n16"]
        for key in ("peak_individual_abs_k_u_n","force_magnitude_sum_n",
                    "height_weighted_force_magnitude_n_mm","force_magnitude_centroid_z_mm"):
            if not _close(left[key],right[key]):
                raise ValueError("STAGE67_SYMMETRIC_GROUP_ENVELOPE_MISMATCH:"+w+":"+key)
    return {
        "scope":SCOPE,"cases_by_window_and_end":result,
        "mesh_8_16_only":True,
        "absolute_k_u_envelope_not_algebraic_global_sum":True,
        "height_weighted_demand_is_derived_about_global_z0_not_recovered_support_moment":True,
        "independent_spring_reaction":"NOT_MEASURED_K_TIMES_U_ONLY",
        "pointwise_mesh_convergence_order":"NOT_ADMITTED",
        "S8R_local_stress_peak":"NOT_EVALUATED",
        "real_connector_or_fastener_capacity":"NOT_ADMITTED",
        "general_six_component_balance":"NOT_ADMITTED",
        "engineering_acceptance":"NOT_ADMITTED",
    }


def check(root:Path):
    stage66=stage66_check(Path(root))
    if (stage66.get("scope")!="SYNTHETIC_S8R_RIB_END_LOCAL_DERIVED_KU"
            or stage66.get("engineering_acceptance")!="NOT_ADMITTED"):
        raise ValueError("STAGE67_STAGE66_PROVENANCE_OR_SCOPE_DRIFT")
    out=compare_meshes(stage66["cases"])
    out["exact_case_artifact_sha256"]={
        key:item["sha256"] for key,item in stage66["cases"].items()}
    out["underlying_study"]="SAME_CI_STAGE65_AND_STAGE66_CHECKERS_REEXECUTED"
    return out


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("USAGE: check_rib_force_peak_distribution.py ROOT")
    print(json.dumps(check(Path(sys.argv[1])),sort_keys=True,allow_nan=False))
    print("STAGE67_LOCAL_FORCE_HEIGHT_MESH_SCREEN_PASS; NO_INDEPENDENT_REACTION_OR_CAPACITY")
