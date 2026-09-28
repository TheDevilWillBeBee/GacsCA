"""Two continuous GPU physical work periods; full raw decoded-step audits.

This is one simulation link in the certified coherent uniform-right family.
No hierarchy-depth-specific rule and no host upper transition during evolution.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import time
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import small_holder_resident_period as gpu,small_holder_prefix_world as prefix,small_holder_recurrent_prefix_world as recurrent,small_holder_suffix_world as suffix
from gacsca.fixed_rule import small_holder_rule as f,small_holder_core as c,small_holder_projected as r,small_holder_quotient as q,small_holder_program as p,small_holder_native as native
from gacsca.fixed_rule import word_workspace_source,word_allocation,small_holder_prefix_description,small_holder_packed,small_holder_flag_profile as profile
from gacsca.fixed_rule.wordcode import Program
from experiments.fixed_rule.small_holder_execution import initial_ring


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def gpu_mib():
    text=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],text=True)
    for line in text.splitlines():
        pid,memory=map(str.strip,line.split(',',1))
        if pid==str(os.getpid()):return int(memory)
    return 0


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();stem=Path(args.output)
    for ext in ('.json','.npz','.progress.json'):
        if stem.with_suffix(ext).exists():raise FileExistsError('preserve prior evidence')
    started=time.perf_counter();top=initial_ring();g=p.layout();n=len(top);reference=prefix.World.encode(top)
    metrics=dict(physical_ticks=0,literal_ticks=0,transport_or_quiet_ticks=0,logical_evaluations=0);probes=[];periods=[];snapshots=[];decoded=[];expected_frames=[];observed=[];gpu_seconds=0.
    try:
        with gpu.World(top) as world:
            allocated=world.device_bytes;observed.append(gpu_mib());current=top
            for period in range(2):
                raw=tuple(r.lift(x) for x in current)
                expected=native.array_from_cells(tuple(r.lift(r.project(x)) for x in f.step_ring(raw)))
                expected_frames.append(expected)
                targets=(c.CAPTURE_AGE,profile.START,f.WF_START+11000,f.WF_END+f.Q//2,f.RESET_AGES[4]+1,f.ACTIVE_ENDS[4],f.U)
                for target in targets:
                    absolute=period*f.U+target
                    while world.time<absolute:
                        dt=min(c.T,absolute-world.time);stage=time.perf_counter()
                        with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator')),patch.object(f,'local_step',side_effect=AssertionError('host upper F')),patch.object(r,'local_step',side_effect=AssertionError('host upper F')),patch.object(native,'local_step',side_effect=AssertionError('host F')):
                            row=world.run(dt)
                        gpu_seconds+=time.perf_counter()-stage
                        for key,value in row.items():metrics[key]+=value
                        reference.run(dt)
                        stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='running',period=period+1,physical_time=world.time,age=world.age,gpu_run_seconds=gpu_seconds,seconds=time.perf_counter()-started,metrics=metrics),indent=2)+'\n')
                    if target==profile.START:
                        handoff=reference.stored;reference.close();reference=suffix.World(handoff);del handoff
                    sample_addresses=tuple(sorted({0,1,2,3,4,5,100,g.info[0],g.hold[0],g.computation_cells-1,f.Q-8,f.Q-5,f.Q-3,f.Q-1}))
                    positions=tuple(col*f.Q+a for col in range(n) for a in sample_addresses)
                    got=world.physical_cells(positions)
                    wanted=tuple(r.lift(reference.cell(col,a)) for col in range(n) for a in sample_addresses)
                    assert got==wanted,(period,target)
                    if target==f.WF_START+11000:assert any(x.f1 for x in got)
                    probe=dict(period=period+1,age=target,physical_time=world.time,full_raw_samples=len(got),gpu_run_seconds=gpu_seconds);probes.append(probe);print(json.dumps(probe),flush=True)
                assert world.age==0 and world.time==(period+1)*f.U
                actual=world.decode();actual_raw=native.array_from_cells(tuple(r.lift(x) for x in actual))
                np.testing.assert_array_equal(actual_raw,expected)
                changes=sum(getattr(old,name)!=getattr(new,name) for old,new in zip(raw,r.cells_from_array(r.array_from_cells(actual))) for name,_ in r.SCHEMA if name.startswith('s'))
                assert changes>0
                final=world.stored();wanted=reference.logical_stored
                np.testing.assert_array_equal(final,wanted)
                # Check all gap cells too: stored core/tail equality alone is
                # insufficient to establish an exact physical handoff.
                gaps=hashlib.sha256()
                for col in range(n):
                    for start in range(g.computation_cells,f.Q-5,gpu.MAX_READ):
                        addresses=tuple(range(start,min(f.Q-5,start+gpu.MAX_READ)))
                        cells=world.logical_cells(tuple(col*f.Q+a for a in addresses))
                        assert cells==tuple(reference.logical_cell(col,a) for a in addresses)
                        gaps.update(q.array_from_cells(cells).tobytes())
                snapshots.append(final);decoded.append(actual_raw);observed.append(gpu_mib())
                periods.append(dict(period=period+1,raw_controller_changes=changes,decoded_all_fields_match=True,entire_coherent_state_matches=True,stored_sha256=hashlib.sha256(final.tobytes()).hexdigest(),gap_sha256=gaps.hexdigest(),old_signals_carried=bool(np.any(final[:,q.COL['signal']]))))
                current=actual
                if period==0:
                    # CPU reference continues from its actual commit. The GPU
                    # object and buffers are untouched across the work periods.
                    reference.close();reference=recurrent.World(wanted);del wanted
    finally:reference.close()
    assert metrics['physical_ticks']==2*f.U==metrics['literal_ticks']+metrics['transport_or_quiet_ticks']
    np.savez_compressed(stem.with_suffix('.npz'),initial_top=r.array_from_cells(top),decoded=np.array(decoded),expected=np.array(expected_frames),first_stored=snapshots[0],second_stored=snapshots[1])
    modules=(gpu,prefix,recurrent,suffix,f,c,r,q,p,native,word_workspace_source,word_allocation,small_holder_prefix_description,small_holder_packed,profile)
    paths=[Path(x.__file__) for x in modules]+[Path(gpu.__file__).with_suffix('.cu'),Path(prefix.__file__).with_suffix('.c'),Path(recurrent.__file__).with_suffix('.c'),Path('gacsca/fixed_rule/small_holder_control_world.py'),Path('gacsca/fixed_rule/small_holder_control_world.c'),Path(__file__),Path('experiments/fixed_rule/small_holder_execution.py')]
    result=dict(passed=True,physical_rule_description=f.self_description().digest(),successive_periods=2,physical_ticks=2*f.U,physical_sites=n*f.Q,periods=periods,probes=probes,metrics=metrics,gpu_run_seconds=gpu_seconds,seconds=time.perf_counter()-started,explicit_device_bytes=allocated,observed_process_gpu_mib=observed,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,one_resident_gpu_state_across_both_periods=True,host_upper_transitions_forbidden_during_advance=True,source_sha256={str(path):digest(path) for path in paths},binary_sha256=digest(gpu.library()._name),artifact_sha256=digest(stem.with_suffix('.npz')),limitations=['two complete periods through one simulation link, not two nested levels','canonical coherent physical states; suffix left Signal zero and uniform right Signal zero or one, with zero mail','physical flag wave follows its separately certified recurrence; no general noisy repair/amplification claim'])
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='complete',physical_time=2*f.U,seconds=result['seconds']))+'\n');print(json.dumps({key:value for key,value in result.items() if key not in ('probes','source_sha256')},indent=2),flush=True)


if __name__=='__main__':main()
