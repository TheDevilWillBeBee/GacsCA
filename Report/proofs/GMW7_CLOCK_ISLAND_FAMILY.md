# GMW7: an all-phase stationary clock-island family

This extends [the accepted WF0 clock-island proof](gray_counterexamples/GMW7_WF0_CLOCK_ISLAND.md).
The rule is the same explicitly changed GMW7, Q8192/U1048576, with
identically-zero Workspace outputs. No rule, programme, dictionary,
constant, active G17 source or accepted agent artifact changes.
The [checker](check_gmw7_clock_island_family.py) and
[receipt](../../figs/robustness/GMW7_clock_island_family_certificate.json)
pin that proof, its actual-native factor certificate and the
[intact initializer](GMW7_INTACT_HIERARCHY.md).

## Exact statement

Let X be the explicit simultaneous intact initializer, and take any
integer theta with 0<=theta<U. The error-free operational state
X_theta=F7^theta(X) has native GF=x mod Q, common Age theta and flags0.
It remains a simultaneous hierarchy by the preceding all-time theorem;
it need not be a boundary encoding at this intermediate phase.

Choose an integer m>=2, a nonzero offset 1<=delta<U, and an aligned
origin b in QZ. At physical row0 overwrite only Age on [b,b+mQ) with
(theta+delta) mod U, leaving every other actual X_theta field untouched.
There are no subsequent errors. Put h_t=min(3t,Q). Then for all t>=0
and x in Z the actual full rule's native projection satisfies

    GF(x,t) = x mod Q;
    Age(x,t) = (theta+t+delta*1_[b,b+mQ)(x)) mod U;
    Flag1(x,t) = 1_[b-h_t,b)(x) OR 1_[b+mQ-h_t,b+mQ)(x);
    Flag2(x,t) = Workspace.Flag1(x,t) = Workspace.Flag2(x,t) = 0.

Consequently every original wrong clock stays wrong forever. The native
projection is periodic after saturation at t2731, with period U and no
translation. All other private fields may evolve arbitrarily under F7;
no periodicity or correctness claim for them is made here. The same
native statement holds for any legal private-field initialization with
this native prefix, whether or not it is an intact operational hierarchy.

For 2<=m<=104 the one finite error row is exactly one actual real2 under
Gray's original lambda24/c104. In particular m2/theta0/delta1/b0 gives
16384 clock-only overwrites of the actual intact X, rather than the
139264-overwrite m17 witness. This is a smaller witness for the same
changed-rule obstruction. It is not an original-Gray/Gács/G17 or iid
memory counterexample.

## Proof of the universal native orbit

The pinned factor proof derives the native equations from the actual
`scalar_native` implementation. With canonical GF, both adjusted GF
votes exist and return canonical GF. Initially F2=0; the missing-GF
source is false, the Workspace source is false, and no left F2 input
is1. Thus F2 stays0. The actual F7 outputs keep both Workspace flags0
on every legal raw state, independently of private data.

The two clock values (theta+t) mod U and (theta+t+delta) mod U are
distinct for every t because delta is nonzero modulo U. Five inputs
always have a majority in this two-value set. Equality, majority and
modular increment therefore depend only on the two labels0/1, not on
theta, delta, numeric order, or wrap. This proves the all-phase/all-offset
extension of the already certified factor, including the wrap cases
where one clock is0 and the other isU-1. There is no ordering operation
in the actual factor.

Let L/R be left/right five-input label majorities; let c be the number
of left in-colony labels unequal to R and f the right in-colony Flag1
count. Exactly as in the pinned proof,

    newFlag1 = [c>=3 or f>=3 or (oldSelfFlag1 and f>=2)];
    newLabel = L if newFlag1 else R.

The clock jumps are at b and b+mQ. Only sites within three positions
of these jumps can have L!=R. At the last three sites of each preceding
colony the in-colony mismatch count is5, forcing Flag1 and the left
label. At the first three sites of each following colony the mismatch
count is at most2; if that colony has no Flag1, the right vote preserves
its label. Elsewhere both votes equal the site's existing label.

The source/predecessor colonies have indices b/Q-1 and b/Q+m-1.
The following colonies have indices b/Q and b/Q+m. For every m>=2
these sets are disjoint. Right-front and self-support tests use only
Flag1 within the site's own colony. Hence only the two predecessor
colonies can acquire Flag1; in particular the two following colonies
remain Flag1=0. This establishes the premise needed in the previous
paragraph without assuming it as a future boundary condition. The two
jumps are separated by at least2Q>10, so their label-vote neighborhoods
do not overlap.

In each predecessor colony the forced last three sites start a suffix.
A site three places to its left sees three right1s and switches on; a
site four places to its left sees only two and has no self-support.
Previously flagged suffix sites persist by right support or the permanent
last-three-site mismatch source. The suffix therefore grows by exactly
three sites each tick until it reaches the colony's left boundary,
where the in-colony test stops its propagation. Induction gives h_t.
Together with the vote analysis this proves all displayed fields at
every update, and therefore the infinite orbit. Since b is Q-aligned,
translation by b preserves every inside-colony test; no translation of
the private initializer is required for this argument.

## Original error class

For 2<=m<=104 the support is a connected row of mQ faulty sites. Every
singleton or adjacent pair has another error within distance24, so E0
is empty. Every proper nonempty candidate1 subset has an adjacent error
in its exterior, and fails isolation(iv). The full row is wider than Q,
so it is not candidate1. Thus E1 is empty.

The full row fits a Q^2 by U^2 box since m<=104<Q. The adjacent pairs
{b,b+1} and {b+2,b+3} are disjoint candidate1 sets, linked at24Q/24U;
this is the recursive candidate2 condition, not a claim that the pairs
are real1. The diameter mQ-1 is strictly less than104Q. Any two
nonempty subsets of the row are consequently linked at104Q/104U, so
Gray's condition(iii) holds even before restricting to candidate2
subsets. The exterior is empty, giving(iv). This proves one real2.
For m>104 the native orbit theorem still holds; no real2 classification
is claimed from this diameter argument.

## Meaning of the two-colony minimum

This is a minimum only for the displayed aligned constant-offset,
zero-initial-flag orbit formula with an integer number of colonies.
For m1 the following colony at the left jump is also the predecessor
colony at the right jump. The displayed clock/suffix formula holds
through t2729, when its inside Flag1 suffix is [b+5,b+Q). The next
update gives site b+2 three right in-colony1s and newFlag1=1. Its left
vote has three outside clocks and two inside clocks, so it selects the
correct outside clock. Its Age becomes(theta+2730) mod U. This is the
first failure of the displayed permanent-island formula. The checker
exhausts all preceding constant-input event intervals and verifies this
exact local update in the actual native rule, rather than assuming the
old clock formula remains valid after its first failure.
It is not a proof of the smallest arbitrary fault support, a global
clock-eroder theorem for m1, or a smallest sufficient reliable repair.

## Certificates and status

The universal proof uses only the pinned actual factor and the explicit
disjoint-colony/equality inductions above. The new checker exhausts
all constant-input transient event intervals for the smaller m2 witness,
with supplemental actual native checks at selected modular phases and
offsets. It stores every m2/theta0/delta1/b0 error coordinate in
[the support asset](../../figs/robustness/GMW7_clock_island_family_errors.npz).
No finite space ring or numerical whole-CA evolution supplies the
infinite-time conclusion.

| Step | Status | Limit |
| --- | --- | --- |
| Intact operational common-phase start | **proved** | Pinned initializer/all-time theorem and native quiet preservation |
| Arbitrary phase/offset/aligned origin and every m>=2 | **proved** | Actual WF0 native factor, disjoint-colony and modular equality inductions |
| One original real2 for2<=m<=104 | **proved** | Exact error-class definitions; no class claim for larger m |
| Smallest m for the displayed stationary formula | **proved** | m2 works, exact m1 first-violation update at2730/x=b+2 |
| Smallest arbitrary damaging support or sufficient repair | **unproved** | No such global optimization or repair theorem follows |
| Gray/Gács/G17/Address/decoded memory/iid counterexample | **unproved** | Only this explicitly changed fixed-WF0 clock factor is obstructed |

The agent independently reviewed the family extension without changing
the frozen accepted artifacts. No commit is made.

The initial proof/checker/receipt/log are retained in the
[m1 history wording correction](../../figs/robustness/GMW7_clock_island_family_initial_m1_wording_correction.json).
That version checked a legitimate scalar update at nominal tick2731 but
described its input as an actual m1 history row. The unchanged-clock
formula had already failed at2730/x=b+2, so the later input was
counterfactual. The new prefix check supplies the actual first-failure
claim; no m>=2 family theorem, accepted agent artifact or rule changes.
