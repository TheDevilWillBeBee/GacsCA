"""A single physical Flag1-bit fault delays a nonzero wave beyond two ticks.

Complete local patches establish the short-time witness. The all-front exact
flag proof establishes later rejoining of the clean wave in this mail-free family.
No claim about arbitrary noisy execution is made.
"""
import argparse,hashlib,json,time
from pathlib import Path
from functools import lru_cache
from dataclasses import replace
import numpy as np
from gacsca.fixed_rule import holder_core as c,holder_rule as f,holder_projected as r,holder_initial as initial,holder_flag_profile as profile
from gacsca.fixed_rule.holder_faults import recovery
from .prove_holder_flag_profile import prove


def execute(output):
    stem=Path(output)
    if stem.with_suffix('.json').exists() or stem.with_suffix('.npz').exists():raise FileExistsError('preserve evidence')
    start=time.monotonic();age=96*f.Q+f.Q//6;front=profile.interval(age)[0]
    @lru_cache(None)
    def logical(pos):
        address=(front+pos)%f.Q
        return c.Cell(**r.record(address),address=address,age=age,signal=profile.signal(address),data=address*39,**dict(zip(('f1','f2','wf1','wf2'),profile.bits(age,address))))
    @lru_cache(None)
    def read(pos):return initial.coherent_cell(logical,pos)
    damaged=replace(read(0),f1=0);run=recovery(read,{0:damaged},8)
    assert run['mismatch']==[(-24,['f1'])]
    frames={f'{kind}_{i}':r.array_from_cells(pair[k]) for i,pair in enumerate(run['frames']) for k,kind in enumerate(('clean','damaged'))}
    # A single first-one deletion is exactly the suffix front+1. Under the proved
    # forced-front recurrence both fronts reach zero by this many ordinary ticks.
    proof=prove();join=(front+1+2)//3;assert age+join<98*f.Q
    assert max(0,front-3*join)==max(0,front+1-3*join)==0
    with stem.with_suffix('.npz').open('xb') as stream:np.savez_compressed(stream,**frames)
    result=dict(passed=True,scope=__doc__,initial_age=age,initial_front=front,initial_patch_start=run['initial_start'],literal_steps=8,final_mismatches=run['mismatch'],single_physical_bit='Flag1 at the first one in the wave',two_tick_full_state_recovery_false=True,procedure_fields_recovered=True,certified_join_by_ticks=join,join_before_forcing_cutoff=True,flag_proof_passed=proof['passed'],rule=r.identity(),seconds=time.monotonic()-start,artifact_sha256=hashlib.sha256(stem.with_suffix('.npz').read_bytes()).hexdigest())
    root=Path(__file__).resolve().parents[2];files=[*root.glob('gacsca/fixed_rule/*.py'),Path(__file__),root/'experiments/fixed_rule/prove_holder_flag_profile.py']
    result['source_sha256']={str(path.relative_to(root)):hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','rule')},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);execute(p.parse_args().output)
