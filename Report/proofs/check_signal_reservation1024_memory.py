#!/usr/bin/env python3
"""SP30 explicit infinite initializers and restricted local bit memory.

Finite contracts supplement the universal rank/time proofs in the Markdown;
this is not a numerical whole-CA trajectory or a positive-iid certificate.
"""
from pathlib import Path
from types import FunctionType
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,const_word,w_eq_const
from gacsca import rule_g
import proposed_sparse_signal_reservation1024 as proposed
import check_commit_reset448_incorporation as reset

SHIFT=-94


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def logical_info(y,b,trace=None):
    assert b in (0,1)
    while True:
        if trace is not None:trace.append(y)
        if -2<=y<=2:return b
        g,p=divmod(y-SHIFT,1024)
        if 59<=p<=68:return (((g-SHIFT)%1024)>>(p-59))&1
        if not 92<=p<=96:return 0
        parent=g+p-94
        assert g!=0 and abs(y)>=1024*abs(g)-2 and abs(parent)<abs(y),(y,parent)
        y=parent


def initial_bits(x,b,candidate):
    gf=(x-SHIFT)%1024
    return [((gf>>i)&1) if f=='addr' else logical_info(x+i-2,b) if f=='info' else 0
            for f,i in candidate.rows]


def centre_identity(p,slot):
    holder=-slot;gf=(holder-SHIFT)%p.Q
    class CanonicalGF(Net):
        def input(self,key):
            if isinstance(key,tuple) and len(key)==4 and key[0]=='x' and key[2]=='addr':
                return (((holder+key[1]-SHIFT)%p.Q)>>key[3])&1
            return super().input(key)
    def controller(n,cells,*args,**kwargs):
        assert cells[0]['addr']==const_word(gf,p.k)
        return dict(addr=cells[0]['addr'],
            age_now=[n.input(('proof','clock',i)) for i in range(p.m)],
            age=[n.input(('proof','next_clock',i)) for i in range(p.m)],
            f1=n.input(('proof','F1')),f2=n.input(('proof','F2')))
    namespace=dict(proposed.legacy.__dict__,schema=proposed.schema,width=proposed.width,
        previous=proposed.previous,dependency_table=proposed.dependency_table,
        service_build=proposed.service_build,generated_source=proposed.generated_source,
        proposed_build=lambda:(controller,'canonical native GF conditional interface'))
    fn=proposed.legacy.full_net
    n,_=FunctionType(fn.__code__,namespace,fn.__name__,fn.__defaults__)(p,CanonicalGF)
    clock=[n.input(('proof','clock',i)) for i in range(p.m)]
    commit=w_eq_const(n,clock,p.age_code(p.U-1))
    old=rule_g.maj5(n,[n.input(('x',slot-s,'info',s+2)) for s in proposed.SLOTS])
    expected=n.MUX(commit,reset.forwarded_hold(n,p,0,slot),old)
    values=reset.normalized(n)
    assert values[n.outputs['y','info',slot+2]]==values[expected],slot
    assert gf+slot==94 and 94 in proposed.layout(p)
    return dict(physical_holder=holder,Info_slot=slot,GF=gf,virtual_primary=94,
        all_raw_clocks_Info_private_flags_and_instructions_free=True,
        actual_centre_carry_or_forwarded_commit_identity=True)


def main():
    started=time.monotonic();p=proposed.parameters();c=proposed.load_artifact();out=ROOT/'figs/robustness'
    table=proposed.dependency_table(p)
    assert (p.Q,p.U,c.W)==(1024,475136,842) and proposed.SLOTS==(-2,-1,0,1,2)
    assert [(r['bit'],r['address']) for r in table if r['field']=='addr']==list(enumerate(range(59,69)))
    assert [(r['bit'],r['address']) for r in table if r['field']=='info']==list(enumerate(range(92,97)))
    assert [(r['field'],r['bit']) for r in table]==c.rows and np.array_equal(c.layout,proposed.layout(p))
    assert (p.Q-1)>4 # Strict universal rank for every nonzero g.
    primary_checks=holder_checks=cell_checks=0
    for b in (0,1):
        assert all(logical_info(y,b)==b for y in range(-2,3))
        for g in range(-1024,1024):
            bits=initial_bits(g,b,c)
            for row,value in zip(table,bits):
                y=SHIFT+g*p.Q+row['address']
                assert logical_info(y,b)==value,(b,g,row,value)
                primary_checks+=1
            for i,s in enumerate(proposed.SLOTS):
                assert bits[c.row['info',i]]==logical_info(g+s,b)
                assert initial_bits(g-s,b,c)[c.row['info',i]]==logical_info(g,b)
                holder_checks+=2
            for phase in (58,965,3,509,515,1021):
                assert logical_info(SHIFT+g*p.Q+phase,b)==0
            cell_checks+=1
    # Actual schema packing and native-field access; no periodic state assumed.
    coordinates=np.arange(-1024,1024,dtype=np.int64)
    for b in (0,1):
        packed=np.array([initial_bits(int(x),b,c) for x in coordinates],dtype=np.uint8).T
        assert packed.shape==(842,2048)
        assert np.array_equal(c.field(packed,'addr'),(coordinates-SHIFT)%p.Q)
        assert not c.field(packed,'age').any()
        assert all(not packed[r].any() for r,(f,i) in enumerate(c.rows) if f not in ('addr','info'))
        for i,s in enumerate(proposed.SLOTS):
            assert packed[c.row['info',i]].tolist()==[logical_info(int(x)+s,b) for x in coordinates]
    # Deep recursive paths reaching both free-bit bases and fixed native leaves.
    traces=[];maximum=0
    for b in (0,1):
        for leaf in (-2,-1,0,1,2,-35,989):
            expected=logical_info(leaf,b)
            for depth in (16,64,320):
                y=leaf
                for j in range(depth):
                    s=proposed.SLOTS[j%5]
                    if y==s:s=proposed.SLOTS[(j+1)%5]
                    y=(y-s)*p.Q+s
                trace=[];assert logical_info(y,b,trace)==expected
                assert trace[-1]==leaf and len(trace)==depth+1,(b,leaf,depth,len(trace))
                assert all(abs(v)<abs(u) for u,v in zip(trace,trace[1:]))
                maximum=max(maximum,len(trace));traces.append(dict(bit=b,leaf=leaf,depth=depth,trace_length=len(trace),value=expected))
    # Majority correction for at most two current whole-holder replacements.
    majority_cases=0
    for b in (0,1):
        for overwritten in range(32):
            if overwritten.bit_count()>2:continue
            for payload in range(32):
                values=[((payload>>i)&1) if ((overwritten>>i)&1) else b for i in range(5)]
                assert int(sum(values)>=3)==b;majority_cases+=1
    identities=[centre_identity(p,s) for s in proposed.SLOTS]
    period=json.loads((out/'SP30_encoded_certificate.json').read_text())
    assert period['complete_encoded_noiseless_and_all_period_E0_simulation_proved']
    assert period['proposed_candidate_sha256']==c.digest()
    fixture=out/'SP30_intact_memory_finite_checks.json'
    fixture.write_text(json.dumps(dict(context_range=[-1024,1024],bits=[0,1],
        represented_primary_equalities=primary_checks,actual_holder_equalities=holder_checks,
        packed_cell_checks=cell_checks,deep_traces=traces,maximum_trace_length=maximum),indent=2)+'\n')
    result=dict(proposal='SP30',scope='J193 explicit two intact infinite self-encodings and all-time local bit memory under noiseless/global E0 physical history; no positive iid threshold',
        proposed_rule_change=False,additional_rule_change=False,active_G17_modified=False,
        Q=p.Q,U=p.U,width=c.W,colony_origin_translation=SHIFT,central_logical_primary=0,central_virtual_address=94,
        recursive_Info_phases=list(range(92,97)),free_recursive_primaries=list(range(-2,3)),
        remembered_bits=[0,1],observable_radius=2,strict_absolute_rank_for_nonbase_recursion_proved=True,
        two_explicit_infinite_initializers_on_Z_proved=True,full_state_literal_self_encoding_fixed_points_proved=True,
        simultaneous_intact_initialization_all_levels_proved=True,
        all_time_noiseless_local_bit_memory_proved=True,all_time_actual_global_E0_raw_and_computed_bit_memory_proved=True,
        arbitrary_whole_cell_payloads_including_current_row_zero_allowed=True,
        independent_upper_error_histories_used=False,positive_iid_noise_satisfies_global_E0_almost_surely=False,
        higher_error_map_or_general_fault_eroder_or_positive_iid_threshold_proved=False,
        globally_sufficient_smallest_change_proved=False,global_reliability_established=False,
        numerical_whole_CA_trajectory_used=False,represented_primary_equalities=primary_checks,
        actual_holder_equalities=holder_checks,packed_cell_checks=cell_checks,deep_trace_count=len(traces),
        maximum_trace_length=maximum,whole_holder_current_error_majority_cases=majority_cases,
        actual_symbolic_clock_centre_Info_identities=identities,
        finite_checks_supplement_universal_written_rank_encoding_and_time_inductions=True,
        checker_sha256=digest(__file__),written_proof_sha256=digest(ROOT/'Report/proofs/SP30_INTACT_MEMORY.md'),
        proposal_source_sha256=digest(proposed.__file__),proposed_candidate_sha256=c.digest(),proposed_netlist_sha256=c.comp.digest,
        full_generated_source_sha256=hashlib.sha256(proposed.generated_source(p).encode()).hexdigest(),fixture_sha256=digest(fixture),
        source_dependencies_sha256={name:digest(ROOT/name) for name in ('gacsca/machine.py','gacsca/netlist.py','gacsca/rule_g.py',
            'Report/proofs/check_commit_reset448_incorporation.py','Report/proofs/check_buffered448_command.py','Report/proofs/check_g17_schedule.py')},
        receipt_dependencies_sha256={name:digest(out/name) for name in ('SP30_encoded_certificate.json','SP30_native_certificate.json',
            'SP30_symbolic_schedule.json','SP30_front_certificate.json')},seconds=time.monotonic()-started)
    (out/'SP30_intact_memory_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('represented_primary_equalities','maximum_trace_length',
        'all_time_noiseless_local_bit_memory_proved','all_time_actual_global_E0_raw_and_computed_bit_memory_proved',
        'global_reliability_established','seconds')}),flush=True)


if __name__=='__main__':main()
