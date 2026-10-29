#!/usr/bin/env python3
"""Read-only GE0 physical-prefix reproduction; no full own-beta claim."""
from pathlib import Path
import hashlib,json,time
import check_gray_early_native_flags as check
import gray_early_native_flags as e
import gray_raw_gather as g
import gray_moving_word_kernel as h
ROOT=Path(__file__).resolve().parents[3]


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate():
    directory=ROOT/'figs/gray_counterexamples';source=Path(__file__).parent
    path=directory/'GE0_early_native_flags_certificate.json'
    r=json.loads(path.read_text())
    assert (r['Q'],r['U'],r['lambda_original'],r['c_original'])==(8192,1048576,24,104)
    assert r['checker_sha256']==digest(check.__file__)
    assert r['proof_sha256']==digest(source/'GE0_EARLY_NATIVE_FLAGS.md')
    for name,value in r['source_dependencies_sha256'].items():assert digest(source/name)==value
    for name,value in r['receipt_dependencies_sha256'].items():assert digest(directory/name)==value
    for name,value in r['emitted_assets_sha256'].items():assert digest(directory/name)==value
    for name,value in r['retained_initial_endpoint_sha256'].items():assert digest(directory/name)==value
    assert r['primary_Gray_text_sha256']==digest(ROOT/'papers_txt/gray_readers_guide.txt')
    beta,listing,labels=e.native_programme()
    packed=bytes(sum(beta[i+j]<<j for j in range(8)) for i in range(0,e.Q,8))
    assert (directory/'GE0_native_prefix_beta.bin').read_bytes()==packed
    assert json.loads((directory/'GE0_native_prefix_listing.json').read_text())==dict(
        entry=e.ENTRY,code_bits=2346,labels=labels,programme=listing)
    assert r['results']==json.loads(json.dumps(check.calculate()))
    retained_history_checks=0
    for name,bank,flag1,derived in check.retained_inputs():
        if not derived:continue
        tape=e.tape_from_native(bank);receiver=int(name.split('_')[0])
        for age in (e.BIRTH,e.SEED-2,e.SEED):
            for start,width in e.NATIVE_COLUMNS.values():
                for primary in range(start,start+width):
                    actual=e.local_transition(check.fixture(primary,age,-1,h.ZERO,tape,
                        lower_f1=flag1,receiver=receiver),beta)
                    expected=tuple((tape.get(primary+s,0)>>bit)&1 for s in e.SLOTS for bit in range(11))
                    for field in ('history2','history3'):
                        assert actual.data[list(dict(g.FIELDS)).index(field)]==expected
                        retained_history_checks+=1
    assert retained_history_checks==444
    assert r['conditional_actual_GT0_history_native_execution_and_flag_delivery_proved']
    assert r['total_component_has_explicit_late_ports']
    assert r['full_intact_completion_and_final_programme_premises_remain']
    assert r['early_reset_birth_run_couriers_added_explicit_schedule_change']
    for name in ('native_programme_is_full_own_beta','actual_island_first_native_Flag2_output_positive',
                 'prepared_Age15_positive_Flag2_reachability_proved','arbitrary_E0_GF_birth_transparency_proved',
                 'registered_components_or_active_rule_changed','full_Gray_or_Gacs_refutation_or_iid_reliability',
                 'shorter_U_proved'):assert not r[name]
    return dict(receipt_sha256=digest(path),actual_three_history_early_native_execution_and_flag_delivery=True,
        actual_retained_History2_and_History3_hold_checks=retained_history_checks,
        own_beta_or_full_Gray_rule_or_iid_theorem=False)


if __name__=='__main__':
    started=time.monotonic();result=validate();result['elapsed_seconds']=time.monotonic()-started
    print(json.dumps(result))
