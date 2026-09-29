"""Unit tests of the microprogram primitives on a single colony (noiseless)."""
import numpy as np, pytest
from gacsca.params import Params
from gacsca.microcode import Tracks, Layout, Compiler
from gacsca.engine_np import Engine, repair

Q, U = 256, 16384


def make(D=1, R=3):
    p = Params(Q=Q, U=U, ncol=2)
    T = Tracks(JMAX=6, wq=8, wu=14, R=R)
    L = Layout(Q, U, T)
    return p, T, L


def run(engine, S, n):
    for _ in range(n):
        S = engine.step(S)
    return S


def set_track(S, T, name, bits, b0):
    """set primary bits of track `name` at addresses b0.. in colony 0 (and copies consistently)"""
    from gacsca.engine_np import redistribute
    B, L_ = S["addr"].shape
    prim = repair(S["trk"])
    prim[0, b0:b0 + len(bits), T[name]] = bits
    S["trk"] = redistribute(prim, T.R)


def get_track(S, T, name, b0, n):
    return repair(S["trk"])[0, b0:b0 + n, T[name]].copy()


@pytest.mark.parametrize("D", [1, 2, 3])
def test_shift_and_sweeps(D):
    p, T, L = make(D)
    C = Compiler(T, L, D=D)
    rng = (20, 36)
    C.shift("T1", "T0", 5, rng)                   # T1[x] = T0[x-5]
    C.add_const("T2", "T0", rng, 1)               # T2 = T0 + 1 mod 2^16
    C.eq_const("T0", rng, 0xBEEF, "BC")           # BC = [T0 == 0xBEEF] broadcast over rng
    C.add_const("T3", "T0", rng, 0x1234)
    C.eq_field("T0", "T3", rng, "T4")
    n = C.t
    eng = Engine(p, T, L, C.prog, wipe_rules=False)
    S = eng.initial(1)
    val = 0xBEEF
    bits = [(val >> i) & 1 for i in range(16)]
    set_track(S, T, "T0", bits, 20)
    S = run(eng, S, n)
    t1 = get_track(S, T, "T1", 20, 16)
    assert list(t1[:5]) == [0] * 5 and list(t1[5:]) == bits[:11]
    t2 = get_track(S, T, "T2", 20, 16)
    assert sum(int(b) << i for i, b in enumerate(t2)) == (val + 1) & 0xFFFF
    assert get_track(S, T, "BC", 20, 16).tolist() == [1] * 16
    t3 = get_track(S, T, "T3", 20, 16)
    assert sum(int(b) << i for i, b in enumerate(t3)) == (val + 0x1234) & 0xFFFF
    assert get_track(S, T, "T4", 20, 16).tolist() == [0] * 16
    assert get_track(S, T, "SIG", 18, 20).sum() == 0
    # the local structure must be untouched
    assert (S["addr"] == np.arange(p.L) % Q).all() and (S["age"] == n).all()


def test_eq_const_false_and_or_reduce():
    p, T, L = make(3)
    C = Compiler(T, L, D=3)
    rng = (40, 49)
    C.eq_const("T0", rng, 5, "BC")
    C.or_reduce("T0", rng, "T1")
    n = C.t
    eng = Engine(p, T, L, C.prog, wipe_rules=False)
    S = eng.initial(1)
    set_track(S, T, "T0", [1, 0, 1, 0, 0, 0, 0, 0, 0], 40)
    S = run(eng, S, n)
    assert get_track(S, T, "BC", 40, 9).tolist() == [1] * 9
    assert get_track(S, T, "T1", 40, 9).tolist() == [1] * 9
    S = eng.initial(1)
    set_track(S, T, "T0", [0] * 9, 40)
    S = run(eng, S, n)
    assert get_track(S, T, "BC", 40, 9).tolist() == [0] * 9
    assert get_track(S, T, "T1", 40, 9).tolist() == [0] * 9


def test_redundancy_single_hit_repaired():
    """A single-cell hit on the track copies is invisible to the repaired values."""
    p, T, L = make(1)
    C = Compiler(T, L, D=1)
    eng = Engine(p, T, L, C.prog, wipe_rules=False)
    S = eng.initial(1)
    bits = np.random.default_rng(0).integers(0, 2, 30)
    set_track(S, T, "T0", bits, 10)
    S["trk"][0, 17] = 1 - S["trk"][0, 17]          # flip every copy held by cell 17
    S = run(eng, S, 2)
    assert get_track(S, T, "T0", 10, 30).tolist() == bits.tolist()


@pytest.mark.parametrize("D", [1, 3])
def test_ltc_and_spread(D):
    p, T, L = make(D)
    C = Compiler(T, L, D=D)
    rng = (40, 48)
    C.lt_const("T0", rng, 100, "T1")
    C.lt_const("T0", rng, 99, "T2")
    C.lt_const("T0", rng, 3, "T3")
    C.eq_const("T0", rng, 99, "BC", bc_rng=(47, 48))     # store only at address 47
    C.spread(47, "T4", (10, 60), "BC")                    # spread it over [10, 60)
    n = C.t
    eng = Engine(p, T, L, C.prog, wipe_rules=False)
    S = eng.initial(1)
    set_track(S, T, "T0", [(99 >> i) & 1 for i in range(8)], 40)
    S = run(eng, S, n)
    assert get_track(S, T, "T1", 40, 8).tolist() == [1] * 8
    assert get_track(S, T, "T2", 40, 8).tolist() == [0] * 8
    assert get_track(S, T, "T3", 40, 8).tolist() == [0] * 8
    assert get_track(S, T, "T4", 10, 50).tolist() == [1] * 50
    assert get_track(S, T, "T4", 60, 5).tolist() == [0] * 5
    assert get_track(S, T, "SIG", 0, 100).sum() == 0
