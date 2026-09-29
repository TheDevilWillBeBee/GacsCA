"""Complete-descriptor phase interfaces for the fixed compact16 candidate.

Proof diagnostics only. No checker supplies an evolving physical transition.
Entry-to-exit semantic induction remains a separate obligation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import sys
import time
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_program as p
from experiments.fixed_rule import certify_compact16_holder_clock_mail_factorization as mail
from experiments.fixed_rule import certify_compact16_holder_quiet_barriers as quiet
from experiments.fixed_rule import certify_compact16_holder_signal_flag_boundaries as boundary
from experiments.fixed_rule import prove_compact16_holder_reset_encoding as reset
from experiments.fixed_rule import join_compact16_holder_signal_schedule as join
from experiments.fixed_rule import certify_compact16_holder_composition as composition


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def checks():
    rows = []
    for phase in (None, *range(8)):
        rows.append(mail.certify_case(phase))
        print(json.dumps(dict(all_clock_mail_phase=phase, passed=True)), flush=True)
    quiet_result = quiet.certify()
    print(json.dumps(dict(quiet_barriers=True)), flush=True)
    reset_result = reset.prove()
    print(json.dumps(dict(full_raw_reset=True)), flush=True)
    signals = dict(passed=True, descriptor_sha256=f.self_description().digest(),
                   formulas=boundary.certify_formulas(),
                   clearing=boundary.clearing_implications(), off_window=boundary.off_window())
    path = Path('figs/fixed_rule/compact16_holder_paths_v1.json')
    receipt = json.loads(path.read_text())
    assert receipt['passed'] and receipt['descriptor_sha256'] == f.self_description().digest()
    assert receipt['ROM_sha256'] == sha_rom()
    for source, digest in {**receipt['source_sha256'], **receipt['input_sha256']}.items():
        assert sha(source) == digest, source
    loaded = {'ordinary': {'rows': receipt['ordinary_rows']},
              'meta': {'paths': receipt['metadata_paths']},
              'dispatch': {'rows': receipt['dispatch_rows']}}
    replay = composition.schedule(loaded)
    assert json.loads(json.dumps(replay)) == receipt['packet_schedule']
    replay['descriptor_sha256'] = f.self_description().digest()
    joined = join.check(replay, signals)
    return dict(passed=True, all_clock_mail_cases=rows,
                all_clock_mail_raw_output_words=sum(row['complete_raw_output_words'] for row in rows),
                quiet_barriers=quiet_result, full_raw_reset=reset_result,
                signal_flag_boundaries=signals, signal_schedule_join=joined,
                input_sha256={str(path): sha(path)},
                whole_period_composition_complete=False, new_physical_period_executed=False,
                scope='All normalized physical clock ages and canonical Address geometry. '
                      'Mail identities assume coherent old procedure/static records and zero or one head; '
                      'physical flags, Signals and Wf are arbitrary. Quiet barrier and clean reset '
                      'premises are explicit. The schedule join is conditional on the checked trajectory; '
                      'this is not an entry-to-exit or noise theorem.')


def sha_rom():
    return hashlib.sha256(p.base_rom().tobytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    start = time.perf_counter()
    result = checks()
    sources = {Path(__file__).resolve()}
    for module in tuple(sys.modules.values()):
        filename = getattr(module, '__file__', None)
        if filename and '/fixed_rule/' in str(Path(filename).resolve()):
            sources.add(Path(filename).resolve())
    result.update(descriptor_sha256=f.self_description().digest(), ROM_sha256=sha_rom(),
                  source_sha256={str(path.relative_to(Path.cwd())): sha(path) for path in sorted(sources)},
                  seconds=time.perf_counter()-start,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    with args.output.open('x') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(passed=True, seconds=result['seconds'],
                          host_max_rss_kib=result['host_max_rss_kib'])), flush=True)


if __name__ == '__main__':
    main()
