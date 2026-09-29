"""Nested broadcast accumulation, not yet a complete third simulation link."""
import numpy as np
import pytest
import torch
from itertools import product

from gacsca.build import make_tower, make_system
from gacsca.engine_np import redistribute
from gacsca.gpu_engine import CleanGraphRunner
from gacsca.hierarchy import encode_state_info, decode_state_info
from gacsca.microcode import Program


def fixture(R, gray=False):
    kw = dict(R=5, D=1, Q0=512, U0=32768, U1=8192) if R == 5 else {}
    if gray:
        kw = dict(R=5, D=1, Q0=8192, U0=1048576, Q1=8192, U1=1048576,
                  ncol0=8192, schedule="gray")
    middle, top = make_tower(**kw)
    projected = Program(D=middle.prog.D, U=middle.p.U)
    ibc = [o for o in middle.prog.ops if o.kind == "IBC"]
    for o in ibc:
        assert middle.prog.ops_at(o.t0) == [o]
        projected.add(o)
    outer = make_system(Q=8192 if gray else 1024, U=1048576 if gray else 65536,
                        ncol=16, R=R, D=middle.prog.D,
                        Qs=middle.p.Q, Us=middle.p.U, Qss=top.p.Q, Uss=top.p.U,
                        with_tracks=True, full_registers=True,
                        schedule="gray" if gray else "compressed", nested_controls=True,
                        prog_up=projected, L_up=middle.L, trickle_up=middle.sched.trickle,
                        regwin_up=middle.sched.reg_window, inner_ctx=middle.sched.ictx)
    return outer, middle, top, ibc


def witnesses(outer, middle, top, ibc):
    """Actual BCAST/IBC phases, both directions, every feasible pass offset."""
    h, D = middle.T.R // 2, top.prog.D
    broadcast = {d: next(o for o in top.prog.ops if o.kind == "BCAST" and o.param == d)
                 for d in (-1, 1)}
    cases = []
    for op in ibc:
        for direction, inner_op in broadcast.items():
            candidates = [(c, k) for c in range(-h, h + 1) for k in range(1, D + 1)
                          if op.param - c == (-k if direction > 0 else k)]
            if candidates:
                c, k = candidates[0]
                cases.append((op, inner_op, c, k))
    B, L = len(cases), outer.p.ncol
    state = {k:np.zeros((B, L), np.int32) for k in
             ("addr", "age", "f1", "f2", "wf1", "wf2", "simage", "simaddr")}
    rng = np.random.default_rng(1000 + middle.T.R)
    values = rng.integers(0, 2, (B, L, middle.T.NT), dtype=np.uint8)
    base = middle.L.b0 + middle.L.track_base
    names = middle.sched.ictx.n
    for b, (op, inner, c, kk) in enumerate(cases):
        # Put site seven at the deeper SIG track's selected copy. Addresses
        # vary normally around it; top addresses are raw holder controls.
        state["addr"][b] = (base + middle.T["SIG"] * middle.T.R + h + c + np.arange(L) - 7) % middle.p.Q
        state["age"][b] = op.t0
        state["simage"][b] = inner.t0
        sh = -kk if inner.param > 0 else kk
        state["simaddr"][b] = (inner.lo - sh - c) % top.p.Q
        values[b, :, names[f"SIG{kk}"]] = 1
        values[b, :, names[f"CARRY{kk}"]] = 1
        values[b, :, names["BFOUND"]] = 0
        values[b, :, names["BVAL"]] = 0
    state["trk"] = redistribute(values, middle.T.R)
    # Retain inconsistent raw backups without changing any repaired source.
    state["trk"][:, ::3, :, 0] ^= rng.integers(0, 2, state["trk"][:, ::3, :, 0].shape, dtype=np.uint8)
    # One isolated raw clock fault must suppress IBC at its holder despite
    # repair restoring that clock in the independently computed output.
    state["simage"][:, 7] = top.p.U - 1
    return state, cases


@pytest.mark.parametrize("R", [3, 5])
def test_nested_ibc_full_outer_period(R):
    outer, middle, top, ibc = fixture(R)
    state, cases = witnesses(outer, middle, top, ibc)
    expected = middle.np_engine().step(state)
    neutral = middle.np_engine()
    neutral.prog = Program(D=middle.prog.D, U=middle.prog.U)
    baseline = neutral.step(state)
    # At least one real write in EVERY direction/pass case. The faulty clock
    # at site seven must remain distinct from the repaired output clock.
    for b in range(len(cases)):
        assert np.any(expected["trk"][b] != baseline["trk"][b]), f"vacuous case {b}"
    assert np.any(expected["simage"][:, 7] != state["simage"][:, 7])
    mgpu = middle.gpu_engine()
    packed = mgpu.to_gpu(state)
    actual = mgpu.to_np(mgpu.step(packed, torch.empty_like(packed), 0))
    for name in expected:
        np.testing.assert_array_equal(actual[name], expected[name], err_msg=f"middle.{name}")
    physical = outer.np_engine().initial(len(cases), info_bits=encode_state_info(state, outer.L, outer.p.Q))
    # No host cache seeding: the new schedule must load the input itself.
    for name in ("simage", "simaddr", "simage2", "simaddr2"):
        physical[name][:] = 65535
    gpu = outer.gpu_engine()
    runner = CleanGraphRunner(gpu, gpu.to_gpu(physical))
    del physical
    runner.run(outer.p.U)
    decoded = decode_state_info(gpu.info_bits(runner.state).cpu().numpy(), outer.L, outer.p.Q)
    for name in expected:
        np.testing.assert_array_equal(decoded[name], expected[name], err_msg=f"outer.{name}")


@pytest.mark.parametrize("R", [3, 5])
def test_nested_ibc_evaluation_numpy_cuda_parity(R):
    outer, middle, top, ibc = fixture(R)
    engine = outer.np_engine()
    state = engine.initial(3)
    op = next(o for o in outer.prog.ops if o.kind == "IEVAL")
    state["age"][:] = op.t0
    state["simage"][:] = ibc[len(ibc) // 2].t0
    state["simaddr"][:] = middle.L.b0 + middle.L.track_base + middle.T["SIG"] * R + R // 2
    inner = next(o for o in top.prog.ops if o.kind == "BCAST")
    state["simage2"][:] = inner.t0
    state["simaddr2"][:] = inner.lo
    rng = np.random.default_rng(1010 + R)
    state["trk"][:] = rng.integers(0, 2, state["trk"].shape, dtype=np.uint8)
    # Independently damaged physical holder controls, including outside the
    # inner table's valid Age range and a full-alphabet Address value.
    state["simage2"][1, 13::19] = 65535
    state["simaddr2"][2, 11::17] = 65535
    expected = engine.step(state)
    gpu = outer.gpu_engine()
    packed = gpu.to_gpu(state)
    actual = gpu.to_np(gpu.step(packed, torch.empty_like(packed), 0))
    for name in expected:
        np.testing.assert_array_equal(actual[name], expected[name], err_msg=name)


@pytest.mark.parametrize("R", [3, 5])
def test_nested_ibc_scalar_truth_table_and_guards(R):
    outer, middle, top, ibc = fixture(R)
    engine = outer.np_engine()
    # Direct arithmetic truth table, independent of the nested selector.
    cases = list(product((-1, 1), (0, 1), (0, 1), (0, 1), ("valid", "range", "clock")))
    state = {k:v[:, :outer.p.Q].copy() for k,v in engine.initial(len(cases)).items()}
    phase = next(o for o in outer.prog.ops if o.kind == "IEVAL")
    state["age"][:] = phase.t0
    n = outer.sched.ictx.n
    values = np.zeros((len(cases), outer.p.Q, outer.T.NT), np.uint8)
    for b, (direction, sig, val, found, guard) in enumerate(cases):
        sh = 1 if direction < 0 else -1
        op = next(o for o in ibc if o.param == sh)
        inner = next(o for o in top.prog.ops if o.kind == "BCAST" and o.param == direction)
        state["simage"][b] = op.t0
        state["simaddr"][b] = middle.L.b0 + middle.L.track_base + middle.T["SIG"] * R + R // 2
        state["simage2"][b] = inner.t0 if guard != "clock" else 65535
        state["simaddr2"][b] = ((inner.hi if guard == "range" else inner.lo) - sh) % top.p.Q
        for track, bit in ((n["S00"], sig), (n["S01"], val), (n["S02"], found), (outer.T["HOLD"], 1 - val)):
            values[b, :, track] = bit
    state["trk"] = redistribute(values, R)
    expected = engine.step(state)
    for b, (direction, sig, val, found, guard) in enumerate(cases):
        take = guard == "valid" and sig and (not found or direction > 0)
        for track in ("BVAL", "BFOUND"):
            writer = outer.sched.ictx.pos(middle.sched.ictx.n[track], R // 2)
            want = (1 if track == "BFOUND" else val) if take else 1 - val
            assert expected["trk"][b, writer, outer.T["HOLD"], R // 2] == want, (b, track)
    gpu = outer.gpu_engine()
    packed = gpu.to_gpu(state)
    actual = gpu.to_np(gpu.step(packed, torch.empty_like(packed), 0))
    for name in expected:
        np.testing.assert_array_equal(actual[name], expected[name], err_msg=name)


@pytest.mark.parametrize("R", [3, 5])
@pytest.mark.parametrize("direction", [-1, 1])
@pytest.mark.parametrize("excluded", [False, True])
def test_nested_ibc_actual_local_latch(R, direction, excluded):
    outer, middle, top, ibc = fixture(R)
    op = next(o for o in ibc if o.param == (1 if direction < 0 else -1))
    inner = next(o for o in top.prog.ops if o.kind == "BCAST" and o.param == direction)
    ctx = outer.sched.ictx
    writer = ctx.pos(middle.sched.ictx.n["BVAL"], R // 2)
    source = ctx.pos(middle.sched.ictx.n["SIG1"], R // 2)
    pass_dir = 1 if writer >= source else -1
    phase = next(o for o in outer.prog.ops if o.kind == "ILATCH" and o.param == 0 and o.param2 == pass_dir)
    clock = phase.t0 + abs(writer - source) // outer.prog.D
    assert clock < phase.t1
    engine = outer.np_engine()
    state = {k:v[:, :outer.p.Q].copy() for k,v in engine.initial(1).items()}
    state["age"][:] = clock
    state["simage"][:] = op.t0
    state["simaddr"][:] = middle.L.b0 + middle.L.track_base + middle.T["SIG"] * R + R // 2
    state["simage2"][:] = inner.t0
    sh = 1 if direction < 0 else -1
    state["simaddr2"][:] = ((inner.hi if excluded else inner.lo) - sh) % top.p.Q
    values = np.zeros((1, outer.p.Q, outer.T.NT), np.uint8)
    values[..., ctx.n["BUS"]] = 1
    state["trk"] = redistribute(values, R)
    expected = engine.step(state)
    assert expected["trk"][0, writer, ctx.n["S00"], R // 2] == int(not excluded)
    gpu = outer.gpu_engine()
    packed = gpu.to_gpu(state)
    actual = gpu.to_np(gpu.step(packed, torch.empty_like(packed), 0))
    for name in expected:
        np.testing.assert_array_equal(actual[name], expected[name], err_msg=name)


def test_nested_ibc_requires_explicit_context_and_loaded_controls():
    from gacsca.interp import InterpCtx
    outer, middle, top, _ = fixture(3)
    with pytest.raises(NotImplementedError, match="IBC"):
        InterpCtx(outer.L, outer.T, outer.sched.ictx.prog_up, middle.L, middle.sched.trickle, None)
    with pytest.raises(ValueError, match="exact middle layout"):
        InterpCtx(outer.L, outer.T, outer.sched.ictx.prog_up, top.L, middle.sched.trickle, None,
                  inner=middle.sched.ictx)
    outer.prog.nested_register_bits = 0
    with pytest.raises(ValueError, match="pair is absent|raw-input control pair"):
        outer.gpu_engine()
    with pytest.raises(ValueError, match="raw-input control loading"):
        make_system(inner_ctx=middle.sched.ictx)


@pytest.mark.parametrize("R", [3, 5])
@pytest.mark.parametrize("field", ["simage2", "simaddr2"])
def test_nested_control_fault_stays_with_its_physical_holder(R, field):
    outer, middle, top, ibc = fixture(R)
    engine = outer.np_engine()
    state = {k:v[:, :outer.p.Q].copy() for k,v in engine.initial(1).items()}
    op = next(o for o in ibc if o.param == -1)
    inner = next(o for o in top.prog.ops if o.kind == "BCAST" and o.param == 1)
    phase = next(o for o in outer.prog.ops if o.kind == "IEVAL")
    state["age"][:] = phase.t0
    state["simage"][:] = op.t0
    state["simaddr"][:] = middle.L.b0 + middle.L.track_base + middle.T["SIG"] * R + R // 2
    state["simage2"][:] = inner.t0
    state["simaddr2"][:] = inner.lo + 1
    values = np.zeros((1, outer.p.Q, outer.T.NT), np.uint8)
    values[..., outer.sched.ictx.n["S00"]] = 1
    values[..., outer.sched.ictx.n["S01"]] = 1
    state["trk"] = redistribute(values, R)
    writer = outer.sched.ictx.pos(middle.sched.ictx.n["BVAL"], R // 2)
    damaged = {k:v.copy() for k,v in state.items()}
    damaged[field][0, writer] = 65535 if field == "simage2" else inner.hi + 1
    clean, fault = engine.step(state), engine.step(damaged)
    changed = np.flatnonzero(np.any(clean["trk"] != fault["trk"], axis=(0, 2, 3)))
    np.testing.assert_array_equal(changed, [writer])
    # The full next transition repairs this isolated raw output discrepancy.
    clean2, fault2 = engine.step(clean), engine.step(fault)
    for name in clean2:
        np.testing.assert_array_equal(fault2[name], clean2[name], err_msg=name)
    gpu = outer.gpu_engine()
    packed = gpu.to_gpu(damaged)
    actual = gpu.to_np(gpu.step(packed, torch.empty_like(packed), 0))
    for name in fault:
        np.testing.assert_array_equal(actual[name], fault[name], err_msg=name)


def test_nested_ibc_gray_stage_five():
    from experiments.gray_protocol import track_bits
    outer, middle, top, ibc = fixture(5, gray=True)
    state, cases = witnesses(outer, middle, top, ibc)
    expected = middle.np_engine().step(state)
    assert outer.L.K == 512 and outer.prog.nested_register_bits == 20
    bits = encode_state_info(state, outer.L, outer.p.Q)
    physical = outer.np_engine().initial(len(cases))
    start = 7 * outer.p.U // 8
    physical["age"][:] = start
    for name in ("simage", "simaddr", "simage2", "simaddr2"):
        physical[name][:] = (1 << 20) - 1
    values = np.zeros((len(cases), outer.p.L, outer.T.NT), np.uint8)
    values[..., outer.T["INFO"]] = bits
    for bank in "ABC":
        for j in range(-5, 6):
            values[..., outer.T.arg(j, bank)] = np.roll(bits, -j * outer.p.Q, axis=1)
    physical["trk"] = redistribute(values, 5)
    del values
    gpu = outer.gpu_engine()
    runner = CleanGraphRunner(gpu, gpu.to_gpu(physical))
    del physical
    runner.run(outer.sched.compute_end - start)
    decoded = decode_state_info(track_bits(gpu, runner.state, outer.T["HOLD"]), outer.L, outer.p.Q)
    for name in expected:
        np.testing.assert_array_equal(decoded[name], expected[name], err_msg=f"Gray HOLD.{name}")
