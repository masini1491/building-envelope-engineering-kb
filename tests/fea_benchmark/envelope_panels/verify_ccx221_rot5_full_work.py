"""Fail-closed *algorithmic* full-MPC elimination replay for CCX 2.21.

This reconstructs internal force bookkeeping on the full expanded DOF graph;
not an independent solver, external constraint dual, or support moment oracle.
"""
from __future__ import annotations
import hashlib, json, math, re, zipfile
from pathlib import Path

SOURCE_SHA = 'd9b36c420feca6a5f8cd50dc8cb07dbba6c2ebbbf0224abb4df57fbfd2291a8b'
OWNER_SHA = '01d03784c7fe0521087602262b36446127bad858ad90765170bc40c44c9d0361'
MANIFEST_SHA = 'd4af3bb7edbd06b5acba0343f07a8932281cd3221d35036daea31bdf6025fd9b'
CASES = tuple(f'n{n}/no_contact/{trial}' for n in (8,16) for trial in ('minus1','zero','plus1'))

def reject(reason): raise ValueError('CCX221_FULL_WORK_'+reason)

def finite(s):
    try: v=float(s)
    except (TypeError, ValueError): reject('BAD_NUMBER')
    if not math.isfinite(v): reject('NONFINITE')
    return v

def integers(s):
    try: v=int(s)
    except (TypeError,ValueError): reject('BAD_INTEGER')
    if v<1:reject('NONPOSITIVE_ID')
    return v

def parse_work(src):
    hdr=None; nodal={};mpcs={};ended=False
    for line in src.splitlines():
        p=line.split()
        if not p or ended:reject('RECORD_SEQUENCE')
        tag=p[0]
        if tag=='KB_WORK_EVENT':
            if hdr is not None or len(p)!=7:reject('EVENT')
            step,inc=map(integers,p[1:3]);time=finite(p[3]);nk,mt,nmpc=map(integers,p[4:7])
            if step!=1 or abs(time-1)>1e-7 or mt<4:reject('EVENT_SCOPE')
            hdr=(step,inc,time,nk,mt,nmpc)
        elif hdr is None:reject('MISSING_EVENT')
        elif tag=='KB_WORK_FN':
            if len(p)!=5:reject('FN_FORMAT')
            node,d,eq=map(int,p[1:4]);f=finite(p[4])
            if not 1<=node<=hdr[3] or not 1<=d<=3 or (node,d) in nodal:
                reject('FN_OWNER')
            # CalculiX 2.21 mastruct.c encodes MPC-dependent DOFs as
            # -(2*i+1), i=0..nmpc-1; SPC DOFs use negative even IDs.
            # Do not misclassify ordinary constraint IDs as invalid forces.
            if eq < 0 and eq % 2 and eq < -(2*hdr[5]-1):
                reject('FN_MPC_INDEX')
            if f==0:reject('FN_ZERO')
            nodal[(node,d)]=(f,eq)
        elif tag=='KB_WORK_MPC':
            if len(p)!=3 or p[2] not in ('MEANROT','FLUID','KNOT','OTHER'):reject('MPC_FORMAT')
            m=integers(p[1]);
            if m in mpcs or m!=len(mpcs)+1:reject('MPC_ORDER')
            mpcs[m]={'tag':p[2],'terms':[]}
        elif tag=='KB_WORK_TERM':
            if len(p)!=6:reject('TERM_FORMAT')
            m,k,n,d=map(integers,p[1:5]);c=finite(p[5]);
            if m not in mpcs or k!=len(mpcs[m]['terms'])+1 or n>hdr[3] or d>max(6,hdr[4]-1):reject('TERM_OWNER')
            if any(node==n and direc==d for node,direc,_ in mpcs[m]['terms']):reject('DUPLICATE_TERM')
            mpcs[m]['terms'].append((n,d,c))
        elif tag=='KB_WORK_END':
            if len(p)!=1:reject('END_FORMAT')
            ended=True
        else:reject('UNKNOWN_'+tag)
    if not ended or hdr is None or len(mpcs)!=hdr[5]:reject('MPC_COVERAGE')
    if not nodal:reject('FN_EMPTY')
    return {'header':hdr,'fn':nodal,'mpcs':mpcs}

def eliminate(work):
    f={nd:x[0] for nd,x in work['fn'].items()}
    coefficients={}
    for m,entry in work['mpcs'].items():
        if entry['tag']=='FLUID':continue
        terms=entry['terms']
        if not terms:reject('EMPTY_MPC')
        depnode,depd,depcoef=terms[0]
        # Match original CCX resultsforc.c: dependent directions above 3
        # are explicitly skipped, not interpreted as expanded translations.
        if depd>3:continue
        if not depcoef or not math.isfinite(depcoef):reject('INVALID_DEPENDENT_COEF')
        if any(d>3 for _,d,_ in terms):reject('ROTATIONAL_MPC_UNSUPPORTED')
        force=f.get((depnode,depd),0)/depcoef
        if not math.isfinite(force):reject('NONFINITE_ELIMINATION')
        coefficients[m]=force
        f[(depnode,depd)]=0.
        for node,d,coef in terms[1:]:
            key=node,d
            f[key]=f.get(key,0.)-coef*force
            if not math.isfinite(f[key]):reject('NONFINITE_ELIMINATION')
    return f,coefficients

def parse_old_dual(txt):
    out={};spc={}
    for row in txt.splitlines():
        p=row.split()
        if len(p)==3 and p[0]=='KB_ROT_MPC':
            m=integers(p[1]);
            if m in out:reject('OLD_DUP_MPC')
            out[m]=finite(p[2])
        if len(p)==8 and p[:2]==['KB_ROT_SPC','Q']:
            pair=(integers(p[3]),integers(p[4]));
            if pair in spc:reject('OLD_DUP_SPC')
            spc[pair]=finite(p[6])
    if not out or not spc:reject('OLD_TRACE_MISSING')
    return out,spc

def input_mode(deck):
    entries=re.findall(r'(?m)^(\d+),5,5,([-+]?[0-9.]+)$',deck.split('*STEP,',1)[-1]);
    if not entries:reject('MISSING_DOF5')
    angles={int(i):finite(v) for i,v in entries}
    if len(angles)!=len(entries):reject('DUP_DOF5')
    m=re.search(r'(?m)^\*NSET,NSET=PLATE_EDGE_RF\s*\n([^*]+)',deck)
    if not m:reject('EDGE_SET')
    node_ids={int(x) for x in re.findall(r'\d+',m.group(1))}
    if node_ids!=set(angles):reject('INPUT_COVERAGE')
    xcoord={}
    for row in deck.split('*NODE\n',1)[1].split('*ELEMENT,',1)[0].splitlines():
        p=[t.strip() for t in row.split(',')]
        if len(p)==4:xcoord[int(p[0])]=finite(p[1])
    if not node_ids<=set(xcoord):reject('INPUT_COORDS')
    return angles,{n:(xcoord[n]-600.)/600. for n in node_ids}

def owner_angle_map(txt, angles, spc):
    mapped={}
    for row in txt.splitlines():
        p=row.split()
        if len(p)!=9 or p[0]!='KB_ROT_OWNER':reject('OWNER_ROW')
        origin,axis,ordinal,aux=int(p[1]),int(p[2]),int(p[3]),int(p[5])
        if origin not in angles or axis!=2 or ordinal!=2:continue
        if origin in mapped or abs(finite(p[7])-angles[origin])>1e-13:reject('OWNER_ANGLE')
        if (aux,1) not in spc or abs(spc[(aux,1)]-angles[origin])>1e-13:reject('OWNER_SPC')
        mapped[origin]=(aux,1)
    if set(mapped)!=set(angles):reject('OWNER_COVERAGE')
    if len(set(mapped.values()))!=len(mapped):reject('OWNER_DUP_AUX')
    return mapped

def signed_slope(energies):
    return (energies['plus1']-energies['minus1'])/(2e-5)

def audit(source_zip:Path,owner_zip:Path,dual_zip:Path)->dict:
    for f,expected in ((source_zip,SOURCE_SHA),(owner_zip,OWNER_SHA)):
        if hashlib.sha256(f.read_bytes()).hexdigest()!=expected:reject('PIN')
    result={}
    with zipfile.ZipFile(source_zip) as source,zipfile.ZipFile(owner_zip) as owner,zipfile.ZipFile(dual_zip) as dual:
        mb=source.read('manifest.json')
        if hashlib.sha256(mb).hexdigest()!=MANIFEST_SHA:reject('MANIFEST')
        manifests=json.loads(mb)['cases']
        for key in CASES:
            deck=source.read(key+'/panel.inp')
            if hashlib.sha256(deck).hexdigest()!=manifests[key]['input_sha256']:reject('DECK_PIN')
            model=deck.decode('ascii');angles,w=input_mode(model)
            try:
                work=parse_work(dual.read('rot-dual/'+key+'/kb_rot_full_work.tsv').decode('ascii'))
                prev,spc=parse_old_dual(dual.read('rot-dual/'+key+'/kb_rot_dual.tsv').decode('ascii'))
            except KeyError:reject('ARTIFACT_COVERAGE')
            mapped=owner_angle_map(owner.read('rot-owner/'+key+'/kb_rot_owner.tsv').decode('ascii'),angles,spc)
            for ext in ('dat','sta'):
                if source.read(key+'/panel.'+ext)!=dual.read('rot-dual/'+key+'/panel.'+ext):reject('AB_'+ext.upper())
            reduced,multipliers=eliminate(work)
            if set(multipliers).intersection(prev)!=set(prev):reject('MEANROT_COVERAGE')
            diffs={m:abs(multipliers[m]-val) for m,val in prev.items()}
            maxdiff=max(diffs.values())
            max_ref=max(abs(v) for v in prev.values())
            # Replay should agree to double precision except cancellation noise,
            # and this threshold does not perform physics admission.
            if maxdiff>1e-8+1e-11*max_ref:reject('REPLAY_MISMATCH')
            q=math.fsum(reduced[mapped[n]]*w[n] for n in sorted(mapped))
            result[key]={'nk':work['header'][3],'mpc':work['header'][5],
                'nonzero_pre_fn':len(work['fn']),
                'observed_meanrot_fmpc':len(prev),
                'max_meanrot_fmpc_replay_abs_n':maxdiff,
                'all_mpc_reduced_spc_dof5_candidate_nmm':q,
                'actual_dual':'NOT_ESTABLISHED'}
    return {'status':'COMPLETE_MPC_ALGORITHM_REPLAY_ONLY','cases':result,
        'dual_zip_sha256':hashlib.sha256(dual_zip.read_bytes()).hexdigest(),
        'physical_support_moment':'NOT_ESTABLISHED',
        'six_component_equilibrium':'NOT_ADMITTED',
        'engineering_acceptance':'NOT_ADMITTED'}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('source_zip',type=Path)
    p.add_argument('owner_zip',type=Path);p.add_argument('dual_zip',type=Path)
    a=p.parse_args();print(json.dumps(audit(a.source_zip,a.owner_zip,a.dual_zip),indent=2,sort_keys=True,allow_nan=False))
