#!/usr/bin/env python3
"""SP31 symbolic interfaces and complete-start encoding obligations.

The written proof supplies the physical induction; this checker proves
its local symbolic identities and audits the entire new listing.
No damaged-input or iid theorem is certified.
"""
from collections import Counter
from pathlib import Path
from types import FunctionType
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,const_word,w_add_const_mod
import proposed_native_command1024 as proposed
import check_signal_reservation1024_encoded as old_encoding
import check_commit_reset448_incorporation as reset
import check_distant_transport_mismatch as transport_check


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def symbolic_native_interface(module,p,shared):
    def controller(n,cells,*args,**kwargs):
        return dict(addr=[n.input(('proof','GF',b)) for b in range(p.k)],
            age_now=[n.input(('proof','AgeNow',b)) for b in range(p.m)],
            age=[n.input(('proof','AgeNext',b)) for b in range(p.m)],
            f1=n.input(('proof','F1')),f2=n.input(('proof','F2')))
    namespace=dict(module.legacy.__dict__,schema=module.schema,width=module.width,
        previous=module.previous,dependency_table=module.dependency_table,
        service_build=module.service_build,pulse=module.pulse,
        generated_source=module.generated_source,proposed_build=lambda:(controller,'conditional interface only'))
    fn=module.legacy.full_net
    return FunctionType(fn.__code__,namespace,fn.__name__,fn.__defaults__)(p,lambda:shared)[0]


def interfaces(p):
    shared=Net();before=symbolic_native_interface(proposed.prior,p,shared)
    old=dict(before.outputs);shared.outputs={};after=symbolic_native_interface(proposed,p,shared)
    private={'wf2','packet_tag','packet_valid','packet_count','service_valid',
        'service_position','service_count','backward_pressure'}
    equal=state=controls=0
    for key,node in old.items():
        if key[0]=='y' and key[1] in private:continue
        assert after.outputs[key]==node,key;equal+=1
        if key[0]=='y':state+=1
        else:controls+=1
    assert (equal,state,controls)==(824,801,23)
    assert proposed.dependency_table(p)==proposed.prior.dependency_table(proposed.prior.parameters())
    return equal,state,controls


def commit(p):
    observed={}
    def controller(n,cells,*args,**kwargs):
        observed['GF']=cells[0]['addr']
        return dict(addr=cells[0]['addr'],age_now=const_word(p.age_code(p.U-1),p.m),
            age=const_word(0,p.m),f1=n.input(('proof','F1')),f2=n.input(('proof','F2')))
    namespace=dict(proposed.legacy.__dict__,schema=proposed.schema,width=proposed.width,
        previous=proposed.previous,dependency_table=proposed.dependency_table,
        service_build=proposed.service_build,pulse=proposed.pulse,
        generated_source=proposed.generated_source,proposed_build=lambda:(controller,'conditional interface only'))
    fn=proposed.legacy.full_net
    n,_=FunctionType(fn.__code__,namespace,fn.__name__,fn.__defaults__)(p)
    fields=set(reset.RESET_FIELDS)|set(proposed.COMMIT_RESET_FIELDS)|{'wf1'}
    assert fields=={f for f,_ in proposed.schema(p)}-{'addr','age','f1','info'}
    zeros=0
    for field,bits in proposed.schema(p):
        if field in fields:
            for bit in range(bits):assert n.outputs['y',field,bit]==0;zeros+=1
    values=reset.normalized(n)
    for slot in proposed.SLOTS:
        address=w_add_const_mod(n,observed['GF'],slot%p.Q,p.Q)
        # allowed() uses only the retained Q,lo/hi and842-bit mask.
        expected=n.AND(old_encoding.allowed(n,address,p),reset.forwarded_hold(n,p,0,slot))
        # Recompute after adding the expected expression to the graph.
        values=reset.normalized(n)
        assert values[n.outputs['y','info',slot+2]]==values[expected],slot
    assert zeros==807
    return zeros,5


def main():
    start=time.monotonic();p=proposed.parameters();c=proposed.load_artifact();out=ROOT/'figs/robustness'
    dependencies=('SP31_program_build.json','SP31_symbolic_schedule.json','SP31_interface_certificate.json',
        'SP31_native_certificate.json','SP31_front_certificate.json')
    build,programme,interface,native,front=[json.loads((out/name).read_text()) for name in dependencies]
    for r in (build,programme,front):assert r['proposed_candidate_sha256']==c.digest()
    assert interface['candidate_sha256']==c.digest()
    assert native['proposed_netlist_sha256']==c.comp.digest
    assert native['all_time_computed_GF_Age_under_pure_E0_proved']
    assert interface['unrestricted_F1_function_unchanged']
    assert interface['unrestricted_native_GF_Age_F1_F2_private_header_instruction_independence']
    assert programme['final_hold_equalities']==842 and programme['early_flag_equalities']==2
    assert front['maximum_simultaneous_arrivals']==1 and front['all_raw_addresses_in_ROM']
    assert front['all_raw_selectors_in_ROM']
    assert max(programme['latest_capture_input_ages'])<p.E0<p.T_sig<p.T_wf
    assert max(programme['early_flag_store_ages'].values())<min(p.courier_ticks()[1:])
    all_clock,state,controls=interfaces(p);zeros,forward=commit(p)
    normal={row['address'] for row in proposed.dependency_table(p)}
    mask=(set(range(58,901))-{509,515})|{901,902,965}
    assert normal==(set(range(59,901))-{509,515})|{901,902}
    assert len(normal)==842 and mask==normal|{p.lo,p.hi-1}
    alias_cases=0
    for shift in (0,512):
        for phase in (3,509,515,1021):
            for slot in proposed.SLOTS:
                holder=(phase-slot)%p.Q
                assert (holder+shift+slot)%p.Q not in mask;alias_cases+=1
    pairs=sum((phase+slot)%p.Q in mask for phase in range(p.Q) for slot in proposed.SLOTS)
    assert pairs==4220 and p.Q*5-pairs==900
    listing_path=out/'SP31_program_listing.json';listing=json.loads(listing_path.read_text())
    assert len(listing)==130476
    sources=proposed.source_names(p);profile={row['address']:row['offsets'] for row in proposed.dependency_table(p)}
    families=Counter();direct=histories=0
    for row in listing:
        for code in row[7:9]:
            family,index=sources[code];families[family]+=1
            if family=='info':assert row[4] in normal and index==0;direct+=1
            elif family=='ln':assert row[4] in normal and index<len(profile[row[4]]);histories+=1
            else:assert family in ('reg','scr','const')
    coordinates=0
    for row in proposed.dependency_table(p):
        for gather in p.gathers_q:
            for offset in row['offsets']:
                assert 8*(abs(offset)*p.Q//8)==abs(offset)*p.Q
                assert gather*p.Q+abs(offset)*(p.Q//8)+1<p.E0
                assert (row['address']+offset*p.Q)%p.Q in normal;coordinates+=1
    assert coordinates==25284
    transport=transport_check.check_corrected_module(proposed)
    assert transport['all_requested_gather_coordinates_proved']
    quiet=next(t for t in range(p.Q+1) if 2*t-2*((t+8)//9)>=p.Q-2)
    closed=p.T_wf+2*p.Q+1;deadline=closed+1+quiet
    assert (quiet,closed,deadline)==(575,280450,281026)
    assert deadline<p.E0+p.NP*p.PL==382336<p.U-1
    result=dict(proposal='SP31',explicit_new_rule=True,active_G17_or_SP30_modified=False,
        Q=p.Q,U=p.U,width=c.W,radius=37,candidate_sha256=c.digest(),netlist_sha256=c.comp.digest,
        checker_sha256=digest(__file__),proposal_source_sha256=digest(proposed.__file__),
        proof_sha256=digest(Path(__file__).with_name('SP31_OWN_RULE.md')),
        receipt_dependencies_sha256={name:digest(out/name) for name in dependencies},
        source_dependencies_sha256={str(path.relative_to(ROOT)):digest(path) for path in
            (Path(old_encoding.__file__),Path(reset.__file__),Path(transport_check.__file__),
             ROOT/'gacsca/rule.py',ROOT/'gacsca/rule_g.py',ROOT/'gacsca/netlist.py')},
        proof_dependencies_sha256={name:digest(Path(__file__).with_name(name)) for name in
            ('SP30_OWN_RULE.md','SP29_OWN_RULE.md')},
        artifact_sha256=digest(out/'SP31_program.npz'),listing_sha256=digest(listing_path),
        every_current_and_successor_clock_word_symbolic=True,
        conditional_SF_and_control_node_equalities=all_clock,
        conditional_core_state_node_equalities=state,conditional_ROM_control_node_equalities=controls,
        literal_commit_zero_bits=zeros,literal_masked_Hold_Info_forwarding_identities=forward,
        unchanged_sparse_capture_table=True,normal_upper_bit_primaries=len(normal),
        alias_phase_shift_slot_zero_cases=alias_cases,allowed_Info_copy_slots=pairs,unused_Info_copy_slots_zero=900,
        actual_instructions_checked=len(listing),actual_operand_reads_checked=sum(families.values()),
        actual_operand_read_family_counts=dict(families),direct_Info_reads_at_normal_primaries=direct,
        history_reads_at_normal_primaries=histories,actual_normal_gather_coordinates=coordinates,
        physical_transport_certificate=transport,early_flag_store_ages=programme['early_flag_store_ages'],
        courier_load_input_ages=list(p.courier_ticks()[1:]),
        computed_WF1_closed_clock=closed,all_computed_Flag1_quiet_clock=deadline,
        complete_start_noiseless_and_all_period_pure_E0_simulation_proved=True,
        arbitrary_coherent_unused_Info_allowed=True,raw_boundary_decoder_proved=True,
        infinite_noiseless_hierarchy_by_compactness_proved=True,
        canonical_common_Age_zero_native_and_fresh_private_start_required=True,
        errors_restricted_to_actual_global_E0=True,
        actual_damaged_history_commands_or_repeated_repair_or_higher_map_proved=False,
        positive_iid_epsilon_or_Gray_G17_refutation_or_minimum_sufficient_change_proved=False,
        global_reliability_established=False,numerical_whole_CA_trajectory_used=False,
        elapsed_seconds=time.monotonic()-start)
    (out/'SP31_encoded_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ('conditional_SF_and_control_node_equalities',
        'literal_commit_zero_bits','actual_instructions_checked','actual_operand_reads_checked',
        'complete_start_noiseless_and_all_period_pure_E0_simulation_proved',
        'global_reliability_established','elapsed_seconds')}),flush=True)


if __name__=='__main__':main()
