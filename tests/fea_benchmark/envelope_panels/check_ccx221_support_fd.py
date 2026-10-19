"""Independent read-only scrutiny of pinned CCX 2.21 support-perturbation outputs.

This checks the *printed* center, plate-edge, contact and raw-rib F3 identity,
as well as 18 source-pinned solution traces. It does NOT admit S8R support
reactions, contact laws, shell rotations, or engineering six-component balance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re


DEFAULT_MANIFEST_SHA256 = "f9d52a1b0f0063527e7596d3766a2a2da08ad2424d63837692dabe8c318a028b"
GROUP = {"plate": "PLATE_EDGE_RF", "rib": "RIB_END_RF"}
PRINT_SETS = ("CENTER_RF", "PLATE_EDGE_RF", "RIB_END_RF", "ALL_ORIGINAL_RF")
ENERGY_SETS = ("PLATE", "RIB")
NUM = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?"


def fail(code: str) -> None:
    raise ValueError("KB_SUPPORT_FD_" + code)


def finite(s: str) -> float:
    try:
        x = float(s.replace("D", "E").replace("d", "e"))
    except ValueError:
        fail("MALFORMED_NUMBER")
    if not math.isfinite(x):
        fail("NONFINITE")
    return x


def one_block(dat: str, header: str) -> str:
    # Terminal time == 1; require unambiguous final section; no wandering
    # forward to a later numerical value when the requested block is malformed.
    # CCX prints element energy "... and time" but CELS "... for time".
    time_connector = " for time" if header == "total contact spring energy" else " and time"
    matches = list(re.finditer(r"(?m)^\s*" + re.escape(header)
                               + re.escape(time_connector) + r"\s+(" + NUM + r")\s*$", dat))
    if not matches:
        fail("MISSING_BLOCK")
    match = matches[-1]
    if abs(finite(match.group(1)) - 1.0) > 1e-8:
        fail("FINAL_TIME")
    tail = dat[match.end():]
    blocks = re.match(r"\s*\n((?:[^\n]*\n)*?)\s*\n", tail)
    if blocks is None:
        fail("BLOCK_TERMINATOR")
    records = [row.strip() for row in blocks.group(1).splitlines() if row.strip()]
    if not records:
        fail("EMPTY_BLOCK")
    return "\n".join(records)


def scalar(dat: str, label: str) -> float:
    records = one_block(dat, label).splitlines()
    if len(records) != 1 or len(records[0].split()) != 1:
        fail("SCALAR_ROWS")
    return finite(records[0])


def node_vectors(dat: str, kind: str, group: str) -> dict[int, tuple[float, float, float]]:
    records = one_block(dat, f"{kind} (fx,fy,fz) for set {group}").splitlines() if kind=="forces" else one_block(dat, f"{kind} (vx,vy,vz) for set {group}").splitlines()
    output = {}
    for row in records:
        data = row.split()
        if len(data) != 4:
            fail("VECTOR_FORMAT")
        try: node = int(data[0])
        except ValueError: fail("VECTOR_NODE")
        if node < 1 or node in output:
            fail("VECTOR_DUPLICATE")
        output[node] = tuple(finite(s) for s in data[1:])
    return output


def surface_f3(dat: str) -> float:
    header = "total surface force (fx,fy,fz) and moment about the origin (mx,my,mz)"
    records = [m for m in re.finditer(re.escape(header) + r"\s*\n\s*\n\s*([^\n]+)", dat)]
    if not records:
        fail("CONTACT_FORCE_MISSING")
    vals = records[-1].group(1).split()
    if len(vals) != 6:
        fail("CONTACT_FORCE_FORMAT")
    return finite(vals[2])


def contact_elements(dat: str) -> set[int]:
    block = one_block(dat, "contact spring energy (slave element+face,energy) for all contact elements")
    ids = set()
    for row in block.splitlines():
        v = row.split()
        if len(v) != 3:
            fail("CONTACT_ELEMENTS_FORMAT")
        try: k = int(v[0]); flag = int(v[1])
        except ValueError: fail("CONTACT_ELEMENTS_ID")
        if k <= 0 or flag < 0:
            fail("CONTACT_ELEMENTS_RANGE")
        finite(v[2])
        ids.add(k)
    return ids


def nset(deck: str, name: str) -> set[int]:
    m = re.search(r"(?m)^\*NSET,NSET=" + re.escape(name) + r"\s*\n([^*]+)", deck)
    if m is None:
        fail("NSET_MISSING")
    ids = {int(s) for s in re.findall(r"\d+", m.group(1))}
    if not ids:
        fail("NSET_EMPTY")
    return ids


def input_claim(deck: str, group: str, delta: float) -> None:
    if deck.count("CENTER_RF,3,3,0.02000000\n") != 1:
        fail("CENTER_BOUNDARY")
    if re.search(r"(?mi)^\*(?:CLOAD|DLOAD)\b", deck):
        fail("EXTRA_APPLIED_LOAD")
    if group == "base":
        if re.search(r"(?m)^(?:PLATE_EDGE_RF|RIB_END_RF),3,3,[^\n]*$", deck):
            fail("BASE_HAS_PERTURBATION")
    else:
        expected = f"{GROUP[group]},3,3,{delta:.8f}\n"
        if deck.count(expected) != 1:
            fail("WRONG_PERTURBATION")
        alternate = GROUP["rib" if group=="plate" else "plate"]
        if re.search(r"(?m)^" + alternate + r",3,3,", deck):
            fail("OTHER_SUPPORT_PERTURBED")


def final_sta(sta: str) -> None:
    rows = re.findall(r"(?m)^\s*1\s+(\d+)\s+\d+\s+\d+\s+([-\d.E+]+)\s+([-\d.E+]+)", sta)
    if not rows or int(rows[-1][0]) != 10:
        fail("STA_INCOMPLETE")
    if abs(finite(rows[-1][1])-1.0)>1e-8 or abs(finite(rows[-1][2])-1.0)>1e-8:
        fail("STA_FINAL_TIME")


def load_case(root: Path, key: str, info: dict) -> dict:
    folder=root/"support-energy"/key
    deck_bytes=(folder/"panel.inp").read_bytes()
    sha=hashlib.sha256(deck_bytes).hexdigest()
    if sha != info["input_sha256"]:
        fail("INPUT_SHA256")
    deck=deck_bytes.decode("ascii")
    input_claim(deck,info["group"],float(info["delta_z_mm"]))
    dat=(folder/"panel.dat").read_text(encoding="latin-1")
    final_sta((folder/"panel.sta").read_text(encoding="ascii"))
    sets={s:nset(deck,s) for s in PRINT_SETS}
    if any(sets[a]&sets[b] for a,b in (("CENTER_RF","PLATE_EDGE_RF"),
                                         ("CENTER_RF","RIB_END_RF"),
                                         ("PLATE_EDGE_RF","RIB_END_RF"))):
        fail("SUPPORT_SETS_OVERLAP")
    forces={s:node_vectors(dat,"forces",s) for s in PRINT_SETS}
    displacements={s:node_vectors(dat,"displacements",s) for s in PRINT_SETS[:3]}
    for s in PRINT_SETS:
        if set(forces[s])!=sets[s]:
            fail("FORCE_NODE_COVERAGE")
    for s in PRINT_SETS[:3]:
        if set(displacements[s])!=sets[s]:
            fail("DISPLACEMENT_NODE_COVERAGE")
        prescribed=(0.02 if s=="CENTER_RF" else
                    (float(info["delta_z_mm"]) if s==GROUP.get(info["group"]) else 0.0))
        if any(abs(v[2]-prescribed)>1e-7 for v in displacements[s].values()):
            fail("DISPLACEMENT_MISMATCH")
    energies={s:scalar(dat,f"total internal energy for set {s}") for s in ENERGY_SETS}
    energies["CELS"]=scalar(dat,"total contact spring energy")
    energies["candidate_sum"]=math.fsum(energies.values())
    rf={s:math.fsum(v[2] for v in forces[s].values()) for s in PRINT_SETS}
    return {"energy":energies,"rf_f3_n":rf,"contact_surface_f3_n":surface_f3(dat),
            "contact_element_ids":contact_elements(dat),"mesh":info["mesh"],
            "group":info["group"],"delta_z_mm":float(info["delta_z_mm"])}


def analyze(root: Path, expected_manifest_sha256: str = DEFAULT_MANIFEST_SHA256) -> dict:
    raw=(root/"support-energy"/"manifest.json").read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected_manifest_sha256:
        fail("MANIFEST_SHA256")
    manifest=json.loads(raw)
    cases=manifest["cases"]
    wanted={f"n{mesh}/base" for mesh in (8,16)}
    wanted|={f"n{mesh}/{group}/{label}" for mesh in (8,16)
             for group in GROUP for label in ("minus1","minus2","plus1","plus2")}
    if set(cases)!=wanted:
        fail("CASE_COVERAGE")
    rows={key:load_case(root,key,info) for key,info in sorted(cases.items())}
    output={}
    for mesh in (8,16):
        prefix=f"n{mesh}"
        base=rows[f"{prefix}/base"]
        rf=base["rf_f3_n"]; contact=base["contact_surface_f3_n"]
        base_balance=math.fsum([rf["CENTER_RF"],rf["PLATE_EDGE_RF"],-contact])
        raw_balance=rf["ALL_ORIGINAL_RF"]
        printed_sum=math.fsum([rf["CENTER_RF"],rf["PLATE_EDGE_RF"],rf["RIB_END_RF"]])
        if abs(base_balance)>1e-4 or abs(printed_sum-raw_balance)>1e-4:
            fail("BASE_PRINTED_FORCE_IDENTITY")
        if abs(raw_balance)<1:
            fail("RAW_RF_GATE_MUST_REMAIN_FAIL_CLOSED")
        meshout={"base":{ "center_rf3_n":rf["CENTER_RF"],
                  "plate_edge_raw_rf3_n":rf["PLATE_EDGE_RF"],
                  "rib_end_raw_rf3_n":rf["RIB_END_RF"],
                  "contact_surface_f3_n":contact,
                  "rib_end_force_from_contact_fbd_n":-contact,
                  "fbd_f3_residual_n":base_balance,
                  "raw_original_rf3_sum_n":raw_balance,
                  "raw_rib_minus_contact_fbd_n":rf["RIB_END_RF"]+contact,
                  "contact_elements":len(base["contact_element_ids"])},
                 "perturbations":{}}
        for group in GROUP:
            grp={}
            E0=base["energy"]["candidate_sum"]
            for sign in ("minus","plus"):
                arr=[]
                for k in (1,2):
                    v=rows[f"{prefix}/{group}/{sign}{k}"]
                    h=(1 if sign=="plus" else -1)*k*0.0001
                    force=(v["energy"]["candidate_sum"]-E0)/h
                    arr.append({"delta_z_mm":h,"candidate_energy_slope_n":force,
                                "contact_surface_f3_n":v["contact_surface_f3_n"],
                                "contact_f3_change_n":v["contact_surface_f3_n"]-contact,
                                "contact_elements":len(v["contact_element_ids"])})
                grp[sign]=arr
            grp["centered_derivative_at_h_0p0001_n"]=(rows[f"{prefix}/{group}/plus1"]["energy"]["candidate_sum"]-rows[f"{prefix}/{group}/minus1"]["energy"]["candidate_sum"])/0.0002
            grp["centered_derivative_at_h_0p0002_n"]=(rows[f"{prefix}/{group}/plus2"]["energy"]["candidate_sum"]-rows[f"{prefix}/{group}/minus2"]["energy"]["candidate_sum"])/0.0004
            grp["branch_asymmetry_relevant"]=(
                any(abs(x["contact_f3_change_n"])>0.1*abs(contact) for x in grp["plus"]+grp["minus"]))
            meshout["perturbations"][group]=grp
        output[f"n{mesh}"]=meshout
    return {"scope":"EXACT_PINNED_CCX221_SUPPORT_FD_OBSERVATION",
            "artifact_manifest_sha256":expected_manifest_sha256,
            "case_count":len(rows),"meshes":output,
            "contact_print_is_not_external_independent_solver_oracle":True,
            "candidate_energy_is_not_admitted_total_potential_energy":True,
            "six_component_force_moment_admission":"NOT_ESTABLISHED",
            "raw_rf3_original_gate":"FAIL_CLOSED",
            "engineering_acceptance":"NOT_ADMITTED"}


if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("artifact_extracted_root", type=Path)
    ap.add_argument("--manifest-sha256",default=DEFAULT_MANIFEST_SHA256)
    args=ap.parse_args()
    print(json.dumps(analyze(args.artifact_extracted_root,args.manifest_sha256),
                     sort_keys=True,indent=2,allow_nan=False))
