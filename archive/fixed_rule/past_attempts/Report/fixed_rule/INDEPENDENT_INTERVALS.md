# Independent local event times between common physical barriers

2026-09-26. This accelerator addresses the measured failure of shared-time event
skipping when colonies query different metadata addresses. It retains the same
physical rule, complete self-description, ROM and coherent representation as
[RESIDENT_PERIOD.md](RESIDENT_PERIOD.md). It introduces no evaluator opcodes,
physical state fields, encoded-level cases or alternate upper transition.
Seven tests pass; the distinct-query benchmark passes through 257 colonies.
The end-to-end two-period comparison also passed with identical complete physical
checkpoints and a measured 2.414456-fold GPU-advance speedup.

## Exact factorization domain

A batch starts from a valid resident state with common canonical Age and Address.
Each colony has at most one head, inside the fixed ROM core; all other controller
words and every mailbox word are zero. Signals have their actual stable five-copy
boundary layouts. The duration cannot cross a reset, temporal vote, capture,
activity-phase change, Wf boundary or final commit. The suffix retains the
restricted flag-profile/Signal conditions described in RESIDENT_PERIOD.md.

On this domain, evolving controller/Data dependencies separate by colony:

1. Canonical first/last markers reflect the sole head within the ROM core.
   It cannot enter the tail/gap or another colony. Only that head can write Data.
2. With no mail, no changing Data or controller field travels across a colony
   boundary. The logical transition at a head near Address zero can read a
   neighboring tail, but those tail Data fields are immutable in the batch.
   The ROM core plus its halo ends before the next colony's mutable memory.
3. All Signals remain in their checked stationary patterns. Geometry stays
   canonical. In the suffix, the separately certified flag recurrence is
   compatible with zero mail and unchanged Address, so it does not clear or
   otherwise alter Data/controller evolution.
4. Every generated local output is checked for mail before it is accepted.
   If any colony emits a packet, the entire staged batch is discarded, including
   earlier writes in every colony. Unsupported states and event-budget exhaustion
   likewise leave the committed state and common clock unchanged.

Thus the admitted per-colony evolution operators commute over the interval.
Different event counters are execution bookkeeping, not physical Age registers:
the returned state has a common time and equals the synchronous orbit at that
barrier. An intermediate set of unequal execution counters is not asserted to
be a physical CA configuration.

## Implementation and locality

`small_holder_resident_independent.cu` includes the frozen resident backend and
calls its exact generated local expression for every literal operation. There
is no handwritten opcode execution path. At each head event it evaluates the
old head site and its possible in-core destinations, using actual radius-five
logical neighborhoods. The coherent lift gives the original radius-seven raw
physical rule. Data reads for these evaluations stay in that neighborhood.
Old inputs are evaluated before any resulting Data writes are installed.

Between events, the head follows the same certified flight/reflection and WAIT
countdown used by the synchronous backend. The stop address is determined by
current controller fields and fixed ROM layout; it is not a distant Data read.
A halted or absent head leaves Data unchanged. Stationary Signal holders retain
their actual positions even when a moving head shares a holder.

The kernel uses 256 worker workspaces. Each worker may process more than one
colony, allowing counts above 256 without additional physical state or a new
kernel. A separate staged Data bank and the resident next-record workspace
hold all tentative changes. Only after every colony succeeds are Data, records,
counts and the common Age committed. An event budget bounds kernel work and
has no physical-rule meaning. A rejected batch can be retried synchronously.

`World.batch` exposes the guarded interval. `World.advance` partitions time at
the fixed physical barriers and a bounded execution chunk. It uses the frozen
synchronous transition for barrier operations, inactive intervals, and rejected
communication intervals. CUDA errors propagate; only explicit batch-domain/
event-limit rejection invokes fallback. It never installs host-computed decoded
states. The physical descriptor remains
`af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`.

The additional peak device storage is exactly 79416 bytes per colony for its
staged Data bank. All host transfer buffers are proportional to colony count,
not Q times the count. For 15 colonies, staging adds 1191240 bytes. The unchanged
resident state costs 5116680 bytes, for 6307920 explicit bytes at peak. No nested
Q-colony allocation has been performed.

## Tests and distinct-address benchmark

```sh
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_resident_independent.py -v
# v1: 5 tests, 32.376 s, OK.
# v2: 6 tests, 35.347 s, OK.
# v3: 7 tests, 32.733 s, OK.
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_independent_scaling --output figs/fixed_rule/small_holder_independent_scaling_v1.json
# Passed, 2.109227 s total, 165524 KiB host RSS.
```

Tests compare complete coherent core/tail arrays and raw boundary/controller
samples with the synchronous backend. They cover the actual ROM instruction
kinds, active phases, Data writes, metadata fallback, waiting, halt, reflection,
stationary left/right Signals, active Flag1 with a live WRITE, and a direct
full-native physical step. Host evaluator/upper-rule calls are forbidden during
the independent call. Rejection tests include actual packet emission, an event
limit after a staged write, multiple heads, mail/controller residues, malformed
Signals and crossed barriers. Integration tests cover communication fallback,
resets, inactive phases and wrap into the following work period.

The scaling fixture starts distinct READ_META controllers, requests count+8
physical ticks, and checks the resulting moving controller state in every colony.
The eight-colony test additionally compares its complete stored physical state.
The 257-colony case exercises reuse of the 256 worker workspaces. Measurements
below are single warm calls, not a statistical benchmark or a nested runtime
estimate:

| Distinct-query colonies | Independent | Synchronous | Ratio |
|---|---:|---:|---:|
| 1 | 0.142 ms | 0.282 ms | 1.99 |
| 8 | 0.221 ms | 1.757 ms | 7.96 |
| 32 | 0.533 ms | 14.165 ms | 26.59 |
| 128 | 0.580 ms | 161.050 ms | 277.70 |
| 257 | 0.709 ms | 615.365 ms | 867.92 |

Each colony executes one literal event independently. The old shared schedule
instead executes count literal global ticks for distinct queries. Synchronized
queries are also measured in the JSON; their old schedule already needs one
literal tick. The result resolves this specific synchronization bottleneck,
without predicting the speed of communication or whole nested work periods.

## Full regression and remaining work

The new experiment completed two periods using one resident GPU state:

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_independent_two_periods --reference figs/fixed_rule/small_holder_resident_two_periods_v1 --output figs/fixed_rule/small_holder_independent_two_periods_v1
```

Both decoded raw states, every stored coherent physical row and every gap row
match the frozen, independently audited two-period result. Their full stored
hashes are respectively a0b0fd7d47c1b9b79194c55033504e003ddd413aa9a5bb7912cd1f9882d67041
and 72a3df54eaa56d91e88bbe8a880e1c9f967808f4b1da40dd0786dc41c68e4a4b.
The existing baseline and backend are unchanged.

| End-to-end measurement | Result |
|---|---:|
| Physical ticks on 491520 sites | 8589934592 |
| Accepted independent batches / rejected atomic attempts | 158 / 32 |
| Physical ticks covered independently | 5234491384 |
| Accepted literal colony events | 5512680 |
| Synchronous literal ticks | 131266 |
| Committed local logical evaluations | 87819750 |
| GPU advance wall time | 133.103585 s |
| Frozen synchronous GPU advance | 321.372800 s |
| GPU advance speedup | 2.414456 |
| Total run with full-state audits | 148.720661 s |
| Maximum host RSS | 560020 KiB (546.89 MiB) |
| Sampled total GPU process memory | 424–426 MiB |

Logical-event counts exclude discarded speculative work; measured wall time
includes it. The sampled GPU readings are not a continuous peak-memory trace.
Explicit resident-plus-staging buffers total 6307920 bytes. The exact independent
kernel reports 220 registers, 48 stack bytes per thread and zero compiler local
bytes; private resource output is preserved as
small_holder_independent_kernel_resources_v1.log. The binary SHA256 is
3a898b1d96c81ea02abd9077650f819fe887f705cca58bd8c390c53bca614021.

A separate provenance/accounting audit passed, recorded in
small_holder_independent_evidence_audit_v1.json. It checks current and frozen
source/binary/artifact hashes, both complete checkpoint hashes, the unchanged
full physical descriptor and ROM, baseline scalar/native/descriptor audit
provenance, terminal progress, and physical/colony tick accounting. The full-state
comparisons are runtime assertions in the separately hashed experiment driver;
the JSON flags alone would not prove those comparisons.

All test/scaling/full-regression handles exited zero, and the final GPU query
was empty. The protected historical third-link job was not observed; nothing
here establishes that job's completion.

Still missing: actual nested initialization/evolution, performance of large
communication phases, integration of arbitrary full-raw faults and nonuniform
suffix Signals, finite-depth boundary verification, and cross-level noise
correction. Independent computation removes one obstacle; U squared remains
2^64, and no practical full nested macrostep follows from this benchmark alone.

Owned files: the new independent Python/CUDA backend, its test module,
`experiments/fixed_rule/small_holder_independent_{scaling,two_periods}.py`, this
report, STATUS.md and named results/private build products under figs/fixed_rule.
No shared change requested. Main agent retains substantial GPU scheduling and
can reply in MAIN_AGENT_NOTES.md, which is still absent.
