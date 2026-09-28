"""Unprojected third-link transitions; not a full upper work-period proof."""
import numpy as np
import pytest
import torch

from gacsca.build import make_tower, make_system
from gacsca.engine_np import redistribute
from gacsca.gpu_engine import CleanGraphRunner
from gacsca.hierarchy import encode_state_info, decode_state_info


def fixture(R=3, ncol=16, compact=False, full=False):
    kw = dict(R=5, D=1, Q0=512, U0=32768, U1=8192) if R == 5 else {}
    if full: kw.update(full_registers=True, U1=8192 if R == 3 else 16384)
    middle, top = make_tower(**kw)
    Q, U = ((256, 16384) if R == 3 else (512, 32768)) if compact else (1024, 65536)
    outer = make_system(Q=Q, U=U, ncol=ncol, R=R, D=middle.prog.D,
                        Qs=middle.p.Q, Us=middle.p.U, Qss=top.p.Q, Uss=top.p.U,
                        with_tracks=True, full_registers=True, nested_controls=True,
                        prog_up=middle.prog, L_up=middle.L, trickle_up=middle.sched.trickle,
                        regwin_up=middle.sched.reg_window, inner_ctx=middle.sched.ictx)
    outer.up = middle
    return outer, middle, top


@pytest.mark.parametrize("R", [3, 5])
def test_public_layer_factory_preserves_full_middle_program_and_geometry(R):
    from gacsca.build import make_simulation_layer
    kw = dict(R=5, D=1, Q0=512, U0=32768, U1=8192) if R == 5 else {}
    middle, top = make_tower(ncol0=1, **kw)
    outer = make_simulation_layer(middle, Q=1024, U=65536)
    assert outer.up is middle and middle.up is top
    assert outer.p.ncol == middle.p.L == middle.p.Q
    assert outer.sched.ictx.prog_up is middle.prog
    assert outer.sched.ictx.inner is middle.sched.ictx
    assert outer.L.full_registers and outer.prog.nested_register_bits == 16
    assert outer.sched.compute_end < outer.p.U - 1
    with pytest.raises(NotImplementedError, match="second control pair"):
        make_simulation_layer(outer, Q=2048, U=131072)


@pytest.mark.parametrize("R,compact,full", [(3, False, False), (5, False, False),
                                          (3, True, False), (5, True, False),
                                          (3, True, True), (5, True, True)])
def test_full_third_link_all_emitted_instruction_families(R, compact, full):
    outer, middle, top = fixture(R, compact=compact, full=full)
    # No instruction projection: controls may reach the whole middle program.
    seen, cases = set(), []
    for op in middle.prog.ops:
        if op.kind not in seen:
            seen.add(op.kind)
            cases.append((op.t0, None))
    for op in top.prog.ops:
        if ("IEVAL", op.kind) not in seen:
            seen.add(("IEVAL", op.kind))
            index = top.prog.ops_at(op.t0).index(op)
            phase = next(o for o in middle.prog.ops if o.kind == "IEVAL" and o.param == index)
            cases.append((phase.t0, op))
    cases += [(middle.p.U - 1, None), (middle.p.U // 2, None)]
    B, L = len(cases), outer.p.ncol
    state = {k:np.zeros((B, L), np.int32) for k in
             ("addr", "age", "f1", "f2", "wf1", "wf2", "simage", "simaddr")}
    rng = np.random.default_rng(1310 + R)
    for b, (age, inner) in enumerate(cases):
        state["age"][b] = age
        center = middle.p.Q // 2 if inner is None or inner.dst is None else middle.sched.ictx.pos(inner.dst, R // 2)
        state["addr"][b] = (center + np.arange(L) - 7) % middle.p.Q
        state["simage"][b] = rng.integers(0, 65536, L) if inner is None else inner.t0
        state["simaddr"][b] = rng.integers(0, 65536, L) if inner is None else inner.lo
    V = rng.integers(0, 2, (B, L, middle.T.NT), dtype=np.uint8)
    state["trk"] = redistribute(V, R)
    state["trk"][:, ::3, :, 0] ^= rng.integers(0, 2, state["trk"][:, ::3, :, 0].shape, dtype=np.uint8)
    state["age"][:, 7] = (state["age"][:, 7] + 1) % middle.p.U
    state["addr"][:, 9] = (state["addr"][:, 9] + 1) % middle.p.Q
    state["f1"][:, 3] = 1
    expected = middle.np_engine().step(state)
    mgpu = middle.gpu_engine()
    packed = mgpu.to_gpu(state)
    actual = mgpu.to_np(mgpu.step(packed, torch.empty_like(packed), 0))
    for name in expected: np.testing.assert_array_equal(actual[name], expected[name], err_msg=f"middle.{name}")
    physical = outer.np_engine().initial(B, info_bits=encode_state_info(state, outer.L, outer.p.Q))
    for name in ("simage", "simaddr", "simage2", "simaddr2"): physical[name][:] = 65535
    gpu = outer.gpu_engine()
    runner = CleanGraphRunner(gpu, gpu.to_gpu(physical))
    del physical
    runner.run(outer.p.U)
    decoded = decode_state_info(gpu.info_bits(runner.state).cpu().numpy(), outer.L, outer.p.Q)
    for name in expected: np.testing.assert_array_equal(decoded[name], expected[name], err_msg=f"outer.{name}")


@pytest.mark.parametrize("R", [3, 5])
def test_full_third_link_consecutive_transitions_whole_middle_colony(R):
    # A complete middle colony, but only one represented top cell (periodic
    # aliasing at that next level); this is not a full top work-period test.
    outer, middle, top = fixture(R, ncol=256 if R == 3 else 512)
    middle_engine = middle.np_engine()
    state = {k:v[:, :outer.p.ncol].copy() for k,v in middle_engine.initial(2).items()}
    # Cross the actual ILATCH/IEVAL boundary and the entire middle rollover.
    phase = next(o for o in middle.prog.ops if o.kind == "IEVAL" and o.param == 0)
    state["age"][0] = phase.t0 - 1
    state["age"][1] = middle.p.U - 2
    state["simage"][:] = next(o.t0 for o in top.prog.ops if o.kind == "BITOP")
    state["simaddr"][:] = 12
    rng = np.random.default_rng(1330 + R)
    state["trk"] = redistribute(rng.integers(0, 2, (2, outer.p.ncol, middle.T.NT), dtype=np.uint8), R)
    state["trk"][:, ::3, :, 0] ^= rng.integers(0, 2, state["trk"][:, ::3, :, 0].shape, dtype=np.uint8)
    physical = outer.np_engine().initial(2, info_bits=encode_state_info(state, outer.L, outer.p.Q))
    gpu = outer.gpu_engine()
    runner = CleanGraphRunner(gpu, gpu.to_gpu(physical))
    del physical
    for period in range(4):
        state = middle_engine.step(state)
        runner.run(outer.p.U)
        decoded = decode_state_info(gpu.info_bits(runner.state).cpu().numpy(), outer.L, outer.p.Q)
        for name in state:
            np.testing.assert_array_equal(decoded[name], state[name], err_msg=f"period {period + 1}.{name}")
