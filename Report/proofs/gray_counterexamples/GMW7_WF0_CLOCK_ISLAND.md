# GMW7's fixed-zero Workspace native rule has a permanent clock island

This is an obstruction to the **explicitly changed GMW7 rule**, at
Q=8192, U=128Q=1048576, lambda=24, c=104. It is not a counterexample
to Gray's construction, Gács, active G17, Address memory or iid reliability.
In particular Gray's Proposition5 is stated for Address; Address remains
correct in this witness. The omitted simulated-flag repair matters to any
proposed *native clock eroder* proof for GMW7.

Sources: [actual total F7](gray_token_gather_v7.py), its actual
[native calculation](gray_moving_word_v2.py),
[finite quotient/event checker](check_gray_token_gather_v7_clock_island.py),
[read-only validator](validate_gray_token_gather_v7_clock_island.py),
[root intact initializer proof](../GMW7_INTACT_HIERARCHY.md),
[root initializer implementation](../check_gmw7_intact_hierarchy.py).
Receipts: [certificate](../../../figs/gray_counterexamples/GMW7_WF0_clock_island_certificate.json),
[all transient event counts](../../../figs/gray_counterexamples/GMW7_WF0_clock_island_transients.json),
[exact finite error support](../../../figs/gray_counterexamples/GMW7_WF0_clock_island_errors.npz).
No existing rule, programme or accepted artifact is changed by this audit.

## Exact intact-context statement

Let X be the intact infinite-line GMW7 initializer in the root proof:
GF(x)=xmodQ, Age0, all native flags0, every non-Info logical SF value0,
and Info slots A(x+s), s in S=(0,-2,-1,1,2). Its recursion is

    A(gQ+4001)=gmodQ,
    A(gQ+4177+i)=A(g+S[i]), i=0..4,
    A(y)=0 at other residues.

Euclidean quotient/remainder is used on all integers. This has a unique
legal solution by strict decrease of absolute coordinate, and X belongs
to E7(X) simultaneously at every level. The root proof certifies this;
the current witness does not replace it with a local prepared state.

At physical tick0 replace only Age with1 on the half-open interval
[0,17Q)=[0,139264). Every other field, including GF, flags and *all*
18500 SF bits, is left at its value in X. There are no later errors.
This is one shared physical error history; there are no independently
chosen upper-level error sets. The support asset stores every altered
site/tick, and the legal payload recipe is `replace(initial_cell(x),age=1)`.

**Theorem.** After t noiseless updates, for every integer x,

    GF(x,t)=xmodQ;
    Age(x,t)=(t+1_[0,17Q)(x))modU;
    Flag1(x,t)=1 iff x is in [-h_t,0) or [17Q-h_t,17Q),
        h_t=min(3t,Q);
    Flag2(x,t)=Workspace.Flag1(x,t)=Workspace.Flag2(x,t)=0.

This statement concerns the actual full F7 transition, for the actual
intact-start SF values and their unrestricted subsequent evolution.
It also holds for arbitrary legal initial/private SF values. The whole
native prefix is independent of them while Workspace outputs remain
identically0. No assumption about those fields' later gathering or head
execution is required.

At t=2731 both preceding colonies [-Q,0) and [16Q,17Q) have Flag1=1
throughout. Thereafter the native projection is exactly periodic with
period U and zero spatial translation. The clock defect is stationary,
not travelling. More generally the same proof works for every nonzero
clock offset delta modulo U, replacing1 by delta; the retained error
payload and numerical cofactors use delta1.

## Exact native factor (proved)

With canonical GF, every adjusted left/right GF vote equals xmodQ and
exists, irrespective of flags and ages. Thus GF stays canonical. Write
the two possible old Ages as (t+e_j)modU, e_j in{0,1}. They are distinct
at every t, including wrap. Five binary inputs always have a whole-word
majority, and equality of their Ages is exactly equality of their labels.
Let R and L be the3/5 majorities of labels at j=1..5 and -5..-1.

Initially Flag2=0. Its missing-GF source is false because the GF vote
exists; its Workspace source is false because Workspace2=0. No left
Flag2 input is1. Its off-to-on predicate is therefore false, so Flag2
stays0 forever, independently of Flag1. Workspace outputs remain0 by
the actual F7 definition.

For a=xmodQ the native equations consequently reduce to

    mismatch = count{j=-5..-1: 0<=a+j<Q and e_j!=R};
    rightflags = count{j=1..5: 0<=a+j<Q and oldFlag1_j=1};
    newFlag1 = [mismatch>=3 or rightflags>=3
                or (oldFlag1_0 and rightflags>=2)];
    newLabel = L if newFlag1 else R.

Incrementing the selected Age gives (t+1+newLabel)modU. No self-Age
fallback is used, since both binary five-votes exist. These equations
are a derivation from `scalar_native`, not a separately assumed native
operator.

The finite inside vectors have eleven classes: a=0..4, one interior
representative5, and a=Q-5..Q-1. The checker verifies the representative
inside vectors for **all8192 Addresses**. For every class it enumerates
all2048 label masks, all attainable rightFlag1 counts and both old self
Flag1 values:208896 direct actual-scalar cofactors. F1 positions outside
the right in-colony set and negative F1 positions are unread by these
equations; permutations within the set affect only its count. Thus the
count representatives cover every F1 payload.22528 further cofactors
check every label mask at wrap clock U-1. Extension to all20-bit t is
the equality/modular-increment argument above. Arbitrary SF values do
not occur in either the scalar equations or F7's constant-zero Workspace
outputs.

## Aligned steps and all transient flags (proved)

The two clock jumps are b=0 and b=17Q, both colony boundaries. Neighbour
majorities L and R differ only at x=b-3..b+2. At x=b-3..b-1, R is the
right-side label, L the left-side label, and all five left neighbours
are in the preceding colony with the left-side label. The mismatch count
is5, so Flag1 is forced1 and the left vote preserves the correct local
label. At x=b..b+2, the in-colony left neighbours, if any, have the
right-side label; their count is at most2. The mismatch source is absent.
Those sites lie in the *following* colony, where Flag1 remains0 as shown
next, so the right vote preserves their local label. Away from these
six-site sets, L and R equal the local label; either vote preserves it.

Every age-mismatch Flag1 source is therefore in the last three sites of
the preceding colony. The right-front/self-support predicates read only
F1 within the site's own colony. Starting from Flag1=0, no other colony
can acquire Flag1: it has no source, no old selfFlag1 and no right in-colony
flags. In particular the following colonies [0,Q) and [17Q,18Q) always
have Flag1=0, justifying the near-jump vote selection above at every tick.

In each preceding colony, the forced last three sites form the initial
tail. If a contiguous tail has length h, a zero cell exactly three sites
left of it sees three1s in its five right neighbours; one four sites left
sees only two and has no self-support. The tail's old sites keep at least
three right1s except near the colony's right boundary, where the persistent
mismatch source keeps them on. No other site switches on. The tail
therefore advances exactly three sites left per update, stopping at its
colony's left boundary. Induction gives h_t=min(3t,Q). Saturation occurs
at ceil(8192/3)=2731, after which the same equations preserve the entire
preceding colony. This proves both clock preservation and the exact F1
formula through all transients and for all later times.

The event checker exhausts rows t=0..2731, including a transition of the
saturated state. For each row it partitions the integer line at old
Age/F1 boundaries shifted by j=-5..5 and colony boundaries shifted by
those j. Between consecutive cuts every old neighbour label/flag and
every in-colony Boolean test is constant. Consequently a sample at the
left endpoint is the exact update for the whole segment. Expected next
boundaries are among those cuts. Exterior infinite tails are the uniform
label0/flag0 ground state and stay so. The checker additionally samples
actual scalar outputs at every segment of rows0,1,2,2730,2731. This
compression is an exact finite partition proof, not a finite ring, a moving
window assumption or a randomly sampled spatial approximation.

## Original error class and consequence (proved, limited scope)

The dense error row has no E0 points: every singleton or adjacent pair
has a nearby exterior error. Any proper nonempty candidate1 subset has
a unit-distance link to its exterior, since the whole row is connected
by unit steps. It fails isolation(iv). The whole row is wider than Q,
so it is not candidate1; hence E1 is empty.

The complete row is candidate2: it fits a Q^2 by U^2 box and contains
the disjoint candidate1 pairs{(0,0),(1,0)} and{(2,0),(3,0)}, linked at
(24Q,24U). All its distances are less than104Q spatially and104U
temporally. No two nonempty subsets of the row can be separated at that scale,
so condition(iii) holds. Its exterior is empty, giving condition(iv).
It is therefore **one actual real2** under Gray's original lambda24/c104
definitions (reader's guide pp16-17). This is not a claimed real1 event.

At every t the17Q clock sites disagree with the clean reference Age
tmodU. Hence no space-time recovery envelope with finite temporal
height can contain all those disagreements, and no finite native-clock
erasure time exists for this error. A fixed17Q *spatial* hull does contain
them forever. Address remains canonical everywhere. Thus the witness
does not refute Gray's Address-only Proposition5, any decoded memory
statement, or any iid theorem.

Changing only a private programme, immutable dictionary or SF equations
cannot remove this native orbit if the native equations and constant-zero
Workspace outputs remain unchanged on every raw state. The native
projection is an autonomous factor under precisely those hypotheses.
Removing the obstruction requires changing that interface or the native
operator; adding authentic Workspace pulses is a possible direction,
**not a sufficiency theorem**. No minimal globally reliable repair is
established here.

| Step | Status |
| --- | --- |
| Intact simultaneous recursive X | **proved in pinned root initializer proof** |
| Binary-clock/GF/F1/F2 native factor, all clocks and SF states | **proved algebraically; finite actual cofactors certify implementation** |
| Event compression and all transient/saturated rows | **proved finite partition and induction** |
| Exact infinite-time stationary native clock island | **proved for changed WF0 GMW7** |
| One shared clock-only finite actual-real2 history | **proved under original lambda24/c104** |
| Private-only fixes with unchanged native/WF0 | **ruled out for this orbit** |
| Gray/Gács/G17, Address/decoded-memory or iid counterexample | **unproved; not claimed** |
