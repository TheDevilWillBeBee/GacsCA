"""Emit the new fixed Q4096 rule's own complete normalized evaluator.

PC operand encoding narrows to12 bits; READ5 still extracts20-bit generic
components. Native Age acquisitions are explicitly normalized to19 bits.
No new opcode or native/whole-rule host evaluation is added.
"""
from pathlib import Path
from dataclasses import replace,asdict
import hashlib,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(HERE),str(HERE.parent/'unregistered_gaw2')]
import build_gray_three_gather_gaw2r as inherited
import small_rule_gawn2 as k
WRITES={'MOVI','ALU','ALUI','ALUX','LDX','CODE','BITCODE','READMASK','FULLCOL'}

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
    e('MOVI',6,0);e('MOVI',7,16);e('MOVI',8,5)
    alu(0,'MOV',5);e('JMPR',15)
    assert sum(name!='LABEL' for name,args in rows)==37
    return rows

def programme():
    a=inherited.programme(engine=k);initial=list(a.rows);rows=[]
    substitutions=[];direct_masks=[];age_vectors=[]
    for index,row in enumerate(initial):
        name,args=row
        changed=row
        if row==('MOVI',(15,13)):
            assert initial[index+1]==('ALU',(0,k.ALU['VADDINDEX'],0,1,15))
            changed=('MOVI',(15,k.GF_BITS));substitutions.append(dict(kind='GF_vector_width',old_row=index))
        elif name=='ALUI' and args[1]==k.ALU['AND']:
            if args==(8,k.ALU['AND'],8,k.SMALL_MASK):
                changed=('ALUI',(8,k.ALU['AND'],8,k.AGE_MASK));substitutions.append(dict(kind='native_Age_successor_modulus',old_row=index))
            elif args[3]==8191 and args[0]==args[2] and args[0] in (2,12):
                changed=('ALUI',(*args[:3],k.GF_MASK));substitutions.append(dict(kind='service_GF_modulus',old_row=index))
        if name=='ALUI' and args[1] in (k.ALU['EQ'],k.ALU['LT']):
            new={102*k.Q+1:k.LATE_BIRTH,102*k.Q+2:k.LATE_BIRTH+1,120*k.Q+1:k.ACTIVE_END+1}.get(args[3])
            if new is not None:
                changed=('ALUI',(*args[:3],new));substitutions.append(dict(kind='late_schedule',old_row=index,old=args[3],new=new))
        rows.append(changed)
        if name=='READ5':
            previous=initial[index-1];assert previous[0]=='MOVI' and previous[1][0]==11
            field=previous[1][1]-k.PRIMARY_START;assert field in (0,1)
            if field==1:
                start=len(rows);rows.extend([('MOVI',(1,0)),('MOVI',(15,k.AGE_BITS)),('ALU',(0,k.ALU['VADDINDEX'],0,1,15))])
                age_vectors.append(dict(old_row=index,new_macro_row=start,field=field))
        if name=='LDX' and args[1:]==(k.PRIMARY_START,11,7,0):
            nearest=next(((i,r) for i,r in reversed(list(enumerate(initial[:index])))
                if r[0] in WRITES and r[1] and r[1][0]==11),None)
            assert nearest and nearest[1][0]=='MOVI' and nearest[1][1][1] in (0,1),nearest
            field=nearest[1][1][1];width=k.NATIVE_WIDTHS[field];start=len(rows)
            rows.append(('ALUI',(args[0],k.ALU['AND'],args[0],(1<<width)-1)))
            direct_masks.append(dict(old_row=index,new_mask_row=start,field=field,width=width))
    assert len(direct_masks)==24 and len(age_vectors)==16
    assert sum(m['field']==0 for m in direct_masks)==16
    assert sum(s['kind']=='GF_vector_width' for s in substitutions)==16
    assert sum(s['kind']=='native_Age_successor_modulus' for s in substitutions)==8
    assert sum(s['kind']=='service_GF_modulus' for s in substitutions)==5
    assert sum(s['kind']=='late_schedule' for s in substitutions)==4
    start=next(i for i,r in enumerate(rows) if r==('LABEL',('vote',)))
    end=next(i for i,r in enumerate(rows) if r==('LABEL',('slots',)))
    old_helper=rows[start:end];block=helper();delta=len(block)-(end-start)
    rows[start:end]=block
    for m in direct_masks:
        if m['new_mask_row']>=end:m['new_mask_row']+=delta
    for m in age_vectors:
        if m['new_macro_row']>=end:m['new_macro_row']+=delta
    a.rows[:]=rows;a.initial_unresolved_rows=initial;a.direct_masks=direct_masks
    a.age_vector_macros=age_vectors;a.substitutions=substitutions;a.old_helper=old_helper
    return a

def instance():
    a=programme();rom,listing,labels,errors=a.assemble();assert not errors,errors
    assert rom.token_count<=k.CODE_CAPACITY and len(rom.bits)<=65536
    rom=replace(rom,bits=rom.bits+(0,)*(65536-len(rom.bits)))
    return rom,listing,labels,a

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def build(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    paths=[out/'GAWN2_rom.json',out/'GAWN2_listing.json',out/'GAWN2_emission.json']
    assert not any(p.exists() for p in paths),'never overwrite frozen emission'
    rom,listing,labels,a=instance()
    paths[0].write_text(json.dumps(asdict(rom),indent=2)+'\n')
    paths[1].write_text(json.dumps(dict(listing=listing,labels=labels),indent=2)+'\n')
    record=dict(explicit_new_rule_constants_schedule_and_own_ROM=True,Q=k.Q,U=k.U,
        original_error_lambda=24,original_error_separation=104,native_widths=k.NATIVE_WIDTHS,PC_BITS=k.PC_BITS,
        generic_READ5_component_bits=20,WORD=k.WORD,FRAME_WORDS=k.FRAME_WORDS,PRIMARY_START=k.PRIMARY_START,
        LATE_RESET=k.LATE_RESET,LATE_BIRTH=k.LATE_BIRTH,ACTIVE_END=k.ACTIVE_END,available_late_updates=k.ACTIVE_END-k.LATE_BIRTH,
        direct_masks=a.direct_masks,Age_vector_normalizations=a.age_vector_macros,substitutions=a.substitutions,
        helper_executed_instructions=37,token_count=rom.token_count,dictionary_used=rom.used_dictionary,
        used_token_stream_bits=rom.token_count*rom.token_bits,immutable_allocated_bits=len(rom.bits)+len(rom.dictionary)*k.WORD+12,
        early_pc=rom.early_pc,rom_sha256=sha(paths[0]),listing_sha256=sha(paths[1]),
        builder_sha256=sha(__file__),rule_sha256=sha(k.__file__),inherited_emitter_sha256=sha(inherited.__file__),
        no_new_opcode_or_host_rule_evaluator=True,G17_or_previously_frozen_rules_modified=False,
        whole_semantics_deadline_period_or_noisy_reliability_proved_by_emission=False)
    paths[2].write_text(json.dumps(record,indent=2)+'\n');return record

if __name__=='__main__':print(json.dumps(build(ROOT/'figs/gray_counterexamples/unregistered_gawn2'),sort_keys=True))
