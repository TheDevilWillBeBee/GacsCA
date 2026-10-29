# SP31: consistent extreme witnesses inside the fourth bank enclosure

This is an algebraic obstruction for the **enlarged captured-bank
table** in [J242](SP31_FOURTH_SOURCE_ENCLOSURE.md). It is not a
physical history, initial-upper-Info witness or noise counterexample.
F31, Q1024/U475136/r37, and G17 remain unchanged.

## Exact statement — proved for the captured-table abstraction

One shared assignment of J242's free native bank words makes all19
complete optional fourth Flag2 commands1. Another shared assignment
makes all19 commands0. The two remaining partial commands are free
in the enclosure; no correct partial interpreter is asserted for them.
Consequently both extreme21-bit command masks used in J241 are
consistent with the proved bank **bounds plus native output equations**.
Neither mask is thereby proved reachable in the actual J225 history.

The native output fragment excludes private SF/instruction inputs by
J223. Those remaining inputs are free in the full-function cofactors;
no physical state or future external command is supplied to a run.

## Shared all-one assignment

Choose a=0 and q134=q141=q149=0. In the true-left table set every
free Age to the single legal word15, every free old F2 bit to1, the
partial141 F1 bit to1 and every free Workspace bit to0. Retain all
known entries, including recovered true142..147 F1/F2=0 and canonical
Age3 through132. In the foreign table set every free Age149..151
to15, its free old F2 at149 to1 and every free Workspace bit to0.
The free foreign F1 bits can be1. Repeated reads use the same bank
word; these assignments respect every erasure and known zero in J242.

J242's joint-refinement identity applies. NewF1=1 in every complete
receiver under discussion. The literal native clauses use

    source3 = (no right GF quorum) AND (selected left Age mod16 =15),
    on = (inside left F2 population >=4)
         OR (newF1 AND all-left F2 population >=4)
         OR source3 OR source4,
    erase = (NOT newF1 AND inside left F2 population <=1)
            OR (newF1 AND all-left F2 population =0).

For true j132..141, raw selfF2=1 and at least one of the five old left
F2 bits is1. Thus erase is false and the self1 is retained. At142/143
raw selfF2=0, but respectively five/four old left F2 bits are1; on
is true. At144..147 raw selfF2=0 and the five left Ages are all15.
No right GF quorum exists. The nonzero modal left-Age fallback selects
15 even without a left GF quorum, so source3 turns F2 on. This proves
all sixteen true optional outputs132..147 are1.

For foreign h149..151 no native GF quorum exists. The five left
captured Ages contain respectively five/four/three erased zeroes;
their majority is0. The literal modal fallback declines a zero Age
vote when the left GF quorum is absent and retains raw selfAge15.
Thus source3 is true in all three foreign receivers and newF2=1.
No protected foreign clock premise is used or claimed.

## Shared all-zero assignment

Keep the same zero GF exceptions and set every free Age, flag and
Workspace bit0. The proper known Age3 words and fixed F1 ones are
retained. Old self/left F2 and Workspace2 are0 everywhere. Selected
left Ages are3 or0, never low-four-ones. Source3/source4 and both
F2 creation populations are therefore false, giving all19 outputs0.

## Consequence and exact limit

These are single consistent assignments to the bank abstraction,
not19 independent cofactor inputs chosen after output calculation.
The literal full F31 functions give these outputs with all other
SF/instruction inputs unrestricted. Thirty-eight symbolic full-rule
cofactors supplement the written clause argument and are read-only
replayed by the checker.

J241's nonshrinking quotient corner measurements therefore cannot
be excluded solely by native equations applied to J242's bank bounds.
The remaining constraint must come from **actual physical bank/partial
history**, a reachability/correlation theorem, or a repair argument
that handles the cases. No actual fourth endpoint or smallest globally
sufficient change is inferred. All-time hierarchy and positive iid
reliability remain unproved.

| Step | Status | Scope |
|---|---|---|
| Fourth actual enclosure/native refinement/dependency separation | previous proved argument applies | J223/J242 unchanged F31 |
| Shared all-one/all-zero complete source witnesses | proved | Enlarged captured-table abstraction and literal clauses |
| Thirty-eight full-rule cofactors | measured supplements | Other SF/instruction inputs symbolic |
| Physical bank/initial-upper-Info reachability, partial outputs | unproved | No actual trajectory supplied |
| Actual fourth endpoint/general repair/higher/iid/minimum | unproved | No operational or Gray/G17 failure claim |
