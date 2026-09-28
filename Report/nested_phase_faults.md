# Physical faults at nested evaluation and rollover

**Setup failure discovered:** the first evaluation pilot reaches the IEVAL clock
phase with SimAge=SimAddr=0, not the intended 901/10. The compressed schedule
expects input-control caches supplied at initialization and reloads them at the
end of a work period. The cold initializer supplied only Info. Thus this pilot
does **not** exercise the intended BITOP. Its data are retained as a negative
setup/control test. The [paired CPU experiment](cache_initialization.md) now
confirms that input-cache initialization activates BITOP and fixes the first
top transition (eight wrong track copies → zero). R=3/5 GPU middle periods also
pass. No transition rule was changed.

**Corrected pilots (completed, 2026-09-24):** schema 2 initializes these caches and
targets top cell 8, middle holder **2133**, where the clean IEVAL actually changes
HOLD **1→0**. A preflight gate rejects inactive/value-preserving targets. Eight
[revised protocol/audit/plot tests](../figs/nested_phase_cached_tests_20260924.xml)
pass. Prefixes are `figs/nested_evaluation_cached_20260924` and
`figs/nested_rollover_cached_20260924`. The older protocol below is retained to
explain the failed setup; its target holder 1365 is not the corrected target.

## Corrected results and mechanism

Both seven-ring pilots completed **49,152 physical steps**: evaluation in
446.87 s and rollover in 478.66 s, with concurrent GPU work. All three retained
boundaries pass independent packed decoding and fresh middle-transition checks.
[Evaluation audit](../figs/nested_evaluation_cached_verified_20260924.json),
[rollover audit](../figs/nested_rollover_cached_verified_20260924.json).

| Window / physical target | Trials | Decoded erroneous middle cells after boundaries 1 → 2 → 3 | Raw track-copy errors at boundary 1 | Final excess physical Flag2 cells |
|---|---:|---|---|---|
| Evaluation / control | 2 | 1 → 1 → 0 | 0 | 97, 114 |
| Evaluation / Info | 2 | 1 → 0 → 0 | 6, 4 | 91, 100 |
| Evaluation / HOLD | 2 | 1 → 0 → 0 | 7, 8 | 53, 51 |
| Rollover / control | 2 | 1 → 0 → 0 | 0 | 114, 115 |
| Rollover / Info | 2 | 1 → 0 → 0 | 5, 3 | 101, 101 |
| Rollover / HOLD | 2 | 1 → 0 → 0 | 7, 8 | 53, 53 |

All corrupted middle fields/copies are initially at holder 2133. No repaired
track bit differs from clean at any of the three sampled boundaries. Physical
Address/clock errors disappear by boundary 2. Yet Flag2 remains in excess of
the clean control in **12/12 faulty rings**; this is not full physical recovery.
The rollover clean control itself has 10,858 Flag2 cells at boundary 3 because
of downward flag activity from the arbitrary top input. The table subtracts
that baseline; plots show raw counts explicitly.

The evaluation/control cases now show a non-vacuous computation fault. At the
first boundary, SimAge changes from 901 to 30536/53180 and SimAddr from 13 to
9/8. The next middle step restores those registers by local voting, but the
instruction reads the **old input controls**. The clean BITOP writes HOLD 1→0;
the damaged holder misses it, leaving **one wrong raw HOLD copy** in each trial.
The other copies outvote it, and the following step restores the full raw state.
The physically decoded next state equals the direct transition from the damaged
state: correct simulation and clean-state recovery are different checks.

For the Info-targeted cases, only high SimAddr bits change (46093/44045 versus
13). The selected BITOP uses `(SimAddr + copy_offset) mod 64`, so its effective
address is unchanged. These trials do not test a wrong low-bit address. This
scope limitation is preserved rather than treating all register faults alike.

At rollover boundary 2, a **second independent decoding** of all seven physical
rings matches a fresh top transition in every field/copy. This uses a CPU-prepared
prior middle prefix, not a full physical middle history. The same audit on the
[cold rollover](../figs/nested_rollover_cold_reaudit_20260924.json) finds eight
wrong top track copies in *every* ring, including the clean control, even though
its physical-to-middle simulation is exact. This is the distinguishing negative
control for the initialization correction.

![Corrected evaluation diagnostics](../figs/nested_evaluation_cached_verified_20260924.png)

![Corrected rollover diagnostics](../figs/nested_rollover_cached_verified_20260924.png)

Figures were visually inspected. Counts are exact sampled outcomes, colors use
per-panel log(1+count), and two trials are not a failure-probability estimate.
Next: faults affecting low Address bits, multiple adjacent middle holders,
persistent iid faults, and matched-depth comparisons with arbitrary payloads.

## Original cold-cache protocol (preserved failed setup)

The earlier [third-link island pilot](third_link_faults.md) tested only middle
mail shifts. This experiment asks whether physical islands affecting encoded
control and data fields are repaired across an actual nested BITOP evaluation
and across middle-clock rollover. It does not estimate a noise threshold.

Geometry is the full-register compact R=3 third link: outer Q=256, U=16384;
middle Q=256, U=16384; top Q=64, U=8192. There are **720,896 physical cells,
2816 middle cells and 11 top cells per ring**. Radius-five top neighbors are
distinct, although the top ring is still smaller than one complete top colony.

The starting middle state is prepared by **CPU evolution from the same seeded
top-state prescription** used by the clean checkpoint experiment. It is then
encoded once into a new physical configuration. This is not an executed physical
prefix or a continuation of the long clean run. After initialization, the CPU
only observes/predicts; no reference state is installed in the physical system.

| Window | Initial middle age | Subsequent middle ages | Purpose |
|---|---:|---|---|
| Evaluation | 10691 | 10692, 10693, 10694 | Faulty first boundary is the input to IEVAL index 2, which selects a BITOP |
| Rollover | 16382 | 16383, 0, 1 | Faulty first boundary is the input to the middle-clock wrap/update |

The selected top cell is index 5 (Address 10). Its BITOP destination is held
at middle Address 85, hence middle holder **1365**. At that holder's physical
colony, width-21 one-step whole-cell replacement islands are centered on:

- physical Address 42: an encoded SimAge bit;
- Address 67: the middle raw INFO primary copy;
- Address 148: the middle raw HOLD primary copy.

These labels identify the *centers*, not field-selective noise. Each island
affects neighboring encoded fields/copies, and every physical state field at the
selected sites is replaced. There are two independent RNG trials per center,
plus one clean control: seven rings per window. Seeds are 1400 (evaluation) and
1410 (rollover), initialization seed 1350. This is a small mechanistic pilot,
not a reliable failure-probability estimate or a matched-depth comparison.

Replacement follows transition t=U−2→U−1 of the first outer period. Three outer
periods execute physically, without certified skipping or noisy graph capture.
Version-2 RNG counters use the new physical trajectory's time, starting at zero;
the CPU-prepared prefix is not counted as prior physical evolution.

## Validation and evidence

[Runner](../experiments/nested_phase_faults.py),
[independent packed-boundary audit](../experiments/analyze_nested_phase_faults.py),
[diagnostic plotter](../experiments/plot_nested_phase_faults.py).

Five [protocol/restart/audit tests](../figs/nested_phase_faults_audit_tests_20260923.xml)
pass in 52.23 s; one [plot test](../figs/nested_phase_plot_tests_20260923.xml) passes
in 1.47 s. Tests check actual opcode/holder/field placement, CPU preparation by
evolution rather than clock relabeling, bit-exact split/resume, idempotent
completion, immutable retained boundaries, source identity, independent packed
decoding and distinct control/raw-copy/repaired-track observables. The restart
test uses a shorter initialization fixture, not the scientific phase itself.

Every period boundary stores the physical packed state and initial/ground/decoded
middle arrays. The audit independently decodes physical Info, recomputes fresh
middle transitions from both the clean and previously damaged states, and checks
stored diagnostics. It reports full-state differences separately from majority-
repaired tracks/Info/HOLD and from physical Address/clock and Flag2 counts.
Correct simulation of a damaged middle state is not restoration of the clean state.

## Run status

The cold evaluation pilot completed 49,152 physical steps in 522.55 s. All six
faulty rings match the clean *cold-cache* middle state after period 2, but this
is not active-BITOP robustness. The cold rollover pilot also completed, in
369.10 s, with all decoded errors gone after period 2. Independent packed audits
pass for [evaluation](../figs/nested_evaluation_cold_audit_20260923.json) and
[rollover](../figs/nested_rollover_cold_audit_20260924.json). These
names deliberately remain unchanged so the failed setup and its sources stay
reproducible.
Exact checkpoint prefixes:

```
figs/nested_evaluation_faults_20260923
figs/nested_rollover_faults_20260923
```

Each has a source/backend archive and a resumable `.npz`, with immutable
`_boundary1.npz` through `_boundary3.npz` written as reached. Inspect metadata
before restarting. Next: independently audit each completed pilot, explain
control-field versus redundant-track outcomes, and add exact-count diagnostics.
