#include <cuda_runtime.h>
#include <cstdint>
#include <utility>
#include "generated.h"
using u64 = uint64_t;

struct World {size_t n; u64 *a, *b, *work;};

__global__ void aos_to_soa(const u64* src, u64* dst, size_t n) {
 size_t i = (size_t)blockIdx.x * blockDim.x + threadIdx.x;
 if (i >= n * FIELDS) return;
 size_t site = i / FIELDS, field = i % FIELDS;
 dst[field * n + site] = src[i];
}

__global__ void soa_to_aos(const u64* src, u64* dst, size_t n) {
 size_t i = (size_t)blockIdx.x * blockDim.x + threadIdx.x;
 if (i >= n * FIELDS) return;
 size_t site = i / FIELDS, field = i % FIELDS;
 dst[i] = src[field * n + site];
}

__global__ void step(World w) {
 size_t worker = (size_t)blockIdx.x * blockDim.x + threadIdx.x;
 if (worker >= WORKERS) return;
 u64* in = w.work + worker;
 u64* tmp = in + USED_INPUTS * WORKERS;
 for (size_t pos = worker; pos < w.n; pos += WORKERS) {
  size_t sources[15];
  size_t left = pos >= 7 ? pos - 7 : pos + w.n - 7;
  #pragma unroll
  for (int j = 0; j < 15; ++j) {
   size_t source = left + j;
   sources[j] = source < w.n ? source : source - w.n;
  }
  gather_inputs(w.a, w.n, sources, in);
  fixed_local(in, w.b, pos, w.n, tmp);
 }
}

extern "C" void fr_free(World* w) {
 if (!w) return;
 cudaFree(w->a); cudaFree(w->b); cudaFree(w->work); delete w;
}

extern "C" int fr_create(size_t n, const u64* raw, u64 budget,
                          World** out, u64* bytes) {
 if (!out || !bytes || !raw || n < 15 || n > (1u << 24)) return 1;
 *out = nullptr;
 *bytes = 8 * (2 * n * FIELDS + WORKSPACE_WORDS);
 u64 staging_bytes = 8 * n * FIELDS;
 if (*bytes + staging_bytes > budget) return 2;
 World* w = new World{}; w->n = n;
 #define ALLOC(name,count) if (cudaMalloc(&w->name, (count) * sizeof(u64)) != cudaSuccess) {fr_free(w); return 3;}
 ALLOC(a,n*FIELDS) ALLOC(b,n*FIELDS) ALLOC(work,WORKSPACE_WORDS)
 #undef ALLOC
 u64* staging = nullptr;
 if (cudaMalloc(&staging, staging_bytes) != cudaSuccess) {fr_free(w); return 3;}
 bool okay = cudaMemcpy(staging, raw, staging_bytes, cudaMemcpyHostToDevice) == cudaSuccess;
 if (okay) {
  size_t count = n * FIELDS;
  aos_to_soa<<<(count + 255) / 256, 256>>>(staging, w->a, n);
  okay = cudaDeviceSynchronize() == cudaSuccess;
 }
 cudaFree(staging);
 if (!okay) {fr_free(w); return 4;}
 *out = w; return 0;
}

extern "C" int fr_run(World* w, u64 ticks) {
 if (!w || ticks > (1u << 20)) return 1;
 for (u64 t = 0; t < ticks; ++t) {
  step<<<(WORKERS + 255) / 256, 256>>>(*w);
  if (cudaGetLastError() != cudaSuccess) return 2;
  std::swap(w->a, w->b);
 }
 return cudaDeviceSynchronize() == cudaSuccess ? 0 : 3;
}

extern "C" int fr_read(World* w, u64* out) {
 if (!w || !out) return 1;
 size_t count = w->n * FIELDS;
 u64* staging = nullptr;
 if (cudaMalloc(&staging, count * sizeof(u64)) != cudaSuccess) return 2;
 soa_to_aos<<<(count + 255) / 256, 256>>>(w->a, staging, w->n);
 bool okay = cudaDeviceSynchronize() == cudaSuccess;
 if (okay) okay = cudaMemcpy(out, staging, count * sizeof(u64), cudaMemcpyDeviceToHost) == cudaSuccess;
 cudaFree(staging);
 return okay ? 0 : 3;
}
