"""Continue all surviving forcing-sweep defects with exact actual flag dynamics."""
import argparse,json,resource,time
from contextlib import ExitStack
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r,retimed_holder_program as p
from gacsca.fixed_rule import retimed_holder_resident_general as general,retimed_holder_general_faults as faults,retimed_holder_cuda_general_snapshot as snapshots
from experiments.fixed_rule.run_retimed_holder_cpu_periods import parents
from experiments.fixed_rule.retimed_holder_cuda_encoded_repair import forbidden,raw
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha


def equal(a,b):
    for key in a:np.testing.assert_array_equal(a[key],b[key],err_msg=key)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output);artifact=out.with_suffix('.npz')
    if out.exists() or artifact.exists():raise FileExistsError(out)
    started=time.perf_counter();prior=Path('figs/fixed_rule/retimed_holder_forcing_fault_sweep_v1.json');receipt=json.loads(prior.read_text());assert receipt['passed']
    assert sha(prior.with_suffix('.npz'))==receipt['artifact_sha256'];selected=[x for x in receipt['cases'] if not x['rejoined']];assert len(selected)==4
    age=f.WF_START+100;target=f.WF_START+12000;assert all(x['age']==age for x in selected)
    saved={};results=[];peak=0
    with np.load(prior.with_suffix('.npz'),allow_pickle=False) as z,general.World(parents(1),device_budget=32*1024**2) as healthy:
        with forbidden():healthy.advance(age+12,extra_device_budget=32*1024**2)
        reference12=snapshots.snapshot(healthy)
        for key,value in reference12.items():saved['healthy12_'+key]=value
        with forbidden():healthy.advance(target-healthy.time,extra_device_budget=32*1024**2)
        terminal=snapshots.snapshot(healthy)
        for key,value in terminal.items():saved['healthy_terminal_'+key]=value
        for case in selected:
            index=case['index'];prefix=f'case{index}';positions=tuple(map(int,z[prefix+'_positions']))
            with general.World(parents(1),device_budget=32*1024**2) as background,ExitStack() as stack:
                with forbidden():background.advance(age,extra_device_budget=32*1024**2)
                actual=stack.enter_context(faults.World(background))
                np.testing.assert_array_equal(raw(actual.read(positions)),z[prefix+'_before'])
                actual.inject({pos:r.project(f.decode_cell(row)) for pos,row in zip(positions,z[prefix+'_injected'])})
                with forbidden():metrics=actual.advance(12,absorb_data=False,absorb_flags=False,literal_budget=12)
                last=tuple(map(int,z[prefix+'_last_positions']));assert actual.positions==last
                np.testing.assert_array_equal(raw(actual.read(last)),z[prefix+'_last_actual'])
                before=raw(actual.read(last));rebased=actual.absorb_flags();assert rebased['flag_fields']==1 and not actual.positions
                np.testing.assert_array_equal(raw(actual.read(last)),before)
                actual12=snapshots.snapshot(background)
                for key in actual12:
                    if key!='flags':np.testing.assert_array_equal(actual12[key],reference12[key],err_msg=key)
                xor=actual12['flags']^reference12['flags'];bits=sum(int(x).bit_count() for x in xor.ravel());assert bits==1
                for key,value in actual12.items():saved[prefix+'_after12_'+key]=value
                with forbidden():later=actual.advance(target-actual.time,absorb_data=False,absorb_flags=False)
                assert not actual.positions;following=snapshots.snapshot(background);equal(following,terminal)
                for key,value in following.items():saved[prefix+'_terminal_'+key]=value
                peak=max(peak,healthy.device_bytes+background.device_bytes+actual.device_bytes+8*(p.layout().memory_count+5+32*6+1));assert peak<64*1024**2
                row=dict(case=index,kind=case['kind'],site_count=case['site_count'],fault_time=age,wrong_flag_bits_at12=bits,rebase_preserves_actual_state=True,complete_rejoin_by=target,literal_metrics=metrics,subsequent_metrics=later)
                results.append(row);print(json.dumps(dict(case=index,complete_rejoin_by=target,seconds=time.perf_counter()-started)),flush=True)
    np.savez_compressed(artifact,**saved)
    result=dict(passed=True,cases=results,seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,explicit_GPU_peak_bound_bytes=peak,source_sweep_sha256=sha(prior),artifact_sha256=sha(artifact),source_sha256={str(x):sha(x) for x in (Path(__file__),Path(general.__file__),Path(faults.__file__),Path(snapshots.__file__))},descriptor_sha256=f.self_description().digest(),scope='All four surviving forcing-sweep defects followed through twelve literal full-G ticks, exact same-state flag rebase and actual GPU flag evolution to complete rejoin. No healthy successor installation or unsupported noiseless endpoint shortcut.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
