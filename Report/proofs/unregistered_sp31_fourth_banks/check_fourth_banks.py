#!/usr/bin/env python3
"""Freeze once with --issue; default replays without changing any asset."""
from pathlib import Path
import argparse,hashlib,json,sys,time

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'figs/robustness/unregistered_sp31_fourth_banks'
CERT=OUT/'fourth_bank_certificate.json'
PROBE=OUT/'bank_cofactor_receipt.json'
sys.path.insert(0,str(HERE))
import probe_fourth_banks as probe

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(r):return json.loads(json.dumps(r))

def contracts(r):
    assert (r['Q'],r['U'],r['radius'])==(1024,475136,37)
    assert r['candidate_sha256']=='dc456bac4904647b66ee1f922788cdeb4428df91e21858fd8de0b3ccb4a69421'
    assert r['netlist_sha256']=='73378f4aa5669c54a21dfcd1f2a277e14aaf4d98e0508d4e6870de7491c36d44'
    assert r['probe_sha256']==sha(HERE/'probe_fourth_banks.py')
    for path,h in r['source_dependencies_sha256'].items():assert sha(ROOT/path)==h,path
    assert (r['q134_native_cofactors'],r['q141_native_cofactors'],r['side_quorums']['cases'])==(22598,24576,30874)
    assert len(r['selected_left_full_cofactors'])==324 and len(r['right_full_cofactors'])==36
    assert r['selected_full_checks_measured_supplements']
    assert (r['protected_left_work_frame_max'],r['protected_right_work_frame_min'])==(141,155)
    assert r['work_range']==[58,966]
    assert 141*1024+965+2+37==145388<142*1024+1
    assert 155*1024+58-2-37==155*1024+19
    assert len(r['Hold_store_records'])==24
    for row in r['Hold_store_records']:
        assert row['materialized_age']==row['issue_age']+2
        assert row['materialized_age']<278401 if row['phase']<512 else row['issue_age']>278401+6144
    zeros=r['new_foreign_GF_F1_F2_zero_primary_records']
    assert len(zeros)==36
    assert [(x['h'],x['physical_phase']) for x in zeros]==[(h,k) for h in range(153,156) for k in (*range(571,581),600,601)]
    for row in zeros:
        y=row['primary'];assert y==(row['h']-1)*1024+row['physical_phase'] and row['value']==0
        assert 152*1024-512<=y-2-37 and y+2+37<155*1024
        assert not 149*1024-512<=y<152*1024
    assert not r['actual_fourth_boundary_bank_lift_supplied_by_written_proof'] # Historical cofactor-only receipt.
    for key in ('full_fourth_Info_SF_or_fifth_source_or_pulse_or_general_higher_iid_or_minimum_proved',
                'additional_rule_change','active_G17_modified','Gray_or_G17_refutation','global_reliability_established'):
        assert not r[key],key

def assets():
    paths={HERE/'probe_fourth_banks.py',HERE/'check_fourth_banks.py',HERE/'SP31_FOURTH_PROTECTED_BANKS.md',PROBE,
        ROOT/'figs/robustness/unregistered_sp31_fourth_banks_run01.log',
        ROOT/'Report/proofs/SP31_OWN_RULE.md',ROOT/'Report/proofs/SP31_FIRST_PULSE.md',
        ROOT/'Report/proofs/SP31_ONE_EXCEPTION_BANK.md',ROOT/'Report/proofs/SP31_THIRD_PULSE.md',
        ROOT/'Report/proofs/SP31_THIRD_BOUNDARY_BANKS.md',ROOT/'Report/proofs/SP31_FOURTH_SOURCE_ENCLOSURE.md',
        ROOT/'Report/proofs/unregistered_sp31_fourth_ternary/SP31_FOURTH_NATIVE_ENCLOSURE.md',
        ROOT/'figs/robustness/SP31_program.npz',ROOT/'figs/robustness/SP31_program_listing.json',
        ROOT/'figs/robustness/SP31_symbolic_schedule.json',ROOT/'figs/robustness/SP31_interface_certificate.json',
        ROOT/'figs/robustness/SP31_third_pulse_certificate.json',
        ROOT/'figs/robustness/SP31_third_boundary_banks_certificate.json',
        ROOT/'figs/robustness/SP31_fourth_source_enclosure_certificate.json',
        ROOT/'figs/robustness/unregistered_sp31_fourth_ternary/ternary_enclosure_certificate.json'}
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path:
            p=Path(path).resolve()
            if p.suffix=='.py' and p.is_relative_to(ROOT):paths.add(p)
    return {str(p.relative_to(ROOT)):sha(p) for p in sorted(paths)}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--issue',action='store_true');args=parser.parse_args()
    start=time.monotonic();original=json.loads(PROBE.read_text());contracts(original)
    if args.issue:
        assert not CERT.exists(),'Already frozen; default is read-only.'
        p=probe.proposed.parameters();c=probe.proposed.load_artifact()
        assert c.digest()==original['candidate_sha256'] and c.comp.digest==original['netlist_sha256']
    else:
        frozen=json.loads(CERT.read_text())
        for path,h in frozen['assets_sha256'].items():assert sha(ROOT/path)==h,path
        result=canonical(probe.compute());contracts(result)
        expected=dict(original);expected.pop('seconds')
        assert result==expected,'Replayed cofactors differ from the frozen historical receipt.'
    cert=dict(passed=True,Q=1024,U=475136,radius=37,
        candidate_sha256=original['candidate_sha256'],netlist_sha256=original['netlist_sha256'],
        cofactor_receipt_sha256=sha(PROBE),proof_sha256=sha(HERE/'SP31_FOURTH_PROTECTED_BANKS.md'),
        checker_sha256=sha(__file__),q134_native_cofactors=22598,q141_native_cofactors=24576,side_quorum_cases=30874,
        selected_full_cofactors=360,selected_full_cofactors_measured_supplements=True,
        protected_work_phase_interval=[58,966],protected_true_frame_sides=[141,155],
        new_foreign_zero_primary_count=36,new_foreign_zero_physical_Info_copies=180,
        actual_protected_fourth_native_Info_banks_proved_by_written_physical_induction=True,
        actual_new_foreign_GF_F1_F2_zero_banks_proved_by_written_timing_and_commit_induction=True,
        shared_free_GF_words_quantified_without_reachability_or_independence_assumption=True,
        full_fourth_Info_SF_or_upper_successor_proved=False,fifth_commands_or_general_higher_iid_or_minimum_proved=False,
        additional_rule_change=False,active_G17_modified=False,Gray_or_G17_refutation=False,
        global_reliability_established=False,assets_sha256=assets())
    if args.issue:CERT.write_text(json.dumps(cert,indent=2)+'\n')
    else:assert cert==frozen,'Read-only certificate differs.'
    print(json.dumps(dict(passed=True,readonly=not args.issue,certificate_sha256=sha(CERT),
        assets_verified=len(cert['assets_sha256']),q134_native_cofactors=22598,q141_native_cofactors=24576,
        side_quorum_cases=30874,selected_full_cofactors=360,new_foreign_zero_primary_count=36,
        actual_restricted_fourth_native_banks_proved=True,full_fourth_or_fifth_or_global_reliability_proved=False,
        seconds=time.monotonic()-start)),flush=True)
if __name__=='__main__':main()
