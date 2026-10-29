# SP31: a conditional right half-line persists to the first upper signal window

This theorem concerns unchanged isolated F31, Q1024/U475136/r37,
TF278401. It uses J255's actual295U boundary, the same J225 native-only
original-c16 real2, every original upper Info and no subsequent errors.
It does not prove arbitrary higher-error repair, full original-data
recovery or an iid threshold. No physical rule, ROM or constant changes.

## Exact predicate and theorem

Age n throughout this document means the legal mixed-clock word
`p.age_code(n)`, not the integer n used as raw bits. The lower common
clock follows the same legal encoding and its fixed increment/reset.

Let R be an integer multiple of Q. Define A(n,R) at a lower physical
work-period boundary by these premises:

1. Raw lower Age is0 everywhere. Raw GF has the binary form
   GF(x)=(x+512b(x))modQ, b(x) in{0,1}; all807 fields other than
   GF/Age/F1/Info are0. Every five physical Info copies of every alias
   primary at phases3/509/515/1021 are0. The actual Programme is F31's.
2. At every x>=RQ, b(x)=0 and raw F1=0. Left raw F1 and left binary
   GF are unrestricted. This is not arbitrary malformed lower-clock
   or arbitrary private-work damage: premise1 is a genuine reset.
3. Every true native bank j>=R has five coherent normal Info copies
   of GF=jmodQ, Age=n and F1/F2/WF1/WF2=0. All other Info is free,
   including every native bank left of R and every SF word on the right.
4. There are no errors during the next period and0<=n<TF.

**Conditional renewal theorem.** Starting with A(n,R), for every row
of this period the entire lower half-line x>=RQ has canonical GF,
the common legal lower clock and F1/F2/WF1/WF2=0. At its next boundary
the actual configuration satisfies A(n+1,R). The numerical bound n<TF
is imposed anew on any further application. No equality of right SF
data with an intact shadow is asserted.

**Actual finite corollary.** J255 gives A(295,1024). Induction therefore
gives A(n,1024) at every integer boundary295<=n<=TF=278401. Canonical
lower GF/common clock and zero native flags/WF hold on x>=1024Q at
every physical row of [295U,TF*U], where TF*U=132,278,337,536.
Left geometry and every unmentioned SF/Info field remain uncontrolled.

**Guard sharpness for this predicate.** Removing n<TF makes the
conditional A renewal false, even on a noiseless complete encoding.
There is a prepared A(TF,0) whose next boundary has a coherent nonzero
upper WF2 bank. This is a legitimate shadow output, not a noise or
reliability counterexample. It proves that this particular zero-WF
predicate cannot be extended to all n with arbitrary right SF/Info.
It does not determine this actual J225 history after the stated horizon.

## 1. Exact joint-word half-line identity — proved

The literal five-word majority returns an existing three-equal whole
word if there is one, otherwise its specified default; its validity
bit is false in the latter case. The joint3/4 block selector replaces
the raw GF/Age pair only if at least three valid block words agree.
These assertions follow directly from majority_word/block_quorum:
three equal words force each bit of the threshold candidate to that
word, and the equality/validity test checks three whole-word matches.
Conversely that test being true supplies precisely such a triple.

Suppose a reader has raw pair a, and its two outward blocks are valid
and equal a. Each of the other two block words and validity bits may
be arbitrary. Any three valid equal words must contain an outward
block and hence equal a. If no triple exists the literal default is a.
Thus the refined pair is a in every case, for every word width and
every unknown inward pair. This is an equality argument, not a sample
of selected Address/Age bit patterns.

On a canonical/common-clock right half-line, the blocks centred+10
and+30 of each reader on that side are entirely known. Adjusting
each GF by its source displacement yields the reader's canonical GF;
their Age words are the common clock. Both five-word quorums are valid
and equal the raw reader pair. The preceding lemma proves that every
refined right pair is canonical/common, including at the edge. No
assumption about the inward block words is necessary. The same proof
works for represented upper native words on j>=R.

The previous free-left full-net cofactor remained symbolic because
the Boolean simplifier did not derive this conditional whole-word
identity. The new adapter substitutes the identity only for readers
on the known right side, after checking both literal outward quorums
in the cofactor construction. It leaves every unknown-side refiner
literal. The physical F31 netlist and immutable programme are unchanged.
Its selected256 two-bit block cases supplement the universal argument.

## 2. Native barrier at an actual colony boundary — proved

Consider a lower right cell, with aliases in its own colony zero.
Section1 makes all right refined GF/Age pairs canonical/common.
Its five right adjusted GF words have a quorum. Since RQ is a true
colony boundary, every left reference accepted by the literal
in-colony mask is also on the known side. Consequently inside-left
GF mismatches are0, the clipped Workspace votes are0, old inside-left
F2 is0, and all right F1 sources are0. The right quiet quorum exists.
The Flag1 inconsistency/right-propagation/self-retention/Workspace/
absent-quiet clauses are therefore all false. NewF1=0. NewF2=0 follows
from old selfF2=0, zero inside-left F2, zero Workspace2 and newF1=0;
the unrestricted outside-left F2 population is multiplied by newF1.

The literal direction predicate

    right_GF_quorum_exists AND (NOT newF1 OR newF2)

is true. GF selects the canonical right GF and Age selects/increments
its common right clock. In particular an unknown left Age quorum
cannot replace that right pair. NewF1 is also0 near a colony end:
the quiet clause is disabled there, and every other source remains0.

Computed WF1/WF2 read only the special Info primaries Q-3 or3 of the
cell's own true colony, behind their right/left-end masks. Their five
copy groups lie within that colony; they cannot read a left-of-RQ
alias. With these groups zero, both WF outputs are0 even when the
lower clock's actual Workspace time guard is enabled. This closes
the local native induction while those actual aliases remain0.

Globally the binary-GF/common-lower-clock factor of J225/J248 applies
to the possibly damaged left side: all adjusted GF have only the two
binary labels and all Age words are common. The five right GF votes
always have a majority, and the side Age vote is common. Thus binary
GF and the common legal successor clock remain closed, irrespective
of native flags/Workspace and private work. This global assertion is
used only with A's common-clock/binary initial premises.

## 3. Fresh actual programme and source closure — proved with previous contracts

Before TF every actual right alias remains0: Info re-voting preserves
its five zero copies; only the literal special write can change these
groups before commit, and that write has the fixed deadline. Ordinary
alias phases509/515 have no special write at canonical GF. This and
section2 keep the entire right native geometry/clock/flags correct
through the actual capture and early evaluation interval.

True frame j>=R has work phases58..965 with five-holder/native margin
39 contained in [jQ+19,jQ+1004], and courier holders [jQ+1,jQ+1023].
These lie strictly inside the right half-line. A route between receiver
j>=R and native source s>=R stays entirely on the canonical/right
side. Its source primaries59..91 have five coherent held values;
keep1 and the fixed gather/capture stages preserve them until commit.
Sources s<R may be wiped, changed or incoherent: their actual captured
native words are treated as arbitrary input words, without imposing
an erased-left or fixed Flag1-strip premise.

The J223/J229/J239/J242/J250/J251 guarded-front, fresh-work, total ROM,
unique-arrival, typed-pending/Match and own-programme induction applies
to these complete right frames. All work and alias private state is
fresh globally, all their virtual Addresses and clocks are correct,
and their work/native margins are protected. Every actual source is
either the known coherent right native word just proved or free actual
data. Correctness of an incomplete left frame is unnecessary. This
uses the guarded-front contracts, not a naive radius bound isolating
the entire SF history. The824 conditional SF/control identities are
used with the actual native outputs; private41-bit headers are not
identified with another rule's history.

In each actual represented native table, every source t>=R is the
canonical/commonAge n/zero old native flags-WF pair, while t<R is free.
Section1 still refines every known right pair identically. RmodQ=0
means every accepted inside-left native reference at each j>=R lies
on this known right side. Apply section2's native clauses one level
up: new GF canonical, Age n+1, F1/F2zero. Since n<TF, both **upper**
Workspace guards are closed independently of every represented SF/
Info/instruction word, so upper WF1/WF2 are0 as well.

The actual early stores and bounded own couriers therefore deliver
zero Flag1/Flag2 commands to the right special groups at the literal
deadline. All their holders are inside the right half-line. Copy/keep
and these zero writes retain the right aliases0 throughout the pulse.
Other left commands cannot enter these special logical groups: they
belong to left colonies; any right writer uses the canonical phase and
the protected right interpreter/courier lineage. Groups509/515 remain
ordinary voted zero Info on the right. Sections2/3 thus close the
induction across the deadline, rather than prescribing a future tape.

The true right native work and keep1 continuation remain protected to
commit. Actual native Hold outputs commit coherently as canonicalGF/
Age n+1/F1-F2-WF0. J251's universal common-clock commit clears807 raw
non-Info/non-GF/non-Age/non-F1 bits, resets19 lower Age bits to0 and
all four alias groups to0 under binary GF. Right raw F1 remains0.
These are exactly A(n+1,R)'s premises. Other Info is not constrained
or silently identified with the original upper state.

## 4. Actual induction and essential upper guard — proved in these scopes

J255's actual295U output supplies all premises of A(295,1024), including
global fresh work/aliases, binary GF, and proper right native banks
canonicalGF/Age295/allflags-WF0. For n295..TF-1, section3 applies and
gives every boundary through TF*U. Its within-period native assertion
gives every physical row between them. This is one conditional family
and its specified actual finite corollary, not all-time noisy repair.

For sharpness, prepare a complete upper raw configuration C with
GF(j)=jmodQ, Age TF, old F1/F2/WF1/WF2zero, all other upper fields0
except a coherent SF Info group at logical primary3 with value1.
Its five holders j=3-slot contain that bit in the corresponding Info
copy; no native word changes. Let the lower boundary be E31(C).
It satisfies A(TF,0): all lower work/reset fields and aliases are0,
and all right represented native banks have the stipulated values.

The unchanged full native output at upper cell0 has canonicalGF0,
Age TF+1/F1-F2-WF1zero and WF2=1. The current upper clock TF opens
the time guard; GF0 opens the left-end guard, Info3 votes1, and F1=0
permits the write. The actual complete-start physical theorem of J223
gives F31^U E31(C)=E31(F31(C)), so the lower normal native WF2 bank
in true frame0 commits1 at primary91 with five coherent copies.
This violates A(TF+1,0)'s zero represented-WF premise. It does not
prove wrong raw lower GF, a fault trajectory or a failed memory bit.
The full unchanged cofactor checks also show that Info3zero at TF,
or Info3one at TF-1, gives WF2zero, isolating the exact guard issue.

| Step | Status | Scope |
| --- | --- | --- |
| Whole-word two-outward-block/default identity | proved | Arbitrary inward pairs and validity; all word widths |
| Native right barrier and represented right output | proved | True colony boundary, right canonical/common native data, stated alias/upper-clock premises |
| Frozen fresh work/guarded-front/own-ROM/copy/courier/commit contracts | previous proved arguments apply | Explicit actual protected margins and reset; SF data may be free |
| Conditional A renewal/actual295U..TF*U native half-line | proved | Same one-fault/no-later-error family, every original upper Info |
| Prepared n=TF failure of the zero-WF predicate | proved | Actual noiseless encoding and legitimate WF2 output, not a noise counterexample |
|256 block cases/86 upper/72 lower/3 guard cofactors | measured supplements | Semantic substitution justified by written identity; selected Ages/phases |
| Actual later dynamics, left/full data repair/arbitrary higher/continuing iid/minimum | unproved | No faithful Gray/G17 theorem or counterexample |

Read-only replay:
`python3 Report/proofs/unregistered_sp31_right_halfline/check_halfline_renewal.py`.
Discovery receipts retain false physical-lift claims; the separate
written proof and final certificate supply the physical scope. The first
checker run incorrectly compared the coded successor word with the
uncoded logical tick at the upper guard. Its source and failure log are
retained; the correction uses age_code and leaves both mathematical
probe receipts unchanged.
