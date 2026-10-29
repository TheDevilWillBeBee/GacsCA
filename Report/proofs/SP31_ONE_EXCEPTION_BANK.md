# SP31: first-boundary GF bank and next repair sources with one free word

This uses frozen F31 of J223 and the actual first history in
[J225's proof](SP31_FIRST_PULSE.md), Q1024/U475136/TF278401.
**No rule, ROM, layout or constant changes occur.** This closes part of
the second-period source gap; it does not prove a second pulse or an eroder.

## Exact statement

Start from the intact encoding and native-only dense16Q row error specified
in J225, with arbitrary initial upper Info and no later physical errors.
Write S=TF+6144=284545. At S J225 proves native T(135,146), with GF
shifted512 on [135Q-512,146Q), its two512-site Flag1 strips, a common
legal clock, and zero native Flag2/Workspace1/Workspace2. This persists
to the first computed boundary U, where807 other private bits reset.

**Theorem.** At U the five Info holders of every primary

    y=jQ+571+k, j134..145, k0..9,

are coherent. For j other than142 they are all zero. At j142 their ten
bits form a single arbitrary word q in [0,1024); no value is asserted.
Consequently at U+TF the actual complete foreign frames h135..145
deliver voted Flag1 command1 to primary (h-1)Q+509. In particular these
eleven MF509 sources, in physical colonies134..144, are all1 for every
q and every original upper Info payload. Other commands and the next
pulse are not characterized.

## 1. Actual stores and pending writes

The checker inspects all81920 own-ROM phase/selector keys at the twenty
possible target phases59..68 and571..580. Each phase has exactly one
Hold store in the actual F31 listing. Its input issue and materialization
ranges are:

| Virtual phases | Input issues | Materialization |
| --- | --- | --- |
| 59..68, GF | 257963..259827 | 257965..259829, before TF |
| 571..580, true H2 | 360587..370671 | 360589..370673, after S |

These are rechecked F31 times; the F30 listing is not substituted. No
Hold store for either possible phase occurs during TF..S. Physical
instruction I always comes from the own ROM. During Match, the matched
I bits retained in registers are simulated upper instruction *data*.
They do not change the physical instruction lookup after Match. Outside
Match the actual clock/arrival selector chooses the own ROM, and during
Match the literal not_match guard forbids Hold/scratch stores. Thus these
timings also apply to the initially partial interpreter, whose data and
register contents may be wrong.

Absence of a raw Hold opcode alone would not exclude a voted pending
Hold: distinct scratch-kind words could vote to zero. Here the actual
one-kind pending argument excludes that possibility. For a primary y,
its five holders are y-slot, slot=-2..2. A pending arrival belonging to y
has virtual address y modQ or (y+512) modQ, since J225 keeps binary
adjusted GF and one common clock at every pulse row. The five comb teeth
differ by multiples of5 of magnitude at most20, never512. At a given
clock at most one of those two addresses can arrive. All present records
for y therefore select the same own-ROM destination kind. Wipes may
remove records, but cannot change their kind. If three records survive,
each voted kind bit equals that kind; otherwise no pending store fires.
The checker covers all5 kinds/all32 presence masks and the actual comb
differences. Pending Hold has target0; scratch has targets1..4. No fresh
pending overwrites are allowed: the original noise retained actual fresh
private state. All earlier pending stores finish before TF.

## 2. The120 surviving bank primaries

For j134..141, primary y=jQ+571+k belongs to the originally complete
foreign frame with origin (j+1)Q-512. J225's actual own-programme prefix
sets its early GF Hold output to0 for all upper Info. Votes and wipes
preserve these zeros through the pulse.

For j143..145, the initial physical phase is true571+k. Hold starts0.
Its sole true H2 store is later than S, so no Hold store precedes the
pulse; during the pulse neither possible virtual phase has a store.
These thirty primaries therefore also have Hold0 at S. Entering a new
true colony on the right has not introduced an unknown GF bank there.

For j142, the original foreign frame h143 was partial. Its early GF
result is not proved. All ten Hold votes are left arbitrary. During
TF..S they are only majority-copied and wiped. No claim is made that
the ten bits share an original data selector or that they are zero.

Every one of the120 targets, its five holders and their radius37 native
refinement neighbourhoods lie strictly inside the new wrong-GF interval:
the nearest primary has59 sites of left clearance, and the rightmost
has444 sites of right clearance. After S all these sites have quiet
foreign GF phase59+k and keep1. Their GF stores have passed; the later
true H2 store cannot address them. Hold votes hence stabilize and remain
constant to commit. This gives110 zero primaries and at most one ten-bit
word q, with its five copies coherent after a quiet voted-hold update.

At input U-1, computed GF equals refined self-GF at all targets. The
actual commit mask includes virtual59..68. J223's807 reset and five
masked-Hold forwarding identities therefore put exactly these votes into
all five Info copies. Thus550 Info bits are0 and50 bits are the five
copies of q. The actual physical aliases3/509/515/1021 are0 by J225.
Nothing is asserted for other Info primaries.

## 3. Actual next gathers

The quiet T(135,146) native lemma applies until next TF; the Workspace
clock guards are closed, native service_force is literally0, and every
Info vote is held with keep1. The correct reset and own-programme
interfaces from J223 apply to each complete foreign working footprint
[hQ-512+1,hQ-512+1023], h135..145, which is wholly unflagged and within
the homogeneous wrong-GF region.

For raw upper offset d, virtual GF bit k reads physical primary

    (h+d-1)Q+571+k.

If it lies in the wrong-GF interval, it is one of the120 bank targets.
It is0 except when h+d=143, in which case it is bit k of q. The latter
route lies wholly between the strips. Some zero sources within the
right strip are additionally erased, which preserves their value. If the
source is outside, its speed-eight voted-Mail route crosses one of the
two512-site Flag1 strips and is erased, irrespective of outside data.
The checker tests all21450 routes, including330 direct reads and all
three actual gathers, using their arithmetic progression and actual
capture clocks. The crossing predicate is the same for all ten GF bits;
the exception is consequently a word at one raw upper coordinate, not
ten unrelated moving exceptions. For a complete frame h, the captured
raw GF pattern is all0 except possibly q at offset ell=143-h. Other raw
fields, including Age and all four flags, remain free in this argument.

## 4. Universal native response to a single GF exception

Consider any five consecutive positions whose raw GF values are zero
apart from at most one arbitrary value. Adjustment to a receiving
coordinate adds minus each displacement modulo1024. The four unchanged
values are distinct. The exceptional value can coincide with at most
one of them, so no adjusted GF value occurs three times. This holds for
every q, independently of every raw Age value.

In each of the four distant five-cell refinement blocks, this precludes
a whole GF/Age3/5 quorum. All four validity bits are0, so the literal
joint3/4 refinement falls back to the receiving cell's raw GF/Age pair.
This applies at every refined offset-5..5. In the subsequent native
right and left five-cell GF votes, the same counting argument excludes
both quorums. Native Flag1 includes the absence of the right quorum,
so it is1. Both GF votes fall back to raw self-GF; the native selector
therefore returns that GF regardless of Flag2, Age or private fields.

This is a universal word-counting proof. The checker additionally
enumerates all5 exception placements/all1024 words for the vote
primitive, then evaluates the actual maintenance cofactors for all11
ell values -2..8/all1024 q, leaving raw Age and flags free. A further
176 actual full-F31 cofactors leave every non-GF raw input and I free;
these selected full-net checks supplement the written refinement proof.
Thus each complete frame's actual early own programme produces Flag1=1
and GF equal to q if h143, otherwise0. The own listing, fresh-work
execution, fivefold pending/copy/scratch controls, total own ROM and
early-courier deadlines are the already certified physical induction
from J223, applied to these captured inputs. The actual right courier
from virtual965 to1021 delivers1 by next TF, at physical(h-1)Q+509.
No future Hold, command or Workspace tape is independently prescribed.
This proves the stated theorem for the same actual J225 fault. QED.

## Limits

The single exceptional word is specific to this first boundary. A later
partial interpreter could create another exception; two exceptions can
produce a3/5 GF quorum. No one-exception induction is claimed. Next
Flag2 commands, true/partial Flag1 commands, Age/H2 banks and the complete
next signal remain unproved. This lemma supplies no second pulse outcome,
arbitrary higher-error repair, continuous-E0 repair, iid threshold, Gray
refutation or smallest globally sufficient change.

The initial checker incorrectly required every in-bank route to avoid a
strip, including the already-zero right-strip sources. That assertion
failed. Its source and failure log are retained in figs; the corrected
checker requires survival only for the exceptional q routes and counts
the additional zero erasures. No failed execution is called a rule fault.

| Step | Status | Scope |
| --- | --- | --- |
| Actual first pulse/native boundary and resets | prior proved argument applies | J225 specified history/all upper Info |
| Twenty-phase own-ROM/pending store exclusion | proved | Binary GF/common clock/fresh actual pending |
| First-boundary110 zero primaries/one coherent free GF word | proved | Same actual history; no complete upper reconstruction |
| Next actual gathers and one-exception GF/Flag1 response | proved | All q/all other captured fields free |
|176 selected full-net cofactors | measured only | Supplement universal word-counting/source proof |
| Eleven actual next foreign MF509 commands | proved | Own programme and courier composition |
| Complete next signal/pulse/repeated banks/general eroder/iid | unproved | No global theorem or minimum rule change |
