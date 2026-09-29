"""Fresh complete GPU periods against independent full terminal-memory formulas.

Host formulas are diagnostics only: none of their output is installed. All physical
scratch is randomized at initialization. No represented transition runs on host
while the physical GPU world evolves. This remains one-link execution.
"""
import argparse,hashlib,json,random,resource,time
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import retimed_holder_terminal_dag as dag,retimed_holder_terminal_reference as reference,retimed_holder_terminal_checks as checks
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r,retimed_holder_program as p,retimed_holder_quotient as q
from gacsca.fixed_rule import retimed_holder_resident_general as gpu,retimed_holder_resident_period as resident,retimed_holder_native as native
from gacsca.fixed_rule import retimed_holder_flags_gpu as flags,retimed_holder_resident_gather as gather,retimed_holder_resident_independent as independent
from gacsca.fixed_rule.retimed_holder_cuda_general_snapshot import snapshot
from gacsca.fixed_rule.wordcode import Program


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    out=Path(args.output);artifact=out.with_suffix('.npz')
    if out.exists() or artifact.exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();seed=2026092701;rng=random.Random(seed);n=15;g=p.layout()
    parents=tuple(r.Cell(**{name:rng.getrandbits(width) for name,width in r.SCHEMA}) for _ in range(n))
    initial=r.array_from_cells(parents)
    signals=np.array([(rng.getrandbits(1),rng.getrandbits(1)) for _ in range(n)],dtype=np.uint64)
    logical={col*f.Q+a:q.Cell(address=a,signal=checks.signal_word(a,*signals[col])) for col in range(n) for a in (*range(1,6),*range(f.Q-5,f.Q)) if checks.signal_word(a,*signals[col])}
    bank=np.array([[rng.getrandbits(64) for _ in range(g.memory_count+5)] for _ in range(n)],dtype=np.uint64)
    for col,parent in enumerate(parents):bank[col,list(g.info)]=f.encode_cell(r.lift(parent))
    saved=dict(initial_upper=initial,initial_bank=bank,initial_signals=signals);results=[];gpu_seconds=0.;metrics={}
    for module in (resident,independent,gather,gpu,flags):module.library()
    with gpu.World(parents,logical=logical,device_budget=32*1024**2) as world:
        # Initialization only. No bank upload occurs after physical time zero.
        for col in range(n):
            row=np.ascontiguousarray(bank[col]);assert world._core.lib.rp_bank(world._core.handle,col,resident.pointer(row))==0
        np.testing.assert_array_equal(world._core.snapshot()[0],bank)
        peak=world.device_bytes+(32*n*(f.Q//64)+2*n)+8*n*(g.memory_count+5+32*6+1)
        assert peak<=64*1024**2
        for epoch in range(2):
            oracle_started=time.perf_counter();expected=dag.terminal(parents);replay=reference.terminal(parents)
            for key in expected:np.testing.assert_array_equal(expected[key],replay[key])
            following=r.step_ring(parents)
            wanted=np.array([f.encode_cell(r.lift(cell)) for cell in following],dtype=np.uint64)
            np.testing.assert_array_equal(expected['committed_bank'][:,list(g.info)],wanted)
            oracle_seconds=time.perf_counter()-oracle_started
            checkpoints=[]
            for name,target in (('precommit',(epoch+1)*f.U-1),('commit',(epoch+1)*f.U)):
                tick=time.perf_counter()
                with ExitStack() as guard:
                    for module,method in ((Program,'evaluate'),(f,'local_step'),(r,'local_step'),(r,'step_ring'),(native,'local_step'),(dag,'terminal'),(reference,'terminal')):
                        guard.enter_context(patch.object(module,method,side_effect=AssertionError('host transition or diagnostic during physical evolution')))
                    row=world.advance(target-world.time,extra_device_budget=32*1024**2)
                gpu_seconds+=time.perf_counter()-tick
                for key,value in row.items():metrics[key]=max(metrics.get(key,0),value) if key=='extra_device_bytes' else metrics.get(key,0)+value
                state=snapshot(world);details=checks.check(state,expected,age=(f.U-1 if name=='precommit' else 0),time=target)
                for key,value in state.items():saved[f'period{epoch+1}_{name}_{key}']=value
                checkpoints.append(dict(name=name,**details))
                print(json.dumps(dict(period=epoch+1,checkpoint=name,gpu_seconds=gpu_seconds,seconds=time.perf_counter()-started)),flush=True)
            assert world.decode()==following
            changes=sum(a!=b for old,new in zip(parents,following) for a,b in zip(r.encode_cell(old),r.encode_cell(new)))
            results.append(dict(period=epoch+1,checkpoints=checkpoints,represented_words_changed=changes,oracle_seconds=oracle_seconds))
            parents=following
        assert metrics['physical_ticks']==2*f.U
        np.savez_compressed(artifact,**saved)
        modules=(dag,reference,checks,f,r,p,q,gpu,resident,native,flags,gather,independent)
        sources=[Path(__file__)]+[Path(m.__file__) for m in modules]+[Path(m.__file__).with_suffix('.cu') for m in (resident,flags,gather,independent)]
        result=dict(passed=True,seed=seed,colonies=n,physical_ticks=world.time,periods=2,period_results=results,metrics=metrics,gpu_evolution_seconds=gpu_seconds,seconds=time.perf_counter()-started,explicit_device_peak_bound_bytes=peak,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,random_typed_upper_all_fields=True,random_initial_MEM_scratch=True,no_host_transition_during_GPU_evolution=True,no_terminal_formula_installed=True,one_retained_physical_state=True,descriptor_sha256=f.self_description().digest(),rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),artifact_sha256=sha(artifact),source_sha256={str(path):sha(path) for path in sources},binaries={str(m.library()._name):sha(m.library()._name) for m in (resident,independent,gather,gpu,flags)},scope='Two noiseless one-link physical work periods, complete terminal Data/controller/Signal/flag states, canonical lower entry and arbitrary typed upper states. Diagnostic full-state identity only; no accelerated physical macrostep or executed depth-two period.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
