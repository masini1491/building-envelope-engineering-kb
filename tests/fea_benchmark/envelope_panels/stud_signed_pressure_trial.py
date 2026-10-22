"""Hot 1: signed-pressure C3D20R four-station synthetic Z links.

The existing positive-pressure deck is reused byte-for-byte. The negative
counterpart changes ONLY the single P1 pressure magnitude sign. This is a
bilateral linear-Z SPRING2 surrogate without contact, release, friction,
weld or shear stiffness. NOT a welded-stud design model.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from stud_solid_trial import CASES, MESHES, STATIONS, deck as positive_deck

DIRECTIONS = {"positive": 1, "negative": -1}
POSITIVE_CARD = "*DLOAD\nPLATE,P1,0.00010000\n"
NEGATIVE_CARD = "*DLOAD\nPLATE,P1,-0.00010000\n"


def fail(code: str):
    raise ValueError("STUD_SIGNED_" + code)


def deck(n: int, case: str, direction: str) -> str:
    if type(n) is not int or n not in MESHES or case not in CASES or direction not in DIRECTIONS:
        fail("SCOPE")
    original = positive_deck(n, case)
    if (original.count(POSITIVE_CARD) != 1 or NEGATIVE_CARD in original or
            original.count("*STEP,NLGEOM=YES,INC=100\n") != 1 or
            "*CONTACT PAIR" in original or "*CLOAD" in original or
            original.count("*NSET,NSET=STUD_PLATE\n") != 1 or
            original.count("*NSET,NSET=STUD_RIB\n") != 1):
        fail("BASE_PROVENANCE")
    if direction == "positive":
        return original
    changed = original.replace(POSITIVE_CARD, NEGATIVE_CARD, 1)
    if changed.replace(NEGATIVE_CARD, POSITIVE_CARD, 1) != original:
        fail("NONPRESSURE_DRIFT")
    return changed


def generate(folder: Path, n: int, case: str, direction: str) -> None:
    folder = Path(folder)
    if folder.exists() or folder.is_symlink():
        fail("DIRECTORY_NOT_FRESH")
    content = deck(n, case, direction)
    folder.mkdir(parents=True)
    (folder / "panel.inp").write_text(content, encoding="utf-8")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mesh", type=int)
    p.add_argument("case", choices=tuple(CASES))
    p.add_argument("direction", choices=tuple(DIRECTIONS))
    p.add_argument("fresh_folder", type=Path)
    args = p.parse_args()
    generate(args.fresh_folder, args.mesh, args.case, args.direction)
