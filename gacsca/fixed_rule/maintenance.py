"""Explicit NAND description of Gray's printed local-structure component.

Fixed Q=8192, U=128Q. Radius five; strict majority and printed Flag2 erasure.
Workspace flags are inputs carried unchanged, NOT a claim to implement Gray's
simulation structure. Source: Gray pp.20–22; see report for D8/D10 boundaries.
This circuit is a target component fixture; it is not yet part of the tape CA.
"""
from functools import lru_cache
from .circuit import Builder

Q, U = 8192, 1048576
SCHEMA = (('addr', 13), ('age', 20), ('f1', 1), ('f2', 1), ('wf1', 1), ('wf2', 1))
WIDTH = sum(w for _, w in SCHEMA)


def pack(record):
    return tuple((record[name] >> i) & 1 for name, width in SCHEMA for i in range(width))


def unpack(bits):
    if len(bits) != WIDTH:
        raise ValueError('incorrect maintenance word')
    out, offset = {}, 0
    for name, width in SCHEMA:
        out[name] = sum(int(bits[offset + i]) << i for i in range(width))
        offset += width
    return out


@lru_cache(maxsize=1)
def description():
    b = Builder(11 * WIDTH)
    records = {}
    offset = 2
    for j in range(-5, 6):
        records[j] = {}
        for name, width in SCHEMA:
            records[j][name] = tuple(range(offset, offset + width))
            offset += width
    c = records[0]

    def any_(bits):
        out = 0
        for bit in bits:
            out = b.either(out, bit)
        return out

    def all_(bits):
        out = 1
        for bit in bits:
            out = b.both(out, bit)
        return out

    def atleast(bits, k):
        ge = [1] + [0] * k
        for bit in bits:
            ge = [1] + [b.either(ge[i], b.both(bit, ge[i - 1])) for i in range(1, k + 1)]
        return ge[k]

    def add_const(word, number):
        carry, out = 0, []
        for x, y in zip(word, b.const(number % (1 << len(word)), len(word))):
            out.append(b.xor(b.xor(x, y), carry))
            carry = any_((b.both(x, y), b.both(x, carry), b.both(y, carry)))
        return tuple(out)

    def less(word, number):
        lt = 0
        for x, y in zip(word, b.const(number, len(word))):
            lt = b.either(b.both(b.inv(x), y), b.both(b.inv(b.xor(x, y)), lt))
        return lt

    def majority(words, default):
        out, exists = default, 0
        for candidate in words:
            valid = atleast([b.eq(candidate, other) for other in words], 3)
            exists = b.either(exists, valid)
            out = b.select(valid, candidate, out)
        return out, exists

    right, left = list(range(1, 6)), list(range(-1, -6, -1))
    adjusted = {j: add_const(records[j]['addr'], -j) for j in left + right}
    v, exists = majority([adjusted[j] for j in right], c['addr'])
    inside = {0: exists}
    for j in right:
        inside[j] = b.both(exists, less(v, Q - j))
    for j in left:
        inside[j] = b.both(exists, b.inv(less(v, -j)))
    age_r, age_exists = majority([records[j]['age'] for j in right], c['age'])
    age_l, _ = majority([records[j]['age'] for j in left], c['age'])
    incons = any_((b.inv(exists), b.inv(age_exists),
                   atleast([b.both(inside[j], b.inv(b.eq(records[j]['addr'], add_const(v, j))))
                            for j in left], 3),
                   atleast([b.both(inside[j], b.inv(b.eq(records[j]['age'], age_r)))
                            for j in left], 3)))
    wf1 = atleast([b.both(inside[j], records[j]['wf1'][0]) for j in range(-5, 6)], 3)
    right_flags = [b.both(inside[j], records[j]['f1'][0]) for j in right]
    f1 = any_((incons, wf1, atleast(right_flags, 3), b.both(c['f1'][0], atleast(right_flags, 2))))
    age_l_next = b.increment(age_l)
    d3 = b.both(b.inv(exists), b.eq(age_l_next[:4], b.const(0, 4)))
    d4 = atleast([b.both(inside[j], records[j]['wf2'][0]) for j in range(-5, 6)], 3)
    left_f2 = [records[j]['f2'][0] for j in left]
    on = any_((atleast([b.both(inside[j], records[j]['f2'][0]) for j in left], 4),
               b.both(f1, atleast(left_f2, 4)), d3, d4))
    # Literal printed 'no left-colony zero': vacuous all is intentional.
    erase = b.either(b.both(b.inv(f1), all_([b.either(b.inv(inside[j]), records[j]['f2'][0]) for j in left])),
                     b.both(f1, b.inv(any_(left_f2))))
    stay = any_((d3, d4, b.inv(erase)))
    f2 = b.mux(c['f2'][0], stay, on)
    vote_right = b.both(exists, b.either(b.inv(f1), f2))
    addr_l, _ = majority([adjusted[j] for j in left], c['addr'])
    addr = b.select(vote_right, v, addr_l)
    age = b.increment(b.select(vote_right, age_r, age_l))
    return b.finish((*addr, *age, f1, f2, *c['wf1'], *c['wf2']))
