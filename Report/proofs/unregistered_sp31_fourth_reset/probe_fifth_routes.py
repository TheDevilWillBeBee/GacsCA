#!/usr/bin/env python3
"""Additional exact route/refinement counts; no new transition rule."""
from collections import Counter
from pathlib import Path
import hashlib,json,sys,time

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'Report/proofs')]
import proposed_native_command1024 as proposed
from check_native_command1024_first_pulse import blocked

OUT=ROOT/'figs/robustness/unregistered_sp31_fourth_reset'
NATIVE=('addr','age','f1','f2','wf1','wf2')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def compute():
    start=time.monotonic();p=proposed.parameters();counts=Counter();rows=[]
    strip=((155*p.Q-512,155*p.Q),)
    for row in proposed.dependency_table(p):
        if row['field'] not in NATIVE:continue
        phase=row['address']
        for j in range(92,142):
            for d in row['offsets']:
                if j+d>=155:
                    hit=blocked(strip,j,d,phase,p.Q)
                    assert hit,(j,d,phase)
                    for gather in p.gathers_q:
                        counts['left_true_native_sources_ge155_erased']+=1
                        rows.append([j,row['field'],row['bit'],d,phase,gather,hit])
    assert counts['left_true_native_sources_ge155_erased']>0
    assert proposed.local.CENTERS==(-30,-10,10,30)
    left=[];foreign=[]
    for t in range(87,147):
        if t<=141:
            negative=[t+c+u for c in (-30,-10) for u in range(-2,3)]
            assert max(negative)<=133<136
            counts['two_left_canonical_joint_blocks']+=2
        if 136<=t<=141:
            far=[t+30+u for u in range(-2,3)]
            assert min(far)>=155
            adjusted=[(-(30+u))%p.Q for u in range(-2,3)]
            assert len(set(adjusted))==5
            left.append(dict(receiver=t,negative_blocks_canonical_Age4=True,
                positive_far_block_no_GF_triple=True,
                replacement_only_canonical_Age4_or_raw_retention=True))
    for t in range(153,160):
        for center in (10,30):
            sources=[t+center+u for u in range(-2,3)]
            assert min(sources)>=153
            adjusted=[(-(center+u))%p.Q for u in range(-2,3)]
            assert len(set(adjusted))==5
            counts['foreign_positive_joint_blocks_invalid']+=1
        foreign.append(dict(reader=t,raw_GF_zero=True,positive_blocks_invalid=True,
            joint_three_valid_blocks_impossible=True,refined_GF_zero=True))
    data=json.dumps(rows,separators=(',',':')).encode()
    return dict(Q=p.Q,U=p.U,TF=p.T_wf,probe_sha256=sha(__file__),
        route_counts=dict(counts),left_erasure_route_rows_sha256=hashlib.sha256(data).hexdigest(),
        left_joint_refinement_reductions=left,foreign_right_reader_refinement=foreign,
        actual_physical_lift_supplied_by_written_proof=False,
        rule_or_ROM_or_G17_change=False,global_reliability_established=False,
        seconds=time.monotonic()-start)

def main():
    OUT.mkdir(parents=True,exist_ok=True);path=OUT/'fifth_route_receipt.json'
    assert not path.exists(),'Retain issued evidence; compute() is the replay interface.'
    result=compute();path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,route_counts=result['route_counts'],
        seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
