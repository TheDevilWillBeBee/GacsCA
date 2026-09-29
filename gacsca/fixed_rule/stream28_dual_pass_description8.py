"""Complete explicit-input WordCode for the fixed dual-pass compact rule."""
from functools import lru_cache

from . import stream28_dual_overlay_description8 as overlay
from . import stream28_dual_pass8 as physical
from . import stream28_holder_core as core
from . import stream28_holder_rule as holder
from .word_prune import prune
from .wordcode_and import Builder,Program,LIT


@lru_cache(maxsize=1)
def build():
    old=overlay.build()
    b=Builder(old.inputs)
    values=list(range(old.inputs))
    for opcode,a,d in old.operations:
        values.append(b.const(a) if opcode==LIT else
                      b.op(opcode,values[a],values[d]))
    outputs=[values[wire] for wire in old.outputs]
    span=physical.FIELDS
    rows={j:{name:(j+7)*span+i for i,(name,_) in
             enumerate(holder.SCHEMA)}
          for j in holder.NEIGHBORHOOD}
    center=rows[0]
    vote_age=b.any(*(b.eq(center['age'],b.const(age))
                     for age in holder.VOTE_AGES))
    out={name:outputs[i] for i,(name,_) in enumerate(holder.SCHEMA)}
    clear=b.all(out['f1'],b.not_(b.eq(out['address'],center['address'])))
    for offset in holder.OFFSETS:
        static=offset+3
        marked=b.nonzero(b.band(center[f'p{static}_a'],
                           b.const(physical.previous.VOTE_SELF)))
        enabled=b.all(vote_age,b.not_(clear),
                      b.eq(center[f'p{static}_kind'],b.const(core.MEM)),
                      marked)
        a,c,d=(overlay.helpers.corrected_data(b,rows,offset+j)
               for j in (-1,0,1))
        majority=b.bor(b.bor(b.band(a,c),b.band(a,d)),b.band(c,d))
        key=f's{offset+2}_data'
        outputs[holder.COL[key]]=b.select(enabled,majority,out[key])
    compact=prune(b.finish(tuple(outputs)))
    return Program(compact.inputs,compact.operations,compact.outputs)
