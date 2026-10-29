# SP31: fourth-period native enclosure, exterior protection and failure of strict shrinkage

This concerns the **unchanged isolated F31**, Q=1024, U=475136,
radius37, TF=278401. It is the same actual J225 native-only original-c16
real2 fault from an intact hierarchy, with arbitrary original upper Info
and no later errors. It changes no transition, programme, constants or G17.
The new C program is an analysis of the existing native/Info equations.

## Exact statement

At physical time 3U+TF=1703809, the actual configuration has J239's
binary-GF template T(149,152) and J242's actual21-bit command enclosure.
Write GF(x)=(x+512b(x)) mod1024, where b is the wrong-phase label.
For every original upper Info configuration allowed by that history:

1. During the fourth pulse and the following quiet interval, through
   physical time4U=1900544, every possible wrong GF lies in
   **[142Q+1,155Q)=[145409,158720)**.
2. From pulse update3698 (physical time1707507) through4U the actual
   native state belongs to the following fixed enclosure. Outside its
   displayed intervals, each field is0; native Age is the common legal
   clock, becoming0 at4U.

| Field | Domain {0,1} | Domain {1} |
|---|---|---|
| b, the wrong GF label | [142Q+1,152Q-512) | [152Q-512,155Q) |
| Flag1 | [142Q-2,152Q-512) | [155Q-512,155Q) |
| Flag2 | [142Q,152Q-512) | empty |
| Workspace.Flag1, Workspace.Flag2 | empty | empty |

The enclosure permits correlations; it does not assert that its free bits
can be set independently by a physical history. In particular, it does
not identify the actual fourth endpoint inside the free intervals.

The known wrong-GF interval [152Q-512,155Q) has length3584=3.5Q,
the exact size of the wrong-GF set at3U. Thus **strict shrinkage of the
wrong-Address support in this fourth work period is false for every
history covered here**. This is a restricted geometric result, not a
counterexample to general erosion, remembered-bit reliability or Gray/G17.
A later period could still repair the defect.

## 1. Reduction to native fields and voted Info — previous proved argument applies

[J242's actual source proof](../SP31_FOURTH_SOURCE_ENCLOSURE.md) supplies
the initial pulse state and all21 free commands without a future tape.
[J225's closed-factor argument](../SP31_FIRST_PULSE.md), section2,
supplies the exact subsequent native/Info equations. Private computation,
service and instruction words do not enter the native projection.
The unchanged F31 sets private service force0.

Binary adjusted GF labels and a common legal Age are closed under
the joint distant refinement and both native selectors. Every five-site
GF vote has one of the two label majorities. A joint four-block tie
retains the old binary label. Every chosen Age is the same old legal
clock, so its increment is common and legal. The no-GF-quorum Flag2
source is therefore always false. These are universal properties of the
binary/common-clock alphabet, independent of a sharp-island shape or
the flags.

Until the next commit, voted Info evolves by its actual holder erasures:

    M(y,t+1) = M(y,t) AND majority5(keep(y-slot,t): slot=-2..2).
    keep(x,t) = NOT(newF1(x,t) AND (newGF(x,t) != refinedSelfGF(x,t))).

There is no new Info write during the covered6144 pulse updates.
All later native source reads are disabled until the next TF window.
Thus no assertion about the private fields, Out or committed Info is
needed for the subsequent native-only quiet extension.

## 2. Sound ternary update — proved

Use domains0={0},1={1},2={0,1}. The analysis stores one domain for
each GF label, four native flags and voted Info at each physical site.
This Cartesian enclosure discards correlations only by adding possibilities.
NOT, AND, OR, XOR and the selector MUX are the unions of their Boolean
outputs over the supplied domains. A MUX with an unknown condition unions
its two branch domains. Equal branch domains are retained. These
operations therefore contain every concrete output, even when their
inputs are correlated.

For a population of domains, let l count definite ones and h count
possible ones. A threshold >=k is1 if l>=k,0 if h<k, and2 otherwise.
Every concrete population lies between l and h. Prefix sums in the C
implementation compute these same counts for the literal inside masks.

For each distant five-site block, enclose its majority with this threshold.
For the four resulting votes let l,h again be their population bounds.
Refined GF can be0 if l<=1, or if l<=2<=h and raw self can be0.
It can be1 if h>=3, or if l<=2<=h and raw self can be1. Union these
possibilities. This is exactly a sound enclosure of the rule's three-vote
replacement and two-vote retention; dependencies between blocks only
make the enclosure larger.

Compute the five-refined-GF right and left majority domains RF and LF.
Split the next calculation over every possible right label r in RF.
With that r fixed, p=(x+512r) modQ gives the exact colony masks. Enclose:

- left inside GF mismatches by counting domains for `refinedGF != r`;
- the eight inside old right F1 bits, both populations of old left F2,
  and the inside old Workspace flags by their l,h counts;
- each quiet-right predicate by `(refinedGF == r) AND NOT(oldF1)`.

The frozen equations are then applied with domain operations:

    f = (inside left mismatches >=3)
        OR (inside right F1 >=3)
        OR (oldSelfF1 AND inside right F1 >=2)
        OR (inside WF1 >=3)
        OR (p<Q-5 AND quiet right <3).
    d4 = (inside WF2 >=3).
    on = (inside left F2 >=4) OR (f AND all left F2 >=4) OR d4.
    erase = (NOT f AND inside left F2 <2) OR (f AND all left F2 =0).
    f2 = (d4 OR NOT erase) if oldSelfF2 else on.
    selectedGF = r if (NOT f OR f2) else LF.

For each possible selected GF label, the corresponding physical phase
gives its exact special Info read and end mask. Apply the literal
Workspace time guard and, for WF2, NOT f. Union these branch outputs,
then union over r. Finally enclose the actual keep equation and voted-Info
majority recurrence above. The real r and selected label are among these
branches, so each real next output belongs to the resulting domain.
Induction proves soundness for every command assignment allowed by J242,
and hence every actual original upper Info, without enumerating2^21 masks.

## 3. Finite certificate on the infinite line — proved with exact finite computation

The execution uses physical sites [80Q,200Q), with zero native/Info
exterior. The native radius is37 and special Info reads have radius3.
Before each successful next row, all domains at distance less than128
from either finite edge are0. The program computes every potentially
nonzero output, at distance at least64 from the edge. Since37<64,
no output omitted by that computation can be nonzero. Every reported
row rechecks the larger128-site zero guard. Thus the finite execution
is an infinite-line enclosure; it is not a periodic simulation or a
driven halo. The initially nonzero native/Info sites also lie strictly
inside these guards.

The retained6145 rows, including the initial row, have zero guard
violations. Uncertain GF first appears at update171, where the earlier
exact-GF-only diagnostic stopped; the new analysis retains it instead
of assuming a chosen label. The minimum possible wrong-GF location over
all rows is145409, and the largest exclusive endpoint is158720.
At update3698 the complete five native-domain arrays are byte-for-byte
unchanged by the next native update, with elapsed time already beyond
the2048-update Workspace window. The decoded fixed arrays give exactly
the table in the statement. A separate6144 run and a stop-at-fixed-point
run give the same native endpoint arrays.

The checker replays both full computations, verifies their complete
JSONL traces and binary state, and supplements the written transcription
with1024 exact concrete cofactors, one at every phase, and1024 selected
concrete realizations of128 ternary neighborhoods. These cofactor tests
are **measured supplements**, not the universal soundness argument.
Receipt [ternary_enclosure_certificate.json](../../../figs/robustness/unregistered_sp31_fourth_ternary/ternary_enclosure_certificate.json)
records all source/output hashes and the exact computed bounds.

An initial compilation failed on a missing parenthesis before any CA
execution; its source and compiler log are retained. The subsequent
6144 run completed in27.482175s; the fixed-point discovery in16.287976s.
The earlier source/binary and all logs are retained. The final checker
rebuilds the final analysis source and requires exact equality with both
retained computations. No failed or discarded physical experiment is
being used as proof.

## 4. Quiet native extension and strict-shrink obstruction — proved

After the Workspace guard closes, native GF/F1/F2 equations in this
binary/common-clock alphabet do not depend on the clock or on Info.
The fixed ternary native array is therefore invariant throughout the
remaining quiet part of this work period. Concrete states may change
within its domains; soundness preserves their membership at every step.
The common clock continues to increment legally. At4U its computed Age
is0 and the Workspace guards are still closed. The commit changes SF
and Info, but these do not enter this native update with the guards closed.
Thus the same enclosure holds at4U. It is not asserted beyond the next
TF source opening without a newly derived command supply.

All concrete endpoints contain3584 wrong-GF sites in the definite-one
interval. Starting T(149,152) has exactly3584 such sites. Hence neither
an all-command nor an actual-history strict-shrink claim is available
for this fourth period. Changing only proof bounds or choosing supposedly
favorable command correlations cannot remove this lower bound. A
multi-period repair argument or an explicitly changed rule could still
handle it; neither is proved here.

| Step | Status | Scope |
|---|---|---|
| Actual3U state and fourth21-bit command supply | previous proved argument applies | J239/J242; same physical history |
| Binary/common-clock closure and native/Info reduction | previous proved argument applies | J223/J225; literal F31 interface |
| Ternary-domain soundness | proved | Universal powerset/count induction |
| All6144 pulse rows and3698 native fixed point | proved with exact finite certificate | Guarded computation on Z; cofactor samples measured supplements |
| Native exterior protection through4U | proved | GF hull plus the fixed native table |
| Strict shrinkage of wrong-GF support in the fourth period | refuted for this restricted history | All actual original upper Info; definite3.5Q core |
| Exact free-domain values, full4U encoding/upper successor/data repair | unproved | No SF/Info boundary theorem |
| Fifth-period sources, eventual/general/higher repair, iid rate, smallest sufficient change | unproved | No global reliability conclusion |

Read-only replay:
`python3 Report/proofs/unregistered_sp31_fourth_ternary/check_fourth_ternary.py`.
