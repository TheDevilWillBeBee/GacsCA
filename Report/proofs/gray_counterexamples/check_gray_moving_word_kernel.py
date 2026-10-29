#!/usr/bin/env python3
"""GMW0 native-programme/physical-head certificate, no whole self-beta claim."""
from pathlib import Path
from dataclasses import replace
import hashlib,json,random,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
import gray_moving_word_kernel as k
import literal_maintenance


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def encoded_neighbourhood(x,age,old_position,packet,tape,out,info=None):
    packed=k.pack(packet);info={} if info is None else info
    return {j:k.Cell(addr=(x+j)%k.Q,age=age,
         heads=tuple(packed if x+j+s==old_position else 0 for s in k.SLOTS),
         mem=tuple(tape.get(x+j+s,0) for s in k.SLOTS),
         out=tuple(out.get(x+j+s,0) for s in k.SLOTS),
         info=tuple(info.get(x+j+s,0) for s in k.SLOTS)) for j in range(-5,6)}


def native_cases():
    rng=random.Random(234634396)
    cases=[]
    for phase in (0,1,2,3,k.Q-4,k.Q-3,k.Q-2,k.Q-1,4170):
        for age in (0,k.U-1):
            cases.append({j:dict(addr=(phase+j)%k.Q,age=age,f1=0,f2=0,wf1=0,wf2=0)
                          for j in range(-5,6)})
    for i in range(64):
        cases.append({j:dict(addr=rng.randrange(k.Q),age=rng.randrange(k.U),
                    f1=rng.randrange(2),f2=rng.randrange(2),wf1=rng.randrange(2),wf2=rng.randrange(2))
                      for j in range(-5,6)})
    # Nonexistent/address/age majority and all raw flag extremes.
    for flags in range(16):
        cases.append({j:dict(addr=(1000+137*j)%k.Q,age=(777777+997*j)%k.U,
                    f1=flags&1,f2=(flags>>1)&1,wf1=(flags>>2)&1,wf2=(flags>>3)&1)
                      for j in range(-5,6)})
    return cases


def main():
    start_time=time.monotonic();directory=ROOT/'figs/gray_counterexamples'
    beta,listing,labels=k.native_word_programme()
    assert (k.HEAD_BITS,k.FRAME_BITS,k.PRIMARY_START,k.ENTRY)==(434,2272,2960,3024)
    assert sum(r['bits'] for r in listing)==2346 and len(listing)==107
    assert listing[-1]['address']+listing[-1]['bits']==5370
    assert 2*k.FRAME_BITS<=k.Q
    for row in listing:
        value=sum(beta[row['address']+i]<<i for i in range(row['bits']))
        assert k.decode_instruction(value)==(row['opcode'],tuple(row['operands']))
    assert max(k.LENGTH.values())==29
    # All branch targets are forward and rejoin before the next memory command.
    branches=[]
    for i,row in enumerate(listing):
        if row['opcode'] not in ('BNZ','JMP'):continue
        target=row['operands'][-1]
        assert target>row['address']
        crossed=[r for r in listing if row['address']<r['address']<target]
        assert all(r['opcode'] not in ('LOAD5','LOADC','LOADCOL','WRITE','HLT') for r in crossed)
        branches.append(dict(address=row['address'],target=target,forward=True,no_memory_command_skipped=True))
    # One tick per code location, plus a deterministic excursion for each IO.
    excursions=[]
    for row in listing:
        name=row['opcode'];a=row['operands']
        if name not in ('LOAD5','LOADC','LOADCOL','WRITE'):continue
        if name=='LOAD5':position,width=a[0],a[1]
        elif name=='LOADCOL':position,width=a[1],1
        else:position,width=a[1],a[2]
        end=row['address']+row['bits']-1;ret=end+1
        # Last instruction bit has already been fetched; return tick also fetches
        # the first return-PC bit, already counted among the programme bits.
        overhead=abs(end-position)+width-1+abs(position+width-1-ret)-1
        excursions.append(dict(opcode=name,instruction_end=end,start=position,width=width,
                               return_pc=ret,extra_ticks=overhead))
    runtime=2346+sum(r['extra_ticks'] for r in excursions)
    assert runtime==34396
    cases=native_cases();outputs=[];ticks=[];inputs=[]
    for cells in cases:
        out,n,packet,_=k.abstract_execute(beta,k.tape_from_native(cells))
        actual=k.native_output(out);expected=literal_maintenance.scalar(cells)
        assert packet.mode==k.HALT and n==runtime
        assert all(actual[field]==expected[field] for field in actual),(actual,expected)
        inputs.append([[cells[j][f] for f in ('addr','age','f1','f2','wf1','wf2')]
                       for j in range(-5,6)])
        outputs.append([actual[f] for f in ('addr','age','f1','f2')]);ticks.append(n)
    # Actual local-transition replay for every head tick, rotating its five
    # physical holders. Input is an arbitrary upper native neighbourhood;
    # lower native geometry is quiet/canonical with the common physical clock.
    cells=cases[18];tape=k.tape_from_native(cells)
    logical_out={};old_position=k.ENTRY;packet=k.initial_packet()
    age=112*k.Q+1;trace_addresses=[];trace_before=[];trace_after=[];trace_writes=[]
    holder_counts=[0]*5
    for tick in range(runtime):
        new_position=old_position+(1 if packet.move==1 else -1 if packet.move==2 else 0)
        nextpacket,write=k.step_packet(packet,new_position,tape.get(new_position,0),beta)
        holder=tick%5;x=new_position-k.SLOTS[holder]
        physical=k.local_transition(encoded_neighbourhood(x,age,old_position,packet,tape,logical_out),beta)
        newout=dict(logical_out)
        if write is not None:newout[new_position]=write
        expected_heads=tuple(k.pack(nextpacket) if x+s==new_position else 0 for s in k.SLOTS)
        assert physical.heads==expected_heads
        assert physical.mem==tuple(tape.get(x+s,0) for s in k.SLOTS)
        assert physical.out==tuple(newout.get(x+s,0) for s in k.SLOTS)
        assert physical.info==(0,)*5
        assert (physical.addr,physical.age,physical.f1,physical.f2,physical.wf1,physical.wf2)==(
                x%k.Q,(age+1)%k.U,0,0,0,0)
        holder_counts[holder]+=1
        trace_addresses.append(new_position)
        trace_before.append(list(k.pack(packet).to_bytes((k.HEAD_BITS+7)//8,'little')))
        trace_after.append(list(k.pack(nextpacket).to_bytes((k.HEAD_BITS+7)//8,'little')))
        trace_writes.append(-1 if write is None else write)
        packet=nextpacket;old_position=new_position;logical_out=newout;age+=1
    assert packet.mode==k.HALT and age==951901
    assert k.native_output(logical_out)==dict(zip(('addr','age','f1','f2'),outputs[18]))
    # Birth, rest, and exact old-Out -> Info before Out reset order.
    special=0
    born=k.local_transition(encoded_neighbourhood(k.ENTRY,112*k.Q,k.ENTRY,k.ZERO,tape,{}),beta)
    assert k.unpack(born.heads[0])==k.initial_packet();special+=1
    for commonage in (0,16*k.Q,32*k.Q,96*k.Q,120*k.Q,127*k.Q):
        rest=k.local_transition(encoded_neighbourhood(old_position,commonage,old_position,packet,tape,logical_out),beta)
        assert rest.heads[0]==k.pack(packet);special+=1
    for commonage in (112*k.Q-1,k.U-1):
        for x in range(k.NATIVE_COLUMNS['addr'][0]-2,k.NATIVE_COLUMNS['f2'][0]+3):
            physical=k.local_transition(encoded_neighbourhood(x,commonage,old_position,packet,tape,logical_out),beta)
            assert physical.heads==(0,)*5 and physical.out==(0,)*5
            expected=tuple(logical_out.get(x+s,0) for s in k.SLOTS) if commonage==k.U-1 else (0,)*5
            assert physical.info==expected;special+=1
    # Invalid instructions/ranges/raw packet modes, collision precedence.
    failures=[]
    for opcode in range(28,32):
        p=k.execute_instruction(k.initial_packet(),k.ENTRY,k.decode_instruction(opcode),k.ENTRY+5)
        assert p.mode==k.ERROR;failures.append('reserved_opcode_'+str(opcode))
    for decoded in (('LOAD5',(8191,2,0)),('LOADC',(0,0,0)),
                    ('WRITE',(0,8190,20)),('WINCNT',(0,1,2,3,6,7))):
        assert k.execute_instruction(k.initial_packet(),k.ENTRY,decoded,k.ENTRY+5).mode==k.ERROR
        failures.append(repr(decoded))
    for mode in (6,7):
        assert k.step_packet(replace(packet,mode=mode),k.ENTRY,0,beta)[0].mode==k.ERROR
        failures.append('raw_mode_'+str(mode))
    assert k.step_packet(replace(packet,move=3),k.ENTRY,0,beta)[0].mode==k.ERROR
    failures.append('raw_move_3')
    collisions=0
    for bits in range(8):
        proposals=[replace(packet,p=(bits>>i)&1,move=(1,0,2)[i]) for i in range(3)]
        chosen=k.incoming(proposals)
        if bits.bit_count()>1:assert chosen.mode==k.ERROR
        elif bits:assert chosen==proposals[(bits&-bits).bit_length()-1]
        else:assert chosen==k.ZERO
        collisions+=1
    # Algebraic majority identities, holder maps and exact dependency offsets.
    majority_cases=0
    for word in (0,1,(1<<k.HEAD_BITS)-1,k.pack(packet)):
        for badcount in (0,1,2):
            for bad in __import__('itertools').combinations(range(5),badcount):
                values=[word]*5
                for i in bad:values[i]=word^((1<<k.HEAD_BITS)-1)
                assert k.vote(values)==word;majority_cases+=1
    head_offsets=sorted({s+j-t for s in k.SLOTS for j in (-1,0,1) for t in k.SLOTS})
    tape_offsets=sorted({s-t for s in k.SLOTS for t in k.SLOTS})
    assert head_offsets==list(range(-5,6)) and tape_offsets==list(range(-4,5))
    betapath=directory/'GMW0_native_beta.bin'
    betapath.write_bytes(np.packbits(np.array(beta,np.uint8),bitorder='little').tobytes())
    listingpath=directory/'GMW0_native_listing.json'
    listingpath.write_text(json.dumps(dict(entry=k.ENTRY,code_bits=2346,labels=labels,
        instruction_fields=k.ARGS,programme=listing),indent=2)+'\n')
    replaypath=directory/'GMW0_native_physical_replays.npz'
    np.savez_compressed(replaypath,inputs=np.array(inputs,np.uint32),outputs=np.array(outputs,np.uint32),
        ticks=np.array(ticks,np.uint32),trace_addresses=np.array(trace_addresses,np.uint16),
        trace_before=np.array(trace_before,np.uint8),trace_after=np.array(trace_after,np.uint8),
        trace_writes=np.array(trace_writes,np.int8))
    proof=Path(__file__).with_name('GMW0_PHYSICAL_NATIVE_PROGRAMME.md')
    result=dict(name='GMW0 total radius-five moving word kernel; physical native prefix only',
        Q=k.Q,U=k.U,error_lambda=k.LAMBDA,error_separation_c=k.ERROR_SEPARATION,
        native_clause='literal printed Flag2 erasure; no h1 correction',
        interpreter_word_bits=k.WORD,registers=16,head_logical_bits=k.HEAD_BITS,
        physical_frame_bits=k.FRAME_BITS,Q_ge_twice_frame=True,primary_start=k.PRIMARY_START,
        native_programme_entry=k.ENTRY,native_programme_end=5370,programme_bits=2346,
        programme_instructions=107,maximum_instruction_bits=29,programme_storage_fits=True,
        native_prefix_runtime_ticks=runtime,runtime_bound_input_independent=True,
        runtime_code_ticks=2346,runtime_excursions=excursions,branches=branches,
        fifth_active_budget_ticks=8*k.Q,head_initial_row_age=112*k.Q+1,
        halt_row_age=age,fifth_active_end_age=120*k.Q,active_end_slack=120*k.Q-age,
        opcode_semantics_defined=True,instruction_fetch_one_immutable_bit_per_tick=True,
        all_raw_physical_component_transition_defined=True,all_raw_radius_at_most5_proved=True,
        head_holder_dependency_offsets=head_offsets,tape_dependency_offsets=tape_offsets,
        native_programme_equivalence_by_register_invariants=True,
        noiseless_physical_native_prefix_by_copy_induction=True,
        quiet_head_uniqueness_by_induction=True,quiet_all_colony_births_synchronized=True,
        immutable_programme_lookup_by_raw_address=True,mutable_input_tape_noise_exposed=True,
        workspace_flag_outputs_forced_zero_explicit_change=True,
        preloaded_native_input_tape_premise=True,physical_input_gather_refinement_proved=False,
        instruction_and_physical_replays_measured_only=True,retained_native_cases=len(cases),
        actual_local_transition_replays=runtime,rotating_holder_replay_counts=holder_counts,
        actual_special_stage_transition_replays=special,invalid_case_replays=failures,
        collision_cases=collisions,majority_identity_replays=majority_cases,
        Info_commit_reads_old_Out_before_Out_reset=True,full_SimBit_WF_order_completed=False,
        own_full_beta_emitted=False,full_self_simulation_proved=False,
        physical_native_prefix_programme_is_own_beta=False,
        h1_GV0_radius8_silently_used=False,faster_U_used=False,
        faithful_Gray_whole_rule_completed=False,faithful_Gray_counterexample_proved=False,
        iid_memory_failure_proved=False,global_reliability_established=False,active_rule_modified=False,
        wall_seconds=time.monotonic()-start_time,kernel_sha256=digest(k.__file__),
        checker_sha256=digest(__file__),written_proof_sha256=digest(proof),
        beta_sha256=digest(betapath),listing_sha256=digest(listingpath),replays_sha256=digest(replaypath),
        literal_module_sha256=digest(literal_maintenance.__file__),
        gray_text_sha256=digest(ROOT/'papers_txt/gray_readers_guide.txt'),
        gray_pdf_sha256=digest(next((ROOT/'papers').glob('A Reader*'))),
        receipt_dependencies_sha256={name:digest(directory/name) for name in
           ('GPN0_native_programme_certificate.json','Gray_computed_simbit_order_certificate.json',
            'GMW0_initial_listing_failure.json')})
    receipt=directory/'GMW0_native_programme_certificate.json'
    receipt.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ('programme_bits','physical_frame_bits',
        'native_prefix_runtime_ticks','actual_local_transition_replays','active_end_slack',
        'own_full_beta_emitted','global_reliability_established','wall_seconds')}))


if __name__=='__main__':main()
