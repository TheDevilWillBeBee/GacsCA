"""Gate counts (gacsca.netlist AND/OR/XOR gates) of per-tick decoders for one block:
 maj3, maj5, a [4,2,3] single-symbol-correcting MDS code over GF(4) and a [6,2,5]
 double-symbol-correcting Reed-Solomon code over GF(8) (Peterson-Gorenstein-Zierler),
 both checked exhaustively. Output = corrected data symbols only."""
import sys, os, itertools
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np
from gacsca.netlist import Net, Compiled, at_least

class GF:
    def __init__(self, m, poly):
        self.m, self.poly, self.q = m, poly, 1 << m
    def mul(self, a, b):
        r = 0
        while b:
            if b & 1: r ^= a
            a <<= 1
            if a >> self.m: a ^= self.poly
            b >>= 1
        return r
    def pw(self, a, e):
        r = 1
        for _ in range(e): r = self.mul(r, a)
        return r
    def inv(self, a):
        return self.pw(a, self.q - 2)

def lin(n, x, f, m):
    """Apply the GF(2)-linear map f (on integers) to the bit vector x."""
    cols = [f(1 << i) for i in range(m)]
    out = []
    for j in range(m):
        v = 0
        for i in range(m):
            if (cols[i] >> j) & 1: v = n.XOR(v, x[i])
        out.append(v)
    return out

def gmul(n, F, a, b):
    m = F.m
    out = [0] * m
    for i in range(m):
        for j in range(m):
            t = F.mul(1 << i, 1 << j)
            ab = n.AND(a[i], b[j])
            for k in range(m):
                if (t >> k) & 1: out[k] = n.XOR(out[k], ab)
    return out

def ginv(n, F, a):
    """a^(q-2) by square and multiply (squaring is linear)."""
    m = F.m
    sq = lambda x: lin(n, x, lambda v: F.mul(v, v), m)
    # a^(2^m - 2) = product of a^(2^i), i = 1..m-1
    cur = sq(a); acc = cur
    for _ in range(m - 2):
        cur = sq(cur); acc = gmul(n, F, acc, cur)
    return acc

def xorw(n, a, b): return [n.XOR(x, y) for x, y in zip(a, b)]
def nz(n, a): return n.any(a)
def cmul(n, F, x, c): return lin(n, x, lambda v: F.mul(v, c), F.m)

def rs625():
    F = GF(3, 0b1011); m = 3; N = 6
    al = [F.pw(2, i) for i in range(N)]                 # locators alpha^i, distinct nonzero
    n = Net()
    r = [[n.input(('r', i, b)) for b in range(m)] for i in range(N)]
    S = {}
    for j in range(1, 5):
        acc = [0] * m
        for i in range(N):
            acc = xorw(n, acc, cmul(n, F, r[i], F.pw(al[i], j)))
        S[j] = acc
    sq = lambda x: lin(n, x, lambda v: F.mul(v, v), m)
    det = xorw(n, sq(S[2]), gmul(n, F, S[1], S[3]))
    two = nz(n, det)
    idet = ginv(n, F, det)
    L1 = gmul(n, F, xorw(n, gmul(n, F, S[1], S[4]), gmul(n, F, S[2], S[3])), idet)
    L2 = gmul(n, F, xorw(n, gmul(n, F, S[2], S[4]), sq(S[3])), idet)
    iL1 = ginv(n, F, L1)
    one = n.AND(n.NOT(two), nz(n, S[1]))
    for i in (0, 1):                                     # data positions
        a = al[i]
        # two errors: located iff a^2 + L1*a + L2 == 0
        ev = xorw(n, xorw(n, cmul(n, F, L1, a), L2), [(F.mul(a, a) >> b) & 1 for b in range(m)])
        hit2 = n.AND(two, n.NOT(nz(n, ev)))
        num = xorw(n, S[2], gmul(n, F, S[1], xorw(n, L1, [(a >> b) & 1 for b in range(m)])))
        Y2 = cmul(n, F, gmul(n, F, num, iL1), F.inv(a))
        # one error: located iff S2 == a*S1
        hit1 = n.AND(one, n.NOT(nz(n, xorw(n, S[2], cmul(n, F, S[1], a)))))
        Y1 = cmul(n, F, S[1], F.inv(a))
        corr = [n.OR(n.AND(hit2, y2), n.AND(hit1, y1)) for y2, y1 in zip(Y2, Y1)]
        for b in range(m):
            n.set_output(('c', i, b), n.XOR(r[i][b], corr[b]))
    comp = Compiled(n)
    # codewords: data (c0, c1), checks c2..c5 solve sum al_i^j c_i = 0, j = 1..4 (brute force)
    words = []
    for c0 in range(8):
        for c1 in range(8):
            for rest in itertools.product(range(8), repeat=4):
                c = [c0, c1] + list(rest)
                ok = True
                for j in range(1, 5):
                    s = 0
                    for i in range(N): s ^= F.mul(F.pw(al[i], j), c[i])
                    if s: ok = False; break
                if ok: words.append(c); break
    assert len(words) == 64
    cases = []
    for c in words:
        cases.append((c, c))
        for i in range(N):
            for e in range(1, 8):
                x = list(c); x[i] ^= e; cases.append((x, c))
        for i, k in itertools.combinations(range(N), 2):
            for e in range(1, 8):
                for g in range(1, 8):
                    x = list(c); x[i] ^= e; x[k] ^= g; cases.append((x, c))
    R = np.array([x for x, _ in cases]); T = np.array([c for _, c in cases])
    vals = {('r', i, b): ((R[:, i] >> b) & 1).astype(bool) for i in range(N) for b in range(m)}
    out = comp.evaluate(vals, dtype=bool)
    bad = 0
    for i in (0, 1):
        got = sum(out[('c', i, b)].astype(int) << b for b in range(m))
        bad += int((got != T[:, i]).sum())
    return len(comp.gates), len(cases), bad

def mds423():
    F = GF(2, 0b111); m = 2
    H = [(1, 1), (1, 2), (1, 3), (0, 1)]                 # columns (h1, h2); data positions 0, 1
    n = Net()
    r = [[n.input(('r', i, b)) for b in range(m)] for i in range(4)]
    S1 = [0] * m; S2 = [0] * m
    for i, (h1, h2) in enumerate(H):
        if h1: S1 = xorw(n, S1, cmul(n, F, r[i], h1))
        S2 = xorw(n, S2, cmul(n, F, r[i], h2))
    for i in (0, 1):
        h2 = H[i][1]
        hit = n.AND(nz(n, S1), n.NOT(nz(n, xorw(n, S2, cmul(n, F, S1, h2)))))
        for b in range(m):
            n.set_output(('c', i, b), n.XOR(r[i][b], n.AND(hit, S1[b])))
    comp = Compiled(n)
    words = []
    for c0 in range(4):
        for c1 in range(4):
            for c2 in range(4):
                for c3 in range(4):
                    c = [c0, c1, c2, c3]
                    s1 = s2 = 0
                    for i, (h1, h2) in enumerate(H):
                        s1 ^= F.mul(h1, c[i]); s2 ^= F.mul(h2, c[i])
                    if s1 == 0 and s2 == 0: words.append(c)
    assert len(words) == 16
    cases = []
    for c in words:
        cases.append((c, c))
        for i in range(4):
            for e in range(1, 4):
                x = list(c); x[i] ^= e; cases.append((x, c))
    R = np.array([x for x, _ in cases]); T = np.array([c for _, c in cases])
    vals = {('r', i, b): ((R[:, i] >> b) & 1).astype(bool) for i in range(4) for b in range(m)}
    out = comp.evaluate(vals, dtype=bool)
    bad = 0
    for i in (0, 1):
        got = sum(out[('c', i, b)].astype(int) << b for b in range(m))
        bad += int((got != T[:, i]).sum())
    return len(comp.gates), len(cases), bad

def maj(kc):
    n = Net(); x = [n.input(('x', i)) for i in range(kc)]
    n.set_output('y', at_least(n, x, kc // 2 + 1)); return len(Compiled(n).gates)

print('maj3 gates per data bit:', maj(3), '  maj5 gates per data bit:', maj(5))
g, ncase, bad = mds423(); print(f'[4,2,3] over GF(4): {g} gates per block of 4 data bits = {g/4:.1f}/bit; {ncase} cases, {bad} wrong')
g, ncase, bad = rs625(); print(f'[6,2,5] RS over GF(8): {g} gates per block of 6 data bits = {g/6:.1f}/bit; {ncase} cases, {bad} wrong')
