"""Convenience constructor of a complete system (parameters, tracks, layout, program, engines)."""
from dataclasses import dataclass
from .params import Params, Variant
from .microcode import Tracks, Layout
from .workperiod import build_workperiod
from .engine_np import Engine


@dataclass
class System:
    p: Params
    T: Tracks
    L: Layout
    prog: object
    sched: object
    variant: Variant

    up: object = None      # the simulated level's System (tower)

    def np_engine(self):
        e = Engine(self.p, self.T, self.L, self.prog, self.variant); e.trickle = self.sched.trickle
        e.ictx = self.sched.ictx
        e.reg_window = self.sched.reg_window
        return e

    def gpu_engine(self, seed=0, wipe=True, trickle=True, noise_version=2, register_bits=None):
        from .gpu_engine import EngineGPU
        win = self.sched.trickle if trickle else (0, 0)
        return EngineGPU(self.p, self.T, self.L, self.prog, win, self.variant, seed=seed, wipe=wipe,
                         ictx=self.sched.ictx, reg_window=self.sched.reg_window, noise_version=noise_version,
                         register_bits=register_bits)


def make_system(Q=256, U=16384, ncol=16, R=3, D=3, variant=Variant(), JMAX=6, Qs=None, Us=None,
                with_tracks=False, Qss=None, Uss=None, schedule="compressed", full_registers=None, **kw):
    """Level-0 system with colony size Q, work period U, simulating cells with parameters (Qs, Us)
    (default: same as level 0).  with_tracks=False: simulated cells are local-only (stage 1)."""
    if R not in (3, 5) or not 1 <= D <= 6 - R:
        raise ValueError("system requires R=3,D<=3 or R=5,D=1 (interaction radius five)")
    p = Params(Q=Q, U=U, ncol=ncol)
    if schedule not in ("compressed", "gray"):
        raise ValueError("schedule must be compressed or gray")
    T = Tracks(JMAX=JMAX, wq=(Q - 1).bit_length(), wu=(U - 1).bit_length(), R=R,
               temporal_banks=schedule == "gray")
    if full_registers is None:
        full_registers = schedule == "gray"
    L = Layout(Q, U, T, Qs=Qs, Us=Us, with_tracks=with_tracks, Qss=Qss, Uss=Uss,
               full_registers=full_registers)
    if schedule == "gray":
        from .gray_schedule import build_gray_workperiod
        prog, sched = build_gray_workperiod(p, T, L, D=D, variant=variant, **kw)
    else:
        prog, sched = build_workperiod(p, T, L, D=D, variant=variant, JMAX=JMAX, **kw)
    return System(p, T, L, prog, sched, variant)


def make_tower(Q0=256, U0=16384, Q1=64, U1=4096, Q2=16, U2=2048, ncol0=64, R=3, D=3, variant=Variant(), JMAX1=5,
               full_registers=None, schedule="compressed"):
    """Depth-2 tower: level-0 cells (Q0, U0) simulate level-1 cells (Q1, U1) which simulate
    local-only level-2 cells (Q2, U2).  Returns (sys0, sys1); sys1 is the level-1 system whose
    program is interpreted by sys0 (ncol of sys1 = ncol0 level-1 cells)."""
    if R not in (3, 5) or not 1 <= D <= 6 - R:
        raise ValueError("tower requires R=3,D<=3 or R=5,D=1 (interaction radius five)")
    if schedule not in ("compressed", "gray"):
        raise ValueError("schedule must be compressed or gray")
    if full_registers is None:
        full_registers = schedule == "gray"
    if schedule == "gray" and (ncol0 < Q1 or ncol0 % Q1 or not full_registers):
        raise ValueError("Gray tower requires whole upper colonies and full-register encoding")
    sys1 = make_system(Q=Q1, U=U1, ncol=max(1, ncol0 // Q1), R=R, D=D, variant=variant, JMAX=JMAX1,
                       Qs=Q2, Us=U2, with_tracks=False, Qss=2, Uss=2,
                       full_registers=full_registers, schedule=schedule)      # level-1 ring has ncol0 cells
    p0 = Params(Q=Q0, U=U0, ncol=ncol0)
    T0 = Tracks(JMAX=6, wq=(Q0 - 1).bit_length(), wu=(U0 - 1).bit_length(), R=R,
                temporal_banks=schedule == "gray")
    L0 = Layout(Q0, U0, T0, Qs=Q1, Us=U1, with_tracks=True, Qss=Q2, Uss=U2,
                full_registers=full_registers)
    assert L0.tracks.NT == sys1.T.NT, "track registries must match"
    if schedule == "gray":
        from .gray_schedule import build_gray_workperiod
        builder, extra = build_gray_workperiod, {}
    else:
        builder, extra = build_workperiod, dict(JMAX=6)
    prog0, sched0 = builder(p0, T0, L0, D=D, variant=variant, **extra, prog_up=sys1.prog, L_up=sys1.L,
                                     trickle_up=sys1.sched.trickle, regwin_up=sys1.sched.reg_window)
    sys0 = System(p0, T0, L0, prog0, sched0, variant, up=sys1)
    return sys0, sys1


def make_simulation_layer(upper, *, Q, U, schedule="compressed"):
    """Wrap an explicit System in one colony per upper cell.

    Parameters/budgets are caller-selected; this is a level-specific finite
    construction, not a uniform encoded-program fixed point. When upper itself
    interprets a program, its exact context and raw input controls are wired
    into the tested nested interpreter. Unsupported further nesting fails in
    InterpCtx rather than silently dropping instructions or state fields.
    """
    lower = make_system(Q=Q, U=U, ncol=upper.p.L, R=upper.T.R, D=upper.prog.D,
                        variant=upper.variant, Qs=upper.p.Q, Us=upper.p.U,
                        Qss=upper.L.Qs, Uss=upper.L.Us, with_tracks=True,
                        full_registers=True, schedule=schedule,
                        nested_controls=upper.sched.ictx is not None,
                        prog_up=upper.prog, L_up=upper.L,
                        trickle_up=upper.sched.trickle, regwin_up=upper.sched.reg_window,
                        inner_ctx=upper.sched.ictx)
    lower.up = upper
    return lower
