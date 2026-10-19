"""Fail-closed structure check for output-stage fn; NOT an SPC dual oracle."""
import json
import math
import pathlib
import sys

def check_trace(lines, expected_nk=None):
    i = 0
    blocks = []
    owners = None
    while i < len(lines):
        head = lines[i].split()
        if len(head) != 5 or head[0] != "KB_OUTPUT_FN_BEGIN":
            raise ValueError("OUTPUT_FN_BAD_BEGIN")
        try:
            step, inc, nk, mt = map(int, head[1:])
        except ValueError as exc:
            raise ValueError("OUTPUT_FN_BAD_HEADER") from exc
        if step != 1 or inc != len(blocks) + 1 or not (1 <= mt <= 10) or nk < 1:
            raise ValueError("OUTPUT_FN_BAD_INCREMENT")
        if expected_nk is not None and nk != expected_nk:
            raise ValueError("OUTPUT_FN_WRONG_NODE_COUNT")
        if blocks and (nk, mt) != (blocks[0][2], blocks[0][3]):
            raise ValueError("OUTPUT_FN_SHAPE_CHANGED")
        i += 1
        mapping = []
        for node in range(1, nk + 1):
            for dof in range(mt):
                if i >= len(lines):
                    raise ValueError("OUTPUT_FN_TRUNCATED")
                row = lines[i].split()
                if len(row) != 5 or row[0] != "KB_OUTPUT_FN":
                    raise ValueError("OUTPUT_FN_BAD_ROW")
                try:
                    n, d, eq = int(row[1]), int(row[2]), int(row[4])
                    force = float(row[3])
                except ValueError as exc:
                    raise ValueError("OUTPUT_FN_BAD_NUMBER") from exc
                if (n, d) != (node, dof) or not math.isfinite(force):
                    raise ValueError("OUTPUT_FN_BAD_INDEX_OR_NONFINITE")
                if eq < -2147483648 or eq > 2147483647:
                    raise ValueError("OUTPUT_FN_BAD_OWNER")
                mapping.append(eq)
                i += 1
        if i >= len(lines) or lines[i] != "KB_OUTPUT_FN_END":
            raise ValueError("OUTPUT_FN_BAD_END")
        i += 1
        if owners is not None and mapping != owners:
            raise ValueError("OUTPUT_FN_OWNER_CHANGED")
        owners = mapping
        blocks.append((step, inc, nk, mt))
    if len(blocks) != 10:
        raise ValueError("OUTPUT_FN_WRONG_BLOCK_COUNT")
    return {"blocks": len(blocks), "nk": blocks[0][2], "mt": blocks[0][3], "rows": sum(b[2] * b[3] for b in blocks)}

def main(root):
    root = pathlib.Path(root)
    cases = []
    for mesh in (8, 16):
        for trial in ("minus1", "zero", "plus1"):
            path = root / f"n{mesh}" / "no_contact" / trial / "kb_ccx221_output_fn.tsv"
            if not path.is_file():
                raise ValueError("OUTPUT_FN_MISSING_CASE")
            report = check_trace(path.read_text().splitlines())
            cases.append({"case": f"n{mesh}/{trial}", **report})
    print(json.dumps({"status": "PASS", "scope": "fn_trace_structure_only_not_spc_dual", "cases": cases}, sort_keys=True))

if __name__ == "__main__":
    main(sys.argv[1])
