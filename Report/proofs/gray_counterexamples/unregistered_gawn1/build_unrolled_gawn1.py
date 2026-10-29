"""Replace only the SF vote helper in the normalized own emitter.

All operations remain existing generic instructions; no new majority
syscall/host rule evaluator is introduced.
"""
from pathlib import Path
from dataclasses import replace,asdict
import hashlib,json,sys
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent/'unregistered_gawn0')]
import build_normalized_gawn0 as prior
import unrolled_gawn1 as k

def helper():
    rows=[('LABEL',('vote',)),('LABEL',('vote_loop',))]
    def e(name,*args):rows.append((name,args))
    def alu(d,op,a,b=0):e('ALU',d,k.ALU[op],a,b,0)
    for i,slot in enumerate(k.SLOTS):
        if slot==0:alu(6,'MOV',12)
        else:e('ALUI',6,k.ALU['SUB' if slot>0 else 'ADD'],12,abs(slot))
        e('LDX',0,k.PRIMARY_START,11,6,0)
        if i==0:alu(3,'MOV',0)
        elif i==1:alu(4,'AND',3,0);alu(3,'OR',3,0)
        elif i==2:
            alu(5,'AND',4,0);alu(1,'AND',3,0);alu(4,'OR',4,1);alu(3,'OR',3,0)
        else:
            alu(1,'AND',4,0);alu(5,'OR',5,1);alu(1,'AND',3,0);alu(4,'OR',4,1);alu(3,'OR',3,0)
        e('ALUI',11,k.ALU['ADD'],11,1)
    # Match every old helper return register, including its table/loop debris.
    e('MOVI',6,0);e('MOVI',7,16);e('MOVI',8,5)
    alu(0,'MOV',5);e('JMPR',15)
    assert sum(name!='LABEL' for name,args in rows)==37
    return rows

def programme():
    a=prior.programme();old=list(a.rows)
    start=next(i for i,row in enumerate(old) if row==('LABEL',('vote',)))
    end=next(i for i,row in enumerate(old) if row==('LABEL',('slots',)))
    block=helper();a.rows[:]=old[:start]+block+old[end:]
    # Retain the old-to-new helper replacement as literal structural evidence.
    a.previous_normalized_rows=old;a.old_helper_rows=old[start:end]
    a.new_helper_rows=block;a.helper_start_row=start;a.helper_row_delta=len(block)-(end-start)
    for m in a.normalization_masks:
        if m['new_mask_row']>=end:m['new_mask_row']+=a.helper_row_delta
    return a

def instance():
    a=programme();rom,listing,labels,errors=a.assemble();assert not errors,errors
    assert len(rom.bits)<=65536
    return replace(rom,bits=rom.bits+(0,)*(65536-len(rom.bits))),listing,labels,a

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def build(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    paths=[out/'GAWN1_rom.json',out/'GAWN1_listing.json',out/'GAWN1_emission.json']
    assert not any(p.exists() for p in paths),'never overwrite frozen emission'
    rom,listing,labels,a=instance()
    paths[0].write_text(json.dumps(asdict(rom),indent=2)+'\n')
    paths[1].write_text(json.dumps(dict(listing=listing,labels=labels),indent=2)+'\n')
    metadata=dict(explicit_new_own_ROM=True,no_new_physical_ISA_primitive=True,
        Q=k.Q,U=k.U,WORD=k.WORD,FRAME_WORDS=k.FRAME_WORDS,PRIMARY_START=k.PRIMARY_START,
        previous_helper_executed_instructions=86,new_helper_executed_instructions=37,
        token_count=rom.token_count,dictionary_used=rom.used_dictionary,
        used_token_stream_bits=rom.token_count*rom.token_bits,immutable_allocated_bits=len(rom.bits)+len(rom.dictionary)*k.WORD+13,
        early_pc=rom.early_pc,rom_sha256=sha(paths[0]),listing_sha256=sha(paths[1]),
        builder_sha256=sha(__file__),rule_source_sha256=sha(k.__file__),
        old_normalized_builder_sha256=sha(prior.__file__),
        noisy_reliability_smaller_Q_U_or_minimum_proved=False,previous_rule_ROM_or_G17_modified=False)
    paths[2].write_text(json.dumps(metadata,indent=2)+'\n');return metadata

if __name__=='__main__':
    root=HERE.parents[3];out=root/'figs/gray_counterexamples/unregistered_gawn1'
    print(json.dumps(build(out),sort_keys=True))
