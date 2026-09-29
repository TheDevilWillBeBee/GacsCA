"""Two lower macrosteps of guarded windows from an actual depth-two initializer.

The entire small periodic bottom simulation is executed. Interior decoded upper
cells are compared with shrinking full-rule causal cones of the true Q-cell upper
ring. This is NOT a full Q-colony bottom allocation or a completed top macrostep.
"""
import argparse,hashlib,json,os,resource,subprocess,time
from pathlib import Path
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import small_holder_resident_gather as gpu,small_holder_stream_initial as stream
from gacsca.fixed_rule import small_holder_rule as f,small_holder_projected as r,small_holder_core as c,small_holder_program as p,small_holder_quotient as q,small_holder_native as native
from gacsca.fixed_rule import small_holder_resident_period as period,small_holder_resident_independent as independent
from gacsca.fixed_rule.wordcode import Program


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def memory():
    for line in subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],text=True).splitlines():
        pid,value=line.split(',',1)
        if int(pid)==os.getpid():return int(value)
    return 0

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();stem=Path(args.output)
    for ext in ('.json','.npz','.progress.json'):
        if stem.with_suffix(ext).exists():raise FileExistsError('preserve prior evidence')
    started=time.perf_counter();top=(r.Cell(address=321,age=117,s2_head=1,s2_phase=c.WRITE,s2_rd=321,s2_value=0x123456789ABCDEF0),)
    initial=stream.InitialRing(top);value_address=p.layout().info[f.COL['s2_value']]
    segments=(tuple(range(-14,19)),tuple(range(value_address-14,value_address+15)))
    positions=sum(segments,());initial_rows=initial.raw(1,positions)
    current=tuple(f.decode_cell(row.tolist()) for row in initial_rows)
    cones=[tuple(f.decode_cell(row.tolist()) for row in initial.raw(1,segment)) for segment in segments]
    metrics={};seconds=0.;snapshots=[];periods=[];observed=[]
    with gpu.World.from_raw_chunks(len(positions),[initial_rows]) as world:
        allocated=world.device_bytes;observed.append(memory())
        for macro in (1,2):
            expected=tuple(r.lift(r.project(x)) for x in native.step_ring(current))
            # These cones have no artificial seam: they are exact neighborhoods
            # of the actual recursively encoded upper ring, with halo shrinking.
            cones=[tuple(r.lift(r.project(native.local_step(cone[i-7:i+8]))) for i in range(7,len(cone)-7)) for cone in cones]
            for target in (f.CAPTURE_AGE,f.U):
                stop=(macro-1)*f.U+target
                while world.time<stop:
                    tick=time.perf_counter()
                    with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator')),patch.object(f,'local_step',side_effect=AssertionError('host simulated step')),patch.object(r,'local_step',side_effect=AssertionError('host simulated step')),patch.object(native,'local_step',side_effect=AssertionError('host rule')):
                        row=world.advance(min(c.T,stop-world.time),chunk=1<<20)
                    seconds+=time.perf_counter()-tick
                    for name,value in row.items():
                        metrics[name]=max(metrics.get(name,0),value) if name=='extra_device_bytes' else metrics.get(name,0)+value
                    stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='running',lower_macrostep=macro,physical_time=world.time,age=world.age,gpu_run_seconds=seconds,metrics=metrics))+'\n')
                if target==f.CAPTURE_AGE:
                    right=[]
                    for col,parent in enumerate(expected):
                        cells=world.logical_cells(tuple(col*f.Q+a for a in range(f.Q-5,f.Q)))
                        assert [x.signal for x in cells]==[parent.f1*x for x in (16,8,4,2,1)]
                        assert not parent.f2
                        right.append(parent.f1)
                    assert 0<sum(right)<len(right)
                    print(json.dumps(dict(macro=macro,capture=True,mixed_right_ones=sum(right),gpu_run_seconds=seconds)),flush=True)
            actual=tuple(r.lift(x) for x in world.decode())
            assert actual==expected
            margin=macro*7;offset=0;interior=0
            for segment,cone in zip(segments,cones):
                assert actual[offset+margin:offset+len(segment)-margin]==cone
                interior+=len(cone);offset+=len(segment)
            head_position=macro-1
            assert actual[14+head_position].s2_head==1
            assert actual[len(segments[0])+14].s2_data==0x123456789ABCDEF0
            snapshots.append(native.array_from_cells(actual));observed.append(memory())
            periods.append(dict(lower_macrostep=macro,all_window_raw_fields_match=True,true_ring_interior_raw_cells_match=interior,upper_head_at=head_position,encoded_top_controller_value_preserved=True,computed_right_signal_ones=sum(x.f1 for x in actual),gpu_run_seconds=seconds))
            print(json.dumps(periods[-1]),flush=True);current=actual
    assert metrics['physical_ticks']==2*f.U
    np.savez_compressed(stem.with_suffix('.npz'),top=r.array_from_cells(top),positions=np.array(positions,dtype=np.int64),initial_raw=initial_rows,decoded=np.array(snapshots))
    paths=[Path(__file__),Path(gpu.__file__),Path(gpu.__file__).with_suffix('.cu'),Path('gacsca/fixed_rule/small_holder_resident_mixed.py'),Path(stream.__file__),Path(period.__file__),Path(period.__file__).with_suffix('.cu'),Path(independent.__file__),Path(independent.__file__).with_suffix('.cu'),Path('experiments/fixed_rule/prove_small_holder_mixed_right.py')]
    result=dict(passed=True,initialized_depth=2,full_initial_upper_ring_sites=f.Q,executed_lower_colonies=len(positions),executed_physical_sites=len(positions)*f.Q,successive_lower_macrosteps=2,guard_per_segment=14,periods=periods,metrics=metrics,gpu_run_seconds=seconds,seconds=time.perf_counter()-started,explicit_resident_device_bytes=allocated,explicit_peak_with_staging_bytes=allocated+metrics['extra_device_bytes'],observed_process_gpu_mib=observed,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,descriptor_sha256=f.self_description().digest(),rom_bytes_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),binary_sha256=digest(gpu.library()._name),artifact_sha256=digest(stem.with_suffix('.npz')),source_sha256={str(path):digest(path) for path in paths},limitations=['executed guarded windows of the true depth-two initializer, not the full Q-colony bottom ring','two upper physical ticks, not a full upper work period/top macrostep','artificial window seams generate flags; shrinking true-ring cones exclude their upper-rule influence','left Signals remain zero and physical state coherent; arbitrary faults/cross-level noise amplification untested'])
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='complete',physical_time=2*f.U))+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
