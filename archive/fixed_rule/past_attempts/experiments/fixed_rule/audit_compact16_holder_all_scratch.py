"""Independently recompute every nested scratch word via vectorized SSA DAG.

Diagnostic only. Retains all SSA values (no physical allocation reuse) until
outputs and final scratch writers are extracted; never evolves a physical world.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c
from gacsca.fixed_rule import compact16_holder_program as p, compact16_holder_projected as r
from gacsca.fixed_rule import compact16_holder_endpoint_image_array as image
from gacsca.fixed_rule import compact16_holder_terminal_dag as scalar
from gacsca.fixed_rule.wordcode import LIT, NAND, ADD, SHR, EQ, LT, MASK
from experiments.fixed_rule.audit_small_holder_position_events import sha


def terminal_rows(raw, start, count):
    """Full committed bank for a bounded window in an immutable raw parent ring."""
    assert raw.dtype == np.uint64 and raw.ndim == 2 and raw.shape[1] == f.FIELDS
    assert 0 <= start < len(raw) and 1 <= count <= 512 and start+count <= len(raw)
    g=p.layout();desc=p.compiled_description();positions=np.arange(start,start+count)
    # Inputs unused by the descriptor still exist in the complete raw parent;
    # a zero placeholder here cannot be read by any descriptor operation.
    values=np.zeros((desc.inputs+len(desc.operations),count),dtype=np.uint64)
    for wire in g.required_inputs:
        offset,field=wire//f.FIELDS-7,wire%f.FIELDS
        values[wire]=raw[(positions+offset)%len(raw),field]
    bank=np.zeros((count,g.memory_count+5),dtype=np.uint64)
    for i,(kind,a,b) in enumerate(desc.operations):
        target=values[desc.inputs+i]
        if kind == LIT: target[:]=a
        elif kind == NAND: np.bitwise_not(np.bitwise_and(values[a],values[b]),out=target)
        elif kind == ADD: np.add(values[a],values[b],out=target)
        elif kind == SHR: np.right_shift(values[a],values[b],out=target)
        elif kind == EQ: target[:]=values[a]==values[b]
        elif kind == LT: target[:]=values[a]<values[b]
        else: raise AssertionError(('unsupported complete descriptor operation',kind))
        bank[:,g.wires[desc.inputs+i]]=target
    for slot,wire in enumerate(g.gathered_inputs):
        offset,field=wire//f.FIELDS-7,wire%f.FIELDS
        for stage in range(3): bank[:,g.history(stage,offset,field)]=values[wire]
        bank[:,g.votes[slot]]=values[wire]
    for wire in g.regenerated_inputs: bank[:,g.wires[wire]]=values[wire]
    output=values[list(desc.outputs)].T.copy();address=output[:,f.COL['address']]
    rom=np.array([[r.record(a)[name] for name in c.STATIC] for a in range(f.Q)],dtype=np.uint64)
    for offset in f.STATIC_OFFSETS:
        indices=(address+np.uint64((f.Q+offset)%f.Q))%np.uint64(f.Q)
        for selector,name in enumerate(c.STATIC):output[:,f.COL[f'p{offset+3}_{name}']]=rom[indices,selector]
    bank[:,list(g.info)]=output;bank[:,list(g.hold)]=output
    query=(address+np.uint64(3))&np.uint64(f.Q-1);temp=g.memory_count-6
    bank[:,p.MASK_ADDRESS]=MASK;bank[:,temp]=3;bank[:,temp+1]=f.Q-1
    bank[:,temp+2]=~query;bank[:,temp+5]=query
    return bank,output[:,[f.COL['f2'],f.COL['f1']]]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reference',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    start=time.perf_counter();receipt=json.loads(args.reference.read_text());assert receipt['passed']
    assert receipt['descriptor_sha256']==f.self_description().digest()
    assert sha(receipt['small_artifact_path'])==receipt['small_artifact_sha256']
    rows=[]
    with np.load(receipt['small_artifact_path'],allow_pickle=False) as saved:
        for epoch in (1,2):
            raw=image.render(saved[f'period{epoch}_upper_C_bank'],saved[f'period{epoch}_upper_signals'],f.U-1)
            path=receipt['period_results'][epoch-1]['bank_path'];assert sha(path)==receipt['bank_sha256'][path]
            bank=np.load(path,mmap_mode='r',allow_pickle=False);checked=0
            for at in range(0,len(raw),512):
                count=min(512,len(raw)-at);expected,signals=terminal_rows(raw,at,count)
                np.testing.assert_array_equal(bank[at:at+count],expected,err_msg=f'all scratch at period {epoch} row {at}')
                np.testing.assert_array_equal(saved[f'period{epoch}_signals'][at:at+count],signals)
                checked+=expected.size
            rows.append(dict(period=epoch,complete_rows_independently_recomputed=len(raw),all_bank_words_independently_recomputed=checked))
            del bank,raw
            print(json.dumps(rows[-1]),flush=True)
    result=dict(passed=True,cases=rows,seconds=time.perf_counter()-start,reference=str(args.reference),reference_sha256=sha(args.reference),
                source_sha256={str(Path(__file__)):sha(__file__)},
                scope='Exhaustive independent SSA recomputation of every saved depth-two terminal bank word and Signal. Descriptor-semantic diagnostic, not literal U^2 replay or general noisy-state backend proof.')
    with args.output.open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
