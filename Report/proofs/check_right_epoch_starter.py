#!/usr/bin/env python3
"""J116: right-epoch startup, packet shadow and native-period premises.

Exact local Boolean cofactors plus written simultaneous induction.
Unincorporated explicitly changed local transition, no own ROM or iid
threshold. Initial native GF/Age halfline at its epoch remains a premise.
"""
from itertools import combinations
from pathlib import Path
from types import FunctionType
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled,const_word,w_eq_const,w_mux,mixed_age_increment,w_in_range
from check_right_barrier import dominant_majority,check_dominance_primitive
from check_buffered448_command import read
import check_buffered448_period_barrier as period
import check_commit_reset448_incorporation as reset
import proposed_right_epoch_starter as proposed

PAIRS=tuple(combinations(range(-5,6),2))
STARTUP_PAIRS=tuple(combinations(range(-5,9),2))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def native_cells(n,p,center,faults,clock):
    age=const_word(p.age_code(clock),p.m) if isinstance(clock,int) else clock
    cells={}
    for j in range(-12,13):
        good=center+j >= 0 and j not in faults
        cells[j]=dict(addr=const_word((center+j)%p.Q,p.k) if good else
                      [n.input(('x',j,'addr',b)) for b in range(p.k)],
            age=age if good else [n.input(('x',j,'age',b)) for b in range(p.m)])
    return cells


def startup_case(p,reader,faults):
    class BoundNet(Net):
        def input(self,key):
            if key[0] == 'x':
                _,off,f,b=key
                if reader+off >= 0 and off not in faults:
                    if f == 'addr': return (((reader+off)%p.Q)>>b)&1
                    if f == 'age': return (p.age_code(p.T_wf)>>b)&1
            return super().input(key)
    n,_=proposed.full_net(p,net_class=BoundNet,symbolic=True,observe=True)
    assert n.outputs['proof','epoch_force'] == 1
    assert [n.outputs['y','addr',b] for b in range(p.k)] == const_word(reader,p.k)
    assert [n.outputs['y','age',b] for b in range(p.m)] == const_word(p.age_code(p.T_wf+1),p.m)
    assert n.outputs['y','f2',0] == 1
    if reader in range(1,6):
        assert n.outputs['proof','birth'] == 1
        assert n.outputs['y','wf2',0] == n.outputs['y','packet_valid',0] == 1
        assert [n.outputs['y','packet_tag',b] for b in range(4)] == const_word(reader-1,4)
        assert all(n.outputs['y','packet_count',b] == 0 for b in range(11))


def birth_geometry(p):
    closed=holder=clean_edges=0
    for reader in range(-1,10):
        for faults in PAIRS:
            n=Net()
            age=[n.input(('common_age',b)) for b in range(p.m)]
            cells=native_cells(n,p,reader,faults,age)
            e=proposed.epoch(n,cells,p,dominant_majority)
            assert e['addr'] == const_word(reader%p.Q,p.k)
            assert e['age'] == age
            if reader not in range(1,6):
                assert e['birth'] == 0,(reader,faults)
                closed += 1
            else:
                assert e['birth'] == e['force'] == w_eq_const(n,age,p.age_code(p.T_wf))
                assert e['tag'] == const_word(reader-1,4)
                holder += 1
    for reader in (-3,-2):
        for faults in PAIRS:
            if any(reader+j in range(4) for j in faults):
                continue
            n=Net()
            age=[n.input(('common_age',b)) for b in range(p.m)]
            cells=native_cells(n,p,reader,faults,age)
            e=proposed.epoch(n,cells,p,dominant_majority)
            assert e['birth'] == 0,(reader,faults)
            clean_edges += 1
    assert (closed,holder,clean_edges) == (330,275,49)
    return closed,holder,clean_edges


def shadow_arithmetic():
    groups=[()]+[(x,) for x in range(-8,15)]+[(x,x+1) for x in range(-9,15)]
    cases=maximum=0
    for group in groups:
        possible=[x for x in (-3,-2)
            if len([y for y in range(x+1,x+6) if y>=0 and y not in group]) < 3]
        for root in range(-4,5):
            births=[x for x in possible if root+1 <= x <= root+5]
            assert len(births) <= 2
            assert not births or set(group)&set(range(4))
            assert root != 0 or not births
            maximum=max(maximum,len(births))
            cases += 1
    exclusions=0
    for charge in range(4):
        for next_error in range(-8,15):
            assert abs(next_error-charge) < 24
            exclusions += 1
    assert (cases,maximum,exclusions) == (432,2,92)
    return dict(dangerous_overlapping_root_group_shadows=cases,max_newborns_per_dangerous_root=maximum,
        dangerous_birth_requires_current_error_on=[0,3],next_row_error_exclusion_interval=[-8,14],
        next_row_E0_separation_cases=exclusions)


def wiring(p):
    n,source=proposed.full_net(p,observe=True)
    base=proposed.base
    read_bit=lambda off,f,b:n.input(('x',off,f,b))
    cells={j:dict(addr=[read_bit(j,'addr',b) for b in range(p.k)],
        age=[read_bit(j,'age',b) for b in range(p.m)],
        **{f:read_bit(j,f,0) for f in ('f1','f2','wf1','wf2')}) for j in range(-12,13)}
    e=proposed.epoch(n,cells,p)
    service=base.service.build(n,{j:dict(packet_tag=[read_bit(j,'packet_tag',b) for b in range(4)],
        packet_valid=read_bit(j,'packet_valid',0),wf2=read_bit(j,'wf2',0),
        packet_count=[read_bit(j,'packet_count',b) for b in range(11)],
        flag_valid=read_bit(j,'service_valid',0),flag_position=[read_bit(j,'service_position',b) for b in range(9)],
        flag_count=[read_bit(j,'service_count',b) for b in range(11)]) for j in range(-5,6)})
    mt=base.proposed_build()[0](n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,
        service_force=n.OR(service['service_force'],e['force']))
    commit=w_eq_const(n,mt['age_now'],p.age_code(p.U-1))
    assert n.outputs['proof','epoch_force'] == e['force'] and n.outputs['proof','birth'] == e['birth']
    expected=dict(addr=mt['addr'],age=mt['age'],f1=mt['f1'],f2=n.AND(mt['f2'],n.NOT(commit)),
        wf2=n.AND(n.OR(e['birth'],service['wf2']),n.NOT(commit)),
        packet_valid=n.AND(n.OR(e['birth'],service['packet_valid']),n.NOT(commit)),
        packet_tag=[n.AND(b,n.NOT(commit)) for b in w_mux(n,e['birth'],e['tag'],service['packet_tag'])],
        packet_count=[n.AND(b,n.NOT(commit)) for b in w_mux(n,e['birth'],[0]*11,service['packet_count'])],
        service_valid=n.AND(service['flag_valid'],n.NOT(commit)),
        service_position=[n.AND(b,n.NOT(commit)) for b in service['flag_position']],
        service_count=[n.AND(b,n.NOT(commit)) for b in service['flag_count']])
    identities=0
    structural_nodes=[]
    for field,word in expected.items():
        for b,node in enumerate(word if isinstance(word,list) else [word]):
            assert n.outputs['y',field,b] == node,(field,b)
            structural_nodes.append(node)
            identities += 1
    assert identities == 66
    reachable=set()
    stack=list(structural_nodes)
    while stack:
        node=stack.pop()
        if node in reachable:
            continue
        reachable.add(node)
        if n.kind[node] == 'G':
            _,a,b=n.gate[node]
            stack.extend((a,b))
    dependencies=[key for key,node in n.input_node.items() if node in reachable]
    assert all(key[0] == 'x' and -5 <= key[1] <= 8 for key in dependencies)
    clean,clean_source=proposed.full_net(p)
    live=set(clean.live_nodes())
    profile={(row['field'],row['bit']):set(row['offsets']) for row in base.dependency_table(p)}
    for key,node in clean.input_node.items():
        if key[0] == 'x' and node in live:
            _,off,f,b=key
            assert off == 0 or off in profile[f,b],key
    assert base.schema(p) == proposed.schema(p) and base.width(p) == 316
    return identities,Compiled(clean).digest,hashlib.sha256(clean_source.encode()).hexdigest()


def WF1_identities(p):
    checked=0
    for reader in range(p.Q-5,p.Q):
        def controller(n,*args,**kwargs):
            age=[n.input(('proof_common_Age',b)) for b in range(p.m)]
            return dict(addr=const_word(reader,p.k),age_now=age,
                age=mixed_age_increment(n,age,p.PB,p.R,p.nb),f1=0,f2=n.input(('proof_free_F2',)))
        n,_=proposed.full_net(p,maintenance=controller)
        age=[n.input(('proof_common_Age',b)) for b in range(p.m)]
        expected=n.AND(w_in_range(n,age,p.age_code(p.T_wf),p.age_code(p.T_wf+2*p.Q-1)+1),
            read(n,p,reader,p.Q-3,'info'))
        assert n.outputs['y','wf1',0] == expected
        checked += 1
    return checked


def timing(p):
    T=p.U-p.T_wf
    increments=excluded=0
    for t in range(T):
        clock=p.T_wf+t
        n=Net()
        assert mixed_age_increment(n,const_word(p.age_code(clock),p.m),p.PB,p.R,p.nb) == const_word(p.age_code((clock+1)%p.U),p.m)
        increments += 1
        if t >= 897:
            assert w_in_range(n,const_word(p.age_code(clock),p.m),p.age_code(p.T_wf),p.age_code(p.T_wf+2*p.Q-1)+1) == 0
            excluded += 1
        if 1 <= t <= 1792:
            assert clock < p.U-1 and clock != p.T_wf
    assert (T,increments,excluded) == (38719,38719,37822)
    old=period.quieting_arithmetic(p)
    assert old['all_C_Flag1_quiet_computed_state']-1792 == 1150 < 1792
    for clock in range(p.T_wf):
        n=Net()
        assert w_in_range(n,const_word(p.age_code(clock),p.m),p.age_code(p.T_wf),p.age_code(p.T_wf+2*p.Q-1)+1) == 0
        assert mixed_age_increment(n,const_word(p.age_code(clock),p.m),p.PB,p.R,p.nb) == const_word(p.age_code(clock+1),p.m)
    return dict(initial_epoch_clock=p.T_wf,current_boundary_state=T,
        mixed_radix_increment_checks=increments,WF1_closed_clock_checks=excluded,
        source_free_WF1_computed_state=898,last_two_Flag1_quiet_computed_state=899,
        further_quiet_suffix_updates=251,all_C_Flag1_quiet_computed_state=1150,
        source_born_computed_state=1,proper_packet_last_active_computed_state=1792,
        proper_holder_noncommit_clock_checks=1792,
        later_period_quiet_native_pre_epoch_increment_and_closed_window_checks=p.T_wf,
        first_full_native_reset_state=T,later_native_reset_spacing=p.U,
        all_time_native_GF_Age_and_periodic_C_native_workspace_reset_proved=True)


def main():
    p=proposed.parameters()
    dominance=check_dominance_primitive()
    identities,net_sha,source_sha=wiring(p)
    startup=0
    for reader in range(7):
        for faults in STARTUP_PAIRS:
            startup_case(p,reader,faults)
            startup += 1
        print(json.dumps(dict(startup_native_cofactors=startup)),flush=True)
    closed,holder,edges=birth_geometry(p)
    shadow=shadow_arithmetic()
    times=timing(p)
    wf=WF1_identities(p)
    fn=FunctionType(reset.commit_identities.__code__,dict(reset.__dict__,proposed=proposed),
        reset.commit_identities.__name__,reset.commit_identities.__defaults__)
    zeros,info=fn(p)
    assert (zeros,info,wf) == (283,5,5)
    out=ROOT/'figs/robustness'
    quiet=json.loads((out/'SP16_quiet_region_certificate.json').read_text())
    native=json.loads((out/'SP16_period_barrier_certificate.json').read_text())
    receipt=dict(proposed_rule_change=True,standalone_unincorporated_module=True,
        active_G17_modified=False,SP17_modified=False,SP16_modified=False,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        base_SP17_proposal_source_sha256=digest(Path(proposed.base.__file__)),helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        module_raw_netlist_sha256=net_sha,module_generated_source_sha256=source_sha,
        actual_maintenance_source_sha256=hashlib.sha256(proposed.base.proposed_build()[1].encode()).hexdigest(),
        majority_helper_sha256=digest(ROOT/'Report/proofs/check_right_barrier.py'),
        WF1_read_helper_sha256=digest(ROOT/'Report/proofs/check_buffered448_command.py'),
        period_helper_sha256=digest(Path(period.__file__)),commit_helper_sha256=digest(Path(reset.__file__)),
        quiet_native_receipt_sha256=digest(out/'SP16_quiet_region_certificate.json'),
        period_native_receipt_sha256=digest(out/'SP16_period_barrier_certificate.json'),
        packet_pressure_receipt_sha256=digest(out/'packet_pressure_certificate.json'),
        buffered_service_receipt_sha256=digest(out/'buffered_framed_service_certificate.json'),
        Q=p.Q,U=p.U,width=316,dominance_primitive_assignments=dominance,
        full_raw_maintenance_packet_code_wiring_identities=identities,
        full_raw_maintenance_packet_code_outputs_dependency_interval=[-5,8],
        full_raw_maintenance_packet_code_outputs_independent_of_I=True,
        actual_full_rule_epoch_native_cofactors=startup,actual_full_rule_unconditional_proper_birth_cofactors=455,
        RF_GF_closed_foreign_birth_cofactors=closed,RF_GF_proper_birth_iff_common_clock_epoch_cofactors=holder,
        negative_edge_birth_requires_positive_GF_fault_cofactors=edges,
        actual_full_rule_WF1_window_Info_identities=wf,literal_commit_reset_zero_bits=zeros,
        literal_commit_Info_Hold_mask_identities=info,
        inherited_quiet_native_cofactors=quiet['quiet_native_GF_Age_Flag1_cofactors'],
        inherited_active_source_GF_Age_cofactors=quiet['source_sealed_GF_Age_free_flags_cofactors'],
        inherited_Flag1_seed_stable_growth_cofactors=[native['last_two_Flag1_seed_cofactors'],
            native['stable_quiet_Flag1_suffix_cofactors'],native['two_cell_quiet_suffix_growth_outside_charge_zone_cofactors']],
        **shadow,**times,
        initial_canonical_GF_and_epoch_Age_halfline_x_ge_zero_required=True,
        all_initial_flags_packets_codes_counters_and_work_arbitrary=True,
        initial_quiet_colony_work_seed_upper_command_and_packet_clearance_not_required=True,
        global_E0_required=True,no_future_native_boundary_prescribed=True,
        actual_birth_geometry_replaces_guard_shadow_in_simultaneous_packet_GF_Age_induction=True,
        protected_proper_packet1_through1792_proved=True,
        positive_GF_Age_native_barrier_through38719_proved=True,
        C_Flag1_WF1_quiet1150_through_boundary_proved=True,
        complete_C_structural_and_workspace_commit_reset_proved=True,
        new_raw_state_or_dependency_offsets_added=False,
        own_ROM_or_complete_self_simulating_candidate_built=False,
        represented_Info_result_or_complete_encoding_boundary_proved=False,
        arbitrary_damaged_GF_Age_seed_recovery_full_upper_error_map_established=False,
        iid_threshold_established=False,global_reliability_established=False,
        scope='ROBUSTNESS J116: explicit unincorporated RF epoch starter; all-time native barrier and periodic C structural/workspace reset from initial positive GF/Age epoch halfline and E0, with all other initial state arbitrary; no own ROM, data correctness, general field-seed reconstruction or iid theorem')
    (out/'right_epoch_starter_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(startup=startup,birth=455,quiet=1150,boundary=38719,
        own_ROM=False,global_reliability_established=False)),flush=True)


if __name__ == '__main__':
    main()
