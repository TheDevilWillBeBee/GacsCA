#!/usr/bin/env python3
"""SP30 restricted corrected pulse projection, not a general eroder."""
from pathlib import Path
from types import FunctionType
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,const_word,w_eq,w_eq_const,w_in_range
from gacsca import rule_g
import proposed_sparse_signal_reservation1024 as proposed
from check_commit_reset448_incorporation import normalized

FIELDS=('addr','age','f1','f2','wf1','wf2','packet_tag','packet_valid','packet_count',
        'service_valid','service_position','service_count','backward_pressure')


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def projection_identities(p):
    shared=Net();old,_=proposed.prior.full_net(proposed.prior.parameters(),lambda:shared)
    before=dict(old.outputs);shared.outputs={};new,_=proposed.full_net(p,lambda:shared)
    keys=[key for key in before if key[0]=='y' and key[1] in FIELDS]
    assert len(keys)==73
    for key in keys:assert before[key]==new.outputs[key],key
    return len(keys)


def copy_identities(p,clock):
    observed={}
    def controller(n,cells,*args,**kwargs):
        observed['old']=cells[0]['addr']
        observed['new']=[n.input(('proof','computed_GF',bit)) for bit in range(p.k)]
        observed['F1']=n.input(('proof','computed_F1'))
        return dict(addr=observed['new'],age_now=const_word(p.age_code(clock),p.m),
            age=const_word(p.age_code(clock+1),p.m),f1=observed['F1'],f2=n.input(('proof','computed_F2')))
    namespace=dict(proposed.legacy.__dict__,schema=proposed.schema,width=proposed.width,
        previous=proposed.previous,dependency_table=proposed.dependency_table,
        service_build=proposed.service_build,generated_source=proposed.generated_source,
        proposed_build=lambda:(controller,'conditional native/clock interface only'))
    fn=proposed.legacy.full_net;n,_=FunctionType(fn.__code__,namespace,fn.__name__,fn.__defaults__)(p)
    def vote(primary):
        return rule_g.maj5(n,[n.input(('x',primary-slot,'info',slot+2)) for slot in proposed.SLOTS])
    keep=n.NOT(n.AND(observed['F1'],n.NOT(w_eq(n,observed['new'],observed['old']))))
    expected={slot:n.AND(keep,vote(slot)) for slot in proposed.SLOTS}
    wf=n.all([w_in_range(n,observed['new'],p.Q-5,p.Q),
        int(p.T_wf<=clock<p.T_wf+2*p.Q),n.any(n.AND(w_eq_const(n,observed['new'],address),
            vote(p.Q-3-address)) for address in range(p.Q-5,p.Q))])
    values=normalized(n)
    for slot,node in expected.items():assert values[n.outputs['y','info',slot+2]]==values[node],slot
    assert values[n.outputs['y','wf1',0]]==values[wf]
    source=proposed.generated_source(p)
    assert source.index('    native_refined = distant_refinement(n, cell, p)')<source.index('    c = cell[0]')
    assert source.count("    wipe = n.AND(f1_new, n.NOT(w_eq(n, addr_now, c['addr'])))\n")==1
    return dict(clock=clock,conditional_Info_identities=5,conditional_WF1_identity=1,
        refined_old_GF_word_preserved_symbolically=True,all_raw_Info_and_other_private_and_instruction_inputs_free=True)


def main():
    start=time.monotonic();out=ROOT/'figs/robustness';p=proposed.parameters();candidate=proposed.load_artifact()
    first=json.loads((out/'SP30_first_signal_certificate.json').read_text())
    prior=json.loads((out/'SP29_refined_wipe_certificate.json').read_text())
    assert first['exact_first_signal_physical_history_proved'] and first['proposed_candidate_sha256']==candidate.digest()
    assert first['first_ghost_MF509_one_colonies']==list(range(128,144))
    assert first['first_true_MF1021_one_colonies']==[124,125,126,144,145,146]
    assert prior['corrected_refined_old_GF_factor_proved'] and prior['infinite_line_pulse_lifts_proved_with_corrected_factor']
    equalities=projection_identities(p)
    copies=[copy_identities(p,t) for t in (p.T_wf,p.T_wf+2*p.Q-1,p.T_wf+2*p.Q,p.T_wf+6143)]
    clocks=range(p.T_wf,p.T_wf+6144)
    assert all(t not in (p.T_sig,p.U-1) for t in clocks)
    routes=[]
    for residue in range(p.Q):
        for label in (0,1):
            gf=(residue+512*label)%p.Q
            if gf>=p.Q-5:
                primary=residue+p.Q-3-gf
                assert -2<=primary-residue<=2 and primary%p.Q==(509 if label else 1021)
                routes.append(dict(reader_phase=residue,label=label,source_phase=primary%p.Q,offset=primary-residue))
    assert len(routes)==10
    majority_cases=0
    for old in range(32):
        for keeps in range(32):
            voted=int(old.bit_count()>=3);actual=[voted*((keeps>>j)&1) for j in range(5)]
            assert int(sum(actual)>=3)==voted*int(keeps.bit_count()>=3);majority_cases+=1
    case=next(c for c in prior['cases'] if c['duration']==2048 and c['initial_true_phase_extras'])
    log=out/case['log_name'];assert digest(log)==case['log_sha256']
    rows=[json.loads(line) for line in log.read_text().splitlines()];summary=rows.pop()
    assert [row['row'] for row in rows]==list(range(6145))
    assert summary==case['exhaustive_checks'] and summary['certificate_complete']
    assert summary['GF_support_sites_checked']==6145*262144 and summary['refined_wipe_active_majority_disagreements']==0
    assert rows[-1]==case['final'] and (rows[-1]['left'],rows[-1]['right_exclusive'],rows[-1]['wrong_Addresses'])==(124416,139264,14848)
    assert rows[-1]['Info509_ones']==8 and rows[-1]['Info1021_ones']==3
    for row in rows:
        assert row['background_lo']==124*1024-8*(row['row']+1)-37
        assert row['background_hi']==147*1024+8*(row['row']+1)+37
    asset=out/'SP29_refined_wipe_final_states.npz';assert digest(asset)==prior['final_state_asset_sha256']
    with np.load(asset,allow_pickle=False) as saved:
        native=saved['duration2048_mode1_native'];code=saved['duration2048_mode1_code'];info=saved['duration2048_mode1_Info']
        assert native.shape==(8,262144) and code.shape==info.shape==(262144,)
        assert np.flatnonzero(native[0]).tolist()==list(range(124416,139264))
        assert not native[[2,3,4,6,7]].any() and not code.any()
        expected=np.zeros(262144,dtype=np.uint8);expected[123904:124416]=1;expected[138752:139264]=1
        assert np.array_equal(native[1],expected)
        assert np.flatnonzero(info[np.arange(1021,262144,1024)]).tolist()==[144,145,146]
        left509=np.flatnonzero(info[np.arange(509,262144,1024)]).tolist();assert len(left509)==8
    dependencies=('SP30_first_signal_certificate.json','SP30_encoded_certificate.json','SP30_native_certificate.json',
        'SP29_refined_wipe_certificate.json','SP28_short_epoch_enclosure_gap_certificate.json')
    result=dict(proposal='SP30',proposed_rule_change=False,additional_rule_change=False,active_G17_modified=False,
        scope='J192 new-own-rule restricted corrected native/Info factor and actual first6144-update pulse on Z; no general eroder/higher/iid',
        Q=p.Q,U=p.U,T_wf=p.T_wf,force_duration=2048,pulse_updates=6144,
        checker_sha256=digest(__file__),written_proof_sha256=digest(ROOT/'Report/proofs/SP30_NATIVE_PULSE.md'),
        proposal_source_sha256=digest(proposed.__file__),parent_proposal_source_sha256=digest(proposed.prior.__file__),
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        full_generated_source_sha256=hashlib.sha256(proposed.generated_source(p).encode()).hexdigest(),
        source_helpers_sha256={name:digest(ROOT/name) for name in ('gacsca/netlist.py','gacsca/rule_g.py',
            'Report/proofs/check_commit_reset448_incorporation.py','Report/proofs/check_g17_schedule.py',
            'Report/proofs/SP29_REFINED_WIPE_FACTOR.md','Report/proofs/SP28_SHORT_EPOCH_ENCLOSURE_GAP.md')},
        receipt_dependencies_sha256={name:digest(out/name) for name in dependencies},
        reused_frozen_factor_source_sha256=digest(out/'SP29_refined_wipe_factor_generated.c'),
        reused_frozen_wrapper_source_sha256=digest(out/'SP29_refined_wipe_pulse_generated.c'),
        reused_all_row_log_name=log.name,reused_all_row_log_sha256=digest(log),
        reused_final_projected_state_asset_sha256=digest(asset),
        unrestricted_native_header_output_node_equalities=equalities,conditional_copy_WF1_cofactors=copies,
        exhaustive_copy_keep_majority_cases=majority_cases,legal_no_write_clock_cases=len(clocks),
        exact_guarded_source_routes=routes,corrected_keep_compares_to_refined_old_GF=True,
        arbitrary_other_private_fields_and_instructions_irrelevant_to_restricted_factor=True,
        arbitrary_binary_labels_and_raw_Flag1_Flag2_allowed_for_factor=True,
        common_legal_clock_and_initial_empty_headers_and_no_later_errors_required=True,
        actual_first_signal_supplies_projected_initial_state=True,
        all6145_reused_rows_equal_new_projected_history_by_induction=True,
        new_actual_first_pulse_on_Z_proved=True,numerical_whole_CA_trajectory_used=False,
        actual_endpoint_time=p.T_wf+6144,initial_wrong_GF_interval=[130560,147456],final_wrong_GF_interval=[124416,139264],
        width_decrease=2048,final_Flag1_intervals=[[123904,124416],[138752,139264]],
        final_native_auxiliaries_and_code_positions_zero=True,final_MF509_one_colonies=left509,final_MF1021_one_colonies=[144,145,146],
        final_protected_infinite_line_interval=[77779,199725],
        full_other_private_trajectory_or_boundary_or_next_signal_proved=False,
        general_clock_phase_width_fault_eroder_or_continuing_E0_proved=False,
        higher_error_map_or_positive_iid_rate_proved=False,global_reliability_established=False,
        seconds=time.monotonic()-start)
    path=out/'SP30_native_pulse_certificate.json';path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('unrestricted_native_header_output_node_equalities',
        'actual_endpoint_time','final_wrong_GF_interval','width_decrease','new_actual_first_pulse_on_Z_proved',
        'seconds','global_reliability_established')}),flush=True)


if __name__=='__main__':main()
