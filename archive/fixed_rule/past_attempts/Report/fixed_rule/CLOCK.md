# Locally clocked self-description and temporal correction

This revision puts stage gating, five reset masks, temporal voting, boot-PC
selection, HALT and boundary commit into the fixed rule's own description. It
retains the same physical alphabet size (585 bits), raw represented width
(783 bits) and radius five as the word candidate. The ROM and transition change
once for this construction revision; neither is selected by requested depth.
This is not yet the complete Gray automaton: spatial redundancy and flag-signal /
trickle initiation are absent. Stage four currently runs a HALT entry.

## Source contract and explicit gaps

Gray pp.31–32 supplies the specialized hard-wiring/projection construction;
Gács §§9.2–9.3 supplies field-level rule descriptions and basic block simulation.
The complete F here includes the evaluator's own raw controller, mail, maintenance
and clock operations. The hard-wired projection G=pi F J_P removes seven static
program words. Each macroprogram computes F, locally reconstructs the seven
program words at the computed Address, and commits J_P G. Actual Address repair
means this reconstruction remains essential.

Gray p.34 defines the five active/rest stages below. The first three gather into
separate histories; stage five votes and computes afresh. A third-stage evaluation
is implemented separately, with its Hold checked before stage four clears it.
It does **not** yet distribute flags to the boundary signal locations, so the
source purpose of stage four is unfinished. The final commit uses old Age U−1
so the new state has Age 0; the subsequent old-Age-0 reset clears Hold, not Info.
Computed-Flag1 mail/workspace clearing still has priority after clock operations.
Wf is zeroed outside the **computed** Age interval [96Q,98Q), but no rule yet
initiates the source Wf waves inside that interval.

| Stage | Active ages / Q | Rest ages / Q | Reset retention |
|---|---|---|---|
| Gather A | [0,16) | [16,32) | Info |
| Gather B | [32,48) | [48,64) | Info, A |
| Gather C; vote/evaluate at 72Q | [64,80) | [80,96) | Info, A, B |
| Reserved trickle stage | [96,104) | [104,112) | Info, A, B, C |
| Vote/evaluate | [112,120) | [120,128) | Info, A, B, C |

Ordinary stage gates use current Age. The Wf window uses computed Age, as specified
on Gray p.41. Program roles for reset/vote/commit come from the current raw program
record. The computed-Address signal rule on p.35 remains missing, not silently
substituted by these roles. D8's printed Flag2 persistence remains; D10's
computed-SimBit interpretation is not resolved. Program reconstruction is still
post-evaluation, whereas Gray describes an early overwrite. An early input-record
reconstruction should be implemented and distinguished from the required
post-Address-change output reconstruction.

## Local memory geometry and noncircular boot

Each raw input word occupies a four-cell group A,V,B,C. At old Ages 72Q and 112Q,
V takes bitwise majority of its neighbors at offsets −1,+1,+2. The three original
histories survive, so stage five can vote them independently of stage three's
computation. This avoids the measured 93,977,870-tick serial-voting composition,
which exceeded the 8Q budget. The vote is an actual radius-two suboperation of F,
not a host preprocessing function or whole-word equality vote.

Each of 31 Info words is immediately followed by its Hold word. At old Age U−1,
Info copies that neighbor locally. No host boundary transfer occurs. The program
writes all complete raw outputs to Hold and uses LOAD/META to replace its seven
program fields from Hold.Address before the boundary commit.

Existing static operand fields encode finite reset-retention masks and roles.
At the first physical cell, a/b/d instead store five 32-bit stage entry PCs
(64+64+32 bits). F describes how to select these slots from local Age. Their
values are emitted only after compiling F, avoiding a cycle in which F would
contain constants determined by its own compiled length. Stage-three evaluation
reuses the fifth entry. HALT removes its matching head through a local transition;
its behavior is also included in F's description. All subsequent stages restart
from the appropriate encoded entry without host intervention.

The scalar transition composes the frozen word rule with these clock operations;
the compiler transcribes that composition into one complete straight-line
2,484-operation word description. There is no depth-dependent call chain or
recursive host interpretation. The 31-field encoding includes every clock,
controller, mail and maintenance field. Strict decoding checks the static program
record against the computed Address as well as all dynamic fields.

## Measured layout and budgets

Q=8,388,608 and U=128Q=1,073,741,824 are fixed. The compiled program has 3,919
memory cells, 3,560 instructions and one final reflection/loop cell: **7,480**
core cells. Entry PCs are (0,343,686,1029,1030). Info occupies the even addresses
1372 through 1432, with paired Hold immediately to the right. Descriptor outputs
and temporary wires are spatial memory, not extra physical register banks.

| Stage computation | Ticks after its reset |
|---|---:|
| Gather A last arrival | 47,523,250 |
| Gather B last arrival | 47,523,252 |
| Gather C last arrival | 47,523,253 |
| Complete evaluation, Hold, reconstruction and HALT | 49,749,480 |
| Evaluation allowance, 8Q | 67,108,864 |
| Evaluation margin | 17,359,384 |

Gather C has 19,585,611 ticks of margin before the 72Q vote. The first two gathers
have over 86 million ticks of margin before rest. Packet characteristics on each
track are checked for collision. No assumption about the old 4,431-cell core or
its continuous cycle supplies these new bounds. Exact descriptor and program
exports are `clock_description_v1.json` and `clock_program_v1.json`.

## Exact CPU representation

The full scalar/native rule is defined on arbitrary radius-five raw states.
`clock_world` accepts only canonical physical Address, uniform actual Age, and
zero physical/workspace flags. Direct substitution in maintenance preserves this
domain. Its specialized 1,503-operation expression has radius two for workspace;
maintenance's wider dependency is discharged only by that invariant. Inputs may
contain arbitrary raw workspace/controller values. Tests compare this expression
against complete F at every stage boundary and on raw workspace states.

Explicit cores are synchronous. Canonical padding has static Address, advancing
uniform Age, no heads and zero data; mail alone varies. Events record its local
speed-one motion using an **active-tick** clock. Motion pauses during rests and
all pending mail is erased by a stage reset, exactly as in F. Uniform Age is
materialized when a raw cell/core array is exposed; private normalized storage
alone is not a raw physical state.

Two exact shortcuts are used:

- Quiet/WAIT spans end at a packet arrival, countdown expiry or clock boundary.
  During a rest, all simulation state freezes except mandated boundary/clearing
  operations, which are handled explicitly. No reset, vote or commit is skipped.
- Head-scan spans require no core packets and at most one active head per colony.
  The next stopping point is its instruction fetch, memory action, META lookup
  or reflection. The shortcut cannot cross it, a packet arrival or a clock
  boundary. Between these events, the physical rule only transports unchanged
  head registers across passive cells, leaving data untouched. The executor moves
  those registers over the proven span and advances physical Age. Arithmetic,
  memory writes, lookups, resets, votes and commits still use the compiled local
  transition. It never evaluates or replaces an upper-layer transition.

Parity tests cover all eight phases in both directions against literal stepping,
multiple-head rejection of unsafe scans, a real nonaliased eleven-colony gather,
mail pausing/reset, and all bulk boundaries against the complete native radius-five
kernel. Structural faults are rejected by this representation. This remains
unsuitable for physical-noise experiments; simulated faults are ordinary encoded
RAM handled by complete F.

## Terminal data and deeper levels

A finite initializer ends at explicit raw top states and nests the same E. The
former unclocked canonical no-head terminal orbit is **false** for this rule:
old Age 0 creates a boot head at Address 0. A distinguishing test preserves that
counterexample. `clock_initial.terminal_data` supplies an alternative same-rule
periodic cap with uniform Address Q−1, Flag1=Flag2=1, no heads/mail and arbitrary
payload. Its Age advances modulo U; every other field stays fixed under G.

This cap is deliberately **not an organized quiet colony**, and is not asserted
to remain a suitable boundary when flag signals and trickle-down are implemented.
It uses initial data only, with no top kernel. Arbitrary finite top data are also
allowed. Lazy initializations at depths 1–3 have identical rule/ROM/width, but no
depth-two/three dynamics have been executed. One depth-two top cell requires
70,368,744,177,664 physical sites and 1,152,921,504,606,846,976 ticks per top step;
even explicit lowest-level cores number 62,746,787,840. The resource problem is
not solved by successful initialization or by the one-link accelerator.

## Validation status

The complete two-period experiment and independent audit passed; see
[CLOCK_VALIDATION.md](CLOCK_VALIDATION.md) for exact commands, measurements,
provenance and the distinction between saved-array audit and runtime assertions. The
experiment checks all three raw histories, both fresh evaluations, five rests,
boundary commit, simulated vote/commit/repair, and an active write across two
successive periods. An isolated stage-five protocol test corrects each one-history
corruption and produces a different full output for two corrupted histories.
Those controlled history corruptions are not localized-noise or iid experiments.

Remaining obligations include early program repair, computed-Address flag signals,
source-faithful trickle/amplification, fivefold spatial redundancy for every
simulation operation, physical-fault execution, organized termination as needed,
deeper dynamics, and measured robustness. The full research goal remains active.
