"""Independent final deformed Z-envelope witness for C3D8 clearance controls.

Bounded to an exact-deck-validated, same-run clearance observation JSON. A
strictly positive min(rib Z) - max(plate Z) is sufficient for disjoint C3D8
solid volumes because their trilinear element shape functions are nonnegative
within the parent domain. This says nothing about S8R/MPC contact reactions.
"""
from __future__ import annotations
import hashlib
import json
import math
import sys
from pathlib import Path

MESHES = (8, 16)
SCOPE = "SYNTHETIC_C3D8_CLEARANCE_FINAL_DEFORMED_VERTICAL_ENVELOPE"
SOURCE_SCOPE = "SYNTHETIC_C3D8_INITIAL_CLEARANCE_NO_ACTIVE_CONTACT_CONTROL"


def safe_file(path: Path, maximum: int) -> bytes:
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size < maximum:
        raise ValueError("C3D8_GAP_MISSING_OR_INVALID_FILE")
    return path.read_bytes()


def geometry(raw: bytes):
    nodes, solids, seen_eids = {}, {"PLATE": set(), "RIB": set()}, set()
    section = None
    for line in raw.decode("ascii").splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("*"):
            if line == "*NODE":
                section = "NODE"
            elif line in ("*ELEMENT,TYPE=C3D8,ELSET=PLATE", "*ELEMENT,TYPE=C3D8,ELSET=RIB"):
                section = line.rsplit("=", 1)[1]
            else:
                section = None
            continue
        fields = line.split(",")
        if section == "NODE":
            if len(fields) != 4:
                raise ValueError("C3D8_GAP_INVALID_NODE")
            node_id = int(fields[0]); xyz = tuple(map(float, fields[1:]))
            if node_id <= 0 or node_id in nodes or not all(map(math.isfinite, xyz)):
                raise ValueError("C3D8_GAP_INVALID_NODE")
            nodes[node_id] = xyz
        elif section in solids:
            if len(fields) != 9:
                raise ValueError("C3D8_GAP_INVALID_ELEMENT")
            eid, *conn = map(int, fields)
            if eid <= 0 or eid in seen_eids or len(set(conn)) != 8:
                raise ValueError("C3D8_GAP_INVALID_ELEMENT")
            seen_eids.add(eid)
            solids[section].update(conn)
    plate, rib = solids["PLATE"], solids["RIB"]
    if not plate or not rib or plate & rib or plate | rib != set(nodes):
        raise ValueError("C3D8_GAP_INVALID_BODY_PARTITION")
    return nodes, plate, rib


def final_displacement(raw: bytes, expected_nodes: set[int]):
    lines = raw.decode("ascii").splitlines()
    indexes = [i for i, line in enumerate(lines) if line.strip().startswith("-4  DISP")]
    if not indexes:
        raise ValueError("C3D8_GAP_MISSING_DISPLACEMENT")
    i = indexes[-1]
    stamp = lines[i-1].split() if i else []
    if len(stamp) < 3 or stamp[0] != "100CL":
        raise ValueError("C3D8_GAP_INVALID_FINAL_TIME")
    try:
        t = float(stamp[2])
    except ValueError as e:
        raise ValueError("C3D8_GAP_INVALID_FINAL_TIME") from e
    if not math.isfinite(t) or abs(t - 1.) > 1e-7:
        raise ValueError("C3D8_GAP_INVALID_FINAL_TIME")
    displacement = {}
    ended = False
    for line in lines[i+1:]:
        mark = line[:3].strip()
        if mark == "-3":
            ended = True
            break
        if mark == "-5":
            continue
        if mark != "-1":
            raise ValueError("C3D8_GAP_MALFORMED_FRD")
        try:
            node_id = int(line[3:13])
            xyz = tuple(float(line[13+12*q:25+12*q]) for q in range(3))
        except ValueError as e:
            raise ValueError("C3D8_GAP_MALFORMED_FRD") from e
        if node_id in displacement or not all(map(math.isfinite, xyz)):
            raise ValueError("C3D8_GAP_DUPLICATE_OR_NONFINITE_DISPLACEMENT")
        displacement[node_id] = xyz
    if not ended or set(displacement) != expected_nodes:
        raise ValueError("C3D8_GAP_NODE_COVERAGE")
    return displacement


def observe(root):
    root = Path(root)
    j = json.loads(safe_file(root/"u_c3d8_clearance_observations.json", 1000000))
    if (j.get("scope") != SOURCE_SCOPE or
        j.get("engineering_acceptance") != "NOT_ADMITTED" or
        set(j.get("cases", {})) != {str(n) for n in MESHES}):
        raise ValueError("C3D8_GAP_INVALID_SOURCE_SCOPE")
    out = {}
    for n in MESHES:
        record = j["cases"][str(n)]
        if (record.get("contact_separation") != "INACTIVE_CONTACT_OBSERVED_FOR_CLEARANCE_CONTROL" or
            record.get("engineering_acceptance") != "NOT_ADMITTED" or
            record.get("raw_rf3_balance_state") != "OBSERVED_WITHIN_BOUNDED_TOLERANCE"):
            raise ValueError("C3D8_GAP_INVALID_SOURCE_STATUS")
        folder = root/f"u_c3d8_control_n{n}_clearance"
        inp = safe_file(folder/"panel.inp", 10000000)
        frd = safe_file(folder/"panel.frd", 64000000)
        for ext, data in (("inp", inp), ("frd", frd)):
            if hashlib.sha256(data).hexdigest() != record["sha256"][ext]:
                raise ValueError("C3D8_GAP_PROVENANCE_MISMATCH")
        nodes, plate, rib = geometry(inp)
        delta = final_displacement(frd, set(nodes))
        max_plate_z = max(nodes[k][2] + delta[k][2] for k in plate)
        min_rib_z = min(nodes[k][2] + delta[k][2] for k in rib)
        gap = min_rib_z - max_plate_z
        if not math.isfinite(gap) or gap <= 0:
            raise ValueError("C3D8_GAP_NOT_POSITIVE")
        out[str(n)] = {"final_global_vertical_separation_lower_bound_mm": gap,
                       "deformed_plate_max_z_mm": max_plate_z,
                       "deformed_rib_min_z_mm": min_rib_z,
                       "node_count": len(nodes),
                       "provenance_sha256": {"inp": record["sha256"]["inp"],
                                             "frd": record["sha256"]["frd"]},
                       "geometric_observation": "STRICT_POSITIVE_GLOBAL_Z_ENVELOPE_GAP"}
    return {"scope": SCOPE, "cases": out,
            "interpretation": "DISJOINT_C3D8_DEFORMED_SOLID_Z_ENVELOPES_ONLY",
            "contact_print": "NOT_USED_TO_COMPUTE_GEOMETRIC_GAP",
            "s8r_mpc_reaction_oracle": "NOT_ESTABLISHED",
            "engineering_acceptance": "NOT_ADMITTED"}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: ROOT")
    print(json.dumps(observe(sys.argv[1]), sort_keys=True, allow_nan=False))
