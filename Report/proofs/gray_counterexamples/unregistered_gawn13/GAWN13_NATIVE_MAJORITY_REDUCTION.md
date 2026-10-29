# GAWN13: exact native majority transport and the remaining boundary feedback

This uses **unchanged frozen GAWN2**, Q4096/U524288/r8/Word100/h1/
own beta/lambda24/c104, with every previously declared departure from Gray.
It does not change a rule, ROM, constant or G17/CURRENT. It is a reduction
of the still-missing termination argument, not a noise theorem.

## 1. Local identity — proved

Let old Address at y be `(y+delta*z_y) modQ`, z_y in{0,1}, with
one fixed delta in{1,...,Q-1}, and correct common old Age on the
late interval from GAWN10. Suppose old Flag2 and Workspace2 are zero
on the radius-eight neighborhood. Flag1 and Workspace1 may be arbitrary,
and every SF field may be arbitrary. The actual computed Workspace guard
is closed. Both adjusted-Address voters have a majority and the missing
Address source is false, so computed Flag2 is zero.

Put `a=x modQ`, `f=(x+delta) modQ`, and let R and L be the binary
majorities of the five old right and five old left z bits. If

    a>=5 and f>=5,

then the computed Address label at x is **exactly L**. If R=L, both
possible selectors already agree. If R differs from L, its apparent
Address is at least5. All five old left sites are therefore inside
the actual apparent-colony mask, and at least three disagree with
R. This forces computed Flag1=1. Computed Flag2=0 then selects L.
Clock inconsistencies and Workspace1 can only add Flag1 sources and
cannot defeat this argument. No statement about future SF is used.

This is a literal algebraic consequence of the full rule under these
local hypotheses. GAWN10 supplies the hypotheses after the final fault
and its Flag2 deadline. No step is borrowed as a reliability claim
from Gray or Gacs.

## 2. At most fifteen exceptional sites — proved

For GAWN10's exact late fault class, wrong Address is always in
`[ell,Q)`, ell>=-8. After its Flag2 deadline, the identity in section1
holds at every site except

    E = {x in[ell,Q): x modQ<5 or (x+delta) modQ<5}.

There is only one intersecting canonical five-site block, at0,...,4,
and at most two foreign five-site blocks, starting at -delta and
Q-delta. Thus `|E|<=15`; overlapping or clipped blocks reduce the count.
Every other site updates by the exact left five-majority, independently
of Flag1 and SF. The exceptional sites remain coupled to the actual
rightward Flag1 feedback; discarding that feedback is not justified.

In particular, if a raw row has canonical Address for all x<c, both
Workspace fields and Flag2 zero, and every site of `[c-3,c+3)` is
ordinary (outside E), the next row is canonical for all x<c+3.
For x<c-3, both GF majorities are canonical. For c-3<=x<c+3,
at least three of the five left old GF words are canonical, and the
local identity selects that left majority. Right-exterior sites remain
canonical by GAWN10. This gives an exact speed-three clean prefix
through each gap between exceptions; it does not cross an exception.

## 3. Why a GF-only boundary argument is insufficient

Consider a foreign colony boundary s with s>=5 and s+9<Q. Assume
Address is canonical to its left, and retain ten z bits at s,...,s+9.
Workspace/Flag2 are zero. For p=5,...,9 the local identity gives the
left five-majority. For p=0,...,4, call the left/right majorities L/R,
and count canonical old left bits at indices p-j, 1<=j<=p.
The actual next z bit is forced1 when L=1, forced0 when L=0 and either
R=0 or the in-colony mismatch count is at least3, and otherwise may be0 or1
depending on Flag1. This is an **overapproximation**: it allows
independent Flag1 choices on each row without enforcing their actual
evolution. It is not an actual CA error history.

The canonical left prefix is preserved: a new foreign target to the
left of s could only be s-3,s-2,s-1. Its foreign apparent phase is
Q-3,Q-2,Q-1, so all five canonical left words are eligible and force
Flag1=1 and the canonical left selector. Farther left both voters are
canonical. Thus holding that prefix canonical adds no future-error tape.

The induced graph restricted to ten-bit states without three consecutive
foreign bits has504 vertices and831 edges. It contains fourteen nonzero
states in seven two-cycles. One is341/682, with least significant bit
at s: the two alternating checkerboard patterns. Therefore an argument
that this GF-only overapproximation must die without a run of three
foreign bits is false. Neither reachability nor persistence of those
cycles under the actual Flag1 equation is proved. No Gray, G17,
GAWN10 admitted-burst or iid counterexample follows.

The checker retains the complete graph digest and the actual cycles.
Its graph is finite enumeration of the stated overapproximation;
the derivation above establishes why the actual local GF transitions
are included. The graph result blocks this proof shortcut only.

## 4. Sparse native histories — measured only

The exploratory campaign starts from the actual intact H_2 row
T0=409602, with one after-row fault in A=[b,b+w). Address is foreign
at every other site of A, canonical elsewhere. All four native flags
are set to the selected constant bits on A; the actual SF and correct
clock are retained. No later faults occur. The990 selected histories
use b in{0,1,5,64,3992}, w in{9,10,31,64,104}, flags in
{0,1,2,3,8,15}, and the distinct offsets
{1,2,3,8,(Q-b)modQ or Q-1,Q/2,Q-1}. All recovered within the12000
native updates tested. The maximum measured full-native recovery was
2100 updates, and the maximum wrong-GF count was69.

These are actual native projections justified by GAWN10's closed
late guard, not full-SF evolving trajectories or full-period physical
simulations. A rectangle is not assigned an error-class label from
geometry alone. The finite campaign neither proves universal admitted
burst recovery nor contradicts the wider stationary profiles in GAWN12.
The replay recomputes all990 record values and new aggregate trace
digests; the initial source and receipt are retained unchanged.

## 5. Exact remaining obligation

The proof still needs a boundary-crossing/reachability lemma for the
actual coupled GF/Flag1 dynamics, including the transient Flag2 region
after an adaptive104-site/104-row fault. GAWN12 shows that the exterior
invariants alone are too weak. The graph above shows that discarding
Flag1 feedback is also too weak. Section1 reduces ordinary GF evolution
exactly, but supplies neither a universal crossing deadline nor small-
burst exclusion of the stationary profiles. Triple upper-cell correction,
earlier/general Address-clock faults, surrounding E0, higher-error
classes and a positive iid threshold remain unproved.

| Step | Status |
|---|---|
| Correct late clock/two labels/closed projection/Flag2 deadline | GAWN10's proved argument applies |
| Exact ordinary-site left five-majority, arbitrary Flag1/Workspace1/SF | proved |
| At most15 GF exception sites/speed-three clean-prefix advance | proved |
| GF-only graph with504 vertices/831 edges/seven nonzero two-cycles | proved finite overapproximation fact, not an actual CA history |
| Exhaustive native cofactors/selected full-kernel comparisons | measured transcription supplements |
| All990 selected sparse histories recover | measured only |
| Actual boundary crossing/104-by104 universal termination | unproved |
| Actual cycle reachability, faithful Gray/G17/iid failure or noise theorem | unproved |
| Full-SF/full-period physical simulation/new rule or constant change | not performed |
