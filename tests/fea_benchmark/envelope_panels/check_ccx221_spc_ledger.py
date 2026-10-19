"""Check SPC trace completeness; does NOT certify support reactions or equilibrium.

Expected input: one ccx221_s8r_force_instrument.py kb_spc_ledger.tsv file.
Rotational constraints are enumerated, but have no 3D expanded-node force mapping.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path


def reject(code: str) -> None:
    raise ValueError("CCX221_SPC_" + code)


def number(s: str) -> float:
    try:
        value = float(s)
    except (ValueError, TypeError) as exc:
        raise ValueError("CCX221_SPC_BAD_NUMBER") from exc
    if not math.isfinite(value):
        reject("NONFINITE")
    return value


def positive(s: str) -> int:
    try:
        value = int(s)
    except (ValueError, TypeError) as exc:
        raise ValueError("CCX221_SPC_BAD_INTEGER") from exc
    if value <= 0:
        reject("BAD_ID")
    return value


def validate(text: str) -> dict:
    if len(text) > 12_000_000:
        reject("TOO_LARGE")
    frames: dict[str, dict] = {}
    current = None
    for row in text.splitlines():
        v = row.split()
        if not v:
            reject("EMPTY_ROW")
        kind = v[0]
        if kind == "KB_SPC_EVENT":
            if len(v) != 7 or v[1] not in {"P", "Q"} or v[1] in frames:
                reject("EVENT_FORMAT")
            phase = v[1]
            step, increment, t, nk, nboun = positive(v[2]), positive(v[3]), number(v[4]), positive(v[5]), positive(v[6])
            if step != 1 or abs(t - 1.0) > 1e-7:
                reject("EVENT_TIME")
            current = frames[phase] = {"step": step, "increment": increment, "time": t,
                                       "nk": nk, "nboun": nboun, "entries": {}}
            continue
        if current is None:
            reject("NO_EVENT")
        if kind == "KB_SPC_INVALID":
            reject("INVALID_NODE_OR_DIRECTION")
        if kind == "KB_SPC":
            if len(v) != 8 or v[1] not in frames or frames[v[1]] is not current:
                reject("TRANSLATION_FORMAT")
            idx,node,direction = positive(v[2]),positive(v[3]),positive(v[4])
            equation = int(v[5])
            prescribed,force = number(v[6]),number(v[7])
            if direction > 3 or node > current["nk"]:
                reject("TRANSLATION_RANGE")
            entry = (node,direction,equation,prescribed,force,"translation")
        elif kind == "KB_SPC_ROT_UNMAPPED":
            if len(v) != 5 or v[1] not in frames or frames[v[1]] is not current:
                reject("ROTATION_FORMAT")
            idx,node,direction = positive(v[2]),positive(v[3]),positive(v[4])
            if direction not in (4,5,6) or node > current["nk"]:
                reject("ROTATION_RANGE")
            entry = (node,direction,None,None,None,"unmapped_rotation")
        else:
            reject("UNKNOWN_RECORD")
        if idx > current["nboun"] or idx in current["entries"]:
            reject("DUPLICATE_OR_RANGE")
        current["entries"][idx] = entry
    if set(frames) != {"P","Q"}:
        reject("PHASE_COVERAGE")
    p,q = frames["P"],frames["Q"]
    if any(p[k] != q[k] for k in ("step","increment","time","nk","nboun")):
        reject("EVENT_MISMATCH")
    for frame in (p,q):
        if set(frame["entries"]) != set(range(1,frame["nboun"]+1)):
            reject("ENTRY_COVERAGE")
    for i in p["entries"]:
        a,b=p["entries"][i],q["entries"][i]
        if a[:4] != b[:4] or a[-1] != b[-1]:
            reject("PRE_POST_OWNER_MISMATCH")
    types=Counter(x[-1] for x in q["entries"].values())
    if types["translation"] == 0 or types["unmapped_rotation"] == 0:
        reject("OBSERVATION_COVERAGE")
    vertical=[e[4] for e in q["entries"].values() if e[-1]=="translation" and e[1]==3]
    return {"observation":"SPC_LEDGER_COMPLETE_NOT_REACTION_ORACLE",
            "expanded_nodes":q["nk"],"spc_count":q["nboun"],
            "translational_count":types["translation"],
            "unmapped_rotational_count":types["unmapped_rotation"],
            "post_mpc_spc_fn3_sum_n":math.fsum(vertical),
            "engineering_acceptance":"NOT_ADMITTED"}


if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("spc_ledger", type=Path)
    args=p.parse_args()
    print(json.dumps(validate(args.spc_ledger.read_text(encoding="ascii")),
                     sort_keys=True,allow_nan=False))
