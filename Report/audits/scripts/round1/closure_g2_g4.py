"""Fill the receipt gap for G2/G4 with successive CPU macrosteps."""
import numpy as np
from gacsca.fixed_rule.design_optimization import candidates, codec

for name in ('G2', 'G4'):
    c = candidates.load(name)
    C = c.c_backend()
    up = codec.random_upper(c, 3, np.random.default_rng(3491))
    P = C.pack(codec.encode(c, up))
    for step in (1, 2):
        P = C.run_packed(P, c.p.U, threads=3)
        ref = c.step_numpy(up)
        X = C.unpack(P, 3 * c.p.Q)
        h = codec.colony_health(c, X)
        print(name, step, 'equal', bool(np.array_equal(codec.decode(c, X), ref)),
              'changed_bits', int((ref != up).sum()),
              'healthy', bool(h['addr'] and h['age'] and h['age0'] == 0), flush=True)
        up = ref
