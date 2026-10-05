"""Independent check of the sub-agent's two claims, on the repository's own code (CPU only)."""
import numpy as np
from gacsca import candidates, codec, gray_errors
# (a) extent of a level-1 error under Gray's definitions
E = [(0, 0), (23, 23), (126, 126), (149, 149)]
print('4 points spanning 150:', gray_errors.classify(E, Q=512, U=25920).get('level1'), '| spanning 151:',
      gray_errors.classify([(0, 0), (23, 23), (127, 127), (150, 150)], Q=512, U=25920).get('level1'))
# (b) a 200-cell burst of shifted states reaching 10 cells into the right-hand colony
c = candidates.load('G16'); p, C = c.p, c.c_backend(); Q, U = p.Q, p.U
n = 32
rng = np.random.default_rng(3)
top = codec.random_upper(c, 1, rng)
up = codec.encode(c, top)[:, (np.arange(n) + Q // 2 - n // 2) % Q]
ref = C.pack(codec.encode(c, up))
b = (n // 2) * Q                                      # boundary between the two middle colonies
N = n * Q
def run(P, t): return C.run_packed_scalar(P.copy(), t)
want = c.step_numpy(up)
for mode in ('shift', 'random'):
    for t0 in (3 * Q, 12 * Q + 3 * Q, p.E0 + 2 * p.PL + 90):
        P = run(ref, t0)
        x0, w, h = b - 190, 200, 200
        r2 = np.random.default_rng(7)
        for t in range(h):
            P = run(P, 1)
            X = C.unpack(P, N)
            if mode == 'shift':
                X[:, x0:x0 + w] = X[:, x0 + Q // 2 + 7:x0 + w + Q // 2 + 7]
            else:
                X[:, x0:x0 + w] = r2.random((c.W, w)) < 0.5
            P = C.pack(X)
        P = run(P, U - t0 - h)
        d1 = codec.decode(c, C.unpack(P, N))
        wrong1 = np.flatnonzero((d1 != want).any(axis=0))
        # the reference ring is not closed at its ends (a slice): compare with the error-free physical run
        R = run(ref, U); dref = codec.decode(c, C.unpack(R, N))
        wrong_vs_ref = np.flatnonzero((d1 != dref).any(axis=0))
        P2, R2 = run(P, U), run(R, U)
        print(mode, 'burst at Age', t0, ': upper cells differing from the error-free ring at U:', (wrong_vs_ref - n // 2).tolist(),
              '(0 = right-hand colony, -1 = left-hand); identical at 2U:', bool(np.array_equal(P2, R2)), flush=True)
