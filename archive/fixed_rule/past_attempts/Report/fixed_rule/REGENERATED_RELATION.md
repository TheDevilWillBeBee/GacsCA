# Macro-boundary relation for the regenerated computing rule

This is an inspectable proof outline for the computing substrate. It does not
establish the missing Gács/Gray maintenance or repair theorem, and it is not a
machine-checked equivalence proof for the complete physical alphabet.

## Admissible lower configurations

For each length-Q block, require:

- Physical Address is the canonical local index 0,...,Q−1. Program records are
  derived from the one fixed ROM; in the unprojected lift they equal that ROM.
- Exactly one physical head is at the first site, facing right, with phase FETCH
  and pc=0. Other sites have no head or stale controller registers.
- There are no pending packets. The two constant wires have values 0 and 1.
- The 194 Info bits encode a complete lifted upper cell, with its static record
  consistent with its encoded Address. Upper controller/packet fields can be any
  raw values; they need not describe a well-formed upper tape.

Other memory bits can be arbitrary. The first head's operand/value registers may
retain values from the preceding period. These are the conditions checked by
`check_boundary` together with the strict decoder. Neither is invoked by the
physical rule as a repair operation.

The encoder chooses one member of this relation by zeroing scratch/neighbor
banks. The end-of-period configuration need **not** equal a fresh encoding:
scratch values and head registers survive. Successive simulation therefore uses
an admissibility relation, not a falsely asserted exact reset to E(G(x)).

## Why the next macrostep depends only on the encoded upper configuration

1. Fixed SEND instructions replace every bit in the two neighbor banks. Their
   destinations are fixed local slots and their payloads are the old Info bits.
   Info is untouched until commit. Packet travel and computation timing are
   independent of payload values. The measured schedule certificate puts every
   arrival before the first description read and separates emissions by more
   than a complete packet lifetime for this geometry.
2. NAND instructions overwrite every circuit gate wire in topological order.
   They read constants, the three complete input words, or earlier gates. READ_A
   replaces the carried value before READ_B consumes it. Stale scratch/head
   operands cannot affect the computed full output.
3. Two NANDs per output bit overwrite every Hold bit before any Info bit changes.
   Outputs that refer directly to old input wires are therefore preserved too.
4. For each projected-out field bit, CLEAR resets the query accumulator; 16 LOADs
   read Hold.Address; META overwrites that Hold bit with the matching local ROM
   record bit. The head scans physically through the program, and the declared
   fallback handles targets outside the program region. The waiting phase makes
   the completion time independent of target Address and bit value.
5. Two NANDs per raw output bit replace every Info bit from Hold. This includes
   head, direction, phase, pc, operand/value registers, packets, Address, and the
   regenerated static fields. LOOP restores pc=0; the scheduled return leaves
   the head at the first site facing right. No packet remains. Constants and
   physical layout fields were unchanged.

Consequently the intended relation maps an admissible encoding of x to an
admissible encoding of G(x) after U ticks. Reapplying the same relation explains
successive periods without host refills. The program includes the transition
of the LOAD/META controller itself in its evaluated description; raw upper META
and reflection branches are exercised by full physical macrostep tests.

## Hierarchy and limits of the evidence

The same encoder can be composed at initialization. There is no level argument
in G, no extra physical registers per level, and no top-specific transition.
A quiescent top configuration terminates the finite initial tower using the same
rule. Given the full macro-boundary relation for all admissible inputs, its
composition would yield a depth-d macrostep in U^d ticks and Q^d cells per top
cell. Lazy initialization and resource tests verify this representation through
three levels; they do not execute those deeper dynamics.

The source/scalar/native/description comparisons, locality tests, metadata timing
checks, staged-word reconstruction, and repeated physical macrosteps are finite
experimental evidence for the relation. The outline still relies on code-level
correctness of the full description, compiler, native implementation, and stated
boundary invariants. Corrupted physical Address, missing heads, damaged mail,
and raw nonadmissible geometry are outside its noise-free invariant. None of the
missing recovery mechanisms follows from self-reference or this outline.
