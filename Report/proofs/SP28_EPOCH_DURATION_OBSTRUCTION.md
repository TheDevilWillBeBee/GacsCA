# Retuning SP28's force duration does not remove the Address island

The result concerns an explicit **duration-only local-transition family**,
not a newly certified self-simulating candidate. In
[proposed_sparse_epoch_duration_family.py](proposed_sparse_epoch_duration_family.py),
SP28's full Boolean transition is unchanged except that its common RF
epoch force lasts mQ ticks. Birth is still only at TF. Q1024, U475136,
TF278401, the alphabet and the field layout are unchanged. The case m=4
is exactly the existing SP28 graph. Other m change the rule; no matching
own programme has been built for them. The active rule is untouched.

## Statement

For every integer 3<=m<=189, set the force duration to mQ. From the
J156 native template (delta512, a=128Q-delta, b=144Q, phase1 on[a,b),
Flag1 on[127Q,a) and[b-delta,b), Age0, Flag2 and auxiliary headers0),
every nU boundary has that same native template translated by -3mnQ.
All other private fields and instruction inputs may evolve arbitrarily.
There are16896 wrong Addresses at every boundary. Auxiliary fields are
empty there. Whole private-state periodicity is not asserted.

Thus shortening4Q to3Q, or any other duration in this range, fails to
restore a fixed finite Address envelope or a finite native Address
eroder. Durations below3Q or nonmultiples of Q are not decided here.
The result neither proves iid failure nor finds a sufficient smallest
reliable change. No new self-simulation or half-line theorem is claimed.

## Full-rule reduction

J156 proves two-Address-phase/common-clock closure independent of every
private field. This proof is unchanged: refinement and both directional
Age votes see the same legal clock; their GF votes remain in the two
phase alphabet. Changing the epoch length cannot change that closure.

The birth row remains TF moduloU. All packet/code/WF2 native sources
and backward pressure expire by TF+1794. This is the same counter
ancestry/window argument, which does not require canonical spatial GF.
Since3Q=3072>1794, every such source remains inside every revised force
window. Within that window the global native force already makes the
computed Flag2 equal1, so those extra positive sources are redundant;
outside it they are0. Actual headers evolve and expire; none are
externally set to zero. Raw WF1 is bounded by J156's literal selected-GF
last-five guard, supported only until TF+2Q+1. These bounds are unchanged
by an arbitrary new programme or instruction history.

Consequently every family member has exactly the same native lower/upper
enclosure during the first3Q rows of the pulse. Before TF the quiet
template and initially empty headers advance without change. The
enclosure is J156's literal six-plane map, including its native Flag2
monotonicity proof. The force-on interval thereafter has WF1=0 and no
other live auxiliary source. Its native map is independent of the
numerical common clock: Age mismatches and fallback are absent, and no
commit or window event occurs there. The force-off tail has the same
property after substituting force0. Common Age still increments normally.

## Finite cycle and tail

The [cycle checker](native_address_epoch_duration_cycle.c) includes the
unchanged J156 projection and evaluates its original4Q pulse and2Q tail.
It compares all six planes at all256Q sites, not just edge locations.
Let T_d move a frame by d sites, and let A be the initial template.
The retained computation establishes:

1. At TF+3Q, the lower/upper Flag1 planes agree, both Flag2 planes are
   identically1, and WF1 is0. Call this exact frame P. Its GF island is
   [121344,138240), still16896 sites wide.
2. The next Q force-on rows give T_(-3Q)P exactly, in all six planes.
   Its GF island is[118272,135168). The same free-private enclosure has
   collapsed at both frames.
3. The following2Q force-off rows give T_(-12Q)A exactly, with both
   native Flags and WF1 in the required quiet template and no Flag2.

This is a finite exhaustive calculation of the previously derived
Boolean map. It uses no random vector or selected private history.
The proof concerns those literal equations; the C executable and state
assets supply a reproducible receipt. J156 separately pins their
correspondence to the actual native/auxiliary interface.

Its integer-line interpretation also reuses J156. Relative to the
uniform phase0 Q-periodic reference, GF support grows at most3 sites
per row and flag discrepancies at most8. For these6Q rows,48Q margins
contain all exceptions, and the actual two array margins are larger.
Outside them the reference/enclosure is Q-periodic. Thus the periodic
calculation proves the same frame equalities on Z. These margins are
used only for the finite basis pulse, not for arbitrarily many later
cycles or periods.

## All187 durations and all periods

On a common legal clock with all auxiliary sources0, the force-on map
commutes with translations by Q. The stored GF phase definition also
commutes with such translations because Q is its period. The exact
one-Q cycle therefore gives, by induction, at TF+mQ

    T_(-3(m-3)Q) P,    for every integer m>=3

as long as the next clock event does not intervene. This is an exact
infinite-line induction, not an extrapolation of sampled durations.

Apply the same force-off tail. From the basis equality at m=4 and
translation commutation, that tail maps P to T_(-9Q)A. From the m frame
it therefore yields

    T_(-3(m-3)Q) T_(-9Q) A = T_(-3mQ) A.

For3<=m<=189, TF+(m+2)Q<U; the largest endpoint is473985, below475136.
There is no next birth, workspace-source window or commit during either
the added force-on cycles or that tail. All subsequently quiet rows
preserve the GF/Flag1 template while incrementing the clock. At U the
common clock returns0 and all headers/workspace sources are empty.
Translation by3mQ, U-periodic source windows and universal private
enclosure restart exactly the same proof for every n. This establishes
the stated orbit for the full local-transition interface family.

The same computation's far-field Q-periodic reference proves that an
initial canonical-GF/common-Age0/zero-native-flag/empty-header state has
canonical native fields and empty auxiliaries at U for arbitrary private
histories in this family. At that row overwrite only GF and Flag1 to
create A. Every actually changed site is in the dense row[127Q,144Q),
and every site in that row changes. J154's classification therefore
applies verbatim: real3 at c16, real2 at c104. No other error is supplied.
A static recursively compatible E28 initialization can be used at time0;
its field layout has not changed. For m!=4, continuing noiseless
self-simulation of that layout is unproved. The finite native creation
and subsequent orbit do not rely on that unproved self-simulation.

## Status

| Step | Status | Limit |
| --- | --- | --- |
| Full duration-only Boolean transition, m4 identical to SP28 | proved | m!=4 explicit rule revisions; matching own programmes absent |
| Common-clock/two-phase closure and auxiliary/native reduction | proved | Same J156 literal interface; initially empty headers; no later errors |
| Exact3Q prefix, one-Q translation cycle and2Q tail on Z | proved | Universal WF1/private enclosure; finite complete basis calculation |
| All187 durations/all-period travelling Address orbit | proved | 3<=m<=189; no wrap/window intrusion; arbitrary private histories |
| One real3(c16)/real2(c104) row creates the native orbit | proved | Static recursive encoding admissible; m!=4 self-simulation unproved |
| Durations below3Q/nonmultiples, restored command or spatial force change | unproved | Their different auxiliary/force interactions are not covered |
| Full reliability, iid failure, sufficient minimal native change | unproved | Per-site eventual recovery is compatible with this orbit |

The initially printed largest endpoint474113 was corrected to473985.
The checker already computed TF+(189+2)Q and checked the correct value.
The [retained provenance failure](../../figs/robustness/J158_J159_initial_endpoint_arithmetic_failure.json)
pins the old proof/validator snapshots. No cycle, parameter induction,
clock-window check or transition was changed by this numeral correction.
