#!/usr/bin/env python3
"""Retained finite full-own-programme comparisons/runtime; proof scope explicit."""
from pathlib import Path
from dataclasses import replace
import hashlib,json,random,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
import gray_moving_word_v2 as k
import build_gray_moving_word_v2 as builder


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fixture(packet=None,commonage=0,memory_seed=0,head_position=0):
    rng=random.Random(memory_seed)
    logical={y:dict(mem=rng.randrange(2048),out=rng.randrange(2),info=rng.randrange(2),
        scratch=rng.randrange(2),program=rng.randrange(2)) for y in range(-7,8)} if memory_seed else {}
    packet=k.ZERO if packet is None else packet
    return {j:k.Cell(addr=j%k.Q,age=commonage,
        heads=tuple(k.pack(packet) if j+s==head_position else 0 for s in k.SLOTS),
        **{name:tuple(logical.get(j+s,{}).get(name,0) for s in k.SLOTS)
           for name in ('mem','out','info','scratch','program')}) for j in range(-5,6)}


def retain_failure(name,cells,actual,expected,code,listing,labels,n,last):
    directory=ROOT/'figs/gray_counterexamples'
    serial=1
    while (directory/('GMW2_semantic_failure_%02d.json'%serial)).exists():serial+=1
    stem='GMW2_semantic_failure_%02d'%serial
    asset=directory/(stem+'.npz')
    np.savez_compressed(asset,input_bits=np.array([k.cell_bits(cells[j]) for j in range(-5,6)],np.uint8),
        actual=np.array(actual,np.uint8),expected=np.array(expected,np.uint8),beta=np.array(code,np.uint8))
    sources={}
    for path in (Path(k.__file__),Path(builder.__file__),Path(__file__)):
        target=directory/(stem+'_'+path.name+'.txt');target.write_bytes(path.read_bytes());sources[target.name]=digest(target)
    record=dict(name=name,status='retained failed implementation comparison',Q=k.Q,U=k.U,
        code_capacity=k.CODE_CAPACITY,programme_bits=len(code),measured_ticks=n,last_mode=last.mode,
        last_pc=last.pc,different_field_bits=[i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b],
        asset_sha256=digest(asset),source_snapshots_sha256=sources,active_rule_modified=False,
        full_own_programme_equivalence_proved=False,Gray_or_iid_failure_proved=False)
    (directory/(stem+'.json')).write_text(json.dumps(record,indent=2)+'\n')
    raise AssertionError(stem+' '+name+' '+str(record['different_field_bits'][:16]))


def physical_prefix(beta,tape,limit=65535):
    """Actual local-rule replay at every active tick, rotating five holders."""
    p=k.initial_packet();position=k.HEAD_ADDRESS;out={};scratch={};age=112*k.Q+1
    before=[];after=[];addresses=[];outwrites=[];scratchwrites=[];counts=[0]*5
    def frame(x):
        return {j:k.Cell(addr=(x+j)%k.Q,age=age,
            heads=tuple(k.pack(p) if x+j+s==position else 0 for s in k.SLOTS),
            mem=tuple(tape.get(x+j+s,0) for s in k.SLOTS),
            out=tuple(out.get(x+j+s,0) for s in k.SLOTS),
            scratch=tuple(scratch.get(x+j+s,0) for s in k.SLOTS),
            program=tuple(beta[(x+j+s)%k.Q] for s in k.SLOTS)) for j in range(-5,6)}
    for tick in range(limit):
        nextposition=position+(1 if p.move==1 else -1 if p.move==2 else 0)
        pp,ow,sw=k.step_packet(p,nextposition,tape.get(nextposition,0),out.get(nextposition,0),
                scratch.get(nextposition,0),beta[nextposition],beta)
        holder=tick%5;x=nextposition-k.SLOTS[holder]
        physical=k.local_transition(frame(x),beta)
        newout=dict(out);newscratch=dict(scratch)
        if ow is not None:newout[nextposition]=ow
        if sw is not None:newscratch[nextposition]=sw
        assert physical.heads==tuple(k.pack(pp) if x+s==nextposition else 0 for s in k.SLOTS)
        assert physical.mem==tuple(tape.get(x+s,0) for s in k.SLOTS)
        assert physical.out==tuple(newout.get(x+s,0) for s in k.SLOTS)
        assert physical.scratch==tuple(newscratch.get(x+s,0) for s in k.SLOTS)
        assert physical.program==tuple(beta[(x+s)%k.Q] for s in k.SLOTS)
        assert physical.info==(0,)*5 and (physical.addr,physical.age,physical.f1,physical.f2)==(x%k.Q,age+1,0,0)
        before.append(list(k.pack(p).to_bytes(48,'little')));after.append(list(k.pack(pp).to_bytes(48,'little')))
        addresses.append(nextposition);outwrites.append(-1 if ow is None else ow);scratchwrites.append(-1 if sw is None else sw)
        p=pp;position=nextposition;out=newout;scratch=newscratch;age+=1;counts[holder]+=1
    assert age==120*k.Q and p.mode!=k.HALT
    # First rest update keeps a pending moving packet at its current logical
    # site instead of executing/migrating it. Out stays fixed.
    rest=k.local_transition(frame(position),beta)
    assert rest.heads[0]==k.pack(p) and rest.out==tuple(out.get(position+s,0) for s in k.SLOTS)
    age=k.U-1;target=k.PRIMARY_START+2006
    for i,s in enumerate(k.SLOTS):
        committed=k.local_transition(frame(target-s),beta)
        assert committed.info[i]==out.get(target,0)==0 and committed.out[i]==0
    return out,counts,dict(prefix_addresses=np.array(addresses,np.uint16),prefix_before=np.array(before,np.uint8),
        prefix_after=np.array(after,np.uint8),prefix_out_writes=np.array(outwrites,np.int8),
        prefix_scratch_writes=np.array(scratchwrites,np.int8))


def main():
    t=time.monotonic();directory=ROOT/'figs/gray_counterexamples'
    code,listing,labels,errors=builder.programme().assemble()
    assert not errors and len(code)<=k.CODE_CAPACITY
    beta=tuple(code+[0]*(k.CODE_CAPACITY-len(code)))
    choices={r['opcode']:r for r in listing};rng=random.Random(17177)
    fixtures=[('canonical_rest',fixture()),('native_wrap',fixture(commonage=k.U-1)),
              ('native_reset',fixture(commonage=112*k.Q-1)),('native_birth',fixture(commonage=112*k.Q))]
    for name,row in choices.items():
        packet=k.Packet(p=1,pc=row['address'],regs=tuple(rng.randrange(1<<20) for _ in range(16)))
        fixtures.append(('RUN_'+name,fixture(packet,112*k.Q+1,memory_seed=63)))
    assert choices['MI5']['operands']==[8,9,12,13,0]
    strict=[0]*16;strict[9]=6;strict[12]=100;strict[13]=1
    fixtures.append(('RUN_MI5_strict',fixture(k.Packet(p=1,pc=choices['MI5']['address'],regs=tuple(strict)),112*k.Q+1)))
    for kind in range(5):
        for mode in (k.SEEK,k.LOAD,k.WRITE):
            packet=k.Packet(p=1,mode=mode,kind=kind,start=0,width=3,index=0,lane=1,dst=7,
                            source=kind%4,dest=kind%2,regs=tuple(rng.randrange(1<<20) for _ in range(16)))
            fixtures.append(('MEM_%d_%d'%(mode,kind),fixture(packet,112*k.Q+1,memory_seed=kind+10)))
    for mode in (k.HALT,k.ERROR,6,7):
        fixtures.append(('MODE_'+str(mode),fixture(k.Packet(p=1,mode=mode),112*k.Q+1)))
    fixtures.append(('invalid_move3',fixture(k.Packet(p=1,move=3),112*k.Q+1)))
    fixtures.append(('nonzero_native_wrap',fixture(commonage=k.U-1,memory_seed=7717)))
    # Arbitrary-raw contexts may contain many heads. These are not intact
    # one-head-per-colony inputs, but are required by an all-raw own evaluator.
    for name in ('HLT','MAJ','WINCNT','ALU','MI5'):
        row=choices[name];regs=[0]*16
        if name=='MI5':regs[9]=6;regs[12]=100;regs[13]=1
        p=k.Packet(p=1,pc=row['address'],regs=tuple(regs))
        cells=fixture(p,112*k.Q+1,memory_seed=87)
        cells={j:replace(c,heads=(k.pack(p),)*5) for j,c in cells.items()}
        fixtures.append(('all_heads_'+name,cells))
    for i in range(8):
        p=k.Packet(p=1,pc=rng.randrange(65536),regs=tuple(rng.randrange(1<<20) for _ in range(16)))
        cells=fixture(p,112*k.Q+1,memory_seed=i+700)
        cells={j:replace(c,heads=(k.pack(p),)*5) for j,c in cells.items()}
        fixtures.append(('misaligned_all_heads_'+str(i),cells))
    inputs=[];outputs=[];ticks=[];names=[]
    for name,cells in fixtures:
        out,n,last,_=k.execute(beta,k.input_tape(cells),limit=400000)
        actual=[out.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_BITS)]
        expected=k.cell_bits(k.local_transition(cells,beta))
        if last.mode!=k.HALT or actual!=expected:
            retain_failure(name,cells,actual,expected,code,listing,labels,n,last)
        print(name,n,flush=True)
        inputs.append([k.cell_bits(cells[j]) for j in range(-5,6)]);outputs.append(actual);ticks.append(n);names.append(name)
    # Actual baseline fifth-stage usable update count excludes the birth tick.
    cells=fixture();out,n,last,history=k.execute(beta,k.input_tape(cells),limit=65535,record=True)
    incomplete=[out.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_BITS)]
    expected=k.cell_bits(k.local_transition(cells,beta))
    wrong=[i for i,(a,b) in enumerate(zip(incomplete,expected)) if a!=b]
    assert last.mode!=k.HALT and wrong
    actual_out,physical_counts,physical_trace=physical_prefix(beta,k.input_tape(cells))
    assert [actual_out.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_BITS)]==incomplete
    # The all-heads HLT context also exceeds the entire remaining16Q interval.
    row=choices['HLT'];packet=k.Packet(p=1,pc=row['address'])
    dense={j:k.Cell(addr=j%k.Q,age=112*k.Q+1,heads=(k.pack(packet),)*5) for j in range(-5,6)}
    dense_expected=k.cell_bits(k.local_transition(dense,beta));dense_rows=[]
    for limit in (13*k.Q-1,16*k.Q-1,400000):
        d,n,dp,_=k.execute(beta,k.input_tape(dense),limit=limit)
        dbits=[d.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_BITS)]
        dense_rows.append(dict(requested_ticks=limit,actual_ticks=n,last_mode=dp.mode,
            differing_bits=[i for i,(x,y) in enumerate(zip(dbits,dense_expected)) if x!=y]))
    assert dense_rows[0]['differing_bits'] and dense_rows[1]['differing_bits']==[66]
    assert dense_rows[2]['actual_ticks']==132803 and not dense_rows[2]['differing_bits']
    betapath=directory/'GMW2_full_own_beta.bin';betapath.write_bytes(np.packbits(np.array(beta,np.uint8),bitorder='little').tobytes())
    listingpath=directory/'GMW2_full_own_listing.json'
    listingpath.write_text(json.dumps(dict(code_capacity=k.CODE_CAPACITY,programme_bits=len(code),
        instructions=listing,labels=labels,errors=errors),indent=2)+'\n')
    asset=directory/'GMW2_full_own_replays.npz'
    np.savez_compressed(asset,input_bits=np.array(inputs,np.uint8),outputs=np.array(outputs,np.uint8),
        ticks=np.array(ticks,np.uint32),names=np.array(names),truncated_output=np.array(incomplete,np.uint8),
        truncated_expected=np.array(expected,np.uint8),truncated_positions=np.array([h[0] for h in history],np.uint16),
        dense_input=np.array([k.cell_bits(dense[j]) for j in range(-5,6)],np.uint8),
        dense_expected=np.array(dense_expected,np.uint8),**physical_trace)
    result=dict(name='GMW2 emitted whole word programme; finite comparisons and baseline fifth-stage obstruction',
        Q=k.Q,U=k.U,lambda_original=k.LAMBDA,c_original=k.ERROR_SEPARATION,
        immutable_ROM_code_capacity_bits=k.CODE_CAPACITY,physical_PC_bits=16,physical_frame_bits=k.FRAME_BITS,
        logical_head_bits=k.HEAD_BITS,programme_bits=len(code),instructions=len(listing),out_of_range_references=0,
        full_field_equations_defined=True,all_raw_total_transition_defined=True,all_raw_radius_at_most5=True,
        proposed_complete_own_programme_emitted=True,full_own_programme_equivalence_proved=False,
        uninterrupted_word_evaluator_replays=len(fixtures),actual_active_local_rule_replays=65535,
        rotating_holder_prefix_counts=physical_counts,rest_and_all_five_Info_commit_outputs_checked=True,
        replays_measured_only=True,measured_ticks=ticks,names=names,
        baseline_usable_fifth_active_ticks=65535,baseline_first_case_completed_ticks=ticks[0],
        baseline_first_case_excess_ticks=ticks[0]-65535,baseline_active_budget_obstruction_proved=True,
        truncated_packet_mode=last.mode,truncated_packet_pc=last.pc,truncated_different_bits=wrong,
        upper_ProgramBit_copy4_expected=1,upper_ProgramBit_copy4_committed=0,upper_wrong_bit=2006,
        physical_wrong_Out_Info_primary=k.PRIMARY_START+2006,error_support=[],
        uninterrupted_full_execution_after_active_end_is_actual_GMW2_execution=False,
        all_head_HLT_fixture_timing=dense_rows,all_head_HLT_initial_upper_context_intact=False,
        all_head_HLT_whole_remaining16Q_output_obstruction_proved=True,
        initial_upper_state_is_intact_recursive_hierarchy=False,input_snapshot_preloaded=True,
        holder_computed_service_address_explicit_change=True,h1_native_explicit_change=True,
        immutable_PC_instruction_lookup_explicit_change=True,mutable_ProgramBit_defined=True,
        mutable_ProgramBit_used_for_instruction_fetch=False,workspace_outputs_zero_explicit_change=True,
        full_Gray_protocol_or_noisy_period_completed=False,faster_U_used=False,active_rule_modified=False,
        Gray_refuted=False,iid_memory_failure_proved=False,global_reliability_established=False,
        kernel_sha256=digest(k.__file__),builder_sha256=digest(builder.__file__),checker_sha256=digest(__file__),
        beta_sha256=digest(betapath),listing_sha256=digest(listingpath),replays_sha256=digest(asset),
        wall_seconds=time.monotonic()-t)
    receipt=directory/'GMW2_full_own_certificate.json';receipt.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
