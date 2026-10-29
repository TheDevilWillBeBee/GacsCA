"""GBD1: actual five independent raw Mem340 slots at every physical site.

Corrects GBD0's one-payload source model, preserving all GBD0 assets.
No full rule, bank preparation, Head decoder or own software is supplied.
"""
from itertools import combinations

Q=8192
U=128*Q
WORD=20
LANES=17
MASK=(1<<WORD)-1
SLOTS=(0,-2,-1,1,2)
INVERSE=tuple(SLOTS.index(-s) for s in SLOTS)
assert INVERSE==(0,4,3,2,1)


def valid(q,centre,lane,phase,stride,count):
    return (0<=q<5 and centre in (-1,0,1) and 0<=lane<17 and
            0<=phase<20 and stride in (1,5) and 0<=count<=20)


def targets(q,centre,phase,stride,count):
    """(physical offset, actual raw backup slot, payload-bit index)."""
    if not valid(q,centre,0,phase,stride,count):return ()
    result=[]
    for i in range(count):
        chunk,bit=divmod(phase+stride*i,20)
        u=SLOTS[q]+centre-2+chunk
        result.append(tuple((u+s,INVERSE[h],bit)
                            for h,s in enumerate(SLOTS)))
    return tuple(result)


def read_window(raw_cells,q,centre,lane,phase,stride,count):
    """Total controls; raw_cells[d][slot] is one independent Word340.

    Every cell has exactly five slots. No coherence/matching-slot values
    are assumed. Logical state y is stored in slot h at physical x=y-S[h].
    Thus holder u+S[h] must access slot INVERSE[h] to represent u.
    """
    if not valid(q,centre,lane,phase,stride,count):return 0
    z=0
    for i,cells in enumerate(targets(q,centre,phase,stride,count)):
        bits=[(raw_cells[d][slot]>>(20*lane+bit))&1 for d,slot,bit in cells]
        z|=int(sum(bits)>=3)<<i
    return z&MASK


def majority_word(values):
    z=0
    for a,b,c in combinations(values,3):z|=a&b&c
    return z&MASK


def composed_window(raw_cells,q,centre,lane,phase,stride,count):
    if not valid(q,centre,lane,phase,stride,count):return 0
    words=[]
    for chunk in range(6):
        u=SLOTS[q]+centre-2+chunk
        values=[(raw_cells[u+s][INVERSE[h]]>>(20*lane))&MASK
                for h,s in enumerate(SLOTS)]
        words.append(majority_word(values))
    z=0
    for i in range(count):
        chunk,bit=divmod(phase+stride*i,20)
        z|=((words[chunk]>>bit)&1)<<i
    return z&MASK


def coherent_raw(logical):
    """Encoding convention: raw cell d/slot q stores logical d+S[q]."""
    return {d:tuple(logical[d+s] for s in SLOTS) for d in range(-8,9)}


def coherent_reference(logical,q,centre,lane,phase,stride,count):
    if not valid(q,centre,lane,phase,stride,count):return 0
    z=0
    for i in range(count):
        chunk,bit=divmod(phase+stride*i,20)
        u=SLOTS[q]+centre-2+chunk
        z|=((logical[u]>>(20*lane+bit))&1)<<i
    return z&MASK
