"""Controlled C3D20R Z-link interior station placement; research, NOT DESIGN.

Freeze station count, each spring k, endpoint stations 150/1050 mm,
symmetric layout, mesh, pressure, and supports. Change only inner stations.
No face contact, shear, weld, or physical stud stiffness.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from stud_pitch_trial import make as base_make, mapping, STUD_KEY, END_KEY
from stud_solid_trial import model_nodes, CASES
from pressure_contact_trial import deck as pressure_deck

LAYOUTS={
    'four_inner_out':('four_300',(150.,375.,825.,1050.)),
    'five_inner_out':('five_225',(150.,300.,600.,900.,1050.)),
}
MESHES=(8,16)


def make(n,layout,case):
    if type(n) is not int or n not in MESHES or layout not in LAYOUTS or case not in ('soft','stiff'):
        raise ValueError('STUD_POSITION_SCOPE')
    parent, positions=LAYOUTS[layout]
    original, old_pairs=base_make(n,parent,case)
    baseline=pressure_deck(n,'unlinked')
    nodes,bodies,last_eid=model_nodes(baseline)
    pairs=mapping(nodes,bodies,positions)
    old_positions={'four_300':(150.,450.,750.,1050.),
                   'five_225':(150.,375.,600.,825.,1050.)}[parent]
    if (len(positions)!=len(old_pairs) or positions[0]!=old_positions[0] or
        positions[-1]!=old_positions[-1] or
        any(abs(positions[i]+positions[-1-i]-1200.)>1e-8 for i in range(len(positions))) or
        (600. in positions)!=(600. in old_positions)):
        raise ValueError('STUD_POSITION_CONTROLLED_LAYOUT')
    if original.count(STUD_KEY)!=1 or original.count(END_KEY)!=1:
        raise ValueError('STUD_POSITION_SOURCE_CARDS')
    a=original.index(STUD_KEY);b=original.index(END_KEY,a)
    k=CASES[case]
    block=(STUD_KEY+','.join(str(p) for p,q in pairs)+'\n'
        '*NSET,NSET=STUD_RIB\n'+','.join(str(q) for p,q in pairs)+'\n'
        '*ELEMENT,TYPE=SPRING2,ELSET=STUD_LINK_SYNTHETIC\n'
        +'\n'.join(f'{last_eid+i},{p},{q}' for i,(p,q) in enumerate(pairs,1))+'\n'
        '*SPRING,ELSET=STUD_LINK_SYNTHETIC\n3,3\n'+f'{k:.8f}'+'\n')
    updated=original[:a]+block+original[b:]
    if (updated[:a]!=original[:a] or updated[a+len(block):]!=original[b:] or
        updated.count('*ELEMENT,TYPE=SPRING2')!=1 or
        updated.count('*DLOAD\nPLATE,P1,0.00010000\n')!=1 or
        '*CONTACT PAIR' in updated):
        raise ValueError('STUD_POSITION_PHYSICS_DRIFT')
    return updated,pairs


def generate(folder,n,layout,case):
    folder=Path(folder)
    if folder.exists() or folder.is_symlink():raise ValueError('STUD_POSITION_NOT_FRESH')
    source,_=make(n,layout,case)
    folder.mkdir(parents=True)
    (folder/'panel.inp').write_text(source,encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('mesh',type=int);p.add_argument('layout');p.add_argument('case');p.add_argument('fresh_directory',type=Path)
    args=p.parse_args()
    generate(args.fresh_directory,args.mesh,args.layout,args.case)
