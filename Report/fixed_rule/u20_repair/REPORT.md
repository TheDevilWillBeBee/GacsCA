# U20 fixed-rule audit and repair result

## Scope

The active physical rule remains `stream28_dual_pass20.local_step`: Q=8192,
U=2^20, radius seven, 421 raw words and 6,465 bits. All work here is in new
`u20_repair/` files. Exact commands, source hashes, state hashes, timings,
resource use and artifact paths are in [STATUS.md](STATUS.md) and the JSON
receipts in `figs/fixed_rule/u20_repair/`.

## Description equivalence

The active optimized WordCode with digest `16bf88a1…6257` is not the physical
rule. At old Age 2392 and site 2491, the literal rule emits a seven-hop
`s2_rp_remaining` packet; the old description emits one hop. The corrected
private builder uses a conditional selection of `abs(offset)`, producing
digest `232fa6b9…f88`. A private native C build agrees with literal Python
and corrected WordCode on 50,099 sampled raw outputs from random typed,
boundary, route-offset and short-trajectory neighborhoods. The builder's
Boolean/word AND sites were manually audited. This is strong differential
evidence, not a proof of equivalence for all 6,465-bit neighborhoods. No SAT
certificate was completed. The hop-count selector alone was exhausted over
both Boolean values and all fifteen route offsets. The corrected predecessor evaluator ROM was
rebuilt: 14,851 gate copies, max 38 routes/site, last event tick 39,517 of
65,536.

All shared ROM, placement, schedule, native and dense CUDA artifacts derived
from `16bf88a1…6257` are invalid for literal F and require regeneration.
Independent literal holder maintenance evidence is unaffected. The
machine-readable inventory lists 390 upper static dependencies; the final
corrected program physically sources 383 and optimizer-prunes seven.

## Physical self-description lookup

The existing 421-word rule does not retrieve upper static data. Its static
SOURCE sites are holder MEM cells with `a=b=0`; the old initializer injects
Address-projected values from the host. A new 433-word, 6,609-bit local
successor adds an Address broadcast and a one-lap request packet. The current
metadata is compiled for the predecessor's 390 static words. All 390
requests launch simultaneously from distinct lower sites and move right at
one site/tick. Each reads the requested local immutable ROM field at the
matching physical Address, returns to its source, and writes fivefold Data
copies at old Age 16,385. This is before the early evaluator capture at Age
393,217. Each Age-0 broadcast reads the current Info Address, but a retained
world across an Address-changing work boundary was not executed. The rule is
radius seven because it embeds the old physical F;
the lookup component alone reads at most radius three. Its complete local
WordCode has digest `e2b91fce…894898f`; literal, WordCode and native C match
on 96 random typed neighborhoods covering every lookup phase boundary. A
separate local test checks the vectorized bus executor against the independent
literal successor at each protocol boundary.

The lookup-only CA executed 16,386 consecutive transitions on a closed
one-colony ring with upper static Data initially zero. For represented
Addresses 173 and 4093, respectively, all 390 requested values and all
1,950 fivefold copy checks matched *post-run* diagnostic projection. The two
Addresses require 105 different values. These runs execute only the lookup
component plus its own Age update. They do not establish that the embedded
holder/evaluator F and lookup can run together throughout a work period. The
successor's own WordCode needs 393 static inputs and a different evaluator
layout; these have not been given matching physical source metadata. Thus the
390-word protocol is a working component, not closed self-description of the
433-word rule.

## One continuous period and successive macrosteps

The oracle-free 15-colony initializer fills lower immutable ROM by each
physical site's own Address, puts all 119 represented evolving words in
Info/Hold, and leaves upper-static SOURCE Data zero. Two consecutive
all-sites native C transitions were executed with the corrected 421-word F;
six sites per tick matched literal Python on all raw outputs. There is no
continuous U-period receipt and no successive decoded upper macrostep.

The 433-word successor cannot use the unchanged three-slot 8Q spatial
evaluator recipe. It needs 2,960 memory words, 393 static source sites and
18,333 fanout gate copies, but the remaining 4,834 gate sites contain only
14,502 slots: a deficit of **3,831**. A raw input with demand 422 also
exceeds the 38-route source limit. This is a counted obstruction to the
*current evaluator layout*, not to every Q8192/U20 redesign. A fixed
five-slot spatial evaluator, or a coherently rescaled Q=16384/U=2^21 rule,
could be investigated. Neither has been compiled or executed, so no
faithful hierarchical self-simulation claim follows from this work.

## Damaged-state repair and noise robustness

The 3,402 lower static bits per old cell are stored state. The local damage
test changes one `p3_kind` field and observes that the wrong value persists
after a physical transition. The spatial evaluator gate/route/mail state is
single-copy. There is no tested repair of static ROM and no noise-robustness
evidence for either the old rule or the lookup successor. The healthy lookup
protocol uses lower Age and Address; arbitrary inconsistent lower geometry
has a defined successor transition, but its retrieval guarantee was tested
only on canonical geometry.

## Gray source fidelity

The current holder uses candidate-B explicit Flag2 erasure. A distinguishing
test starts with an isolated center Flag2=1, all left Flag2=0 and computed
Flag1=0: this rule clears Flag2, while the printed persistence condition in
Gray p. 21 leaves it set. At `CAPTURE_AGE=80Q`, the implemented Signal path
takes the corrected local `Data & 1`. A test yields Signal bit 2 set while
computed physical Flag1/Flag2 remain zero. Gray p. 35 instead requests the
computed upper F1/F2 values at computed Addresses Q−3 and 3 before the end
of the third active stage. These are source-fidelity deviations, not noise
repair results.

Gray p. 34 divides U=128Q into three 32Q stages and two 16Q stages, each
half active and half rest. The implemented reset/active intervals are
`[0,16Q)`, `[16Q,32Q)`, `[32Q,79Q)`, `[84Q,88Q)`, and `[88Q,127Q)`.
They allocate extra continuous time to the third gather/evaluation and final
update, with no Gray-style equal rest halves. The encoded route and dual
evaluator schedule motivate these timings, but this is a construction
change; no source-faithful equivalence proof was attempted.

## Precise limits of the evidence

| Claim | Status |
|---|---|
| Corrected 421-word description equals literal F | Sampled all-word Python/WordCode/C parity; no formal all-state proof |
| Physical self-description lookup | 390-word lookup-only execution on a closed ring; successor local rule and description parity |
| One full continuous U period | Not executed |
| Successive upper macrosteps | Not executed |
| Damaged-state repair | Static-field damage demonstrably persists one step |
| Noise robustness | Not tested |

The fixed candidate's own-rule circuit and the 433-word successor's physical
lookup have each been exercised separately. Their composition still lacks a
placed same-rule evaluator ROM, matching successor lookup metadata, and a
full-period execution.

## Continuation: widened packet reader, 2026-09-29 18:32 UTC

The 433-word successor had another construction defect: its packet read only
fields 0..420, so it could not fetch its three new immutable lookup fields.
The repaired literal rule, WordCode and native C now read all 433 fields.
The resulting WordCode digest was `b13445f0…eccc` (18,410 operations),
superseding the earlier `e2b91fce…898f` receipt. A vectorized component
executor also broadcast 16 low bits of a full-width Info word where literal
F keeps 13; that executor mismatch was fixed and tested.

The lookup component completed 16,386 consecutive ticks on a one-colony
closed ring for upper Address 3218. All **393** own static dependencies and
their 1,965 fivefold stored copies matched post-run diagnostic projection,
including nonzero values of the new metadata fields. This establishes a
physical lookup component for the successor's actual static input set. Its
three added source sites are provisional and overlap predecessor gate sites;
the run did not execute the full successor F at every site.

The full successor F did run for two uninterrupted ticks on a 15-colony ring
with random upper states, zero upper-static SOURCE Data and all 393 lower
lookup metadata rows selected by physical Address. Sampled sites matched
literal F on every raw field. The lower evaluator ROM in that pilot still
describes the corrected 421-word predecessor, so the pilot does not establish
an upper macrostep. Across separate differential suites, 2,071 predecessor
cases and 2,048 final successor cases gave 1,758,675 matching all-field
Python/WordCode/native outputs. Additional traced coherent cases witnessed
all eight controller opcode paths, packed LIT, fourteen actual stream-offset
emissions and 32 stage boundary ages. There is still no formal all-state
equivalence certificate or CUDA parity for the successor.

That successor description raised the unchanged layout deficit to **3,927 gate
slots**: 18,429 required fanout copies versus 14,502 available slots.
Three raw inputs also exceed the 38-route source limit, with demands 434,
47 and 41. No own-rule evaluator ROM or schedule has been placed. Thus U20
construction remains incomplete; a full oracle-free U period and successive
decoded upper macrosteps remain unexecuted. The separate smaller-Q fixed
candidates in `design_optimization/` have executed one-level closure, but
they are different rules and do not close this U20 candidate.

## Balanced packet selector, 2026-09-29 18:41 UTC

The latest description replaces 433 one-by-one packet-field comparisons
with a fixed 9-bit binary mux. This preserves the literal successor rule
while reducing the optimized WordCode to 16,328 operations, digest
`8d6dc2b0…aaab0a`. All 512 typed selector values were exercised at a real
fetch event across literal Python, WordCode and native C, and 2,048 random
typed successor neighborhoods again matched on all 433 outputs. A fresh
two-tick whole-ring run produced the same full-state hashes as the preceding
backend.

The final **three-slot** capacity count is 16,363 required gate copies
against 14,319 available slots, leaving a **2,044-slot deficit**. Two raw
sources still exceed the 38-route limit. A fourth gate slot requires a new
fixed alphabet and circuit compilation because slot value 3 currently marks
an output sink. This has not been implemented or validated. There is still
no placed own-rule circuit or continuous full-U period.
