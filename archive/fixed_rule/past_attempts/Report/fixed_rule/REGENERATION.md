# Local regeneration of represented program records

The new candidate retains a **125-bit, radius-one physical rule**, with one
compiled ROM independent of hierarchy depth. Its underlying unprojected rule has
194 bits and a complete 4,345-gate NAND description, including the new metadata
controller. Previous projection files and artifacts are preserved as separate
construction revisions; none is selected by the requested depth.

This is a computing-substrate result. Physical Address is still static. There is
no integrated Gray/Gács colony repair, redundancy, or noise-robustness result.

## Source and exact scope

Gray pp.31–32 explicitly reads the simulated Address, finds the matching local
ProgramBit, and overwrites the represented program bit; projection then removes
that field from the physical alphabet. The resulting machine is specialized for
self-simulation. Gács §9.2 permits an identical or suitably modified simulated
rule, and §9.3 includes the interpreter in the program and separates retrieval,
evaluation, and update. These sources support local self-description access;
neither requires an arbitrary user-program platform.

Our adaptation projects seven program fields rather than one ProgramBit. They
are opcode, index, three operands, and two region-boundary markers: 69 bits in
total. Regeneration occurs in a full staged output word **after evaluation and
before commit**, rather than at Gray's stated early-work-period point. This
choice is explicit and is not a resolution of the source's computed-SimBit timing
ambiguity. Its contract is to canonicalize the represented static record to the
computed Address. Real maintenance integration must justify its update timing.

## Local mechanism and description closure

`regenerative.py` supplies CLEAR, LOAD, and META in addition to NAND, SEND, and
LOOP. CLEAR zeroes the existing 16-bit destination accumulator. Sixteen LOAD
instructions read the staged Address bits locally, most significant bit first.
META then traverses the colony, reads one bit of the static record at the site
whose Address matches that accumulator, and stores the bit in staged output.
It does not read another physical cell's state without moving the head there.

The original three-bit phase and existing registers suffice. The unprojected
opcode grows from two to three bits; those bits are projected out, leaving the
physical width unchanged at 125 bits. All new fetch, load, scan, missing-target,
reflection, and write transitions are in the evaluated NAND description.
Unused opcodes, head collisions, malformed controller words, and missing target
Addresses have total transitions. No depth, ROM pointer, or simulated transition
callback is passed to the runtime kernel.

A META instruction at physical site p, targeting output location h, finishes
`1 + 4Q + h - p` ticks after the head arrives at its fetch site. It first completes
the partial traversal, then scans the entire colony, then waits for the next
first-site reflection before writing. A missing target uses the declared total
extension: MEM opcode, index equal to the queried Address, other static fields
zero. Present and absent targets have the same duration. A simpler immediate
write after the match would introduce target-dependent colony timing.

`regenerative_block.py` compiles neighbor retrieval, the complete rule description,
a full true-bit Hold bank, 69 local regeneration queries, and a full raw-state
commit. A fresh CLEAR plus 16 LOADs precedes each query, so there is no hidden
persistent register for the queried Address. Raw controller and packet fields
are encoded alongside data. Encoding reads only the represented cell assigned
to that colony; neighboring words arrive through physical SEND packets.

## Encoding relation

Let F be the total unprojected 194-bit local rule, P the fixed compiled colony
program, J_P(a) its seven-field record, iota the lift restoring J_P(Address), and
pi the projection dropping it. The physical rule is G = pi F iota. Its constant
ROM lookup depends only on a local cell's own Address. Let C_P = iota pi denote
canonicalization of a represented output word.

The colony program computes **C_P F**: evaluate F, regenerate its output program
record, commit. The block encoder writes the complete lifted word, and decoding
rejects records inconsistent with the encoded Address. At clean macro-boundaries,
the intended relation is `decode(G^U(E_G(x))) = G(x)`, with the full encoded word
matching `iota(G(x))`. Initialization is the same block map at every depth.

For the present F, Address and static fields are unchanged, so F iota = iota G
also holds. This simpler identity would fail after an Address-changing extension
that retained stale program fields. The stage test explicitly injects such a
stale staged word and checks local regeneration. That fixture is **not** a claim
that Address changed autonomously or was repaired. An actual maintenance rule
must be included in a new complete description and tested in the full cycle.

## Resource budget

| Quantity | Value |
|---|---:|
| Physical raw width / stored uint32 columns | 125 / 18 |
| Represented lifted width | 194 |
| Complete description gates | 4,345 |
| Memory cells | 5,318 |
| Instructions before LOOP | 6,753 |
| Colony size Q | 12,072 |
| Literal ticks per macrostep U | 207,565,968 |
| Compiled ROM bytes | 169,008 |
| Retrieval last-arrival margin | 108,593 ticks |

The period is 17,194 Q, about 134.33 times Gray's entire 128 Q work period.
Padding a colony does not remove this serial scanning cost. Even before the
additional radius-five maintenance, spatial redundancy and three retrieval
rounds, this compiler fails Gray's computation budget. It must not be inserted
unchanged into the existing Q/U scheduler. A faster local evaluator, or a
separately justified modified maintenance schedule, is required.

## Validation and outstanding work

The exact test and artifact results are recorded in [STATUS.md](../../../../../Report/fixed_rule/STATUS.md).
[REGENERATED_RELATION.md](REGENERATED_RELATION.md) states the reusable boundary
relation, including arbitrary scratch memory and carried head operands.
[EVALUATOR_BUDGET.md](EVALUATOR_BUDGET.md) analyzes the failed scheduling bound. Tests cover the full
scalar/NAND/native controller, dense/sparse parity, radius-one locality, fixed
META timing, raw-state encoding, staged-Address regeneration, and active complete
self-simulation. Depths two and three are initialization/resource checks only.
There are no deeper physical trajectories and no measured noise threshold.

The eight-step artifact audit passed: 46 archived/live sources, 4,000 projected
and 6,208 lifted post-initial bits, scalar/native/NAND agreement, and final decode.
The run took 1,660,527,744 literal ticks with zero mismatches. The first auditor
incorrectly assumed both NAND writes targeted the same cell; its failure is
preserved, and the corrected auditor verifies writes to cells 1 and 3 at steps
2 and 8. The physical trace was unchanged. Seventeen tests passed across four
separate targeted runs, including a poisoned-scratch macrostep.

Next: resolve the evaluator/work-period inequality before merging
actual maintenance. Gray's Flag2 persistence counterexample and computed-SimBit
timing ambiguity remain open. Full faithful Gács/Gray hierarchy construction is
still the goal, not an established property of this computing substrate.
