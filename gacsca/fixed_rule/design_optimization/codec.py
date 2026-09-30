"""Encoding of upper configurations into colonies, and decoding.

A ring state is a boolean (W, N) array in `rule.schema` row order. Upper cell
j is represented by physical colony j: cell a has Address a, the common Age
`age` (0 at a work boundary), all flags zero, and Info[layout[b]] equal to
upper bit b. Every other physical field starts at zero. The same function
encodes any ring, so a two-level configuration is encode(encode(top)).
Decoding reads Info only.
"""
import numpy as np
from . import rule


def encode(cand, upper, age=0):
    p = cand.p
    W, n1 = upper.shape
    assert W == cand.W
    X = np.zeros((W, n1 * p.Q), dtype=bool)
    cand.set_field(X, 'addr', np.tile(np.arange(p.Q), n1))
    code = getattr(p, 'age_code', lambda t: t)
    cand.set_field(X, 'age', np.full(n1 * p.Q, code(age)))
    N = n1 * p.Q
    for bit, off in p.fam().info_copies(p):
        row = cand.row[('info', bit)]
        for b in range(W):
            cells = (np.arange(cand.layout[b], N, p.Q) + off) % N
            X[row, cells] = upper[b]
    return X


def logical_info(cand, X):
    """Logical Info of every physical cell: majority of its stored copies."""
    p = cand.p
    N = X.shape[1]
    copies = []
    for bit, off in p.fam().info_copies(p):
        copies.append(np.roll(X[cand.row[('info', bit)]], -off))
    copies = np.array(copies)
    return copies.sum(axis=0) * 2 > len(copies), bool((copies == copies[0]).all())


def decode(cand, X):
    p = cand.p
    W, N = X.shape
    assert N % p.Q == 0
    info, _ = logical_info(cand, X)
    return np.stack([info[cand.layout[b]::p.Q] for b in range(W)])


def random_upper(cand, n1, rng, age=None):
    """Arbitrary upper states: every field bit uniformly random."""
    X = rng.random((cand.W, n1)) < 0.5
    if age is not None:
        code = np.vectorize(getattr(cand.p, 'age_code', lambda t: t))
        cand.set_field(X, 'age', code(np.full(n1, age) if np.isscalar(age) else np.asarray(age)))
    return X


def colony_health(cand, X):
    """Physical Address/Age/flags consistent with aligned healthy colonies."""
    p = cand.p
    addr = cand.field(X, 'addr')
    age = cand.field(X, 'age')
    ok_addr = np.array_equal(addr, np.tile(np.arange(p.Q), X.shape[1] // p.Q))
    ok_age = bool(np.all(age == age[0]))
    flags = sum(int(X[cand.row[(f, 0)]].sum()) for f in ('f1', 'f2', 'wf1', 'wf2'))
    _, copies_agree = logical_info(cand, X)
    return dict(addr=ok_addr, age=ok_age, age0=int(age[0]), flags=flags,
                info_copies_agree=copies_agree)
