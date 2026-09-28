"""Actual compact evaluator checkpoint and literal full-ring controller faults."""
import argparse
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_projected as r
from gacsca.fixed_rule import compact16_holder_core as c, compact16_holder_program as p
from gacsca.fixed_rule import compact16_holder_resident_general as general, compact16_holder_native as native
from gacsca.fixed_rule import compact16_holder_cuda_general_snapshot as snapshots, compact16_holder_active_snapshot as active
from gacsca.fixed_rule import compact16_holder_records as q
from experiments.fixed_rule.run_compact16_holder_cpu_periods import parents
from experiments.fixed_rule.validate_compact16_holder_endpoint import guard
from experiments.fixed_rule.audit_compact16_holder_terminal import step as diagnostic_step
from experiments.fixed_rule.audit_small_holder_position_events import sha


def literal(raw):
    assert raw.dtype==np.uint64 and raw.shape==(f.Q,f.FIELDS)
    source=np.ascontiguousarray(raw);out=np.empty_like(source)
    native.library().compact16_holder_ring(native.pointer(source),native.pointer(out),len(raw))
    return out


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();artifact=args.output.with_suffix('.npz')
    if args.output.exists() or artifact.exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();g=p.layout();start,end=g.stage_ranges[4];_,times=g.schedule(start,end)
    index=next(i for i in range(g.description_instruction,end) if g.instructions[i].kind==c.NAND)
    op=g.instructions[index];age=c.RESET_AGES[4]+times[index-start][2]-1
    assert age>c.WF_END+f.Q
    saved={};metrics=[];top=parents(1)
    def save(name,state):
        for key,value in state.items():saved[name+'_'+key]=value
    with general.World(top,device_budget=32*1024**2) as healthy:
        with guard():metrics.append(healthy.advance(age-1,extra_device_budget=32*1024**2))
        previous=snapshots.snapshot(healthy);save('previous',previous);saved['previous_raw']=active.render(previous)
        with guard():healthy.step()
        checkpoint=snapshots.snapshot(healthy);save('checkpoint',checkpoint);middle=active.render(checkpoint);saved['checkpoint_raw']=middle
        np.testing.assert_array_equal(literal(saved['previous_raw']),middle)
        records=checkpoint['active_rows'][0,:int(checkpoint['counts'][0])];heads=records[records[:,q.COL['head']]!=0]
        assert len(heads)==1;head=heads[0]
        assert (int(head[q.COL['address']]),int(head[q.COL['phase']]),int(head[q.COL['rb']]),int(head[q.COL['alu']]))==(op.b,c.READ_B,op.b,c.NAND)
        probes=sorted({(x+d)%f.Q for x in (0,op.a,op.b,op.d,g.memory_count,g.computation_cells,f.Q-3) for d in range(-7,8)})
        np.testing.assert_array_equal(middle[probes],[f.encode_cell(cell) for cell in healthy.physical_cells(probes)])
        print(json.dumps(dict(stage='live complete evaluator checkpoint',age=age,instruction=index,seconds=time.perf_counter()-started)),flush=True)
        with guard():healthy.step()
        after=snapshots.snapshot(healthy);save('after',after);after_raw=active.render(after);saved['after_raw']=after_raw
        np.testing.assert_array_equal(literal(middle),after_raw)
        observed=healthy.logical_cells((op.b+1,))[0]
        assert observed.head and observed.phase==c.WRITE
        assert observed.value==c.arithmetic(c.NAND,int(head[q.COL['value']]),int(middle[op.b,f.COL['s2_data']]))
        with guard():healthy.step()
        second=snapshots.snapshot(healthy);save('second',second);saved['second_raw']=active.render(second)
        np.testing.assert_array_equal(literal(after_raw),saved['second_raw'])
        cases=[]
        for count in (2,3):
            damaged=middle.copy();faults=[]
            for offset in range(-2,-2+count):
                pos=(op.b-offset)%f.Q;field=f.COL[f's{offset+2}_rb']
                damaged[pos,field]^=np.uint64(1);faults.append((pos,field,1))
            result=literal(damaged)
            frontier=sorted({(pos-j)%f.Q for pos,_,_ in faults for j in f.NEIGHBORHOOD})
            for at in frontier:
                neighbors=tuple(f.decode_cell(damaged[(at+j)%f.Q]) for j in f.NEIGHBORHOOD)
                np.testing.assert_array_equal(result[at],f.encode_cell(f.local_step(neighbors)))
            outside=np.ones(f.Q,dtype=bool);outside[frontier]=False
            np.testing.assert_array_equal(result[outside],after_raw[outside])
            saved[f'case{count}_faults']=np.array(faults,dtype=np.uint64)
            saved[f'case{count}_frontier']=np.array(frontier,dtype=np.uint64)
            saved[f'case{count}_after']=result
            different=int(np.count_nonzero(result!=after_raw))
            if count==2:
                np.testing.assert_array_equal(result,after_raw)
                np.testing.assert_array_equal(literal(result),saved['second_raw'])
            else:
                assert different>0
                assert result[op.b+1,f.COL['s2_phase']]==c.READ_B and result[op.b+1,f.COL['s2_rb']]==(op.b^1)
            cases.append(dict(fault_copies=count,physical_raw_bit_flips=faults,full_ring_raw_words_checked=f.Q*f.FIELDS,
                              raw_output_differences=different,scalar_frontier_sites=len(frontier)))
        with guard():metrics.append(healthy.advance(f.U-healthy.time,extra_device_budget=32*1024**2))
        save('healthy_terminal',snapshots.snapshot(healthy));assert healthy.decode()==diagnostic_step(top)
        bound=healthy.device_bytes+max(row.get('extra_device_bytes',0) for row in metrics)+32*f.Q//64+2
        assert bound<64*1024**2
    saved['initial_top']=np.array([f.encode_cell(r.lift(cell)) for cell in top],dtype=np.uint64)
    np.savez_compressed(artifact,**saved)
    result=dict(passed=True,age=age,rom_instruction=index,description_instruction=g.description_instruction,
                rom_operands=dict(a=op.a,b=op.b,d=op.d),cases=cases,actual_middle_sites=f.Q,
                two_copy_complete_rejoin_after_one_literal_tick=True,healthy_complete_suffix_executed=True,
                native_ring_transitions=6,full_ring_words_per_transition=f.Q*f.FIELDS,
                explicit_device_buffer_bound=bound,metrics=metrics,artifact=str(artifact),artifact_sha256=sha(artifact),
                descriptor_sha256=f.self_description().digest(),rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),
                source_sha256={str(Path(module.__file__)):sha(module.__file__) for module in (f,c,p,native,general,active,snapshots)},
                native_binary=str(native.library()._name),native_binary_sha256=sha(native.library()._name),seconds=time.perf_counter()-started,
                scope='Two/three raw controller-copy faults at an actually executed middle evaluator NAND. Complete native physical rings and independent scalar frontier checks; encoded bottom execution is separate. Not stochastic robustness.')
    result['source_sha256'][str(Path(__file__))]=sha(__file__)
    with args.output.open('x') as out:out.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
