#!/usr/bin/env python3
"""Read-only actual GMW6 emission, finite replays and universal budget check."""
from pathlib import Path
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
import gray_token_word_v6 as k
import build_gray_token_word_v6 as builder
import check_gray_token_word_v6 as check
import check_gray_token_word_v6_bound as bound


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def failures(directory):
    names=('GMW6_first_token_overflow.json','GMW6_slot_alias_failure.json',
        'GMW6_slot_shift_failure.json','GMW6_initial_bound_import_failure.json',
        'GMW6_bound_singleton_failure.json','GMW6_wipe_fixture_failure.json',
        'GMW6_bound_predicate_hardening.json','GMW6_initial_validator_minimum_failure.json')
    for name in names:
        row=json.loads((directory/name).read_text())
        for file,value in row.get('source_snapshots_sha256',{}).items():assert digest(directory/file)==value
        if 'snapshot' in row:assert digest(directory/row['snapshot'])==row['snapshot_sha256']
        if 'retained_checker' in row:assert digest(directory/row['retained_checker'])==row['retained_checker_sha256']
        assert not row['Gray_or_iid_failure_proved']
    first=json.loads((directory/names[0]).read_text())
    assert (first['token_count'],first['programme_bits'],first['instructions'],first['used_dictionary_words'])==(920,8280,905,417)
    assert first['architecture_specific_failure'] and not first['errors']
    for suffix in ('beta.bin','dictionary.json','listing.json'):
        assert digest(directory/('GMW6_first_token_overflow_'+suffix))==first[suffix+'_sha256']
    hardened=json.loads((directory/'GMW6_bound_predicate_hardening.json').read_text())
    assert hardened['abstract_checker_hardening']
    assert not hardened['concrete_kernel_or_beta_changed'] and not hardened['concrete_counterexample_obtained']
    return {name:digest(directory/name) for name in names}


def validate(directory=None):
    directory=directory or ROOT/'figs/gray_counterexamples';source=Path(__file__).parent
    receipt=json.loads((directory/'GMW6_token_word_certificate.json').read_text())
    for key,path in (('kernel_sha256',k.__file__),('builder_sha256',builder.__file__),
        ('checker_sha256',check.__file__),('bound_checker_sha256',bound.__file__),
        ('proof_sha256',source/'GMW6_TOKEN_WORD_EVALUATOR.md')):
        assert receipt[key]==digest(path),(key,path)
    for name,value in receipt['dependency_sources_sha256'].items():assert digest(source/name)==value
    assert (receipt['Q'],receipt['U'],receipt['lambda_original'],receipt['c_original'])==(8192,1048576,24,104)
    assert (receipt['used_beta_bits'],receipt['beta_capacity_bits'],receipt['used_dictionary_words'],
        receipt['dictionary_capacity_bits'],receipt['total_immutable_capacity_bits'],receipt['alphabet_bits'],
        receipt['frame_words'])==(8091,8192,406,51200,59392,18537,191)
    for key in ('physical_word_PC_dictionary_BITCODE_and_scratch_change_explicit',
        'no_whole_rule_or_native_or_HeadStep_syscall','prepared_no_error_upper_raw_semantics_proved_by_contracts',
        'finite_comparisons_measured_only'):
        assert receipt[key]
    for key in ('complete_period_proved','Gray_faithful_Q_bit_evaluator_proved',
        'continuing_E0_or_higher_or_intact_counterexample_proved',
        'iid_reliability_or_shorter_U_proved','active_rule_modified'):
        assert not receipt[key]
    rom,listing,labels,errors=builder.programme().assemble();assert not errors
    expected_static=check.static_certificates(rom,listing,labels)
    assert expected_static==receipt['static']
    for key,name in (('beta_sha256','GMW6_token_beta.bin'),('dictionary_sha256','GMW6_dictionary.json'),
        ('listing_sha256','GMW6_token_listing.json'),('replay_sha256','GMW6_full_replays.json'),
        ('bound_sha256','GMW6_execution_bound.json')):
        assert receipt[key]==digest(directory/name),(key,name)
    assert np.unpackbits(np.fromfile(directory/'GMW6_token_beta.bin',np.uint8),bitorder='little').tolist()==list(rom.bits)
    assert [int(v,16) for v in json.loads((directory/'GMW6_dictionary.json').read_text())]==list(rom.dictionary)
    assert json.loads((directory/'GMW6_token_listing.json').read_text())==dict(instructions=listing,labels=labels,errors=errors)
    rows=json.loads((directory/'GMW6_full_replays.json').read_text())
    generated=check.fixtures(rom,listing,labels)
    assert len(rows)==len(generated)==receipt['finite_comparisons']==91
    for row,(name,generated_cells) in zip(rows,generated):
        assert row['name']==name
        cells={j:k.cell_from_words([int(v,16) for v in row['inputs'][j+5]]) for j in range(-5,6)}
        assert cells==generated_cells
        assert [[hex(v) for v in k.cell_words(cells[j])] for j in range(-5,6)]==row['inputs']
        expected=k.cell_words(k.local_transition(cells,rom))
        out,ticks,last,_=k.execute(rom,k.input_tape(cells),limit=65535)
        assert last.mode==k.HALT and ticks==row['ticks']
        assert [out.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_WORDS)]==expected==[int(v,16) for v in row['outputs']]
    assert (min(r['ticks'] for r in rows),max(r['ticks'] for r in rows))==(1103,46188)==(receipt['min_ticks'],receipt['max_ticks'])
    retained=json.loads((directory/'GMW6_execution_bound.json').read_text());actual=bound.validate()
    for value in (retained,actual):value.pop('elapsed_seconds')
    assert retained==actual and actual['total_active_execution_bound']==receipt['universal_prepared_deadline_bound']==47913
    assert actual['fixed_overhead_bound']==269 and actual['available_active_updates']==65535
    assert [r['maximum_ticks'] for r in actual['copies']]==[9759,9638,9517,9396,9334]
    assert sum(r['abstract_states'] for r in actual['copies'])==147800
    assert actual['no_error_preloaded_execution_only'] and not actual['full_Gray_period_or_iid_theorem']
    return dict(used_beta_bits=8091,total_immutable_capacity_bits=59392,
        prepared_raw_beta_contracts=True,universal_prepared_execution_bound=47913,
        finite_measured_comparisons=91,max_observed_ticks=46188,
        failures_sha256=failures(directory),receipt_sha256=digest(directory/'GMW6_token_word_certificate.json'),
        full_period_Gray_intact_E0_or_iid_theorem=False)


if __name__=='__main__':
    started=time.monotonic();result=validate();result['elapsed_seconds']=time.monotonic()-started
    print(json.dumps(result))
