"""Timed literal faults at a READ_B state reached by actual colony execution."""
import argparse, hashlib, json, resource, time
from dataclasses import replace
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_core as c, retimed_holder_program as p
from gacsca.fixed_rule import retimed_holder_resident_general as general, retimed_holder_general_faults as faults
from gacsca.fixed_rule import retimed_holder_cuda_general_snapshot as snapshots
from gacsca.fixed_rule import retimed_holder_active_snapshot as active, retimed_holder_quotient as q
from gacsca.fixed_rule import retimed_holder_native as native
from experiments.fixed_rule.run_retimed_holder_cpu_periods import parents
from experiments.fixed_rule.retimed_holder_cuda_encoded_repair import forbidden, raw


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def equal(a,b):
    for key in a:np.testing.assert_array_equal(a[key],b[key],err_msg=key)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    out=Path(args.output);artifact=out.with_suffix('.npz')
    if out.exists() or artifact.exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();g=p.layout();start,end=g.stage_ranges[4];_,times=g.schedule(start,end)
    index=next(i for i in range(start,end) if g.instructions[i].kind==c.NAND)
    op=g.instructions[index];age=c.RESET_AGES[4]+times[index-start][2]-1
    saved={};metrics=[];top=parents(1);peak=0
    def save(name,state):
        for key,value in state.items():saved[name+'_'+key]=value
    general.library();faults.library();native.library()
    with general.World(top,device_budget=32*1024**2) as healthy:
        with forbidden():metrics.append(healthy.advance(age-1,extra_device_budget=32*1024**2))
        previous=snapshots.snapshot(healthy);save('previous',previous)
        with forbidden():healthy.step()
        checkpoint=snapshots.snapshot(healthy);save('checkpoint',checkpoint)
        records=checkpoint['active_rows'][0,:int(checkpoint['counts'][0])]
        heads=records[records[:,q.COL['head']]!=0];assert len(heads)==1
        head=heads[0];assert (int(head[q.COL['address']]),int(head[q.COL['phase']]),int(head[q.COL['rb']]),int(head[q.COL['alu']]))==(op.b,c.READ_B,op.b,c.NAND)
        middle=active.render(checkpoint);saved['checkpoint_raw']=middle;saved['previous_raw']=active.render(previous)
        # Compare independent vector reconstruction with actual GPU readback.
        anchors=(0,g.memory_count,g.computation_cells,op.a,op.b,op.d,f.Q-3)
        probes=sorted({(x+d)%f.Q for x in anchors for d in range(-7,8)})
        np.testing.assert_array_equal(middle[probes],raw(healthy.physical_cells(probes)))
        print(json.dumps(dict(stage='actual READ_B checkpoint',age=age,rom_instruction=index,head=int(head[q.COL['address']]),seconds=time.perf_counter()-started)),flush=True)
        with forbidden():healthy.step()
        after=snapshots.snapshot(healthy);save('after',after);after_raw=active.render(after);saved['after_raw']=after_raw
        # READ_B consumes an operand then moves to its next physical position.
        after_head=healthy.logical_cells((op.b+1,))[0]
        assert after_head.head and after_head.phase==c.WRITE
        assert after_head.value==c.arithmetic(c.NAND,int(head[q.COL['value']]),int(middle[op.b,f.COL['s2_data']]))
        with forbidden():healthy.step()
        save('second',snapshots.snapshot(healthy));saved['second_raw']=active.render(snapshots.snapshot(healthy))
        with forbidden():metrics.append(healthy.advance(f.U-healthy.time,extra_device_budget=32*1024**2))
        terminal=snapshots.snapshot(healthy);save('healthy_terminal',terminal)
        assert healthy.decode()==r.step_ring(top)
        results=[]
        for count in (2,3):
            with active.restore(checkpoint) as background,faults.World(background) as actual:
                equal(snapshots.snapshot(background),checkpoint)
                peak=max(peak,healthy.device_bytes+background.device_bytes+actual.device_bytes+8*(g.memory_count+5+32*6+1))
                changes={};initial=middle.copy();fault_list=[]
                for offset in range(-2,-2+count):
                    pos=(op.b-offset)%f.Q;field=f's{offset+2}_rb';cell=r.project(actual.read((pos,))[0])
                    changes[pos]=replace(cell,**{field:getattr(cell,field)^1});initial[pos,f.COL[field]]^=np.uint64(1)
                    fault_list.append((pos,f.COL[field],1))
                actual.inject(changes);assert len(actual.positions)==count
                frontier=sorted({(pos-j)%f.Q for pos in changes for j in f.NEIGHBORHOOD})
                before=raw(actual.read(frontier));np.testing.assert_array_equal(before,initial[frontier])
                with forbidden():row=actual.step()
                observed=raw(actual.read(frontier));expected=[]
                for pos in frontier:
                    neighbors=tuple(f.decode_cell(initial[(pos+j)%f.Q]) for j in f.NEIGHBORHOOD)
                    expected.append(f.encode_cell(r.lift(r.project(native.local_step(neighbors)))))
                np.testing.assert_array_equal(observed,np.array(expected,dtype=np.uint64))
                # Independent scalar source transcription at all affected outputs.
                for j,pos in enumerate(frontier):
                    neighbors=tuple(f.decode_cell(initial[(pos+d)%f.Q]) for d in f.NEIGHBORHOOD)
                    np.testing.assert_array_equal(observed[j],f.encode_cell(r.lift(r.project(f.local_step(neighbors)))))
                equal(snapshots.snapshot(background),after) # no rebase into reference
                saved[f'case{count}_faults']=np.array(fault_list,dtype=np.uint64)
                saved[f'case{count}_frontier']=np.array(frontier,dtype=np.uint64)
                saved[f'case{count}_before']=before;saved[f'case{count}_after']=observed
                if count==2:
                    assert not actual.positions
                    np.testing.assert_array_equal(observed,after_raw[frontier])
                    with forbidden():metrics.append(actual.advance(f.U-actual.time,absorb_data=False,absorb_flags=False))
                    assert not actual.positions;equal(snapshots.snapshot(background),terminal)
                    save('repaired_terminal',snapshots.snapshot(background))
                else:
                    assert actual.positions
                    central=actual.read((op.b+1,))[0]
                    assert central.s2_phase==c.READ_B and central.s2_rb==(op.b^1)
                    assert not np.array_equal(observed,after_raw[frontier])
                results.append(dict(fault_copies=count,faults=fault_list,literal_metrics=row,raw_output_differences=int(np.count_nonzero(observed!=after_raw[frontier]))))
                print(json.dumps(dict(stage='fault case',copies=count,seconds=time.perf_counter()-started,**row)),flush=True)
        assert peak<64*1024**2
    saved['initial_top']=raw(top);np.savez_compressed(artifact,**saved)
    sources=[Path(__file__),Path(active.__file__),Path(snapshots.__file__),Path(general.__file__),Path(faults.__file__)]
    receipt=dict(passed=True,age=age,rom_instruction=index,rom_operands=dict(a=op.a,b=op.b,d=op.d),cases=results,actual_middle_sites=f.Q,physical_period=f.U,seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,explicit_device_peak_bound_bytes=peak,advance_metrics=metrics,full_checkpoint_preserved=True,two_copy_complete_rejoin_after_one_literal_tick=True,repaired_suffix_and_complete_terminal_equal=True,host_transitions_forbidden_during_GPU_evolution=True,artifact_sha256=sha(artifact),source_sha256={str(x):sha(x) for x in sources},descriptor_sha256=f.self_description().digest(),rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),binaries={str(x.library()._name):sha(x.library()._name) for x in (general,faults,native)},scope='Timed procedure-replica faults in an actual running middle colony; full raw frontier parity and one-period continuation. No encoded bottom fault run, stochastic noise or general recovery theorem.')
    out.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2),flush=True)

if __name__=='__main__':main()
