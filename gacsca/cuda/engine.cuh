// ---------------------------------------------------------------- track engine (Report/design_selfsim.md)
// State words: 0 addr, 1 age, 2 flags. Packed16: word 3 is simage|simaddr<<16,
// tracks start at 4. Wide: words 3,4 are simage,simaddr, tracks start at 5.
// Copy r of cell x holds the track bits of cell x + (r - h), h = (R-1)/2.
#define NWMAX 3
#define OPK_RESET 17
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
    int t_hold, t_busup;   // HOLD track; BUS track index of the simulated level (same registry)
    int reg_lo, reg_hi;    // level-0 register-load window (repair suspended)
    int reg_bits, tw0;
    int nested_bits, nested_base;
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

#include "interp.cuh"

// Apply the ops scheduled at age a to cell ky (index into the 11-cell window).  V: repaired
// track words for window cells [NWMAX each]; addr[]: addresses; P: output words for cell ky.
// simage/simaddr: registers of the window cells (for the interpretation ops); regs_out: the
// own cell's registers (only updated when ky == 5, by BUSLATCH_INT).
__device__ void apply_ops_cell(int ky, const uint32_t* V, const int* addr, int computed_addr, int a, uint32_t* P,
                               const EngineCfg& E, const int* __restrict__ ops,
                               const int* __restrict__ age_ptr, const int* __restrict__ op_idx,
                               const ICtx& I, const int* simage, const int* simaddr, int g2, int sa2, int* regs_out) {
    for (int w = 0; w < E.NW; w++) P[w] = V[ky * NWMAX + w];
    if (a < 0 || a >= E.U) return;
    int s = age_ptr[a], e = age_ptr[a + 1];
    // Redundant computation uses the holder's clock, address and registers.
    const int ay = (addr[5] + ky - 5 + E.Q) % E.Q;
    const int g1 = simage[5], sa1 = simaddr[5];
    for (int q = s; q < e; q++) {
        const int* op = ops + (size_t)op_idx[q] * OPW;
        int kind = op[0], lo = op[3], hi = op[4], dst = op[5], src = op[6], src2 = op[7], src3 = op[8];
        int param = op[9], param2 = op[10], skind = op[11];
        bool inr = (ay >= lo && ay < hi);
        if (kind == OPK_MOV && param2) {
            int computed_ay = (computed_addr + ky - 5 + E.Q) % E.Q;
            inr = computed_ay >= lo && computed_ay < hi;
        }
        const uint32_t* Vy = V + ky * NWMAX;
        int tau = a - op[1];
        if (kind == OPK_RESET) {
            if (inr) {
                for (int t = dst; t < param; t++) sb(P, t, 0);
                if (param2 && ky == 5 && regs_out != nullptr) {
                    regs_out[0] = regs_out[1] = 0;
                    if (E.nested_bits) regs_out[2] = regs_out[3] = 0;
                }
            }
            continue;
        }
        if (kind >= OPK_IINIT) {
            if (!inr) continue;
            Op1 o1 = load_op(op);
            switch (kind) {
                case OPK_IINIT: {
                    int r, t, c; if (cell_geom(I, E.R, E.NT, ay, r, t, c) && c == param) {
                        int z = ky - (param2 ? 0 : param); if (z >= 0 && z <= 10) sb(P, dst, gb(V + z * NWMAX, src));
                    }
                } break;
                case OPK_ILATCH: interp_ilatch(P, V, ky, ay, g1, sa1, o1, tau, I, E.R, E.NT, E.t_sig, E.t_acc, E.t_info, E.t_hold, E.t_busup, E.D, g2, sa2); break;
                case OPK_ICHAIN: interp_ichain(P, Vy, ay, g1, sa1, o1, I, E.R, E.NT, E.t_sig, E.t_acc); break;
                case OPK_IBC: interp_ibc(P, Vy, ay, g1, sa1, o1, I, E.R, E.NT, E.t_sig, E.t_acc); break;
                case OPK_IEVAL: interp_ieval(P, Vy, ay, g1, sa1, o1, I, E.R, E.NT, E.t_sig, E.t_acc, E.t_info, E.t_hold, g2, sa2); break;
                case OPK_IWF: interp_iwf(P, Vy, ay, g1, sa1, I, E.t_hold); break;
                case OPK_REGWIN: sb(P, dst, (g1 >= I.rw_lo && g1 < I.rw_hi) ? 1 : 0); break;
                case OPK_BUSLATCH_INT: if (ky == 5 && regs_out != nullptr) {
                    if (param < 0 || param > 1 || (param == 1 && !E.nested_bits)) break;
                    // own registers: latch bit i of the Hold AGE/ADDR fields riding on the bus
                    for (int f = 0; f < 2; f++) {
                        int lo_f = param == 0 ? (f == 0 ? I.age_lo : I.addr_lo) : (f == 0 ? I.simage_lo : I.simaddr_lo);
                        int hi_f = param == 0 ? (f == 0 ? I.age_hi : I.addr_hi) : (f == 0 ? I.simage_hi : I.simaddr_hi);
                        for (int i = 0; i < hi_f - lo_f; i++) {
                            int tt, j;
                            if (!latch_time(ay, lo_f + i, param2, E.D, tt, j) || tt != tau) continue;
                            int z = ky - param2 * j; if (z < 0 || z > 10) continue;
                            int v = gb(V + z * NWMAX, src);
                            int rf = 2 * param + f;
                            regs_out[rf] = (regs_out[rf] & ~(1 << i)) | (v << i);
                        }
                    }
                } break;
            }
            continue;
        }
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
                    int az = ay - d;
                    if (az >= lo && az < hi) val = gb(V + z * NWMAX, src);
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
                        int az = ay - k;
                        if (gb(V + z * NWMAX, E.t_sig) == 1 && az >= lo - 1) {
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
                    int az = ay + sh;
                    if (gb(V + z * NWMAX, E.t_sig) == 1 && az >= lo && az < hi) {
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
                                   const int* __restrict__ op_idx, EngineCfg E, RuleParams P, NoiseParams N, ICtx I) {
    int x = blockIdx.x * blockDim.x + threadIdx.x;
    int b = blockIdx.y;
    if (x >= E.L || b >= E.B) return;
    const int L = E.L, W = E.W, Q = E.Q, NW = E.NW;
    const int h = (R - 1) / 2;
    const uint32_t* row = in + (size_t)b * L * W;
    int addr[11], age[11], f1[11], f2[11], wf1[11], wf2[11], sg[11], sa[11];
    int sg2[11], sa2[11];
    uint32_t T[11][R][NWMAX];
    for (int k = 0; k < 11; k++) {
        int y = x + (k - 5); y = (y % L + L) % L;
        const uint32_t* c = row + (size_t)y * W;
        addr[k] = (int)c[0]; age[k] = (int)c[1];
        uint32_t fl = c[2];
        f1[k] = fl & F1_BIT ? 1 : 0; f2[k] = fl & F2_BIT ? 1 : 0;
        wf1[k] = fl & WF1_BIT ? 1 : 0; wf2[k] = fl & WF2_BIT ? 1 : 0;
        uint32_t reg_mask = (1u << E.reg_bits) - 1u;
        sg[k] = (int)(c[3] & reg_mask);
        sa[k] = E.reg_bits == 16 ? (int)(c[3] >> 16) : (int)(c[4] & reg_mask);
        if (E.nested_bits) {
            uint32_t mask2 = (1u << E.nested_bits) - 1u;
            sg2[k] = c[E.nested_base] & mask2;
            sa2[k] = E.nested_bits == 16 ? c[E.nested_base] >> 16 : c[E.nested_base + 1] & mask2;
        }
        for (int r = 0; r < R; r++) for (int w = 0; w < NWMAX; w++) T[k][r][w] = (w < NW) ? c[E.tw0 + r * NW + w] : 0u;
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
    int ADDR, AGE, F1, F2, SIMAGE, SIMADDR;
    local_rule(addr, age, f1, f2, wf1, wf2, sg, sa, P, ADDR, AGE, F1, F2, SIMAGE, SIMADDR);
    if (age[5] >= E.reg_lo && age[5] < E.reg_hi) { SIMAGE = sg[5]; SIMADDR = sa[5]; }
    int regs[4] = {SIMAGE, SIMADDR, 0, 0};
    if (E.nested_bits) {
        // Same colony-restricted repair contract, independently for the second pair.
        int aa, ag, ff1, ff2;
        local_rule(addr, age, f1, f2, wf1, wf2, sg2, sa2, P, aa, ag, ff1, ff2, regs[2], regs[3]);
        if (age[5] >= E.reg_lo && age[5] < E.reg_hi) { regs[2] = sg2[5]; regs[3] = sa2[5]; }
    }
    // ops for the R cells whose copies x holds
    uint32_t newT[R][NWMAX];
    for (int r = 0; r < R; r++) {
        int ky = 5 + (r - h);
        apply_ops_cell(ky, &V[0][0], addr, ADDR, age[5], newT[r], E, ops, age_ptr, op_idx, I, sg, sa,
                       E.nested_bits ? sg2[5] : 0, E.nested_bits ? sa2[5] : 0, ky == 5 ? regs : nullptr);
    }
    SIMAGE = regs[0]; SIMADDR = regs[1];
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
        uint64_t hh = noise_word(N, b, x);
        if (noise_hit(hh, N)) {
            uint64_t h2 = splitmix64(hh), h3 = splitmix64(h2), h4 = splitmix64(h3), h5 = splitmix64(h4);
            ADDR = (int)(h2 % (uint64_t)Q); AGE = (int)(h3 % (uint64_t)E.U); FL = (uint32_t)(h4 & 15ull);
            uint32_t reg_mask = (1u << E.reg_bits) - 1u;
            SIMAGE = (int)((uint32_t)h5 & reg_mask);
            SIMADDR = E.reg_bits == 16 ? (int)((h5 >> 16) & 0xFFFF) : (int)((uint32_t)(h5 >> 32) & reg_mask);
            uint64_t g = h5;
            for (int r = 0; r < R; r++) for (int w = 0; w < NW; w++) { g = splitmix64(g); newT[r][w] = (uint32_t)g; }
            if (E.nested_bits) {
                // Append the extra draw so all legacy field/track draws stay identical.
                g = splitmix64(g);
                uint32_t mask2 = (1u << E.nested_bits) - 1u;
                regs[2] = (uint32_t)g & mask2;
                regs[3] = E.nested_bits == 16 ? (g >> 16) & 0xFFFF : (g >> 32) & mask2;
            }
        }
    }
    uint32_t* o = out + ((size_t)b * L + x) * W;
    o[0] = (uint32_t)ADDR; o[1] = (uint32_t)AGE; o[2] = FL;
    if (E.reg_bits == 16) o[3] = (uint32_t)SIMAGE | ((uint32_t)SIMADDR << 16);
    else { o[3] = (uint32_t)SIMAGE; o[4] = (uint32_t)SIMADDR; }
    if (E.nested_bits == 16) o[E.nested_base] = (uint32_t)regs[2] | ((uint32_t)regs[3] << 16);
    else if (E.nested_bits) { o[E.nested_base] = regs[2]; o[E.nested_base + 1] = regs[3]; }
    for (int r = 0; r < R; r++) for (int w = 0; w < NW; w++) o[E.tw0 + r * NW + w] = newT[r][w];
}
