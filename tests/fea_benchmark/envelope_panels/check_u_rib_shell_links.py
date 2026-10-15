"""Synthetic plate/open-U S8R connection study; no real stud/contact admission.

An independent shell plate and a disconnected sharp-corner U shell are joined
ONLY via 4 synthetic DOF3 SPRING2 elements at nominal @300-mm positions.
No tied midsurface, weld, shear spring, contact, measured stiffness, buckling,
or actual curtain-wall support condition is implied.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

from u_rib_stud_geometry import load
from check_u_fold_cantilever import _completed, _dat_vectors
from check_aluminum_ritz import I0, I1, I2, IX

HERE = Path(__file__).parent
FIXTURE = HERE / 'fixtures' / 'u_rib_stud_50x50_t3_synthetic.json'
LENGTH, PANEL_WIDTH = 1200.0, 300.0
E, NU, LOAD_N = 69000.0, 0.33, 1.0
MESHES = (8, 16)
PLATE_CROSS = 8
CASES = ('unlinked', 'soft', 'stiff')
STUD_STIFFNESS = {'unlinked': 0., 'soft': 50., 'stiff': 5000.}
SCOPE = 'SYNTHETIC_CLAMPED_PLATE_PLUS_OPEN_U_S8R_POINT_STUD_Z_SPRINGS'


def _configuration():
    g=load(FIXTURE)
    i=g['inputs']; sec=g['section']; stud=g['stud_centers']
    if (g['engineering_acceptance'] != 'NOT_ADMITTED' or
        g['connection_transfer'] != 'NOT_ESTABLISHED' or
        g['finite_element_deck'] != 'NOT_GENERATED' or
        i['units'] != 'mm' or i['rib_length_mm'] != LENGTH or
        i['panel_thickness_mm'] != 3 or i['rib_thickness_mm'] != 3 or
        sec['outer_base_width_mm'] != 50 or sec['outer_height_from_panel_interface_mm'] != 50 or
        stud['positions_along_length_mm'] != [150.,450.,750.,1050.] or
        stud['number_of_rows'] != 1 or stud['nominal_pitch_mm'] != 300.):
        raise ValueError('U_SHELL_STUD_CANONICAL_FIXTURE_CHANGED')
    return g


def _segment(j: int, b: float, h: float, panel_t: float, t: float):
    # Outer U bottom face touches panel's nominal rear face, but midsurface
    # shells remain distinct; gap is panel_t/2 + rib_t/2, not a weld or tie.
    low=(panel_t+t)/2
    top=panel_t/2 + h - t/2
    offset=b/2-t/2
    anchors=((-offset,top),(-offset,low),(0.,low),(offset,low),(offset,top))
    seg, remainder=divmod(j,2)
    if remainder==0:return anchors[seg]
    a,c=anchors[seg],anchors[seg+1]
    return ((a[0]+c[0])/2,(a[1]+c[1])/2)


def mesh(n: int):
    if type(n) is not int or n not in MESHES:raise ValueError('U_SHELL_MESH_OUTSIDE_SCOPE')
    g=_configuration(); i=g['inputs']
    panel_nodes={}; rib_nodes={}; coords={}
    def node(group: str, ai: int, bj: int):
        container=panel_nodes if group=='plate' else rib_nodes
        key=(ai,bj)
        if key not in container:
            nid=len(coords)+1
            container[key]=nid
            x=LENGTH*ai/(2*n)
            if group=='plate':
                y=PANEL_WIDTH*(bj/(2*PLATE_CROSS)-.5)
                z=0.
            else:
                y,z=_segment(bj,i['rib_base_width_mm'],i['rib_height_mm'],
                             i['panel_thickness_mm'],i['rib_thickness_mm'])
            coords[nid]=(x,y,z)
        return container[key]
    def tiles(group: str, across: int):
        els=[]
        for a in range(n):
            for b in range(across):
                x,y=2*a,2*b
                inds=((x,y),(x+2,y),(x+2,y+2),(x,y+2),
                      (x+1,y),(x+2,y+1),(x+1,y+2),(x,y+1))
                els.append(tuple(node(group,*q) for q in inds))
        return els
    plate=tiles('plate',PLATE_CROSS)
    rib=tiles('rib',4)
    clamped_plate={nid for (a,b),nid in panel_nodes.items()
                   if a in (0,2*n) or b in (0,2*PLATE_CROSS)}
    clamped_rib_end={nid for (a,b),nid in rib_nodes.items() if a in (0,2*n)}
    center=panel_nodes[n,PLATE_CROSS]
    stations=tuple(int(p/(LENGTH/(2*n))) for p in g['stud_centers']['positions_along_length_mm'])
    panel_studs=tuple(panel_nodes[a,PLATE_CROSS] for a in stations)
    rib_studs=tuple(rib_nodes[a,4] for a in stations)
    if (len(set(panel_studs))!=4 or len(set(rib_studs))!=4 or
        set(panel_nodes.values()) & set(rib_nodes.values()) or
        center in clamped_plate or any(z in clamped_plate for z in panel_studs) or
        len(plate)!=n*PLATE_CROSS or len(rib)!=4*n or
        len(clamped_plate)!=4*(n+PLATE_CROSS) or
        len(clamped_rib_end)!=2*(2*4+1) or
        any(abs(coords[a][2]-coords[b][2]+3.)>1e-8 for a,b in zip(panel_studs,rib_studs))):
        raise ValueError('U_SHELL_MESH_STUD_TOPOLOGY_INVALID')
    return dict(coords=coords,plate=plate,rib=rib,clamped_plate=clamped_plate,
                clamped_rib_end=clamped_rib_end,center=center,
                panel_studs=panel_studs,rib_studs=rib_studs)


def _nset(lines:list[str], name:str, nodes)->None:
    lines.append('*NSET,NSET='+name)
    items=sorted(nodes)
    lines.extend(','.join(str(a) for a in items[j:j+12]) for j in range(0,len(items),12))


def deck(n:int,case:str)->str:
    if case not in CASES:raise ValueError('U_SHELL_CASE_OUTSIDE_SCOPE')
    topo=mesh(n); g=_configuration(); p_t=g['inputs']['panel_thickness_mm'];r_t=g['inputs']['rib_thickness_mm']
    lines=['*HEADING',f'synthetic-open-U-shell-four-point-studs-{case}-mesh-{n}','*NODE']
    lines += [f'{id},{x:.8f},{y:.8f},{z:.8f}' for id,(x,y,z) in sorted(topo['coords'].items())]
    for label,els,start in (('PLATE',topo['plate'],1),('RIB',topo['rib'],1+len(topo['plate']))):
        lines += [f'*ELEMENT,TYPE=S8R,ELSET={label}']
        lines += [str(start+i)+','+','.join(map(str,e)) for i,e in enumerate(els)]
    if STUD_STIFFNESS[case]:
        lines += ['*ELEMENT,TYPE=SPRING2,ELSET=STUD_Z']
        start=len(topo['plate'])+len(topo['rib'])+1
        lines += [f'{start+i},{a},{b}' for i,(a,b) in enumerate(zip(topo['panel_studs'],topo['rib_studs']))]
    lines += ['*MATERIAL,NAME=SYNTH_ELASTIC','*ELASTIC',f'{E:.8f},{NU:.8f}',
              '*SHELL SECTION,ELSET=PLATE,MATERIAL=SYNTH_ELASTIC',str(p_t),
              '*SHELL SECTION,ELSET=RIB,MATERIAL=SYNTH_ELASTIC',str(r_t)]
    if STUD_STIFFNESS[case]:
        lines += ['*SPRING,ELSET=STUD_Z','3,3',f'{STUD_STIFFNESS[case]:.8f}']
    for label,ids in (('PLATE_CLAMP',topo['clamped_plate']),('RIB_END_CLAMP',topo['clamped_rib_end']),
                      ('PLATE_CENTER',(topo['center'],)),('P_STUD',topo['panel_studs']),('R_STUD',topo['rib_studs'])):
        _nset(lines,label,ids)
    lines += ['*BOUNDARY','PLATE_CLAMP,1,6,0.','RIB_END_CLAMP,1,6,0.',
              '*STEP','*STATIC','0.1,1.,0.00001,0.1',
              '*CLOAD',f'{topo["center"]},3,{-LOAD_N:.8f}',
              '*NODE PRINT,NSET=PLATE_CENTER','U',
              '*NODE PRINT,NSET=P_STUD','U',
              '*NODE PRINT,NSET=R_STUD','U',
              '*NODE FILE,OUTPUT=3D','U','*END STEP']
    out='\n'.join(lines)+'\n'
    if (out.count('*CLOAD')!=1 or out.count('*ELEMENT,TYPE=S8R')!=2 or
        out.count('*ELEMENT,TYPE=SPRING2')!=(case!='unlinked') or
        any(x in out for x in ('*EQUATION','*RIGID BODY','*DLOAD','NLGEOM','*PLASTIC','*CONTACT'))):
        raise ValueError('U_SHELL_SCOPE_ESCALATION')
    return out


def ritz_point_load_center()->float:
    # Independent one-term clamped plate Ritz for F at center, NOT exact shell value.
    a,b=LENGTH,PANEL_WIDTH
    D=E*3.**3/(12*(1-NU**2)); jac=a*b/4
    K=jac*(16*I2*I0*(a**-4+b**-4)+32*(NU*IX**2+(1-NU)*I1**2)/(a*a*b*b))
    return LOAD_N/(D*K)


def compare(observed: dict[tuple[int,str],float])->dict:
    if set(observed)!={(n,c) for n in MESHES for c in CASES} or any(
        type(v) not in (int,float) or not math.isfinite(v) or v<=0 for v in observed.values()):
        raise ValueError('U_SHELL_INCOMPLETE_OR_INVALID_RESULTS')
    for n in MESHES:
        if not observed[n,'unlinked']>observed[n,'soft']>observed[n,'stiff']:
            raise ValueError('U_SHELL_COMPLIANCE_TREND_FAILED')
        if observed[n,'unlinked']>=.05*3:raise ValueError('U_SHELL_DISPLACEMENT_OUTSIDE_SMALL_LOAD_SCOPE')
    ref=ritz_point_load_center()
    difference=abs(observed[16,'unlinked']-ref)/ref
    if difference>.7:raise ValueError('U_SHELL_ONE_TERM_PLATE_ORACLE_SCREEN_FAILED')
    meshdiff={}
    for c in CASES:
        d=abs(observed[16,c]-observed[8,c])/observed[16,c]
        if d>.25:raise ValueError('U_SHELL_TWO_MESH_CHANGE_TOO_LARGE')
        meshdiff[c]=d
    return {'scope':SCOPE,'unlinked_plate_one_term_ritz_mm':ref,
            'ritz_screen_relative_difference':difference,
            'center_point_displacement_mm':{str(n):{c:observed[n,c] for c in CASES} for n in MESHES},
            'two_mesh_relative_difference':meshdiff,
            'synthetic_stud_k_n_per_mm':STUD_STIFFNESS,
            'real_panel_rib_contact':'NOT_MODELED',
            'real_stud_shear_bending_and_capacity':'NOT_ADMITTED',
            'real_rib_end_support':'NOT_MODELED',
            'global_six_component_balance':'NOT_ADMITTED',
            'engineering_acceptance':'NOT_ADMITTED'}


def _case(folder:Path,n:int,c:str)->dict:
    paths={e:folder/('panel.'+e) for e in ('inp','sta','dat','frd')}
    for e,p in paths.items():
        if p.is_symlink() or not p.is_file() or not 0<p.stat().st_size<=(64_000_000 if e=='frd' else 10_000_000):
            raise ValueError('U_SHELL_ARTIFACT_MISSING:'+e)
    if paths['inp'].read_bytes()!=deck(n,c).encode('utf-8'):
        raise ValueError('U_SHELL_INPUT_PROVENANCE_CHANGED')
    _completed(paths['sta'])
    topo=mesh(n)
    dat=paths['dat']
    center=_dat_vectors(dat,'PLATE_CENTER','U')
    pu=_dat_vectors(dat,'P_STUD','U')
    ru=_dat_vectors(dat,'R_STUD','U')
    if set(center)!={topo['center']} or set(pu)!=set(topo['panel_studs']) or set(ru)!=set(topo['rib_studs']):
        raise ValueError('U_SHELL_PRINTED_NODE_COVERAGE_FAILED')
    v=-center[topo['center']][2]
    if not math.isfinite(v) or v<=0 or v>=.15:
        raise ValueError('U_SHELL_CENTER_DEFLECTION_INVALID')
    derived={str(x):STUD_STIFFNESS[c]*(pu[a][2]-ru[b][2])
             for x,a,b in zip(_configuration()['stud_centers']['positions_along_length_mm'],
                              topo['panel_studs'],topo['rib_studs'])}
    if c=='unlinked' and any(abs(q)>1e-12 for q in derived.values()):
        raise ValueError('U_SHELL_UNLINKED_TRANSFER_NONZERO')
    return dict(center_deflection_mm=v,stud_k_relative_u_derived_n=derived,
                provenance_sha256={key:hashlib.sha256(path.read_bytes()).hexdigest() for key,path in paths.items()})


def assess(root:Path)->dict:
    cases={(n,c):_case(root/f'open_u_shell_n{n}_{c}',n,c) for n in MESHES for c in CASES}
    out=compare({k:v['center_deflection_mm'] for k,v in cases.items()})
    out['cases']={f'n{n}_{c}':v for (n,c),v in cases.items()}
    return out


def generate(folder:Path,n:int,c:str)->None:
    if folder.exists() or folder.is_symlink():raise ValueError('U_SHELL_WORKSPACE_MUST_BE_NEW')
    out=deck(n,c)
    folder.mkdir(parents=True)
    (folder/'panel.inp').write_text(out,encoding='utf-8')


if __name__=='__main__':
    if len(sys.argv)==5 and sys.argv[1]=='--generate':
        generate(Path(sys.argv[2]),int(sys.argv[3]),sys.argv[4])
        print('U_SHELL_SYNTHETIC_DISCRETE_STUD_DECK_CREATED')
    elif len(sys.argv)==2:
        print(json.dumps(assess(Path(sys.argv[1])),sort_keys=True,allow_nan=False))
        print('U_SHELL_DISCRETE_STUD_SYNTHETIC_BENCHMARK_PASS; NO_CAPACITY')
    else:
        raise SystemExit('USAGE: check_u_rib_shell_links.py ROOT | --generate DIR MESH CASE')
