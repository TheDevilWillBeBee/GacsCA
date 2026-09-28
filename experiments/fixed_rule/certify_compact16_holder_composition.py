"""Direct smaller-rule controller paths and regular-mail composition checks.

Diagnostics only. Canonical entry, clock barriers, capture/forcing and the
whole-period induction remain explicit separate obligations.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import sys
import time
from types import FunctionType, SimpleNamespace
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c
from gacsca.fixed_rule import compact16_holder_program as p
from experiments.fixed_rule import certify_compact16_holder_clock_events as clock
from experiments.fixed_rule import certify_compact16_holder_meta_paths as meta
from experiments.fixed_rule import certify_compact16_holder_instruction_paths as ordinary
from experiments.fixed_rule import certify_compact16_holder_dispatch_paths as dispatch
from experiments.fixed_rule import certify_compact16_holder_event_support as support
from experiments.fixed_rule import certify_compact16_holder_mail_factorization as mail
from experiments.fixed_rule import prove_compact16_holder_packet_flight as flight
from experiments.fixed_rule import certify_retimed_holder_mail_schedule as schedule_reference


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bind(function, **extra):
    namespace = dict(function.__globals__)
    namespace.update(f=f, c=c, p=p, **extra)
    result = FunctionType(function.__code__, namespace, function.__name__,
                          function.__defaults__, function.__closure__)
    result.__kwdefaults__ = function.__kwdefaults__
    return result


def schedule(loaded, rom=None):
    check = bind(schedule_reference.check,
                 verify_geometry=bind(schedule_reference.verify_geometry),
                 verify_packets=bind(schedule_reference.verify_packets),
                 phases=bind(schedule_reference.phases),
                 paths=SimpleNamespace(regular_intervals=clock.regular_intervals))
    return check(loaded, rom)


def verify_clock_receipt():
    path = Path('figs/fixed_rule/compact16_holder_clock_events_v1.json')
    receipt = json.loads(path.read_text())
    assert receipt['passed'] and receipt['descriptor_sha256'] == f.self_description().digest()
    assert receipt['source_sha256'] == sha(clock.__file__)
    expected = {(event['family'], event['name'], interval)
                for event in clock.cases() for interval in clock.regular_intervals()}
    actual = {(row['family'], row['name'], tuple(row['interval']))
              for row in receipt['cases'] if row['passed'] and row['full_raw_outputs'] == 9*f.FIELDS}
    assert actual == expected and receipt['case_count'] == len(expected)
    return {str(path): sha(path)}


def paths():
    inputs = verify_clock_receipt()
    geometry = meta.verify_rom()
    exterior = support.certify()
    leaves = []
    for interval in clock.regular_intervals():
        leaves.append(dict(kind='last_left', result=meta.prove_last_left(interval)))
        leaves.append(dict(kind='MEM_fetch', result=dispatch.prove_memory_leaf(interval)))
        for key in ordinary.nonmemory_cases():
            leaves.append(dict(kind='nonMEM', result=ordinary.prove_leaf(key, interval)))
        print(json.dumps(dict(interval=interval, additional_leaves=len(leaves))), flush=True)
    trace = hashlib.sha256()
    rows = []
    for pc, op in enumerate(p.layout().instructions):
        if op.kind == c.META:
            continue
        for third in ((False, True) if op.kind == c.IF_THIRD else (False,)):
            path = ordinary.InstructionPath(pc, third=third)
            row = path.check()
            rows.append((pc, op.kind, int(third), row['duration'],
                         -1 if row['final_head'] is None else row['final_head'], row['leaf_segments']))
            trace.update(json.dumps(dict(result=row, steps=path.steps), sort_keys=True).encode())
        if pc % 2048 == 0:
            print(json.dumps(dict(pc=pc, ordinary_paths=len(rows))), flush=True)
    length = len(p.base_rom())
    domains = ((0, length-2), (length-1, length-1), (length, f.Q-6), (f.Q-5, f.Q-1))
    metadata = []
    for pc, op in enumerate(p.layout().instructions):
        if op.kind == c.META:
            for domain in domains:
                row = meta.MetaPath(pc, domain).check()
                trace.update(json.dumps(row, sort_keys=True).encode())
                metadata.append({key: value for key, value in row.items() if key != 'steps'})
    loaded = {'ordinary': {'rows': rows}, 'meta': {'paths': metadata}}
    routes = []
    for route in dispatch.routes(loaded):
        row = dispatch.DispatchPath(route['start'], route['pc']).check()
        routes.append((route['origin'], route['origin_id'], route['start'], route['pc'],
                       row['duration'], int(route['requires_mail_composition'])))
        trace.update(json.dumps(dict(route=route, result=row), sort_keys=True).encode())
    loaded['dispatch'] = {'rows': routes}
    timed = schedule(loaded)
    return dict(passed=True, input_sha256=inputs, ROM_geometry=geometry,
                quiet_exterior_support=exterior, additional_leaves=leaves,
                ordinary_rows=rows, ordinary_path_count=len(rows), metadata_paths=metadata,
                metadata_path_count=len(metadata), dispatch_rows=routes,
                dispatch_path_count=len(routes), packet_schedule=timed,
                trace_sha256=trace.hexdigest(), query_domains=domains,
                scope='Full controller physical paths and conditional packet schedule for the new rule/ROM. '
                      'SEND-to-successor composition additionally uses the separate regular-mail proof. '
                      'Canonical entry, reset/vote/capture/forcing/commit and whole-period closure remain open.')


def mail_checks():
    results = []
    dependency = mail.certify_support()
    for interval in clock.regular_intervals():
        for phase in (None, *range(8)):
            results.append(mail.certify_case(phase, interval))
        print(json.dumps(dict(interval=interval, mail_cases=len(results))), flush=True)
    packets = [flight.prove_case(hops) for hops in range(8)]
    return dict(passed=True, mail_support=dependency, mail_cases=results,
                case_count=len(results), packet_flight_cases=packets,
                complete_raw_output_words=sum(row['full_raw_output_words'] for row in results),
                scope='Direct complete-descriptor regular-mail factorization and exact packet-coordinate '
                      'induction. Canonical coherent geometry, uniform regular active clock, one head or '
                      'quiet, zero flags/Signal/Wf; arbitrary packet words. Protected MEM targets, '
                      'collision and read/write ordering are checked by the separate schedule.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--part', choices=('paths', 'mail'), required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    start = time.perf_counter()
    result = paths() if args.part == 'paths' else mail_checks()
    result.update(descriptor_sha256=f.self_description().digest(),
                  ROM_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),
                  seconds=time.perf_counter()-start,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    sources = {Path(__file__).resolve()}
    for module in tuple(sys.modules.values()):
        filename = getattr(module, '__file__', None)
        if filename and '/fixed_rule/' in str(Path(filename).resolve()):
            sources.add(Path(filename).resolve())
    result['source_sha256'] = {str(path.relative_to(Path.cwd())): sha(path) for path in sorted(sources)}
    with args.output.open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(passed=True, part=args.part, output=str(args.output),
                          seconds=result['seconds'], host_max_rss_kib=result['host_max_rss_kib'])), flush=True)


if __name__ == '__main__':
    main()
