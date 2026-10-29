#!/usr/bin/env python3
"""SP26 complete-boundary E0 proof interfaces, not an iid theorem.

The physical induction is in ROBUSTNESS J130. This checker verifies
literal commit interfaces, native/copy-controller provenance and the
parameter-specific quieting reserve. It does not sample trajectories.
"""
from pathlib import Path
from types import FunctionType
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import proposed_sparse_distant_short1024 as proposed
import check_commit_reset448_incorporation as reset
from gacsca.netlist import Net,const_word,w_add_const_mod,w_in_range,w_eq_const


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def commit_interfaces(p):
    observed={}
    def controller(n,cells,*args,**kwargs):
        # The actual native theorem makes this equality true under E0.
        # Preserve the full refined raw GF node, not a replacement integer.
        observed['GF']=cells[0]['addr']
        return dict(addr=cells[0]['addr'],age_now=const_word(p.age_code(p.U-1),p.m),
                    age=const_word(0,p.m),f1=n.input(('proof','F1')),f2=n.input(('proof','F2')))
    ns=dict(proposed.prior.__dict__,schema=proposed.schema,width=proposed.width,
        dependency_table=proposed.dependency_table,service_build=proposed.service_build,
        generated_source=proposed.generated_source,proposed_build=lambda:(controller,'proof interface only'))
    fn=proposed.prior.full_net
    n,_=FunctionType(fn.__code__,ns,fn.__name__,fn.__defaults__)(p)
    zero_fields=set(reset.RESET_FIELDS)|set(proposed.COMMIT_RESET_FIELDS)|{'wf1'}
    zeros=0
    for field,bits in proposed.schema(p):
        if field in zero_fields:
            for b in range(bits):
                assert n.outputs['y',field,b]==0,(field,b)
                zeros+=1
    assert zeros==proposed.width(p)-p.k-p.m-1-5==807
    # All state bits apart from native GF/Age/F1 and Info are reset.
    assert zero_fields=={f for f,_ in proposed.schema(p)}-{'addr','age','f1','info'}
    expected={}
    for slot in proposed.SLOTS:
        address=w_add_const_mod(n,observed['GF'],slot%p.Q,p.Q)
        allowed=n.OR(w_in_range(n,address,p.lo,p.lo+proposed.width(p)+1),w_eq_const(n,address,p.hi-1))
        expected[slot]=n.AND(allowed,reset.forwarded_hold(n,p,0,slot))
    values=reset.normalized(n)
    for slot,node in expected.items():assert values[n.outputs['y','info',slot+2]]==values[node],slot
    return zeros,len(expected)


def arithmetic(p):
    primaries=set(proposed.layout(p).tolist())|{p.lo,p.hi-1}
    assert primaries==set(range(58,901))|{965} and len(primaries)==844
    assert min(primaries)-2>=0 and max(primaries)+2<p.Q
    allowed=0
    for phase in range(p.Q):
        for slot in proposed.SLOTS:
            if (phase+slot)%p.Q in primaries:
                assert 0<=phase+slot<p.Q
                allowed+=1
    assert allowed==len(primaries)*5==4220
    # J112's source-free contraction uses the same actual maintenance:
    # gain >=2t-2ceil(t/9), once the last two GF positions are quiet.
    quiet=next(t for t in range(p.Q+1) if 2*t-2*((t+8)//9)>=p.Q-2)
    assert quiet==575 and 2*quiet-2*((quiet+8)//9)==1022
    closed=p.T_wf+2*p.Q+1
    deadline=closed+1+quiet
    assert (closed,deadline)==(278594,279170)
    assert deadline<p.E0+p.NP*p.PL<p.U-1
    return dict(allowed_Info_primaries=len(primaries),Info_phase_slot_checks=p.Q*5,
        allowed_Info_copy_slots=allowed,unused_Info_copy_slots_zero=p.Q*5-allowed,
        computed_WF1_closed_clock=closed,last_two_computed_Flag1_quiet_clock=closed+1,
        source_free_Flag1_contraction_updates=quiet,all_computed_Flag1_quiet_clock=deadline,
        evaluation_end_input_clock=p.E0+p.NP*p.PL,commit_input_clock=p.U-1)


def main():
    started=time.monotonic();out=ROOT/'figs/robustness'
    candidate=proposed.load_artifact();p=candidate.p
    build=json.loads((out/'SP26_program_build.json').read_text())
    programme=json.loads((out/'SP26_symbolic_schedule.json').read_text())
    native=json.loads((out/'SP26_native_certificate.json').read_text())
    assert candidate.digest()==build['proposed_candidate_sha256']==programme['proposed_candidate_sha256']
    assert candidate.comp.digest==native['proposed_netlist_sha256']==proposed.cached(p)[1].digest
    assert native['all_time_computed_GF_Age_under_E0_plus_real1_proved']
    assert programme['history_ranks_checked']==64 and programme['final_hold_equalities']==842
    assert max(programme['latest_capture_input_ages'])<p.E0<p.T_wf
    assert max(programme['early_flag_store_ages'].values())<min(p.courier_ticks()[1:])
    zero,info=commit_interfaces(p)
    # Pin the exact shared generic copy/update equations and NF1 rule.
    source=proposed.generated_source(p)
    for line in (
        "    wipe = n.AND(f1_new, n.NOT(w_eq(n, addr_now, c['addr'])))\n",
        "    keep = n.NOT(wipe)\n"):
        assert source.count(line)==1
    assert source.index('    native_refined = distant_refinement(n, cell, p)')<source.index('    c = cell[0]')
    dependencies={name:digest(out/file) for name,file in (
        ('build_receipt_sha256','SP26_program_build.json'),('programme_receipt_sha256','SP26_symbolic_schedule.json'),
        ('native_receipt_sha256','SP26_native_certificate.json'),('front_receipt_sha256','SP26_front_certificate.json'))}
    result=dict(proposal='SP26',proposed_rule_change=True,active_G17_modified=False,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        Q=p.Q,U=p.U,width=candidate.W,radius=37,history_ranks=64,
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),base_rule_source_sha256=digest(ROOT/'gacsca/rule_g.py'),
        actual_maintenance_source_sha256=hashlib.sha256(proposed.proposed_build()[1].encode()).hexdigest(),
        full_generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        commit_helper_sha256=digest(Path(reset.__file__)),transport_checker_sha256=digest(ROOT/'Report/proofs/check_fast_mail_proposal.py'),
        Flag1_contraction_helper_sha256=digest(ROOT/'Report/proofs/check_buffered448_period_barrier.py'),
        **dependencies,**arithmetic(p),literal_commit_zero_bits=zero,literal_forwarded_Hold_Info_mask_identities=info,
        distant_refinement_before_copy_keep_controller=True,copy_keep_identically_one_under_global_canonical_native_induction=True,
        abstract_execution_lifted_to_physical_complete_encodings_under_E0=False,
        complete_encoded_noiseless_and_all_period_E0_simulation_proved=False,
        full_boundary_encoding_identity_before_current_overwrites=False,raw_boundary_five_copy_decoder_exact_under_current_E0=False,
        initial_complete_boundary_encoding_required=True,errors_restricted_to_actual_E0=True,
        component_count_or_expiry_lemma_needed_for_this_encoded_E0_proof=False,
        arbitrary_damaged_colony_restoration_proved=False,real1_complete_data_map_proved=False,
        higher_error_map_or_iid_threshold_established=False,global_reliability_established=False,
        physical_encoding_claim_withdrawn=True,physical_gather_premise_refuted=True,
        withdrawn_original_checker_file='SP26_withdrawn_encoded_checker.py',
        withdrawn_original_checker_sha256=digest(out/'SP26_withdrawn_encoded_checker.py'),
        withdrawn_original_receipt_file='SP26_withdrawn_encoded_certificate.json',
        withdrawn_original_receipt_sha256=digest(out/'SP26_withdrawn_encoded_certificate.json'),
        seconds=time.monotonic()-started,proof='ROBUSTNESS J130 local interfaces only; physical lift withdrawn by J134',
        scope='local commit/reset interfaces only; physical encoding proof withdrawn by J134 due to distance12 fast mail/distance37 gathers')
    (out/'SP26_encoded_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(commit_zero_bits=zero,Info_identities=info,Flag1_quiet=result['all_computed_Flag1_quiet_clock'],
                         encoded_E0=False,physical_proof_withdrawn=True,iid=False,seconds=result['seconds'])),flush=True)


if __name__=='__main__':main()
