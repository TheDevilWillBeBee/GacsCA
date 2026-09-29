"""Certified skipping of instruction-free, noiseless, fixed-state intervals.

This does not replace simulated transitions by an oracle. It checks the actual
physical state and a full physical transition before advancing only its clock.
Noisy steps, clock wraps, scheduled instructions and clock-dependent register/
Workspace windows are never skipped. See Report/exact_acceleration.md.
"""
import operator

import torch

from gacsca.gpu import field
from gacsca.gpu_engine import CleanGraphRunner, EngineGPU


def quiet_intervals(engine):
    """Conservative old-Age intervals on which only clock-independent repair acts."""
    U = engine.p.U
    busy = [(max(0, o.t0), min(U, o.t1)) for o in engine.prog.ops]
    # Workspace flags use computed Age=old Age+1 in the certified ground state.
    tlo, thi = map(int, engine.cfg[11:13])
    busy.append((max(0, tlo - 1), min(U, thi - 1)))
    rlo, rhi = map(int, engine.cfg[16:18])
    busy.append((max(0, rlo), min(U, rhi)))
    # Never infer behavior through clock rollover.
    busy.append((U - 1, U))
    merged = []
    for lo, hi in sorted((a, b) for a, b in busy if a < b):
        if merged and lo <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(hi, merged[-1][1]))
        else:
            merged.append((lo, hi))
    quiet, end = [], 0
    for lo, hi in merged:
        if end < lo:
            quiet.append((end, lo))
        end = hi
    return quiet


def uniform_age(state):
    age = int(state[0, 0, 1].item())
    return age if bool((field(state, "age") == age).all()) else None


def try_skip_quiescent(runner, steps):
    """Return a certificate if successful, otherwise None without advancing state.

    The buffer may be overwritten by the probe; it is scratch storage, not part
    of the CA state. Successful skipping preserves graph storage addresses.
    """
    steps = operator.index(steps)
    if steps < 0:
        raise ValueError("steps must be nonnegative")
    if type(runner) is not CleanGraphRunner or type(runner.engine) is not EngineGPU:
        raise TypeError("certificate applies only to the audited full-rule clean runner")
    if torch.cuda.current_stream(runner.state.device) != runner.stream:
        raise ValueError("use the runner's construction stream")
    if steps == 0:
        return None
    engine, state = runner.engine, runner.state
    age = uniform_age(state)
    if age is None or not any(lo <= age and age + steps <= hi for lo, hi in quiet_intervals(engine)):
        return None
    if state.shape[1] % engine.p.Q or bool((state[..., 2] != 0).any()):
        return None
    # Require actual healthy phase-zero geometry, not merely the right shape.
    ideal = torch.arange(state.shape[1], device=state.device) % engine.p.Q
    if not bool((field(state, "addr") == ideal).all()):
        return None
    engine.step(state, runner.buffer, 0, eps=0.0)
    probe = runner.buffer
    if (not torch.equal(probe[..., 0], state[..., 0]) or
            not torch.equal(probe[..., 2:], state[..., 2:]) or
            not bool((field(probe, "age") == age + 1).all())):
        return None
    # All non-clock rules are independent of Age on this interval. The full
    # one-step fixed-point check therefore extends by induction to every step.
    state[..., 1] = age + steps
    runner.steps += steps
    return dict(old_age=age, new_age=age + steps, steps=steps,
                batches=state.shape[0], physical_cells_per_ring=state.shape[1],
                proof="ground geometry, zero flags, no clock guards, full non-clock fixed-point probe")


def advance_certified(runner, steps, certificates=None):
    """Exact noiseless execution, conservatively skipping only certified intervals."""
    steps = operator.index(steps)
    if steps < 0:
        raise ValueError("steps must be nonnegative")
    quiet = quiet_intervals(runner.engine)
    remaining = steps
    while remaining:
        age = uniform_age(runner.state)
        if age is None:
            runner.run(remaining)
            break
        interval = next(((lo, hi) for lo, hi in quiet if lo <= age < hi), None)
        if interval:
            length = min(remaining, interval[1] - age)
            certificate = try_skip_quiescent(runner, length)
            if certificate is not None:
                if certificates is not None:
                    certificates.append(certificate)
            else:
                runner.run(length)
        else:
            next_quiet = min([lo for lo, _ in quiet if lo > age] + [runner.engine.p.U])
            length = min(remaining, max(1, next_quiet - age))
            runner.run(length)
        remaining -= length
    return runner.state
