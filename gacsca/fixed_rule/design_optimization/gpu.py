"""Batched CUDA simulator for front candidates, with Gray-style error injection.

The per-site transition is generated from the candidate's compiled netlist
exactly as the C backend's scalar word step (64 sites per u64 word; Pi looked
up only where `arrive` is set). It is an execution backend for the same fixed
rule and is compared bit-for-bit with the C kernel in tests.

Layout: `nrings` independent rings of the same length, one CUDA block per
ring, one persistent kernel launch for many ticks with __syncthreads()
between ticks. Rings can carry different initial states and different error
configurations, e.g. ring 0 fault-free as a reference.

Errors ("malicious demon", Gray section 5.1): an error at (site, tick)
replaces the site's *whole* new state by random bits. Per ring:
  * E0 grid: space-time is tiled by G x G cells (G >= 26); each cell holds
    one error at a hashed offset in [0, G-25)^2, on one site or (with the
    pair probability) two adjacent sites. Distinct errors are then at least
    25 apart in space or time, i.e. every error is a level-0 error in Gray's
    sense ((24, 24)-separated from the rest); G = 50 is close to the densest
    such pattern. Cells cut by the ring end are skipped.
  * Boxes: up to 8 space-time boxes [x0, x0+w) x [t0, t0+h) in which each
    site-tick is an error with probability p (p=1: every site randomized at
    every tick of the box). A 200 x 200 box is a level-1 error in Gray's
    sense; boxes of colony or multi-colony size are higher-level errors.
Time is the absolute tick index passed by the host, so runs can be split.
"""
import ctypes
import hashlib
import os
import subprocess
import numpy as np
from .machine import BUILD

NVCC = '/usr/local/cuda/bin/nvcc'
MAXB = 32
VALUE_MODES = ('random', 'zero', 'one', 'invert', 'freeze', 'copy')


class Box(ctypes.Structure):
    _fields_ = [('x0', ctypes.c_int), ('w', ctypes.c_int), ('t0', ctypes.c_long),
                ('h', ctypes.c_long), ('p16', ctypes.c_uint)]


class NoiseCfg(ctypes.Structure):
    _fields_ = [('seed', ctypes.c_ulonglong), ('e0_grid', ctypes.c_int),
                ('e0_pair16', ctypes.c_uint), ('nbox', ctypes.c_int), ('mode', ctypes.c_int),
                ('shift', ctypes.c_int), ('box', Box * MAXB)]


def noise(seed=0, e0_grid=0, e0_pair=0.5, boxes=(), mode='random', shift_sites=0):
    """boxes: iterable of (x0, w, t0, h, p).

    mode: the value an error site takes (after the rule's own update):
      random   seeded random bits (depending only on seed, site and tick);
      zero, one  every bit 0 / 1 (stuck-at);
      invert   every bit of the correct new state flipped;
      freeze   the site keeps its previous state (it misses the update);
      copy     the current state of the site shift_sites further along the
               ring (shift_sites = Q: the cell with the same Address in the
               next colony, a plausible but wrong state)."""
    c = NoiseCfg()
    c.mode = VALUE_MODES.index(mode)
    assert shift_sites % 32 == 0
    c.shift = int(shift_sites // 32)
    c.seed = seed & ((1 << 64) - 1)
    c.e0_grid = int(e0_grid)
    assert c.e0_grid == 0 or c.e0_grid >= 26
    c.e0_pair16 = int(e0_pair * 65535)
    boxes = list(boxes)
    assert len(boxes) <= MAXB
    c.nbox = len(boxes)
    for i, (x0, w, t0, h, pr) in enumerate(boxes):
        c.box[i] = Box(int(x0), int(w), int(t0), int(h), int(pr * 65535))
    return c


def _order(comp, roots, done, n_in):
    """Iterative DFS postorder over gate nodes reachable from roots, skipping
    nodes in `done` (updated in place). Keeps live ranges short."""
    out = []
    for r in roots:
        if r < n_in or r in done:
            continue
        stack = [(r, False)]
        while stack:
            x, expanded = stack.pop()
            if x < n_in or x in done:
                continue
            if expanded:
                done.add(x)
                out.append(x)
                continue
            stack.append((x, True))
            _, a, b = comp.gates[x - n_in]
            stack.append((b, False))
            stack.append((a, False))
    return out


def _source(cand, order='dfs'):
    """CUDA source: 32 sites per thread word (native 32-bit logic), the same
    netlist as the C backend. Input bits are loaded at first use and gates are
    emitted in DFS postorder from the outputs, with the Pi lookup placed right
    after the cone of (psel, arrive, laddr)."""
    comp, p = cand.comp, cand.p
    idx = comp.index
    n_in = 2 + len(comp.inputs)
    name_of = {node: nm for nm, node in idx.items()}
    dep = [False] * comp.n_nodes
    for nm, node in idx.items():
        if nm[0] == 'I':
            dep[node] = True
    for g, (op, a, b) in enumerate(comp.gates):
        dep[n_in + g] = dep[a] or dep[b]
    psel_nodes = [comp.outputs[('psel', i)] for i in range(p.PW)]
    arrive_node = comp.outputs[('arrive', 0)]
    laddr_nodes = ([comp.outputs[('laddr', i)] for i in range(p.k)]
                   if ('laddr', 0) in comp.outputs else None)
    roots_a = psel_nodes + [arrive_node] + (laddr_nodes or [])
    assert not any(dep[x] for x in roots_a)
    addr_rows = [cand.row[('addr', i)] for i in range(p.k)]
    I_nodes = [idx.get(('I', i)) for i in range(p.IW)]
    y_nodes = [comp.outputs[('y', f, i)] for (f, i) in cand.rows]
    done = set()
    if order == 'dfs':
        seq_a = _order(comp, roots_a, done, n_in)
        seq_b = _order(comp, y_nodes, done, n_in)
    else:
        seq_a = [n_in + g for g in range(len(comp.gates)) if not dep[n_in + g]]
        seq_b = [n_in + g for g in range(len(comp.gates)) if dep[n_in + g]]
    ops = {0: '&', 1: '|', 2: '^'}
    L = []
    emit = L.append
    loaded = set()

    def v(x):
        if x == 0:
            return '0u'
        if x == 1:
            return '0xFFFFFFFFu'
        if x < n_in and x not in loaded:
            nm = name_of[x]
            assert nm[0] == 'x', nm
            _, j, f, i = nm
            r = cand.row[(f, i)]
            base = f'X[{r} * NW + '
            if j == 0:
                expr = f'{base}w]'
            elif j > 0:
                expr = f'(({base}w] >> {j}) | ({base}wr] << {32 - j}))'
            else:
                expr = f'(({base}w] << {-j}) | ({base}wl] >> {32 + j}))'
            emit(f'  const wd v{x} = {expr};')
            loaded.add(x)
        return f'v{x}'

    out_rows = {}
    for r, x in enumerate(y_nodes):
        out_rows.setdefault(x, []).append(r)
    stored = set()

    def store(x):
        # outputs are written as soon as they are defined (short live ranges)
        for r in out_rows.get(x, ()):
            emit(f'  Y[{r} * NW + w] = {v(x)};')
            stored.add(r)

    def gates(seq):
        for x in seq:
            op, a, b = comp.gates[x - n_in]
            va, vb = v(a), v(b)
            emit(f'  const wd v{x} = {va} {ops[op]} {vb};')
            store(x)

    emit('typedef uint32_t wd;')
    emit('typedef unsigned long long u64;')
    emit(f'#define W {cand.W}')
    emit(f'#define NPT {p.NPT}')
    emit('__device__ __forceinline__ void word_step(const wd* __restrict__ X, wd* __restrict__ Y, int NW, int w,')
    emit('                                          const uint32_t* __restrict__ rom) {')
    emit('  const int wl = (w == 0) ? NW - 1 : w - 1, wr = (w + 1 == NW) ? 0 : w + 1;')
    gates(seq_a)
    for x in roots_a:
        v(x)
    emit('  ' + 'wd ' + ', '.join(f'v{x} = 0u' for x in I_nodes if x is not None) + ';')
    for x in I_nodes:
        if x is not None:
            loaded.add(x)
    emit('  {')
    emit(f'    wd arr = {v(arrive_node)};')
    emit('    while (arr) {')
    emit('      int t = __ffs(arr) - 1; arr &= arr - 1;')
    emit('      unsigned a = 0, ps = 0;')
    if laddr_nodes is not None:
        for i, x in enumerate(laddr_nodes):
            emit(f'      a |= (({v(x)} >> t) & 1u) << {i};')
    else:
        for i, r in enumerate(addr_rows):
            emit(f'      a |= ((X[{r} * NW + w] >> t) & 1u) << {i};')
    for i, x in enumerate(psel_nodes):
        emit(f'      ps |= (({v(x)} >> t) & 1u) << {i};')
    emit('      const uint32_t word = rom[a * NPT + ps];')
    for i, x in enumerate(I_nodes):
        if x is not None:
            emit(f'      v{x} |= ((word >> {i}) & 1u) << t;')
    emit('    }')
    emit('  }')
    for x in I_nodes:
        if x is not None:
            store(x)
    gates(seq_b)
    for r in range(len(cand.rows)):
        if r not in stored:
            emit(f'  Y[{r} * NW + w] = {v(y_nodes[r])};')
    emit('}')
    kernel = '\n'.join(L) + '\n'
    tail = r'''
#define MAXB 32
struct Box { int x0, w; long t0, h; unsigned int p16; };
struct NoiseCfg { unsigned long long seed; int e0_grid; unsigned int e0_pair16; int nbox; int mode; int shift;
                  Box box[MAXB]; };

__device__ static inline u64 mix64(u64 z) {
  z += 0x9E3779B97F4A7C15ULL;
  z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
  z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
  return z ^ (z >> 31);
}

/* Error sites among the 64 sites of 64-bit word w64 at tick t. The pattern
   and the random replacement bits depend only on (config, site, tick): not on
   the ring index or the kernel word size. */
__device__ static u64 error_mask(const NoiseCfg& c, int ring, int NW64, int w, long t) {
  u64 mask = 0;
  long x0 = 64L * w;
  if (c.e0_grid > 0) {
    /* cell (cx, ct) of the G x G tiling holds one error at an offset in
       [0, G-25)^2; cells cut by the ring end are skipped, so distinct errors
       are at least 25 apart in space or in time (Chebyshev), wrap included */
    int G = c.e0_grid;
    long ct = t / G, ot_in = t % G, span = G - 25;
    for (long cx = x0 / G; cx * G < x0 + 64 && (cx + 1) * G <= 64L * NW64; cx++) {
      u64 h = mix64(c.seed ^ mix64(((u64)cx << 24) ^ (u64)ct));
      long ox = (long)(h % span), ot = (long)((h >> 20) % span);
      if (ot != ot_in) continue;
      long xs = cx * G + ox;
      int pair = ((h >> 40) & 0xFFFF) < c.e0_pair16;
      for (int d = 0; d <= pair; d++) {
        long x = xs + d;
        if (x >= x0 && x < x0 + 64 && x < 64L * NW64) mask |= 1ULL << (x - x0);
      }
    }
  }
  for (int b = 0; b < c.nbox; b++) {
    const Box& B = c.box[b];
    if (t < B.t0 || t >= B.t0 + B.h) continue;
    long lo = B.x0 > x0 ? B.x0 : x0, hi = (B.x0 + B.w) < (x0 + 64) ? (B.x0 + B.w) : (x0 + 64);
    if (lo >= hi) continue;
    u64 m = (hi - lo == 64) ? ~0ULL : (((1ULL << (hi - lo)) - 1) << (lo - x0));
    if (B.p16 < 65535) {               /* independent Bernoulli(p) per site */
      u64 keep = 0;
      for (int q = 0; q < 16; q++) {
        u64 r = mix64(c.seed ^ mix64(((u64)b << 44) ^ ((u64)t << 12) ^ ((u64)w << 4) ^ (u64)q));
        for (int k = 0; k < 4; k++)
          if (((r >> (16 * k)) & 0xFFFF) < B.p16) keep |= 1ULL << (4 * q + k);
      }
      m &= keep;
    }
    mask |= m;
  }
  return mask;
}

__device__ __forceinline__ void tick_word(const wd* X, wd* Y, int NW64, int w, const uint32_t* rom,
                                          const NoiseCfg& c, int ring, long t) {
  const int NW = 2 * NW64;
  word_step(X, Y, NW, w, rom);
  if (c.e0_grid > 0 || c.nbox > 0) {
    const int w64 = w >> 1, half = w & 1;
    const wd m = (wd)(error_mask(c, ring, NW64, w64, t) >> (32 * half));
    if (m) {
      for (int r = 0; r < W; r++) {
        const wd y = Y[(size_t)r * NW + w];
        wd v;
        switch (c.mode) {
          case 0: v = (wd)(mix64(c.seed ^ mix64(((u64)t << 24) ^ ((u64)w64 << 10) ^ (u64)r))
                           >> (32 * half)); break;
          case 1: v = 0; break;
          case 2: v = ~(wd)0; break;
          case 3: v = ~y; break;
          case 4: v = X[(size_t)r * NW + w]; break;
          default: v = X[(size_t)r * NW + (w + c.shift) % NW]; break;
        }
        Y[(size_t)r * NW + w] = (y & ~m) | (v & m);
      }
    }
  }
}

/* Block mode: one block per ring. Thread i handles 32-bit words i,
   i + blockDim, ... of its ring; __syncthreads() separates ticks. */
extern "C" __global__ void __launch_bounds__(256, 1) k_run(u64* A, u64* B, int NW64, const uint32_t* rom,
                                 long t0, long ticks, const NoiseCfg* cfg, int nrows, const int* rows,
                                 int stride, u64* snap, int nrings) {
  const int ring = blockIdx.x, NW = 2 * NW64;
  wd* X = (wd*)(A + (size_t)ring * W * NW64);
  wd* Y = (wd*)(B + (size_t)ring * W * NW64);
  __shared__ NoiseCfg c;
  if (threadIdx.x == 0) c = cfg[ring];
  __syncthreads();
  for (long i = 0; i < ticks; i++) {
    for (int w = threadIdx.x; w < NW; w += blockDim.x)
      tick_word(X, Y, NW64, w, rom, c, ring, t0 + i);
    __syncthreads();
    wd* T = X; X = Y; Y = T;
    if (stride > 0 && (i + 1) % stride == 0) {
      const long s = (i + 1) / stride - 1;
      wd* S = (wd*)snap;
      for (int w = threadIdx.x; w < NW; w += blockDim.x)
        for (int j = 0; j < nrows; j++)
          S[((size_t)(s * nrings + ring) * nrows + j) * NW + w] = X[(size_t)rows[j] * NW + w];
    }
  }
  wd* D = (wd*)(A + (size_t)ring * W * NW64);
  if (X != D)
    for (int i = threadIdx.x; i < W * NW; i += blockDim.x) D[i] = X[i];
}

/* Grid mode (cooperative launch): all words of all rings are spread over the
   whole grid; grid.sync() separates ticks. Used for large rings. */
extern "C" __global__ void __launch_bounds__(256, 1) k_run_grid(u64* A, u64* B, int NW64,
                                 const uint32_t* rom, long t0, long ticks, const NoiseCfg* cfg,
                                 int nrows, const int* rows, int stride, u64* snap, int nrings) {
  cg::grid_group grid = cg::this_grid();
  const int NW = 2 * NW64;
  const long total = (long)nrings * NW;
  const long gid = (long)blockIdx.x * blockDim.x + threadIdx.x, gsz = (long)gridDim.x * blockDim.x;
  int flip = 0;
  for (long i = 0; i < ticks; i++) {
    const wd* Xb = (const wd*)(flip ? B : A);
    wd* Yb = (wd*)(flip ? A : B);
    for (long g = gid; g < total; g += gsz) {
      const int ring = (int)(g / NW), w = (int)(g % NW);
      const size_t off = (size_t)ring * W * NW;
      tick_word(Xb + off, Yb + off, NW64, w, rom, cfg[ring], ring, t0 + i);
    }
    grid.sync();
    flip ^= 1;
    if (stride > 0 && (i + 1) % stride == 0) {
      const long s = (i + 1) / stride - 1;
      wd* S = (wd*)snap;
      for (long g = gid; g < total; g += gsz) {
        const int ring = (int)(g / NW), w = (int)(g % NW);
        for (int j = 0; j < nrows; j++)
          S[((size_t)(s * nrings + ring) * nrows + j) * NW + w] = Yb[(size_t)ring * W * NW + (size_t)rows[j] * NW + w];
      }
    }
  }
  if (flip) {
    wd* D = (wd*)A; const wd* Sx = (const wd*)B;
    for (long g = gid; g < total * W; g += gsz) D[g] = Sx[g];
  }
}

extern "C" __global__ void k_masks(const NoiseCfg* cfg, int ring, int NW64, long t0, int nt, u64* out) {
  for (long g = (long)blockIdx.x * blockDim.x + threadIdx.x; g < (long)nt * NW64; g += (long)gridDim.x * blockDim.x)
    out[g] = error_mask(*cfg, ring, NW64, (int)(g % NW64), t0 + g / NW64);
}

struct Sim { int nrings, NW; u64 *A, *B; uint32_t* rom; NoiseCfg* cfg; };

/* Error masks of one ring for ticks t0..t0+nt-1 (for tests and receipts). */
extern "C" int sim_error_masks(const NoiseCfg* host_cfg, int ring, int NW64, long t0, int nt,
                               unsigned long long* out_host) {
  NoiseCfg* d; u64* o;
  cudaMalloc(&d, sizeof(NoiseCfg)); cudaMalloc(&o, (size_t)nt * NW64 * 8);
  cudaMemcpy(d, host_cfg, sizeof(NoiseCfg), cudaMemcpyHostToDevice);
  k_masks<<<256, 128>>>(d, ring, NW64, t0, nt, o);
  cudaMemcpy(out_host, o, (size_t)nt * NW64 * 8, cudaMemcpyDeviceToHost);
  cudaFree(d); cudaFree(o);
  return (int)cudaGetLastError();
}

extern "C" void* sim_create(int nrings, int NW, const unsigned int* rom_host, int rom_words) {
  Sim* s = new Sim; s->nrings = nrings; s->NW = NW;
  size_t bytes = (size_t)nrings * W * NW * sizeof(u64);
  if (cudaMalloc(&s->A, bytes) || cudaMalloc(&s->B, bytes) || cudaMalloc(&s->rom, rom_words * 4)
      || cudaMalloc(&s->cfg, nrings * sizeof(NoiseCfg))) return 0;
  cudaMemcpy(s->rom, rom_host, rom_words * 4, cudaMemcpyHostToDevice);
  cudaMemset(s->cfg, 0, nrings * sizeof(NoiseCfg));
  return s;
}
extern "C" void sim_upload(void* h, const unsigned long long* host) {
  Sim* s = (Sim*)h; cudaMemcpy(s->A, host, (size_t)s->nrings * W * s->NW * 8, cudaMemcpyHostToDevice);
}
extern "C" void sim_download(void* h, unsigned long long* host) {
  Sim* s = (Sim*)h; cudaMemcpy(host, s->A, (size_t)s->nrings * W * s->NW * 8, cudaMemcpyDeviceToHost);
}
extern "C" void sim_set_noise(void* h, const NoiseCfg* host) {
  Sim* s = (Sim*)h; cudaMemcpy(s->cfg, host, s->nrings * sizeof(NoiseCfg), cudaMemcpyHostToDevice);
}
extern "C" int sim_max_grid_blocks(int threads) {
  int per_sm = 0, dev = 0, sms = 0;
  cudaOccupancyMaxActiveBlocksPerMultiprocessor(&per_sm, k_run_grid, threads, 0);
  cudaGetDevice(&dev);
  cudaDeviceGetAttribute(&sms, cudaDevAttrMultiProcessorCount, dev);
  return per_sm * sms;
}
extern "C" int sim_run(void* h, long t0, long ticks, int threads, int grid_blocks, int nrows,
                       const int* rows_host, int stride, unsigned long long* snap_host, float* ms) {
  Sim* s = (Sim*)h;
  int* rows = 0; u64* snap = 0; size_t snap_bytes = 0;
  if (stride > 0 && nrows > 0) {
    cudaMalloc(&rows, nrows * sizeof(int));
    cudaMemcpy(rows, rows_host, nrows * sizeof(int), cudaMemcpyHostToDevice);
    snap_bytes = (size_t)(ticks / stride) * s->nrings * nrows * s->NW * 8;
    if (cudaMalloc(&snap, snap_bytes)) return -1;
  }
  cudaEvent_t e0, e1; cudaEventCreate(&e0); cudaEventCreate(&e1);
  cudaEventRecord(e0);
  if (grid_blocks <= 0) {
    k_run<<<s->nrings, threads>>>(s->A, s->B, s->NW, s->rom, t0, ticks, s->cfg, nrows, rows,
                                   stride, snap, s->nrings);
  } else {
    int NW64 = s->NW, nr = s->nrings;
    void* args[] = {&s->A, &s->B, &NW64, &s->rom, &t0, &ticks, &s->cfg, &nrows, &rows, &stride,
                    &snap, &nr};
    cudaLaunchCooperativeKernel((void*)k_run_grid, grid_blocks, threads, args, 0, 0);
  }
  cudaEventRecord(e1); cudaEventSynchronize(e1);
  cudaEventElapsedTime(ms, e0, e1);
  int err = (int)cudaGetLastError();
  if (snap) { cudaMemcpy(snap_host, snap, snap_bytes, cudaMemcpyDeviceToHost); cudaFree(snap); cudaFree(rows); }
  cudaEventDestroy(e0); cudaEventDestroy(e1);
  return err;
}
extern "C" void sim_destroy(void* h) {
  Sim* s = (Sim*)h; cudaFree(s->A); cudaFree(s->B); cudaFree(s->rom); cudaFree(s->cfg); delete s;
}
'''
    return ('#include <stdint.h>\n#include <cooperative_groups.h>\nnamespace cg = cooperative_groups;\n'
            + kernel + tail)


def build(cand, maxreg=None, order='dfs'):
    src = _source(cand, order)
    flags = ['-O3', '-arch=sm_80', '-shared', '-Xcompiler', '-fPIC']
    if maxreg:
        flags.append(f'-maxrregcount={maxreg}')
    tag = hashlib.sha256((src + ' '.join(flags)).encode()).hexdigest()[:16]
    os.makedirs(BUILD, exist_ok=True)
    cu = os.path.join(BUILD, f'gpu_{tag}.cu')
    so = os.path.join(BUILD, f'gpu_{tag}.so')
    if not os.path.exists(so):
        with open(cu, 'w') as fh:
            fh.write(src)
        tmp = so + f'.tmp{os.getpid()}'
        subprocess.run([NVCC] + flags + [cu, '-o', tmp], check=True)
        os.replace(tmp, so)
    lib = ctypes.CDLL(so)
    lib.sim_create.restype = ctypes.c_void_p
    lib.sim_create.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_int]
    for fn in ('sim_upload', 'sim_download', 'sim_set_noise'):
        getattr(lib, fn).argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    lib.sim_run.argtypes = [ctypes.c_void_p, ctypes.c_long, ctypes.c_long, ctypes.c_int, ctypes.c_int,
                            ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p,
                            ctypes.POINTER(ctypes.c_float)]
    lib.sim_max_grid_blocks.argtypes = [ctypes.c_int]
    lib.sim_error_masks.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_long,
                                    ctypes.c_int, ctypes.c_void_p]
    lib.sim_destroy.argtypes = [ctypes.c_void_p]
    return lib, hashlib.sha256(src.encode()).hexdigest()


class GpuSim:
    """nrings rings of `colonies` colonies each, resident on the GPU.

    mode 'block': one CUDA block per ring (small rings, many experiments).
    mode 'grid': cooperative launch over the whole GPU (large rings, e.g. a
    two-level ring of Q^2 sites). 'auto' picks grid when a ring has more
    32-bit words than one block has threads.
    """

    def __init__(self, cand, nrings, colonies, threads=None, maxreg=None, order='dfs', mode='auto'):
        self.cand, self.p = cand, cand.p
        self.nrings = nrings
        self.N = colonies * cand.p.Q
        assert self.N % 64 == 0
        self.NW = self.N // 64
        self.lib, self.source_sha256 = build(cand, maxreg, order)
        if mode == 'auto':
            mode = 'grid' if 2 * self.NW > 256 else 'block'
        self.mode = mode
        if mode == 'block':
            self.threads = threads or min(2 * self.NW, 256)
            self.grid_blocks = 0
        else:
            self.threads = threads or 128
            maxb = self.lib.sim_max_grid_blocks(self.threads)
            need = -(-(2 * self.NW * nrings) // self.threads)
            self.grid_blocks = max(1, min(maxb, need))
        rom = np.ascontiguousarray(cand.rom, dtype=np.uint32)
        self.h = self.lib.sim_create(nrings, self.NW, rom.ctypes.data, rom.size)
        if not self.h:
            raise RuntimeError('CUDA allocation failed')
        self.t = 0
        self.last_ms = 0.0

    def __del__(self):
        if getattr(self, 'h', None):
            self.lib.sim_destroy(self.h)
            self.h = None

    def set_state(self, packed, t=0):
        """packed: (nrings, W, NW) uint64, or (W, NW) broadcast to every ring."""
        P = np.asarray(packed, dtype=np.uint64)
        if P.ndim == 2:
            P = np.broadcast_to(P, (self.nrings,) + P.shape)
        P = np.ascontiguousarray(P)
        assert P.shape == (self.nrings, self.cand.W, self.NW)
        self.lib.sim_upload(self.h, P.ctypes.data)
        self.t = t

    def state(self):
        P = np.empty((self.nrings, self.cand.W, self.NW), dtype=np.uint64)
        self.lib.sim_download(self.h, P.ctypes.data)
        return P

    def set_noise(self, cfgs):
        cfgs = list(cfgs)
        assert len(cfgs) == self.nrings
        arr = (NoiseCfg * self.nrings)(*cfgs)
        self.lib.sim_set_noise(self.h, ctypes.cast(arr, ctypes.c_void_p))

    def error_masks(self, cfg, ring, t0, nt):
        """Boolean (nt, N) array: the sites that ring `ring` corrupts at ticks
        t0..t0+nt-1 under noise config `cfg` (as the kernel computes them)."""
        out = np.empty((nt, self.NW), dtype=np.uint64)
        c = NoiseCfg(); ctypes.pointer(c)[0] = cfg
        err = self.lib.sim_error_masks(ctypes.byref(c), ring, self.NW, t0, nt, out.ctypes.data)
        if err:
            raise RuntimeError(f'CUDA error {err}')
        return np.unpackbits(out.view(np.uint8).reshape(nt, -1), axis=1, bitorder='little').astype(bool)

    def run(self, ticks, rows=None, stride=0):
        """Advance every ring by `ticks`. If rows and stride are given, returns
        snapshots of those rows every `stride` ticks: array
        (ticks//stride, nrings, len(rows), NW) uint64."""
        ms = ctypes.c_float()
        snap = None
        if rows is not None and stride > 0:
            rows_arr = np.ascontiguousarray(rows, dtype=np.int32)
            snap = np.empty((ticks // stride, self.nrings, len(rows_arr), self.NW), dtype=np.uint64)
            err = self.lib.sim_run(self.h, self.t, ticks, self.threads, self.grid_blocks, len(rows_arr),
                                   rows_arr.ctypes.data, stride, snap.ctypes.data, ctypes.byref(ms))
        else:
            err = self.lib.sim_run(self.h, self.t, ticks, self.threads, self.grid_blocks, 0, None, 0,
                                   None, ctypes.byref(ms))
        if err:
            raise RuntimeError(f'CUDA error {err}')
        self.t += ticks
        self.last_ms = ms.value
        return snap
