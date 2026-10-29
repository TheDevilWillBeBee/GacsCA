"""GBD0 proposed generic word-window component, not a complete automaton.

No host rule/native evaluator is called.  The inputs are actual raw
five-copy Mem340 values at fixed physical coordinates -8..8.  Head
selection, gathering/packing, programme, stores and time are NOT supplied.
This is an explicitly changed word-data primitive, not Gray's binary I/O.
"""
from itertools import combinations

Q = 8192
U = 128 * Q
WORD = 20
MASK = (1 << WORD) - 1
SLOTS = (0, -2, -1, 1, 2)
LANES = 17
RADIUS = 8


def valid(q, centre, lane, phase, stride, count):
    return (0 <= q < 5 and centre in (-1, 0, 1) and
            0 <= lane < LANES and 0 <= phase < WORD and
            stride in (1, 5) and 0 <= count <= WORD)


def targets(q, centre, phase, stride, count):
    """Exact physical five-holder/bit coordinate of every output bit.

    A head acts at the source logical centre x+SLOTS[q]+centre.  Its
    read window consists of six consecutive packed-word containers
    at that centre-2 .. centre+3.  No raw Address substitutes for these
    physical offsets.  The caller must arrange the real container base.
    """
    if not valid(q, centre, 0, phase, stride, count):
        return ()
    out = []
    for i in range(count):
        chunk, bit = divmod(phase + stride * i, WORD)
        logical = SLOTS[q] + centre - 2 + chunk
        out.append(tuple((logical + s, bit) for s in SLOTS))
    return tuple(out)


def read_window(raw_mem, q, centre, lane, phase, stride, count):
    """Total all-raw component: malformed controls produce zero.

    raw_mem[d] contains seventeen concatenated Word20 lane payloads.
    Values are masked locally; missing neighbourhood keys represent
    omitted inputs and are rejected rather than treated as boundary0.
    Five copies are voted BITWISE. This is not whole-word equality quorum.
    """
    if not valid(q, centre, lane, phase, stride, count):
        return 0
    result = 0
    for i, cells in enumerate(targets(q, centre, phase, stride, count)):
        votes = [((raw_mem[d] >> (WORD * lane + bit)) & 1)
                 for d, bit in cells]
        result |= int(sum(votes) >= 3) << i
    return result & MASK


def majority_word(words):
    """Explicit finite generic Boolean implementation, without lookup ROM."""
    z = 0
    for a, b, c in combinations(words, 3):
        z |= a & b & c
    return z & MASK


def composed_window(raw_mem, q, centre, lane, phase, stride, count):
    """Independent word-vote then bit-extraction formulation.

    Exactly six containers may be needed: phase19 + 5*19 = 114.
    Assuming five containers for all phases would miss the sixth one.
    """
    if not valid(q, centre, lane, phase, stride, count):
        return 0
    words = []
    for chunk in range(6):
        logical = SLOTS[q] + centre - 2 + chunk
        copies = [(raw_mem[logical + s] >> (WORD * lane)) & MASK
                  for s in SLOTS]
        words.append(majority_word(copies))
    z = 0
    for i in range(count):
        chunk, bit = divmod(phase + stride * i, WORD)
        z |= ((words[chunk] >> bit) & 1) << i
    return z & MASK


def circuit_upper_bound():
    """An explicit loose AND/OR/NOT fan-in-two hardware upper bound.

    Each control is first decoded by <=40 gates per equality (even if
    supplied as a full Word20). Validation is charged a loose 1000.
    Every table below is fixed CIRCUIT WIRING, counted in the gate bound,
    not an immutable data ROM hidden outside the programme.
    It is for THIS component, not the full transition or own software.
    """
    # Inputs at d=-8..8, seventeen Word20 lanes, five-copy majority at
    # each possible logical container centre u=-5..6: 12*17*20 bit votes.
    majority_gates = 12 * LANES * WORD * (10 * 2 + 9)
    # Decode q, centre, lane, phase, stride, count to one-hot predicates;
    # each equality may use all 20 raw control bits (<=40 gates).
    control_terms = 5 + 3 + LANES + WORD + 2 + (WORD + 1)
    decode_gates = 40 * control_terms + 1000
    # Decode q/c/lane once. For each of six containers and twenty bits,
    # OR 255 (decoded-control AND pre-voted-data) terms. The source port
    # is u=SLOTS[q]+c-2+chunk, an explicit fixed coordinate, never raw GF.
    qcl_terms = 5 * 3 * LANES
    qcl_predicates = 2 * qcl_terms
    container_selectors = 6 * WORD * (qcl_terms + qcl_terms - 1)
    # Forty phase/stride predicates; each output has forty data choices.
    # n>i predicates are ORs of decoded n=i+1..20, sharing per output.
    phase_stride = 20 * 2
    count_predicates = sum(range(20))
    bit_selectors = WORD * (40 + 39 + 1)
    selector_gates = (qcl_predicates + container_selectors + phase_stride +
                      count_predicates + bit_selectors)
    return dict(majority_gates=majority_gates, decode_gates=decode_gates,
                selector_gates=selector_gates,
                total=majority_gates + decode_gates + selector_gates,
                immutable_data_bits=0, new_state_bits=0,
                own_software_emitted=False)
