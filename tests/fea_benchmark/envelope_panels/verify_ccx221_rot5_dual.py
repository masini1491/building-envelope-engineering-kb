"""Fail-closed replay of DOF5 / MEANROTBS fmpc virtual-work *candidate*.

Source: prior 20-case ZIP + kinematic owner ZIP + new read-only solver
instrumentation. A synthetic 48 N.mm couple checks the algebra and sign.
The actual CCX fmpc is NOT certified as a physical MPC multiplier/dual;
energy slopes likewise remain candidate energy observations.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import hashlib
import json
import math
import re
import zipfile

SOURCE_SHA = 'd9b36c420feca6a5f8cd50dc8cb07dbba6c2ebbbf0224abb4df57fbfd2291a8b'
OWNER_SHA = '01d03784c7fe0521087602262b36446127bad858ad90765170bc40c44c9d0361'
MANIFEST_SHA = 'd4af3bb7edbd06b5acba0343f07a8932281cd3221d35036daea31bdf6025fd9b'
TRIALS = ('minus1','zero','plus1')
NUM = r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?'

def fail(tag):
    raise ValueError('CCX221_ROT_DUAL_'+tag)

def finite(s):
    try: x=float(s.replace('D','E'))
    except (ValueError,AttributeError): fail('NUMBER')
    if not math.isfinite(x): fail('NONFINITE')
    return x

def parse_owner(raw):
    entries=[]
    for line in raw.splitlines():
        p=line.split()
        if len(p)!=9 or p[0]!='KB_ROT_OWNER': fail('OWNER_ROW')
        try:
            x=dict(origin=int(p[1]), axis=int(p[2]), ordinal=int(p[3]),
                   spc=int(p[4]),aux=int(p[5]), direction=int(p[6]),
                   angle=finite(p[7]),mpc=int(p[8]))
        except ValueError: fail('OWNER_VALUE')
        if min(x['origin'],x['axis'],x['ordinal'],x['spc'],x['aux'],x['direction'],x['mpc'])<=0:
            fail('OWNER_RANGE')
        entries.append(x)
    if not entries: fail('OWNER_EMPTY')
    if len({(x['origin'],x['axis'],x['ordinal']) for x in entries})!=len(entries): fail('OWNER_DUPLICATE')
    return entries

def parse_trace(text):
    events={}; spcs={'P':{},'Q':{}}; mpcs={}
    current=None
    for line in text.splitlines():
        p=line.split()
        if not p: fail('EMPTY_ROW')
        kind=p[0]
        if kind=='KB_ROT_PHASE':
            if len(p)!=8 or p[1] not in ('P','Q') or p[1] in events: fail('PHASE')
            current=p[1]
            e=dict(step=int(p[2]),inc=int(p[3]),time=finite(p[4]),
                   nk=int(p[5]),nboun=int(p[6]),nmpc=int(p[7]))
            if e['step']!=1 or min(e['inc'],e['nk'],e['nboun'],e['nmpc'])<=0 or abs(e['time']-1)>1e-7:
                fail('PHASE_SCOPE')
            events[current]=e
        elif kind=='KB_ROT_SPC':
            if len(p)!=8 or p[1]!=current: fail('SPC_ROW')
            i,node,d,eq=map(int,p[2:6]);val,force=map(finite,p[6:8])
            if i<=0 or node<=0 or d not in (1,2,3) or i>events[current]['nboun'] or node>events[current]['nk']:
                fail('SPC_SCOPE')
            if i in spcs[current]:fail('SPC_DUPLICATE')
            spcs[current][i]=(node,d,eq,val,force)
        elif kind=='KB_ROT_MPC':
            if current!='Q' or len(p)!=3: fail('MPC_ROW')
            i=int(p[1]);lam=finite(p[2])
            if i<=0 or i>events['Q']['nmpc'] or i in mpcs:fail('MPC_DUPLICATE_OR_SCOPE')
            mpcs[i]={'fmpc':lam,'terms':[]}
        elif kind=='KB_ROT_TERM':
            if current!='Q' or len(p)!=6:fail('TERM_ROW')
            m,k,node,d=map(int,p[1:5]);coef=finite(p[5])
            if m not in mpcs or k!=len(mpcs[m]['terms'])+1 or node<=0 or d not in (1,2,3):fail('TERM_ORDER')
            mpcs[m]['terms'].append((node,d,coef))
        elif kind=='KB_ROT_TERM_LIMIT':
            fail('TERM_LIMIT')
        else:fail('UNKNOWN_ROW')
    if set(events)!= {'P','Q'} or events['P']!=events['Q'] or not mpcs:fail('PHASE_COVERAGE')
    if set(spcs['P'])!=set(spcs['Q']) or not spcs['P']:fail('SPC_COVERAGE')
    for i in spcs['P']:
        if spcs['P'][i][:4]!=spcs['Q'][i][:4]:fail('SPC_PRE_POST_OWNER')
    if len({(s[0],s[1]) for s in spcs['Q'].values()})!=len(spcs['Q']):
        fail('SPC_NODE_DIRECTION_DUPLICATE')
    # usermpc.f may reorder the dependent term and remove zero regular-node
    # coefficients. 4- and 6-term lists occur for the same one-point shell
    # mean-rotation MPC; neither term count nor tail position is a dual owner.
    spc_pairs={(s[0],s[1]) for s in spcs['Q'].values()}
    for v in mpcs.values():
        ts=v['terms']
        if len(ts)<4 or len({(node,d) for node,d,c in ts})!=len(ts):
            fail('MEANROT_TOPOLOGY')
        coeff={(node,d):c for node,d,c in ts}
        aux=[node for node,d,c in ts
             if d==1 and (node,1) in spc_pairs and (node,2) in spc_pairs
             and (node,2) in coeff]
        if len(aux)!=1:fail('MEANROT_TOPOLOGY')
        node=aux[0];angle=coeff[(node,1)];inhom=coeff[(node,2)]
        n=round(-angle)
        if n<1 or abs(angle+n)>1e-10 or abs(inhom-n/2)>1e-10:
            fail('ANGLE_COEFFICIENT')
        v['aux_node']=node
        v['angle_coef']=angle
        v['inhom_coef']=inhom
        v['nodal_cloud_count']=n
    return {'events':events,'spcs':spcs,'mpcs':mpcs}

def deck_mode(deck):
    t=deck.split('*STEP,',1)
    if len(t)!=2:fail('DECK_STEP')
    pairs=re.findall(r'(?m)^(\d+),5,5,([-+]?[0-9.]+)$',t[1])
    if not pairs:fail('DECK_DOF5')
    angles={int(n):finite(a) for n,a in pairs}
    if len(angles)!=len(pairs):fail('DECK_DUPLICATE')
    ns=re.search(r'(?m)^\*NSET,NSET=PLATE_EDGE_RF\s*\n([^*]+)',deck)
    if ns is None:fail('DECK_EDGE')
    ids=[int(n) for n in re.findall(r'\d+',ns.group(1))]
    if set(angles)!=set(ids):fail('DECK_COVERAGE')
    nodes=deck.split('*NODE\n',1)
    if len(nodes)!=2:fail('DECK_NODE')
    xs={}
    for line in nodes[1].split('*ELEMENT,',1)[0].splitlines():
        q=[s.strip() for s in line.split(',')]
        if len(q)==4:xs[int(q[0])]=finite(q[1])
    if not set(ids)<=set(xs):fail('DECK_COORDS')
    return angles,{i:(xs[i]-600.)/600. for i in ids}

def energy(dat,label):
    hits=re.findall(r'(?m)^\s*'+re.escape(label)+r'\s+('+NUM+r')\s*\n\s*\n\s*([^\n]+)',dat)
    vals=[]
    for t,r in hits:
        if abs(finite(t)-1)<1e-8:
            tok=r.split()
            if len(tok)!=1:fail('ENERGY_FORMAT')
            vals.append(finite(tok[0]))
    if not vals or max(vals)-min(vals)>1e-7:fail('ENERGY_ABSENT_OR_DUPLICATE')
    return vals[-1]

def analytic_48():
    # Model-independent signed virtual work. MPC form: u_z + x*theta = 0.
    x=(-100.,100.);theta=2e-5;k=120.
    f=tuple(-k*r*theta for r in x)
    q=-math.fsum(r*force for r,force in zip(x,f))
    power=math.fsum(force*(-r) for r,force in zip(x,f))
    if abs(sum(f))>1e-12 or not math.isclose(q,48.,rel_tol=0,abs_tol=1e-12) or q!=power:
        fail('ANALYTIC_COUPLE')
    return {'net_force_n':sum(f),'internal_virtual_work_nmm_per_rad':power,
            'mpc_elimination_signed_nmm':q,'analytic_expected_nmm':48.}

def reconstruct(owner,trace,angles,weights):
    rows=[r for r in owner if r['origin'] in angles and r['axis']==2 and r['ordinal']==2]
    if len(rows)!=len(angles) or {r['origin'] for r in rows}!=set(angles):fail('OWNER_COVERAGE')
    terms=[]
    for r in rows:
        if r['direction']!=1 or not math.isclose(r['angle'],angles[r['origin']],abs_tol=1e-13,rel_tol=0):
            fail('ROT_VALUE')
        # Creation-time SPC indices can be renumbered by later bounadd calls.
        # Verify against the final physical auxiliary node and direction,
        # never infer current identity from a historical slot index alone.
        matched=[s for s in trace['spcs']['Q'].values() if s[:2]==(r['aux'],1)]
        if len(matched)!=1:fail('AUX_SPC_MAPPING')
        s=matched[0]
        if abs(s[3]-r['angle'])>1e-13:fail('AUX_SPC_VALUE')
        v=trace['mpcs'].get(r['mpc'])
        if v is None or v['aux_node']!=r['aux']:fail('AUX_MPC_MAPPING')
        # This is a bookkeeping candidate, not a certified dual-force moment.
        terms.append(-v['fmpc']*v['angle_coef']*weights[r['origin']])
    return {'node_count':len(rows),'internal_fmpc_weighted_candidate_nmm':math.fsum(terms),
            'angle_coefficient_proven_for_selected_mpcs':True,
            'independent_dual_reaction':'NOT_ESTABLISHED'}

def verify(source:Path,owner:Path,dual:Path):
    raws=[x.read_bytes() for x in (source,owner,dual)]
    if hashlib.sha256(raws[0]).hexdigest()!=SOURCE_SHA or hashlib.sha256(raws[1]).hexdigest()!=OWNER_SHA:
        fail('SOURCE_OR_OWNER_ZIP_SHA')
    report={};zsha=hashlib.sha256(raws[2]).hexdigest()
    with zipfile.ZipFile(source) as src,zipfile.ZipFile(owner) as own,zipfile.ZipFile(dual) as ins:
        manifestbytes=src.read('manifest.json')
        if hashlib.sha256(manifestbytes).hexdigest()!=MANIFEST_SHA:fail('MANIFEST_SHA')
        manifest=json.loads(manifestbytes)['cases']
        for n in (8,16):
            d={}
            for trial in TRIALS:
                key=f'n{n}/no_contact/{trial}'
                inp=src.read(key+'/panel.inp')
                if hashlib.sha256(inp).hexdigest()!=manifest[key]['input_sha256']:fail('INPUT_SHA')
                a,w=deck_mode(inp.decode('ascii'))
                os=parse_owner(own.read('rot-owner/'+key+'/kb_rot_owner.tsv').decode('ascii'))
                trace=parse_trace(ins.read('rot-dual/'+key+'/kb_rot_dual.tsv').decode('ascii'))
                for ext in ('dat','sta'):
                    if src.read(key+'/panel.'+ext)!=ins.read('rot-dual/'+key+'/panel.'+ext):
                        fail('AB_'+ext.upper())
                val=reconstruct(os,trace,a,w)
                dat=src.read(key+'/panel.dat').decode('latin-1')
                e=sum(energy(dat,label) for label in ('total internal energy for set PLATE and time',
                              'total internal energy for set RIB and time'))
                d[trial]={'candidate_energy_nmm':e,**val}
            slope=(d['plus1']['candidate_energy_nmm']-d['minus1']['candidate_energy_nmm'])/2e-5
            candidate=d['zero']['internal_fmpc_weighted_candidate_nmm']
            report['n'+str(n)]={'cases':d,'energy_central_slope_nmm':slope,
                'fmpc_candidate_at_zero_nmm':candidate,
                'candidate_minus_energy_slope_nmm':candidate-slope,
                'physics_reaction_moment':'NOT_ESTABLISHED'}
    return {'status':'MEANROTBS_FMPC_VIRTUAL_WORK_CANDIDATE_ONLY',
         'source_zip_sha256':SOURCE_SHA,'owner_zip_sha256':OWNER_SHA,
         'dual_zip_sha256':zsha,'analytic_external_oracle':analytic_48(),
         'results':report,'contact':'NOT_TESTED',
         'independent_mpc_dual':'NOT_ESTABLISHED',
         'six_component_balance':'NOT_ADMITTED',
         'engineering_acceptance':'NOT_ADMITTED'}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('source_zip',type=Path)
    p.add_argument('owner_zip',type=Path);p.add_argument('dual_zip',type=Path)
    a=p.parse_args();print(json.dumps(verify(a.source_zip,a.owner_zip,a.dual_zip),sort_keys=True,indent=2,allow_nan=False))

