"""Exact local resource/reference audit, not a universal semantic proof."""
import argparse
import hashlib
import json
from pathlib import Path

import binary_own_emitter as incomplete
import binary_own_emitter_full_v1 as rejected
import binary_own_emitter_full_rom_v2 as enlarged
import binary_own_rule_v1 as qrule
import binary_own_rule_rom_v2 as b


def resolved_listing(asm,rule=b):
    length,labels,rows=asm.listing()
    resolved=[];invalid=[]
    for pc,name,args,size in rows:
        values=[labels[x.name] if hasattr(x,'name') else x for x in args]
        if name!='DATA20':
            for value,width in zip(values,rule.ARGS[name]):
                if not 0<=value<(1<<width):invalid.append([pc,name,value,width])
        resolved.append([pc,name,values,size])
    return length,labels,resolved,invalid


def run(output):
    prefix=incomplete.OwnEmitter().prefix()
    try:prefix.assemble();raise AssertionError('incomplete Q overflow unexpectedly accepted')
    except incomplete.ProgrammeOverflow as exc:prefail=exc.args[0]
    qasm=rejected.FullEmitter().complete()
    try:qasm.assemble();raise AssertionError('full Q overflow unexpectedly accepted')
    except rejected.ProgrammeOverflow as exc:qfail=exc.args[0]
    assert (prefail['bits'],prefail['instructions'])==(16401,736)
    assert (qfail['bits'],qfail['instructions'],len(qfail['invalid_references']))==(65159,2918,372)
    asm=enlarged.FullEmitter().complete();beta,labels,rows=asm.assemble()
    length,labels,resolved,invalid=resolved_listing(asm)
    assert length==66815 and not invalid
    assert sum(name!='DATA20' for _,name,_,_ in rows)==2913
    assert sum(size for _,name,_,size in rows if name=='DATA20')==980
    assert len(beta)==73728 and beta[length:]==(0,)*(73728-length)
    assert (b.HEAD_BITS,b.FRAME_BITS,b.PRIMARY_START,b.COLLECTOR)==(746,4052,2070,2106)
    assert 2*b.FRAME_BITS<=b.Q
    assert b.CODE_BITS==9*b.Q and b.PC_BITS==17 and b.CODE_BITS>b.Q
    assert b.LANES==tuple(range(-8,9)) and sum(w for _,w in b.NATIVE)==37
    assert sum(w for _,w in b.META)==119 and b.WORK_BITS==37*11
    for pc,name,values,size in resolved:
        if name=='DATA20':
            assert size==20*len(values)
            continue
        word=sum(beta[pc+i]<<i for i in range(size))
        assert b.decode(word)==(name,tuple(values),size)
    # All retained old failure files are checked by the manifest, never replayed
    # as if they defined the current rule. These are exact listing obstructions.
    r={'passed':True,'scope':'exact specified-emitter size/reference/alphabet audit',
       'Q':b.Q,'U':b.U,'lambda':b.LAMBDA,'c':b.ERROR_SEPARATION,
       'GBP1_incomplete_prefix_failure':prefail,'GBP1_complete_Q_failure':qfail,
       'GBP1_K':qrule.FRAME_BITS,'GBP1_2K':2*qrule.FRAME_BITS,
       'GBP1R_K':b.FRAME_BITS,'GBP1R_2K':2*b.FRAME_BITS,
       'GBP1R_primary_interval':[b.PRIMARY_START,b.PRIMARY_START+b.FRAME_BITS],
       'GBP1R_code_bits':length,'GBP1R_instructions':2913,'GBP1R_data_words':49,
       'GBP1R_ROM_bits':b.CODE_BITS,'GBP1R_ROM_padding_bits':len(beta)-length,
       'GBP1R_PC_bits':b.PC_BITS,'GBP1R_Head_bits':b.HEAD_BITS,
       'GBP1R_metadata_bits':sum(w for _,w in b.META),
       'GBP1R_register_bits':b.REGISTERS*b.WORD,'GBP1R_work_bits':b.WORK_BITS,
       'GBP1R_invalid_references':invalid,
       'GBP1R_beta_sha256':hashlib.sha256(bytes(beta)).hexdigest(),
       'GBP1R_listing_sha256':hashlib.sha256(json.dumps(resolved,separators=(',',':')).encode()).hexdigest(),
       'active_late_updates':8*b.Q-2,'hypothetical_full_fifth_updates':16*b.Q-2,
       'literal_half_open_birth_execution_convention':True,
       'universal_emitted_identity':False,'universal_deadline':False,
       'Q_beta_fit':False,'gray_refutation':False,'iid_failure':False,'shorter_U':False}
    output.write_text(json.dumps(r,indent=2)+'\n')
    return r


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    r=run(ap.parse_args().output)
    print(json.dumps({k:v for k,v in r.items() if not k.endswith('_failure')},sort_keys=True))
