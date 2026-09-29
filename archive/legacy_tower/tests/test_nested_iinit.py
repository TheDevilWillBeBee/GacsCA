"""First nested-interpreter component, not a complete third simulation link.

Project a real middle-level program onto its IINIT ages and their following MOV.
The latter is reachable under the one-step clock fault. The new outer colony
must reproduce these actual middle transitions, including every raw track copy.
Other nested kinds remain rejected, so this cannot silently claim depth three.
"""
import numpy as np
import pytest
import torch

from gacsca.build import make_tower, make_system
from gacsca.engine_np import repair
from gacsca.gpu_engine import CleanGraphRunner
from gacsca.hierarchy import encode_state_info, decode_state_info
from gacsca.microcode import Program


def nested_fixture(R):
    kw = dict(R=5, D=1, Q0=512, U0=32768, U1=8192) if R == 5 else {}
    middle, top = make_tower(**kw)
    projected = Program(D=middle.prog.D, U=middle.prog.U)
    selected = [op for op in middle.prog.ops if op.kind == "IINIT"]
    assert len(selected) == R
    for op in selected:
        assert middle.prog.ops_at(op.t0) == [op]
        projected.add(op)
        for following in middle.prog.ops_at(op.t0 + 1):
            assert following.kind == "MOV"
            projected.add(following)
    outer = make_system(Q=1024, U=65536, ncol=16, R=R, D=middle.prog.D,
                        Qs=middle.p.Q, Us=middle.p.U, Qss=top.p.Q, Uss=top.p.U,
                        with_tracks=True, full_registers=True,
                        prog_up=projected, L_up=middle.L,
                        trickle_up=middle.sched.trickle, regwin_up=middle.sched.reg_window)
    return outer, middle, selected


@pytest.mark.parametrize("R", [3, 5])
def test_nested_iinit_full_period_reproduces_actual_middle_transition(R):
    outer, middle, ops = nested_fixture(R)
    B = 2 * len(ops)
    direct = middle.np_engine()
    state = {k:v[:, :16].copy() for k,v in direct.initial(B).items()}
    state["age"][:] = np.array([op.t0 for op in ops] * 2)[:, None]
    base = middle.L.b0 + middle.L.track_base
    state["addr"][:] = (base + np.arange(16)) % middle.p.Q
    rng = np.random.default_rng(930 + R)
    state["trk"][:] = rng.integers(0, 2, state["trk"].shape, dtype=np.uint8)
    for name in ("simage", "simaddr"):
        state[name][:] = rng.integers(0, 65536, state[name].shape, dtype=np.int32)
    # Force a genuine changed primary for every slot while retaining arbitrary
    # raw copies elsewhere; a random source/destination can accidentally agree.
    repaired = repair(state["trk"])
    for b, op in enumerate(ops):
        y = 5 + (op.param + R // 2 - 5) % R
        source = y if op.param2 else y - op.param
        opposite = 1 - repaired[b, source, op.src]
        for r in range(R):
            state["trk"][b, y - (r - R // 2), op.dst, r] = opposite
    # Independent raw control/flag faults in the second half of the batch.
    state["addr"][len(ops):, 7] = 1
    state["age"][len(ops):, 9] += 1
    state["f1"][len(ops):, 3] = 1
    state["f2"][len(ops):, 4] = 1
    for age in np.unique(state["age"]):
        assert middle.prog.ops_at(age) == outer.sched.ictx.prog_up.ops_at(age)
    expected = direct.step(state)
    neutral = middle.np_engine()
    neutral.prog = Program(D=middle.prog.D, U=middle.prog.U)
    no_instruction = neutral.step(state)
    for b in range(len(ops)):
        assert np.any(expected["trk"][b] != no_instruction["trk"][b]), "IINIT witness must change output"
    # Direct GPU agreement makes the upper reference independently exercised.
    mgpu = middle.gpu_engine()
    packed = mgpu.to_gpu(state)
    actual_direct = mgpu.to_np(mgpu.step(packed, torch.empty_like(packed), 0))
    for name in expected:
        np.testing.assert_array_equal(actual_direct[name], expected[name], err_msg=f"direct.{name}")
    physical = outer.np_engine().initial(B, info_bits=encode_state_info(state, outer.L, outer.p.Q))
    physical["simage"][:] = np.repeat(state["age"], outer.p.Q, axis=1)
    physical["simaddr"][:] = np.repeat(state["addr"], outer.p.Q, axis=1)
    ogpu = outer.gpu_engine()
    runner = CleanGraphRunner(ogpu, ogpu.to_gpu(physical))
    del physical
    runner.run(outer.p.U)
    decoded = decode_state_info(ogpu.info_bits(runner.state).cpu().numpy(), outer.L, outer.p.Q)
    for name in expected:
        np.testing.assert_array_equal(decoded[name], expected[name], err_msg=f"nested.{name}")


@pytest.mark.parametrize("R", [3, 5])
def test_nested_iinit_evaluation_numpy_cuda_parity(R):
    outer, middle, ops = nested_fixture(R)
    engine = outer.np_engine()
    state = engine.initial(len(ops))
    eval_op = next(o for o in outer.prog.ops if o.kind == "IEVAL")
    state["age"][:] = eval_op.t0
    state["simage"][:] = np.array([op.t0 for op in ops])[:, None]
    state["simaddr"][:] = middle.L.b0 + middle.L.track_base + 4
    rng = np.random.default_rng(940 + R)
    state["trk"][:] = rng.integers(0, 2, state["trk"].shape, dtype=np.uint8)
    expected = engine.step(state)
    gpu = outer.gpu_engine()
    packed = gpu.to_gpu(state)
    actual = gpu.to_np(gpu.step(packed, torch.empty_like(packed), 0))
    for name in expected:
        np.testing.assert_array_equal(actual[name], expected[name], err_msg=name)


def test_remaining_nested_instructions_still_rejected():
    from gacsca.interp import InterpCtx
    outer, middle, _ = nested_fixture(3)
    with pytest.raises(NotImplementedError, match="ILATCH"):
        InterpCtx(outer.L, outer.T, middle.prog, middle.L, middle.sched.trickle, None)


def test_nested_iinit_rejects_nonlocal_unrouted_outer_copy():
    from dataclasses import replace
    from gacsca.interp import InterpCtx
    outer, middle, ops = nested_fixture(5)
    bad = Program(D=1, U=middle.p.U)
    bad.add(replace(ops[0], param=-2, param2=0))
    with pytest.raises(ValueError, match="radius-safe"):
        InterpCtx(outer.L, outer.T, bad, middle.L, middle.sched.trickle, None)


def test_nested_iinit_gray_stage_five_with_full_register_alphabet():
    """Full-Q stage-five execution on 16 arbitrary middle cells, not a full tower period."""
    from gacsca.engine_np import redistribute
    from experiments.gray_protocol import track_bits

    middle, top = make_tower(Q0=8192, U0=1048576, Q1=8192, U1=1048576,
                             ncol0=8192, R=5, D=1, schedule="gray")
    projected = Program(D=1, U=middle.p.U)
    ops = [op for op in middle.prog.ops if op.kind == "IINIT"]
    assert len(ops) == 5
    for op in ops:
        assert middle.prog.ops_at(op.t0) == [op]
        projected.add(op)
        for following in middle.prog.ops_at(op.t0 + 1):
            assert following.kind == "MOV"
            projected.add(following)
    outer = make_system(Q=8192, U=1048576, ncol=16, R=5, D=1, schedule="gray",
                        Qs=8192, Us=1048576, Qss=8192, Uss=1048576,
                        with_tracks=True, full_registers=True, prog_up=projected,
                        L_up=middle.L, trickle_up=middle.sched.trickle,
                        regwin_up=middle.sched.reg_window)
    assert outer.L.K == 512
    assert outer.L.fields["SIMAGE"][1] == outer.L.fields["SIMADDR"][1] == 20
    # Both levels have the same 87-track registry; using the small top factory
    # avoids allocating the entire 67-million-cell middle initial ring.
    state = {k:v[:, :16].copy() for k,v in top.np_engine().initial(5).items()}
    state["age"][:] = np.array([op.t0 for op in ops])[:, None]
    state["addr"][:] = middle.L.b0 + middle.L.track_base + np.arange(16)
    rng = np.random.default_rng(955)
    state["trk"][:] = rng.integers(0, 2, state["trk"].shape, dtype=np.uint8)
    for name in ("simage", "simaddr"):
        state[name][:] = rng.integers(0, 1 << 20, state[name].shape, dtype=np.int32)
    state["addr"][:, 7] = 1
    state["age"][:, 9] += 1
    for age in np.unique(state["age"]):
        assert middle.prog.ops_at(age) == projected.ops_at(age)
    expected = middle.np_engine().step(state)
    bits = encode_state_info(state, outer.L, outer.p.Q)
    physical = outer.np_engine().initial(5)
    physical["age"][:] = 7 * outer.p.U // 8
    physical["simage"][:] = (1 << 20) - 1
    physical["simaddr"][:] = (1 << 20) - 1
    values = np.zeros((5, outer.p.L, outer.T.NT), dtype=np.uint8)
    values[..., outer.T["INFO"]] = bits
    for bank in "ABC":
        for j in range(-5, 6):
            values[..., outer.T.arg(j, bank)] = np.roll(bits, -j * outer.p.Q, axis=1)
    physical["trk"] = redistribute(values, 5)
    del values
    gpu = outer.gpu_engine()
    runner = CleanGraphRunner(gpu, gpu.to_gpu(physical))
    del physical
    runner.run(outer.sched.compute_end - 7 * outer.p.U // 8)
    decoded = decode_state_info(track_bits(gpu, runner.state, outer.T["HOLD"]), outer.L, outer.p.Q)
    for name in expected:
        np.testing.assert_array_equal(decoded[name], expected[name], err_msg=f"gray nested HOLD.{name}")
