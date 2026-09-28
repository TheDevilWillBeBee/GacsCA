"""Nested register-load component; this does not enable a complete third link."""
import numpy as np
import pytest
import torch

from gacsca.build import make_tower, make_system
from gacsca.gpu_engine import CleanGraphRunner
from gacsca.hierarchy import encode_state_info, decode_state_info
from gacsca.microcode import Program


def bus_fixture(R, gray=False):
    kw = dict(R=5, D=1, Q0=512, U0=32768, U1=8192) if R == 5 else {}
    if gray:
        assert R == 5
        kw = dict(Q0=8192, U0=1048576, Q1=8192, U1=1048576,
                  ncol0=8192, R=5, D=1, schedule="gray")
    middle, top = make_tower(**kw)
    load_ops = [op for op in middle.prog.ops if op.kind == "BUSLATCH_INT"]
    assert len(load_ops) == 2 and {op.param2 for op in load_ops} == {-1, 1}
    ages = [op.t0 + tau for op in load_ops for tau in (0, 2)]
    projected = Program(D=middle.prog.D, U=middle.p.U)
    reachable = {id(op) for age in ages for g in (age, age + 1) for op in middle.prog.ops_at(g)}
    for op in middle.prog.ops:
        if id(op) in reachable:
            assert op.kind in ("BUSLATCH_INT", "RSHIFT")
            projected.add(op)
    outer = make_system(Q=8192 if gray else 1024, U=1048576 if gray else 65536,
                        schedule="gray" if gray else "compressed", ncol=64, R=R, D=middle.prog.D,
                        Qs=middle.p.Q, Us=middle.p.U, Qss=top.p.Q, Uss=top.p.U,
                        with_tracks=True, full_registers=True, prog_up=projected,
                        L_up=middle.L, trickle_up=middle.sched.trickle,
                        regwin_up=middle.sched.reg_window)
    return outer, middle, load_ops, ages


@pytest.mark.parametrize("R", [3, 5])
def test_nested_register_load_full_period(R):
    outer, middle, load_ops, ages = bus_fixture(R)
    B = len(ages)
    direct = middle.np_engine()
    state = {k:v[:, :outer.p.ncol].copy() for k,v in direct.initial(B).items()}
    state["age"][:] = np.array(ages)[:, None]
    state["addr"][:] = middle.L.frange("ADDR")[0] - 2 + np.arange(outer.p.ncol)
    rng = np.random.default_rng(960 + R)
    state["trk"][:] = rng.integers(0, 2, state["trk"].shape, dtype=np.uint8)
    for name in ("simage", "simaddr"):
        state[name][:] = rng.integers(0, 65536, state[name].shape, dtype=np.int32)
    state["addr"][:, 7] = 1
    state["age"][:, 9] += 1
    for age in np.unique(state["age"]):
        assert middle.prog.ops_at(age) == outer.sched.ictx.prog_up.ops_at(age)
    expected = direct.step(state)
    for name, field in (("simage", "AGE"), ("simaddr", "ADDR")):
        width = middle.L.fields[field][1]
        high = 65535 ^ ((1 << width) - 1)
        np.testing.assert_array_equal(expected[name] & high, state[name] & high)
    # Every direction/timing case must perform an observable register update.
    for b in range(B):
        assert any(np.any(expected[name][b] != state[name][b]) for name in ("simage", "simaddr"))
    mgpu = middle.gpu_engine()
    packed = mgpu.to_gpu(state)
    actual_direct = mgpu.to_np(mgpu.step(packed, torch.empty_like(packed), 0))
    for name in expected:
        np.testing.assert_array_equal(actual_direct[name], expected[name], err_msg=f"direct.{name}")
    physical = outer.np_engine().initial(B, info_bits=encode_state_info(state, outer.L, outer.p.Q))
    physical["simage"][:] = np.repeat(state["age"], outer.p.Q, axis=1)
    physical["simaddr"][:] = np.repeat(state["addr"], outer.p.Q, axis=1)
    gpu = outer.gpu_engine()
    runner = CleanGraphRunner(gpu, gpu.to_gpu(physical))
    del physical
    runner.run(outer.p.U)
    decoded = decode_state_info(gpu.info_bits(runner.state).cpu().numpy(), outer.L, outer.p.Q)
    for name in expected:
        np.testing.assert_array_equal(decoded[name], expected[name], err_msg=f"nested.{name}")


@pytest.mark.parametrize("R", [3, 5])
@pytest.mark.parametrize("phase", ["ILATCH", "IEVAL"])
@pytest.mark.parametrize("excluded", [False, True])
def test_nested_register_load_local_stages_and_address_guard(R, phase, excluded):
    from gacsca.engine_np import redistribute
    outer, middle, load_ops, _ = bus_fixture(R)
    upper_op = load_ops[0]
    addr = middle.L.frange("AGE")[0]
    if excluded:
        # Shared instruction object: both references now have the same narrow
        # address guard. The bit timing still matches, but the write must not.
        upper_op.lo = addr + 1
    context = outer.sched.ictx
    writer = outer.L.frange("SIMAGE")[0]
    if phase == "ILATCH":
        op = next(o for o in outer.prog.ops if o.kind == phase and o.param == 0 and o.param2 == -1)
        source = context.pos(upper_op.src, R // 2)
        tau = (source - writer) // outer.prog.D
        assert 0 <= tau < op.t1 - op.t0
        clock = op.t0 + tau
        source_track, target_track = context.n["BUS"], context.n["BLB"]
    else:
        slot = middle.prog.ops_at(upper_op.t0).index(upper_op)
        op = next(o for o in outer.prog.ops if o.kind == phase and o.param == slot)
        clock = op.t0
        source_track, target_track = context.n["BLB"], outer.T["HOLD"]
    engine = outer.np_engine()
    state = engine.initial(1)
    state["age"][:] = clock
    state["simage"][:] = upper_op.t0
    state["simaddr"][:] = addr
    values = np.zeros((1, outer.p.L, outer.T.NT), dtype=np.uint8)
    values[..., source_track] = 1
    state["trk"] = redistribute(values, R)
    expected = engine.step(state)
    assert expected["trk"][0, writer, target_track, R // 2] == int(not excluded)
    gpu = outer.gpu_engine()
    packed = gpu.to_gpu(state)
    actual = gpu.to_np(gpu.step(packed, torch.empty_like(packed), 0))
    for name in expected:
        np.testing.assert_array_equal(actual[name], expected[name], err_msg=f"{phase}.{name}")


def test_nested_register_load_gray_stage_five():
    """Full Gray stage five, four load phases, arbitrary 20-bit middle registers."""
    from gacsca.engine_np import redistribute
    from experiments.gray_protocol import track_bits
    outer, middle, _, ages = bus_fixture(5, gray=True)
    B = len(ages)
    assert outer.L.K == 512 and outer.L.fields["SIMAGE"][1] == 20
    state = {k:np.zeros((B, outer.p.ncol), dtype=np.int32) for k in
             ("addr", "age", "f1", "f2", "wf1", "wf2", "simage", "simaddr")}
    state["age"][:] = np.array(ages)[:, None]
    state["addr"][:] = middle.L.frange("ADDR")[0] - 2 + np.arange(outer.p.ncol)
    rng = np.random.default_rng(970)
    state["trk"] = rng.integers(0, 2, (B, outer.p.ncol, middle.T.NT, 5), dtype=np.uint8)
    for name in ("simage", "simaddr"):
        state[name][:] = rng.integers(0, 1 << 20, state[name].shape, dtype=np.int32)
    state["addr"][:, 7] = 1
    state["age"][:, 9] += 1
    for age in np.unique(state["age"]):
        assert middle.prog.ops_at(age) == outer.sched.ictx.prog_up.ops_at(age)
    expected = middle.np_engine().step(state)
    for b in range(B):
        assert any(np.any(expected[name][b] != state[name][b]) for name in ("simage", "simaddr"))
    bits = encode_state_info(state, outer.L, outer.p.Q)
    physical = outer.np_engine().initial(B)
    physical["age"][:] = 7 * outer.p.U // 8
    physical["simage"][:] = (1 << 20) - 1
    physical["simaddr"][:] = (1 << 20) - 1
    values = np.zeros((B, outer.p.L, outer.T.NT), dtype=np.uint8)
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
