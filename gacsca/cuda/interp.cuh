// ---------------------------------------------------------------- interpretation phase (stage 2 tower)
// Mirrors gacsca/interp.py.  All quantities are for the cell ky of the 11-cell window.
#define OPK_IINIT 9
#define OPK_ILATCH 10
#define OPK_ICHAIN 11
#define OPK_IBC 12
#define OPK_IEVAL 13
#define OPK_IWF 14
#define OPK_BUSLATCH_INT 15
#define OPK_REGWIN 16

struct ICtx {
    int has;                         // interpretation enabled
    int b0, track_base, K, Qs, Us, D_up, JI;
    int addr_lo, addr_hi, age_lo, age_hi, wf1_pos, wf2_pos, simage_lo, simage_hi, simaddr_lo, simaddr_hi;
    int up_age_lo, up_age_hi, up_addr_lo, up_addr_hi;
    int trk_lo, trk_hi;              // trickle_up
    int rw_lo, rw_hi;                // regwin_up
    int t_vt, t_bus, t_sa, t_sb, t_sig[4], t_carry[4], t_bfound, t_bval, t_shsrc[3], t_s[3][3], t_blb, t_wfb, t_f1n;
    const int* ops_up; const int* age_ptr_up; const int* op_idx_up; int U_up;
};

struct Op1 { int kind, t0, t1, lo, hi, dst, src, src2, src3, param, param2, skind; };

__device__ __forceinline__ Op1 load_op(const int* o) {
    Op1 r; r.kind = o[0]; r.t0 = o[1]; r.t1 = o[2]; r.lo = o[3]; r.hi = o[4]; r.dst = o[5]; r.src = o[6]; r.src2 = o[7];
    r.src3 = o[8]; r.param = o[9]; r.param2 = o[10]; r.skind = o[11]; return r;
}

// active level-1 ops at simulated age g1 (at most 3)
__device__ __forceinline__ int active_ops_up(const ICtx& I, int g1, Op1* out) {
    if (g1 < 0 || g1 >= I.U_up) return 0;
    int s = I.age_ptr_up[g1], e = I.age_ptr_up[g1 + 1], n = 0;
    for (int q = s; q < e && n < 3; q++) out[n++] = load_op(I.ops_up + (size_t)I.op_idx_up[q] * OPW);
    return n;
}

__device__ __forceinline__ bool op_writes(const Op1& o, int t, int t_sig, int t_acc) {
    switch (o.kind) {
        case OPK_CONST: case OPK_MOV: case OPK_BITOP: case OPK_SHIFT: case OPK_RSHIFT: case OPK_BCAST_INIT: return t == o.dst;
        case OPK_SWEEP_INIT: return t == t_sig || t == o.dst;
        case OPK_SWEEP: return t == t_sig || t == t_acc || (o.dst >= 0 && t == o.dst);
        case OPK_BCAST: return t == o.dst || t == t_sig;
    }
    return false;
}

// pass step at which the bit at X passes cell p; j = neighbour offset to read (BUS[p - dir*j]); ok if it passes
__device__ __forceinline__ bool latch_time(int p, int X, int dirn, int D, int& tau, int& j) {
    int d = dirn > 0 ? p - X : X - p;
    if (d < 0) return false;
    j = d % D; tau = (d - j) / D; return true;
}

__device__ __forceinline__ int kbit_of(int c, int a) { return (a >= 0 && a < 31) ? (c >> a) & 1 : 0; }

__device__ __forceinline__ int chain_i(int skind, int cin, int sv, int s2v, int kb, int& out) { return chain(skind, cin, sv, s2v, kb, out); }

// geometry of cell ky: position q in the track range -> slot r, track t, offset c
__device__ __forceinline__ bool cell_geom(const ICtx& I, int R, int NT, int p, int& r, int& t, int& c) {
    int q = p - (I.b0 + I.track_base);
    if (q < 0 || q >= NT * R) { r = t = c = 0; return false; }
    r = q % R; t = q / R; c = r - (R - 1) / 2; return true;
}

// latch helper: cell ky wants bit X of the bus (offset o pass) at this tau -> target track in P
__device__ __forceinline__ void try_latch(uint32_t* P, const uint32_t* V, int ky, int p, int X, int dirn, int D, int tau,
                                          int t_bus, int target) {
    int tt, j;
    if (!latch_time(p, X, dirn, D, tt, j)) return;
    if (tt != tau) return;
    int z = ky - dirn * j;
    if (z < 0 || z > 10) return;
    sb(P, target, gb(V + z * NWMAX, t_bus));
}

__device__ void interp_ilatch(uint32_t* P, const uint32_t* V, int ky, int p, int g1, int simaddr, const Op1& op, int tau,
                              const ICtx& I, int R, int NT, int t_sig, int t_acc, int t_info, int t_busup, int D) {
    int o = op.param, dirn = op.param2;
    int r, t, c; bool inr = cell_geom(I, R, NT, p, r, t, c);
    int a1 = ((simaddr + c) % I.Qs + I.Qs) % I.Qs;
    Op1 ops1[3]; int n1 = active_ops_up(I, g1, ops1);
    int D1 = I.D_up;
    int oo = o - c;
    #define PH(tr) (I.b0 + I.track_base + (tr) * R + (R - 1) / 2)
    for (int i = 0; i < n1; i++) {
        const Op1& o1 = ops1[i];
        if (o1.kind == OPK_BUSLATCH_INT) {
            // writer cells: SIMAGE/SIMADDR field positions (c = 0 only)
            int tau1 = g1 - o1.t0, dir1 = o1.param2;
            for (int f = 0; f < 2; f++) {
                int plo = f == 0 ? I.simage_lo : I.simaddr_lo, phi = f == 0 ? I.simage_hi : I.simaddr_hi;
                int slo = f == 0 ? I.up_age_lo : I.up_addr_lo, shi = f == 0 ? I.up_age_hi : I.up_addr_hi;
                int w = min(phi - plo, shi - slo);
                if (p < plo || p >= plo + w) continue;
                int ii = p - plo, X1 = slo + ii;
                int d = dir1 * (simaddr - X1);
                if (d < 0) continue;
                int j1 = d % D1, tt1 = (d - j1) / D1;
                if (tt1 != tau1) continue;
                int rel = -dir1 * j1;
                if (rel != o) continue;
                try_latch(P, V, ky, p, PH(t_busup), dirn, D, tau, I.t_bus, I.t_blb);
            }
            continue;
        }
        if (!inr) continue;
        bool wr = op_writes(o1, t, t_sig, t_acc);
        if (!wr) continue;
        int k = o1.kind;
        if (k == OPK_MOV || k == OPK_BITOP || k == OPK_BCAST_INIT) {
            if (oo == 0) {
                if (o1.src >= 0) try_latch(P, V, ky, p, PH(o1.src), dirn, D, tau, I.t_bus, I.t_s[i][0]);
                if (o1.src2 >= 0) try_latch(P, V, ky, p, PH(o1.src2), dirn, D, tau, I.t_bus, I.t_s[i][1]);
                if (o1.src3 >= 0) try_latch(P, V, ky, p, PH(o1.src3), dirn, D, tau, I.t_bus, I.t_s[i][2]);
            }
        } else if (k == OPK_SHIFT || k == OPK_RSHIFT) {
            if (oo == -o1.param) try_latch(P, V, ky, p, PH(o1.src), dirn, D, tau, I.t_bus, I.t_shsrc[i]);
        } else if (k == OPK_SWEEP) {
            if (oo == 0) {
                if (o1.src >= 0) try_latch(P, V, ky, p, PH(o1.src), dirn, D, tau, I.t_bus, I.t_s[i][0]);
                if (o1.src2 >= 0) try_latch(P, V, ky, p, PH(o1.src2), dirn, D, tau, I.t_bus, I.t_s[i][1]);
                try_latch(P, V, ky, p, PH(t_sig), dirn, D, tau, I.t_bus, I.t_s[i][2]);
            }
            for (int kk = 1; kk <= D1; kk++) if (oo == -kk) {
                try_latch(P, V, ky, p, PH(t_sig), dirn, D, tau, I.t_bus, I.t_sig[kk]);
                try_latch(P, V, ky, p, PH(t_acc), dirn, D, tau, I.t_bus, I.t_carry[kk]);
            }
            for (int kk = 1; kk < D1; kk++) if (oo == -kk) {
                if (o1.src >= 0) try_latch(P, V, ky, p, PH(o1.src), dirn, D, tau, I.t_bus, I.t_s[i][0]);
                if (o1.src2 >= 0) try_latch(P, V, ky, p, PH(o1.src2), dirn, D, tau, I.t_bus, I.t_s[i][1]);
            }
        } else if (k == OPK_BCAST) {
            int dir1 = (o1.param == 0) ? -1 : o1.param;
            if (oo == 0) try_latch(P, V, ky, p, PH(t_sig), dirn, D, tau, I.t_bus, I.t_s[i][2]);
            for (int kk = 1; kk <= D1; kk++) {
                int sh = dir1 < 0 ? kk : -kk;
                if (oo == sh) {
                    try_latch(P, V, ky, p, PH(t_sig), dirn, D, tau, I.t_bus, I.t_sig[kk]);
                    try_latch(P, V, ky, p, PH(o1.dst), dirn, D, tau, I.t_bus, I.t_carry[kk]);
                }
            }
        }
    }
    // workspace-flag INFO latches
    if (p == I.wf1_pos && (I.Qs - 3) - simaddr == o) try_latch(P, V, ky, p, PH(t_info), dirn, D, tau, I.t_bus, I.t_wfb);
    if (p == I.wf2_pos && 3 - simaddr == o) try_latch(P, V, ky, p, PH(t_info), dirn, D, tau, I.t_bus, I.t_wfb);
    #undef PH
}

__device__ void interp_ichain(uint32_t* P, const uint32_t* Vy, int p, int g1, int simaddr, const Op1& op, const ICtx& I, int R, int NT, int t_sig, int t_acc) {
    int o = op.param; int r, t, c;
    if (!cell_geom(I, R, NT, p, r, t, c)) return;
    int a1 = ((simaddr + c) % I.Qs + I.Qs) % I.Qs;
    Op1 ops1[3]; int n1 = active_ops_up(I, g1, ops1);
    int D1 = I.D_up, oo = o - c;
    for (int i = 0; i < n1; i++) {
        const Op1& o1 = ops1[i];
        if (o1.kind != OPK_SWEEP) continue;
        if (!op_writes(o1, t, t_sig, t_acc)) continue;
        int sv = gb(Vy, I.t_s[i][0]), s2v = gb(Vy, I.t_s[i][1]);
        for (int kk = 2; kk <= D1; kk++) {
            if (!(oo < 0 && oo > -kk)) continue;
            int kb = kbit_of(o1.param, a1 + oo - o1.lo);
            int cin = gb(Vy, I.t_carry[kk]), out;
            int cout = chain_i(o1.skind, cin, sv, s2v, kb, out);
            sb(P, I.t_carry[kk], cout);
        }
    }
}

__device__ void interp_ibc(uint32_t* P, const uint32_t* Vy, int p, int g1, int simaddr, const Op1& op, const ICtx& I, int R, int NT, int t_sig, int t_acc) {
    int o = op.param; int r, t, c;
    if (!cell_geom(I, R, NT, p, r, t, c)) return;
    int a1 = ((simaddr + c) % I.Qs + I.Qs) % I.Qs;
    Op1 ops1[3]; int n1 = active_ops_up(I, g1, ops1);
    int D1 = I.D_up, oo = o - c;
    for (int i = 0; i < n1; i++) {
        const Op1& o1 = ops1[i];
        if (o1.kind != OPK_BCAST) continue;
        if (!op_writes(o1, t, t_sig, t_acc)) continue;
        int dir1 = (o1.param == 0) ? -1 : o1.param;
        for (int kk = 1; kk <= D1; kk++) {
            int sh = dir1 < 0 ? kk : -kk;
            if (oo != sh) continue;
            int sig = gb(Vy, I.t_sig[kk]), val = gb(Vy, I.t_carry[kk]), found = gb(Vy, I.t_bfound);
            bool inr = (a1 + sh >= o1.lo) && (a1 + sh < o1.hi);
            if (found == 0 && sig == 1 && inr) { sb(P, I.t_bval, val); sb(P, I.t_bfound, 1); }
        }
    }
}

__device__ void interp_ieval(uint32_t* P, const uint32_t* Vy, int p, int g1, int simaddr, const Op1& op, const ICtx& I,
                             int R, int NT, int t_sig, int t_acc, int t_hold) {
    int i = op.param;
    Op1 ops1[3]; int n1 = active_ops_up(I, g1, ops1);
    if (i >= n1) return;
    const Op1& o1 = ops1[i];
    int D1 = I.D_up;
    if (o1.kind == OPK_BUSLATCH_INT) {
        int tau1 = g1 - o1.t0, dir1 = o1.param2;
        for (int f = 0; f < 2; f++) {
            int plo = f == 0 ? I.simage_lo : I.simaddr_lo, phi = f == 0 ? I.simage_hi : I.simaddr_hi;
            int slo = f == 0 ? I.up_age_lo : I.up_addr_lo, shi = f == 0 ? I.up_age_hi : I.up_addr_hi;
            int w = min(phi - plo, shi - slo);
            if (p < plo || p >= plo + w) continue;
            int ii = p - plo, X1 = slo + ii;
            int d = dir1 * (simaddr - X1);
            if (d < 0) continue;
            int j1 = d % D1, tt1 = (d - j1) / D1;
            if (tt1 != tau1) continue;
            sb(P, t_hold, gb(Vy, I.t_blb));
        }
        return;
    }
    int r, t, c;
    if (!cell_geom(I, R, NT, p, r, t, c)) return;
    if (!op_writes(o1, t, t_sig, t_acc)) return;
    int a1 = ((simaddr + c) % I.Qs + I.Qs) % I.Qs;
    bool inr = (a1 >= o1.lo) && (a1 < o1.hi);
    int S0 = gb(Vy, I.t_s[i][0]), S1 = gb(Vy, I.t_s[i][1]), S2 = gb(Vy, I.t_s[i][2]);
    switch (o1.kind) {
        case OPK_CONST: if (inr) sb(P, t_hold, o1.param); break;
        case OPK_MOV: if (inr) sb(P, t_hold, S0); break;
        case OPK_BITOP: if (inr) sb(P, t_hold, (o1.param >> ((S0 << 2) | (S1 << 1) | S2)) & 1); break;
        case OPK_SHIFT: if (inr) {
            int d = o1.param; bool inside = (a1 - d >= o1.lo) && (a1 - d < o1.hi);
            sb(P, t_hold, inside ? gb(Vy, I.t_shsrc[i]) : o1.param2);
        } break;
        case OPK_RSHIFT: if (inr) sb(P, t_hold, gb(Vy, I.t_shsrc[i])); break;
        case OPK_SWEEP_INIT: if (inr) { if (t == t_sig) sb(P, t_hold, 1); if (t == o1.dst) sb(P, t_hold, o1.param); } break;
        case OPK_BCAST_INIT: if (inr) sb(P, t_hold, S0); break;
        case OPK_SWEEP: {
            int lo = o1.lo, hi = o1.hi;
            bool tokrange = (a1 >= lo - 1) && (a1 < hi);
            bool keep = (a1 == hi - 1) && (S2 == 1);
            bool acted = false; int out = 0, cout = 0; bool last = false;
            for (int kk = 1; kk <= D1 && !acted; kk++) {
                int sig = gb(Vy, I.t_sig[kk]);
                if (sig == 1 && a1 - kk >= lo - 1 && inr) {
                    acted = true;
                    int cin = gb(Vy, I.t_carry[kk]);
                    int kb = kbit_of(o1.param, a1 - lo);
                    cout = chain_i(o1.skind, cin, S0, S1, kb, out);
                    last = (kk == D1) || (a1 == hi - 1);
                }
            }
            if (t == t_sig && tokrange) sb(P, t_hold, acted ? (last ? 1 : 0) : (keep ? 1 : 0));
            if (acted && t == t_acc) sb(P, t_hold, cout);
            if (acted && o1.dst >= 0 && t == o1.dst) sb(P, t_hold, out);
        } break;
        case OPK_BCAST: {
            int found = gb(Vy, I.t_bfound), val = gb(Vy, I.t_bval);
            if (inr && S2 == 0 && found == 1) { if (t == o1.dst) sb(P, t_hold, val); if (t == t_sig) sb(P, t_hold, 1); }
        } break;
    }
}

__device__ void interp_iwf(uint32_t* P, const uint32_t* Vy, int p, int g1, int simaddr, const ICtx& I, int t_hold) {
    int A = simaddr, G = ((g1 + 1) % I.Us + I.Us) % I.Us;
    bool in_win = (G >= I.trk_lo) && (G < I.trk_hi);
    int wfb = gb(Vy, I.t_wfb), f1n = gb(Vy, I.t_f1n);
    if (p == I.wf1_pos) sb(P, t_hold, (A >= I.Qs - 5 && A <= I.Qs - 1 && in_win && wfb == 1) ? 1 : 0);
    if (p == I.wf2_pos) sb(P, t_hold, (A >= 0 && A <= 4 && in_win && wfb == 1 && f1n == 0) ? 1 : 0);
}
