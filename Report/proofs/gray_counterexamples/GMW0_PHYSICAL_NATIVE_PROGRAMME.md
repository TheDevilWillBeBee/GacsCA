# GMW0: an emitted compact native word programme and physical execution

This is a construction checkpoint at **Q=8192, U=128Q=1048576,
lambda=24, c=104**. It supplies an actual finite radius-five moving-head
interpreter primitive, its emitted bit programme, and a physical fifth-stage
execution certificate for the **native prefix**. It does not supply an own
programme for every field of this interpreter, a self-simulating automaton, or
a counterexample to Gray's intended construction. All changes below are
isolated from the repository's active rule.

Sources: [kernel](gray_moving_word_kernel.py),
[checker](check_gray_moving_word_kernel.py),
[receipt](../../../figs/gray_counterexamples/GMW0_native_programme_certificate.json),
[actual beta](../../../figs/gray_counterexamples/GMW0_native_beta.bin),
[listing](../../../figs/gray_counterexamples/GMW0_native_listing.json),
[retained inputs and physical trace](../../../figs/gray_counterexamples/GMW0_native_physical_replays.npz).
The immutable source hash and receipt hashes are in the receipt/checkpoint.
The [initial listing failure](../../../figs/gray_counterexamples/GMW0_initial_listing_failure.json)
and source snapshots are retained: signed presentation operands were initially
compared directly with their unsigned finite-width decoded residues. The
corrected listing records the decoded residues; the emitted beta is unchanged.

## Exact primitive statement

Let C[j], -5<=j<=5, be any eleven legal raw native words: Address in
[0,8192), Age in [0,1048576), and four binary flags (Flag1, Flag2,
Workspace.Flag1 and Workspace.Flag2). No consistency, common clock, or flags
assumption is made on these **simulated inputs**.

At the physical level, start in canonical Address x mod Q, common Age
112Q+1, all four native flags zero, and exactly one GMW0 head at Address3024
in each colony. Its five copies, all native-input tape copies, Info copies and
Out copies are coherent. The input tape holds the eleven input words C[j]
at the 37 columns2960..2996. Out and Info are initially zero. The immutable
code lookup is the emitted GMW0 beta. There are no errors during execution.

**Theorem (proved for this primitive).** The native programme occupies2346
bits and uses107 instructions. It halts after34396 physical ticks, at common
Age951901, before the fifth active interval ends at120Q=983040. The head
stays in its colony and remains unique there. Its Out bits at columns
2960..2994 are exactly the35 native output bits of the literal scalar
transcription of Gray pp20--22 on C. These Out bits persist through rest.
At the update producing Age0 they are committed into all five corresponding
Info copies, before Out is reset. The native geometry remains canonical and
the physical native flags remain zero throughout.

The theorem also applies to different C inputs in different colonies:
heads, input accesses and writes never cross colony boundaries. The theorem
does not identify the other2237 frame bits with their correct upper outputs.
It therefore is a **native-prefix execution theorem**, not an upper whole-cell
transition theorem or a complete encoded period theorem.

The literal printed Flag2 predicate is retained; no h1 correction is used.
The physical native Workspace.Flag1/2 outputs of this primitive are explicitly
fixed zero. It is this quiet interface, not a construction of Gray's complete
workspace sources, that ensures the physical native flag premise persists.

## Defined finite machine, including raw states

The physical alphabet has2272 bits per cell. Native fields use37 bits. A
logical head has434 bits:114 metadata bits and sixteen20-bit registers.
There are five434-bit head copies, five11-bit memory-column copies, five Out
bits and five Info bits. Thus

    K = 37 + 5*434 + 5*11 + 5 + 5 = 2272; 2K=4544<=Q.

This layout is an explicit tentative new layout, not Gray's illustrative
earlier layout. The represented bit strip is centered at2960. Its native
prefix is Address2960..2972, Age2973..2992, Flag1 at2993, Flag2 at2994,
Workspace.Flag1 at2995 and Workspace.Flag2 at2996. Code starts at3024 and
ends just before5370. Code is
not a mutable SF field: beta(old raw Address) is a fixed finite lookup table.
The register packet and tape are mutable, copy-voted fields and can be
overwritten by noise; immutable code does not imply a reliable computation.

Each instruction is encoded little-endian with a five-bit opcode followed
by the widths in `ARGS`. The maximal instruction is29 bits. These generic
primitives are word move,20-bit arithmetic/bit operations, comparisons,
Boolean NOT, bit selection, five-word equality-majority with a default and
an existence bit, integer window counts, mismatch counts, branches, loads,
writes, NOP and HALT. The definitions are explicit finite equations. None
calls the native transition or the whole physical transition as an intrinsic
operation. Majority and window count can be implemented by finite Boolean
circuits; they are part of this enlarged alphabet's local rule.

The total kernel first bit-votes each prospective incoming old head, selects
one according to its old movement, then executes that packet at its destination
using the destination's current raw Address and voted tape column. Candidate
precedence is stationary self, then left, then right. Multiple candidates
produce a stationary ERROR head. Modes6/7, movement3, reserved opcodes28..31,
and invalid memory/window ranges have explicit ERROR outcomes. A missing head
produces zero. Packet fields are masked to their finite widths. FETCH reads
one fixed code bit per tick and retains its partial instruction in the packet;
SEEK walks to a requested code or tape coordinate; LOAD/WRITE walks consecutive
bit columns. HALT and ERROR stay stationary. Invalid raw packets may have
additional stationary or travelling behavior, but every update is defined;
the theorem does not certify convergence from them.

The primitive resets head and Out on the update producing Age112Q, births
heads on the update producing112Q+1, executes while112Q+1<newAge<=120Q, and
holds voted fields otherwise. At newAge0, Info reads the **old voted Out**,
then head and Out reset. This is a defined write/reset order; it does not
resolve Gray p41's computed-SimBit workspace-source order. Finally the mandatory
SF wipe `newFlag1 && newAddress != old raw Address` zeroes head, tape, Out
and Info at the physical holder. Native flags/geometry are computed before
this wipe; Workspace.Flag outputs zero remain the stated component change.

## Radius proof (proved, all raw physical states)

Use S=(0,-2,-1,1,2). Copy s at physical x represents logical y=x+s. A voted
word at y reads its holders y-t, t in S. An incoming head can come from
y-1,y,y+1, so its furthest required holder is x+s+j-t, |s|<=2, |j|<=1,
|t|<=2. These offsets are exactly[-5,5]. A current tape, Info or Out vote
uses offsets s-t in[-4,4]. Code lookup and raw Address use x+s in[-2,2].
The outer native transition/wipe uses[-5,5]. Reset/active gates use the
physical holder's computed native Age. No migrated packet reads a source's
computed Age or Address; this is crucial to avoid a sixth-site dependency.
Every field of the defined primitive therefore has radius at most five.
This is neither the literal all-raw computed-SimBit composition nor GV0;
its fixed-zero workspace interface is what avoids that unresolved integration.

## Native programme correctness (proved by register invariants)

The following is a finite straight-line word computation with three forward
branches. Registers0..4 are the scratch five-word window. Registers12/13
retain raw central Address/Age. All loaded Address words are13-bit; adjusted
Address is computed by20-bit add/subtract followed by AND8191, exactly modQ.
All Age arithmetic is mod2^20=U. Branches and writes use the final fields only.

1. Right adjusted Address majority is R6; its existence is R7. Right Age
   majority is R8; its existence initially R9. Both defaults are the raw
   central words. Left adjusted Address/Age majorities are R10/R11, with the
   same defaults. MAJ compares full words, not majority of individual bits.
2. R14 begins `!R7 || !AgeRightExists`. The two MI5 counts add the left,
   inside-colony Address and Age discrepancies >=3. Thus it is exactly the
   native inconsistency predicate before flag-source terms. The apparent
   inside filter is `R7 && 0<=R6+j<Q`, even when another field has no majority.
3. LOADCOL packs the eleven raw Flag1/Flag2/WF1/WF2 values into R0/R1/R2/R3,
   with lane j+5. WINCNT then adds WF1 inside-count>=3, right Flag1
   inside-count>=3, and raw central Flag1 with right inside-count>=2. R14
   is exactly computed Flag1.
4. R4 is `!R7 && (R11+1)%16==0`, the printed source3. R9 becomes the WF2
   inside-count>=3, source4. R15 first computes the off-to-on Flag2 predicate:
   left inside-count>=4, or Flag1 and raw left-count>=4, or either source.
5. Complementing the eleven-bit Flag2 mask with XOR2047 and counting inside
   left entries computes the number of left in-colony zeros. Testing count<1
   and !Flag1 gives the **literal printed** erasure clause(a). Raw left
   count<1 with Flag1 gives clause(b). Their complement, or either source,
   is the keep predicate. A forward branch replaces R15 by this predicate
   exactly when raw central Flag2 is1. Thus R15 is printed computed Flag2.
6. `R7 && (!R14 || R15)` chooses right native votes; otherwise R6/R8 are
   replaced by R10/R11. R8 is incremented modU. The four WRITE instructions
   write R6's13 bits, R8's20 bits, R14 and R15. These are the scalar's35
   native outputs for every legal raw C input.

Each register step follows the emitted listing and the generic opcode
equations, so this proof uses no successful-random-input premise. The checker
retains98 concrete raw inputs/results, including full-range Age, nonexistent
majorities and flag extremes, as additional **measured** implementation checks.

## Physical lifting, initialization and time (proved for noiseless premise)

For a coherent logical word v, all five voted holder words equal v. Thus a
quiet coherent tape remains equal to its logical tape. An isolated coherent
head moving by -1,0 or+1 creates exactly one incoming candidate at its next
logical site and none elsewhere. All five output holders compute the same
packet and optional write from the same vote, raw Address and code bit. This
proves coherent head/tape/Out/Info closure by induction on ticks. The birth
equation makes exactly one logical head per canonical colony. Every SEEK
target is inside that colony. Writes target native columns2960..2994. The
packet therefore never crosses a boundary, and uniqueness is preserved.

Canonical Address and a common legal clock with zero flags stay canonical
under the literal native scalar: adjusted Address and Age right and left
votes agree, inconsistency and workspace sources vanish, Flag1/2 remain0,
and Age increments modU. The physical wipe is consequently absent. This
induction applies independently of the arbitrary **upper** C tape contents.

Every code position from3024 through5369 consumes one tick: branch skips
walk through the skipped positions at one site per tick instead of fetching
them. All branches are forward and skip no memory command. Consequently
they change registers but not the total travel time. For each memory command,
let e be its final instruction-bit coordinate, a its first tape column, w
its number of bit columns, and r=e+1 its return PC. Its extra ticks beyond
the code-position count are

    |e-a| + (w-1) + |a+w-1-r| - 1.

The final subtraction removes the first return-code fetch already counted
among code positions. Summing the emitted14 load/write excursions gives
32050 extra ticks; together with2346 code ticks this is34396. (The checker
pins the actual excursion count/list rather than relying on this prose count.)
The birth row112Q+1 is917505; halt is951901; the slack to120Q is31139 ticks.
HALT/rest keep Out coherent; the update to Age0 reads voted old Out into Info
before resetting Out. This proves the stated boundary native-prefix commit.

The checker also replays the **actual local-transition function at every one
of the34396 execution ticks**, rotating among the head's five physical
holders. These finite replays and invalid-state receipts are measured checks.
The universal physical lift rests on the copy/migration induction above,
not on treating this finite replay as exhaustive all-state verification.

## Remaining whole-rule obligations (unproved)

This beta describes only the native35 output bits, not the2272-bit physical
rule. It does not evaluate the interpreter metadata/register/copy transitions,
arbitrary instruction decoding, mutable memory, output/Info equations, or
immutable beta lookup for simulated upper cells. An own full beta must
describe those fields and fit/runtime in the same layout; no fixed point is
claimed here. Our native execution uses nearly half the fifth active budget,
so the remaining service evaluation cannot be assumed to fit.

The input tape is preloaded. Faithful three gatherings, retention/reset,
third-gather early native evaluation, ProgramBit/hardwirer transfer, full
fifth-stage evaluation and full Info distribution have not been integrated
with GMW0. The native inputs may be arbitrary, but the physical interpreter
initialization is coherent and quiet; continuing E0 robustness for this
different mutable kernel is unproved. In particular one voted operation
does not prove that a travelling error head cannot collide with the correct
head. The fixed-zero WF interface is a changed component, not Gray p41.
The earlier raw computed-SimBit/radius/order obstruction remains accepted
with its original scope and is not repaired by this quiet primitive.

Thus GMW0 closes the earlier **specific bit-SSA encoding obstruction** for
the native prefix by a different representation. It is an actual emitted,
physically executing prefix, and still leaves the full self-programme and
Gray-protocol refinement open. No iid theorem, decoded memory failure or
faithful full-Gray counterexample follows.
