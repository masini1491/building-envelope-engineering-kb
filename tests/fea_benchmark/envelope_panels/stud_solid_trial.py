"""C3D20R panel/U-rib four-station synthetic DOF3 stud-spring comparator.

No contact; an ideal bilateral Z connector surrogate, not a welded stud,
fastener strength or calibrated fastener stiffness.
"""
from __future__ import annotations
import argparse
import math
from pathlib import Path

MESHES=(8,16)
CASES={'unlinked':0.,'soft':50.,'stiff':500.}
STATIONS=(150.,450.,750.,1050.)


def model_nodes(inp: str):
    nodes={};bodies={'PLATE':set(),'RIB':set()};section=None;pending=[];max_eid=0
    for line in inp.splitlines():
        line=line.strip()
        if line=='*NODE':section='NODE';continue
        if line=='*ELEMENT,TYPE=C3D20R,ELSET=PLATE':section='PLATE';pending=[];continue
        if line=='*ELEMENT,TYPE=C3D20R,ELSET=RIB':section='RIB';pending=[];continue
        if line.startswith('*'):section=None;continue
        if not line or section is None:continue
        values=[x for x in line.split(',') if x.strip()]
        if section=='NODE':
            if len(values)!=4:raise ValueError('STUD_SOLID_NODE_FORMAT')
            nid=int(values[0]);xyz=tuple(float(v) for v in values[1:])
            if nid in nodes or not all(map(math.isfinite,xyz)):raise ValueError('STUD_SOLID_NODE_FORMAT')
            nodes[nid]=xyz
        else:
            pending.extend(map(int,values))
            if len(pending)==21:
                max_eid=max(max_eid,pending[0]);bodies[section].update(pending[1:]);pending=[]
            elif len(pending)>21:raise ValueError('STUD_SOLID_ELEMENT_FORMAT')
    if not nodes or not all(bodies.values()) or bodies['PLATE']&bodies['RIB'] or pending:
        raise ValueError('STUD_SOLID_TOPOLOGY')
    if set(nodes)!=set().union(*bodies.values()):raise ValueError('STUD_SOLID_NODE_COVERAGE')
    return nodes,bodies,max_eid


def add_studs(original: str,n: int,case: str):
    if type(n) is not int or n not in MESHES or case not in CASES:
        raise ValueError('STUD_SOLID_SCOPE')
    if (original.count('*DLOAD\nPLATE,P1,0.00010000\n')!=1 or
        '*CONTACT PAIR' in original or '*SURFACE,NAME=' in original or
        original.count('*NODE FILE,OUTPUT=3D\nU\n')!=1 or
        original.count('*MATERIAL,NAME=SYNTH\n')!=1 or
        original.count('*STEP,NLGEOM=YES,INC=100\n')!=1 or
        '*SPRING' in original or '*ELEMENT,TYPE=SPRING' in original):
        raise ValueError('STUD_SOLID_BASE_DECK_CONTRACT')
    from check_u_rib_stud_link import positions
    if tuple(positions()) != STATIONS:
        raise ValueError('STUD_SOLID_GEOMETRY_FIXTURE_MISMATCH')
    nodes,bodies,last_eid=model_nodes(original)
    targets=[]
    for x in STATIONS:
        coord=(x,0.,1.5)
        pair=[]
        for body in ('PLATE','RIB'):
            found=[i for i in bodies[body] if all(abs(nodes[i][j]-coord[j])<1e-7 for j in range(3))]
            if len(found)!=1:raise ValueError('STUD_SOLID_AMBIGUOUS_ANCHOR')
            pair.append(found[0])
        if pair[0]==pair[1]:raise ValueError('STUD_SOLID_NONINDEPENDENT_BODIES')
        targets.append(tuple(pair))
    if len(set(i for pair in targets for i in pair))!=8:raise ValueError('STUD_SOLID_ANCHOR_COLLISION')
    add='*NSET,NSET=STUD_PLATE\n'+','.join(str(p) for p,_ in targets)+'\n'
    add+='*NSET,NSET=STUD_RIB\n'+','.join(str(q) for _,q in targets)+'\n'
    if CASES[case]>0:
        add+='*ELEMENT,TYPE=SPRING2,ELSET=STUD_LINK_SYNTHETIC\n'
        add+='\n'.join(f'{last_eid+i},{p},{q}' for i,(p,q) in enumerate(targets,1))+'\n'
        add+='*SPRING,ELSET=STUD_LINK_SYNTHETIC\n3,3\n'+f'{CASES[case]:.8f}'+'\n'
    changed=original.replace('*MATERIAL,NAME=SYNTH\n',add+'*MATERIAL,NAME=SYNTH\n')
    changed=changed.replace('*NODE FILE,OUTPUT=3D\nU\n',
        '*NODE PRINT,NSET=STUD_PLATE\nU\n*NODE PRINT,NSET=STUD_RIB\nU\n'+
        '*NODE FILE,OUTPUT=3D\nU\n')
    if changed.count('*ELEMENT,TYPE=SPRING2')!=int(case!='unlinked') or changed.count('*DLOAD')!=1:
        raise ValueError('STUD_SOLID_GENERATION_CONTRACT')
    return changed,tuple(targets)


def deck(n,case):
    from pressure_contact_trial import deck as baseline
    return add_studs(baseline(n,'unlinked'),n,case)[0]


def generate(folder:Path,n:int,case:str):
    if folder.exists() or folder.is_symlink():raise ValueError('STUD_SOLID_NOT_FRESH')
    text=deck(n,case)
    folder.mkdir(parents=True)
    (folder/'panel.inp').write_text(text,encoding='utf-8')


if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('mesh',type=int);a.add_argument('case');a.add_argument('fresh_dir',type=Path)
    x=a.parse_args();generate(x.fresh_dir,x.mesh,x.case)
