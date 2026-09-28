# Projected physical faults and targeted simulated repair

2026-09-26. The nonperiodic resident GPU representation now supports individual
faults in every mutable physical field. Independent causal-cone tests pass. A
full-period experiment starts with six physical bit flips in incoherent lower
holders: lower majority spreads the wrong bits, then the encoded upper rule
repairs the two damaged controller replicas. Nine flips damaging three upper
replicas produce the expected failure. This is one simulation link/two scales,
not a complete nested upper period or a stochastic noise threshold.

## Physical rule and source scope

The physical rule here is the hard-wired projection
`G(x[-7:7]) = project(F(lift(x[-7]), ..., lift(x[7])))`.
`small_holder_projected` supplies all 49 program metadata words from each
holder's own Address and the fixed ROM. The 105 mutable fields (2704 bits)
include every procedure backup, head, controller, mail field, Wf, raw Address,
Age, flags and Signal. Fault injection accepts complete projected cells. Read
and diagnostic caches expose the full 154-word lifted record (4090 bits).

Gray pp.31–32 motivate eliminating the ProgramBit and specializing the machine;
Gács §§9.2–9.3 allow an appropriate modified simulated rule. Neither establishes
this implementation's correction theorem. Candidate-B Flag2 and old-Signal D10
remain explicit source modifications. The ROM still evaluates the unchanged
full raw F description; these tests add no proof of projection closure for
arbitrary upper geometry faults, robust boundary termination, or full nesting.
Do not conflate projected physical faults with the older raw-F fixtures, whose
metadata fields can themselves be corrupted.

The fixed descriptor remains
`af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`.
Q=32768, U=4294967296, radius seven, ROM and alphabet are unchanged. Q and U
remain optimization targets; U/Q=128 is not a constraint. The practical target
is actual two-level GPU execution, then measured repair across levels.

## Exact exception representation

New `gacsca/fixed_rule/small_holder_resident_faults.{py,cu}` borrows an existing
resident reference B. The actual state X is B plus complete physical records at
exception positions E. All evolving records remain on GPU. Host operations
manage integer positions, equality flags, external fault injection and diagnostic
decoding; they never supply a simulated transition.

For each tick, the GPU computes both G(X) and G(B) on the radius-seven expansion
of E, reading each complete old local neighborhood. It retains precisely those
outputs whose full records differ. Outside that expansion the input neighborhoods
are identical, so the outputs agree. The reference advances once through its
existing certified path. Derived metadata is regenerated using each output's
computed Address. This matters when the fault changes physical geometry.

The frontier limit is 8192 sites. Overflow rejects before the tick mutates
state. The fixed GPU buffers occupy 18,579,456 bytes, independently of hierarchy
depth and reference colony count. Full evaluation uses 256 external workspaces;
it does not allocate a large per-thread local array. The reference must remain
inside its existing supported domain; an actual faulty state can deviate through
its exception rows, but this is not an unrestricted dense noisy-world engine.

## State-preserving Data rebase

After a fault tick, all five actual holders may agree on a wrong MEM Data word.
Keeping those identical values as exceptions would prevent fast execution forever.
`absorb_data()` may put that exact value into the reference Data bank, then compare
and retain every remaining full exception. This changes the representation at
the same time, not the actual state or physical rule.

For logical position a, its five copies are physical fields `s{2-d}_data` at
`a+d`, d=-2,...,2. A bank value changes only if all five actual copies agree.
If that value differs from the old bank, each of those five holders was already
an exception. Thus every physical field affected by the rebase is explicitly
represented with the new value; every other field remains unchanged. Distinct
logical targets modify distinct Data fields, even when their holders overlap.
Wrong Data stays wrong. An empty exception set means coherence with the current
reference, not recovery to a healthy trajectory. Non-MEM Data is not absorbed.

The rebase keeps unrelated controller/geometry exceptions. While any exception
remains, physical ticks use the full local descriptor. Once none remain, existing
guarded communication/controller acceleration resumes on the actual coherent
state. If a reference advances outside its owning fault wrapper, the wrapper
rejects further use.

## Tests and measured resources

Executed with `OPENBLAS_NUM_THREADS=1`, using Python's
`unittest.defaultTestLoader.discover('tests/fixed_rule', pattern=...)` and
`unittest.TextTestRunner(verbosity=2).run(suite)`:

| Pattern | Result | Test time | Whole runner | Host max RSS |
|---|---|---:|---:|---:|
| `test_small_holder_resident_faults.py` | 6 passed | 1.541 s | 1.682987 s | 174560 KiB |
| `test_small_holder_rule.py` | 4 passed | 2.163 s | 2.264088 s | 65824 KiB |

Logs: `figs/fixed_rule/small_holder_resident_faults_tests_v1.log` and
`small_holder_faults_identity_tests_v1.log`. The first smoke test compiled and
matched complete initial reads in 16.477174 s (163600 KiB host RSS). A preceding
attempt to use `/usr/bin/time` exited 127 because that utility is absent; timing
then used Python `time` and `resource`.

The new tests compare three literal ticks in independent shrinking native-rule
cones after randomizing all 105 mutable fields, including at a ring boundary and
an active WRITE. They forbid host evaluator/rule calls during GPU evolution;
check two-holder procedure repair and return to acceleration; retain a wrong
three-holder Data majority; preserve unrelated raw fields through rebase; reject
incomplete/nonprojected injections and external clock changes; and verify atomic
frontier overflow. The existing four tests verify raw scalar/native/descriptor
agreement, complete self-description lowering, all raw controller words at
three encoded depths, fixed identity/width, and neighborhood dependence.

## Full-period incoherent-fault experiment

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_incoherent_repair --reference figs/fixed_rule/small_holder_resident_two_periods_v1 --output figs/fixed_rule/small_holder_incoherent_repair_v1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_incoherent_repair --input figs/fixed_rule/small_holder_incoherent_repair_v1 --output figs/fixed_rule/small_holder_incoherent_repair_audit_v1.json
```

Both exited zero. The initial fixture has an actual upper WRITE of
`0x123456789ABCDEF0`, including its complete controller state. For each damaged
upper value replica, exactly three lower physical Data holders receive a one-bit
flip. These are individually injected physical records, not a coherent logical
initializer override. The first full GPU tick creates five wrong copies per
logical word. Exact rebase preserves that state; the physical lower controller
then executes its remaining work period.

| Case | Initial physical flips | Exceptions after tick 1 | Decoded result |
|---|---:|---:|---|
| Two upper value replicas | 6 | 10 | All 154 words equal healthy; WRITE ends EF0 |
| Three upper value replicas | 9 | 15 | Expected majority failure; WRITE ends EF1 |

The incorrect words persist through all three gathers and temporal vote. At
capture, Hold matches the complete intended upper transition. At U the decoded
state matches that transition; in the two-copy case, after the next local reset
at U+1, every physical core/tail/gap row equals the independently restored healthy
reference. No healthy state is installed into the damaged world.

GPU advance: 35.900505 s; total: 51.693960 s; host peak: 569976 KiB; sampled GPU
process: 444 MiB. Audit: 1.304527 s, 60484 KiB host RSS. The audit reconstructs
initial physical fault placement independently, compares the first physical tick
against scalar, native and descriptor evaluations on complete saved causal cones,
and checks every decoded upper field. Full-period history persistence and whole
physical rejoin are runtime assertions in the hashed driver; the small archive
does not contain the entire physical trajectory.

Artifact SHA256:
`d3606b6664ae582e82242b20b6937c342a81bbf18ca75db8ad5a96646338ec08`.
Fault backend binary SHA256:
`605dee3127f755e8680054d0a1317cd945e41cfd080ec93eb38bacd4feddf954`.
The experiment manifest records sources, baseline and accelerator hashes.

## Ownership and next steps

Only new fixed_rule backend, test, experiment, audit and report files were added;
STATUS.md was updated. Frozen sources, shared modules/reports and historical GPU
jobs were untouched. All test/experiment handles exited. The protected historical
third-link job was absent on inspection; that does not establish its completion.
MAIN_AGENT_NOTES.md remains absent; the previously requested 8 GiB whole-Q reset
pilot remains unlaunched pending scheduling coordination.

Next: exercise overlapping and temporally separated physical faults, quantify
how geometry/controller deviations expand or recover within the frontier limit,
and establish a broader supported reference domain. Separately resolve projected
closure under upper geometry repair and the full nested-period cost. Whole Q²
physical execution and a completed upper work period remain outstanding; U² is
2^64. Finite-depth robust termination and cross-level stochastic amplification
are still open. The final goal remains active.
