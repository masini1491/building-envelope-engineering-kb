"""Stage 36: same solver + same canonical synthetic deck across clean workspaces.

Requires exact machine-consumed numerical evidence, never strength admission.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

_HASH_FIELDS=("input_deck_sha256","solver_executable_sha256","final_dat_sha256",
              "final_frd_sha256","final_sta_sha256")


def load(path:Path)->dict:
    def reject_constant(value):
        raise ValueError("INVALID_JSON_NONFINITE")
    data=json.loads(path.read_text(encoding="utf-8"),parse_constant=reject_constant)
    if not isinstance(data,dict) or data.get("execution_status")!="SYNTHETIC_BENCHMARK_EVIDENCE_PASS":
        raise ValueError("REPLAY_REQUIRED_BOUNDED_SUCCESS")
    if (data.get("engineering_acceptance")!="NOT_ADMITTED" or
        data.get("six_component_global_balance")!="NOT_ADMITTED" or
        data.get("design_capacity")!="NOT_COMPUTED"):
        raise ValueError("REPLAY_ADMISSION_SCOPE_DRIFT")
    if data.get("material_proxy") not in ("glass","aluminum") or data.get("mesh") not in (4,8,16):
        raise ValueError("REPLAY_UNSUPPORTED_MODEL")
    identity=data.get("artifact_provenance")
    if not isinstance(identity,dict) or set(identity)!=set(_HASH_FIELDS):
        raise ValueError("REPLAY_INCOMPLETE_PROVENANCE")
    for name in _HASH_FIELDS:
        value=identity[name]
        if not isinstance(value,str) or len(value)!=64 or any(c not in "0123456789abcdef" for c in value):
            raise ValueError("REPLAY_INVALID_SHA256")
    for field in ("translational_balance","expanded_moment_partition"):
        if not isinstance(data.get(field),dict) or not data[field]:
            raise ValueError("REPLAY_MISSING_NUMERIC_AUDIT")
    return data


def compare(a:dict,b:dict)->dict:
    keys=("model_scope","material_proxy","mesh","translational_balance",
          "expanded_moment_partition")
    if any(a.get(k)!=b.get(k) for k in keys):
        raise ValueError("REPLAY_BOUNDED_NUMERIC_MISMATCH")
    for k in ("input_deck_sha256","solver_executable_sha256"):
        if a["artifact_provenance"][k]!=b["artifact_provenance"][k]:
            raise ValueError("REPLAY_INPUT_OR_SOLVER_IDENTITY_MISMATCH")
    return {"execution_status":"INDEPENDENT_WORKSPACE_SYNTHETIC_REPLAY_PASS",
            "material_proxy":a["material_proxy"],"mesh":a["mesh"],
            "input_deck_sha256":a["artifact_provenance"]["input_deck_sha256"],
            "solver_executable_sha256":a["artifact_provenance"]["solver_executable_sha256"],
            "output_byte_identity":"NOT_REQUIRED",
            "rotational_support_reaction":"UNOBSERVED",
            "engineering_acceptance":"NOT_ADMITTED"}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("baseline",type=Path)
    p.add_argument("replay",type=Path)
    args=p.parse_args()
    print(json.dumps(compare(load(args.baseline),load(args.replay)),sort_keys=True))


if __name__=="__main__":
    main()
