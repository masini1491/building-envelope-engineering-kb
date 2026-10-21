#!/usr/bin/env python3
"""Fail-closed increment-aware audit of *fixed* CalculiX 2.21 contact output.

Reads .dat and .sta from a pinned artifact ZIP without changing solver files.
Reports printed force statistics and support RF3, but does not establish
independent contact traction balance, SPC dual or engineering admission.
"""
import argparse
import hashlib
import json
import math
import re
import zipfile
from collections import defaultdict

CASES = tuple(f'envelope_panels/u_base_contact_n{n}_{case}/panel'
              for n in (8, 16) for case in ('toward', 'away', 'unlinked'))
STA_ROW = re.compile(r'^\s*(\d+)\s+(\d+)\s+(\d+)\s+([\d]+)\s+([0-9.E+\-]+)\s+([0-9.E+\-]+)\s+([0-9.E+\-]+)\s*$', re.M)
SECTION = re.compile(r'^\s*(?:S T E P\s+(?P<step>\d+)|INCREMENT\s+(?P<inc>\d+))\s*$', re.M)
STATS = re.compile(r'statistics for slave set (\S+), master set (\S+) and time\s+([0-9.E+\-]+)')
FORCE = re.compile(r'total surface force \(fx,fy,fz\) and moment about the origin \(mx,my,mz\)\s*\n\s*([^\n]+)')
COG = re.compile(r'center of gravity and mean normal\s*\n\s*([^\n]+)')
MOMENT = re.compile(r'moment about the center of gravity\(mx,my,mz\)\s*\n\s*([^\n]+)')
AREA = re.compile(r'area,\s+normal force \(\+ = tension\) and shear force \(size\)\s*\n\s*([^\n]+)')
CONTACT_COUNT = re.compile(r'total number of contact elements for time\s+([0-9.E+\-]+)\s*\n\s*(\d+)')
SUPPORT = re.compile(r'forces \(fx,fy,fz\) for set (PLATE_EDGE_RF|RIB_END_RF|CENTER_RF) and time\s+([0-9.E+\-]+)\s*\n')
DATA_ROW = re.compile(r'^\s*(\d+)\s+([-+0-9.Ee]+)\s+([-+0-9.Ee]+)\s+([-+0-9.Ee]+)\s*$')


def fail(message):
    raise ValueError('CONTACT_INCREMENT_' + message)


def numeric_vector(text, count, label):
    try:
        value = tuple(float(x) for x in text.split())
    except ValueError:
        fail(label + '_NONNUMERIC')
    if len(value) != count or not all(math.isfinite(x) for x in value):
        fail(label + '_SHAPE_OR_NONFINITE')
    return value


def check_time(printed, expected):
    """Check display rounding only; never use printed time as increment identity."""
    if not math.isfinite(printed):
        fail('TIME_NONFINITE')
    # .dat shows ~8 sig. digits, .sta ~7; their rounding may collide.
    if abs(printed - expected) > 2e-6 * max(1., abs(expected)):
        fail('STA_DAT_TIME_MISMATCH')


def sta_increments(sta):
    result = {}
    for m in STA_ROW.finditer(sta):
        step, inc, attempt, iters = map(int, m.group(1, 2, 3, 4))
        total, step_time, delta = numeric_vector(' '.join(m.group(i) for i in (5, 6, 7)), 3, 'STA_TIME')
        if step == 0 or inc == 0 or attempt == 0 or iters == 0 or delta <= 0:
            fail('BAD_STA_ROW')
        if (step, inc) in result:
            fail('DUPLICATE_STA_INCREMENT')
        result[step, inc] = {'total_time': total, 'step_time': step_time, 'increment_time': delta}
    if not result:
        fail('NO_STA_ROWS')
    return result


def dat_increments(dat):
    markers = list(SECTION.finditer(dat))
    if not markers:
        fail('NO_DAT_MARKERS')
    records = {}
    step = None
    for k, m in enumerate(markers):
        if m.group('step') is not None:
            step = int(m.group('step'))
            continue
        if step is None:
            fail('INCREMENT_BEFORE_STEP')
        inc = int(m.group('inc'))
        key = (step, inc)
        if key in records:
            fail('DUPLICATE_DAT_INCREMENT')
        payload = dat[m.end(): markers[k + 1].start() if k + 1 < len(markers) else len(dat)]
        records[key] = payload
    if not records:
        fail('NO_DAT_INCREMENTS')
    return records


def supports(payload, total_time):
    values = {}
    matches = list(SUPPORT.finditer(payload))
    for k, m in enumerate(matches):
        label = m.group(1)
        check_time(float(m.group(2)), total_time)
        if label in values:
            fail('DUPLICATE_SUPPORT_' + label)
        block = payload[m.end():matches[k + 1].start() if k + 1 < len(matches) else len(payload)]
        seen = {}
        for line in block.splitlines():
            v = DATA_ROW.match(line)
            if v:
                nid = int(v.group(1))
                if nid in seen:
                    fail('DUPLICATE_NODE_' + label)
                seen[nid] = numeric_vector(' '.join(v.group(i) for i in (2, 3, 4)), 3, 'RF')
            elif seen:
                break
        if not seen:
            fail('EMPTY_SUPPORT_' + label)
        values[label] = (math.fsum(v[2] for v in seen.values()), set(seen))
    if set(values) != {'PLATE_EDGE_RF', 'RIB_END_RF', 'CENTER_RF'}:
        fail('SUPPORT_COVERAGE')
    groups = list(values.values())
    if any(groups[i][1] & groups[j][1] for i in range(3) for j in range(i + 1, 3)):
        fail('SUPPORT_NODE_OVERLAP')
    return {'plate_edge_rf3_n': values['PLATE_EDGE_RF'][0],
            'rib_end_rf3_n': values['RIB_END_RF'][0],
            'center_rf3_n': values['CENTER_RF'][0],
            'summed_support_rf3_n': math.fsum(values[k][0] for k in ('PLATE_EDGE_RF', 'RIB_END_RF', 'CENTER_RF')),
            'support_node_counts': {k: len(v[1]) for k, v in values.items()}}


def statistics(payload, total_time, linked):
    count = CONTACT_COUNT.findall(payload)
    blocks = list(STATS.finditer(payload))
    if not linked:
        if count or blocks:
            fail('UNLINKED_HAS_CONTACT_STATISTICS')
        return {'contact_statistics_blocks': 0, 'contact_pairs': [], 'contact_element_count': 0}
    if len(count) != 1:
        fail('CONTACT_COUNT_CARDINALITY')
    check_time(float(count[0][0]), total_time)
    contact_n = int(count[0][1])
    if not blocks:
        fail('MISSING_CONTACT_STATISTICS')
    by_pair = defaultdict(list)
    for k, m in enumerate(blocks):
        check_time(float(m.group(3)), total_time)
        chunk = payload[m.end():blocks[k + 1].start() if k + 1 < len(blocks) else len(payload)]
        row = {}
        for label, regex, length in [('force_and_origin_moment', FORCE, 6),
                                      ('center_and_normal', COG, 6),
                                      ('center_moment', MOMENT, 3),
                                      ('area_normal_shear', AREA, 3)]:
            hits = list(regex.finditer(chunk))
            if len(hits) != 1:
                fail('BAD_STATISTICS_FIELD_' + label)
            row[label] = numeric_vector(hits[0].group(1), length, label)
        by_pair[m.group(1), m.group(2)].append(row)
    if set(by_pair) != {('RIB_BASE_UNDERSIDE', 'PLATE_TOP')}:
        fail('UNEXPECTED_CONTACT_PAIR')
    result = []
    for (slave, master), rows in sorted(by_pair.items()):
        if len(rows) < 2 or any(row != rows[0] for row in rows[1:]):
            fail('SAME_INCREMENT_DUPLICATE_CONFLICT')
        result.append({'slave': slave, 'master': master, 'copies': len(rows),
                       'force_fz_n': rows[0]['force_and_origin_moment'][2],
                       'area_mm2': rows[0]['area_normal_shear'][0],
                       'mean_normal_z': rows[0]['center_and_normal'][5]})
    return {'contact_statistics_blocks': len(blocks), 'contact_element_count': contact_n, 'contact_pairs': result}


def audit_case(z, stem):
    dat = z.read(stem + '.dat').decode('utf-8', errors='replace')
    sta = z.read(stem + '.sta').decode('ascii', errors='replace')
    sta_records = sta_increments(sta)
    dat_records = dat_increments(dat)
    if set(sta_records) != set(dat_records):
        fail('STA_DAT_INCREMENT_SET_MISMATCH')
    linked = not stem.endswith('_unlinked/panel')
    rows = []
    for (step, inc), payload in sorted(dat_records.items()):
        t = sta_records[step, inc]['total_time']
        row = {'step': step, 'increment': inc, 'sta_total_time': t,
               **supports(payload, t), **statistics(payload, t, linked)}
        rows.append(row)
    return {'case': stem, 'increment_count': len(rows),
            'statistics_count': sum(row['contact_statistics_blocks'] for row in rows),
            'last_increment': rows[-1],
            'printed_total_time_collisions': [
                {'total_time': t, 'increments': v} for t, v in sorted(_formatted_collisions(rows).items())],
            'all_increment_keys': [[r['step'], r['increment']] for r in rows],
            'scope': 'READ_ONLY_INCREMENT_ALIGNED_OUTPUT_AUDIT_NOT_EQUILIBRIUM'}


def _formatted_collisions(rows):
    by_time = defaultdict(list)
    for row in rows:
        by_time[format(row['sta_total_time'], '.6g')].append(row['increment'])
    return {k: v for k, v in by_time.items() if len(v) > 1}


def audit_archive(path):
    with zipfile.ZipFile(path) as z:
        output = [audit_case(z, stem) for stem in CASES]
    with open(path, 'rb') as source:
        digest = hashlib.sha256(source.read()).hexdigest()
    return {'source_artifact_sha256': digest,
            'cases': output,
            'contact_force_oracle': 'NOT_ESTABLISHED',
            'independent_external_spc_dual': 'NOT_ESTABLISHED',
            'engineering_acceptance': 'NOT_ADMITTED'}


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('artifact_zip')
    args = cli.parse_args()
    print(json.dumps(audit_archive(args.artifact_zip), ensure_ascii=False, indent=2, allow_nan=False))
