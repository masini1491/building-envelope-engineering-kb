"""Stage 31 exact per-MPC cascade term count transitions; no force admission."""
from pathlib import Path
from collections import defaultdict
import argparse
from check_cascade_trace import parse as check_stage30

def examine(summary:Path,detail:Path):
    old=check_stage30(summary)
    if not detail.is_file() or not 0<detail.stat().st_size<4000000:
        raise ValueError("CASCADE_DETAIL_MISSING_OR_OVERSIZED")
    lines=detail.read_text(encoding="ascii").splitlines()
    if not lines or len(lines)>100000:
        raise ValueError("CASCADE_DETAIL_UNBOUNDED")
    calls=defaultdict(lambda:{"IN":{},"OUT":{}})
    for line in lines:
        p=line.split(",")
        if len(p)!=5 or p[0]!="CASCADE_DETAIL_V1":
            raise ValueError("CASCADE_DETAIL_BAD_RECORD")
        try:call,mid,terms=int(p[1]),int(p[3]),int(p[4])
        except ValueError as e:raise ValueError("CASCADE_DETAIL_INVALID_VALUE") from e
        phase=p[2]
        if call<1 or call>old["cascade_calls"] or mid<1 or terms<1 or terms>96 or phase not in ("IN","OUT"):
            raise ValueError("CASCADE_DETAIL_INVALID_VALUE")
        part=calls[call][phase]
        if mid in part:raise ValueError("CASCADE_DETAIL_DUPLICATE_MPC")
        part[mid]=terms
    if not calls:raise ValueError("CASCADE_DETAIL_UNOBSERVED")
    for line in summary.read_text(encoding="ascii").splitlines():
        p=line.split(",")
        call=int(p[1]);phase=p[2]
        expected_count,expected_total,expected_max=map(int,p[3:6])
        observed=calls[call][phase]
        if (len(observed),sum(observed.values()),max(observed.values(),default=0))!=(expected_count,expected_total,expected_max):
            raise ValueError("CASCADE_DETAIL_AGGREGATE_MISMATCH")
    changes=0
    reductions=0
    specific_8_to_4=0
    for call,d in calls.items():
        if not d["IN"] or not d["OUT"] or set(d["IN"])!=set(d["OUT"]):
            raise ValueError("CASCADE_DETAIL_UNMATCHED_MPC_IDS")
        for mid,initial in d["IN"].items():
            final=d["OUT"][mid]
            if initial!=final:changes+=1
            if final<initial:reductions+=1
            if initial==8 and final==4:specific_8_to_4+=1
    return {"cascade_calls":old["cascade_calls"],
            "observed_detail_calls":len(calls),
            "changed_mpc_term_count_pairs":changes,
            "reduced_mpc_term_count_pairs":reductions,
            "observed_8_to_4_transitions":specific_8_to_4,
            "per_mpc_transition_in_cascade":"OBSERVED" if changes else "NONE_OBSERVED",
            "global_term_lineage":"NOT_ESTABLISHED",
            "moment_reaction":"UNOBSERVED",
            "six_component_balance":"NOT_ADMITTED"}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("summary",type=Path)
    p.add_argument("detail",type=Path)
    x=p.parse_args()
    print(examine(x.summary,x.detail))
