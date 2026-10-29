"""EXPLICIT unincorporated timed packet proposal; no existing rule changed.

Four tag bits, valid and an eleven-bit counter reuse WF2. Birth initializes
the five holders with tags0..4 and common counter0. Subsequent outputs
need three matching alive (adjusted-tag,counter) words. The counter only
increases; it cannot be refreshed by at most two packet faults per window.
Birth is an external premise and no own-ROM candidate is built here.
"""
from gacsca.netlist import at_least,const_word,w_add_const,w_eq,w_mux,w_ult_const


TAG_BITS = 4
COUNTER_BITS = 11
LIFETIME = 1792
PACKET_SIZE = 5
RADIUS = 5


def build(n,cells,lifetime=LIFETIME,counter_bits=COUNTER_BITS):
    assert 2<=lifetime<=(1<<counter_bits)
    adjusted = {j:w_add_const(n,cells[j]['tag'],(-j)%16)
                for j in range(-RADIUS,RADIUS+1)}
    alive = {j:n.AND(cells[j]['valid'],cells[j]['wf2']) for j in adjusted}
    selected_tag = const_word(0,TAG_BITS)
    selected_count = const_word(0,counter_bits)
    exists = 0
    for j in range(-RADIUS,RADIUS+1):
        votes = [n.all([alive[k],w_eq(n,adjusted[j],adjusted[k]),
                        w_eq(n,cells[j]['count'],cells[k]['count'])]) for k in adjusted]
        found = n.AND(alive[j],at_least(n,votes,3))
        selected_tag = w_mux(n,found,adjusted[j],selected_tag)
        selected_count = w_mux(n,found,cells[j]['count'],selected_count)
        exists = n.OR(exists,found)
    valid = n.all([exists,w_ult_const(n,selected_tag,PACKET_SIZE),
                   w_ult_const(n,selected_count,lifetime-1)])
    return dict(valid=valid,wf2=valid,
        tag=w_mux(n,valid,selected_tag,const_word(0,TAG_BITS)),
        count=w_mux(n,valid,w_add_const(n,selected_count,1),const_word(0,counter_bits)))
