"""Gray pp.34–35 five-stage protocol with optional upper-track interpretation.

This supplies source timing, resets, independent gather histories and stage-five
evaluation. It is not the uniform Gács construction; D10's computed-SimBit timing
remains unresolved. Stage five reloads input controls before interpretation;
both links can use this schedule, but full-tower validation is separate evidence.
"""
from .microcode import Compiler, Op
from .trlocal import TrLocal
from .workperiod import Schedule
from .params import Variant
from .interp import InterpCtx, compile_iphase, compile_register_load


def stage_windows(U):
    if U % 16:
        raise ValueError("U must be divisible by 16")
    edges = (0, U // 4, U // 2, 3 * U // 4, 7 * U // 8, U)
    return tuple((a, (a + b) // 2, b) for a, b in zip(edges, edges[1:]))


def reset_ranges(T, stage):
    """Stage is zero-based. Preserve Info always, and only needed raw histories."""
    keep = {T["INFO"]}
    for bank in "ABC"[:min(stage, 3)]:
        keep.update(T.arg(j, bank) for j in range(-5, 6))
    ranges, start = [], None
    for t in range(T.NT + 1):
        clear = t < T.NT and t not in keep
        if clear and start is None:
            start = t
        if not clear and start is not None:
            ranges.append((start, t)); start = None
    return ranges


def build_gray_workperiod(p, T, L, D=1, variant=Variant(), prog_up=None, L_up=None,
                          trickle_up=None, regwin_up=(0, 0), nested_controls=False, inner_ctx=None):
    if T.R != 5 or D != 1 or p.U != 128 * p.Q or p.Q < 8192 or p.Q < 2 * L.K:
        raise ValueError("Gray mode requires R=5,D=1,Q>=8192,U=128Q,Q>=2K")
    if p.Q & (p.Q - 1) or L.Qs & (L.Qs - 1) or L.Us & (L.Us - 1):
        raise ValueError("the bit-serial compiler currently requires power-of-two Q,Qs,Us")
    if L.with_tracks and (prog_up is None or L_up is None or trickle_up is None):
        raise ValueError("Gray upper-track mode requires prog_up, L_up, trickle_up")
    if not L.with_tracks and prog_up is not None:
        raise ValueError("upper program requires a full-track simulated state")
    if nested_controls and not L.with_tracks:
        raise ValueError("nested controls require a represented full-track state")
    if inner_ctx is not None and not nested_controls:
        raise ValueError("nested interpretation requires raw-input control loading")
    if "ARGC+0" not in T.idx or "ARGD+0" not in T.idx:
        raise ValueError("Gray mode requires three history banks and a signal scratch bank")
    Q, U = p.Q, p.U
    windows = stage_windows(U)
    C = Compiler(T, L, D=D)
    C.reg_window = (0, 0)
    ictx = InterpCtx(L, T, prog_up, L_up, trickle_up, None, regwin_up=regwin_up, inner=inner_ctx) if L.with_tracks else None
    info_rng = (L.b0, L.b0 + L.K)
    starts, signal_compute, signal_write = [], None, None

    def reset(stage):
        C.t = windows[stage][0]
        for i, (lo, hi) in enumerate(reset_ranges(T, stage)):
            C.emit("RESET", dst=lo, param=hi, param2=int(i == 0))
        C.t += 1

    def vote(bank):
        # Separate microsteps keep the same bounded instruction concurrency
        # as the rest of the interpreter-facing instruction set.
        for j in range(-5, 6):
            C.bitop(f"ARG{bank}{j:+d}", 0b11101000,
                    f"ARGA{j:+d}", f"ARGB{j:+d}", f"ARGC{j:+d}", rng=info_rng)

    for stage, bank in enumerate("ABC"):
        reset(stage)
        start = C.t; starts.append(start)
        C.mov("MAILL", "INFO", advance=False)
        C.mov("MAILR", "INFO", advance=False)
        C.mov(f"ARG{bank}+0", "INFO", rng=info_rng)
        duration = 5 * Q + 1
        C.emit("RSHIFT", dur=duration, dst=T["MAILL"], src=T["MAILL"], param=-1)
        C.emit("RSHIFT", dur=duration, dst=T["MAILR"], src=T["MAILR"], param=1)
        for j in range(1, 6):
            receive = start + j * Q + 1
            for offset, mail in ((j, "MAILL"), (-j, "MAILR")):
                C.prog.add(Op("MOV", receive, receive + 1, *info_rng,
                              dst=T.arg(offset, bank), src=T[mail]))
        C.t += duration
        if stage == 2:
            vote("D")
            t0 = C.t
            TrLocal(C, variant=variant, arg_bank="D").build()
            signal_compute = (t0, C.t)
            # The source leaves the early flag computation's input selection
            # implicit. Use the same three-way vote as the final transition,
            # preserving all histories for a fresh stage-five evaluation.
            a1, a2 = L.frange("F1")[0], L.frange("F2")[0]
            C.const("T0", 0, advance=False); C.const("T1", 0)
            C.mov("T0", "HOLD", rng=(a1, a1 + 1), advance=False)
            C.mov("T1", "HOLD", rng=(a2, a2 + 1))
            C.shift("T0", "T0", Q - 3 - a1, (a1, Q - 2))
            C.shift("T1", "T1", 3 - a2, (3, a2 + 1))
            signal_write = C.t
            C.mov("INFO", "T0", rng=(Q - 3, Q - 2), advance=False, computed_address=True)
            C.mov("INFO", "T1", rng=(3, 4), computed_address=True)
        if C.t > windows[stage][1]:
            raise ValueError(f"stage {stage+1} requires {C.t-windows[stage][0]} active steps")
    reset(3)
    reset(4)
    vote("A")
    if ictx is not None:
        compile_register_load(C, "ARGA+0", "T0", nested=nested_controls)
    compute_start = C.t
    tl = TrLocal(C, variant=variant)
    tl.build()
    iphase = None
    if ictx is not None:
        start = C.t
        # Registers describe this period's voted input. No speculative output
        # cache is needed: the next stage-one reset clears them anyway.
        compile_iphase(C, ictx, tl.al, tl.F1N, load_output_registers=False)
        iphase = (start, C.t)
    compute_end = C.t
    if C.t > windows[4][1]:
        raise ValueError("stage-five computation exceeds its active half")
    # Old Age U-1 -> new Age 0: commit reads old HOLD, then the first
    # stage's reset occurs at old Age 0. No sequential in-step dependence.
    C.prog.add(Op("MOV", U - 1, U, *info_rng, dst=T["INFO"], src=T["HOLD"]))
    C.prog.U = U
    schedule = Schedule(starts, compute_start, compute_end,
                        (3 * U // 4, 3 * U // 4 + 2 * Q), U - 1, compute_end,
                        iphase=iphase, ictx=ictx, reg_window=C.reg_window)
    schedule.mode = "gray"
    schedule.stages = windows
    schedule.signal_compute = signal_compute
    schedule.signal_write = signal_write
    return C.prog, schedule
