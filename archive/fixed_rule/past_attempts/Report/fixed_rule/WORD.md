# Word-based fixed-rule construction: maintenance enters the described rule

This candidate replaces individual fetched NAND-bit gates with a fixed, finite
set of operations on 64-bit fields. It includes printed Gray maintenance in the
same local rule as the evaluator. This advances complete self-description and
simulated structural repair; it is not yet the full Gray work-period simulator.
The prior computing-only construction and its validation remain preserved.

## Source justification and mathematical choices

Gray pp.31–32 explicitly hard-wires a specialized self-simulator and removes
ProgramBit by a projection. Gács §§9.2–9.3 describes computation using fields and
permits an identical or suitably modified simulated rule. Neither requires
arbitrary user-program support. The local arithmetic primitives here are NAND,
addition modulo 2^64, logical right shift (zero for shift >=64), equality,
unsigned less-than and literal assignment. These suffice to describe all
controller, arithmetic, routing and maintenance branches. They are finite-state
local operations, not external subroutines that advance an upper layer.

The source maintenance component is ported with exact domains Q=2^23 and
U=128Q=2^30. Radius five, strict majority votes, Address/Age repair and printed
Flag2 erasure follow the existing independently written scalar source oracle.
The printed singleton Flag2 persistence counterexample remains. Gray p.33's
computed-Flag1 clearing of mail and clearing of simulation workspace on an
Address change are coupled into the described transition. All four physical
flags and the full Age are encoded. No external clock replaces Age.

There is an explicit source departure: the evaluator currently runs continuously
and is not gated by Gray's five active/rest stages, three retrieval rounds,
voting, clocked resets or final commit window. Gray's computed-SimBit ambiguity
and early program-overwrite versus post-evaluation reconstruction remain open.
This candidate demonstrates a building block, not an equivalence theorem for
Gray's complete construction or Gács's correction/amplification machinery.

## Fixed transition and representation

`word_rule.py` defines a total radius-five transition F over 31 raw fields,
783 bits. `word_description.py` independently compiles every branch into a
straight-line word description: 341 input words, 1,834 operations, 31 outputs.
Every evaluator field is included: phase, program counter, operands, destination,
value, selected ALU, direction, both packet tracks, and structural fields.
Randomized and branch-directed checks compare scalar F, described F and native F.

Seven program fields (kind, index, two operands, destination, first, last) are
removed by projection pi. The physical alphabet has 24 fields / **585 bits**.
One immutable local ROM P restores these seven fields from the cell's Address:
J_P is the lift, and the physical rule is **G = pi F J_P** (J_P applied to each
neighbor). The ROM has 4,431 rows; padding returns LOOP, index=Address and zero
for the other program fields. No constructor, transition, descriptor or ROM takes
hierarchy depth as a parameter. Host initialization may nest the same encoding.

Actual repair changes Address, so F need not preserve J_P's image. In particular,
F can output Address 111 with old raw index 143. The intended macro relation is
therefore

`D(G^T(E(x))) = G(x)`

with the stronger internal-record obligation

`Info(G^T(E(x))) = J_P(G(x))`.

It is **not** the false static-Address assertion `F J_P = J_P G`. After computing
all outputs into Hold, the local evaluator uses its own META operation to rebuild
seven program words from Hold.Address. It then commits all 31 words. META is
itself described in F, including selector, scan, wait, fallback and head state.
This is how the complete rule plus local reconstruction realizes the specialized
self-reference diagram; merely including an opcode inventory would not suffice.

Raw input encoding uses one memory cell per full field, including controller and
flags. Ten neighboring raw records are sent by local mail, in two independent
tracks, with remaining-hop counters supporting distances one through five. This
populates all eleven input banks. A locally loaded WAIT countdown permits those
packets to arrive before evaluation. NAND/ADD/SHR/EQ/LT instructions evaluate the
fixed descriptor using reflected head scans in the core. Static padding never
executes an upper transition. Recurrence may leave scratch RAM dirty: every
necessary descriptor wire, input bank and output word is overwritten each cycle.

## Resource accounting

| Quantity | Fixed value |
|---|---:|
| Physical bits / uint64 storage columns | 585 / 24 |
| Complete represented bits / raw words | 783 / 31 |
| Neighborhood | -5 through +5 |
| Colony size Q | 8,388,608 |
| Structural Age period U=128Q | 1,073,741,824 |
| Complete descriptor operations | 1,834 |
| Memory cells | 2,207 |
| Program instructions | 2,223 |
| Core size including loop | 4,431 |
| Unclocked cycle T | 67,368,118 |
| T/Q | 8.030905485153198 |

The radius-five retrieval overlaps five-colony packet travel with the head's
prefix. The last arrival is tick 44,690,291; first descriptor RAM access is
44,717,187, leaving 26,896 ticks. Same-track packet characteristics are checked
modulo Q for collision. The descriptor-fetch-to-final-boundary tail is
22,657,613 ticks, below Gray's 8Q=67,108,864 active-update allowance. **The whole
cycle is slightly above 8Q**, and the existing continuous cycle is not a
128Q work period. Tail capacity is necessary but does not establish a correct
clocked five-stage schedule.

Q and T are chosen once for this candidate, independently of hierarchy depth.
Depth d requires Q^d physical cells and T^d ticks per top cell/transition under
the current block interpretation. Lazy initialization/resources at depths 1–3
are tests of uniformity, not execution evidence. These sizes still make literal
multi-level dynamics impractical; any future acceleration needs its own exact
representation proof, with no host replacement of simulated transitions.

## Exact CPU representation and limits

The general scalar and native radius-five kernels accept the whole finite
alphabet. For a CPU run, `word_world` uses a restricted physical domain:
canonical Address modulo Q, uniform Age, and zero Flag1/Flag2/Wf1/Wf2. Direct
substitution into the printed maintenance equations proves this domain invariant:
Address is unchanged, Age increments modulo U, all flags stay zero. Workspace,
heads and packets do not affect those maintenance equations. This allows a
1,018-operation specialization of F on the domain, using only three neighboring
raw workspace records; structural radius-five dependence has been discharged by
the invariant. It is not a level-dependent transition.

Canonical padding has no heads, zero data, static Address and the same uniform
advancing Age. Only the two mail tracks vary; their speed-one trajectories are
stored as events. Core neighborhoods are stepped synchronously by the physical
transition. WAIT may skip exactly to its countdown expiry or the next packet
arrival. Age is stored as an initial epoch plus elapsed physical time and is
materialized in exposed cells/arrays. The normalized private array alone is not
a complete raw physical state. Boundary, packet-crossing, missing-target, multiple
hop, arbitrary payload and Age-rollover tests compare with the full local rule.

The accelerator rejects damaged physical structure. Encoded upper damage is
ordinary data, so complete maintenance executes locally on that data without
violating the physical-domain restriction. This distinction permits a simulated
repair experiment, **not** a noise-robustness claim or a demonstration of repair
of the lowest physical layer.

## Finite termination and outstanding obligations

`word_initial.TerminalOrbit` supplies a same-rule periodic cap: no heads or mail,
canonical Address and uniform Age with a fixed payload. Age keeps advancing with
period U under G; no special top kernel exists. Nested initial configurations
use the same E and G. This cap does not prove stabilization of nonterminal upper
configurations or completed depth-two/three trajectories.

Still required: local source stage clocks/reset/commit; actual spatial and
temporal redundant codes and voting; simulated-layer correction beyond the
present printed maintenance; trickle-down/amplification; correct behavior on
damaged physical structure; successive deeper dynamics; and measured noise
robustness. Preserve and distinguish source alternatives for Flag2 and SimBit
instead of silently choosing a convenient correction. The full project goal
remains active.

The completed two-macrostep run and independent audit are recorded in
[WORD_VALIDATION.md](WORD_VALIDATION.md). The next stage-controller design and a
measured failure of serial temporal voting are in [WORD_CLOCK_PLAN.md](WORD_CLOCK_PLAN.md).
