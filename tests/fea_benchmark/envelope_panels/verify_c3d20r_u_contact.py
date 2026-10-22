"""Read-only C3D20R six-case force/contact and FRD gap screen; NOT DESIGN."""
import argparse,hashlib,json,math,re
from pathlib import Path
from quadratic_contact_trial import deck
from check_u_rib_contact_observations import rf, contact_print

MESHES=(8,16)
CASES=('toward','unlinked','clearance')
SETS=('PLATE_EDGE_RF','RIB_END_RF','CENTER_RF')
# Original synthetic C3D8 comparator absolute observation bound.
ABS_N=0.002
REL=0.025
FLOAT=re.compile(r'[+-]?\d+\.\d+E[+-]\d+')

def reject(s): raise ValueError('C3D20R_'+s)

def status(sta):
    incs=[]; pending=0
    for line in sta.splitlines():
        a=line.split()
        if len(a)!=7 or not a[0].isdigit(): continue
        if a[0]!='1' or not a[1].isdigit():reject('STA_STEP')
        att=a[2]; failed=att.endswith('U'); number=att[:-1] if failed else att
        if not number.isdigit():reject('STA_ATT')
        inc=int(a[1]);attempt=int(number)
        try: it=int(a[3]);t=float(a[4]);dt=float(a[6])
        except ValueError:reject('STA_NUMBER')
        if not all(map(math.isfinite,(t,dt))) or it<1 or dt<=0 or inc!=len(incs)+1 or attempt<=pending or (incs and t<incs[-1][1]):
            reject('STA_SEQUENCE')
        pending=attempt
        if not failed:incs.append((inc,t));pending=0
    if not incs or abs(incs[-1][1]-1)>1e-7:reject('STA_INCOMPLETE')
    return len(incs)

def parse_input(inp):
    sets={};nodes={};bodies={'PLATE':set(),'RIB':set()}
    section=None;pending=[]
    for line in inp.splitlines():
        t=line.strip()
        if t=='*NODE':section='NODE';continue
        m=re.fullmatch(r'\*ELEMENT,TYPE=C3D20R,ELSET=(PLATE|RIB)',t)
        if m:section=m.group(1);pending=[];continue
        m=re.fullmatch(r'\*NSET,NSET=(PLATE_EDGE_RF|RIB_END_RF|CENTER_RF)',t)
        if m:
            section=m.group(1)
            if section in sets:reject('DUPLICATE_NSET')
            sets[section]=set();continue
        if t.startswith('*'):section=None;continue
        if not t or section is None:continue
        if section=='NODE':
            v=t.split(',')
            if len(v)!=4:reject('NODE_ROW')
            k=int(v[0])
            if k in nodes:reject('NODE_DUPLICATE')
            nodes[k]=tuple(map(float,v[1:]))
        elif section in bodies:
            ids=[int(z) for z in t.split(',') if z.strip()]
            pending.extend(ids)
            if len(pending)==21:
                bodies[section].update(pending[1:]);pending=[]
            elif len(pending)>21:reject('ELEMENT_CONN')
        elif section in SETS:
            for z in t.split(','):
                if z.strip():
                    i=int(z)
                    if i in sets[section]:reject('NSET_DUPLICATE_NODE')
                    sets[section].add(i)
    if set(sets)!=set(SETS) or not all(sets.values()) or not all(bodies.values()) or bodies['PLATE']&bodies['RIB']:
        reject('SETS')
    if set(nodes)!=bodies['PLATE']|bodies['RIB'] or any(not v<=set(nodes) for v in sets.values()):reject('COVERAGE')
    if sum(map(len,sets.values()))!=len(set().union(*sets.values())):reject('NSET_OVERLAP')
    return sets,nodes,bodies

def deformed_gap(frd,nodes,bodies):
    lines=frd.splitlines()
    starts=[i for i,line in enumerate(lines) if line.strip().startswith('-4  DISP')]
    if not starts:reject('DISPLACEMENT_BLOCK_MISSING')
    disps={}
    for line in lines[starts[-1]+5:]:
        if line.startswith(' -3'):break
        if line.startswith(' -1'):
            i=int(line[3:13].strip());v=tuple(float(x) for x in FLOAT.findall(line[13:]))
            if i in disps or len(v)!=3 or not all(map(math.isfinite,v)):reject('BAD_FRD_DISPLACEMENT')
            disps[i]=v
    if set(disps)!=set(nodes):reject('FRD_NODE_COVERAGE')
    plate_top=max(nodes[k][2]+disps[k][2] for k in bodies['PLATE'])
    rib_bottom=min(nodes[k][2]+disps[k][2] for k in bodies['RIB'])
    gap=rib_bottom-plate_top
    if not math.isfinite(gap) or gap<=0:reject('CLEARANCE_DEFORMED_GAP')
    return gap

def verify_case(root,n,case):
    loc=Path(root)/f'n{n}_{case}'
    files={s:loc/f'panel.{s}' for s in ('inp','sta','dat','frd')}
    for ext,p in files.items():
        if p.is_symlink() or not p.is_file() or not 0<p.stat().st_size<(64_000_000 if ext=='frd' else 16_000_000):reject('FILE_'+ext)
    inp=files['inp'].read_text()
    if files['inp'].read_bytes()!=deck(n,case).encode():reject('INPUT_PROVENANCE')
    sets,nodes,bodies=parse_input(inp)
    count=status(files['sta'].read_text())
    dat=files['dat'].read_text(errors='replace')
    sums={k:rf(dat,k,expected_nodes=v)['sum_rf3_n'] for k,v in sets.items()}
    total=math.fsum(sums.values());scale=math.fsum(abs(x) for x in sums.values())
    if abs(total)>max(ABS_N,REL*scale):reject('RF3_IMBALANCE')
    cp=None
    if case=='unlinked':
        if 'statistics for slave set' in dat:reject('UNLINKED_FALSE_CONTACT')
    else:
        cp=contact_print(dat)
        if case=='toward':
            if cp['contact_statistics_state']!='FINITE_SURFACE_STATISTICS' or cp['contact_area_mm2']<=0 or cp['slave_total_force_n'][2]<=0:reject('TOWARD_CONTACT')
            if abs(sums['RIB_END_RF']+cp['slave_total_force_n'][2])>ABS_N:reject('RIB_CONTACT_PAIR_FORCE')
        else:
            if cp['contact_statistics_state']!='INACTIVE_ZERO_AREA_UNDEFINED_NORMAL_AND_SHEAR' or cp['contact_area_mm2']!=0 or any(x!=0 for x in cp['slave_total_force_n']):reject('CLEARANCE_CONTACT')
    if case!='toward' and abs(sums['RIB_END_RF'])>ABS_N:reject('INACTIVE_RIB_TRANSFER')
    gap=deformed_gap(files['frd'].read_text(errors='replace'),nodes,bodies) if case=='clearance' else None
    return {'mesh':n,'case':case,'increments':count,'raw_support_rf3_n':sums,'raw_rf3_residual_n':total,
            'contact':cp,'deformed_envelope_gap_mm':gap,
            'sha256':{s:hashlib.sha256(p.read_bytes()).hexdigest() for s,p in files.items()},
            'status':'BOUNDED_SYNTHETIC_OBSERVATION_ONLY'}

def verify(root):
    results=[verify_case(root,n,c) for n in MESHES for c in CASES]
    pressures={n:next(x['contact'] for x in results if x['mesh']==n and x['case']=='toward') for n in MESHES}
    return {'scope':'SYNTHETIC_C3D20R_OPEN_U_NOT_DESIGN','cases':results,
      'contact_force_difference_n8_n16_n':pressures[8]['slave_total_force_n'][2]-pressures[16]['slave_total_force_n'][2],
      'contact_area_ratio_n8_n16':pressures[8]['contact_area_mm2']/pressures[16]['contact_area_mm2'],
      'mesh_convergence':'NOT_ESTABLISHED','independent_bending_oracle':'NOT_ESTABLISHED',
      'contact_capacity':'NOT_ADMITTED','engineering_acceptance':'NOT_ADMITTED'}

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('root')
    print(json.dumps(verify(a.parse_args().root),indent=2,sort_keys=True,allow_nan=False))
