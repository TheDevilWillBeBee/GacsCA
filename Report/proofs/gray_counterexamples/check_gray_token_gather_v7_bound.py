#!/usr/bin/env python3
"""Sound interval over-approximation of emitted GMW7 execution, not samples.

One copy block starts with arbitrary legal simulated words and an arbitrary
physical cursor in the frame.  Exact lower loop counters and CODE table
values are retained.  Both data-dependent branches are considered.  Opcode
fetch, IO initiation and all real one-site operand travel are charged.
This certifies a PRELOADED noiseless execution budget, not a Gray period.
"""
from dataclasses import dataclass
from pathlib import Path
import json,time,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
import gray_token_gather_v7 as k
import build_gray_token_gather_v7 as builder


@dataclass(frozen=True)
class D:
    lo:int
    hi:int
    values:tuple=()
    def __post_init__(self):
        assert 0<=self.lo<=self.hi<=k.MASK
        if self.lo==self.hi and not self.values:object.__setattr__(self,'values',(self.lo,))


def exact(n):return D(n,n,(n,))
UNKNOWN=D(0,k.MASK)


def domain(values):
    values=tuple(sorted(set(values)));assert values
    return D(values[0],values[-1],values if len(values)<=32 else ())


def join(values):
    values=list(values);assert values
    if all(v.values for v in values):return domain(n for v in values for n in v.values)
    return D(min(v.lo for v in values),max(v.hi for v in values))


def restrict(v,lo=0,hi=k.MASK):
    lo=max(lo,v.lo);hi=min(hi,v.hi)
    if lo>hi:return None
    if v.values:
        values=[n for n in v.values if lo<=n<=hi]
        return domain(values) if values else None
    return D(lo,hi)


def alu(fn,a,b,c):
    if a.values and b.values and c.values and len(a.values)*len(b.values)*len(c.values)<=64:
        return domain(k.generic_alu(fn,x,y,z) for x in a.values for y in b.values for z in c.values)
    if fn==0:return a
    if fn in (1,2):
        lo,hi=(a.lo+b.lo,a.hi+b.hi) if fn==1 else (a.lo-b.hi,a.hi-b.lo)
        if hi<0:lo+=k.MASK+1;hi+=k.MASK+1
        elif lo>k.MASK:lo-=k.MASK+1;hi-=k.MASK+1
        return D(lo,hi) if 0<=lo<=hi<=k.MASK else UNKNOWN
    if fn==22:
        lo=5*a.lo+b.lo;hi=5*a.hi+b.hi
        return D(lo,hi) if hi<=k.MASK else UNKNOWN
    if fn==3:return D(0,min(a.hi,b.hi))
    if fn in (4,5):return D(0,(1<<max(a.hi.bit_length(),b.hi.bit_length()))-1)
    if fn in (6,7):
        if a.hi<b.lo or b.hi<a.lo:return exact(fn==7)
        return domain((0,1))
    if fn==8:
        if a.hi<b.lo:return exact(1)
        if a.lo>=b.hi:return exact(0)
        return domain((0,1))
    if fn==9:return exact(0) if a.lo else exact(1) if not a.hi else domain((0,1))
    if fn==10:return domain((0,1))
    if fn in (11,21) and b.lo==b.hi:
        n=b.lo
        if fn==11:
            n=(n if n<(1<<19) else n-(1<<20)) if n<(1<<20) else n if n<(1<<99) else n-(1<<100)
            if abs(n)>=100:return exact(0)
            if n<0:return D(a.lo>>-n,a.hi>>-n)
            return D(a.lo<<n,a.hi<<n) if a.hi<<n<=k.MASK else UNKNOWN
        return D(a.lo>>n,a.hi>>n) if n<100 else exact(0)
    if fn==13:return D(0,100)
    if fn in (15,):return domain((0,1))
    if fn in (17,18):return D(0,31)
    if fn==19:return D(k.MASK-a.hi,k.MASK-a.lo)
    return UNKNOWN


def rom_word(rom,a):
    if a.values:return domain(k.beta_word(rom,n) for n in a.values)
    lo=max(a.lo,0);hi=min(a.hi,k.CODE_CAPACITY-1)
    values=[k.beta_word(rom,n) for n in range(lo,hi+1)]
    if a.hi>=k.CODE_CAPACITY:values.append(0)
    return domain(values or (0,))


def memory_read(memory,target,source):
    if source==0:return UNKNOWN
    if source==3:return domain((0,1))
    locations=target.values or range(target.lo,target.hi+1)
    return join(memory.get((source,n),UNKNOWN) for n in locations)


def memory_write(memory,target,source,value):
    locations=target.values or range(target.lo,target.hi+1)
    memory=dict(memory)
    if target.lo==target.hi:memory[source,target.lo]=value
    else:
        for n in locations:memory.pop((source,n),None)
    return memory


def refine(regs,preds,index,positive):
    regs=list(regs);p=preds[index]
    r=restrict(regs[index],lo=1) if positive else restrict(regs[index],hi=0)
    if r is None:return None
    regs[index]=r
    if p:
        src,before,fn,value=p
        if regs[src]==before:
            if fn==8:r=restrict(before,hi=value-1) if positive else restrict(before,lo=value)
            elif fn==6:r=restrict(before,lo=value,hi=value) if positive else before
            elif fn==7:r=before if positive else restrict(before,lo=value,hi=value)
            else:raise AssertionError(fn)
            if r is None:return None
            regs[src]=r
    return tuple(regs)


def copy_bound(rom,listing,labels,copy):
    rows={r['address']:r for r in listing};stop=labels['copy_done']
    regs=[UNKNOWN]*16;regs[14]=exact(copy)
    memory={(1,k.PRIMARY_START):D(0,k.Q-1),(1,k.PRIMARY_START+1):D(0,k.U-1),
        (1,k.PRIMARY_START+2):domain((0,1)),(1,k.PRIMARY_START+3):domain((0,1)),
        (1,k.PRIMARY_START+4):exact(0),(1,k.PRIMARY_START+5):exact(0)}
    # State: pc, register domains, comparison predicates, position domain,
    # known mutable memory, elapsed upper bound, executed instruction count.
    pending=[(labels['copy_loop'],tuple(regs),(None,)*16,D(k.PRIMARY_START,k.PRIMARY_START+190),memory,0,0)]
    seen={};maximum=0;terminals=0;max_steps=0;states=0
    while pending:
        pc,regs,preds,position,memory,cost,steps=pending.pop()
        if pc==stop:
            maximum=max(maximum,cost);max_steps=max(max_steps,steps);terminals+=1;continue
        assert steps<50000,('unbounded abstract control',pc)
        key=(pc,regs,preds,position,tuple(sorted(memory.items())))
        if seen.get(key,-1)>=cost:continue
        seen[key]=cost;states+=1
        assert pc in rows,('instruction fetch outside emitted instruction rows',pc)
        row=rows[pc];name=row['opcode'];args=tuple(v&((1<<w)-1) for v,w in zip(row['operands'],k.ARGS[name]))
        r=list(regs);pr=list(preds);nextpc=pc+1;cost+=1;steps+=1
        def write(d,value,predicate=None):
            # A same-domain write can still change the concrete value.  Old
            # comparisons mentioning this register cease to constrain it.
            for i,old in enumerate(pr):
                if old and old[0]==d:pr[i]=None
            r[d]=value;pr[d]=predicate
        if name=='MOVI':write(args[0],exact(args[1]))
        elif name in ('ALU','ALUI','ALUX'):
            if name=='ALUI':d,fn,ai,value=args;b=exact(value);c=exact(0)
            else:
                d,fn,ai,bi,ci=args;b=r[bi];c=r[ci]
                if name=='ALUX':fn=None
            a=r[ai];predicate=None
            if fn in (6,7,8) and b.lo==b.hi and ai!=d:predicate=(ai,a,fn,b.lo)
            write(d,UNKNOWN if fn is None else alu(fn,a,b,c),predicate)
        elif name in ('CODE','BITCODE'):
            d,index=args
            write(d,rom_word(rom,r[index]) if name=='CODE' else exact(k.beta_bit(rom,r[index].lo)) if r[index].lo==r[index].hi else domain((0,1)))
        elif name in ('LDX','STX'):
            if name=='LDX':
                d,base,index,lane,source=args
                assert r[lane].hi<=10,(pc,name,lane,r[lane],r[8],r[12])
            else:d,base,index,dest=args;source=2 if dest else 1
            assert r[index].hi<k.Q and base+r[index].hi<k.Q,(pc,name,index,r[index])
            target=alu(1,r[index],exact(base),exact(0))
            assert k.PRIMARY_START<=target.lo<=target.hi<=k.PRIMARY_START+190,(pc,target)
            cost+=max(1,abs(position.lo-target.hi),abs(position.hi-target.lo));position=target
            if name=='LDX':write(d,memory_read(memory,target,source))
            else:memory=memory_write(memory,target,source,r[d])
        elif name=='JMP':nextpc=args[0]
        elif name=='JMPR':
            targets=r[args[0]].values;assert targets,('non-finite indirect branch',pc,r[args[0]])
            for target in targets:pending.append((target,tuple(r),tuple(pr),position,memory,cost,steps))
            continue
        elif name=='BNZ':
            index,target=args
            for positive,destination in ((False,nextpc),(True,target)):
                refined=refine(tuple(r),tuple(pr),index,positive)
                if refined is not None:pending.append((destination,refined,tuple(pr),position,memory,cost,steps))
            continue
        else:raise AssertionError(('unexpected opcode inside copy block',pc,name))
        pending.append((nextpc,tuple(r),tuple(pr),position,memory,cost,steps))
    return dict(copy=copy,maximum_ticks=maximum,maximum_instructions=max_steps,
        abstract_states=states,terminal_states=terminals)


def validate():
    start=time.monotonic();rom,listing,labels,errors=builder.programme().assemble()
    assert not errors and len(rom)==8192
    bounds=[copy_bound(rom,listing,labels,copy) for copy in range(5)]
    # Native prefix133 instructions +16 IO excursions of distance at most5;
    # main gate<=40; five copy-loop tails3 each; final HLT1.
    overhead=133+16*5+40+5*3+1
    total=overhead+sum(row['maximum_ticks'] for row in bounds)
    assert total<65535,(total,bounds)
    # The separate wipe branch has185 consecutive writes and four control
    # instructions per row;213+40+185*6+1 is a deliberately loose bound.
    wipe=213+40+185*6+1;assert wipe<65535
    return dict(name='GMW7 universal preloaded execution deadline bound',copies=bounds,
        fixed_overhead_bound=overhead,total_active_execution_bound=total,wipe_execution_bound=wipe,
        available_active_updates=65535,elapsed_seconds=time.monotonic()-start,
        arbitrary_legal_upper_raw_words=True,all_mutable_input_bits_overapproximated=True,
        no_error_preloaded_execution_only=True,full_Gray_period_or_iid_theorem=False)


if __name__=='__main__':print(json.dumps(validate(),indent=2))
