# Retimed physical CPU events and complete evaluation phase

2026-09-26. A private CPU event executor now runs the retimed candidate's entire
final evaluation phase, including active controller motion, reads/writes, META
scans and the final halt. The 15-colony fixture advances 790020767 physical ticks
in 32.010418 s, making 2775116 calls to the complete native physical rule. All
2310 raw Hold words agree with both the scalar and word-descriptor reference.
Seventy represented controller words change, so the fixture exercises simulated
controller dynamics rather than just stored initialization.

This is a complete computation phase from initialized history data. Gathering,
Signal/flag forcing, commit and a second whole physical period were not executed.
The [retimed noiseless proof](RETIMED_NOISELESS_MACROSTEP.md) remains separate
from this measured execution result. Practical full depth two and noise
correction across levels are still open.

## Execution mechanism and supported domain

retimed_holder_cpu_events.py/.cpp stores actual Data for each physical cell and
one complete head/controller per colony core. It reconstructs all 154 raw fields
of each physical neighbor from that coherent representation and the fixed ROM.
At every controller event it calls retimed_holder_native's **complete physical
word descriptor**, including all controller and raw mail outputs. It computes
old-state outputs before committing simultaneous Data/head changes.

The physical rule, alphabet, radius, description and ROM are unchanged. The
25-word quotient helper describes a restricted state representation; it is not
a new physical alphabet. The executor has no hierarchy-level input and does
not interpret the represented instruction stream. In particular, it never calls
an upper transition to evolve its stored state. The reference upper rule is used
only to compare the completed Hold output.

Its supported domain has canonical Address, uniform legal Age, fixed metadata,
coherent procedure copies, zero physical flags/Wf/Signals/mail, zero inactive
controllers, one or zero heads confined to each core, and zero non-MEM Data.
Calls must stay in a single regular clock interval, excluding reset, vote,
capture and commit transitions. Signals remain zero because capture is excluded;
zero Signals and flags keep Wf zero. A send-emitting event is rejected.

Between events, the executor changes only head position and elapsed clock.
Distance comes from the verbatim function in the frozen resident CUDA backend,
rechecked against this new ROM. Leftward travel stops at the first marker;
rightward travel stops at the relevant operand/metadata/fetch point or endpoint.
WAIT is absent from the fixed ROM and is explicitly checked absent. All eight
controller phases and both directions are covered by the distance audit.

The travel justification uses the retimed instruction-flight lemmas, regular
clock predicates and the actual fixed ROM. Over each skipped segment there is
no operand match, reflection or other controller event. Data and the complete
controller persist while head position translates. At an event, the structural
support lemma confines changes to the head and adjacent logical primaries;
complete F calls produce their actual new Data/controllers. Unaffected primaries
retain their values. Mail is checked zero rather than discarded.

Columns execute independently only in this restricted domain. Near a first
record, raw-neighborhood reconstruction can read the previous colony's last
nine logical positions; those positions have no head or changing Data here.
The 5047-cell inter-core gap prevents an adjacent colony's evolving head from
entering that neighborhood. The executor does not accept packet interaction as
an independent-column update.

Updates use staged copies. Unsupported emission, a failed domain guard or an
exhausted event budget leaves the original stored world and time unchanged.
The CPU adapter permits at most 64 colonies to bound host memory; that capacity
limit does not change the physical rule. This adapter does not yet support
arbitrary raw-state restoration or noise injection.

## Distance and literal checks

The new distance audit passes 5169366 breakpoint cases: eight phases, two
directions, two zero/nonzero value classes, and 32772 target classes. Unused
registers have distinct values. The oracle finds events from actual ROM records.
The function and oracle are affine in position between checked breakpoints;
out-of-range targets belong to explicitly checked equivalence classes. Both an
overshoot mutation and a wrong-target-register mutation fail. Distance alone
is not a complete backend proof.

Six tests pass in 2.174 s. Twenty-two controller cases cover operand reads and
writes, FETCH, both endpoint reflections, WAIT_META and all seven META selectors.
For three physical ticks each, 66 reconstructed raw outputs agree with literal
native causal cones on every field. Additional tests check clock-domain guards,
exact identity with the audited distance function, invalid state rejection, and
atomic SEND/budget rejection. These comparisons check reconstruction and event
scheduling; universal scalar/native equivalence is not inferred from them.

## Executed fixtures and independent audit

The fixture initializes Info and three history copies for a typed upper ring,
with differing Data and an active READ_B controller. Voted words are supplied as
explicit initial fixture data. The first controller is bootstrapped using an
actual native reset/vote output; the complete prior gather/reset trajectory is
not claimed. The physical run starts at Age 1232000001.

Execution stops one tick before the predicted halt to verify every head is still
present, then advances one more physical tick. At Age 2022020768 all heads and
all stale controller words are zero. All raw Hold words equal iota(G(upper)).
The 15-colony fixture has distinct source cells throughout the radius-seven
represented neighborhood. Independent scalar and direct descriptor evaluations
reproduce the saved physical-output hashes, without rerunning the event backend.

| Measure | One-colony pilot | 15 colonies |
|---|---:|---:|
| Physical ticks per colony | 790020767 | 790020767 |
| Total colony event ticks | 71151 | 1067538 |
| Complete raw F evaluations | 184948 | 2775116 |
| Execution seconds | 2.461932 | 32.010418 |
| Total run seconds | 3.018213 | 32.665876 |
| Peak RSS, KiB | 63892 | 69428 |
| Verified raw Hold words | 154 | 2310 |
| Changed represented controller words | 2 | 70 |

Actual event counts vary with META query positions; the padded physical phase
duration remains equal. The independent output audit took 0.746331 s /63316 KiB.
The distance audit took 2.035155 s /55860 KiB. No run needed large CPU allocations
or a GPU. All commands had a 512 MiB virtual-memory ceiling and one OpenBLAS
thread. The main agent's separate GPU reservation remains pending and unused.

## Files and reproduction

Owned additions are retimed_holder_cpu_events.py/.cpp and
retimed_holder_quotient.py; certify_retimed_holder_backend_distance.py,
run_retimed_holder_cpu_evaluation.py and audit_retimed_holder_cpu_evaluation.py;
test_retimed_holder_cpu_events.py; this report and the corresponding evidence.
All build products live under figs/fixed_rule/build/retimed_*.

From the repository root, use `ulimit -v 524288` and
`OPENBLAS_NUM_THREADS=1`. Successful output names refuse overwrite.

```
python -m experiments.fixed_rule.certify_retimed_holder_backend_distance --output figs/fixed_rule/retimed_holder_backend_distance_v1.json
python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_cpu_events.py -v
python -m experiments.fixed_rule.run_retimed_holder_cpu_evaluation --colonies 1 --output figs/fixed_rule/retimed_holder_cpu_evaluation_pilot_v1.json
python -m experiments.fixed_rule.run_retimed_holder_cpu_evaluation --colonies 15 --output figs/fixed_rule/retimed_holder_cpu_evaluation_v1.json
python -m experiments.fixed_rule.audit_retimed_holder_cpu_evaluation --execution figs/fixed_rule/retimed_holder_cpu_evaluation_pilot_v1.json --execution figs/fixed_rule/retimed_holder_cpu_evaluation_v1.json --output figs/fixed_rule/retimed_holder_cpu_evaluation_audit_v1.json
```

Matching logs are retained. The [evidence index](../../../../../figs/fixed_rule/retimed_holder_cpu_events_evidence_v1.json)
records all manifests and the test log with hashes. Recorded source/input hashes
were checked after completion. No shared source, reference CUDA file, historical
GPU job or dataset was changed. No new failed attempt occurred.

## Next work

Extend physical event execution to actual emitted packets and their local
transport, then to reset/vote/capture/commit boundaries. Validate the additional
state reconstruction and simultaneous-event priorities against literal F, with
atomic rejection where the domain is insufficient. Then run successive complete
physical periods with decoded controller comparisons. Initialized history banks
must be replaced by executed gathers for that milestone.

This CPU measurement supplies a correctness and cost reference for a retimed
GPU backend; it does not solve complete depth-two feasibility. U^2 remains
2^62 literal ticks. Further evaluator/layout optimization or proved acceleration,
plus cross-level repair and stochastic-noise experiments, remains necessary.
