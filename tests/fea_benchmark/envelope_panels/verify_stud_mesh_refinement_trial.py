"""Hot 2 real C3D20R signed four-Z-link mesh evidence and convergence screen.

The n8/n16/n24 decks are re-generated at the same pinned Git revision;
the solver's DAT/STA/FRD are checked case by case. This is not a study of
physical stud stiffness, true welded joint resistance or contact stress.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

from stud_mesh_refinement_trial import MESHES, CASES, DIRECTIONS, STATIONS, deck
from verify_stud_solid_trial import field, sets
from check_u_rib_contact_observations import rf
from verify_c3d20r_u_contact import status
from verify_pressure_contact_trial import nominal_pressure_equivalents
from pressure_contact_trial import APPLIED_TOTAL_Z_N

ABS_BALANCE_N = 0.002
STATION_SYMMETRY_N = 0.002
REFINEMENT_SCREEN_RELATIVE = 0.05   # declared screening threshold, NOT a convergence proof


def fail(code):
    raise ValueError("STUD_REFINEMENT_" + code)


def sample(n, case, direction, groups, plate, rib, center, plate_rf, rib_rf):
    if type(n) is not int or n not in MESHES or case not in CASES or direction not in DIRECTIONS:
        fail("SCOPE")
    for label, values in (("STUD_PLATE", plate), ("STUD_RIB", rib), ("CENTER_RF", center)):
        if set(values) != set(groups[label]):
            fail("OBSERVATION_NODE_COVERAGE")
    if len(groups["STUD_PLATE"]) != 4 or len(groups["STUD_RIB"]) != 4:
        fail("STATION_COUNT")
    sign = DIRECTIONS[direction]
    k = CASES[case]
    forces = [k * (plate[p][2] - rib[q][2])
              for p,q in zip(groups["STUD_PLATE"], groups["STUD_RIB"])]
    if not all(math.isfinite(v) for v in forces):
        fail("STATION_NONFINITE")
    if k > 0:
        if min(sign * x for x in forces) <= 1e-7:
            fail("STATION_WRONG_DIRECTION")
        if abs(forces[0]-forces[3]) > STATION_SYMMETRY_N or abs(forces[1]-forces[2]) > STATION_SYMMETRY_N:
            fail("SYMMETRY")
    elif any(forces) or abs(rib_rf)>ABS_BALANCE_N:
        fail("UNLINKED")
    force_total=math.fsum(forces)
    rib_balance=math.fsum([force_total,rib_rf])
    if abs(rib_balance)>ABS_BALANCE_N:
        fail("RIB_ACTION_REACTION")
    eq=nominal_pressure_equivalents(n)
    global_balance=math.fsum([plate_rf,rib_rf,-sign*eq["edge_pressure_n"],sign*APPLIED_TOTAL_Z_N])
    if abs(global_balance)>ABS_BALANCE_N:
        fail("GLOBAL_BALANCE")
    center_u=math.fsum(values[2] for values in center.values())/len(center)
    if not math.isfinite(center_u) or sign*center_u<=0:
        fail("CENTER_SIGN")
    return {
      "mesh":n,"case":case,"direction":direction,
      "nominal_signed_pressure_n_per_mm2":sign*.0001,
      "synthetic_k_n_per_mm":k,
      "stud_positions_mm":list(STATIONS),
      "signed_forces_n":forces,
      "max_signed_force_magnitude_n":max(map(abs,forces)),
      "total_signed_force_n":force_total,
      "rib_end_observed_rf3_n":rib_rf,
      "rib_balance_residual_n":rib_balance,
      "global_z_balance_residual_n":global_balance,
      "center_mean_u3_mm":center_u,
    }


def compare(rows):
    if len(rows)!=len(MESHES)*len(CASES)*len(DIRECTIONS):
        fail("CASE_COUNT")
    idx={}
    for item in rows:
        key=(item["mesh"],item["case"],item["direction"])
        if key in idx:fail("DUPLICATE_CASE")
        idx[key]=item
    comparisons=[]
    for case in CASES:
        for direction in DIRECTIONS:
            prev=None
            for n in MESHES:
                record=idx.get((n,case,direction))
                if record is None:fail("MISSING_CASE")
                if prev:
                    center_change=abs(record["center_mean_u3_mm"]-prev["center_mean_u3_mm"])
                    center_relative=center_change/max(abs(record["center_mean_u3_mm"]),1.e-12)
                    old=prev["signed_forces_n"];new=record["signed_forces_n"]
                    if len(old)!=len(new):fail("LINK_COUNT_DRIFT")
                    per_station=[abs(b-a) for a,b in zip(old,new)]
                    peak_difference=max(per_station)
                    peak_magnitude=max(abs(v) for v in new)
                    if CASES[case]:
                        link_relative=peak_difference/max(peak_magnitude,1.e-12)
                        link_status="WITHIN_DECLARED_5_PERCENT_SCREEN" if link_relative<=REFINEMENT_SCREEN_RELATIVE else "NOT_WITHIN_SCREEN"
                    else:
                        link_relative=None
                        link_status="UNLINKED_ZERO_BY_DEFINITION"
                    comparisons.append({
                        "case":case,"direction":direction,
                        "coarse_mesh":prev["mesh"],"fine_mesh":n,
                        "max_station_force_change_n":peak_difference,
                        "max_station_force_change_relative":link_relative,
                        "center_change_mm":center_change,
                        "center_change_relative":center_relative,
                        "force_screen":link_status,
                        "center_screen":"WITHIN_DECLARED_5_PERCENT_SCREEN" if center_relative<=REFINEMENT_SCREEN_RELATIVE else "NOT_WITHIN_SCREEN",
                    })
                prev=record
    if len(comparisons)!=12:fail("COMPARISON_COVERAGE")
    statuses=[x["force_screen"] for x in comparisons if x["force_screen"]!="UNLINKED_ZERO_BY_DEFINITION"]
    last=[x for x in comparisons if x["fine_mesh"]==24]
    last_ok=all(x["center_screen"]=="WITHIN_DECLARED_5_PERCENT_SCREEN" and
                x["force_screen"]!="NOT_WITHIN_SCREEN" for x in last)
    return {
        "scope":"SYNTHETIC_C3D20R_FIXED_FOUR_STATION_SIGNED_MESH_STUDY_NOT_DESIGN",
        "mesh_list":list(MESHES),
        "case_count":len(rows),
        "cases":rows,"comparisons":comparisons,
        "last_refinement_passes_declared_5_percent_screen":last_ok,
        "last_refinement_status":"BOUNDED_MESH_SENSITIVITY_SCREEN_ONLY" if last_ok else "MESH_SENSITIVITY_NOT_WITHIN_SCREEN",
        "local_connector_force_convergence":"NOT_ESTABLISHED",
        "mesh_independent_true_stud_force":"NOT_ESTABLISHED",
        "real_stud_strength_and_stiffness":"NOT_ADMITTED",
        "engineering_acceptance":"NOT_ADMITTED",
    }


def verify(root):
    root=Path(root);records=[]
    for n in MESHES:
        for case in CASES:
            for direction in DIRECTIONS:
                folder=root/f"refine_{n}_{case}_{direction}"
                sources={suffix:folder/f"panel.{suffix}" for suffix in ("inp","dat","sta","frd")}
                if any(path.is_symlink() or not path.is_file() or path.stat().st_size==0 for path in sources.values()):
                    fail("SOURCE_FILE")
                expected=deck(n,case,direction)
                if sources["inp"].read_text(encoding="utf8")!=expected:fail("INPUT_PROVENANCE")
                status(sources["sta"].read_text(encoding="utf8",errors="replace"))
                groups=sets(expected)
                dat=sources["dat"].read_text(encoding="utf8",errors="replace")
                plate=field(dat,"STUD_PLATE",groups["STUD_PLATE"])
                rib=field(dat,"STUD_RIB",groups["STUD_RIB"])
                center=field(dat,"CENTER_RF",groups["CENTER_RF"])
                plate_rf=rf(dat,"PLATE_EDGE_RF",expected_nodes=groups["PLATE_EDGE_RF"])["sum_rf3_n"]
                rib_rf=rf(dat,"RIB_END_RF",expected_nodes=groups["RIB_END_RF"])["sum_rf3_n"]
                records.append(sample(n,case,direction,groups,plate,rib,center,plate_rf,rib_rf))
    return compare(records)


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("source_directory",type=Path)
    args=ap.parse_args()
    print(json.dumps(verify(args.source_directory),indent=2,sort_keys=True,allow_nan=False))
