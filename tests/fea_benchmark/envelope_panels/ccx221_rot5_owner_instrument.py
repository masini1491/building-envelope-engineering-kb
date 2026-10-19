"""Observe CCX 2.21 shell-rotation SPC owner creation in isolated copied GPL source.

Research-only opt-in diagnostic binary; writes KB_ROT_OWNER records in its
working directory. Never changes loads, constraints, MPC coefficients, or
solver results. The canonical upstream gen3dboun.f is kept OUT of the KB.
"""
from __future__ import annotations
import pathlib
import sys

OWNER_1 = """                  ne2boun(1,node)=nboun"""
OWNER_2 = """                    ne2boun(2,node)=nboun"""
TRACE_1 = """                  open(unit=97,file='kb_rot_owner.tsv',
     &                 status='unknown',position='append')
                  write(97,*) 'KB_ROT_OWNER',node,idirref,1,nboun,
     &                 nodeboun(nboun),ndirboun(nboun),val,nmpc
                  close(97)
"""
TRACE_2 = """                    open(unit=97,file='kb_rot_owner.tsv',
     &                   status='unknown',position='append')
                    write(97,*) 'KB_ROT_OWNER',node,idirref,2,nboun,
     &                   nodeboun(nboun),ndirboun(nboun),val,nmpc
                    close(97)
"""

def insert_once(source: str, anchor: str, trace: str) -> str:
    if source.count(anchor + "\n") != 1:
        raise ValueError("KB_ROT_OWNER_SOURCE_ANCHOR_MISMATCH")
    return source.replace(anchor + "\n", anchor + "\n" + trace, 1)

def patch(directory: pathlib.Path) -> None:
    target = directory / "src" / "gen3dboun.f"
    original = target.read_text(encoding="latin-1")
    new = insert_once(original, OWNER_1, TRACE_1)
    new = insert_once(new, OWNER_2, TRACE_2)
    if new == original:
        raise ValueError("KB_ROT_OWNER_EMPTY_PATCH")
    target.write_text(new, encoding="latin-1")
    print("KB_ROT_OWNER_PATCHED_GEN3DBOUN_RESEARCH_ONLY")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: ccx221_rot5_owner_instrument.py CCX_DIR")
    patch(pathlib.Path(sys.argv[1]))
