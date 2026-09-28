# Fixed-rule evaluator slice — 2026-09-25

**The current computing candidate uses one fixed 237-bit physical rule with a
compact computation window, colony-scale mail, and local program regeneration.**
Its complete 370-bit represented controller, including WAIT, is in its evaluated
NAND description. Two nonaliased macrosteps passed with an active NAND write.
The computing cycle now fits 5.104Q, but the first maintenance integration
estimate exceeds the available update budget. Address is still static in the
executed rule; full Gács/Gray maintenance and repair remain unfinished.

[Current window result](WINDOW.md) · [Maintenance integration gate](MAINTENANCE_INTEGRATION.md) ·
[Previous regeneration](REGENERATION.md) · [Previous timing failure](EVALUATOR_BUDGET.md) ·
[Architecture](ARCHITECTURE.md) · [Exact results and coordination](STATUS.md)

The earlier whole-ring evaluator below is preserved as historical evidence,
including its capacity failure. Its limitations do not describe the newer local
block encoder. No deeper physical run or noise-robustness claim has been added.

## Historical evaluator slice: implemented and measured

- A single total **135-bit, radius-one local rule**, with no depth argument,
  recursive host interpreter, or per-depth hardware registers. Its finite NAND
  description includes every raw controller and tape field, not just payload.
- Physical execution of that description on a represented three-cell ring for
  **26 fixed-time macrosteps**, checking all 135 bits of every represented cell.
  The represented controller visits all four computation phases; memory changes
  **0→1 at macrostep 9 and 1→0 at macrostep 21**. No state is re-encoded or supplied
  by the host between steps. Physical NAND feedback updates the input bank.
- A separate, fixed Gray maintenance description at Q=8192, U=1048576. It matches
  the existing scalar printed-rule specification on 91 healthy/damaged/boundary
  neighborhoods. Physical execution preserves the known singleton Flag2 error
  through clock rollover. This is source-discrepancy evidence, not repair success.

| Measurement | Self-description harness | Gray component fixture |
|---|---:|---:|
| Description NAND gates | 1,128 | 14,349 |
| Physical cells used | 8,391 | 29,108 |
| Physical ticks per evaluation | 50,983,716 | 574,198,758 |
| Evaluations in recorded run | 26 | 1 |
| Total local ticks | 1,325,576,616 | 574,198,758 |
| Measured execution time | 17.54 s | 7.55 s |

These CPU timings use a single-head sparse implementation: **every tick still
executes local transitions**, but headless fixed-point cells need no reevaluation.
They are not dense cell-update throughput, GPU measurements, or noise experiments.
The tests and experiment ran concurrently, so timings are not isolated benchmarks.
The self harness has 4,194 instructions, 4,196 memory records, 1,132,785 logical
physical-state bits, and a 436,332-byte uint32 storage array.

## Validation and artifacts

```bash
python -m unittest discover -s tests/fixed_rule -v
python -m experiments.fixed_rule.vertical_slice --output figs/fixed_rule/NEW_NAME
```

The experiment refuses to overwrite existing evidence.
**10 tests passed in 24.723 s** in the final recorded run:
[test log](../../figs/fixed_rule/tests_v2.log).
Coverage includes raw field roundtrips, scalar/C/NAND-description agreement on
133 arbitrary or branch-targeted local inputs, exterior-perturbation locality,
dense/sparse/scalar tick parity, invalid sparse-state rejection, fixed rule
identity across ring sizes, active self-description execution, fixed-duration
feedback, explicit recursive-encoding rejection, and Gray maintenance parity.
These tests do not exhaust the physical alphabet or certify an absent hierarchy.

The [experiment manifest](../../figs/fixed_rule/vertical_slice_v2.json) records
source hashes, geometry, actual tick counts, timing, and limitations. The
[raw artifact](../../figs/fixed_rule/vertical_slice_v2.npz) retains all 27 decoded
frames and final physical tapes. A separate [audit](../../figs/fixed_rule/audit_v2.json)
checks **10,530 post-initial raw bits**, every transition with both scalar and
dense C rules, final physical decoding, fixed macroperiod, and source/data hashes.
There are zero raw transition mismatches.

[Exact v2 sources](../../figs/fixed_rule/sources_v2.tar.gz) have SHA-256
`4f2125ee631ddaa88472907c048b1b858d9ff43a70aef16ecdd7f420aef6c77c`.
The [evaluator](../../figs/fixed_rule/evaluator_description_v1.json) and
[maintenance](../../figs/fixed_rule/maintenance_description_v1.json) descriptions
are exported as explicit gate lists; they are unchanged between v1 and v2.

Historical v1 evidence and sources remain intact. V1 started the physical head
at the first instruction, making the first observation interval 4,196 ticks
shorter. V2 starts just after LOOP and runs **exactly the same predetermined U**
each time, rather than stopping conditionally on a completion marker. The earlier
schema-test failure was a test bug: the maximal `kind` value equaled the default,
so the purported perturbation changed nothing. It did not indicate state loss.

## What is missing

The initializer still installs ordinary, unprotected program records. There is
no Gray ProgramBit overwrite/projection, combined maintenance/evaluator rule,
colony-local retrieval, redundant computation, simulated-layer repair, finite-depth
hierarchy initializer/termination, or noise-robustness measurement.

In particular, the whole-ring harness can represent at most **46 cells** with its
fixed 16-bit labels. Even its one-cell encoding has 2,799 physical cells, so that
encoding cannot be recursively reapplied. The test rejects this operation without
widening state or selecting another rule. Consequently **zero hierarchy levels**
are reported, although complete raw evaluator dynamics are physically computed.
Depth-identity tests remain required once a local block encoder exists.

The maintenance circuit is also too large and slow for the existing Gray colony
budget. A larger fixed U or a substantially better evaluator needs its own
source justification and complete resource accounting. Gács's interpreter bound
is not evidence that this measured serial overhead is necessary.

## Next concrete construction steps

1. Confine finite-state evaluators to locally marked colonies and implement local
   neighbor retrieval. Keep one physical schema and one rule at every depth.
2. Combine maintenance, transport, evaluator, commit, and program-projection
   machinery in one raw-state description. Resolve projection behavior when
   Address repairs, and retain separate distinguishing tests for D8/D10.
3. Establish a recursively admissible block encoding and fixed work period;
   compare all controller fields over successive macrosteps at depths 1/2/3.
   Freeze and compare rule/alphabet/description identities across those runs.
4. Add spatial and temporal correction and simulated-layer repair before measuring
   matched-depth noise performance. The current tape cannot establish robustness.

No existing shared module, experiment, dataset, or CUDA artifact was modified.
At the read-only run check, the shared initialized-third-link checkpoint remained
at 3,120 periods with status `running` and no top checks; no matching process was
visible. This was left to the main agent to investigate, not reported as completed.
