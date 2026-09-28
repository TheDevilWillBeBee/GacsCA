"""Nested mail-latch closure; a complete third simulation link still needs IEVAL."""
import numpy as np
import pytest
import torch

from gacsca.build import make_tower, make_system
from gacsca.engine_np import redistribute
from gacsca.gpu_engine import CleanGraphRunner
from gacsca.hierarchy import encode_state_info, decode_state_info
from gacsca.microcode import Program, Op


def fixture(R=3, gray=False, D=None):
    kw = dict(R=5, D=1, Q0=512, U0=32768, U1=8192) if R == 5 else {}
    if R == 3 and D == 2:
        kw = dict(R=3, D=2, Q0=512, U0=32768, U1=8192)
    if gray:
        kw = dict(R=5, D=1, Q0=8192, U0=1048576, Q1=8192, U1=1048576,
                  ncol0=8192, schedule="gray")
    middle, top = make_tower(**kw)
    projected = Program(D=middle.prog.D, U=middle.p.U)
    latch = [o for o in middle.prog.ops if o.kind == "ILATCH"]
    needed = {id(o) for op in latch for o in middle.prog.ops_at(op.t0)}
    for op in middle.prog.ops:
        if id(op) in needed:
            assert op.kind in ("ILATCH", "RSHIFT")
            projected.add(op)
    outer = make_system(Q=8192 if gray else 1024, U=1048576 if gray else 65536,
                        ncol=16, R=R, D=middle.prog.D,
                        Qs=middle.p.Q, Us=middle.p.U, Qss=top.p.Q, Uss=top.p.U,
                        with_tracks=True, full_registers=True,
                        schedule="gray" if gray else "compressed", nested_controls=True,
                        prog_up=projected, L_up=middle.L, trickle_up=middle.sched.trickle,
                        regwin_up=middle.sched.reg_window, inner_ctx=middle.sched.ictx)
    return outer, middle, top, latch


def input_witnesses(outer, middle, top, latch):
    # An actual MOV phase; each middle copy slot latches its own source into S00.
    R, h, D = middle.T.R, middle.T.R // 2, middle.prog.D
    cases = []
    from gacsca.interp import slot_of
    for direction in (-1, 1):
        inner = next(o for o in top.prog.ops if o.kind == "MOV" and not o.param2
                     and (o.dst - o.src) * direction > 0)
        i = slot_of(top.prog.ops_at(inner.t0), top.prog.ops_at(inner.t0).index(inner))
        for c2 in range(-h, h + 1):
            a1 = middle.sched.ictx.pos(inner.dst, c2 + h)
            X = middle.sched.ictx.pos(inner.src, h)
            op = next(o for o in latch if o.param == c2 and o.param2 == direction)
            tau = abs(a1 - X) // D
            assert op.t0 + tau < op.t1
            relative = -direction * (abs(a1 - X) % D)
            cases.append((op, tau, a1, inner, i, relative))
    B, L = len(cases), outer.p.ncol
    state = {k:np.zeros((B, L), np.int32) for k in
             ("addr", "age", "f1", "f2", "wf1", "wf2", "simage", "simaddr")}
    for b, (op, tau, a1, inner, _, _) in enumerate(cases):
        state["age"][b] = op.t0 + tau
        state["addr"][b] = (a1 + np.arange(L) - 7) % middle.p.Q
        state["simage"][b] = inner.t0
        state["simaddr"][b] = inner.lo
    rng = np.random.default_rng(1100 + R)
    V = rng.integers(0, 2, (B, L, middle.T.NT), dtype=np.uint8)
    V[..., middle.sched.ictx.n["BUS"]] = 0
    for b, (_, _, _, _, i, relative) in enumerate(cases):
        V[b, 7 + relative, middle.sched.ictx.n["BUS"]] = 1
        V[b, :, middle.sched.ictx.n[f"S{i}0"]] = 0
    state["trk"] = redistribute(V, R)
    state["trk"][:, ::3, :, 0] ^= rng.integers(0, 2, state["trk"][:, ::3, :, 0].shape, dtype=np.uint8)
    # One input control fault: its repaired output is NOT the latch selector.
    state["simage"][:, 7] = top.p.U - 2
    return state


@pytest.mark.parametrize("R,D", [(3, 3), (3, 2), (5, 1)])
def test_nested_ilatch_complete_outer_period(R, D):
    outer, middle, top, latch = fixture(R, D=D)
    state = input_witnesses(outer, middle, top, latch)
    expected = middle.np_engine().step(state)
    # Removing only ILATCH (not its concurrent RSHIFT) must change output.
    neutral = middle.np_engine()
    neutral.prog = Program(D=middle.prog.D, U=middle.p.U)
    for op in middle.prog.ops:
        if op.kind != "ILATCH": neutral.prog.add(op)
    baseline = neutral.step(state)
    B = state["addr"].shape[0]
    for b in range(B):
        assert np.any(expected["trk"][b] != baseline["trk"][b]), f"vacuous latch case {b}"
    mgpu = middle.gpu_engine()
    packed = mgpu.to_gpu(state)
    actual = mgpu.to_np(mgpu.step(packed, torch.empty_like(packed), 0))
    for name in expected:
        np.testing.assert_array_equal(actual[name], expected[name], err_msg=f"middle.{name}")
    physical = outer.np_engine().initial(B, info_bits=encode_state_info(state, outer.L, outer.p.Q))
    for name in ("simage", "simaddr", "simage2", "simaddr2"): physical[name][:] = 65535
    gpu = outer.gpu_engine()
    runner = CleanGraphRunner(gpu, gpu.to_gpu(physical))
    del physical
    runner.run(outer.p.U)
    decoded = decode_state_info(gpu.info_bits(runner.state).cpu().numpy(), outer.L, outer.p.Q)
    for name in expected:
        np.testing.assert_array_equal(decoded[name], expected[name], err_msg=f"outer.{name}")


def operand_cases(middle, top, latch):
    """Independently enumerate the operands, their writer and source positions."""
    from gacsca.interp import slot_of
    J, T, R = middle.sched.ictx, top.T, middle.T.R
    h = R // 2
    result = []
    selected = [next(o for o in top.prog.ops if o.kind == kind and (kind != "SWEEP" or o.src2 is not None))
                for kind in ("MOV", "BITOP", "SHIFT", "RSHIFT", "SWEEP", "BCAST_INIT", "BCAST")]
    selected += [o for o in top.prog.ops_at(selected[0].t0) if o.kind == "MOV" and o is not selected[0]]
    selected.append(next(o for o in top.prog.ops if o.kind == "BCAST" and o.param == 1))
    for op2 in selected:
        kind = op2.kind
        active = top.prog.ops_at(op2.t0)
        i = slot_of(active, active.index(op2))
        roles = []
        if kind in ("MOV", "BITOP", "BCAST_INIT"):
            roles = [(0, src, J.n[f"S{i}{j}"]) for j, src in enumerate((op2.src, op2.src2, op2.src3)) if src is not None]
        elif kind in ("SHIFT", "RSHIFT"):
            roles = [(-op2.param, op2.src, J.n[f"SHSRC{i}"])]
        elif kind == "SWEEP":
            roles = [(0, op2.src, J.n[f"S{i}0"]), (0, op2.src2, J.n[f"S{i}1"]), (0, T["SIG"], J.n[f"S{i}2"])]
            for k in range(1, top.prog.D + 1):
                roles += [(-k, T["SIG"], J.n[f"SIG{k}"]), (-k, T["ACC"], J.n[f"CARRY{k}"])]
            for k in range(1, top.prog.D):
                roles += [(-k, op2.src, J.n[f"S{i}0"]), (-k, op2.src2, J.n[f"S{i}1"])]
        else:
            roles = [(0, T["SIG"], J.n[f"S{i}2"])]
            for k in range(1, top.prog.D + 1):
                sh = k if op2.param <= 0 else -k
                roles += [(sh, T["SIG"], J.n[f"SIG{k}"]), (sh, op2.dst, J.n[f"CARRY{k}"])]
        target = T["SIG"] if kind in ("SWEEP", "BCAST") else op2.dst
        for j, (offset, source, dest) in enumerate(roles):
            c2 = j % R - h
            a1, X = J.pos(target, c2 + h), J.pos(source, h)
            direction = 1 if a1 >= X else -1
            op1 = next(o for o in latch if o.param == c2 + offset and o.param2 == direction)
            distance = abs(a1 - X)
            g1 = op1.t0 + distance // middle.prog.D
            assert g1 < op1.t1
            relative = -direction * (distance % middle.prog.D)
            result.append((kind, g1, a1, op2.t0, op2.lo, dest, relative))
    return result


def local_cases(outer, middle, cases, phase, expected_bit=1):
    from gacsca.interp import slot_of
    engine = outer.np_engine()
    state = {k:v[:, :outer.p.Q].copy() for k,v in engine.initial(len(cases)).items()}
    values = np.zeros((len(cases), outer.p.Q, outer.T.NT), np.uint8)
    checks = []
    for b, (_, g1, a1, g2, sa2, dest, relative) in enumerate(cases):
        active = middle.prog.ops_at(g1)
        index = next(i for i,o in enumerate(active) if o.kind == "ILATCH")
        slot = slot_of(active, index)
        writer = outer.sched.ictx.pos(dest, outer.T.R // 2)
        if phase == "IEVAL":
            op = next(o for o in outer.prog.ops if o.kind == phase and o.param == index)
            clock, source, target = op.t0, outer.sched.ictx.n[f"S{slot}0"], outer.T["HOLD"]
        else:
            X = outer.sched.ictx.pos(middle.sched.ictx.n["BUS"], outer.T.R // 2)
            direction = 1 if writer >= X else -1
            op = next(o for o in outer.prog.ops if o.kind == phase and o.param == relative and o.param2 == direction)
            clock = op.t0 + abs(writer - X) // outer.prog.D
            assert clock < op.t1
            source, target = outer.sched.ictx.n["BUS"], outer.sched.ictx.n[f"S{slot}0"]
        state["age"][b] = clock
        state["simage"][b], state["simaddr"][b] = g1, a1
        state["simage2"][b], state["simaddr2"][b] = g2, sa2
        values[b, :, source] = 1
        checks.append((writer, target))
    state["trk"] = redistribute(values, outer.T.R)
    expected = engine.step(state)
    for b, (writer, target) in enumerate(checks):
        assert expected["trk"][b, writer, target, outer.T.R // 2] == expected_bit, (b, cases[b][0], phase)
    gpu = outer.gpu_engine()
    packed = gpu.to_gpu(state)
    actual = gpu.to_np(gpu.step(packed, torch.empty_like(packed), 0))
    for name in expected:
        np.testing.assert_array_equal(actual[name], expected[name], err_msg=f"{phase}.{name}")


@pytest.mark.parametrize("R,D", [(3, 3), (3, 2), (5, 1)])
@pytest.mark.parametrize("phase", ["ILATCH", "IEVAL"])
def test_nested_ilatch_every_emitted_operand_class(R, D, phase):
    outer, middle, top, latch = fixture(R, D=D)
    cases = operand_cases(middle, top, latch)
    assert {c[0] for c in cases} == {"MOV", "BITOP", "SHIFT", "RSHIFT", "SWEEP", "BCAST_INIT", "BCAST"}
    local_cases(outer, middle, cases, phase)


@pytest.mark.parametrize("R,D", [(3, 3), (3, 2), (5, 1)])
@pytest.mark.parametrize("phase", ["ILATCH", "IEVAL"])
def test_nested_ilatch_workspace_request_at_empty_inner_age(R, D, phase):
    outer, middle, top, latch = fixture(R, D=D)
    cases = []
    J = middle.sched.ictx
    for field, address in (("WF1", top.p.Q - 3), ("WF2", 3)):
        a1 = middle.L.frange(field)[0]
        X = J.pos(top.T["INFO"], R // 2)
        direction = 1 if a1 >= X else -1
        op = next(o for o in latch if o.param == 0 and o.param2 == direction)
        distance = abs(a1 - X)
        g1 = op.t0 + distance // middle.prog.D
        assert g1 < op.t1 and not top.prog.ops_at(65535)
        cases.append((field, g1, a1, 65535, address, J.n["WFB"], -direction * (distance % middle.prog.D)))
    local_cases(outer, middle, cases, phase)


@pytest.mark.parametrize("R,D", [(3, 3), (3, 2), (5, 1)])
@pytest.mark.parametrize("phase", ["ILATCH", "IEVAL"])
def test_nested_ilatch_register_bit_requests(R, D, phase):
    outer, middle, top, latch = fixture(R, D=D)
    J = middle.sched.ictx
    program = Program(D=top.prog.D, U=top.p.U)
    cases = []
    for direction in (-1, 1):
        t0 = 2 if direction < 0 else 32
        op2 = Op("BUSLATCH_INT", t0, t0 + 8, 0, top.p.Q, src=top.T["T0"], param2=direction)
        program.add(op2)
        for field, source_field in (("SIMAGE", "AGE"), ("SIMADDR", "ADDR")):
            lo, hi = middle.L.frange(field)
            slo, shi = top.L.frange(source_field)
            for bit in (0, min(hi - lo, shi - slo) - 1):
                for j2 in range(top.prog.D):
                    sa2 = slo + bit + direction * (top.prog.D + j2)
                    assert 0 <= sa2 < top.p.Q
                    a1, X = lo + bit, J.pos(op2.src, R // 2)
                    dir1 = 1 if a1 >= X else -1
                    op1 = next(o for o in latch if o.param == -direction * j2 and o.param2 == dir1)
                    distance = abs(a1 - X)
                    g1 = op1.t0 + distance // middle.prog.D
                    assert g1 < op1.t1
                    cases.append((field, g1, a1, t0 + 1, sa2, J.n["BLB"], -dir1 * (distance % middle.prog.D)))
    J.prog_up = program
    local_cases(outer, middle, cases, phase)


def test_nested_ilatch_gray_stage_five():
    from experiments.gray_protocol import track_bits
    outer, middle, top, latch = fixture(5, gray=True)
    state = input_witnesses(outer, middle, top, latch)
    expected = middle.np_engine().step(state)
    B = state["addr"].shape[0]
    assert outer.L.K == 512 and outer.prog.nested_register_bits == 20
    bits = encode_state_info(state, outer.L, outer.p.Q)
    physical = outer.np_engine().initial(B)
    physical["age"][:] = start = 7 * outer.p.U // 8
    for name in ("simage", "simaddr", "simage2", "simaddr2"):
        physical[name][:] = (1 << 20) - 1
    values = np.zeros((B, outer.p.L, outer.T.NT), np.uint8)
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
    for index, field in enumerate(("simage", "simaddr")):
        raw_cache = runner.state[..., gpu.nested_base + index].cpu().numpy()
        np.testing.assert_array_equal(raw_cache, np.repeat(state[field], outer.p.Q, axis=1))


@pytest.mark.parametrize("R", [3, 5])
@pytest.mark.parametrize("field", ["simage2", "simaddr2"])
def test_nested_ilatch_control_fault_remains_holder_local(R, field):
    from gacsca.interp import slot_of
    outer, middle, top, latch = fixture(R)
    if field == "simage2":
        _, g1, a1, g2, sa2, dest, _ = operand_cases(middle, top, latch)[0]
        damaged_value = 65535
    else:
        J = middle.sched.ictx
        a1 = middle.L.frange("WF1")[0]
        X = J.pos(top.T["INFO"], R // 2)
        direction = 1 if a1 >= X else -1
        op = next(o for o in latch if o.param == 0 and o.param2 == direction)
        g1, g2, sa2 = op.t0 + abs(a1 - X) // middle.prog.D, 65535, top.p.Q - 3
        dest, damaged_value = J.n["WFB"], sa2 + 1
    active = middle.prog.ops_at(g1)
    index = next(i for i,o in enumerate(active) if o.kind == "ILATCH")
    slot = slot_of(active, index)
    phase = next(o for o in outer.prog.ops if o.kind == "IEVAL" and o.param == index)
    engine = outer.np_engine()
    state = {k:v[:, :outer.p.Q].copy() for k,v in engine.initial(1).items()}
    for name, value in (("age", phase.t0), ("simage", g1), ("simaddr", a1), ("simage2", g2), ("simaddr2", sa2)):
        state[name][:] = value
    V = np.zeros((1, outer.p.Q, outer.T.NT), np.uint8)
    V[..., outer.sched.ictx.n[f"S{slot}0"]] = 1
    state["trk"] = redistribute(V, R)
    writer = outer.sched.ictx.pos(dest, R // 2)
    damaged = {k:v.copy() for k,v in state.items()}
    damaged[field][0, writer] = damaged_value
    clean, fault = engine.step(state), engine.step(damaged)
    assert clean["trk"][0, writer, outer.T["HOLD"], R // 2] == 1
    assert fault["trk"][0, writer, outer.T["HOLD"], R // 2] == 0
    np.testing.assert_array_equal(np.flatnonzero(np.any(clean["trk"] != fault["trk"], axis=(0, 2, 3))), [writer])
    clean2, fault2 = engine.step(clean), engine.step(fault)
    for name in clean2:
        np.testing.assert_array_equal(fault2[name], clean2[name], err_msg=name)
    gpu = outer.gpu_engine()
    packed = gpu.to_gpu(damaged)
    actual = gpu.to_np(gpu.step(packed, torch.empty_like(packed), 0))
    for name in fault:
        np.testing.assert_array_equal(actual[name], fault[name], err_msg=name)


@pytest.mark.parametrize("R", [3, 5])
@pytest.mark.parametrize("phase", ["ILATCH", "IEVAL"])
def test_nested_ilatch_initialization_operand_requests(R, phase):
    outer, middle, top, latch = fixture(R)
    J, h = middle.sched.ictx, R // 2
    program = Program(D=top.prog.D, U=top.p.U)
    cases = []
    for i, copy in enumerate(range(-h, h + 1)):
        routed = int(abs(copy) > top.prog.D)
        op2 = Op("IINIT", 2 + i, 3 + i, 0, top.p.Q,
                 dst=top.T["HOLD"], src=top.T["T0"], param=copy, param2=routed)
        program.add(op2)
        a1, X = J.pos(op2.dst, copy + h), J.pos(op2.src, h)
        direction = 1 if a1 >= X else -1
        offset = copy + (0 if routed else -copy)
        op1 = next(o for o in latch if o.param == offset and o.param2 == direction)
        distance = abs(a1 - X)
        g1 = op1.t0 + distance // middle.prog.D
        assert g1 < op1.t1
        cases.append(("IINIT", g1, a1, op2.t0, 0, J.n["S00"], -direction * (distance % middle.prog.D)))
    J.prog_up = program
    local_cases(outer, middle, cases, phase)


@pytest.mark.parametrize("R", [3, 5])
@pytest.mark.parametrize("phase", ["ILATCH", "IEVAL"])
@pytest.mark.parametrize("guard", ["time", "middle_range", "inner_clock", "operand_pass"])
def test_nested_ilatch_guard_prevents_write(R, phase, guard):
    outer, middle, top, latch = fixture(R)
    kind, g1, a1, g2, sa2, dest, relative = operand_cases(middle, top, latch)[0]
    op1 = next(o for o in middle.prog.ops_at(g1) if o.kind == "ILATCH")
    if guard == "time": g1 += 1
    if guard == "middle_range": op1.lo = a1 + 1
    if guard == "inner_clock": g2 = 65535
    if guard == "operand_pass": op1.param += 1
    local_cases(outer, middle, [(kind, g1, a1, g2, sa2, dest, relative)], phase, expected_bit=0)
