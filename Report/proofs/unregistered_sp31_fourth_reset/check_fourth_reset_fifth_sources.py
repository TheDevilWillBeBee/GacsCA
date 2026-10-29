#!/usr/bin/env python3
"""Issue a frozen proof receipt once; default performs a read-only replay."""
from pathlib import Path
import argparse,hashlib,json,sys,time

ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
OUT=ROOT/'figs/robustness/unregistered_sp31_fourth_reset'
CERT=OUT/'fourth_reset_fifth_source_certificate.json'
PROOF=HERE/'SP31_FOURTH_RESET_FIFTH_SOURCES.md'
sys.path.insert(0,str(HERE))
import probe_fourth_reset as reset
import probe_fifth_sources as sources
import probe_fifth_routes as routes

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(r):return json.loads(json.dumps(r))
def without_time(r):return {k:v for k,v in canonical(r).items() if k!='seconds'}

def contracts(a,b,c):
    for r in (a,b,c):assert (r['Q'],r['U'])==(1024,475136)
    for r in (a,b):
        assert r['candidate_sha256']=='dc456bac4904647b66ee1f922788cdeb4428df91e21858fd8de0b3ccb4a69421'
        assert r['netlist_sha256']=='73378f4aa5669c54a21dfcd1f2a277e14aaf4d98e0508d4e6870de7491c36d44'
        assert r['radius']==37
        for k in ('additional_rule_change','active_G17_modified','Gray_or_G17_refutation','global_reliability_established'):
            assert not r[k],k
    assert a['probe_sha256']==sha(HERE/'probe_fourth_reset.py')
    assert a['conditional_commit']['private_and_native_reset_bits']==807
    assert a['conditional_commit']['refined_self_and_computed_GF_independent']
    assert len(a['conditional_commit']['masked_keep_Hold_Info_identities'])==5
    assert a['actual_common_clock_commit']['all807_reset_bits_zero']
    assert a['actual_common_clock_commit']['native_successor_Age_zero_bits']==19
    assert a['actual_common_clock_commit']['raw_GF_flags_SF_and_instruction_all_free']
    assert len(a['alias_cases'])==40 and all(x['Info_zero'] for x in a['alias_cases'])
    assert not a['actual_fourth_boundary_and_quiet_fifth_prefix_lift_supplied_by_written_proof']
    assert not a['fifth_commands_or_full_upper_successor_or_eventual_general_higher_iid_or_minimum_proved']
    assert b['probe_sha256']==sha(HERE/'probe_fifth_sources.py')
    assert (b['TF'],b['fifth_source_time'])==(278401,2178945)
    assert b['left_flag_population']['right_quorum_word_population_cases']==34816
    assert b['left_flag_population']['no_right_quorum_forces_F1']
    assert len(b['native_checks']['selected_right_word_native_cofactors'])==170
    assert len(b['native_checks']['known_left_native_flags'])==41
    assert len(b['full_checks']['complete_foreign_full_cofactors'])==3
    assert len(b['full_checks']['right_full_cofactors'])==41
    assert b['native_checks']['selected_checks_measured_supplements']
    assert len(b['physical_routes']['complete_foreign_work_and_courier_margins'])==3
    e=b['command_enclosure']
    assert e['one_colonies']=={'509':list(range(152,155)),'1021':[*range(100,140),*range(155,158)],'3':[],'515':[]}
    assert e['free_colonies']=={'509':list(range(142,152)),'1021':list(range(140,151)),'3':list(range(133,152)),'515':list(range(142,155))}
    assert (e['free_votes'],e['one_votes'],e['enclosure_members'])==(53,46,1<<53)
    assert len(e['holder_alias_roles'])==2080 and e['other_votes_zero']
    assert not e['independence_or_reachability_proved']
    assert not b['actual_fifth_source_lift_supplied_by_written_proof']
    assert not b['actual_fifth_pulse_or_full_upper_successor_or_eventual_general_higher_iid_or_minimum_proved']
    assert c['probe_sha256']==sha(HERE/'probe_fifth_routes.py')
    assert c['route_counts']['left_true_native_sources_ge155_erased']==23055
    assert c['route_counts']['foreign_positive_joint_blocks_invalid']==14
    assert len(c['left_joint_refinement_reductions'])==6
    assert len(c['foreign_right_reader_refinement'])==7
    for k in ('actual_physical_lift_supplied_by_written_proof','rule_or_ROM_or_G17_change','global_reliability_established'):
        assert not c[k],k

def assets():
    pinned={}
    parents=[ROOT/'figs/robustness/unregistered_sp31_fourth_banks/fourth_bank_certificate.json',
        ROOT/'figs/robustness/unregistered_sp31_fourth_ternary/ternary_enclosure_certificate.json']
    for path in parents:
        original=json.loads(path.read_text())
        for rel,h in original['assets_sha256'].items():
            assert sha(ROOT/rel)==h,rel
            assert rel not in pinned or pinned[rel]==h,rel
            pinned[rel]=h
        pinned[str(path.relative_to(ROOT))]=sha(path)
    paths={PROOF,HERE/'check_fourth_reset_fifth_sources.py',HERE/'probe_fourth_reset.py',
        HERE/'probe_fifth_sources.py',HERE/'probe_fifth_routes.py',
        OUT/'reset_cofactor_receipt.json',OUT/'fifth_source_cofactor_receipt.json',OUT/'fifth_route_receipt.json',
        ROOT/'figs/robustness/unregistered_sp31_fourth_reset_probe01.log',
        OUT/'fifth_probe01.log',OUT/'routes_probe01.log'}
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path:
            p=Path(path).resolve()
            if p.suffix=='.py' and p.is_relative_to(ROOT):paths.add(p)
    for path in paths:
        rel=str(path.relative_to(ROOT));h=sha(path)
        assert rel not in pinned or pinned[rel]==h,rel
        pinned[rel]=h
    return dict(sorted(pinned.items()))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--issue',action='store_true');args=parser.parse_args()
    start=time.monotonic()
    if args.issue:assert not CERT.exists(),'Already issued; use the default read-only replay.'
    else:
        frozen=json.loads(CERT.read_text())
        for rel,h in frozen['assets_sha256'].items():assert sha(ROOT/rel)==h,rel
    original=[json.loads((OUT/name).read_text()) for name in
        ('reset_cofactor_receipt.json','fifth_source_cofactor_receipt.json','fifth_route_receipt.json')]
    contracts(*original)
    replay=[reset.compute(),sources.compute(),routes.compute()];contracts(*replay)
    for before,after in zip(original,replay):
        assert without_time(before)==without_time(after),'Exact cofactor/count replay differs.'
    cert=dict(passed=True,Q=1024,U=475136,radius=37,TF=278401,fourth_boundary=1900544,fifth_source_time=2178945,
        candidate_sha256=original[0]['candidate_sha256'],netlist_sha256=original[0]['netlist_sha256'],
        proof_sha256=sha(PROOF),checker_sha256=sha(__file__),
        universal_common_legal_clock_commit_reset_bits=807,universal_Age_zero_bits=19,
        arbitrary_raw_GF_flags_SF_and_instruction_commit_reset_proved=True,
        actual_fourth_boundary_private_native_reset_and_all_alias_Info_zero_proved=True,
        actual_native_quiet_prefix_through_fifth_source_proved=True,
        actual_complete_fifth_command_enclosure_proved_by_written_physical_induction=True,
        free_votes=53,one_votes=46,enclosure_members=1<<53,
        all_shared_words_and_unknown_interior_enlarged_without_independence_assumption=True,
        fixed_one_colonies=original[1]['command_enclosure']['one_colonies'],
        free_colonies=original[1]['command_enclosure']['free_colonies'],
        right_word_population_cases=34816,selected_native_cofactors=170,known_left_native_cofactors=41,
        full_foreign_cofactors=3,full_right_cofactors=41,selected_cofactors_are_supplements=True,
        selected_free_vote_reachability_or_independence_proved=False,
        fifth_pulse_or_full_fourth_upper_successor_or_eventual_general_higher_iid_or_minimum_proved=False,
        additional_rule_change=False,active_G17_modified=False,Gray_or_G17_refutation=False,
        global_reliability_established=False,assets_sha256=assets())
    if args.issue:CERT.write_text(json.dumps(cert,indent=2)+'\n')
    else:assert cert==frozen,'Read-only certificate differs.'
    print(json.dumps(dict(passed=True,readonly=not args.issue,certificate_sha256=sha(CERT),
        assets_verified=len(cert['assets_sha256']),reset_bits=807,Age_zero_bits=19,
        actual_fifth_command_enclosure_proved=True,free_votes=53,one_votes=46,
        fifth_pulse_or_global_reliability_proved=False,seconds=time.monotonic()-start)),flush=True)
if __name__=='__main__':main()
