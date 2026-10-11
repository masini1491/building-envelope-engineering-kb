"""Stage 28 fail-closed MEANROT term roles from exact usermpc source."""
from pathlib import Path
from collections import defaultdict
import sys
import argparse
sys.path.insert(0,str(Path(__file__).resolve().parent))
from ccx_mpc_terms import parse_terms

def parse_roles(path):
    if not path.is_file() or path.stat().st_size>8000000:
        raise ValueError("ROLE_TRACE_UNAVAILABLE")
    lines=path.read_text(encoding="ascii").splitlines()
    if not lines or len(lines)>200000:
        raise ValueError("ROLE_TRACE_UNBOUNDED")
    roles={}
    pending=None
    for line in lines:
        p=line.split(",")
        if p[0]=="ROLE_TERM" and len(p)==8:
            try: mid,slot,node,dof,role,ref,axis=map(int,p[1:])
            except ValueError as e:raise ValueError("INVALID_ROLE_FIELD") from e
            if not(mid>0 and slot>0 and node>0 and dof in (0,1,2,3)
                    and role in (0,1,2) and ref>0 and axis in (1,2,3)):
                raise ValueError("INVALID_ROLE_FIELD")
            if pending is None:pending=(mid,[],ref,axis)
            if mid!=pending[0] or (ref,axis)!=(pending[2],pending[3]) or slot!=len(pending[1])+1:
                raise ValueError("ROLE_SEQUENCE_MISMATCH")
            pending[1].append((node,dof,role))
        elif p[0]=="ROLE_END" and len(p)==7:
            try: mid,total,angle,inhom,ref,axis=map(int,p[1:])
            except ValueError as e:raise ValueError("INVALID_ROLE_END") from e
            if pending is None or mid in roles or (mid,total,ref,axis)!=(pending[0],len(pending[1]),pending[2],pending[3]):
                raise ValueError("ROLE_END_MISMATCH")
            items=pending[1]
            if sum(x[2]==1 for x in items)!=1 or sum(x[2]==2 for x in items)!=1:
                raise ValueError("HELPER_ROLE_MULTIPLICITY")
            if not any(x[0]==angle and x[2]==1 for x in items) or not any(x[0]==inhom and x[2]==2 for x in items):
                raise ValueError("HELPER_ROLE_IDENTITY")
            roles[mid]=tuple(items)
            pending=None
        else:raise ValueError("MALFORMED_ROLE_TRACE")
    if pending is not None or not roles:raise ValueError("ROLE_TRACE_INCOMPLETE")
    return roles

def compare(role_path,term_path):
    roles=parse_roles(role_path)
    terms=defaultdict(list)
    for mid,slot,node,dof,coeff,mult in parse_terms(term_path)["last_call_terms"]:
        terms[mid].append((node,dof))
    if not roles or not terms:
        raise ValueError("NO_MEANROT_OBSERVATIONS")
    counts=[0,0,0]
    for items in roles.values():
        for node,dof,role in items:counts[role]+=1
    common=set(roles)&set(terms)
    equal=sum(1 for mid in common if [(n,d) for n,d,_ in roles[mid]]==terms[mid])
    return {"creation_meanrot_mpcs":len(roles),"final_meanrot_mpcs":len(terms),
            "creation_regular_terms":counts[0],
            "creation_angle_axis_terms":counts[1],
            "creation_inhomogeneous_terms":counts[2],
            "common_numeric_mpc_ids":len(common),
            "matching_term_sequences_within_common_ids":equal,
            "creation_to_final_mapping":"NOT_ESTABLISHED",
            "term_role_labels_apply_to":"USRMPC_CREATION_SNAPSHOT_ONLY",
            "support_reaction_moment":"UNOBSERVED",
            "six_component_balance":"NOT_ADMITTED"}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("roles",type=Path)
    p.add_argument("terms",type=Path)
    a=p.parse_args();print(compare(a.roles,a.terms))
