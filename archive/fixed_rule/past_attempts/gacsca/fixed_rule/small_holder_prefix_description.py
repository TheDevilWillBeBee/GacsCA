"""Exact canonical, zero-flag specialization before the Wf window.

Valid only for canonical Address, uniform Age, physical flags all zero, and
output Age below WF_START. Signals and all controller/Data words remain arbitrary.
This is a physical execution kernel, never the self-description stored in P.
"""
from . import small_holder_core as r,small_holder_core_clock_description
from .wordcode import Builder,LIT
from .word_prune import prune


def build():
    b=Builder(11*r.FIELDS);rows={j:{name:(j+5)*r.FIELDS+i for i,(name,_) in enumerate(r.SCHEMA)} for j in range(-5,6)}
    core=small_holder_core_clock_description.build(healthy_domain=True)
    mapping=[rows[j][name] for j in range(-2,3) for name,_ in r.SCHEMA]
    for op,a,d in core.operations:mapping.append(b.const(a) if op==LIT else b.op(op,mapping[a],mapping[d]))
    out={name:mapping[index] for (name,_),index in zip(r.SCHEMA,core.outputs)}
    zero,one=b.const(0),b.const(1);c=rows[0]
    capture=b.eq(out['age'],b.const(r.CAPTURE_AGE));signal=zero
    for d in range(-2,3):
        vote=b.count([b.band(b.shr(rows[d+e]['signal'],b.const(2-e)),one) for e in range(-2,3)],3)
        at=b.any(*(b.eq(out['address'],b.const(target-d)) for target in (3,r.Q-3)))
        bit=b.select(b.all(capture,at),b.band(c['data'],one),vote)
        for _ in range(d+2):bit=b.add(bit,bit)
        signal=b.bor(signal,bit)
    out['signal']=signal
    return prune(b.finish(tuple(out[name] for name,_ in r.SCHEMA)))
