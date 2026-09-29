"""A protected local temporal-vote primitive, not a new self-simulating rule.

It uses the holder's existing radius-seven raw neighborhood and state fields.
Clock gating, maintenance priorities, full self-description and ROM integration
remain obligations for any replacement rule. No holder dependency is modified.
"""
from functools import lru_cache
from . import holder_rule as f
from .wordcode import Builder
from .word_prune import prune

HISTORY = (-1, 1, 2)
SUPPORT = tuple(sorted({d+h+e for d in f.OFFSETS for h in HISTORY for e in f.OFFSETS}))


def local_votes(cells):
    """Return the five proposed backup Data values using only old local data."""
    if len(cells) != 15:
        raise ValueError('exact radius-seven neighborhood required')
    def corrected(target):
        return f.majority5(tuple(getattr(cells[7+target+e], f's{2-e}_data') for e in f.OFFSETS))
    result=[]
    for d in f.OFFSETS:
        a,b,c=(corrected(d+h) for h in HISTORY)
        result.append((a&b)|(a&c)|(b&c))
    return tuple(result)


@lru_cache(maxsize=1)
def description():
    """Complete expression for this primitive only, with all raw input slots."""
    b=Builder(15*f.FIELDS)
    def majority5(v):
        a,c,d,e,g=v
        pairs=b.bor(b.bor(b.band(a,c),b.band(a,d)),b.band(c,d))
        return b.bor(b.bor(b.band(b.band(a,c),d), b.band(pairs,b.bor(e,g))),
                     b.band(b.bor(b.bor(a,c),d),b.band(e,g)))
    corrected={t: majority5([(7+t+e)*f.FIELDS+f.COL[f's{2-e}_data'] for e in f.OFFSETS])
               for t in sorted({d+h for d in f.OFFSETS for h in HISTORY})}
    out=[]
    for d in f.OFFSETS:
        a,c,e=(corrected[d+h] for h in HISTORY)
        out.append(b.bor(b.bor(b.band(a,c),b.band(a,e)),b.band(c,e)))
    return prune(b.finish(tuple(out)))
