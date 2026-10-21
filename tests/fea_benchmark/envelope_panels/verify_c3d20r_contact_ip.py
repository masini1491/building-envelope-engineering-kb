"""Pinned, read-only C3D20R contact IP stress regional diagnostic.

The printed CSTR values lack quadrature coordinates/weights. Every reported
regional statistic is per-record UNWEIGHTED, with element-face midpoint used
solely to assign a physical x-zone. NOT a traction integral or design check.
"""
import argparse
import hashlib
import json
import math
import re
import statistics
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

PINS = {
    'ip': '4ac6e4f277ad9ccde2ea93f37c465a254400038fad249eef896421fb999669f1',
    'n16': 'b44717b04ad268e2cf49197d8a03444e5cec69897c2d7f6fbed4423e6256ce52',
    'n24': '4fb99ab36edd3fbaba7fb23171eaea04d1ee895d38174f390de874fca723c823',
}
BASE_CARD = '*CONTACT PRINT,SLAVE=RIB_BASE_UNDERSIDE,MASTER=PLATE_TOP\nCF,CFN,CNUM\n'
IP_CARD = '*CONTACT PRINT,SLAVE=RIB_BASE_UNDERSIDE,MASTER=PLATE_TOP\nCF,CFN,CNUM,CSTR\n'
HEADER = 'contact stress (slave element+face,press,tang1,tang2) for all contact elements and time 0.1000000E+01'
CONTACT_FORCE = re.compile(r'total surface force \(fx,fy,fz\) and moment about the origin \(mx,my,mz\)')
CONTACT_AREA = re.compile(r'area,  normal force \(\+ = tension\) and shear force \(size\)')
NUMBER = re.compile(r'[+-]?\d+\.\d+E[+-]\d+')


def fail(code):
    raise ValueError('C3D20R_CONTACT_IP_' + code)


def open_pinned(path, key):
    f = Path(path)
    if f.is_symlink() or not f.is_file() or not 0 < f.stat().st_size < 32_000_000:
        fail('MISSING_OR_OVERSIZE_ZIP')
    with f.open('rb') as source:
        if hashlib.file_digest(source, 'sha256').hexdigest() != PINS[key]:
            fail('SOURCE_SHA256')
    return ZipFile(f)


def read_member(z, path, max_bytes=20_000_000):
    try:
        m = z.getinfo(path)
        if m.file_size > max_bytes or m.file_size < 1:
            fail('ZIP_MEMBER_SIZE')
        return z.read(path)
    except KeyError:
        fail('ZIP_MEMBER_MISSING')


def parse_input(source):
    """Map rib base S1 physical centroids (initial coordinates only)."""
    nodes = {}
    elements = {}
    slave = set()
    mode = None
    pending = []
    for line in source.splitlines():
        t = line.strip()
        if t == '*NODE':
            mode = 'NODE'; continue
        if t == '*ELEMENT,TYPE=C3D20R,ELSET=RIB':
            mode = 'RIB'; pending=[]; continue
        if t == '*SURFACE,NAME=RIB_BASE_UNDERSIDE,TYPE=ELEMENT':
            mode = 'SLAVE'; continue
        if t.startswith('*'):
            mode = None; continue
        if not t or mode is None: continue
        if mode == 'NODE':
            row=t.split(',')
            if len(row)!=4: fail('NODE_FORMAT')
            k=int(row[0]);xyz=tuple(float(v) for v in row[1:])
            if k in nodes or not all(map(math.isfinite,xyz)):fail('NODE_FORMAT')
            nodes[k]=xyz
        elif mode == 'RIB':
            pending.extend(int(i) for i in t.split(',') if i.strip())
            if len(pending)==21:
                eid=pending[0]
                if eid in elements:fail('RIB_CONNECTIVITY')
                elements[eid]=tuple(pending[1:]);pending=[]
            elif len(pending)>21:fail('RIB_CONNECTIVITY')
        elif mode == 'SLAVE':
            v=t.split(',')
            if len(v)!=2 or v[1].strip()!='S1':fail('SLAVE_FACE')
            eid=int(v[0])
            if eid in slave:fail('SLAVE_FACE')
            slave.add(eid)
    if not elements or not slave or not slave<=set(elements) or not nodes or pending:
        fail('INPUT_TOPOLOGY')
    result={}
    for eid in slave:
        corners=elements[eid][:4]
        if not set(corners)<=set(nodes):fail('INPUT_NODE_IDENTITY')
        x=sum(nodes[k][0] for k in corners)/4
        y=sum(nodes[k][1] for k in corners)/4
        if not 0 <= x <= 1200 or abs(y)>25:fail('CENTROID_BOUNDS')
        result[eid]=(x,y)
    return result


def parse_cstr_final(dat, known_faces):
    if dat.count(HEADER)!=1:fail('CSTR_FINAL_HEADER')
    before, after=dat.split(HEADER,1)
    m=re.search(r'total number of contact elements for time\s+0\.1000000E\+01\s+(\d+)\s*$',before)
    if not m: fail('CSTR_COUNT_HEADER')
    declared=int(m.group(1))
    section=after.split(' statistics for slave set',1)
    if len(section)!=2: fail('CSTR_FINAL_TERMINATOR')
    groups=defaultdict(list)
    for row in section[0].splitlines():
        if not row.strip():continue
        v=row.split()
        if len(v)!=5:fail('CSTR_ROW')
        try: eid,face=int(v[0]),int(v[1]);p,sh1,sh2=map(float,v[2:])
        except ValueError:fail('CSTR_ROW')
        if face!=1 or eid not in known_faces or not all(map(math.isfinite,(p,sh1,sh2))) or p<0:
            fail('CSTR_FACE_VALUE')
        groups[eid].append(p)
    if not groups or sum(map(len,groups.values())) !=declared:
        fail('CSTR_COUNT_MISMATCH')
    return groups,declared


def dat_summary(dat):
    f=list(CONTACT_FORCE.finditer(dat));a=list(CONTACT_AREA.finditer(dat))
    if not f or not a:fail('DAT_CONTACT_SUMMARY')
    fvals=NUMBER.findall(dat[f[-1].end():].splitlines()[2])
    avals=NUMBER.findall(dat[a[-1].end():].splitlines()[2])
    if len(fvals)!=6 or len(avals)!=3:fail('DAT_CONTACT_SUMMARY')
    return float(fvals[2]),float(avals[0])


def zone(x):
    d=min(x,1200-x)
    if d <150: return 'end_0_150_mm'
    if d <300: return 'transition_150_300_mm'
    return 'interior_300_600_mm'


def regional_stats(groups,centers):
    buckets=defaultdict(lambda: {'pressures':[], 'elements':set()})
    for eid,pressure in groups.items():
        z=zone(centers[eid][0]);b=buckets[z]
        b['elements'].add(eid);b['pressures'].extend(pressure)
    output={}
    for name in ('end_0_150_mm','transition_150_300_mm','interior_300_600_mm'):
        b=buckets[name];v=b['pressures']
        if not v: fail('ZONE_MISSING_'+name)
        output[name]={'active_slave_faces':len(b['elements']), 'cstr_rows':len(v),
                      'max_cpress_n_mm2':max(v), 'unweighted_mean_cpress_n_mm2':statistics.mean(v),
                      'unweighted_median_cpress_n_mm2':statistics.median(v)}
    return output


def verify(ipfile,baseline16,baseline24):
    with open_pinned(ipfile,'ip') as ip,open_pinned(baseline16,'n16') as b16,open_pinned(baseline24,'n24') as b24:
        result={}
        for n,baseline in ((16,b16),(24,b24)):
            i=f'ip{n}_toward/panel.';b=f'p{n}_toward/panel.'
            source=read_member(ip,i+'inp').decode()
            prior=read_member(baseline,b+'inp').decode()
            if source.count(IP_CARD)!=1 or source.replace(IP_CARD,BASE_CARD)!=prior:
                fail('PHYSICAL_DECK_DRIFT')
            if read_member(ip,i+'sta') != read_member(baseline,b+'sta'):
                fail('STA_DRIFT')
            dat=read_member(ip,i+'dat').decode(errors='replace')
            olddat=read_member(baseline,b+'dat').decode(errors='replace')
            if dat_summary(dat)!=dat_summary(olddat):
                fail('CONTACT_GLOBAL_DRIFT')
            coords=parse_input(source)
            pressures,declared=parse_cstr_final(dat,coords)
            result[n]={'cstr_rows':declared,'active_slave_faces':len(pressures),
                       'printed_contact_fz_n':dat_summary(dat)[0],
                       'printed_contact_area_mm2':dat_summary(dat)[1],
                       'element_centroid_zones':regional_stats(pressures,coords)}
        return {'scope':'C3D20R_CONTACT_IP_CSTR_REGIONAL_SAMPLE_ONLY_NOT_DESIGN',
                'source_artifact_sha256':PINS,'meshes':result,
                'centroid_zone_edges_mm':[0,150,300,600],
                'integration_point_coordinates':'NOT_AVAILABLE',
                'quadrature_weights':'NOT_AVAILABLE',
                'area_weighted_contact_stress':'NOT_ESTABLISHED',
                'force_from_cstr_integration':'NOT_ESTABLISHED',
                'contact_local_convergence':'NOT_ESTABLISHED',
                'engineering_acceptance':'NOT_ADMITTED'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('ip_zip');p.add_argument('baseline16_zip');p.add_argument('baseline24_zip')
    v=p.parse_args();print(json.dumps(verify(v.ip_zip,v.baseline16_zip,v.baseline24_zip),indent=2,sort_keys=True,allow_nan=False))
