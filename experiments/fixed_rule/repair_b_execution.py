"""Explicit candidate-B fixed-ROM retrieval/evaluation/delivery/capture prefix.

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
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import repair_b_rule as f,repair_b_projected as r,repair_b_program as p
from gacsca.fixed_rule.repair_b_prefix_world import World
from gacsca.fixed_rule.wordcode import Program


def initial_ring():
    cells=[r.Cell(address=100+i,age=1,f1=1,f2=1) for i in range(23)]
    # An actual simulated controller WRITE survives when structural Address does.
    cells[11]=replace(cells[11],head=1,phase=f.WRITE,rd=111,value=0x123456789ABCDEF0)
    # Mix the desired computed upper flags instead of hard-wiring a constant
    # packet pattern. Right Flag1 support ends in the center of this interval.
    for i in range(13,22):cells[i]=replace(cells[i],f1=0,f2=0)
    cells[17]=replace(cells[17],signal=31)
    return tuple(cells)


def words_at(core,addresses):
    g=p.layout();return np.stack([part[np.array(addresses),r.COL['data']] for part in core.reshape(-1,g.computation_cells,len(r.SCHEMA))])


def execute(stem):
    stem=Path(stem);paths={ext:stem.with_suffix(ext) for ext in ('.json','.npz','.tar.gz','.progress.json')}
    if any(path.exists() for path in paths.values()):raise FileExistsError('preserve evidence')
    root=Path(__file__).resolve().parents[2]
    files=sorted([*root.glob('gacsca/fixed_rule/*.py'),*root.glob('gacsca/fixed_rule/*.c'),*root.glob('gacsca/fixed_rule/*.cpp'),*root.glob('gacsca/fixed_rule/*.h'),*root.glob('tests/fixed_rule/*.py'),*root.glob('experiments/fixed_rule/*.py')])
    contents={str(path.relative_to(root)):path.read_bytes() for path in files};hashes={name:hashlib.sha256(data).hexdigest() for name,data in contents.items()}
    with tarfile.open(paths['.tar.gz'],'x:gz') as archive:
        for name,data in contents.items():info=tarfile.TarInfo(name);info.size=len(data);archive.addfile(info,io.BytesIO(data))
    g=p.layout();certificate=g.timing_certificate();assert certificate['fits'];top=initial_ring()
    old=np.array([f.encode_cell(r.lift(c)) for c in top],dtype=np.uint64)
    expected=np.array([f.encode_cell(r.lift(r.project(c))) for c in f.step_ring(tuple(r.lift(c) for c in top))],dtype=np.uint64)
    neighborhoods=np.stack([old[(np.arange(len(top))+j)%len(top)] for j in range(-5,6)],axis=1).reshape(len(top),-1)
    assert int(expected[11,f.COL['data']])==0x123456789ABCDEF0
    repair=g.schedule(0,14)[0]
    arrival=f.VOTE_AGES[0]+certificate['stage3_last_delivery']
    times=(repair,16*f.Q,48*f.Q,70*f.Q,70*f.Q+1,arrival, f.CAPTURE_AGE-1,f.CAPTURE_AGE,80*f.Q,96*f.Q-1)
    metrics=dict(physical_ticks=0,literal_core_ticks=0,quiet_ticks_skipped=0,scan_ticks_skipped=0,local_evaluations=0)
    histories=[];history_keys=[];votes=[];holds=[];buffers=[];signals=[];repairs=[];probes=[];started=time.monotonic()
    with World.encode(top) as world:
        binary=hashlib.sha256(Path(world.lib._name).read_bytes()).hexdigest()
        for target in times:
            # If the executor substituted host transition calls this fails.
            with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator during physical dynamics')),patch.object(f,'local_step',side_effect=AssertionError('host upper transition during physical dynamics')):
                while world.time<target:
                    row=world.run(min(5000000,target-world.time))
                    for key,value in row.items():metrics[key]+=value
                    paths['.progress.json'].write_text(json.dumps(dict(status='running',physical_time=world.time,elapsed_seconds=time.monotonic()-started,**metrics),indent=2)+'\n')
            core=world.cores;probe=dict(time=target,pending=world.pending)
            np.testing.assert_array_equal(words_at(core,g.info),old)
            if target==repair:repairs.append(words_at(core,g.info))
            if target in (16*f.Q,48*f.Q,70*f.Q):
                last={16*f.Q:0,48*f.Q:1,70*f.Q:2}[target]
                for history in range(last+1):
                    addresses=[g.history(history,j,k) for j in range(-5,6) for k in range(f.FIELDS)]
                    raw=words_at(core,addresses);np.testing.assert_array_equal(raw,neighborhoods);histories.append(raw);history_keys.append((target,history))
                probe['histories_match']=True
            if target==70*f.Q+1:
                raw=words_at(core,g.votes);np.testing.assert_array_equal(raw,neighborhoods);votes.append(raw);probe['vote_matches']=True
            if target>=arrival:
                raw=words_at(core,g.hold);np.testing.assert_array_equal(raw,expected);holds.append(raw);probe['hold_matches']=True
                payload=np.array([[world.cell(c,a).data for a in (*range(1,6),*range(f.Q-5,f.Q))] for c in range(len(top))],dtype=np.uint64)
                want=np.repeat(expected[:,[f.COL['f2'],f.COL['f1']]],5,axis=1)
                np.testing.assert_array_equal(payload,want);buffers.append(payload);probe['computed_flag_payloads_delivered']=True
                signal=np.array([[world.cell(c,a).signal for a in (*range(1,6),*range(f.Q-5,f.Q))] for c in range(len(top))],dtype=np.uint64)
                if target<f.CAPTURE_AGE:np.testing.assert_array_equal(signal,np.zeros_like(signal))
                else:
                    wanted=np.concatenate((expected[:,f.COL['f2'],None]*np.array([16,8,4,2,1]),expected[:,f.COL['f1'],None]*np.array([16,8,4,2,1])),axis=1)
                    np.testing.assert_array_equal(signal,wanted);probe['computed_flags_captured']=True
                signals.append(signal)
                assert world.pending==0
            probes.append(probe);print(json.dumps(probe),flush=True)
        assert np.all(world.stored[:,[r.COL[n] for n in ('f1','f2','wf1','wf2')]]==0)
        with paths['.npz'].open('xb') as stream:
            np.savez_compressed(stream,initial_top=r.array_from_cells(top),initial_lifted=old,expected_hold=expected,repair_frames=np.stack(repairs),history_frames=np.stack(histories),history_keys=np.array(history_keys),vote_frames=np.stack(votes),hold_frames=np.stack(holds),buffer_frames=np.stack(buffers),signal_frames=np.stack(signals),stored_final=world.stored,rom=r.rom())
    assert sum(metrics[k] for k in ('literal_core_ticks','quiet_ticks_skipped','scan_ticks_skipped'))==metrics['physical_ticks']==96*f.Q-1
    result=dict(scope=__doc__,rule=r.identity(),timing=certificate,metrics=metrics,seconds=time.monotonic()-started,probes=probes,represented_cells=len(top),physical_sites=len(top)*f.Q,stored_sites=len(top)*(g.computation_cells+5),source_sha256=hashes,binary_sha256=binary,artifact_sha256=hashlib.sha256(paths['.npz'].read_bytes()).hexdigest(),archive_sha256=hashlib.sha256(paths['.tar.gz'].read_bytes()).hexdigest())
    paths['.json'].write_text(json.dumps(result,indent=2)+'\n');paths['.progress.json'].write_text(json.dumps(dict(status='complete',physical_time=metrics['physical_ticks']),indent=2)+'\n')
    print(json.dumps(dict(status='complete',seconds=result['seconds'],metrics=metrics)),flush=True)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    execute(parser.parse_args().output)
