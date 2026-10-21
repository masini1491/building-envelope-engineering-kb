"""Bounded FRD contact-field audit for pinned CCX 2.21 artifacts; NOT DESIGN.

FRD is fixed-width: node IDs can touch negative displacement values.  Never use
whitespace token count to select lines, or nonzero field entries disappear.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
from zipfile import ZipFile

FIELD_CARD = '*CONTACT FILE\nCDIS,CSTR\n'
FLOAT = re.compile(r'[+-]?\d+\.\d+E[+-]\d+')
PINS = {
    'field': '23dd21cb4e43a6a6043a149de4dc5151e28648a315730239f20f542511db10d5',
    'n16': 'b44717b04ad268e2cf49197d8a03444e5cec69897c2d7f6fbed4423e6256ce52',
    'n24': '4fb99ab36edd3fbaba7fb23171eaea04d1ee895d38174f390de874fca723c823',
}


def reject(msg):
    raise ValueError('C3D20R_FIELD_' + msg)


def verified_zip(path, digest):
    path = Path(path)
    if not path.is_file() or path.is_symlink() or not 0 < path.stat().st_size < 32_000_000:
        reject('MISSING_OR_OVERSIZE_ZIP')
    with path.open('rb') as stream:
        actual = hashlib.file_digest(stream, 'sha256').hexdigest()
    if actual != digest:
        reject('ARTIFACT_SHA256')
    return ZipFile(path)


def parse_frd(text):
    lines = text.splitlines()
    coords = {}
    in_nodes = False
    for line in lines:
        if line.lstrip().startswith('2C '):
            in_nodes = True
            continue
        if in_nodes and line.startswith(' -3'):
            break
        if in_nodes and line.startswith(' -1'):
            node = int(line[3:13])
            xyz = FLOAT.findall(line[13:])
            if node in coords or len(xyz) != 3:
                reject('FRD_NODE_FORMAT')
            coords[node] = tuple(map(float, xyz))
    if not coords:
        reject('FRD_NO_NODES')
    blocks = []
    i = 0
    while i < len(lines):
        if not lines[i].startswith(' -4  CONTACT'):
            i += 1
            continue
        headers = [line[5:].split()[0] for line in lines[i+1:i+7]]
        if headers != ['COPEN','CSLIP1','CSLIP2','CPRESS','CSHEAR1','CSHEAR2']:
            reject('FRD_CONTACT_HEADERS')
        values = {}
        j = i + 7
        while j < len(lines) and not lines[j].startswith(' -3'):
            if lines[j].startswith(' -1'):
                node = int(lines[j][3:13])
                nums = FLOAT.findall(lines[j][13:])
                if len(nums) != 6 or node in values:
                    reject('FRD_CONTACT_ROW')
                v = tuple(map(float, nums))
                if not all(map(math.isfinite, v)):
                    reject('FRD_NONFINITE')
                values[node] = v
            j += 1
        if j == len(lines) or set(values) != set(coords):
            reject('FRD_CONTACT_COVERAGE')
        blocks.append(values)
        i = j + 1
    if len(blocks) != 10:
        reject('FRD_CONTACT_STEPS')
    return coords, blocks


def contact_dat(dat):
    x = list(re.finditer(r'total surface force \(fx,fy,fz\) and moment about the origin \(mx,my,mz\)', dat))
    y = list(re.finditer(r'area,  normal force \(\+ = tension\) and shear force \(size\)', dat))
    if not x or not y:
        reject('DAT_NO_CONTACT_PRINT')
    fx = FLOAT.findall(dat[x[-1].end():].splitlines()[2])
    area = FLOAT.findall(dat[y[-1].end():].splitlines()[2])
    if len(fx) != 6 or len(area) != 3:
        reject('DAT_CONTACT_PRINT_FORMAT')
    return {'fz_n': float(fx[2]), 'area_mm2': float(area[0])}


def run(field_zip, baseline16_zip, baseline24_zip):
    with verified_zip(field_zip,PINS['field']) as f, \
         verified_zip(baseline16_zip,PINS['n16']) as b16, \
         verified_zip(baseline24_zip,PINS['n24']) as b24:
        results = {}
        for n, baseline in ((16,b16),(24,b24)):
            ff = f'f{n}_toward/panel.'
            bb = f'p{n}_toward/panel.'
            if f.read(ff+'inp').replace(FIELD_CARD.encode(),b'') != baseline.read(bb+'inp'):
                reject('PHYSICAL_INPUT_DRIFT')
            for ext in ('dat','sta'):
                if f.read(ff+ext) != baseline.read(bb+ext):
                    reject('PHYSICAL_OUTPUT_DRIFT')
            coords,blocks = parse_frd(f.read(ff+'frd').decode('utf-8',errors='replace'))
            cp = {coords[k]: row[3] for k,row in blocks[-1].items() if row[3] > 0}
            if not cp or any(row[3]<0 for row in blocks[-1].values()):
                reject('CONTACT_PRESSURE_ABSENT_OR_NEGATIVE')
            if len(cp) != sum(row[3]>0 for row in blocks[-1].values()):
                reject('ACTIVE_COORDINATE_COLLISION')
            dat = contact_dat(f.read(ff+'dat').decode('utf8',errors='replace'))
            if dat['fz_n']<=0 or dat['area_mm2']<=0:
                reject('CONTACT_FORCE_ABSENT')
            results[n] = {'active_cpress_nodes':len(cp),
                'max_cpress_n_mm2':max(cp.values()),
                'median_active_cpress_n_mm2':statistics.median(cp.values()),
                'printed_force_fz_n':dat['fz_n'], 'printed_area_mm2':dat['area_mm2'],
                'num_nodes':len(coords), 'num_increments_with_contact_field':len(blocks),
                'active':cp}
        common=set(results[16]['active']) & set(results[24]['active'])
        if not common:
            reject('NO_COMMON_ACTIVE_COORDINATES')
        matched_l1=sum(abs(results[16]['active'][p]-results[24]['active'][p]) for p in common)
        denominator=sum(abs(results[16]['active'][p]) for p in common)
        if denominator<=0:reject('NO_NONZERO_MATCHED_PRESSURE')
        matched_rel_l1=matched_l1/denominator
        maxima_delta = (results[16]['max_cpress_n_mm2']-results[24]['max_cpress_n_mm2'])/results[16]['max_cpress_n_mm2']
        for n in results:results[n].pop('active')
        return {'scope':'SYNTHETIC_CONTACT_FIELD_NOT_DESIGN',
            'artifact_sha256':PINS,'meshes':results,
            'matched_positive_nodes':len(common),
            'common_node_unweighted_relative_l1_vs_n16':matched_rel_l1,
            'peak_pressure_relative_drop_n16_to_n24':maxima_delta,
            'contact_pressure_distribution_convergence':'NOT_ESTABLISHED',
            'independent_local_traction_oracle':'NOT_ESTABLISHED',
            'engineering_acceptance':'NOT_ADMITTED'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('field_zip')
    parser.add_argument('baseline16_zip')
    parser.add_argument('baseline24_zip')
    args = parser.parse_args()
    print(json.dumps(run(args.field_zip,args.baseline16_zip,args.baseline24_zip),
                     indent=2,sort_keys=True,allow_nan=False))
