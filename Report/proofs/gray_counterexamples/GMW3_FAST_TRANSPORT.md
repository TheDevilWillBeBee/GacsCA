# GMW3: fast radius-five travel, a legal E0 loss, and paired restoration

This isolated branch retains **Q=8192, U=128Q=1048576, lambda=24,
c=104** and GMW2's2007-bit alphabet. It explicitly changes transport;
all GMW1/GMW2 sources and accepted receipts remain unchanged. It inherits
GMW2's h1 native correction, holder-computed GF service convention,
zero Workspace outputs, immutable64K ROM/16-bit PC and preloaded-input
limitations. It is not Gray's velocity-one programme protocol.

The [kernel](gray_moving_word_v3.py),
[builder](build_gray_moving_word_v3.py),
[transport checker](check_gray_moving_word_v3_transport.py),
[transport receipt](../../../figs/gray_counterexamples/GMW3_fast_transport_certificate.json),
[full-emission checker](check_gray_moving_word_v3.py) and
[full-emission receipt](../../../figs/gray_counterexamples/GMW3_full_proposed_certificate.json)
define and distinguish the component, finite experiments and remaining gaps.
The [actual proposed beta](../../../figs/gray_counterexamples/GMW3_full_proposed_beta.bin),
[listing](../../../figs/gray_counterexamples/GMW3_full_proposed_listing.json)
and [86 retained full-field inputs](../../../figs/gray_counterexamples/GMW3_full_proposed_replays.npz)
are not a universal equivalence proof.

## Total changed transition and radius

Let S=(0,-2,-1,1,2). Physical holder x, slot s, represents y=x+s.
For a prospective old head at y+delta, delta in[-3,3], read each of its
five nominal holders y+delta-t, t in S, only if

    |s+delta-t|<=5.

An unavailable holder contributes the zero word. The vote remains the
threshold3 bitwise vote over **five nominal values**, not majority of
the three visible values. This zero padding is a specified all-raw
equation; it does not assume inaccessible state values. At least three
holders are visible for every s/delta. Thus a coherent noiseless word
is recovered exactly even at the far holder of a three-site jump.

At an active output row, self with old movement0/3, left sources at
distances1,2,3 and right sources at distances1,2,3 are tested in that
priority order. Missing heads give0; multiple candidates give the first
packet in stationary ERROR. Movement1 means right,2 means left. On a
fast row an IO-mode packet (SEEK/LOAD/WRITE) requests a stride equal
to min(3,positive distance to start+index). A nonpositive distance,
other mode, or a restoration row requests stride1. A candidate is
accepted exactly when its direction and requested stride reach the
output logical site. Its source service Address is computed from the
output holder's repaired GF plus s+delta, mod Q. Descriptor validation
and the actual one-column/word-instruction head step remain GMW2's
explicit finite equations. Raw invalid packets are therefore defined;
no code/native/head/whole-rule Apply operation is added.

The unpaused variant sets rest_period=0. The GMW3 candidate sets
rest_period=2: odd computed-Age output rows may jump up to3; even
rows move at most1 and use complete five-holder source votes. This
is a **one-site restoration**, an explicitly different alternative to
a stationary pause. It restores redundancy without spending a wholly
stationary tick. Reset/birth, active end120Q, rest, mandatory wipe and
old-Out-to-Info-before-reset order are otherwise unchanged.

**Radius theorem (proved for every raw state).** Every consulted head
holder satisfies the displayed radius5 predicate. Other SF votes use
s-t in[-4,4]. Native/control/wipe inputs have radius5; all source service
Addresses reuse the receiving holder's already computed GF. The code
table introduces no spatial read. Thus the entire defined component
has radius at most5, including all invalid-state and collision cases.
Literal Gray computed-SimBit/Workspace composition is still absent,
because the inherited Workspace outputs are0.

## Exact legal E0 counterexample to unpaused travel

Use the fixed zero ROM, with all65536 bits0. It is a defined parameter
of this component, **not an own programme**. Prepare physical GF=x mod Q,
common Age T=112Q+1=917505, all native flags0, all other SF0, and one
coherent head at a=3093. Its exact packet is

    p=1, move=1, mode=SEEK, pc=0,
    start=3213, width=1, index=0, kind=1, lane=5,
    dst=source=dest=0, all sixteen registers0.

This valid prepared SEEK context is not an intact recursive hierarchy
or a proved result of gathering/evaluation. Until the target is reached,
the packet stays unchanged and requests a right three-site jump.

Apply precisely these shared physical overwrites, retaining native fields
and replacing every head slot at that cell by0:

| Actual physical holder | Absolute output tick | Relative row |
|---:|---:|---:|
|3092|917505|0|
|3093|917505|0|
|3117|917513|8|

Overwrites occur after that row's deterministic update/preparation.
The first two points are an adjacent spatial pair at one tick. The
later singleton is spatially25/24 sites from them; hence the two groups
are (24,24)-separated despite the eight-tick difference. The complete
three-point history is original E0, with no real1 or higher points.
The [receipt](../../../figs/gray_counterexamples/GMW3_fast_transport_certificate.json)
classifies the actual relative support with c104 and retains its absolute
translation; error classes are invariant under this translation. It
does not classify head-center positions in place of holder coordinates.

After the first jump, the three trailing/central holders have the correct
packet and the two leading holders have0. In slot order S, their presence
pattern is(1,0,0,1,1). A further right three-site jump reproduces exactly
that pattern translated by3: the far three-copy vote sees one positive
and two zeros; the adjacent four-copy vote sees two positives and two
zeros; the remaining full votes see three positives. The two absent
copies persist through each further three-site SEEK jump before the
target or stage gate changes, if no restoration or further error occurs.
This is a proved invariant of this unpaused prepared SEEK trajectory,
not five-copy one-step closure.

At relative row8, the reference head is at3117. Its two leading holders
3118/3119 already have0. The singleton erases its center3117, leaving
only two positive copies. At the next jump every source vote is below
threshold3, and all five output head copies are0. With no head, no new
head appears before the next scheduled birth. In the noiseless reference
the head remains present. Exact full-field finite trajectories and
replacement words are retained in the
[witness asset](../../../figs/gray_counterexamples/GMW3_unpaused_E0_transport_witness.npz).
The finite interval margins exceed the entire nine-update radius cone;
the calculation therefore has the stated infinite-line local meaning.

This refutes pure-E0 preservation of the **unpaused changed transport**
from its prepared context. It does not refute Gray's velocity-one
transport, a compiled intact hierarchy, or iid memory reliability. It
rules out simply replacing one-site movement with unpaused three-site
movement while claiming the previous one-tick E0 invariant.

## Why one-site restoration repairs arbitrary payloads

The proof uses every complete-cell replacement value, not merely zero
erasures or valid head packets. It treats the head word and all its
metadata/register bits together. Code is the immutable parameter B.

**Visibility/capacity lemma.** Fix logical output y. Suppose at most two
physical sites have arbitrary SF replacements, and all other input words
are coherently encoded. At least three of its five output slots have
**every** prospective head-source vote exact, simultaneously for all
delta in[-3,3].

To prove it, list visible source holders y+delta-t. A bit0 cannot become1:
at most two erroneous sites supply positive bits, and missing holders
supply0. A bit1 is correct whenever at least three visible holders are
not faulty. Slots s=0 have all five holders for every delta. The only
deficient masks are:

- s=-1, delta=-3: four visible holders with positions[-4,-1] relative y;
- s=-2, delta=-3: three visible holders[-3,-1]; s=-2, delta=-2:
  four visible holders[-3,0];
- their reflected positive-side versions for s=1,2.

A four-holder vote can be wrong only if **both** faulty sites belong to
its displayed interval. A three-holder vote can be wrong if at least
one does. If both faults are on one side, only that side's two partial
slots can fail. If they straddle the two sides, only the two far
three-holder slots can fail; neither inner four-holder slot has two
faults. Fault at0 does not add a third bad slot. Thus at most two output
slots have any incorrect prospective head word. Equivalently, all
possible fault supports intersecting[-5,5] have size at most2; the
67-case mask enumeration in the transport checker exhausts them,
including nonadjacent pairs as a stronger local capacity lemma.
All sites outside this interval are absent from these head votes.

In each of the three good slots, every candidate packet, the candidate
list/collision result and every instruction/IO input are exact. Other
SF input votes are complete five-holder votes, so those inputs are exact
too. All three good slots calculate the same complete reference output
head, Out and Scratch. Mem, Info and ProgramBit are exact in all five
slots unless an optional erroneous head write affects Out/Scratch in
one of the two bad slots. Therefore **each logical SF word has at least
three correct complete output copies** after one fast update. No head
uniqueness assumption, payload-value restriction or valid-mode assumption
is required: arbitrary multiple heads and collision cases are included.
All native fields/control values are repaired under E0 by the inherited
h1/zero-Workspace three-correct-words argument; computed Flag1=0 makes
the mandatory wipe absent even at a faulty raw-GF holder.

**Restoration lemma.** A one-site row reads complete five-holder votes
at all candidate sources y-1,y,y+1. The three correct complete words
from the preceding fast row win every vote. All five output slots then
compute exactly the same reference fields. This repairs arbitrary
partial metadata, absent/false head copies, collision disagreements,
and optional wrong Out/Scratch copies; it is not limited to a presence
bit or the specific erasure witness.

**Original-E0 paired coupling theorem.** Let R_t be a noiseless GMW3
reference with canonical GF, common legal Age, native flags0 and arbitrary
coherent logical SF data. Let X start in R, permitting current isolated
E0 replacements. Allow an infinite history consisting solely of original
E0 groups, with arbitrary complete replacement cells. Then on every
even-Age row X equals R outside that row's fresh error sites. On every
row, the five-copy majority of every logical SF word equals its reference
word. Native geometry/flags agree outside current error sites.

**Proof.** Noiseless coherent copies stay coherent: every clipped vote
has at least three equal correct words, controls are common and every
slot calculates the same logical transition. Native geometry/flags
repair each row independently of SF data, because Workspace outputs
are0. Consider a fast odd output followed by a one-site even output at
physical site x. Its two-update dependency cone has radius10 and
spatial diameter20, over two input/error sections differing by one tick.
Two original E0 groups in this cone would be (24,24)-linked, contrary
to their global isolation. Thus there is at most one group, at most two
sites at one tick. If it occurs before the fast row, the capacity and
restoration lemmas repair it. If it occurs between those rows, the fast
row is locally coherent and the ordinary full-vote one-site row repairs
the new group. After the even update, only fresh errors remain. Reset,
birth and inactive rows already use full votes/defined coherent stores,
so they satisfy the same conclusion without a fast update. Induction
over pairs proves the even-row assertion on the infinite line.

At an odd row a logical word's possible earlier wake comes from an
input group within y+[-5,5]. A fresh overwrite of one of that word's
holders is within y+[-2,2]. Their spatial distance would be at most7
and their temporal distance one, so two distinct original groups cannot
both occur there. Thus either the wake has at most two bad copies, or
there were five good copies before at most two fresh overwrites. In
both cases its majority is correct. This proves the all-row decoder
claim. U is even, so Age wrap preserves the pairing; boundary/reset0
is a full restoration row. The theorem is an **E0-only component
coupling**, not an upper-cell simulation theorem or a positive iid rate.

Longer restoration periods are not proved. In particular lambda24 does
not justify allowing arbitrarily many successive three-site updates:
the exact unpaused history already demonstrates the failure. The receipt
retains204 Boolean transport and5670 opaque control cofactors as finite
checks; the all-payload theorem uses the complete mask/capacity argument.

## Full proposed beta and actual deadline scope

The newly emitted beta is58129 bits/2410 instructions with no out-of-range
references. It remains an explicitly declared64K immutable-ROM candidate,
not Gray's Q-bit ProgrammeBits. Its emitted changes implement seven
candidate sources, computed-Age parity and clipped lane loads. Instruction
fetch and CODE already take one update; all physical operand travel
remains explicit. A
[retained failed emission](../../../figs/gray_counterexamples/GMW3_emission_failure_01.json)
documents our initial missing no-candidate branch. It incorrectly stepped
zero heads; the count0 path now reaches zero_head. Exact sources and
input/output bits are preserved. This was our compiler mistake.

All86 retained full-field comparisons now pass, covering parity, modes,
movement codes, clipped-source distances, dense heads and native/reset
cases. **Universal full-beta equivalence remains unproved.** On the
corresponding own-beta canonical input, uninterrupted halt falls from
GMW2's102026 updates to71354. Dense HLT falls from132803 to98633; tested
dense MI5 takes105980. These are finite timings of the changed emission,
not all-input bounds or successful physical runs after the active gate.

At the usable8Q-1=65535 deadline, the canonical input has **all2007 correct
output bits**, despite its unfinished head. The remaining writes agree
with the initial zeros, so incomplete halt alone is not a decoded failure.
Dense HLT has wrong output fields at that deadline. The separate
[deadline checker](check_gray_moving_word_v3_deadline.py) and
[deadline receipt](../../../figs/gray_counterexamples/GMW3_deadline_certificate.json)
use a normalized zero-SF dense-HLT input and check all five actual physical
holder equations on every one of the65,535 active updates (327,675 cell
transitions). The [prepared trace](../../../figs/gray_counterexamples/GMW3_prepared_deadline_traces.npz)
retains every head/column recurrence. Its expected mode output bit66 is1,
while unfinished Out primary3159 is0. Rest retains0 and Age0 commits0
into all five represented Info holders. This proves a specific wrong
decoded field with an empty error history, rather than inferring failure
from the unfinished head. These prepared contexts are not intact
recursive initial hierarchies. No shorter U or changed active end has
been used.

The normalized cost traces give:

| Prepared fixture | Instructions | Mutable columns | Travel | Total halt |
|---|---:|---:|---:|---:|
| Canonical zero-SF |25151|12425|33778|71354|
| Normalized dense HLT |35787|14581|48265|98633|

Those uninterrupted totals continue the head beyond the actual active
gate. They are finite timing measurements and exact runner recurrences,
not a universal all-input runtime bound or a physical post-gate execution.
Extending an interval needs a new own beta and all gather,
flag/rest/special-write deadlines; finite timing success would still
leave universal beta identity and whole-period composition open.

| Claim | Status | Limit |
|---|---|---|
| Total raw radius5 fast/restoration component | **proved** | Explicit transport/h1/zero-Workspace/immutable-ROM departures. |
| Unpaused current-E0 one-tick five-copy closure | **refuted** | Leading-copy defect persists under repeated three-site travel. |
| Unpaused legal original-E0 loss of all five prepared head copies | **proved** | Two groups/three exact physical overwrites; zero ROM, prepared SEEK context. |
| Alternating fast/full-vote one-site E0 coupling | **proved** | Arbitrary coherent SF data and complete replacements; no head uniqueness restriction. |
| Longer pause spacing or real1/higher recovery | **unproved** | Cannot borrow lambda24 confinement claims unchanged. |
| Proposed full beta identity/storage | **proved fit; universal semantics unproved** |58129bits/2410instructions fit separate64K ROM, exceed Q storage. |
| Finite full-field beta comparisons | **measured only** |86 retained inputs after a retained compiler failure. |
| Canonical output at65535 despite halt71354 | **proved by exact finite recurrence/coupling** | Prepared input only; no halt-based false counterexample. |
| Dense-HLT actual wrong-field boundary commit | **proved by exact finite recurrence/coupling** | Preloaded non-intact context; unchanged128Q stage deadline. |
| Faithful Gray programme/gather/flags/special writes and encoded period | **unproved** | Interface departures and physical initialization gaps remain. |
| Corrected Gray/intact hierarchy/iid memory counterexample | **unproved** | Changed transport failures do not establish that attribution. |

Reproduce the isolated new branch:

```sh
python3 Report/proofs/gray_counterexamples/check_gray_moving_word_v3_transport.py
python3 Report/proofs/gray_counterexamples/check_gray_moving_word_v3.py
python3 Report/proofs/gray_counterexamples/check_gray_moving_word_v3_deadline.py
```
