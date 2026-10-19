"""Fail-closed observational replay of CCX 2.21 DOF5 contact branch.

Uses the existing full 20-case verifier, never admits rotational reactions.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from verify_ccx221_rot5 import observe as verify,finite

RUN_ID=39194487445
ARTIFACT_ID=12161706369
MANIFEST_SHA="d4af3bb7edbd06b5acba0343f07a8932281cd3221d35036daea31bdf6025fd9b"
HEADER=re.compile(r"(?m)^\s*statistics for slave set RIB_BASE_UNDERSIDE, master set PLATE_TOP and time\s+(\S+)\s*$")
FORCE="total surface force (fx,fy,fz) and moment about the origin (mx,my,mz)"

def fail(code):
    raise ValueError("CCX221_ROT_BRANCH_"+code)

def final_contact(dat:str)->tuple[float,...]:
    sections=list(HEADER.finditer(dat))
    records=[]
    for i,m in enumerate(sections):
        if abs(finite(m.group(1))-1.0)>1e-8:continue
        end=sections[i+1].start() if i+1<len(sections) else len(dat)
        block=dat[m.end():end]
        hits=list(re.finditer(r"(?m)^\s*"+re.escape(FORCE)+r"\s*\n\s*([^\n]+)",block))
        if len(hits)!=1:fail("FORCE_ROWS")
        fields=hits[0].group(1).split()
        if len(fields)!=6:fail("FORCE_DIMENSION")
        records.append(tuple(finite(x) for x in fields))
    if len(records)!=2:fail("FINAL_DUPLICATE_COVERAGE")
    if records[0]!=records[1]:fail("FINAL_DUPLICATE_DRIFT")
    return records[-1]

def replay(root:Path)->dict:
    manifest_bytes=(root/"manifest.json").read_bytes()
    if hashlib.sha256(manifest_bytes).hexdigest()!=MANIFEST_SHA:fail("MANIFEST_PIN")
    prior=verify(root)
    if prior["case_count"]!=20 or prior["engineering_acceptance"]!="NOT_ADMITTED":fail("PRIOR_GATE")
    samples=("minus2","minus1","zero","plus1","plus2")
    result={}
    for mesh in (8,16):
        name=f"n{mesh}/contact"
        force={}
        for sample in samples:
            dat=(root/name/sample/"panel.dat").read_text(encoding="latin-1")
            force[sample]=final_contact(dat)
        baseline=force["zero"][2]
        deriv=prior["results"][name]["derivatives"]
        result[f"n{mesh}"]={
            "contact_f3_by_angle_n":{k:force[k][2] for k in samples},
            "contact_f3_change_from_zero_n":{k:force[k][2]-baseline for k in samples},
            "paired_half_step_contact_f3_difference_n":{str(i):force[f"plus{i}"][2]-force[f"minus{i}"][2] for i in (1,2)},
            "candidate_central_slope_nmm":{h:v["central_nmm"] for h,v in deriv.items()},
            "candidate_central_slope_h2_minus_h1_nmm":deriv["2e-05"]["central_nmm"]-deriv["1e-05"]["central_nmm"],
            "contact_active_set_change_proven":False,
            "shell_rotational_reaction_admitted":False}
    no_contact={f"n{n}":{h:v["central_nmm"] for h,v in prior["results"][f"n{n}/no_contact"]["derivatives"].items()} for n in (8,16)}
    return {"status":"DOF5_CONTACT_BRANCH_OBSERVATION_ONLY",
            "provenance_run_id":RUN_ID,"artifact_id":ARTIFACT_ID,
            "manifest_sha256":MANIFEST_SHA,"case_count":20,
            "no_contact_central_slope_nmm":no_contact,
            "contact_cases":result,"contact_energy_additivity":"UNVERIFIED",
            "original_rf3_gate":"FAIL_CLOSED",
            "rotational_reaction_admission":"NOT_ESTABLISHED",
            "engineering_acceptance":"NOT_ADMITTED"}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("artifact_root",type=Path)
    args=p.parse_args()
    print(json.dumps(replay(args.artifact_root),sort_keys=True,indent=2,allow_nan=False))
