# GAWN15: tagged Address suffix and universal late adjacent-pair repair

This proves a restricted deterministic theorem for **unchanged frozen
GAWN2**, Q4096/U524288/radius8/Word100/h1/beta2/lambda24/c104. All
departures from Gray remain. No rule, ROM, schedule, constant or CURRENT
is changed. No faithful Gray refutation or positive iid theorem follows.

## 1. Exact statement

Use precisely GAWN10's actual intact H_2, clean history Y, first fault
T0=100Q+2=409602, fixed A=[b,b+w) subset[0,Q), width1..104,
fixed delta1..Q-1 and fault rows T0..T0+D, D<=103. Overwrites on
arbitrary subsets of those rows/sites may be adaptive. They retain
the correct reference Age, replace GF by either x modQ or(x+delta)modQ,
and replace all four flags and all thirteen SF by arbitrary legal values.
There are no other errors. Let t*=T0+D be the last allowed fault row.
As in GAWN10 put

    r=(b-3+delta)modQ
    ell=b-3-r if r<=5, else b-3
    s=Q-delta.

**Theorem.** If ell>=1, all six native fields are correct globally by
t*+11602, and the faulty history X satisfies complete raw equality
X_(2U)=Y_(2U) and X_t=Y_t for every t>=2U.

This includes every stated adaptive mixed burst in the adjacent-pair
geometry, not merely GF/Flag1-only one-row tails. It covers16,756,730
legal(b,delta) pairs. The16,390 remaining pairs with ell<=0 are excluded.
No real-error class is assigned from support geometry alone. Earlier
faults, arbitrary Age replacements, multiple GF offsets, surrounding E0,
upper triple repair and higher-error/iid induction remain unproved.

## 2. Previously proved native projection and deadline

GAWN10 applies verbatim: binary five-voters always exist, the correct
clock stays common, and the actual late Workspace guard is closed
independent of arbitrary evolving SF. GF is canonical outside[ell,Q),
Flag1 is zero outside[-Q,Q), and Flag2 has its stated fixed support.
After t*, computed Workspace is zero by one update; the h1 Flag2
zero front gives all Flag2 zero by

    N2=Q-b+4

updates. They stay zero through U. On every later row the actual
GF selector is L if computed Flag1 is1, otherwise R, where L/R are
the five old left/right binary GF majorities. The missing-GF source
is false. All arguments below start on the actual row t*+N2, and
operate within the same closed late period. No future flag tape is imposed.

## 3. Tagged suffix in the positive foreign-colony tail — proved

For x in[s,Q), define a raw tag

    tag(x)=[GF(x) is canonical] or [raw Flag1(x)=1].

Tag all x>=Q too: their GF is canonical by the native exterior theorem.
Left GF and Flag1 may be arbitrary here. Five tagged old right neighbors
of x imply that x is tagged on the next row. To prove this, if the right
GF voter R is canonical, a foreign computed GF would have to choose L,
and hence computed Flag1=1; in either event the next tag is true.
If R is foreign, at least three right GF witnesses are foreign. Because
each is tagged, each has old Flag1=1. Every foreign right witness lies
in[s,Q), inside the target's foreign apparent colony[s,s+Q). Thus
the actual eligible right Flag1 count is at least three. Computed
Flag1=1 and the next tag again holds. This uses neither an actual
contiguous Flag1 triple nor any assumption about the left GF voter.

At the last three tail sites, intersected with[s,Q), at least three
right GF witnesses lie at or beyond Q and are canonical. Thus R is
canonical and the next tag is true, without any old tag premise.
After one update there is a tagged suffix of length min(delta,3).
A suffix remains tagged and extends one site to the left per update,
by the five-right implication; witnesses beyond Q are tagged too.
Consequently the whole tail is tagged after at most

    T=max(1,delta-2)

updates, and it remains tagged independently of arbitrary left GF.

## 4. Canonical prefix advance and geometry — proved

For a target whose old left GF majority L is canonical, if R is also
canonical, either GF selector is canonical. If R is foreign and its
apparent phase is at least5, all five left words are inside the apparent
colony. At least three canonical left words mismatch R, so computed
Flag1=1 and selects canonical L. **The true apparent phase need not
be at least5** for this implication. Thus a canonical prefix advances
three sites per update across any such foreign-phase gap; GF below ell
is protected separately by GAWN10's invariant.

The geometry gives exactly three cases when ell>=1:

* ell=s; this occurs in the low-r extension case.
* ell<s and r=ell+delta>=6; every x in[ell,s) has foreign phase>=6.
* ell>=s+6 and r=ell-s>=6; every x in[ell,Q) has foreign phase>=6.

Indeed if r<=5, ell is either -delta or Q-delta; positivity forces
ell=s. Otherwise ell=b-3 and r>=6. These observations prove the
classification for every legal b/delta, rather than assuming ell is far
from the true colony boundary.

If ell>=s+6, prefix advance immediately gives global GF correctness
in G=ceil((Q-ell)/3) further updates after the Flag2 deadline.
Otherwise the prefix reaches s in

    H=ceil((s-ell)/3)

updates, with H=0 if ell=s. The canonical GF prefix x<s is then
preserved: a foreign right voter to its left is possible only at
s-3,s-2,s-1, whose foreign phases Q-3,Q-2,Q-1 include five canonical
left words and force the left selector. Farther left both voters
are canonical. This reasoning allows s=1,2,3,4 too.

Wait at most T further updates for the proved whole-tail tags. With
all tail tags and a canonical prefix x<c, c>=s, every x<c+3 has
canonical left majority. If its R is foreign, its at least three foreign
right witnesses are tagged Flag1 ones inside[s,s+Q), so computed
Flag1=1 and selects canonical L. If R is canonical, both selectors
are canonical. Thus the prefix now advances three sites per update
through the tail, without any foreign- or true-phase restriction.
GF is globally canonical in

    G=H+T+ceil(delta/3)

updates after the Flag2 deadline. This additive bound is conservative;
tag growth could proceed concurrently with the first prefix advance.

## 5. Native deadline and complete raw repair — proved composition

GAWN10's common-clock Flag1 erasure applies once GF and Flag2 are
correct. Its rightmost-two-per-update zero front, with Flag1 zero
outside[-Q,Q), clears all remaining Flag1 by Q/2=2048 further
updates. The full native deadline is

    N(b,delta)=Q-b+4+G+2048.

The checker's exact integer enumeration of all16,773,120 geometry
pairs, restricted to ell>=1, gives max N=11602. A maximizer is
b=4/delta4094/ell1/s2/r4095: N2=4096, H=1, T=4092,
ceil(delta/3)=1365, G=5458. In particular

    T0+D+N <=409602+103+11602=421307 <T0+4Q=425986 <U-1.

There are4679 updates of slack before the first-fault4Q deadline.
The bound also proves the same-period assumption used above: the
correct clock never reaches the next open Workspace interval during
these arguments. Correct native fields subsequently persist through U.

GAWN11 applies verbatim to this actual native-correct row: logical SF
confinement to[0,2Q), protected outer movement bits, next-row coherence,
the actual U commit/reset and its encoded adjacent upper-pair boundary.
Its final composition uses GAWN4's universal upper adjacent-pair
correction and GAWN2's normalized period theorem. Hence complete
X_(2U)=Y_(2U); determinism and no later faults give all later equality.
No unproved native-quiet premise remains in this ell>=1 theorem.

## 6. Receipts and exact limits

The C table uses the separately frozen GAWN10 transition and enumerates
the two-label native cofactors at explicitly listed positive-tail
positions. The Python checker checks the five-right tag implication,
the tagged canonical-left implication, every geometry/bound and
selected literal full-kernel cofactors with arbitrary SF. These are
measured transcription/arithmetic supplements to the written universal
proof. No evolving full-SF trajectory or physical2U simulation is run.
The standalone manifest inherits GAWN14 and preserves its frozen arrays.

| Step | Status |
|---|---|
| Correct clocks/native exterior/actual closed Workspace/Flag2 deadline | GAWN10's proved argument applies |
| Five-right tag and suffix-growth/all-tail deadline | proved |
| Prefix advance/three positive-ell geometry cases/global GF bound | proved |
| Full native quiet <=11602 for all stated positive-ell bursts | proved |
| Actual U encoding/adjacent-pair2U/all-later complete equality | GAWN11/GAWN4/GAWN2's proved arguments apply |
| Native/full-kernel/all-geometry comparisons | measured transcription/arithmetic supplements |
| ell<=0 and upper triple correction/general GF-clock/E0/higher-iid | unproved |
| Faithful Gray/G17/iid counterexample or positive threshold/minimum change | unproved |
| Rule/ROM/constants/CURRENT change or commit | none |
