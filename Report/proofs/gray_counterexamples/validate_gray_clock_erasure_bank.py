#!/usr/bin/env python3
"""Read-only GT0 Mailbox-barrier/native-bank replay with explicit prefix scope."""
from pathlib import Path
import hashlib,json,time
import check_gray_clock_erasure_bank as check
ROOT=Path(__file__).resolve().parents[3]


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate():
    source=Path(__file__).parent;directory=ROOT/'figs/gray_counterexamples'
    path=directory/'GT0_clock_erasure_bank_certificate.json';r=json.loads(path.read_text())
    assert (r['Q'],r['U'],r['lambda_original'],r['c_original'])==(8192,1048576,24,104)
    assert r['checker_sha256']==digest(check.__file__)
    assert r['proof_sha256']==digest(source/'GT0_CLOCK_ERASURE_BANK.md')
    for name,value in r['source_dependencies_sha256'].items():assert digest(source/name)==value
    for name,value in r['receipt_dependencies_sha256'].items():assert digest(directory/name)==value
    assert r['primary_Gray_text_sha256']==digest(ROOT/'papers_txt/gray_readers_guide.txt')
    assert r['results']==json.loads(json.dumps(check.calculate()))
    assert r['conditional_Gt0_prefix_native_and_actual_blocked_banks_proved']
    assert r['no_preloaded_bank_or_independent_upper_error']
    assert r['initial_native_layout_and_intact_full_completion_premises_explicit']
    for name in ('full_Gray_beta_layout_early_evaluation_or_late_repair_proved',
        'Gray_or_Gacs_refuted_or_iid_memory_failure','active_rule_or_existing_GT0_modified',
        'new_rule_schedule_or_shorter_U_emitted'):assert not r[name]
    return dict(receipt_sha256=digest(path),conditional_actual_GT0_Mailbox_barrier_and_native_banks_validated=True,
        genuine_complete_Gray_rule_or_counterexample_proved=False,early_flag_execution_or_recovery_proved=False)


if __name__=='__main__':
    started=time.monotonic();r=validate();r['elapsed_seconds']=time.monotonic()-started
    print(json.dumps(r))
