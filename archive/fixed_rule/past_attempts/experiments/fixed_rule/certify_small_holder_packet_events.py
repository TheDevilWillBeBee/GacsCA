"""Full-raw packet transport/delivery identities and controller interactions.

Diagnostic refinement only. Incoming tracks are specified independently of F;
complete old/new physical records are then compared through F's description.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c
from gacsca.fixed_rule.wordcode import ADD, MASK
from experiments.fixed_rule import certify_small_holder_clock_events as clock
from experiments.fixed_rule.prove_small_holder_boundary import validate


def cases():
    result = []
    for geometry in ('interior', 'left_edge', 'right_edge'):
        lp_modes = ('absent', 'carry', 'miss', 'hit') + (('drop',) if geometry == 'right_edge' else ())
        rp_modes = ('absent', 'carry', 'miss', 'hit') + (('drop',) if geometry == 'left_edge' else ())
        for lp in lp_modes:
            for rp in rp_modes:
                result.append(dict(name=f'{geometry}_{lp}_{rp}', geometry=geometry,
                                   lp=lp, rp=rp, actor=dict(name='quiet', role='quiet')))
        result.append(dict(name=f'{geometry}_nonmemory_match', geometry=geometry,
                           lp='nonmemory', rp='nonmemory', actor=dict(name='quiet', role='quiet')))
    actors = [dict(name='read_a', role='read_a'), dict(name='load', role='load'),
              dict(name='write', role='write')]
    actors += [dict(name=f'read_b_{kind}', role='read_b', opcode=kind) for kind in c.ALU_KINDS]
    actors += [dict(name=f'send_{direction}_{hops}', role='send', direction=direction, hops=hops)
               for direction in (0, 1) for hops in range(8)]
    for actor in actors:
        result.append(dict(name='interior_deliver_' + actor['name'], geometry='interior',
                           lp='hit', rp='hit', actor=actor))
        if actor['role'] == 'send':
            result.append(dict(name='interior_overwrite_' + actor['name'], geometry='interior',
                               lp='carry', rp='carry', actor=actor))
    for geometry in ('left_edge', 'right_edge'):
        result.append(dict(name=geometry + '_deliver_write', geometry=geometry,
                           lp='hit', rp='hit', actor=dict(name='write', role='write')))
    return tuple(result)


def prepare(event, interval):
    actor = dict(event['actor'], family='position')
    terms, base = clock.prepare(actor, interval)
    geometry = event['geometry']
    lo, hi = {'interior': (1, f.Q - 2), 'left_edge': (0, 0),
              'right_edge': (f.Q - 1, f.Q - 1)}[geometry]
    terms.bounded('base_address', 15, lo, hi)
    zero, one = terms.const(0), terms.const(1)
    center = base(0)
    index = center[f.COL['p3_index']]
    nonmemory = event['lp'] == 'nonmemory' or event['rp'] == 'nonmemory'
    if nonmemory:
        assert actor['role'] == 'quiet'
    before, after, deliveries = {}, {}, {}
    for channel in ('lp', 'rp'):
        mode = event[channel]
        edge = geometry == ('right_edge' if channel == 'lp' else 'left_edge')
        target = terms.variable(channel + '_incoming_target', 32)
        payload = terms.variable(channel + '_incoming_data', 64)
        valid = one
        if mode == 'absent':
            count = terms.variable(channel + '_incoming_remaining', 3)
            valid = zero
        elif mode == 'drop':
            assert edge
            count = zero
        elif mode == 'carry':
            count = terms.bounded(channel + '_incoming_remaining', 3, 2 if edge else 1, 7)
        elif mode in ('hit', 'miss', 'nonmemory'):
            count = terms.const(int(edge))
            if mode in ('hit', 'nonmemory'):
                target = index
            else:
                terms.unequal(target, index)
        else:
            raise ValueError(mode)
        before[channel] = dict(target=target, data=payload, remaining=count, valid=valid)
        deliveries[channel] = mode == 'hit'
        if mode in ('carry', 'miss', 'nonmemory'):
            # On carry, count >= 2; on miss/nonmemory at an edge, count = 1.
            # Thus the ordinary u64 subtraction fits the three-bit output.
            remaining = terms.op(ADD, count, terms.const(MASK)) if edge else count
            after[channel] = dict(target=target, data=payload, remaining=remaining, valid=one)
        else:
            after[channel] = dict.fromkeys(('target', 'data', 'remaining', 'valid'), zero)
    delivered = (before['rp']['data'] if deliveries['rp'] else
                 before['lp']['data'] if deliveries['lp'] else None)

    def raw(pos, after_step=False, **kwargs):
        # Accept the common raw(..., after=True) certificate interface.
        after_step = kwargs.pop('after', after_step)
        assert not kwargs
        values = list(base(pos, after=after_step))
        for delta in f.STATIC_OFFSETS:
            if pos + delta == 0:
                # Quiet actor permits arbitrary metadata except this explicit kind.
                if actor['role'] == 'quiet':
                    values[f.COL[f'p{delta+3}_kind']] = terms.const(c.LOOP if nonmemory else c.MEM)
        for delta in f.OFFSETS:
            site = pos + delta
            prefix = f's{delta+2}_'
            if not after_step:
                for channel, source in (('lp', 1), ('rp', -1)):
                    if site == source:
                        for name, value in before[channel].items():
                            values[f.COL[prefix + channel + '_' + name]] = value
            elif site == 0:
                if delivered is not None and actor['role'] != 'write':
                    values[f.COL[prefix + 'data']] = delivered
                for channel in ('lp', 'rp'):
                    emitted = actor['role'] == 'send' and channel == ('lp' if actor['direction'] else 'rp')
                    if not emitted:
                        for name, value in after[channel].items():
                            values[f.COL[prefix + channel + '_' + name]] = value
        return tuple(values)
    return terms, raw


def certify_case(event, interval, description=None):
    desc = f.self_description() if description is None else description
    validate(desc)
    terms, raw = prepare(event, interval)
    for pos in range(-4, 5):
        actual = terms.expression(desc, tuple(w for j in f.NEIGHBORHOOD for w in raw(pos+j)))
        expected = raw(pos, after=True)
        for (name, _), a, b in zip(f.SCHEMA, actual, expected):
            if a != b:
                raise AssertionError((event['name'], interval, pos, name, terms.nodes[a], terms.nodes[b]))
    return dict(name=event['name'], interval=interval, passed=True,
                full_raw_outputs=9*f.FIELDS, symbolic_terms=len(terms.nodes),
                bounds={terms.nodes[x][1]: list(bounds) for x, bounds in terms.ranges.items()},
                disequalities=[(terms.nodes[a], terms.nodes[b]) for a, b in sorted(terms.disequalities)])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', action='store_true')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    out = Path(args.output)
    if out.exists():
        raise FileExistsError('preserve evidence')
    started = time.perf_counter()
    intervals = clock.regular_intervals()[:1] if args.pilot else clock.regular_intervals()
    rows = []
    for interval in intervals:
        for event in cases():
            rows.append(certify_case(event, interval))
        print(json.dumps(dict(interval=interval, cases=len(rows), seconds=time.perf_counter()-started)), flush=True)
    sources = [Path(__file__), Path(clock.__file__), Path('experiments/fixed_rule/certify_small_holder_position_events.py'),
               Path('experiments/fixed_rule/certify_small_holder_scan_events.py'),
               Path('experiments/fixed_rule/certify_small_holder_local_events.py'),
               Path('experiments/fixed_rule/certify_small_holder_rom_dataflow.py')]
    result = dict(passed=True, pilot=args.pilot, event_families=len(cases()), case_count=len(rows),
                  cases=rows, complete_raw_output_words=sum(row['full_raw_outputs'] for row in rows),
                  descriptor_sha256=f.self_description().digest(),
                  source_sha256={str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in sources},
                  seconds=time.perf_counter()-started,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  limitation='Canonical coherent geometry, zero flags/Signal/Wf, two incoming tracks, quiet or stated one-head interaction, regular active clocks. No damaged geometry, packet trains, arbitrary head location, whole-period or nested/noisy theorem.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'cases'}, indent=2), flush=True)


if __name__ == '__main__':
    main()
