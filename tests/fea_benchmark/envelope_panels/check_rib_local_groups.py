"""Stage 66: per-end/per-elevation shell displacement & derived SPRING1 k*u.

Post-process exact same-run Stage 65 CCX solver cases (no new mesh/deck).
Every selected DOF1 spring is analyzed separately, then by rib end and height.
Signed two-end cancellation does not mean zero local response or independent
CCX connector reaction. This is synthetic research, NOT design capacity.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

from check_rib_spring_height import (
    K_PER_NODE, MESHES, WINDOWS, make_deck, observed as stage65_observed,
)
from check_rib_end_transfer import _dat_vectors

SCOPE="SYNTHETIC_S8R_RIB_END_LOCAL_DERIVED_KU"
MAX_PAIR_RELATIVE_ASYMMETRY=.025
ABS_DISPLACEMENT_SYMMETRY_MM=1e-9
MIN_LOCAL_ABS_FORCE_N=1e-5


def local_groups(coords,selected,vectors,expected_energy=None):
    """Bounded postprocess of CCX U; reaction signs are NOT observed.

    coords: entire original S8R deck; selected: 8 spring nodes from Stage65;
    vectors: all 16 rib-end nodes, not just those with springs.
    """
    ends={nid for nid,(x,y,z) in coords.items()
          if x in (0.,100.) and y==50. and z in tuple(float(i) for i in range(1,9))}
    if (len(ends)!=16 or set(vectors)!=ends or len(selected)!=8
            or not selected<=ends
            or any(not isinstance(v,tuple) or len(v)!=3
                   or any(type(t) not in (float,int) or not math.isfinite(t) for t in v)
                   for v in vectors.values())):
        raise ValueError("STAGE66_LOCAL_NODE_OR_VECTOR_COVERAGE")
    profiles={side:{} for side in ("x0","x100")}
    chosen={side:[] for side in ("x0","x100")}
    for nid in sorted(ends):
        x,y,z=coords[nid]
        side="x0" if x==0. else "x100"
        level=int(z)
        if float(level)!=z or level not in range(1,9) or level in profiles[side]:
            raise ValueError("STAGE66_HEIGHT_IDENTITY_INVALID")
        u=vectors[nid]
        profiles[side][level]={"node_id":nid,"u_x_mm":u[0],
                               "u_y_mm":u[1],"u_z_mm":u[2],
                               "spring_active":nid in selected}
        if nid in selected:
            chosen[side].append(nid)
    if any(set(profiles[x])!=set(range(1,9)) for x in profiles):
        raise ValueError("STAGE66_HEIGHT_PROFILE_INCOMPLETE")
    if any(len(chosen[x])!=4 for x in chosen):
        raise ValueError("STAGE66_SPRING_ENDPOINT_DISTRIBUTION")

    per_height={}
    per_end={}
    energies=[]
    selected_force=[]
    selected_moment=[]
    for side in ("x0","x100"):
        records=[]
        for nid in sorted(chosen[side], key=lambda n:coords[n][2]):
            z=coords[nid][2]
            ux=vectors[nid][0]
            ku=K_PER_NODE*ux
            zu=z*ku
            energy=0.5*K_PER_NODE*ux*ux
            records.append({"node_id":nid,"z_mm":z,"u_x_mm":ux,
                            "k_times_u_x_n":ku,
                            "z_times_k_u_n_mm":zu,
                            "half_k_u_squared_n_mm":energy})
            selected_force.append(ku)
            selected_moment.append(zu)
            energies.append(energy)
        signed=math.fsum(v["k_times_u_x_n"] for v in records)
        absolute=math.fsum(abs(v["k_times_u_x_n"]) for v in records)
        signed_moment=math.fsum(v["z_times_k_u_n_mm"] for v in records)
        abs_moment=math.fsum(abs(v["z_times_k_u_n_mm"]) for v in records)
        if absolute<=MIN_LOCAL_ABS_FORCE_N or abs(signed)<.05*absolute or abs_moment<=0:
            raise ValueError("STAGE66_LOCAL_SPRING_RESPONSE_NOT_ESTABLISHED:"+side)
        per_end[side]={"selected_nodes":records,
                       "derived_signed_k_u_n":signed,
                       "derived_sum_absolute_k_u_n":absolute,
                       "derived_signed_z_k_u_n_mm":signed_moment,
                       "derived_sum_absolute_z_k_u_n_mm":abs_moment,
                       "derived_spring_energy_n_mm":math.fsum(v["half_k_u_squared_n_mm"] for v in records),
                       "largest_abs_individual_k_u_n":max(abs(v["k_times_u_x_n"]) for v in records)}
    for z in range(1,9):
        left=profiles["x0"][z]
        right=profiles["x100"][z]
        ux0=left["u_x_mm"]
        ux100=right["u_x_mm"]
        scale=max(abs(ux0),abs(ux100))
        mismatch=abs(ux0+ux100)
        if mismatch>max(ABS_DISPLACEMENT_SYMMETRY_MM,MAX_PAIR_RELATIVE_ASYMMETRY*scale):
            raise ValueError("STAGE66_TWO_END_LOCAL_DISPLACEMENT_ASYMMETRY:"+str(z))
        if left["spring_active"]!=right["spring_active"]:
            raise ValueError("STAGE66_SPRING_PAIR_ACTIVITY_MISMATCH:"+str(z))
        per_height[str(z)]={"x0_ux_mm":ux0,"x100_ux_mm":ux100,
                            "opposite_displacement_residual_mm":mismatch,
                            "selected_spring_pair":left["spring_active"],
                            "derived_pair_k_u_sum_n":(K_PER_NODE*(ux0+ux100)
                                                       if left["spring_active"] else None),
                            "derived_pair_abs_k_u_sum_n":(K_PER_NODE*(abs(ux0)+abs(ux100))
                                                           if left["spring_active"] else None)}
    e=math.fsum(energies)
    if (not math.isfinite(e) or e<=1e-15 or
            (expected_energy is not None and
             (type(expected_energy) not in (float,int) or not math.isfinite(expected_energy)
              or abs(e-expected_energy)>max(1e-12,1e-5*expected_energy)))):
        raise ValueError("STAGE66_SPRING_ENERGY_IDENTITY_MISMATCH")
    signed=math.fsum(selected_force)
    signed_m=math.fsum(selected_moment)
    absolute=math.fsum(abs(v) for v in selected_force)
    abs_m=math.fsum(abs(v) for v in selected_moment)
    if (abs(signed)>max(1e-6,MAX_PAIR_RELATIVE_ASYMMETRY*absolute)
            or abs(signed_m)>max(1e-5,MAX_PAIR_RELATIVE_ASYMMETRY*abs_m)):
        raise ValueError("STAGE66_TWO_END_DERIVED_CANCELLATION_FAILED")
    return {"per_end":per_end,"per_height":per_height,
            "all_rib_end_node_displacements_mm":profiles,
            "selected_spring_count":len(selected),
            "derived_total_signed_k_u_n":signed,
            "derived_total_abs_k_u_n":absolute,
            "derived_total_signed_z_k_u_n_mm":signed_m,
            "derived_total_abs_z_k_u_n_mm":abs_m,
            "derived_spring_energy_n_mm":e,
            "k_u_from_solver_displacement_not_independent_reaction":True,
            "local_reaction_or_moment_independently_measured":"NO"}


def case(root:Path,n:int,window:str):
    root=Path(root)
    stage65=stage65_observed(root,n,window)
    deck,web,end_nodes,elements,coords,selected=make_deck(n,window)
    # stage65_observed already verifies exact input, required DAT/STA/FRD,
    # solver completion, full field coverage, and valid pressure-work proxy.
    vectors=_dat_vectors(root/"panel.dat","RIB_END_SPRING_NODES","U")
    if set(vectors)!=end_nodes:
        raise ValueError("STAGE66_FULL_RIB_END_FIELD_INCOMPLETE")
    groups=local_groups(coords,selected,vectors,stage65["spring_energy_derived_n_mm"])
    return {"mesh":n,"spring_height_window":window,
            "web_work_conjugate_mean_u3_mm":stage65["web_work_conjugate_mean_u3_mm"],
            "provenance":"SAME_CI_EXACT_STAGE65_CASE_RECHECK",
            "sha256":stage65["sha256"],**groups}


def assess(cases):
    if set(cases)!={f"n{n}_{w}" for n in MESHES for w in WINDOWS}:
        raise ValueError("STAGE66_CASE_COVERAGE_INVALID")
    for w in WINDOWS:
        for n in MESHES:
            c=cases[f"n{n}_{w}"]
            if c["selected_spring_count"]!=8 or c["derived_total_abs_k_u_n"]<=2*MIN_LOCAL_ABS_FORCE_N:
                raise ValueError("STAGE66_SPRING_GROUP_NO_SIGNAL")
    return {"scope":SCOPE,
            "cases":cases,
            "two_ends_cancel_but_each_end_has_nonzero_derived_spring_load":True,
            "global_zero_result_does_not_imply_zero_local_load":True,
            "mesh_8_16_local_pointwise_convergence_rate":"NOT_CLAIMED",
            "local_connection_force_capacity":"NOT_ADMITTED",
            "independent_support_reaction_moment":"NOT_ADMITTED",
            "S8R_local_stress_peak":"NOT_EVALUATED",
            "general_six_component_balance":"NOT_ADMITTED",
            "engineering_acceptance":"NOT_ADMITTED"}


def check(root:Path):
    root=Path(root)
    cases={f"n{n}_{w}":case(root/f"rib_height_{w}_n{n}",n,w)
           for n in MESHES for w in WINDOWS}
    return assess(cases)


if __name__=="__main__":
    if len(sys.argv)==2:
        print(json.dumps(check(Path(sys.argv[1])),sort_keys=True,allow_nan=False))
        print("STAGE66_LOCAL_SPRING_GROUP_POSTPROCESS_PASS; NO_INDEPENDENT_SUPPORT_REACTION")
    else:
        raise SystemExit("USAGE: check_rib_local_groups.py ROOT (Stage65 same-workflow solver output)")
