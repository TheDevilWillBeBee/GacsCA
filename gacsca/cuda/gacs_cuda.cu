// CUDA implementation of Gray's level-0 rules (local structure + Flags) for Gacs' automaton.
// Semantics: gacsca/level0_spec.py.  State layout: uint32 tensor (B, L, W), W >= 3 words per cell:
//   word 0: Address, word 1: Age, word 2: flag bits (bit0 Flag1, bit1 Flag2, bit2 Workspace.Flag1,
//   bit3 Workspace.Flag2).  Further words are reserved for the simulation structure.
#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>
#include <cuda_runtime.h>
#include <stdexcept>
#include <cstdint>

namespace nb = nanobind;
using namespace nb::literals;

using U32Array3D = nb::ndarray<uint32_t, nb::shape<-1, -1, -1>, nb::c_contig, nb::device::cuda>;
using U8Array2D = nb::ndarray<uint8_t, nb::shape<-1, -1>, nb::c_contig, nb::device::cuda>;

#define cuda_check(call)                                                                           \
    do {                                                                                           \
        cudaError_t error = call;                                                                  \
        if (error != cudaSuccess)                                                                  \
            throw std::runtime_error(std::string("CUDA error at ") + __FILE__ + ":" +              \
                                     std::to_string(__LINE__) + " - " + cudaGetErrorString(error)); \
    } while (0)

#define RANGE 5
#define F1_BIT 1u
#define F2_BIT 2u
#define WF1_BIT 4u
#define WF2_BIT 8u

struct RuleParams {
    int Q, U, L, B, W;
    int flag1_ii_in_colony;   // 1: Gray (R(x)&C(x)); 0: Masumori (R(x))
    int flag2_iii_current;    // 0: Gray (computed Age); 1: Masumori (current Age)
    int plurality;            // 0: strict majority (>=3 of 5); 1: plurality
};

struct NoiseParams {
    float eps;
    uint64_t seed;
    int t;
    int addr_mode;   // 0: uniform in [0,Q) / [0,U); 1: uniform over bit width
    int use_mask;    // 1: multiply by mask[b, x]
};

// ---- hash-based RNG (splitmix64) ----
__device__ __forceinline__ uint64_t splitmix64(uint64_t z) {
    z += 0x9E3779B97F4A7C15ull;
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
    return z ^ (z >> 31);
}
__device__ __forceinline__ float u01(uint64_t h) { return (float)(h >> 40) * (1.0f / 16777216.0f); }

// majority among 5 values with Gray's convention
__device__ __forceinline__ int majority5(const int v[5], int current, int plurality) {
    int best = -1, nbest = 0, second = 0;
    for (int i = 0; i < 5; i++) {
        int c = 0;
        for (int j = 0; j < 5; j++) c += (v[j] == v[i]);
        if (c > nbest) { second = nbest; nbest = c; best = v[i]; }
        else if (c == nbest && v[i] != best) { second = c; }
    }
    if (!plurality) return (nbest >= 3) ? best : current;
    return (second == nbest) ? current : best;
}

__device__ __forceinline__ int modq(int a, int q) { int r = a % q; return r < 0 ? r + q : r; }


// ---------------------------------------------------------------- Gray Sec 5.2 local rule
// inputs indexed k = 0..10 for sites x-5..x+5 (k=5 is x).  Outputs the computed values.
__device__ __forceinline__ void local_rule(const int* addr, const int* age, const int* f1, const int* f2,
                                           const int* wf1, const int* wf2, const RuleParams& P,
                                           int& ADDR, int& AGE, int& F1, int& F2) {
    const int Q = P.Q, U = P.U;
    #define RR(i) (5 + (i))
    #define LL(i) (5 - (i))
    const int cur_addr = addr[5], cur_age = age[5];
    int votes[5];
    for (int i = 1; i <= 5; i++) votes[i - 1] = modq(addr[RR(i)] - i, Q);
    int v = -1, nv = 0;
    for (int i = 0; i < 5; i++) { int c = 0; for (int j = 0; j < 5; j++) c += (votes[j] == votes[i]); if (c > nv) { nv = c; v = votes[i]; } }
    const bool exists = nv >= 3;
    if (!exists) v = -1;
    bool inR[6], inL[6];
    for (int i = 1; i <= 5; i++) { inR[i] = exists && (v + i <= Q - 1); inL[i] = exists && (v - i >= 0); }
    bool incons = !exists;
    if (exists) { int bad = 0; for (int i = 1; i <= 5; i++) bad += (inL[i] && addr[LL(i)] != v - i); if (bad >= 3) incons = true; }
    int agesR[5]; for (int i = 1; i <= 5; i++) agesR[i - 1] = age[RR(i)];
    int a = 0, na = 0;
    for (int i = 0; i < 5; i++) { int c = 0; for (int j = 0; j < 5; j++) c += (agesR[j] == agesR[i]); if (c > na) { na = c; a = agesR[i]; } }
    if (na < 3) incons = true;
    else if (exists) { int d = 0; for (int i = 1; i <= 5; i++) d += (inL[i] && age[LL(i)] != a); if (d >= 3) incons = true; }
    int cnt_ii = 0, cnt_ii_all = 0, cnt_iii = exists ? wf1[5] : 0, cnt_a = 0;
    for (int i = 1; i <= 5; i++) {
        cnt_ii += inR[i] && f1[RR(i)]; cnt_ii_all += f1[RR(i)];
        cnt_iii += (inR[i] && wf1[RR(i)]) + (inL[i] && wf1[LL(i)]);
        cnt_a += inR[i] && f1[RR(i)];
    }
    bool c_ii = (P.flag1_ii_in_colony ? cnt_ii : cnt_ii_all) >= 3;
    bool c_iii = cnt_iii >= 3;
    if (f1[5] == 0) F1 = (incons || c_ii || c_iii) ? 1 : 0;
    else F1 = (!incons && !c_iii && cnt_a <= 1) ? 0 : 1;
    int agesL[5]; for (int i = 1; i <= 5; i++) agesL[i - 1] = age[LL(i)];
    int age_from_L = (majority5(agesL, cur_age, P.plurality) + 1) % U;
    int cnt_i = 0, cnt_all = 0, cnt_iv = exists ? wf2[5] : 0, zerosLC = 0;
    for (int i = 1; i <= 5; i++) {
        cnt_i += inL[i] && f2[LL(i)]; cnt_all += f2[LL(i)];
        cnt_iv += (inR[i] && wf2[RR(i)]) + (inL[i] && wf2[LL(i)]);
        zerosLC += inL[i] && !f2[LL(i)];
    }
    bool d_i = cnt_i >= 4, d_ii = (F1 == 1) && cnt_all >= 4;
    bool d_iii = !exists && (((P.flag2_iii_current ? cur_age : age_from_L) % 16) == 0);
    bool d_iv = cnt_iv >= 3;
    if (f2[5] == 0) F2 = (d_i || d_ii || d_iii || d_iv) ? 1 : 0;
    else { bool a2 = (F1 == 0) && zerosLC == 0, b2 = (F1 == 1) && cnt_all == 0; F2 = (!d_iii && !d_iv && (a2 || b2)) ? 0 : 1; }
    bool vote_right = exists && (F1 == 0 || F2 == 1);
    int av[5], gv[5];
    for (int i = 1; i <= 5; i++) {
        if (vote_right) { av[i - 1] = modq(addr[RR(i)] - i, Q); gv[i - 1] = age[RR(i)]; }
        else { av[i - 1] = modq(addr[LL(i)] + i, Q); gv[i - 1] = age[LL(i)]; }
    }
    ADDR = majority5(av, cur_addr, P.plurality);
    AGE = (majority5(gv, cur_age, P.plurality) + 1) % U;
    #undef RR
    #undef LL
}

__global__ void level0_step_kernel(const uint32_t* __restrict__ in, uint32_t* __restrict__ out,
                                   const uint8_t* __restrict__ mask, RuleParams P, NoiseParams N) {
    int x = blockIdx.x * blockDim.x + threadIdx.x;
    int b = blockIdx.y;
    if (x >= P.L || b >= P.B) return;
    const int L = P.L, W = P.W, Q = P.Q, U = P.U;
    const uint32_t* row = in + (size_t)b * L * W;
    int addr[11], age[11], f1[11], f2[11], wf1[11], wf2[11];
    for (int k = 0; k < 11; k++) {
        int y = x + (k - 5); y = (y % L + L) % L;
        const uint32_t* c = row + (size_t)y * W;
        addr[k] = (int)c[0]; age[k] = (int)c[1];
        uint32_t fl = c[2];
        f1[k] = fl & F1_BIT ? 1 : 0; f2[k] = fl & F2_BIT ? 1 : 0;
        wf1[k] = fl & WF1_BIT ? 1 : 0; wf2[k] = fl & WF2_BIT ? 1 : 0;
    }
    int ADDR, AGE, F1, F2;
    local_rule(addr, age, f1, f2, wf1, wf2, P, ADDR, AGE, F1, F2);
    uint32_t FL = (F1 ? F1_BIT : 0) | (F2 ? F2_BIT : 0);
    if (N.eps > 0.f) {
        uint64_t h = splitmix64(N.seed ^ splitmix64(((uint64_t)N.t << 40) ^ ((uint64_t)b << 28) ^ (uint64_t)x));
        bool hit = u01(h) < N.eps;
        if (N.use_mask) hit = hit && mask[(size_t)b * L + x];
        if (hit) {
            uint64_t h2 = splitmix64(h), h3 = splitmix64(h2), h4 = splitmix64(h3);
            int qa = Q, qu = U;
            if (N.addr_mode) { qa = 1; while (qa < Q) qa <<= 1; qu = 1; while (qu < U) qu <<= 1; }
            ADDR = (int)(h2 % (uint64_t)qa); AGE = (int)(h3 % (uint64_t)qu); FL = (uint32_t)(h4 & 15ull);
        }
    }
    uint32_t* o = out + ((size_t)b * L + x) * W;
    o[0] = (uint32_t)ADDR; o[1] = (uint32_t)AGE; o[2] = FL;
    for (int w = 3; w < W; w++) o[w] = row[(size_t)x * W + w];
}

#include "engine.cuh"

using I32Array1D = nb::ndarray<int32_t, nb::shape<-1>, nb::c_contig, nb::device::cuda>;
using I32Array2D = nb::ndarray<int32_t, nb::shape<-1, -1>, nb::c_contig, nb::device::cuda>;

void engine_step(U32Array3D in, U32Array3D out, I32Array2D ops, I32Array1D age_ptr, I32Array1D op_idx,
                 I32Array1D cfg, int flag1_ii_in_colony, int flag2_iii_current, int plurality,
                 float eps, uint64_t seed, int t) {
    // cfg (host-readable copy needed): pass as cuda tensor -> copy to host
    int c[32];
    cuda_check(cudaMemcpy(c, cfg.data(), sizeof(int) * std::min<size_t>(32, cfg.shape(0)), cudaMemcpyDeviceToHost));
    EngineCfg E;
    E.Q = c[0]; E.U = c[1]; E.R = c[2]; E.NW = c[3]; E.NT = c[4]; E.D = c[5];
    E.t_sig = c[6]; E.t_acc = c[7]; E.t_info = c[8]; E.t_maill = c[9]; E.t_mailr = c[10];
    E.tlo = c[11]; E.thi = c[12]; E.wipe = c[13];
    E.B = (int)in.shape(0); E.L = (int)in.shape(1); E.W = (int)in.shape(2);
    if (E.W != 3 + E.R * E.NW) throw std::runtime_error("state width mismatch");
    if (E.NW > NWMAX) throw std::runtime_error("too many tracks");
    if ((int)age_ptr.shape(0) != E.U + 1) throw std::runtime_error("age_ptr size must be U+1");
    RuleParams P{E.Q, E.U, E.L, E.B, E.W, flag1_ii_in_colony, flag2_iii_current, plurality};
    NoiseParams N{eps, seed, t, 0, 0};
    dim3 block(128), grid((E.L + 127) / 128, E.B);
    if (E.R == 3) engine_step_kernel<3><<<grid, block>>>(in.data(), out.data(), ops.data(), age_ptr.data(), op_idx.data(), E, P, N);
    else if (E.R == 5) engine_step_kernel<5><<<grid, block>>>(in.data(), out.data(), ops.data(), age_ptr.data(), op_idx.data(), E, P, N);
    else throw std::runtime_error("R must be 3 or 5");
    cuda_check(cudaGetLastError());
}

void level0_step(U32Array3D in, U32Array3D out, nb::object mask_obj, int Q, int U, int flag1_ii_in_colony,
                 int flag2_iii_current, int plurality, float eps, uint64_t seed, int t, int addr_mode) {
    RuleParams P{Q, U, (int)in.shape(1), (int)in.shape(0), (int)in.shape(2), flag1_ii_in_colony, flag2_iii_current, plurality};
    if (P.W < 3) throw std::runtime_error("state needs >= 3 words");
    if (out.shape(0) != in.shape(0) || out.shape(1) != in.shape(1) || out.shape(2) != in.shape(2))
        throw std::runtime_error("shape mismatch");
    NoiseParams N{eps, seed, t, addr_mode, 0};
    const uint8_t* mask = nullptr;
    if (!mask_obj.is_none()) {
        U8Array2D m = nb::cast<U8Array2D>(mask_obj);
        if ((int)m.shape(0) != P.B || (int)m.shape(1) != P.L) throw std::runtime_error("mask shape mismatch");
        mask = m.data(); N.use_mask = 1;
    }
    dim3 block(128), grid((P.L + 127) / 128, P.B);
    level0_step_kernel<<<grid, block>>>(in.data(), out.data(), mask, P, N);
    cuda_check(cudaGetLastError());
}

NB_MODULE(gacs_cuda, m) {
    m.def("engine_step", &engine_step, "in"_a, "out"_a, "ops"_a, "age_ptr"_a, "op_idx"_a, "cfg"_a,
          "flag1_ii_in_colony"_a, "flag2_iii_current"_a, "plurality"_a, "eps"_a, "seed"_a, "t"_a);
    m.def("level0_step", &level0_step, "in"_a, "out"_a, "mask"_a.none(), "Q"_a, "U"_a, "flag1_ii_in_colony"_a,
          "flag2_iii_current"_a, "plurality"_a, "eps"_a, "seed"_a, "t"_a, "addr_mode"_a);
}
