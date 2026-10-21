"""Bounded CalculiX 2.21 face-to-face contact integration-point CSTR probe.

One output-only keyword modification; geometry, contact law and load are frozen.
Do not interpret nodal FRD CPRESS as integrable contact traction.
"""
import sys
from pathlib import Path
from pressure_contact_trial import deck as original_deck

ORIGINAL = ('*CONTACT PRINT,SLAVE=RIB_BASE_UNDERSIDE,MASTER=PLATE_TOP\n'
            'CF,CFN,CNUM\n')
INSTRUMENTED = ('*CONTACT PRINT,SLAVE=RIB_BASE_UNDERSIDE,MASTER=PLATE_TOP\n'
                'CF,CFN,CNUM,CSTR\n')


def instrument_deck(source):
    if (source.count(ORIGINAL) != 1 or INSTRUMENTED in source or
            source.count('*CONTACT PAIR,INTERACTION=NORMAL,TYPE=SURFACE TO SURFACE') != 1 or
            source.count('*DLOAD\nPLATE,P1,0.00010000\n') != 1 or
            source.count('*END STEP\n') != 1):
        raise ValueError('C3D20R_CONTACT_IP_DECK_CONTRACT')
    updated = source.replace(ORIGINAL, INSTRUMENTED)
    if updated.replace(INSTRUMENTED, ORIGINAL) != source:
        raise ValueError('C3D20R_CONTACT_IP_PHYSICAL_INPUT_DRIFT')
    return updated


def deck(n, case):
    if type(n) is not int or n not in (16, 24) or case != 'toward':
        raise ValueError('C3D20R_CONTACT_IP_SCOPE')
    return instrument_deck(original_deck(n, case))


if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SystemExit('usage: N CASE FRESH_DIRECTORY')
    target = Path(sys.argv[3])
    if target.exists() or target.is_symlink():
        raise ValueError('C3D20R_CONTACT_IP_DIRECTORY_NOT_FRESH')
    content = deck(int(sys.argv[1]), sys.argv[2])
    target.mkdir(parents=True)
    (target/'panel.inp').write_text(content, encoding='utf-8')
