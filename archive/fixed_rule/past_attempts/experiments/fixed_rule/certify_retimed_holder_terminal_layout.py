"""Finite structural obligations for the complete terminal-memory identity.

Extends the existing physical path/period induction with all MEM last writers.
This certificate does not itself execute a physical work period or prove a GPU
macro-accelerator. The accompanying argument states the semantic premises.
"""
import argparse,hashlib,json,resource,time
from pathlib import Path
from gacsca.fixed_rule import retimed_holder_program as p,retimed_holder_rule as f,retimed_holder_core as c
from gacsca.fixed_rule.wordcode import LIT,ADD,NAND,MASK
from gacsca.fixed_rule.word_program import Instruction
from gacsca.fixed_rule.word_allocation import allocate,verify


def certify(layout=None):
    g=p.layout() if layout is None else layout;desc=p.compiled_description()
    assert g.description_sha256==desc.digest()
    assert desc.inputs==15*f.FIELDS and len(desc.outputs)==f.FIELDS
    assert f.STATIC_OFFSETS==tuple(range(-3,4)) and f.Q&(f.Q-1)==0
    zero=next(desc.inputs+i for i,(op,a,_) in enumerate(desc.operations) if op==LIT and a==0)
    allocation=allocate(desc,pins=(zero,),capacity=p.RESULT_CAPACITY);assert verify(desc,allocation)
    base=p.RESERVED+4*desc.inputs+2*f.FIELDS;temp=base+allocation.count;query=temp+5
    assert g.memory_count==temp+6
    assert g.wires==g.votes+tuple(base+i for i in allocation.slots)
    assert g.info==tuple(p.RESERVED+4*desc.inputs+2*i for i in range(f.FIELDS))
    assert g.hold==tuple(at+1 for at in g.info)
    assert not set(g.info)&set(g.hold)
    assert g.stage_ranges[4][0]==g.description_instruction==g.entries[4]
    expected=[]
    for i,(kind,a,b) in enumerate(desc.operations):
        a,b=(a,0) if kind==LIT else (g.wires[a],g.wires[b])
        if kind in (NAND,ADD,c.EQ) and a>b:a,b=b,a
        expected.append(Instruction(kind,a,b,g.wires[desc.inputs+i]))
    expected += [Instruction(ADD,g.wires[out],g.wires[zero],at) for at,out in zip(g.hold,desc.outputs)]
    for offset in f.STATIC_OFFSETS:
        source=g.hold[f.COL['address']]
        if offset:
            expected += [Instruction(LIT,offset&MASK,0,temp),Instruction(ADD,source,temp,query),Instruction(LIT,f.Q-1,0,temp+1),Instruction(NAND,query,temp+1,temp+2),Instruction(NAND,temp+2,temp+2,query)]
            source=query
        for selector,name in enumerate(c.STATIC):
            expected += [Instruction(c.LOAD,source,0,0),Instruction(c.META,g.hold[f.COL[f'p{offset+3}_{name}']],selector,0)]
    expected.append(Instruction(c.IF_THIRD,0,0,0))
    assert tuple(expected)==g.instructions[slice(*g.stage_ranges[4])],'final instruction/state-writing stream changed'
    assert g.stage_ranges[3][1]-g.stage_ranges[3][0]==1 and g.instructions[g.entries[3]].kind==c.HALT
    rom=p.base_rom();history=set();votes=set(g.votes);info=set(g.info);hold=set(g.hold)
    for offset in f.NEIGHBORHOOD:
        for field in range(f.FIELDS):
            for stage in range(3):
                address=g.history(stage,offset,field);history.add(address)
                assert int(rom[address,0])==c.MEM and int(rom[address,2])==(1<<(stage+1))-1
                assert not (int(rom[address,2])&((1<<3)|(1<<4)))
    assert len(history)==3*15*f.FIELDS
    categories=dict(history=history,votes=votes,info=info,hold=hold,result=set(range(base,temp)),query_workspace=set(range(temp,g.memory_count)),reserved=set(range(p.RESERVED)))
    union=set()
    for name,addresses in categories.items():
        assert not union&addresses,('overlapping memory category',name);union|=addresses
    assert union==set(range(g.memory_count)),'unaccounted MEM state'
    for address in range(1,g.memory_count):
        mask=int(rom[address,2]);assert int(rom[address,0])==c.MEM
        if address in history or address in info:assert not mask&(1<<4)
        else:assert mask&(1<<4)
        assert bool(mask&c.INFO)==(address in info)
        assert bool(mask&c.VOTE)==(address in votes)
    assert all((int(rom[a,2])&1)==0 for a in info)
    assert all(int(rom[a,2])&1 for a in range(1,g.memory_count) if a not in info)
    for at in g.votes:assert {at-1,at+1,at+2}<=history
    assert temp+3 not in {op.d for op in expected if op.kind in (*c.ALU_KINDS,LIT)}
    assert temp+4 not in {op.d for op in expected if op.kind in (*c.ALU_KINDS,LIT)}
    timing=g.timing_certificate();assert timing['fits']
    assert c.WF_END+f.Q<c.RESET_AGES[4]
    assert c.RESET_AGES[4]+timing['evaluation_ticks']<c.ACTIVE_ENDS[4]<f.U-1
    return dict(passed=True,complete_memory_categories={name:len(values) for name,values in categories.items()},memory_words=g.memory_count,tail_words=5,full_terminal_bank_words=g.memory_count+5,final_instructions=len(expected),descriptor_operations=len(desc.operations),last_writer_slots=allocation.count,all_raw_outputs=f.FIELDS,all_mutable_fields=105,metadata_queries=49,query_zero_words=[temp+3,temp+4],entry_domain='Canonical coherent lower Age-zero state, empty controller/mail/flags/Wf, valid full raw Info, arbitrary MEM scratch and coherent localized Signal bits; no faults during the period.',limitation='Structural certificate plus inherited instruction/path/period semantic induction. Not a proof assistant result, universal backend parity, or executed depth-two trace.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError(out)
    started=time.perf_counter();result=certify();result.update(seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,descriptor_sha256=f.self_description().digest(),rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),source_sha256={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in (Path(__file__),Path(p.__file__))})
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
