"""Capacity of literal six-NAND temporal votes before the frozen word descriptor.

This is an optimistic computation-only schedule, not a new self-simulating rule:
all three histories are assumed already present, and retrieval/reset/stage-control
code is omitted. It decides whether this specified composition fits Gray's 8Q.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from gacsca.fixed_rule import word_rule as f,word_program as p
from gacsca.fixed_rule.wordcode import NAND,LIT,ADD,MASK


def majority(a,b,c):
    ab=(~(a&b))&MASK;ac=(~(a&c))&MASK;bc=(~(b&c))&MASK
    pair=(~(ab&ac))&MASK
    return (~(((~(pair&pair))&MASK)&bc))&MASK


def composition():
    desc=f.self_description();inputs=desc.inputs;ops=[];wire=3*inputs;voted=[]
    def emit(kind,a,b):
        nonlocal wire
        result=wire;wire+=1;ops.append(p.Instruction(kind,a,b,result));return result
    for i in range(inputs):
        ab=emit(NAND,i,inputs+i);ac=emit(NAND,i,2*inputs+i);bc=emit(NAND,inputs+i,2*inputs+i)
        # ~(ab & ac & bc) uses three more NANDs after the first three.
        pair=emit(NAND,ab,ac);both=emit(NAND,pair,pair)
        voted.append(emit(NAND,both,bc))
    # Six gates, not five: the three-way conjunction needs a re-inversion.
    vote_operations=len(ops)
    mapping=list(voted)
    for kind,a,b in desc.operations:
        mapping.append(emit(kind,a if kind==LIT else mapping[a],0 if kind==LIT else mapping[b]))
    hold=wire;wire+=f.FIELDS
    zero=next(mapping[desc.inputs+i] for i,(kind,a,_) in enumerate(desc.operations) if kind==LIT and a==0)
    for i,output in enumerate(desc.outputs):ops.append(p.Instruction(ADD,mapping[output],zero,hold+i))
    for selector,name in enumerate(f.STATIC):
        ops.append(p.Instruction(f.LOAD,hold+f.COL['address'],0,0))
        ops.append(p.Instruction(f.META,hold+f.COL[name],selector,0))
    for i in range(f.FIELDS):ops.append(p.Instruction(ADD,hold+i,zero,5*f.FIELDS+i))
    layout=p.Layout(wire,tuple(ops),desc.digest());ticks,_=layout.schedule()
    return layout,dict(frozen_rule_description=desc.digest(),histories=3,raw_words_per_history=inputs,
        vote_operations=vote_operations,descriptor_operations=len(desc.operations),memory_cells=wire,
        instruction_cells=len(ops),core_cells=layout.computation_cells,computation_only_ticks=ticks,
        source_stage5_ticks=8*f.Q,fits_stage5=ticks<=8*f.Q,ratio=ticks/(8*f.Q),
        scope='optimistic frozen-rule six-NAND bitwise majority then evaluator; already-gathered inputs; no retrieval/reset/clock description; not closure')


def execute(output):
    output=Path(output)
    if output.exists():raise FileExistsError('preserve evidence')
    layout,result=composition();root=Path(__file__).resolve().parents[2]
    files=[Path(__file__).resolve(),*(root/'gacsca/fixed_rule').glob('word*.py')]
    result['source_sha256']={str(path.relative_to(root)):hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(files)}
    result['program_sha256']=hashlib.sha256(json.dumps([asdict(op) for op in layout.instructions],separators=(',',':')).encode()).hexdigest()
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'},indent=2));return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();execute(args.output)
