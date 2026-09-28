# Five-stage Gray schedule: implementation and validation

This is a new explicit **schedule mode**, not a claim that all Gray/Gács fidelity
questions are resolved. Select `make_system(..., schedule="gray", R=5, D=1)`.
The compressed mode remains the default for historical replay and the existing
tower. Gray mode requires Q≥8192, U=128Q, Q≥2K and power-of-two parameters.
Upper-track interpretation and compilation of both tower links are implemented;
phase tests pass, but a complete Gray-tower trajectory is not yet validated.

## Source contract and executable choices

Gray [pp.34–35](../papers_txt/gray_readers_guide.txt) prescribes:

| Stage | Active interval, in Q units | Rest interval | Required storage retained at reset |
|---|---|---|---|
| Gather 1 | [0,16) | [16,32) | Info only |
| Gather 2 | [32,48) | [48,64) | Info and gather A |
| Gather 3 + flag signals | [64,80) | [80,96) | Info and gathers A,B |
| Trickle | [96,104) | [104,112) | Info and gathers A,B,C |
| Vote + compute | [112,120) | [120,128) | Info and gathers A,B,C |

`gacsca/gray_schedule.py` uses separate A/B/C history banks, plus a disposable
D bank for stage-three flag computation: 87 tracks total (five redundant copies
each). Gathers retrieve exactly five neighbors on each side. Their posting
steps follow the one-step reset at each stage start. All three original gathered
records survive the third-stage computation and the fourth-stage reset.

The source leaves the flag computation's input-selection details implicit.
Here D receives the bitwise A/B/C majority, the local transition is computed
from D, and its flags are copied to Info at Q−3 and 3. The fifth-stage reset
erases this intermediate computation. A **fresh** majority/evaluation in stage
five produces HOLD; this is not reuse of the third-stage result. At old Age
U−1, Info takes HOLD and the local clock becomes 0. The first-stage reset at
old Age 0 then clears HOLD. This ordering avoids a sequential read-after-clear
inside a synchronous transition. Computed-SimBit timing remains D10.

An explicit `RESET` instruction clears a contiguous track range and optionally
both integer workspace registers. Disjoint reset ranges run simultaneously;
Info and needed histories are excluded. Each holder uses its own clock/address,
as for other redundant operations. The CUDA packing capacity is now 96 tracks
(three words per redundant copy); the former two-word capacity could not hold
three separate records plus signal scratch storage.

For Q=8192,U=1048576 and the reduced terminal rule Q*=16,U*=2048, with
the current full-register encoding (K=51):

| Operation | Physical old-age interval/time |
|---|---|
| Gather posting | 1, 262145, 524289 |
| Third-stage local evaluation | [565262,572756) |
| Flag-signal write | 580945 |
| Workspace flag window (computed Age) | [786432,802816) |
| Fifth-stage local evaluation | [917516,925010) |
| Commit | 1048575 → new Age 0 |

## Evidence

`tests/test_gray_schedule.py` checks all five reset masks, every prescribed
rest interval (excluding the next-period commit), independent history storage,
and NumPy/CUDA agreement with inconsistent copies and damaged holder controls.
Reset tests include nonzero workspace registers and the third packed word.
The combined schedule/backend/RNG/graph set passed **28 tests**
([record](../figs/gray_schedule_backend_20260920.xml)).

A complete **fifth-stage computation**, on a 16-cell non-aliased upper ring,
passes five adversarial scenarios: clean; complemented A; complemented B;
complemented C; complemented A+B. Each single corrupted history produces the
clean direct transition in every field. Two corrupted histories produce the
transition of the complemented input and differ from the clean result—the
negative control verifies the vote's actual correction limit.
[Test record](../figs/gray_temporal_vote_20260920.xml).
This tests temporal voting, not a physically localized burst or iid fault law.

`experiments/gray_protocol.py` completed a work period on four
physical rings, each containing 16 colonies of 8192 cells. It compares all
retrieved bits, third-stage flags, fifth-stage output and committed output;
checks simulation fields across every rest; and checks physical Address/Age.
The fault controls complement one entire gathered record after its retrieval.
Every chunk is checkpointed; a deliberately stopped 32768-step run was resumed.
[Checkpoint](../figs/gray_protocol_20260920.npz): **1048576/1048576** steps,
1058.62 s wall time. All three gathers match every expected bit before injection,
all five complete rests preserve simulation fields, and signals, HOLD and commit
match all eight upper fields in all four scenarios. Its source and binary are archived
for exact replay ([archive](../figs/gray_protocol_sources_20260920.tar.gz)); every
member used in the checkpoint fingerprint has been hash-verified. This run used
the **older K=34 encoding**, not the expanded alphabet below. Its fifth-stage
evaluation ended at 922789; those timings should not be used for current runs.

The RESET instruction is now also implemented in the finite-tower interpreter.
Complete R=3/R=5 lower periods match a direct upper rule with disjoint reset
ranges, nonzero registers, inconsistent copies, a faulty clock, and a changed
Address. A faulty clock correctly skips its own reset; out-of-range registers
are retained. All encoded fields/raw copies match. Unsupported upper opcodes now
fail explicitly. **3 tests pass** ([record](../figs/interpreted_reset_20260920.xml)).
This primitive by itself did not supply the reload schedule; that integration is below.

The combined reset-extension regression run passed **66 tests** in 156 s
([record](../figs/gray_reset_regressions_20260920.xml)). A final refinement clears
unused ±6 history slots at every stage and permits four simultaneous no-input
reset operations without reading nonexistent value-latch slots; all 12 affected
tests pass ([record](../figs/gray_reset_padding_20260920.xml)).
The final fivefold/damaged-state/backend checks also pass: **11 tests**
([record](../figs/reset_final_backend_20260920.xml)).
The completed full-period run uses the archived pre-refinement rule. Its padding
tracks are zero initially and at the inspected 491520-step checkpoint, have no
non-reset writers, and are not touched by the ±5-bank fault injections. Thus
the extra padding clears cannot alter these particular trajectories; general
faulty padding behavior is covered by the new reset tests, not by that archived run.

## Reset-safe hierarchy and alphabet audit

The CUDA backend now supports **16–31-bit** integer simulation registers. Width
16 preserves the old packed header exactly; wider widths use two words and a
dynamic track offset. Width is automatically sufficient for the represented
Address/Age. Invalid or truncated values are rejected. NumPy/CUDA, version-1/2
noise vectors, graph replay, and a complete interpreted transition across the
20-bit clock wrap pass ([20-test record](../figs/wide_registers_20260920.xml)).

**D13:** legacy encoding allocated only log2(Uss), log2(Qss) bits for the represented
registers, while the upper implementation's noise could set every one of 16 bits.
A legal value 65535 therefore could not be encoded in its 11-bit field. New
`full_registers=True` encodes the actual upper alphabet (shared width at least 16);
Gray mode defaults to it and Gray towers require it. Compressed defaults remain
legacy/replay-only in this respect. Random full-width values, the 65535 witness,
and full interpreted transitions pass ([12-test record including schedule tests](../figs/register_alphabet_20260920.xml)).

Each Gray stage clears scratch registers. Before stage-five interpretation,
two local bus passes now load **input** Age/Address from the voted A record.
Only this short load interval disables register repair; computation retains the
input controls, and the next period resets/reloads them. Compressed towers retain
their historical output-register cache. For both Gray links at Q=8192,U=1048576:

| Lower-colony operation | Physical old-age interval |
|---|---|
| Input register load | [917518,933905) |
| Local transition | [933905,943502) |
| Upper-track interpretation | [943502,954200) |
| Active stage-five deadline | 983040 |

The lower encoded cell has K=504 bits, including 87×5 raw tracks. The factory
checks a complete upper colony: **67,108,864 physical cells**. This geometry
compiles; it has **not** been executed through a complete work period.
Dynamic tests use a 16-cell arbitrary upper ring (no neighbor aliasing, but not
a full Q1=8192 colony), seed its gather banks, and execute reset/load/computation.
Six upper phases cover two resets, gather receive, flag signal, trickle onset,
and commit. Every field/raw copy matches the direct upper rule; each lower
register holds the input controls. A separate commit microstep passes, without
claiming the intervening rest was executed. A NumPy ring-length assumption found
by this test was corrected. **3 tests pass** including the compressed 20-bit-clock
regression ([record](../figs/gray_tower_reload_20260920.xml)).
Broader schedule/reset/tower/alphabet/noise/graph/checkpoint regressions:
**51 passed in 138.45 s** ([record](../figs/gray_integration_regressions_20260920.xml)).

The full-period protocol completed with K=51 and arbitrary full16-bit
input registers, including 65535: [checkpoint](../figs/gray_protocol_full_registers_20260920.npz),
[hash-verified source/binary archive](../figs/gray_protocol_full_registers_sources_20260920.tar.gz).
**1048576/1048576 steps, 1222.66 s wall time**: all three gathers, five rests,
signals, HOLD and committed eight-field outputs pass in all four scenarios.
This is independent evidence for the full-register encoding, not a transfer of
the archived narrow run's result. It uses the printed Flag2 rule; no physical
faults were injected in this protocol-level gather-corruption test.

## Physical transient-fault experiment

`experiments/gray_faults.py` runs clean, single-cell/single-step, early 200-cell ×
200-step, and update-stage 200×200 whole-cell replacement trajectories. Noise is
probability one **inside** the space-time box and zero outside, using counter RNG
v2. Faults replace states after the transition; no stochastic step is graph-captured.
The masking helper matches an explicit clean/noisy kernel reference and split
execution (**2 tests**, [record](../figs/spatial_faults_20260920.xml)).
Two full periods measure physical Address/Age recovery, flags, spatial damage
bins, and every decoded field against both the ground trajectory and the direct
transition of the previous decoded state. These are single-seed diagnostics,
not iid sweeps, independent-trial intervals, or logical-memory measurements.
[Checkpoint](../figs/gray_physical_faults_20260920.npz),
[hash-verified archive](../figs/gray_physical_faults_sources_20260920.tar.gz).
The 32768-step pilot was deliberately stopped and resumed. In its early burst,
106 sites still have bad Address/Age 16 steps after noise stops; none do at the
57-step sample. Thus sampled structural recovery is bracketed by (16,57] steps,
not an exact recovery time or recovery of every field. Flag2 remains active.
The single-cell control restores Address/Age at the first clean step but retains
one Flag2 bit (consistent with D8). The printed run has now completed both
periods: **2,097,152 steps, 1865.35 s**. The late burst restores physical
Address/Age in the sampled (16,64]-step bracket, but produces one decoded
Address error and one decoded Age error in colony 7 at the first boundary
(Address 0 instead of 7; Age 1 instead of 778). At the second boundary, all
eight decoded fields match both the ground trajectory and the direct transition
of the previous decoded state, in every scenario. Thus the simulated layer
repairs this particular first-period error. Final physical Flag2 counts remain
1, 4079 and 4228 in the three fault scenarios. This is not complete-state recovery.
The [source-confirmed D8 counterexample and candidate tests](flag2_recovery_gap.md)
now explain why those residual flags must not be called recovery.

![Sampled physical damage and residual flags; completed printed-rule run](../figs/gray_physical_faults_20260920.png)

Candidate B (`--flag2-erase at_most_one`) completed the same two-period boxes
and counter draws in **1408.82 s**. Final physical flags are all zero;
its decoded period-boundary outcomes are identical to the printed baseline.
A strict-provenance reset probe clears residual gathered histories, but 6/4
unused primary Info bits remain after the early/late burst: decoded recovery
is not exact full-state recovery. The separate variant/backend and Gray
regression sets pass 29 and 33 tests respectively; see the
[D8 comparison and paired noise audit](flag2_recovery_gap.md).

## Computed-address signal correction (D14)

Gray p.35 specifies **computed Address** when choosing the signal locations.
Two distinguishing tests fail against the previous raw-address implementation:
a wrong raw Address at the intended destination suppresses its primary write;
an unrelated cell with the signal's raw Address receives a spurious primary
write. Local structure repairs in the same step and Flag1 remains zero, so
wiping cannot hide this distinction. The witnesses are about fidelity, not a
proof that one fault defeats the redundant logical signal.
[Failing baseline record](../figs/signal_address_before_20260921.xml).

Gray signal MOV instructions now select their destinations using each holder's
own computed Address, plus the offset of the copy it holds. This keeps the
radius at five: it does not evaluate a neighbor's local rule. NumPy and CUDA
agree. The finite-tower interpreter broadcasts bit-serial comparisons of
`HOLD.Address` to the appropriate Info-copy writers; no extra integer register
or state track is needed. Its supported computed-address MOV contract is
explicitly limited to at most two singleton Info destinations; other forms
are rejected, not silently interpreted with raw controls. Ordinary MOVs and
the historical compressed schedule retain their prior semantics.

Both direct source-contract tests and a 32-site, non-aliased damaged-state upper
ring pass. The latter executes the complete lower stage-five reset/load/local
computation/interpretation and compares **every field/raw track copy**, with
faults forcing both signal guards to differ from raw Address. This is not a
whole upper colony or a complete lower work period.
**3 targeted tests pass in 59.63 s**
([record](../figs/signal_address_targeted_20260921.xml)); the broader reset,
six-phase tower, locality, fivefold and graph suite passes **28 tests in 155.60 s**
([record](../figs/signal_address_regressions_20260921.xml), includes the two direct witnesses).
Lower interpretation gains 762 steps, ending at **954200 < 983040**; both
Gray links still compile within their active intervals. Earlier full-period
archives predate this correction and remain labelled by their exact sources.

Direct packed GPU initialization now matches NumPy initialization exactly for
R=3/5 and 16/20-bit register storage (**3 tests**,
[record](../figs/gpu_initial_20260921.xml)). This avoids a roughly 29 GB unpacked
host track array when initializing a whole 67,108,864-cell Gray lower ring.
The [whole-colony benchmark](../figs/gray_whole_colony_benchmark_20260921.json)
ran 256 genuine trajectory steps on **67,108,864 physical cells** in 17.34 s
(including graph setup), with zero Address/Age errors and 26.86 GB peak PyTorch
allocation. Its average 67.7 ms/step extrapolates to 19.7 hours per lower period
and roughly 2360 years per complete upper period under this brute-force strategy.
These are prefix-based planning estimates, **not** measured full-period times,
lower bounds, or impossibility results; active-stage throughput may differ.
[Checked fixed-point acceleration](exact_acceleration.md) now passes full-protocol
and full-geometry quiet-span bitwise comparisons; it can skip only checked-quiescent noiseless
intervals, not noisy steps or arbitrary simulated transitions.

A checkpointed full-geometry transition pilot reached 256 steps and archived
all 23 source/binary files. Direct execution reached a saved 246016-step state;
after bitwise validation the run switched to a separately archived certified
executor, preserving the direct checkpoint. Its whole upper colony starts at the signal-write phase with seeded
arbitrary workspace/raw copies/registers and one damaged Address; the reference
includes a signal change 0→1 at that damaged site. The end check compares all
504 encoded bits per cell against a direct upper transition.
[Checkpoint](../figs/gray_whole_colony_transition_20260921.npz),
[archive](../figs/gray_whole_colony_transition_20260921_sources.tar.gz).
The [certified continuation](../figs/gray_whole_colony_certified_20260921.npz)
has now completed the lower period: **all 504 encoded bits of all 8192 upper
cells match**, with no sampled physical Address/Age damage. This validates
**one upper microstep**, not a whole upper work period. Continuation timing,
657,947 certified skipped steps, and the explicit direct-process stop are in the
[acceleration report](exact_acceleration.md).
The fresh [four-scenario protocol rerun](../figs/gray_protocol_signal_fix_20260921.npz)
completed **1,048,576 steps in 1505.72 s** under the corrected signal rule.
Every gather, five complete rests, signal, computation and commit check passes
([verified archive](../figs/gray_protocol_signal_fix_sources_20260921.tar.gz)).
The complete default regression suite passes **140 tests**, with one slow test
deselected, in 1551.51 s ([record](../figs/full_regressions_20260921.xml)); the
subsequently added phase-observer tests separately pass three cases.

## Remaining integration requirements

1. Extend the completed paired physical-fault case studies to independent trials
   and iid noise, preserving distinct physical, simulated and full-state metrics.
2. Validate complete Gray-tower dynamics, not only isolated phases. Preserve
   the distinction between a full upper colony and arbitrary short test rings.
3. Resolve D10's computed-SimBit timing and develop exact acceleration for longer
   Gray-tower validation. The corrected one-link protocol is now revalidated.

This Gray schedule still must not be identified with Gács Algorithms 19.5–19.8:
their repeated decode/evaluate/encode and payload-refresh mechanisms remain
additional work, as do arbitrary logical memory and a third simulation link.
