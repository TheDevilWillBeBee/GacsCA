import numpy as np, pytest
from gacsca.params import Params, Variant
from gacsca import level0_spec as spec, level0_np as npimpl


def to_cfg(S, b):
    return spec.Cfg(list(S["addr"][b]), list(S["age"][b]), list(S["f1"][b]), list(S["f2"][b]),
                    list(S["wf1"][b]), list(S["wf2"][b]))


@pytest.mark.parametrize("variant", [Variant.gray(), Variant.masumori(), Variant(majority="plurality")])
def test_np_matches_spec_random(variant):
    rng = np.random.default_rng(0)
    p = Params(Q=16, ncol=3)
    S = npimpl.random_state(p, 4, rng)
    S["wf1"] = rng.integers(0, 2, S["f1"].shape).astype(np.int8)
    S["wf2"] = rng.integers(0, 2, S["f1"].shape).astype(np.int8)
    T = npimpl.step(S, p, variant)
    for b in range(4):
        c = spec.step(to_cfg(S, b), p.Q, p.U, variant)
        assert list(T["addr"][b]) == c.addr
        assert list(T["age"][b]) == c.age
        assert list(T["f1"][b]) == c.f1
        assert list(T["f2"][b]) == c.f2


def test_np_matches_spec_near_ground_state():
    """Ground state with sparse damage: exercises the colony-boundary logic."""
    rng = np.random.default_rng(1)
    p = Params(Q=32, ncol=3)
    S = npimpl.initial(p, 6)
    S["age"] += rng.integers(0, p.U)
    for b in range(6):
        for _ in range(4):
            x = rng.integers(0, p.L)
            S["addr"][b, x] = rng.integers(0, p.Q)
            S["age"][b, x] = rng.integers(0, p.U)
            S["f1"][b, x] = rng.integers(0, 2)
            S["f2"][b, x] = rng.integers(0, 2)
    for t in range(3):
        T = npimpl.step(S, p)
        for b in range(6):
            c = spec.step(to_cfg(S, b), p.Q, p.U)
            assert list(T["addr"][b]) == c.addr and list(T["age"][b]) == c.age
            assert list(T["f1"][b]) == c.f1 and list(T["f2"][b]) == c.f2
        S = T


def test_ground_state_fixed():
    p = Params(Q=16, ncol=4)
    S = npimpl.initial(p, 1)
    for t in range(5):
        S = npimpl.step(S, p)
    assert (S["addr"] == np.arange(p.L) % p.Q).all()
    assert (S["age"] == 5).all() and S["f1"].sum() == 0 and S["f2"].sum() == 0


def test_single_error_repaired_in_one_step():
    p = Params(Q=16, ncol=4)
    S = npimpl.initial(p, 1)
    S["addr"][0, 20] = 3; S["age"][0, 20] = 77; S["f1"][0, 20] = 1
    S = npimpl.step(S, p)
    assert (S["addr"] == np.arange(p.L) % p.Q).all() and (S["age"] == 1).all()
    S = npimpl.step(S, p)
    assert S["f1"].sum() == 0
