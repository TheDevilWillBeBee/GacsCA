# One-link block self-simulation of the computing substrate

**The missing retrieval/feedback mechanism now runs physically.** One fixed
177-bit radius-one computation rule simulates its entire own raw transition in
locally communicating colonies. Eight successive macrosteps pass, including two
represented NAND writes. This is an unprotected computation substrate, **not yet
the requested Gács/Gray maintenance-and-repair rule**. Program projection, source
maintenance, correction, and deeper physical runs remain unfinished.

## Fixed rule and representation

[communicating.py](../../gacsca/fixed_rule/communicating.py) defines the total rule
F. Its state includes the complete NAND/SEND controller, reflecting boundary
markers, and two packet tracks. Each packet carries a 16-bit target, data bit,
one-boundary-crossing bit and validity bit. A packet moves one site per tick;
after crossing a boundary it deposits at its target memory record. It is dropped
on a second crossing. Send/receive/write collisions have an explicit priority in
the scalar rule and its circuit; no behavior is left to host scheduling.

The [complete description](../../../../../figs/fixed_rule/communicating_description_v1.json)
has **3,029 NAND gates**, 531 input bits and 177 output wires. It includes packet
transport and SEND interpretation as well as the original evaluator. There is
no recursion/depth opcode or callback to a host transition.

The fixed colony program in [block.py](../../gacsca/fixed_rule/block.py) sends all
177 center-state bits to both neighbors, performs two guard NANDs, evaluates this
same description, stages every output, and commits it to the center Info bank.
The [explicit program](../../../../../figs/fixed_rule/block_program_v1.json) has 3,739
instructions and SHA-256
`a987a2d644ddbba0f1bedf5dbfa46f6c1fbdab44dc742c4381f4b079ebeb5392`.
Neither program nor geometry depends on ring size or requested depth.

Each colony has Q=7,480 physical cells. Its memory addresses are:

| Region | Addresses |
|---|---|
| Constant zero and one | 0, 1 |
| Retrieved left raw state | 2–178 |
| Center Info (decoder reads this bank) | 179–355 |
| Retrieved right raw state | 356–532 |
| Description intermediates | 533–3561 |
| Staged inverted outputs | 3562–3738 |
| Guard scratch | 3739 |

Instruction records occupy physical sites 3740–7478; LOOP occupies site 7479.
Memory and instruction labels are separate by record kind, so overlapping numeric
labels are intentional. Every colony repeats this same layout.

The encoder E is strictly block-local: it writes only the represented center
cell into Info; both neighbor banks start at zero. It never reads a neighboring
represented state. The decoder D reads the same Info bank at every macroperiod
boundary. All 177 bits, including raw controller and packet fields, are present.

## Macroperiod and admissibility argument

The physical head traverses a reflected path with 2Q phases. Its route through
the fixed linear program is independent of data bits. The assembled schedule
therefore gives one fixed **U=71,269,440 ticks = 9,528Q**.

Both packet directions travel Q−177 = 7,303 hops. Consecutive sends are separated
by at least 14,960 ticks. The final packet arrives at tick 5,303,499; the first
description-input read occurs at tick 5,370,780, leaving **67,281 ticks** of margin.
The two guard instructions and their travel are real local computation. Packet
deposits target the left/right banks, never center Info. Center Info remains
unchanged until output commit. Thus retrieval does not mix work periods.

Let A be configurations tiled by these colonies with their fixed program and
boundary records, intact constant wires, no packets, one rightward head at each
first cell, phase FETCH and pc=0. Headless controller fields are zero. Memory
scratch, retrieved banks, and the head's operand/value registers may be arbitrary.
`check_boundary` checks precisely these conditions; it does not repair them.

For a∈A, the first instruction overwrites all operand registers it needs. Local
sends retrieve neighboring Info from the same old configuration. The described
NAND circuit computes F on those three complete raw states. Staging all outputs
before changing any center input prevents old/new-state aliasing. The final LOOP
and return traversal restore the head phase, and every packet has already been
delivered. Consequently the construction argument is

    F^U(A) ⊆ A,       D(F^U(a)) = F(D(a)),       D(E(x)) = x.

This explains successive simulation without reinitializing scratch or supplying
host transitions. The tests exercise the relation; they are not exhaustive
verification over the entire 2^177-state alphabet or a mechanized proof. The
argument also explains how iterated E could produce further simulation links;
that fact must not be reported as physically executed depth-two/three evidence.

This is the Retrieve/Eval/Update architecture of Gács §9.3, including evaluation
of its own controller. The rest of his self-correcting construction is absent.
The immutable-in-clean-evolution program records are still ordinary physical
state exposed to noise, not Gray's eliminated ProgramBit mechanism.

## Physical tests and evidence

```bash
python -m unittest discover -s tests/fixed_rule -p test_communicating.py -v
python -m unittest discover -s tests/fixed_rule -p test_block_initial.py -v
python -m experiments.fixed_rule.block_selfsim --output figs/fixed_rule/NEW_NAME
```

**8 dynamic/local-rule tests pass in 79.539 s**
([log](../../../../../figs/fixed_rule/communicating_tests_v1.log));
**3 initialization tests pass in 0.181 s**
([log](../../../../../figs/fixed_rule/block_initial_tests_v1.log)). These are separate from
historical suites, not a claim of a new combined full-suite execution.

Tests include scalar/native/NAND-description comparisons on 172 random or
branch-targeted neighborhoods; arbitrary raw-state sparse/dense parity; literal
packet motion; locality exterior perturbations; block-local initialization;
eight successive complete-controller macrosteps with memory 1→0→1; and two steps
of five arbitrary raw target cells. The target ring is non-aliased for radius one.
No reference outputs are written into the physical state.

The [recorded run](../../../../../figs/fixed_rule/block_selfsim_v1.json) uses 22,440 physical
cells and executes **570,155,520 ticks in 56.021919917315245 s**. Every macrostep
uses the same U and passes the admissibility check. Each performs 657,027,864
local cell evaluations. Sparse execution computes the radius-one neighborhoods
of heads/packets synchronously from old data; canonical inactive cells are fixed
points. Stale raw inactive fields are explicitly included in the initial active
set, so the native routine also handles arbitrary raw configurations.

A [separate artifact audit](../../../../../figs/fixed_rule/block_audit_v1.json) verifies
all 24 archived/live source hashes, **4,248 post-initial raw bits**, every decoded
transition against both scalar and dense C rules, and the final physical decoder.
It also checks a physical first-SEND snapshot: leftward packets at sites
179/7659/15139 contain distinct source bits 0/0/1. Represented memory writes occur
at macrosteps 2 and 8. There are zero transition mismatches.

[Raw traces/tapes](../../../../../figs/fixed_rule/block_selfsim_v1.npz) ·
[Exact sources](../../../../../figs/fixed_rule/block_selfsim_v1.tar.gz)

## Depth and resource limits

[block_initial.py](../../gacsca/fixed_rule/block_initial.py) provides exact lazy
access to E^d of an ordinary top configuration. Depths 1/2/3 round-trip by reading
Info, with the same physical schema, rule fingerprint and program. The sampler
is initialization only and never evolves a simulated state. Quiescent top cells
with bit 0 or 1 use the same F; no local-only top kernel is selected.

For **one top cell**, literal dense requirements are:

| Depth | Physical cells | uint32 storage bytes | Physical ticks / top transition |
|---|---:|---:|---:|
| 1 | 7,480 | 718,080 | 71,269,440 |
| 2 | 55,950,400 | 5,371,238,400 | 5,079,333,077,913,600 |
| 3 | 418,508,992,000 | 40,176,863,232,000 | 362,001,224,036,378,640,384,000 |

No depth-two/three physical run or large GPU allocation was attempted. Lazy
initialization does not remove these evolution costs. A certified acceleration
would need to preserve actual local dynamics; replacing macrosteps with host F
calls would violate the task. The present budget also does not fit Gray's Q≥8192,
U=128Q schedule, even before redundancy and maintenance are added.

## Remaining target and next step

The next construction step is **hard-wiring/projection**, while continuing to
account for the complete evaluator transition. A promising clean-computation
route is an explicit address field plus a lift that restores static program and
boundary records from the one fixed description. Test the local commuting
relation for that lift/projection, including arbitrary controller/packet data.
Do not merely hide the initial program in a host lookup during simulated evolution.

Then incorporate source-grounded local maintenance, redundant computation,
trickle-down/simulated repair, and the associated state-size/time inequalities.
Address correction makes projection more delicate: a stale program associated
with the old Address need not match the repaired Address. This requires an
explicit simulated-program regeneration mechanism and distinguishing tests,
not an assumption that the clean static-address projection still applies.
D8 and D10 remain unresolved. The full goal is active and not complete.
