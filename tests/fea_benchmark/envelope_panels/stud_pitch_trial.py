"""Synthetic C3D20R Z-only stud station-spacing/count sensitivity; NOT DESIGN.

Freeze first/last stations at 150/1050 mm. Compare 450, 300, 225 mm
nominal pitches (3/4/5 stations), with no face contact.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from pressure_contact_trial import deck as pressure_deck
from stud_solid_trial import add_studs, model_nodes, CASES

PROFILES = {
    'three_450': (150., 600., 1050.),
    'four_300': (150., 450., 750., 1050.),
    'five_225': (150., 375., 600., 825., 1050.),
}
TRIALS = ('three_450', 'five_225')
MESHES = (8, 16)
STUD_KEY = '*NSET,NSET=STUD_PLATE\n'
END_KEY = '*MATERIAL,NAME=SYNTH\n'


def mapping(nodes, bodies, stations):
    result=[]
    for x in stations:
        values=[]
        for body in ('PLATE', 'RIB'):
            exact=[i for i in bodies[body] if nodes[i] == (x, 0., 1.5)]
            if len(exact)!=1:raise ValueError('STUD_PITCH_MISSING_UNIQUE_ANCHOR')
            values.append(exact[0])
        if values[0]==values[1]:raise ValueError('STUD_PITCH_IDENTICAL_NODES')
        result.append(tuple(values))
    if len({v for pair in result for v in pair})!=len(result)*2:
        raise ValueError('STUD_PITCH_ANCHOR_COLLISION')
    return tuple(result)


def make(n,profile,case):
    if type(n) is not int or n not in MESHES or profile not in PROFILES or case not in ('soft','stiff'):
        raise ValueError('STUD_PITCH_SCOPE')
    positions=PROFILES[profile]
    if positions[0]!=150. or positions[-1]!=1050. or len(positions) not in (3,4,5):
        raise ValueError('STUD_PITCH_GEOMETRY_SCOPE')
    baseline=pressure_deck(n,'unlinked')
    original,existing=add_studs(baseline,n,case)
    nodes,bodies,last_eid=model_nodes(baseline)
    found=mapping(nodes,bodies,positions)
    if profile=='four_300':
        if found!=existing:raise ValueError('STUD_PITCH_CANONICAL_DRIFT')
        return original,found
    if original.count(STUD_KEY)!=1 or original.count(END_KEY)!=1:
        raise ValueError('STUD_PITCH_CARD_ANCHOR')
    start=original.index(STUD_KEY)
    end=original.index(END_KEY,start)
    k=CASES[case]
    block=(STUD_KEY+','.join(str(p) for p,q in found)+'\n'
           '*NSET,NSET=STUD_RIB\n'+','.join(str(q) for p,q in found)+'\n'
           '*ELEMENT,TYPE=SPRING2,ELSET=STUD_LINK_SYNTHETIC\n'
           +'\n'.join(f'{last_eid+i},{p},{q}' for i,(p,q) in enumerate(found,1))+'\n'
           '*SPRING,ELSET=STUD_LINK_SYNTHETIC\n3,3\n'+f'{k:.8f}'+'\n')
    changed=original[:start]+block+original[end:]
    if changed[:start]!=original[:start] or changed[start+len(block):]!=original[end:]:
        raise ValueError('STUD_PITCH_UNEXPECTED_DECK_MUTATION')
    if changed.count('*ELEMENT,TYPE=SPRING2')!=1 or '*CONTACT PAIR' in changed or changed.count('*DLOAD')!=1:
        raise ValueError('STUD_PITCH_GENERATED_DECK_CONTRACT')
    return changed,found


def generate(target,n,profile,case):
    target=Path(target)
    if target.exists() or target.is_symlink():raise ValueError('STUD_PITCH_NOT_FRESH')
    content,_=make(n,profile,case)
    target.mkdir(parents=True)
    (target/'panel.inp').write_text(content,encoding='utf-8')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('n',type=int);parser.add_argument('profile');parser.add_argument('case')
    parser.add_argument('fresh_directory',type=Path)
    a=parser.parse_args()
    generate(a.fresh_directory,a.n,a.profile,a.case)
