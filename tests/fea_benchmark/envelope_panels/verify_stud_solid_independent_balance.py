"""Independent synthetic four-station C3D20R rib-reaction crosscheck; NOT DESIGN.

Requires an unmodified pinned true CCX 2.21 six-case ZIP. In a case with
no rib external loads, compare the clean rib-end SPC RF3 to the negative
sum of independently calculated four SPRING2 k * relative-U3 forces.
SPRING2 native element force and real welded-stud stiffness remain unproven.
"""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from zipfile import ZipFile

PIN='03cda477016e945c5f76a5b88a0548a08027c62ec777e4d5e7afec4c6b0e7f7a'
STATIONS=(150.,450.,750.,1050.)
K={'unlinked':0.,'soft':50.,'stiff':500.}
NUM=r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?'
ROW=re.compile(r'^\s*(\d+)\s+('+NUM+r')\s+('+NUM+r')\s+('+NUM+r')\s*$')


def fail(message):
    raise ValueError('STUD_INDEPENDENT_'+message)


def final_field(dat,kind,name):
    if kind not in ('displacements','forces') or name not in ('STUD_PLATE','STUD_RIB','RIB_END_RF'):
        fail('FIELD_SCOPE')
    pat=re.compile(r'(?im)^\s*'+kind+r'\s+\([^\n]*\)\s+for set\s+'+name+r'\s+and time\s+('+NUM+r')\s*$')
    found=list(pat.finditer(dat))
    if not found or abs(float(found[-1].group(1).replace('D','E'))-1.)>1e-7:
        fail('FINAL_FIELD')
    result={}
    for line in dat[found[-1].end():].splitlines():
        if not line.strip():
            if result:break
            continue
        row=ROW.fullmatch(line)
        if row:
            node=int(row.group(1))
            vals=tuple(float(row.group(i).replace('D','E')) for i in (2,3,4))
            if node in result or not all(map(math.isfinite,vals)):
                fail('BAD_FIELD_ROW')
            result[node]=vals
        elif result:
            break
    if not result:fail('EMPTY_FIELD')
    return result


def node_sets(inp):
    want={'STUD_PLATE','STUD_RIB','RIB_END_RF'}
    groups={}
    active=None
    for line in inp.splitlines():
        if line.startswith('*'):
            m=re.fullmatch(r'\*NSET,NSET=([A-Z_]+)',line)
            active=m.group(1) if m and m.group(1) in want else None
            if active:
                if active in groups:fail('DUPLICATE_SET')
                groups[active]=[]
        elif active:
            groups[active].extend(int(i) for i in line.split(',') if i.strip())
    if set(groups)!=want or len(groups['STUD_PLATE'])!=4 or len(groups['STUD_RIB'])!=4 or not groups['RIB_END_RF']:
        fail('STATION_NODE_COVERAGE')
    return groups


def input_guard(inp,case,groups):
    if case not in K:fail('CASE_SCOPE')
    if ('*CONTACT PAIR' in inp or '*CLOAD' in inp or '*DSLOAD' in inp or
        inp.count('*DLOAD\nPLATE,P1,0.00010000\n')!=1 or
        inp.count('RIB_END_RF,1,3,0.')!=1):
        fail('EXTERNAL_RIB_LOAD_OR_CONTACT')
    keyword='*ELEMENT,TYPE=SPRING2,ELSET=STUD_LINK_SYNTHETIC\n'
    if case=='unlinked':
        if keyword in inp:fail('UNLINKED_SPRINGS')
    else:
        if inp.count(keyword)!=1 or inp.count('*SPRING,ELSET=STUD_LINK_SYNTHETIC\n3,3\n')!=1:
            fail('SPRING_DEFINITION')
        if f'\n{K[case]:.8f}\n' not in inp:fail('WRONG_K')
        values=inp.split(keyword,1)[1].split('*',1)[0]
        links=[tuple(int(x) for x in line.split(',')) for line in values.splitlines() if line.strip()]
        if len(links)!=4 or [pair[1:] for pair in links]!=list(zip(groups['STUD_PLATE'],groups['STUD_RIB'])):
            fail('CONNECTION_NODE_PAIRS')


def check_pair(forces,rib_reaction,case):
    if case not in K or len(forces)!=4 or any(not math.isfinite(x) for x in forces) or not math.isfinite(rib_reaction):
        fail('BAD_FORCE_INPUT')
    total=math.fsum(forces)
    residual=math.fsum((total,rib_reaction))
    if abs(residual)>0.002:fail('RIB_ACTION_REACTION')
    if case=='unlinked':
        if any(forces) or abs(rib_reaction)>0.002:fail('UNLINKED_FORCE')
    else:
        if min(forces)<=0:fail('TRANSFER_DIRECTION')
        if abs(forces[0]-forces[3])>0.002 or abs(forces[1]-forces[2])>0.002:
            fail('STATION_SYMMETRY')
    return total,residual


def verify(path):
    file=Path(path)
    if file.is_symlink() or not file.is_file() or not 0<file.stat().st_size<32_000_000:
        fail('SOURCE_FILE')
    with file.open('rb') as stream:
        if hashlib.file_digest(stream,'sha256').hexdigest()!=PIN:fail('ARTIFACT_SHA256')
    output=[]
    with ZipFile(file) as z:
        for n in (8,16):
            for case,k in K.items():
                root=f'stud_{n}_{case}/panel.'
                inp=z.read(root+'inp').decode('utf8')
                dat=z.read(root+'dat').decode('utf8',errors='replace')
                sta=z.read(root+'sta').decode('utf8')
                completed=[]
                for line in sta.splitlines():
                    vals=line.split()
                    if len(vals)==7 and vals[0]=='1' and vals[1].isdigit() and vals[2].isdigit():
                        completed.append(float(vals[4]))
                if not completed or abs(completed[-1]-1)>1e-7:fail('INCOMPLETE_SOLVE')
                sets=node_sets(inp)
                input_guard(inp,case,sets)
                plate=final_field(dat,'displacements','STUD_PLATE')
                rib=final_field(dat,'displacements','STUD_RIB')
                rf=final_field(dat,'forces','RIB_END_RF')
                if set(plate)!=set(sets['STUD_PLATE']) or set(rib)!=set(sets['STUD_RIB']) or set(rf)!=set(sets['RIB_END_RF']):
                    fail('OBSERVATION_NODE_COVERAGE')
                forces=[k*(plate[p][2]-rib[q][2]) for p,q in zip(sets['STUD_PLATE'],sets['STUD_RIB'])]
                reaction=math.fsum(vec[2] for vec in rf.values())
                force,residual=check_pair(forces,reaction,case)
                output.append({'mesh':n,'case':case,'positions_mm':STATIONS,
                    'synthetic_k_per_link_n_per_mm':k,'four_derived_link_forces_n':forces,
                    'derived_total_n':force,'rib_support_observed_rf3_n':reaction,
                    'independent_transfer_balance_residual_n':residual})
    return {'scope':'SYNTHETIC_4_STATION_RIB_REACTION_CROSSCHECK_NOT_DESIGN',
            'pinned_artifact_sha256':PIN,'cases':output,
            'native_spring_element_force':'NOT_OBSERVED',
            'physical_stud_calibration_and_capacity':'NOT_ADMITTED',
            'engineering_acceptance':'NOT_ADMITTED'}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('artifact_zip')
    args=parser.parse_args()
    print(json.dumps(verify(args.artifact_zip),indent=2,sort_keys=True,allow_nan=False))
