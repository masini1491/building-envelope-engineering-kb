"""Controlled distributed synthetic face-pressure comparator; never a design capacity."""
from pathlib import Path
import sys
from quadratic_contact_trial import deck as original_deck

PRESSURE_N_MM2 = 0.0001
PLATE_AREA_MM2 = 1200. * 300.
APPLIED_TOTAL_Z_N = PRESSURE_N_MM2 * PLATE_AREA_MM2  # P1 bottom face -> inward +Z


def deck(n, case):
    if type(n) is not int or n not in (8, 16) or case not in ('toward', 'unlinked', 'clearance'):
        raise ValueError('C3D20R_PRESSURE_SCOPE')
    original = original_deck(n, case)
    imposed = '-0.02000000' if case == 'clearance' else '0.02000000'
    old = '*BOUNDARY\nCENTER_RF,3,3,' + imposed + '\n'
    if original.count(old) != 1 or original.count('*DLOAD') != 0:
        raise ValueError('C3D20R_PRESSURE_DRIVER_ANCHOR')
    revised = original.replace(old, '*DLOAD\nPLATE,P1,0.00010000\n')
    revised = revised.replace('Synthetic explicit C3D20R open-U',
                              'Synthetic distributed-pressure C3D20R open-U', 1)
    if revised.count('*DLOAD') != 1 or 'CENTER_RF,3,3,' in revised or revised.count('*NODE PRINT') != 3:
        raise ValueError('C3D20R_PRESSURE_DECK_CONTRACT')
    return revised


if __name__ == '__main__':
    if len(sys.argv) != 5 or sys.argv[1] != '--generate':
        raise SystemExit('usage: --generate EMPTY_DIRECTORY MESH CASE')
    folder = Path(sys.argv[2])
    if folder.exists() or folder.is_symlink():
        raise ValueError('C3D20R_PRESSURE_NOT_FRESH')
    content = deck(int(sys.argv[3]), sys.argv[4])
    folder.mkdir(parents=True)
    (folder / 'panel.inp').write_text(content, encoding='utf-8')
