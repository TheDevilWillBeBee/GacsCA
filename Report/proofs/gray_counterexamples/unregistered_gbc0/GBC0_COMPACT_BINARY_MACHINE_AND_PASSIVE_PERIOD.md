# GBC0: compact binary machine, a counted partial programme, and its exact limit

This is a new isolated component. It preserves `Q=8192`, `U=128Q=1048576`,
`lambda=24` and integer error separation `c=104`. Its declared binary
radius-eight rule is total. It has **no complete own programme**. The actual
1,058-bit programme below computes a comparison map `delta`, and computes
the physical rule only on a specified upper-clock family. At the next
capture phase there is an exact clean disagreement. Neither result is a
counterexample to Gray, Gács, G17, an intact recursive hierarchy, or iid
memory. No noise history is asserted here.

The new files do not modify the frozen GBP1R diagnostic. Its measured cost
profile motivated eliminating its eleven-register decoder and sequential
five-column read buffer. That profile is not a lower bound on interpreters.
Gray's sufficient-size promise is also distinct from his displayed
`Q>=2^13` lower bound; see [the primary text](../../../../papers_txt/gray_readers_guide.txt),
lines 1404–1410 and 1557. No failing emitter at 8192 establishes a failure
of his sufficiently-large-Q theorem.

## 1. Exact state, rule, and changes

[compact_stream_rule.py](compact_stream_rule.py) declares the entire
alphabet. The native fields have widths `13,20,1,1,1,1`. The logical SF
fields are Info, two Mail fields, three 17-bit History banks, Next, two
one-bit couriers and one 553-bit Head. Every SF has five copies with offsets
`S=(0,-2,-1,1,2)`. One cell therefore has

`K = 37 + 5(57+553) = 3087` binary coordinates;
`2K=6174<Q`; its represented primary interval is `[2553,5640)`.

Head contains presence, movement, mode, four 13-bit control words, two
buffer bits, a five-bit lane, a four-bit function, a two-bit I/O kind,
two Word20 registers A/B, a 407-bit Work word and a 35-bit native result.
These are exactly 553 bits. There is no register file, dictionary, page
table, uncounted mutable tape or host-evaluation opcode.

The rule contains an immutable **Q-bit** code string. The issued string
contains 1,058 instruction bits and 7,134 zero padding bits. PC and return
have 13 bits. Both instruction fetch and CODE read that same string,
zero outside `[0,Q)`. A generic finite native primitive maps the declared
407 input bits to the 35 Address/Age/Flag1/Flag2 output bits by the pinned
`maintenance_scalar` equations; it excludes the SF and Workspace outputs.
It is not an opcode for the whole cell rule.

Material departures from Gray remain: radius eight and seventeen gathered
lanes; corrected h1 Flag2 erasure; immutable code in place of noisy
ProgrammeBits and a hardwirer; the new Head/ISA; computed-holder Address
plus copy offset for service control; the explicitly defined binary
collect/evaluate and guarded courier implementation. Final Workspace reads
the **final computed primary Info**, including its commit and wipe. All
those equations are included in the total local rule, but no full Gray
refinement is asserted. Retaining lambda/c does not transfer his radius-five
error arguments to this rule.

The inherited schedule is unchanged: three actual gathers, History ready
by `72Q+2`, native collection `72Q+3`, native evaluation `72Q+40`, flag
delivery `80Q-1`, Workspace gate `[96Q,98Q)`, reset `112Q`, birth row
`112Q+1`, execution outputs `112Q+2..120Q-1`, rest and old-Next commit at
the period boundary. There are exactly `8Q-2=65534` usable execution
updates. This checkpoint does not shorten U.

## 2. Total generic ISA and locality — proved

`pack/unpack` and `pack_cell/unpack_cell` fix a bijection between the
declared bit vectors and typed states. All 13-bit GF and 20-bit Age words
are legal numbers because Q and U are powers of two. No native padding
completion is used. Other bit patterns, including invalid modes, are
explicit raw states, with defined transitions.

Presence zero returns ZERO. Movement 3 or modes 5–7 return a stationary
ERROR packet. HALT and ERROR hold their data and clear movement. Incoming
packets are selected in self/left/right order with the exact movement
predicate; a collision returns ERROR with the first selected data. A
pending I/O moves one site toward its 13-bit target, then consumes once.
Return and normal successor PCs must be in `[0,Q)`. HALT does not advance
PC. Instruction boundaries are not a raw-state premise.

| Decoded instruction | Entire data semantics |
| --- | --- |
| HLT | Stationary HALT, data preserved. |
| LIT | Set A from the specified bounded unary-length/little-endian payload. At most 20 unary zeros are allowed; missing delimiter or value above Word20 returns ERROR. |
| SWAP | Exchange A and B. |
| ALU | Set A to `alu(selector,A,B)` for selector 0–15; selector 16 uses the four-bit Fn; 17–31 return ERROR. Arithmetic masks to Word20; shifts of at least 20 and division/modulo by zero return zero. |
| SETFN | Set Fn to the low four bits of A. |
| BR | Fixed immediate target with condition always/A=0/A!=0/A has bit19. |
| JMP | Jump to A if A<Q, otherwise ERROR. |
| READ | Target B<Q; consume one selected bit, a five-column vote, or the whole local 17-bit History word. The kind/lane guards are explicit. Encoded lane16 uses signed Fn; it is resolved when I/O is entered. |
| WRITE | Target B<Q; consume one write of `A&1`, preserving the other data. |
| WGET | Set A to the 20-bit Work window at bit offset A, zero for offset at least 407. |
| WSET | Replace the 20-bit window at B, clipping to 407 bits; offset at least 407 is a no-op. |
| NATIVE | Interpret precisely 37 columns of eleven native input bits and set NC to the 35 explicit native result bits. |
| NCGET | Set A to the native-result window at B, zero for B>=35. |
| CODE | Set A to the same immutable code's 20-bit window at B. |
| STREAM | The generic interleaved field operation specified below, with stride one or five. |
| EXT/SELF | Select one of sixteen explicitly listed metadata/current-address words; it never calls a simulated transition. |
| EXT/ALUI | Word20 arithmetic with an immediate function and bounded literal, preserving B and Fn. |
| EXT/PUSH | Shift Work by a width 0–20 and append those low A bits; width 21–31 returns ERROR. |
| EXT/reserved | ERROR. |

LIT has maximum length 45 bits and ALUI maximum length 51 bits. Fetch is
bounded by those finite decoders and the finite code string. A future own
emitter must implement these decoders, including malformed prefixes; a
two-window virtual fetch would be insufficient for ALUI. The mathematical
definitions in the table are the complete opcode semantics, not assumed
library capabilities. Their finite guards exhaust every possible raw mode,
kind, function, lane and typed word.

Write `H_d` for the majority of the three *voted* History words at the
logical location `y+d`, for `d=-4..4`. For a service Address a, let
`q=a mod5`. An unaligned vote with source centre b is

`vote(H_(r-q)[8+b-S[r]] : r=0..4)`.

Aligned STREAM instead uses centre `b+S[q]`. Unaligned centres are limited
to `[-6,6]`, aligned centres to `[-4,4]`. Thus every selector is in
`[0,16]`. A pending STREAM keeps total length A, start, remaining index
and stride. It rejects `A=0`, `A>Q`, `index>=A`, a span leaving `[0,Q)`,
invalid kind or lane. Its next target is
`start+(A-index-1)*stride`. It travels one site at a time, writes only at
that target, decrements the index, and resumes its return PC after the
last write. Every corrupt typed pending STREAM state is covered by those
same equations; no clean-seeking premise is built into its semantics.

For output holder x and copy offset s, a History word in that vote reads
actual raw cells

`x+s+(r-q)-S[t]`, `t=0..4`.

Here `|s|<=2`, `|r-q|<=4`, `|S[t]|<=2`, so every coordinate is within
`[x-8,x+8]`. This calculation uses the actual holder offsets and raw
History components. It does not replace them by the head centre or
computed geometry. Arbitrary GF/Age/Head values can change q and selectors
but cannot enlarge that set.

Other SF votes and migration need at most radius five. Final-source native
composition reads a source at displacement at most three and its native
radius-five cone, hence at most eight. The guards ensure the source is
queried only in that displacement range. These bounds prove total
radius-eight locality for every state of Sigma.

The retained two cofactors change only the raw cell at -8 or +8 and flip
one actual output Next copy through two changed raw History components.
They certify sharpness for this specified STREAM primitive. They have
canonical native geometry but are local raw-state cofactors, not intact
encoded histories or reliability counterexamples. The finite vote table
checks all 32 input-bit patterns for every valid q/centre/alignment.

## 3. Actual emitted programme — proved universal prepared execution

[compact_passive_emitter.py](compact_passive_emitter.py) emits only generic
instructions above. `emitted_map` is a mathematical comparator; the CPU
never invokes it. The programme computes the following map delta on **all**
seventeen raw upper binary records, including arbitrary old flags, clocks,
mode/PC/Head bits and incoherent SF copies, from the corresponding stable
prepared captured-input matrix:

* the 35 native outputs are the literal native function of the eleven
  raw native words;
* both Workspace outputs are zero;
* every raw SF output copy votes the input field at its logical offset;
  MailL additionally shifts centre by +1 and MailR by -1.

This is a prepared execution statement. Arbitrary upper native words are
not asserted to yield a quiet physical lower period. That separate premise
is discharged only for the family in section 4.

Let `T_g(a)[8+j]` be bit a of the represented raw record `C(g+j)`.
The input loop scans native columns `P+36..P`, extracts lanes 3..13 and
PUSHes eleven bits. Induction on the descending column index gives

`Work = sum(C(g+j).native_bit(k) * 2^(11k+j+5))`,
`k=0..36`, `j=-5..5`.

The loop uses physical Address to choose the next column; it does not keep
uncounted scratch inside Work. NATIVE then gives exactly the promised
35 bits for every possible 407-bit buffer. The output loop writes those
35 bits one by one, and explicitly writes two zero Workspace bits.

Every SF primary group starts at an Address congruent to zero modulo five.
For its copy-q column, aligned STREAM reads

`C(g+S[q]+b-S[r]).field[r]`, `r=0..4`,

where b is 0 for held fields, +1 for MailL, and -1 for MailR. Its five-bit
truth table therefore gives exactly the stated field vote, independently
for every bit and every incoherent input copy. Ten actual STREAMs write
all 3,050 SF columns. No output is read as an input. All 3,087 represented
columns are written once, and no unused column is written.

Control does not branch on any input data. From a fresh head at P, the
native load takes 440 updates; NATIVE one; native-output setup two;
35 output iterations 591; the two zero writes ten; the ten field streams
`4*10+3050=3090`; and HALT one. The exact sum is **4135**.
This count includes opcode issue, pending I/O consumption and every real
one-site move. The head remains in `[P,P+K)`. Thus 4135 is a universal
prepared bound for this actual programme, not a sampled runtime or a bound
for the missing full own programme.

## 4. Exact encoded physical-period theorem — proved restricted family

For any infinite upper configuration C, assume

`C(g).GF=g modQ`, `C(g).Age=theta`, `1<=theta<=Q`, and all old native
Flag1/Flag2/Workspace fields zero. Each SF word in every copy may be any
bit pattern of its declared width, without a copy-coherence premise.

Define global E(C,0) as follows. The lower native fields are canonical GF,
common Age0 and zero native flags/Workspace. Each logical lower Info at
`gQ+a`, `P<=a<P+K`, contains bit `a-P` of `encode_cell(C(g))`; all unused
Info is zero. Its five raw Info copies are the corresponding values at
logical locations `x+S[q]`. Every other lower SF field is zero.

For the immutable issued programme beta, the theorem is

`F_beta^U(E(C,0)) = E(F_beta(C),0)`.

It applies to precisely this native family, not arbitrary upper clocks,
not recursively intact starts, and not a noisy history.

Proof: canonical native geometry and a common legal clock are preserved
whenever Workspace is zero. Before the pulse the Workspace gate is closed.
During the three real gathers, Info is unchanged at represented primaries;
no erase occurs; the speed-one Mail shifts give T at every specified
capture. Last capture is `72Q+2`. Each lower temporal bank thus holds the
same T. Early collection reconstructs the exact upper eleven-word native
input at the new collector 2589. Its native result flags are zero for
canonical GF/common theta/zero old flags, by the printed native equations.
Every courier seed, forwarded value and delivered unused Info at 3/Q-3
is therefore zero. The entire Workspace pulse is zero. This closes the
native induction for the whole lower period; arbitrary represented upper
SF data cannot supply those unused sources.

Reset96Q ends Mail movement and preserves the captured History. Reset112Q
clears the lower Head and Next, then computed-holder service Address
creates one coherent head at P on row112Q+1. During execution the stable
three-bank matrix is precisely T; native flags and wipes remain zero.
The usual five-holder encoding induction follows directly from the
physical coordinates in section 2, migration's unique selected packet,
and the generic CPU equations. Thus the literal rule performs exactly
the programme's 4135 updates. HALT is reached on row `112Q+4136`, before
the last legal execution row. It has 61,399 usable-update slack. All other
logical heads are zero; the halt packet then holds throughout rest.

For the upper state itself, computed Age is `theta+1` in `[2,Q+1]`.
No reset, Info delivery, History capture, early collection/evaluation,
late birth/execution, or Workspace pulse is enabled there. Mail is in
its ordinary first-gather shifting stage. Its native result is canonical,
the flags and wipe are zero, and every other SF holds its five-holder vote.
Consequently `F_beta(C)=delta(C)` for every state in this family. Section 3
therefore writes exactly its represented output word, including all
upper Head bits. This is an equality of raw legal binary records, not
merely of voted critical fields.

At the lower boundary, Info commits OLD Next before private reset. All
represented Next columns contain the written output bits; all unused Next
remained zero. The boundary resets every private field, including History
and Head, and preserves canonical native fields with Age0. Crossing a
colony boundary causes no issue: represented groups are strictly inside
each colony and unused cells are zero. This proves the global infinite-line
equality, without a finite-domain boundary or independently chosen future
bank/command premise.

The checker separately tests all five actual output holders at every one
of the 4,135 retained execution updates, using the literal `total_rule`
and the old Head/Next data. Its Info/History words are derived from C's
same input matrix. The universal proof above, rather than that finite
test, supplies the quantifiers on C and theta.

## 5. First omitted capture — proved prototype own-programme failure

Keep the same rule, code, layout and clock schedule. Take a legal global
upper C with canonical GF, common Age `Q+1`, zero native flags/Workspace,
MailL copies all one, and every other SF word zero. Lower E(C,0) is an
actual global one-level encoding. There are no errors.

The lower gathers, zero-courier/native induction, actual fresh-head
execution and raw boundary argument above still apply. The programme
writes delta(C). But the actual upper computed Age is `Q+2`, the first
off-centre History1 capture. Its +1 lane captures old MailL=1, so every
upper History1 copy is `2^9=512`. Delta instead holds old History1=0.
Exactly relative raw record bits **97..101** differ. The issued five
full-value records and exact execution certify this disagreement.

Thus the issued partial beta fails the full own-simulation identity.
This is its first excluded phase within the stated first-stage interval,
not a claim of globally earliest failure over every upper state. It is an
implementation scope limit. It supplies neither an admissible random-noise
counterexample nor a contradiction to Gray.

## 6. Proof and construction status

| Step | Status |
| --- | --- |
| Declared alphabet, exact K and finite total local rule | **proved** |
| Generic opcode definitions and every malformed-state guard | **proved** |
| All-raw radius-eight bound, actual raw-holder ±8 cofactors | **proved** |
| Counted immutable programme 1058 bits, no dictionary | **proved** |
| Universal prepared delta computation and exact 4135 bound | **proved** |
| Real three gathers/native-zero flags/courier closure/reset/birth/store for section 4 | **proved** |
| Restricted global raw encoded period equality | **proved** |
| Clean own-identity failure at the first excluded capture phase | **proved**, prototype only |
| Complete software stage/active-CPU/final-source emitter | **unproved / not emitted** |
| Existence of a full own beta<=Q and its universal fifth deadline | **unproved** |
| Gray ProgrammeBits/hardwirer/radius-five refinement | **unproved**, explicit departures above |
| Recursive intact hierarchy/noisy real1/higher/iid memory | **unproved** |
| Shorter U or minimum feasible Q/U | **unproved** |

Next full-emitter work is delta plus the actual stage, active-CPU and
final-source corrections. It must handle arbitrary raw PC/mode/movement,
bounded literal decoding, collisions, pending READ/STREAM guards, work
updates and source wipe/commit ordering. The small slice and its fast path
are not evidence that those corrections will fit Q or the fifth window.
There is no architecture-wide impossibility result here.

The standalone manifest pins proof, code, checker, emitted bits, receipts,
logs and native source. Its read-only validator checks before/after hashes
and reproduces all new checks in a temporary directory. Main Gray reports,
frozen older constructions, active rule sources and CURRENT are untouched.
