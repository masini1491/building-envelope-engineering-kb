"""Stage 26: bounded internal MPC term trace for isolated CalculiX 2.21 builds.

The values are internal solver coefficients and fmpc, NOT independently
observed shell rotational support reactions or global six-component balance.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

ANCHOR = "    return;\n\n}\n"
INSTRUMENT = r'''    /* Stage 26 experimental GPL-2.0 term observation, opt-in only. */
    if (*calcul_fn==1) {
        const char *term_path=getenv("CCX_MPC_TERMS_FILE");
        if (term_path!=NULL && term_path[0]!='\0') {
            static unsigned long trace_call=0;
            long long trace_rows=0;
            FILE *term_file=fopen(term_path,"a");
            if(term_file==NULL) {
                fprintf(stderr,"MPC_TERMS_FILE_OPEN_FAILED\n");
                exit(96);
            }
            trace_call++;
            fprintf(term_file,"CALL,%lu,%lld\n",trace_call,(long long)*nmpc);
            for(j=0;j<*nmpc;j++) {
                ITG term_index,term_count=0;
                double multiplier;
                ist=ipompc[j]-1;
                if(ist<0) continue;
                if(nodempc[3*ist+1]>3) continue;
                if(strncmp(&labmpc[20*j],"MEANROT",7)!=0) continue;
                multiplier=fmpc[j];
                if(!isfinite(multiplier)) {
                    fprintf(stderr,"MPC_TERMS_NONFINITE_MULTIPLIER\n");
                    exit(95);
                }
                term_index=ist;
                while(term_index>=0) {
                    ITG term_node,term_dof;
                    double term_coeff;
                    term_count++;
                    if(term_count>96) {
                        fprintf(stderr,"MPC_TERMS_CHAIN_TOO_LONG\n");
                        exit(94);
                    }
                    term_node=nodempc[3*term_index];
                    term_dof=nodempc[3*term_index+1];
                    term_coeff=coefmpc[term_index];
                    if(term_node<1 || term_dof<0 || term_dof>3 || !isfinite(term_coeff)) {
                        fprintf(stderr,"MPC_TERMS_INVALID_TERM\n");
                        exit(93);
                    }
                    fprintf(term_file,"TERM,%lu,%lld,%lld,%lld,%lld,%.17g,%.17g\n",
                        trace_call,(long long)(j+1),(long long)term_count,
                        (long long)term_node,(long long)term_dof,term_coeff,multiplier);
                    trace_rows++;
                    if(trace_rows>250000) {
                        fprintf(stderr,"MPC_TERMS_UNBOUNDED_CALL\n");
                        exit(92);
                    }
                    term_index=nodempc[3*term_index+2]-1;
                }
            }
            fprintf(term_file,"END,%lu,%lld\n",trace_call,trace_rows);
            if(fclose(term_file)!=0) {
                fprintf(stderr,"MPC_TERMS_FILE_CLOSE_FAILED\n");
                exit(91);
            }
        }
    }
'''


def append_patch(source: str) -> str:
    if source.count(ANCHOR)!=1 or source.count("MPC_TRACE_V1")!=1:
        raise ValueError("STAGE25_SOURCE_NOT_RECOGNIZED")
    if "MPC_TERMS_FILE" in source or "MPC_TERMS_CHAIN_TOO_LONG" in source:
        raise ValueError("ALREADY_STAGE26_INSTRUMENTED")
    return source.replace(ANCHOR, INSTRUMENT+ANCHOR,1)


def parse_terms(path: Path) -> dict:
    if path.stat().st_size > 12_000_000:
        raise ValueError("MISSING_UNBOUNDED_OR_TRUNCATED_TERM_TRACE")
    with path.open(encoding="ascii") as stream:
        lines=stream.readlines()
    if not lines or len(lines)>300000 or any(len(s)>512 or not s.endswith("\n") for s in lines):
        raise ValueError("MISSING_UNBOUNDED_OR_TRUNCATED_TERM_TRACE")
    call_index=0
    open_call=False
    current_nmpc=None
    final_terms=[]
    current_terms=[]
    current_mpc_ids={}
    rows=0
    for line in lines:
        a=line.strip().split(",")
        if a[0]=="CALL" and len(a)==3:
            if open_call:raise ValueError("INCOMPLETE_TERM_CALL")
            try:seq,nmpc=map(int,a[1:])
            except ValueError as e:raise ValueError("INVALID_CALL_METADATA") from e
            if seq!=call_index+1 or nmpc<0:raise ValueError("INVALID_CALL_METADATA")
            call_index=seq
            current_nmpc=nmpc
            open_call=True
            current_terms=[]
            current_mpc_ids={}
            rows=0
        elif a[0]=="TERM" and len(a)==8:
            if not open_call:raise ValueError("ORPHAN_MPC_TERM")
            try:
                seq,mid,slot,node,dof=map(int,a[1:6])
                coeff,multiplier=map(float,a[6:])
            except ValueError as e:raise ValueError("INVALID_TERM_RECORD") from e
            if (seq!=call_index or not 1<=mid<=current_nmpc or slot<1 or slot>96
                    or node<1 or dof not in (0,1,2,3) or not math.isfinite(coeff)
                    or not math.isfinite(multiplier)):
                raise ValueError("INVALID_TERM_RECORD")
            prev=current_mpc_ids.get(mid)
            if prev is None:
                if slot!=1:raise ValueError("MPC_TERM_SEQUENCE_ERROR")
                current_mpc_ids[mid]=(slot,multiplier)
            else:
                if slot!=prev[0]+1 or multiplier!=prev[1]:
                    raise ValueError("MPC_TERM_SEQUENCE_ERROR")
                current_mpc_ids[mid]=(slot,multiplier)
            current_terms.append((mid,slot,node,dof,coeff,multiplier))
            rows+=1
            if rows>250000:raise ValueError("UNBOUNDED_MPC_TERMS")
        elif a[0]=="END" and len(a)==3:
            if not open_call:raise ValueError("ORPHAN_MPC_END")
            try:seq,total=map(int,a[1:])
            except ValueError as e:raise ValueError("INVALID_END_METADATA") from e
            if seq!=call_index or total!=rows:raise ValueError("MPC_TERM_COUNT_MISMATCH")
            open_call=False
            final_terms=current_terms
        else:
            raise ValueError("MALFORMED_MPC_TERM_TRACE")
    if open_call:raise ValueError("TRUNCATED_MPC_TERM_TRACE")
    if not final_terms:raise ValueError("FINAL_MEANROT_TERMS_UNOBSERVED")
    return {"calls":call_index,"final_nmpc":current_nmpc,"final_mpc_count":len({t[0] for t in final_terms}),
            "final_term_count":len(final_terms),"last_call_terms":final_terms}


def compare_with_frd(stage25_trace: Path, terms_path: Path, frd_path: Path):
    from ccx_mpc_probe import read_trace
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"envelope_panels"))
    from check_expanded_frd import read_expanded_frd
    older=read_trace(stage25_trace)
    newer=parse_terms(terms_path)
    if older["resultforc_calls"]!=newer["calls"]:
        raise ValueError("STAGE25_26_CALL_MISMATCH")
    if older["maximum_observed_nmpc"]<newer["final_nmpc"]:
        raise ValueError("MPC_COUNT_EXCEEDS_STAGE25_TRACE")
    if older["maximum_observed_MEANROT_count"]<newer["final_mpc_count"]:
        raise ValueError("MEANROT_COUNT_EXCEEDS_STAGE25_TRACE")
    coords, _, displacements=read_expanded_frd(frd_path)
    if not coords or set(displacements)!=set(coords):
        raise ValueError("FRD_POSITION_COVERAGE_MISMATCH")
    terms=newer["last_call_terms"]
    matched=sum(1 for t in terms if t[2] in coords)
    unmapped=len(terms)-matched
    return {"resultforc_calls":newer["calls"],
            "last_call_MEANROT_mpcs":newer["final_mpc_count"],
            "last_call_MEANROT_terms":len(terms),
            "term_node_ids_in_expanded_FRD":matched,
            "term_node_ids_not_in_expanded_FRD":unmapped,
            "frd_id_match_is_physical_identity":"NOT_ESTABLISHED",
            "multiplier_times_coefficient_is_support_reaction":"NOT_ADMITTED",
            "six_component_global_moment_balance":"NOT_ADMITTED"}


def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="action",required=True)
    sub.add_parser("instrument").add_argument("source",type=Path)
    check=sub.add_parser("check")
    check.add_argument("stage25_trace",type=Path)
    check.add_argument("terms_trace",type=Path)
    check.add_argument("frd",type=Path)
    args=parser.parse_args()
    if args.action=="instrument":
        source=args.source.read_text(encoding="latin1")
        args.source.write_text(append_patch(source),encoding="latin1",newline="")
        print("STAGE26_SOURCE_PATCHED")
    else:
        print(compare_with_frd(args.stage25_trace,args.terms_trace,args.frd))


if __name__=="__main__":main()
