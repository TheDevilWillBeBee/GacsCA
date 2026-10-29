# GAWN26: larger interior supports and the exact two-bank phase criterion

This extends the hypotheses of frozen GAWN24 for **unchanged GAWN2**:
Q4096, U524288, radius8, Word100, h1, own beta, lambda24/c104 and all
previously declared departures from Gray. No equation, programme,
constant, initializer or frozen asset is changed. This is a deterministic
restricted repair theorem, not an iid reliability or memory theorem.

## Exact statement

Let F,H2,Y_t=F^t(H2), I=[0,Q), and the represented-D encoding E be
exactly those in [GAWN24](../unregistered_gawn24/GAWN24_INTERIOR_ALL_AGE_MIXED_PHASE_REPAIR.md).
Choose a fixed interval A=[b,b+w) contained in [1,Q-1), with
1<=w<=Q-2=4094. Choose integers 0<=tau<=L<=514049 satisfying the
following phase criterion:

| First possible after-row fault tau | Maximum last possible after-row fault L |
|---|---|
| 0..32769 | 120833 |
| 32770..163841 | 251905 |
| 163842..294913 | 382977 |
| 294914..514049 | 514049 |

On any subset of rows tau,...,L, replace any subset of cells in A
adaptively. Retain their actual Address; every other native field and
all thirteen SF fields may be arbitrary legal values. At tau=0 the
overwrite follows initialization. There are no other errors.

Then GAWN24's conclusions hold verbatim:

1. Address is canonical globally. Outside I, Age is the reference row
   modulo U, F2 and both Workspace fields are0, and F1 differs only in
   I and its left neighbor. Both actual Head endpoints of I are protected.
2. Every outside-I early/late evaluator has an actual seventeen-record
   tape equal to the corresponding H2 records except possibly record0.
   Its completed outputs, bounded couriers and special Info sources are
   correct. Private intermediate traces need not equal the reference.
3. All native fields are quiet by

       q=max(L+10238,407552)<=U-1.

4. The complete raw U boundary is E(dprime,Bprime), with dprime equal
   to cell_words(F(H2)) outside upper physical cell0. Its record0 and
   auxiliary Info inside I may be arbitrary, including represented
   native padding. Complete X_(2U)=Y_(2U), and every later row is equal.

In particular, the theorem holds for every such interior A and every
tau,L<=514049 with L-tau<=88064, that is at most88065 possible fault
rows. This uniform sufficient bound is sharp **for the phase criterion
above**, not a claimed maximum duration that the rule can repair.
The piecewise criterion also admits substantially longer intervals.
Neither support size nor duration alone assigns an original error class.

## 1. Removing the spatial bound — proved

The native exterior and recovery arguments in GAWN6/8/21/24 already
permit arbitrary native/SF values at every site of I. Their bounds use
Q, not the number of overwritten sites. The two endpoints are the only
spatial restriction used for GAWN24's SF isolation.

The five holders of logical0 are [-2,2]. A excludes physical0 and
negative sites, so it can overwrite at most physical1,2. The holders
of logical Q-1 are [Q-3,Q+1]; A excludes Q-1 and greater sites, leaving
at most Q-3,Q-2 vulnerable. Thus each endpoint always has three normal
holders preserving its forbidden outward movement bit, regardless of
different internal clocks, malformed work, repeated overwrites or w.
GAWN22's all-clock endpoint invariant applies unchanged. No Head exits I.

For any logical y outside I, at most two holders are in I, independently
of w. The three actual outside holders have canonical service Address
and correct reference clock. The wipe is false. F1 affects only Mail:
the other eleven SF equations do not depend on it. Consequently their
logical equations and immunity to after-row overwrites are exactly
GAWN24 sections1-2. This includes Info holding, History retention,
own Programme generation, evaluation, couriers and Out.

No argument here says that private SF stays pointwise inside I: Mail
can transport contamination, and evaluator intermediate traces can
differ. The conclusions concern restored tapes and completed outputs.

## 2. Deriving the temporal criterion — proved

Write R=10238, W_g=[S_g,S_g+8Q+1], S_g=0,32Q,64Q. These are the
actual old-Mail vulnerability windows from GAWN23/24:

    W_1=[0,32769], W_2=[131072,163841],
    W_3=[262144,294913].

Before the actual96Q Workspace pulse the arbitrary-clock tagged suffix,
h1 F2 front, first-three clock argument and F1 sweep of GAWN21 give
native quiet by L+R whenever L+R<=96Q-1. The proof permits faults at
all sites of I on every row through L; it does not use a104-row bound.
Only its closed-reference-guard requirement is used here, not GAWN21's
earlier whole-U result. Extending that native induction from32Q to
96Q-1 uses the same literal guard and the same modulo-clock equations,
as already established in GAWN24 section3.

If tau<=294913, put q_early=L+R and require

    q_early<=96Q-1=393215,
    #{g : tau<=max(W_g) and q_early>=min(W_g)}<=1.       (P)

Outside-I F1/Mail disturbance before the last capture is confined in
time to [tau,q_early]. A bank whose window misses this interval is
correct: either its old capture operands were consumed before tau, or
its actual subsequent reset/load/shift occurs after native quiet.
Direct History overwrites cannot change outside-I votes. All sources
outside I are original Info; sources inside I are arbitrary and may
differ between snapshots. Therefore at least two actual outside-I
banks have the correct source words except for upper record0.

Condition(P) is exactly the first three rows of the statement's table.
For tau<=32769 it says q_early<131072, hence L<=120833.
For 32770<=tau<=163841 it says q_early<262144, hence L<=251905.
For 163842<=tau<=294913 only W_3 remains; the bound is instead
q_early<=393215, hence L<=382977. These are inclusive after-row bounds.

If tau>294913, every old capture operand was consumed before the
first possible overwrite. At tau=294914 the last normal capture
precedes the after-row overwrite; its outside-I vote survives it.
All three outside-I banks remain good. No early quiet bound or fault
duration restriction is needed for this case. The sole last-fault
bound is L<=U-1-R=514049, giving the fourth table row.

The smallest L_max(tau)-tau across all allowed starts is88064, attained
at32769,163841,294913. Thus L-tau<=88064 implies the table everywhere.
At tau32769, allowing one more row gives L120834 and q_early131072:
[tau,q_early] meets both W_1 and W_2. The analogous second edge meets
W_2,W_3. At tau294913 one more row gives q_early393216, opening the
reference pulse. These are failures of this sufficient criterion;
no failing actual history or minimal necessary repair limit is inferred.

## 3. Early evaluation does not require global quiet before75Q — proved

The broader criterion can put q_early between75Q and96Q-1. GAWN24's
old104-row hypotheses gave q_early<75Q, but that inequality is not
needed by its **outside-I** early evaluator.

Before96Q the exterior clock/native invariant already holds while
inside native fields remain arbitrary. All outside logical Head/Mem/
Out/Scratch/Programme equations use the three correct-clock holders;
their only potentially different native flag is F1. Inspection of the
unchanged `_physical_transition` shows F1 changes Mail only, and the
GF wipe is absent. Both endpoint shields exclude an inside packet.
Hence the actual72Q+3 reset/Mem load and72Q+4 early birth derive the
same valid S1 execution outside I. The two good banks from section2
are already correct at their respective captures, so they are available
at this load even if q_early is later. They are not future banks.

The arbitrary one-upper-D-cell identity at actual H2, GAWN19, applies
to each restored tape separately. S1 completes correct outside native
outputs within221 updates, before75Q. Couriers then carry the correct0
flags within their true colonies and actual80Q-1 writes leave outside
special Info0. This conclusion is independent of the later q_early.
No unknown global execution trace or future command is assumed.

## 4. Closing the actual pulse, late stage and two periods — proved

Now GAWN24 sections4-6 apply unchanged. The attained outside special
Info0 makes actual computed-primary Workspace0 outside I throughout
96Q..98Q; the exterior invariant therefore extends through U without
prescribing a source. Tags cover I by L+Q-2. At B=max(L+Q-2,98Q)
actual WF2 is0: the correct-clock guard is closed, or computed F1=1
closes its gate. WF1 may remain arbitrary. The h1 F2 front and tagged
clock prefix give correct clocks/F2 by B+Q, then the F1 sweep gives
q=B+Q+Q/2=max(L+10238,407552)<=U-1.

Outside-I History remains retained. Actual100Q reset/reload/birth
and the same shield/three-holder/readonly-bank argument give correct
completed496-word outside Out by127Q. F1 can be nonzero outside while
that evaluator runs, but does not enter its SF equations. At U all
native fields are quiet globally; old Out commits before all work
resets, producing the stated E(dprime,Bprime). The proved arbitrary
single-upper-cell correction at C1=F(H2), followed by unchanged S2,
gives complete2U equality; determinism gives every later equality.

## Status and verification

| Step | Status | Exact scope |
|---|---|---|
| Whole-interior endpoint/vote protection | proved | A excludes physical0,Q-1; fixed support |
| Native exterior/tag/front/10238 component | proved antecedent argument applies | GAWN6/8/21/24; h1 and Address retention |
| Piecewise phase criterion/two actual banks | proved | (P), or all captures before first fault |
| Outside early evaluator despite q_early>=75Q | proved | Literal F1 independence, actual preparation/three holders |
| Open-pulse exterior/late stage/U/2U/all later | proved antecedent arguments apply | GAWN24/19/S1/S2 with derived hypotheses |
| Full support/phase arithmetic checks | exact finite supplements | No evolving native/SF or U/2U experiment |
| GF/boundary changes/multiple supports/E0/higher/iid | unproved | No positive epsilon or bit-memory theorem |
| Faithful Gray/G17 refutation/minimal sufficient change | unproved | All prior proposal departures remain |
| Rule/ROM/constants/CURRENT changes or commit | none | Frozen prior assets preserved |

The checker recomputes all8,382,465 interior interval endpoint counts,
the phase table at all514050 possible starts, allowed-pair counts and
sharp uniform-bound witnesses. It checks the inherited780 pins before
and after. These arithmetic supplements do not simulate noisy histories;
universal repair follows from the inductions above and linked antecedents.
