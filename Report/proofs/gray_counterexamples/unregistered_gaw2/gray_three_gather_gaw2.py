"""GAW2: explicitly changed total radius8 WORD100 three-gather rule.

Q8192/U128Q/lambda24/c104. h1/radius8/word/dictionary departures retained.
Authentic Mailbox erasure, three distinct banks and bitwise temporal vote.
Early native-only pass after complete third gather is a new finite schedule.
"""
from dataclasses import dataclass,replace
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'unregistered_gaw0'))
import gray_wider_word_gaw0 as base
from gray_wider_word_gaw0 import *
STAGE_STARTS=(0,32*Q,64*Q,96*Q,112*Q)
GATHER_STARTS=STAGE_STARTS[:3]
EARLY_RESET=72*Q+3
EARLY_BIRTH=EARLY_RESET+1
FIELD_NAMES=base.FIELD_NAMES+('mail_l','mail_r')+tuple('h%d_%d'%(g,lane) for g in (1,2,3) for lane in range(17))
FIELD={name:6+5*i for i,name in enumerate(FIELD_NAMES)}
FRAME_WORDS=6+5*len(FIELD_NAMES)
PRIMARY_START=Q//2-FRAME_WORDS//2
HEAD_ADDRESS=PRIMARY_START
# Explicit diagnostic code capacity; physical Programme only has Q sites.
TOKEN_BITS=11;DICTIONARY_SIZE=2048;CODE_CAPACITY=Q

@dataclass(frozen=True)
class ROM(base.ROM):
    early_pc:int=0

@dataclass(frozen=True)
class Cell(base.Cell):
    mail_l:tuple=(0,)*5
    mail_r:tuple=(0,)*5
    history1:tuple=(0,)*5
    history2:tuple=(0,)*5
    history3:tuple=(0,)*5


def majority3(a,b,c):return (a&b)|(c&(a|b))

def capture(g,lane):
    d=lane-8;s=GATHER_STARTS[g-1]
    return s+1 if not d else s+2+abs(d)*Q


def local_transition(cells,beta):
    assert set(cells)==set(range(-8,9))
    a=native_at(cells);age=a['age'];addr=a['addr'];wipe=a['f1'] and addr!=cells[0].addr
    a['wf1']=a['wf2']=0
    if not wipe and 96*Q<=age<98*Q:
        if Q-5<=addr<Q:a['wf1']=computed_primary(cells,Q-3-addr)&1
        if addr<=4 and not a['f1']:a['wf2']=computed_primary(cells,3-addr)&1
    reset=age in STAGE_STARTS or age==EARLY_RESET
    birth=age in (EARLY_BIRTH,112*Q+1)
    active=EARLY_BIRTH<age<75*Q or 112*Q+1<age<=120*Q
    names=('heads','mem','out','info','scratch','program','courier_l','courier_r','mail_l','mail_r','history1','history2','history3')
    values={name:[] for name in names}
    for y in SLOTS:
        address=(addr+y)%Q
        histories=[logical(cells,'history'+str(g),y)&((1<<(17*WORD))-1) for g in (1,2,3)]
        mem=logical(cells,'mem',y)&((1<<(17*WORD))-1)
        if age in STAGE_STARTS:mem=0
        elif age in (EARLY_RESET,112*Q+1):mem=majority3(*histories)
        ml=logical(cells,'mail_l',y)&MASK;mr=logical(cells,'mail_r',y)&MASK
        if age in STAGE_STARTS:ml=mr=0
        elif age in tuple(s+1 for s in GATHER_STARTS):ml=mr=logical(cells,'info',y)&MASK
        elif any(s<=age<s+16*Q for s in GATHER_STARTS):
            ml=logical(cells,'mail_l',y+1)&MASK;mr=logical(cells,'mail_r',y-1)&MASK
        if a['f1']:ml=mr=0
        for g in (1,2,3):
            if age in GATHER_STARTS[:g]:histories[g-1]=0
            else:
                for lane in range(17):
                    if age==capture(g,lane):
                        source='info' if lane==8 else 'mail_r' if lane<8 else 'mail_l'
                        word=logical(cells,source,y)&MASK
                        histories[g-1]=(histories[g-1]&~(MASK<<(lane*WORD)))|(word<<(lane*WORD))
        out=logical(cells,'out',y)&MASK;scratch=logical(cells,'scratch',y)&MASK
        info=out if age==0 else logical(cells,'info',y)&MASK;pb=beta_bit(beta,address)
        left=logical(cells,'courier_l',y)&MASK;right=logical(cells,'courier_r',y)&MASK
        if age in STAGE_STARTS:left=right=0
        elif age==75*Q:
            left=(out&1) if address==PRIMARY_START+3 else 0
            right=(out&1) if address==PRIMARY_START+2 else 0
        elif 75*Q<age<80*Q:
            incoming_left=logical(cells,'courier_l',y+1)&MASK;incoming_right=logical(cells,'courier_r',y-1)&MASK
            left=((left|incoming_left) if address==3 else incoming_left) if 3<=address<=PRIMARY_START+3 else 0
            right=((right|incoming_right) if address==Q-3 else incoming_right) if PRIMARY_START+2<=address<=Q-3 else 0
        if age==80*Q-1:
            if address==3:info=logical(cells,'courier_l',y)&MASK
            if address==Q-3:info=logical(cells,'courier_r',y)&MASK
        if reset:head=ZERO;out=scratch=0
        elif birth:head=Packet(p=1,pc=beta.early_pc if age==EARLY_BIRTH else 0) if address==HEAD_ADDRESS else ZERO
        elif active:
            head=incoming([unpack(logical(cells,'heads',y+j)) for j in (-1,0,1)])
            head,ow,sw=step_packet(head,address,mem,out,scratch,logical(cells,'program',y)&MASK,beta)
            if ow is not None:out=ow
            if sw is not None:scratch=sw
        else:head=unpack(logical(cells,'heads',y))
        if wipe:head=ZERO;mem=out=info=scratch=pb=left=right=ml=mr=0;histories=[0]*3
        for name,value in zip(names,(pack(head),mem,out,info,scratch,pb,left,right,ml,mr,*histories)):values[name].append(value)
    return Cell(**a,**{name:tuple(v) for name,v in values.items()})


def cell_words(c):
    result=[getattr(c,n) for n in NATIVE_NAMES];packets=[unpack(v) for v in c.heads]
    for name in FIELD_NAMES:
        if name in META:result.extend(getattr(p,name) for p in packets)
        elif name.startswith('r') and name[1:].isdigit():result.extend(p.regs[int(name[1:])] for p in packets)
        elif name.startswith('m') and name[1:].isdigit():result.extend((v>>(int(name[1:])*WORD))&MASK for v in c.mem)
        elif name.startswith('h') and '_' in name:
            g,lane=map(int,name[1:].split('_'));result.extend((v>>(lane*WORD))&MASK for v in getattr(c,'history'+str(g)))
        else:result.extend(getattr(c,name))
    assert len(result)==FRAME_WORDS;return result


def cell_from_words(words):
    assert len(words)==FRAME_WORDS
    data=dict(zip(NATIVE_NAMES,words[:6]));packets=[dict(regs=[0]*16) for _ in range(5)]
    for field in ('mem','history1','history2','history3'):data[field]=[0]*5
    for i,name in enumerate(FIELD_NAMES):
        vals=words[6+5*i:11+5*i]
        if name in META:
            for q,v in enumerate(vals):packets[q][name]=v
        elif name.startswith('r') and name[1:].isdigit():
            for q,v in enumerate(vals):packets[q]['regs'][int(name[1:])]=v
        elif name.startswith('m') and name[1:].isdigit():
            for q,v in enumerate(vals):data['mem'][q]|=v<<(int(name[1:])*WORD)
        elif name.startswith('h') and '_' in name:
            g,lane=map(int,name[1:].split('_'))
            for q,v in enumerate(vals):data['history'+str(g)][q]|=v<<(lane*WORD)
        else:data[name]=tuple(vals)
    for field in ('mem','history1','history2','history3'):data[field]=tuple(data[field])
    data['heads']=tuple(pack(Packet(**{**p,'regs':tuple(p['regs'])})) for p in packets)
    return Cell(**data)


def input_tape(cells):
    words={j:cell_words(cells[j]) for j in range(-8,9)}
    return {PRIMARY_START+i:sum(words[j][i]<<((j+8)*WORD) for j in range(-8,9)) for i in range(FRAME_WORDS)}


def execute(beta,tape,limit=200000,record=False,early=False):
    p=Packet(p=1,pc=beta.early_pc if early else 0);address=HEAD_ADDRESS;out={};scratch={};trace=[]
    for tick in range(limit):
        address+=1 if p.move==1 else -1 if p.move==2 else 0
        assert 0<=address<Q
        oldp=p;p,ow,sw=step_packet(p,address,tape.get(address,0),out.get(address,0),scratch.get(address,0),beta_bit(beta,address),beta)
        if ow is not None:out[address]=ow
        if sw is not None:scratch[address]=sw
        if record:trace.append((address,oldp,p,ow,sw))
        if p.mode in (HALT,ERROR):return out,tick+1,p,trace
    return out,limit,p,trace
