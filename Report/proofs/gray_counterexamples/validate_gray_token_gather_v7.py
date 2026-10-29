#!/usr/bin/env python3
"""Read-only GMW7 emission, prepared execution and physical gather validator."""
from pathlib import Path
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
import gray_token_gather_v7 as k
import build_gray_token_gather_v7 as builder
import check_gray_token_gather_v7 as prepared
import check_gray_token_gather_v7_bound as bound
import check_gray_token_gather_v7_period as period


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate(directory=None):
    directory=directory or ROOT/'figs/gray_counterexamples';source=Path(__file__).parent
    first=json.loads((directory/'GMW7_prepared_execution_certificate.json').read_text())
    final=json.loads((directory/'GMW7_single_gather_period_certificate.json').read_text())
    for row in (first,final):
        assert (row['Q'],row['U'],row['lambda_original'],row['c_original'])==(8192,1048576,24,104)
        assert row['kernel_sha256']==digest(k.__file__) and row['builder_sha256']==digest(builder.__file__)
        assert row['total_immutable_capacity_bits']==59392 and not row['active_rule_modified']
    assert first['checker_sha256']==digest(prepared.__file__)
    assert first['bound_checker_sha256']==digest(bound.__file__)
    for name,value in first['ancestors_sha256'].items():assert digest(source/name)==value
    assert (first['tokens'],first['beta_bits'],first['used_dictionary_words'],first['instructions'])==(878,7902,425,863)
    assert first['prepared_comparisons_measured_only'] and not first['faithful_Gray_or_iid_or_shorter_U_proved']
    # The first receipt records emission before the separate period proof.
    assert not first['own_beta_universal_semantics_or_full_period_proved']
    for key,name in (('beta_sha256','GMW7_token_beta.bin'),('dictionary_sha256','GMW7_dictionary.json'),
        ('listing_sha256','GMW7_token_listing.json'),('replay_sha256','GMW7_full_replays.json'),
        ('bound_sha256','GMW7_execution_bound.json')):
        assert first[key]==digest(directory/name)
    rom,listing,labels,errors=builder.programme().assemble();assert not errors
    assert np.unpackbits(np.fromfile(directory/'GMW7_token_beta.bin',np.uint8),bitorder='little').tolist()==list(rom.bits)
    assert [int(v,16) for v in json.loads((directory/'GMW7_dictionary.json').read_text())]==list(rom.dictionary)
    assert json.loads((directory/'GMW7_token_listing.json').read_text())==dict(instructions=listing,labels=labels,errors=[])
    for row in listing:
        args=tuple(v&((1<<width)-1) for v,width in zip(row['operands'],k.ARGS[row['opcode']]))
        assert k.decode(k.beta_word(rom,row['address']))==(row['opcode'],args)
    replays=json.loads((directory/'GMW7_full_replays.json').read_text())
    cases=prepared.cases(rom,listing,labels)
    assert len(replays)==len(cases)==97==first['prepared_comparisons']
    for row,(name,cells) in zip(replays,cases):
        assert row['name']==name
        assert [[hex(v) for v in k.cell_words(cells[j])] for j in range(-5,6)]==row['inputs']
        out,ticks,last,_=k.execute(rom,k.input_tape(cells),limit=65535)
        expected=k.cell_words(k.local_transition(cells,rom))
        assert last.mode==k.HALT and ticks==row['ticks']
        assert [out.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_WORDS)]==expected
        assert [hex(v) for v in expected]==row['expected']
    assert max(r['ticks'] for r in replays)==47085==first['max_ticks']
    assert min(r['ticks'] for r in replays)==first['min_ticks']
    retained=json.loads((directory/'GMW7_execution_bound.json').read_text());actual=bound.validate()
    for row in (retained,actual):row.pop('elapsed_seconds')
    assert actual==retained and actual['total_active_execution_bound']==49068==first['execution_bound']
    assert [r['maximum_ticks'] for r in actual['copies']]==[9990,9869,9748,9627,9565]
    assert sum(r['abstract_states'] for r in actual['copies'])==1522930
    assert final['checker_sha256']==digest(period.__file__)
    assert final['proof_sha256']==digest(source/'GMW7_SINGLE_GATHER_PERIOD.md')
    assert final['prepared_receipt_sha256']==digest(directory/'GMW7_prepared_execution_certificate.json')
    assert final['bound_receipt_sha256']==digest(directory/'GMW7_execution_bound.json')
    assert final['ancestor_E0_proof_sha256']==digest(source/'GMW6_E0_COMPONENT_COUPLING.md')
    assert final['ancestor_E0_checker_sha256']==digest(period.ancestor.__file__)
    for key,name in (('routes','GMW7_gather_routes.json'),('replays','GMW7_gather_full_cell_replays.json')):
        assert final['asset_sha256'][key]==digest(directory/name)
    assert period.route_arithmetic()==json.loads((directory/'GMW7_gather_routes.json').read_text())
    checks,rows=period.actual_gather_checks(rom)
    assert checks==final['finite_gather_checks']
    assert rows==json.loads((directory/'GMW7_gather_full_cell_replays.json').read_text())
    assert final['all_lane_tick_route_identities']==450571 and final['represented_capture_routes']==2101
    assert final['actual_holder_source_radius']==5 and final['final_capture_age']==37*k.Q
    assert final['active_updates']==65535 and final['universal_execution_bound']==49068
    for key in ('own_beta_semantics_proved_by_register_contracts',
        'broad_Info_encoded_period_proved_for_changed_rule',
        'pure_E0_majority_decoder_period_proved_for_changed_rule',
        'single_gather_fixed_zero_Workspace_word_IO_extra_dictionary_changes_explicit'):
        assert final[key]
    assert not final['literal_Gray_three_gathers_early_flags_or_flag_repair_proved']
    assert not final['real1_higher_or_iid_or_shorter_U_proved']
    return dict(receipt_sha256=digest(directory/'GMW7_single_gather_period_certificate.json'),
        beta_bits=7902,total_immutable_bits=59392,prepared_comparisons=97,
        universal_execution_bound=49068,actual_gather_comparisons=checks['whole_cell_support_comparisons'],
        changed_broad_Info_noiseless_and_pure_E0_encoded_period=True,
        faithful_Gray_real1_higher_or_iid_theorem=False)


if __name__=='__main__':
    started=time.monotonic();result=validate();result['elapsed_seconds']=time.monotonic()-started
    print(json.dumps(result))
