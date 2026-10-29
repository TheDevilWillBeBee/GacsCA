"""Structural bounded-loop cost certificate; no sampled execution bound.

The only backward edges are CELL (11 iterations), Q5_TEST (5 per
candidate), and Q5_CANDIDATE (5 candidates). Both sides of every other
conditional branch are admitted. Native/raw/RAM MOVE targets all lie in
[P+2,RAM_BASE+11], span195. Each first Q5 RAW can travel195; all later
Q5 RAWs target P+2 and cost one stationary restoration tick.
"""
from functools import lru_cache
import native_emitter as n
import controller as c
import layout as l

METRICS=('instruction_updates','travel_updates','RAW_calls','RAM_calls','Q5_calls')

def add(a,b):return tuple(x+y for x,y in zip(a,b))
def maxima(values):return tuple(max(v[i] for v in values) for i in range(len(METRICS)))
ZERO=(0,)*len(METRICS)

def bound(program):
    rows=program['rows'];positions=program['positions'];labels=program['labels']
    bypc={positions[i]:row for i,row in enumerate(rows)}
    nextpc={positions[i]:positions[i+1] for i in range(len(rows))}
    span=(n.RAM_BASE+max(n.RAM.values())+2)-(l.P+2)
    assert span==195
    calls=set(row[1] for row in rows if row[0]=='CALL')
    assert calls=={labels[z] for z in ('RAW','RAMLOAD','RAMLOAD5','RAMSTORE','Q5')}
    backward=[(positions[i],row[-1]) for i,row in enumerate(rows)
              if row[0]=='BR' and row[-1]<=positions[i]]
    assert set(target for _,target in backward)=={
        labels['CELL'],labels['Q5_CANDIDATE'],labels['Q5_TEST']}

    @lru_cache(None)
    def helper(pc,travel):
        name,*args=bypc[pc]
        assert name!='CALL','non-Q5 helper must not nest a call'
        weight=(1,travel if name=='MOVE' else 0,0,0,0)
        if name=='RET':return weight
        if name=='BR':
            cond=args[0];choices=[]
            if cond!=7:choices.append(helper(args[-1],travel))
            if cond!=0:choices.append(helper(nextpc[pc],travel))
            return add(weight,maxima(choices))
        return add(weight,helper(nextpc[pc],travel))

    @lru_cache(None)
    def q5(pc,candidate=1,test=1,seen_raw=False):
        name,*args=bypc[pc];weight=(1,0,0,0,0)
        if name=='RET':return weight
        if name=='CALL':
            assert args[0]==labels['RAW']
            raw=helper(labels['RAW'],1 if seen_raw else span)
            weight=add(weight,add(raw,(0,0,1,0,0)))
            return add(weight,q5(nextpc[pc],candidate,test,True))
        if name=='BR':
            cond=args[0];to=args[-1];choices=[]
            if cond!=7:
                if to==labels['Q5_TEST']:
                    if test<5:choices.append(q5(to,candidate,test+1,seen_raw))
                elif to==labels['Q5_CANDIDATE']:
                    if candidate<5:choices.append(q5(to,candidate+1,1,seen_raw))
                else:choices.append(q5(to,candidate,test,seen_raw))
            # Fallthrough at loop bound is permitted; earlier fallthrough
            # is an overapproximation. The algebra proof establishes the
            # actual five tests/at-most-five candidates.
            if cond!=0:choices.append(q5(nextpc[pc],candidate,test,seen_raw))
            assert choices,(pc,candidate,test)
            return add(weight,maxima(choices))
        return add(weight,q5(nextpc[pc],candidate,test,seen_raw))

    @lru_cache(None)
    def main(pc,cell=1):
        name,*args=bypc[pc];weight=(1,span if name=='MOVE' else 0,0,0,0)
        if name=='HALT':return weight
        assert name!='RET','main may not enter helper bodies directly'
        if name=='CALL':
            target=args[0]
            if target==labels['Q5']:
                cost=add(q5(target),(0,0,0,0,1))
            elif target==labels['RAW']:
                cost=add(helper(target,span),(0,0,1,0,0))
            else:
                assert target in {labels[z] for z in ('RAMLOAD','RAMLOAD5','RAMSTORE')}
                cost=add(helper(target,span),(0,0,0,1,0))
            return add(add(weight,cost),main(nextpc[pc],cell))
        if name=='BR':
            cond=args[0];to=args[-1];choices=[]
            if cond!=7:
                if to==labels['CELL']:
                    if cell<11:choices.append(main(to,cell+1))
                else:choices.append(main(to,cell))
            if cond!=0:choices.append(main(nextpc[pc],cell))
            assert choices,(pc,cell)
            return add(weight,maxima(choices))
        return add(weight,main(nextpc[pc],cell))

    values=main(0)
    result=dict(zip(METRICS,values))
    result['total_updates']=sum(values[:2])
    result['Head_span']=span
    result['Q5_max']=dict(zip(METRICS,q5(labels['Q5'])))
    result['RAW_max195']=dict(zip(METRICS,helper(labels['RAW'],span)))
    result['bounded_backedges']=[dict(pc=pc,target=target) for pc,target in backward]
    result['branch_overapproximation']=True
    # CELL left/right branches are overapproximated independently on every
    # iteration: the bound allows BOTH left and right clauses on all11 rows.
    return result
