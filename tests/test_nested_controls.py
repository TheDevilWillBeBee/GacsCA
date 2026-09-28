"""Optional second control-pair storage, repair, noise and actual local loading."""
import numpy as np
import pytest
import torch

from gacsca.params import Params
from gacsca.microcode import Tracks, Layout, Compiler, Program, Op
from gacsca.engine_np import Engine, redistribute, apply_noise
from gacsca.gpu_engine import EngineGPU, CleanGraphRunner
from gacsca.interp import compile_register_load
from gacsca.hierarchy import encode_state_info
from gacsca.noise import cell_noise_word, splitmix64
from gacsca.checkpoint import save_checkpoint, load_checkpoint


def setup(R=5, bits=20, load=False, window=(0, 0), primary_bits=None):
    p = Params(Q=128, U=2048, ncol=2)
    T = Tracks(R=R)
    L = Layout(p.Q, p.U, T, Qs=16, Us=32, Qss=16, Uss=1 << bits,
               with_tracks=False, full_registers=True)
    C = Compiler(T, L, D=1 if R == 5 else 3)
    if load:
        C.emit("RESET", dst=T["HOLD"], param=T.NT, param2=1)
        C.t += 1
        window = compile_register_load(C, "ARGA+0", "T0", nested=True)
    else:
        C.prog.nested_register_bits = bits
    C.prog.U = p.U
    cpu = Engine(p, T, L, C.prog)
    cpu.reg_window = window
    cpu.trickle = (0, 0)
    gpu = EngineGPU(p, T, L, C.prog, (0, 0), reg_window=window, seed=982,
                    register_bits=primary_bits)
    return cpu, gpu, C


@pytest.mark.parametrize("R", [3, 5])
@pytest.mark.parametrize("bits", [16, 20])
def test_both_pairs_load_raw_input_fields_locally(R, bits):
    cpu, gpu, compiler = setup(R, bits, load=True)
    values = dict(addr=np.array([[2, 9]]), age=np.array([[3, 17]]),
                  simage=np.array([[(1 << bits) - 3, (1 << (bits - 1)) + 7]]),
                  simaddr=np.array([[(1 << bits) - 7, 567]]))
    for name in ("f1", "f2", "wf1", "wf2"):
        values[name] = np.zeros((1, 2), np.int32)
    encoded = encode_state_info(values, cpu.L, cpu.p.Q)
    state = cpu.initial(1)
    for name in cpu.register_names:
        state[name][:] = 12345
    V = np.zeros((1, cpu.p.L, cpu.T.NT), np.uint8)
    V[..., cpu.T.arg(0)] = encoded
    state["trk"] = redistribute(V, R)
    packed = gpu.to_gpu(state)
    for _ in range(compiler.t):
        state = cpu.step(state)
    runner = CleanGraphRunner(gpu, packed)
    runner.run(compiler.t)
    actual = gpu.to_np(runner.state)
    for name in state:
        np.testing.assert_array_equal(actual[name], state[name], err_msg=name)
    for physical, field in (("simage", "age"), ("simaddr", "addr"),
                            ("simage2", "simage"), ("simaddr2", "simaddr")):
        np.testing.assert_array_equal(state[physical], np.repeat(values[field], cpu.p.Q, axis=1))


@pytest.mark.parametrize("age,inhibited", [(4, False), (5, True), (9, True), (10, False)])
def test_second_pair_repairs_without_cross_colony_leakage(age, inhibited):
    cpu, gpu, _ = setup(window=(5, 10))
    state = cpu.initial(1)
    ideal = np.repeat([[17, (1 << 19) + 91]], cpu.p.Q, axis=1)
    state["simage2"][:] = ideal
    state["simaddr2"][:] = ideal + 3
    state["age"][:] = age
    for x in (0, cpu.p.Q - 1):
        state["simage2"][0, x] = 56789
        state["simaddr2"][0, x] = 98765
    expected = cpu.step(state)
    packed = gpu.to_gpu(state)
    actual = gpu.to_np(gpu.step(packed, torch.empty_like(packed), 0))
    for name in expected:
        np.testing.assert_array_equal(actual[name], expected[name], err_msg=name)
    np.testing.assert_array_equal(expected["simage2"], state["simage2"] if inhibited else ideal)
    np.testing.assert_array_equal(expected["simaddr2"], state["simaddr2"] if inhibited else ideal + 3)


@pytest.mark.parametrize("R,bits,primary", [(3, 16, 16), (5, 20, 16), (3, 16, 20), (5, 20, 20), (3, 17, 16), (5, 31, 31)])
def test_packing_noise_oracle_and_legacy_noise_projection(R, bits, primary):
    cpu, gpu, _ = setup(R, bits, primary_bits=primary)
    state = cpu.initial(2)
    state["simage2"][:] = (1 << bits) - 1
    state["simaddr2"][:] = (1 << (bits - 1)) + 1
    packed = gpu.to_gpu(state)
    for k, v in state.items():
        np.testing.assert_array_equal(gpu.to_np(packed)[k], v)
    t = (1 << 40) + 31
    out = gpu.step(packed, torch.empty_like(packed), t, eps=1).cpu().numpy()
    for b, x in ((0, 0), (1, 127)):
        g = cell_noise_word(gpu.seed, t, b, x)
        for _ in range(4 + R * gpu.NW + 1):
            g = splitmix64(g)
        a = g & ((1 << bits) - 1)
        z = (g >> (16 if bits == 16 else 32)) & ((1 << bits) - 1)
        assert out[b, x, gpu.nested_base] == (a | (z << 16) if bits == 16 else a)
        if bits != 16:
            assert out[b, x, gpu.nested_base + 1] == z
    legacy_program = Program(D=cpu.prog.D, U=cpu.p.U)
    legacy = EngineGPU(cpu.p, cpu.T, cpu.L, legacy_program, (0, 0), seed=gpu.seed, register_bits=primary)
    old = legacy.initial(2)
    old_out = legacy.step(old, torch.empty_like(old), t, eps=1).cpu().numpy()
    np.testing.assert_array_equal(out[..., :gpu.nested_base], old_out[..., :legacy.track_base])
    np.testing.assert_array_equal(out[..., gpu.track_base:], old_out[..., legacy.track_base:])
    with pytest.raises(ValueError, match="legacy"):
        legacy.to_gpu(state)
    state["simage2"][0, 0] = -1
    with pytest.raises(ValueError, match="nested register schema"):
        gpu.to_gpu(state)


def test_extended_checkpoint_and_stochastic_restart(tmp_path):
    cpu, gpu, _ = setup()
    original = gpu.initial(2)
    whole = gpu.run(original.clone(), 8, .2, t0=1 << 40)
    partial = gpu.run(original.clone(), 3, .2, t0=1 << 40)
    identity = dict(register_bits=gpu.register_bits, nested_register_bits=gpu.nested_register_bits)
    path = tmp_path / "extended.npz"
    save_checkpoint(path, dict(identity=identity), dict(physical=partial.cpu().numpy()))
    _, arrays = load_checkpoint(path, identity)
    resumed = gpu.run(torch.from_numpy(arrays["physical"]).cuda(), 5, .2, t0=(1 << 40) + 3)
    assert torch.equal(whole, resumed)
    damaged = apply_noise(cpu.initial(1), cpu.p, 1, np.random.default_rng(3), nested_register_bits=20)
    for name in ("simage2", "simaddr2"):
        assert damaged[name].min() >= 0 and damaged[name].max() < 1 << 20
        assert np.any(damaged[name] > 65535)
    with pytest.raises(ValueError, match="explicit nested"):
        apply_noise(cpu.initial(1), cpu.p, 1, np.random.default_rng(3))


def test_gray_nested_controls_keep_raw_input_not_repaired_output():
    from gacsca.build import make_system
    from experiments.gray_protocol import track_bits
    from gacsca.hierarchy import decode_state_info
    upper = make_system(Q=8192, U=1048576, ncol=1, R=5, D=1,
                        Qs=16, Us=1 << 20, schedule="gray")
    lower = make_system(Q=8192, U=1048576, ncol=16, R=5, D=1,
                        Qs=8192, Us=1048576, Qss=16, Uss=1 << 20,
                        with_tracks=True, schedule="gray", nested_controls=True,
                        prog_up=upper.prog, L_up=upper.L,
                        trickle_up=upper.sched.trickle, regwin_up=upper.sched.reg_window)
    assert lower.sched.compute_end <= 15 * lower.p.U // 16
    state = {k:v[:, :16].copy() for k,v in upper.np_engine().initial(1).items()}
    state["age"][:] = upper.sched.gather_starts[0] + 17
    state["simage"][:] = 233
    state["simaddr"][:] = 111
    state["simage"][0, 7] = 98765
    state["simaddr"][0, 7] = 88888
    expected = upper.np_engine().step(state)
    assert expected["simage"][0, 7] == 233
    assert expected["simaddr"][0, 7] == 111
    bits = encode_state_info(state, lower.L, lower.p.Q)
    physical = lower.np_engine().initial(1)
    physical["age"][:] = 7 * lower.p.U // 8
    for name in ("simage", "simaddr", "simage2", "simaddr2"):
        physical[name][:] = (1 << 20) - 1
    V = np.zeros((1, lower.p.L, lower.T.NT), np.uint8)
    V[..., lower.T["INFO"]] = bits
    for bank in "ABC":
        for j in range(-5, 6):
            V[..., lower.T.arg(j, bank)] = np.roll(bits, -j * lower.p.Q, axis=1)
    physical["trk"] = redistribute(V, 5)
    del V
    gpu = lower.gpu_engine()
    runner = CleanGraphRunner(gpu, gpu.to_gpu(physical))
    del physical
    runner.run(lower.sched.compute_end - 7 * lower.p.U // 8)
    for word, name in ((gpu.nested_base, "simage"), (gpu.nested_base + 1, "simaddr")):
        np.testing.assert_array_equal(runner.state[..., word].cpu().numpy(), np.repeat(state[name], lower.p.Q, axis=1))
    decoded = decode_state_info(track_bits(gpu, runner.state, lower.T["HOLD"]), lower.L, lower.p.Q)
    for name in expected:
        np.testing.assert_array_equal(decoded[name], expected[name], err_msg=name)


def test_extended_state_cannot_be_silently_encoded_or_dropped():
    from gacsca.interp import InterpCtx
    cpu, _, _ = setup()
    state = cpu.initial(1)
    with pytest.raises(ValueError, match="discard state"):
        encode_state_info(state, cpu.L, cpu.p.Q)
    legacy = Engine(cpu.p, cpu.T, cpu.L, Program(D=1, U=cpu.p.U))
    with pytest.raises(ValueError, match="legacy"):
        legacy.step(state)
    with pytest.raises(NotImplementedError, match="second control pair"):
        InterpCtx(cpu.L, cpu.T, cpu.prog, cpu.L, (0, 0), None)


def test_register_load_rejects_absent_or_narrow_second_pair():
    cpu, _, compiler = setup(load=True)
    for width in (0, 16):
        compiler.prog.nested_register_bits = width
        with pytest.raises(ValueError, match="absent or too narrow"):
            Engine(cpu.p, cpu.T, cpu.L, compiler.prog)
        with pytest.raises(ValueError, match="absent or too narrow"):
            EngineGPU(cpu.p, cpu.T, cpu.L, compiler.prog, (0, 0))


@pytest.mark.parametrize("R", [3, 5])
def test_second_pair_with_joint_structure_flags_and_track_faults(R):
    cpu, gpu, _ = setup(R=R)
    state = cpu.initial(3)
    rng = np.random.default_rng(990 + R)
    state["age"][:] = 17
    for name, maximum in (("addr", cpu.p.Q), ("age", cpu.p.U)):
        hit = rng.random(state[name].shape) < .15
        state[name][hit] = rng.integers(0, maximum, hit.sum())
    for name in ("f1", "f2", "wf1", "wf2"):
        state[name][:] = rng.integers(0, 2, state[name].shape)
    for name in ("simage2", "simaddr2"):
        state[name][:] = np.repeat(rng.integers(0, 1 << 20, (3, 2)), cpu.p.Q, axis=1)
        hit = rng.random(state[name].shape) < .4
        state[name][hit] = rng.integers(0, 1 << 20, hit.sum())
    state["trk"][:] = rng.integers(0, 2, state["trk"].shape, dtype=np.uint8)
    packed = gpu.to_gpu(state)
    for t in range(4):
        state = cpu.step(state)
        packed = gpu.step(packed, torch.empty_like(packed), t)
        actual = gpu.to_np(packed)
        for name in state:
            np.testing.assert_array_equal(actual[name], state[name], err_msg=f"{t}.{name}")


def test_quiescent_certificate_checks_extended_registers():
    from experiments.quiescent import try_skip_quiescent
    cpu, gpu, _ = setup()
    state = cpu.initial(1)
    state["simage2"][0, 17] = 98765
    runner = CleanGraphRunner(gpu, gpu.to_gpu(state))
    original = runner.state.clone()
    assert try_skip_quiescent(runner, 10) is None
    assert torch.equal(runner.state, original)
    runner.run(1)
    direct = gpu.run(runner.state.clone(), 10, 0)
    assert try_skip_quiescent(runner, 10) is not None
    assert torch.equal(runner.state, direct)
