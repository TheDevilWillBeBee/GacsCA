"""Sound bit-cube execution of frozen GAW2R on one arbitrary Word100 record.

This is a proof checker, not a changed CA. Unknown input words are never
projected. READ5/READMASK perform only the existing instruction semantics.
Unsupported precision is an overapproximation, never a guessed constant.
"""
from pathlib import Path
from dataclasses import dataclass,field
from collections import Counter
from functools import lru_cache
import hashlib,json,sys,time
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
sys.path.insert(0,str(S.parent/'unregistered_gaw18'))
import check_gaw18_malformed_period as prior
k=prior.k;own=prior.own;base=prior.base;P=k.PRIMARY_START;MASK=k.MASK
D=ROOT/'figs/gray_counterexamples/unregistered_gaw19'

@dataclass(frozen=True)
class B:
    v:int=0;u:int=0
    def __post_init__(self):assert 0<=self.v<=MASK and 0<=self.u<=MASK and not self.v&self.u
    @property
    def high(self):return self.v|self.u
    @property
    def constant(self):return not self.u
    def contains(self,x):return 0<=x<=MASK and (x&~self.u)==self.v

def C(v):return B(v&MASK,0)
TOP=B(0,MASK);BOOL=B(0,1)
def cube(lo,hi):
    assert 0<=lo<=hi<=MASK
    u=(1<<(lo^hi).bit_length())-1
    return B(lo&~u,u)
def band(a,b):
    lo=a.v&b.v;hi=a.high&b.high;return B(lo,hi&~lo)
def bor(a,b):
    lo=a.v|b.v;hi=a.high|b.high;return B(lo,hi&~lo)
def bxor(a,b):
    u=a.u|b.u;return B((a.v^b.v)&~u,u)
def lnot(a):return C(1) if not a.high else C(0) if a.v else BOOL
def eq(a,b):
    if (a.v^b.v)&~(a.u|b.u):return C(0)
    return C(a.v==b.v) if a.constant and b.constant else BOOL
def lt(a,b):return C(1) if a.high<b.v else C(0) if a.v>=b.high else BOOL
def cut(a,start,width):return B((a.v>>start)&((1<<width)-1),(a.u>>start)&((1<<width)-1))
def shift(a,n):return B((a.v<<n)&MASK,(a.u<<n)&MASK) if n>=0 else B(a.v>>-n,a.u>>-n)

def alu(op,a,b,c):
    """Overapproximation of every finite generic_alu operation used here."""
    if op==0:return a
    if op==3:return band(a,b)
    if op==4:return bor(a,b)
    if op==5:return bxor(a,b)
    if op==6:return eq(a,b)
    if op==7:return lnot(eq(a,b))
    if op==8:return lt(a,b)
    if op==9:return lnot(a)
    if op==19:return B(MASK^a.high,a.u)
    arity=1 if op in (0,9,13,19) else 3 if op in (12,16,18) else 2
    used=(a,b,c)[:arity]
    if all(x.constant for x in used):return C(k.generic_alu(op,a.v,b.v,c.v))
    if op==10:
        return cut(a,b.v,1) if b.constant and b.v<100 else C(0) if b.v>=100 else BOOL
    if op in (11,21) and b.constant:
        if op==21:return C(0) if b.v>=100 else shift(a,-b.v)
        n=(b.v if b.v<(1<<19) else b.v-(1<<20)) if b.v<(1<<20) else b.v if b.v<(1<<99) else b.v-(1<<100)
        return C(0) if abs(n)>=100 else shift(a,n)
    if op==13:return cube(a.v.bit_count(),a.high.bit_count())
    if op in (14,15):
        chunks=[cut(a,20*i,20) for i in range(5)]
        known=Counter(v.v for v in chunks if v.constant)
        quorum=next((v for v,n in known.items() if n>=3),None)
        if quorum is not None:return C(1 if op==15 else quorum)
        if all(v.constant for v in chunks):return C(0) if op==15 else b
        return BOOL if op==15 else TOP
    if op==16 and b.constant and c.constant and 1<=c.v<=20:
        step=b.v if b.v<(1<<99) else b.v-(1<<100)
        result=C(0)
        for i in range(5):
            q=cut(a,20*i,20)
            part=C((q.v+step*(i+1))&((1<<c.v)-1)) if q.constant else B(0,(1<<c.v)-1)
            result=bor(result,shift(part,20*i))
        return result
    if op==17:
        r=C(0)
        for i in range(5):r=bor(r,shift(lnot(eq(cut(a,20*i,20),b)),i))
        return r
    if op==12 and b.constant and c.constant:
        lo=c.v&15;hi=(c.v>>4)&15;lo=lo if lo<8 else lo-16;hi=hi if hi<8 else hi-16
        if not -5<=lo<=hi<=5:return C(1<<99)
        positions=[j+5 for j in range(lo,hi+1) if (c.v>>8)&1 and 0<=b.v+j<k.Q]
        return cube(sum((a.v>>j)&1 for j in positions),sum((a.high>>j)&1 for j in positions))
    if op==20 and b.constant and 1<=b.v<=100:
        q=cut(a,0,b.v);sign=cut(q,b.v-1,1);high=MASK^((1<<b.v)-1)
        return B(q.v|(high if sign.v else 0),q.u|(high if sign.u else 0))
    # Addition/subtraction/multiplication or varying shifts not determined
    # by their inputs stay TOP. A proof may consequently fail, safely.
    return TOP

@dataclass
class Machine:
    pc:int=0;mode:int=k.RUN;target:int=0;args:int=0;move:int=0;address:int=P
    regs:tuple=(C(0),)*16
    out:dict=field(default_factory=dict);scratch:dict=field(default_factory=dict)
    def clone(self):return Machine(self.pc,self.mode,self.target,self.args,self.move,self.address,self.regs,dict(self.out),dict(self.scratch))
    def same(self,b):return (self.pc,self.mode,self.target,self.args,self.move,self.address,self.regs,self.out,self.scratch)==(b.pc,b.mode,b.target,b.args,b.move,b.address,b.regs,b.out,b.scratch)

@lru_cache(None)
def clean_words(g):return tuple(k.cell_words(base.nextH(g)))

def input_word(g,address,lane):
    i=address-P;assert 0<=i<k.FRAME_WORDS and 0<=lane<=16
    h=g+lane-8
    return TOP if h==0 else C(clean_words(h)[i])

def number(a,context):assert a.constant,(context,'unresolved symbolic control',hex(a.v),hex(a.u));return a.v

def step(state,g,counts):
    s=state;s.address+=1 if s.move==1 else -1 if s.move==2 else 0
    assert P<=s.address<P+k.FRAME_WORDS,('unsafe symbolic address',g,s.address)
    if s.mode in (k.HALT,k.ERROR):s.move=0;return [s],None
    if s.mode==k.RUN:
        ins=k.decode(k.beta_word(own.ROM,s.pc));assert ins is not None
        name,args=ins;counts['opcode_'+name]+=1;nextpc=(s.pc+1)%k.Q;r=list(s.regs)
        if name=='HLT':s.mode=k.HALT;s.move=0;return [s],None
        if name in ('JMP','JMPR','BNZ'):
            if name=='BNZ':
                q=r[args[0]];poss=([False] if not q.high else [True] if q.v else [False,True])
                result=[]
                for true in poss:
                    v=s.clone() if len(poss)>1 else s
                    v.pc=args[1] if true else nextpc;v.move=0;result.append(v)
                if len(poss)>1:counts['unresolved_branch_forks']+=1
                return result,None
            s.pc=args[0] if name=='JMP' else number(r[args[0]],('JMPR',s.pc))
            assert s.pc<k.Q;s.move=0;return [s],None
        if name=='MOVI':r[args[0]]=C(args[1])
        elif name in ('CODE','BITCODE'):
            v=number(r[args[1]],(name,s.pc));r[args[0]]=C(k.beta_word(own.ROM,v) if name=='CODE' else k.beta_bit(own.ROM,v))
        elif name in ('ALU','ALUI','ALUX'):
            if name=='ALUI':dst,op,ai,value=args;x,y,z=r[ai],C(value),C(0)
            else:
                dst,op,ai,bi,ci=args;op=number(r[op],('ALUX',s.pc)) if name=='ALUX' else op;x,y,z=r[ai],r[bi],r[ci]
            r[dst]=alu(op,x,y,z);counts['alu_'+str(op)]+=1
            if op in (14,15):
                if any(v.u for v in (x,y,z)):counts['quorum_operations_with_unknown_input']+=1
                assert r[dst].constant,('unresolved native quorum',g,s.pc,op)
        else:
            if name=='LDX':
                dst,start,index,lane,source=args;ix=number(r[index],('LDX index',s.pc));la=number(r[lane],('LDX lane',s.pc))
                assert ix<k.Q and start+ix<k.Q and la<=16
                target=start+ix;task=k.descriptor(0,dst,lane=la,source=source)
            elif name=='STX':
                value,start,index,dest=args;ix=number(r[index],('STX index',s.pc));assert ix<k.Q and start+ix<k.Q
                target=start+ix;task=k.descriptor(1,value,dest=dest)
            elif name=='READ5':
                index,side,centre=args;target=number(r[index],('READ5',s.pc));assert 5<=centre<=11
                task=k.descriptor(2,lane=centre,side=side)
            else:
                dst,index=args;target=number(r[index],(name,s.pc));task=k.descriptor(3,dst,side=int(name=='FULLCOL'))
            assert P<=target<P+k.FRAME_WORDS,('unsafe symbolic target',g,s.pc,target)
            s.pc=nextpc;s.mode=k.SEEK;s.target=target;s.args=task
            s.move=1 if s.address<target else 2 if s.address>target else 0
            return [s],None
        s.pc=nextpc;s.move=0;s.regs=tuple(r);return [s],None
    assert s.mode==k.SEEK
    if s.address!=s.target:
        s.move=1 if s.address<s.target else 2;return [s],None
    r=list(s.regs);kind=s.args&3;dst=(s.args>>2)&15;lane=(s.args>>6)&31
    source=(s.args>>11)&3;dest=(s.args>>13)&1;side=(s.args>>14)&1;write=None
    if kind==0:
        if source==0:
            r[dst]=input_word(g,s.address,lane);counts['input_reads']+=1
            if r[dst].u:counts['unprojected_unknown100_input_reads']+=1
        else:r[dst]=s.out.get(s.address,C(0)) if source==1 else s.scratch.get(s.address,C(0)) if source==2 else C(k.beta_bit(own.ROM,s.address))
    elif kind==1:
        if dest:s.scratch[s.address]=r[dst]
        else:s.out[s.address]=r[dst];counts['Out_writes']+=1
        write=(s.address,dest,r[dst].v,r[dst].u)
    elif kind==2:
        result=C(0)
        for i in range(5):
            q=cut(input_word(g,s.address,lane+(i+1)*(1 if side else -1)),0,20)
            result=bor(result,shift(q,20*i))
        r[0]=result
    else:
        result=C(0)
        for j in range(17 if side else 11):result=bor(result,shift(cut(input_word(g,s.address,j+(0 if side else 3)),0,1),j))
        r[dst]=result
    s.regs=tuple(r);s.mode=k.RUN;s.move=0;return [s],write

def execute(g,early=False):
    states=[Machine(pc=own.ROM.early_pc if early else 0)];counts=Counter();digest=hashlib.sha256();lo=hi=P;maxstates=1;unknownpcs=set()
    limit=75*k.Q-1-k.EARLY_BIRTH if early else 120*k.Q-(102*k.Q+1)
    for tick in range(1,limit+1):
        new=[];summary=[]
        for state in states:
            beforepc=state.pc;branched,write=step(state,g,counts)
            if len(branched)>1:unknownpcs.add(beforepc)
            for s in branched:
                if not any(s.same(v) for v in new):new.append(s)
                lo=min(lo,s.address);hi=max(hi,s.address)
                summary.append([s.pc,s.mode,s.address,s.move,None if write is None else [write[0],write[1],hex(write[2]),hex(write[3])]])
        states=new;maxstates=max(maxstates,len(states));assert len(states)<=8,('symbolic branch explosion',g,tick)
        digest.update(json.dumps(summary,separators=(',',':')).encode()+b'\n')
        if all(s.mode in (k.HALT,k.ERROR) for s in states):break
    assert all(s.mode==k.HALT for s in states),(g,early,'symbolic deadline/ERROR',tick)
    output=[[s.out.get(P+i,C(0)) for i in range(k.FRAME_WORDS)] for s in states]
    assert all(v.constant for ws in output for v in ws),(g,early,'unresolved symbolic output')
    assert all(ws==output[0] for ws in output)
    expected=k.cell_words(base.next2H(g))
    if early:assert [v.v for v in output[0][:6]]==expected[:6]
    else:assert [v.v for v in output[0]]==expected,(g,'universal output differs')
    return dict(receiver=g,early=early,updates=tick,available_updates=limit,
        universal_HALT=True,maximum_symbolic_states=maxstates,final_symbolic_states=len(states),
        unresolved_branch_pcs=sorted(unknownpcs),min_head_address=lo,max_head_address=hi,
        all496_output_words_known=True,output_words=[hex(v.v) for v in output[0]],
        primitive_counts=dict(sorted(counts.items())),symbolic_trace_sha256=digest.hexdigest(),
        full_Word100_input_not_projected=True)

def main():
    started=time.monotonic();cases=[]
    for g in range(-8,9):
        e=execute(g,True);l=execute(g);cases.append(dict(receiver=g,early=e,late=l))
        print(json.dumps(dict(receiver=g,early=e['updates'],late=l['updates'],branches=l['unresolved_branch_pcs'],states=l['maximum_symbolic_states'],universal_shadow=True)),flush=True)
    r=dict(Q=k.Q,U=k.U,error_lambda=24,error_separation=104,
        quantified_single_record_words=496,quantified_bits=49600,background='exact intact first-U shadow R(H)',
        arbitrary_native_GF_Age_flag_padding_and_allSF_Word100=True,
        actual_input_projection_or_legal_malformed_theorem_assumed=False,cases=cases,
        universal_single_prepared_record_emitted_outputs_and_deadline=True,
        later_phase_or_reachability_Gray_iid_or_shorter_U_claim=False)
    path=D/'GAW19_symbolic_execution_certificate.json'
    if '--issue' in sys.argv:assert not path.exists();path.write_text(json.dumps(r,indent=2)+'\n')
    else:assert r==json.loads(path.read_text())
    print(json.dumps(dict(passed=True,elapsed_seconds=time.monotonic()-started,stage='universal_symbolic_prepared_execution_only')),flush=True)
    return r

if __name__=='__main__':main()
