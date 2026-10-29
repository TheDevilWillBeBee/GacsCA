"""EXPLICIT standalone framed service-wave proposal; no CA/ROM changed.

Replace the timed packet's arbitrary winner with the minimum-counter
qualified cohort, and add a 21-bit flag carrier (valid, position9,
count11). Each physical word contributes at most one combined vote.
The computed flag carrier forces RF through a separately changed
maintenance equation. Birth, the own-ROM program and the upper error map
are not supplied here. See ROBUSTNESS J87 for the exact conditional proof.
"""
from functools import lru_cache
from gacsca import maintenance
from gacsca.netlist import (at_least, const_word, w_add_const, w_eq, w_eq_const,
                            w_mux, w_ult_const)
from check_right_barrier import dominant_majority
import proposed_modal_clock

Q = 448
RADIUS = 5
POSITION_BITS = 9
POSITION_MODULUS = 1 << POSITION_BITS
COUNTER_BITS = 11
LIFETIME = 1792
TAG_BITS = 4
PACKET_SIZE = 5
ADDED_FLAG_BITS = 1 + POSITION_BITS + COUNTER_BITS


def word_less(n, a, b):
    """Unsigned, equal-width comparison, with a direct MSB induction."""
    assert len(a) == len(b)
    less, equal = 0, 1
    for ai, bi in zip(reversed(a), reversed(b)):
        less = n.OR(less, n.all([equal, n.NOT(ai), bi]))
        equal = n.AND(equal, n.NOT(n.XOR(ai, bi)))
    return less


def select(n, carriers, position_bits, position_limit):
    """Minimum counter among qualified three-word cohorts.

    Input carriers have alive/position/count. All positions are adjusted
    to the center, modulo 2**position_bits; the output range check has a
    gap of at least 2*RADIUS, preventing wrap in the ancestry proof.
    """
    assert (1 << position_bits) - position_limit > 2 * RADIUS
    adjusted = {j: w_add_const(n, carriers[j]['position'], (-j) % (1 << position_bits))
                for j in range(-RADIUS, RADIUS + 1)}
    position, count = const_word(0, position_bits), const_word(0, COUNTER_BITS)
    exists, any_cohort = 0, 0
    for j in range(-RADIUS, RADIUS + 1):
        votes = [n.all([carriers[k]['alive'], w_eq(n, adjusted[j], adjusted[k]),
                        w_eq(n, carriers[j]['count'], carriers[k]['count'])])
                 for k in adjusted]
        found = n.AND(carriers[j]['alive'], at_least(n, votes, 3))
        any_cohort = n.OR(any_cohort, found)
        qualified = n.all([found, w_ult_const(n, adjusted[j], position_limit),
                           w_ult_const(n, carriers[j]['count'], LIFETIME - 1)])
        choose = n.AND(qualified, n.OR(n.NOT(exists), word_less(n, carriers[j]['count'], count)))
        position = w_mux(n, choose, adjusted[j], position)
        count = w_mux(n, choose, carriers[j]['count'], count)
        exists = n.OR(exists, qualified)
    return dict(valid=exists,
                position=w_mux(n, exists, position, const_word(0, position_bits)),
                count=w_mux(n, exists, w_add_const(n, count, 1), const_word(0, COUNTER_BITS)),
                any_cohort=any_cohort)


def build(n, cells):
    """Return separate packet/flag components from eleven raw cell words."""
    packet_alive = {j: n.all([cells[j]['packet_valid'], cells[j]['wf2'],
                             w_ult_const(n, cells[j]['packet_tag'], PACKET_SIZE)])
                    for j in range(-RADIUS, RADIUS + 1)}
    packet_carriers = {j: dict(alive=packet_alive[j], position=cells[j]['packet_tag'],
                              count=cells[j]['packet_count']) for j in packet_alive}
    packet = select(n, packet_carriers, TAG_BITS, PACKET_SIZE)
    combined = {}
    for j in packet_alive:
        usable_packet = n.AND(packet_alive[j], w_ult_const(n, cells[j]['packet_count'], LIFETIME - 1))
        usable_flag = n.all([cells[j]['flag_valid'],
                             w_ult_const(n, cells[j]['flag_position'], Q),
                             w_ult_const(n, cells[j]['flag_count'], LIFETIME - 1)])
        packet_position = w_add_const(n, [*cells[j]['packet_tag'], *([0] * (POSITION_BITS - TAG_BITS))], 1)
        use_packet = n.AND(usable_packet, n.OR(n.NOT(usable_flag),
            n.NOT(word_less(n, cells[j]['flag_count'], cells[j]['packet_count']))))
        combined[j] = dict(alive=n.OR(usable_packet, usable_flag),
                           position=w_mux(n, use_packet, packet_position, cells[j]['flag_position']),
                           count=w_mux(n, use_packet, cells[j]['packet_count'], cells[j]['flag_count']))
    flag = select(n, combined, POSITION_BITS, Q)
    return dict(packet_valid=packet['valid'], wf2=packet['valid'],
                packet_tag=packet['position'], packet_count=packet['count'],
                packet_any_cohort=packet['any_cohort'],
                flag_valid=flag['valid'], flag_position=flag['position'],
                flag_count=flag['count'], service_force=flag['valid'])


@lru_cache(None)
def maintenance_build(symbolic=False):
    """The old diagnostics remain; computed coded pressure also forces RF."""
    _, source = proposed_modal_clock.proposed_build()
    signature = 'def build(n, cells, k, m, Q=None, nb=None, radix=None, pos_bits=None):'
    assert source.count(signature) == 1
    source = source.replace(signature, signature[:-2] + ', service_force=0):')
    old = "    vote_right = n.AND(exists, n.OR(n.NOT(f1), f2))"
    new = "    f2 = n.OR(f2, service_force)\n" + old
    assert source.count(old) == 1
    source = source.replace(old, new)
    namespace = dict(maintenance.__dict__, w_eq_const=w_eq_const)
    if symbolic:
        namespace['majority_word'] = dominant_majority
    exec(compile(source, '<EXPLICIT framed service force; not an existing candidate>', 'exec'), namespace)
    return namespace['build'], source
