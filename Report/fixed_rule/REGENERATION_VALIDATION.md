# Previous regeneration validation — historical

Superseded for current status by [STATUS.md](STATUS.md). These results remain valid;
this document preserves their exact commands and limitations.

## Previous completed regeneration result

[REGENERATION.md](REGENERATION.md): one fixed **125-bit radius-one physical rule**
now locally regenerates all 69 represented instruction-record bits from staged
Address before committing the full output. Its complete **194-bit unprojected
controller**, including CLEAR/LOAD/META and packet dynamics, is described by
**4,345 NAND gates** and actually self-evaluated. No depth, runtime ROM, or host
simulated-transition callback is passed to the physical kernel.

Gray pp.31–32 motivates reading the colony's own program at simulated Address
before projecting ProgramBit away. Gács §§9.2–9.3 permits specialized self-simulation
and requires the interpreter in the description. This implementation generalizes
the projected record and places regeneration after evaluation/before commit;
that timing difference is explicit, not a resolution of D10.

Address remains static in the physical rule. A diagnostic stage fixture changes
Hold.Address and corrupts its record, then checks actual local reconstruction.
That fixture is not autonomous Address repair. **One computing-substrate link;
zero completed Gács/Gray hierarchy levels.**

## Commands and exact results

Four separate targeted runs, **17 tests total**, not a new aggregate full-suite run:

- `python -m unittest discover -s tests/fixed_rule -p test_regenerative.py -v`:
  **5 passed in 2.237 s**, `figs/fixed_rule/regenerative_tests_v1.log`.
- `python -m unittest discover -s tests/fixed_rule -p test_regenerated_initial.py -v`:
  **3 passed in 0.314 s**, `regenerated_initial_tests_v1.log`.
- `python -m unittest discover -s tests/fixed_rule -p test_regenerated.py -v`:
  **8 passed in 243.643 s**, `regenerated_tests_v1.log`.
- `python -m unittest discover -s tests/fixed_rule -p test_regenerated_admissibility.py -v`:
  **1 passed in 60.424 s**, `regenerated_admissibility_tests_v1.log`.
  Arbitrary physical scratch and carried head operands still produce the complete
  correct next represented state. This late-added test has a separate source hash
  in `regenerated_admissibility_source_v1.json`.

Artifact run:

`python -m experiments.fixed_rule.regenerated_selfsim --output figs/fixed_rule/regenerated_selfsim_v1`

- Four represented cells, **48,288 physical cells**.
- **8 × 207,565,968 = 1,660,527,744 literal ticks**, **595.8052477566525 s**.
- Every period: **2,527,807,592 local evaluations**, zero projected/full-lift
  raw-state mismatches, valid macro-boundary.
- Incoming packet writes cell 0 at step 1; NAND writes cell 1 at step 2 and cell 3
  at step 8. No host refills or replacement of upper transitions.
- The exact sparse CPU implementation evaluates every tick; it skips only
  canonical inactive fixed points. Timings are not isolated dense benchmarks.

Independent audit:

`python -m experiments.fixed_rule.audit_regenerated_v2 --input figs/fixed_rule/regenerated_selfsim_v1 --output figs/fixed_rule/regenerated_audit_v2.json`

**Passed:** 46 live/archived source hashes, 4,000 projected and 6,208 lifted
post-initial bits, scalar/native/NAND-description agreement, final physical decode,
macro-boundary invariants, ROM and binary identity. The original auditor incorrectly
expected both NAND writes in cell 1. Its failed check is preserved in
`audit_regenerated.py` and `regenerated_audit_failure_v1.json`; v2 checks all memory
locations. The physical experiment and archived sources were not changed. The
corrected auditor's own hash is recorded separately in its audit result.

Exact description/program and budget files:
`regenerative_description_v1.json`, `regenerated_program_v1.json`,
`regeneration_budget_v1.json` under `figs/fixed_rule/`.

- ROM SHA-256: `e2393c393706dcaf5c81f275398c4780a1c58e76dd81edc2fe946f2401f0e2fe`.
- Source archive SHA-256: `aaf923afeef9c32ad4f888bcfb70499876cd63e391f2ff8929a6ad99779a0500`.
- Raw artifact SHA-256: `3574d884279f0aab8ede3be492ed767e71256888ee773af3d7665c95241de614`.

## Architecture and limitations

[REGENERATED_RELATION.md](REGENERATED_RELATION.md) defines the reusable encoding
relation. Workspace need not return to a freshly initialized pattern; every
readable scratch value is overwritten before use. All raw represented controller
and packet fields are included. The strict decoder rejects stale projected
program fields. This is an inspectable argument plus finite experiments, not an
exhaustive or machine-checked proof over the physical alphabet.

Q=12,072; U=207,565,968=17,194Q; ROM 169,008 bytes. **U exceeds Gray's full 128Q
period by 134.328125 times.** Evaluation alone uses about 10,044Q; metadata adds
about 2,484Q. Do not reuse the baseline colony/work-period budget. See
[EVALUATOR_BUDGET.md](EVALUATOR_BUDGET.md) for exact stage costs and alternatives.

Depths 1/2/3 use the same alphabet, rule and ROM in lazy initial configurations.
No depth-two or depth-three dynamics were executed. One top cell at depth two
would need 145,733,184 physical cells, 10,492,789,248 dense uint32 bytes, and
43,083,631,071,777,024 ticks per top transition. These are resource estimates,
not evidence from an allocated/evolved tower.

Still missing: actual Address/Age/flag maintenance, clock/reset integration,
spatial/temporal redundancy, simulated-layer repair, faithful source schedule,
deeper physical execution, and noise robustness. Printed Flag2 persistence and
computed-SimBit timing remain unresolved source issues.

## Files owned / coordination

Only authorized `fixed_rule` namespaces were edited. Current new modules:

- `gacsca/fixed_rule/regenerative.py`, `regenerative_native.c/.py`,
  `regenerative_block.py`, `regenerated.py`, `regenerated_native.c/.py`,
  `regenerated_initial.py`.
- Four corresponding new test modules under `tests/fixed_rule/`.
- `experiments/fixed_rule/regenerated_selfsim.py`, `audit_regenerated.py`,
  `audit_regenerated_v2.py`.
- Research documents and exact evidence under owned report/figure namespaces.

Earlier candidates and failures are preserved. All 33 source hashes of the prior
projection artifact still match. Prior results remain in [PROJECTION.md](PROJECTION.md),
[BLOCK.md](BLOCK.md), [CONFINED.md](CONFINED.md), and historical [REPORT.md](REPORT.md).
Construction revisions are not kernels selected by requested hierarchy depth.

No shared module, main report, existing test, experiment dependency, historical
dataset or CUDA artifact changed. No GPU job, process control, commit, reset or
branch operation. No shared-file handoff is currently needed.

