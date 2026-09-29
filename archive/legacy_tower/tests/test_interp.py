"""The interpretation phase: the colony's Hold track bits after the I-phase must equal the new
primaries that the level-1 rule (prog_up) produces on a level-1 ring, for the simulated cell and
its two neighbours (copies), at level-1 ages exercising every op kind."""
import numpy as np, pytest, collections
from gacsca.build import make_tower
from gacsca.engine_np import repair, redistribute, apply_ops
from gacsca.microcode import Program

sys0, sys1 = make_tower(ncol0=3)
p0, T, L0 = sys0.p, sys0.T, sys0.L
eng = sys0.np_engine()
sched = sys0.sched
R, h, NT = T.R, (T.R - 1) // 2, T.NT
prog1 = sys1.prog


def ages_by_kind():
    d = collections.defaultdict(list)
    for op in prog1.ops:
        d[op.kind].append(op)
    return d


def pick_ages():
    d = ages_by_kind()
    picks = {}
    for kind in ("MOV", "BITOP", "SHIFT", "RSHIFT", "SWEEP_INIT", "SWEEP", "BCAST_INIT", "BCAST", "CONST", "BUSLATCH_INT"):
        ops = d.get(kind, [])
        if not ops: continue
        # prefer ops in the middle of their interval and, for sweeps, later steps (multi-cell chains)
        op = ops[len(ops) // 2]
        a = op.t0 + (op.t1 - op.t0) // 2
        picks[kind] = a
    # receive ages of the gathers: 4 concurrent ops (2 RSHIFT + 2 MOV / BITOP)
    for a in range(prog1.U):
        if len(prog1.ops_at(a)) >= 4:
            picks[f"RECV{a}"] = a
            if len([k for k in picks if k.startswith("RECV")]) >= 3: break
    # a few extra sweep ages (chain hypotheses k = 1..3)
    sw = d.get("SWEEP", [])
    for kk, op in enumerate(sw[:6]):
        picks[f"SWEEP{kk}"] = op.t0 + min(kk, op.t1 - op.t0 - 1)
    return picks


def level1_ring(rng, g1, a1_center, ncell=13):
    """13 level-1 cells (positions 0..12; centre 6 has address a1_center), age g1, random consistent tracks."""
    prim = rng.integers(0, 2, (ncell, NT), dtype=np.uint8)
    prim[:, T["SIG"]] = (rng.random(ncell) < 0.3)          # some tokens around
    st = []
    for j in range(ncell):
        tr = np.zeros((NT, R), np.uint8)
        for r in range(R):
            tr[:, r] = prim[(j + (r - h)) % ncell]
        st.append(dict(addr=(a1_center + j - 6) % sys1.p.Q, age=g1, f1=0, f2=0, tracks=tr,
                       simage=int(rng.integers(0, 4)), simaddr=int(rng.integers(0, 4))))
    return st, prim


def expected_new_primaries(st, prim, g1):
    """apply prog1 ops directly on the level-1 ring (positions 0..12) -> new primaries (13, NT)."""
    V1 = prim[None].copy()
    addr1 = np.array([[s["addr"] for s in st]]); age1 = np.full((1, len(st)), g1)
    P1 = apply_ops(V1, addr1, age1, prog1, T)
    return P1[0]


@pytest.mark.parametrize("a1_center", [7, 0, 63])
def test_iphase_matches_direct(a1_center):
    rng = np.random.default_rng(3)
    picks = pick_ages()
    for name, g1 in picks.items():
        st, prim = level1_ring(rng, g1, a1_center)
        S = eng.initial(1)
        S["age"][:] = sched.iphase[0]
        S["simage"][:] = g1; S["simaddr"][:] = a1_center
        V = repair(S["trk"])
        for j in range(-6, 7):
            s = st[6 + j]
            bits = L0.encode(s["addr"], s["age"], s["f1"], s["f2"], s["tracks"], simage=s["simage"], simaddr=s["simaddr"])
            V[0, L0.b0:L0.b0 + L0.K, T.arg(j)] = bits
        # Hold's local fields as Tr_local would have left them (age+1, same address)
        own = st[6]
        hb = L0.encode(own["addr"], (g1 + 1) % sys1.p.U, 0, 0, None)
        V[0, L0.b0:L0.b0 + L0.track_base, T["HOLD"]] = hb[:L0.track_base]
        S["trk"] = redistribute(V, R)
        for _ in range(sched.iphase[1] - sched.iphase[0]):
            S = eng.step(S)
        H = repair(S["trk"])[0, :, T["HOLD"]]
        exp = expected_new_primaries(st, prim, g1)
        base = L0.b0 + L0.track_base
        for c in (-1, 0, 1):
            r = c + h
            got = np.array([H[base + t * R + r] for t in range(NT)])
            bad = np.where(got != exp[6 + c])[0]
            assert len(bad) == 0, (name, g1, c, [(T.names[t], int(got[t]), int(exp[6 + c][t])) for t in bad[:8]])
        # register load: simage/simaddr must now hold the Hold AGE/ADDR fields (= the encoded own state here)
        Q0 = p0.Q
        assert (S["simage"][0, :Q0] == (g1 + 1) % sys1.p.U).all() and (S["simaddr"][0, :Q0] == a1_center).all(), (name, np.unique(S["simage"][0, :Q0]), np.unique(S["simaddr"][0, :Q0]))
