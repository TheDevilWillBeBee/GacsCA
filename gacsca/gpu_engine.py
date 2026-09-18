"""Torch/CUDA front-end for the full rule (local structure + track engine)."""
import numpy as np, torch
from . import gpu
from .gpu import gacs_cuda
from .params import Params, Variant
from .microcode import Tracks, Layout, Program

KIND = dict(CONST=0, MOV=1, BITOP=2, SHIFT=3, RSHIFT=4, SWEEP_INIT=5, SWEEP=6, BCAST_INIT=7, BCAST=8,
            IINIT=9, ILATCH=10, ICHAIN=11, IBC=12, IEVAL=13, IWF=14, BUSLATCH_INT=15, REGWIN=16)
SKIND = dict(EQC=0, EQF=1, ORF=2, ANDF=3, ADDC=4, LTC=5)


def pack_program(prog: Program, U: int):
    ops = np.zeros((len(prog.ops), 12), np.int32)
    for i, op in enumerate(prog.ops):
        ops[i] = [KIND[op.kind], op.t0, op.t1, op.lo, op.hi,
                  -1 if op.dst is None else op.dst, -1 if op.src is None else op.src,
                  -1 if op.src2 is None else op.src2, -1 if op.src3 is None else op.src3,
                  op.param, op.param2, SKIND.get(op.skind, 0)]
    lists = [[] for _ in range(U)]
    for i, op in enumerate(prog.ops):
        for a in range(op.t0, min(op.t1, U)):
            lists[a].append(i)
    age_ptr = np.zeros(U + 1, np.int32)
    for a in range(U):
        age_ptr[a + 1] = age_ptr[a] + len(lists[a])
    op_idx = np.array([i for l in lists for i in l], np.int32) if age_ptr[-1] else np.zeros(1, np.int32)
    return ops, age_ptr, op_idx


class EngineGPU:
    def __init__(self, p: Params, T: Tracks, L: Layout, prog: Program, trickle, variant=Variant(),
                 seed=0, wipe=True, ictx=None, reg_window=(0, 0)):
        self.p, self.T, self.L, self.prog, self.v, self.seed = p, T, L, prog, variant, seed
        self.R, self.NT = T.R, T.NT
        self.NW = (T.NT + 31) // 32
        self.W = 4 + self.R * self.NW
        ops, age_ptr, op_idx = pack_program(prog, p.U)
        self.ops = torch.from_numpy(ops).cuda(); self.age_ptr = torch.from_numpy(age_ptr).cuda()
        self.op_idx = torch.from_numpy(op_idx).cuda()
        cfg = np.zeros(96, np.int32)
        cfg[:18] = [p.Q, p.U, self.R, self.NW, self.NT, prog.D, T["SIG"], T["ACC"], T["INFO"], T["MAILL"], T["MAILR"],
                    trickle[0], trickle[1], int(wipe), T["HOLD"], -1, reg_window[0], reg_window[1]]
        self.ops_up = self.age_ptr_up = self.op_idx_up = None
        if ictx is not None:
            I = ictx; Lu = I.L_up
            cfg[15] = I.T["BUS"] if "BUS" in I.T.idx else I.n["BUS"]
            cfg[20:28] = [1, L.b0, L.track_base, L.K, L.Qs, L.Us, I.D_up, I.JI]
            cfg[28:38] = [*L.frange("ADDR"), *L.frange("AGE"), L.frange("WF1")[0], L.frange("WF2")[0], *L.frange("SIMAGE"), *L.frange("SIMADDR")]
            cfg[38:42] = [*Lu.frange("AGE"), *Lu.frange("ADDR")]
            cfg[42:46] = [*I.trickle_up, *I.regwin_up]
            names = ["VT", "BUS", "SA", "SB", "SIG1", "SIG2", "SIG3", "CARRY1", "CARRY2", "CARRY3", "BFOUND", "BVAL",
                     "SHSRC0", "SHSRC1", "SHSRC2", "S00", "S01", "S02", "S10", "S11", "S12", "S20", "S21", "S22", "BLB", "WFB", "F1N"]
            cfg[46:46 + len(names)] = [I.n[nm] for nm in names]
            cfg[46 + len(names)] = I.prog_up.U
            cfg[15] = I.n["BUS"]
            ou, au, iu = pack_program(I.prog_up, I.prog_up.U)
            self.ops_up = torch.from_numpy(ou).cuda(); self.age_ptr_up = torch.from_numpy(au).cuda(); self.op_idx_up = torch.from_numpy(iu).cuda()
        self.cfg = torch.from_numpy(cfg).cuda()

    # ---- conversions with the NumPy engine state ----
    def to_gpu(self, S):
        B, L = S["addr"].shape
        st = np.zeros((B, L, self.W), np.uint32)
        st[..., 0] = S["addr"]; st[..., 1] = S["age"]
        st[..., 2] = S["f1"] * 1 + S["f2"] * 2 + S.get("wf1", 0) * 4 + S.get("wf2", 0) * 8
        st[..., 3] = S["simage"].astype(np.uint32) | (S["simaddr"].astype(np.uint32) << 16)
        trk = S["trk"]                                   # (B,L,NT,R)
        for r in range(self.R):
            for t in range(self.NT):
                st[..., 4 + r * self.NW + (t >> 5)] |= (trk[..., t, r].astype(np.uint32) << (t & 31))
        return torch.from_numpy(st).cuda()

    def to_np(self, st):
        a = st.cpu().numpy()
        B, L, _ = a.shape
        fl = a[..., 2]
        trk = np.zeros((B, L, self.NT, self.R), np.uint8)
        for r in range(self.R):
            for t in range(self.NT):
                trk[..., t, r] = (a[..., 4 + r * self.NW + (t >> 5)] >> (t & 31)) & 1
        return dict(addr=a[..., 0].astype(np.int32), age=a[..., 1].astype(np.int32),
                    f1=((fl & 1) > 0).astype(np.int8), f2=((fl & 2) > 0).astype(np.int8),
                    wf1=((fl & 4) > 0).astype(np.int8), wf2=((fl & 8) > 0).astype(np.int8), trk=trk,
                    simage=(a[..., 3] & 0xFFFF).astype(np.int32), simaddr=(a[..., 3] >> 16).astype(np.int32))

    def step(self, st, out, t, eps=0.0):
        gacs_cuda.engine_step(st, out, self.ops, self.age_ptr, self.op_idx, self.cfg,
                              int(self.v.flag1_ii_in_colony), int(self.v.flag2_iii_age == "current"),
                              int(self.v.majority == "plurality"), float(eps), int(self.seed), int(t),
                              self.ops_up, self.age_ptr_up, self.op_idx_up)
        return out

    def run(self, st, T, eps_schedule, t0=0, callback=None):
        eps_f = eps_schedule if callable(eps_schedule) else (lambda t: eps_schedule)
        buf = torch.empty_like(st)
        for t in range(t0 + 1, t0 + T + 1):
            self.step(st, buf, t, eps_f(t)); st, buf = buf, st
            if callback is not None: callback(t, st)
        return st

    def info_bits(self, st):
        """repaired primary Info bits (B, L) as int tensor (majority over holders)."""
        R, h = self.R, (self.R - 1) // 2
        t = self.T["INFO"]
        votes = torch.zeros(st.shape[:2], dtype=torch.int32, device=st.device)
        for r in range(R):
            w = st[..., 4 + r * self.NW + (t >> 5)].contiguous().view(torch.int32)
            bit = (w >> (t & 31)) & 1
            votes += torch.roll(bit, shifts=(r - h), dims=1)     # holder x = y - (r-h) keeps copy r of bit y
        return (votes * 2 > R).to(torch.int32)
