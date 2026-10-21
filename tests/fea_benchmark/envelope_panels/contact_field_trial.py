"""Opt-in C3D20R contact-field capture; result is diagnostic, not design."""
import sys
from pathlib import Path

FIELD_CARD = '*CONTACT FILE\nCDIS,CSTR\n'


def instrument_deck(raw):
    """Add a read-only field-output request to an otherwise unchanged deck."""
    anchor = '*END STEP\n'
    if (raw.count(anchor) != 1 or '*CONTACT FILE' in raw or
            raw.count('*CONTACT PRINT,SLAVE=RIB_BASE_UNDERSIDE,MASTER=PLATE_TOP') != 1 or
            raw.count('*CONTACT PAIR,INTERACTION=NORMAL,TYPE=SURFACE TO SURFACE') != 1 or
            raw.count('*STEP,NLGEOM=YES') != 1):
        raise ValueError('C3D20R_CONTACT_FIELD_DECK_CONTRACT')
    result = raw.replace(anchor, FIELD_CARD + anchor)
    if result.replace(FIELD_CARD,'') != raw:
        raise ValueError('C3D20R_CONTACT_FIELD_INPUT_DRIFT')
    return result


def deck(n, case):
    if type(n) is not int or n not in (16,24) or case not in ('toward','unlinked'):
        raise ValueError('C3D20R_CONTACT_FIELD_SCOPE')
    if case == 'unlinked':
        raise ValueError('C3D20R_CONTACT_FIELD_NO_CONTACT_PAIR')
    from pressure_contact_trial import deck as source_deck
    return instrument_deck(source_deck(n,case))


if __name__ == '__main__':
    if len(sys.argv)!=4:
        raise SystemExit('usage: N CASE FRESH_DIR')
    target=Path(sys.argv[3])
    if target.exists() or target.is_symlink():
        raise ValueError('C3D20R_CONTACT_FIELD_NOT_FRESH')
    content=deck(int(sys.argv[1]),sys.argv[2])
    target.mkdir(parents=True)
    (target/'panel.inp').write_text(content,encoding='utf-8')
