"""Validate complete GPU endpoint acceleration against actual physical traces."""
import argparse,hashlib,json,resource,time
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import retimed_holder_endpoint_gpu as gpu,retimed_holder_terminal_checks as checks
from gacsca.fixed_rule import retimed_holder_terminal_dag as dag,retimed_holder_terminal_reference as replay
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r,retimed_holder_program as p,retimed_holder_native as native
from gacsca.fixed_rule.wordcode import Program


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def evolve(world,method):
    tick=time.perf_counter()
    with ExitStack() as guard:
        for module,name in ((Program,'evaluate'),(f,'local_step'),(r,'local_step'),(r,'step_ring'),(native,'local_step'),(dag,'terminal'),(replay,'terminal')):
            guard.enter_context(patch.object(module,name,side_effect=AssertionError('host transition during GPU endpoint evolution')))
        getattr(world,method)()
    return time.perf_counter()-tick


def load(stem):
    path=Path('figs/fixed_rule')/(stem+'.json');receipt=json.loads(path.read_text());assert receipt['passed']
    assert receipt['descriptor_sha256']==f.self_description().digest()
    assert receipt['rom_sha256']==hashlib.sha256(p.base_rom().tobytes()).hexdigest()
    artifact=path.with_suffix('.npz');assert sha(artifact)==receipt['artifact_sha256']
    return path,np.load(artifact,allow_pickle=False)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output);artifact=out.with_suffix('.npz')
    if out.exists() or artifact.exists():raise FileExistsError(out)
    started=time.perf_counter();gpu.library();g=p.layout();results=[];saved={};references=[];peak=0
    reference,z=load('retimed_holder_cuda_terminal_v2');references.append(reference)
    with z,gpu.World(z['initial_bank'],z['initial_signals']) as world:
        peak=max(peak,world.device_bytes);parents=r.cells_from_array(z['initial_upper'])
        for epoch in (1,2):
            expected=dag.terminal(parents)
            for phase,method in (('precommit','precommit'),('commit','commit')):
                elapsed=evolve(world,method);state=world.snapshot()
                prefix=f'period{epoch}_{phase}_';actual={key[len(prefix):]:z[key] for key in z.files if key.startswith(prefix)}
                checks.check(state,expected,age=world.age,time=world.time)
                checks.check(actual,expected,age=world.age,time=world.time)
                for key in ('bank','signals','flags','age','time'):np.testing.assert_array_equal(state[key],actual[key],err_msg=key)
                for key,value in state.items():saved[prefix+key]=value
                results.append(dict(case='fresh_random',period=epoch,phase=phase,seconds=elapsed,all_physical_fields_match=True,bank_words=state['bank'].size))
            parents=r.step_ring(parents)
    reference,z=load('retimed_holder_cuda_encoded_repair_v1');references.append(reference)
    with z:
        witness=[]
        for name,initial,output in (('healthy',z['initial'],'healthy_boundary_1_bank'),('damaged',z['faulty_upper_initial'],'boundary_1_bank')):
            bank=np.zeros((len(initial),g.memory_count+5),dtype=np.uint64);bank[:,list(g.info)]=initial
            with gpu.World(bank,np.zeros((len(initial),2),dtype=np.uint64)) as world:
                peak=max(peak,world.device_bytes);elapsed=evolve(world,'period');state=world.snapshot()
                np.testing.assert_array_equal(state['bank'],z[output]);witness.append(state['bank'])
                parents=tuple(r.project(f.decode_cell(row)) for row in initial)
                checks.check(state,dag.terminal(parents),age=0,time=f.U)
                saved[name+'_bank']=state['bank'];results.append(dict(case=name,seconds=elapsed,all_terminal_bank_words_match=True,bank_words=state['bank'].size))
        np.testing.assert_array_equal(witness[0][:,list(g.info)],witness[1][:,list(g.info)])
        different=int(np.count_nonzero(witness[0]!=witness[1]));assert different==120
    np.savez_compressed(artifact,**saved)
    paths=[Path(__file__),Path(gpu.__file__),Path(gpu.__file__).with_suffix('.cu'),Path(checks.__file__),Path(dag.__file__)]
    result=dict(passed=True,cases=results,case_count=len(results),distinct_terminal_scratch_words_for_equal_decodes=different,peak_explicit_device_bytes=peak,seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,descriptor_sha256=f.self_description().digest(),rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),artifact_sha256=sha(artifact),source_sha256={str(path):sha(path) for path in paths},references={str(path):sha(path) for path in references},binary=str(gpu.library()._name),binary_sha256=sha(gpu.library()._name),scope='Complete GPU C/B endpoint operator in the certified noiseless entry domain, compared against actual one-link physical trajectories and the equal-output/different-scratch witness. No faults are skipped; no complete depth-two execution yet.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
