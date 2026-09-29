# Compact computation window with colony-scale mail

This construction revision addresses the measured whole-colony-scan bottleneck.
It uses one **237-bit radius-one physical rule**, one **370-bit unprojected
self-description**, and one immutable program ROM for every initialized depth.
The description has **9,445 NAND gates**, including the WAIT controller and all
packet, metadata, and boundary behavior. It is not a depth-selected version of
the earlier 125-bit prototype; the earlier code and evidence remain unchanged.

The computation window has **L=27,522 cells** inside a colony of fixed
**Q=268,435,456** cells. The compiled schedule is **U=1,370,086,072 ticks**, or
**5.1039683520793915 Q**. These are construction constants, not runtime parameters
or functions of hierarchy depth. The complete computing cycle is now shorter
than Gray's 8Q active-update allowance. That comparison is limited to this
computing substrate: the missing maintenance, redundancy, radius-five retrieval,
and clock-stage scheduling must be included before claiming Gray's budget is met
by a faithful implementation.

## Source and architectural reason

Gray pp.31,34 invokes a description and computation that grow mildly with the
word lengths while colony space/time grows with Q. Gács §9.3 similarly distinguishes
computation locations from the whole colony. The earlier evaluator reflected its
head at the colony boundaries for every operand read. Padding that design made
both runtime and available time grow by the same factor and did not solve its
17,194Q schedule.

Here the head reflects at computation-window boundaries. Mail crosses colonies
using local **Address==0** and **Address==Q−1** tests, independent of the head's
reflection flags. Instruction operands and raw words use a fixed 32-bit width;
that width never varies with requested depth. An explicit WAIT instruction reuses
the destination register as a countdown. It holds the head in place while
positive, decrements it locally, and advances pc when zero. Every branch and the
counter decrement are in the self-description.

The program emits neighboring-state packets as a pipeline, loads Q from the two
existing constant wires using described CLEAR/LOAD instructions, then executes
WAIT. The delay is part of the physical rule, not a host pause. It provides time
for the final packet to reach the destination bank before evaluation begins.
The schedule certificate checks both arrival time and coincident moving-packet
characteristics, rather than incorrectly requiring each packet to finish before
the next emission.

## Projection and padding

Let F be the complete unprojected rule. Its 133 projected-out bits are opcode,
index, three operands and two head-reflection flags. P is the fixed program
compiled from the complete description of F. For Address<L, J_P(Address) comes
from P. Outside the window, J uses the LOOP opcode, index=Address, and zero
operands/flags. The padding opcode is intentionally non-memory: a padding site
must not consume a packet whose destination matches its index. META's missing-
target fallback produces this same record, including its opcode, locally.

The immutable ROM stores only the L actual program records. Its current constant
entries fit in uint16 storage; a capacity guard rejects truncation. Runtime state
and operands still have the declared 32-bit widths. The physical rule is
G=pi F iota, with iota restoring J from Address and pi dropping the static record.
The colony program evaluates F, regenerates all 133 static record bits in Hold,
and commits the entire 370-bit represented word. Physical Address remains static,
so the lift also obeys the same static-Address commuting relation as before.

The encoder changes only the complete Info word in the target colony. Both
neighbor words arrive through physical packets. Decoding validates every static
record bit against encoded Address and retains raw controller/packet fields.
Lazy initialization composes this same encoder through three levels. No deeper
physical evolution or colony repair is implied by those initialization tests.

## Exact CPU representation and its restricted domain

A dense three-colony array would require 805,306,368 physical cells. The CPU
reference stores only the 82,566 computation-window cells explicitly. Canonical
padding is represented by its fixed Address pattern and zero data/controller
fields, plus finite packet world-lines. The complete physical transition remains
`fp_local`; no upper-cell oracle or self-simulated state update appears in the
runtime. Oracles are called only after a macrostep for diagnostic comparison.

Two analytic operations represent exact physical evolution on this domain:

1. **Padding transport.** Padding never has a head and its opcode is non-memory,
   so it cannot modify data or consume mail. Each packet track shifts one site
   per tick; the two tracks do not interact when they cross. Events retain packet
   target, bit, crossing flag, destination colony, and the exact arrival time.
   The runtime reconstructs ghost cells at the computation-window edges and
   performs the actual local transition on reentry. Rightward crossing occurs
   on entry at Address 0; leftward crossing occurs when leaving Address 0.
   A second boundary drops the packet according to that same local rule.
2. **WAIT/empty-window intervals.** If all active core sites are holding WAIT
   heads, all core packet tracks are empty, and no arrival intervenes, a span of
   d ticks subtracts d from each positive countdown. A skip stops at the earliest
   zero countdown, next arrival, or requested end time. With no active core sites
   at all, the core is fixed over the same arrival-free interval. Other core
   transitions are evaluated at each physical tick. The run records literal core
   ticks and skipped ticks separately; their sum is the represented physical time.

Events persist across runtime calls; no host transition is installed at chunk or
macrostep boundaries. A diagnostic can reconstruct any individual padding cell
at the current time. The full saved macro-boundary state consists of explicit
cores and an empty padding-event set, with the declared canonical padding rule.

This representation is **not** justified for arbitrary damaged padding. It rejects
noncanonical physical Address in its explicit initial cores; it has no interface
for a hidden head or mutable data in padding. Those restrictions are on the CPU
representation, not on the total local rule. Actual maintenance would change
this invariant, especially for Age evolution and Address faults. Its integration
must extend or replace the representation and prove/test the new conditions.

## Exact schedule

| Quantity | Value |
|---|---:|
| Physical state bits / uint32 fields | 237 / 18 |
| Complete represented state bits | 370 |
| Self-description NAND gates | 9,445 |
| Memory cells | 11,298 |
| Instructions before LOOP | 16,223 |
| Computation-window cells L | 27,522 |
| Physical colony cells Q | 268,435,456 |
| Work-cycle ticks U | 1,370,086,072 |
| U/Q | 5.1039683520793915 |
| U minus described Q-tick wait | 1,101,650,616 |
| Packet lifetime | 268,435,086 ticks |
| Last arrival | 309,168,388 |
| First description read | 311,204,913 |
| Arrival margin | 2,036,525 ticks |

These values come from the generated program and its schedule certificate, not
from the old colony/work-period parameters. Two three-colony macrosteps completed in 506.0526903234422 seconds with zero
projected or lifted raw-state mismatches. They represent 2,740,172,144 physical
ticks: 2,223,120,652 literal core ticks plus 517,051,492 exactly skipped wait/quiet
core ticks. Padding transport uses the explicit world-line representation. The
second macrostep performs an active NAND write. The independent audit verified
63 source files, all 1,422 projected and 2,220 lifted post-initial bits, the
compiled kernel, complete NAND/scalar/native agreement, final decode, and empty
padding. Exact commands/artifacts are in STATUS.md. Complete primitive tests
check scalar/C/NAND equivalence, local boundary behavior and 32-bit carries.
Transport tests compare local physical steps around real core boundaries and in
padding, including a three-colony nonaliased delivery fixture. WAIT skipping is
compared to literal execution; malformed geometry is rejected explicitly.

## Remaining objective

This is still a computing self-simulation link, not a completed Gács/Gray level.
It resolves a specific measured evaluator timing obstacle for the present rule.
Missing work includes source-faithful local structure maintenance, a 128Q stage
clock, resets and commit timing, radius-five communication, spatial and temporal
redundancy, simulated repair, and measured noise robustness. The first maintenance capacity check already rejects naive unshared circuit
concatenation: its gate traversals alone exceed the current active-update budget.
[MAINTENANCE_INTEGRATION.md](MAINTENANCE_INTEGRATION.md) records the checked
26,799-gate maintenance component, rejection calculation, and concrete next
obligations. The timing margin must be re-established for the full rule.

The printed Flag2 persistence witness and computed-SimBit timing ambiguity remain
open. The current program regenerates after evaluation, before commit. Source
comparisons must continue to distinguish this choice from Gray's early-work-
period program-bit overwrite. Do not infer repair or a noise threshold from the
faster computation, wider fixed alphabet, or implicit representation.
