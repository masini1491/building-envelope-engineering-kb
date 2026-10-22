"""Fail-closed six-case C3D20R spring Z connector pilot."""
import json,math,re,sys
from pathlib import Path
from stud_solid_trial import deck,CASES,MESHES,STATIONS
from verify_c3d20r_u_contact import status
from check_u_rib_contact_observations import rf
from verify_pressure_contact_trial import nominal_pressure_equivalents
NUM=r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?'
def field(dat,label,expected):
    headers=list(re.finditer(r'(?im)^\s*displacements\s+\([^\n]*\)\s+for set '+label+r'\s+and time\s+('+NUM+r')\s*$',dat))
    if not headers or abs(float(headers[-1].group(1))-1)>1e-7:raise ValueError('STUD_FIELD_HEADER_'+label)
    rows={}
    regex=re.compile(r'^\s*(\d+)\s+('+NUM+r')\s+('+NUM+r')\s+('+NUM+r')\s*$')
    for line in dat[headers[-1].end():].splitlines():
        if not line.strip():
            if rows:break
            continue
        m=regex.fullmatch(line)
        if m:
            k=int(m.group(1))
            if k in rows:raise ValueError('STUD_DUPLICATE')
            rows[k]=tuple(float(m.group(i).replace('D','E')) for i in (2,3,4))
        elif rows:break
    if set(rows)!=set(expected):raise ValueError('STUD_FIELD_COVERAGE_'+label)
    return rows
def sets(inp):
    out={};active=None
    for line in inp.splitlines():
        if line.startswith('*'):
            m=re.fullmatch(r'\*NSET,NSET=(PLATE_EDGE_RF|RIB_END_RF|CENTER_RF|STUD_PLATE|STUD_RIB)',line)
            active=m.group(1) if m else None
            if active:out[active]=[]
        elif active:out[active].extend(int(v) for v in line.split(',') if v.strip())
    if len(out)!=5 or any(not v for v in out.values()):raise ValueError('STUD_NSET')
    return out
def verify(root):
    report=[]
    for n in MESHES:
        values={}
        for case,k in CASES.items():
            folder=Path(root)/f'stud_{n}_{case}'
            files={ext:folder/f'panel.{ext}' for ext in ('inp','dat','sta','frd')}
            if any(not f.is_file() or f.is_symlink() or not f.stat().st_size for f in files.values()):
                raise ValueError('STUD_FILES')
            inp=files['inp'].read_text()
            if inp!=deck(n,case):raise ValueError('STUD_INPUT_PROVENANCE')
            status(files['sta'].read_text())
            groups=sets(inp);dat=files['dat'].read_text(errors='replace')
            plate=field(dat,'STUD_PLATE',groups['STUD_PLATE'])
            rib=field(dat,'STUD_RIB',groups['STUD_RIB'])
            center=field(dat,'CENTER_RF',groups['CENTER_RF'])
            u=sum(v[2] for v in center.values())/len(center)
            if not math.isfinite(u) or u<=0:raise ValueError('STUD_CENTER')
            transferred=[]
            for i in range(4):
                transferred.append(k*(plate[groups['STUD_PLATE'][i]][2]-rib[groups['STUD_RIB'][i]][2]))
            if k and max(abs(x) for x in transferred)<1e-8:raise ValueError('STUD_INACTIVE')
            if not k and any(transferred):raise ValueError('STUD_UNLINKED')
            rf3=sum(rf(dat,s,expected_nodes=groups[s])['sum_rf3_n'] for s in ('PLATE_EDGE_RF','RIB_END_RF'))
            balance=rf3-nominal_pressure_equivalents(n)['edge_pressure_n']+36.
            if abs(balance)>.002:raise ValueError('STUD_BALANCE')
            values[case]=u
            report.append({'mesh':n,'case':case,'center_u3_mm':u,'four_derived_link_forces_n':transferred,'nominal_z_balance_n':balance,'stiffness_n_mm':k})
        if not values['unlinked']>values['soft']>values['stiff']>0:
            raise ValueError('STUD_MONOTONICITY')
    return {'scope':'SYNTHETIC_C3D20R_FOUR_STATION_Z_SPRING_ONLY','cases':report,'real_stud_stiffness_and_capacity':'NOT_ADMITTED','spring_transfer_oracle':'DERIVED_K_TIMES_DELTA_U_ONLY','engineering_acceptance':'NOT_ADMITTED'}
if __name__=='__main__':
    print(json.dumps(verify(sys.argv[1]),indent=2))
