"""Torch/CUDA front-end for the full rule (local structure + track engine)."""
import numpy as np, torch
from . import gpu
from .gpu import gacs_cuda
from .params import Params, Variant
from .microcode import Tracks, Layout, Program

KIND = dict(CONST=0, MOV=1, BITOP=2, SHIFT=3, RSHIFT=4, SWEEP_INIT=5, SWEEP=6, BCAST_INIT=7, BCAST=8,
            IINIT=9, ILATCH=10, ICHAIN=11, IBC=12, IEVAL=13, IWF=14, BUSLATCH_INT=15, REGWIN=16, RESET=17)
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
                 seed=0, wipe=True, ictx=None, reg_window=(0, 0), noise_version=2, register_bits=None):
        if noise_version not in (1, 2):
            raise ValueError("noise_version must be 1 (legacy) or 2")
        self.noise_version = noise_version
        self.p, self.T, self.L, self.prog, self.v, self.seed = p, T, L, prog, variant, seed
        self.R, self.NT = T.R, T.NT
        required = max((L.Us - 1).bit_length(), (L.Qs - 1).bit_length())
        self.register_bits = max(16, required) if register_bits is None else register_bits
        if not isinstance(self.register_bits, int) or not 16 <= self.register_bits <= 31:
            raise ValueError("register_bits must be an integer in [16,31]")
        if self.register_bits < required:
            raise ValueError(f"simulated controls need at least {required} register bits")
        # Keep the historical packed16 format exactly. Wide registers each
        # occupy a separate word; low-level track offsets must use track_base.
        self.track_base = 4 if self.register_bits == 16 else 5
        self.nested_base = self.track_base
        self.nested_register_bits = getattr(prog, "nested_register_bits", 0)
        if not isinstance(self.nested_register_bits, int) or (self.nested_register_bits != 0 and not 16 <= self.nested_register_bits <= 31):
            raise ValueError("nested register width must be 0 or 16..31")
        self.nested_mask = (1 << self.nested_register_bits) - 1
        self.track_base += 0 if not self.nested_register_bits else 1 if self.nested_register_bits == 16 else 2
        self.register_mask = (1 << self.register_bits) - 1
        reach = 6 - self.R
        if self.R not in (3, 5) or not 1 <= prog.D <= reach:
            raise ValueError("redundant operations must stay within interaction radius five")
        for op in prog.ops:
            if op.kind == "BUSLATCH_INT" and (op.param not in (0, 1) or (op.param == 1 and
                    self.nested_register_bits < max(L.fields["SIMAGE"][1], L.fields["SIMADDR"][1]))):
                raise ValueError("register-load pair is absent or too narrow")
            shift = op.param if op.kind in ("SHIFT", "RSHIFT") or (op.kind == "IINIT" and not op.param2) else 0
            if abs(shift) > reach:
                raise ValueError(f"{op.kind} shift {shift} exceeds physical reach {reach}")
        self.NW = (T.NT + 31) // 32
        self.W = self.track_base + self.R * self.NW
        ops, age_ptr, op_idx = pack_program(prog, p.U)
        self.ops = torch.from_numpy(ops).cuda(); self.age_ptr = torch.from_numpy(age_ptr).cuda()
        self.op_idx = torch.from_numpy(op_idx).cuda()
        nested = ictx is not None and ictx.inner is not None
        if nested and self.nested_register_bits < max(L.fields["SIMAGE"][1], L.fields["SIMADDR"][1]):
            raise ValueError("nested interpretation requires a sufficiently wide raw-input control pair")
        cfg = np.zeros(160 if nested else 96, np.int32)
        cfg[:18] = [p.Q, p.U, self.R, self.NW, self.NT, prog.D, T["SIG"], T["ACC"], T["INFO"], T["MAILL"], T["MAILR"],
                    trickle[0], trickle[1], int(wipe), T["HOLD"], -1, reg_window[0], reg_window[1]]
        cfg[18] = self.register_bits
        cfg[19] = variant.flag2_erase_code
        cfg[80] = self.nested_register_bits
        # Register loading is a local primitive, also usable without a table interpreter.
        cfg[28:38] = [*L.frange("ADDR"), *L.frange("AGE"), L.frange("WF1")[0], L.frange("WF2")[0], *L.frange("SIMAGE"), *L.frange("SIMADDR")]
        self.ops_up = self.age_ptr_up = self.op_idx_up = None
        if ictx is not None:
            I = ictx; Lu = I.L_up
            cfg[20:28] = [1, L.b0, L.track_base, L.K, L.Qs, L.Us, I.D_up, I.JI]
            cfg[28:38] = [*L.frange("ADDR"), *L.frange("AGE"), L.frange("WF1")[0], L.frange("WF2")[0], *L.frange("SIMAGE"), *L.frange("SIMADDR")]
            cfg[38:42] = [*Lu.frange("AGE"), *Lu.frange("ADDR")]
            cfg[42:46] = [*I.trickle_up, *I.regwin_up]
            names = ["VT", "BUS", "SA", "SB", "SIG1", "SIG2", "SIG3", "CARRY1", "CARRY2", "CARRY3", "BFOUND", "BVAL",
                     "SHSRC0", "SHSRC1", "SHSRC2", "S00", "S01", "S02", "S10", "S11", "S12", "S20", "S21", "S22", "BLB", "WFB", "F1N"]
            cfg[46:46 + len(names)] = [I.n[nm] for nm in names]
            cfg[46 + len(names)] = I.prog_up.U
            cfg[74:78] = -1
            for i, target in enumerate(I.computed_move_addresses):
                cfg[74 + i] = I.n[f"CM{i}"]
                cfg[76 + i] = target
            cfg[78:80] = [Lu.b0 + Lu.track_base, Lu.b0 + Lu.track_base + Lu.tracks.NT * Lu.tracks.R]
            cfg[15] = -1          # legacy reserved bus override; each upper instruction now carries its source
            ou, au, iu = pack_program(I.prog_up, I.prog_up.U)
            if nested:
                J = I.inner
                oj, aj, ij = pack_program(J.prog_up, J.prog_up.U)
                # Version four adds inner computed-Address and IINIT guards.
                # Table slices retain local indices; nothing is silently rebased.
                cfg[81:98] = [4, J.L.Qs, J.D_up, J.base, J.n["BFOUND"], J.n["BVAL"],
                              *[J.n[f"SIG{k}"] for k in range(1, 4)],
                              *[J.n[f"CARRY{k}"] for k in range(1, 4)],
                              J.prog_up.U, len(ou), len(au), len(iu), J.NT]
                cfg[98:107] = [J.n[f"S{i}{j}"] for i in range(3) for j in range(3)]
                cfg[107:123] = [*[J.n[f"SHSRC{i}"] for i in range(3)],
                                J.n["BLB"], J.n["WFB"], J.n["BUS"],
                                J.L.frange("WF1")[0], J.L.frange("WF2")[0],
                                *J.L.frange("SIMAGE"), *J.L.frange("SIMADDR"),
                                *J.L_up.frange("AGE"), *J.L_up.frange("ADDR")]
                cfg[123:127] = -1
                for i, target in enumerate(J.computed_move_addresses):
                    cfg[123 + i] = J.n[f"CM{i}"]
                    cfg[125 + i] = target
                cfg[127:129] = [J.L_up.b0 + J.L_up.track_base,
                                J.L_up.b0 + J.L_up.track_base + J.NT * J.R]
                ou = np.concatenate((ou, oj))
                au = np.concatenate((au, aj))
                iu = np.concatenate((iu, ij))
            self.ops_up = torch.from_numpy(ou).cuda(); self.age_ptr_up = torch.from_numpy(au).cuda(); self.op_idx_up = torch.from_numpy(iu).cuda()
        self.cfg = cfg

    # ---- conversions with the NumPy engine state ----
    def initial(self, B=1, info_bits=None):
        """Initialize directly in packed GPU storage, avoiding a dense CPU track array.

        This is exactly the NumPy initial-state factory followed by to_gpu,
        including all redundant Info copies. It makes full Gray geometry
        practical without allocating 435 unpacked track bytes per site on CPU.
        """
        if not isinstance(B, int) or B < 1:
            raise ValueError("B must be a positive integer")
        info = None
        if info_bits is not None:
            info = torch.as_tensor(info_bits, device=self.ops.device)
            if info.shape != (B, self.p.L) or not bool(((info == 0) | (info == 1)).all()):
                raise ValueError("Info must be a binary array of shape (B, L)")
            info = info.to(torch.int32)
        state = torch.zeros((B, self.p.L, self.W), dtype=torch.uint32, device=self.ops.device)
        state[..., 0] = (torch.arange(self.p.L, device=state.device) % self.p.Q).to(torch.uint32)
        if info is not None:
            t = self.T["INFO"]
            h = self.R // 2
            for r in range(self.R):
                state[..., self.track_base + r * self.NW + t // 32] = (
                    torch.roll(info, -(r - h), dims=1) << (t % 32)).to(torch.uint32)
        return state

    def to_gpu(self, S):
        if not self.nested_register_bits and ("simage2" in S or "simaddr2" in S):
            raise ValueError("extended controls cannot be dropped into a legacy schema")
        B, L = S["addr"].shape
        st = np.zeros((B, L, self.W), np.uint32)
        st[..., 0] = S["addr"]; st[..., 1] = S["age"]
        st[..., 2] = S["f1"] * 1 + S["f2"] * 2 + S.get("wf1", 0) * 4 + S.get("wf2", 0) * 8
        for name in ("simage", "simaddr"):
            value = np.asarray(S[name])
            if value.shape != (B, L) or value.dtype.kind not in "iu" or np.any(value < 0) or np.any(value > self.register_mask):
                raise ValueError(f"{name} does not fit the {self.register_bits}-bit register schema")
        if self.register_bits == 16:
            st[..., 3] = S["simage"].astype(np.uint32) | (S["simaddr"].astype(np.uint32) << 16)
        else:
            st[..., 3] = S["simage"]; st[..., 4] = S["simaddr"]
        if self.nested_register_bits:
            for name in ("simage2", "simaddr2"):
                value = np.asarray(S[name])
                if value.shape != (B, L) or value.dtype.kind not in "iu" or np.any(value < 0) or np.any(value > self.nested_mask):
                    raise ValueError(f"{name} does not fit nested register schema")
            if self.nested_register_bits == 16:
                st[..., self.nested_base] = S["simage2"].astype(np.uint32) | (S["simaddr2"].astype(np.uint32) << 16)
            else:
                st[..., self.nested_base] = S["simage2"]
                st[..., self.nested_base + 1] = S["simaddr2"]
        trk = S["trk"]                                   # (B,L,NT,R)
        for r in range(self.R):
            for t in range(self.NT):
                st[..., self.track_base + r * self.NW + (t >> 5)] |= (trk[..., t, r].astype(np.uint32) << (t & 31))
        return torch.from_numpy(st).cuda()

    def to_np(self, st):
        if st.shape[-1] != self.W:
            raise ValueError("state width does not match the engine's register schema")
        a = st.cpu().numpy()
        B, L, _ = a.shape
        fl = a[..., 2]
        trk = np.zeros((B, L, self.NT, self.R), np.uint8)
        for r in range(self.R):
            for t in range(self.NT):
                trk[..., t, r] = (a[..., self.track_base + r * self.NW + (t >> 5)] >> (t & 31)) & 1
        result = dict(addr=a[..., 0].astype(np.int32), age=a[..., 1].astype(np.int32),
                    f1=((fl & 1) > 0).astype(np.int8), f2=((fl & 2) > 0).astype(np.int8),
                    wf1=((fl & 4) > 0).astype(np.int8), wf2=((fl & 8) > 0).astype(np.int8), trk=trk,
                    simage=(a[..., 3] & self.register_mask).astype(np.int32),
                    simaddr=((a[..., 3] >> 16) if self.register_bits == 16 else (a[..., 4] & self.register_mask)).astype(np.int32))
        if self.nested_register_bits:
            result["simage2"] = (a[..., self.nested_base] & self.nested_mask).astype(np.int32)
            result["simaddr2"] = ((a[..., self.nested_base] >> 16) if self.nested_register_bits == 16 else
                                  (a[..., self.nested_base + 1] & self.nested_mask)).astype(np.int32)
        return result

    def step(self, st, out, t, eps=0.0):
        gacs_cuda.engine_step(st, out, self.ops, self.age_ptr, self.op_idx, self.cfg,
                              int(self.v.flag1_ii_in_colony), int(self.v.flag2_iii_age == "current"),
                              int(self.v.majority == "plurality"), float(eps), int(self.seed), int(t),
                              self.ops_up, self.age_ptr_up, self.op_idx_up, self.noise_version,
                              torch.cuda.current_stream(st.device).cuda_stream)
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
            w = st[..., self.track_base + r * self.NW + (t >> 5)].contiguous().view(torch.int32)
            bit = (w >> (t & 31)) & 1
            votes += torch.roll(bit, shifts=(r - h), dims=1)     # holder x = y - (r-h) keeps copy r of bit y
        return (votes * 2 > R).to(torch.int32)


class CleanGraphRunner:
    """Replay exact *noiseless* microsteps with stable, owned double buffers.

    The state (not a host counter) controls the local rule. Capturing stochastic
    steps would repeat the same noise on each replay, so this interface has no
    noise argument. ``state`` can be inspected or modified between ``run`` calls;
    it is a clone of the constructor's input and always keeps the same storage.
    Calls must use the construction CUDA device and stream, as with other
    stateful asynchronous CUDA objects.
    """

    def __init__(self, engine, state, block_steps=256):
        import operator
        block_steps = operator.index(block_steps)
        if block_steps <= 0 or block_steps % 2:
            raise ValueError("block_steps must be a positive even integer")
        if not state.is_cuda:
            raise ValueError("state must be a CUDA tensor")
        self.engine, self.block_steps = engine, block_steps
        self.state = state.clone()
        self.buffer = torch.empty_like(state)
        self.steps = 0
        self.stream = torch.cuda.current_stream(state.device)
        self.graph = torch.cuda.CUDAGraph()
        capture_stream = torch.cuda.Stream(device=state.device)
        capture_stream.wait_stream(self.stream)
        # Warm the launch path on disposable storage, never advancing state.
        with torch.cuda.stream(capture_stream):
            warm = state.clone()
            engine.step(warm, torch.empty_like(warm), 0, 0.0)
        self.stream.wait_stream(capture_stream)
        with torch.cuda.graph(self.graph, stream=capture_stream):
            a, b = self.state, self.buffer
            for _ in range(block_steps):
                engine.step(a, b, 0, 0.0)
                a, b = b, a

    def run(self, steps):
        import operator
        steps = operator.index(steps)
        if steps < 0:
            raise ValueError("steps must be nonnegative")
        if torch.cuda.current_stream(self.state.device) != self.stream:
            raise ValueError("run must use the runner's construction CUDA stream")
        blocks, tail = divmod(steps, self.block_steps)
        for _ in range(blocks):
            self.graph.replay()
        a, b = self.state, self.buffer
        for _ in range(tail):
            self.engine.step(a, b, 0, 0.0)
            a, b = b, a
        if tail % 2:
            self.state.copy_(a)
        self.steps += steps
        return self.state
