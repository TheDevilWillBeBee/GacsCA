# GAWN14: exact coupled right-end tails and a conditional boundary pulse

This is an analysis of **unchanged frozen GAWN2**, not a new rule or a
change to G17. Its Q=4096/U=524288/radius8/Word100/h1/beta2/lambda24/c104
and every departure from Gray remain those explicitly recorded in
GAWN2. No claim is made about faithful Gray, G17, general fault recovery,
or a positive iid threshold. All results below require the correct common
late clock, two fixed Address labels, zero Flag2/Workspace flags, and no
further errors. The actual computed Workspace guard is closed by GAWN10;
it is not an imposed future Workspace tape. All SF may evolve arbitrarily
under the actual rule: the native equations are independent of them.

## 1. Closure and exact finite system (proved algebraic reduction)

Choose delta in{1,...,12}, s=Q-delta. At an initial late row write raw
GF(x)=(x+delta*z_x)modQ, z_x in{0,1}. Suppose z_x=0 outside[s,Q),
Flag1(x)=0 for x>=Q, and all old Flag2/Workspace1/Workspace2 are zero.
Flag1 left of s is arbitrary. Age is the correct common late clock and
all SF is retained. This includes a GF/Flag1-only one-row replacement
of the actual intact H_2 row T0=100Q+2 on[s,Q), with no later errors.

The GF prefix x<s is preserved. A right voter could become foreign
there only at s-3,s-2,s-1; its foreign apparent phases Q-3,Q-2,Q-1
include all five canonical left words. At least three mismatch, forcing
computed Flag1=1 and the canonical left selector. Farther left both
voters are canonical. A canonical right exterior x>=Q is preserved:
the right voter is canonical; any foreign left words are outside its
true apparent colony. The right Flag1 quorum and old self Flag1 are
zero, so computed Flag1=0. The other native flags remain zero. This also
proves that Flag1>=Q stays zero. Arbitrary Flag1 left of s cannot affect
the tail: only the old self and right Flag1 words occur in its equation.

Thus the tail is a deterministic finite system with exactly4^delta
states. Pack low delta bits as GF labels g and high delta bits as
Flag1 f. For p=0,...,delta-1, let

    k=min(p,5)
    a=number of g bits at p-k,...,p-1
    b=number of g bits at p+1,...,p+5
    h=number of f bits at p+1,...,p+5
    L=[a>=3], R=[b>=3]
    M=([k-a>=3] if R else [a>=3])
    f'_p=M or [h>=3] or (f_p and [h>=2])
    g'_p=(L if f'_p else R).

Bits at p>=delta are zero; GF bits at p<0 are zero. If R is foreign,
the apparent phase is p, so exactly the k listed left words are inside
the foreign colony and canonical ones mismatch it. If R is canonical,
the true phase s+p is at least5; all five left words are eligible and
exactly a foreign ones mismatch it. Both possible apparent colonies
contain every nonzero right Flag1 witness in the tail, and all right
witnesses outside it are zero. Both GF voters exist; the missing-GF
source is false. Computed Flag2 remains zero, so this is the actual GF
selector. This proves every displayed formula for every raw tail state.

## 2. Exhaustive rank certificate (result supplied by the receipt)

`gawn14_tail_rank.c` enumerates every successor for each delta1..12.
The checker retains the complete successor and distance arrays. If a
nonzero cycle is found, it retains the actual cycle instead of claiming
recovery. If all states reach zero, it verifies for **every** nonzero
state v that rank(v)=1+rank(next(v)), and rank(0)=0, next(0)=0. A finite
rank satisfying these identities is a complete proof of tail absorption
with the displayed maximum rank; it is not a random-history campaign.
Its applicability to the physical native system rests on the separately
proved closure and algebra in section1. This proves only the stated
finite family, not tails of arbitrary length or universal GAWN10 recovery.

The Python checker additionally computes the literal formula separately
and compares it with all successor entries. Frozen GAWN10 native C
cofactors are compared exhaustively for delta1..8 and on explicit
deterministic larger samples. Selected literal full-kernel cofactors use
arbitrary legal SF, arbitrary left Flag1, the correct common late clock,
and the actual native outputs. These comparisons are measured
transcription supplements, not the logical basis of the finite rank
implication. No full-SF trajectory or full-period physical simulation is
performed. A tail GF deadline plus GAWN10's conditional Flag1-erasure
argument yields full native quiet at most Q/2 further ticks later,
provided that deadline lies within the same late work period and the
global Flag1 exterior assumptions of that argument hold.

## 3. Flag1 packet and conditional crossing (proved)

More generally choose delta in{1,...,Q-5}, s=Q-delta>=5. Suppose the
same correct common late clock, zero Flag2/Workspace flags and no later
errors, with canonical GF for x<s and x>=Q, and Flag1=0 for x>=Q.
The prefix and right-exterior argument in section1 still applies.

An old contiguous Flag1 packet [a,b] of ones, s<=a<=b<Q and width>=3,
forces ones in the next row on[max(s,a-3),b-2], whenever this interval
is nonempty. Both possible apparent colonies at a target in[s,Q)
contain all the right witnesses from the old packet. Targets before
the old packet have at least three in their five right positions;
targets within it up to b-2 have old self=1 and at least two to the
right. These are sufficient actual Flag1 clauses independent of GF
and SF. Before clipping at s, the packet's left end moves -3 and its
right end -2. After clipping, its guaranteed right end still moves -2.

If raw Flag1 has three consecutive ones at[a,a+2], with d=a-s>=17
and a+2<Q, put n=ceil(d/3). After n updates the guaranteed computed
packet starts at s and has width d+3-2n>=8. GF uses **this same computed
Flag1**, so the canonical GF prefix has reached s+3 by that row.
At the next update the guaranteed Flag1 packet still covers[s,s+5],
and the canonical GF prefix reaches s+6. These claims also allow an
already farther-advanced canonical prefix.

Once the GF prefix reaches a point c>=s+6, it advances by three each
update without any further Flag1-packet premise. At x<s the preserved
prefix applies. For x=s,s+1,s+2 the right voter is canonical because
its first three witnesses are canonical. At x=s+3,s+4 a foreign right
voter has at least three canonical left witnesses inside its apparent
colony, forcing Flag1 and the canonical left selector. At all x>=s+5
and x<Q, both phases are at least5 and GAWN13's exact left majority
applies. Every x<c+3 has at least three canonical left witnesses. The
right exterior remains canonical. Consequently GF is globally canonical
by at most

    n+1+ceil(max(Q-s-6,0)/3)

updates after the row containing the triple, if this deadline is within
the current late period. GAWN10 supplies its conditional full-native
quiet deadline. Existence or timing of such a triple after every admitted
104-site/104-row adaptive burst is **unproved**. This conditional lemma
does not fill that obligation by assuming its conclusion.

## 4. Status and remaining obligation

| Step | Status |
|---|---|
| Correct common late clock/closed native projection | GAWN10's proved argument applies |
| Canonical GF prefix/right exterior and exact tail formula | proved |
| Full finite-tail absorption or cycle | proved only when its exhaustive certificate verifies the stated outcome |
| Native/full-kernel comparisons | measured transcription supplements |
| Flag1 packet transport and triple-conditioned crossing deadline | proved |
| A sufficient actual triple for every admitted burst | unproved |
| General boundary crossing/104-by104 termination/higher-error induction | unproved |
| Faithful Gray/G17/iid failure, positive noise theorem, sufficient minimum fix | unproved |
| Rule/ROM/constants/CURRENT change or commit | none |
