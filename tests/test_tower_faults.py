"""Block simulation must also commute on damaged simulated configurations."""
import numpy as np
import pytest

from gacsca.build import make_tower
from gacsca.engine_np import repair, redistribute
from gacsca.hierarchy import encode_info


@pytest.mark.parametrize("flag,cell,signal", [("WF1", 63, 61), ("WF2", 0, 3)])
def test_trickle_flags_use_computed_simulated_address_and_age(flag, cell, signal):
    lower, upper = make_tower(ncol0=64)
    direct, gpu = upper.np_engine(), lower.gpu_engine()
    S = direct.initial(1)
    S["age"][:] = upper.sched.trickle[0] - 1
    V = repair(S["trk"])
    V[0, signal, upper.T["INFO"]] = 1
    S["trk"] = redistribute(V, upper.T.R)
    S["addr"][0, cell] = 0 if cell else 63
    S["age"][0, cell] = 0
    cells = []
    for i in range(64):
        record = {k: int(S[k][0, i]) for k in ("addr", "age", "f1", "f2", "wf1", "wf2", "simage", "simaddr")}
        record["tracks"] = S["trk"][0, i]
        cells.append(record)
    encoded = encode_info(cells, lower.L, lower.p.Q)[None]
    physical = lower.np_engine().initial(1, info_bits=encoded)
    physical["simage"][:] = np.repeat(S["age"], lower.p.Q, axis=1)
    physical["simaddr"][:] = np.repeat(S["addr"], lower.p.Q, axis=1)
    state = gpu.to_gpu(physical)
    for period in range(2):
        S = direct.step(S)
        state = gpu.run(state, lower.p.U, 0, t0=period * lower.p.U)
        info = gpu.info_bits(state).cpu().numpy()[0]
        for i in range(64):
            start = i * lower.p.Q + lower.L.b0
            decoded = lower.L.decode(info[start:start + lower.L.K])
            for name in lower.L.fields:
                assert decoded[name] == S[name.lower()][0, i], (period, i, name)
            np.testing.assert_array_equal(decoded["tracks"], S["trk"][0, i], err_msg=f"period={period},cell={i}")
        if period == 0:
            assert S[flag.lower()][0, cell] == 1


def test_fivefold_tower_rejects_nonlocal_speed():
    with pytest.raises(ValueError, match="radius five"):
        make_tower(R=5, D=3, Q0=512, U0=65536)
