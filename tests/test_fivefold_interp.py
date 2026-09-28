"""Fivefold repair and complete finite-tower transitions, including defects."""
import numpy as np
import torch

from gacsca.build import make_tower
from gacsca.engine_np import Engine, repair, redistribute
from gacsca.gpu_engine import EngineGPU
from gacsca.hierarchy import encode_info
from gacsca.interp import compile_repaired_tracks
from gacsca.microcode import Compiler
import pytest


def tower(ncol0=64):
    return make_tower(R=5, D=1, Q0=512, U0=32768, U1=8192, ncol0=ncol0)


def test_fivefold_repair_truth_table_numpy_and_gpu():
    lower, _ = tower(ncol0=1)
    p, T, L, ctx = lower.p, lower.T, lower.L, lower.sched.ictx
    C = Compiler(T, L, D=1)
    names = dict(SA="T0", SB="T1", VT="T2", BUS="T3")
    compile_repaired_tracks(C, ctx, 0, names)
    C.prog.U = p.U
    engine = Engine(p, T, L, C.prog, wipe_rules=False)
    state = engine.initial(32)
    V = repair(state["trk"])
    expected = np.zeros((32, T.NT), np.uint8)
    for b in range(32):
        for t in range(T.NT):
            pattern = (b + t) % 32
            expected[b, t] = pattern.bit_count() >= 3
            for r in range(5):
                V[b, L.pos(t, r), T.arg(2 - r)] = (pattern >> r) & 1
    state["trk"] = redistribute(V, 5)
    gpu = EngineGPU(p, T, L, C.prog, (0, 0), wipe=False)
    st = gpu.run(gpu.to_gpu(state), C.t, 0)
    for _ in range(C.t):
        state = engine.step(state)
    for result in (state, gpu.to_np(st)):
        V = repair(result["trk"])
        got = V[:, [L.pos(t, 2) for t in range(T.NT)], T["T2"]]
        np.testing.assert_array_equal(got, expected)


def test_fivefold_full_periods_match_damaged_upper_rule():
    lower, upper = tower()
    # Every operation kind, gather receive concurrency, trickle and commit.
    ages = [0, upper.sched.gather_starts[0] + upper.p.Q + 1,
            upper.sched.gather_starts[2] + upper.p.Q + 1,
            upper.sched.trickle[0] - 1, upper.p.U - 1]
    for kind in ("CONST", "SHIFT", "SWEEP_INIT", "SWEEP", "BCAST_INIT", "BCAST"):
        op = next(o for o in upper.prog.ops if o.kind == kind)
        ages.append(op.t0 + (op.t1 - op.t0) // 2)
    ages = sorted(set(ages))
    B = len(ages)
    engine = upper.np_engine()
    S = engine.initial(B)
    S["age"][:] = np.array(ages)[:, None]
    rng = np.random.default_rng(925)
    # Arbitrary, inconsistent copies exercise actual five-way repair, not
    # only the already-consistent tracks used in the inherited phase tests.
    S["trk"][:] = rng.integers(0, 2, S["trk"].shape, dtype=np.uint8)
    S["addr"][:, 0] = 23
    S["age"][:, 63] = 19
    S["wf1"][:, 59:64] = 1
    S["wf2"][:, :5] = 1
    S["f1"][:, 4:9] = 1
    S["f2"][:, 54:59] = 1
    encoded = []
    for b in range(B):
        cells = []
        for i in range(64):
            c = {k: int(S[k][b, i]) for k in ("addr", "age", "f1", "f2", "wf1", "wf2", "simage", "simaddr")}
            c["tracks"] = S["trk"][b, i]
            cells.append(c)
        encoded.append(encode_info(cells, lower.L, lower.p.Q))
    physical = lower.np_engine().initial(B, info_bits=np.stack(encoded))
    physical["simage"][:] = np.repeat(S["age"], lower.p.Q, axis=1)
    physical["simaddr"][:] = np.repeat(S["addr"], lower.p.Q, axis=1)
    gpu = lower.gpu_engine()
    state = gpu.to_gpu(physical)
    for period in range(2):
        state = gpu.run(state, lower.p.U, 0, t0=period * lower.p.U)
        S = engine.step(S)
        info = gpu.info_bits(state).cpu().numpy()
        for b in range(B):
            for i in range(64):
                start = i * lower.p.Q + lower.L.b0
                decoded = lower.L.decode(info[b, start:start + lower.L.K])
                for field in lower.L.fields:
                    assert decoded[field] == S[field.lower()][b, i], (period, ages[b], i, field)
                np.testing.assert_array_equal(decoded["tracks"], S["trk"][b, i],
                                              err_msg=f"period={period},age={ages[b]},cell={i}")


def test_routed_copy_ops_match_reference_and_remain_local():
    lower, _ = tower(ncol0=1)
    engine, gpu = lower.np_engine(), lower.gpu_engine()
    rng = np.random.default_rng(91)
    for op in (o for o in lower.prog.ops if o.kind == "IINIT"):
        S = engine.initial(1)
        S["age"][:] = op.t0
        S["simage"][:] = 500
        S["simaddr"][:] = 29
        S["trk"] = rng.integers(0, 2, S["trk"].shape, dtype=np.uint8)
        S["addr"][0, 70] = 20
        S["age"][0, 80] = 9
        expected = engine.step(S)
        st = gpu.to_gpu(S)
        got = gpu.to_np(gpu.step(st, torch.empty_like(st), t=0))
        for k in expected:
            np.testing.assert_array_equal(got[k], expected[k], err_msg=f"offset={op.param},field={k}")
        assert op.param2 or abs(op.param) <= 1
    # A manually constructed instruction that would read past the loaded
    # 11-cell window must fail explicitly, rather than use undefined memory.
    C = Compiler(lower.T, lower.L, D=1)
    C.emit("RSHIFT", src=lower.T["T0"], dst=lower.T["T1"], param=2)
    with pytest.raises(ValueError, match="exceeds physical reach"):
        EngineGPU(lower.p, lower.T, lower.L, C.prog, (0, 0))
