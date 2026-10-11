"""Fail-closed cascade entry/exit observational record checker."""
from pathlib import Path
import argparse

def parse(path:Path):
    if not path.is_file() or not 0<path.stat().st_size<=1000000:
        raise ValueError("CASCADE_TRACE_MISSING_OR_OVERSIZED")
    lines=path.read_text(encoding="ascii").splitlines()
    if not lines or len(lines)>20000:
        raise ValueError("CASCADE_TRACE_UNBOUNDED")
    pairs=[]
    opening=None
    for line in lines:
        p=line.split(",")
        if len(p)!=6 or p[0]!="CASCADE_V1":
            raise ValueError("CASCADE_TRACE_BAD_RECORD")
        try:seq,count,terms,maximum=map(int,(p[1],p[3],p[4],p[5]))
        except ValueError as e:raise ValueError("CASCADE_TRACE_INVALID_VALUE") from e
        phase=p[2]
        if seq<1 or count<0 or terms<0 or maximum<0 or (count==0 and (terms or maximum)) or (count>0 and (terms<count or maximum<1 or maximum>96)):
            raise ValueError("CASCADE_TRACE_INVALID_VALUE")
        if phase=="IN":
            if opening or seq!=len(pairs)+1:raise ValueError("CASCADE_TRACE_INCOMPLETE_PAIR")
            opening=(seq,count,terms,maximum)
        elif phase=="OUT":
            if not opening or opening[0]!=seq:raise ValueError("CASCADE_TRACE_INCOMPLETE_PAIR")
            pairs.append((opening[1:],(count,terms,maximum)))
            opening=None
        else:raise ValueError("CASCADE_TRACE_INVALID_PHASE")
    if opening:raise ValueError("CASCADE_TRACE_INCOMPLETE_PAIR")
    if not any(a[0]>0 or b[0]>0 for a,b in pairs):
        raise ValueError("NO_MEANROT_CASCADE_OBSERVED")
    return {
        "cascade_calls":len(pairs),
        "calls_with_meanrot":sum(a[0]>0 or b[0]>0 for a,b in pairs),
        "changed_total_term_count_calls":sum(a[1]!=b[1] for a,b in pairs),
        "changed_meanrot_mpc_count_calls":sum(a[0]!=b[0] for a,b in pairs),
        "largest_meanrot_chain_seen":max(max(a[2],b[2]) for a,b in pairs),
        "specific_8_to_4_causality":"NOT_ESTABLISHED",
        "term_lineage":"NOT_ESTABLISHED",
        "support_moment":"UNOBSERVED",
        "global_six_component_balance":"NOT_ADMITTED",
    }

if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("trace",type=Path)
    x=a.parse_args();print(parse(x.trace))
