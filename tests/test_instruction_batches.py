"""Interpreter dispatch must preserve the real simultaneous 23-clear batch."""
import numpy as np
import pytest
import torch

from gacsca.build import make_tower, make_system
from gacsca.engine_np import redistribute
from gacsca.gpu_engine import CleanGraphRunner
from gacsca.hierarchy import encode_state_info, decode_state_info
from gacsca.microcode import Program, Op


def fixture(R=3, gray=False):
    kw = dict(R=5, D=1, Q0=512, U0=32768, U1=8192) if R == 5 else {}
    if gray:
        kw = dict(R=5, D=1, Q0=8192, U0=1048576, Q1=8192, U1=1048576,
                  ncol0=8192, schedule="gray")
    middle, top = make_tower(**kw)
    age = max({o.t0 for o in middle.prog.ops}, key=lambda a:len(middle.prog.ops_at(a)))
    batch = middle.prog.ops_at(age)
    assert len(batch) == 23 and all(o.kind == "CONST" and o.param == 0 for o in batch)
    projected = Program(D=middle.prog.D, U=middle.p.U)
    reachable = {id(o) for a in (age, age + 1) for o in middle.prog.ops_at(a)}
    for op in middle.prog.ops:
        if id(op) in reachable: projected.add(op)
    outer = make_system(Q=8192 if gray else 1024, U=1048576 if gray else 65536,
                        ncol=16, R=R, D=middle.prog.D,
                        Qs=middle.p.Q, Us=middle.p.U, Qss=top.p.Q, Uss=top.p.U,
                        with_tracks=True, full_registers=True,
                        schedule="gray" if gray else "compressed", prog_up=projected,
                        L_up=middle.L, trickle_up=middle.sched.trickle,
                        regwin_up=middle.sched.reg_window)
    return outer, middle, age, batch


def reference(outer, middle, age, batch, gray=False):
    B, L = 2, outer.p.ncol
    state = {k:np.zeros((B, L), np.int32) for k in
             ("addr", "age", "f1", "f2", "wf1", "wf2", "simage", "simaddr")}
    state["age"][:] = age
    state["addr"][:] = (middle.L.b0 + middle.L.track_base + np.arange(L)) % middle.p.Q
    rng = np.random.default_rng(1200 + middle.T.R)
    V = rng.integers(0, 2, (B, L, middle.T.NT), dtype=np.uint8)
    for op in batch: V[..., op.dst] = 1
    state["trk"] = redistribute(V, middle.T.R)
    state["trk"][:, ::3, :, 0] ^= rng.integers(0, 2, state["trk"][:, ::3, :, 0].shape, dtype=np.uint8)
    for field in ("simage", "simaddr"):
        state[field][:] = rng.integers(0, 1 << (20 if gray else 16), (B, L), dtype=np.int32)
    state["age"][1, 9] += 1
    state["addr"][1, 7] = 1
    state["f1"][1, 3] = 1
    expected = middle.np_engine().step(state)
    for op in batch:
        np.testing.assert_array_equal(expected["trk"][0, :, op.dst], 0)
    gpu = middle.gpu_engine()
    packed = gpu.to_gpu(state)
    actual = gpu.to_np(gpu.step(packed, torch.empty_like(packed), 0))
    for name in expected:
        np.testing.assert_array_equal(actual[name], expected[name], err_msg=f"middle.{name}")
    return state, expected


@pytest.mark.parametrize("R", [3, 5])
def test_real_23_clear_batch_complete_outer_period(R):
    outer, middle, age, batch = fixture(R)
    state, expected = reference(outer, middle, age, batch)
    assert len([o for o in outer.prog.ops if o.kind == "IEVAL"]) == 23
    physical = outer.np_engine().initial(2, info_bits=encode_state_info(state, outer.L, outer.p.Q))
    physical["simage"][:] = np.repeat(state["age"], outer.p.Q, axis=1)
    physical["simaddr"][:] = np.repeat(state["addr"], outer.p.Q, axis=1)
    gpu = outer.gpu_engine()
    runner = CleanGraphRunner(gpu, gpu.to_gpu(physical))
    runner.run(outer.p.U)
    decoded = decode_state_info(gpu.info_bits(runner.state).cpu().numpy(), outer.L, outer.p.Q)
    for name in expected:
        np.testing.assert_array_equal(decoded[name], expected[name], err_msg=name)


def test_real_23_clear_batch_gray_stage_five():
    from experiments.gray_protocol import track_bits
    outer, middle, age, batch = fixture(5, gray=True)
    state, expected = reference(outer, middle, age, batch, gray=True)
    assert outer.L.K == 512
    bits = encode_state_info(state, outer.L, outer.p.Q)
    physical = outer.np_engine().initial(2)
    physical["age"][:] = start = 7 * outer.p.U // 8
    physical["simage"][:] = physical["simaddr"][:] = (1 << 20) - 1
    V = np.zeros((2, outer.p.L, outer.T.NT), np.uint8)
    V[..., outer.T["INFO"]] = bits
    for bank in "ABC":
        for j in range(-5, 6): V[..., outer.T.arg(j, bank)] = np.roll(bits, -j * outer.p.Q, axis=1)
    physical["trk"] = redistribute(V, 5)
    del V
    gpu = outer.gpu_engine()
    runner = CleanGraphRunner(gpu, gpu.to_gpu(physical))
    runner.run(outer.sched.compute_end - start)
    decoded = decode_state_info(track_bits(gpu, runner.state, outer.T["HOLD"]), outer.L, outer.p.Q)
    for name in expected:
        np.testing.assert_array_equal(decoded[name], expected[name], err_msg=f"Gray HOLD.{name}")


@pytest.mark.parametrize("R", [3, 5])
def test_large_mixed_batch_preserves_old_reads_and_last_guarded_write(R):
    old_outer, middle, _, _ = fixture(R)
    T, age = middle.T, 17
    program = Program(D=middle.prog.D, U=middle.p.U)
    program.add(Op("CONST", age, age + 1, 0, middle.p.Q, dst=T["T1"], param=0))
    program.add(Op("MOV", age, age + 1, 0, middle.p.Q, dst=T["T0"], src=T["T1"]))
    for j in range(63):
        program.add(Op("CONST", age, age + 1, 0, middle.p.Q, dst=T["T1"], param=j % 2))
    program.add(Op("CONST", age, age + 1, 0, middle.p.Q, dst=T["T2"], param=1))
    program.add(Op("CONST", age, age + 1, 0, middle.p.Q // 2, dst=T["T2"], param=0))
    assert len(program.ops) == 67
    outer = make_system(Q=1024, U=65536, ncol=16, R=R, D=program.D,
                        Qs=middle.p.Q, Us=middle.p.U, Qss=old_outer.L.Qss, Uss=old_outer.L.Uss,
                        with_tracks=True, full_registers=True, prog_up=program, L_up=middle.L,
                        trickle_up=middle.sched.trickle, regwin_up=middle.sched.reg_window)
    middle.prog = program
    state = {k:v[:, :16].copy() for k,v in middle.np_engine().initial(1).items()}
    state["age"][:] = age
    state["addr"][:] = middle.p.Q // 2 - 8 + np.arange(16)
    V = np.zeros((1, 16, T.NT), np.uint8)
    V[..., T["T1"]] = 1
    state["trk"] = redistribute(V, R)
    expected = middle.np_engine().step(state)
    # These sites are away from the short periodic ring's structural seam.
    for site, final_bit in ((6, 0), (9, 1)):
        assert expected["trk"][0, site, T["T0"], R // 2] == 1  # old input, not the earlier clear
        assert expected["trk"][0, site, T["T1"], R // 2] == 0
        assert expected["trk"][0, site, T["T2"], R // 2] == final_bit
    gpu_mid = middle.gpu_engine()
    packed = gpu_mid.to_gpu(state)
    actual = gpu_mid.to_np(gpu_mid.step(packed, torch.empty_like(packed), 0))
    for name in expected:
        np.testing.assert_array_equal(actual[name], expected[name], err_msg=f"middle.{name}")
    physical = outer.np_engine().initial(1, info_bits=encode_state_info(state, outer.L, outer.p.Q))
    physical["simage"][:] = age
    physical["simaddr"][:] = np.repeat(state["addr"], outer.p.Q, axis=1)
    gpu = outer.gpu_engine()
    runner = CleanGraphRunner(gpu, gpu.to_gpu(physical))
    runner.run(outer.p.U)
    decoded = decode_state_info(gpu.info_bits(runner.state).cpu().numpy(), outer.L, outer.p.Q)
    for name in expected:
        np.testing.assert_array_equal(decoded[name], expected[name], err_msg=name)


def test_dispatch_capacity_does_not_remove_operand_slot_bounds():
    from gacsca.interp import InterpCtx, validate_resource_slots
    outer, middle, age, batch = fixture(3)
    validate_resource_slots(outer.sched.ictx.prog_up)
    bad = Program(D=middle.prog.D, U=middle.p.U)
    for op in batch: bad.add(op)
    bad.add(Op("MOV", age, age + 1, 0, middle.p.Q, dst=middle.T["T0"], src=middle.T["T1"]))
    with pytest.raises(ValueError, match="concurrent upper value instructions"):
        InterpCtx(outer.L, outer.T, bad, middle.L, middle.sched.trickle, None)


@pytest.mark.parametrize("R", [3, 5])
@pytest.mark.parametrize("active", [True, False])
def test_high_instruction_index_numpy_cuda_and_inactive_slot(R, active):
    outer, middle, age, batch = fixture(R)
    phase = next(o for o in outer.prog.ops if o.kind == "IEVAL" and o.param == 22)
    engine = outer.np_engine()
    state = {k:v[:, :outer.p.Q].copy() for k,v in engine.initial(1).items()}
    state["age"][:] = phase.t0
    state["simage"][:] = age if active else age + 1
    state["simaddr"][:] = middle.p.Q // 2
    V = np.zeros((1, outer.p.Q, outer.T.NT), np.uint8)
    V[..., outer.T["HOLD"]] = 1
    state["trk"] = redistribute(V, R)
    expected = engine.step(state)
    writer = outer.sched.ictx.pos(batch[-1].dst, R // 2)
    assert expected["trk"][0, writer, outer.T["HOLD"], R // 2] == int(not active)
    gpu = outer.gpu_engine()
    packed = gpu.to_gpu(state)
    actual = gpu.to_np(gpu.step(packed, torch.empty_like(packed), 0))
    for name in expected:
        np.testing.assert_array_equal(actual[name], expected[name], err_msg=name)


@pytest.mark.parametrize("R,gray", [(3, False), (5, False), (5, True)])
def test_all_other_middle_opcodes_compile_without_serializing_the_middle(R, gray):
    old_outer, middle, _, _ = fixture(R, gray=gray)
    projected = Program(D=middle.prog.D, U=middle.p.U)
    for op in middle.prog.ops:
        if op.kind != "IEVAL": projected.add(op)
    kwargs = dict(Q=old_outer.p.Q, U=old_outer.p.U, ncol=16, R=R, D=middle.prog.D,
                  Qs=middle.p.Q, Us=middle.p.U, Qss=old_outer.L.Qss, Uss=old_outer.L.Uss,
                  with_tracks=True, full_registers=True,
                  schedule="gray" if gray else "compressed", nested_controls=True,
                  L_up=middle.L, trickle_up=middle.sched.trickle,
                  regwin_up=middle.sched.reg_window, inner_ctx=middle.sched.ictx)
    outer = make_system(prog_up=projected, **kwargs)
    assert len([o for o in outer.prog.ops if o.kind == "IEVAL"]) == 23
    assert projected.ops == [o for o in middle.prog.ops if o.kind != "IEVAL"]
    deadline = 15 * outer.p.U // 16 if gray else outer.p.U - 1
    assert outer.sched.compute_end < deadline
    # Opcode closure is a compilation result, not an execution theorem.
    full = make_system(prog_up=middle.prog, **kwargs)
    assert full.sched.ictx.prog_up is middle.prog
    assert full.sched.compute_end == outer.sched.compute_end
    assert len([o for o in full.prog.ops if o.kind == "IEVAL"]) == 23
