# GAWN11: SF confinement for late two-offset Address faults

This concerns the **unchanged frozen GAWN2** rule, Q4096/U524288,
radius8/Word100/h1/own beta/lambda24/c104. All previously stated
departures from Gray remain. No rule, ROM, schedule or constant changes.
The native conclusions are [GAWN10's proved projection and exterior](../unregistered_gawn10/GAWN10_TWO_OFFSET_NATIVE_EXTERIOR.md).
This proves the previously missing SF confinement for that exact fault
class. Native Address termination and a positive iid rate remain open.

## 1. Exact theorem

Use exactly GAWN10's hypotheses: actual intact H_2 at T_0=100Q+2,
fixed A=[b,b+w) inside I=[0,Q), 1<=w<=104, fixed nonzero delta modQ,
and0<=D<=103. Arbitrary adaptive after-row overwrites on subsets of A
and rows T_0..T_0+D retain the correct reference Age. Each replacement
Address is either x modQ or(x+delta) modQ. All four flags and all thirteen
SF fields may otherwise be arbitrary legal values. There are no other
errors, including none after t_*=T_0+D. Support geometry alone is not
declared real1. Let Y_t=F^t(H_2) and X_t be the faulty raw rows.

As in GAWN10, put r=(b-3+delta) modQ and

    ell=b-3-r if r<=5, otherwise ell=b-3.
    P=[0,2Q) if ell>=1, otherwise P=[-Q,2Q).

**Theorem.** Throughout the burst and through the current U boundary:

1. All thirteen voted logical SF tracks of X equal Y outside P.
   The full raw SF differences have only the ordinary two-site holder
   halo, hence lie in[P.left-2,P.right+2). Native differences retain
   exactly GAWN10's separate bounds.
2. Both outer logical Head endpoints of P have a zero voted forbidden
   outward movement bit on every row. No malformed packet can bypass
   that shield. Arbitrarily many internal escapes are allowed.

These two assertions do **not** assume native recovery.

Additionally suppose all six native fields are correct globally at
some row t_*<=q<=U-1, after the last allowed overwrite. They remain
correct through U. Then:

3. All SF copies regain coherence on the next ordinary update. The
   actual U boundary is E(dprime,Bprime), with the actual own Programme
   and complete work reset; dprime equals cell_words(F(H_2)) outside
   the two upper indices{0,1} if ell>=1, or the three indices{-1,0,1}
   otherwise. Arbitrary native representation padding is admitted.
4. If ell>=1, X_(2U)=Y_(2U) as complete raw rows, and equality holds
   for all later time. GAWN4's upper adjacent-pair correction and
   GAWN2's normalized period arguments apply to the derived U boundary.
5. If ell<=0, the proved boundary reduction gives

       X_(2U)=E(F(pi(dprime)),0).

   Equality with Y_(2U), and eventual full repair of that upper triple,
   are not proved. Pair correction cannot simply be used for three cells.

GAWN10 supplies one sufficient **conditional** native premise: Address
correct at t_*+a and max(a,Q-b+4)+Q/2<=U-t_*-1. This gives q<=U-1
by its Flag2/Flag1 deadlines. No Address-termination premise is silently
removed. In particular the unconditional SF confinement is not a
complete repair theorem.

## 2. Canonical exterior holders — proved

GAWN10 proves correct clocks everywhere, canonical Address for x<ell
and x>=Q, Flag1 zero outside[-Q,Q), Flag2 zero outside[b-3,Q), and
raw Workspace only in A. Computed Workspace is actually zero; every
computed clock from the first fault through U is above100Q, or0 at U.
Those facts hold despite arbitrary SF, so using them in the SF proof
does not introduce circularity.

For a logical field at y the physical holders are y-S[h], where
S=(0,-2,-1,1,2). A holder outside[ell,Q) has canonical computed and
old self Address. Its service Address is therefore y modQ and its
GF wipe is false. Its computed clock is the correct reference clock.
The true colony endpoints below are far from the Head birth Address1800.

If ell<=0, both endpoints -Q and2Q-1 of P and all their holders
lie outside[ell,Q), since ell>=-8. All holders of logical y outside
P are likewise outside that possible geometry-error interval, even
for y=-Q-1 or2Q.

If ell>=1, at endpoint0 at least the holders at physical -2,-1,0
are canonical. At endpoint2Q-1 every holder is canonical. For any
logical y outside[0,2Q), at least three holders are canonical; at
y=-1 at most its holder at1 can lie in[ell,Q), and further left none
can. A starts at b>=4 when ell>=1, so no endpoint0 holder can be
directly overwritten, and a current overwrite cannot affect three
holders of any logical y outside P. The far right holders are untouched.

Canonical holders are counted physically; incorrect computed Addresses
of the other holders are not treated as legitimate controls.

## 3. Protected Head bits — proved

The total packet case argument of GAWN4 applies at canonical service
Address0 orQ-1. At0, a valid seek/IO target in[0,Q) cannot prescribe
movement2; atQ-1 it cannot prescribe movement1. Invalid target, mode,
movement, instruction or metadata gives ERROR/movement0. HALT, local
instructions and collisions also produce movement0. This covers every
legal packed Word100 value, not just well formed heads.

Let the forbidden bit be movement bit1 at the left endpoint, and bit0
at the right endpoint. A zero in this bit excludes the literal outward
movement even if higher bits or other metadata are arbitrary. Incoming
accepts a neighboring packet only for literal movement1 or2.

Initially the actual clean late Head at each endpoint has that bit0.
If its old logical bitwise vote is0, every canonical holder produces
an output with that bit0: the active branch has the total target guard,
rest preserves the vote, and the U reset produces ZERO. Birth and any
other reset also produce zero there, though there is no birth during
the admitted interval. There are at least three canonical holders at
each outer endpoint by §2. Overwrites cannot corrupt those three.
Thus their three zeros keep the next voted forbidden bit0, regardless
of all remaining raw Head bits and noncanonical holder outputs.
Induction proves both shields on every fault row and subsequent row.
This allows repeated internal packet passages and assumes no native
termination or Head absence inside P.

## 4. All-thirteen-track logical SF confinement — proved

All computed clocks are correct and greater than100Q, until0 at U.
After T_0 there are no Mail transports, History captures, early native
collect/evaluation, courier movements,80Q Info deliveries or births.
The Head is active through127Q and then holds; the actual U update
commits old Out before the work reset. Before U, every non-Head SF
operand is an old vote at the same logical y, plus the immutable beta
and the actual native controls. Head's only neighboring operands are
at y-1,y,y+1; its mem/Out/Scratch operands are local to y.

Initially all logical SF votes outside P are clean, and every current
overwrite preserves that property. Suppose it holds on the old row.
At a logical y outside P, at least three canonical, correctly clocked
holders use the clean operands and the actual clean service Address.
Incoming Head from the edge of P is excluded by §3; the other Head
operands are clean by induction. The clean history also obeys the
same endpoint guard, so deleting that outward candidate preserves
exactly its incoming selection and collision behavior.

Native Flag1 can differ in the left adjacent colony even outside the
two-colony choice of P. With canonical Address its only relevant extra
SF effect is Mail erasure. The actual clean late Mail is already zero
and no transport occurs, so this still gives the clean Mail output.
All other controls at those holders are the clean ones, and wipe is
false. Each of the three canonical holders therefore produces the
entire clean word in all thirteen fields. The other two outputs cannot
alter the bitwise vote, and an allowed overwrite cannot alter those
three clean results. This closes the induction through the U commit
and reset as well as every preceding row.

For a raw physical x outside[P.left-2,P.right+2), all its logical
positions x+S[h] are outside P; x itself is canonical and not directly
overwritten. The same equations give all its clean raw slots. This
proves the stated holder halo, rather than conflating logical and raw
confinement.

## 5. Conditional actual boundary and upper reduction — proved

At a native-correct row t_*<=q<=U-1, GAWN10's closed guards preserve all
native fields through U. On the following update every holder of each
logical position uses the same canonical service Address, correct
clock and zero Flag1, with identical old votes. All thirteen SF fields
become coherent globally, without restricting their contents in P.

At U the literal old-Out Info commit precedes complete work reset.
Head/Mem/Out/Scratch/Mail/couriers/History are zero, Programme equals
actual beta, and lower native fields are canonical/Age0/flags0.
The normalized represented-D encoding argument used in GAWN4/GAWN9
therefore gives E(dprime,Bprime). Exterior logical SF confinement
places the differing frame words only at the upper indices of P.
Auxiliary Info and high native padding need not have been repaired.

For the adjacent-pair case, actual C1=F(H_2) has canonical GF/common
Age1/zero flags and coherent SF. The arbitrary pair pi(dprime) differs
from C1 only at{0,1}. GAWN4 §5's three-correct-copy/native-quorum/h1
argument gives F(pi(dprime))=F(C1). The normalized represented-D
period theorem gives equality of the complete2U raw boundaries, hence
all later rows by determinism. No independently assigned upper state
or extra reset was inserted.

For the triple case the same normalized period theorem gives the exact
displayed2U encoding, but does not give upper triple correction. A
three-site interval can intersect three of five SF holders. Thus the
pair proof's immediate three-clean-input premise fails at that step.
This is a failure of that proof route, not a proved permanent error
or a general impossibility theorem for this rule.

## 6. Verification and status

Finite supplements enumerate the ell choices, check physical holder
counts and protected endpoints, compare selected full-kernel holder
updates with arbitrary SF/noncanonical minority controls, and check
selected exterior updates including harmless external Flag1. They
are transcription checks. No evolving full-SF Address-burst or
complete2U physical simulation is performed, and no finite run proves
the unresolved Address-termination premise.

| Step | Status |
|---|---|
| Native projection/exterior/common clocks/actual closed Workspace | GAWN10's proved argument applies |
| Canonical exterior-holder counts and outer Head-bit shields | proved |
| All-thirteen logical SF confinement, with raw two-site halo | proved without native-recovery premise |
| Correct native row<=U-1 implies actual U represented-D encoding | proved conditionally |
| Adjacent-pair case complete2U/all-later equality | GAWN4 pair correction/GAWN2 normalized period arguments apply conditionally |
| Triple case exact2U encoding reduction | GAWN2 normalized period argument applies conditionally |
| Universal native Address termination for the admitted burst class | unproved |
| Upper triple correction/general complete repair | unproved; immediate pair-quorum premise fails |
| Earlier/arbitrary clocks/multiple offsets/E0-surrounded/higher/iid reliability | unproved |
| Faithful Gray/G17 refutation, shorterU or globally sufficient/minimal fix | unproved |
