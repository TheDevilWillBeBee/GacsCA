"""Full WordCode description of the fixed 8Q in-place-vote rule."""
from functools import lru_cache

from . import stream28_holder_core as core
from . import stream28_holder_rule as holder
from . import stream28_compact_vote8 as physical
from . import stream28_spatial_description8 as previous
from .wordcode_and import Builder,Program,LIT
from .word_prune import prune


@lru_cache(maxsize=1)
def build():
    old=previous.build()
    b=Builder(old.inputs)
    values=list(range(old.inputs))
    for opcode,a,d in old.operations:
        values.append(b.const(a) if opcode==LIT else
                      b.op(opcode,values[a],values[d]))
    outputs=[values[wire] for wire in old.outputs]
    span=physical.FIELDS
    rows={j:{name:(j+7)*span+i for i,(name,_) in enumerate(holder.SCHEMA)}
          for j in holder.NEIGHBORHOOD}
    center=rows[0]
    def eq(x,value):return b.eq(x,b.const(value))
    vote_age=b.any(*(eq(center['age'],age) for age in holder.VOTE_AGES))
    out={name:outputs[i] for i,(name,_) in enumerate(holder.SCHEMA)}
    clear=b.all(out['f1'],b.not_(b.eq(out['address'],center['address'])))
    for offset in holder.OFFSETS:
        static=offset+3
        marked=b.nonzero(b.band(center[f'p{static}_a'],
                           b.const(physical.VOTE_SELF)))
        enabled=b.all(vote_age,b.not_(clear),
                      eq(center[f'p{static}_kind'],core.MEM),marked)
        a,c,d=(previous.corrected_data(b,rows,offset+j)
               for j in (-1,0,1))
        majority=b.bor(b.bor(b.band(a,c),b.band(a,d)),b.band(c,d))
        key=f's{offset+2}_data'
        outputs[holder.COL[key]]=b.select(enabled,majority,out[key])
    compact=prune(b.finish(tuple(outputs)))
    return Program(compact.inputs,compact.operations,compact.outputs)
