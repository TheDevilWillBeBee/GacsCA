#!/usr/bin/env python3
"""Exact prepared-input GMW3 prefix and wrong-Info commit certificate.

Halt time and output completion are separate assertions. No intact hierarchy,
gathering implementation, universal beta identity, or Gray/iid claim follows.
"""
from pathlib import Path
from collections import Counter
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
import gray_moving_word_v3 as k


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fixtures(listing):
    hlt=[r for r in listing['instructions'] if r['opcode']=='HLT'][-1]['address']
    p=k.Packet(p=1,pc=hlt)
    return dict(canonical={j:k.Cell(addr=j%k.Q) for j in range(-5,6)},
        normalized_dense_HLT={j:k.Cell(addr=j%k.Q,age=112*k.Q+1,
            heads=(k.pack(p),)*5) for j in range(-5,6)})


def physical_prefix(beta,cells):
    """All five actual output-holder transitions at each execution update.

    The quiet coherent-copy closure proves the remaining sites. The physical
    tape is preloaded; its provenance from three gathers is not assumed.
    """
    tape=k.input_tape(cells);out={};scratch={};p=k.initial_packet()
    position=k.HEAD_ADDRESS;age=112*k.Q+1;history=[];checks=0
    for tick in range(65535):
        newage=age+1;fast=bool(newage%2)
        stride=k.travel_stride(p,position,fast) if p.move in (1,2) else 0
        address=position+(stride if p.move==1 else -stride if p.move==2 else 0)
        assert 0<=address<k.Q and 112*k.Q+1<newage<=120*k.Q
        before=k.pack(p)
        nextp,ow,sw=k.base.step_packet(p,address,tape.get(address,0),
            out.get(address,0),scratch.get(address,0),beta[address],beta)
        packednext=k.pack(nextp)
        def word(x,atage,headword,headpos,new=False):
            def value(bank,y,write):
                return write if new and y==address and write is not None else bank.get(y,0)
            return k.Cell(addr=x%k.Q,age=atage,
                heads=tuple(headword if x+s==headpos else 0 for s in k.SLOTS),
                mem=tuple(tape.get(x+s,0) for s in k.SLOTS),
                out=tuple(value(out,x+s,ow) for s in k.SLOTS),
                scratch=tuple(value(scratch,x+s,sw) for s in k.SLOTS),
                program=tuple(beta[(x+s)%k.Q] for s in k.SLOTS))
        # One common old field assignment, never a different initialization
        # chosen for each holder. All15 sites cover the five radius5 cones.
        old={x:word(x,age,before,position) for x in range(address-7,address+8)}
        for s in k.SLOTS:
            x=address-s
            actual=k.local_transition({j:old[x+j] for j in range(-5,6)},beta)
            expected=word(x,newage,packednext,address,True)
            assert actual==expected,(tick,x)
            checks+=1
        history.append((address,before,packednext,-1 if ow is None else ow,
            -1 if sw is None else sw,age,newage,stride))
        if ow is not None:out[address]=ow
        if sw is not None:scratch[address]=sw
        p=nextp;position=address;age=newage
        if (tick+1)%8192==0:print('physical prefix',tick+1,flush=True)
    assert age==120*k.Q and p.mode not in (k.HALT,k.ERROR)
    expectedbits=k.cell_bits(k.local_transition(cells,beta))
    actualbits=[out.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_BITS)]
    assert expectedbits[66]==1 and actualbits[66]==0
    # Rest retains unfinished Out. The unchanged Age0 commit then reads it
    # before resetting Out/Scratch; this is a wrong represented Info field.
    badprimary=k.PRIMARY_START+66
    commits=[]
    for q,s in enumerate(k.SLOTS):
        x=badprimary-s
        def frame(atage):
            return {j:word(x+j,atage,k.pack(p),position) for j in range(-5,6)}
        rest=k.local_transition(frame(120*k.Q),beta)
        assert rest.out[q]==0
        committed=k.local_transition(frame(k.U-1),beta)
        assert committed.info[q]==0 and committed.out[q]==0
        commits.append(dict(holder=x,slot=q,committed_Info=committed.info[q]))
    trace=dict(address=np.array([h[0] for h in history],np.uint16),
        before=np.array([list(h[1].to_bytes(48,'little')) for h in history],np.uint8),
        after=np.array([list(h[2].to_bytes(48,'little')) for h in history],np.uint8),
        out_writes=np.array([h[3] for h in history],np.int8),
        scratch_writes=np.array([h[4] for h in history],np.int8),
        old_age=np.array([h[5] for h in history],np.uint32),
        new_age=np.array([h[6] for h in history],np.uint32),
        stride=np.array([h[7] for h in history],np.uint8),
        output=np.array(actualbits,np.uint8),expected=np.array(expectedbits,np.uint8))
    return trace,dict(actual_physical_updates=65535,all_five_holder_equations_checked=checks,
        final_mode=p.mode,final_pc=p.pc,different_field_bits=np.flatnonzero(
            np.array(actualbits)!=np.array(expectedbits)).tolist(),wrong_represented_bit=66,
        wrong_represented_primary=badprimary,expected_Info=1,committed_Info=0,
        five_boundary_commits=commits)


def main():
    started=time.monotonic();directory=ROOT/'figs/gray_counterexamples'
    beta=tuple(np.unpackbits(np.fromfile(directory/'GMW3_full_proposed_beta.bin',np.uint8),bitorder='little').tolist())
    listing=json.loads((directory/'GMW3_full_proposed_listing.json').read_text())
    data=fixtures(listing);assets={};results=[]
    for name,cells in data.items():
        expected=k.cell_bits(k.local_transition(cells,beta))
        output,n,p,history=k.execute(beta,k.input_tape(cells),65535,True)
        actual=[output.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_BITS)]
        diffs=[i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b]
        assert n==65535 and p.mode not in (k.HALT,k.ERROR)
        if name=='canonical':assert not diffs
        else:assert 66 in diffs and expected[66]==1 and actual[66]==0
        complete,halt,final,full=k.execute(beta,k.input_tape(cells),400000,True)
        assert final.mode==k.HALT and [complete.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_BITS)]==expected
        costs=Counter()
        for address,old,*_ in full:
            costs['instruction_updates' if old.mode==k.RUN else
                'operand_travel_updates' if address!=old.start+old.index else
                'mutable_column_updates']+=1
        assert sum(costs.values())==halt
        assets[name+'_input_bits']=np.array([k.cell_bits(cells[j]) for j in range(-5,6)],np.uint8)
        assets[name+'_expected']=np.array(expected,np.uint8)
        assets[name+'_truncated']=np.array(actual,np.uint8)
        results.append(dict(fixture=name,uninterrupted_halt_ticks=halt,**dict(costs),
            actual_active_update_budget=65535,halted_at_deadline=False,
            all_decoded_outputs_correct_at_deadline=not diffs,different_field_bits=diffs,
            final_deadline_mode=p.mode,final_deadline_pc=p.pc,
            post_gate_uninterrupted_runner_is_actual_physical_execution=False))
        print(name,results[-1],flush=True)
    trace,physical=physical_prefix(beta,data['normalized_dense_HLT'])
    assets.update({'physical_'+name:value for name,value in trace.items()})
    asset=directory/'GMW3_prepared_deadline_traces.npz';np.savez_compressed(asset,**assets)
    proof=Path(__file__).with_name('GMW3_FAST_TRANSPORT.md')
    result=dict(name='GMW3 prepared physical deadline and wrong represented-field commit',Q=k.Q,U=k.U,
        lambda_original=24,c_original=104,rest_period=2,frame_bits=k.FRAME_BITS,
        fixtures=results,physical_prefix=physical,
        canonical_unfinished_halt_does_not_imply_wrong_decoded_output=True,
        dense_prepared_output_deadline_failure_proved=True,error_history=[],
        lower_native_geometry_and_flags_canonical=True,
        input_tape_preloaded=True,upper_context_has_normalized_dense_HLT_heads=True,
        initial_context_is_intact_recursive_hierarchy=False,
        universal_full_beta_identity_proved=False,universal_runtime_bound_proved=False,
        physical_gather_early_flags_special_write_whole_period_completed=False,
        Gray_faithful=False,iid_failure_proved=False,global_reliability_established=False,
        active_rule_modified=False,shorter_U_used=False,
        kernel_sha256=digest(k.__file__),base_GMW2_kernel_sha256=digest(k.base.__file__),
        checker_sha256=digest(__file__),proof_sha256=digest(proof),asset_sha256=digest(asset),
        beta_sha256=digest(directory/'GMW3_full_proposed_beta.bin'),
        listing_sha256=digest(directory/'GMW3_full_proposed_listing.json'),
        receipt_dependencies_sha256={'GMW3_full_proposed_certificate.json':digest(directory/'GMW3_full_proposed_certificate.json')},
        wall_seconds=time.monotonic()-started)
    (directory/'GMW3_deadline_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
