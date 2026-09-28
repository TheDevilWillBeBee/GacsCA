"""Two physical periods of the ordinary cap, with one physical Info-bit fault.

Two represented cap cells start at Age 1; only the second lower colony receives
one bit flip in the physical Data word encoding upper Data. The same fixed rule
runs everywhere. This is a negative repair experiment, not a robustness claim.
"""
import argparse,hashlib,io,json,tarfile,time
from pathlib import Path
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import repair_b_rule as f,repair_b_projected as r,repair_b_program as p,repair_b_initial as initial
from gacsca.fixed_rule.repair_b_prefix_world import World as Fresh
from gacsca.fixed_rule.repair_b_recurrent_prefix_world import World as Recurrent
from gacsca.fixed_rule.repair_b_composed_world import World as Suffix
from gacsca.fixed_rule.wordcode import Program


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def execute(stem):
    stem=Path(stem)
    if any(stem.with_suffix(e).exists() for e in ('.json','.npz','.tar.gz')):raise FileExistsError('preserve evidence')
    root=Path(__file__).resolve().parents[2];g=p.layout();top=initial.terminal_data(age=1)*2
    files=sorted(p for directory in ('gacsca/fixed_rule','tests/fixed_rule','experiments/fixed_rule') for p in (root/directory).iterdir() if p.is_file() and p.suffix in ('.py','.c','.cpp','.h','.cu'));hashes={}
    with tarfile.open(stem.with_suffix('.tar.gz'),'x:gz') as archive:
        for path in files:
            name=str(path.relative_to(root));data=path.read_bytes();hashes[name]=sha(path);info=tarfile.TarInfo(name);info.size=len(data);archive.addfile(info,io.BytesIO(data))
    with Fresh.encode(top) as world:
        clean=world.stored
        for c in range(2):
            for address in (*range(10),*g.info,*g.hold,g.computation_cells,f.Q//2,f.Q-1):assert world.cell(c,address)==initial.cell_at(top,1,c*f.Q+address)
    state=clean.copy();fault_row=g.computation_cells+5+g.info[f.COL['data']];state[fault_row,r.COL['data']]^=np.uint64(1)
    assert sum(int(v).bit_count() for v in (state^clean).ravel())==1
    records=[];arrays={'clean_initial':clean,'fault_initial':state.copy(),'clean_top':r.array_from_cells(top)};started=time.monotonic()
    for period in range(2):
        start=state.copy();core=start.reshape(2,g.computation_cells+5,len(r.SCHEMA))[:,:g.computation_cells].copy().reshape(-1,len(r.SCHEMA));upper=r.decode_cores(core)
        expected=tuple(r.project(c) for c in f.step_ring(tuple(r.lift(c) for c in upper)))
        old=np.array([f.encode_cell(r.lift(c)) for c in upper],dtype=np.uint64);want=np.array([f.encode_cell(r.lift(c)) for c in expected],dtype=np.uint64)
        neighbors=np.stack([old[(np.arange(2)+j)%2] for j in range(-5,6)],axis=1).reshape(2,-1)
        gathers=[];holds=[];snapshots=[]
        with Recurrent(start) as world:
            for target in (16*f.Q,48*f.Q,70*f.Q,70*f.Q+1,f.CAPTURE_AGE,96*f.Q-1):
                with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator')),patch.object(f,'local_step',side_effect=AssertionError('host upper transition')),patch.object(r,'local_step',side_effect=AssertionError('host projected transition')):world.run(target-world.time)
                a=world.cores.reshape(2,g.computation_cells,len(r.SCHEMA));np.testing.assert_array_equal(a[:,np.array(g.info),r.COL['data']],old)
                if target in (16*f.Q,48*f.Q,70*f.Q):
                    stage={16*f.Q:0,48*f.Q:1,70*f.Q:2}[target];addresses=[g.history(stage,j,k) for j in range(-5,6) for k in range(f.FIELDS)]
                    got=a[:,addresses,r.COL['data']];np.testing.assert_array_equal(got,neighbors);gathers.append(got)
                if target==70*f.Q+1:np.testing.assert_array_equal(a[:,np.array(g.votes),r.COL['data']],neighbors)
                if target>=f.CAPTURE_AGE:
                    got=a[:,np.array(g.hold),r.COL['data']];np.testing.assert_array_equal(got,want);holds.append(got)
                print(json.dumps(dict(period=period+1,prefix_time=world.time,seconds=time.monotonic()-started)),flush=True)
            assert world.pending==0;prefix=world.stored
        with Suffix(prefix) as world:
            for target in (98*f.Q,99*f.Q,112*f.Q+1,f.U):
                with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator')),patch.object(f,'local_step',side_effect=AssertionError('host upper transition')):world.run(target-(96*f.Q-1)-world.time)
                if target>=99*f.Q:assert not np.any(world.flags.runs[:,1:])
                if target in (99*f.Q,f.U):snapshots.append(world.stored)
            state=world.stored;actual=world.decode();assert actual==expected
            assert actual[0]==initial.terminal_data(age=period+2)[0]
            assert actual[1].data==1 and actual[0].data==0
            row=dict(period=period+1,physical_ticks=f.U,upper_ages=[c.age for c in actual],upper_data=[c.data for c in actual],flags=world.flags.info,seconds=time.monotonic()-started);records.append(row);print(json.dumps(row),flush=True)
        arrays.update({f'start_{period}':start,f'prefix_{period}':prefix,f'final_{period}':state,f'decoded_{period}':r.array_from_cells(actual),f'gathers_{period}':np.stack(gathers),f'holds_{period}':np.stack(holds),f'stored_suffix_{period}':np.stack(snapshots)})
    np.savez_compressed(stem.with_suffix('.npz'),**arrays)
    result=dict(scope=__doc__,rule=r.identity(),fault=dict(stored_row=fault_row,column=r.COL['data'],bit=0,physical_address=f.Q+g.info[f.COL['data']]),records=records,physical_ticks=2*f.U,one_physical_Info_bit_persists_two_periods=True,clean_cap_advances_under_ordinary_rule=True,source_sha256=hashes,archive_sha256=sha(stem.with_suffix('.tar.gz')),artifact_sha256=sha(stem.with_suffix('.npz')),seconds=time.monotonic()-started,limitation='two-colony negative repair witness with aliased simulated neighbors; does not replace the separate nonaliased active-controller experiments, prove deeper dynamics, or establish a robust cap')
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','rule')}),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);execute(parser.parse_args().output)
