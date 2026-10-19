"""Exact-artifact, read-only CCX 2.21 DOF5 contact-state reconciliation.

Interprets CDIS/CSTR/CELS as solver-reported contact observations only.
Never admits physical contact capacity, MPC torque or shell reactions.
"""
from __future__ import annotations
import argparse, hashlib, json, math, re, zipfile
from collections import Counter
from pathlib import Path

PINS = {
    'original_zip': 'd9b36c420feca6a5f8cd50dc8cb07dbba6c2ebbbf0224abb4df57fbfd2291a8b',
    'pressure_zip': '5a025b9f7e87ec3b03078cfaddc4fc11e3bfdcd04c2ce95eec97076d6bc45354',
    'source_manifest': 'd4af3bb7edbd06b5acba0343f07a8932281cd3221d35036daea31bdf6025fd9b',
}
CASES = [f'n{n}/contact/{trial}' for n, trials in ((8,('minus1','zero','plus1')),(16,('minus2','minus1','zero','plus1','plus2'))) for trial in trials]
LABELS = {'energy':'contact spring energy (slave element+face,energy)',
          'gap':'relative contact displacement (slave element+face,normal,tang1,tang2)',
          'pressure':'contact stress (slave element+face,press,tang1,tang2)'}
SCI = re.compile(r'^[+-]?\d\.\d{6}E[+-]\d\d$')

def reject(code): raise ValueError('CCX221_CONTACT_STATE_'+code)
def sha(b): return hashlib.sha256(b).hexdigest()
def num(s):
    if not SCI.fullmatch(s):reject('NUMBER_FORMAT')
    v=float(s)
    if not math.isfinite(v):reject('NONFINITE')
    return v

def final_rows(t, label, suffix='and time'):
    pattern=r'(?m)^\s*'+re.escape(label)+r' for all contact elements '+suffix+r'\s+([^\n]+)\n'
    matches=[m for m in re.finditer(pattern,t) if abs(float(m.group(1))-1.)<1e-8]
    if len(matches)!=1:reject('FINAL_'+label[:7].upper()+'_COVERAGE')
    block=t[matches[0].end():].split('\n\n',1)[0].strip()
    out=[]
    for row in block.splitlines():
        v=row.split()
        if len(v)!= (3 if label==LABELS['energy'] else 5):reject('ROW_FIELDS')
        try: i,j=int(v[0]),int(v[1])
        except ValueError:reject('ROW_ID')
        if i<1 or j<1:reject('ROW_ID')
        out.append((i,j,*(num(s) for s in v[2:])))
    if not out:reject('NO_ROWS')
    return out

def final_scalar(t,label,suffix='for time'):
    matches=[m for m in re.finditer(r'(?m)^\s*'+re.escape(label)+r' '+suffix+r'\s+([^\n]+)\n\s*\n\s*([^\n]+)',t)
             if abs(float(m.group(1))-1.)<1e-8]
    if len(matches)!=1:reject('TOTAL_COVERAGE')
    return num(matches[0].group(2).strip())

def final_force(t):
    h='total surface force (fx,fy,fz) and moment about the origin (mx,my,mz)'
    matches=list(re.finditer(r'(?m)^\s*'+re.escape(h)+r'\s*\n\s*([^\n]+)',t))
    if len(matches)<2:reject('FORCE_COVERAGE')
    v=[num(x) for x in matches[-1].group(1).split()]
    if len(v)!=6:reject('FORCE_DIMENSION')
    return v

def analyze(orig_zip:Path,pressure_zip:Path):
    raw_o,raw_n=orig_zip.read_bytes(),pressure_zip.read_bytes()
    if sha(raw_o)!=PINS['original_zip'] or sha(raw_n)!=PINS['pressure_zip']:reject('ARTIFACT_PROVENANCE')
    with zipfile.ZipFile(orig_zip) as orig,zipfile.ZipFile(pressure_zip) as now:
        manifest_raw=orig.read('manifest.json')
        if sha(manifest_raw)!=PINS['source_manifest']:reject('MANIFEST_PROVENANCE')
        previous=json.loads(manifest_raw)
        latest=json.loads(now.read('rot5-pressure/manifest.json'))
        if latest.get('engineering_acceptance')!='NOT_ADMITTED' or set(latest['cases'])!=set(CASES):reject('MANIFEST_SCOPE')
        report={}
        for key in CASES:
            before=key+'/'
            after='rot5-pressure/'+before
            old=orig.read(before+'panel.inp');new=now.read(after+'panel.inp')
            if sha(old)!=previous['cases'][key]['input_sha256'] or sha(old)!=latest['cases'][key]['source_input_sha256'] or sha(new)!=latest['cases'][key]['pressure_input_sha256']:reject('INPUT_PROVENANCE')
            if old.replace(b'CF,CFN,CNUM,CELS\n',b'CF,CFN,CNUM,CELS,CDIS,CSTR\n')!=new:reject('INPUT_MUTATION')
            current=now.read(after+'panel.dat').decode('ascii')
            original=orig.read(before+'panel.dat').decode('ascii')
            rows={k:final_rows(current,h) for k,h in LABELS.items()}
            count=len(rows['energy'])
            if not all(len(r)==count for r in rows.values()):reject('ROW_COVERAGE')
            for i in range(count):
                a,b,c=(rows[k][i] for k in ('energy','gap','pressure'))
                if a[:2]!=b[:2] or a[:2]!=c[:2]:reject('SPRING_ORDER')
                gap,press=b[2],c[2]
                if gap>=0 or press<=0:reject('COMPRESSIVE_PAIR')
                if abs(press+100000*gap)>0.000002:reject('GAP_PRESSURE_RELATION')
            energies=[r[2] for r in rows['energy']]
            total=final_scalar(current,'total contact spring energy')
            if abs(math.fsum(energies)-total)>1e-10:reject('ENERGY_TOTAL')
            f1,f0=final_force(current),final_force(original)
            identical=(now.read(after+'panel.sta')==orig.read(before+'panel.sta') and f1==f0 and final_scalar(original,'total contact spring energy')==total)
            report[key]={'count':count,'slave_ids':dict(sorted(Counter(r[0] for r in rows['energy']).items())),
                         'positive_pressure_count':sum(r[2]>0 for r in rows['pressure']),
                         'negative_gap_count':sum(r[2]<0 for r in rows['gap']),
                         'positive_pressure_zero_reported_energy_count':sum(e==0 and rows['pressure'][i][2]>0 for i,e in enumerate(energies)),
                         'contact_f3_n':f1[2], 'baseline_contact_f3_n':f0[2],
                         'contact_f3_change_on_rerun_n':f1[2]-f0[2],
                         'original_and_new_solver_output_equal_in_checked_fields':identical,
                         'reported_contact_energy_nmm':total}
        for k in CASES:
            if report[k]['count']!=report[k]['positive_pressure_count']:reject('NOT_ALL_PRINTED_PAIRS_COMPRESSIVE')
        for n in (8,16):
            current=report[f'n{n}/contact/zero']['slave_ids']
            if n==16:
                for step in ('plus1','plus2'):
                    new=set(report[f'n{n}/contact/{step}']['slave_ids'])-set(current)
                    if new!={130,131,190,191}:reject('NEW_SLAVE_SET')
        return {'status':'SOLVER_REPORTED_CONTACT_COMPRESSION_CONFIRMED_WITHIN_PRINTED_ROWS',
                'count_cases':len(CASES),'results':report,
                'solver_reported_compression_not_independent_physics_oracle':True,
                'rotational_reaction_moment':'NOT_ESTABLISHED',
                'original_rf3_gate':'FAIL_CLOSED','engineering_acceptance':'NOT_ADMITTED'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('original_zip',type=Path);p.add_argument('pressure_zip',type=Path)
    a=p.parse_args();print(json.dumps(analyze(a.original_zip,a.pressure_zip),indent=2,sort_keys=True,allow_nan=False))
