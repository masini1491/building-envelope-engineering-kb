"""Hot 2: controlled n8/n16/n24 refinement, four bilateral synthetic Z links.

For n8/n16, reproduce the pinned Hot-1 signed decks byte-exact.
For n24, extend ONLY the identical original unlinked C3D20R plate/U geometry
with four coincident plate/rib anchor pairs at 150/450/750/1050 mm.
The pressure sign is the only change between positive/negative load cases.
No contact, real studs, actual weld stiffness, or design load is admitted.
"""
from __future__ import annotations
import argparse
from pathlib import Path

from stud_solid_trial import STATIONS, CASES, model_nodes
from stud_signed_pressure_trial import (
    deck as hot1_deck, POSITIVE_CARD, NEGATIVE_CARD, DIRECTIONS,
)
from pressure_contact_trial import deck as pressure_deck

MESHES = (8, 16, 24)
STATION_Y_MM = 0.
INTERFACE_Z_MM = 1.5


def fail(code):
    raise ValueError("STUD_REFINEMENT_INPUT_" + code)


def n24_positive(case):
    if case not in CASES:
        fail("CASE")
    original = pressure_deck(24, 'unlinked')
    if (original.count(POSITIVE_CARD) != 1 or
        original.count("*MATERIAL,NAME=SYNTH\n") != 1 or
        original.count("*NODE FILE,OUTPUT=3D\nU\n") != 1 or
        "*CONTACT PAIR" in original or "*SPRING" in original or "*CLOAD" in original or
        original.count("*STEP,NLGEOM=YES,INC=100\n") != 1):
        fail("BASE_DECK_CONTRACT")
    nodes, bodies, last_element = model_nodes(original)
    station_nodes = []
    for x in STATIONS:
        xyz = (x, STATION_Y_MM, INTERFACE_Z_MM)
        pair = []
        for name in ("PLATE", "RIB"):
            candidates = [
                nid for nid in bodies[name] if
                all(abs(nodes[nid][j] - xyz[j]) <= 1.e-7 for j in range(3))
            ]
            if len(candidates) != 1:
                fail("STATION_COORDINATE_NOT_UNIQUE")
            pair.append(candidates[0])
        if pair[0] == pair[1]:
            fail("BODY_NODE_NOT_INDEPENDENT")
        station_nodes.append(tuple(pair))
    if len({nid for pair in station_nodes for nid in pair}) != 8:
        fail("STATION_NODE_COLLISION")
    insert = (
        "*NSET,NSET=STUD_PLATE\n" +
        ",".join(str(p) for p, _ in station_nodes) + "\n" +
        "*NSET,NSET=STUD_RIB\n" +
        ",".join(str(q) for _, q in station_nodes) + "\n"
    )
    k = CASES[case]
    if k:
        insert += "*ELEMENT,TYPE=SPRING2,ELSET=STUD_LINK_SYNTHETIC\n"
        insert += "\n".join(
            f"{last_element + i},{p},{q}"
            for i, (p, q) in enumerate(station_nodes, 1)
        ) + "\n"
        insert += (
            "*SPRING,ELSET=STUD_LINK_SYNTHETIC\n3,3\n" +
            f"{k:.8f}\n"
        )
    revised = original.replace("*MATERIAL,NAME=SYNTH\n",
                               insert + "*MATERIAL,NAME=SYNTH\n", 1)
    revised = revised.replace(
        "*NODE FILE,OUTPUT=3D\nU\n",
        "*NODE PRINT,NSET=STUD_PLATE\nU\n"
        "*NODE PRINT,NSET=STUD_RIB\nU\n"
        "*NODE FILE,OUTPUT=3D\nU\n", 1)
    if (revised.count("*DLOAD") != 1 or
        revised.count("*ELEMENT,TYPE=SPRING2") != int(k > 0) or
        revised.count("*NSET,NSET=STUD_PLATE") != 1 or
        revised.count("*NSET,NSET=STUD_RIB") != 1):
        fail("GENERATOR_CONTRACT")
    return revised


def deck(n, case, direction):
    if type(n) is not int or n not in MESHES or case not in CASES or direction not in DIRECTIONS:
        fail("SCOPE")
    if n in (8, 16):
        return hot1_deck(n, case, direction)
    original = n24_positive(case)
    if direction == "positive":
        return original
    changed = original.replace(POSITIVE_CARD, NEGATIVE_CARD, 1)
    if changed.replace(NEGATIVE_CARD, POSITIVE_CARD, 1) != original:
        fail("NONPRESSURE_DRIFT")
    return changed


def generate(folder, n, case, direction):
    folder = Path(folder)
    if folder.exists() or folder.is_symlink():
        fail("FRESH_DIRECTORY")
    content = deck(n, case, direction)
    folder.mkdir(parents=True)
    (folder / 'panel.inp').write_text(content, encoding='utf-8')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mesh', type=int)
    ap.add_argument('case', choices=tuple(CASES))
    ap.add_argument('direction', choices=tuple(DIRECTIONS))
    ap.add_argument('fresh_dir', type=Path)
    args = ap.parse_args()
    generate(args.fresh_dir, args.mesh, args.case, args.direction)
