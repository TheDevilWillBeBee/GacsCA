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

// Explicit bounded inner-table metadata, consumed by nested IBC/ICHAIN/ILATCH.
// No recursive device calls and no host-side simulated-state evaluation.
struct BCtx {
    int has, Qs, D, base, t_bfound, t_bval, t_sig[4], t_carry[4], U, NT;
    int t_s[3][3];
    int t_shsrc[3], t_blb, t_wfb, t_bus, wf1_pos, wf2_pos;
    int simage_lo, simage_hi, simaddr_lo, simaddr_hi, up_age_lo, up_age_hi, up_addr_lo, up_addr_hi;
    int t_cm[2], cm_addr[2], up_trk_lo, up_trk_hi;
    const int* ops; const int* age_ptr; const int* op_idx;
};

struct ICtx {
    int has;                         // interpretation enabled
    int b0, track_base, K, Qs, Us, D_up, JI;
    int addr_lo, addr_hi, age_lo, age_hi, wf1_pos, wf2_pos, simage_lo, simage_hi, simaddr_lo, simaddr_hi;
    int up_age_lo, up_age_hi, up_addr_lo, up_addr_hi;
    int trk_lo, trk_hi;              // trickle_up
    int rw_lo, rw_hi;                // regwin_up
    int t_vt, t_bus, t_sa, t_sb, t_sig[4], t_carry[4], t_bfound, t_bval, t_shsrc[3], t_s[3][3], t_blb, t_wfb, t_f1n;
    const int* ops_up; const int* age_ptr_up; const int* op_idx_up; int U_up;
    int t_cm[2], cm_addr[2];
    int up_trk_lo, up_trk_hi;
    BCtx inner;
};

struct Op1 { int kind, t0, t1, lo, hi, dst, src, src2, src3, param, param2, skind; };

__device__ __forceinline__ Op1 load_op(const int* o) {
    Op1 r; r.kind = o[0]; r.t0 = o[1]; r.t1 = o[2]; r.lo = o[3]; r.hi = o[4]; r.dst = o[5]; r.src = o[6]; r.src2 = o[7];
    r.src3 = o[8]; r.param = o[9]; r.param2 = o[10]; r.skind = o[11]; return r;
}

// A view into immutable device tables, not a fixed-size per-thread opcode
// array. In particular, the middle interpreter's 23 simultaneous clears must
// not be truncated to four instructions or serialized in the middle rule.
struct ActiveOps {
    const int* ops;
    const int* indices;
    int start, size;
    __device__ __forceinline__ Op1 operator[](int i) const {
        return load_op(ops + (size_t)indices[start + i] * OPW);
    }
};
__device__ __forceinline__ ActiveOps active_ops_up(const ICtx& I, int g1) {
    if (g1 < 0 || g1 >= I.U_up) return {I.ops_up, I.op_idx_up, 0, 0};
    int s = I.age_ptr_up[g1], e = I.age_ptr_up[g1 + 1];
    return {I.ops_up, I.op_idx_up, s, e - s};
}
__device__ __forceinline__ bool is_shift_kind(const Op1& o) { return o.kind == OPK_SHIFT || o.kind == OPK_RSHIFT; }
// resource-class slot of op i0 among the active ops (shift-kind ops use SHSRC slots, others S slots)
__device__ __forceinline__ int slot_of(const ActiveOps& ops1, int i0) {
    int s = 0; bool cl = is_shift_kind(ops1[i0]);
    for (int j = 0; j < i0; j++) if (is_shift_kind(ops1[j]) == cl) s++;
    return s;
}

__device__ __forceinline__ bool op_writes(const Op1& o, int t, int t_sig, int t_acc) {
    switch (o.kind) {
        case OPK_RESET: return t >= o.dst && t < o.param;
        case OPK_CONST: case OPK_MOV: case OPK_BITOP: case OPK_SHIFT: case OPK_RSHIFT: case OPK_BCAST_INIT: case OPK_REGWIN: case OPK_IINIT: return t == o.dst;
        case OPK_SWEEP_INIT: return t == t_sig || t == o.dst;
        case OPK_SWEEP: return t == t_sig || t == t_acc || (o.dst >= 0 && t == o.dst);
        case OPK_BCAST: return t == o.dst || t == t_sig;
    }
    return false;
}

__device__ __forceinline__ bool nested_bc_guard(const ICtx& I, const Op1& op1, const Op1& op2,
                                                int a1, int sa2, int R, int& kk, int& direction) {
    const BCtx& J = I.inner;
    if (!J.has || op2.kind != OPK_BCAST || a1 < op1.lo || a1 >= op1.hi) return false;
    int q = a1 - J.base;
    if (q < 0 || q >= J.NT * R) return false;
    int c2 = q % R - (R - 1) / 2;
    direction = op2.param ? op2.param : -1;
    int sh = op1.param - c2;
    kk = direction < 0 ? sh : -sh;
    if (kk < 1 || kk > J.D) return false;
    int a2 = ((sa2 + c2) % J.Qs + J.Qs) % J.Qs;
    return a2 + sh >= op2.lo && a2 + sh < op2.hi;
}

__device__ __forceinline__ bool nested_chain_select(const ICtx& I, const Op1& op1, int a1, int t,
                                                    int g2, int sa2, int R, int t_sig, int t_acc,
                                                    Op1& selected, int& slot, int& kk, int& bit_index) {
    const BCtx& J = I.inner;
    if (J.has < 2 || J.D == 1 || g2 < 0 || g2 >= J.U || a1 < op1.lo || a1 >= op1.hi) return false;
    int q = a1 - J.base;
    if (q < 0 || q >= J.NT * R) return false;
    int c2 = q % R - (R - 1) / 2, oo = op1.param - c2;
    kk = t == J.t_carry[2] ? 2 : t == J.t_carry[3] ? 3 : 0;
    if (kk < 2 || kk > J.D || oo >= 0 || oo <= -kk) return false;
    // Choose the final eligible instruction before latching any operand.
    int start = J.age_ptr[g2], end = J.age_ptr[g2 + 1];
    for (int z = end - 1; z >= start; z--) {
        Op1 o2 = load_op(J.ops + (size_t)J.op_idx[z] * OPW);
        if (o2.kind != OPK_SWEEP || !op_writes(o2, q / R, t_sig, t_acc)) continue;
        slot = 0;
        for (int v = start; v < z; v++) {
            Op1 previous = load_op(J.ops + (size_t)J.op_idx[v] * OPW);
            if (!is_shift_kind(previous)) slot++;
        }
        if (slot >= 3) return false;
        int a2 = ((sa2 + c2) % J.Qs + J.Qs) % J.Qs;
        bit_index = a2 + oo - o2.lo; selected = o2;
        return true;
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

__device__ bool nested_latch_source(const ICtx& I, const Op1& op1, int a1, int t, int g1, int g2, int sa2,
                                   int R, int t_sig, int t_acc, int t_info, int& relative) {
    const BCtx& J = I.inner;
    if (J.has < 3 || a1 < op1.lo || a1 >= op1.hi) return false;
    int q = a1 - J.base, h = (R - 1) / 2;
    bool inrng = q >= 0 && q < J.NT * R;
    int t2 = inrng ? q / R : 0, c2 = inrng ? q % R - h : 0;
    int oo = op1.param - c2, dir1 = op1.param2, tau1 = g1 - op1.t0;
    bool hit = false;
    auto ph = [&](int track) { return J.base + track * R + h; };
    auto request = [&](bool eligible, int X, int target) {
        int tt, j;
        if (eligible && t == target && latch_time(a1, X, dir1, I.D_up, tt, j) && tt == tau1) {
            hit = true; relative = -dir1 * j;
        }
    };
    if (g2 >= 0 && g2 < J.U) {
        int value_slot = 0, shift_slot = 0;
        for (int z = J.age_ptr[g2]; z < J.age_ptr[g2 + 1]; z++) {
            Op1 o2 = load_op(J.ops + (size_t)J.op_idx[z] * OPW);
            int i2 = is_shift_kind(o2) ? shift_slot++ : value_slot++;
            if (o2.kind == OPK_BUSLATCH_INT) {
                if (sa2 < o2.lo || sa2 >= o2.hi) continue;
                for (int f = 0; f < 2; f++) {
                    int lo = f ? J.simaddr_lo : J.simage_lo, hi = f ? J.simaddr_hi : J.simage_hi;
                    int slo = f ? J.up_addr_lo : J.up_age_lo, shi = f ? J.up_addr_hi : J.up_age_hi;
                    int bit = a1 - lo, tt, j;
                    if (bit < 0 || bit >= min(hi - lo, shi - slo)) continue;
                    if (!latch_time(sa2, slo + bit, o2.param2, J.D, tt, j)) continue;
                    request(tt == g2 - o2.t0 && -o2.param2 * j == op1.param, ph(o2.src), J.t_blb);
                }
                continue;
            }
            if (!inrng || !op_writes(o2, t2, t_sig, t_acc) || i2 >= 3) continue;
            int kind = o2.kind;
            if (kind == OPK_MOV || kind == OPK_BITOP || kind == OPK_BCAST_INIT) {
                if (o2.src >= 0) request(oo == 0, ph(o2.src), J.t_s[i2][0]);
                if (o2.src2 >= 0) request(oo == 0, ph(o2.src2), J.t_s[i2][1]);
                if (o2.src3 >= 0) request(oo == 0, ph(o2.src3), J.t_s[i2][2]);
            } else if (kind == OPK_IINIT) {
                request(oo == (o2.param2 ? 0 : -o2.param), ph(o2.src), J.t_s[i2][0]);
            } else if (kind == OPK_SHIFT || kind == OPK_RSHIFT) {
                request(oo == -o2.param, ph(o2.src), J.t_shsrc[i2]);
            } else if (kind == OPK_SWEEP) {
                if (o2.src >= 0) request(oo == 0, ph(o2.src), J.t_s[i2][0]);
                if (o2.src2 >= 0) request(oo == 0, ph(o2.src2), J.t_s[i2][1]);
                request(oo == 0, ph(t_sig), J.t_s[i2][2]);
                for (int kk = 1; kk <= J.D; kk++) {
                    request(oo == -kk, ph(t_sig), J.t_sig[kk]);
                    request(oo == -kk, ph(t_acc), J.t_carry[kk]);
                }
                for (int kk = 1; kk < J.D; kk++) {
                    if (o2.src >= 0) request(oo == -kk, ph(o2.src), J.t_s[i2][0]);
                    if (o2.src2 >= 0) request(oo == -kk, ph(o2.src2), J.t_s[i2][1]);
                }
            } else if (kind == OPK_BCAST) {
                int direction = o2.param ? o2.param : -1;
                request(oo == 0, ph(t_sig), J.t_s[i2][2]);
                for (int kk = 1; kk <= J.D; kk++) {
                    int sh = direction < 0 ? kk : -kk;
                    request(oo == sh, ph(t_sig), J.t_sig[kk]);
                    request(oo == sh, ph(o2.dst), J.t_carry[kk]);
                }
            }
        }
    }
    // Unlike instruction operands, these requests also run at an empty Age.
    request(a1 == J.wf1_pos && J.Qs - 3 - sa2 == op1.param, ph(t_info), J.t_wfb);
    request(a1 == J.wf2_pos && 3 - sa2 == op1.param, ph(t_info), J.t_wfb);
    return hit;
}

__device__ bool nested_eval_op(const ICtx& I, const Op1& op1, int g2, Op1& selected, int& slot) {
    const BCtx& J = I.inner;
    if (J.has < 4 || g2 < 0 || g2 >= J.U) return false;
    int start = J.age_ptr[g2], end = J.age_ptr[g2 + 1];
    if (op1.param < 0 || op1.param >= end - start) return false;
    ActiveOps active{J.ops, J.op_idx, start, end - start};
    selected = active[op1.param]; slot = slot_of(active, op1.param);
    return true;
}

__device__ void nested_eval_transport(uint32_t* P, const uint32_t* V, int ky, int p, int direction, int D,
                                      int tau, const ICtx& I, const Op1& op2, int slot, int R) {
    const BCtx& J = I.inner;
    auto request = [&](int source, int target) {
        int X = I.b0 + I.track_base + source * R + (R - 1) / 2;
        try_latch(P, V, ky, p, X, direction, D, tau, I.t_bus, target);
    };
    int kind = op2.kind;
    if (kind == OPK_BUSLATCH_INT) { request(J.t_blb, I.t_blb); return; }
    if (kind == OPK_CONST || kind == OPK_RESET || kind == OPK_SWEEP_INIT || kind == OPK_REGWIN) return;
    if (kind == OPK_SHIFT || kind == OPK_RSHIFT) { request(J.t_shsrc[slot], I.t_shsrc[0]); return; }
    if (kind == OPK_BCAST) {
        request(J.t_s[slot][2], I.t_s[0][2]); request(J.t_bfound, I.t_bfound); request(J.t_bval, I.t_bval);
        return;
    }
    request(J.t_s[slot][0], I.t_s[0][0]);
    if (kind == OPK_MOV && op2.param2) {
        int ci = op2.lo == J.cm_addr[0] ? 0 : 1;
        if (J.t_cm[ci] >= 0) request(J.t_cm[ci], I.t_blb);
    }
    if (kind == OPK_BITOP || kind == OPK_SWEEP) {
        request(J.t_s[slot][1], I.t_s[0][1]); request(J.t_s[slot][2], I.t_s[0][2]);
    }
    if (kind == OPK_SWEEP) for (int k = 1; k <= J.D; k++) {
        request(J.t_sig[k], I.t_sig[k]); request(J.t_carry[k], I.t_carry[k]);
    }
}

__device__ bool nested_eval_value(const uint32_t* V, const ICtx& I, const Op1& op1, int a1, int g2,
                                  int sa2, int R, int t_sig, int t_acc, int& result) {
    const BCtx& J = I.inner;
    Op1 o; int slot;
    if (a1 < op1.lo || a1 >= op1.hi || !nested_eval_op(I, op1, g2, o, slot)) return false;
    bool changed = false;
    auto put = [&](bool mask, int value) { if (mask) { changed = true; result = value; } };
    bool raw_range = sa2 >= o.lo && sa2 < o.hi;
    if (o.kind == OPK_BUSLATCH_INT) {
        for (int f = 0; f < 2; f++) {
            int lo = f ? J.simaddr_lo : J.simage_lo, hi = f ? J.simaddr_hi : J.simage_hi;
            int slo = f ? J.up_addr_lo : J.up_age_lo, shi = f ? J.up_addr_hi : J.up_age_hi;
            int bit = a1 - lo, tt, j;
            if (raw_range && bit >= 0 && bit < min(hi - lo, shi - slo) &&
                latch_time(sa2, slo + bit, o.param2, J.D, tt, j) && tt == g2 - o.t0)
                put(true, gb(V, I.t_blb));
        }
        return changed;
    }
    if (o.kind == OPK_RESET && o.param2 && raw_range)
        put((a1 >= J.simage_lo && a1 < J.simage_hi) || (a1 >= J.simaddr_lo && a1 < J.simaddr_hi), 0);
    int q = a1 - J.base;
    if (q < 0 || q >= J.NT * R) return changed;
    int track = q / R, copy = q % R - (R - 1) / 2;
    if (!op_writes(o, track, t_sig, t_acc)) return changed;
    int a2 = ((sa2 + copy) % J.Qs + J.Qs) % J.Qs;
    bool inr = a2 >= o.lo && a2 < o.hi;
    if (o.kind == OPK_MOV && o.param2) inr = gb(V, I.t_blb);
    if (o.kind == OPK_IINIT) {
        int q2 = a2 - J.up_trk_lo;
        inr = inr && q2 >= 0 && a2 < J.up_trk_hi && q2 % R == o.param + (R - 1) / 2;
    }
    int S0 = gb(V, I.t_s[0][0]), S1 = gb(V, I.t_s[0][1]), S2 = gb(V, I.t_s[0][2]);
    switch (o.kind) {
        case OPK_CONST: put(inr, o.param); break;
        case OPK_RESET: case OPK_REGWIN: put(inr, 0); break;
        case OPK_MOV: case OPK_IINIT: case OPK_BCAST_INIT: put(inr, S0); break;
        case OPK_BITOP: put(inr, (o.param >> ((S0 << 2) | (S1 << 1) | S2)) & 1); break;
        case OPK_SHIFT: put(inr, a2 - o.param >= o.lo && a2 - o.param < o.hi ? gb(V, I.t_shsrc[0]) : o.param2); break;
        case OPK_RSHIFT: put(inr, gb(V, I.t_shsrc[0])); break;
        case OPK_SWEEP_INIT:
            put(inr && track == t_sig, 1); put(inr && track == o.dst, o.param); break;
        case OPK_SWEEP: {
            bool acted = false, last = false; int out = 0, carry = 0;
            for (int k = 1; k <= J.D && !acted; k++) {
                if (gb(V, I.t_sig[k]) && a2 - k >= o.lo - 1 && inr) {
                    acted = true;
                    carry = chain_i(o.skind, gb(V, I.t_carry[k]), S0, S1, kbit_of(o.param, a2 - o.lo), out);
                    last = k == J.D || a2 == o.hi - 1;
                }
            }
            put(track == t_sig && a2 >= o.lo - 1 && a2 < o.hi, acted ? last : a2 == o.hi - 1 && S2);
            put(acted && track == t_acc, carry);
            put(acted && o.dst >= 0 && track == o.dst, out);
        } break;
        case OPK_BCAST: {
            bool act = inr && !S2 && gb(V, I.t_bfound);
            put(act && track == o.dst, gb(V, I.t_bval)); put(act && track == t_sig, 1);
        } break;
    }
    return changed;
}

__device__ void interp_ilatch(uint32_t* P, const uint32_t* V, int ky, int p, int g1, int simaddr, const Op1& op, int tau,
                              const ICtx& I, int R, int NT, int t_sig, int t_acc, int t_info, int t_hold, int t_busup, int D,
                              int g2, int sa2) {
    int o = op.param, dirn = op.param2;
    int r, t, c; bool inr = cell_geom(I, R, NT, p, r, t, c);
    int a1 = ((simaddr + c) % I.Qs + I.Qs) % I.Qs;
    ActiveOps ops1 = active_ops_up(I, g1); int n1 = ops1.size;
    int D1 = I.D_up;
    int oo = o - c;
    #define PH(tr) (I.b0 + I.track_base + (tr) * R + (R - 1) / 2)
    for (int i0 = 0; i0 < n1; i0++) {
        const Op1& o1 = ops1[i0];
        int i = slot_of(ops1, i0);
        if (o1.kind == OPK_BUSLATCH_INT) {
            if (simaddr < o1.lo || simaddr >= o1.hi) continue;
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
                try_latch(P, V, ky, p, PH(o1.src), dirn, D, tau, I.t_bus, I.t_blb);
            }
            continue;
        }
        if (!inr) continue;
        if (o1.kind == OPK_IEVAL && I.inner.has) {
            Op1 selected; int slot;
            if (t == t_hold && oo == 0 && a1 >= o1.lo && a1 < o1.hi && nested_eval_op(I, o1, g2, selected, slot))
                nested_eval_transport(P, V, ky, p, dirn, D, tau, I, selected, slot, R);
            continue;
        }
        if (o1.kind == OPK_ILATCH && I.inner.has) {
            int relative = 0;
            if (nested_latch_source(I, o1, a1, t, g1, g2, sa2, R, t_sig, t_acc, t_info, relative) && o == c + relative)
                try_latch(P, V, ky, p, PH(I.inner.t_bus), dirn, D, tau, I.t_bus, I.t_s[i][0]);
            continue;
        }
        if (o1.kind == OPK_ICHAIN && I.inner.has) {
            if (oo != 0) continue;
            Op1 selected; int slot, kk, bit_index;
            if (!nested_chain_select(I, o1, a1, t, g2, sa2, R, t_sig, t_acc, selected, slot, kk, bit_index)) continue;
            try_latch(P, V, ky, p, PH(I.inner.t_s[slot][0]), dirn, D, tau, I.t_bus, I.t_s[i][0]);
            try_latch(P, V, ky, p, PH(I.inner.t_s[slot][1]), dirn, D, tau, I.t_bus, I.t_s[i][1]);
            try_latch(P, V, ky, p, PH(I.inner.t_carry[kk]), dirn, D, tau, I.t_bus, I.t_s[i][2]);
            continue;
        }
        if (o1.kind == OPK_IBC && I.inner.has) {
            const BCtx& J = I.inner;
            if ((t != J.t_bfound && t != J.t_bval) || oo != 0 || g2 < 0 || g2 >= J.U) continue;
            int q2 = a1 - J.base;
            if (q2 < 0 || q2 >= J.NT * R) continue;
            for (int z = J.age_ptr[g2]; z < J.age_ptr[g2 + 1]; z++) {
                Op1 o2 = load_op(J.ops + (size_t)J.op_idx[z] * OPW);
                int kk, direction;
                if (!nested_bc_guard(I, o1, o2, a1, sa2, R, kk, direction)) continue;
                if (q2 / R != t_sig && q2 / R != o2.dst) continue;
                try_latch(P, V, ky, p, PH(J.t_sig[kk]), dirn, D, tau, I.t_bus, I.t_s[i][0]);
                try_latch(P, V, ky, p, PH(J.t_carry[kk]), dirn, D, tau, I.t_bus, I.t_s[i][1]);
                try_latch(P, V, ky, p, PH(J.t_bfound), dirn, D, tau, I.t_bus, I.t_s[i][2]);
            }
            continue;
        }
        bool wr = op_writes(o1, t, t_sig, t_acc);
        if (!wr) continue;
        int k = o1.kind;
        if (k == OPK_MOV || k == OPK_BITOP || k == OPK_BCAST_INIT) {
            if (oo == 0) {
                if (o1.src >= 0) try_latch(P, V, ky, p, PH(o1.src), dirn, D, tau, I.t_bus, I.t_s[i][0]);
                if (o1.src2 >= 0) try_latch(P, V, ky, p, PH(o1.src2), dirn, D, tau, I.t_bus, I.t_s[i][1]);
                if (o1.src3 >= 0) try_latch(P, V, ky, p, PH(o1.src3), dirn, D, tau, I.t_bus, I.t_s[i][2]);
            }
        } else if (k == OPK_IINIT) {
            int source_offset = o1.param2 ? 0 : -o1.param;
            if (oo == source_offset) try_latch(P, V, ky, p, PH(o1.src), dirn, D, tau, I.t_bus, I.t_s[i][0]);
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
    ActiveOps ops1 = active_ops_up(I, g1); int n1 = ops1.size;
    int D1 = I.D_up, oo = o - c;
    for (int i0 = 0; i0 < n1; i0++) {
        const Op1& o1 = ops1[i0];
        if (o1.kind != OPK_SWEEP) continue;
        int i = slot_of(ops1, i0);
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
    ActiveOps ops1 = active_ops_up(I, g1); int n1 = ops1.size;
    int D1 = I.D_up, oo = o - c;
    for (int i0 = 0; i0 < n1; i0++) {
        const Op1& o1 = ops1[i0];
        if (o1.kind != OPK_BCAST) continue;
        if (!op_writes(o1, t, t_sig, t_acc)) continue;
        int dir1 = (o1.param == 0) ? -1 : o1.param;
        for (int kk = 1; kk <= D1; kk++) {
            int sh = dir1 < 0 ? kk : -kk;
            if (oo != sh) continue;
            int sig = gb(Vy, I.t_sig[kk]), val = gb(Vy, I.t_carry[kk]), found = gb(Vy, I.t_bfound);
            bool inr = (a1 + sh >= o1.lo) && (a1 + sh < o1.hi);
            if ((found == 0 || dir1 > 0) && sig == 1 && inr) { sb(P, I.t_bval, val); sb(P, I.t_bfound, 1); }
        }
    }
}

__device__ void interp_ieval(uint32_t* P, const uint32_t* Vy, int p, int g1, int simaddr, const Op1& op, const ICtx& I,
                             int R, int NT, int t_sig, int t_acc, int t_info, int t_hold, int g2, int sa2) {
    int i0 = op.param;
    ActiveOps ops1 = active_ops_up(I, g1); int n1 = ops1.size;
    if (i0 >= n1) return;
    const Op1& o1 = ops1[i0];
    int i = slot_of(ops1, i0);
    int D1 = I.D_up;
    if (o1.kind == OPK_RESET && o1.param2 && simaddr >= o1.lo && simaddr < o1.hi) {
        if ((p >= I.simage_lo && p < I.simage_hi) || (p >= I.simaddr_lo && p < I.simaddr_hi))
            sb(P, t_hold, 0);
    }
    if (o1.kind == OPK_BUSLATCH_INT) {
        if (simaddr < o1.lo || simaddr >= o1.hi) return;
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
    int a1 = ((simaddr + c) % I.Qs + I.Qs) % I.Qs;
    if (o1.kind == OPK_IEVAL && I.inner.has) {
        int result;
        if (t == t_hold && nested_eval_value(Vy, I, o1, a1, g2, sa2, R, t_sig, t_acc, result))
            sb(P, t_hold, result);
        return;
    }
    if (o1.kind == OPK_ILATCH && I.inner.has) {
        int relative = 0;
        if (nested_latch_source(I, o1, a1, t, g1, g2, sa2, R, t_sig, t_acc, t_info, relative))
            sb(P, t_hold, gb(Vy, I.t_s[i][0]));
        return;
    }
    if (o1.kind == OPK_ICHAIN && I.inner.has) {
        Op1 selected; int slot, kk, bit_index;
        if (!nested_chain_select(I, o1, a1, t, g2, sa2, R, t_sig, t_acc, selected, slot, kk, bit_index)) return;
        int sv = gb(Vy, I.t_s[i][0]), s2v = gb(Vy, I.t_s[i][1]), cin = gb(Vy, I.t_s[i][2]), unused;
        sb(P, t_hold, chain_i(selected.skind, cin, sv, s2v, kbit_of(selected.param, bit_index), unused));
        return;
    }
    if (o1.kind == OPK_IBC && I.inner.has) {
        const BCtx& J = I.inner;
        if ((t != J.t_bfound && t != J.t_bval) || g2 < 0 || g2 >= J.U) return;
        int q2 = a1 - J.base;
        if (q2 < 0 || q2 >= J.NT * R) return;
        int sig = gb(Vy, I.t_s[i][0]), val = gb(Vy, I.t_s[i][1]), found = gb(Vy, I.t_s[i][2]);
        for (int z = J.age_ptr[g2]; z < J.age_ptr[g2 + 1]; z++) {
            Op1 o2 = load_op(J.ops + (size_t)J.op_idx[z] * OPW);
            int kk, direction;
            if (!nested_bc_guard(I, o1, o2, a1, sa2, R, kk, direction)) continue;
            if (q2 / R != t_sig && q2 / R != o2.dst) continue;
            if (sig && (!found || direction > 0)) sb(P, t_hold, t == J.t_bfound ? 1 : val);
        }
        return;
    }
    if (!op_writes(o1, t, t_sig, t_acc)) return;
    bool inr = (a1 >= o1.lo) && (a1 < o1.hi);
    if (o1.kind == OPK_MOV && o1.param2) {
        int ci = o1.lo == I.cm_addr[0] ? 0 : 1;
        inr = I.t_cm[ci] >= 0 && o1.lo == I.cm_addr[ci] && gb(Vy, I.t_cm[ci]);
    }
    if (o1.kind == OPK_IINIT) {
        int q = a1 - I.up_trk_lo;
        inr = inr && q >= 0 && a1 < I.up_trk_hi && q % R == o1.param + (R - 1) / 2;
    }
    if (o1.kind == OPK_RESET || o1.kind == OPK_CONST) {
        if (inr) sb(P, t_hold, o1.kind == OPK_RESET ? 0 : o1.param);
        return;
    }
    int S0 = gb(Vy, I.t_s[i][0]), S1 = gb(Vy, I.t_s[i][1]), S2 = gb(Vy, I.t_s[i][2]);
    switch (o1.kind) {
        case OPK_RESET: if (inr) sb(P, t_hold, 0); break;
        case OPK_CONST: if (inr) sb(P, t_hold, o1.param); break;
        case OPK_REGWIN: if (inr) sb(P, t_hold, 0); break;     // depth-2 tower: level-2 has no register window
        case OPK_MOV: case OPK_IINIT: if (inr) sb(P, t_hold, S0); break;
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
