# GacsCA — current research report

Updated 2026-09-24. Goal: a source-grounded Gray/Masumori local automaton,
executable finite-depth self-simulation, and measured noise robustness. **The
project is not complete.** No GKL work is included.

## Current result and its limits

A finite, level-specific **third simulation link** now executes one complete
reduced middle work period: **16,384 middle transitions / 268,435,456 physical
steps**, with every decoded field/raw copy checked. A separate CPU replay checks
all 252 physical-derived diagnostic frames (12,321,792 state elements) and the
independently decoded top-cell transition. Runtime: 4.51 h; 62,618,396 physical
idle steps were skipped only after exact fixed-point certificates.

The top ring has **one cell**, so its neighbors alias. This is not a full top
work period, the full Gray three-link geometry, an encoded universal interpreter,
an infinite construction, or a proof of depth-dependent noise robustness.
[Data, independent replay and scope](third_link_execution.md).
**New non-vacuity finding:** its top track array does not change. An 11-cell
counterexample exposes missing compressed input-cache initialization; supplied
caches fix the macrostep (8 wrong track copies → 0). [Diagnosis](cache_initialization.md).

## Implementation and verification

State fields, redundant bit tracks, encoding, local repair, microcode, work-period
schedule, transport, noise and layer construction are separate modules. NumPy is
the reference; CUDA uses local physical transitions and batched rings on the A100.
All noisy steps use distinct version-2 counters; noisy graph replay is prohibited.

| Implemented / checked | Evidence and remaining boundary |
|---|---|
| Scalar/NumPy/CUDA local colony rules | Source comparisons and damaged-state parity; printed-rule discrepancies remain below. [Audit](audit_20260920.md) |
| Holder-local redundant computation | Single-fault clock/Address coupling fixed; R=3/5 tests. [Details](continuation_20260920.md) |
| Gray's five-stage schedule | Q=8192, U=128Q, R=5; separate gathers, resets, full-register encoding. Four-scenario full-period checks pass. [Schedule](gray_schedule.md) |
| Whole Gray upper colony | 67,108,864 physical cells; all 504 encoded bits of 8192 upper cells match after one lower period. Not a full upper period. [Evidence](exact_acceleration.md) |
| Nested instruction machinery | Local IINIT/register loading/mail/carry/broadcast/evaluation; all emitted middle instructions retained. Dynamic dispatch handles 23 simultaneous clears. [Derivation/tests](nested_interpreter.md) |
| Compact third link | Full 16-bit register alphabet at every layer; R=3/5 transition checks, restart, independent decoding. Complete R=3 middle period above. [Execution](third_link_execution.md) |

The frozen nested-evaluation build passes **340 default tests**, one slow test
deselected ([record](../figs/full_regressions_nested_ieval_20260923.xml)). Later
execution/recorder and fault tools have **21 additional focused passing cases**;
these are separate runs, not a claim of a newer full-suite execution. Exact
[source/backend/data bundle](../figs/third_link_completion_sources_20260923.tar.gz),
[67-member verified manifest](../figs/third_link_completion_identity_20260923.json).
The corrected cache/phase tools separately pass **11 tests in 52.84 s**
([record](../figs/cache_and_phase_verified_tests_20260924.xml)); core transitions
were not changed for this initialization correction.
[New source/audit/plot bundle](../figs/cache_phase_sources_20260924.tar.gz):
[63 verified members and 18 external dataset hashes](../figs/cache_phase_sources_20260924.json),
with all 22 core/backend files identical to the earlier tested archive.

## What the robustness experiments actually show

**Physical islands through the third link:** 24 trials plus a clean control,
widths 1/21/101, one-step whole-cell replacements early or just before update,
two outer periods. Late widths 21/101 damage one middle holder in 8/8 trials;
all decoded fields/raw copies recover by the following period. Independent
inspection verifies that the represented threefold majority restores the bits:

\[
V(x)=\operatorname{Maj}_{r=-1}^{1}X^{(r)}(x-r),\qquad
V_{damaged}=V_{clean}.
\]

But physical **Flag2 remains set in 21/24 trials**, including 5/8 single-cell
faults. Decoded recovery is not complete physical-state recovery. These cases
occur during middle mail shifts, not its nested evaluation phase.
[Counts, retained boundaries, recovery plots and mechanism](third_link_faults.md).

New **nested-evaluation/rollover pilots** use 11 distinct top cells and target
encoded control, Info and HOLD locations. Their CPU-prepared initial phases are
explicitly distinguished from physical history; all subsequent evolution is
physical. The original cold-cache pilots completed but did not activate the
intended BITOP. Corrected pilots target a verified **1→0** computation with
initialized controls. Both completed: control faults leave one wrong HOLD copy
after computation, repaired on the next step; rollover recovery also passes a
second decoding to the fresh top transition. All 12 faulty rings retain excess
physical Flag2. [Audits, counts and plots](nested_phase_faults.md).

**Persistent noise / local structure:** qualitative Masumori behavior is
reproduced, but the reported ≈0.55–0.6 recovery threshold is not. Tested protocols
lose original-phase recovery around ≈0.4; alternative state/noise conventions
have not resolved the discrepancy. [Replication audit](level0.md).

**Redundancy versus depth:** a matched one-link noise-v2 experiment at ε=0.003
observes 1977/2048 decoded cell-period errors at R=3 and 44/2048 at R=5. This is
a finite redundancy comparison, not a hierarchy exponent or threshold. Trials
are independent rings; correlated cell-periods are not independent samples.
[Parameters, uncertainty and raw links](history_through_20260923.md#8-new-matched-redundancy-experiment-corrected-rule).

**Observer dependence:** at ε=0.30, whole-ring sampled phase failures decrease
34→25→4/256 as colony count increases 1→4→16, while fixed-Q-window failures
increase 34→73→131/256. A wrong-phase traveling region was independently replayed.
Neither global averaging nor phase memory establishes arbitrary per-site payload
memory. [Observables and replay](memory_observables.md).

## Fidelity gaps that must remain explicit

- **D8:** the literal printed Flag2 rule has an isolated-error persistence
  counterexample. Defaults remain literal; `no_ones` / `at_most_one` are labeled
  hypotheses, not uniquely source-authorized fixes. [Proof and experiments](flag2_recovery_gap.md).
- **D10:** the computed-SimBit timing is unresolved. A literal post-wipe neighbor
  interpretation has a radius-violation witness; the repaired-Info convention is
  provisional. Computed Address/Age signal and Workspace timing defects were fixed.
  [Discrepancies](discrepancies.md), [source audit](audit_20260920.md).
- **Uniformity / payload:** immutable level-specific tables are not Gray's
  ProgramBit fixed point or a universal encoded interpreter. Further nesting
  beyond the supported control layout fails explicitly. Gács's arbitrary
  per-site Refresh/Compute payload machinery is not implemented.
- Earlier pre-fix hierarchy plots and a quadratic fault-law claim are not valid
  evidence for the corrected rule. [Preserved history](history_through_20260923.md).

## Active run and next concrete steps

The corrected **11-top-cell** run has 2816 middle cells and 720,896 physical
cells. Its 16-period physical pilot passes independent decoding (678,656 encoded
bits); initialization separately passes full CPU and R=3/5 GPU middle periods.
The corrected full physical run is now
running at `figs/third_link_initialized_R3_20260924.npz`, with trace
`figs/third_link_initialized_trace_20260924.npz`. Its immutable
[pilot snapshot](../figs/third_link_initialized_pilot_snapshot_20260924.npz) and
[audit](../figs/third_link_initialized_pilot_audit_20260924.json) remain separate.
It still is not a whole Q=64 top colony. The older cold-cache non-aliased run
was stopped at its saved 192-period prefix; its metadata still says `running`.
Do not resume that old run as valid top-transition evidence. [Exact paths and reason](cache_initialization.md).

1. Complete and independently audit the non-aliased middle period; then test
   whole top colonies and additional periods without substituting host transitions.
2. Extend the phase pilots to low Address bits and multiple middle holders,
   then persistent iid noise, matched sizes/depths and lifetimes
   with independent-ring uncertainty and explicit decoder definitions.
3. Resolve D8/D10 and the Masumori protocol discrepancy alongside these executable
   tests; do not silently modify the source baseline.
4. Develop the missing encoded-program and arbitrary-payload machinery. Finite
   opcode closure and successful noiseless simulation do not replace this work.

Sources: Gray (2001), especially §§5.2–5.5; Masumori, Sinapayen & Ikegami (2024);
Gács (2001), especially §§12–20. [Source relationships and audit](audit_20260920.md).
Latest [hierarchy space-time figure](../figs/third_link_space_time_20260923.png),
[physical island figure](../figs/third_link_islands_verified_20260923_space_time.png).
Full prior chronology, equations, older measurements and failed approaches are
preserved in [history_through_20260923.md](history_through_20260923.md) and linked sub-reports.
