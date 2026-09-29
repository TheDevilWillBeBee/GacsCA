"""Bounded actual GPU replay: full raw defects, then lossless flag attachment."""
import argparse
import json
from pathlib import Path
import resource
import time
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_resident_general as general,retimed_holder_general_faults as faults
from gacsca.fixed_rule import retimed_holder_resident_period as period,retimed_holder_cuda_general_snapshot as snapshots
from gacsca.fixed_rule import retimed_holder_contextual_flags as oldview,retimed_holder_early_flag_snapshot as view
from gacsca.fixed_rule import retimed_holder_early_flags_gpu as early,retimed_holder_literal_cone as cone
from gacsca.fixed_rule import retimed_holder_terminal_reference as terminal
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha
from experiments.fixed_rule.retimed_holder_cuda_encoded_repair import forbidden


def restore(state):
    assert int(state['age'])==0
    for key in ('active_rows','counts','flags','signals'):assert not np.any(state[key]),key
    world=general.World((r.Cell(),)*len(state['bank']),device_budget=16*1024**2)
    try:
        for col in range(len(state['bank'])):
            bank=np.ascontiguousarray(state['bank'][col])
            if world._core.lib.rp_bank(world._core.handle,col,period.pointer(bank)):raise RuntimeError('complete initial bank upload failed')
        world._core.time=int(state['time'])
        got=snapshots.snapshot(world)
        for key in state:np.testing.assert_array_equal(got[key],state[key],err_msg=key)
        return world
    except BaseException:
        world.close();raise


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    out=Path(parser.parse_args().output);artifact=out.with_suffix('.npz')
    if out.exists() or artifact.exists():raise FileExistsError(out)
    started=time.perf_counter();root=Path('figs/fixed_rule')
    names=('wide_next_periods_3_v2','residual_reactivation_audit_v3','fresh_geometry_recovery_128_v1','fresh_full_repair_v2','full_ring_repair_v1')
    paths={name:root/('retimed_holder_'+name+'.json') for name in names}
    docs={name:json.loads(path.read_text()) for name,path in paths.items()}
    for name,doc in docs.items():
        assert doc.get('passed',doc.get('completed')) is True
        assert sha(paths[name].with_suffix('.npz'))==doc['artifact_sha256']
    begin,end=28,45;shift=begin*f.Q;n=end-begin;anchor=8*f.Q+30960
    with np.load(paths['wide_next_periods_3_v2'].with_suffix('.npz'),allow_pickle=False) as old:
        state={key:old['period3_'+key][begin:end].copy() for key in ('bank','active_rows','counts','signals')}
        state['flags']=old['period3_flags'][begin*f.Q//64:end*f.Q//64].copy()
        for key in ('age','time'):state[key]=old['period3_'+key]
        residue_positions=old['retained_positions']-shift;residue_values=old['retained_values']
    # Full terminal-bank context, not just selected Info words, matches this
    # 17-colony initial window. All31 parents supply its complete radius7 halo.
    with np.load(paths['full_ring_repair_v1'].with_suffix('.npz'),allow_pickle=False) as old:
        parents=old['period2_full_healthy'][np.arange(9550,9581)]
    derived=terminal.terminal(tuple(r.project(f.decode_cell(row)) for row in parents))
    np.testing.assert_array_equal(state['bank'],derived['committed_bank'][7:24])
    np.testing.assert_array_equal(state['signals'],derived['signals'][7:24])
    assert min(anchor,n*f.Q-1-anchor)>14*16989+5
    with np.load(paths['residual_reactivation_audit_v3'].with_suffix('.npz'),allow_pickle=False) as old:
        marks=[(int(t),int(pos)-shift,row.copy()) for t,pos,row in zip(old['fault_times'],old['fault_positions'],old['fault_replacements'])]
        first={key:old[key] for key in old.files if key.startswith('tick')}
    with np.load(paths['fresh_geometry_recovery_128_v1'].with_suffix('.npz'),allow_pickle=False) as old:
        prefix_positions=old['final_positions']-shift;prefix_actual=old['final_actual']
    saved={};observations=[]
    def save_state(label,state):
        for key,value in state.items():saved[label+'_'+key]=value.copy()
    with restore(state) as background,restore(state) as healthy,faults.World(background) as actual:
        peak=background.device_bytes+healthy.device_bytes+actual.device_bytes+32*n*(f.Q//64)+2*n+8*n*(9916+32*6+1)
        assert peak<64*1024**2,peak
        sites=np.arange(int(residue_positions[0])-2,int(residue_positions[-1])+3)
        raw=cone.BankImage(state['bank'],state['signals']).cells(sites)
        for pos,value in zip(residue_positions,residue_values):
            for d in f.OFFSETS:raw[sites+d==pos,f.COL[f's{d+2}_data']]=value
        actual.inject({int(pos):r.project(f.decode_cell(row)) for pos,row in zip(sites,raw)})
        initial_read=np.array([f.encode_cell(cell) for cell in actual.read(tuple(map(int,sites)))],dtype=np.uint64)
        np.testing.assert_array_equal(initial_read,raw)
        maximum=0;evaluations=0
        with forbidden():
            for tick in range(640):
                replacements={pos:r.project(f.decode_cell(row)) for t,pos,row in marks if t==tick}
                if replacements:actual.inject(replacements)
                metric=actual.step();maximum=max(maximum,len(actual.positions));evaluations+=metric['full_local_evaluations']
                if tick+1 in (1,2,3,4,5,128,256,512,640):
                    snap,ep,ev=oldview.capture(actual);image=view.View(snap,ep,ev)
                    if tick<5:
                        selected=first[f'tick{tick+1}_positions']-shift
                        np.testing.assert_array_equal(image.cells(selected),first[f'tick{tick+1}_actual'])
                    if tick+1==128:np.testing.assert_array_equal(image.cells(prefix_positions),prefix_actual)
                    if tick+1==640:
                        save_state('before_attachment',snap);saved['before_attachment_positions']=ep;saved['before_attachment_values']=ev
                    row=dict(tick=tick+1,raw_exception_sites=len(ep),seconds=time.perf_counter()-started)
                    observations.append(row);print(json.dumps(row),flush=True)
            attachment=view.attach(actual)
            assert not actual.positions,'nonflag damage must remain represented, not discarded'
            print(json.dumps(dict(attachment=attachment,seconds=time.perf_counter()-started)),flush=True)
            attached=snapshots.snapshot(background);save_state('attached',attached)
            for target in (1024,10321,16988,16989):
                actual.advance(4*f.U+target-actual.time,absorb_data=False,absorb_flags=False)
                snap=snapshots.snapshot(background);save_state(f'tick{target}',snap)
                counts=[sum(int(x).bit_count() for x in snap['flags'][:,k]) for k in range(2)]
                observations.append(dict(tick=target,flag_bits=counts,exceptions=len(actual.positions),seconds=time.perf_counter()-started))
                print(json.dumps(observations[-1]),flush=True)
            healthy.advance(16989,extra_device_budget=16*1024**2)
        final=snapshots.snapshot(background);reference=snapshots.snapshot(healthy)
        for key in final:np.testing.assert_array_equal(final[key],reference[key],err_msg=key)
        av,hv=view.View(final),view.View(reference);raw_checked=0
        for col in range(n):
            sites=np.arange(col*f.Q,(col+1)*f.Q)
            np.testing.assert_array_equal(av.cells(sites),hv.cells(sites));raw_checked+=len(sites)*f.FIELDS
        assert not actual.positions and not np.any(final['flags'])
        save_state('final',final);save_state('healthy_final',reference)
    np.savez_compressed(artifact,**saved)
    sources=(Path(__file__),Path(view.__file__),Path(early.__file__),Path(faults.__file__),Path(faults.old.__file__),Path(faults.old.__file__).with_suffix('.cu'),Path(general.__file__),Path(period.__file__),Path(period.__file__).with_suffix('.cu'))
    result=dict(passed=True,physical_ticks=16989,colonies=n,complete_initial_bank_words=state['bank'].size,
                full_rule_exception_ticks=640,full_local_GPU_evaluations=evaluations,maximum_exception_sites=maximum,
                same_time_attachment=attachment,post_attachment_GPU_physical_ticks=16349,
                final_complete_raw_words_compared=raw_checked,old_residues_erased=True,complete_rejoin=True,
                exact_scalar_native_prefix_matched=True,full_ring_initial_window_verified=True,
                sufficient_radius_seven_double_cone_margin=True,
                explicit_GPU_peak_bound_bytes=peak,observations=observations,
                descriptor_sha256=f.self_description().digest(),
                input_sha256={str(path):sha(path) for path in paths.values()},source_sha256={str(path):sha(path) for path in sources},
                binary_sha256={str(Path(lib._name)):sha(lib._name) for lib in (early.library(),faults.library(),general.library())},
                artifact_sha256=sha(artifact),seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                scope='Executed actual full raw GPU exceptions through640, losslessly attached '
                      'actual canonical flags, then evolved all represented physical fields '
                      'on GPU to complete rejoin at16989. Uses existing validated canonical '
                      'procedure/flag factorization after attachment, not a dense literal '
                      'full-ring run. No host-simulated transition or installed reference state.')
    with out.open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='observations'},indent=2),flush=True)


if __name__=='__main__':main()
