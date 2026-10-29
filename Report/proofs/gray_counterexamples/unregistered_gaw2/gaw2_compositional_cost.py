"""GAW1 audit of frozen GAW0D: bounded CFG with proved helper/address contracts.

No kernel/emission change. Mutable payload values are never sampled.
All payload branches fork; loop/control/address contracts are the proof inputs.
"""
from pathlib import Path
import sys,json,time,hashlib
from functools import lru_cache
import gray_three_gather_gaw2 as k
import build_gray_three_gather_gaw2 as b
from dataclasses import replace
def instance():
    rom,rows,labels,errors=b.programme().assemble();assert not errors
    rom=replace(rom,bits=rom.bits+(0,)*(65536-len(rom.bits)))
    return rom,rows,labels
R=Path(__file__).resolve().parents[4]
D=R/'figs/gray_counterexamples/unregistered_gaw2'

ROM,LISTING,LABEL=instance();ROWS={r['address']:r for r in LISTING}
NATIVE_END=LABEL['workspace'];MAIN=LABEL['main'];COPY=LABEL['copy_loop'];ACTIVE=LABEL['active'];COPY_DONE=LABEL['copy_done']
LABEL_AT={}
for label,pc in LABEL.items():LABEL_AT.setdefault(pc,[]).append(label)

def distance(a,b):return max(1,abs(a[0]-b[1]),abs(a[1]-b[0]))

def recent(pc,reg):
    """Only use a literal nearest definition of this register, not a guessed value."""
    for q in range(pc-1,max(-1,pc-20),-1):
        row=ROWS.get(q)
        if row and row['operands'] and row['opcode'] in ('MOVI','ALU','ALUI','ALUX','LDX','CODE','BITCODE') and row['operands'][0]==reg:
            assert row['opcode']=='MOVI',(pc,reg,row)
            return row['operands'][1]
    raise AssertionError(('no recent literal',pc,reg))

# Loop counts belong to syntax-level integer counter invariants, not raw data.
LOOPS={LABEL['baseline_loop']:len(k.FIELD_NAMES),LABEL['incoming_loop']:22,LABEL['io_five_loop']:5,LABEL['io_mask_loop']:17,LABEL['wipe_loop']:k.FRAME_WORDS-6}
LOOPS.update({pc:22 for name,pc in LABEL.items() if name.startswith('zero_head_')})
BACK={}
for pc,row in ROWS.items():
    if row['opcode']=='BNZ' and row['operands'][1]<=pc:
        target=row['operands'][1]
        if target==COPY:continue
        if target==LABEL['vote_loop']:continue
        if target not in LOOPS:
            assert target in {LABEL[n] for n in ('head_error','move_right','move_left')},(pc,target)
            continue
        BACK[pc]=target

def region(pc,start,end):return LABEL[start]<=pc<LABEL[end]

def vote_field(pc,counts):
    """Every actual helper-call site and its typed old-field contract."""
    if pc<MAIN:return (201,226) # source chooses Out/Info/CourierL/CourierR
    if region(pc,'baseline_loop','data_updates'):
        field=6+5*dict(counts).get(LABEL['baseline_loop'],0);return (field,field)
    if region(pc,'data_updates','commit_info'):
        value=recent(pc,11);assert value in k.FIELD.values();return (value,value)
    if region(pc,'courier_move','courier_after'):
        value=recent(pc,11);assert value in (221,226);return (value,value)
    if region(pc,'special_left','special_right'):return (221,221)
    if region(pc,'special_right','special_after'):return (226,226)
    if region(pc,'active','has_head'):
        # Call parameter is an explicit preceding MOVI11 and is p or move.
        value=recent(pc,11);assert value in (6,11);return (value,value)
    if region(pc,'incoming_loop','head_step'):
        field=6+5*dict(counts).get(LABEL['incoming_loop'],0);return (field,field)
    if region(pc,'io_nonmem','io_out'):return (216,216)
    raise AssertionError(('uncontracted vote call',pc))

def target(pc,copy,counts,mask):
    row=ROWS[pc];op=row['opcode'];args=row['operands'];ct=dict(counts)
    if op in ('READ5','READMASK','FULLCOL'):
        reg=args[0] if op=='READ5' else args[1];value=recent(pc,reg)-k.PRIMARY_START;return (value,value)
    if op not in ('LDX','STX'):return None
    if op=='LDX':dst,base,index,lane,source=args
    else:dst,base,index,dest=args;source=2 if dest else 1
    base-=k.PRIMARY_START
    if base==128:
        value=recent(pc,index);return (128+value,128+value)
    if base in k.FIELD.values():
        if index==14:return (base+copy,base+copy)
        assert index==6,(pc,args)
        if base==36:return (36+copy,111+copy) # guarded four-bit register index
        assert base==116,(pc,args)
        if region(pc,'io_mask_loop','io_done'):
            j=ct.get(LABEL['io_mask_loop'],0);lane=j+(0 if mask else 3)
            return (116+5*lane+copy,116+5*lane+copy)
        if region(pc,'io_five_loop','io_mask'):
            j=ct.get(LABEL['io_five_loop'],0)
            return (116+5*(4-j)+copy,116+5*(12+j)+copy) # centres5..11, either side
        return (116+copy,196+copy) # kind0 has guarded lane0..16
    assert base==0,(pc,args)
    if index==6:
        loop=LABEL['incoming_loop'] if region(pc,'incoming_loop','head_step') else LABEL['baseline_loop']
        f=6+5*ct.get(loop,0);return (f+copy,f+copy)
    assert index==11,(pc,args)
    if LABEL['wipe_loop']<=pc<LABEL['vote']:return (6+ct.get(LABEL['wipe_loop'],0),)*2
    for loop in LOOPS:
        if any(n.startswith('zero_head_') for n in LABEL_AT.get(loop,())) and loop<=pc<loop+5:
            return (6+5*ct.get(loop,0)+copy,)*2
    if pc==LABEL['source_write']+3:return (4,5)
    value=recent(pc,11);assert 0<=value<=5,(pc,value);return (value,value)

# The central Age tests refer to Out[1]. These truth values are universal in
# each listed finite phase partition. Source-native Age tests are not fixed.
def clock_branch(pc,clock,counts):
    row=ROWS[pc];reg,dst=row['operands'];name=LABEL_AT.get(dst,[])
    if LABEL['workspace']<=pc<LABEL['workspace_choose']:
        previous=ROWS.get(pc-1)
        if previous and previous['opcode']=='ALUI' and previous['operands'][0:3]==[6,8,8]:return clock<previous['operands'][3]
        return None
    if pc<COPY or pc>=ACTIVE:return None
    previous=ROWS.get(pc-1)
    if previous and previous['opcode']=='ALUI':
        out,fn,src,value=previous['operands']
        if out==6 and src==8 and fn in (6,8):return (clock==value) if fn==6 else clock<value
    return None

def run(clock):
    # Explicit postorder longest-path traversal of the bounded contract DAG.
    # Python call depth is irrelevant; no payload register state is retained.
    def edge(state):
        pc,copy,counts,mask,pos=state
        row=ROWS[pc];op=row['opcode'];args=row['operands'];cost=1
        if op=='HLT':return cost,[]
        if pc in LOOPS and pc not in dict(counts):counts=tuple(sorted((*counts,(pc,0))))
        if pc==LABEL['io_mask'] and mask is None:return 0,[(pc,copy,counts,m,pos) for m in (0,1)]
        if op=='JMP' and args[0]==LABEL['vote']:
            f=vote_field(pc,counts);first=distance(pos,f);cost+=86+first+4
            return cost,[(recent(pc,15),copy,counts,mask,(f[0]+4,f[1]+4))]
        t=target(pc,copy,counts,mask)
        if t is not None:
            assert 0<=t[0]<=t[1]<k.FRAME_WORDS,(pc,t,counts)
            cost+=distance(pos,t);pos=t
        if op=='JMPR':
            assert pc<LABEL['v_halt'],('uncontracted indirect branch',pc)
            destinations=[LABEL[n] for n in ('v_halt','v_jmpr','v_imm','v_alu','v_ldx','v_stx','v_five','v_mask','v_code','v_branch','v_jump','v_alui','v_alux','v_bitcode','v_fullcol')]
        elif op=='JMP':destinations=[args[0]]
        elif op=='BNZ':
            dst=args[1]
            if dst==COPY:
                return cost,[(COPY,copy+1,(),None,pos)] if copy<4 else [(pc+1,copy,counts,mask,pos)]
            if pc in BACK:
                loop=BACK[pc];i=dict(counts)[loop];bound=(11 if mask==0 else 17) if loop==LABEL['io_mask_loop'] else LOOPS[loop]
                if i+1<bound:
                    revised=dict(counts);revised[loop]=i+1
                    return cost,[(loop,copy,tuple(sorted(revised.items())),mask,pos)]
                return cost,[(pc+1,copy,counts,mask,pos)]
            if mask is not None and dst in (LABEL['mask_full_lane'],LABEL['mask_full_bound']):choice=bool(mask)
            else:choice=clock_branch(pc,clock,counts)
            destinations=[dst] if choice is True else [pc+1] if choice is False else [pc+1,dst]
        else:destinations=[pc+1]
        return cost,[(nxt,copy,counts,mask,pos) for nxt in destinations]
    initial=(0,0,(),None,(0,0));done={};edges={};active={initial};stack=[(initial,0)]
    while stack:
        state,index=stack[-1]
        if state not in edges:
            edges[state]=edge(state)
            assert len(edges)<1000000,('state limit',clock,len(edges))
        cost,children=edges[state]
        if index==len(children):
            done[state]=cost+(max(done[c] for c in children) if children else 0)
            active.remove(state);stack.pop();continue
        child=children[index];stack[-1]=(state,index+1)
        if child not in done:
            assert child not in active,('contract CFG cycle',child)
            active.add(child);stack.append((child,0))
    return dict(clock=clock,tick_bound=done[initial],states=len(done))

def main():
    started=time.monotonic();cuts={0,1,k.U}
    for pc,row in ROWS.items():
        if row['opcode']=='ALUI':
            dst,fn,source,value=row['operands']
            if dst==6 and source==8 and fn in (k.ALU['EQ'],k.ALU['LT']) and (LABEL['workspace']<=pc<LABEL['workspace_choose'] or COPY<=pc<ACTIVE):
                cuts.add(value)
                if fn==k.ALU['EQ']:cuts.add(value+1)
    cuts={x for x in cuts if 0<=x<=k.U}
    points=sorted(cuts);clocks=points[:-1]
    records=[]
    for clock in clocks:
        row=run(clock);records.append(row);print(row,flush=True)
    data=dict(name='GAW2D compositional CFG/travel bound',phase_partition=points,records=records,
        maximum_ticks=max(r['tick_bound'] for r in records),available_ticks=65535,
        elapsed_seconds=time.monotonic()-started)
    (D/'GAW2_compositional_cost.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data))

if __name__=='__main__':main()
