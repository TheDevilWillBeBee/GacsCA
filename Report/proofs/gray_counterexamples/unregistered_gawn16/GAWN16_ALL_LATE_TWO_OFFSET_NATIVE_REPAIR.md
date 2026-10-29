# GAWN16: all admitted late two-offset native bursts recover

This is a proof for **unchanged frozen GAWN2**, Q4096/U524288/radius8/
Word100/h1/beta2/lambda24/c104. Every recorded departure from Gray
remains. No transition, ROM, schedule, constant, CURRENT or frozen asset
is changed. This is a restricted deterministic recovery theorem; a
faithful Gray counterexample or a positive iid threshold is not proved.

## 1. Exact theorem and what is still missing

Use exactly GAWN10's actual intact H_2, reference Y_t=F^t(H_2), first
fault T0=100Q+2=409602, fixed A=[b,b+w) subset[0,Q),1<=w<=104,
fixed delta1..Q-1 and allowed fault rows T0..T0+D,0<=D<=103.
Adaptive after-row overwrites may occur on any subsets of these rows
and sites. They retain the correct reference Age; GF is independently
either x modQ or(x+delta)modQ. Every one of the four flags and thirteen
SF fields may otherwise be replaced by arbitrary legal values. There
are no other errors. Write t*=T0+D, r=(b-3+delta)modQ and

    ell=b-3-r if r<=5, otherwise ell=b-3,
    s=Q-delta.

**Theorem.** All six native fields of the faulty history X are correct
globally by t*+11608 and remain correct through the current U boundary.
The actual complete raw U boundary has GAWN11's encoding E(dprime,Bprime).
If ell>=1, X_(2U)=Y_(2U) as complete raw rows and equality holds for
every later tick. If ell<=0, the proved conclusion is instead

    X_(2U)=E(F(pi(dprime)),0),

with dprime differing from the clean upper state only on{-1,0,1}.
Correcting that arbitrary upper triple, and equality at2U or later for
this second case, remain unproved. No native-quiet premise remains in
either actual-U encoding conclusion. No error class is assigned from
rectangle geometry alone.

The theorem covers every stated payload and adaptive fault history.
It does not cover arbitrary clock replacements, multiple GF offsets,
earlier phases, surrounding E0, separated higher errors or iid noise.

## 2. Reused exterior and an exact support cone

GAWN10 applies verbatim. Binary GF voters exist; the clock stays common
and correct; the actual late Workspace guard is closed independently
of evolving SF. GF is canonical outside[ell,Q), Flag1 is zero outside
[-Q,Q), Flag2 is zero outside[b-3,Q). After the last overwrite all raw
Workspace is zero by one update. Its h1 Flag2 front gives, at every
elapsed a>=1, zero Flag2 on

    x < b-3+(a-1),

as well as for x>=Q. This zero prefix never retreats. Globally Flag2
is zero by N2=Q-b+4 and remains zero through U.

One additional universal fact holds even while Flag2 and Workspace
are arbitrary: if GF is canonical for all x>=B on an old row, it is
canonical for all x>=B+3 on the next row. At x>=B+3 the left five
positions include at most two possibly foreign words and all right
words are canonical. Both GF voters are therefore canonical; either
actual selector gives canonical GF. This proves the radius-three
right support bound without assuming native recovery or Flag2 zero.
An overwrite in A cannot exceed this growing right support. Induction
over the D fault updates gives canonical GF on x>=R0 at t*, where

    R0=b+w+3D.

After t* its foreign support has exclusive right bound R0+3a.
This support cone is a proved implication for all histories, not a
measured worst case or a native simulator stopping criterion.

## 3. Ordinary geometry extends to nonpositive ell

GAWN15's positive-ell proof uses positivity only to exclude the other
low-r foreign boundary. Its ordinary canonical-prefix argument applies
unchanged when ell<=0 and r>=6: ell=b-3, its foreign phase r is at
least6, and ell<s. The true phase need not be at least5. For every
target with canonical left GF majority, canonical R gives canonical
GF. Foreign R with phase>=5 has all five left words inside its
apparent colony; at least three canonical ones mismatch, forcing
computed Flag1 and the canonical left selector when Flag2 is zero.

When r>=6 the same two geometric alternatives hold: ell<s with
r=ell+delta>=6, or ell>=s+6 with r=ell-s>=6. If r<=5 and ell>0,
ell=s, already covered by GAWN15. Thus only ell<=0,r<=5 needs a new
crossing argument. Exactly33(b,delta) pairs satisfy it. For each,

    ell=-delta,   3<=b+delta<=8,   1<=delta<=8,   0<=b<=7.

The negative alternative follows by expanding the remainder formula:
b-3+delta is in[0,5], since it is at least -2 and has low nonnegative
remainder only in this interval. Subtracting r gives ell=-delta.
The other low-r alternative would give ell=Q-delta>0.

## 4. Reachable tagged suffix before the foreign right boundary

Consider one of these33 pairs. Its foreign apparent colony is
C=[ell,s)=[-delta,Q-delta). Define tag(x) as canonical GF or raw
Flag1=1. While GF is canonical for x>=s, five tagged right neighbors
of a target x in C imply a next tag. This holds **with arbitrary Flag2
and Workspace**. Canonical R can give foreign GF only by selecting
L with computed Flag1=1. Foreign R has at least three foreign right
witnesses; all are inside C and tagged, hence are eligible old Flag1
ones. Its right Flag1 threshold forces computed Flag1=1 regardless
of Flag2/Workspace. In each case the actual next raw tag is true.

At t*, all x>=R0 are GF-canonical, so the initial tagged suffix of C
starts at R0. It stays tagged and extends one site left per update by
the five-right implication. Put

    T=R0-ell=b+w+3D+delta <=421,
    W=max(T,10-(b+delta)) <=421.

The apparently required right-exterior assumption is established,
rather than assumed during tag propagation. For every 0<=a<=W+2,
the support cone in section2 gives an exclusive right bound at most
R0+3(W+2). Because R0=T-delta,

    s-[R0+3(W+2)] = Q-T-3W-6 >=2406 >0.

Thus GF remains canonical at and beyond s on this entire interval.
Tag induction is valid throughout it; all C is tagged by T and hence
at W and W+1. This is where the104-site/104-row hypotheses enter
essentially. The wider stationary profiles of GAWN12 do not satisfy
this small-support inequality.

At elapsed W, the actual Flag2 zero prefix contains[ell,ell+6):

    b-3+(W-1) >= ell+6

is exactly W>=10-(b+delta). These sites keep Flag2 zero forever.
On the next update, the first three targets ell,ell+1,ell+2 have
canonical left majority, since at least three of their left witnesses
lie below ell. If R is foreign, its three tagged right foreign witnesses
inside C force computed Flag1=1. Local computed Flag2 is zero, so
the left selector is used. If R is canonical, both selectors are
canonical. The prefix reaches ell+3 at W+1. The same reasoning on
the next row reaches ell+6 at W+2, using the actual tags at W+1.
No imposed Flag1/Workspace tape or assumed triple is involved.

The prefix c=ell+6 then persists even after the right support may
eventually leave C. At the first three boundary sites, the first
three right GF words are canonical, so R is canonical. At phases3
and4, foreign R encounters three/four canonical eligible left words
and forces Flag1. At phase5 all five left words are eligible. Local
Flag2 remains zero; below ell GAWN10's exterior protects GF. These
facts preserve every x<c on every subsequent row. Right tags and
the support-cone assumption are no longer required for persistence.

Finally W+2<=423<N2, since b<=7 gives N2>=4093. Thus at the actual
global Flag2 deadline the prefix c=ell+6 already holds, with foreign
phase6 and no conditional boundary-crossing premise.

## 5. Universal GF and native deadline

At elapsed N2 define the effective canonical prefix

    c=ell+6 if ell<=0 and r<=5, otherwise c=ell.

Sections3–4 and GAWN15 justify that prefix for every legal geometry.
If c>=s+6, ordinary prefix advance clears GF in
G=ceil((Q-c)/3) further updates. Otherwise c<=s and its foreign
phase is at least6, unless c=s. It reaches s in
H=ceil((s-c)/3) updates. GAWN15's actual positive-tail tags then
fill[s,Q) in max(1,delta-2), and canonical GF advances through it
in ceil(delta/3). Hence a conservative bound is

    G=ceil((s-c)/3)+max(1,delta-2)+ceil(delta/3).

For the33 small-boundary pairs, H=ceil((Q-6)/3)=1364. The whole
argument stays in the actual late period: the final bound below is
less than the remaining ticks. Once GF clears, GAWN10's Flag1
zero suffix clears both affected true colonies in2048 further ticks.
Native correctness persists through U. The complete bound is

    N=Q-b+4+G+2048.

Exact integer enumeration of all16,773,120 legal(b,delta) pairs gives
max N=11608. A maximizer is b0/delta4095/ell-3/r4092/s1:
N2=4100,H=2,tail-tag time4093,ceil(delta/3)=1365,G=5460.
With D<=103,

    q<=T0+103+11608=421313<T0+4Q=425986<U-1.

The slack before the first-fault4Q limit is4673 updates. This proves
the same-period guard assumption throughout the induction.

GAWN11 now applies to an actual native-correct row for every stated
burst: SF confinement and outer endpoint shields were already
unconditional; next-row coherence and the actual U commit/reset give
E(dprime,Bprime). Its positive-ell pair correction and normalized
period composition give complete2U and all-later equality. For
ell<=0 its same normalized period gives only the displayed upper
triple reduction. There is no proof here that this triple corrects.

## 6. Supplements, provenance and precise status

The checker recomputes all geometry/native bounds, and all356928
small-boundary(b,delta,w,D) support/tag/local-front inequalities.
A C table enumerates actual native cofactors with arbitrary old
Flag2-left/self patterns and two raw Workspace modes at six foreign
boundary positions. It checks the tag implication even before Flag2
clears and the canonical-left implication when computed Flag2 is
zero. Selected literal full-kernel cofactors use arbitrary SF.
These are measured transcription/arithmetic supplements to the
written universal history proof. No evolving full-SF history or
physical2U simulation is performed. The standalone manifest
inherits frozen GAWN15; all earlier proofs and receipts are unchanged.

| Step | Status |
|---|---|
| Native projection/exterior/actual Workspace guard/global and local Flag2 fronts | GAWN10's proved argument applies |
| Three-site GF support cone through arbitrary admitted overwrites | proved |
| Generalized tag with arbitrary Flag2/Workspace | proved |
| All33 small-boundary reachability/local-front crossing and persistence | proved |
| Every stated late burst full native quiet <=11608 | proved |
| Actual U encoding, pair complete2U/all later equality, triple boundary reduction | GAWN11/GAWN4/GAWN2's proved arguments apply |
| Native/full-kernel/support/all-geometry checks | measured transcription/arithmetic supplements |
| Complete correction of arbitrary upper triple/ell<=0 eventual equality | unproved |
| Earlier/general clocks/GF/E0/higher/iid or faithful Gray/G17 failure | unproved |
| Positive iid threshold/minimum sufficient change | unproved |
| Rule/ROM/constants/CURRENT change or commit | none |
