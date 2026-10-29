"""Emit the isolated new own evaluator; all added masks are explicit."""
from pathlib import Path
from dataclasses import replace,asdict
import hashlib,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'unregistered_gaw2'))
import build_gray_three_gather_gaw2r as old_builder
import normalized_gawn0 as k

WRITES={'MOVI','ALU','ALUI','ALUX','LDX','CODE','BITCODE','READMASK','FULLCOL'}

def programme():
    a=old_builder.programme(engine=k)
    original_rows=list(a.rows);new_rows=[];masks=[];other_raw_reads=[]
    for index,(opcode,operands) in enumerate(original_rows):
        new_rows.append((opcode,operands))
        if opcode!='LDX' or operands[1:]!=(k.PRIMARY_START,11,7,0):continue
        nearest=next(((i,row) for i,row in reversed(list(enumerate(original_rows[:index])))
            if row[0] in WRITES and row[1] and row[1][0]==11),None)
        if nearest and nearest[1][0]=='MOVI' and nearest[1][1][1] in (0,1):
            field=nearest[1][1][1];width=k.NATIVE_WIDTHS[field];dst=operands[0]
            mask=('ALUI',(dst,k.ALU['AND'],dst,(1<<width)-1))
            masks.append(dict(original_row=index,new_mask_row=len(new_rows),field=field,
                width=width,destination_register=dst,old_index_definition_row=nearest[0]))
            new_rows.append(mask)
        else:other_raw_reads.append(dict(original_row=index,operands=operands))
    assert len(masks)==24 and sum(m['field']==0 for m in masks)==16
    assert sum(m['field']==1 for m in masks)==8
    # The sole other source0/P/index11 read is the unchanged SF vote helper.
    # Its lane-register is6, so it is excluded by the exact tuple above.
    assert not other_raw_reads,other_raw_reads
    a.rows[:]=new_rows
    a.normalization_masks=masks;a.original_unresolved_rows=original_rows
    return a

def instance():
    a=programme();rom,listing,labels,errors=a.assemble();assert not errors,errors
    assert len(rom.bits)<=65536
    rom=replace(rom,bits=rom.bits+(0,)*(65536-len(rom.bits)))
    return rom,listing,labels,a

def sha_bytes(data):return hashlib.sha256(data).hexdigest()

def build(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    targets=[out/'GAWN0_rom.json',out/'GAWN0_listing.json',out/'GAWN0_emission.json']
    assert not any(p.exists() for p in targets),'new emission only; never overwrite accepted artifacts'
    rom,listing,labels,a=instance()
    targets[0].write_text(json.dumps(asdict(rom),indent=2)+'\n')
    targets[1].write_text(json.dumps(dict(listing=listing,labels=labels),indent=2)+'\n')
    metadata=dict(explicit_new_own_ROM_proposal=True,frozen_GAW2R_or_G17_changed=False,
        Q=k.Q,U=k.U,WORD=k.WORD,FRAME_WORDS=k.FRAME_WORDS,PRIMARY_START=k.PRIMARY_START,
        native_widths=k.NATIVE_WIDTHS,normalization_masks=a.normalization_masks,
        token_count=rom.token_count,used_dictionary=rom.used_dictionary,early_pc=rom.early_pc,
        used_token_stream_bits=rom.token_count*rom.token_bits,
        uncompressed_instruction_bit_sum=sum(k.LENGTH[k.OP[r['opcode']]] if r['opcode']!='DATA' else k.WORD for r in listing),
        immutable_allocated_bits=len(rom.bits)+len(rom.dictionary)*k.WORD+13,
        rom_sha256=sha_bytes(targets[0].read_bytes()),listing_sha256=sha_bytes(targets[1].read_bytes()),
        builder_sha256=sha_bytes(Path(__file__).read_bytes()),
        rule_source_sha256=sha_bytes(Path(k.__file__).read_bytes()),
        universal_padded_execution_or_physical_period_proved_by_emission=False,
        higher_error_repair_iid_or_smaller_constants_proved=False)
    targets[2].write_text(json.dumps(metadata,indent=2)+'\n')
    return metadata

if __name__=='__main__':
    root=Path(__file__).resolve().parents[4]
    result=build(root/'figs/gray_counterexamples/unregistered_gawn0')
    print(json.dumps({key:result[key] for key in ('Q','U','token_count','used_dictionary','used_token_stream_bits','uncompressed_instruction_bit_sum',
        'immutable_allocated_bits','rom_sha256','listing_sha256')},sort_keys=True))
