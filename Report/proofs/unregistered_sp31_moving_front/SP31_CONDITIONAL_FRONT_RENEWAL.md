# SP31: conditional front renewal and an actual finite moving core

This is a theorem about unchanged isolated F31, Q1024/U475136/r37,
TF278401. It is not a change to the rule, its ROM or G17. The actual
history corollary uses J225's one native-only, original-c16 dense16Q
real2 fault, arbitrary original upper Info, and no subsequent errors.
It proves a finite lower bound on recovery, not an all-time orbit or
a contradiction to operational higher-error repair or iid memory.

## Exact conditional theorem

Write b(x) for the binary wrong-Address label: raw GF(x) is
(x+512b(x)) modQ. Put a=LQ-512 and b=RQ, where R=L+3. Define S(L,R):

| Field | x<a | a<=x<b-512 | b-512<=x<b | x>=b |
| --- | --- | --- | --- | --- |
| wrong-GF label | free | 1 | 1 | 0 |
| F1 | free | 0 | 1 | 0 |

In this document a free domain contains both0 and1; it does not assert
independence or actual reachability of all choices.

Let B(n,L,R) be a physical work-period boundary with these premises:

1. All raw lower Ages are0, GF is binary adjusted as above and GF/F1
   belong to S(L,R). All other807 non-Info/non-GF/non-Age/non-F1 raw
   bits are0. Every physical Info copy of a primary at phase
   3/509/515/1021 is0. The actual immutable Programme is unchanged.
2. For foreign h=L+1..R, the ten GF primaries
   (h-1)Q+571..580 have five coherent zero Info copies. Other foreign
   represented words need not be known.
3. For every true frame j>=R, its normal native Info words are coherent
   GF=jmodQ, Age=n and F1/F2/WF1/WF2=0. All other Info is unrestricted.
4. No errors occur during the next period. The upper represented Age
   satisfies 0<=n<TF, and 5<=RmodQ<=Q-3=1021.

**Conditional renewal theorem.** After one literal physical period U,
the actual state satisfies B(n+1,L+3,R+3). Premise4's numerical bounds
are required for this transition; they need not hold at its output.
The output also has coherent foreign F1/F2zero in h=L+4..R+3.
No complete upper successor or interior SF/Info characterization is
part of B or the conclusion.

**Actual finite corollary.** For the stated J225 history, every boundary
nU, 4<=n<=293, has definite wrong GF on

    [L_n Q-512, R_n Q),
    L_n=152+3(n-4), R_n=155+3(n-4).

This interval has width3.5Q=3584. From4U to293U it moves867Q to the
right. B(n,L_n,R_n) holds throughout those boundaries, except that the
numerical condition for a *further* transition is not asserted at293.
At293U the endpoints are L293=1019/R293=1022. The next transition is
outside this proof: its third right Flag1 source crosses the upper
colony boundary and is not forced1 by the argument below.

## 1. Exact powerset native front calculation — proved finite certificate

Use J225's exact binary-GF/common-clock factor and J248's powerset
lifting of that factor. Domains0/1/2 mean {0}/{1}/{0,1}; NOT, AND, OR,
MUX and union are their explicit powerset images. Count intervals give
sound threshold domains. At the distant joint refiner each five-site
label vote has a majority; three of the four equal block votes replace
raw GF, while a two-two split retains raw GF. Splitting on the right
GF label before evaluating inside masks/Flag1/Flag2/selector/Workspace
guards includes every concrete branch. These are the unchanged J248
equations, including keep comparing computed GF with **refined** self
GF. Dropping correlations only enlarges domains.

The new C analysis keeps those equations byte-identical to J248, apart
from its exported checker name. It changes the seed and enclosure
boundary, not a transition rule. Initially take S(152,155), F2/WF=0,
and voted M on the four physical aliases as follows:

- At every alias with x<152Q-512, M is free.
- MF509 in colonies152..154 is1.
- MF1021 in colonies155..157 is1.
- MF515 in [152Q-512,155Q) is free.
- All other aliases on the core/right side are0.

Every subsequent voted M is enclosed by old M AND majority5(keep).
This is the actual between-commit Info erasure identity of J225;
commands are seeds of this calculation, not a supplied physical tape.
Section3 proves that actual physical execution supplies them.

The finite window is [80Q,200Q). Its omitted left64 cells are top GF,
F1,F2/Info domains; WF is top during the first2Q active updates and0
after the literal guard closes. Every computed cell has all radius37
native and special Info dependencies inside the window. Actual arbitrary
left continuations are therefore included; no left-side repair is
forced. At the right, the outer128 cells stay canonical/zero in all
6145 rows. This guard is wider than both native radius37 and the
39-site combined holder/native margin. It justifies the zero right
continuation by local induction. The preliminary canonical-exterior
comment in the C refers to this right guard only; the subsequent code
and explicit left-top assignments define the left enclosure.

The exact finite run reaches a native fixed point at update2562:

| Field | Free domain | Definite-one domain | Outside |
| --- | --- | --- | --- |
| wrong GF | x<155Q-512 | [155Q-512,158Q) | 0 |
| F1 | x<155Q-512 | [158Q-512,158Q) | 0 |
| F2 | x<155Q-512 | none | 0 |
| WF1/WF2 | none | none | 0 |

The left domains here extend to -infinity; the finite calculation uses
top at its omitted boundary. All computed positions have the displayed
domains and native equality on the last two updates. Top-left outputs
are automatically included. Right guard outputs are0. Thus the
displayed infinite native domain is a postfixed enclosure for the
closed-Workspace equations, not a finite periodic simulation.
Native equations after elapsed2Q no longer read Info. A separate full
6144-update replay has the same terminal native arrays. Throughout,
all possible wrong GF is strictly left of158Q. Unknown left Info and
the actual command erasures are included in the finite pulse.

Translation by any integer multiple of Q preserves every physical
residue, native equation and alias position. Hence the calculation
proves the corresponding S(L,R)->S(L+3,R+3) enclosure for every
integer L with R=L+3 and the stated generic seed. This calculation
itself requires no upper phase restriction. That restriction is needed
to derive the seed from actual represented native data.

For a quiet prefix, translate the closed-guard postfixed enclosure
back by3Q. S(L,R), with F2zero, is a subset of it. Actual lower clock
is common/legal and binary GF remains closed under refinement and
selection. The five right GF labels have a majority, so native
Flag2's absent-quorum source is false. Old F2/WF2zero yields newF2zero;
the closed time guards yield WFzero. Thus S(L,R) persists, with actual
F2/WFzero, until the source deadline. No SF/instruction input enters
these native equations (private service force is literally0).

The randomized cofactor inclusions are measured supplements. The
universal soundness is the explicit powerset/count/branch induction
above and J248's unchanged algebra; the trajectory and fixed-point
equalities are exact finite computations replayed by the checker.

## 2. Actual reset, fresh execution and captured banks — proved

At B, fresh private work and alias Info are genuine raw zeros. Common
lower Age evolves0..TF. The alias copies remain0 until the update at
current AgeTF-1: only the literal special command write can alter
them before commit, and its clock guard is fixed. That update still
has closed Workspace guards, so state AgeTF has native WFzero.

For true receivers j>=R, work phases58..965, their five holders and
radius37 margins are strictly right of RQ (minimum jQ+19). The
quiet-prefix enclosure gives canonical GF/common clock there. Two
outward distant joint blocks force refined self GF canonical; computed
GF is canonical, so keep1. For complete foreign h=L..R-1, origin
o=(h-1)Q+512 has

    [o+58-39,o+965+39] within [a,b-512),
    [o+1,o+1023] within [a,b-512).

Their entire work/native margins and both courier holder paths have
wrong-GF label1/F1zero and keep1. These are the same translated work
margins as J251's complete foreign frames152..154.

Apply the fresh-frame/guarded-front/typed-pending/Match/own-ROM
induction of J223/J239/J242/J250/J251 to these complete frames. The
changed premises are only the translated hull endpoints and represented
native values. The actual global reset, all work addresses58..965,
clock, guard schedules, total/unique-arrival controls, immutable ROM,
pending type and Match predicates are identical. Unknown Info is
captured as actual binary data. No correctness of an incomplete frame
or a small SF causal cone is assumed. The824 conditional SF/core
identities are used with the actual computed native outputs.

The fixed F1 strip [b-512,b) cuts the unchanged speed-eight Mail paths.
The exact progression crossing test, for every native field bit/source
offset/gather, gives:

- True j>=R receives0 from every source s<R and retains every known
  native source s>=R.
- Complete foreign h=L..R-1 receives0 from every native source s>=R.
  Its GF sources L+1..R were already coherent0 at B, with stable
  label1/no-wipe holders before the deadline. Thus all captured GF
  sources s>=L+1 are0; more-left native fields remain unrestricted.

The healthy tails follow the same route inequalities. The finite route
checks cover the full nonuniform dependency range and every gather;
integer-Q translations preserve them. Three gathered copies of every
known source agree; free captures are an enclosure of actual words,
not independently chosen upper histories.

## 3. Actual source renewal — proved; phase restriction is essential

In a true right receiver's captured table, raw native data is erased0
for s<R and canonical GF/commonAge n/allflags-WF0 for s>=R.
Every valid distant joint block has the canonical GF/Age pair. Erased
GF words adjusted from distinct sources are distinct, so an all-erased
block has no triple. In a mixed block a valid triple can only be the
canonical pair (an erased GF0 at a canonical zero residue, if it
matches at all, still contributes that same pair). For an erased reader,
both negative blocks are erased, so it has at most two valid positive
blocks and retains its raw zero pair. A right canonical reader either
retains or replaces by its canonical pair. Hence refined GF is exactly
the erased/canonical step, including wraps, and the right GF quorum of
every j>=R is canonical.

Put r=RmodQ, 5<=r<=1021. At j=R,R+1,R+2, the literal in-colony left
GF mismatch populations are respectively at least4,4,3. Usually the
first count is5; at r=5 the erased source of canonical residue0 can
coincide. In every case threshold3 forces newF1=1. At j>=R+3 at most
two erased sources lie left and all other Flag1/Workspace sources are0,
so newF1=0. Right GF quorum exists; all old F2/WF2 bits are0, hence
newF2=0 throughout the right. Each side Age vote used at j>=R+3 has
at least three known n entries; coupled fallback cannot introduce a
different clock. GF is canonical and Age successor is n+1 there.
Since n<TF, all computed upper WF guards are closed, independently of
unrestricted represented SF/Info. This proves the native outputs
needed later for right-bank renewal, not a full SF successor.

The8136 exact residue/receiver population cases cover r5..1021 and
offsets0..7. Above offset7 the same erased-population bound applies;
above offset4 no erased left native source remains. Forty-eight full
F31 symbolic cofactors with unrestricted nonnative inputs supplement
the written joint-refinement/native argument. Their chosen Age4 is not
a substitute for quantifying every n<TF.

For complete foreign h=L..R-1, every right native reader
t=h+1..h+5 has raw GF0. Both of its positive distant blocks contain
only captured GF0 sources (their least source is h+9>=L+9). Their
adjusted GF words are distinct, so both blocks are invalid. Three
valid block votes are impossible; raw GF0 is retained regardless of
Age or other fields. The five right adjusted GF words then have no
quorum. The literal absence clause forces newF1=1. Foreign newF2 is
left free. This is J251's three foreign cofactor proof translated;
there is no foreign common-clock or complete native-state assumption.

Actual interpreters and couriers from section2 deliver these flags at
TF. In the core label1, physical MF509 is virtual1021 and receives
the three complete-foreign ones L..R-1; physical MF515 is virtual3
and is free, including partial foreign R. Physical MF3/MF1021 are
ordinary virtual515/509 and stay reset0 there. On the right label0,
MF1021 receives the three true ones R..R+2 and is0 beyond, MF3 is0,
and MF509/MF515 remain ordinary0. To the left all four aliases may be
free. All holders of a fixed primary lie strictly within its stated
label/work side; erasures and incomplete work only enlarge the free
part. This is exactly the generic seed in section1, supplied by actual
physical computation rather than prescribed commands.

At r=1022, j=R+2 has canonical phase0 and no in-colony left mismatches.
Its old flags/Workspace are0 and right geometry is canonical, so its
Flag1 is0. The required three-one source is therefore absent. The
renewal theorem must not be applied there. This is an explicit failure
of this lemma's premise, not a claim about the subsequent dynamics.

## 4. Physical bank renewal and next boundary — proved

Section1 encloses the actual pulse supplied by section3. By elapsed2562
the native state is in S(L+3,R+3), both WFzero and possible F2 confined
strictly left of the new core. The closed guards and postfixed native
enclosure extend it to commit. The common legal clock and binary-GF
closure are preserved. J251's universal common-clock reset clears807
other raw bits plus19 Age bits and clears all alias Info copies at U.
Native F2 becomes0 there. Resetting F2 is a subset of its enclosure,
and GF/F1 remain in S(L+3,R+3).

For true frames j>=R+3, all work/native margins are right of (R+3)Q,
where the pulse enclosure has canonical GF and keep1 at every tick.
Their actual held operands were captured before the pulse in section2.
The same protected actual interpreter continuation of J250 applies
through masked Hold commit; subsequent Mail erasures cannot change
completed captures. Section3 gives coherent normal native outputs
GF=jmodQ/Age=n+1/allflags-WF0. The actual five-holder commit writes
these values at every j>=R+3, proving premise3 for the next boundary.
This protection uses the guarded-front theorem as well as the margins;
it does not assume isolation from arbitrary SF solely by radius.

For new foreign h=L+4..R+3, consider the36 GF/F1/F2 physical primaries
(h-1)Q+571..580/600/601. Initially they are strictly right of old b,
canonical, and their virtual phases are the late opposite phases.
All their Hold fields start0 from the actual reset. The24 literal
own-ROM normal/opposite Hold issue records are exactly J250's frozen
records: normal59..68/88/89 issue and materialize before TF, opposite
571..580/600/601 issue after TF+6144. No such Hold issue occurs during
the pulse. J227's one-kind pending/Match proof, used verbatim in J250,
excludes manufacturing a missing Hold opcode from arbitrary work or
simulated instruction data. Votes/wipes preserve0 during changing GF.

At elapsed2562, every one of these primaries, its five holders and
radius37 margins is strictly inside the new definite label1 core.
Its virtual phase is now the early native phase, whose Hold issue
already passed; the future opposite issue cannot address it. Refined
and computed GF agree and keep1 holds at these margins for the suffix.
Thus its voted Hold remains0. The actual virtual commit mask includes
it and forwards0 to all five physical Info copies. This proves new
foreign GF/F1/F2 coherence and zero values, without proving foreign
Age/Workspace or any incomplete interpreter correct. It excludes old
foreign h=L+3 because that target can have a different early history.

All premises of B(n+1,L+3,R+3), except the separately imposed bounds
for a future transition, now hold. This completes the conditional proof.

## 5. Actual finite induction and limits — proved in its stated scope

J251 supplies actual B's reset, common clock and GF/F1 enclosure at4U;
its smaller left uncertainty is contained in S(152,155). J250 supplies
the coherent foreign GF0 in h153..155 and the canonical/native Age4/
zero-flag right banks j>=155. Thus B(4,152,155) holds for every original
upper Info in the specified history.

For n4..292, R_n runs155..1019 in steps3, hence always satisfies the
phase bound5..1021, and n<TF. Conditional renewal inductively gives
every boundary through293U. The final outgoing r=1022 is excluded,
as proved in section3. No assumption about the unknown left Info,
command correlation or complete upper configuration is added.

The finite moving core does not establish an all-time glider, eventual
recovery failure, operational real2 confinement failure, a Gray/G17
counterexample or any iid noise threshold. Its travel remains within
one upper-colony scale. The upper boundary changes the native masks;
the later state must be analyzed anew. General higher-error repair and
a smallest globally sufficient rule/constant change remain unproved.

| Step | Status | Exact scope |
| --- | --- | --- |
| J223/J225/J227/J239/J242/J248/J250/J251 actual factor/reset/work/courier/Hold contracts | previous proved arguments apply | Explicit translated/native premises above; unchanged ROM/rule |
| Maximal-left powerset seed, right guard and2562 postfixed front | proved finite exact calculation and written soundness | Includes arbitrary left continuation and actual command erasures |
| Quiet prefix, full physical native sources and phase-bound populations | proved | B's canonical/common/zero right native banks; n<TF/r5..1021 |
| Protected true native banks/new foreign GF/F1/F2zeros/common commit | proved | Same guarded-front and pending/Match proofs with explicit margins |
| Conditional one-period B renewal and actual4U..293U core | proved | Same one-fault/no-later-error family, every original upper Info |
| Selected cofactors/random realizations | measured supplements | Not arbitrary-input, phase or physical-history substitutes |
| Next boundary crossing, all-time orbit/eventual repair/arbitrary higher/iid/minimum | unproved | No faithful Gray/G17 theorem or globally sufficient new construction |

Read-only replay:

`python3 Report/proofs/unregistered_sp31_moving_front/check_front_renewal.py`

The separate certificate pins this written physical composition. Historical
exploratory C markers and probe receipts keep their false physical/global
claims; they certify their original analysis scope and are not rewritten.
