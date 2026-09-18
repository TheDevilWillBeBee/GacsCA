// ---------------------------------------------------------------- track engine (Report/design_selfsim.md)
// State words: 0 addr, 1 age, 2 flags (f1,f2,wf1,wf2), then R*NW track words: copy r, word w at 3 + r*NW + w.
// Copy r of cell x holds the track bits of cell x + (r - h), h = (R-1)/2.
#define NWMAX 2
#define OPK_CONST 0
#define OPK_MOV 1
#define OPK_BITOP 2
#define OPK_SHIFT 3
#define OPK_RSHIFT 4
#define OPK_SWEEP_INIT 5
#define OPK_SWEEP 6
#define OPK_BCAST_INIT 7
#define OPK_BCAST 8
#define SK_EQC 0
#define SK_EQF 1
#define SK_ORF 2
#define SK_ANDF 3
#define SK_ADDC 4
#define SK_LTC 5
#define OPW 12   // ints per op: kind,t0,t1,lo,hi,dst,src,src2,src3,param,param2,skind

struct EngineCfg {
    int Q, U, L, B, W, R, NW, NT, D;
    int t_sig, t_acc, t_info, t_maill, t_mailr;
    int tlo, thi;      // trickle-down window
    int wipe;
};

__device__ __forceinline__ int gb(const uint32_t* w, int t) { return (w[t >> 5] >> (t & 31)) & 1; }
__device__ __forceinline__ void sb(uint32_t* w, int t, int v) {
    uint32_t m = 1u << (t & 31);
    if (v) w[t >> 5] |= m; else w[t >> 5] &= ~m;
}

template <int R>
__device__ __forceinline__ uint32_t majR(const uint32_t* c) {   // bitwise majority of R words
    if (R == 3) return (c[0] & c[1]) | (c[0] & c[2]) | (c[1] & c[2]);
    // R == 5: full adders
    uint32_t s1 = c[0] ^ c[1] ^ c[2], c1 = (c[0] & c[1]) | (c[0] & c[2]) | (c[1] & c[2]);
    uint32_t s2 = c[3] ^ c[4] ^ s1, c2 = (c[3] & c[4]) | (c[3] & s1) | (c[4] & s1);
    return (c1 & c2) | ((c1 ^ c2) & s2);
}

// chain step of a sweep: returns cout, sets out (may be unused)
__device__ __forceinline__ int chain(int skind, int cin, int sv, int s2v, int kb, int& out) {
    out = 0;
    switch (skind) {
        case SK_EQC: return cin & (sv == kb);
        case SK_EQF: return cin & (sv == s2v);
        case SK_ORF: return cin | sv;
        case SK_ANDF: return cin & sv;
        case SK_ADDC: out = sv ^ kb ^ cin; return (sv & kb) | (sv & cin) | (kb & cin);
        case SK_LTC: return ((1 - sv) & kb) | ((sv == kb) & cin);
    }
    return 0;
}

// Apply the ops scheduled at age a to cell ky (index into the 11-cell window).  V: repaired
// track words for window cells [NWMAX each]; addr[]: addresses; P: output words for cell ky.
__device__ void apply_ops_cell(int ky, const uint32_t* V, const int* addr, int a, uint32_t* P,
                               const EngineCfg& E, const int* __restrict__ ops,
                               const int* __restrict__ age_ptr, const int* __restrict__ op_idx) {
    for (int w = 0; w < E.NW; w++) P[w] = V[ky * NWMAX + w];
    if (a < 0 || a >= E.U) return;
    int s = age_ptr[a], e = age_ptr[a + 1];
    const int ay = addr[ky];
    for (int q = s; q < e; q++) {
        const int* op = ops + (size_t)op_idx[q] * OPW;
        int kind = op[0], lo = op[3], hi = op[4], dst = op[5], src = op[6], src2 = op[7], src3 = op[8];
        int param = op[9], param2 = op[10], skind = op[11];
        bool inr = (ay >= lo && ay < hi);
        const uint32_t* Vy = V + ky * NWMAX;
        switch (kind) {
            case OPK_CONST: if (inr) sb(P, dst, param); break;
            case OPK_MOV: if (inr) sb(P, dst, gb(Vy, src)); break;
            case OPK_BITOP: if (inr) {
                int b1 = gb(Vy, src), b2 = src2 >= 0 ? gb(Vy, src2) : 0, b3 = src3 >= 0 ? gb(Vy, src3) : 0;
                sb(P, dst, (param >> ((b1 << 2) | (b2 << 1) | b3)) & 1);
            } break;
            case OPK_SHIFT: if (inr) {
                int d = param, z = ky - d;
                int val = param2;
                if (z >= 0 && z <= 10) {
                    int az = addr[z];
                    if (az == ay - d && az >= lo && az < hi) val = gb(V + z * NWMAX, src);
                }
                sb(P, dst, val);
            } break;
            case OPK_RSHIFT: if (inr) { int z = ky - param; sb(P, dst, gb(V + z * NWMAX, src)); } break;
            case OPK_SWEEP_INIT: if (inr) { sb(P, E.t_sig, 1); sb(P, dst, param); } break;
            case OPK_BCAST_INIT: if (inr) sb(P, dst, gb(Vy, src)); break;
            case OPK_SWEEP: {
                bool tokrange = (ay >= lo - 1 && ay < hi);
                if (!tokrange) break;
                bool keep = (ay == hi - 1) && gb(Vy, E.t_sig);
                bool acted = false;
                if (inr) {
                    for (int k = 1; k <= E.D && !acted; k++) {
                        int z = ky - k; if (z < 0) break;
                        int az = addr[z];
                        if (gb(V + z * NWMAX, E.t_sig) == 1 && az == ay - k && az >= lo - 1) {
                            acted = true;
                            int cin = gb(V + z * NWMAX, E.t_acc), out = 0;
                            for (int m = 1; m < k; m++) {
                                int zz = z + m, azz = ay - (k - m);
                                int kb = (azz - lo >= 0 && azz - lo < 31) ? (param >> (azz - lo)) & 1 : 0;
                                int sv = src >= 0 ? gb(V + zz * NWMAX, src) : 0, s2v = src2 >= 0 ? gb(V + zz * NWMAX, src2) : 0;
                                cin = chain(skind, cin, sv, s2v, kb, out);
                            }
                            int kb = (ay - lo >= 0 && ay - lo < 31) ? (param >> (ay - lo)) & 1 : 0;
                            int sv = src >= 0 ? gb(Vy, src) : 0, s2v = src2 >= 0 ? gb(Vy, src2) : 0;
                            int cout = chain(skind, cin, sv, s2v, kb, out);
                            bool last = (k == E.D) || (ay == hi - 1);
                            sb(P, E.t_sig, last ? 1 : 0);
                            sb(P, E.t_acc, cout);
                            if (dst >= 0) sb(P, dst, out);
                        }
                    }
                }
                if (!acted) sb(P, E.t_sig, keep ? 1 : 0);
            } break;
            case OPK_BCAST: if (inr && gb(Vy, E.t_sig) == 0) {
                int dir = (param == 0) ? -1 : param;
                for (int k = 1; k <= E.D; k++) {
                    int sh = dir < 0 ? k : -k; int z = ky + sh;
                    if (z < 0 || z > 10) continue;
                    int az = addr[z];
                    if (gb(V + z * NWMAX, E.t_sig) == 1 && az == ay + sh && az >= lo && az < hi) {
                        sb(P, dst, gb(V + z * NWMAX, dst)); sb(P, E.t_sig, 1); break;
                    }
                }
            } break;
        }
    }
}

template <int R>
__global__ void engine_step_kernel(const uint32_t* __restrict__ in, uint32_t* __restrict__ out,
                                   const int* __restrict__ ops, const int* __restrict__ age_ptr,
                                   const int* __restrict__ op_idx, EngineCfg E, RuleParams P, NoiseParams N) {
    int x = blockIdx.x * blockDim.x + threadIdx.x;
    int b = blockIdx.y;
    if (x >= E.L || b >= E.B) return;
    const int L = E.L, W = E.W, Q = E.Q, NW = E.NW;
    const int h = (R - 1) / 2;
    const uint32_t* row = in + (size_t)b * L * W;
    int addr[11], age[11], f1[11], f2[11], wf1[11], wf2[11];
    uint32_t T[11][R][NWMAX];
    for (int k = 0; k < 11; k++) {
        int y = x + (k - 5); y = (y % L + L) % L;
        const uint32_t* c = row + (size_t)y * W;
        addr[k] = (int)c[0]; age[k] = (int)c[1];
        uint32_t fl = c[2];
        f1[k] = fl & F1_BIT ? 1 : 0; f2[k] = fl & F2_BIT ? 1 : 0;
        wf1[k] = fl & WF1_BIT ? 1 : 0; wf2[k] = fl & WF2_BIT ? 1 : 0;
        for (int r = 0; r < R; r++) for (int w = 0; w < NWMAX; w++) T[k][r][w] = (w < NW) ? c[3 + r * NW + w] : 0u;
    }
    // repaired values for window cells [h, 10-h]: bit of cell k, copy r held by cell k - (r-h)
    uint32_t V[11][NWMAX];
    for (int k = 0; k < 11; k++) for (int w = 0; w < NWMAX; w++) V[k][w] = 0u;
    for (int k = h; k <= 10 - h; k++) {
        for (int w = 0; w < NW; w++) {
            uint32_t c[R];
            for (int r = 0; r < R; r++) c[r] = T[k - (r - h)][r][w];
            V[k][w] = majR<R>(c);
        }
    }
    int ADDR, AGE, F1, F2;
    local_rule(addr, age, f1, f2, wf1, wf2, P, ADDR, AGE, F1, F2);
    // ops for the R cells whose copies x holds
    uint32_t newT[R][NWMAX];
    for (int r = 0; r < R; r++) {
        int ky = 5 + (r - h);
        apply_ops_cell(ky, &V[0][0], addr, age[ky], newT[r], E, ops, age_ptr, op_idx);
    }
    if (E.wipe && F1) {
        for (int r = 0; r < R; r++) { sb(newT[r], E.t_maill, 0); sb(newT[r], E.t_mailr, 0); }
        if (ADDR != addr[5]) for (int r = 0; r < R; r++) for (int w = 0; w < NWMAX; w++) newT[r][w] = 0u;
    }
    // Workspace flags from computed Address/Age and current repaired Info at addresses Q-3 / 3
    int WF1 = 0, WF2 = 0;
    bool in_win = (AGE >= E.tlo) && (AGE < E.thi);
    if (in_win && ADDR >= Q - 5 && ADDR <= Q - 1) {
        int o = (Q - 3) - ADDR;                      // in [-2, 2]
        if (gb(V[5 + o], E.t_info)) WF1 = 1;
    }
    if (in_win && ADDR >= 0 && ADDR <= 4 && !F1) {
        int o = 3 - ADDR;                            // in [-1, 3]
        if (gb(V[5 + o], E.t_info)) WF2 = 1;
    }
    uint32_t FL = (F1 ? F1_BIT : 0) | (F2 ? F2_BIT : 0) | (WF1 ? WF1_BIT : 0) | (WF2 ? WF2_BIT : 0);
    if (N.eps > 0.f) {
        uint64_t hh = splitmix64(N.seed ^ splitmix64(((uint64_t)N.t << 40) ^ ((uint64_t)b << 28) ^ (uint64_t)x));
        if (u01(hh) < N.eps) {
            uint64_t h2 = splitmix64(hh), h3 = splitmix64(h2), h4 = splitmix64(h3);
            ADDR = (int)(h2 % (uint64_t)Q); AGE = (int)(h3 % (uint64_t)E.U); FL = (uint32_t)(h4 & 15ull);
            uint64_t g = h4;
            for (int r = 0; r < R; r++) for (int w = 0; w < NW; w++) { g = splitmix64(g); newT[r][w] = (uint32_t)g; }
        }
    }
    uint32_t* o = out + ((size_t)b * L + x) * W;
    o[0] = (uint32_t)ADDR; o[1] = (uint32_t)AGE; o[2] = FL;
    for (int r = 0; r < R; r++) for (int w = 0; w < NW; w++) o[3 + r * NW + w] = newT[r][w];
}
