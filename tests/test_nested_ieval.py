"""Nested evaluation closure: actual middle transitions, not host-side oracles."""
import numpy as np
import pytest
import torch
from dataclasses import replace
from itertools import product

from gacsca.build import make_tower, make_system
from gacsca.engine_np import redistribute
from gacsca.gpu_engine import CleanGraphRunner
from gacsca.hierarchy import encode_state_info, decode_state_info
from gacsca.microcode import Program


def local_evaluations(outer, middle, phase, inner, cases):
    """Independent expected bits; cases = (middle Address, raw Address2, scratch, old, new)."""
    engine = outer.np_engine()
    B, R = len(cases), outer.T.R
    state = {k:np.repeat(v[:, :outer.p.Q], B, axis=0) for k,v in engine.initial(1).items()}
    state["age"][:] = next(o.t0 for o in outer.prog.ops if o.kind == "IEVAL" and o.param == 0)
    state["simage"][:] = phase.t0
    state["simage2"][:] = inner.t0
    V = np.zeros((B, outer.p.Q, outer.T.NT), np.uint8)
    writer = outer.sched.ictx.pos(middle.T["HOLD"], R // 2)
    for b, (address, raw, scratch, old, _) in enumerate(cases):
        state["simaddr"][b] = address
        state["simaddr2"][b] = raw
        V[b, :, outer.T["HOLD"]] = old
        for name, value in scratch.items(): V[b, :, outer.sched.ictx.n[name]] = value
    state["trk"] = redistribute(V, R)
    expected = engine.step(state)
    for b, case in enumerate(cases):
        assert expected["trk"][b, writer, outer.T["HOLD"], R // 2] == case[-1], (b, case)
    gpu = outer.gpu_engine()
    packed = gpu.to_gpu(state)
    actual = gpu.to_np(gpu.step(packed, torch.empty_like(packed), 0))
    for name in expected:
        np.testing.assert_array_equal(actual[name], expected[name], err_msg=name)


def single_inner(middle, op):
    p = Program(D=middle.sched.ictx.prog_up.D, U=middle.sched.ictx.prog_up.U)
    p.add(op)
    middle.sched.ictx.prog_up = p


def fixture(R=3, gray=False):
    kw = dict(R=5, D=1, Q0=512, U0=32768, U1=8192) if R == 5 else {}
    if gray:
        kw = dict(R=5, D=1, Q0=8192, U0=1048576, Q1=8192, U1=1048576,
                  ncol0=8192, schedule="gray")
    middle, top = make_tower(**kw)
    projected = Program(D=middle.prog.D, U=middle.p.U)
    evaluate = [o for o in middle.prog.ops if o.kind == "IEVAL"]
    for op in evaluate:
        assert middle.prog.ops_at(op.t0) == [op]
        projected.add(op)
    outer = make_system(Q=8192 if gray else 1024, U=1048576 if gray else 65536,
                        ncol=16, R=R, D=middle.prog.D,
                        Qs=middle.p.Q, Us=middle.p.U, Qss=top.p.Q, Uss=top.p.U,
                        with_tracks=True, full_registers=True,
                        schedule="gray" if gray else "compressed", nested_controls=True,
                        prog_up=projected, L_up=middle.L, trickle_up=middle.sched.trickle,
                        regwin_up=middle.sched.reg_window, inner_ctx=middle.sched.ictx)
    return outer, middle, top, evaluate


@pytest.mark.parametrize("R", [3, 5])
def test_nested_ieval_actual_value_operations_complete_outer_period(R):
    from gacsca.interp import slot_of
    outer, middle, top, phases = fixture(R)
    kinds = ("CONST", "MOV", "BITOP", "SHIFT", "RSHIFT", "BCAST_INIT")
    selected = [next(o for o in top.prog.ops if o.kind == kind) for kind in kinds]
    B, L = len(selected), outer.p.ncol
    state = {k:np.zeros((B, L), np.int32) for k in
             ("addr", "age", "f1", "f2", "wf1", "wf2", "simage", "simaddr")}
    rng = np.random.default_rng(1250 + R)
    V = rng.integers(0, 2, (B, L, middle.T.NT), dtype=np.uint8)
    for b, op in enumerate(selected):
        active = top.prog.ops_at(op.t0)
        index, slot = active.index(op), slot_of(active, active.index(op))
        phase = next(o for o in phases if o.param == index)
        state["age"][b] = phase.t0
        state["addr"][b] = (middle.sched.ictx.pos(op.dst, R // 2) + np.arange(L) - 7) % middle.p.Q
        state["simage"][b] = op.t0
        state["simaddr"][b] = min(op.hi - 1, op.lo + 3)
        V[b, :, middle.T["HOLD"]] = 1 - (op.param if op.kind == "CONST" else 1)
        for name in (f"S{slot}0", f"S{slot}1", f"S{slot}2", f"SHSRC{slot}"):
            V[b, :, middle.sched.ictx.n[name]] = 1
    state["trk"] = redistribute(V, R)
    state["trk"][:, ::3, :, 0] ^= rng.integers(0, 2, state["trk"][:, ::3, :, 0].shape, dtype=np.uint8)
    expected = middle.np_engine().step(state)
    neutral = middle.np_engine()
    neutral.prog = Program(D=middle.prog.D, U=middle.p.U)
    baseline = neutral.step(state)
    for b, kind in enumerate(kinds):
        assert np.any(expected["trk"][b] != baseline["trk"][b]), f"vacuous {kind}"
    mgpu = middle.gpu_engine()
    packed = mgpu.to_gpu(state)
    actual = mgpu.to_np(mgpu.step(packed, torch.empty_like(packed), 0))
    for name in expected:
        np.testing.assert_array_equal(actual[name], expected[name], err_msg=f"middle.{name}")
    physical = outer.np_engine().initial(B, info_bits=encode_state_info(state, outer.L, outer.p.Q))
    for name in ("simage", "simaddr", "simage2", "simaddr2"): physical[name][:] = 65535
    gpu = outer.gpu_engine()
    runner = CleanGraphRunner(gpu, gpu.to_gpu(physical))
    runner.run(outer.p.U)
    decoded = decode_state_info(gpu.info_bits(runner.state).cpu().numpy(), outer.L, outer.p.Q)
    for name in expected:
        np.testing.assert_array_equal(decoded[name], expected[name], err_msg=name)


@pytest.mark.parametrize("kind", ["EQC", "EQF", "ORF", "ANDF", "LTC", "ADDC"])
def test_nested_ieval_sweep_boolean_table_token_priority_and_boundaries(kind):
    outer, middle, top, phases = fixture()
    op = replace(next(o for o in top.prog.ops if o.kind == "SWEEP"),
                 lo=10, hi=18, param=1, skind=kind, dst=top.T["T0"])
    single_inner(middle, op)
    phase = next(o for o in phases if o.param == 0)
    J, cases = middle.sched.ictx, []
    def add(track, address, scratch, old, new):
        cases.append((J.pos(top.T[track], 1), address, scratch, old, new))
    for cin, x, y, bit in product((0, 1), repeat=4):
        address = 10 + (1 - bit)
        scratch = dict(S00=x, S01=y, SIG1=1, CARRY1=cin)
        if kind == "EQC": carry = int(cin and x == bit)
        elif kind == "EQF": carry = int(cin and x == y)
        elif kind == "ORF": carry = int(cin or x)
        elif kind == "ANDF": carry = int(cin and x)
        elif kind == "LTC": carry = int(x < bit or (x == bit and cin))
        else: carry = int(x + bit + cin >= 2)
        add("ACC", address, scratch, 1 - carry, carry)
        out = (x + bit + cin) % 2 if kind == "ADDC" else 0
        add("T0", address, scratch, 1 - out, out)
    # Lowest available valid distance wins, not the largest/latest token.
    for k in (1, 2, 3):
        scratch = {f"SIG{j}":int(j >= k) for j in (1, 2, 3)}
        add("SIG", 12, scratch, 1 - int(k == 3), int(k == 3))
    for address, scratch, old, new in (
        (8, {}, 1, 1), (9, {}, 1, 0), (10, {"SIG2":1}, 1, 0),
        (10, {"SIG1":1}, 1, 0), (17, {"S02":1}, 0, 1),
        (17, {"S02":0}, 1, 0), (17, {"SIG1":1}, 0, 1),
        (18, {"SIG1":1}, 1, 1)):
        add("SIG", address, scratch, old, new)
    local_evaluations(outer, middle, phase, op, cases)


@pytest.mark.parametrize("kind", ["BCAST", "SWEEP_INIT", "SHIFT", "RESET", "REGWIN", "MOV"])
def test_nested_ieval_special_guards(kind):
    outer, middle, top, phases = fixture(5, gray=True) if kind == "MOV" else fixture()
    from gacsca.microcode import Op
    # Synthetic descriptors isolate guards that actual clean schedules hide.
    op = Op(kind, 2, 3, 10, 18, dst=top.T["T0"], src=top.T["T1"], param=1)
    if kind == "SHIFT": op.param2 = 0
    if kind == "RESET": op.param, op.param2 = top.T["T0"] + 1, 1
    if kind == "MOV":
        op.lo = middle.sched.ictx.computed_move_addresses[0]
        op.hi, op.dst, op.param2 = op.lo + 1, top.T["INFO"], 1
    single_inner(middle, op)
    phase, J, cases = next(o for o in phases if o.param == 0), middle.sched.ictx, []
    pos = lambda t:J.pos(t, middle.T.R // 2)
    if kind == "BCAST":
        for found, token, value in product((0, 1), repeat=3):
            scratch = dict(S02=token, BFOUND=found, BVAL=value)
            for t in (op.dst, top.T["SIG"]):
                new = (1 if t == top.T["SIG"] else value) if found and not token else 0
                cases.append((pos(t), 12, scratch, 0, new))
        cases += [(pos(op.dst), a, dict(BFOUND=1, BVAL=1), 0, 0) for a in (9, 18)]
    elif kind == "SWEEP_INIT":
        cases = [(pos(t), a, {}, 0, int(10 <= a < 18))
                 for t in (op.dst, top.T["SIG"]) for a in (9, 10, 17, 18)]
    elif kind == "SHIFT":
        cases = [(pos(op.dst), a, dict(SHSRC0=1), 0, int(11 <= a < 18)) for a in (9, 10, 11, 17, 18)]
    elif kind == "RESET":
        cases = [(pos(op.dst), a, {}, 1, int(not 10 <= a < 18)) for a in (9, 10, 17, 18)]
        for field in ("SIMAGE", "SIMADDR"):
            lo, hi = J.L.frange(field)
            cases += [(a, raw, {}, 1, int(not 10 <= raw < 18))
                      for a in (lo, hi - 1) for raw in (9, 10, 17, 18)]
    elif kind == "REGWIN":
        cases = [(pos(op.dst), a, {}, 1, int(not 10 <= a < 18)) for a in (9, 10, 17, 18)]
    else:
        # Transported computed-Address match controls MOV, not raw Address2.
        cases = [(pos(op.dst), a, dict(S00=1, BLB=guard), 0, guard)
                 for a in (op.lo, (op.lo + 5) % top.p.Q) for guard in (0, 1)]
    local_evaluations(outer, middle, phase, op, cases)


@pytest.mark.parametrize("R", [3, 5])
def test_nested_ieval_every_operand_locally_transported(R):
    from gacsca.interp import slot_of
    outer, middle, top, phases = fixture(R)
    J, I = middle.sched.ictx, outer.sched.ictx
    chosen = [next(o for o in top.prog.ops if o.kind == k) for k in
              ("MOV", "BITOP", "SHIFT", "RSHIFT", "SWEEP", "BCAST_INIT", "BCAST")]
    chosen += [o for o in top.prog.ops if o.kind == "MOV" and o.param2]
    cases = []
    for op in chosen:
        active = top.prog.ops_at(op.t0)
        index, slot = active.index(op), slot_of(active, active.index(op))
        phase = next(o for o in phases if o.param == index)
        if op.kind in ("SHIFT", "RSHIFT"):
            roles = [(f"SHSRC{slot}", "SHSRC0")]
        elif op.kind == "BCAST":
            roles = [(f"S{slot}2", "S02"), ("BFOUND", "BFOUND"), ("BVAL", "BVAL")]
        else:
            roles = [(f"S{slot}0", "S00")]
            if op.kind == "MOV" and op.param2:
                roles += [(f"CM{J.computed_move_addresses.index(op.lo)}", "BLB")]
            if op.kind in ("BITOP", "SWEEP"):
                roles += [(f"S{slot}{j}", f"S0{j}") for j in (1, 2)]
            if op.kind == "SWEEP":
                roles += [(f"{prefix}{k}", f"{prefix}{k}") for k in range(1, J.D_up + 1) for prefix in ("SIG", "CARRY")]
        for copy in range(R):
            writer = I.pos(middle.T["HOLD"], copy)
            for source, target in roles:
                X = I.pos(J.n[source], R // 2)
                direction = 1 if writer >= X else -1
                latch = next(o for o in outer.prog.ops if o.kind == "ILATCH" and
                             o.param == copy - R // 2 and o.param2 == direction)
                age = latch.t0 + abs(writer - X) // outer.prog.D
                assert age < latch.t1
                cases.append((phase.t0, op.t0, age, writer, I.n[target]))
    engine = outer.np_engine()
    B = len(cases)
    state = {k:np.repeat(v[:, :outer.p.Q], B, axis=0) for k,v in engine.initial(1).items()}
    V = np.zeros((B, outer.p.Q, outer.T.NT), np.uint8)
    V[..., I.n["BUS"]] = 1
    for b, (g1, g2, age, _, _) in enumerate(cases):
        state["age"][b], state["simage"][b], state["simage2"][b] = age, g1, g2
        state["simaddr"][b] = middle.p.Q // 2
    state["trk"] = redistribute(V, R)
    expected = engine.step(state)
    for b, (_, _, _, writer, target) in enumerate(cases):
        assert expected["trk"][b, writer, target, R // 2] == 1, cases[b]
    gpu = outer.gpu_engine()
    packed = gpu.to_gpu(state)
    actual = gpu.to_np(gpu.step(packed, torch.empty_like(packed), 0))
    for name in expected: np.testing.assert_array_equal(actual[name], expected[name], err_msg=name)


@pytest.mark.parametrize("R,gray", [(3, False), (5, False), (5, True)])
def test_nested_ieval_actual_token_operations_end_to_end(R, gray):
    from gacsca.interp import slot_of
    outer, middle, top, phases = fixture(R, gray=gray)
    by_kind = {o.skind:o for o in reversed(top.prog.ops) if o.kind == "SWEEP"}
    selected = [(op, top.T["ACC"]) for op in by_kind.values()]
    selected += [(next(o for o in top.prog.ops if o.kind == kind), top.T["SIG"])
                 for kind in ("SWEEP_INIT", "BCAST")]
    B, L = len(selected), outer.p.ncol
    state = {k:np.zeros((B, L), np.int32) for k in
             ("addr", "age", "f1", "f2", "wf1", "wf2", "simage", "simaddr")}
    rng = np.random.default_rng(1280 + R)
    V = rng.integers(0, 2, (B, L, middle.T.NT), dtype=np.uint8)
    J = middle.sched.ictx
    for b, (op, target) in enumerate(selected):
        active = top.prog.ops_at(op.t0)
        index, slot = active.index(op), slot_of(active, active.index(op))
        state["age"][b] = next(o.t0 for o in phases if o.param == index)
        state["addr"][b] = (J.pos(target, R // 2) + np.arange(L) - 7) % middle.p.Q
        state["simage"][b] = op.t0
        state["simaddr"][b] = min(op.lo + 3, op.hi - 1)
        V[b, :, middle.T["HOLD"]] = 0
        x = (op.param >> 3) & 1 if op.skind == "EQC" else int(op.skind in ("ORF", "ANDF", "ADDC"))
        for name, value in ((f"S{slot}0", x), (f"S{slot}1", 0), (f"S{slot}2", 0),
                            ("SIG1", 1), ("CARRY1", 1), ("BFOUND", 1), ("BVAL", 1)):
            V[b, :, J.n[name]] = value
    state["trk"] = redistribute(V, R)
    state["trk"][:, ::3, :, 0] ^= rng.integers(0, 2, state["trk"][:, ::3, :, 0].shape, dtype=np.uint8)
    state["simage"][:, 7] = (1 << (20 if gray else 16)) - 1
    expected = middle.np_engine().step(state)
    neutral = middle.np_engine()
    neutral.prog = Program(D=middle.prog.D, U=middle.p.U)
    baseline = neutral.step(state)
    for b, (op, _) in enumerate(selected):
        assert np.any(expected["trk"][b] != baseline["trk"][b]), (op.kind, op.skind)
    mgpu = middle.gpu_engine()
    packed = mgpu.to_gpu(state)
    actual = mgpu.to_np(mgpu.step(packed, torch.empty_like(packed), 0))
    for name in expected: np.testing.assert_array_equal(actual[name], expected[name], err_msg=name)
    bits = encode_state_info(state, outer.L, outer.p.Q)
    physical = outer.np_engine().initial(B, info_bits=bits)
    start = 0
    if gray:
        assert outer.L.K == 512
        physical["age"][:] = start = 7 * outer.p.U // 8
        V = np.zeros((B, outer.p.L, outer.T.NT), np.uint8)
        V[..., outer.T["INFO"]] = bits
        for bank in "ABC":
            for j in range(-5, 6): V[..., outer.T.arg(j, bank)] = np.roll(bits, -j * outer.p.Q, axis=1)
        physical["trk"] = redistribute(V, R)
        del V
    for name in ("simage", "simaddr", "simage2", "simaddr2"):
        physical[name][:] = (1 << (20 if gray else 16)) - 1
    gpu = outer.gpu_engine()
    runner = CleanGraphRunner(gpu, gpu.to_gpu(physical))
    del physical
    runner.run(outer.sched.compute_end - start if gray else outer.p.U)
    if gray:
        from experiments.gray_protocol import track_bits
        bits_out = track_bits(gpu, runner.state, outer.T["HOLD"])
    else:
        bits_out = gpu.info_bits(runner.state).cpu().numpy()
    decoded = decode_state_info(bits_out, outer.L, outer.p.Q)
    for name in expected: np.testing.assert_array_equal(decoded[name], expected[name], err_msg=name)


@pytest.mark.parametrize("direction", [-1, 1])
def test_nested_ieval_register_bit_timing(direction):
    from gacsca.microcode import Op
    outer, middle, top, phases = fixture()
    op = Op("BUSLATCH_INT", 2, 20, 0, top.p.Q, src=top.T["T0"], param2=direction)
    single_inner(middle, op)
    J, cases = middle.sched.ictx, []
    for field, source in (("SIMAGE", "AGE"), ("SIMADDR", "ADDR")):
        lo, hi = J.L.frange(field)
        slo, shi = J.L_up.frange(source)
        for i in (0, min(hi - lo, shi - slo) - 1):
            for dt, expected in ((0, 1), (J.D_up - 1, 1), (J.D_up, 0), (-1, 0)):
                cases.append((lo + i, slo + i + direction * dt, dict(BLB=1), 0, expected))
    local_evaluations(outer, middle, next(o for o in phases if o.param == 0), op, cases)


@pytest.mark.parametrize("R", [3, 5])
def test_nested_ieval_iinit_uses_inner_encoded_copy_guard(R):
    from gacsca.microcode import Op
    outer, middle, top, phases = fixture(R)
    J = middle.sched.ictx
    op = Op("IINIT", 2, 3, 0, top.p.Q, dst=top.T["T0"], src=top.T["T1"], param=-1, param2=1)
    single_inner(middle, op)
    base = J.L_up.b0 + J.L_up.track_base
    cases = [(J.pos(op.dst, R // 2), a, dict(S00=1), 0, int(a >= base and (a-base) % R == R // 2 - 1))
             for a in range(base - 1, min(base + R * 2, top.p.Q))]
    assert any(c[-1] for c in cases) and any(not c[-1] for c in cases)
    local_evaluations(outer, middle, next(o for o in phases if o.param == 0), op, cases)


@pytest.mark.parametrize("field", ["simage", "simaddr", "simage2", "simaddr2"])
def test_nested_ieval_holder_control_fault_does_not_become_shared_oracle(field):
    from gacsca.microcode import Op
    outer, middle, top, phases = fixture()
    op = Op("CONST", 2, 3, 10, 18, dst=top.T["T0"], param=1)
    single_inner(middle, op)
    phase = next(o for o in phases if o.param == 0)
    engine = outer.np_engine()
    state = {k:v[:, :outer.p.Q].copy() for k,v in engine.initial(1).items()}
    state["age"][:] = next(o.t0 for o in outer.prog.ops if o.kind == "IEVAL" and o.param == 0)
    state["simage"][:] = phase.t0
    state["simaddr"][:] = middle.sched.ictx.pos(op.dst, 1)
    state["simage2"][:] = op.t0
    state["simaddr2"][:] = 12
    state["trk"][:] = 0
    writer = outer.sched.ictx.pos(middle.T["HOLD"], 1)
    damaged = {k:v.copy() for k,v in state.items()}
    damaged[field][0, writer] = 65535
    clean, fault = engine.step(state), engine.step(damaged)
    np.testing.assert_array_equal(np.flatnonzero(np.any(clean["trk"] != fault["trk"], axis=(0, 2, 3))), [writer])
    clean2, fault2 = engine.step(clean), engine.step(fault)
    for name in clean2: np.testing.assert_array_equal(clean2[name], fault2[name], err_msg=name)
    gpu = outer.gpu_engine()
    packed = gpu.to_gpu(damaged)
    actual = gpu.to_np(gpu.step(packed, torch.empty_like(packed), 0))
    for name in fault: np.testing.assert_array_equal(actual[name], fault[name], err_msg=name)


@pytest.mark.parametrize("defect", ["negative_index", "concurrent", "deeper_regwin"])
def test_nested_ieval_rejects_unimplemented_descriptor_context(defect):
    from gacsca.interp import InterpCtx
    outer, middle, top, phases = fixture()
    p = Program(D=middle.prog.D, U=middle.p.U)
    op = replace(phases[0])
    p.add(op)
    match, error = "instruction index", ValueError
    if defect == "negative_index": op.param = -1
    elif defect == "concurrent":
        p.add(replace(op))
        match, error = "dedicated instruction age", NotImplementedError
    else:
        middle.sched.ictx.regwin_upup = (1, 2)
        match, error = "deeper REGWIN", NotImplementedError
    with pytest.raises(error, match=match):
        InterpCtx(outer.L, outer.T, p, middle.L, middle.sched.trickle, None, inner=middle.sched.ictx)
