"""EXPLICIT unincorporated repair-packet state and local rule proposal.

Adds four tag bits and one valid bit to the existing WF2 bit. A nonzero
packet consists of five physical holders with consecutive tags 0..4.
The clock gate and packet birth are external premises. No existing CA or
own program is changed; no complete self-simulation/reliability claim.
"""
from gacsca.netlist import at_least,const_word,w_add_const,w_eq,w_mux,w_ult_const


TAG_BITS = 4
PACKET_SIZE = 5
RADIUS = 5


def build(n,cells,gate):
    adjusted = {j:w_add_const(n,cells[j]['tag'],(-j)%16)
                for j in range(-RADIUS,RADIUS+1)}
    alive = {j:n.AND(cells[j]['valid'],cells[j]['wf2']) for j in adjusted}
    selected = const_word(0,TAG_BITS)
    exists = 0
    # Priority is part of the definition. Under the certified invariant,
    # two arbitrary fault words cannot create a second three-word cohort.
    for j in range(-RADIUS,RADIUS+1):
        votes = [n.AND(alive[k],w_eq(n,adjusted[j],adjusted[k])) for k in adjusted]
        found = n.AND(alive[j],at_least(n,votes,3))
        selected = w_mux(n,found,adjusted[j],selected)
        exists = n.OR(exists,found)
    valid = n.all([gate,exists,w_ult_const(n,selected,PACKET_SIZE)])
    return dict(valid=valid,wf2=valid,
                tag=w_mux(n,valid,selected,const_word(0,TAG_BITS)))
