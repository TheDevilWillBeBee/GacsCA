"""CUDA execution backend for a front candidate (same netlist, same ROM).

The kernel body is generated from the compiled netlist exactly as the C
backend's scalar word step: one thread evaluates 64 sites per u64 word, Pi is
looked up only where `arrive` is set. A single persistent block advances all
ticks with __syncthreads() between them (rings of at most 1024 words =
65,536 sites). It is an execution backend for the same fixed rule, compared
against the C kernel on every call path in tests; it has no depth input.
"""
import ctypes
import hashlib
import os
import subprocess
import numpy as np
from .machine import BUILD, _c_source

NVCC = '/usr/local/cuda/bin/nvcc'


def _cuda_source(cand):
    src = _c_source(cand)
    # Keep only the scalar word step and its helpers; make them device code.
    head, rest = src.split('static void word_step1', 1)
    body, _ = rest.split('static void word_step4', 1)
    helpers = head.split('static inline V ldv')[0]
    helpers = helpers.replace('#include <omp.h>\n', '')
    helpers = helpers.replace('typedef u64 V __attribute__((vector_size(32)));\n', '')
    helpers = helpers.replace('static inline u64 shl_in', '__device__ static inline u64 shl_in')
    kernel = '__device__ static void word_step1' + body
    kernel = kernel.replace('__builtin_ctzll(arr)', '(__ffsll((long long)arr) - 1)')
    out = [helpers, kernel]
    out.append('''
extern "C" __global__ void run_block(u64* A, u64* B, int NW, const uint32_t* rom, long ticks) {
  u64* X = A; u64* Y = B;
  for (long t = 0; t < ticks; t++) {
    for (int w = threadIdx.x; w < NW; w += blockDim.x) word_step1(X, Y, NW, w, rom);
    __syncthreads();
    u64* T = X; X = Y; Y = T;
  }
  if (X != A) {
    for (int i = threadIdx.x; i < W * NW; i += blockDim.x) A[i] = X[i];
  }
}

extern "C" int fr_run(unsigned long long* host, int NW, const unsigned int* rom_host, int rom_words,
                      long ticks, int threads, float* ms) {
  size_t bytes = (size_t)W * NW * sizeof(u64);
  u64 *A, *B; uint32_t* R;
  if (cudaMalloc(&A, bytes) || cudaMalloc(&B, bytes) || cudaMalloc(&R, rom_words * 4)) return 1;
  cudaMemcpy(A, host, bytes, cudaMemcpyHostToDevice);
  cudaMemcpy(R, rom_host, rom_words * 4, cudaMemcpyHostToDevice);
  cudaEvent_t e0, e1; cudaEventCreate(&e0); cudaEventCreate(&e1);
  cudaEventRecord(e0);
  run_block<<<1, threads>>>(A, B, NW, R, ticks);
  cudaEventRecord(e1); cudaEventSynchronize(e1);
  cudaEventElapsedTime(ms, e0, e1);
  int err = (int)cudaGetLastError();
  cudaMemcpy(host, A, bytes, cudaMemcpyDeviceToHost);
  cudaFree(A); cudaFree(B); cudaFree(R);
  return err;
}
''')
    return '#include <stdint.h>\n#include <string.h>\n' + '\n'.join(out)


class CudaKernel:
    def __init__(self, cand):
        self.cand = cand
        src = _cuda_source(cand)
        tag = hashlib.sha256(src.encode()).hexdigest()[:16]
        os.makedirs(BUILD, exist_ok=True)
        cu = os.path.join(BUILD, f'front_cuda_{tag}.cu')
        so = os.path.join(BUILD, f'front_cuda_{tag}.so')
        if not os.path.exists(so):
            with open(cu, 'w') as fh:
                fh.write(src)
            tmp = so + f'.tmp{os.getpid()}'
            subprocess.run([NVCC, '-O3', '-arch=sm_80', '-shared', '-Xcompiler', '-fPIC',
                            '-maxrregcount=128', cu, '-o', tmp], check=True)
            os.replace(tmp, so)
        self.lib = ctypes.CDLL(so)
        self.lib.fr_run.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_int,
                                    ctypes.c_long, ctypes.c_int, ctypes.POINTER(ctypes.c_float)]
        self.source_sha256 = hashlib.sha256(src.encode()).hexdigest()
        self.so_path = so
        self.last_ms = None

    def run_packed(self, P, ticks, threads=256):
        P = np.ascontiguousarray(P, dtype=np.uint64).copy()
        NW = P.shape[1]
        assert NW <= 1024 * 64
        ms = ctypes.c_float()
        rom = np.ascontiguousarray(self.cand.rom, dtype=np.uint32)
        err = self.lib.fr_run(P.ctypes.data, NW, rom.ctypes.data, rom.size, int(ticks),
                              int(min(threads, 1024)), ctypes.byref(ms))
        if err:
            raise RuntimeError(f'CUDA error {err}')
        self.last_ms = ms.value
        return P
