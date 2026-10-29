# GBD6: a total rule family, two-field software and its budget failure

GBD6 defines every local field equation for an isolated finite rule family
at Q=8192, U=128Q=1,048,576, λ=24 and integer c=104. It does **not** supply a
complete own programme. Its specified native-plus-Mailbox/History listing
already occupies12653 bits (h1) or12708 bits (printed Flag2), before ten
remaining output fields are emitted. This rejects this append-only encoder
at Q; it is not an architectural lower bound, a refutation of Gray or a
noise counterexample. No active construction was changed.

## Exact objects and quantifiers

[full_rule_family.py](full_rule_family.py) defines a total autonomous local
map Rβ on the unchanged3387-bit binary alphabet for each fixed immutable
bit string β of length at most Q. A field is always interpreted at its
declared binary width. Every bit pattern of this alphabet is included;
there is no exclusion of invalid Heads, incoherent backup slots or unusual
native clocks. The choice between the printed Flag2 equation and h1 is an
explicit fixed parameter. The transition has radius at most7, within the
declared radius8 proposal budget.

The software result is narrower. Let17 raw upper records be stored in a
coherent lower Mem340 bank with the unchanged packed input layout. Native
GF and Age may be any of their13/20-bit values; all upper SF backup slots
may be arbitrary. Let the lower execution row have canonical GF, one
common legal clock, no wipes, an untouched input bank, the unique initial
Head and the correct native-result ABI: R3=newGF, R4=newAge, and actual
scratch Out word2596=newFlag1. Native results here are those of the same
raw upper neighbourhood. The standalone6043-bit component then writes
exactly the five Mailbox copies and all five copies of each of the three
History banks required by Rβ at upper centre0. It halts within15064 updates.
These are prepared execution premises, not supplied rule ports. The
component is not a complete own programme, and the ABI is not autonomous
for this standalone execution.

A separate clean chronological lemma composes the **native-only** programme
with the accepted GBD5 actual three gathers, packing and birth, and with
the new couriers. From any actual global E(C,A) row0, without errors, its
native Flag1/Flag2 outputs reach the two special Info sources before80Q.
C ranges over all3387-bit records and A over arbitrary unused lower Info.
This does not assert self-simulation of Rβ. The fixed programme used in
that lemma calculates four native fields, not Rβ's entire alphabet.

## Total physical rule and order

The fields remain native37 bits plus five backup slots of
Info1/Mailbox4/History51/Mem340/InputTag14/Out20/OutputTag14/Scratch20/
Couriers2/Head204. K3387, P2403,170 chunks and all Head204 bits are counted.
Each Head has eight Word20 registers, one13-bit return link and the
unchanged explicitly specified finite instruction decoder. There is no
dictionary, descriptor array, hidden call stack, upper-rule opcode or
native-evaluation opcode. Immutable β lookup is a declared departure from
mutable ProgrammeBits; its existence does not prove that an own β fits.

Each update first computes the actual native quorum/flag outputs from OLD
native fields, including OLD Workspace. Only these **centre** computed
controls are consumed by the SF equations. For role q the logical address
is `(newGF+S[q]) mod Q`; its logical time is the centre's selected
pre-increment clock. Every data read is from OLD raw backup slots with
their actual inverse role. Thus no neighbouring computed field is read.

The entire following schedule is part of the rule, not an external driver:

| Branch | Actual action |
|---|---|
| Three gathers | Starts0,32Q,64Q; reset, next-action load, then speed1 shifts for16Q; computed Flag1 erases Mailbox |
| History | Three17-lane banks; reset before the bank's captures; self capture start+1, nonzero lane capture start+2+abs(d)Q |
| Input packing | Actual temporal majority of OLD History; unchanged seed/merge/load and tagged left transport |
| Early Head | Birth593065; active on593065<t<80Q; actual old Head/Out interpreter equations |
| Early flag couriers | Seed action78Q at P+1 from OLD voted Out bits13/14; clamped forward/hold to Q−3 and3 |
| Source Info | During78Q<t<98Q the special primaries read OLD courier bits |
| Workspace | Half-open96Q<=t<98Q; reads FINAL computed self Info after all branches and wipe |
| Late Head | Reset Out at112Q; birth112Q+1; execution112Q+1<t<120Q |
| Output transport | Load action120Q, tagged right transport through986257 |
| Expansion | Seed Scratch at986258;19 within-chunk left spreads; then hold |
| Commit | Action U−1 writes normal Info from OLD Scratch and resets every other SF field |

All other actions and malformed cases are defined in the source. Tagged
packet collisions yield zero; invalid tags clear. Invalid CPU instructions
and movement targets use the frozen total Head equation. Courier forwarding
is zero outside the seed-to-destination interval; hold is confined to its
destination. Info outside normal primaries is zero at commit.

The wipe in this proposal zeroes SF whenever computed GF differs from raw
self GF. Gray p33 prints an additional computed-Flag1 condition. This
unconditional wipe is an explicit stronger-wipe departure, inherited from
GBD5, not a faithful transcription on arbitrary raw states. It vanishes
on the clean native trajectory used here.

Workspace consumes the final self-role Info after that wipe, commit or
source update. Therefore the source function is specified without changing
“computed SimBit” into a pre-wipe intermediate. The source still uses only
the centre computed-native controls. Its support is their radius5 unioned
with self-role old SF sources, not a second computed-native neighbourhood.

Native reads have radius5. A logical old backup vote has radius2; role
offsets add at most2, and one-site gather/packet/courier forwarding adds1,
giving5. Actual Head movement reads offsets S[q]+d+S[h], with d=−1,0,1,
giving radius5, as the accepted separate GBD4 erratum establishes. Literal
READ/READQ and balanced WRITE have radius7. Controls are unioned with
these source sets. This proves radius at most7 on every raw state, not
merely the clean run. The checker supplements this derivation with source
access traces; the traces are not the universal locality proof.

## Emitted Mailbox and History theorem

[controller_emitter.py](controller_emitter.py) keeps the frozen native
listing and changes its4-bit HALT to a26-bit jump into the new BODY. It
does not truncate any target or issue an invalid concatenated β. BODY
loops over q=0..4 and g=0..2. It reads actual raw upper-copy majorities with
FGET and writes each actual output slot with FPUT. These generic helpers
have the accepted literal raw-coordinate implementation; a logical upper
vote is distinct from the physical lower five-copy vote.

Let θ be the selected pre-increment native clock. R4−1 modulo2^20 recovers
θ exactly. BODY compares R3 with actual raw upper self GF via RAW and saves
the Boolean keep. Neither operand is silently projected outside its
declared width. The helper targets remain within the Head travel frame.

For Mailbox the emitted branches are precisely: old voted value masked to
two bits; stage starts reset; the next action loads Info into both streams;
remaining active actions read left bit0 and right bit1; rest holds. New
Flag1, !keep or θ=U−1 forces zero. FPUT writes all five actual4-bit slots.

For each History bank g, stage-start resets apply only when that stage is
no later than g. Offset1 replaces bit8 by the old Info vote. A nonzero
offset2+kQ with1<=k<=8 replaces bits8−k and8+k by OLD Mailbox bits0/1.
Otherwise the old17-bit word holds. !keep or commit erases. Stage and
offset arithmetic uses ordinary Word20 operations, and bank g uses the
literal raw offset `HistoryBase+85g`. There is no History or native opcode.
This is exhaustive for all θ in0..U−1.

**ABI/liveness.** R6 is q and R7 is g. The frozen native RAM helpers clobber
those registers and therefore are not reused in BODY. The new counted
BLOAD/BSTORE preserve R1/R3/R4/R6/R7 and use R2/R5 as temporaries. FGET
clobbers R0/R3/R5 and preserves R1/R2/R4/R6/R7; FPUT clobbers R2/R3/R5 and
preserves R0/R1/R4/R6/R7. Hence k and the right bit index are saved in real
Out RAM before helper calls. No helper makes a nested CALL; one return link
suffices. The exact13 scratch words are2589..2601 inclusive: the old native
words, NOW at2597, KEEP at2599, k at2600 and right index at2601. Their
positions are beyond the170 packed output words and do not collide with
represented output bits. They are existing physical Out fields, not new
cell bits or a hidden memory bank.

These branch identities and helper contracts prove the two-field output
theorem. Fourteen literal controller replays with arbitrary upper SF
include a GF-wipe case and a missing-GF-quorum case; they supplement, rather
than replace, the universal compositional argument.

**Universal cost.** Upper SF values affect arithmetic and writes but no
branch or move target. All variable control depends on θ, newFlag1 and
keep. [component_cost.py](component_cost.py) partitions all1,048,576 θ
values into47 exact predicate-path classes, retaining the phase-zero
fallthrough even when its final functional result is “hold.” Four Boolean
Flag1/keep combinations give188 complete controls. All primitive CALLs,
returns, variable READ field travel, q/g loops and actual one-site motion
are included. The maximum is15064 updates. The fourteen physical replays
match their zero-SF cost factor exactly. This is a universal cost for the
issued6043-bit component only, not for an unissued overflowing programme
or the whole Rβ rule.

## Counted rejection and conditional output transport

| Listing | Native prefix | Added controller | Total | Out-of-Q targets |
|---|---:|---:|---:|---:|
| h1 |7051|5602|12653|65|
| Printed Flag2 |7106|5602|12708|68|

The added5602 bits are22 for the replacement jump,5107 for BODY,140 for
FGET,137 for FPUT,100 for BLOAD and96 for BSTORE. Standalone BODY plus its
real463-bit RAW helper occupies6043 bits/336 instructions. The rejected
concatenated listings contain719/722 instructions. Every target and its
full value is retained. Their β is explicitly absent: issuing a13-bit
truncated address would describe another incorrect programme.

Info, Mem, InputTag, Out, OutputTag, Scratch, Couriers, Head, WF1 and WF2
still require own software. Even a complete body for those fields would
not remove the existing4461/4516-bit excess. This is a precise failure of
the specified encoder and append-only strategy, not a proof that no
compact interpreter or other finite-state construction fits Q.

For the separately specified output shipment, assume canonical/common
lower native controls through commit and completed packed Out words at
120Q. Chunk h starts at P+h. After e right-forward steps it is at
`min(source(h),P+h+e)`. Adjacent positions cannot collide: both the initial
and terminal sequences are strictly increasing, and taking the minimum of
the corresponding strictly increasing sequences preserves their order.
The explicit terminal collision rule is therefore inactive in this clean
case. All chunks arrive by3217 steps. Expansion seeds each right endpoint,
then19 within-chunk OR steps copy its word over its own20 sites (seven for
the final chunk). At commit every normal Info bit is its corresponding
word bit, all five physical roles agree, and all other SF is zero. The
checker replays824063 literal packet-site updates and16955 commit roles.
The completed-Out and quiet-control premises remain **unproved for a
complete own programme**. This is not an E-to-E period theorem.

## Actual early source lemma and timing correction

Use the fixed native-only7051-bit h1 programme and actual global E(C,A),
with no errors. Before78Q the new local rule has the same native, gather,
packing, Head and Out equations as the accepted GBD5 clean prefix.
Couriers are zero. The new source writes have not begun. All extra later
branches are inactive. Thus GBD5 derives the actual three captured banks,
packing and birth without a prepared tape or independently chosen upper
state. Every native calculation halts by627003.

The 75Q=614400 seed is **not justified** by that universal bound. Selected
native halts at610614 do not establish universal75Q readiness. The earlier
GBD6 draft instead seeded at80Q, which misses the printed source deadline
after positive-distance forwarding. Those drafts and receipts are retained.
This version explicitly seeds at78Q=638976, after the universal halt by
11973 ticks. No shorter U is claimed.

At this action old packed word1 contains new upper Flag1 and Flag2 at
bits13 and14, as the native output layout proves. Birth generated the
actual Head; the native software, not a supplied command, wrote those
bits. All copies agree by the clean physical factor. The right and left
distances from P+1=2404 are5785 and2401. Seed action t creates raw courier
row t+1; the endpoint sees it after d advances, and Info reads the OLD
courier one update later. Therefore the correct source raw rows are
644763 and641379. Both precede80Q=655360, with right-deadline slack10597.

The two forwarding intervals are [2404,Q−3] and[3,2404]. They have zero
gaps between colonies; no incoming neighbour command can enter a terminal
hold. Pure forwarding moves the seed at speed1, then the terminal OR holds
the same bit. Every other source bit stays zero. Once the source Info is
written it holds until the pulse window. The last gather capture already
wrote row72Q+3, so these unused source writes cannot change any consumed
History. Before96Q the Workspace guard is closed even if the delivered
upper flags are positive. Native flags remain0 and GF/clock remain correct.
These observations prove actual held source Info through raw96Q.

The checker enumerates all64 two-bit command triples in three adjacent
colonies using the literal clamped equation and checks all five raw roles
at seed, source arrival and hold. These are component/cofactor checks;
they are not a fabricated full-state replay with assigned future Out.
The **actual** source provenance is the preceding native-programme
composition. No whole own-rule or noisy early evaluation is inferred.
The printed native programme has the separately retained7106-bit listing;
its clean lower-zero-flag closure and33937 bound allow the same composition,
without claiming that printed positive-Flag2 repair works.

## Primary-paper comparison and remaining obligations

Gray's programme discussion is on printed pp30–32
([local text](../../../../papers_txt/gray_readers_guide.txt), lines1365–1425).
His promise is for **sufficiently large** Q and an actual own interpreter,
hardwirer and programme; the displayed lower bound8192 does not guarantee
that this particular7051/12653-bit encoder fits. The printed SF/stage
protocol is on pp33–35, text lines1480–1590.

| Step | Status in GBD6 | Paper/refinement scope |
|---|---|---|
| Total Rβ field equations, all raw states | Proved | Isolated new rule family; not an own β |
| Native/GF/Age/Flag1 calculation | Frozen GBD4 argument applies | Printed/h1 Flag2 choices remain distinct |
| Actual clean three captures and input packing | Frozen GBD5 argument applies |17 lanes rather than Gray's five-neighbour gather |
| Mailbox-on-Flag1 erasure | Proved | Literal erasure present; noisy banks not proved |
| Final computed self Info to Workspace order | Proved | Centre-control convention and stronger wipe are changes |
| Mailbox/History own software and15064 bound | Proved under prepared lower/ABI premises | Two fields only; no full own evaluator |
| Native-only actual early flag delivery before80Q | Proved by composition |78Q seed is a declared timing choice |
| Tagged output scatter/commit | Proved conditionally | Completed Out/quiet native premises not discharged |
| Complete β<=8192 | Unproved; specified encoder rejected | Remaining ten software fields absent |
| Complete late deadline | Unproved | Usable112Q+1<t<120Q gives65534 execution updates; not a full runtime bound |
| Gray rest refinement | Unproved/changed | Output forwarding after120Q explicitly continues into rest |
| Mutable ProgrammeBits/hardwirer/final self identity | Unproved/absent | Immutable β is a material departure |
| Noisy recovery/original error classes/higher hierarchy | Unproved | λ24/c104 retained as baseline, no error history tested here |
| Faithful Gray counterexample or iid reliability theorem | Unproved | None asserted |

The next fit strategy must replace the5107-bit duplicated/control BODY
with a genuinely shared, counted whole-rule computation scheme and emit
the ten remaining fields, rather than append further unissued software.
It must prove actual helper/register liveness, literal raw data access,
all malformed CPU/controller branches, full code identity and a complete
late execution bound. A wider frame, primitive or altered schedule would
be a new declared rule choice and would require fresh physical proofs.

## Receipts and reproduction

[check_component.py](check_component.py) emits the rejected listings, issued
component, literal runs and mathematical receipt.
[validate_gbd6.py](validate_gbd6.py) checks every pinned source/dependency,
recomputes every new result in a temporary directory and compares exact
artifacts. [REPRODUCE.md](REPRODUCE.md) gives the read-only command.
Inherited GBD5 sources and accepted terminal replay receipts are pinned;
they are reused by exact-hash provenance, not silently re-proved from
selected executions. Attempts01–03 retain the original80Q courier draft;
attempt02 also retains the insufficiently fine cost path partition. No
old accepted source or active rule was edited.
