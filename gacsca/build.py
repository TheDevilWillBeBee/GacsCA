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

    def np_engine(self):
        e = Engine(self.p, self.T, self.L, self.prog, self.variant); e.trickle = self.sched.trickle
        return e

    def gpu_engine(self, seed=0, wipe=True, trickle=True):
        from .gpu_engine import EngineGPU
        win = self.sched.trickle if trickle else (0, 0)
        return EngineGPU(self.p, self.T, self.L, self.prog, win, self.variant, seed=seed, wipe=wipe)


def make_system(Q=256, U=8192, ncol=16, R=3, D=3, variant=Variant(), JMAX=6, **kw):
    p = Params(Q=Q, U=U, ncol=ncol)
    T = Tracks(JMAX=JMAX, wq=(Q - 1).bit_length(), wu=(U - 1).bit_length(), R=R)
    L = Layout(Q, U, T)
    prog, sched = build_workperiod(p, T, L, D=D, variant=variant, JMAX=JMAX, **kw)
    return System(p, T, L, prog, sched, variant)
