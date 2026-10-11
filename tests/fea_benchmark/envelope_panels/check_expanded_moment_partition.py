"""Stage 24 exact geometric moment partition for expanded CCX 2.21 forces.

The partition is algebraic: sum[(x3D-o) x F3D] equals the moment from
projected S8R translational force plus sum[(x3D-xS8R) x F3D].
The latter is a geometric local couple, NOT a measured rotational reaction.
"""
from __future__ import annotations

import math
from pathlib import Path

from check_expanded_moment_diagnostic import force_and_geometric_moment
from check_expanded_frd import read_expanded_frd
from check_rf_3d_projection import (
    NODE8_GROUPS, project_expanded_rf, read_final_expanded_rf,
    reconcile as check_stage18)
from check_pressure_equilibrium import parse_deck
from check_follower_pressure import displacement_block


def partition_moment(original_elements, expanded_elements, original_xyz,
                     expanded_xyz, forces, origin=(0.,0.,0.)):
    projected, _ = project_expanded_rf(
        original_elements, expanded_elements, forces)
    if not projected or set(projected) != set(original_xyz):
        raise ValueError("SHELL_MOMENT_COORDINATE_COVERAGE_MISMATCH")
    if set(expanded_xyz) != set(forces):
        raise ValueError("EXPANDED_MOMENT_COORDINATE_COVERAGE_MISMATCH")
    assoc = {}
    for eid, original in enumerate(original_elements,1):
        expanded = expanded_elements[eid]
        for shell_id, indices in zip(original,NODE8_GROUPS):
            for index in indices:
                exp_id=expanded[index]
                if exp_id in assoc and assoc[exp_id]!=shell_id:
                    raise ValueError("MOMENT_EXPANDED_NODE_OWNERSHIP_AMBIGUOUS")
                assoc[exp_id]=shell_id
    if set(assoc)!=set(forces):
        raise ValueError("MOMENT_EXPANDED_NODE_COVERAGE_MISMATCH")
    total_f,total_m=force_and_geometric_moment(expanded_xyz,forces,origin)
    shell_f,shell_m=force_and_geometric_moment(original_xyz,projected,origin)
    rel_pos={}
    for eid,shell_id in assoc.items():
        p=expanded_xyz[eid];s=original_xyz[shell_id]
        rel_pos[eid]=tuple(p[i]-s[i] for i in range(3))
    local_f,local_m=force_and_geometric_moment(rel_pos,forces)
    fscale=max(1.,*(abs(x) for x in total_f))
    mscale=max(1.,*(abs(x) for x in (*total_m,*shell_m,*local_m)))
    ferr=max(abs(a-b) for a,b in zip(total_f,shell_f))
    merr=max(abs(total_m[i] - math.fsum((shell_m[i],local_m[i]))) for i in range(3))
    if ferr>1e-9*fscale or merr>1e-9*mscale:
        raise ValueError("EXPANDED_MOMENT_PARTITION_NOT_CLOSED")
    return dict(
        expanded_total_moment_Nmm=total_m,
        projected_shell_force_moment_Nmm=shell_m,
        expanded_relative_geometric_couple_Nmm=local_m,
        max_moment_partition_residual_Nmm=merr,
        max_force_partition_residual_N=ferr,
        observed_expanded_nodes=len(forces),
        six_component_balance="NOT_ADMITTED",
        rotational_reaction="UNOBSERVED",
        MPC_multiplier="UNOBSERVED")


def observe_case(deck: Path, frd: Path, dat: Path, material: str):
    from check_reconstructed_pressure_balance import reconcile as check_stage19
    from check_expanded_face import integrate_p1_expanded_face
    check_stage19(deck,frd,dat,material)
    check_stage18(deck,frd,dat)
    nodes,original,e,pressure=parse_deck(deck)
    xyz,expanded,du=read_expanded_frd(frd)
    if set(xyz)!=set(du):
        raise ValueError("INCOMPLETE_EXPANDED_DISPLACEMENT")
    actual={n:tuple(xyz[n][i]+du[n][i] for i in range(3)) for n in xyz}
    original_u=displacement_block(dat.read_text(errors="replace"),set(nodes))
    shell_xyz={n:tuple(nodes[n][i]+original_u[n][i] for i in range(3)) for n in nodes}
    internal=read_final_expanded_rf(frd,set(actual))
    external={n:[0.,0.,0.] for n in actual}
    for eid,conn in expanded.items():
        nodal,_=integrate_p1_expanded_face([actual[n] for n in conn],pressure)
        for nid,f in zip(conn,nodal):
            for axis in range(3):
                external[nid][axis]+=f[axis]
    results={}
    for label,forces in (("internal",internal),("P1_pressure",external)):
        results[label]=partition_moment(original,expanded,shell_xyz,actual,forces)
    return results


def main():
    for material in ("glass","aluminum"):
        for n in (4,8,16):
            p=Path(f"{material}_large_{n}")
            observed=observe_case(p/"panel.inp",p/"panel.frd",p/"panel.dat",material)
            print(f"{material} n={n}: {observed}")
            print("EXPANDED_MOMENT_PARTITION_ALGEBRA_ONLY; ROTATIONAL_REACTION_UNOBSERVED")
    print("STAGE24_MOMENT_PARTITION_DIAGNOSTIC_COMPLETE; GENERAL_GLOBAL_BALANCE_NOT_ADMITTED")


if __name__=="__main__":
    main()
