# Fixed AND opcode: measured ROM candidate

2026-09-28. This is a new fixed finite-state rule candidate, not an upgrade of
the earlier physical-period or depth-two execution certificates. It keeps
Q=16384, U=2^30, radius seven, 154 raw 64-bit words with 4090 meaningful
bits, and the 105-word/2704-bit projected alphabet. The rule, ROM, and
neighborhood do not depend on requested depth. Q/U and all clock constants
are pinned in this candidate's own parameters module. Depth is supplied to the
initializer, which places encoded parent states in colony Info cells; no
depth-specific evolution kernel is used.

Gray pp. 31–32 explicitly removes ProgramBit after hard-wiring a program that
is determined by Address. The resulting automaton need not support arbitrary
programs. Gács §9.3 calls simulation of an identical or suitably modified
self-correcting rule “self-simulation.” This candidate uses that latitude to
give its complete own finite rule a specialized word-code description. It does
not claim Gray's Q=8192, U=128Q numerical budget or Gács's noise theorem.

## Change and measured cost

The physical four-bit `kind` has unused value 14. The three-bit `alu` has
unused value 6. One new fixed instruction kind, `AND=14`, fetches the same
two operands and writes the same destination as existing binary ALU
instructions. The moving controller records `alu=6`, and the local MEM
READ_B transition computes `a & b`. The complete raw rule description
includes this new fetch branch and READ_B computation. Its compiled ROM
therefore describes the actual modified evaluator, including its controller.
Its raw description digest is
`13753641417305409333a10208609b932c28b26643a6c88d49d2c8a8d2b0e48f`.

The compiler keeps the rule description's Boolean logic in compact NAND
form, then replaces an **exclusive** two-NAND cone
`NAND(NAND(a,b), NAND(a,b))` with one AND operation. This is an exact
64-bit identity for every possible raw input. The graph pass retains every
declared input and all 154 outputs; it fuses 1629 cones, reducing the
optimized self-description from 10555 to 8926 operations. It emits 1635
AND instructions because six were already part of the rule description. A
verified dependency ordering then visits output dependencies in reverse order;
scratch capacity 256 is fixed in the ROM compiler. The final ordered
descriptor digest is
`81b018a5f73c324e5caf14ce4a6d8781cdef03ec9823ee87501a3477841b331c`.

| Resource | Previous compiler-only candidate | Fixed AND candidate |
|---|---:|---:|
| Physical Q / U | 16384 / 2^30 | same |
| MEM cells | 3397 | 3383 |
| Instruction cells | 12883 | 11380 |
| Core cells | 16281 | 14764 |
| Core plus reserved tail | 16286 | 14769 |
| Scheduled controller path ticks | 811855585 | 648041233 |

The new ROM saves 1517 core cells and 163814352 scheduled controller ticks
(20.18% of the previous path). Its ROM SHA-256 is
`09394d7d9f357c66cbaea14d549d90de396d8592252c5735a60d89848221090a`.
The schedule's three gathers, two evaluations, third-stage delivery, and
capture all fit their existing windows. The new cost **does not lower Q or U**:
14769 physical sites still exceed Q=8192, and the sequential controller
path 648041233 ticks exceeds 2^29. Thus no smaller Q/U pair is claimed.
Holding the current 3383-cell MEM bank fixed, Q8192 would leave only 4803
instruction cells plus the loop/tail reservations, so at least 6577 of the
11380 instructions must disappear. One evaluation consumes about 289 million
head ticks; this serial execution architecture is the main time bottleneck.
For scale, Gray's illustrative U=128Q at Q8192 is 1048576 ticks, about
618 times shorter than this candidate's total scheduled controller path.
This comparison is an engineering gap, not a contradiction of Gray's
asymptotic construction or a lower bound on another implementation.

The bounded 8-order × 7-capacity search exposed a Pareto tradeoff. With the
selected reverse-output dependency order, capacity 256 has the smallest core,
14764 cells, and 648041233 path ticks. Capacity 270 has the fastest path,
647887321 ticks, with 14778 core cells. Capacity 256 was chosen to reduce
space at a cost of 153912 ticks, 0.024% of the path. These are only layout
variants of the same fixed rule; the search is not an optimality proof.

## What was checked

`python -m unittest tests.fixed_rule.test_and_holder_candidate -v` passed
8/8 in 4.678 seconds. Tests require distinct HALT/AND codes, fixed widths
and radius, equality of all raw scalar outputs to the compiled descriptor on
random and clock-boundary inputs, a real moving-controller AND fetch and
READ_B local step, locality under a change at distance eight, intact raw
controller decoding at depths one and two, and ROM identity through depth
three. The projected state schema and decoder are owned by the new rule,
rather than imported from the older baseline. Mutating the compiled `s2_pc`
output fails the exact symbolic check.

`python -m experiments.fixed_rule.certify_and_holder_read_b` passed. Under
explicit coherent procedure/geometry and regular active-clock premises, a
symbolic one-step comparison checks all 154 raw outputs at nine target
positions for every canonical base Address for AND READ_B, and likewise for
both ordinary and right-endpoint AND FETCH. This covers 4158 raw output
words over the three event cases. The one-step proof uses arbitrary
surrounding static metadata and Data. It does not compose the fetch, scans,
reads and write into an entire physical instruction flight.

`python -m experiments.fixed_rule.certify_and_holder_rom` passed. Structural
term equivalence compares every one of the 154 complete raw outputs of the
new physical rule and optimized description on arbitrary typed inputs.
Conditional own-ROM symbolic data flow checks 15 colonies, 62010 history
instances, 310125 instructions, 2940 metadata queries, 26790 packets, two
evaluations, and commit/reset of every Info word including controller fields.
It explicitly executes all 1635 encoded AND instructions as word operations.
The independent measurement receipt is
`figs/fixed_rule/and_holder_candidate_v6.json`: 5.223 seconds, peak
376136 KiB CPU RSS, with 71 SHA-256s for imported fixed_rule proof
dependencies and explicit owned sources. Every receipt hash was independently
rechecked against the worktree. No substantial GPU job or
shared CUDA build was launched. The preordering receipt
`and_holder_candidate_v1.json`, earlier source seals
`and_holder_candidate_v2.json`, `and_holder_candidate_v3.json`, and
`and_holder_candidate_v4.json`, `and_holder_candidate_v5.json`, and the 56-trial search receipt
`and_holder_order_search_v1.json` are retained as data outside Git.

The own-ROM dataflow proof is conditional on each instruction and packet
refining its physical local evolution. The full-raw AND FETCH/READ_B
one-step events pass, but the
complete new-ROM physical path composition, an actual continuous U-tick
period, successive decoded physical macrosteps, level-two repair, level-three
execution, and noise amplification have **not** been re-established. The
earlier baseline certificates cannot be transferred to a changed physical
rule and ROM. Address-derived static metadata makes this a specialized
hard-wired self-ROM; it is not a general-purpose program interpreter.

## Failed approaches retained

Initially the new `Builder.band` emitted direct AND throughout the whole
self-description. The resulting core required 16707 cells, 328 past Q after
tail reservation, and 861162314 scheduled controller ticks. The direct
description was too expensive despite saving gates downstream. Keeping the
description in NAND form and fusing only stored exclusive cones solved that
problem.

The first fusion prototype allocated AND kind 12, which already means HALT.
Its apparent 14815-cell fit was invalid: a symbolic gather passed through
HALT instead of stopping and missed its deadline. AND now uses unused kind
14. This failure is a regression guard in the tests and is why the valid
numbers above come only from the corrected rule and ROM.

## Next gates

Establish physical instruction and packet composition for this specific ROM,
including kind 14 and its complete controller state. Then run a private
accelerated continuous period and a decoded depth-two endpoint before
comparing repair behavior. For Q/U reduction, the remaining architectural
bottleneck is the unrolled, one-pass expression ROM and its serial head
travel. Replacing repeated code with verified loops/subroutines or changing
the execution layout must still keep one fixed rule and describe its own
controller; a smaller scratch bank alone cannot reach Q=8192 or U=2^29.
