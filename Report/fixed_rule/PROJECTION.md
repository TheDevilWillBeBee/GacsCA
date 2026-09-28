# Fixed ROM projection of the complete computing rule

**Program records have been removed from the physical alphabet.** The current
candidate uses one fixed **125-bit, radius-one physical rule**, with opcode,
operand, index and boundary records supplied by a compiled Address-indexed ROM.
Eight physical macrosteps match both the projected raw state and its complete
193-bit representation. This remains a **static-Address computation substrate**,
not Gács/Gray maintenance or noise repair.

[Recorded experiment](../../figs/fixed_rule/projected_selfsim_v1.json) ·
[Independent audit](../../figs/fixed_rule/projected_audit_v1.json) ·
[Next regeneration mechanism](REGENERATION_PLAN.md)

## What is actually self-described

[addressed.py](../../gacsca/fixed_rule/addressed.py) defines an unprojected rule F
on 193-bit cells: the complete 177-bit evaluator/packet state plus a 16-bit Address.
Address and the static record fields are unchanged by F. The
[explicit NAND description](../../figs/fixed_rule/addressed_description_v1.json)
includes all 193 output bits and every controller/packet transition. It has
3,029 gates and 579 inputs. It contains no ROM lookup or host interpreter opcode.

[addressed_block.py](../../gacsca/fixed_rule/addressed_block.py) assembles that
description into one retrieve/evaluate/stage/commit program. Let P denote this
fixed program and J_P(a) its seven static fields at physical Address a:
`kind`, `index`, `a`, `b`, `d`, `first`, `last`. For legal 16-bit addresses outside
the colony, J_P returns a declared total extension: MEM, index=a, other fields zero.

[projected.py](../../gacsca/fixed_rule/projected.py) drops these **68 static bits**
from physical state. Its lift iota_P restores them from the physical cell's Address;
pi drops them. The physical transition is G = pi F iota_P, sitewise on the same
radius-one neighborhood. The native kernel has the ROM compiled as a `const`
table; its evolution API receives no program, ROM pointer, depth or target kernel.

The description evaluated by G is F's complete description, **not a purported
literal NAND description of the projected ROM lookup**. The precise reason it
still self-simulates is the commuting relation below. This distinction is
essential: an unrelated ROM or a list of supported opcodes would not establish it.

## Projection and block relation

For every projected raw state x, including arbitrary controllers, packets and
Address values, pi(iota_P(x))=x. F preserves Address and the seven static fields.
Therefore the image of iota_P is invariant and

    F iota_P = iota_P G.

The [tests](../../tests/fixed_rule/test_projected.py) compare this local relation,
the full 193-bit circuit, the scalar rule and the compiled projected kernel.
The invariance argument uses the actual transition's unchanged fields, not an
assumption that projecting a CA automatically gives another CA.

Let E_F,D_F be the fixed block representation for F. Its physical template sets
Address to the within-colony position, so every template cell lies in the image
of iota_P. Define

    E_G = pi E_F iota_P,       D_G = pi D_F iota_P.

Info bits survive projection unchanged. On valid encoding boundaries, the full
Info word is itself in the lift image. The decoder checks this instead of silently
discarding mismatched program bits. Combining the complete F block relation with
the commuting relation gives D_G G^U E_G = G and preserves the boundary conditions
for successive macrosteps. This is a construction argument backed by executions,
not an exhaustive or mechanized proof of every raw-state case.

It implements the projection principle described by Gray pp.31–32 for this
restricted computing rule. Gray's self-correcting automaton also changes Address
and explicitly reconstructs represented program data. That part is **not** supplied
by the static-Address argument.

## Physical execution and tests

```bash
python -m unittest discover -s tests/fixed_rule -p test_projected.py -v
python -m unittest discover -s tests/fixed_rule -p test_projected_initial.py -v
python -m experiments.fixed_rule.projected_selfsim --output figs/fixed_rule/NEW_NAME
```

**6 projection/dynamics tests passed in 56.127 s**
([log](../../figs/fixed_rule/projected_tests_v1.log));
**3 initialization tests passed in 0.230 s**
([log](../../figs/fixed_rule/projected_initial_tests_v1.log)). The former includes
156 random/targeted local triples, complete schema checks, sparse/dense parity,
exterior locality, strict decoding, and two full projected macrosteps. These are
separate runs, not a new aggregate full-suite claim.

The recorded four-cell represented ring runs **8 × 74,193,216 = 593,545,728
physical ticks** on 30,432 physical cells, in **222.73244603630155 s**. Each period
performs 913,361,248 local evaluations. All projected and lifted raw fields match;
all boundary checks pass. A pre-existing READ_B computes a write at step 2, and a
ROM-selected NAND instruction executes a second write at step 8. Incoming packet
data and old-value reads are both active in this trajectory.

The independent audit checks **4,000 projected raw bits and 6,176 lifted raw bits**
after the initial frame. It verifies scalar and dense C projected transitions,
full lifted F transitions, the final physical decoder, the ROM snapshot, the
compiled binary hash, and all **33 live/archived source hashes**. Zero mismatches.

[Raw projected/lifted traces and final physical state](../../figs/fixed_rule/projected_selfsim_v1.npz) ·
[Exact sources](../../figs/fixed_rule/projected_selfsim_v1.tar.gz) ·
[Program](../../figs/fixed_rule/projected_program_v1.json)

Source archive SHA-256:
`fbac4720d170798c48e8394f704989d22ceb413eb5df1ed19dfc61e83deebb34`.
ROM SHA-256:
`eafb3cb1da192aef716370a821843a62864a0d30374b514e38cdae54b879c71b`.
The ROM occupies 106,512 compiled bytes; it is not counted as evolving cell state.

The local CPU engine still executes every physical tick. It evaluates old
radius-one neighborhoods of active heads/packets and synchronously commits their
outputs. Stale inactive fields are handled explicitly. The fixed ROM lookup only
uses the Address of each supplied local neighbor; it does not fetch distant
physical state or replace a simulated transition.

## Depth and costs

The colony size is Q=7,608 and U=74,193,216. The final retrieval arrival precedes
the first description read by 68,417 ticks. Physical state is always 125 bits;
the represented word is always the complete 193-bit lift. Neither size changes
with requested depth.

[projected_initial.py](../../gacsca/fixed_rule/projected_initial.py) lazily constructs
E_G^d using the same ROM and physical schema at depths 1/2/3. It also tests ordinary
quiescent top data under G, rather than a top-specific kernel. These are initial
configuration checks; **depth-two/three physical dynamics were not executed**.
For one top cell:

| Depth | Physical cells | Dense uint32 bytes | Literal ticks / top transition |
|---|---:|---:|---:|
| 1 | 7,608 | 547,776 | 74,193,216 |
| 2 | 57,881,664 | 4,167,479,808 | 5,504,633,300,422,656 |
| 3 | 440,363,699,712 | 31,706,186,379,264 | 408,406,447,459,051,007,901,696 |

These are state-storage counts, not peak initializer memory or measured feasible
runtimes. They do not satisfy Gray's Q≥8192, U=128Q construction budget, and no
shared GPU allocation was requested or used.

## Address-repair counterexample and next work

The tests retain a concrete failed extension. Change an unprojected cell's Address
from the first program record to the next, keeping its old static fields. Its old
instruction index is 0, while J_P of the new Address has index 1. The state no longer
equals the lift of its projection. Thus the current commuting relation cannot be
reused unchanged when maintenance repairs Address. Also, an Address error in this
static rule persists; the ROM supplies no Address repair by itself.

[REGENERATION_PLAN.md](REGENERATION_PLAN.md) specifies the next local controller
mechanism: load the computed represented Address, scan to its program record,
read the record locally, and reconstruct represented program fields before
commit. The complete controller and fixed timing must be included in the new
description. This is needed before adding real maintenance, not an optional
polish to an already correct noisy construction.

Gray/Gács local maintenance, spatial/temporal redundancy, simulated-layer repair,
D8/D10 resolution, deeper physical execution and robustness remain unfinished.
**One projected computing link executes; zero completed Gács/Gray hierarchy levels
are claimed. The full goal remains active.**
