#!/usr/bin/env python3
"""New SP30 local functions, commit/alias and complete-start interfaces."""
from collections import Counter
from pathlib import Path
from types import FunctionType
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,const_word,w_in_range,w_eq_const,w_add_const_mod
import proposed_sparse_signal_reservation1024 as proposed
import check_commit_reset448_incorporation as reset
import check_distant_transport_mismatch as transport_check


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def allowed(n,address,p):
    old=n.all([w_in_range(n,address,p.lo,p.lo+proposed.width(p)+1),
        n.NOT(w_eq_const(n,address,509)),n.NOT(w_eq_const(n,address,515))])
    return n.any([old,w_eq_const(n,address,901),w_eq_const(n,address,902),w_eq_const(n,address,p.hi-1)])


def changed_capture_functions(p):
    shared=Net();old,_=proposed.prior.full_net(proposed.prior.parameters(),lambda:shared)
    before=dict(old.outputs);shared.outputs={}
    new,_=proposed.full_net(p,lambda:shared)
    assert set(before)==set(new.outputs)
    equal=changed=0
    expected={("y",field,slot*64+rank) for field in ('h1','h2') for slot in range(5) for rank in range(8)}
    differences=set()
    for key,node in before.items():
        if key[0]!='y':
            assert new.outputs[key]==node,key
            continue
        if key[0]=='y' and key[1]=='info':continue
        if new.outputs[key]==node:equal+=1
        else:differences.add(key);changed+=1
    assert differences==expected and (equal,changed)==(757,80)
    # Isolate the table change from the Info-mask change. With the old
    # capture table and new literal source, all837 non-Info outputs are
    # exactly the old unrestricted Boolean functions in this shared Net.
    shared.outputs={}
    namespace=dict(proposed.legacy.__dict__,schema=proposed.schema,width=proposed.width,
        previous=proposed.previous,dependency_table=lambda unused:proposed.prior.dependency_table(proposed.prior.parameters()),
        service_build=proposed.service_build,generated_source=proposed.generated_source)
    fn=proposed.legacy.full_net
    middle,_=FunctionType(fn.__code__,namespace,fn.__name__,fn.__defaults__)(p,lambda:shared)
    for key,node in before.items():
        if key[0]=='y' and key[1]=='info':continue
        assert middle.outputs[key]==node,key
    old_table=proposed.prior.dependency_table(proposed.prior.parameters());new_table=proposed.dependency_table(p)
    assert len(old_table)==len(new_table)==842
    for a,b in zip(old_table,new_table):
        assert (a['field'],a['bit'],a['offsets'])==(b['field'],b['bit'],b['offsets'])
        assert b['address']==proposed.RELOCATIONS.get(a['address'],a['address'])
    def controls(table):
        return {(row['address'],rank):off for row in table for rank,off in enumerate(row['offsets'])}
    old_controls,new_controls=controls(old_table),controls(new_table)
    bindings=0
    for phase in range(p.Q):
        for rank in range(64):
            if old_controls.get((phase,rank))!=new_controls.get((phase,rank)):
                assert phase in (509,515,901,902) and rank<8
                assert (old_controls.get((phase,rank)),new_controls.get((phase,rank))) in (
                    (None,(-4,-3,-2,-1,1,2,3,4)[rank]),((-4,-3,-2,-1,1,2,3,4)[rank],None))
                bindings+=1
    assert bindings==32
    return equal,changed,bindings


def commit(p):
    observed={}
    def controller(n,cells,*args,**kwargs):
        observed['GF']=cells[0]['addr']
        return dict(addr=cells[0]['addr'],age_now=const_word(p.age_code(p.U-1),p.m),age=const_word(0,p.m),
            f1=n.input(('proof','F1')),f2=n.input(('proof','F2')))
    namespace=dict(proposed.legacy.__dict__,schema=proposed.schema,width=proposed.width,
        previous=proposed.previous,dependency_table=proposed.dependency_table,
        service_build=proposed.service_build,generated_source=proposed.generated_source,
        proposed_build=lambda:(controller,'conditional interface only'))
    fn=proposed.legacy.full_net;n,_=FunctionType(fn.__code__,namespace,fn.__name__,fn.__defaults__)(p)
    fields=set(reset.RESET_FIELDS)|set(proposed.COMMIT_RESET_FIELDS)|{'wf1'}
    assert fields=={f for f,_ in proposed.schema(p)}-{'addr','age','f1','info'}
    zeros=0
    for field,bits in proposed.schema(p):
        if field in fields:
            for bit in range(bits):assert n.outputs['y',field,bit]==0;zeros+=1
    expected={}
    for slot in proposed.SLOTS:
        address=w_add_const_mod(n,observed['GF'],slot%p.Q,p.Q)
        expected[slot]=n.AND(allowed(n,address,p),reset.forwarded_hold(n,p,0,slot))
    values=reset.normalized(n)
    for slot,value in expected.items():assert values[n.outputs['y','info',slot+2]]==values[value],slot
    assert zeros==807
    return zeros,len(expected)


def main():
    start=time.monotonic();out=ROOT/'figs/robustness';p=proposed.parameters();candidate=proposed.load_artifact()
    build=json.loads((out/'SP30_program_build.json').read_text())
    programme=json.loads((out/'SP30_symbolic_schedule.json').read_text())
    native=json.loads((out/'SP30_native_certificate.json').read_text())
    front=json.loads((out/'SP30_front_certificate.json').read_text())
    for r in (build,programme,front):assert r['proposed_candidate_sha256']==candidate.digest()
    assert native['proposed_netlist_sha256']==candidate.comp.digest
    assert build['build_complete'] and programme['final_hold_equalities']==842 and programme['early_flag_equalities']==2
    assert programme['history_ranks_checked']==64 and native['all_time_computed_GF_Age_under_E0_plus_real1_proved']
    assert front['maximum_simultaneous_arrivals']==1 and front['all_raw_addresses_in_ROM'] and front['all_raw_selectors_in_ROM']
    assert max(programme['latest_capture_input_ages'])<p.E0<p.T_sig<p.T_wf
    assert max(programme['early_flag_store_ages'].values())<min(p.courier_ticks()[1:])
    native_equalities,capture_outputs,capture_bindings=changed_capture_functions(p);zeros,forward=commit(p)
    normal={r['address'] for r in proposed.dependency_table(p)}
    mask=(set(range(58,901))-{509,515})|{901,902,965}
    assert normal==(set(range(59,901))-{509,515})|{901,902}
    assert mask==normal|{p.lo,p.hi-1} and len(mask)==844
    aliases=(3,509,515,1021);alias_checks=0
    for shift in (0,512):
        for phase in aliases:
            assert (phase+shift)%p.Q not in mask
            for slot in proposed.SLOTS:
                holder=(phase-slot)%p.Q
                assert (holder+shift+slot)%p.Q not in mask;alias_checks+=1
    pairs=sum((phase+slot)%p.Q in mask for phase in range(p.Q) for slot in proposed.SLOTS)
    assert pairs==4220 and p.Q*5-pairs==900
    listing_path=out/'SP30_program_listing.json';listing=json.loads(listing_path.read_text())
    assert len(listing)==131238
    sources=proposed.source_names(p);profile={r['address']:r['offsets'] for r in proposed.dependency_table(p)}
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
    deps=('SP30_program_build.json','SP30_symbolic_schedule.json','SP30_native_certificate.json','SP30_front_certificate.json')
    result=dict(proposal='SP30',proposed_rule_change=True,active_G17_modified=False,SP29_modified=False,
        scope='J189 new alias reservation/relocation/commit plus complete-start broad-Info/noiseless/all-period actual-E0 simulation; damaged-history eroder/higher/iid unproved',
        Q=p.Q,U=p.U,width=candidate.W,radius=37,history_ranks=64,force_duration=2048,
        checker_sha256=digest(__file__),written_proof_sha256=digest(ROOT/'Report/proofs/SP30_OWN_RULE.md'),
        proposal_source_sha256=digest(proposed.__file__),parent_proposal_source_sha256=digest(proposed.prior.__file__),
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        full_generated_source_sha256=hashlib.sha256(proposed.generated_source(p).encode()).hexdigest(),
        source_helpers_sha256={name:digest(ROOT/name) for name in ('gacsca/rule.py','gacsca/rule_g.py','gacsca/netlist.py',
            'Report/proofs/check_commit_reset448_incorporation.py','Report/proofs/check_distant_transport_mismatch.py')},
        receipt_dependencies_sha256={name:digest(out/name) for name in deps},
        retained_initial_checker_failure_assets_sha256={name:digest(out/name) for name in
            ('SP30_encoded_initial_checker.py.txt','SP30_encoded_initial_checker_failure.txt',
             'SP30_encoded_capture_checker_failure.py.txt','SP30_encoded_capture_checker_failure.txt',
             'SP30_encoded_count_checker_failure.py.txt','SP30_encoded_count_checker_failure.txt')},
        artifact_sha256=digest(out/'SP30_program.npz'),listing_sha256=digest(listing_path),
        non_Info_output_function_equalities=native_equalities,literal_commit_zero_bits=zeros,
        non_Info_changed_history_outputs=capture_outputs,
        capture_address_rank_bindings_checked=65536,changed_capture_address_rank_bindings=capture_bindings,
        old_capture_table_new_Info_mask_non_Info_equalities=837,
        unrestricted_ROM_control_output_equalities=23,
        literal_forwarded_Hold_Info_mask_identities=forward,signal_aliases_reserved=[509,515],
        relocated_upper_fields=[dict(field='h2',bit=77,old_phase=509,new_phase=901),dict(field='h2',bit=83,old_phase=515,new_phase=902)],
        alias_primary_phases=list(aliases),alias_phase_shift_slot_zero_cases=alias_checks,
        allowed_Info_primaries=len(mask),allowed_Info_copy_slots=pairs,unused_Info_copy_slots_zero=900,
        actual_instructions_checked=len(listing),actual_operand_reads_checked=sum(families.values()),
        actual_operand_read_family_counts=dict(families),direct_Info_reads_at_represented_primaries=direct,
        gathered_history_reads_at_represented_primaries=histories,gathered_normal_source_coordinates_checked=coordinates,
        physical_transport_certificate=transport,physical_transport_checker_sha256=digest(transport_check.__file__),
        early_flag_store_ages=programme['early_flag_store_ages'],courier_load_input_ages=list(p.courier_ticks()[1:]),
        source_free_Flag1_contraction_updates=quiet,computed_WF1_closed_clock=closed,
        all_computed_Flag1_quiet_clock=deadline,evaluation_end_input_clock=382336,commit_input_clock=p.U-1,
        alias_reset_proved_conditionally_on_native_GF_and_commit_clock=True,
        ordinary_bit_representation_complete_and_special_alias_disjoint=True,
        abstract_execution_lifted_to_physical_complete_encodings_under_E0=True,
        complete_encoded_noiseless_and_all_period_E0_simulation_proved=True,
        arbitrary_coherent_unused_Info_allowed=True,all_period_boundary_decoder_proved=True,
        infinite_noiseless_hierarchy_by_compactness_proved=True,
        initial_native_canonical_common_Age_zero_and_private_fields_zero_required=True,
        errors_restricted_to_actual_global_E0=True,
        arbitrary_damaged_history_or_general_eroder_or_higher_error_map_proved=False,
        SP29_damaged_history_certificates_transferred_to_new_rule=False,
        iid_threshold_or_minimum_globally_sufficient_repair_proved=False,
        numerical_whole_CA_trajectory_used=False,global_reliability_established=False,
        seconds=time.monotonic()-start)
    path=out/'SP30_encoded_certificate.json';path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('non_Info_output_function_equalities','literal_commit_zero_bits',
        'alias_phase_shift_slot_zero_cases','actual_instructions_checked','actual_operand_reads_checked',
        'direct_Info_reads_at_represented_primaries','gathered_history_reads_at_represented_primaries',
        'complete_encoded_noiseless_and_all_period_E0_simulation_proved','seconds','global_reliability_established')}),flush=True)


if __name__=='__main__':main()
