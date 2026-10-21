"""Inspect original vs expanded shell nodal internal fn (not independent RF)."""
import argparse
import json
import math
from pathlib import Path


def reject(reason):
    raise ValueError('CONTACT_FN_' + reason)


def original_nodes(deck):
    seen = set(); active = False
    for line in deck.splitlines():
        s=line.strip()
        if s.upper() == '*NODE':
            if active: reject('DUPLICATE_NODE_HEADER')
            active=True; continue
        if active and s.startswith('*'): break
        if active and s:
            v=s.split(',')
            if len(v)!=4: reject('BAD_NODE_ROW')
            try: node=int(v[0]); pos=[float(x) for x in v[1:]]
            except ValueError: reject('BAD_NODE_VALUE')
            if node<1 or node in seen or not all(math.isfinite(x) for x in pos):
                reject('DUPLICATE_OR_NONFINITE_NODE')
            seen.add(node)
    if not seen or seen != set(range(1,len(seen)+1)):reject('NODE_COVERAGE')
    return len(seen)


def parse_trace(lines, n_original):
    blocks=[]; k=0; stable_shape=None
    while k<len(lines):
        h=lines[k].split()
        if len(h)!=5 or h[0]!='KB_OUTPUT_FN_BEGIN': reject('BAD_BEGIN')
        try: step,inc,nk,mt=map(int,h[1:])
        except ValueError:reject('BAD_HEADER_NUMERIC')
        if step!=1 or inc!=len(blocks)+1 or nk<n_original or mt<4 or mt>10:
            reject('WRONG_INCREMENT_OR_SHAPE')
        if stable_shape is not None and (nk,mt)!=stable_shape:reject('SHAPE_CHANGED')
        stable_shape=(nk,mt)
        k+=1; orig=[];expanded=[]; active=0;inactive=0
        for node in range(1,nk+1):
            for dof in range(mt):
                if k>=len(lines):reject('TRUNCATED')
                row=lines[k].split()
                if len(row)!=5 or row[0]!='KB_OUTPUT_FN':reject('BAD_ROW')
                try: nid,d,force,owner=int(row[1]),int(row[2]),float(row[3]),int(row[4])
                except ValueError:reject('BAD_NUMBER')
                if (nid,d)!=(node,dof) or not math.isfinite(force) or not (-2147483648<=owner<=2147483647):
                    reject('BAD_ROW_INDEX_OR_FORCE')
                if dof==3:
                    (orig if nid<=n_original else expanded).append(force)
                    active+=int(owner>0);inactive+=int(owner<=0)
                k+=1
        if k>=len(lines) or lines[k]!='KB_OUTPUT_FN_END':reject('BAD_END')
        k+=1
        oa=math.fsum(orig); ea=math.fsum(expanded)
        blocks.append({'step':step,'increment':inc,'original_node_count':n_original,
                       'expanded_node_count':nk-n_original,'total_node_count':nk,'mt':mt,
                       'original_fn3_n':oa,'expanded_fn3_n':ea,
                       'all_fn3_n':math.fsum([oa,ea]),
                       'original_abs_fn3_n':math.fsum(map(abs,orig)),
                       'expanded_abs_fn3_n':math.fsum(map(abs,expanded)),
                       'active_dof3_count':active,'inactive_dof3_count':inactive})
    if not blocks:reject('NO_BLOCKS')
    return blocks


def sta_increments(data):
    incs=[]
    for line in data.splitlines():
        v=line.split()
        if len(v)==7 and v[0]=='1':
            try: inc=int(v[1]); time=float(v[4])
            except ValueError:reject('BAD_STA_ROW')
            if inc!=len(incs)+1 or not math.isfinite(time):reject('BAD_STA_INCREMENT')
            incs.append((inc,time))
    if not incs or abs(incs[-1][1]-1.)>1e-6:reject('INCOMPLETE_STA')
    return incs


def examine(root):
    root=Path(root);cases=[]
    for n in (8,16):
        for scenario in ('toward','unlinked'):
            case=root/f'u_base_contact_n{n}_{scenario}'
            num=original_nodes((case/'panel.inp').read_text())
            if num!={8:346,16:666}[n]:reject('WRONG_ORIGINAL_NODE_COUNT')
            blocks=parse_trace((case/'kb_ccx221_output_fn.tsv').read_text().splitlines(),num)
            sta=sta_increments((case/'panel.sta').read_text())
            if [row['increment'] for row in blocks]!=[key for key,t in sta]:
                reject('STA_FN_INCREMENT_MISMATCH')
            cases.append({'mesh':n,'case':scenario,'block_count':len(blocks),
                          'final':blocks[-1],
                          'raw_fn3_per_increment_n':[b['all_fn3_n'] for b in blocks]})
    return {'scope':'OUTPUT_STAGE_ORIGINAL_VS_EXPANDED_FN_NOT_SPC_DUAL',
            'cases':cases,'contact_equilibrium':'NOT_ESTABLISHED',
            'engineering_acceptance':'NOT_ADMITTED'}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('case_root')
    print(json.dumps(examine(ap.parse_args().case_root),indent=2,allow_nan=False))
