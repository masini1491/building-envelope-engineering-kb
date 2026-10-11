"""Opt-in parameterized aluminum shell research, not member strength design."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from run_synthetic_panel import (_digest_file,_completed_step,SyntheticPanelEvidenceError,
                                 probe_calculix)
from generate import build
from aluminum_research_input import load
from check_reconstructed_pressure_balance import reconcile
from check_expanded_moment_partition import observe_case
from aluminum_result_summary import summarize

def run(*,input_json:Path,workspace:Path,executable:str,execute:bool=False)->dict:
    config=load(input_json)
    if not execute:
        return {"execution_status":"NOT_EXECUTED_OPT_IN_REQUIRED",
                "engineering_acceptance":"NOT_ADMITTED"}
    if workspace.is_symlink() or not workspace.is_dir() or any(workspace.iterdir()):
        raise ValueError("WORKSPACE_MUST_BE_EXISTING_EMPTY_DIRECTORY")
    build("aluminum",config["mesh"],"large",workspace,research=config)
    inp=workspace/"panel.inp"
    before=_digest_file(inp,5_000_000)
    solver=_digest_file(Path(executable),250_000_000)
    result=probe_calculix(executable=executable,job_name="panel",
                          workspace=workspace,timeout_seconds=120,execute=True)
    if result.execution_status!="PROCESS_EXIT_ZERO_UNVERIFIED":
        raise SyntheticPanelEvidenceError("SOLVER_PROCESS_FAILED:"+result.execution_status)
    if _digest_file(inp,5_000_000)!=before or _digest_file(Path(executable),250_000_000)!=solver:
        raise SyntheticPanelEvidenceError("INPUT_OR_SOLVER_CHANGED")
    frd=workspace/"panel.frd";dat=workspace/"panel.dat";sta=workspace/"panel.sta"
    for p,limit in ((frd,64_000_000),(dat,10_000_000),(sta,2_000_000)):
        if p.is_symlink():raise SyntheticPanelEvidenceError("SYMLINK_RESULT_REJECTED")
        _digest_file(p,limit)
    _completed_step(sta)
    try:
        balance=reconcile(inp,frd,dat,"aluminum")
        partition=observe_case(inp,frd,dat,"aluminum")
    except (ValueError,OSError) as exc:
        raise SyntheticPanelEvidenceError("RESEARCH_AUDIT_REJECTED:"+type(exc).__name__) from exc
    summary=summarize(deck=inp,dat=dat,inputs=config,translational_balance=balance)
    return {"execution_status":"ALUMINUM_PARAMETRIC_RESEARCH_EVIDENCE_PASS",
            "model_scope":"RECTANGULAR_FOUR_EDGE_CLAMPED_LINEAR_ELASTIC_S8R_NLGEOM_P1",
            "inputs":config,"translational_balance":balance,
            "research_observations":summary,
            "expanded_moment_partition":partition,
            "artifact_provenance":{"input_sha256":before,"solver_sha256":solver,
               "dat_sha256":_digest_file(dat,10_000_000),
               "frd_sha256":_digest_file(frd,64_000_000),
               "sta_sha256":_digest_file(sta,2_000_000)},
            "engineering_acceptance":"NOT_ADMITTED",
            "global_six_component_balance":"NOT_ADMITTED",
            "aluminum_design_manual_capacity":"NOT_COMPUTED",
            "rotational_support_reaction":"UNOBSERVED"}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--workspace",type=Path,required=True)
    parser.add_argument("--ccx",required=True)
    parser.add_argument("--execute",action="store_true")
    a=parser.parse_args()
    try:print(json.dumps(run(input_json=a.input,workspace=a.workspace,executable=a.ccx,execute=a.execute),allow_nan=False))
    except (OSError,ValueError) as exc:
        print(json.dumps({"execution_status":"EVIDENCE_REJECTED","reason":str(exc)[:180],
                          "engineering_acceptance":"NOT_ADMITTED"}))
        return 2
    return 0

if __name__=="__main__":raise SystemExit(main())
