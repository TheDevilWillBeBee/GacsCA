"""Counted GBD6 Mailbox/History extension of frozen native software.

This listing is deliberately complete for THESE two output fields only.
Full Head/Info/WF/packing software is not substituted by an oracle. If this
extension alone exceeds Q, the stated append-only architecture is rejected.
"""
from pathlib import Path
import sys
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'unregistered_gbd4'))
import controller as c
import layout as l
import native_emitter as n
sys.path.insert(0,str(BASE/'unregistered_gbd3'))
import helpers as h

NOW=8;KEEP=10
def load(a,slot):a.lit(5,slot);a.call('BLOAD')
def store(a,slot):a.lit(5,slot);a.call('BSTORE')

def lane(a,offset=0,prefix='LANE'):
    """R2=8+S[R6]+offset, preserves R4/R6/R7, no hidden table."""
    a.cp(2,6);a.lit(5,0);a.br(3,6,5,prefix+'_ZERO')
    a.lit(5,3);a.br(5,6,5,prefix+'_NEG')
    a.lit(5,2);a.alu('sub',2,2,5);a.jump(prefix+'_DONE')
    a.mark(prefix+'_NEG');a.lit(5,3);a.alu('sub',2,2,5);a.jump(prefix+'_DONE')
    a.mark(prefix+'_ZERO');a.lit(2,0)
    a.mark(prefix+'_DONE');a.lit(5,8+offset);a.alu('add',2,2,5)

def get(a,name,count,prefix,offset=0,bank=False):
    a.lit(0,l.SF_OFFSETS[name]);a.lit(1,count)
    if bank:
        a.lit(5,85);a.alu('mul',5,7,5);a.alu('add',0,0,5)
    lane(a,offset,prefix);a.call('FGET')

def put(a,name,count,bank=False):
    a.cp(0,4);a.lit(1,count);a.lit(2,l.SF_OFFSETS[name])
    if bank:a.lit(5,85);a.alu('mul',5,7,5);a.alu('add',2,2,5)
    a.alu('add',2,2,6);a.call('FPUT')

def native_rows(printed=False):
    original=n.native_program(printed)
    reverse={pc:name for name,pc in original['labels'].items()}
    a=n.Assembly()
    by_row={}
    for name,pc in original['labels'].items():
        row=original['positions'].index(pc);by_row.setdefault(row,[]).append(name)
    for i,row in enumerate(original['rows']):
        for name in by_row.get(i,[]):a.mark(name)
        if row[0]=='HALT':a.jump('BODY');continue
        values=list(row[1:])
        if row[0] in ('BR','CALL'):values[-1]=reverse[values[-1]]
        a.e(row[0],*values)
    return a,original

def programme(printed=False):
    a,original=native_rows(printed)
    a.mark('BODY')
    # Frozen native tail leaves selected newGF in R3, incremented Age inR4.
    # NOW is the formerly unused real RAM word2597. KEEP adds word2599.
    a.lit(7,1);a.alu('sub',0,4,7);store(a,NOW)
    a.lit(4,n.descriptor(0,13));a.lit(5,8);a.call('RAW')
    a.alu('eq',0,0,3);store(a,KEEP)
    a.lit(6,0);a.mark('MAIL_Q')
    get(a,'Mailbox',4,'MAIL_OLD');a.lit(5,3);a.alu('and',4,0,5)
    load(a,NOW);a.cp(1,0)
    a.lit(5,18);a.alu('shr',2,1,5);a.lit(5,3);a.br(6,5,2,'MAIL_FINISH')
    a.lit(5,(1<<18)-1);a.alu('and',1,1,5)
    a.lit(5,0);a.br(3,1,5,'MAIL_ZERO')
    a.lit(5,1);a.br(3,1,5,'MAIL_INFO')
    a.lit(5,16*c.Q);a.br(6,5,1,'MAIL_FINISH')
    get(a,'Mailbox',4,'MAIL_LEFT',offset=-1)
    a.lit(5,1);a.alu('and',4,0,5)
    get(a,'Mailbox',4,'MAIL_RIGHT',offset=1)
    a.lit(5,2);a.alu('and',0,0,5);a.alu('or',4,4,0);a.jump('MAIL_FINISH')
    a.mark('MAIL_INFO');get(a,'Info',1,'MAIL_SOURCE')
    a.lit(5,3);a.alu('mul',4,0,5);a.jump('MAIL_FINISH')
    a.mark('MAIL_ZERO');a.lit(4,0)
    a.mark('MAIL_FINISH');load(a,n.RAM['F1']);a.br(2,0,0,'MAIL_ERASE')
    load(a,KEEP);a.br(1,0,0,'MAIL_ERASE')
    load(a,NOW);a.lit(5,c.U-1);a.br(3,0,5,'MAIL_ERASE');a.jump('MAIL_WRITE')
    a.mark('MAIL_ERASE');a.lit(4,0)
    a.mark('MAIL_WRITE');put(a,'Mailbox',4)
    a.lit(5,1);a.alu('add',6,6,5);a.lit(5,5);a.br(5,6,5,'MAIL_Q')

    a.lit(6,0);a.mark('HIST_Q');a.lit(7,0);a.mark('HIST_G')
    get(a,'History',17,'HIST_OLD',bank=True);a.cp(4,0)
    load(a,NOW);a.cp(1,0)
    a.lit(5,(1<<18)-1);a.alu('and',2,1,5);a.lit(5,0);a.br(4,2,5,'HIST_CAPTURE')
    a.lit(5,18);a.alu('shr',2,1,5);a.br(6,2,7,'HIST_ZERO')
    a.mark('HIST_CAPTURE')
    a.lit(5,32*c.Q);a.alu('mul',5,7,5);a.alu('sub',1,1,5)
    a.lit(5,1);a.br(3,1,5,'HIST_SELF')
    a.lit(5,2);a.alu('sub',1,1,5)
    a.lit(5,c.Q-1);a.alu('and',2,1,5);a.lit(5,0);a.br(4,2,5,'HIST_FINISH')
    a.lit(5,13);a.alu('shr',1,1,5)
    a.lit(5,1);a.br(5,1,5,'HIST_FINISH')
    a.lit(5,8);a.br(5,5,1,'HIST_FINISH')
    # Keep actual k in R3 while fetching Mailbox; FGET clobbers R3,
    # so cache k in a real Out RAM word before that call.
    a.cp(0,1);store(a,11)
    get(a,'Mailbox',4,'HIST_MAIL')
    a.cp(1,0);load(a,11);a.cp(2,0)
    a.lit(5,8);a.alu('sub',3,5,2);a.alu('add',2,5,2)
    # Save right index in RAM12; RAMLOAD preserves left indexR3/mailR1.
    a.cp(0,2);store(a,12)
    a.lit(0,1);a.alu('shl',0,0,3);a.alu('not',0,0,0);a.alu('and',4,4,0)
    a.lit(0,1);a.alu('and',0,1,0);a.alu('shl',0,0,3);a.alu('or',4,4,0)
    load(a,12);a.cp(3,0)
    a.lit(0,1);a.alu('shl',0,0,3);a.alu('not',0,0,0);a.alu('and',4,4,0)
    a.lit(0,1);a.alu('shr',0,1,0);a.lit(5,1);a.alu('and',0,0,5)
    a.alu('shl',0,0,3);a.alu('or',4,4,0);a.jump('HIST_FINISH')
    a.mark('HIST_SELF');get(a,'Info',1,'HIST_SOURCE')
    a.lit(5,8);a.alu('shl',0,0,5);a.lit(5,c.MASK^(1<<8));a.alu('and',4,4,5)
    a.alu('or',4,4,0);a.jump('HIST_FINISH')
    a.mark('HIST_ZERO');a.lit(4,0)
    a.mark('HIST_FINISH');load(a,KEEP);a.br(1,0,0,'HIST_ERASE')
    load(a,NOW);a.lit(5,c.U-1);a.br(3,0,5,'HIST_ERASE');a.jump('HIST_WRITE')
    a.mark('HIST_ERASE');a.lit(4,0)
    a.mark('HIST_WRITE');put(a,'History',17,bank=True)
    a.lit(5,1);a.alu('add',7,7,5);a.lit(5,3);a.br(5,7,5,'HIST_G')
    a.lit(5,1);a.alu('add',6,6,5);a.lit(5,5);a.br(5,6,5,'HIST_Q')
    a.e('HALT')
    a.mark('FGET')
    for row in h.field_get_rows():a.e(*row)
    a.mark('FPUT')
    for row in h.field_put_rows():a.e(*row)
    # The native RAM helpers clobberR6/R7, so they cannot serve the new
    # q/g loops. These explicitly counted helpers preserveR1/R3/R4/R6/R7.
    # R2 andR5 are temporary; one real Head return link suffices.
    for label,kind in (('BLOAD','READ'),('BSTORE','WRITE')):
        a.mark(label);a.lit(2,n.RAM_BASE+2);a.alu('add',5,5,2);a.e('MOVE',5)
        a.lit(2,0);a.lit(5,20)
        if kind=='READ':a.e('READ',0,2,2,5,0,1)
        else:a.e('WRITE',0,2,5,0)
        a.e('RET')
    result=a.compile()
    result['complete_native_Mailbox_History_only']=True
    result['native_prefix_bits']=original['bits']
    result['new_controller_bits']=result['bits']-original['bits']
    result['scratch_Out_positions']=list(range(n.RAM_BASE,n.RAM_BASE+13))
    result['omitted_full_own_fields']=['Info','Mem','InputTag','Out','OutputTag','Scratch','Couriers','Head','WF1','WF2']
    return result

def standalone(printed=False):
    """Issued <=Q controller component, with declared native-result ABI.

    This tests the same BODY software, relocated to entry0, plus its real
    RAW/helper code. It is NOT an issued concatenated own programme.
    """
    full=programme(printed);positions=full['positions']
    begin=positions.index(full['labels']['BODY'])
    raw_begin=positions.index(full['labels']['RAW'])
    raw_end=positions.index(full['labels']['RAMLOAD'])
    selected=list(range(begin,len(full['rows'])))+list(range(raw_begin,raw_end))
    selected_set=set(selected);by_row={}
    reverse={pc:name for name,pc in full['labels'].items()}
    for name,pc in full['labels'].items():
        index=positions.index(pc)
        if index in selected_set:by_row.setdefault(index,[]).append(name)
    a=n.Assembly()
    for index in selected:
        for name in by_row.get(index,[]):a.mark(name)
        row=full['rows'][index];values=list(row[1:])
        if row[0] in ('BR','CALL'):values[-1]=reverse[values[-1]]
        a.e(row[0],*values)
    result=a.compile();assert result['beta'] is not None and result['bits']<=c.Q
    return result
