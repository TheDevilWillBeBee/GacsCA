#!/usr/bin/env python3
"""J139: arbitrary-work synchronized layout after J137 native recovery.

Literal full-rule commit identities with free raw work/Info/I, not a
claim to restore original data or equate auxiliary flags to upper flags.
The earlier complete E28 shape assertion is withdrawn; original receipt
and checker retained. No trajectories sampled.
"""
from pathlib import Path
from types import FunctionType
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,const_word
import proposed_sparse_distant_epoch1024 as proposed
import check_commit_reset448_incorporation as reset
from check_buffered448_command import forwarded_hold


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def literal_interfaces(p):
    class SharedNet(Net):
        reader=0
        def input(self,key):
            if key[0]=='x':
                _,off,field,bit=key
                key=('x',self.reader+off,field,bit)
            return super().input(key)
    n=SharedNet();reset_count=0;outputs=[]
    for slot in proposed.SLOTS:
        n.outputs={}
        # One primary is placed at absolute coordinate0. Its five
        # physical holders use relative native phases lo-slot. The
        # controller cut is justified by J137 at the actual commit.
        n.reader=-slot
        phase=p.lo-slot
        def controller(net,cells,*args,**kwargs):
            return dict(addr=const_word(phase,p.k),age_now=const_word(p.age_code(p.U-1),p.m),
                age=const_word(0,p.m),f1=0,f2=net.input(('proof','free_F2')))
        fn=proposed.legacy.full_net
        namespace=dict(proposed.legacy.__dict__,schema=proposed.schema,width=proposed.width,
            previous=proposed.previous,dependency_table=proposed.dependency_table,
            service_build=proposed.service_build,generated_source=proposed.generated_source,
            proposed_build=lambda:(controller,'J139 native commit proof cut'))
        FunctionType(fn.__code__,namespace,fn.__name__,fn.__defaults__)(p,net_class=lambda:n)
        n.reader=0
        zero_fields=set(reset.RESET_FIELDS)|set(proposed.COMMIT_RESET_FIELDS)|{'wf1'}
        assert zero_fields=={f for f,_ in proposed.schema(p)}-{'addr','age','f1','info'}
        for field,bits in proposed.schema(p):
            if field in zero_fields:
                for bit in range(bits):
                    assert n.outputs['y',field,bit]==0,(slot,field,bit)
                    reset_count+=1
        assert [n.outputs['y','addr',b] for b in range(p.k)]==const_word(phase,p.k)
        assert all(n.outputs['y','age',b]==0 for b in range(p.m))
        assert n.outputs['y','f1',0]==0
        outputs.append(n.outputs['y','info',slot+2])
    expected=forwarded_hold(n,p,0,0)
    values=reset.normalized(n)
    assert all(values[node]==values[expected] for node in outputs)
    assert reset_count==5*807
    return reset_count,len(outputs),hashlib.sha256(proposed.generated_source(p).encode()).hexdigest()


def main():
    started=time.monotonic();p=proposed.parameters();out=ROOT/'figs/robustness'
    native=json.loads((out/'SP28_epoch_halfline_certificate.json').read_text())
    assert native['all_period_three_colony_native_halfline_expansion_proved']
    zeros,copies,source_sha=literal_interfaces(p)
    primaries=set(proposed.layout(p).tolist())|{p.lo,p.hi-1}
    assert len(primaries)==844 and min(primaries)-2>=0 and max(primaries)+2<p.Q
    masks=0
    for phase in range(p.Q):
        for slot in proposed.SLOTS:
            absolute=phase+slot
            modded=absolute%p.Q
            allowed=modded in primaries
            assert allowed==(p.lo<=modded<p.lo+proposed.width(p)+1 or modded==p.hi-1)
            if allowed:assert 0<=absolute<p.Q
            masks+=1
    boundary=p.U-p.T_wf
    assert boundary==196735>native['three_colonies_all_Flag1_quiet_state']
    normal={};index=0
    for field,bits in proposed.schema(p):
        if field in ('f1','f2'):normal[field]=int(proposed.layout(p)[index])
        index+=bits
    pairs=[dict(upper_field=f,normal_primary=normal[f],auxiliary_primary=a)
           for f,a in (('f2',p.lo),('f1',p.hi-1))]
    assert [(x['normal_primary'],x['auxiliary_primary']) for x in pairs]==[(89,58),(88,965)]
    for pair in pairs:
        assert set(range(pair['normal_primary']-2,pair['normal_primary']+3)).isdisjoint(
            range(pair['auxiliary_primary']-2,pair['auxiliary_primary']+3))
    receipt=dict(proposal='SP28',proposed_rule_change=True,active_G17_modified=False,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        full_generated_source_sha256=source_sha,
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        normalized_term_helper_sha256=digest(Path(reset.__file__)),
        forwarded_Hold_helper_sha256=digest(ROOT/'Report/proofs/check_buffered448_command.py'),
        native_halfline_receipt_sha256=digest(out/'SP28_epoch_halfline_certificate.json'),
        proposed_netlist_sha256=native['proposed_netlist_sha256'],
        Q=p.Q,U=p.U,width=proposed.width(p),T_wf=p.T_wf,
        literal_commit_zero_bit_identities_across_five_free_work_readers=zeros,
        arbitrary_forwarded_Hold_shared_primary_copy_identities=copies,
        Info_mask_phase_slot_checks=masks,allowed_Info_primaries=len(primaries),
        allowed_Info_copy_slots=5*len(primaries),unused_Info_copy_slots_zero=5*(p.Q-len(primaries)),
        first_commit_boundary_state_relative_to_initial_T_wf=boundary,
        later_commit_boundary_states='U-T_wf+k*U, k>=0',
        correctly_native_canonical_halfline_left_boundary='s-3*Q*(k+1)',
        initial_aligned_native_GF_Age_halfline_at_T_wf_required=True,
        actual_global_E0_required=True,initial_work_and_Info_and_flags_and_I_arbitrary=True,
        no_future_boundary_or_work_command_prescribed=True,
        complete_computed_boundary_encoding_of_some_upper_halfline_proved=False,
        full_boundary_E28_identity_claim_withdrawn=True,
        fivefold_computed_boundary_layout_with_independent_auxiliary_flags_proved=True,
        auxiliary_flag_equality_with_represented_upper_flags_proved=False,
        auxiliary_flag_normal_primary_pairs=pairs,
        normal_and_auxiliary_Hold_votes_use_disjoint_free_inputs=True,
        withdrawn_original_checker_sha256=digest(out/'SP28_withdrawn_canonicalization_checker.py'),
        withdrawn_original_receipt_sha256=digest(out/'SP28_withdrawn_canonicalization_certificate.json'),
        upper_halfline_values_determined_by_arbitrary_forwarded_Hold=True,
        original_simulation_data_recovery_or_clean_upper_evolution_proved=False,
        full_upper_error_map_or_iid_threshold_established=False,global_reliability_established=False,
        seconds=time.monotonic()-started,
        scope='J139 recovered native halfline commit has synchronized fivefold layout with two independent auxiliary flags; complete E28 shape withdrawn; no alias equality/original data/confinement/iid theorem')
    (out/'SP28_canonicalization_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(zero_bits=zeros,copy_identities=copies,masks=masks,boundary=boundary,
        original_data_recovered=False,seconds=receipt['seconds'])),flush=True)


if __name__=='__main__':main()
