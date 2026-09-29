"""Acid test of the simulation (stage 1, level-1 cells with local structure only): the decoded
level-1 trajectory of the level-0 automaton equals the direct level-1 trajectory."""
import numpy as np, time, pytest
from gacsca.params import Params, Variant
from gacsca.microcode import Tracks, Layout
from gacsca.engine_np import Engine, repair
from gacsca.workperiod import build_workperiod
from gacsca.hierarchy import encode_info, decode_info, level1_to_arrays
from gacsca import level0_np as l0


@pytest.mark.slow
def test_decoded_trajectory_equals_direct(nsteps=2, ncol=16, Q=256, U=16384, D=3):
    p = Params(Q=Q, U=U, ncol=ncol)
    T = Tracks(JMAX=6, wq=8, wu=(U - 1).bit_length(), R=3)
    L = Layout(Q, U, T)
    prog, sched = build_workperiod(p, T, L, D=D)
    print("schedule:", sched)
    rng = np.random.default_rng(0)
    # level-1 initial configuration: a damaged ground state on the ring of ncol cells
    level1 = [dict(addr=i % Q, age=0, f1=0, f2=0) for i in range(ncol)]
    for k in [3, 9]:
        level1[k] = dict(addr=int(rng.integers(0, Q)), age=int(rng.integers(0, U)), f1=1, f2=0)
    eng = Engine(p, T, L, prog)
    S = eng.initial(1, info_bits=encode_info(level1, L, Q)[None, :])
    direct = level1_to_arrays(level1)
    p1 = Params(Q=Q, U=U, ncol=1)   # level-1 ring of ncol cells uses the same Q, U
    t0 = time.time()
    for tau in range(1, nsteps + 1):
        for _ in range(U):
            S = eng.step(S)
        direct = l0.step(direct, p1); direct.pop("_info")
        dec = decode_info(S, L, T, Q)[0]
        got = [(d["ADDR"], d["AGE"], d["F1"], d["F2"]) for d in dec]
        exp = [(int(direct["addr"][0, i]), int(direct["age"][0, i]), int(direct["f1"][0, i]), int(direct["f2"][0, i])) for i in range(ncol)]
        print(f"tau={tau} ({time.time()-t0:.0f}s) decoded={got[:6]} ... direct={exp[:6]}")
        assert got == exp, (tau, got, exp)
        # level-0 local structure intact and synchronised
        assert (S["addr"] == np.arange(p.L) % Q).all() and (S["age"] == (tau * U) % U).all()
        assert S["f1"].sum() == 0


if __name__ == "__main__":
    test_decoded_trajectory_equals_direct()
