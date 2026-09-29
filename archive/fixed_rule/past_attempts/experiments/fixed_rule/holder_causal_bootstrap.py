"""Actual physical light-cone execution inside a recursively encoded hierarchy.

Executes complete lower work periods. The decoded observations are individual
controller ticks at the next level, not complete top-level macrosteps. A full
physical radius*time guard, not an assumed macro-locality bound, separates the
observed region from the artificial finite-ring seam. Host upper transitions are
used only as independent diagnostic expectations, never to advance the executor.
"""
import argparse,gc,hashlib,io,json,resource,tarfile,time
from pathlib import Path
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import holder_rule as f,holder_projected as r,holder_core as c,holder_program as p,holder_quotient as q,holder_initial as initial,holder_boundary as cap,holder_native as native,holder_snapshot as snapshot
from gacsca.fixed_rule.holder_omp_prefix_world import World as Prefix
from gacsca.fixed_rule.holder_omp_suffix_mixed import World as Suffix
from gacsca.fixed_rule.wordcode import Program


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def words(array,addresses):return np.ascontiguousarray(array[:,addresses,q.COL['data']])


def execute(output,periods=2,depth=2,interior_radius=7,benchmark_colonies=None):
    if not isinstance(periods,int) or periods<1 or not isinstance(depth,int) or depth<2 or interior_radius<0:raise ValueError('positive periods, depth >= 2 and nonnegative interior radius required')
    stem=Path(output);paths={ext:stem.with_suffix(ext) for ext in ('.json','.npz','.tar.gz','.progress.json')}
    if any(path.exists() for path in paths.values()):raise FileExistsError('preserve evidence')
    started=time.monotonic();g=p.layout();horizon=periods*f.U;required=7*horizon//f.Q+interior_radius+1
    guard=required if benchmark_colonies is None else benchmark_colonies//2
    if benchmark_colonies is not None and (benchmark_colonies<15 or benchmark_colonies%2!=1):raise ValueError('odd benchmark ring >=15 required')
    positions=np.arange(-guard,guard+1,dtype=np.int64);n=len(positions);certified=guard>=required
    physical_interval=(-guard*f.Q,(guard+1)*f.Q);observed=(-interior_radius*f.Q,(interior_radius+1)*f.Q)
    if certified:assert physical_interval[0]<observed[0]-7*horizon and observed[1]+7*horizon<physical_interval[1]
    top=(cap.cell(),);parents=tuple(initial.cell_at(top,depth-1,int(pos)) for pos in positions)
    original=r.array_from_cells(parents);original_raw=native.array_from_cells(tuple(r.lift(cell) for cell in parents));current=original_raw.copy()
    root=Path(__file__).resolve().parents[2];files=[]
    for directory,patterns in (('gacsca/fixed_rule',('*.py','*.c','*.cpp','*.h','*.cu')),('experiments/fixed_rule',('*.py',)),('tests/fixed_rule',('*.py',))):
        for pattern in patterns:files.extend((root/directory).glob(pattern))
    contents={str(path.relative_to(root)):path.read_bytes() for path in sorted(set(files))}
    with tarfile.open(paths['.tar.gz'],'x:gz') as archive:
        for name,data in contents.items():row=tarfile.TarInfo(name);row.size=len(data);archive.addfile(row,io.BytesIO(data))
    hashes={name:hashlib.sha256(data).hexdigest() for name,data in contents.items()};artifacts=dict(top=r.array_from_cells(top),parent_positions=positions,initial_parents=original,initial_raw=original_raw);stages=[];endpoints=[];binaries={};saved=None
    def progress(**values):
        values.update(seconds=time.monotonic()-started,max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss);paths['.progress.json'].write_text(json.dumps(values,indent=2)+'\n');print(json.dumps(values),flush=True)
    progress(status='initializing',colonies=n,physical_horizon=horizon,physical_light_cone_certified=certified,dense_logical_state_bytes=n*(g.computation_cells+5)*len(q.SCHEMA)*8)
    for period in range(periods):
        raw_cells=native.cells_from_array(current);expected=native.array_from_cells(tuple(r.lift(r.project(cell)) for cell in native.step_ring(raw_cells)))
        if np.any(expected[:,f.COL['f2']]):raise ValueError('this suffix executor requires computed left Signal zero')
        neighbors=np.stack([current[(np.arange(n)+j)%n] for j in range(-7,8)],axis=1).reshape(n,-1)
        array=snapshot.cold(parents) if saved is None else snapshot.expand(saved)
        # No upper-state replacement occurs at handoff: snapshot restores every
        # physical Data/Signal word and validates all omitted words as zero.
        with Prefix(array) as world:
            del array;gc.collect();binaries['prefix']=sha(world.lib._name)
            vote=c.VOTE_AGES[0]+g.schedule(g.entries[4],g.description_instruction)[0]
            delivery=c.VOTE_AGES[0]+g.timing_certificate()['stage3_last_delivery']
            milestones=(16*f.Q,48*f.Q,72*f.Q,vote,delivery,c.CAPTURE_AGE,96*f.Q-1)
            for target in milestones:
                metrics={}
                with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator during dynamics')),patch.object(f,'local_step',side_effect=AssertionError('host upper rule during dynamics')),patch.object(native,'step_ring',side_effect=AssertionError('host upper native during dynamics')):
                    while world.time<target:
                        row=world.run(min(f.Q,target-world.time))
                        for key,value in row.items():metrics[key]=metrics.get(key,0)+value
                        progress(status='running',period=period+1,component='prefix',physical_time=period*f.U+world.time)
                a=world._cores.reshape(n,g.computation_cells+5,len(q.SCHEMA))
                np.testing.assert_array_equal(words(a,g.info),current)
                if target in (16*f.Q,48*f.Q,72*f.Q):
                    stage=(16*f.Q,48*f.Q,72*f.Q).index(target);addresses=[g.history(stage,j,k) for j in range(-7,8) for k in range(f.FIELDS)];frame=words(a,addresses)
                    np.testing.assert_array_equal(frame,neighbors);artifacts[f'history_{period}_{stage}']=frame
                if target==vote:
                    frame=words(a,g.votes);np.testing.assert_array_equal(frame,neighbors);artifacts[f'vote_{period}']=frame
                if target>=delivery:np.testing.assert_array_equal(words(a,g.hold),expected)
                if target==96*f.Q-1:
                    saved=snapshot.collapse(world);np.testing.assert_array_equal(saved['signal'][:,-5:],expected[:,f.COL['f1'],None]*np.array([16,8,4,2,1]));assert not np.any(saved['signal'][:,:5])
                stages.append(dict(period=period+1,component='prefix',target=target,metrics=metrics))
        del world,a;gc.collect()
        array=snapshot.expand(saved)
        with Suffix(array) as world:
            del array;gc.collect();binaries['suffix']=sha(world.control.lib._name)
            for target in (98*f.Q,99*f.Q,112*f.Q,120*f.Q,f.U):
                metrics={}
                with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator during dynamics')),patch.object(f,'local_step',side_effect=AssertionError('host upper rule during dynamics')),patch.object(native,'step_ring',side_effect=AssertionError('host upper native during dynamics')):
                    while world.age<target:
                        row=world.run(min(f.Q,target-world.age))
                        for key,value in row.items():metrics[key]=metrics.get(key,0)+value
                        progress(status='running',period=period+1,component='suffix',physical_time=period*f.U+world.age)
                stages.append(dict(period=period+1,component='suffix',target=target,metrics=metrics))
            saved=snapshot.collapse(world.control);a=world.control._cores.reshape(n,g.computation_cells+5,len(q.SCHEMA));decoded=words(a,g.info)
            np.testing.assert_array_equal(decoded,expected);np.testing.assert_array_equal(words(a,g.hold),expected)
            artifacts[f'decoded_{period}']=decoded;artifacts[f'endpoint_data_{period}']=saved['data'];artifacts[f'endpoint_signal_{period}']=saved['signal'];artifacts[f'expected_{period}']=expected
            current=decoded.copy();center=r.project(f.decode_cell(current[guard].tolist()));neighbor=r.project(f.decode_cell(current[guard+1].tolist()))
            endpoints.append(dict(period=period+1,age=center.age,center_head=center.s2_head,right_head=neighbor.s2_head,primary_heads=[int(v) for v in current[guard-interior_radius:guard+interior_radius+1,f.COL['s2_head']]]))
            progress(status='period_complete',**endpoints[-1])
        del world,a;gc.collect()
    metrics={key:sum(stage['metrics'].get(key,0) for stage in stages) for key in ('physical_ticks','literal_core_ticks','quiet_ticks_skipped','scan_ticks_skipped','local_evaluations')}
    assert metrics['physical_ticks']==horizon==sum(metrics[key] for key in ('literal_core_ticks','quiet_ticks_skipped','scan_ticks_skipped'))
    if periods>=1:assert endpoints[0]['center_head']==1
    if periods>=2:assert endpoints[1]['center_head']==0 and endpoints[1]['right_head']==1
    with paths['.npz'].open('xb') as stream:np.savez_compressed(stream,**artifacts)
    result=dict(scope=__doc__,hierarchy_depth_in_initial_data=depth,full_configuration_sites=f.Q**depth,lower_colonies=n,physical_interval=physical_interval,observed_physical_interval=observed,interior_parent_radius=interior_radius,physical_horizon=horizon,physical_radius=7,physical_light_cone_certified=certified,benchmark_only=not certified,rule=r.identity(),top_level_macrosteps_completed=0,decoded_next_level_controller_ticks=periods,endpoint_observations=endpoints,metrics=metrics,stages=stages,binary_sha256=binaries,source_sha256=hashes,archive_sha256=sha(paths['.tar.gz']),artifact_sha256=sha(paths['.npz']),seconds=time.monotonic()-started,max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,limitation='A causal prefix of hierarchy dynamics; controller reset/motion, not a complete depth-two top macrostep or noise experiment. A benchmark ring does not have the physical causal-embedding guarantee.')
    paths['.json'].write_text(json.dumps(result,indent=2)+'\n');progress(status='complete',physical_time=horizon,physical_light_cone_certified=certified);return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);parser.add_argument('--periods',type=int,default=2);parser.add_argument('--depth',type=int,default=2);parser.add_argument('--interior-radius',type=int,default=7);parser.add_argument('--benchmark-colonies',type=int);args=parser.parse_args();execute(args.output,args.periods,args.depth,args.interior_radius,args.benchmark_colonies)
