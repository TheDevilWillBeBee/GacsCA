"""Compare complete terminal formulas with saved physical evolution and each other."""
import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import random
import time
import numpy as np
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_projected as r, compact16_holder_program as p
from gacsca.fixed_rule import compact16_holder_terminal_reference as replay, compact16_holder_terminal_dag as dag
from experiments.fixed_rule.audit_small_holder_position_events import sha


def step(parents):
    n=len(parents)
    return tuple(r.local_step(tuple(parents[(col+j)%n] for j in f.NEIGHBORHOOD)) for col in range(n))


def compare(parents):
    first=replay.terminal(parents);second=dag.terminal(parents)
    for key in first:np.testing.assert_array_equal(first[key],second[key],err_msg=key)
    expected=np.array([f.encode_cell(r.lift(cell)) for cell in step(parents)],dtype=np.uint64)
    np.testing.assert_array_equal(first['committed_bank'][:,list(p.layout().info)],expected)
    return first


def witness():
    # A single raw replica defect is corrected in decoded output, but input
    # histories can retain it. This forbids replacement by fresh encoding.
    from experiments.fixed_rule.compact16_holder_active_fixture import parents
    before=parents();healthy=step(before);base=dag.terminal(before)
    for name in ('s0_value','s1_value','s2_value','s3_value','s4_value','s2_pc'):
        damaged=list(before);damaged[15]=replace(damaged[15],**{name:getattr(damaged[15],name)^1});damaged=tuple(damaged)
        if step(damaged)!=healthy:continue
        changed=compare(damaged)
        different=int(np.count_nonzero(base['committed_bank']!=changed['committed_bank']))
        if different:
            return dict(field=name,upper_cell=15,xor=1,equal_decoded_outputs=True,different_retained_bank_words=different)
    raise AssertionError('no distinguishing complete-state witness')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    start=time.perf_counter();rows=[];references={}
    for stem in ('compact16_holder_gpu_periods_v2','compact16_holder_gpu_active_v1'):
        path=Path('figs/fixed_rule')/(stem+'.json');receipt=json.loads(path.read_text());assert receipt['passed']
        assert sha(receipt['artifact'])==receipt['artifact_sha256'];references[str(path)]=sha(path)
        with np.load(receipt['artifact'],allow_pickle=False) as saved:
            parents=r.cells_from_array(saved['initial_upper'])
            for epoch in range(2):
                result=compare(parents)
                np.testing.assert_array_equal(result['committed_bank'],saved['boundary_banks'][epoch])
                np.testing.assert_array_equal(result['signals'],np.stack((saved['boundary_left'][epoch],saved['boundary_right'][epoch]),axis=1))
                rows.append(dict(source=stem,period=epoch+1,all_bank_words_checked=int(result['committed_bank'].size)))
                parents=step(parents)
    rng=random.Random(2026092778)
    random_parents=tuple(r.Cell(**{name:rng.getrandbits(width) for name,width in r.SCHEMA}) for _ in range(3))
    compare(random_parents)
    result=dict(passed=True,physical_boundary_comparisons=rows,random_typed_parents=3,distinguishing_witness=witness(),references=references,
                seconds=time.perf_counter()-start,descriptor_sha256=f.self_description().digest(),
                rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),
                source_sha256={str(Path(module.__file__)):sha(module.__file__) for module in (replay,dag,p,f,r)})
    result['source_sha256'][str(Path(__file__))]=sha(__file__)
    with args.output.open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
