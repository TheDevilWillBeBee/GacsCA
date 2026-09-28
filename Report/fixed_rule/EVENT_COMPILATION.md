# Exact physical event compilation and input support

2026-09-26. Two complete lower work periods now take **9.483492 s** of GPU
advance on the established 15-colony fixture, versus **37.209585 s** for the
previous gather backend (3.923616 times faster). Both complete physical
checkpoints, all decoded controller fields, and every event/accounting metric
match the frozen reference. This changes execution cost, not Q, U, the physical
rule, its alphabet, the hard-wired description, or the hierarchy achieved.

## Construction and equivalence obligations

The first private backend, `small_holder_register_events.py`, retains only the
18 outputs that the independent/gather event loops actually consume: Data,
head, all controller fields, and both packet records. Pure DAG pruning removes
unreachable arithmetic from the existing 1785-operation canonical physical
prefix expression, leaving 1564 operations. It emits each intermediate as a
local unsigned 64-bit C++ scalar. The CUDA compiler can keep these intermediates
in registers rather than writing the caller-owned global workspace after every
operation. Inputs, arithmetic, and output destinations are unchanged. Right
shifts of at least 64 still return zero; addition and NAND remain unsigned.

The second private backend, `small_holder_supported_events.py`, gathers all and
only the expression's 70 referenced words, out of the previously filled 352.
The support consists of fields at offsets -1, 0 and 1 and Data at offset 2.
Static fields come from the same immutable ROM. Mutable Data and controller
inputs come from the same physical event neighborhood as before, including
left-colony wrap. Every referenced packet word is explicitly zero, exactly as
in the original `independent_input`: independent batches reject actual mail;
gather batches separately advance actual packets with collision, delivery-order,
and protected-access checks. The head-input condition retains both the source
colony and head-address tests. No uninitialized referenced word is permitted.

This is the coherent logical representation of the existing radius-seven holder
rule; the smaller core input support does not assert a smaller physical radius.
The transform does not evaluate a simulated upper transition on the host, select
a kernel by hierarchy level, substitute a different interpreter, or skip an
additional physical tick. All batching distances, barriers, rejection rules,
atomic staged commits, and fallback steps are the frozen ones. Synchronous
boundary transitions retain the complete original physical prefix expression.
Unused output fields are not installed as a purported complete physical state:
these event loops already reconstruct geometry, flags, and stationary Signals
through their existing certified representation. The consumed outputs are all
retained.

Generated CUDA files live in separate content-addressed directories under
`figs/fixed_rule/build/`. The original sources and binaries remain untouched.
The supported backend inherits the same immutable initializer interface; this
experiment does not run an entire depth-two allocation. Its domain remains the
older canonical/coherent gather domain with left Signals zero. The newer general
flag and physical-exception backends are not silently switched to this compiler.

The scientific interpretation remains the specialized self-description approach
in Gray pp.31–32 and Gacs sections 9.2–9.3, discussed in SMALL_HOLDER_CLOSURE.md.
Those sources motivate self-simulation of a suitably modified rule; they do not
justify removing actual dependencies or prove this compiler's correctness.
Candidate-B Flag2 and old-Signal D10 remain explicit source-fidelity limits.

## Executed validation

```sh
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_register_events.py -v
# 3 tests, 16.789 s, OK (including private build).
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_supported_events.py -v
# Final v2: 4 tests, 16.800 s, OK (including private build).
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_register_periods --output figs/fixed_rule/small_holder_register_periods_v1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_supported_periods --output figs/fixed_rule/small_holder_supported_periods_v1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_event_emission --register-result figs/fixed_rule/small_holder_register_periods_v1.json --supported-result figs/fixed_rule/small_holder_supported_periods_v1.json --output figs/fixed_rule/small_holder_event_emission_audit_v1.json
```

Tests cover arbitrary width-valid neighborhoods, exact expression output slicing,
actual SEND/WRITE/META controller execution, complete checkpoint comparison,
collision rejection with no committed mutation, fallback, and poisoning all
unused input words. The initial supported-input test run failed on a conservative
source-matching guard that counted `==` as `=` and on missing diagnostic aliases.
No physical comparison failed: those cases stopped before construction. Both
issues were fixed; `small_holder_supported_events_tests_v1.log` preserves the
failed attempt, and v2 preserves the passing run.

The independent audit establishes structural equality of the selected expression
DAGs, then compiles the scalar emitter separately with g++. It checks 1024
arbitrary/boundary neighborhoods twice, including poisoned unused inputs: 2048
compiled-C comparisons, including untouched output words and allocation canaries.
The GPU drivers compare all 154 decoded raw words, every coherent core/tail row,
and every gap row at both commits against the frozen reference archive. Host
physical/upper-rule evaluation is forbidden during advancement. All accounting
metrics are identical: 8589934592 physical ticks, 4760 independent batches,
6421740 colony literal events, 17768670 logical local evaluations, and two
rejected batches with normal fallback. Full physical trajectory equality is a
runtime check in the hashed drivers, at the stated checkpoints; the later audit
checks their provenance and does not independently replay that whole trajectory.
The audit passed in 1.473235 s with 64452 KiB host RSS.

## Resource measurements and practical implications

| Same 15-colony, two-period fixture | GPU advance | Whole run | Host peak | GPU process |
|---|---:|---:|---:|---:|
| Previous gather backend | 37.209585 s | 52.386922 s | 563896 KiB | 424 MiB |
| Scalar event outputs | 22.000456 s | 37.212113 s | 563732 KiB | 424 MiB |
| Scalar outputs plus exact input support | 9.483492 s | 24.337732 s | 564068 KiB | 424 MiB |

The physical world still has 491520 sites. Explicit resident/peak buffers remain
5116680/6331080 bytes. The register-only event kernels use 255/254 registers for
gather/independent execution with zero spill bytes and 48-byte stacks. Narrower
input loading uses 255 registers in both kernels, with 4/16-byte spill stores
and loads and 56/64-byte stacks. Despite those small spills, removing unused
neighborhood loading improves measured execution. These are individual timings
against a historical reference, not a controlled throughput distribution.

The final interval timings total 3.772608 s before the first vote and 5.710884 s
later across both periods. No extra simulation capacity or successful higher
hierarchy level is inferred. U remains 2^32. Merely repeating the measured
15-colony per-period cost U times would take about 645 years; that illustration
is not a runtime prediction for the much larger Q-colony nested world. It shows
why this constant-factor improvement alone cannot close the practical target.
A substantive next step must reduce nested work through a justified construction
or certified trajectory composition, while retaining the actual physical
controller and intermediate-state relation. More small window runs cannot
substitute for that obligation.

Exact scalar-event binary SHA256: `7216ecbe8f36fe1adba65d469480924f34583ad2025bbe35b111c25fba2f5f27`.

Exact supported-input binary SHA256: `4419e5fdd8caeb81c884db3ede3d709d677693aee1943482040e171bc54f1c7e`.

Manifest `figs/fixed_rule/small_holder_register_periods_v1.json` SHA256: `27df9bfc9e8f1c0d4d493f0cf012cf125ba997e17c48c96948addb3f32985d40`.

Manifest `figs/fixed_rule/small_holder_supported_periods_v1.json` SHA256: `1732b823c8e1a66491ddf9f5e4dc047d6f06bb629f60d5251e59233e2b080ac5`.

Manifest `figs/fixed_rule/small_holder_event_emission_audit_v1.json` SHA256: `2df7697245d4deef866648ba17eb47dbe57486a1954e5163255ae2e94eeb7e92`.

Physical description remains
`af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`;
ROM remains `c59c72abe15729e4848ce549b31f1faec63465f16da2c717f0eb233fb1e7cbe4`.

## Ownership and unfinished goal

Owned additions: the two backend modules, two test modules, register/support
period drivers, emitted-expression audit, this report and namespaced evidence.
STATUS.md is updated; no shared dependency, report, historical dataset, or CUDA
artifact was changed. The full goal remains active: whole nested upper periods,
finite-depth boundary dynamics, and general cross-level noise amplification are
unproved. MAIN_AGENT_NOTES.md is absent; the separate 8 GiB allocation request
remains pending and no large allocation was launched. The protected historical
third-link process was not observed; that does not establish its completion.
