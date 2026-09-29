"""Exact GPU noise vectors, long counters, historical replay and chunking."""
import numpy as np
import pytest
import torch

from gacsca import gpu
from gacsca.build import make_system
from gacsca.noise import cell_noise_word, splitmix64
from gacsca.params import Params


def setup_engine(full, version, seed=920, batch=2):
    if full:
        system = make_system(ncol=1)
        engine = system.gpu_engine(seed=seed, noise_version=version)
        state = engine.to_gpu(system.np_engine().initial(batch))
    else:
        engine = gpu.Level0GPU(Params(Q=32, ncol=1), seed=seed, noise_version=version)
        state = gpu.initial(engine.p, batch)
    return engine, state


@pytest.mark.parametrize("full", [False, True])
@pytest.mark.parametrize("version", [1, 2])
def test_gpu_noise_matches_scalar_counter_oracle(full, version):
    engine, state = setup_engine(full, version)
    for t in (1, 1 + (1 << 24), (1 << 32) + 123, (1 << 63) + 9, (1 << 64) - 1):
        result = engine.step(state, torch.empty_like(state), t=t, eps=1).cpu().numpy()
        for b, x in ((0, 0), (1, 0), (1, 17)):
            h = cell_noise_word(engine.seed, t, b, x, version)
            h2 = splitmix64(h); h3 = splitmix64(h2); h4 = splitmix64(h3); h5 = splitmix64(h4)
            words = [h2 % engine.p.Q, h3 % engine.p.U, h4 & 15, h5 & 0xFFFFFFFF]
            g = h5
            for _ in range(state.shape[-1] - 4):
                g = splitmix64(g); words.append(g & 0xFFFFFFFF)
            np.testing.assert_array_equal(result[b, x], words)


@pytest.mark.parametrize("full", [False, True])
def test_time_wrap_and_batch_overlap_are_removed(full):
    engine, state = setup_engine(full, 2, batch=4097)
    at_zero = engine.step(state, torch.empty_like(state), t=0, eps=1)
    at_one = engine.step(state, torch.empty_like(state), t=1, eps=1)
    wrapped = engine.step(state, torch.empty_like(state), t=1 + (1 << 24), eps=1)
    assert not torch.equal(at_one, wrapped)
    # Old (t << 40) ^ (b << 28) equated (0,4096) with (1,0).
    assert not torch.equal(at_zero[4096], at_one[0])
    engine.noise_version = 1
    legacy_zero = engine.step(state, torch.empty_like(state), t=0, eps=1)
    legacy_one = engine.step(state, torch.empty_like(state), t=1, eps=1)
    legacy_wrapped = engine.step(state, torch.empty_like(state), t=1 + (1 << 24), eps=1)
    assert torch.equal(legacy_one, legacy_wrapped)
    assert torch.equal(legacy_zero[4096], legacy_one[0])


@pytest.mark.parametrize("full", [False, True])
def test_noise_restarts_and_chunking_at_large_times(full):
    engine, state = setup_engine(full, 2)
    t0 = (1 << 40) + 3
    whole = engine.run(state.clone(), 8, 0.13, t0=t0)
    partial = engine.run(state.clone(), 3, 0.13, t0=t0)
    partial = engine.run(partial, 5, 0.13, t0=t0 + 3)
    replay = engine.run(state.clone(), 8, 0.13, t0=t0)
    assert torch.equal(whole, partial) and torch.equal(whole, replay)


def unmix64(value):
    """Invert the bijection to force a rare draw, avoiding a flaky huge sample."""
    mask = (1 << 64) - 1
    def undo_xor(y, shift):
        x = y
        for _ in range(64 // shift):
            x = y ^ (x >> shift)
        return x
    value = undo_xor(value, 31)
    value = value * pow(0x94D049BB133111EB, -1, 1 << 64) & mask
    value = undo_xor(value, 27)
    value = value * pow(0xBF58476D1CE4E5B9, -1, 1 << 64) & mask
    return (undo_xor(value, 30) - 0x9E3779B97F4A7C15) & mask


@pytest.mark.parametrize("full", [False, True])
def test_fault_probability_is_not_quantized_to_24_bits(full):
    word, t = 1 << 35, 17
    # This draw has 53-bit u=2^-29, but the old 24-bit u rounded down to zero.
    seed2 = unmix64(unmix64(unmix64(word)) ^ t) ^ 0xD2B74407B1CE6E93
    seed1 = unmix64(word) ^ splitmix64(t << 40)
    assert cell_noise_word(seed2, t, 0, 0, 2) == word
    assert cell_noise_word(seed1, t, 0, 0, 1) == word
    for version, seed in ((1, seed1), (2, seed2)):
        engine, state = setup_engine(full, version, seed=seed)
        clean = engine.step(state, torch.empty_like(state), t=t, eps=0)
        noisy = engine.step(state, torch.empty_like(state), t=t, eps=2 ** -30)
        assert torch.equal(clean[0, 0], noisy[0, 0]) == (version == 2)
