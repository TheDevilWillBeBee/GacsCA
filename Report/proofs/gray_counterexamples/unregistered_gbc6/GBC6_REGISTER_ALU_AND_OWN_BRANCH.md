# GBC6: generic register ALU, conditional own branch, rejected full size

This isolated proposal adds two generic instructions to the GBC4/GBC5
binary rule. It is a **rule change**. Q=8192, U=1048576, lambda=24 and
integer c=104 stay fixed; no schedule is shortened. The full folded
listing has **42,716 bits, 3,140 instructions and 384 references outside
Q**, so it cannot be issued as this rule's Q-bit own programme. It is
1,938 bits larger than GBC5's rejected 40,778-bit listing. This is a
failure of this encoding, not a lower bound for other architectures or a
contradiction to Gray's sufficiently-large-Q construction.

The useful result is a total generic operation and an explicit software
implementation of its branch, with a conditional universal semantic and
time contract. The software contract assumes valid execution of the
listed instructions. The complete listing does not meet that premise
inside Q. No full own-emitter, physical-period or reliability theorem is
asserted here.

## Total changed rule and counted resources — proved by definition

The [rule](compact_completion_rule.py) defines F_beta for every declared
raw cell pattern and every fixed beta in {0,1}^8192. The raw alphabet,
407-bit Work, 553-bit Head and 3,087-bit encoded frame remain unchanged;
2K=6174<Q. There is no added register file, dictionary, stack or lookup
table. The instruction decoder reuses previously erroneous EXT/PUSH
markers 21..29. Markers 21..28 encode REG; marker29 encodes REGI. The
ordinary PUSH encoder now permits only widths0..20. CALL30, PUTWORD31,
RETURN and every other branch retain their equations.

For a raw packet p define, for five-bit selector s,

    r(p,s) = (Work(p) >> (20s)) & (2^20-1)       if 0<=s<=20,
             A(p)                             if s=21,
             B(p)                             if s=22,
             0                                if 23<=s<=31.

Writing selector0..20 changes only that existing Work slice, clipped at
bit407. In particular selector20 is a seven-bit destination/source with
zero high bits. Selector21 writes A, selector22 writes B, and selectors
23..31 ignore the destination. All arithmetic is the existing total
Word20 ALU: modular add/subtract/multiply, bit operations, comparisons,
shifts with excessive shifts returning0, and divide/remainder with
zero-divisor returning0. No opcode evaluates a cell rule or CPU callback.

REG(dst,s1,s2,fn) reads both sources from the **old** packet, computes
v=ALU_fn(r(p,s1),r(p,s2)), sets A=v and B=r(p,s2), and writes dst with v.
Thus dst22 replaces B by v. REGI(dst,s,fn,imm) sets A to
ALU_fn(r(p,s),imm), preserves old B, and writes dst; dst22 again replaces
B. They produce no output-tape write. Each takes one native RUN update.
Their total continuation occurs *after* these data effects. A next PC
outside Q leaves those effects and old PC, and sets ERROR/move0.

REG has27 bits: the11-bit EXT/marker prefix, three five-bit selectors
and fn's low bit; the marker gives its three high bits. REGI has a25-bit
header and the inherited unary/little-endian literal of length1+2n,
0<=n<=20. Its length is26..66. Fetch past Q yields0. A missing unary
delimiter or excessive literal is ERROR before data changes. Raw PC is
not required to point to an instruction boundary. The inherited modes,
collision, movement, stream, malformed fields, stage, reset, output and
source equations still define their total outcomes. The added operations
do not change any input coordinate: they use the already voted old Head,
so the declared radius remains8.

## Conditional software branch theorem — proved under explicit premises

Use the exact folded symbolic listing in
[the emitter](register_control_emitter.py) and its ordinary constituent
instructions in [the full source](complete_branch_emitter.py).
Let an arbitrary selected old raw packet have p=1, mode=RUN and move!=3;
every other declared packet bit is arbitrary. Its beta is arbitrary,
including arbitrary raw PC and malformed literal fetch. The following
are **lower execution premises**, not upper data coherence restrictions:

1. A single physical CPU executes the listed software at the stated
   REG/REGI entry with correct opcode/marker dispatch and valid instruction
   fetch/continuations. The wide-listing diagnostic can satisfy this
   premise; the rejected complete Q-bit programme cannot.
2. QCOL=q in0..4, CENTRE=c in{-1,0,1}, VPC/VA/VB contain the selected
   old PC/A/B. The output template contains the old selected packet.
   For REG, VRET contains its decoded marker. REGI fetches its own header.
3. The captured input tape is stable and supplies the exact voted old
   raw Head values; controls, CPU, output and tape suffer no errors or
   wipes during this component. Its CODE primitive reads the same
   stipulated beta used by the upper decoder. An independent host
   evaluator is not supplied.

Then, on reaching cpu_next, the output Head patch is exactly the changed
rule's REG/REGI CPU output. This quantifies over every raw Work/A/B value,
selector, fn, old retained field and beta under these premises. On a
malformed REGI literal it emits exactly fail(p). Every untargeted bit of
the copied packet is retained. This is a branch theorem, not the theorem
that the full software computes F_beta for all raw neighborhoods.

### Actual captured input coordinates

The emitted register reader receives selector s in VSTART. For s<=20 it
sets the physical Fn to c and issues aligned READ-SPAN at

    T = HEAD_BASE + 5*(HEAD_OFFSET.work + 20s) + q,
    w = min(20,407-20s).

HEAD_BASE=2875 and HEAD_OFFSET.work=111. Its successive consumed columns
are T+5i, 0<=i<w. For raw holder r in0..4 the actual column displacement
is r-q in[-4,4], and its History lane is

    8 + c + S[q] - S[r],    S=(0,-2,-1,1,2).

The lane lies in3..13; the logical source displacement from the output
centre is at most5. These are actual raw-holder columns and captured
History lanes, not substituted head-centre accesses. Their last Work
column is at most2875+5*(111+406)+4=5464<Q. The five-holder vote therefore
returns the indicated old Work slice; selector20 returns just seven
bits. Selectors21/22 use the already read old VA/VB, and23..31 return0.
The surrounding native/final-source cone is still the declared radius8;
this helper adds no larger access.

The helper writes only ADDRESS320 and LENGTH340, changes physical A/B/Fn,
and uses return bank1 at Work380. It preserves RAW80, VALUE300, CTRL0,
VRET260, VA200 and VB220. In particular a REGI literal length in RAW80
survives the register read. Old upper Work360/380 are read from the input
tape; they are distinct from these lower CPU's software return words.

### Branch composition and liveness

REG obtains fn from its marker and CODE bit26, and packs its three
selectors from CODE bits11..25. It reads s1 to VALUE300 and s2 to TEMP40;
the second helper preserves VALUE. It invokes the ordinary ALU with
exactly those two values and fn, saves the result, patches output B/A,
then advances VPC by27. REGI obtains dst/src/fn from bits11..24, calls
the literal helper at oldPC+25, saves the immediate in VINDEX280, reads
the source, computes/patches A, and advances VPC by25+RAW. The literal
helper preserves packed VRET and CTRL; the reader preserves RAW/VINDEX.
No operand is reread from the already patched output.

The common destination block clips a Work write to its remaining width,
or patches B for dst22. dst21 needs no second write because A is already
the result; selectors23..31 perform no further patch. Its existing
write_word helper consumes VALUE only after all required A/B patches.
Finally virtual_continue compares the advanced Word20 VPC with Q,
patching PC and RUN/header on success, or just ERROR/header on failure.
The PC+66 arithmetic is at most8257, so Word20 wrap cannot change this
decision. The overflow path retains the data patches, as the raw CPU
does. The literal-error path branches directly to cpu_fail before any
data patch, retaining the copied old A/B/Work/PC.

Register reads return through bank1. Literal parsing and each output
write return through bank0. These calls are sequential, not nested; the
register reader contains neither CALL nor PUSH nor a return-bank write.
Its only two Work destinations are320 and340. The literal helper writes
only280/40/80, and the output helper only300/320/340. Consequently each
live return word survives until its RETURN. The inherited shared header
tails add no CALL or return-word mutation. This discharges the new
RAW80/return liveness directly at these two callers.

### Conditional time bound

[The cost checker](register_branch_cost.py) traverses the *exact folded*
symbolic control graph from each entry through cpu_next, including calls
and every branch alternative. It counts physical RUN updates separately
from vector issues. The only possible loop is the unary literal parser:
VINDEX starts0; every repeat increments it and continues only when the
new value is less than21. Therefore at most21 visits to literal_unary
occur. The checker's pruning of visit22 is justified by this invariant;
it is not an assumed observed iteration maximum. All other paths are
acyclic with finite, intact CALL/RETURN words under the preceding ABI.

Every input/output vector has width at most20, stride5 and valid endpoints
inside the colony. From an arbitrary position inside it, the first
movement/consume takes at most Q updates and each remaining consume at
most5. Charging Q+5*19+1=8288 extra updates per issue is conservative and
also reserves one completion update. These runs do not reset or wipe
the physical CPU under the stated execution premises.

The graph gives REG at most155 RUN updates and7 issues, hence
155+7*8288=**58,171** updates. REGI has at most377 RUN updates and5 issues,
hence377+5*8288=**41,817**. The two maxima can take different branch
paths; summing independent maxima only increases the bound. These bounds
include literal failure and data/PC overflow continuations. They exclude
entry dispatch/metadata/template setup, processing other raw holders,
the rest of the full evaluator, gathers, couriers and the physical
period. They do not prove a complete112Q..120Q deadline.

## Exact folding and the negative whole-program budget

Only label-free old blocks are folded. For Work selectors0..20,
WGET(s2), SWAP, WGET(s1), ALU(fn), WSET(dst) and REG(dst,s1,s2,fn)
have identical final A/B/Work for all raw data; both use the same clipped
Word20 source/destination convention. Their lengths are40 and27 bits.
Likewise WGET(src), ALUI(fn,imm), WSET(dst) and REGI have identical
A/B/Work; their lengths differ by3 bits. This is a *valid-code block*
substitution with labels relocated, not equality of two rules at every
arbitrary raw PC or of intermediate instruction rows.

The complete unfolded new listing is42,942 bits/3,272 instructions with
385 out-of-Q references. Four REG folds save52 bits;58 REGI folds save174
bits. The folded listing is42,716 bits/3,140 instructions with384 invalid
references. The added complete software branch costs2,164 bits relative
to GBC5, while these folds save226; the net cost is1,938 bits. The shallow
generic ALU therefore fails to close the roughly fivefold code excess.
It neither supplies beta<=Q nor rules out a more compact generic machine.

## Evidence, statuses and remaining fidelity gaps

[The direct/diagnostic checker](check_register_component.py) records
116,736 actual-Q-bit opcode cofactors,80 fold boundary supplements,10
end-fetch cases and14 selected complete wide-listing comparisons in
[its receipt](../../../../figs/gray_counterexamples/unregistered_gbc6/GBC6_register_component_attempt01.json).
End-fetch tests allow a truncated tag to decode as another instruction;
they do not assume intended-opcode recovery. Direct opcode cofactors
do not enumerate every Word20 value; the source algebra above supplies
the conditional universal result. The14 full comparisons are measured
only, not a universal full-emitter proof. The diagnostic's extra finite
instruction table and wider physical PC/return are explicit experimental
resources excluded from the candidate's Q-fit accounting.

The exact
[unfolded listing](../../../../figs/gray_counterexamples/unregistered_gbc6/GBC6_complete_unfolded_attempt01.json),
[folded listing](../../../../figs/gray_counterexamples/unregistered_gbc6/GBC6_complete_register_attempt01.json)
and [cost receipt](../../../../figs/gray_counterexamples/unregistered_gbc6/GBC6_register_branch_cost_attempt01.json)
are reproducible. The standalone manifest pins prior accepted GBC5
sources, receipts and successful terminal replay rather than rewriting
their historical status.

[The additional reader checker](check_register_reader.py) actually
issues a small Q-bit CALL/reader/HLT programme, rather than the diagnostic
instruction table. It checks all480 choices of centre{-1,0,1}, holderq
and selector0..31 against real captured columns, and verifies the new
helper's Work-write set and sequential return-bank calls. Its exact code
size, actual input cells, per-case trace hashes and times are in
[the reader receipt](../../../../figs/gray_counterexamples/unregistered_gbc6/GBC6_register_reader_attempt01.json).
This issues the generic read component, not the whole own evaluator.

| Claim | Status |
|---|---|
| Total REG/REGI equation, locality and resource count | proved for this changed rule |
| Generic arithmetic/raw-selector semantics | proved |
| Own REG/REGI branch at specified entry/tape/fetch | proved under stated premises |
| New RAW80 and return-bank liveness | proved under stated entry/fetch |
| Conditional branch bounds58171/41817 | proved under stated execution premises |
| Exact full size and384 invalid references | proved for this encoder |
| Direct opcode and14 complete comparisons | measured only |
| Universal complete emitter/evaluator deadline | unproved |
| Own beta<=Q/final whole construction/physical period | unproved |
| Faithful Gray refinement, admissible repair/noise theorem | unproved |
| Gray counterexample, iid failure or shorter U | unproved |

The h1 healthy-erasure correction, binary state/layout, radius8 and
seventeen gathered lanes, immutable code, service-Address convention,
final computed-source interpretation and the earlier component's staged
protocol choices remain explicit departures from literal Gray. No
adversarial error history is tested by this checkpoint. Matching Q/U/c
cannot remove those gaps. No prior frozen file, main document, CURRENT
or active repository rule was changed.
