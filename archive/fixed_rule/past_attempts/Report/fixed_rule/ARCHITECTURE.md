# Fixed-rule construction: architecture and proof obligations

This is a construction plan supported by an executable evaluator slice, **not a
completed Gács/Gray self-simulator**. See [REPORT.md](REPORT.md) for measured results.
No arbitrary user-program platform is proposed. NAND is an explicit low-level
representation for testing the intended rule family's computations.

## Source constraints

- [Gray, pp.27–30](../../../../../papers_txt/gray_readers_guide.txt): a colony represents a
  **whole cell state**, gathers neighboring represented states, computes, then
  updates. The rule description includes the interpreter, transport, and local
  maintenance. A truth table is too large; a concise computational description
  resolves that obstacle. His finite moving signals motivate a fixed controller
  with workspace distributed across cells.
- Gray pp.31–32: simulated ProgramBit is overwritten using simulated Address and
  the colony program. The projected automaton removes ProgramBit, deriving it
  from physical Address. Gray explicitly describes the result as specialized.
  Requiring a general-purpose language would add an unnecessary goal.
- Gray pp.33–34: fivefold storage **and procedure** redundancy, three gathers,
  stage resets, temporal separation, trickle-down and update are separate
  obligations. None follows merely from a working interpreter.
- [Gács §§9.2–9.3](../../../../../papers_txt/gacs_2001.txt): identical or suitably modified
  self-correcting rules are allowed. `My-rules` must describe the evaluator too.
  Algorithms 9.3–9.7 give Retrieve/Eval/Update and local mail. Condition 9.20 gives
  capacity and computation-time bounds; Theorem 9.2's bound is an **upper** bound.
- Gács §19, Definitions 19.4–19.6 and Algorithms 19.1–19.7: error-correcting
  encoding, history-sensitive decoding where needed, repeated Legalize,
  three evaluations with voting, and locally maintained outputs. These are not
  implemented by the present bare tape evaluator. Section 11's amplifier
  hypotheses remain obligations, not properties inherited from self-description.
- [Masumori](../../../../../papers_txt/masumori.txt) explicitly omits self-simulation; its
  local-structure experiments cannot validate the missing hierarchical machinery.

The shared [audit](../../../../legacy_tower/Report/audit_20260920.md), [Flag2 counterexample](../../../../legacy_tower/Report/flag2_recovery_gap.md)
and [current report](../../../../legacy_tower/Report/REPORT.md) remain applicable. The present work does not
resolve printed Flag2 persistence or computed-SimBit timing (D10).

## Proposed route to an actual fixed rule

Choose a single finite physical state schema and radius (at most five for a
Gray-based version), then describe **all** local transitions in one finite rule
language. Separate logical parameters, simulated raw controller bits, and payload
from the fixed physical controller. They occupy encoded spatial data. Evaluation
must process that data with local tape/head or equivalent finite-state dynamics.
There is no register pair indexed by hierarchy level.

The next implementation should use a fixed-size computation region **per
colony**, with heads confined by local boundary markers and separate local mail
tracks. Each region retrieves the complete encoded raw neighborhood, evaluates
one description of the combined maintenance/transport/evaluator rule, stores the
result in Hold, and commits at a fixed work-period boundary. The current single
ring head does not provide colony confinement or inter-colony retrieval.

Initially keep Q and U the same at every level. This avoids introducing variable
logical parameters before a single closure relation works. If amplification
later requires varying parameters, encode Height/Frame spatially and have a fixed
rule compute them, as in Gács §19.3. Merely choosing new host-side tables by level
would reinstate the existing tower's limitation.

For a projected construction, let B* be the unprojected rule including the
simulated-ProgramBit overwrite, and P its complete description. Let iota_P insert
the program derived from Address, and pi discard ProgramBit. A candidate
projected local rule is F = pi B* iota_P. This expression is **not a proof**:

1. The description P must cover B*'s own lookup/copy controller, not just payload
   maintenance or a test program. Its serialized size and evaluation cost must fit.
2. On the selected encoding manifold, prove B* iota_P = iota_P F (or explicitly
   formulate the modified-rule simulation relation). Then prove the block
   simulation relation D F^U E = F on complete raw states, with admissibility
   preserved for successive periods.
3. Gray's projection is described on specially chosen histories. Extending it to
   malformed states needs a total convention. In particular, an immutable
   unprojected ProgramBit is not necessarily a function of the **new** Address
   after repair. An address-change witness distinguishes keeping the old program
   bit from regenerating it from the repaired Address. Do not assume projection
   commutes on those states without checking the actual convention.
4. Include the expanded controller in the self-description again whenever
   retrieval, ROM projection, resets, voting, or commit logic changes. Freeze the
   rule only after those components and their size inequalities close together.

An alternative follows Gács's explicitly interpreted `My-rules` construction,
with a fixed description-generating mechanism. It has the same complete-controller
and resource obligations. Neither approach requires arbitrary user programs.

Finite-depth initialization can recursively place E-translated states in Info;
that host recursion is initialization only. A top boundary must be a designated
ordinary state or encoded boundary condition handled by F. It cannot select a
local-only top kernel. Whether a quiescent top marker is dynamically admissible
under the eventual maintenance rule must be proved and tested; no such hierarchy
initializer or termination marker is implemented here.

## Implemented evaluator substrate

[machine.py](../../gacsca/fixed_rule/machine.py) defines a total local rule on
2^135 raw states. Its dependency offsets are exactly a subset of {-1,0}; it takes
only two Cell values, not a ring or host callback. Static tape fields are kind,
16-bit index/a/b/d, and one memory bit. Dynamic fields are head, two-bit phase,
16-bit pc/ra/rb/rd, and one carried value. All fields are encoded, including stale
or malformed raw controller values.

A head processes its present site then moves one cell right. FETCH loads one
NAND instruction, READ_A retrieves its first operand, READ_B computes NAND with
the second, WRITE stores the result and advances pc. A LOOP record resets pc.
Unmatched records consume one ordinary local tick. The transition is defined
also for multiple heads and invalid tape layouts; only the optimized runner
requires the single-head invariant.

The self-description is a 1,128-gate acyclic NAND circuit with 270 input bits and
135 output wires. It explicitly describes the controller and token transport.
There is no `SELF`, host-function, recursion, or depth opcode. This is stronger
than an opcode inventory or identity program: its physical evaluation reproduces
active transitions of the evaluator itself. It is still the preliminary,
unprotected self-description that Gács §9.2 distinguishes from the desired
self-correcting construction.

[native.c](../../gacsca/fixed_rule/native.c) executes literal local ticks. For a
single head with zero controller fields elsewhere, only the head site and its
right neighbor can change. It calls the same local function at those two sites;
all other sites are fixed points. No tick is skipped and no represented
transition is substituted. Dense evolution, scalar Python evolution, and sparse
C evolution are tested against one another. The sparse invariant is rejected,
not assumed, on entry; arbitrary damaged configurations can use the dense rule.

The ring harness duplicates the same local circuit for every represented cell.
It stores all outputs separately before writing any inputs, so even direct
neighbor input wires respect synchronous old-state semantics. All feedback is
physical NAND execution. From the canonical initial head position, the route is
data-independent; an initializer computes one fixed U from tape geometry. Tests
run exactly U ticks per macrostep, with no stop-on-output or input refill.

## Why the harness cannot be counted as a hierarchy

Its encoding places a **whole represented ring on one physical tape**. It is not
one colony per represented cell, and its gate layout changes with ring size.
The local transition and one-cell description remain fixed, but there is no
Gray hard-wired/projected program and no local block encoding invariant.

With n represented cells, the harness has 1,398n NAND instructions,
2 + 1,398n memory records, and 3 + 2,796n physical cells. Fixed 16-bit labels
permit at most 46 represented cells. Even encoding a one-cell ring yields 2,799
physical cells, so applying this same whole-ring encoder recursively already
exceeds capacity. Widening the labels per depth would be a failed approach.
The regression test explicitly rejects this attempted recursion without changing
the rule. This is a preserved architectural counterexample, **not a claim that
arbitrary-depth fixed rules are impossible**. Separate, locally communicating
colonies remove the need for one global label space.

Rule identity tests currently cover raw-state widths, fingerprints, and different
represented ring sizes. They cannot certify depth invariance of a hierarchy that
does not yet exist. Depths one, two, and three must ultimately use the same schema,
compiled transition, hard-wired description, and radius; their test must compare
those identities while also checking successive decoded controller transitions.

## Source fidelity and resource decisions

[maintenance.py](../../gacsca/fixed_rule/maintenance.py) separately lowers Gray's
printed maintenance component into 14,349 NAND gates at Q=8192, U=1048576. It
returns Address/Age/Flag1/Flag2 and carries the supplied workspace flags unchanged.
Strict majority, computed-Age Flag2 timing, and literal printed erasure match the
scalar reference. This circuit is a component test, **not integrated into the
135-bit physical evaluator**, and supplies no computed workspace/trickle behavior.

The physical maintenance evaluation costs 574,198,758 ticks on 29,108 cells.
That does not fit the existing Q=8192, U=1048576 work period. The self-description
harness also takes over 50 million ticks per macrostep. These are measurements of
this deliberately simple serial evaluator, not lower bounds on the construction.

Two explicit alternatives remain: optimize/localize computation enough to meet
Gray's U=128Q schedule, or select a documented Gács-style modified schedule with
larger fixed U and re-establish the relevant maintenance and error-separation
bounds. Increasing Q alone does not justify either choice; recompute the complete
program size, routing, all three evaluations/gathers, correction, and clock widths.
The present implementation supports neither schedule claim.

For D8, retain printed behavior as the source fixture; candidate erasers are
separate hypotheses. For D10, compare repaired-current Info with a precisely
specified pre-wipe signal; the literal final-neighbor post-wipe interpretation
already has a radius violation. Integration tests must reproduce that witness
rather than silently reading outside radius five.
