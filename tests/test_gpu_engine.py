import numpy as np, torch, pytest
from gacsca.params import Params, Variant
from gacsca.microcode import Tracks, Layout
from gacsca.engine_np import Engine, redistribute, repair
from gacsca.workperiod import build_workperiod
from gacsca.gpu_engine import EngineGPU


def setup(R, D, Q=None, U=None, ncol=3):
    Q = Q or (256 if R == 3 else 512)
    U = U or (16384 if R == 3 else 32768)
    p = Params(Q=Q, U=U, ncol=ncol)
    T = Tracks(JMAX=6, wq=(Q - 1).bit_length(), wu=(U - 1).bit_length(), R=R)
    L = Layout(Q, U, T)
    prog, sched = build_workperiod(p, T, L, D=D)
    eng = Engine(p, T, L, prog); eng.trickle = sched.trickle
    g = EngineGPU(p, T, L, prog, sched.trickle)
    return p, T, L, prog, sched, eng, g


def random_state(eng, rng, B, age):
    p, T = eng.p, eng.T
    S = eng.initial(B)
    S["age"][:] = age
    S["simage"][:] = rng.integers(0, p.U); S["simaddr"][:] = rng.integers(0, p.Q)
    trk = rng.integers(0, 2, (B, p.L, T.NT), dtype=np.uint8)
    trk[:, :, T["SIG"]] = 0
    S["trk"] = redistribute(trk, T.R)
    # sparse damage of the local structure
    for b in range(B):
        for _ in range(6):
            x = rng.integers(0, p.L)
            S["addr"][b, x] = rng.integers(0, p.Q); S["age"][b, x] = rng.integers(0, p.U)
            S["f1"][b, x] = rng.integers(0, 2); S["f2"][b, x] = rng.integers(0, 2)
    return S


def same(A, Bn, keys=("addr", "age", "f1", "f2", "wf1", "wf2", "simage", "simaddr")):
    for k in keys:
        if not (A[k] == Bn[k]).all():
            return k
    if not (A["trk"] == Bn["trk"]).all():
        return "trk"
    return None


@pytest.mark.parametrize("R,D", [(3, 3), (5, 1)])
def test_gpu_engine_matches_numpy(R, D):
    p, T, L, prog, sched, eng, g = setup(R, D)
    rng = np.random.default_rng(11)
    for start, nsteps in [(sched.gather_starts[0], 300), (sched.compute_start + 5, 400), (sched.trickle[0] - 3, 40),
                          (sched.update_age - 2, 6)]:
        S = random_state(eng, rng, 3, start)
        st = g.to_gpu(S); out = torch.empty_like(st)
        assert same(g.to_np(st), S) is None
        for t in range(nsteps):
            S = eng.step(S)
            g.step(st, out, t=1); st, out = out, st
        bad = same(g.to_np(st), S)
        assert bad is None, (start, nsteps, bad)


def test_gpu_noise_smoke():
    p, T, L, prog, sched, eng, g = setup(3, 3)
    S = eng.initial(4)
    st = g.to_gpu(S); out = torch.empty_like(st)
    g.step(st, out, t=1, eps=0.05)
    N = g.to_np(out)
    frac = (N["addr"] != np.arange(p.L) % p.Q).mean()
    assert 0.02 < frac < 0.08


def test_gpu_tower_matches_numpy():
    """Stage 2: the CUDA interpretation phase equals the NumPy one on random states."""
    from gacsca.build import make_tower
    sys0, sys1 = make_tower(ncol0=3)
    p, T = sys0.p, sys0.T
    eng = sys0.np_engine(); g = sys0.gpu_engine()
    sched = sys0.sched
    rng = np.random.default_rng(21)
    for start, nsteps in [(sched.iphase[0] - 3, sched.iphase[1] - sched.iphase[0] + 6), (sched.compute_start + 200, 300)]:
        S = random_state(eng, rng, 2, start)
        S["simage"][:] = rng.integers(0, sys1.p.U); S["simaddr"][:] = rng.integers(0, sys1.p.Q)
        st = g.to_gpu(S); out = torch.empty_like(st)
        for t in range(nsteps):
            S = eng.step(S)
            g.step(st, out, t=1); st, out = out, st
        bad = same(g.to_np(st), S)
        assert bad is None, (start, nsteps, bad)
