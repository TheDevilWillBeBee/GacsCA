# Historical project report through 2026-09-23

This chronology is preserved intact apart from this heading. Some status and
next-step statements describe earlier stages. The compact current report is
[REPORT.md](REPORT.md); source/data archives provide immutable historical evidence.

Last updated: 2026-09-23. Source audit: [audit_20260920.md](audit_20260920.md).
Latest implementation/validation: [continuation_20260920.md](continuation_20260920.md).
New source-timed compiler: [gray_schedule.md](gray_schedule.md).
Printed-rule recovery counterexample: [flag2_recovery_gap.md](flag2_recovery_gap.md).
Memory metrics and missing payload machinery: [memory_observables.md](memory_observables.md).
Checked noiseless acceleration: [exact_acceleration.md](exact_acceleration.md).
Third-link component progress: [nested_interpreter.md](nested_interpreter.md).
Checkpointed physical third-link runs: [third_link_execution.md](third_link_execution.md).
Physical islands and observed higher-layer repair: [third_link_faults.md](third_link_faults.md).
Sub-reports: [design_selfsim.md](design_selfsim.md),
[discrepancies.md](discrepancies.md), [level0.md](level0.md), [selfsim_stage1.md](selfsim_stage1.md),
[selfsim_stage2.md](selfsim_stage2.md).

## 0. Goal and status in one paragraph
Build an executable, source-grounded Gray/Gács automaton and study finite-depth robustness.
The inherited project contains scalar/NumPy/CUDA local rules, a colony computer, and a
finite tower with **two simulation links (three dynamical layers)**. Clean decoding was
previously checked across phases and one complete upper work period. This is a reduced,
level-specific construction; full Gray-tower execution, uniform self-simulation,
arbitrary logical memory, and long-time three-link validation remain incomplete.
The finite third link now passes **one complete reduced middle work period**
(268 million physical steps), independently replayed and decoded through two
layers; its single periodic top cell remains an explicit limitation.
The new audit found and fixed a **single-cell clock/address fault channel**: all backup
computations had trusted the same raw control fields. Each holder now computes independently,
as Gray's redundant-procedure requirement demands. New targeted tests pass for R=3 and R=5.
Fivefold tower interpretation now passes damaged-state transition tests; the noise
generator has been corrected for long trajectories and very small probabilities.
An explicit five-stage schedule with stage resets and three separate gather
histories is now implemented, including reset-safe upper-track interpretation.
A one-link full-period protocol passes all four scenarios under both its archived narrow
encoding and its full-register-alphabet replication. Gray-tower phase
tests pass, but do not establish a complete upper work period.
Old hierarchy noise/island measurements below describe the **pre-fix rule** and need
replication; the claimed quadratic fault law is not established.
The literal printed Flag2 rule also has a verified isolated-error persistence
counterexample (D8); resolving this source discrepancy is now a fidelity priority.

## 1. Sources and how they relate
- Gács 2001 (J. Stat. Phys. 103) — the full construction: media, block codes, amplifiers, robust
  media, a rule language, and the program (Secs 12–20). Nearest-neighbour, variable cell kinds.
- Gray 2001 — Reader's Guide: a simplified range-5 model with fields Address, Age, Flags,
  SimBit(5), Workspace, Mailbox; Q colony size, U = 128Q; Props 1–5.
- Masumori, Sinapayen, Ikegami — Java implementation of Gray's local structure only
  (no self-simulation), Q = 271, recovery vs error rate. The [arXiv record](https://arxiv.org/abs/2405.04060)
  identifies this as a 2018 manuscript uploaded unchanged in 2024.

## 2. Model (level 0) — implemented
Ring of L = ncol·Q cells, neighbourhood N(x) = {x−5..x+5}. Fields: Address ∈ [0,Q),
Age ∈ [0,U), Flag1, Flag2 (+ Workspace.Flag1/2 read from the simulation structure).
Apparent colony C(x): the position v of x such that ≥3 of the five sites x+i (i=1..5) satisfy
(Address(x+i) − i) mod Q = v. Inconsistency (i)–(iv), Flag1 and Flag2 rules, and the Address/Age
majority votes are transcribed literally in `gacsca/level0_spec.py` (Gray pp. 20–22). Ambiguities
and Masumori's modifications are catalogued in [discrepancies.md](discrepancies.md); the main
finding is that two of Masumori's three "errors in Gray" are not errors (D2, D4).

Noise: each cell independently with probability ε per step is replaced by a uniformly random
state (Address uniform in [0,Q), Age in [0,U), flags uniform) — Gray's ε-perturbation with a
strictly positive ν.

Code: `gacsca/level0_np.py` (NumPy, batch×L), `gacsca/cuda/gacs_cuda.cu` (CUDA, one thread per
cell, hash-based reproducible noise), `gacsca/gpu.py` (torch front-end). Tests: `tests/`
(spec ≡ NumPy ≡ CUDA on random and near-ground configurations; noise statistics).

## 3. Level-0 results (details in [level0.md](level0.md))
- Qualitative reproduction of Masumori Fig. 7A: leftward Flag1 waves confined to colonies; after
  the noise stops, Flag1 clears in a wave from the right end at speed ≈ 2.7 (Gray: ≥ 1.75).
- Recovery threshold (500 noisy steps then 500 clean, Q=271, 4 colonies, 256 trials/point):
  P(Address fully recovered) = 1.00 up to ε = 0.34, 0.92 at 0.38, 0.27 at 0.40, ≈0 at ≥ 0.42.
  Masumori report failure only above ≈0.55–0.6; this discrepancy is unresolved (D7). A corrected
  mean-field recursion c' = (1−ε)[c + (1−c)g(c)], g(c) = P(Bin(5,c) ≥ 3), gives ε_c = 0.334;
  spatial correlation (colony structure) pushes the real threshold up to ≈0.40.
- Q dependence: smaller colonies are less robust (Q=32: threshold ≈0.33; Q ≥ 271: ≈0.40).
  Larger systems fail slightly earlier (more colonies, more chances for one to fail).
- The Masumori rule variant (Flag1 (ii) counting all of R(x)) is slightly less robust.
- New protocol audit: neither full-bit-width noise nor disabling the unimplemented
  Workspace flags resolves the published threshold discrepancy. At ε=0.5, original-phase
  recovery is 0/128 in every tested variant, although 15–22/128 rings recover spatial
  order at another phase. [Details and counts](level0.md#replication-audit-2026-09-20).

![level-0 recovery](../../../figs/legacy_tower/level0_recovery.png)

## 4. Self-simulation design (summary; full text in design_selfsim.md)
Level-specific finite rules; simulated state laid out one bit per cell on the Info track; R-fold redundant
tracks; two timed mail streams retrieve all 10 neighbour colonies (sample MailL at t0+jQ);
three gathering stages with majority; an Age-scheduled microprogram (compiled from a Python
DSL into an op table) computes the simulated transition bit-serially; the same table is used to
interpret the simulated cell's own microstep (self-reference without an interpreter string).
Exact noiseless CUDA-graph replay now accelerates long runs. A third simulation
link now passes a complete reduced middle work period; a full top work period,
the full Gray three-link schedule and noise-depth robustness remain unvalidated.

## 5. Stage-1 results (summary; details in selfsim_stage1.md)
- Block simulation verified (decoded == direct). Work period 8010 steps (U = 8192), K = 210 bits.
- Historical noise runs found induced errors well below the local structure's noise threshold.
  Their attribution to ε₁ ∝ QUε² is withdrawn after the single-fault counterexample; reruns
  with independent-trial uncertainty are underway.
- Misaligned-colony island: fixed point for level-0 rules; with trickle-down it becomes a glider
  (erodes 3 colonies/period on the left, invades 3 on the right) until a level-2 boundary.

## 6. Stage-2 results (summary; details in selfsim_stage2.md)
- Tower: level 0 (Q=256, U=16384) → level 1 (Q=64, U=4096, full rule) → level 2 (Q=16, local-only).
- Historical interpretation phase: 1505 level-0 steps per period; `tower_acid.py` ALL OK on 8 phase cases; a full
  level-1 work period (6.7×10⁷ level-0 steps) reproduces the level-2 transition exactly
  (`tower_full_period.py`: RESULT OK), **before the current corrections**, on a one-terminal-cell ring.
- Self-reference boundary documented: a uniform rule needs one integer register pair per nesting
  depth. Gács's data-driven interpreter avoids it; his runtime upper bound does not
  establish a necessary execution cost or infeasibility.
- R=5,D=1 tower now supported: (Q₀,U₀)=(512,32768), (Q₁,U₁)=(64,8192).
  K₁=343; every field and all 61×5 raw track copies match damaged upper transitions
  across operation types, gather receives, trickle, and commit. A complete upper
  work period is a separate, longer validation requirement.
- Injected islands: 1 misaligned colony heals at level 0; 2–3 misaligned colonies are level-0
  fixed points and heal at depth 1 (period 80); time-misaligned islands heal at depth 1 in 2
  periods; random bursts (up to 2000 cells × 500 steps) heal at level 0 within 3 periods.

## 7. Current audit and next concrete steps

- Third-link components now implemented: nested `IINIT`, `BUSLATCH_INT`, `IBC`,
  `ICHAIN`, `ILATCH` and `IEVAL`, with explicit inner tables and an optional second
  raw-input control pair. Local loading, repair, reset, independent noise,
  16–31-bit packing and restart are tested. **One reduced middle work period now
  passes; a complete top work period and depth-dependent robustness do not.**
- Nested evaluation passes **30 component tests**, including independent carry
  truth tables, local operand transport, raw-control faults, complete reduced
  outer periods and full-Q Gray stage five. **Five integration/compilation tests
  pass**: every emitted middle family runs in unprojected reduced R=3/5 programs;
  complete programs also compile within the Gray budget. **Two whole-middle-colony
  tests pass four consecutive outer periods** across evaluation and rollover
  boundaries; the explicit layer-extension factory also passes two tests.
  [Evidence and limits](nested_interpreter.md#nested-evaluation-and-full-opcode-closure-2026-09-23).
- Latest latch build passes **46 tests**: complete reduced outer periods at
  all tested speeds (R,D)=(3,3),(3,2),(5,1), spatially distinct source bits,
  all emitted operand classes, guard and holder-fault witnesses, and full-Q
  Gray stage five with all 512 encoded bits/20-bit controls. Earlier archived
  latch build also completed **148 component/backend regressions**. Earlier
  archives separately pass 222 full-suite tests (broadcast build, one slow
  test deselected) and 82 nested-component tests (carry build).
  [Evidence and snapshots](nested_interpreter.md).
- The 23-simultaneous-clear dispatch barrier is now removed without changing
  the middle rule or state alphabet. **13 new tests pass**, including actual
  23-clear transitions, a 67-instruction old-state/guard-order witness, and
  retained scratch-slot bounds. Full middle programs now compile together at
  the tested geometries; the full Gray diagnostic has 10,766 active steps spare.
  Opcode closure is not an encoded universal interpreter or long-time validation.
  [Updated inventory](../../../figs/legacy_tower/nested_inventory_closed_20260923.json).
- The archived **pre-IEVAL dispatch build** completed **304 default tests**, one
  slow test deselected, in 2436.13 s. This broad result does **not** cover the
  later nested-evaluation changes. [Record](../../../figs/legacy_tower/full_regressions_dispatch_20260923.xml).
- The subsequent frozen nested-evaluation build completed **340 default tests**,
  one slow test deselected, in 4007.00 s. The later experiment/recorder and fault
  tools have 21 additional focused passing cases, reported separately.
  [Full-suite record](../../../figs/legacy_tower/full_regressions_nested_ieval_20260923.xml).
- Compact third-link geometries now pass execution checks. A new checkpointed
  runner preserves the **full register alphabet at every layer**, checks each
  physical-to-middle transition and compares the top endpoint independently.
  Six full-alphabet integration/restart checks and two standalone middle-period
  endpoint checks pass. The 16-period physical R=3 pilot passed, and an independent
  CPU decode audited all 61,696 encoded bits after 128 and 384 periods without
  mismatches; the 384-period physical checkpoint is preserved immutably.
  The full **16,384-transition middle period completed** in 4.51 h. Fresh CPU
  replay matches all 252 recorded physical-derived frames and independently
  verifies the decoded top microstep. The one-top-cell aliasing remains explicit.
  Actual middle-level space-time diagnostics and immutable source archives are saved.
  [Parameters, evidence and scope](third_link_execution.md).
- Removing the one-cell alias: an 11-top-cell pilot (720,896 physical cells)
  passes 16 periods. Its full middle-period continuation is running with exact
  checkpoints; approximately 30+ hours is an estimate, not a completed result.
  This ring has distinct radius-five neighbors but is not a whole top colony.
- **24 physical island trials**: late widths 21/101 corrupt one middle holder in
  8/8 cases; all decoded fields/copies recover by the next outer period. Direct
  inspection verifies the represented threefold-majority repair. Physical Flag2
  remains set in 21/24 trials, so this is **not full physical-state recovery** or
  a depth-scaling result. [Data, plots and mechanism](third_link_faults.md).

- New tests: 22 adversarial redundancy tests pass (including two full-period GPU cases);
  four existing CUDA/NumPy engine tests pass after the correction. Two damaged-state tower
  tests pass after fixing Workspace flags to use computed simulated Address/Age.
- Clean tower rerun: all 48 simulated transitions match every encoded field/track;
  [saved log](../../../figs/legacy_tower/tower_audit_20260920.log). Earlier audit: **56 tests passed**: 52 in the full default
  suite (1066 s; [record](../../../figs/legacy_tower/verification_20260920.xml)), plus two locality tests
  including Q=8192 and two simultaneous-clock-fault threshold tests added during that run.
- The old depth-2 island process is **stopped**, not running: its log ends at period 11968
  with 236 misaligned level-1 cells. Recovery has not been demonstrated in that run.
- Noise counter **fixed**: version 2 independently mixes the 64-bit time and batch/site
  tuple and uses 53-bit probability resolution; exact CPU/GPU and restart tests pass.
  Version 1 is retained for historical replay. The table below used version 1.
- Noiseless graph replay and atomic checkpoints pass 10 tests, including inconsistent
  track states and write failure. A real resumed 4-period GPU run matches all 18 state
  arrays of its uninterrupted counterpart. Corrected full-period validation **completed**
  via `experiments/tower_checkpoint.py` (R=3, one terminal cell): **4096/4096 transitions**,
  every encoded field/raw copy checked, zero mismatches or physical Address/Age damage.
  Both decode routes match every terminal field after the top transition.
  [Checkpoint and all diagnostics](../../../figs/legacy_tower/tower_checked_R3_20260920.npz); 1637 s wall time
  with other GPU jobs running. This remains a reduced-parameter, one-terminal-cell baseline.
- Combined current regressions: **50 passed** in 53.44 s ([record](../../../figs/legacy_tower/continuation_regressions_20260920.xml)).
  Full-Q schedule audit confirms a clean third-gather write during Gray's first rest
  (D12); [timing comparison and witness](continuation_20260920.md#fidelity-priority).
  Two additional tests demonstrate a scratch island surviving the required period-boundary
  reset. They document a fidelity gap, not a correct implementation of Gray's reset.
- Resolve Gray's computed-SimBit timing. Damaged-address flag placement is now
  corrected in Gray mode (D14): failing source-contract witnesses became passing
  direct and interpreted tests; 28 regression and 3 targeted tests pass (overlapping
  suites). The interpreter still fits the active-stage budget.
  [Implementation and evidence](gray_schedule.md#computed-address-signal-correction-d14).
  The post-correction full default suite passes **140 tests** (one slow test
  deselected); the full four-scenario one-link protocol also completed with
  every diagnostic passing, **1,048,576 steps, 1505.72 s**.
  R=5 interpretation is now implemented,
  but fivefold storage does not supply missing temporal isolation automatically.
- Whole Gray upper-colony geometry now executes: a 256-step prefix on
  67,108,864 physical cells passes structure checks (17.34 s, 26.86 GB peak
  allocation). The source-archived full lower-period validation now **passes**:
  all 504 encoded bits of all 8192 upper cells match. This checks one upper
  transition, not an entire upper period. Prefix throughput suggested roughly
  20 hours without acceleration; multi-level
  long-time studies need measured optimization/exact acceleration, not only
  larger brute-force loops. [Benchmark and validation scope](gray_schedule.md).
- Checked noiseless acceleration now passes 14 differential tests and a complete
  four-scenario protocol: all packed words/events/rest hashes match direct
  execution, while 647,847 steps are skipped only after fixed-point checks.
  A whole-size fork also matches all **1.34 billion packed words** of a direct
  checkpoint. The full-size continuation completed with 657,947 certified
  skipped steps and no sampled structure damage; no full upper work period is
  claimed. [Proof conditions, timing and parity records](exact_acceleration.md).
- New persistent-noise phase-memory runs use a strict-majority two-phase observer,
  64 independent rings, Q=271 and four colonies. In 10,000 steps, printed/B
  variants show 6/7, 24/24 and 58/58 rings with sampled erasures at ε=0.30,
  0.32 and 0.34; none give the opposite bit. Some erasures later recover.
  This is local-only, sampled observer performance—not irreversible memory loss
  or an arbitrary payload result. [Data, censoring and bounds](memory_observables.md).
- A paired-observer size study and independent replication expose a decoder
  effect: at ε=0.30, whole-ring sampled failures fall 34→25→4 out of 256
  for 1→4→16 colonies, while fixed-Q-site failures rise 34→73→131.
  Exact replay confirms one fixed-window wrong-bit excursion: a wrong-phase
  region travels through the window and persists elsewhere after window
  recovery. Whole-ring averaging is not evidence of improved local repair;
  both observers and initial-bit strata must accompany size/hierarchy comparisons.
- New `schedule="gray"` mode implements the five stages and resets at full physical
  Q=8192,U=128Q,R=5. Tests cover all reset masks and a full fifth-stage computation:
  one corrupted gather is corrected; two provide the expected failing control.
  The archived full period completed **1048576/1048576** steps, all four scenarios,
  all gathers/rests/signals/HOLD/commit checks passing (16 upper cells, no neighborhood aliasing).
  Wide 16–31-bit registers and reset-safe stage-five input loading now support
  Gray tower compilation and six-phase dynamic tests. An alphabet audit exposed
  a legacy encoding gap (D13); Gray defaults now encode the actual full register
  alphabet. The enlarged-alphabet replication completed **1048576/1048576** steps,
  all four scenarios and every diagnostic passing (1222.66 s wall time);
  [implementation and evidence](gray_schedule.md).
  Combined reset-extension regressions: **66 passed**; the final padding/latch fix
  separately passed all 12 affected schedule/reset tests.
- Then repeat full-period and island experiments, add logical memory and lifetime/size/depth
  studies, and extend to three simulation links. See the [audit](audit_20260920.md) for evidence.
- Physical 200×200 fault-box diagnostics completed two periods at full Gray parameters. The
  early burst restores Address/Age within the sampled (16,57]-step window after
  noise stops, but Flag2 persists. A new D8 invariant proves the literal printed
  rule cannot clear isolated interior Flag2 islands in an otherwise healthy
  configuration. A late burst corrupts one simulated cell at the first boundary;
  all eight decoded fields recover by the second, but physical Flag2 errors remain.
  Candidate corrections are explicit opt-ins, not silently substituted (29 + 33
  targeted/regression tests pass, plus three local recovery contracts). The paired
  candidate-B trajectory completed both periods with all physical flags cleared;
  decoded errors/recovery are identical to the printed baseline. Unused Info
  remains damaged under both rules even after scratch reset, so this is not
  full-state recovery. A 128-ring/point paired level-0 audit finds identical
  address-recovery outcomes across all three erasers, not a resolution of the
  published threshold discrepancy. [Results and uncertainty](flag2_recovery_gap.md).

## 8. New matched-redundancy experiment (corrected rule)

`experiments/redundancy_noise.py`: Q=256, U=32768, D=1 at both R values;
top local-only rule Qs=16, Us=2048; 16 independent rings × 32 colonies × 4 periods
= 2048 observed cell-periods per point. Initial simulated Age=777; noise replaces whole
physical cells after each step. Metric: any decoded Address/Age/Flag1/Flag2 mismatch
against the upper rule applied to the previous decoded configuration. No burn-in excluded.
The following table uses legacy noise generator version 1; see the completed version-2
replication below.

| Physical ε | R=3 errors / 2048 | R=5 errors / 2048 |
|---|---:|---:|
| 0 | 0 | 0 |
| 10⁻⁵ | 0 | 0 |
| 3×10⁻⁵ | 2 | 0 |
| 10⁻⁴ | 10 | 0 |
| 3×10⁻⁴ | 62 | 0 |
| 10⁻³ | 618 | 2 |
| 3×10⁻³ | 1974 | 35 |

At ε=10⁻³ the measured rates are 0.302 (ring-bootstrap 95% interval 0.279–0.324)
and 0.000977 (0–0.00244), respectively. Fivefold redundancy markedly improves this
finite experiment. No exponent, threshold, logical-memory lifetime, or hierarchy-depth
advantage is inferred. Zero observed errors are not proof of zero risk: with 16 independent
rings, the one-sided 95% bound on **a ring having any error in four periods** is 0.171.
The 2048 cell-periods are correlated; they are not 2048 independent Bernoulli trials.

![Matched redundancy and independent-ring uncertainty](../../../figs/legacy_tower/redundancy_comparison_20260920.png)

Raw trial counts, physical structure damage, seeds, parameters, environment and source hashes:
[low-noise JSON](../../../figs/legacy_tower/redundancy_noise_20260920.json),
[high-noise JSON](../../../figs/legacy_tower/redundancy_noise_high_20260920.json).

Version-2 replication (same geometry and trial count, independent pseudorandom streams):

| Physical ε | R=3 errors / 2048 | R=5 errors / 2048 |
|---|---:|---:|
| 0 | 0 | 0 |
| 10⁻³ | 628 | 0 |
| 3×10⁻³ | 1977 | 44 |

At ε=0.003, R=5 rate = 0.02148, ring-bootstrap 95% interval 0.01563–0.02783;
15/16 rings have an error. At ε=0.001, zero R=5 errors still leaves the same
0.171 one-sided bound on four-period ring risk. The qualitative redundancy
contrast survives the RNG correction; zero versus two observed errors at the
lower rate does not establish a change in the underlying error law.
[Raw v2 trials](../../../figs/legacy_tower/redundancy_noise_v2_20260920.json),
[v2 figure](../../../figs/legacy_tower/redundancy_noise_v2_20260920.png).
