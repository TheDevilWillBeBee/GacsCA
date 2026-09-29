# Next optimization routes for the fixed AND candidate

2026-09-28. This was the pre-implementation priority list for the fixed AND
candidate (Q=16384, U=2^30, 3383 MEM, 11380 instructions, 14764 core cells,
648041233 scheduled controller-path ticks). Routes 1 and the inexpensive
shared-gather part of route 2 have since been implemented and measured as
isolated candidates; see
[BRANCH_AND_GATHER29_CANDIDATES.md](BRANCH_AND_GATHER29_CANDIDATES.md).
Their complete own-ROM symbolic results remain conditional on physical
instruction/packet refinement. The estimates below are historical planning
numbers, not the final measurements.

## 1. Compute only Flag1/Flag2 in the early pass

The work period runs one evaluation after the third temporal vote to send
Flag1/Flag2 signals and another full evaluation later to commit the complete
encoded state. The current first pass computes all 154 outputs to obtain just
two needed values. A backward slice of the final descriptor finds 300
operations for Flag1 and 445 for Flag2, with 445 in their union. In the
current verified dependency order, the latest required operation is index
467 of 8926. The ROM reaches it after 600 instructions and 20348033
scheduled ticks, versus 9295 instructions and 289005289 ticks for the full
evaluation. This is a *measured prefix of the existing ROM*, not a new
candidate schedule.

Introduce one fixed branch kind (15 is unused in the four-bit kind field):
in the early stage, jump over the rest of the description to the Flag send
instructions; in the later stage, fall through. Store the two Flag words
before branching. The moving head can scan passively until the target PC;
no extra register pair or depth selector is needed. The full later
evaluation and commit remain, so this is preferable to simply deleting
the second pass, which would weaken late recomputation after faults.

Replacing one full pass by the measured prefix gives a rough total path
of 379383977 ticks before branch overhead, changed self-description, and
recomputed ROM layout. This is below 2^29=536870912. It could enable
U=2^29 after retiming all reset, vote, capture, Wf, and commit windows.
The branch itself changes the physical rule; its controller transition and
both outcomes must be included in its own description. Re-run complete
raw output equivalence, own-ROM dataflow, physical paths, successive
decoded macrosteps, and repair checks. The actual new path might differ
from this estimate.

## 2. Replace unrolled rule routines with counted loops

The dominant remaining Q cost is 11380 instruction cells. At the current
3383-cell MEM allocation, Q8192 would leave at most 4803 instruction
cells after the loop cell and five tail reservations: at least 6577
instructions must disappear. The three gather bodies are 691 instructions
each; sharing one body across stages could remove roughly 1382 cells,
before any parameter and branch overhead, and would still not reach Q8192.
The evaluator itself is the major target: its full body is 9295
instructions. Gray pp. 29–31 describes copying/comparison routines in
nested loops and a short program whose parameter constants grow mildly
with log(Q U); Gács §9.2 similarly uses a concise rule language. That
supports a fixed specialized counted-loop instruction set for this rule
family, with ROM, counters and all evolving data local to colonies.

A useful first slice is a shared gather loop, followed by repeated
majority/correction kernels. Measure instruction count and physical travel
separately: ROM compression alone does not ensure a shorter work period
if the head still performs the same number of long scans. Every new loop
mechanism must describe its own controller and remain fixed across depth.

## 3. Change the serial head's data movement

The three gather stages take about 23.24 million head ticks each. A full
evaluation takes 289.01 million. Reordering and scratch tuning already
saved only a few million ticks; the basic cost is moving a head around a
roughly 14764-cell core for thousands of operations. A local streaming
or spatially distributed evaluator, or a small number of carefully chosen
fixed compound operations, could reduce travel much more than further
topological ordering. This is higher implementation and proof risk: packet
exclusion, local causality, fivefold repair, and the evaluator's own state
must be re-established. Benchmark on the A100 only after a CPU local-rule
reference and coordination with the main agent.

## 4. Pack encoded raw fields and reuse workspace

The complete raw state has 4090 meaningful bits in 154 word slots; the
projected state has 2704 meaningful bits in 105 word slots. The ROM needs
738 distinct raw neighborhood inputs, 689 of them gathered, and reserves
four history/vote slots per gathered input. Packing narrow fields or
recomputing some cheap derived fields could lower MEM and communication
cost. It adds unpacking operations and complicates fault localization;
therefore measure *net* core and time after recompiling the complete own
rule. It is less likely than routes 1–2 to cross the next Q/U threshold.

Do not prioritize reducing the fivefold protection or dropping the late
full evaluation solely for clean-run speed. Both changes touch the repair
contract that the project ultimately needs. The printed Flag2 persistence
counterexample and computed-SimBit timing ambiguity also remain source
qualifications, independent of compiler cost.
