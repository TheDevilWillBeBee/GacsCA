"""Read-only replay of GAW4, with frozen rule/ROM/shadow/error identity."""
from pathlib import Path
from dataclasses import asdict
import sys,json,hashlib,time,importlib.util
ROOT=Path(__file__).resolve().parents[4]
S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gaw4'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    start=time.monotonic();path=D/'GAW4_standalone_assets.json'
    manifest=json.loads(path.read_text());assets=manifest['assets_sha256']
    for p,h in assets.items():assert sha(ROOT/p)==h,('source/receipt mismatch',p)
    c=json.loads((D/'GAW4_intact_real1_mail_certificate.json').read_text())
    assert c['proof_sha256']==sha(S/'GAW4_INTACT_REAL1_MAIL.md')
    assert (c['Q'],c['U'],c['error_lambda'],c['error_separation'])==(8192,1048576,24,104)
    assert c['intact_initializer_every_level_proved'] and c['actual_Programme_choices_proved']
    assert c['history_is_one_real1_and_no_E0'] and c['actual_first_boundary_E_Cprime_proved']
    assert c['first_decoded_boundary_sacrifices_one_upper_holder']
    assert c['temporary_raw_SF_three_colony_footprint_proved'] and c['literal_Prop4_transplant_to_GAW2R_refuted']
    assert c['complete_second_boundary_shadow_recovery_proved']
    assert c['proof_lift_from_actual_gathers_and_period_contracts']
    for name in ('independent_preloaded_history_assumed','complete_physical_period_direct_simulation_claimed',
                 'Gray_construction_refuted','iid_memory_failure_proved','failure_caused_by102Q_proved',
                 'shorter_U_proved','new_rule_created','active_rule_modified','registered_main_modified'):
        assert not c[name],name
    previous=ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw2/validate_gaw2_period_v2.py'
    sys.path.insert(0,str(previous.parent))
    spec=importlib.util.spec_from_file_location('frozen_gaw2_for_gaw4',previous)
    replay=importlib.util.module_from_spec(spec);spec.loader.exec_module(replay);replay.main()
    import check_gaw4_real1_mail as checker
    rom=json.loads((ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_rom.json').read_text())
    rom['dictionary']=[int(v,0) if isinstance(v,str) else v for v in rom['dictionary']]
    assert json.loads(json.dumps(asdict(checker.own.ROM)))==rom
    receipt=checker.main(write=False);w=receipt['witness']
    assert [receipt[n]['updates'] for n in ('first_actual_execution','second_actual_execution')]==[66185,65062]
    assert w['error_support']==[(x,1048575) for x in range(4052,4057)]
    assert w['error_classification']['level1'] and w['error_classification']['level0']==0
    assert w['simultaneous_show_tick']==1056769 and w['simultaneous_difference_colonies']==[-1,0,1]
    for p,h in assets.items():assert sha(ROOT/p)==h,('read-only replay mutated asset',p)
    print(json.dumps(dict(passed=True,assets_verified=len(assets),frozen_GAW2R_replayed=True,
        actual_simulator_emitted_ROM_equal=True,intact_start=True,actual_real1_support=w['error_support'],
        temporary_SF_colonies=[-1,0,1],next_boundary_recovers=True,
        Gray_iid_or102Q_cause=False,registered_main_modified=False,
        checkpoint_sha256=sha(path),elapsed_seconds=time.monotonic()-start)))

if __name__=='__main__':main()
