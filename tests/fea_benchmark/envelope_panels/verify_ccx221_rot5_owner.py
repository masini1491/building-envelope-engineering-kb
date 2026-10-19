"""Verify original S8R DOF5 prescribed-angle ownership in CCX 2.21.

Pairs original 20-case source input with actual instrumented gen3dboun.f
output, checks exact binary-artifact lineage, node-wise val transfer and
axis/direction. This is a kinematic bookkeeping check, NOT a moment oracle.
"""
from __future__ import annotations
from collections import Counter
import hashlib
import json
import math
import re
import zipfile
from pathlib import Path

ORIG_SHA="d9b36c420feca6a5f8cd50dc8cb07dbba6c2ebbbf0224abb4df57fbfd2291a8b"
OWNER_SHA="01d03784c7fe0521087602262b36446127bad858ad90765170bc40c44c9d0361"
ORIG_MANIFEST_SHA="d4af3bb7edbd06b5acba0343f07a8932281cd3221d35036daea31bdf6025fd9b"
TRIALS=("minus1","zero","plus1")
def error(label):raise ValueError("CCX221_DOF5_OWNER_"+label)

def angles(deck: str) -> dict[int,float]:
    boundary=deck[deck.index("*STEP,"):]
    matches=re.findall(r"(?m)^(\d+),5,5,([-+]?[0-9.]+)$",boundary)
    if not matches:error("INPUT_ROT_MISSING")
    vals={}
    for sn,sv in matches:
        n=int(sn)
        if n in vals:error("INPUT_DUP")
        v=float(sv)
        if not math.isfinite(v):error("INPUT_NONFINITE")
        vals[n]=v
    return vals

def records(trace: str) -> list[dict]:
    result=[]
    for line in trace.splitlines():
        col=line.split()
        if len(col)!=9 or col[0]!="KB_ROT_OWNER":error("ROW_FORMAT")
        try:
            origin,axis,ordinal,spc,aux,direction,mpc=(
                int(col[1]),int(col[2]),int(col[3]),int(col[4]),
                int(col[5]),int(col[6]),int(col[8]))
            angle=float(col[7])
        except ValueError:error("ROW_VALUE")
        if not math.isfinite(angle):error("NONFINITE")
        if min(origin,axis,ordinal,spc,aux,direction,mpc)<1 or direction!=1 or ordinal not in (1,2):error("ROW_SCOPE")
        result.append({"node":origin,"axis":axis,"ordinal":ordinal,"spc":spc,
                       "aux_node":aux,"aux_dir":direction,"angle":angle,"mpc_count":mpc})
    if not result:error("NO_OWNER_ROWS")
    if len({x["spc"] for x in result})!=len(result):error("SPC_DUPLICATE")
    if len({(x["aux_node"],x["aux_dir"]) for x in result})!=len(result):error("AUX_DUPLICATE")
    return result

def verify(original_zip:Path, owner_zip:Path)->dict:
    raw1=original_zip.read_bytes();raw2=owner_zip.read_bytes()
    if hashlib.sha256(raw1).hexdigest()!=ORIG_SHA or hashlib.sha256(raw2).hexdigest()!=OWNER_SHA:error("ZIP_PROVENANCE")
    report={}
    with zipfile.ZipFile(original_zip) as o,zipfile.ZipFile(owner_zip) as k:
        manifestbytes=o.read("manifest.json")
        if hashlib.sha256(manifestbytes).hexdigest()!=ORIG_MANIFEST_SHA:error("MANIFEST_PIN")
        manifest=json.loads(manifestbytes)["cases"]
        for n in (8,16):
            for trial in TRIALS:
                key=f"n{n}/no_contact/{trial}"
                deck=o.read(key+"/panel.inp")
                if hashlib.sha256(deck).hexdigest()!=manifest[key]["input_sha256"]:error("DECK_SHA")
                cards=angles(deck.decode("ascii"))
                rs=records(k.read("rot-owner/"+key+"/kb_rot_owner.tsv").decode("ascii"))
                owned={r["node"]:r for r in rs if r["axis"]==2 and r["ordinal"]==2 and r["node"] in cards}
                if set(owned)!=set(cards):error("ROT_CARD_COVERAGE")
                for origin,requested in cards.items():
                    if abs(owned[origin]["angle"]-requested)>1e-13:error("ROT_ANGLE_TRANSFER")
                nnz=sum(v!=0. for v in cards.values())
                mpc=Counter(r["axis"] for r in rs)
                if n==8 and (len(cards),len(rs),nnz)!=(64,156,0 if trial=="zero" else 62):error("N8_OBSERVATION")
                if n==16 and (len(cards),len(rs),nnz)!=(96,220,0 if trial=="zero" else 94):error("N16_OBSERVATION")
                report[key]={"prescribed_dof5_nodes":len(cards),"nonzero_prescribed_angles":nnz,
                             "aux_spc_owner_rows":len(rs),"mapped_card_count":len(owned),
                             "mapped_rotation_axis":2,"all_angle_values_exact":True,
                             "all_auxiliary_spcs_direction":1,
                             "rot_owner_axis_histogram":dict(sorted(mpc.items()))}
    return {"status":"DOF5_VALUE_TO_AUX_SPC_OWNER_MATCH_ONLY",
            "source_zip_sha256":ORIG_SHA,"owner_zip_sha256":OWNER_SHA,
            "cases":report,"mpc_dual_reaction_moment":"NOT_ESTABLISHED",
            "virtual_work_equality":"NOT_ESTABLISHED",
            "six_component_balance":"NOT_ADMITTED",
            "engineering_acceptance":"NOT_ADMITTED"}

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("source_zip",type=Path);p.add_argument("owner_zip",type=Path)
    args=p.parse_args();print(json.dumps(verify(args.source_zip,args.owner_zip),sort_keys=True,indent=2))
