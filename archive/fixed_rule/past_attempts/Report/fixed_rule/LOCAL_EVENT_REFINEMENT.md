# Physical local event identities and exact META timing

2026-09-26. The completed-instruction abstraction now has direct full-descriptor
checks for 67 local event cases with arbitrary operands and stale controller
words. Separately, actual GPU execution checks the exact META write boundary for
all 32768 valid query Addresses and all seven selectors at seven real instruction
locations. This advances physical refinement of [ROM_DATAFLOW.md](ROM_DATAFLOW.md),
but does not yet prove every program location, scan interval or complete period.

## Full raw physical event identities

`certify_small_holder_local_events.py` constructs coherent physical neighborhoods
and independently specifies the intended next physical state. The old controller
words not fixed by the event are symbolic, as is surrounding MEM Data. It then
evaluates the unchanged complete 13442-operation descriptor and compares every
one of its 154 raw outputs at nine holders around the event.

The proof cases cover all five arithmetic READ_B operations, READ_A, WRITE, LOAD,
both SEND directions with every hop count, FETCH of every instruction kind used
in the fixed ROM, HALT and both IF_THIRD branches, all seven metadata selectors,
left-end metadata/reflection events, and gap/tail fallback queries. A quiet case
checks preservation of arbitrary coherent Data without a head. Controller fields
that an event should retain remain symbolic; they are not silently zeroed.

The word proof uses structural expression identities with unsigned 64-bit
semantics. In addition to the earlier constant/commutative/zero reductions, it
uses double complement, NAND with zero/all-ones, and NAND of identical words.
These identities collapse coherent five-holder majority without restricting the
operand values. The separate expected state includes every replica/controller,
Data, packet, metadata, geometry, flag and Wf output.

There are 67 cases, 603 complete raw output records, or 92862 checked output
words. Symbolic check time is 8.344888 s, host peak 57400 KiB. The scope is explicit:
canonical coherent geometry, zero flags/Signal, no incoming mail, the concrete ROM
positions and event Ages listed in the artifact, and arbitrary specified operand/
stale-controller words. These cases are not a symbolic quantification over every
ROM position or clock phase. Quiet positions farther away and combination with
actual incoming packets still need their appropriate locality/composition argument.

Four tests passed in 8.667 s. Mutations that lose arithmetic output, fail to
advance PC, drop a stale ALU field or omit an emitted packet are rejected; an
incomplete raw output schema is rejected. Added bitwise normalizations are tested
on boundary word values. This is more than matching a simplified controller:
the comparisons use the full physical descriptor with all five procedure copies.

## Actual META completion time

For a real META instruction at physical Address m, writing to MEM Address d,
let L be the fixed computation-core length. The schedule recipe predicts

    D = 4 L + d - m + 1

physical updates from old FETCH at the META instruction to completed WRITE and
head arrival at d+1. A clean query follows the same right/left sweeps whether it
hits a ROM record, hits an endpoint, or uses the gap/tail fallback. A successful
metadata read switches to WAIT_META even if the returned metadata word is zero;
that distinction prevents zero results from being mistaken for a missed query.

The controller path suggests the following timing derivation, relative to old
FETCH: after the first pair of sweeps it is ready to search at Address zero at
2L-m; after the search/return pair it is in WRITE at zero at 4L-m; completion at d
then takes d+1 more steps. This explains the recipe and the tested boundary
cases. A fully parameterized proof against all raw physical transitions remains
necessary before treating it as a universal physical scan certificate.

`small_holder_meta_event_timing.py` initializes a real head at each of seven
output-regeneration META instructions, with deliberately stale ra/rb/value/alu
and a poisoned destination. Only ordinary initial fields supply the query in rd.
The host supplies no query result during evolution. The unchanged supported-input
physical event backend advances to D-1 and D. The driver requires:

- At D-1: the full destination record has the correct WRITE head and fetched
  metadata value, but its Data is still the poison.
- At D: Data has changed to the correct value; the entire moved head/controller
  record, including retained ALU, has the correct FETCH phase and next PC.
- The old instruction site has no residual head/controller state.

All selectors were queried at every Address in [0,Q). Thus the experiment covers
229376 actual META completions, including first/last core addresses, all gap and
tail addresses, and all zero-valued results. For the chosen seven instruction/
destination pairs, D is exactly 101557 ticks. Checks occur immediately before
and after that time, not merely at a later halted checkpoint. The existing
exhaustive regeneration experiment checked final values of whole subroutines;
this experiment adds exact physical completion-time and controller observations.

| Measurement | Result |
|---|---:|
| Pilot completions | 91 |
| Exhaustive completions | 229376 |
| Queries per selector | 32768 |
| Batch colonies | At most 128 |
| Full local evaluations in exhaustive run | 3856440 |
| GPU advance wall time | 7.749542 s |
| Whole run, including initialization/readback | 102.630788 s |
| Host peak | 172408 KiB |
| Recorded GPU process memory | 442 MiB |

The pilot passed first in 0.916432 s (168108 KiB host), covering 13 endpoint/
fallback Addresses per selector. Both artifacts are preserved. No hierarchy-sized
allocation, shared CUDA rebuild or depth-selected physical kernel was used.

## Commands and independent audit

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.certify_small_holder_local_events --output figs/fixed_rule/small_holder_local_events_v1.json
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_local_events.py -v
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_meta_event_timing --output figs/fixed_rule/small_holder_meta_event_timing_pilot_v1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_meta_event_timing --all-addresses --output figs/fixed_rule/small_holder_meta_event_timing_all_v1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_local_events --certificate figs/fixed_rule/small_holder_local_events_v1.json --timing figs/fixed_rule/small_holder_meta_event_timing_all_v1 --output figs/fixed_rule/small_holder_local_events_audit_v1.json
# Independent audit passed, 7.299437 s, 62672 KiB host RSS.
```

The audit instantiates all event expressions with all-zero, width-limited
all-ones and seeded random words. It compares 1809 complete raw outputs against
independent scalar and native physical transitions, covering overflow and retained
fields as well as arithmetic results. It independently recomputes every saved
META value and duration from the actual ROM. Exact GPU write-boundary observations
are runtime assertions in the hashed experiment driver; this audit does not replay
all micro-trajectories. The symbolic proof has arbitrary-value scope in its
stated event cases; the concrete audit is implementation evidence.

## Remaining refinement and full-goal obligations

The next proof must generalize the local cases over the actual program's positions
and relevant clock intervals, include right-end reflection and ordinary flights,
and establish exact total instruction duration. It must also compose events with
incoming packet transport under the actual noninterference/collision conditions.
Only then can the ROM data-flow certificate, flag/Signal machinery and complete
reset relation be joined into an all-input physical work-period theorem.

No new interpreter or instruction-level simulator is installed as a physical
backend. These symbolic tools are diagnostics. The self-description and ROM remain
fixed independently of encoded depth, and all GPU evolution here uses the existing
physical local transition. Gray's specialized hard-wiring and Gacs's modified
self-simulation remain the source motivation in the existing closure report;
neither supplies the missing refinement theorem automatically. Full nested upper
periods, fault-aware trajectory composition, terminal reliability and general
cross-level noise suppression are still unfinished.

## Provenance and ownership

`figs/fixed_rule/small_holder_local_events_v1.json` SHA256: `4f9b63d26da6765ccf911e7a0792fe5ab1f75f306db8a39018462f0fab92b166`.

`figs/fixed_rule/small_holder_meta_event_timing_all_v1.json` SHA256: `b4636fa08ff557554d423f0b033867b19726621bde076e3e6104d5d7dad37a0f`.

`figs/fixed_rule/small_holder_meta_event_timing_all_v1.npz` SHA256: `792950f51f2bdff1f7b1b9c861de360dd7a253fd056a3fd17d44770c8922a8f9`.

`figs/fixed_rule/small_holder_local_events_audit_v1.json` SHA256: `b074d74e3c2531ce9c203b8f953bdb55f8d3e802eb582e13f607591b0fef2a5d`.

Physical descriptor remains
`af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`.
GPU binary remains `4419e5fdd8caeb81c884db3ede3d709d677693aee1943482040e171bc54f1c7e`.
Owned additions: local-event certificate/test/audit, META timing experiment,
this report and namespaced evidence. No frozen/shared source or existing CUDA
artifact changed. All own handles are terminal. MAIN_AGENT_NOTES.md remains
absent and the separate 8 GiB reservation request is pending. The historical
third-link job was not observed; absence does not prove successful completion.
The full goal remains active.
