"""Redundant holder fixed-ROM retrieval/evaluation/delivery/capture prefix.

Stops at Age 96Q-1 before Wf appears. No macrostep commit or full-period claim.
"""
import argparse
from dataclasses import replace
import hashlib
import io
import json
from pathlib import Path
import tarfile
import time
import resource
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import parallel_holder_rule as f,parallel_holder_projected as r,parallel_holder_program as p,parallel_holder_core as c,parallel_holder_quotient as q,parallel_holder_initial as initial
from gacsca.fixed_rule.parallel_holder_prefix_world import World
from gacsca.fixed_rule.wordcode import Program


def initial_ring():
    logical=[c.Cell(**r.record(100+i),address=100+i,age=1,f1=1) for i in range(15)]
    logical[7]=replace(logical[7],head=1,phase=c.WRITE,rd=107,value=0x123456789ABCDEF0)
    return tuple(initial.coherent_cell(lambda pos:logical[pos%15],i) for i in range(15))


def words_at(core,addresses):
    g=p.layout();return np.stack([part[np.array(addresses),q.COL['data']] for part in core.reshape(-1,g.computation_cells,len(q.SCHEMA))])


def execute(stem):
    stem=Path(stem);paths={ext:stem.with_suffix(ext) for ext in ('.json','.npz','.tar.gz','.progress.json')}
    if any(path.exists() for path in paths.values()):raise FileExistsError('preserve evidence')
    root=Path(__file__).resolve().parents[2]
    files=sorted([*root.glob('gacsca/fixed_rule/*.py'),*root.glob('gacsca/fixed_rule/*.c'),*root.glob('gacsca/fixed_rule/*.cpp'),*root.glob('gacsca/fixed_rule/*.h'),*root.glob('gacsca/fixed_rule/*.cu'),*root.glob('tests/fixed_rule/*.py'),*root.glob('experiments/fixed_rule/*.py')])
    contents={str(path.relative_to(root)):path.read_bytes() for path in files};hashes={name:hashlib.sha256(data).hexdigest() for name,data in contents.items()}
    with tarfile.open(paths['.tar.gz'],'x:gz') as archive:
        for name,data in contents.items():info=tarfile.TarInfo(name);info.size=len(data);archive.addfile(info,io.BytesIO(data))
    g=p.layout();certificate=g.timing_certificate();assert certificate['fits'];top=initial_ring()
    vote_complete=c.VOTE_AGES[0]+g.schedule(g.entries[4],g.description_instruction)[0]
    old=np.array([f.encode_cell(r.lift(c)) for c in top],dtype=np.uint64)
    expected=np.array([f.encode_cell(r.lift(r.project(c))) for c in f.step_ring(tuple(r.lift(c) for c in top))],dtype=np.uint64)
    neighborhoods=np.stack([old[(np.arange(len(top))+j)%len(top)] for j in range(-7,8)],axis=1).reshape(len(top),-1)
    assert int(expected[7,f.COL['s2_data']])==0x123456789ABCDEF0
    assert np.all(expected[:,f.COL['f1']]==1) and not np.any(expected[:,f.COL['f2']])
    repair=g.schedule(0,next(i for i,op in enumerate(g.instructions) if op.kind==c.LIT and op.a==0 and op.d==g.memory_count-6)+1)[0]
    arrival=c.VOTE_AGES[0]+certificate['stage3_last_delivery']
    times=tuple(sorted(set((repair,16*f.Q,48*f.Q,72*f.Q,72*f.Q+1,vote_complete,arrival,c.CAPTURE_AGE-1,c.CAPTURE_AGE,80*f.Q,96*f.Q-1))))
    metrics=dict(physical_ticks=0,literal_core_ticks=0,quiet_ticks_skipped=0,scan_ticks_skipped=0,local_evaluations=0)
    histories=[];history_keys=[];votes=[];holds=[];buffers=[];signals=[];repairs=[];probes=[];started=time.monotonic()
    with World.encode(top) as world:
        binary=hashlib.sha256(Path(world.lib._name).read_bytes()).hexdigest()
        for target in times:
            # If the executor substituted host transition calls this fails.
            with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator during physical dynamics')),patch.object(f,'local_step',side_effect=AssertionError('host upper transition during physical dynamics')):
                while world.time<target:
                    row=world.run(min(f.Q,target-world.time))
                    for key,value in row.items():metrics[key]+=value
                    paths['.progress.json'].write_text(json.dumps(dict(status='running',physical_time=world.time,elapsed_seconds=time.monotonic()-started,**metrics),indent=2)+'\n')
            core=world.cores;probe=dict(time=target,pending=world.pending)
            np.testing.assert_array_equal(words_at(core,g.info),old)
            if target==repair:repairs.append(words_at(core,g.info))
            if target in (16*f.Q,48*f.Q,72*f.Q):
                last={16*f.Q:0,48*f.Q:1,72*f.Q:2}[target]
                for history in range(last+1):
                    addresses=[g.history(history,j,k) for j in range(-7,8) for k in range(f.FIELDS)]
                    raw=words_at(core,addresses);np.testing.assert_array_equal(raw,neighborhoods);histories.append(raw);history_keys.append((target,history))
                probe['histories_match']=True
            if target==72*f.Q+1:
                np.testing.assert_array_equal(words_at(core,g.votes),neighborhoods)
            if target==vote_complete:
                raw=words_at(core,g.votes);np.testing.assert_array_equal(raw,neighborhoods);votes.append(raw);probe['vote_matches']=True
            if target>=arrival:
                raw=words_at(core,g.hold);np.testing.assert_array_equal(raw,expected);holds.append(raw);probe['hold_matches']=True
                payload=np.array([[world.cell(c,a).s2_data for a in (*range(1,6),*range(f.Q-5,f.Q))] for c in range(len(top))],dtype=np.uint64)
                want=np.repeat(expected[:,[f.COL['f2'],f.COL['f1']]],5,axis=1)
                np.testing.assert_array_equal(payload,want);buffers.append(payload);probe['computed_flag_payloads_delivered']=True
                signal=np.array([[world.cell(c,a).signal for a in (*range(1,6),*range(f.Q-5,f.Q))] for c in range(len(top))],dtype=np.uint64)
                if target<c.CAPTURE_AGE:np.testing.assert_array_equal(signal,np.zeros_like(signal))
                else:
                    wanted=np.concatenate((expected[:,f.COL['f2'],None]*np.array([16,8,4,2,1]),expected[:,f.COL['f1'],None]*np.array([16,8,4,2,1])),axis=1)
                    np.testing.assert_array_equal(signal,wanted);probe['computed_flags_captured']=True
                signals.append(signal)
                assert world.pending==0
            probes.append(probe);print(json.dumps(probe),flush=True)
        assert np.all(world.stored[:,[q.COL[n] for n in ('f1','f2','wf1','wf2')]]==0)
        with paths['.npz'].open('xb') as stream:
            np.savez_compressed(stream,initial_top=r.array_from_cells(top),initial_lifted=old,expected_hold=expected,repair_frames=np.stack(repairs),history_frames=np.stack(histories),history_keys=np.array(history_keys),vote_frames=np.stack(votes),hold_frames=np.stack(holds),buffer_frames=np.stack(buffers),signal_frames=np.stack(signals),logical_stored_final=world.stored,rom=p.base_rom())
    assert sum(metrics[k] for k in ('literal_core_ticks','quiet_ticks_skipped','scan_ticks_skipped'))==metrics['physical_ticks']==96*f.Q-1
    result=dict(host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope=__doc__,rule=r.identity(),timing=certificate,metrics=metrics,seconds=time.monotonic()-started,probes=probes,represented_cells=len(top),physical_sites=len(top)*f.Q,stored_sites=len(top)*(g.computation_cells+5),representation="coherent fivefold physical state; logical procedure records plus exact ballistic events",source_sha256=hashes,binary_sha256=binary,artifact_sha256=hashlib.sha256(paths['.npz'].read_bytes()).hexdigest(),archive_sha256=hashlib.sha256(paths['.tar.gz'].read_bytes()).hexdigest())
    paths['.json'].write_text(json.dumps(result,indent=2)+'\n');paths['.progress.json'].write_text(json.dumps(dict(status='complete',physical_time=metrics['physical_ticks']),indent=2)+'\n')
    print(json.dumps(dict(status='complete',seconds=result['seconds'],metrics=metrics)),flush=True)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    execute(parser.parse_args().output)
