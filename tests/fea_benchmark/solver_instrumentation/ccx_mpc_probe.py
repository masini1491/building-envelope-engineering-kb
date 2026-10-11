"""Bounded CCX 2.21-1 MPC instrumentation for isolated GPL solver builds.

No original solver source or instrumented executable is checked into the KB.
All reported fmpc values are solver-internal redistribution observations,
NOT independent rotational support reactions or global moment acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import math
from pathlib import Path
import sys

ANCHOR = "    return;\n\n}\n"
INCLUDE = '#include "CalculiX.h"\n'
EXPECTED_C_SOURCE_SHA256 = "d1de9498ac715a7f08da0b7beba3c92c7c2f1030c85c37122d2708f2f480cad0"
INSTRUMENT = '''    /* Experimental MPC observation; contribution GPL-2.0-only. */
    if (*calcul_fn==1) {
        const char *audit_path=getenv("CCX_MPC_AUDIT_FILE");
        if (audit_path!=NULL && audit_path[0]!='\\0') {
            static unsigned long audit_seq=0;
            ITG audit_count=0;
            double audit_max=0.;
            FILE *audit_file;
            for(j=0;j<*nmpc;j++) {
                ist=ipompc[j]-1;
                if(ist<0) continue;
                ndir=nodempc[3*ist+1];
                if(ndir>3) continue;
                if(strncmp(&labmpc[20*j],"MEANROT",7)==0) {
                    audit_count++;
                    if(fabs(fmpc[j])>audit_max) audit_max=fabs(fmpc[j]);
                }
            }
            audit_file=fopen(audit_path,"a");
            if(audit_file==NULL) {
                fprintf(stderr,"MPC_AUDIT_FILE_OPEN_FAILED\\n");
                exit(98);
            }
            fprintf(audit_file,"MPC_TRACE_V1,%lu,%lld,%lld,%.17g\\n",
                    ++audit_seq,(long long)*nmpc,(long long)audit_count,audit_max);
            if(fclose(audit_file)!=0) {
                fprintf(stderr,"MPC_AUDIT_FILE_CLOSE_FAILED\\n");
                exit(99);
            }
        }
    }
'''


def patch(source: str) -> str:
    if source.count(ANCHOR) != 1 or source.count(INCLUDE) != 1:
        raise ValueError("UNRECOGNIZED_CALCULIX_221_RESULTSFORC")
    if "MPC_TRACE_V1" in source:
        raise ValueError("ALREADY_INSTRUMENTED")
    return source.replace(INCLUDE, INCLUDE + '#include <string.h>\n', 1).replace(
        ANCHOR, INSTRUMENT + ANCHOR, 1)


def read_trace(path: Path) -> dict:
    lines = path.read_text(encoding="ascii").splitlines()
    if not lines or len(lines) > 100000:
        raise ValueError("MISSING_OR_UNBOUNDED_MPC_TRACE")
    totals = []
    for index, line in enumerate(lines, 1):
        parts = line.split(",")
        if len(parts) != 5 or parts[0] != "MPC_TRACE_V1":
            raise ValueError("MALFORMED_MPC_TRACE")
        try:
            seq, nmpc, meanrot = map(int, parts[1:4])
            value = float(parts[4])
        except ValueError as exc:
            raise ValueError("INVALID_MPC_TRACE_VALUE") from exc
        if seq != index or nmpc < 0 or not 0 <= meanrot <= nmpc or not math.isfinite(value) or value < 0:
            raise ValueError("INVALID_MPC_TRACE_VALUE")
        totals.append((nmpc, meanrot, value))
    if not any(mean > 0 for _, mean, _ in totals):
        raise ValueError("MEANROT_MPC_NOT_OBSERVED")
    return {
        "resultforc_calls": len(lines),
        "maximum_observed_nmpc": max(v[0] for v in totals),
        "maximum_observed_MEANROT_count": max(v[1] for v in totals),
        "maximum_observed_abs_fmpc": max(v[2] for v in totals),
        "MPC_reaction": "NOT_INDEPENDENTLY_MEASURED",
        "six_component_balance": "NOT_ADMITTED",
    }


def compare(base: Path, instrumented: Path, trace: Path):
    panels = Path(__file__).resolve().parents[1] / "envelope_panels"
    sys.path.insert(0, str(panels))
    from check_pressure_equilibrium import parse_deck
    from check_follower_pressure import displacement_block
    from audit_rf_projection import rf_block
    from check_expanded_frd import read_expanded_frd
    from check_rf_3d_projection import read_final_expanded_rf

    a, b = base / "panel.inp", instrumented / "panel.inp"
    if a.read_bytes() != b.read_bytes():
        raise ValueError("SOURCE_DECKS_DIFFER")
    nodes, _, _, _ = parse_deck(a)
    dat_a, dat_b = a.with_suffix(".dat").read_text(errors="replace"), b.with_suffix(".dat").read_text(errors="replace")
    ua, ub = displacement_block(dat_a, set(nodes)), displacement_block(dat_b, set(nodes))
    fa, fb = rf_block(dat_a, "NALL", set(nodes)), rf_block(dat_b, "NALL", set(nodes))
    ca, ea, da = read_expanded_frd(a.with_suffix(".frd"))
    cb, eb, db = read_expanded_frd(b.with_suffix(".frd"))
    if ca != cb or ea != eb or set(da) != set(db):
        raise ValueError("EXPANDED_DATA_IDENTITY_MISMATCH")
    force_a = read_final_expanded_rf(a.with_suffix(".frd"), set(ca))
    force_b = read_final_expanded_rf(b.with_suffix(".frd"), set(cb))
    for name, x, y in (
        ("NALL_U", ua, ub), ("NALL_RF", fa, fb),
        ("EXPANDED_U", da, db), ("EXPANDED_RF", force_a, force_b)
    ):
        if x != y:
            raise ValueError(f"INSTRUMENTED_SOLVER_CHANGED_{name}")
    return {
        "original_nodes": len(nodes), "expanded_nodes": len(da),
        "output_comparison": "EXACT_TEXT_NUMERIC_MATCH",
        "trace": read_trace(trace), "rotational_support_reaction": "UNOBSERVED",
    }


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("instrument").add_argument("source", type=Path)
    c = sub.add_parser("compare")
    for name in ("baseline", "instrumented", "trace"):
        c.add_argument(name, type=Path)
    args = parser.parse_args()
    if args.cmd == "instrument":
        raw = args.source.read_bytes()
        if hashlib.sha256(raw).hexdigest() != EXPECTED_C_SOURCE_SHA256:
            raise ValueError("CALCULIX_221_SOURCE_SHA256_MISMATCH")
        changed = patch(raw.decode("latin1"))
        args.source.write_bytes(changed.encode("latin1"))
        print("BEFORE_SHA256", hashlib.sha256(raw).hexdigest())
        print("AFTER_SHA256", hashlib.sha256(args.source.read_bytes()).hexdigest())
    else:
        print(compare(args.baseline, args.instrumented, args.trace))


if __name__ == "__main__":
    main()
