"""Check every compact terminal-memory category and exact final write stream."""
import argparse
import hashlib
import json
from pathlib import Path
import time
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c
from gacsca.fixed_rule import compact16_holder_program as p
from gacsca.fixed_rule.wordcode import LIT, ADD, NAND, MASK
from gacsca.fixed_rule.word_program import Instruction
from gacsca.fixed_rule.word_allocation import allocate, verify


def certify(layout=None):
    g = p.layout() if layout is None else layout; desc = p.compiled_description()
    assert g.description_sha256 == desc.digest()
    assert desc.inputs == 15*f.FIELDS and len(desc.outputs) == f.FIELDS
    required = p.dependencies(desc)
    static = tuple(w for w in required if w%f.FIELDS < len(f.STATIC))
    gathered = tuple(w for w in required if w not in set(static))
    assert g.required_inputs == required and g.regenerated_inputs == static and g.gathered_inputs == gathered
    assert len(static) == 49 and all(w//f.FIELDS == 7 for w in static)
    zero = next(desc.inputs+i for i,(op,a,_) in enumerate(desc.operations) if op == LIT and a == 0)
    allocation = allocate(desc, pins=(zero,), capacity=p.RESULT_CAPACITY); assert verify(desc, allocation)
    info_start = p.RESERVED+4*len(gathered); static_start = info_start+2*f.FIELDS
    base = static_start+len(static); temp = base+allocation.count; query = temp+5
    assert g.memory_count == temp+6 and p.MASK_ADDRESS in range(1,p.RESERVED)
    assert g.info == tuple(info_start+2*i for i in range(f.FIELDS)) and g.hold == tuple(a+1 for a in g.info)
    assert g.votes == tuple(p.RESERVED+4*i+1 for i in range(len(gathered)))
    for wire in range(desc.inputs):
        expected = g.votes[gathered.index(wire)] if wire in gathered else static_start+static.index(wire) if wire in static else None
        assert g.wires[wire] == expected
    assert g.wires[desc.inputs:] == tuple(base+i for i in allocation.slots)
    stream = []
    def emit(kind,a,b,d,low=False):
        if low and kind == NAND and a == b: a,b = p.MASK_ADDRESS,a
        if kind in (NAND,ADD,c.EQ) and a > b: a,b = b,a
        stream.append(Instruction(kind,a,b,d))
    def metadata(targets):
        for offset in f.STATIC_OFFSETS:
            source = targets[f.COL['address']]
            if offset:
                emit(LIT,offset&MASK,0,temp); emit(ADD,source,temp,query)
                source = query
            emit(LIT,f.Q-1,0,temp+1); emit(NAND,source,temp+1,temp+2)
            emit(NAND,temp+2,temp+2,query,low=True)
            for selector,name in enumerate(c.STATIC):
                emit(c.LOAD,query,0,0); emit(c.META,targets[f.COL[f'p{offset+3}_{name}']],selector,0)
    emit(LIT,MASK,0,p.MASK_ADDRESS)
    metadata(g.wires[7*f.FIELDS:8*f.FIELDS])
    assert g.description_instruction == g.entries[4]+len(stream)
    for i,(kind,a,b) in enumerate(desc.operations):
        a,b = (a,0) if kind == LIT else (g.wires[a],g.wires[b])
        emit(kind,a,b,g.wires[desc.inputs+i],low=True)
    for field,(target,out) in enumerate(zip(g.hold,desc.outputs)):
        if field >= len(f.STATIC): emit(ADD,g.wires[out],g.wires[zero],target)
    metadata(g.hold); emit(c.IF_THIRD,0,0,0)
    assert tuple(stream) == g.instructions[slice(*g.stage_ranges[4])], 'changed final writer stream'
    assert g.stage_ranges[3][1]-g.stage_ranges[3][0] == 1 and g.instructions[g.entries[3]].kind == c.HALT
    rom = p.base_rom(); history = set()
    for slot,wire in enumerate(gathered):
        offset,field = wire//f.FIELDS-7,wire%f.FIELDS
        for stage in range(3):
            address = g.history(stage,offset,field); history.add(address)
            assert address == p.RESERVED+4*slot+p.HISTORY_OFFSETS[stage]
            assert int(rom[address,2]) == (1 << (stage+1))-1
    categories = dict(history=history,votes=set(g.votes),info=set(g.info),hold=set(g.hold),
                      regenerated_inputs=set(range(static_start,base)),result=set(range(base,temp)),
                      query_workspace=set(range(temp,g.memory_count)),reserved=set(range(p.RESERVED)))
    union = set()
    for name, values in categories.items():
        assert not union & values, ('overlapping memory',name)
        union |= values
    assert union == set(range(g.memory_count))
    for address in range(1,g.memory_count):
        mask = int(rom[address,2]); assert int(rom[address,0]) == c.MEM
        assert bool(mask & (1 << 4)) == (address not in history and address not in categories['info'])
        assert bool(mask & c.INFO) == (address in categories['info'])
        assert bool(mask & c.VOTE) == (address in categories['votes'])
        assert bool(mask & 1) == (address not in categories['info'])
    assert all({a-1,a+1,a+2} <= history for a in g.votes)
    writes = {op.d for op in stream if op.kind in (*c.ALU_KINDS,LIT)} | {op.a for op in stream if op.kind == c.META}
    assert not writes & (history|categories['votes']|categories['info'])
    assert not writes & {temp+3,temp+4}
    assert writes & categories['reserved'] == {p.MASK_ADDRESS}
    timing = g.timing_certificate(); assert timing['fits']
    assert c.WF_END+f.Q < c.RESET_AGES[4]
    assert c.RESET_AGES[4]+timing['evaluation_ticks'] < c.ACTIVE_ENDS[4] < f.U-1
    return dict(passed=True,complete_memory_categories={k:len(v) for k,v in categories.items()},
                memory_words=g.memory_count,tail_words=5,final_instructions=len(stream),
                last_writer_slots=allocation.count,metadata_queries=98,all_raw_outputs=f.FIELDS,
                query_zero_words=[temp+3,temp+4],reserved_nonzero={str(p.MASK_ADDRESS):MASK},
                scope='Complete-state last-writer obligations, conditional on the sealed compact physical period/path/clock proof; no new physical execution or universal backend theorem.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    start=time.perf_counter();result=certify()
    result.update(seconds=time.perf_counter()-start,descriptor_sha256=f.self_description().digest(),
                  rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),
                  source_sha256={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in (Path(__file__),Path(p.__file__))})
    with args.output.open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
