"""Stage 68: clean-SPC SPRING2 RF observation and RF-vs-reaction contamination.

Only a two-node translational spring, no MPC, S8R shell, real connector,
rotational DOF spring or engineering capacity. N-mm-N/mm units. The verified
support is not directly loaded in the clean variant, so CCX RF there has a
narrow support-reaction interpretation. Loaded-node RF is an internal nodal resultant at this unconstrained point,
NOT a support reaction. The directly loaded fixed-node variant probes whether
CCX's raw RF responds to that load; it DOES NOT assume a universal rule.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from pathlib import Path

from check_u_fold_cantilever import _completed

CASES=("clean_spc","loaded_spc")
K=250.0                 # N/mm
P=1.25                  # N applied at free node, global z
SUPPORT_LOAD={"clean_spc":0.0,"loaded_spc":0.4}
EXPECTED_U2=P/K
FLOATING_NODE=2
FIXED_NODE=1
NUMBER=r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?"
VALUE_LINE=re.compile(r"\s*(\d+)\s+("+NUMBER+r")\s+("+NUMBER+r")\s+("+NUMBER+r")\s*")

def deck(case:str)->str:
    if case not in CASES:
        raise ValueError("STAGE68_CASE_OUTSIDE_SCOPE")
    lines=[
        "*HEADING",f"stage68-synthetic-two-node-translational-spring-{case}",
        "*NODE","1,0.,0.,0.","2,1.,0.,0.",
        "*NSET,NSET=FIXED","1",
        "*NSET,NSET=LOADED","2",
        "*ELEMENT,TYPE=SPRING2,ELSET=LINK","1,1,2",
        "*SPRING,ELSET=LINK","3,3",f"{K:.8f}",
        "*BOUNDARY","1,1,3,0.","2,1,2,0.",
        "*STEP","*STATIC","0.1,1.,0.00001,0.1",
        "*CLOAD",f"2,3,{P:.8f}",
    ]
    if case=="loaded_spc":
        lines.append(f"1,3,{SUPPORT_LOAD[case]:.8f}")
    lines += [
        "*NODE PRINT,NSET=FIXED","U,RF",
        "*NODE PRINT,NSET=LOADED","U,RF",
        # Diagnostic probe: S for a SPRING2 element may be unsupported.
        # Neither presence nor absence may be promoted to verified spring force.
        "*EL PRINT,ELSET=LINK","S",
        "*END STEP"
    ]
    out="\n".join(lines)+"\n"
    if (out.count("*ELEMENT,TYPE=SPRING2,ELSET=LINK")!=1
        or out.count("*CLOAD")!=1 or out.count("*NODE PRINT")!=2
        or "*EQUATION" in out or "*RIGID BODY" in out
        or "SPRING1" in out or "NLGEOM" in out or "*PLASTIC" in out):
        raise ValueError("STAGE68_ISOLATION_DECK_INVALID")
    return out

def generate(folder:Path,case:str)->None:
    folder=Path(folder)
    if case not in CASES or folder.exists() or folder.is_symlink():
        raise ValueError("STAGE68_FRESH_WORKSPACE_REQUIRED")
    folder.mkdir(parents=True)
    (folder/"panel.inp").write_text(deck(case),encoding="utf-8")

def field(dat:Path,kind:str,set_name:str)->dict[int,tuple[float,float,float]]:
    if kind not in ("displacements","forces") or set_name not in ("FIXED","LOADED"):
        raise ValueError("STAGE68_UNAPPROVED_FIELD_QUERY")
    s=dat.read_text(encoding="utf-8",errors="replace")
    header=re.compile(
        r"(?im)^\s*"+kind+r"\s+\([^\n]*\)\s+for set\s+"+set_name+
        r"\s+and time\s+("+NUMBER+r")\s*$")
    matches=list(header.finditer(s))
    if not matches or abs(float(matches[-1].group(1))-1.)>1e-7:
        raise ValueError("STAGE68_FINAL_FIELD_NOT_FOUND:"+kind+":"+set_name)
    rows={}
    for line in s[matches[-1].end():].splitlines():
        if not line.strip():
            if rows: break
            continue
        found=VALUE_LINE.fullmatch(line)
        if found is None:
            if rows: break
            continue
        node=int(found.group(1))
        vector=tuple(float(found.group(j)) for j in (2,3,4))
        if node in rows or not all(map(math.isfinite,vector)):
            raise ValueError("STAGE68_DUPLICATE_OR_NONFINITE_FIELD")
        rows[node]=vector
    if not rows: raise ValueError("STAGE68_EMPTY_FIELD:"+kind+":"+set_name)
    return rows

def _near(a:float,b:float,abs_tol:float=2e-5,rel_tol:float=.003):
    return math.isfinite(a) and abs(a-b)<=max(abs_tol,rel_tol*abs(b))

def inspect(folder:Path,case:str)->dict:
    if case not in CASES:raise ValueError("STAGE68_CASE_OUTSIDE_SCOPE")
    root=Path(folder)
    files={ext:root/("panel."+ext) for ext in ("inp","dat","sta","frd")}
    for ext,f in files.items():
        limit=64000000 if ext=="frd" else 10000000
        if f.is_symlink() or not f.is_file() or not 0<f.stat().st_size<=limit:
            raise ValueError("STAGE68_REQUIRED_OUTPUT_MISSING:"+ext)
    if files["inp"].read_bytes()!=deck(case).encode("utf-8"):
        raise ValueError("STAGE68_DECK_PROVENANCE_MISMATCH")
    _completed(files["sta"])
    uz1=field(files["dat"],"displacements","FIXED")
    uz2=field(files["dat"],"displacements","LOADED")
    rf1=field(files["dat"],"forces","FIXED")
    rf2=field(files["dat"],"forces","LOADED")
    if set(uz1)!= {FIXED_NODE} or set(uz2)!={FLOATING_NODE} or set(rf1)!={FIXED_NODE} or set(rf2)!={FLOATING_NODE}:
        raise ValueError("STAGE68_NODE_COVERAGE_MISMATCH")
    support_uz=uz1[FIXED_NODE][2]
    loaded_uz=uz2[FLOATING_NODE][2]
    fixed_rf=rf1[FIXED_NODE][2]
    loaded_rf=rf2[FLOATING_NODE][2]
    if not _near(support_uz,0.,1e-9,0.):
        raise ValueError("STAGE68_SPC_DISPLACEMENT_INVALID")
    if not _near(loaded_uz,EXPECTED_U2,2e-5,.003):
        raise ValueError("STAGE68_DISPLACEMENT_ORACLE_MISMATCH")
    # The observed CCX RF at an SPC includes external nodal loads. With the
    # pure clean SPC and no direct *CLOAD there, it can be interpreted narrowly
    # as mechanical support reaction. This is NOT a native spring element force.
    if not _near(fixed_rf,-P) or not _near(loaded_rf,P):
        raise ValueError("STAGE68_OBSERVED_RF_RESULTANT_MISMATCH")
    # The fixed RF reported by CCX does not change when a CLOAD is added
    # directly at this SPC in this specific input. Do not infer an unseen
    # reaction by subtracting that CLOAD: no independent observation supports it.
    if not _near(fixed_rf,-P):
        raise ValueError("STAGE68_FIXED_NODE_RF_NOT_STABLE")
    data=files["dat"].read_text(encoding="utf-8",errors="replace")
    native_s_print_observed=bool(re.search(
        r"(?im)^\s*stresses\b[^\n]*\bfor set LINK\b",data))
    return {
        "case":case,
        "unit_system":"N_mm",
        "analytic_displacement_mm":EXPECTED_U2,
        "observed_uz2_mm":loaded_uz,
        "observed_uz1_mm":support_uz,
        "derived_spring_k_delta_u_n":K*(loaded_uz-support_uz),
        "observed_fixed_rf3_n":fixed_rf,
        "observed_loaded_rf3_n":loaded_rf,
        "external_load_at_fixed_node_n":SUPPORT_LOAD[case],
        "fixed_rf_stable_with_direct_spc_load":True,
        "fixed_spc_applied_external_load_n":SUPPORT_LOAD[case],
        "pure_reaction_in_loaded_spc":"NOT_DERIVED_FROM_RF_ALONE",
        "fixed_rf_includes_applied_spc_cload":"NOT_OBSERVED_IN_THIS_CASE",
        "clean_spc_reaction_interpretation":"BOUNDED_NO_DIRECT_LOAD",
        "spring_element_stress_key_observation":{
            "key":"S","requested":True,"stress_label_present_in_dat":native_s_print_observed,
            "spring_element_force_validated":"NO"
        },
        "mpc_transmission":"NOT_MODELED",
        "independent_spring_element_force":"NOT_ADMITTED",
        "S8R_connector_force":"NOT_ADMITTED",
        "six_component_balance":"NOT_ADMITTED",
        "engineering_capacity":"NOT_ADMITTED",
        "artifact_sha256":{ext:hashlib.sha256(f.read_bytes()).hexdigest() for ext,f in files.items()}
    }

def crosscheck(cases:dict)->dict:
    if set(cases)!=set(CASES):raise ValueError("STAGE68_CASE_COVERAGE_MISMATCH")
    a,b=(cases[c] for c in CASES)
    if not (_near(a["observed_fixed_rf3_n"],b["observed_fixed_rf3_n"])
            and _near(a["observed_loaded_rf3_n"],b["observed_loaded_rf3_n"])
            and _near(a["observed_uz2_mm"],b["observed_uz2_mm"])
            and _near(b["fixed_spc_applied_external_load_n"]-
                      a["fixed_spc_applied_external_load_n"],
                      SUPPORT_LOAD["loaded_spc"])):
        raise ValueError("STAGE68_FIXED_LOAD_CONTAMINATION_IDENTITY_FAILED")
    return {"cases":cases,"independent_evidence_scope":"NO_DIRECT_CLOAD_CLEAN_SPC_RF_VS_ANALYTIC_FORCE_ONLY",
            "solver_RF_at_loaded_node":"OBSERVED_INTERNAL_RESULTANT_NOT_SUPPORT_REACTION",
            "RF_INCLUDES_DIRECT_SPC_CLOAD":"NOT_OBSERVED_IN_THIS_BOUNDED_CASE",
            "spring_element_force":"NOT_ADMITTED_NATIVE_ELEMENT_OUTPUT_UNVERIFIED",
            "mpc_reaction":"NOT_ADMITTED_NOT_TESTED",
            "S8R_shell_application":"NOT_ADMITTED",
            "general_six_component_balance":"NOT_ADMITTED",
            "design_capacity":"NOT_ADMITTED"}

if __name__=="__main__":
    if len(sys.argv)==4 and sys.argv[1]=="--generate":
        generate(Path(sys.argv[2]),sys.argv[3])
        print("STAGE68_DECK_GENERATED_NO_SOLVER")
    elif len(sys.argv)==2:
        root=Path(sys.argv[1])
        x=crosscheck({c:inspect(root/("rf_observe_"+c),c) for c in CASES})
        print(json.dumps(x,sort_keys=True,allow_nan=False))
        print("STAGE68_CLEAN_SPC_RF_SCREEN_PASS; NO_NATIVE_SPRING_FORCE_OR_CAPACITY")
    else:
        raise SystemExit("USAGE: check_spring_rf_observation.py ROOT | --generate DIR CASE")
