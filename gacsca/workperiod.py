"""The colony work period: gathering (timed mail streams), compute (Tr_local), F1*/F2* signalling,
trickle-down window, update.  Builds the Age-scheduled Program for the whole rule."""
from dataclasses import dataclass
from .microcode import Compiler, Tracks, Layout, Op
from .trlocal import TrLocal
from .params import Params, Variant
from . import interp as _interp


@dataclass
class Schedule:
    gather_starts: list
    compute_start: int
    compute_end: int
    trickle: tuple
    update_age: int
    length: int
    iphase: tuple = None
    ictx: object = None
    reg_window: tuple = (0, 0)


def build_workperiod(p: Params, T: Tracks, L: Layout, D=3, variant=Variant(), gather_rest=None,
                     compute_margin=64, JMAX=6, c_list=(0,), prog_up=None, L_up=None, trickle_up=None,
                     regwin_up=(0, 0)):
    """prog_up/L_up/trickle_up: the simulated level's program, layout and trickle window; if given,
    the interpretation phase is emitted after Tr_local (stage 2)."""
    Q, U = p.Q, p.U
    gather_rest = 2 * Q if gather_rest is None else gather_rest
    C = Compiler(T, L, D=D, t=1)
    K = L.K
    info_rng = (L.b0, L.b0 + K)
    starts = []
    for stage in range(3):
        t0 = C.t
        starts.append(t0)
        # post: both streams <- INFO ; own state -> ARG_0
        C.emit("MOV", dst=T["MAILL"], src=T["INFO"], rng=(0, Q))
        C.emit("MOV", dst=T["MAILR"], src=T["INFO"], rng=(0, Q))
        if stage == 0:
            C.emit("MOV", dst=T.arg(0, "A"), src=T["INFO"], rng=info_rng)
        elif stage == 1:
            C.emit("MOV", dst=T.arg(0, "B"), src=T["INFO"], rng=info_rng)
        else:
            C.emit("BITOP", dst=T.arg(0, "A"), src=T.arg(0, "A"), src2=T.arg(0, "B"), src3=T["INFO"],
                   param=0b11101000, rng=info_rng)      # MAJ3 truth table (b1<<2|b2<<1|b3)
        C.t += 1
        # streams move every step for JMAX*Q steps (+1 so the last RECV sees JMAX*Q shifts)
        n = JMAX * Q + 1
        C.emit("RSHIFT", dur=n, dst=T["MAILL"], src=T["MAILL"], param=-1, rng=(0, Q))
        C.emit("RSHIFT", dur=n, dst=T["MAILR"], src=T["MAILR"], param=+1, rng=(0, Q))
        for j in range(1, JMAX + 1):
            ta = t0 + j * Q + 1
            for sgn, mail in ((+1, "MAILL"), (-1, "MAILR")):
                if stage == 0:
                    C.prog.add(Op("MOV", ta, ta + 1, *info_rng, dst=T.arg(sgn * j, "A"), src=T[mail]))
                elif stage == 1:
                    C.prog.add(Op("MOV", ta, ta + 1, *info_rng, dst=T.arg(sgn * j, "B"), src=T[mail]))
                else:
                    C.prog.add(Op("BITOP", ta, ta + 1, *info_rng, dst=T.arg(sgn * j, "A"), src=T.arg(sgn * j, "A"),
                                  src2=T.arg(sgn * j, "B"), src3=T[mail], param=0b11101000))
        C.t += n
        C.t += gather_rest
    compute_start = C.t
    for c in c_list:
        tl = TrLocal(C, c=c, variant=variant)
        tl.build()
    iphase = None; ictx = None
    C.reg_window = (0, 0)
    if prog_up is not None:
        ictx = _interp.InterpCtx(L, T, prog_up, L_up, trickle_up, None, regwin_up=regwin_up)
        t_i0 = C.t
        _interp.compile_iphase(C, ictx, tl.al, tl.F1N, tl.VRT, L.Qs, L.Us)
        iphase = (t_i0, C.t)
    compute_end = C.t
    # F1*, F2* -> INFO at addresses Q-3 and 3 (Gray p.35)
    aF1, aF2 = L.frange("F1")[0], L.frange("F2")[0]
    C.const("T0", 0, rng=(0, Q), advance=False); C.const("T1", 0, rng=(0, Q))
    C.mov("T0", "HOLD", rng=(aF1, aF1 + 1), advance=False); C.mov("T1", "HOLD", rng=(aF2, aF2 + 1))
    C.shift("T0", "T0", (Q - 3) - aF1, (aF1, Q - 2))
    C.shift("T1", "T1", 3 - aF2, (3, aF2 + 1))
    C.mov("INFO", "T0", rng=(Q - 3, Q - 2), advance=False); C.mov("INFO", "T1", rng=(3, 4))
    C.t += compute_margin
    trickle = (C.t, C.t + 2 * Q)
    C.t += 2 * Q + compute_margin
    update_age = U - 1
    assert C.t <= update_age, f"work period needs {C.t + 1} > U={U} steps"
    C.prog.add(Op("MOV", update_age, update_age + 1, *info_rng, dst=T["INFO"], src=T["HOLD"]))
    C.prog.U = U
    sched = Schedule(starts, compute_start, compute_end, trickle, update_age, C.t, iphase, ictx, C.reg_window)
    return C.prog, sched
