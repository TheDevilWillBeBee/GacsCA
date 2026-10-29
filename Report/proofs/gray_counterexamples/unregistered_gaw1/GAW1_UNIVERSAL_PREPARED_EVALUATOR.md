# GAW1: universal prepared own-evaluation of frozen GAW0D

This is a compiler/interpreter theorem for the explicitly changed GAW0D rule.
It is not a faithful instantiation of Gray, a whole-period theorem, or a noise
proof. Nothing in the frozen kernel, emitter, ROM or prior receipts is changed.
Q=8192, U=128Q=1,048,576, lambda=24 and c=104 remain the baseline. Radius eight,
17 WORD100 lanes, h1 Flag2 erasure, immutable code/dictionary, word encoding,
one 32Q gather, FULLCOL/centre READ5 and an early 42Q pass remain departures.

The prior GAW0 measurements established 124 prepared comparisons only. Here
we replace that sample premise by a compositional argument for every legal
upper raw neighborhood. The certificate checks exact emitted instances and
finite syntax contracts; the word algebra and their composition below are
part of the proof. It does not exhaust the complete state space by experiment.

## 1. Exact theorem and preparations — proved in this scope

Fix the 1979-word GAW0D ROM emitted by the frozen
`../unregistered_gaw0/build_gray_wider_word_gaw0.py`, with its ten-bit tokens,
32,768 beta-bit capacity and 1024 WORD100 dictionary slots. Let F be the
frozen `local_transition` using this very same ROM. Legal raw native fields
have widths (13,20,1,1,1,1); all SF words have width100. Every one of the
2^22,537 bit patterns is included: Q=2^13 and U=2^20 make the full native
Address and Age ranges legal, and invalid full-width head metadata is allowed.
The six native words have zero high padding in their WORD100 encoding rows;
arbitrary 231-word tape vectors violating that padding are not raw cells of
this declared finite alphabet. Thus the rule's raw
alphabet has 22,537 bits. No promise about valid simulated heads, old flags,
old Programme words, old clocks or consistent SF copies is made about the
**upper** raw input.

For any 17 legal raw upper cells C[-8] through C[8], form the readonly input
tape I at P+w, 0<=w<231, by packing word w of C[j] into lane j+8. Here P=3981
and the 231 words are exactly the six native words followed by five consecutive
copy words of each of the 45 SF fields. Prepare lower Out/Scratch zero, one
running lower head with PC=0 at P, and instruction/bit lookups from that fixed
ROM. Run the frozen `execute` physical moving-head semantics: each ordinary
instruction consumes one update; an IO instruction also consumes
max(1,abs(destination-current_address)) further updates for its SEEK task.

Then the unique head halts, visits only addresses P through P+230, and writes
all 231 output words equal to `cell_words(F(C))`. Its runtime is at most
**58,973 updates**, for every such input C. Therefore this prepared run fits
both the late **65,535 = 8Q-1** usable updates and the early **270,334 = 33Q-2**
usable updates. Late birth is at computed lower Age112Q+1; execution occupies
112Q+2 through120Q. The birth update is not available for execution. Slack in
the smaller window is 6,562 updates.

The same run is realized by five coherent physical copies under these explicit
additional lower-CA premises: canonical GF, common clock, no errors, the
readonly Mem bank I remains unchanged, zero Out/Scratch and the unique head
at birth, and no active SF wipe. Every initially coherent SF word is understood
as a logical track L(y), with copy i at physical holder y-S[i], S=(0,-2,-1,1,2).
For the current kernel canonical GF/common Age imply no SF wipe regardless
of evolving lower flags: both positive and negative native majorities give
the same GF and clock; the raw self-GF equals the computed GF. Those premises
still do not prove that a damaged gather prepares I, or that a complete encoded
period has the required reset/birth bank. They are not silently removed.

“All raw” in the theorem quantifies the simulated upper input, including all
invalid upper interpreter states. It does not quantify arbitrary broken lower
execution controls or assert noise tolerance.

## 2. Code identity and finite primitives — proved

The structural checker reconstructs the emitted ROM and compares it with the
retained actual ROM/listing. Every emitted instruction decodes to its exact
masked operands; the slots word and all fifteen virtual dispatch words are
checked. Every label fits a 13-bit word PC. Code padding is zero, hence HLT.
CODE reads one whole immutable instruction/data word in one native update;
BITCODE reads one beta bit. Neither calls a host evaluator or F.

The generic ALU is a fixed total WORD100 function. Unknown operations return
the high-bit sentinel; signed shifts outside the word return0; invalid WINDOW
and vector-width arguments have their stated sentinel behavior. Virtual ALU,
ALUI and ALUX invoke this same finite primitive with the simulated operands.
Their proof consequently requires equality of operand selection, not an
unstated constant-time whole-transition oracle. The fixed code primitive is
also shared: the evaluator simulates upper CODE/BITCODE by the same lookup on
the simulated raw PC/address. Choosing the fixed finite ROM after emitting
these lookup instructions is well-defined: neither lookup's emitted syntax
contains a copy of the entire transition table. This proves self-identity for
this declared immutable-ROM rule, not Gray's mutable Q-bit Programme protocol.

Immutable storage is **135,168 bits = 32,768 + 1024*100**. The 231-word layout
is a word-alphabet layout, not 231 bits. Extra dictionary bits are not hidden
in beta, and the following semantics theorem does not close Q-bit fit.

## 3. Actual five-holder reads and vote — proved

For a field's five consecutive rows beginning at f, a call with logical centre
lane z reads readonly Mem at P+f+i, lane z-S[i], i=0..4. These are actual raw
holders of that logical field. They are not five head-centre reads. All caller
centres are in5..11, hence every selected lane is in3..13 within the 17-lane
bank. The source centres are6..11; the main copy centres are8+S[i]; gathers and
incoming heads shift the latter by at most one. The checker lists all35
centre/copy pairs explicitly.

The helper starts U=V=W=0 and on reading b performs
W := W OR (V AND b), V := V OR (U AND b), U := U OR b, in that order. After n
reads, U/V/W denote at least1/2/3 ones among those n reads, separately at each
of the 100 bit positions. Induction proves this statement; the certificate
also checks all32 single-bit patterns. The returned W is bitwise three-of-five.
It is exactly the rule's vote, and bitwise voting commutes with concatenation
of the 22 head words and 17 Mem words.

The literal helper changes only R0,R1,R3,R4,R5,R6,R7,R8,R11. It preserves
R2,R9,R10,R12,R13,R14,R15. In particular the baseline counter, old clock delta,
logical centre, output-copy index and return address survive each call. R11
advances by five. Its cost is 86 ordinary updates (4 initialization + five
16-instruction iterations +2 exit) and five actual IO completions. After the
first completion at f, four further destinations are f+1..f+4. Every emitted
call stores its literal next PC in R15 before JMP; the checker verifies them.

## 4. Native and final-source interface — proved

The native prefix computes exactly the kernel's h1 native function. Here is
its register-level derivation, which also covers the six source-native copies.
Right/left five GF words are adjusted by minus/plus i modulo2^13; R6/R10 hold
the right/left categorical majority or raw self-GF fallback. R7 is right GF
majority existence. R8/R11 are right/left categorical Age majorities or raw
self-Age fallback; R9 initially denotes right Age majority existence.

Inside(j) means R7 and 0<=R6+j<Q. VNE and VINSIDE mask each left mismatch with
Inside. WINDOW masks the eleven flag bits by Inside and its stated endpoints.
The instructions therefore calculate new F1 as the OR of: no right GF
majority; no right Age majority; at least three left in-colony GF mismatches;
at least three left in-colony Age mismatches; at least three right in-colony
old F1 ones; self old F1 with at least two of those right ones; and at least
three in-colony old WF1 ones. These are the scalar native equations.

Let a be the left in-colony F2 count and b the unrestricted five-left F2 count.
The F2 source3 is no right GF majority and (left Age+1) mod16=0; source4 is at
least three in-colony WF2 ones. For old self-F2=0 the result is
(a>=4) OR (newF1 AND b>=4) OR source3 OR source4. For old self-F2=1 it is
source3 OR source4 OR NOT((NOT newF1 AND a<=1) OR (newF1 AND b=0)). This is
explicit h1, not the printed erasure predicate. The final selection is right
iff R7 AND (NOT newF1 OR newF2); selected Age increments modulo2^20.
Each threshold is literal LT followed by NOT, and all scalar fields are legal
width. MOVI(-1) encodes 2^20-1, whose residue modulo2^13 is indeed -1.

The checker normalizes only input acquisitions and branch-label names, then
compares **all remaining arithmetic instructions literally** across seven
native instances. Central READMASK uses lanes3..13; a source centre c uses
(FULLCOL >> (c-5)) AND2047. Both are exactly its eleven-cell native mask.
Thus the derivation applies at every source without a source-radius premise
imported from the reader.

The central native words are written first. New WF defaults to0. Reader wipe
(newF1 AND newGF!=raw self-GF) has priority. Otherwise, at96Q<=newAge<98Q,
WF1 at newGF>=Q-5 reads final primary Info at offset Q-3-newGF; WF2 at
newGF<=4 and newF1=0 reads final primary Info at offset3-newGF. Those offsets
are exactly -2..3. The six source bodies use their own native result. Source
wipe gives0; source Age0 gives its voted OLD Out; source Age80Q-1 at GF3/Q-3
gives its voted OLD corresponding courier; otherwise it gives its voted OLD
Info. This is `computed_primary`, including its commit and special writes.
No pre-wipe intermediate is substituted for final computed primary. Only its
low bit is stored into WF4/5. All source/reader support is within[-8,8].
Subsequent SF computation does not consume new WF, matching the kernel's
old-WF/native/new-WF ordering and preventing a same-update circular dependency.

## 5. Baseline, snapshots, couriers and resets — proved

For copy i=0..4, R14=i and logical centre R12=8+S[i]. The baseline loop visits
all45 fields f=6+5h, h=0..44. The helper returns the old voted word and stores it
at output f+i. Its counter R13 is unaffected by the helper. This initializes
all SF output words before the phase-dependent overrides below.

At new Age32Q the old logical Info vote is cached in R9 and seeds all17 Mem
lanes. Otherwise for lane d=lane-8, a nonzero lane moves one logical site toward
its source while0<newAge-32Q<=abs(d)Q; it holds afterward. Lane0 holds. The
emitted delta is WORD100 subtraction. Before32Q it wraps to a value greater
than8Q, so every lane holds, exactly as the kernel's signed-delta guard.
R13 determines the left/right shift, and R12 is restored after every shifted
vote. Thus this also proves the actual SF function for arbitrary raw banks,
not only a successfully transported snapshot.

New Age0 overrides Info with the old voted Out, and subsequently resets
head/Out/Scratch. The prior Out is read from its baseline output before reset;
readonly Mem remains separate. Programme is BITCODE at
(newGF+S[i]) modQ, the changed holder-computed service convention. Couriers are
cleared at Ages0/32Q; at75Q their low-bit seeds come from old voted Out at
P+3/P+2; during75Q<Age<80Q they vote logical neighbours y+1/y-1. At80Q-1,
Info at service GF3/Q-3 receives the **old** courier vote. The source vote uses
readonly input, even though the courier output was computed earlier. This
avoids a one-row timing substitution. All other Info/courier values hold.

At Ages0/42Q/112Q the 22 head words and Out/Scratch become0. At42Q+1/112Q+1
the same 22 words become0 except p=1 iff the service Address is P; Out/Scratch
retain their baseline values. Outside active Ages(42Q+1,75Q) and
(112Q+1,120Q], head remains its old voted head. None of these guards assumes
that the simulated upper clock is synchronized with the lower execution clock.

## 6. All raw head and IO semantics — proved

In an active row, three candidates are checked in priority self,left,right.
The self candidate requires nonzero voted p and move not1/2; the left requires
move1; the right requires move2. The selected centre and candidate count are
cached. If none exist all22 head words become0. Otherwise the incoming loop
copies all22 voted words of the first candidate. If the count exceeds1, the
shared error path sets p=1,move=0,mode=ERROR and restores its old PC. This is
exactly `incoming` then `fail`; other payload words retain the selected packet.

The head's move>=3 or mode>=4 fails before any instruction. HALT/ERROR retain
all payload and PC, with move0. SEEK validates target<Q, compares it with the
holder-computed service Address, and either moves toward it or performs the
following total descriptor operation. RUN validates raw PC<8192, obtains one
whole CODE word, rejects opcode15, saves the old PC and assigns nextPC=(PC+1)
mod8192 before dispatch. HLT restores oldPC; every later guard error also
restores oldPC. These shared paths implement the exact frozen `step_packet`.

The fifteen opcode cases use these literal decoded fields (bit0..3 opcode):

| Opcode | Operand selection and output |
|---|---|
| HLT | mode=HALT, move0, oldPC restored |
| JMPR / JMP / BNZ | four-bit register or13-bit immediate target; register target>=8192 fails; BNZ uses nonzero test |
| MOVI | destination bits4..7; zero-extended20-bit immediate bits8..27 |
| ALU | destination4..7, operation8..12, input register indices13..16/17..20/21..24 |
| ALUX | destination4..7; operation-register8..11; inputs12..15/16..19/20..23; operation value is full WORD100 |
| ALUI | destination4..7, operation8..12, input13..16, literal17..36 |
| CODE / BITCODE | destination4..7, input-register8..11; shared total fixed ROM primitive |
| LDX | destination4..7, base8..20, index-register21..24, lane-register25..28, source29..30; reject index>=Q, base+index>=Q or lane>16 |
| STX | value-register4..7, base8..20, index-register21..24, destination25; reject index/base+index>=Q |
| READ5 | index-register4..7, side8, immediate centre9..12; reject target>=Q or centre outside5..11 |
| READMASK / FULLCOL | destination4..7, index-register8..11, reject target>=Q |

The sixteen register indices are masked four-bit fields, so register getters
and writers select exactly one row r0..r15 of the selected copy. ALU inputs
are read before its result is written, including overlapping register operands.
For IO initiation, the args descriptor is
kind | dst<<2 | lane<<6 | source<<11 | dest<<13 | side<<14. Metadata PC advances
before SEEK; target, args, mode and move are the same values as the kernel.
Target travel and IO completion occur in the lower evaluator, whereas a
simulated upper SEEK target only determines its upper packet metadata.

On descriptor completion, kind0 rejects lane>16 then reads the already
computed Mem word for source0, baseline Out for1, baseline Scratch for2, or
**old voted Programme** for3. Programme's current BITCODE output is not used
for this old-field read. Kind1 writes the selected register into Out/Scratch.
Kind2 rejects centre outside5..11, then for i=0..4 reads lane centre plus/minus
(i+1), masks to20bits and packs them at20i into R0. Kind3 reads eleven lanes
3..13 or all seventeen lanes0..16 and packs only their low bits. These guarded
loops produce exactly READ5/READMASK/FULLCOL even for arbitrary unused high
bits in args. The output registers are the selected incoming packet's rows;
all other packet words preserve their baseline incoming values. Every
successful IO restores modeRUN/move0 without changing already advanced PC.

Temporary scratch at offsets128..149 is a different physical track from the
231 output words and readonly Mem. Each cached value (centre, incoming count,
oldPC, dispatch, target, IO destination, side, accumulator, full-column mode,
centre lane, service Address, courier seed, Workspace destination/source)
is written on the entering path before any restore on that path. IO mode
branches retain the same cached side throughout their loop. No arbitrary
upper payload can alter a lower loop counter or return address.

Finally, reader wipe takes the common main branch that writes0 to every SF
word6..230 after retaining the already computed native output; WF is already0.
This is the kernel's highest-priority wipe, including programme and couriers.

## 7. Physical and deadline composition — proved with stated preparations

Coherent five-copy fields vote to their logical words. With a unique head,
its next logical site is its old site plus move(+1/-1/0). Every holder sees all
five old logical packet copies in radius five, and exactly one matching incoming
candidate. Thus head/Out/Scratch updates are the same `step_packet` updates as
the prepared moving-head execution. Copies are restored coherently in the
same update. Common phase and canonical GF give the same service Address at
all five holders. The already frozen radius-eight rule therefore implements
the declared physical one-site head; no faster transport primitive is used.

The compositional cost checker explores a finite acyclic graph after replacing
only the following proven integer loops by their exact counters: five output
copies,45 baseline fields,22 incoming/zero-head words,5 READ5 entries,11 or17
column entries,225 wipe words, and the five-read helper just proved. Lower
R14 is the output-copy counter; R13 or R11 are these syntax counters, not
simulated register values. A separate all-branch CFG intersection dataflow also checks that every actual
temporary restore has a preceding write on every entering path; its helper
returns and fifteen dispatch destinations are literal. Every back edge's increment and bound is checked
against the actual emitted listing. Virtual opcode dispatch forks all fifteen
literal dispatch targets; every other upper-payload branch forks both ways.
Only central computed clock predicates and these exact counters constrain
branches. No random payload values or presumed common upper Ages are used.

Each ordinary instruction costs1. Every lower IO target lies in offsets0..230:
native0..5; scratch128..149; ordinary field f+copy; registers36..115; Mem116..200;
head6..115; wipe6..230. READ5/Mem bounds follow the guards just proved. The
helper's field and cursor intervals include every actual source/copy. For
intervals A,B, max(1,|Alo-Bhi|,|Ahi-Blo|) bounds every actual SEEK completion
cost. Replacing correlations by intervals increases, never decreases, the
bound. After a helper the cursor is f+4. The certificate counts the initiating
JMP separately from its86 internal instructions and all five IO completions.

Clock branches are constant on the63 boundary points defining62 half-open
intervals in `[0,U)`. The points include every literal EQ value and successor,
every LT threshold,0/1/U,32Q seed and every strict lane threshold(32+d)Q+1.
Before32Q modular WORD100 delta is uniformly large. Source-native clocks
remain unrestricted payload branches. Therefore one representative per
interval bounds every computed upper clock in that interval. The DAG's
postorder longest path gives58,973, including HLT and every IO completion.
A physical run lies along one of these bounded paths by induction on its
instruction PC, loop counts and cursor interval. Hence it halts before the
65,535-th late execution update, writes F(C), and stays in the verified frame.
The check against124 retained runtimes is a consistency check, not the proof.

## 8. Exact storage obstruction and remaining tasks

The frozen direct token emission needs605 distinct dictionary words and1979
nine-bit tokens:17,811beta bits>Q and605>512. GAW0D's declared larger capacity
makes the semantics theorem possible but does not meet the original Q-bit
Programme target. A separately specified lossless dictionary512/raw-word/LZ
representation reconstructs every one of the1979 words exactly but needs
12,780bits. Its dynamic programme is optimal **only for its fixed selected
dictionary and that grammar**, not over all dictionaries, encoders or rules.
It reserves an8192*100-bit temporary decoding buffer explicitly. It has not
been made a new physical CA primitive or timed on the fifth pass. The initial
phrase-dictionary diagnostic also fails, at18,078bits. A further fully specified syntax-only relocation copy reconstructs
the six repeated source-native bodies using internal-branch retargeting and
centre rebasing; its exact whole stream still needs10,871bits. The transform
never evaluates a cell or F, and its finite decoder counts the same51200-bit
dictionary and819200-bit temporary buffer. It is not installed as a physical
CODE primitive and is not a compiled new self-rule. These are retained
failed representations, not proofs that no Gray completion can fit.

The new claims and their status are:

| Claim | Status |
|---|---|
| All legal upper raw inputs evaluate to the complete frozen GAW0D transition on prepared coherent lower tape | proved by sections2–7 and exact-instance checks |
| Universal late/early prepared deadline, including actual operand travel | proved,58,973<=65,535<270,334 |
| Q-bit/512-slot direct emission fits | disproved for this specified emitter |
| Fixed selected512-slot/LZ representation fits | disproved for this specified representation |
| Any other exact whole emission fitsQ/512 | unproved |
| Actual three gathers with Flag1 mail erasure / temporal voting | unproved; current rule has one gather |
| Full encoded noiseless period, damaged gathers, native/Workspace higher repair | unproved |
| Gray-faithfulness, positive iid noise rate, shorter U | unproved; no such conclusion |

Artifacts are under the two isolated `unregistered_gaw0/` and
`unregistered_gaw1/` source/figs directories. The standalone validator pins
all dependencies and replays the new structural/cost checks without rerunning
unrelated historical campaigns. The active G17 rule and accepted earlier
sources/receipts are unchanged.
