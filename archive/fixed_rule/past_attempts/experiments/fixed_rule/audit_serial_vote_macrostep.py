"""Independent full-state boundary audit of one candidate-B macrostep.

Replays the controller quotient, checks all stored flags against whole-ring RLE,
and checks complete local transitions around every RLE/colony boundary at saved
frames. The long flag trajectory uses the separately tested packed executor;
it is not independently rerun here. Canonical unforced clearing has a direct
Q-tick bound, documented in REPAIR_B.md.
"""
import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tarfile
import time
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import serial_vote_rule as f,serial_vote_projected as r,serial_vote_program as p,serial_vote_native as native
from gacsca.fixed_rule.serial_vote_control_world import World as Control
from gacsca.fixed_rule.serial_vote_composed_world import World as Complete
from gacsca.fixed_rule.serial_vote_flags import World as Flags
from gacsca.fixed_rule.wordcode import Program


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit(stem,output):
    stem,output=Path(stem),Path(output)
    if output.exists():raise FileExistsError('preserve evidence')
    started=time.monotonic();root=Path(__file__).resolve().parents[2];x=json.loads(stem.with_suffix('.json').read_text())
    assert sha(stem.with_suffix('.npz'))==x['artifact_sha256'] and sha(stem.with_suffix('.tar.gz'))==x['archive_sha256']
    with tarfile.open(stem.with_suffix('.tar.gz')) as archive:
        assert set(archive.getnames())==set(x['source_sha256'])
        for name,digest in x['source_sha256'].items():assert sha(root/name)==digest==hashlib.sha256(archive.extractfile(name).read()).hexdigest(),name
    assert x['rule']==json.loads(json.dumps(r.identity()))
    prefix=Path(x['input_prefix']);assert sha(prefix.with_suffix('.json'))==x['input_json_sha256'] and sha(prefix.with_suffix('.npz'))==x['input_artifact_sha256']
    with np.load(prefix.with_suffix('.npz'),allow_pickle=False) as a:initial=a['stored_final'];top=r.cells_from_array(a['initial_top']);old=a['initial_lifted']
    with np.load(stem.with_suffix('.npz'),allow_pickle=False) as a:saved={name:a[name] for name in a.files}
    full=f.step_ring(tuple(r.lift(c) for c in top));assert full==native.cells_from_array(native.dense_step(native.array_from_cells(tuple(r.lift(c) for c in top))))
    described=tuple(f.decode_cell(f.self_description().evaluate(tuple(word for j in range(-5,6) for word in f.encode_cell(r.lift(top[(i+j)%len(top)]))))) for i in range(len(top)))
    assert full==described;expected=tuple(r.project(c) for c in full);raw=np.array([f.encode_cell(r.lift(c)) for c in expected],dtype=np.uint64)
    np.testing.assert_array_equal(saved['decoded'],r.array_from_cells(expected));np.testing.assert_array_equal(saved['lifted'],raw)
    np.testing.assert_array_equal(saved['initial_top'],r.array_from_cells(top));np.testing.assert_array_equal(saved['initial_lifted'],old)
    neighbors=np.stack([old[(np.arange(len(top))+j)%len(top)] for j in range(-5,6)],axis=1).reshape(len(top),-1)
    for a in saved['votes']:np.testing.assert_array_equal(a,neighbors)
    assert saved['votes'].shape==(1,len(top),11*f.FIELDS)
    for a in saved['holds']:np.testing.assert_array_equal(a,raw)
    assert saved['holds'].shape==(3,len(top),f.FIELDS)
    g=p.layout();n=len(top);epoch=96*f.Q-1;checks=0;sites_checked=0
    a=initial.reshape(n,g.computation_cells+5,len(r.SCHEMA));left=((a[:,3,r.COL['signal']]>>np.uint64(2))&1).tolist();right=((a[:,g.computation_cells+2,r.COL['signal']]>>np.uint64(2))&1).tolist()
    vote_complete=112*f.Q+g.schedule(g.entries[4],g.description_instruction)[0]
    ages=(96*f.Q,98*f.Q,99*f.Q,104*f.Q,112*f.Q,112*f.Q+1,vote_complete,120*f.Q,f.U-1,f.U)
    with Control(initial) as control:
        assert sha(control.lib._name)==x['binary_sha256']['controller']
        for age in ages:
            with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator')),patch.object(f,'local_step',side_effect=AssertionError('host transition')):control.run(age-epoch-control.time)
            runs=saved['flags_age'+str(age)]
            assert runs.ndim==2 and runs.shape[1]==3 and runs.dtype==np.uint64
            assert all(int(a)<int(b) for a,b in zip([0,*runs[:-1,0]],runs[:,0])) and int(runs[-1,0])==n*f.Q//64
            if age>=99*f.Q:np.testing.assert_array_equal(runs,np.array([(n*f.Q//64,0,0)],dtype=np.uint64))
            if age<f.U:
                with Complete(control.stored,flag_runs=runs) as complete:
                    assert sha(complete.flags.lib._name)==x['binary_sha256']['flags']
                    positions={c*f.Q+address for c in range(n) for address in (0,3,g.info[0],g.hold[0],g.computation_cells,f.Q//2,f.Q-6,f.Q-3,f.Q-1)}
                    for end in runs[:,0]:
                        for delta in (-6,-1,0,1,5):positions.add((int(end)*64+delta)%(n*f.Q))
                    wanted={position:r.project(native.local_step(tuple(r.lift(complete.cell(*divmod((position+j)%(n*f.Q),f.Q))) for j in range(-5,6)))) for position in positions}
                    # Full stored-state reconstruction checked independently
                    # below; do not trust the same composition method twice.
                    complete.run(1)
                    for position,value in wanted.items():assert complete.cell(*divmod(position,f.Q))==value,(age,position)
                    checks+=len(wanted)
            name='stored_age'+str(age)
            if name in saved:
                expected_stored=control.stored;addresses=[*range(g.computation_cells),*range(f.Q-5,f.Q)];row=0
                for c in range(n):
                    for j,address in enumerate(addresses):
                        pos=c*f.Q+address
                        while int(runs[row,0])*64<=pos:row+=1
                        for field,flag in enumerate(('f1','f2')):expected_stored[c*len(addresses)+j,r.COL[flag]]=(int(runs[row,field+1])>>(pos%64))&1
                # All stored frames begin at cutoff or later, so Wf is zero.
                assert age>=98*f.Q
                np.testing.assert_array_equal(saved[name],expected_stored);sites_checked+=len(expected_stored)
            info=control.cores.reshape(n,g.computation_cells,len(r.SCHEMA))[:,np.array(g.info),r.COL['data']]
            np.testing.assert_array_equal(info,raw if age==f.U else old)
        np.testing.assert_array_equal(saved['stored_final'],control.stored)
        assert control.decode()==expected and control.pending==0
    final=saved['stored_final'];assert not np.any(final[:,[r.COL[name] for name in ('f1','f2','wf1','wf2','head')]])
    assert np.all(final[:,r.COL['age']]==0)
    assert x['prefix_ticks']+x['suffix_ticks']==x['complete_physical_macrostep_ticks']==f.U
    assert x['controller_metrics']['physical_ticks']==x['final_flags']['time']==32*f.Q+1
    assert x['final_flags']['literal_ticks']+x['final_flags']['quiet_ticks']==32*f.Q+1
    result=dict(passed=True,verifier_sha256=sha(__file__),source_files=len(x['source_sha256']),complete_physical_macrosteps=1,physical_ticks=f.U,decoded_raw_words=len(top)*f.FIELDS,complete_scalar_native_description_agreement=True,all_stored_fields_checked_sites=sites_checked,complete_native_local_comparisons=checks,physical_flags_zero_at_commit=True,raw_controller_vote_hold_commit_match=True,seconds=time.monotonic()-started,artifact_sha256=x['artifact_sha256'],limitation='candidate-B canonical noiseless one-macrostep result; full spatial repair, organized termination, deeper dynamics and noise robustness remain unproved')
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',required=True,type=Path);parser.add_argument('--output',required=True,type=Path);a=parser.parse_args();audit(a.input,a.output)
