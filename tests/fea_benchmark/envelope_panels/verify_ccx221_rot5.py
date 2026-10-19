"""Parse research-only DOF5 finite differences; never admit shell reactions."""
from __future__ import annotations
import argparse,hashlib,json,math,re
from pathlib import Path
from generate_ccx221_rot5 import ANGLES,PINS
NUM=r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?'
ENERGY={'plate':'total internal energy for set PLATE and time','rib':'total internal energy for set RIB and time','contact':'total contact spring energy for time'}
def fail(x):raise ValueError('CCX221_ROT_OBSERVE_'+x)
def finite(s):
    try:v=float(s.replace('D','E'))
    except ValueError:fail('BAD_NUMBER')
    if not math.isfinite(v):fail('NONFINITE')
    return v
def scalar(dat,label):
    hits=list(re.finditer(r'(?m)^\s*'+re.escape(label)+r'\s+('+NUM+r')\s*\n\s*\n\s*([^\n]+)',dat))
    vals=[]
    for h in hits:
        if abs(finite(h.group(1))-1)<1e-8:
            tokens=h.group(2).split()
            if len(tokens)!=1:fail('SCALAR_FORMAT')
            vals.append(finite(tokens[0]))
    if not vals:fail('FINAL_ENERGY_MISSING')
    if max(vals)-min(vals)>1e-7:fail('DUPLICATE_ENERGY')
    return vals[-1]
def observe(root:Path):
    obj=json.loads((root/'manifest.json').read_text())
    if obj.get('admission')!='NOT_ADMITTED':fail('ADMISSION')
    cases=obj['cases']
    expected={f'n{m}/{b}/{k}' for m in PINS for b in ('contact','no_contact') for k in ANGLES}
    if set(cases)!=expected:fail('CASE_COVERAGE')
    rows={}
    for key,record in sorted(cases.items()):
        mesh=int(key.split('/')[0][1:]);branch=key.split('/')[1];k=key.split('/')[2]
        if record['mesh']!=mesh or record['branch']!=branch or record['source_sha256']!=PINS[mesh] or record['mode']!='LINEAR_X_ANTISYMMETRIC_NOT_RIGID_ROTATION':fail('MANIFEST')
        folder=root/key;deck=(folder/'panel.inp').read_bytes()
        if hashlib.sha256(deck).hexdigest()!=record['input_sha256']:fail('SHA')
        text=deck.decode('ascii')
        if ('*CONTACT PAIR' in text)!=(branch=='contact'):fail('CONTACT_SCOPE')
        if text.count('*EL PRINT')!=2:fail('ENERGY_SCOPE')
        if not re.search(r'(?m)^\s*RIB_END_RF,1,6,0\.$',text):fail('RIB_CONSTRAINT')
        if text.count('CENTER_RF,3,3,0.02000000')!=1:fail('CENTER_SCOPE')
        sta=(folder/'panel.sta').read_text()
        sta_rows=[]
        for line in sta.splitlines():
            cols=line.split()
            if len(cols)==7 and cols[0]=='1' and cols[1].isdigit():
                sta_rows.append((int(cols[1]),finite(cols[4]),finite(cols[5])))
        if not sta_rows or max(abs(t-1) for t in sta_rows[-1][1:])>1e-8:fail('NOT_CONVERGED')
        dat=(folder/'panel.dat').read_text(encoding='latin-1')
        energies={name:scalar(dat,label) for name,label in ENERGY.items() if name!='contact' or branch=='contact'}
        if branch=='no_contact' and 'total contact spring energy' in dat:fail('CONTACT_LEAK')
        rows[key]={'parts':energies,'candidate_energy':math.fsum(energies.values())}
    result={}
    for m in PINS:
        for branch in ('contact','no_contact'):
            root_key=f'n{m}/{branch}/'
            r={k:rows[root_key+k]['candidate_energy'] for k in ANGLES}
            derivatives={}
            for i,h in [(1,1e-5),(2,2e-5)]:
                derivatives[str(h)]={'central_nmm':(r[f'plus{i}']-r[f'minus{i}'])/(2*h),
                   'forward_nmm':(r[f'plus{i}']-r['zero'])/h,
                   'backward_nmm':(r['zero']-r[f'minus{i}'])/h}
            result[root_key[:-1]]={'baseline_candidate_energy':r['zero'],'derivatives':derivatives}
    return {'status':'SHELL_DOF5_RESEARCH_OBSERVATION_ONLY','case_count':len(rows),'results':result,'rotational_mpc_reaction_admission':'NOT_ESTABLISHED','contact_energy_additivity':'UNVERIFIED','engineering_acceptance':'NOT_ADMITTED'}
if __name__=='__main__':
    pa=argparse.ArgumentParser();pa.add_argument('root',type=Path);args=pa.parse_args();print(json.dumps(observe(args.root),indent=2,sort_keys=True,allow_nan=False))
