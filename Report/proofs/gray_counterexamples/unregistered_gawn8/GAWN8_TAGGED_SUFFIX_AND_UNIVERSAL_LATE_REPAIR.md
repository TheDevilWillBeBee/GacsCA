# GAWN8: a tagged suffix closes the late five-clock gap

This is a proof for the **unchanged frozen GAWN2** rule,
Q4096/U524288/radius8/Word100/h1/beta_2/lambda24/c104, with all its
previous departures from Gray. No rule, ROM, schedule, constant or
active G17 candidate is changed. It continues the proved
[GAWN6 exterior and boundary reduction](../unregistered_gawn6/GAWN6_CANONICAL_ADDRESS_CLOCK_CONFINEMENT.md)
and [GAWN7 component deadlines](../unregistered_gawn7/GAWN7_FLAG2_DEADLINE_AND_FIVE_CLOCK_REDUCTION.md).
The latter's sufficient five-clock premise is now proved for its
specified late class. General noisy reliability remains unproved.

## 1. Histories and exact conclusion

Start with the actual recursively intact H_2 history at physical row
T=100Q+2=409602. Replace any subset of the true colony I=[0,Q),
retaining Address. Give each replaced Age a legal value in

    V=[96Q-1,U-4Q-1]=[393215,507903].

All four native flags and all thirteen SF fields may otherwise be
arbitrary legal values. There are no later errors. The support alone
does not imply a real1 classification; actual original-c104 real1
faults satisfying these restrictions are included.

Write t for physical updates elapsed since that same replacement row,
theta(t) for the clean raw clock, and L=4Q=16384. GAWN6 gives canonical
Address everywhere, correct clocks outside I, zero outside Flag2 and
Workspace, and Flag1 damage only in I and its left adjacent colony,
through the current U boundary. In particular, every site to the right
of I has correct Age and Flag1=0. Its range argument gives unwrapped
clocks and the actual closed Workspace guard from t_b=2Q+1=8193
through L. GAWN7 gives the Flag2 zero prefix inside I: at row t_b+s,
the first min(s,Q) sites have Flag2=0, for 0<=s<=Q, and remain zero.

The following are **proved universally for these histories**:

1. At every x in I, the disjunction
   Age(x,T+t)=theta(t) or Flag1(x,T+t)=1 holds from t=Q-2=4094
   through L.
2. The first three actual clocks are correct from t_b+3=8196;
   the first five are correct from t_b+5=8198. They remain correct.
3. All raw clocks are correct globally by 3Q+1=12289.
4. All six native fields agree with the clean history globally by
   R=3Q+1+ceil(Q/2)=14337, with L-R=2047. Native equality persists
   through the current U boundary.

For the subclass retaining every SF field except Info, GAWN6's proved
boundary reduction now applies without a native-quiet premise:
the complete current U boundary has only upper physical cell0 damaged,
and complete raw equality with the clean history holds at 2U and at
every later tick. For arbitrary-SF replacements, only the native
conclusion is asserted. Malformed Head faults are not covered by that
full-boundary reduction.

## 2. The tagged right-suffix invariant — proved

Call a raw site **tagged** on row t when its clock is correct or its
raw Flag1 is1. This is an analytical predicate, not a new field or a
change to the transition. Every site to the right of I is tagged by
its correct clock and has Flag1=0.

Two implications follow directly from the actual native equations:

* If at least three of a site's five right raw clocks are correct,
  its right Age majority is theta(t). If its computed Flag1=0,
  canonical Address makes the selector choose that right majority,
  giving theta(t+1). If its computed Flag1=1, its next raw Flag1=1.
  Either way its next raw state is tagged. Flag2 may be arbitrary.
* If at least three right neighbors inside its true colony have
  Flag1=1, the propagation clause forces computed Flag1=1, so its
  next raw state is tagged, regardless of clocks, Flag2 or Workspace.

If all five right raw neighbors are tagged, either at least three
have correct clocks, or at least three have Flag1=1. Any right
neighbor outside I has Flag1=0, so the latter three are necessarily
inside the true colony and eligible for the propagation clause.
The two implications therefore prove: **five tagged right neighbors
force a tagged next state** for every center in I.

On the first update the three rightmost sites of I each have at least
three correct right clocks from outside I, so they become tagged.
Suppose a suffix of length m is tagged. All five right neighbors of
every suffix site, and of its immediately preceding site, lie in that
suffix or the tagged exterior. The suffix consequently remains tagged
and extends left by at least one site per update. Its length is at
least min(Q,t+2) for t>=1. At t=Q-2 all of I is tagged, and this
predicate cannot retreat through L. Additional inconsistency or
Workspace forcing only adds Flag1; no source approximation is used.

This argument does not require Flag2 to be zero, a binary model of
wrong clocks, agreement among wrong clocks, or a stationary island.
The disjunction is important: a tagged site need not yet have the
correct clock.

## 3. The Flag2 zero front brings correct clocks with it — proved

From t_b onward, both raw Workspace fields are globally0. GAWN7's
h1 argument supplies a Flag2 zero prefix of length min(s,Q) at
row t_b+s. The tagged predicate has already covered I, since

    Q-2=4094 < t_b=8193.

At each of Addresses0,1,2 the five left raw clocks include at least
three correct exterior clocks. The left Age majority is therefore
theta(t), regardless of all internal clocks. On an update with
computed Flag2=0, all five right neighbors are tagged. If at least
three have correct clocks, both right and left majorities are correct
and either selector gives theta(t+1). Otherwise at least three
eligible right Flag1 bits are1, forcing computed Flag1=1 and selection
of the correct left majority. Thus each of these first three sites
has a correct new clock whenever its computed Flag2=0.

At row t_b+3 the Flag2 zero prefix includes all three, so their clocks
are correct. They stay correct on every subsequent row through L,
using the same tagged-neighbor argument. This does not assume that
the right clock quorum is already correct.

We now induct on s=3,...,Q. On row t_b+s suppose the first s clocks
are correct. On the next row the Flag2 zero prefix includes site s.
Consider any center x with 3<=x<=s. All five left clocks are correct:
they lie in the old correct prefix or the correct exterior. At least
three of these left neighbors are inside its true colony. If the
right Age majority is absent, inconsistency forces computed Flag1=1.
If that majority exists and is wrong, the three correct left-inside
clocks disagree with it, again forcing Flag1=1. In either case
computed Flag2=0 selects the correct left majority. If the right
majority is correct, either selector is correct. All old prefix
sites remain correct, and the next site becomes correct.

Together with persistence at Addresses0..2, this proves a correct
clock prefix of length min(s,Q) on row t_b+s for every s>=3. In
particular the first five clocks are actually correct at8198,
closing GAWN7's premise before its row12289, and all clocks are
correct by t_b+Q=3Q+1=12289. This proof follows the actual Flag2
front; it does not require the faster three-site clock prefix to
outrun a still nonzero Flag2 region.

## 4. Full native deadline and the restricted boundary theorem — proved

At t=3Q+1, canonical Address, correct common clocks, and globally zero
Flag2/Workspace have been proved. GAWN7's common-clock Flag1 argument
applies unchanged. In each true colony its remaining equation is

    newF1 = (right-inside count>=3)
            or (oldSelfF1 and right-inside count>=2).

A true-colony zero suffix grows by at least two sites each update
and never retreats. All colonies clear simultaneously within
ceil(Q/2)=2048 updates, including the possible left adjacent colony.
Thus all native fields are correct by14337<16384. Once they are
correct, the common clock from this row through the current U boundary
is outside the Workspace pulse, including the final wrap to0. The
actual guard remains closed, all inconsistency/missing-C sources are
absent and zero flags stay zero. Native equality persists through U.

For Age/flags/Info replacements retaining every other SF field,
GAWN6 §2 now applies with its actual native-quiet hypothesis proved.
The Info coherence, Mail/courier zero, retained Head endpoint shield,
three clean exterior holders, actual U encoding E_2(dprime,Bprime),
one-upper-cell quorum correction and represented-D period theorem
are reused without modifying their equations or hypotheses. Complete
raw equality follows at2U and all later ticks. The disturbed first
interpreter is still not assumed to complete correctly.

## 5. Verification and limits

The checker below supplies finite native/cofactor and actual full
physical-kernel transcriptions of the tagged-neighbor and prefix
implications. Its selected wrong clock values may be distinct.
The universal quantifiers are proved by the disjunction, value counts
and inductions above; these samples are not exhaustive full histories.
No new evolving native-quiet run or complete2U physical simulation is
performed. No positive iid noise rate is claimed.

| Step | Status |
|---|---|
| Actual initializer/canonical Address/native exterior/clock range | GAWN6's proved argument applies unchanged |
| Workspace deadline and h1 Flag2 zero front | GAWN7's proved argument applies unchanged |
| Tagged suffix covers I byQ-2 and persists | Proved for every admitted payload |
| First-three/five clocks and zero-front clock prefix | Proved for every admitted payload |
| Common clocks by3Q+1; full native quiet by14337 and through U | Proved |
| Restricted complete2U and all-later equality | GAWN6's proved reduction applies with its quiet premise now proved |
| Broad arbitrary-SF complete2U repair | Unproved; only native equality is asserted |
| Earlier/GF-changing/E0-surrounded/mixed/higher/iid reliability | Unproved |
| Printed Gray/G17 refutation, shorterU or globally minimal sufficient fix | Unproved |
