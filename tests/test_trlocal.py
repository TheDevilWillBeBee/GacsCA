import numpy as np, pytest
from gacsca.params import Params, Variant
from gacsca.microcode import Tracks, Layout, Compiler
from gacsca.engine_np import Engine, repair, redistribute
from gacsca.trlocal import TrLocal
from gacsca import level0_spec as spec

Q, U = 256, 16384


def random_neigh(rng, Q, U, n=13):
    """13 simulated states: half the time a consistent colony neighbourhood with a few corruptions."""
    if rng.random() < 0.5:
        base = int(rng.integers(0, Q)); age = int(rng.integers(0, U))
        st = [dict(addr=(base + k) % Q, age=age, f1=0, f2=0) for k in range(n)]
        for _ in range(int(rng.integers(0, 4))):
            k = int(rng.integers(0, n))
            st[k] = dict(addr=int(rng.integers(0, Q)), age=int(rng.integers(0, U)), f1=int(rng.integers(0, 2)), f2=int(rng.integers(0, 2)))
        if rng.random() < 0.5:
            for k in range(n):
                if rng.random() < 0.4: st[k]["f1"] = 1
                if rng.random() < 0.3: st[k]["f2"] = 1
        if rng.random() < 0.3:     # ages near a multiple of 16 to exercise Flag2 (iii)
            for k in range(n): st[k]["age"] = (st[k]["age"] // 16) * 16 - (k % 3)
        return st
    return [dict(addr=int(rng.integers(0, Q)), age=int(rng.integers(0, U)), f1=int(rng.integers(0, 2)), f2=int(rng.integers(0, 2))) for _ in range(n)]


@pytest.mark.parametrize("variant,D", [(Variant.gray(), 3), (Variant.masumori(), 1)])
def test_trlocal_matches_spec(variant, D):
    p = Params(Q=Q, U=U, ncol=2)
    T = Tracks(JMAX=6, wq=8, wu=14, R=3)
    L = Layout(Q, U, T)
    C = Compiler(T, L, D=D, t=100)
    tl = TrLocal(C, c=0, variant=variant)
    n = tl.build()
    print("trlocal ops:", len(C.prog.ops), "steps:", n - 100, "peak temps:", tl.al.peak)
    eng = Engine(p, T, L, C.prog, wipe_rules=False)
    rng = np.random.default_rng(5)
    B = 24
    S = eng.initial(B)
    S["age"][:] = 100
    neighs = []
    prim = repair(S["trk"])
    for b in range(B):
        st = random_neigh(rng, Q, U)
        neighs.append(st)
        for j in range(-6, 7):
            s = st[6 + j]
            bits = L.encode(s["addr"], s["age"], s["f1"], s["f2"], None)
            prim[b, L.b0:L.b0 + L.K, T.arg(j)] = bits
    S["trk"] = redistribute(prim, T.R)
    for _ in range(n - 100):
        S = eng.step(S)
    H = repair(S["trk"])[:, L.b0:L.b0 + L.K, T["HOLD"]]
    for b in range(B):
        got = L.decode(H[b])
        st = neighs[b]
        cfg = spec.Cfg([s["addr"] for s in st], [s["age"] for s in st], [s["f1"] for s in st], [s["f2"] for s in st])
        ADDR, AGE, F1, F2, info = spec.step_cell(cfg, 6, Q, U, variant)
        assert (got["ADDR"], got["AGE"], got["F1"], got["F2"]) == (ADDR, AGE % (1 << L.wu), F1, F2), (b, got, (ADDR, AGE, F1, F2), info, st)
