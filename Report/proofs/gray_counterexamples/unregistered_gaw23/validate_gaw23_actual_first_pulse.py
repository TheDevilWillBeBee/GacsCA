"""Read-only full lineage and physical-native replay of GAW23.

No main report/checkpoint mutation and no new CA transition. Native state
only at U; auxiliary source bits at commit are explicitly not an Info
theorem. Rebuilt event bytes, source hashes and every payload are checked.
"""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys,tempfile,time
import check_gaw23_first_banks as banks
import check_gaw23_actual_native_factor as factor
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw23'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def assets(m):
    for p,h in m['assets_sha256'].items():
        assert sha(ROOT/p)==h,(p,'immutable isolated asset or inherited dependency differs')
def run(command):
    p=subprocess.run(list(map(str,command)),cwd=ROOT,capture_output=True,text=True)
    assert p.returncode==0,(command,p.returncode,p.stdout,p.stderr)
    assert p.stderr=='',p.stderr
    return p.stdout

def main():
    started=time.monotonic();mp=D/'GAW23_standalone_assets.json';m=load(mp);assets(m)
    inherited=load(ROOT/m['inherited_manifest']);assets(inherited)
    assert len(inherited['assets_sha256'])==m['inherited_assets']==563
    assert all(m['assets_sha256'][p]==h for p,h in inherited['assets_sha256'].items())
    sys.path.insert(0,str(S.parent/'unregistered_gaw22'))
    spec=importlib.util.spec_from_file_location('gaw23_accepted_gaw22_replay',
        S.parent/'unregistered_gaw22/validate_gaw22_actual_recurrence.py')
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    prior=old.main();assert prior['passed'] and prior['assets_verified']==563
    assert prior['exact_unchanged_GAW2R_ROM_dictionary_listing_actual_local_R']
    print(json.dumps(dict(inherited_GAW22_replay_passed=True,assets=563)),flush=True)
    k=banks.k
    assert (k.Q,k.U,k.WORD,k.PRIMARY_START,k.FRAME_WORDS)==(8192,1048576,100,3848,496)
    assert k.SLOTS==(0,-2,-1,1,2) and k.STAGE_STARTS==(0,32*k.Q,64*k.Q,96*k.Q,102*k.Q)
    # Exact intact origins of every alternatively addressed WF source.
    assert k.FIELD['h1_0']+4==4093-k.PRIMARY_START==245
    assert k.FIELD['h1_2']==4099-k.PRIMARY_START==251
    for g in (-101,-3,-1,0,1,17,8191,8192,9000):
        assert all(banks.base.I(g*k.Q+r)==0 for r in (3,4093,4099,k.Q-3))
    previous_argv=sys.argv
    try:
        sys.argv=[str(S/'check_gaw23_first_banks.py')]
        actual_banks=banks.main()
        assert actual_banks==load(D/'GAW23_actual_first_native_banks.json')
        assert actual_banks['exact_GF_only_fault']['points']==139264
        assert actual_banks['no_future_noise_tapes_heads_or_commands_prescribed']
        # Keep the earlier receipt's historical unproved pulse scope.
        assert actual_banks['native_Info_factor_pulse_and_U_Address_result_not_yet_certified']
        with tempfile.TemporaryDirectory(prefix='gaw23_readonly_') as tmp:
            tmp=Path(tmp);exe=tmp/'interval';audit=tmp/'audit'
            flags=['gcc','-O3','-std=c11','-Wall','-Wextra','-Werror']
            # Match the retained build's source spelling, including C's
            # assert filename strings, without changing any input source.
            run(flags+[S.relative_to(ROOT)/'gaw23_interval_native.c','-o',exe])
            run(flags+[S.relative_to(ROOT)/'gaw23_general_native_audit.c','-o',audit])
            assert sha(exe)==sha(D/'gaw23_interval_native')
            assert sha(audit)==sha(D/'gaw23_general_native_audit')
            for mode in ('prefix','pulse'):
                events=tmp/(mode+'.bin');command=[exe,mode,events]
                if mode=='pulse':command.append(D/'GAW23_derived_actual_first_F1_sources.txt')
                result=json.loads(run(command))
                assert result==load(D/f'GAW23_{"first_pulse" if mode=="pulse" else "prefix"}_discovery02.json')
                assert sha(events)==sha(D/f'GAW23_{"first_pulse" if mode=="pulse" else "prefix"}_events02.bin')
            scalar=json.loads(run([audit,tmp/'pulse.bin']))
            assert scalar==load(D/'GAW23_general_native_audit_issue01.log')
            assert scalar['passed'] and scalar['exact_computed_updates']==28676
            assert scalar['independent_word_quorum_event_intervals']==20406053
        sys.argv=[str(S/'check_gaw23_actual_native_factor.py')]
        pulse=factor.main()
    finally:sys.argv=previous_argv
    assert pulse==load(D/'GAW23_actual_first_native_pulse_certificate.json')
    assert pulse['inherited_actual_bank_receipt_sha256']==sha(D/'GAW23_actual_first_native_banks.json')
    assert pulse['native_event_file_sha256']==sha(D/'GAW23_first_pulse_events02.bin')
    assert pulse['actual_local_R_cofactors']['actual_frozen_local_R_native_and_computed_primary_checks']==3080
    assert pulse['actual_mail_and_courier_contracts']['maximum_first_arrival_after75Q']==4339
    assert len(pulse['actual_mail_and_courier_contracts']['exact_actual_destination_sources'])==21
    assert pulse['first_native_U_GF_foreign_interval']==[61440,163840]
    assert pulse['first_native_U_Flag1_intervals']==[[57344,61440],[159744,163840]]
    assert pulse['first_native_U_foreign_width']==102400==25*k.Q//2
    assert pulse['actual_source_Info_claim_only_before_U_commit']
    assert pulse['sources_at_U_from_auxiliary_tracker_not_claimed_physical']
    for flag in ('full_late_pass_all496word_banks_U_encoding_later_orbit_or_operational_repair_proved',
        'printed_Gray_Address_Proposition5_failure_claim',
        'faithful_Gray_Gacs_iid_memory_higher_error_or_shorter_U_claim'):
        assert pulse[flag] is False
    assets(m);assets(inherited)
    result=dict(passed=True,assets_verified=len(m['assets_sha256']),inherited_assets_verified=563,
        Q=k.Q,U=k.U,error_lambda=24,error_separation=104,
        exact_frozen_GAW2R_ROM_dictionary_local_R_and_rebuilt_analysis_binaries=True,
        actual_intact_H_chronological_row1_GF_only139264_complete_shared_real2_payloads=True,
        actual_three_gathers_native_banks39_early_emission_runs_and21_source_couriers=True,
        exact_native_event_intervals=20406053,scalar_native_WF_cofactors=40871730,
        source_holder_wipe_cofactors=3010980,actual_frozen_full_local_R_native_cofactors=3080,
        infinite_line_binary_GF_common_Age_Flag2zero_Info_source_factor=True,
        actual_native_U_wrong_GF_interval=[61440,163840],native_repair_not_complete_atU=True,
        full_U_Out_encoding_decoded_damage_later_orbit_or_Gray_P5_failure_proved=False,
        faithful_Gray_Gacs_iid_higher_error_memory_or_shorter_U_claim=False,
        old_GAW_main_reports_G17_rule_ROM_or_constants_changed=False,
        manifest_sha256=sha(mp),proof_sha256=sha(S/'GAW23_ACTUAL_FIRST_ADDRESS_PULSE.md'),
        bank_receipt_sha256=sha(D/'GAW23_actual_first_native_banks.json'),
        pulse_receipt_sha256=sha(D/'GAW23_actual_first_native_pulse_certificate.json'),
        elapsed_seconds=time.monotonic()-started)
    print(json.dumps(result),flush=True);return result

if __name__=='__main__':main()
