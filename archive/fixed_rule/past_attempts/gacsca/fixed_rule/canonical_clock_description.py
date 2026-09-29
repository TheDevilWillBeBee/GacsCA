"""Exact clock-rule specialization with canonical geometry and arbitrary flags.

The self-simulator still describes complete F. This conditional-domain kernel is
for future physical flag-wave execution, not a new hierarchy-level transition.
"""
from . import clock_rule as f,clock_description
from .wordcode import Builder,LIT


def build():
    b=Builder(11*f.FIELDS);rows={j:{n:(j+5)*f.FIELDS+i for i,(n,_) in enumerate(f.SCHEMA)} for j in range(-5,6)}
    c=rows[0];zero,one=b.const(0),b.const(1)
    core=clock_description.build(healthy_domain=True)
    mapping=[rows[j][n] for j in range(-2,3) for n,_ in f.SCHEMA]
    for op,a,d in core.operations:mapping.append(b.const(a) if op==LIT else b.op(op,mapping[a],mapping[d]))
    out={n:mapping[index] for (n,_),index in zip(f.SCHEMA,core.outputs)}
    inside={0:one}
    for j in range(1,6):inside[j]=b.lt(c['address'],b.const(f.Q-j))
    for j in range(-5,0):inside[j]=b.not_(b.lt(c['address'],b.const(-j)))
    wf1=b.count([b.band(inside[j],rows[j]['wf1']) for j in range(-5,6)],3)
    right=[b.band(inside[j],rows[j]['f1']) for j in range(1,6)]
    flag1=b.any(wf1,b.count(right,3),b.band(c['f1'],b.count(right,2)))
    d4=b.count([b.band(inside[j],rows[j]['wf2']) for j in range(-5,6)],3)
    left=[rows[j]['f2'] for j in range(-1,-6,-1)]
    on=b.any(b.count([b.band(inside[j],rows[j]['f2']) for j in range(-1,-6,-1)],4),b.band(flag1,b.count(left,4)),d4)
    erase=b.any(b.all(b.not_(flag1),b.all(*(b.any(b.not_(inside[j]),rows[j]['f2']) for j in range(-1,-6,-1)))),b.all(flag1,b.not_(b.any(*left))))
    flag2=b.select(c['f2'],b.any(d4,b.not_(erase)),on)
    out['f1'],out['f2']=flag1,flag2
    reset=b.any(*(b.eq(c['age'],b.const(age)) for age in f.RESET_AGES))
    window=b.all(b.not_(reset),b.not_(b.lt(out['age'],b.const(96*f.Q))),b.lt(out['age'],b.const(98*f.Q)))
    for name in ('wf1','wf2'):out[name]=b.select(window,c[name],zero)
    for name,_ in f.SCHEMA:
        if name.startswith(('lp_','rp_')):out[name]=b.select(flag1,zero,out[name])
    return b.finish(tuple(out[n] for n,_ in f.SCHEMA))
