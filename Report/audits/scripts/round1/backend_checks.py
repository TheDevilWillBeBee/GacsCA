"""Compare CPU implementations on nonzero arbitrary match-pass states."""
import numpy as np
from gacsca.fixed_rule.design_optimization import candidates

rng = np.random.default_rng(81647)
for name in ('G13', 'G14'):
    c = candidates.load(name)
    p = c.p
    N = 2 * p.Q
    X = rng.random((c.W, N)) < 0.5
    c.set_field(X, 'addr', np.tile(np.arange(p.Q), 2))
    t = p.E0 + p.MP * p.PL + p.PL // 2
    c.set_field(X, 'age', np.full(N, p.age_code(t)))
    Y = c.step_numpy(X)
    C = c.c_backend()
    P = C.pack(X)
    scalar = C.unpack(C.run_packed_scalar(P.copy(), 1), N)
    avx2 = C.unpack(C.run_packed(P.copy(), 1, threads=3), N)
    offsets = [abs(nm[1]) for nm in c.comp.inputs if nm[0] == 'x']
    print(name, 'radius', max(offsets), 'numpy_scalar', bool(np.array_equal(Y, scalar)),
          'numpy_avx2', bool(np.array_equal(Y, avx2)),
          'arriving_output_bits', int((Y != X).sum()), flush=True)
