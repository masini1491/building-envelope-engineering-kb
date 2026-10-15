"""Four-station discrete stud-link spring *analogue*; never a panel/rib FEA.

K values are arbitrary synthetic N/mm numbers. CalculiX SPRING1/SPRING2
DOF3 network is checked against an independent 8x8 matrix equilibrium and
energy identity. Coordinates follow the canonical U-rib stud geometry fixture;
there is NO physical mapping from 50x50x3 section to the spring stiffnesses.
"""
from __future__ import annotations
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from u_rib_stud_geometry import load

CASES = ('unlinked', 'soft', 'stiff')
STUD_K = {'unlinked': 0.0, 'soft': 50.0, 'stiff': 500.0}
P_GROUND, R_GROUND, P_CHAIN, R_CHAIN, LOAD = 100., 200., 40., 400., 1.
FIXTURE = Path(__file__).with_name('fixtures') / 'u_rib_stud_50x50_t3_synthetic.json'
NUM = r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?'
ROW = re.compile(r'^\s*(\d+)\s+('+NUM+r')\s+('+NUM+r')\s+('+NUM+r')\s*$')


def positions() -> tuple[float, ...]:
    g = load(FIXTURE)
    x = tuple(g['stud_centers']['positions_along_length_mm'])
    if (g['engineering_acceptance'] != 'NOT_ADMITTED' or
        g['finite_element_deck'] != 'NOT_GENERATED' or
        g['connection_transfer'] != 'NOT_ESTABLISHED' or
        g['scope'] != 'SHARP_CORNER_U_STIFFENER_SINGLE_CENTER_STUD_ROW_GEOMETRY_ONLY' or
        len(x) != 4 or x != (150., 450., 750., 1050.) or
        g['stud_centers']['nominal_pitch_mm'] != 300. or
        g['section']['outer_base_width_mm'] != 50. or
        g['section']['outer_height_from_panel_interface_mm'] != 50. or
        g['inputs']['rib_thickness_mm'] != 3. or
        g['inputs']['panel_thickness_mm'] != 3.):
        raise ValueError('STUD_ANALOGUE_FIXTURE_NOT_CANONICAL')
    return x


def edges(case: str):
    if case not in CASES:
        raise ValueError('STUD_ANALOGUE_CASE_NOT_ADMITTED')
    pos = positions()
    # Nodes 1-4 represent panel DOF3; 5-8 rib DOF3 at common axial positions.
    # Each node has synthetic ground compliance. Chains connect neighbors.
    base = [((i,), P_GROUND, 'PG') for i in range(1,5)]
    base += [((i,), R_GROUND, 'RG') for i in range(5,9)]
    base += [((i,i+1), P_CHAIN, 'PC') for i in range(1,4)]
    base += [((i,i+1), R_CHAIN, 'RC') for i in range(5,8)]
    if STUD_K[case]:
        base += [((i,i+4), STUD_K[case], 'STUD') for i in range(1,5)]
    return pos, base


def deck(case: str) -> str:
    pos, items = edges(case)
    groups = ('PG','RG','PC','RC','STUD')
    lines=['*HEADING','SYNTHETIC scalar 4 station spring-link analogue '+case,'*NODE']
    for i,x in enumerate(pos,1):
        lines += [f'{i},{x:.8f},0.,0.']
        lines += [f'{i+4},{x:.8f},10.,0.']
    for group in groups:
        part=[nodes for nodes,k,label in items if label==group]
        if not part:continue
        typ='SPRING1' if group in ('PG','RG') else 'SPRING2'
        lines += [f'*ELEMENT,TYPE={typ},ELSET={group}']
        for nodes in part:
            number=1+next(i for i,item in enumerate(items) if item[0]==nodes and item[2]==group)
            lines.append(f'{number},'+','.join(str(n) for n in nodes))
        k=next(k for nodes,k,label in items if label==group)
        lines += [f'*SPRING,ELSET={group}', '3' if typ=='SPRING1' else '3,3',f'{k:.8f}']
    lines += ['*NSET,NSET=PLATE','1,2,3,4','*NSET,NSET=RIB','5,6,7,8',
              '*BOUNDARY','PLATE,1,2,0.','RIB,1,2,0.',
              '*STEP','*STATIC','0.1,1.,0.00001,0.1',
              '*CLOAD',f'2,3,{LOAD:.8f}',
              '*NODE PRINT,NSET=PLATE','U',
              '*NODE PRINT,NSET=RIB','U',
              '*NODE FILE,OUTPUT=3D','U', '*END STEP']
    result='\n'.join(lines)+'\n'
    if result.count('*CLOAD')!=1 or any(s in result for s in ('*EQUATION','*RIGID BODY','*PLASTIC','S8R','*DLOAD')):
        raise ValueError('STUD_ANALOGUE_SCOPE_ESCALATION')
    return result


def make_matrix(case: str):
    _, items=edges(case)
    mat=[[0.]*8 for _ in range(8)]
    for nodes,k,group in items:
        if len(nodes)==1:
            mat[nodes[0]-1][nodes[0]-1]+=k
        else:
            a,b=(v-1 for v in nodes)
            mat[a][a]+=k;mat[b][b]+=k
            mat[a][b]-=k;mat[b][a]-=k
    rhs=[0.]*8;rhs[1]=LOAD
    return mat,rhs


def oracle(case: str) -> tuple[float, ...]:
    """Independent Gaussian elimination with partial pivoting; no CCX output."""
    a,b=make_matrix(case)
    for i in range(8):
        pivot=max(range(i,8),key=lambda j:abs(a[j][i]))
        if abs(a[pivot][i])<1e-12:raise ValueError('STUD_ANALOGUE_SINGULAR')
        a[i],a[pivot]=a[pivot],a[i]; b[i],b[pivot]=b[pivot],b[i]
        for j in range(i+1,8):
            f=a[j][i]/a[i][i]
            for z in range(i,8):a[j][z]-=f*a[i][z]
            b[j]-=f*b[i]
    x=[0.]*8
    for i in range(7,-1,-1):
        x[i]=(b[i]-math.fsum(a[i][j]*x[j] for j in range(i+1,8)))/a[i][i]
    if not all(math.isfinite(v) for v in x):raise ValueError('STUD_ANALOGUE_NONFINITE_ORACLE')
    return tuple(x)


def _printed(data: str, name: str) -> dict[int,float]:
    pattern=re.compile(r'(?im)^\s*displacements\s+\([^\n]*\)\s+for set\s+'+name+r'\s+and time\s+('+NUM+r')\s*$')
    headers=list(pattern.finditer(data))
    if not headers or abs(float(headers[-1].group(1).replace('D','E'))-1.)>1e-7:
        raise ValueError('STUD_ANALOGUE_DAT_FINAL_HEADER_MISSING:'+name)
    out={}
    for line in data[headers[-1].end():].splitlines():
        if not line.strip():
            if out:break
            continue
        m=ROW.fullmatch(line)
        if m:
            node=int(m.group(1));xyz=[float(m.group(i).replace('D','E')) for i in (2,3,4)]
            if node in out or not all(math.isfinite(v) for v in xyz) or any(abs(v)>1e-7 for v in xyz[:2]):
                raise ValueError('STUD_ANALOGUE_DAT_NODE_INVALID')
            out[node]=xyz[2]
        elif out:break
    expected=set(range(1,5)) if name=='PLATE' else set(range(5,9))
    if set(out)!=expected:raise ValueError('STUD_ANALOGUE_DAT_NODE_COVERAGE_INVALID:'+name)
    return out


def _complete(path: Path) -> None:
    rows=[]
    for line in path.read_text(encoding='ascii').splitlines():
        vals=line.split()
        if len(vals)==7 and vals[0]=='1':
            try:rows.append(float(vals[4]))
            except ValueError:raise ValueError('STUD_ANALOGUE_STA_BAD')
    if not rows or not math.isfinite(rows[-1]) or abs(rows[-1]-1.)>1e-7:
        raise ValueError('STUD_ANALOGUE_SOLVER_NOT_COMPLETED')


def verify(root: Path, case: str) -> dict:
    want=deck(case).encode('utf-8')
    folder=root/('stud_link_'+case)
    paths={ext:folder/('panel.'+ext) for ext in ('inp','dat','sta','frd')}
    for ext,p in paths.items():
        if p.is_symlink() or not p.is_file() or not 0<p.stat().st_size<=(64_000_000 if ext=='frd' else 10_000_000):
            raise ValueError('STUD_ANALOGUE_ARTIFACT_MISSING:'+ext)
    if paths['inp'].read_bytes()!=want:raise ValueError('STUD_ANALOGUE_DECK_PROVENANCE_MISMATCH')
    _complete(paths['sta'])
    dat=paths['dat'].read_text(encoding='utf-8',errors='replace')
    plate,rib=(_printed(dat,name) for name in ('PLATE','RIB'))
    u=tuple({**plate,**rib}[i] for i in range(1,9))
    independent=oracle(case)
    for val,ref in zip(u,independent):
        if abs(val-ref)>max(3e-6,abs(ref)*.002):
            raise ValueError('STUD_ANALOGUE_SOLVER_ORACLE_MISMATCH')
    mat,rhs=make_matrix(case)
    residual=max(abs(math.fsum(mat[i][j]*u[j] for j in range(8))-rhs[i]) for i in range(8))
    if residual>0.002:raise ValueError('STUD_ANALOGUE_EQUILIBRIUM_RESIDUAL')
    ground=math.fsum(P_GROUND*u[i]+R_GROUND*u[i+4] for i in range(4))
    if abs(ground-LOAD)>.002:raise ValueError('STUD_ANALOGUE_EXTERNAL_GROUND_BALANCE')
    pos=positions()
    transfers={str(pos[i]):STUD_K[case]*(u[i]-u[i+4]) for i in range(4)}
    _,links=edges(case)
    energy=math.fsum(.5*k*((u[nodes[0]-1] if len(nodes)==1 else u[nodes[0]-1]-u[nodes[1]-1])**2) for nodes,k,g in links)
    if abs(2*energy-LOAD*u[1])>0.002*LOAD*max(1e-8,u[1]):
        raise ValueError('STUD_ANALOGUE_ENERGY_IDENTITY_FAILED')
    return {'case':case,'scope':'SYNTHETIC_SCALAR_Z_SPRING_GRAPH_4_STUD_STATIONS',
       'positions_mm':pos,'synthetic_k_stud_per_station_n_mm':STUD_K[case],
       'plate_loaded_station_u3_mm':u[1], 'oracle_plate_loaded_station_u3_mm':independent[1],
       'u3_plate_mm':u[:4],'u3_rib_mm':u[4:],
       'derived_k_relative_u_link_n':transfers,'equilibrium_max_residual_n':residual,
       'ground_force_from_synthetic_springs_n':ground,
       'energy_n_mm':energy,'actual_stud_stiffness':'NOT_KNOWN_NOT_MODELED',
       'physical_panel_rib_section_fea':'NOT_MODELED',
       'real_stud_force_or_capacity':'NOT_ADMITTED',
       'general_six_component_balance':'NOT_ADMITTED',
       'engineering_acceptance':'NOT_ADMITTED',
       'sha256':{e:hashlib.sha256(p.read_bytes()).hexdigest() for e,p in paths.items()}}


def assess(root: Path) -> dict:
    results={c:verify(root,c) for c in CASES}
    a,b,c=(results[case]['plate_loaded_station_u3_mm'] for case in CASES)
    if not a>b>c>0:raise ValueError('STUD_ANALOGUE_COMPLIANCE_TREND_NOT_OBSERVED')
    if any(abs(f)>1e-10 for f in results['unlinked']['derived_k_relative_u_link_n'].values()):
        raise ValueError('STUD_ANALOGUE_UNLINKED_SHOULD_NOT_TRANSFER')
    return {'scope':'SYNTHETIC_SPRING_STATION_TRANSFER_SCREEN_ONLY','cases':results,
      'comparison_loaded_plate_u3_mm':{k:results[k]['plate_loaded_station_u3_mm'] for k in CASES},
      'section_and_stud_positions_from_existing_fixture':True,
      'physical_pitch_effect':'NOT_EVALUATED',
      'connection_force_independent_measurement':'NOT_ESTABLISHED',
      'actual_curtain_wall_design':'NOT_ADMITTED'}


def generate(folder: Path, case: str) -> None:
    if folder.exists() or folder.is_symlink() or case not in CASES:
        raise ValueError('STUD_ANALOGUE_FRESH_WORKSPACE_REQUIRED')
    text=deck(case)
    folder.mkdir(parents=True)
    (folder/'panel.inp').write_text(text,encoding='utf-8')


if __name__=='__main__':
    if len(sys.argv)==4 and sys.argv[1]=='--generate':
        generate(Path(sys.argv[2]),sys.argv[3]);print('STUD_ANALOGUE_SYNTHETIC_DECK_GENERATED')
    elif len(sys.argv)==2:
        print(json.dumps(assess(Path(sys.argv[1])),allow_nan=False,sort_keys=True))
        print('STUD_ANALOGUE_SPRING_GRAPH_PASS; NO_PHYSICAL_STUD_CAPACITY')
    else:
        raise SystemExit('USAGE: check_u_rib_stud_link.py ROOT | --generate DIR CASE')
