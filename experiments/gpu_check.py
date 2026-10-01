"""GPU backend check for one candidate: bit-exact parity with the C kernel on
arbitrary states (several tick counts), then one work period of closure on
random upper states (decoded ring == the rule applied upstairs).

Usage: python experiments/gpu_check.py G9
"""
import sys
import time
import numpy as np
from gacsca import candidates, codec, gpu


def main():
    name = sys.argv[1]
    cand = candidates.load(name)
    p, C = cand.p, cand.c_backend()
    code = getattr(p, 'age_code', lambda t: t)
    t = time.time()
    nr, ncol = 4, (8 if name.startswith('R') else 4)
    sim = gpu.GpuSim(cand, nr, ncol)
    print('build', round(time.time() - t, 1), 's, words', sim.NW, flush=True)
    rng = np.random.default_rng(1)
    states = []
    for r in range(nr):
        X = rng.random((cand.W, sim.N)) < 0.5
        ages = [code(int(a)) for a in rng.integers(0, p.U, size=sim.N)]
        cand.set_field(X, 'age', np.array(ages))
        states.append(C.pack(X))
    sim.set_state(np.stack(states))
    for ticks in (1, 5, 40):
        sim.run(ticks)
        G = sim.state()
        for r in range(nr):
            states[r] = C.run_packed_scalar(states[r], ticks)
            assert np.array_equal(G[r], states[r]), (ticks, r)
    print('parity OK on arbitrary states,', nr, 'rings', flush=True)
    up = codec.random_upper(cand, 12 if name.startswith('R') else 8, rng)
    sim2 = gpu.GpuSim(cand, 2, up.shape[1])
    sim2.set_state(C.pack(codec.encode(cand, up)))
    t = time.time()
    sim2.run(p.U)
    Y = sim2.state()
    ref = cand.step_numpy(up)
    ok = [bool(np.array_equal(codec.decode(cand, C.unpack(Y[r], sim2.N)), ref)) for r in range(2)]
    print('closure', ok, 'period', round(time.time() - t, 1), 's,',
          round(sim2.last_ms * 1000 / p.U, 1), 'us/tick', flush=True)
    assert all(ok)


if __name__ == '__main__':
    main()
