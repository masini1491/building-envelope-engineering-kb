"""Reconstruct CCX 2.21 Z-force output's MPC phase attribution.

This is a source/trace consistency diagnostic, NOT an independent support-
reaction oracle, contact acceptance, or a fix to an engineering RF3 gate.
"""
from __future__ import annotations
from collections import defaultdict
import argparse
import json
import math
import re
from pathlib import Path


def fail(s):
    raise ValueError('CCX221_MPC_RESTORE_' + s)


def finite(s):
    try: v = float(s)
    except (ValueError, TypeError): fail('NUMBER')
    if not math.isfinite(v): fail('NONFINITE')
    return v


def integer(s):
    try: return int(s)
    except (ValueError, TypeError): fail('INTEGER')


def parse(data):
    frames=[]
    current=None
    if len(data)>20_000_000: fail('SIZE')
    for line in data.splitlines():
        t=line.split()
        if not t: fail('BLANK')
        kind=t[0]
        if kind=='KB_EVENT':
            if len(t)!=8 or t[1] not in ('P','Q'): fail('EVENT_FORMAT')
            current={'phase':t[1],'inc':integer(t[3]),'time':finite(t[4]),
                     'nk':integer(t[5]),'mt':integer(t[6]),'nmpc':integer(t[7]),
                     'fn':{},'mpc':{},'terms':defaultdict(dict)}
            if integer(t[2])!=1 or current['mt']!=4 or current['nk']<=0 or current['nmpc']<0:
                fail('EVENT_CONTEXT')
            frames.append(current)
        elif current is None: fail('MISSING_EVENT')
        elif kind=='KB_FN':
            if len(t)!=6 or t[1]!=current['phase']: fail('FN_FORMAT')
            node,axis,active=map(integer,t[2:5]);v=finite(t[5])
            if not (1<=node<=current['nk'] and 1<=axis<=3) or (node,axis) in current['fn']:
                fail('FN_SCOPE')
            current['fn'][(node,axis)]=v
        elif kind=='KB_MPC':
            if current['phase']!='Q' or len(t) not in (3,4):fail('MPC_FORMAT')
            i=integer(t[1]);label=t[2] if len(t)==4 else 'EMPTY';mu=finite(t[-1]);
            if not 1<=i<=current['nmpc'] or i in current['mpc']:fail('MPC_COVERAGE')
            current['mpc'][i]=(label,mu)
        elif kind=='KB_TERM':
            if current['phase']!='Q' or len(t)!=6:fail('TERM_FORMAT')
            i,order,node,axis=map(integer,t[1:5]);coef=finite(t[5])
            if not (1<=i<=current['nmpc'] and 1<=order<=10000 and 1<=node<=current['nk'] and 1<=axis<=3):fail('TERM_SCOPE')
            if order in current['terms'][i]:fail('TERM_DUP')
            current['terms'][i][order]=(node,axis,coef)
        elif kind=='KB_ACTIVE':
            if current['phase']!='Q' or len(t)!=3:fail('ACTIVE_FORMAT')
            integer(t[1]);finite(t[2])
        elif kind=='KB_MPC_NOT_EVALUATED':fail('MPC_NOT_EVALUATED')
        else:fail('UNKNOWN_'+kind)
    if not frames or len(frames)%2:fail('FRAME_COUNT')
    for n in range(0,len(frames),2):
        p,q=frames[n:n+2]
        if (p['phase'],q['phase'])!=('P','Q') or any(p[k]!=q[k] for k in ('inc','time','nk','mt','nmpc')):fail('PAIR')
        if p['inc']!=n//2+1 or len(q['mpc'])!=q['nmpc'] or set(q['terms'])!=set(q['mpc']):fail('MPC_COVERAGE')
        for i,terms in q['terms'].items():
            if set(terms)!=set(range(1,len(terms)+1)) or terms[1][2]==0:fail('TERM_COVERAGE')
    return frames


def reconstruct(p,q):
    values=defaultdict(float,p['fn']);by_label=defaultdict(lambda: [[],[]]);mu_errors=[]
    def update(node,axis,new,label,phase):
        key=(node,axis);old=values[key];values[key]=new
        if axis==3:by_label[label][phase].append(new-old)
    for i in range(1,q['nmpc']+1):
        label,mu=q['mpc'][i];terms=q['terms'][i];node,axis,coef=terms[1]
        observed=values[node,axis]/coef
        mu_errors.append(abs(observed-mu))
        if not math.isclose(observed,mu,rel_tol=1e-10,abs_tol=1e-7):fail('MULTIPLIER')
        update(node,axis,0.,label,0)
        for j in range(2,len(terms)+1):
            node,axis,coef=terms[j]
            update(node,axis,values[node,axis]-coef*mu,label,0)
    for i in range(1,q['nmpc']+1):
        label,mu=q['mpc'][i];terms=q['terms'][i];node,axis,coef=terms[1]
        update(node,axis,coef*mu,label,1)
        for j in range(2,len(terms)+1):
            node,axis,coef=terms[j]
            update(node,axis,values[node,axis]+coef*mu,label,1)
    keys={key for key in set(values)|set(q['fn']) if key[1]==3}
    err=max((abs(values[k]-q['fn'].get(k,0.)) for k in keys),default=0.)
    if err>1e-8:fail('REPLAY_OUTPUT')
    out={label:{'elimination_f3_n':math.fsum(pair[0]),'restoration_f3_n':math.fsum(pair[1]),
                'net_f3_n':math.fsum(pair[0]+pair[1])} for label,pair in sorted(by_label.items())}
    pre=math.fsum(v for (n,a),v in p['fn'].items() if a==3)
    post=math.fsum(v for (n,a),v in q['fn'].items() if a==3)
    net=math.fsum(v['net_f3_n'] for v in out.values())
    if not math.isclose(post-pre,net,rel_tol=1e-10,abs_tol=1e-8):fail('PHASE_BALANCE')
    return {'increment':q['inc'],'pre_mpc_fn3_sum_n':pre,'post_mpc_fn3_sum_n':post,
            'net_mpc_fn3_change_n':net,'max_abs_z_output_replay_error_n':err,
            'max_abs_mpc_multiplier_replay_error_n':max(mu_errors,default=0.),'mpc_type_contributions':out}


def dat_original_rf3(dat):
    pattern=r'^\s*forces \(fx,fy,fz\) for set ALL_ORIGINAL_RF and time\s+([^\n]+)\n'
    matches=list(re.finditer(pattern,dat,re.M))
    if not matches: fail('DAT_NO_ORIGINAL_RF')
    mark=matches[-1];t=finite(mark.group(1))
    if abs(t-1.0)>1e-8:fail('DAT_TIME')
    end=dat.find('\n\n',mark.end())
    if end<0:fail('DAT_SECTION')
    rows=dat[mark.end():end].strip().splitlines()
    force=[]
    for row in rows:
        v=row.split()
        if len(v)!=4 or integer(v[0])<1:fail('DAT_RECORD')
        force.append(finite(v[3]))
    if not force:fail('DAT_EMPTY')
    return math.fsum(force)


def audit(force_text,dat_text):
    frames=parse(force_text)
    measurements=[reconstruct(*frames[i:i+2]) for i in range(0,len(frames),2)]
    final=measurements[-1];printed=dat_original_rf3(dat_text)
    difference=printed-final['post_mpc_fn3_sum_n']
    if abs(difference)>0.00005:fail('ORIGINAL_RF_PROJECTION')
    knot=final['mpc_type_contributions'].get('KNOT1')
    if not knot or abs(knot['net_f3_n'])>1e-7:fail('KNOT1_NOT_BALANCED')
    if 'MEANROTBS' not in final['mpc_type_contributions']:fail('MISSING_MEANROT')
    return {'status':'CCX221_MPC_Z_FORCE_REPLAY_ONLY_NOT_PHYSICAL_EQUILIBRIUM',
            'increment_count':len(measurements),'final':final,
            'all_increment_max_replay_error_n':max(x['max_abs_z_output_replay_error_n'] for x in measurements),
            'raw_dat_all_original_rf3_sum_n':printed,'raw_dat_minus_post_mpc_f3_n':difference,
            'external_load_support_balance':'NOT_ESTABLISHED','engineering_acceptance':'NOT_ADMITTED'}


if __name__=='__main__':
    pa=argparse.ArgumentParser()
    pa.add_argument('force_ledger',type=Path);pa.add_argument('dat',type=Path)
    ar=pa.parse_args()
    print(json.dumps(audit(ar.force_ledger.read_text(encoding='ascii'),ar.dat.read_text(encoding='latin-1')),
                     sort_keys=True,allow_nan=False))
