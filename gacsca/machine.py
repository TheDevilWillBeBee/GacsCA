"""Physical ring execution of one fixed candidate (netlist + ROM table).

A ring state is a boolean array X of shape (W, N): one row per field bit in
`rule.schema` order, one column per physical site. Both backends apply the
same rule at every site and tick; neither takes a depth argument or an
upper-level callback.

* `step_numpy` is the reference: it evaluates the netlist, looks up
  I = Pi[stored Address][psel] at *every* site, and re-evaluates.
* The C backend is generated from the same compiled netlist. It bit-slices
  64 sites per machine word and looks up Pi only at sites where the
  netlist's `arrive` node is set; the netlist uses I only through `arrive`,
  and tests compare the backends on arbitrary states.
"""
import ctypes
import hashlib
import os
import subprocess
import numpy as np
from . import rule

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BUILD = os.path.join(ROOT, 'figs', 'build')


class Candidate:
    """A fixed rule: Params, its netlist, the ROM table Pi and the layout.

    rom[a, psel] is the 21-bit instruction at Address a for every value of
    the psel field (entries beyond the evaluation window are word 0, a no-op).
    layout[b] is the colony cell holding upper-state bit b.
    """

    def __init__(self, p, rom, layout):
        self.p = p.check()
        self.net, self.comp = p.fam().cached(p)
        self.rom = np.ascontiguousarray(rom, dtype=np.uint32)
        assert self.rom.shape == (p.Q, p.NPT)
        self.layout = np.asarray(layout, dtype=np.int64)
        self.schema = p.fam().schema(p)
        self.W = p.fam().width(p)
        assert self.layout.shape == (self.W,)
        assert len(set(self.layout.tolist())) == self.W and self.layout.max() < p.Q
        self.rows = [(f, i) for f, w in self.schema for i in range(w)]
        self.row = {fi: r for r, fi in enumerate(self.rows)}

    def digest(self):
        h = hashlib.sha256()
        h.update(self.comp.digest.encode())
        h.update(self.rom.tobytes())
        h.update(self.layout.tobytes())
        return h.hexdigest()

    def identity(self):
        d = self.p.fam().identity(self.p)
        d.update(candidate_sha256=self.digest(),
                 rom_sha256=hashlib.sha256(self.rom.tobytes()).hexdigest(),
                 rom_nonzero_words=int(np.count_nonzero(self.rom)))
        return d

    # ------------------------------------------------------------ fields
    def field(self, X, f):
        w = dict(self.schema)[f]
        r0 = self.row[(f, 0)]
        out = np.zeros(X.shape[1], dtype=np.int64)
        for i in range(w):
            out |= X[r0 + i].astype(np.int64) << i
        return out

    def set_field(self, X, f, values):
        w = dict(self.schema)[f]
        r0 = self.row[(f, 0)]
        values = np.asarray(values, dtype=np.int64)
        for i in range(w):
            X[r0 + i] = (values >> i) & 1

    # ------------------------------------------------------------ reference
    def step_numpy(self, X):
        comp = self.comp
        values = {}
        zeros = np.zeros(X.shape[1], dtype=bool)
        for name in comp.inputs:
            if name[0] == 'x':
                _, j, f, i = name
                values[name] = np.roll(X[self.row[(f, i)]], -j)
            else:
                values[name] = zeros
        out = comp.evaluate(values, bool)
        psel = np.zeros(X.shape[1], dtype=np.int64)
        for i in range(self.p.PW):
            psel |= out[('psel', i)].astype(np.int64) << i
        if ('laddr', 0) in out:          # lookup key = computed Address
            addr = np.zeros(X.shape[1], dtype=np.int64)
            for i in range(self.p.k):
                addr |= out[('laddr', i)].astype(np.int64) << i
        else:
            addr = self.field(X, 'addr')
        word = self.rom[addr, psel].astype(np.int64)
        for i in range(self.p.IW):
            values[('I', i)] = ((word >> i) & 1).astype(bool)
        out = comp.evaluate(values, bool)
        return np.stack([out[('y', f, i)] for f, i in self.rows])

    def run_numpy(self, X, ticks):
        for _ in range(ticks):
            X = self.step_numpy(X)
        return X

    # ------------------------------------------------------------ C backend
    def c_backend(self):
        if not hasattr(self, '_c'):
            self._c = CKernel(self)
        return self._c


def _c_source(cand):
    """Generate the bit-sliced C kernel from the compiled netlist.

    Two word_step variants share the same straight-line gate list: a scalar
    one (64 sites per u64) and an AVX2 one (4 x 64 sites per GCC vector).
    run() uses the vector variant when the ring has a multiple of 256 sites.
    """
    comp, p = cand.comp, cand.p
    idx = comp.index
    lines = []
    emit = lines.append
    emit('#include <stdint.h>')
    emit('#include <string.h>')
    emit('#include <omp.h>')
    emit('typedef uint64_t u64;')
    emit('typedef u64 V __attribute__((vector_size(32)));')
    emit(f'#define W {cand.W}')
    emit(f'#define NPT {p.NPT}')
    emit('static inline u64 shl_in(const u64* r, int w, int NW, int j) {')
    emit('  /* bit t of result = site 64w+t+j of plane r (ring) */')
    emit('  if (j == 0) return r[w];')
    emit('  if (j > 0) { int w1 = (w + 1 == NW) ? 0 : w + 1; return (r[w] >> j) | (r[w1] << (64 - j)); }')
    emit('  { int jj = -j; int w0 = (w == 0) ? NW - 1 : w - 1; return (r[w] << jj) | (r[w0] >> (64 - jj)); }')
    emit('}')
    emit('static inline V ldv(const u64* q) { V v; memcpy(&v, q, sizeof v); return v; }')
    emit('static inline V fetch4(const u64* r, int w, int NW, int j) {')
    emit('  if (j == 0) return ldv(r + w);')
    emit('  if (w >= 1 && w + 5 <= NW) {')
    emit('    if (j > 0) { V a = ldv(r + w), b = ldv(r + w + 1); return (a >> j) | (b << (64 - j)); }')
    emit('    { int jj = -j; V a = ldv(r + w), b = ldv(r + w - 1); return (a << jj) | (b >> (64 - jj)); }')
    emit('  }')
    emit('  V out; for (int e = 0; e < 4; e++) out[e] = shl_in(r, w + e, NW, j); return out;')
    emit('}')
    n_in = 2 + len(comp.inputs)
    dep = [False] * comp.n_nodes
    for name, node in idx.items():
        if name[0] == 'I':
            dep[node] = True
    for g, (op, a, b) in enumerate(comp.gates):
        node = n_in + g
        dep[node] = dep[a] or dep[b]
    psel_nodes = [comp.outputs[('psel', i)] for i in range(p.PW)]
    arrive_node = comp.outputs[('arrive', 0)]
    assert not any(dep[x] for x in psel_nodes + [arrive_node])
    addr_rows = [cand.row[('addr', i)] for i in range(p.k)]
    laddr_nodes = ([comp.outputs[('laddr', i)] for i in range(p.k)]
                   if ('laddr', 0) in comp.outputs else None)
    if laddr_nodes is not None:
        assert not any(dep[x] for x in laddr_nodes)
    I_nodes = [idx.get(('I', i)) for i in range(p.IW)]
    ops = {0: '&', 1: '|', 2: '^'}

    for vec in (False, True):
        T = 'V' if vec else 'u64'
        zero = '((V){0,0,0,0})' if vec else '(u64)0'
        one = '((V){~0ULL,~0ULL,~0ULL,~0ULL})' if vec else '~(u64)0'

        def v(x):
            if x == 0: return zero
            if x == 1: return one
            return f'v{x}'

        name = 'word_step4' if vec else 'word_step1'
        emit(f'static void {name}(const u64* X, u64* Y, int NW, int w, const uint32_t* rom) {{')
        for nm, node in idx.items():
            if nm[0] == 'x':
                _, j, f, i = nm
                fetch = 'fetch4' if vec else 'shl_in'
                emit(f'  const {T} v{node} = {fetch}(X + (size_t){cand.row[(f, i)]} * NW, w, NW, {j});')
        for phase in (False, True):
            if phase:
                emit(f'  {T} ' + ', '.join(f'v{x} = {zero}' for x in I_nodes if x is not None) + ';')
                lanes = range(4) if vec else [None]
                for e in lanes:
                    sub = f'[{e}]' if vec else ''
                    off = f' + {e}' if vec else ''
                    emit('  {')
                    emit(f'    u64 arr = {v(arrive_node)}{sub};')
                    emit('    while (arr) {')
                    emit('      int t = __builtin_ctzll(arr); arr &= arr - 1;')
                    emit('      unsigned a = 0, ps = 0;')
                    if laddr_nodes is not None:
                        for i, x in enumerate(laddr_nodes):
                            emit(f'      a |= (unsigned)(({v(x)}{sub} >> t) & 1) << {i};')
                    else:
                        for i, r in enumerate(addr_rows):
                            emit(f'      a |= (unsigned)((X[(size_t){r} * NW + w{off}] >> t) & 1) << {i};')
                    for i, x in enumerate(psel_nodes):
                        emit(f'      ps |= (unsigned)(({v(x)}{sub} >> t) & 1) << {i};')
                    emit('      uint32_t word = rom[a * NPT + ps];')
                    for i, x in enumerate(I_nodes):
                        if x is not None:
                            emit(f'      v{x}{sub} |= (u64)((word >> {i}) & 1) << t;')
                    emit('    }')
                    emit('  }')
            for g, (op, a, b) in enumerate(comp.gates):
                node = n_in + g
                if dep[node] != phase:
                    continue
                emit(f'  const {T} v{node} = {v(a)} {ops[op]} {v(b)};')
        for r, (f, i) in enumerate(cand.rows):
            out = v(comp.outputs[("y", f, i)])
            if vec:
                emit(f'  {{ V o = {out}; memcpy(Y + (size_t){r} * NW + w, &o, sizeof o); }}')
            else:
                emit(f'  Y[(size_t){r} * NW + w] = {out};')
        emit('}')
    emit('void run(u64* A, u64* B, int NW, const uint32_t* rom, long ticks, int threads) {')
    emit('  /* one persistent parallel region; the implicit barrier of each omp for')
    emit('     separates ticks, so every tick reads only the previous state */')
    emit('  int vec = (NW % 4 == 0);')
    emit('  #pragma omp parallel num_threads(threads) if(threads > 1)')
    emit('  {')
    emit('    u64* X = A; u64* Y = B;')
    emit('    for (long t = 0; t < ticks; t++) {')
    emit('      if (vec) {')
    emit('        #pragma omp for schedule(static)')
    emit('        for (int w = 0; w < NW; w += 4) word_step4(X, Y, NW, w, rom);')
    emit('      } else {')
    emit('        #pragma omp for schedule(static)')
    emit('        for (int w = 0; w < NW; w++) word_step1(X, Y, NW, w, rom);')
    emit('      }')
    emit('      u64* T = X; X = Y; Y = T;')
    emit('    }')
    emit('    #pragma omp single')
    emit('    { if (X != A) memcpy(A, X, (size_t)W * NW * sizeof(u64)); }')
    emit('  }')
    emit('}')
    emit('void run_scalar(u64* A, u64* B, int NW, const uint32_t* rom, long ticks) {')
    emit('  u64* X = A; u64* Y = B;')
    emit('  for (long t = 0; t < ticks; t++) {')
    emit('    for (int w = 0; w < NW; w++) word_step1(X, Y, NW, w, rom);')
    emit('    u64* T = X; X = Y; Y = T;')
    emit('  }')
    emit('  if (X != A) memcpy(A, X, (size_t)W * NW * sizeof(u64));')
    emit('}')
    return '\n'.join(lines) + '\n'


class CKernel:
    def __init__(self, cand):
        self.cand = cand
        src = _c_source(cand)
        tag = hashlib.sha256(src.encode()).hexdigest()[:16]
        os.makedirs(BUILD, exist_ok=True)
        c_path = os.path.join(BUILD, f'front_{tag}.c')
        so_path = os.path.join(BUILD, f'front_{tag}.so')
        if not os.path.exists(so_path):
            with open(c_path, 'w') as fh:
                fh.write(src)
            tmp = so_path + f'.tmp{os.getpid()}'
            subprocess.run(['gcc', '-O2', '-march=native', '-fopenmp', '-shared', '-fPIC',
                            c_path, '-o', tmp], check=True)
            os.replace(tmp, so_path)
        self.lib = ctypes.CDLL(so_path)
        self.lib.run.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int,
                                 ctypes.c_void_p, ctypes.c_long, ctypes.c_int]
        self.lib.run_scalar.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int,
                                        ctypes.c_void_p, ctypes.c_long]
        self.source_sha256 = hashlib.sha256(src.encode()).hexdigest()
        self.so_path = so_path

    @staticmethod
    def pack(X):
        W, N = X.shape
        assert N % 64 == 0
        bits = np.packbits(X.astype(np.uint8), axis=1, bitorder='little')
        return np.ascontiguousarray(bits.view(np.uint64).reshape(W, N // 64))

    @staticmethod
    def unpack(P, N):
        bytes_ = P.view(np.uint8).reshape(P.shape[0], -1)
        return np.unpackbits(bytes_, axis=1, bitorder='little')[:, :N].astype(bool)

    def run_packed(self, P, ticks, threads=1):
        P = np.ascontiguousarray(P, dtype=np.uint64)
        B = np.empty_like(P)
        self.lib.run(P.ctypes.data, B.ctypes.data, P.shape[1], self.cand.rom.ctypes.data,
                     int(ticks), int(threads))
        return P

    def run_packed_scalar(self, P, ticks):
        P = np.ascontiguousarray(P, dtype=np.uint64)
        B = np.empty_like(P)
        self.lib.run_scalar(P.ctypes.data, B.ctypes.data, P.shape[1], self.cand.rom.ctypes.data,
                            int(ticks))
        return P

    def run(self, X, ticks, threads=1):
        P = self.pack(X)
        P = self.run_packed(P, ticks, threads)
        return self.unpack(P, X.shape[1])
