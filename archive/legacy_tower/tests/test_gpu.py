import numpy as np, pytest, torch
from gacsca.params import Params, Variant
from gacsca import level0_np as npimpl
from gacsca import gpu


@pytest.mark.parametrize("variant", [Variant.gray(), Variant.masumori(), Variant(majority="plurality")])
def test_gpu_matches_np_random(variant):
    rng = np.random.default_rng(3)
    p = Params(Q=16, ncol=5)
    S = npimpl.random_state(p, 16, rng)
    S["wf1"] = rng.integers(0, 2, S["f1"].shape).astype(np.int8)
    S["wf2"] = rng.integers(0, 2, S["f1"].shape).astype(np.int8)
    st = gpu.to_gpu(S)
    g = gpu.Level0GPU(p, variant)
    out = torch.empty_like(st)
    g.step(st, out, t=1, eps=0.0)
    T = npimpl.step(S, p, variant)
    G = gpu.to_np(out)
    for k in ("addr", "age", "f1", "f2"):
        assert (G[k] == T[k]).all(), k


def test_gpu_matches_np_trajectory_near_ground():
    rng = np.random.default_rng(4)
    p = Params(Q=64, ncol=4)
    S = npimpl.initial(p, 8)
    for b in range(8):
        for _ in range(30):
            x = rng.integers(0, p.L)
            S["addr"][b, x] = rng.integers(0, p.Q); S["age"][b, x] = rng.integers(0, p.U)
            S["f1"][b, x] = rng.integers(0, 2); S["f2"][b, x] = rng.integers(0, 2)
    st = gpu.to_gpu(S)
    g = gpu.Level0GPU(p)
    out = torch.empty_like(st)
    for t in range(1, 40):
        g.step(st, out, t=t, eps=0.0); st, out = out, st
        S = npimpl.step(S, p); S.pop("_info")
        G = gpu.to_np(st)
        for k in ("addr", "age", "f1", "f2"):
            assert (G[k] == S[k]).all(), (k, t)


def test_noise_rate_and_determinism():
    p = Params(Q=32, ncol=8)
    st = gpu.initial(p, 64)
    g = gpu.Level0GPU(p, seed=7)
    out = torch.empty_like(st); out2 = torch.empty_like(st)
    g.step(st, out, t=1, eps=0.1); g.step(st, out2, t=1, eps=0.1)
    assert torch.equal(out, out2)
    hit = gpu.damage_mask(out, p, t=1) | ((gpu.flags(out) & 3) != 0)
    frac = hit.float().mean().item()
    assert 0.08 < frac < 0.11, frac   # ~ eps (a hit may coincidentally leave addr/age/flags intact)
    g.step(st, out2, t=2, eps=0.1)
    assert not torch.equal(out, out2)
