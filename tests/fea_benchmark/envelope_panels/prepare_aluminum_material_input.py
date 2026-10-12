"""Opt-in CS Aluminum alloy/temper selector for *explicit* linear research inputs.

Does not contain a property database, infer E/nu, load private source files,
or approve a material card. Emits the unchanged Stage 37 research input schema.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from aluminum_research_input import _KEYS, validate
from check_aluminum_material_evidence import read_metadata, check

_ALLOWED_ALLOYS = frozenset(("3003-H14", "3004-H12", "3004-O"))
_FIELDS = (_KEYS - {"material_provenance"}) | {
    "alloy_temper", "manufacturer", "property_evidence_status"
}
_EVIDENCE = "USER_DECLARED_UNVERIFIED"
_MANUFACTURER = "CS Aluminum"


def prepare(selection: dict) -> dict:
    """Validate exact selection; never fill any value from a grade or maker."""
    if not isinstance(selection, dict) or set(selection) != _FIELDS:
        raise ValueError("MATERIAL_SELECTION_SCHEMA_MISMATCH")
    grade = selection["alloy_temper"]
    if (type(grade) is not str or grade not in _ALLOWED_ALLOYS
            or selection["manufacturer"] != _MANUFACTURER
            or selection["property_evidence_status"] != _EVIDENCE):
        raise ValueError("MATERIAL_SELECTION_NOT_ADMITTED")
    core = {k: selection[k] for k in _KEYS if k != "material_provenance"}
    core["material_provenance"] = (
        f"USER_DECLARED_UNVERIFIED:{_MANUFACTURER}:{grade}:"
        "ELASTIC_RESEARCH_ONLY:NO_AUTO_PROPERTIES"
    )
    return validate(core)


def read_selection(path: Path, evidence_path: Path | None = None) -> dict:
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= 4096:
        raise ValueError("MATERIAL_SELECTION_FILE_NOT_BOUNDED")

    def reject_constant(_value):
        raise ValueError("MATERIAL_SELECTION_NONFINITE_JSON")

    def reject_duplicate(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("MATERIAL_SELECTION_DUPLICATE_KEY")
            result[key] = value
        return result

    obj = json.loads(path.read_text(encoding="utf-8"),
                     parse_constant=reject_constant,
                     object_pairs_hook=reject_duplicate)
    if evidence_path is None:
        return prepare(obj)
    if not isinstance(obj, dict) or set(obj) != _FIELDS | {"product_id"}:
        raise ValueError("MATERIAL_SELECTION_PRODUCT_ID_REQUIRED")
    core = {k: v for k, v in obj.items() if k != "product_id"}
    prepared = prepare(core)
    check(obj, read_metadata(evidence_path))
    return prepared


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence", type=Path)
    args = parser.parse_args()
    result = read_selection(args.selection, args.evidence)
    # Never silently replace an existing input or use a caller-supplied deck.
    with args.output.open("x", encoding="utf-8") as out:
        json.dump(result, out, ensure_ascii=False, sort_keys=True, allow_nan=False)
        out.write("\n")
    state = "DECLARED_METADATA_CONSISTENCY_ONLY" if args.evidence else "UNVERIFIED"
    print(f"ALUMINUM_EXPLICIT_MATERIAL_SELECTION_PREPARED; {state}; "
          "NO SOLVER EXECUTION OR CAPACITY ADMISSION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
