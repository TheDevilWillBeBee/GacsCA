"""Adversarial tests of redundant computation, beyond backend equivalence."""
import numpy as np
import pytest

from gacsca.params import Params
from gacsca.microcode import Tracks, Layout, Compiler
from gacsca.engine_np import Engine, repair, redistribute


@pytest.mark.parametrize("R,D,Q", [(3, 3, 256), (5, 1, 512)])
@pytest.mark.parametrize("fault", ["age", "addr", "whole_cell"])
@pytest.mark.parametrize("target", [0, 20, -1])
def test_isolated_control_fault_cannot_corrupt_redundant_operation(R, D, Q, fault, target):
    """Exercise every holder of an output bit, including colony boundaries."""
    p = Params(Q=Q, U=16384, ncol=2)
    T = Tracks(R=R)
    L = Layout(Q, p.U, T)
    x = target % Q
    C = Compiler(T, L, D=D, t=10)
    C.const("HOLD", 1, rng=(x, x + 1))
    eng = Engine(p, T, L, C.prog)
    clean = eng.initial(1)
    clean["age"][:] = 10
    expected = eng.step(clean)
    h = (R - 1) // 2
    for offset in range(-h, h + 1):
        S = {k: v.copy() for k, v in clean.items()}
        hit = (x + offset) % p.L
        if fault in ("age", "whole_cell"):
            S["age"][0, hit] = 11
        if fault in ("addr", "whole_cell"):
            S["addr"][0, hit] = (S["addr"][0, hit] + 7) % Q
        if fault == "whole_cell":
            S["trk"][0, hit] ^= 1
            for k in ("f1", "f2", "wf1", "wf2"):
                S[k][0, hit] = 1
            S["simage"][0, hit] = S["simaddr"][0, hit] = 65535
        got = eng.step(S)
        np.testing.assert_array_equal(repair(got["trk"]), repair(expected["trk"]))


@pytest.mark.parametrize("R,D,Q", [(3, 3, 256), (5, 1, 512)])
def test_holder_control_semantics_match_cuda(R, D, Q):
    from gacsca.gpu_engine import EngineGPU
    import torch

    p = Params(Q=Q, U=16384, ncol=2)
    T = Tracks(R=R)
    L = Layout(Q, p.U, T)
    C = Compiler(T, L, D=D, t=10)
    C.const("HOLD", 1, rng=(20, 21))
    C.prog.U = p.U
    eng = Engine(p, T, L, C.prog)
    gpu = EngineGPU(p, T, L, C.prog, (0, 0))
    S = eng.initial(1)
    S["age"][:] = 10
    S["age"][0, 20] = 11
    S["addr"][0, Q - 1] = 19
    V = np.random.default_rng(25).integers(0, 2, (1, p.L, T.NT), dtype=np.uint8)
    S["trk"] = redistribute(V, R)
    st = gpu.to_gpu(S)
    got = gpu.to_np(gpu.step(st, torch.empty_like(st), t=1))
    expected = eng.step(S)
    for k in expected:
        np.testing.assert_array_equal(got[k], expected[k], err_msg=k)


@pytest.mark.parametrize("R,D,Q,U", [(3, 3, 256, 16384), (5, 1, 512, 65536)])
def test_single_clock_fault_at_update_preserves_simulated_transition(R, D, Q, U):
    """Target one clock at commit after running the full colony work period.

    Previously every copy skipped Info:=Hold and simulated Age stayed at 0.
    """
    from gacsca.build import make_system
    from gacsca.hierarchy import encode_info
    import torch

    system = make_system(Q=Q, U=U, ncol=16, R=R, D=D, Qs=16, Us=2048)
    gpu = system.gpu_engine()
    cells = [dict(addr=i, age=0, f1=0, f2=0) for i in range(16)]
    S = system.np_engine().initial(1, info_bits=encode_info(cells, system.L, Q)[None])
    before = gpu.run(gpu.to_gpu(S), U - 1, 0)
    faulty = before.clone()
    x = 2 * Q + system.L.frange("AGE")[0]
    faulty[0, x, 1] = 0
    clean = gpu.step(before, torch.empty_like(before), t=U)
    got = gpu.step(faulty, torch.empty_like(faulty), t=U)
    np.testing.assert_array_equal(gpu.info_bits(got).cpu(), gpu.info_bits(clean).cpu())
    info = gpu.info_bits(got).cpu().numpy()[0]
    for i in range(16):
        b = i * Q + system.L.b0
        decoded = system.L.decode(info[b:b + system.L.K])
        assert (decoded["ADDR"], decoded["AGE"], decoded["F1"], decoded["F2"]) == (i, 1, 0, 0)


@pytest.mark.parametrize("R,Q", [(3, 256), (5, 512)])
def test_simultaneous_clock_fault_threshold(R, Q):
    """Redundant computation tolerates h faulty holders, but not h+1.

    This distinguishes a local failure mechanism; it does not establish the
    exponent of the complete stochastic automaton's logical error rate.
    """
    p = Params(Q=Q, U=16384, ncol=2)
    T = Tracks(R=R)
    L = Layout(Q, p.U, T)
    C = Compiler(T, L, D=1, t=10)
    C.const("HOLD", 1, rng=(20, 21))
    engine = Engine(p, T, L, C.prog)
    h = (R - 1) // 2
    for n_faults in (h, h + 1):
        S = engine.initial(1)
        S["age"][:] = 10
        S["age"][0, 20:20 + n_faults] = 11
        result = repair(engine.step(S)["trk"])[0, 20, T["HOLD"]]
        assert result == int(n_faults <= h)
