"""Packet transport through arbitrary non-MEM program/fallback records.

Complements the MEM packet-event partition without changing its frozen evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import small_holder_rule as f
from experiments.fixed_rule import certify_small_holder_packet_events as base

clock = base.clock


def cases():
    result = []
    for geometry in ('interior', 'left_edge', 'right_edge'):
        lp_modes = ('absent', 'carry', 'nonmemory') + (('drop',) if geometry == 'right_edge' else ())
        rp_modes = ('absent', 'carry', 'nonmemory') + (('drop',) if geometry == 'left_edge' else ())
        for lp in lp_modes:
            for rp in rp_modes:
                result.append(dict(name=f'nonMEM_{geometry}_{lp}_{rp}', geometry=geometry,
                                   lp=lp, rp=rp, actor=dict(name='quiet', role='quiet')))
    return tuple(result)


def prepare(event, interval):
    terms, original = base.prepare(event, interval)
    kind = terms.bounded('transport_kind', 4, 1, 15)
    targets = {channel: terms.variable(channel+'_nonmemory_target', 32) for channel in ('lp', 'rp')}
    def raw(pos, after=False):
        values = list(original(pos, after=after))
        for delta in f.STATIC_OFFSETS:
            if pos + delta == 0:
                values[f.COL[f'p{delta+3}_kind']] = kind
        for delta in f.OFFSETS:
            site = pos + delta
            for channel, source in (('lp', 1), ('rp', -1)):
                if event[channel] == 'nonmemory' and site == (0 if after else source):
                    values[f.COL[f's{delta+2}_{channel}_target']] = targets[channel]
        return tuple(values)
    return terms, raw


def certify_case(event, interval):
    terms, raw = prepare(event, interval)
    for pos in range(-4, 5):
        actual = terms.expression(f.self_description(), tuple(w for j in f.NEIGHBORHOOD for w in raw(pos+j)))
        expected = raw(pos, after=True)
        for (name, _), a, b in zip(f.SCHEMA, actual, expected):
            if a != b:
                raise AssertionError((event['name'], interval, pos, name, terms.nodes[a], terms.nodes[b]))
    return dict(name=event['name'], interval=interval, passed=True, full_raw_outputs=9*f.FIELDS,
                symbolic_terms=len(terms.nodes), all_nonMEM_kinds=15, arbitrary_packet_targets=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    out = Path(args.output)
    if out.exists():
        raise FileExistsError('preserve evidence')
    started = time.perf_counter()
    rows = []
    for interval in clock.regular_intervals():
        rows.extend(certify_case(event, interval) for event in cases())
        print(json.dumps(dict(interval=interval, cases=len(rows), seconds=time.perf_counter()-started)), flush=True)
    paths = [Path(__file__), Path(base.__file__), Path(clock.__file__)]
    result = dict(passed=True, pilot=False, event_families=len(cases()), case_count=len(rows), cases=rows,
                  descriptor_sha256=f.self_description().digest(),
                  complete_raw_output_words=sum(row['full_raw_outputs'] for row in rows),
                  source_sha256={str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
                  seconds=time.perf_counter()-started,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  limitation='Quiet non-MEM transport on canonical coherent zero-flag/Signal/Wf regular clocks. No general head/mail superposition, damaged geometry, packet-path or whole-period theorem.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'cases'}, indent=2), flush=True)


if __name__ == '__main__':
    main()
