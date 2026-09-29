"""Torch/CUDA front-end for the nanobind kernels.  State: uint32 tensor (B, L, W) on cuda."""
import os, sys, numpy as np, torch
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "cuda"))
import gacs_cuda  # noqa: E402
from .params import Params, Variant

W_LEVEL0 = 4
F1_BIT, F2_BIT, WF1_BIT, WF2_BIT = 1, 2, 4, 8


def to_gpu(S, W=W_LEVEL0):
    """NumPy dict-of-arrays state -> packed uint32 tensor (B, L, W)."""
    B, L = S["addr"].shape
    st = np.zeros((B, L, W), np.uint32)
    st[..., 0] = S["addr"]; st[..., 1] = S["age"]
    fl = S["f1"].astype(np.uint32) * F1_BIT + S["f2"].astype(np.uint32) * F2_BIT
    if "wf1" in S: fl += S["wf1"].astype(np.uint32) * WF1_BIT + S["wf2"].astype(np.uint32) * WF2_BIT
    st[..., 2] = fl
    if "simage" in S:
        st[..., 3] = S["simage"].astype(np.uint32) | (S["simaddr"].astype(np.uint32) << 16)
    return torch.from_numpy(st).cuda()


def to_np(st):
    a = st.cpu().numpy()
    fl = a[..., 2]
    return dict(addr=a[..., 0].astype(np.int32), age=a[..., 1].astype(np.int32),
                f1=((fl & F1_BIT) > 0).astype(np.int8), f2=((fl & F2_BIT) > 0).astype(np.int8),
                wf1=((fl & WF1_BIT) > 0).astype(np.int8), wf2=((fl & WF2_BIT) > 0).astype(np.int8),
                simage=(a[..., 3] & 0xFFFF).astype(np.int32), simaddr=(a[..., 3] >> 16).astype(np.int32))


def initial(p: Params, B: int, W=W_LEVEL0):
    st = torch.zeros((B, p.L, W), dtype=torch.uint32, device="cuda")
    st[..., 0] = (torch.arange(p.L, device="cuda") % p.Q).to(torch.uint32)
    return st


class Level0GPU:
    def __init__(self, p: Params, variant: Variant = Variant(), seed: int = 0, addr_mode="valid", noise_version=2):
        if noise_version not in (1, 2):
            raise ValueError("noise_version must be 1 (legacy) or 2")
        self.noise_version = noise_version
        self.p, self.v, self.seed = p, variant, seed
        self.addr_mode = 0 if addr_mode == "valid" else 1

    def step(self, st, out, t, eps=0.0, mask=None):
        gacs_cuda.level0_step(st, out, mask, self.p.Q, self.p.U, int(self.v.flag1_ii_in_colony),
                              int(self.v.flag2_iii_age == "current"), int(self.v.majority == "plurality"),
                              float(eps), int(self.seed), int(t), self.addr_mode, self.noise_version,
                              self.v.flag2_erase_code)
        return out

    def run(self, st, T, eps_schedule, t0=0, mask=None, callback=None):
        """Advance T steps in place (returns final state tensor).  callback(t, state) each step."""
        eps_f = eps_schedule if callable(eps_schedule) else (lambda t: eps_schedule)
        buf = torch.empty_like(st)
        for t in range(t0 + 1, t0 + T + 1):
            self.step(st, buf, t, eps_f(t), mask)
            st, buf = buf, st
            if callback is not None:
                callback(t, st)
        return st


def flags(st):
    """int32 view of the flag word (torch has no bitwise ops for uint32)."""
    return st[..., 2].contiguous().view(torch.int32)


def field(st, name):
    """Extract a field as int32 tensor: 'addr','age','f1','f2','wf1','wf2'."""
    if name == "addr": return st[..., 0].contiguous().view(torch.int32)
    if name == "age": return st[..., 1].contiguous().view(torch.int32)
    bit = dict(f1=F1_BIT, f2=F2_BIT, wf1=WF1_BIT, wf2=WF2_BIT)[name]
    return (flags(st) & bit) != 0


def damage_mask(st, p: Params, t=None):
    """Bool (B,L): Address (and Age if t given) differs from the ground-state trajectory."""
    L = p.L
    bad = field(st, "addr") != (torch.arange(L, device=st.device) % p.Q)
    if t is not None:
        bad |= field(st, "age") != (t % p.U)
    return bad
