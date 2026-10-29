"""Explicit standalone radius-six packet birth-guard proposal, J94.

This is a proposed change to SP14's birth predicate, not an installed
rule, a self-simulating candidate or a complete reliability design.
Packet selection remains J87's radius-five minimum-counter circuit.
Only the any-three-packet-cohort birth exclusion examines13 raw words.
Own-program fitting and protection of the coded flag wave are unproved.
"""
from gacsca.netlist import at_least, w_add_const, w_eq, w_ult_const

RADIUS = 6
TAG_BITS = 4
PACKET_SIZE = 5
COUNTER_BITS = 11


def build(n, cells):
    """True if any three eligible raw packets agree after tag adjustment.

    Eligibility and counter equality are exactly SP14's packet-cohort
    test. There is no output-tag/count range check in the birth guard.
    Extra false positives only suppress a proposed birth.
    """
    offsets = range(-RADIUS, RADIUS + 1)
    alive = {j: n.all([cells[j]['packet_valid'], cells[j]['wf2'],
                      w_ult_const(n, cells[j]['packet_tag'], PACKET_SIZE)]) for j in offsets}
    tags = {j: w_add_const(n, cells[j]['packet_tag'], (-j) % (1 << TAG_BITS)) for j in offsets}
    found = 0
    for j in offsets:
        votes = [n.all([alive[k], w_eq(n, tags[j], tags[k]),
                        w_eq(n, cells[j]['packet_count'], cells[k]['packet_count'])]) for k in offsets]
        found = n.OR(found, n.AND(alive[j], at_least(n, votes, 3)))
    return found
