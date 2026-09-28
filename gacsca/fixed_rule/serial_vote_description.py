"""Complete candidate F, including evaluator, signal votes/capture and Wf.

This is a finite expression description, not evidence that a local colony ROM
executes the enlarged description within the current work period.
"""
from . import serial_vote_rule as r,serial_vote_clock_description
from .wordcode import Builder,LIT


def build(*,optimize=True):
    b=Builder(11*r.FIELDS)
    rows={j:{name:(j+5)*r.FIELDS+i for i,(name,_) in enumerate(r.SCHEMA)} for j in range(-5,6)}
    c=rows[0];zero,one=b.const(0),b.const(1)
    core=serial_vote_clock_description.build()
    mapping=[rows[j][name] for j in range(-5,6) for name,_ in r.SCHEMA]
    for op,a,d in core.operations:mapping.append(b.const(a) if op==LIT else b.op(op,mapping[a],mapping[d]))
    out={name:mapping[index] for (name,_),index in zip(r.SCHEMA,core.outputs)}
    votes={target:b.count([b.band(b.shr(rows[target+e]['signal'],b.const(2-e)),one) for e in range(-2,3)],3) for target in range(-3,4)}
    capture=b.eq(out['age'],b.const(r.CAPTURE_AGE));data=b.band(c['data'],one)
    signal=zero
    for d in range(-2,3):
        at=b.any(*(b.eq(out['address'],b.const(target-d)) for target in (3,r.Q-3)))
        bit=b.select(b.all(capture,at),data,votes[d])
        for _ in range(d+2):bit=b.add(bit,bit)
        signal=b.bor(signal,bit)
    clear=b.all(out['f1'],b.not_(b.eq(out['address'],c['address'])))
    out['signal']=b.select(clear,zero,signal)
    window=b.all(b.not_(b.lt(out['age'],b.const(96*r.Q))),b.lt(out['age'],b.const(98*r.Q)),b.not_(clear))
    out['wf1']=b.all(window,b.any(*(b.all(b.eq(out['address'],b.const(address)),votes[r.Q-3-address]) for address in range(r.Q-5,r.Q))))
    out['wf2']=b.all(window,b.not_(out['f1']),b.any(*(b.all(b.eq(out['address'],b.const(address)),votes[3-address]) for address in range(5))))
    full=b.finish(tuple(out[name] for name,_ in r.SCHEMA))
    if not optimize:return full
    from .word_prune import prune
    return prune(full)
