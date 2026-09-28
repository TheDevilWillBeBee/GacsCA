"""Source/binary seal for the executed optimized fixed-rule physical periods."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import gather29_holder_rule as f
from gacsca.fixed_rule import gather29_holder_program as p
from gacsca.fixed_rule import gather29_holder_native as native
from gacsca.fixed_rule import gather29_holder_cpu_events as events
from gacsca.fixed_rule import gather29_holder_cpu_gather as gather
from gacsca.fixed_rule import gather29_holder_cpu_boundary as boundary
from gacsca.fixed_rule import gather29_holder_cpu_general as general
from gacsca.fixed_rule import gather29_holder_flags_cpu as flags
from experiments.fixed_rule.audit_gather29_holder_cpu_general_periods import audit
from experiments.fixed_rule.validate_gather29_holder_physical_events import check as event_check


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def seal(execution,audit_path):
    started=time.perf_counter()
    execution=Path(execution);audit_path=Path(audit_path)
    receipt=json.loads(execution.read_text())
    previous=json.loads(audit_path.read_text())
    assert receipt['passed'] and previous['passed'] and len(previous['cases'])==1
    assert previous['cases'][0]['execution_sha256']==sha(execution)
    assert receipt['snapshot_sha256']==sha(receipt['snapshot'])
    assert receipt['descriptor_sha256']==f.self_description().digest()
    assert receipt['rom_sha256']==hashlib.sha256(p.base_rom().tobytes()).hexdigest()
    for source,digest in receipt['source_sha256'].items():assert sha(source)==digest,source
    for source,digest in previous['source_sha256'].items():assert sha(source)==digest,source
    assert audit(execution)['passed']
    observed=event_check();assert observed['passed'] and observed['case_count']==8
    sources={Path(__file__),Path(audit.__code__.co_filename),
             Path(event_check.__code__.co_filename)}
    for module in (f,p,native,events,gather,boundary,general,flags):
        sources.add(Path(module.__file__))
    root=Path('gacsca/fixed_rule')
    sources.update(root/name for name in (
        'word_native_and.py','wordcode_and.py','gather29_holder_flags_cpu.c',
        'gather29_holder_cpu_events.cpp','gather29_holder_cpu_gather.cpp',
        'gather29_holder_cpu_boundary.cpp','gather29_holder_cpu_general.cpp',
        'gather29_holder_quotient.py','gather29_holder_period_relation.py',
        'small_holder_resident_independent.cu'))
    binaries={name:sha(module.library()._name) for name,module in
              (('native',native),('events',events),('gather',gather),
               ('boundary',boundary),('general',general),('flags',flags))}
    return dict(passed=True,execution=str(execution),execution_sha256=sha(execution),
                audit=str(audit_path),audit_sha256=sha(audit_path),
                snapshot_sha256=sha(receipt['snapshot']),
                colonies=receipt['colonies'],periods=receipt['periods'],
                physical_ticks=receipt['physical_ticks'],
                decoded_hashes=[row['decoded_sha256'] for row in receipt['period_results']],
                changed_projected_words=[row['changed_projected_words'] for row in receipt['period_results']],
                actual_packets_emitted=receipt['metrics']['packets_emitted'],
                actual_packets_delivered=receipt['metrics']['packets_delivered'],
                actual_packet_drops=receipt['metrics']['packets_dropped'],
                complete_raw_upper_words_per_period=receipt['colonies']*f.FIELDS,
                physical_sites_validated_per_period=receipt['colonies']*f.Q,
                selected_literal_physical_events=observed['case_count'],
                source_sha256={str(path):sha(path) for path in sorted(sources)},
                binary_sha256=binaries,
                seconds=time.perf_counter()-started,
                host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                scope='Two continuous accelerated physical lower work periods '
                      'on encoded upper cells; decoded F/G macrosteps.',
                limitation='Guarded event acceleration, not literal all-tick replay; '
                           'canonical coherent two-sided Signal domain. Does not '
                           'execute a complete depth-two upper work period or '
                           'establish noisy repair/amplification.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execution',type=Path,required=True)
    parser.add_argument('--audit',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=seal(args.execution,args.audit)
    with args.output.open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()
                      if k not in ('source_sha256','binary_sha256')},indent=2))


if __name__=='__main__':main()
