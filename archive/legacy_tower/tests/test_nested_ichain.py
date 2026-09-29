"""Nested carry propagation: actual-period witnesses and independent bit algebra."""
from dataclasses import replace
from itertools import product
import numpy as np
import pytest
import torch

from gacsca.build import make_tower, make_system
from gacsca.engine_np import redistribute
from gacsca.gpu_engine import CleanGraphRunner
from gacsca.hierarchy import encode_state_info, decode_state_info
from gacsca.microcode import Program


def fixture(R=3, gray=False, skind=None):
    kw = dict(R=5, D=1, Q0=512, U0=32768, U1=8192) if R == 5 else {}
    if gray:
        kw = dict(R=5, D=1, Q0=8192, U0=1048576, Q1=8192, U1=1048576,
                  ncol0=8192, schedule="gray")
    middle, top = make_tower(**kw)
    projected = Program(D=middle.prog.D, U=middle.p.U)
    chain = [o for o in middle.prog.ops if o.kind == "ICHAIN"]
    for op in chain:
        assert middle.prog.ops_at(op.t0) == [op]
        projected.add(op)
    if skind is not None:
        source = next(o for o in top.prog.ops if o.kind == "SWEEP")
        inner_program = Program(D=top.prog.D, U=top.p.U)
        for kind in ((skind,) if isinstance(skind, str) else skind):
            inner_program.add(replace(source, skind=kind, param=1))
        middle.sched.ictx.prog_up = inner_program
    outer = make_system(Q=8192 if gray else 1024, U=1048576 if gray else 65536,
                        ncol=16, R=R, D=middle.prog.D,
                        Qs=middle.p.Q, Us=middle.p.U, Qss=top.p.Q, Uss=top.p.U,
                        with_tracks=True, full_registers=True,
                        schedule="gray" if gray else "compressed", nested_controls=True,
                        prog_up=projected, L_up=middle.L, trickle_up=middle.sched.trickle,
                        regwin_up=middle.sched.reg_window, inner_ctx=middle.sched.ictx)
    return outer, middle, top, chain


def scalar_carry(kind, cin, x, y, bit):
    if kind == "EQC": return int(cin and x == bit)
    if kind == "EQF": return int(cin and x == y)
    if kind == "ORF": return int(cin or x)
    if kind == "ANDF": return int(cin and x)
    if kind == "LTC": return int(x < bit or (x == bit and cin))
    if kind == "ADDC": return int(cin + x + bit >= 2)
    raise AssertionError(kind)


@pytest.mark.parametrize("kind", ["EQC", "EQF", "ORF", "ANDF", "LTC", "ADDC"])
def test_nested_ichain_independent_boolean_table(kind):
    outer, middle, top, chain = fixture(skind=kind)
    inner = middle.sched.ictx.prog_up.ops[0]
    op = next(o for o in chain if o.param == -1)
    phase = next(o for o in outer.prog.ops if o.kind == "IEVAL")
    cases = list(product((0, 1), repeat=4))  # cin, source, second source, constant bit
    engine = outer.np_engine()
    state = {k:v[:, :outer.p.Q].copy() for k,v in engine.initial(len(cases)).items()}
    state["age"][:] = phase.t0
    state["simage"][:] = op.t0
    state["simaddr"][:] = middle.L.b0 + middle.L.track_base + middle.T["SIG"] * 3 + 1
    state["simage2"][:] = inner.t0
    values = np.zeros((len(cases), outer.p.Q, outer.T.NT), np.uint8)
    n = outer.sched.ictx.n
    for b, (cin, x, y, bit) in enumerate(cases):
        # Const=1: bit at index zero is one and at index one is zero.
        state["simaddr2"][b] = inner.lo + 1 + (1 - bit)
        for track, value in ((n["S00"], x), (n["S01"], y), (n["S02"], cin)):
            values[b, :, track] = value
    state["trk"] = redistribute(values, 3)
    expected = engine.step(state)
    for b, (cin, x, y, bit) in enumerate(cases):
        for kk in (2, 3):
            writer = outer.sched.ictx.pos(middle.sched.ictx.n[f"CARRY{kk}"], 1)
            assert expected["trk"][b, writer, outer.T["HOLD"], 1] == scalar_carry(kind, cin, x, y, bit)
    gpu = outer.gpu_engine()
    packed = gpu.to_gpu(state)
    actual = gpu.to_np(gpu.step(packed, torch.empty_like(packed), 0))
    for name in expected:
        np.testing.assert_array_equal(actual[name], expected[name], err_msg=name)


def test_nested_ichain_complete_outer_period_actual_middle_program():
    from gacsca.interp import slot_of
    outer, middle, top, chain = fixture()
    by_kind = {o.skind:o for o in reversed(top.prog.ops) if o.kind == "SWEEP"}
    cases = [(op, inner, c, kk) for op in chain for inner in by_kind.values()
             for c in (-1, 0, 1) for kk in (2, 3) if -kk < op.param - c < 0]
    B, L = len(cases), outer.p.ncol
    state = {k:np.zeros((B, L), np.int32) for k in
             ("addr", "age", "f1", "f2", "wf1", "wf2", "simage", "simaddr")}
    rng = np.random.default_rng(1040)
    values = rng.integers(0, 2, (B, L, middle.T.NT), dtype=np.uint8)
    n = middle.sched.ictx.n
    for b, (op, inner, c, kk) in enumerate(cases):
        state["age"][b] = op.t0
        state["addr"][b] = (middle.L.b0 + middle.L.track_base + middle.T["SIG"] * 3 + 1 + c + np.arange(L) - 7) % middle.p.Q
        state["simage"][b] = inner.t0
        # At target seven, constant bit index is zero.
        state["simaddr"][b] = (inner.lo - op.param) % top.p.Q
        bit = inner.param & 1
        cin, x, y = next((ci, x, y) for ci, x, y in product((0, 1), repeat=3)
                         if scalar_carry(inner.skind, ci, x, y, bit) != ci)
        i = slot_of(top.prog.ops_at(inner.t0), top.prog.ops_at(inner.t0).index(inner))
        values[b, :, n[f"S{i}0"]] = x
        values[b, :, n[f"S{i}1"]] = y
        values[b, :, n[f"CARRY{kk}"]] = cin
    state["trk"] = redistribute(values, 3)
    state["trk"][:, ::3, :, 0] ^= rng.integers(0, 2, state["trk"][:, ::3, :, 0].shape, dtype=np.uint8)
    state["simage"][:, 7] = top.p.U - 1
    direct = middle.np_engine()
    expected = direct.step(state)
    neutral = middle.np_engine()
    neutral.prog = Program(D=middle.prog.D, U=middle.prog.U)
    baseline = neutral.step(state)
    for b in range(B):
        assert np.any(expected["trk"][b] != baseline["trk"][b]), f"vacuous carry witness {b}"
    mgpu = middle.gpu_engine()
    packed = mgpu.to_gpu(state)
    actual = mgpu.to_np(mgpu.step(packed, torch.empty_like(packed), 0))
    for name in expected:
        np.testing.assert_array_equal(actual[name], expected[name], err_msg=f"middle.{name}")
    physical = outer.np_engine().initial(B, info_bits=encode_state_info(state, outer.L, outer.p.Q))
    for name in ("simage", "simaddr", "simage2", "simaddr2"):
        physical[name][:] = 65535
    gpu = outer.gpu_engine()
    runner = CleanGraphRunner(gpu, gpu.to_gpu(physical))
    del physical
    runner.run(outer.p.U)
    decoded = decode_state_info(gpu.info_bits(runner.state).cpu().numpy(), outer.L, outer.p.Q)
    for name in expected:
        np.testing.assert_array_equal(decoded[name], expected[name], err_msg=f"outer.{name}")


def test_nested_ichain_concurrent_sweeps_use_last_eligible_operands():
    outer, middle, top, chain = fixture(skind=("ORF", "ANDF"))
    op = next(o for o in chain if o.param == -1)
    inner = middle.sched.ictx.prog_up.ops[0]
    inner.dst = top.T["HOLD"]
    middle.sched.ictx.prog_up.ops[1].dst = top.T["INFO"]
    engine = middle.np_engine()
    state = {k:v[:, :outer.p.ncol].copy() for k,v in engine.initial(2).items()}
    state["age"][:] = op.t0
    for b, target in enumerate((middle.T["SIG"], middle.T["HOLD"])):
        state["addr"][b] = (middle.L.b0 + middle.L.track_base + target * 3 + 1 + np.arange(outer.p.ncol) - 7) % middle.p.Q
    state["simage"][:] = inner.t0
    state["simaddr"][:] = inner.lo + 1
    n = middle.sched.ictx.n
    values = np.zeros((2, outer.p.ncol, middle.T.NT), np.uint8)
    values[..., n["S00"]] = 1  # first ORF -> 1
    values[..., n["S10"]] = 0  # last ANDF -> 0, not the earlier operand
    values[..., n["CARRY2"]] = 1
    values[..., n["CARRY3"]] = 1
    state["trk"] = redistribute(values, 3)
    expected = engine.step(state)
    for kk in (2, 3):
        assert expected["trk"][0, 7, n[f"CARRY{kk}"], 1] == 0
        assert expected["trk"][1, 7, n[f"CARRY{kk}"], 1] == 1  # later instruction cannot write HOLD
    # Removing the final instruction demonstrably changes the target output.
    first = Program(D=top.prog.D, U=top.p.U)
    first.add(inner)
    from copy import copy
    first_engine = middle.np_engine()
    first_engine.ictx = copy(first_engine.ictx)
    first_engine.ictx.prog_up = first
    earlier = first_engine.step(state)
    for kk in (2, 3):
        assert earlier["trk"][0, 7, n[f"CARRY{kk}"], 1] == 1
    physical = outer.np_engine().initial(2, info_bits=encode_state_info(state, outer.L, outer.p.Q))
    gpu = outer.gpu_engine()
    runner = CleanGraphRunner(gpu, gpu.to_gpu(physical))
    runner.run(outer.p.U)
    decoded = decode_state_info(gpu.info_bits(runner.state).cpu().numpy(), outer.L, outer.p.Q)
    for name in expected:
        np.testing.assert_array_equal(decoded[name], expected[name], err_msg=name)


@pytest.mark.parametrize("gray", [False, True])
def test_nested_ichain_speed_one_is_exact_noop(gray):
    """D=1 has no intermediate carry cells, even for arbitrary faulty inputs."""
    outer, middle, top, chain = fixture(5, gray=gray)
    B, L = len(chain), outer.p.ncol
    state = {k:np.zeros((B, L), np.int32) for k in
             ("addr", "age", "f1", "f2", "wf1", "wf2", "simage", "simaddr")}
    state["age"][:] = np.array([o.t0 for o in chain])[:, None]
    state["addr"][:] = (middle.L.b0 + middle.L.track_base + np.arange(L)) % middle.p.Q
    sweeps = [o for o in top.prog.ops if o.kind == "SWEEP"]
    state["simage"][:] = np.array([sweeps[b].t0 for b in range(B)])[:, None]
    rng = np.random.default_rng(1050)
    state["simaddr"][:] = rng.integers(0, 1 << (20 if gray else 16), (B, L), dtype=np.int32)
    state["simage"][:, 7] = (1 << (20 if gray else 16)) - 1
    state["trk"] = rng.integers(0, 2, (B, L, middle.T.NT, 5), dtype=np.uint8)
    expected = middle.np_engine().step(state)
    neutral = middle.np_engine()
    neutral.prog = Program(D=1, U=middle.p.U)
    local = neutral.step(state)
    for name in expected:
        np.testing.assert_array_equal(expected[name], local[name], err_msg=f"D1 no-op.{name}")
    bits = encode_state_info(state, outer.L, outer.p.Q)
    physical = outer.np_engine().initial(B, info_bits=bits)
    if gray:
        physical["age"][:] = 7 * outer.p.U // 8
        values = np.zeros((B, outer.p.L, outer.T.NT), np.uint8)
        values[..., outer.T["INFO"]] = bits
        for bank in "ABC":
            for j in range(-5, 6):
                values[..., outer.T.arg(j, bank)] = np.roll(bits, -j * outer.p.Q, axis=1)
        physical["trk"] = redistribute(values, 5)
        del values
    for name in ("simage", "simaddr", "simage2", "simaddr2"):
        physical[name][:] = (1 << (20 if gray else 16)) - 1
    gpu = outer.gpu_engine()
    runner = CleanGraphRunner(gpu, gpu.to_gpu(physical))
    del physical
    runner.run(outer.sched.compute_end - 7 * outer.p.U // 8 if gray else outer.p.U)
    if gray:
        from experiments.gray_protocol import track_bits
        actual_bits = track_bits(gpu, runner.state, outer.T["HOLD"])
    else:
        actual_bits = gpu.info_bits(runner.state).cpu().numpy()
    decoded = decode_state_info(actual_bits, outer.L, outer.p.Q)
    for name in expected:
        np.testing.assert_array_equal(decoded[name], expected[name], err_msg=name)


def test_nested_ichain_rejects_unavailable_inner_scratch_slot():
    with pytest.raises(ValueError, match="concurrent inner value instructions"):
        fixture(skind=("ORF", "ANDF", "EQF", "LTC"))


@pytest.mark.parametrize("field", ["simage2", "simaddr2"])
def test_nested_ichain_isolated_physical_control_fault_is_contained(field):
    outer, middle, top, chain = fixture(skind="EQC")
    inner = middle.sched.ictx.prog_up.ops[0]
    op = next(o for o in chain if o.param == -1)
    phase = next(o for o in outer.prog.ops if o.kind == "IEVAL")
    engine = outer.np_engine()
    state = {k:v[:, :outer.p.Q].copy() for k,v in engine.initial(1).items()}
    state["age"][:] = phase.t0
    state["simage"][:] = op.t0
    state["simaddr"][:] = middle.L.b0 + middle.L.track_base + middle.T["SIG"] * 3 + 1
    state["simage2"][:] = inner.t0
    state["simaddr2"][:] = inner.lo + 1
    values = np.zeros((1, outer.p.Q, outer.T.NT), np.uint8)
    values[..., outer.sched.ictx.n["S00"]] = 1
    values[..., outer.sched.ictx.n["S02"]] = 1
    state["trk"] = redistribute(values, 3)
    writer = outer.sched.ictx.pos(middle.sched.ictx.n["CARRY2"], 1)
    damaged = {k:v.copy() for k,v in state.items()}
    damaged[field][0, writer] = 65535 if field == "simage2" else inner.lo + 2
    clean, fault = engine.step(state), engine.step(damaged)
    np.testing.assert_array_equal(np.flatnonzero(np.any(clean["trk"] != fault["trk"], axis=(0, 2, 3))), [writer])
    clean2, fault2 = engine.step(clean), engine.step(fault)
    for name in clean2:
        np.testing.assert_array_equal(fault2[name], clean2[name], err_msg=name)
    gpu = outer.gpu_engine()
    packed = gpu.to_gpu(damaged)
    actual = gpu.to_np(gpu.step(packed, torch.empty_like(packed), 0))
    for name in fault:
        np.testing.assert_array_equal(actual[name], fault[name], err_msg=name)


@pytest.mark.parametrize("offset,kk,guard,write", [
    (-3, 3, "valid", False), (-2, 3, "valid", True),
    (-2, 2, "valid", False), (-1, 2, "valid", True),
    (-1, 3, "valid", True), (0, 2, "valid", False),
    (-1, 2, "middle_range", False), (-1, 2, "geometry", False),
    (-1, 2, "clock", False), (-1, 2, "wide_address", True),
])
def test_nested_ichain_strict_intermediate_cell_and_control_guards(offset, kk, guard, write):
    outer, middle, top, chain = fixture(skind="ORF")
    inner = middle.sched.ictx.prog_up.ops[0]
    op = next(o for o in chain if o.param == offset)
    phase = next(o for o in outer.prog.ops if o.kind == "IEVAL")
    a1 = middle.L.b0 + middle.L.track_base + middle.T["SIG"] * 3 + 1
    if guard == "middle_range":
        op.lo = a1 + 1
    if guard == "geometry":
        a1 = middle.L.b0 + middle.L.track_base - 1
    engine = outer.np_engine()
    state = {k:v[:, :outer.p.Q].copy() for k,v in engine.initial(1).items()}
    state["age"][:] = phase.t0
    state["simage"][:] = op.t0
    state["simaddr"][:] = a1
    state["simage2"][:] = 65535 if guard == "clock" else inner.t0
    state["simaddr2"][:] = 65535 if guard == "wide_address" else inner.lo + 1
    values = np.zeros((1, outer.p.Q, outer.T.NT), np.uint8)
    values[..., outer.T["HOLD"]] = 1
    state["trk"] = redistribute(values, 3)
    expected = engine.step(state)
    writer = outer.sched.ictx.pos(middle.sched.ictx.n[f"CARRY{kk}"], 1)
    assert expected["trk"][0, writer, outer.T["HOLD"], 1] == int(not write)
    gpu = outer.gpu_engine()
    packed = gpu.to_gpu(state)
    actual = gpu.to_np(gpu.step(packed, torch.empty_like(packed), 0))
    for name in expected:
        np.testing.assert_array_equal(actual[name], expected[name], err_msg=name)
