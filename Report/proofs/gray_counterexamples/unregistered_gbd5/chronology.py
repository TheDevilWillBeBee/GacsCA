"""Derived clean trajectory formulas; not an initialization of future tapes.

The written proof inducts these formulas through prefix_rule.local from
the single actual encoded row0. The checker replays reset/load/capture,
all19 merge rows/all3217 transport rows, actual birth and selected CPU
histories. No History/port value is an independently selected input.
"""
import prefix_rule as r
from functools import lru_cache

@lru_cache(None)
def payload(g,h,records):
    data=0
    for lane,d in enumerate(r.LANES):
        for bit in range(20):
            b=20*h+bit
            if b<r.K:data|=((records(g+d)>>b)&1)<<(20*lane+bit)
    return data

def info(y,records,unused):
    g,a=divmod(y,r.Q)
    return ((records(g)>>(a-r.P))&1) if r.P<=a<r.P+r.K else (unused(y)&1)

def mailbox(t,y,records,unused):
    starts=[start for start in r.STARTS if start<t]
    if not starts:return 0
    start=max(starts)
    if t==start+1:return 0
    distance=min(t,start+r.ACTIVE)-start-2
    return info(y-distance,records,unused)|(info(y+distance,records,unused)<<1)

def history(t,y,records,unused):
    word=0
    for g in range(3):
        for lane,d in enumerate(r.LANES):
            if t>r.capture(g,d):word|=info(y+d*r.Q,records,unused)<<(17*g+lane)
    return word

def packet(t,y,records):
    g,a=divmod(y,r.Q);i=a-r.P;p=r.p
    if not 0<=i<r.K or t<=p.SEED:return p.ZERO
    # At/after the proven final transport output row every route is at
    # its destination. This is the exact min/max formula below simplified;
    # it adds no new rule and no independently prepared packet data.
    if t>=p.DONE+1:
        return p.Packet(payload(g,i,records),i,1) if i<p.CHUNKS else p.ZERO
    if t<=p.LOAD:
        elapsed=t-p.SEED-1;first=max(20*(i//20),i-elapsed)
        data=0
        for b in range(first,i+1):
            lanes=sum(((records(g+d)>>b)&1)<<lane for lane,d in enumerate(r.LANES))
            data|=p.seed_data(lanes,b%20)
        return p.Packet(data,i//20,1)
    elapsed=min(t-p.LOAD-1,p.MAX_TRAVEL)
    for h in range(p.CHUNKS):
        if a==max(p.destination(h),p.source(h)-elapsed):
            return p.Packet(payload(g,h,records),h,1)
    return p.ZERO

def row(t,x,records,unused,heads=None,outputs=None):
    """Actual derived row through the pre-pulse prefix; optional current
    Head/Out functions are previous results of actual CPU updates only.
    """
    assert 0<=t<96*r.Q
    hs=[];outs=[];mem=[];tags=[]
    for s in r.S:
        y=x+s;v=packet(t,y,records)
        mem.append(v.data);tags.append(v.tag|(v.valid<<13))
        hs.append(r.c.pack_head(heads(y)) if heads else 0)
        outs.append(outputs(y)&r.c.MASK if outputs else 0)
    return r.Cell(addr=x%r.Q,age=t,
        Info=tuple(info(x+s,records,unused) for s in r.S),
        Mailbox=tuple(mailbox(t,x+s,records,unused) for s in r.S),
        History=tuple(history(t,x+s,records,unused) for s in r.S),
        Mem=tuple(mem),InputTag=tuple(tags),Head=tuple(hs),Out=tuple(outs))

class Frame(dict):
    def __init__(self,t,records,unused,heads=None,outputs=None):
        super().__init__();self.t=t;self.records=records;self.unused=unused
        self.heads=heads;self.outputs=outputs
    def __missing__(self,x):
        value=row(self.t,x,self.records,self.unused,self.heads,self.outputs)
        self[x]=value;return value
