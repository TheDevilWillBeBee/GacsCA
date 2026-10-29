"""Exact reductions for a conditional SP30 quiet-frame protocol theorem.

No actual damaged-history recurrence or iid conclusion is certified here.
The written proof supplies the physical induction from its native premises.
"""
from collections import Counter
from pathlib import Path
from types import FunctionType
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'Report/proofs'))
from gacsca import rule_g
import proposed_sparse_signal_reservation1024 as proposed
import check_short_force1024_GF_bank_closure as bank


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(write=True):
    started=time.monotonic();p=proposed.parameters();out=ROOT/'figs/robustness'
    candidate=proposed.load_artifact();listing_path=out/'SP30_program_listing.json'
    listing=json.loads(listing_path.read_text());comp=candidate.comp
    assert (p.Q,p.U,p.PL,p.E0,p.T_wf,p.IW,p.PW)==(1024,475136,928,25984,278401,26,12)
    retained=json.loads((out/'SP30_symbolic_schedule.json').read_text())
    assert retained['proposed_candidate_sha256']==candidate.digest()
    assert retained['proposed_netlist_sha256']==comp.digest
    assert retained['listing_sha256']==sha(listing_path)
    assert (retained['key_equalities'],retained['final_hold_equalities'])==(22,842)
    assert retained['global_reliability_established'] is False

    # A structural dependency test, not a numerical instruction sample.
    deps=[0,0]+[(1<<key[1]) if key[0]=='I' else 0 for key in comp.inputs]
    for _,a,b in comp.gates:deps.append(deps[a]|deps[b])
    assert len(deps)==comp.n_nodes
    native=[('y',field,bit) for field,width in
            (('addr',p.k),('age',p.m),('f1',1),('wf1',1)) for bit in range(width)]
    assert len(native)==31 and all(deps[comp.outputs[key]]==0 for key in native)

    # Repeat the schedule's definedness argument after discarding all Match
    # registers except front0's arbitrary26-bit word. Undefined registers
    # cannot be read; physical values in them are therefore irrelevant.
    sources=proposed.source_names(p);regs=[[False]*p.L for _ in range(p.fronts)]
    scratch=set();reads=Counter();post=Counter();last_page=-1;match_reset=False
    replayed=0;issues=[]
    for row in listing:
        seq,page,tick,front,cell,op,kind,a,b,dest,_=row
        assert page>=last_page
        if page>p.MP and not match_reset:
            regs=[[False]*p.L for _ in range(p.fronts)]
            for bit in range(p.IW):regs[0][p.k+bit]=True
            match_reset=True
        last_page=page
        assert page!=p.MP and 0<=front<p.fronts
        expected=p.lo-p.H+(tick if page%2==0 else p.PL-1-tick)+front*p.delta
        assert cell==expected and p.lo<=cell<p.hi
        word=op|(kind<<2)|(a<<4)|(b<<(4+p.SB))|(dest<<(4+2*p.SB))
        assert int(candidate.rom[cell,page+(front<<p.logNP)])==word
        for code in (a,b):
            family,index=sources[code];reads[family]+=1
            if page>p.MP:post[family]+=1
            if family=='reg':assert regs[front][index],('undefined',row,index)
            elif family=='scr':assert (cell,index) in scratch,('undefined scratch',row,index)
            else:assert family in ('info','ln','const')
        if kind==rule_g.K_REG:regs[front][dest]=True
        elif kind==rule_g.K_SCR:scratch.add((cell,dest))
        elif kind==rule_g.K_HOLD:
            issues.append(dict(phase=cell,input_issue=p.E0+page*p.PL+tick,front=front))
        replayed+=1
    assert match_reset and replayed==131238
    assert sum(reads.values())==262476

    # Exact physical support of every comb register update and every
    # represented operand. No modulo wrap enters a complete frame.
    visits=turns=0;minimum=p.Q;maximum=0;previous=None
    for page in range(p.NP):
        for tick in range(p.PL):
            step=tick if page%2==0 else p.PL-1-tick
            centers=[p.lo-p.H+step+f*p.delta for f in range(p.fronts)]
            assert all(b-a==5 for a,b in zip(centers,centers[1:]))
            assert centers[0]-3>=1 and centers[-1]+3<p.Q
            minimum=min(minimum,centers[0]-3);maximum=max(maximum,centers[-1]+3)
            if previous is not None:
                move=0 if tick==0 else (-1 if page%2==0 else 1)
                assert [x+move for x in centers]==previous
            if tick==0 and page:turns+=p.fronts
            previous=centers;visits+=p.fronts
    assert (minimum,maximum,visits,turns)==(35,988,1781760,1915)
    normal={r['address'] for r in proposed.dependency_table(p)}
    assert len(normal)==842 and normal.isdisjoint({3,509,515,1021})
    assert all(1<=a-2 and a+2<p.Q for a in normal|{p.lo,p.hi-1,3,p.Q-3})
    operand_checks=0
    for row in listing:
        for code in row[7:9]:
            family,index=sources[code]
            if family in ('info','ln'):
                assert row[4] in normal
                if family=='ln':
                    r=next(r for r in proposed.dependency_table(p) if r['address']==row[4])
                    assert index<len(r['offsets'])
                operand_checks+=1
    # Native quiet-template/refinement equations are checked with common
    # clock symbolic; full history/header premise supply remains explicit.
    quiet=FunctionType(bank.quiet.__code__,dict(bank.__dict__,proposed=proposed),'quiet')
    quiet_records=[quiet(p,0,6),quiet(p,-17,-11)]
    guards=[]
    for issue in issues:
        if issue['phase'] in (*range(59,69),88,p.lo,p.hi-1):
            guards.append(issue)
            assert issue['input_issue']+2<p.T_wf
    assert len(guards)==13
    mail_path=out/'unregistered_quiet_mail/receipt.json';mail=json.loads(mail_path.read_text())
    assert mail['universal_symbolic_copy_output_identities']==15
    assert mail['quiet_gate_boundary_checks']==28
    assert len(mail['capture_timing_records'])==111
    assert not mail['actual_global_quiet_template_or_controller_lift_or_regeneration_proved']
    proof=ROOT/'Report/proofs/unregistered_terminal/SP30_QUIET_FRAME_PROTOCOL.md'
    source_dependencies=('gacsca/rule.py','gacsca/rule_g.py','gacsca/netlist.py',
        'Report/proofs/proposed_sparse_signal_reservation1024.py',
        'Report/proofs/check_sparse_backward_fitted448_schedule.py',
        'Report/proofs/check_signal_reservation1024_schedule.py',
        'Report/proofs/check_short_force1024_GF_bank_closure.py',
        'Report/proofs/unregistered_terminal/probe_sp30_quiet_mail_wiring.py')
    receipt_dependencies=('SP30_symbolic_schedule.json','SP30_front_certificate.json',
        'SP30_native_certificate.json','SP30_encoded_certificate.json',
        'SP30_program_build.json','SP30_program.npz','SP30_program_listing.json',
        'SP30_GF_bank_closure_certificate.json','unregistered_quiet_mail/receipt.json')
    result=dict(name='SP30 conditional quiet-frame physical protocol',
        checker_sha256=sha(__file__),proof_sha256=sha(proof),Q=p.Q,U=p.U,
        candidate_sha256=candidate.digest(),netlist_sha256=comp.digest,
        source_dependencies_sha256={name:sha(ROOT/name) for name in source_dependencies},
        receipt_dependencies_sha256={name:sha(out/name) for name in receipt_dependencies},
        instruction_word_bits=p.IW,Match_key_bits=p.k+p.PW,
        native_outputs_structurally_instruction_independent=len(native),
        listing_instructions_replayed=replayed,operand_definedness_reads=sum(reads.values()),
        post_Match_read_families=dict(post),all_other_Match_registers_discarded_before_definedness=True,
        comb_holder_visits=visits,turn_register_interfaces=turns,
        compact_register_source_interval=[minimum,maximum],data_operand_checks=operand_checks,
        complete_frame_SF_holder_interval=[1,1023],native_footprint_interval=[-36,1060],
        protected_full_left_frame_native_clearance=540,
        quiet_native_records=quiet_records,early_protected_issue_records=guards,
        conditional_Mail_Info_and_complete_frame_execution_proved=True,
        complete_frame_native_geometry_clock_keep_and_fresh_reset_required=True,
        protected_late_frame_claim_requires_whole_remaining_native_footprint=True,
        actual_all_period_native_premise_supply_or_recurrence_proved=False,
        permanent_defect_or_general_eroder_or_higher_or_iid_proved=False,
        active_rule_or_frozen_SP30_modified=False,global_reliability_established=False,
        retained_draft_assets_sha256={name:sha(out/'unregistered_quiet_frame'/name) for name in
            ('draft_01_proof.md.txt','draft_01_checker.py.txt','draft_01_certificate.json','draft_01_run.log')},
        elapsed_seconds=time.monotonic()-started)
    if write:
        dest=out/'unregistered_quiet_frame';dest.mkdir(exist_ok=True)
        (dest/'certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('instruction_word_bits','Match_key_bits',
        'listing_instructions_replayed','operand_definedness_reads','comb_holder_visits',
        'conditional_Mail_Info_and_complete_frame_execution_proved',
        'actual_all_period_native_premise_supply_or_recurrence_proved',
        'global_reliability_established','elapsed_seconds')}),flush=True)
    return result


if __name__=='__main__':main()
