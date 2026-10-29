# GAWN7: native flag deadlines and the remaining five clocks

This is about the **unchanged frozen GAWN2** rule, Q4096/U524288,
radius8/Word100/h1/beta_2/lambda24/c104, with all its existing departures
from Gray. No transition, programme, schedule or constant is changed.
It continues
[GAWN6](../unregistered_gawn6/GAWN6_CANONICAL_ADDRESS_CLOCK_CONFINEMENT.md).

The new universal deadlines clear Workspace and Flag2. A bulk clock
identity then reduces the remaining full native recovery premise to
the actual clocks at five sites on one specified row. Correctness of
those five clocks for every payload is **unproved**. The conditional
complete2U result below is not a random-noise reliability theorem.

## 1. Initial histories and exact statements

Use the actual recursively intact H_2 history and late row
T=100Q+2=409602 of GAWN6. At rowT replace an arbitrary subset of true
colony I=[0,Q), retaining Address and choosing each replaced Age in

    V=[96Q-1,U-4Q-1]=[393215,507903].

All four native flags and all thirteen SF fields may otherwise be
arbitrary legal values. There are no later errors. No classification
is inferred merely from the size of this support. GAWN6's universal
exterior theorem applies, including to supported original-c104 real1
faults that actually meet its definition.

Write t for elapsed physical updates after rowT and L=4Q=16384.
Every raw clock throughL is v+t for some v in V; there is no wrap.
Outside I the raw clock is exactly T+t. The following are **proved**:

1. Both raw Workspace flags are0 globally from t=2Q+1=8193 throughL.
2. Raw Flag2 is0 globally from t=3Q+1=12289 throughL.
3. Whenever computed Flag2 is0, the clock update at every canonical
   Address a>=5 equals the left five-word majority with self fallback,
   followed by +1 modU, independently of Flag1.
4. If the five actual clocks at x=0,1,2,3,4 are correct on row
   T+3Q+1, all six native fields are correct globally by t=15701<4Q.

The last assertion is conditional on five **actual raw clock equalities**;
it does not reset them, assign their future values or infer them from
finite runs. No new native trajectory is measured here.

For the subclass retaining every SF field except Info, item4 implies
the complete raw2U equality and all later equality with the clean
history by GAWN6 §2. For the broad arbitrary-SF class above, item4
asserts native equality only; malformed raw Head faults are not
covered by that full-boundary reduction.

## 2. Workspace closes at2Q+1 — proved

The whole-word voters and self fallback select an old clock, then add1.
GAWN6's range proof gives minAge(t)>=96Q-1+t and maxAge(t)<=U-4Q-1+t
throughL. At t=2Q+1 the computed clocks are at least98Q and belowU.
They remain in[98Q,U) throughL. The actual Workspace equations have
the strict guard96Q<=computedAge<98Q. Both return0 outside that
guard, regardless of the actual computed Info, reader Flag1 or SF
payload. Thus raw Workspace1 and Workspace2 are0 from2Q+1 onward.
Arbitrary initially overwritten raw Workspace values are included.

This is not a source approximation. The conclusion follows from the
guard in the full physical transition after bounding its selected
computed clocks.

## 3. Flag2 clears at3Q+1 — proved, using h1

Start at t_b=2Q+1. GAWN6 proves raw Flag2=0 outside I, including all
five sites to the left of its endpoint0. All old Workspace2 values
are now0; canonical Address makes C exist, so the missing-C source
is absent. In one update, a site whose five left raw Flag2 bits are0
has computed Flag2=0, whatever its old self bit or computed Flag1.

If old self is0, neither the left-inside nor untruncated left turn-on
threshold is met. If old self is1, h1 erases it: with computed Flag1=0
the left-inside count0 is <=1, and with computed Flag1=1 all five
untruncated left bits are0. No source overrides erasure.

Consequently the guaranteed zero prefix of I extends at least one
site per update. Each established prefix remains zero, and its next
site has all five left neighbors zero. At t_b+Q=3Q+1 all Flag2 bits
inside I are0 too. They remain0 throughL because both sources remain
absent. This deadline permits arbitrary old Flag2 patterns, clocks,
Flag1 and SF payloads inside I.

The h1 erasure clause is material to this proof. Gray's literal
printed healthy-erasure clause is not silently substituted here.
This is not a theorem for his printed rule.

## 4. The bulk clock identity — proved

Consider a site with canonical Address a>=5 and computed Flag2=0.
Let R be the old right Age quorum, with self fallback, and M the old
left Age quorum, with self fallback. All five left neighbors are in
the true apparent colony.

If computed Flag1=1, the actual selector chooses M. If computed
Flag1=0, the actual Flag1 equation implies that the right Age majority
exists and that at most two of the five left clocks disagree with R.
At least three left clocks equal R, so their clear majority is R:
M=R. The selector chooses R, which is again M. Both cases therefore
give M+1 modU. Additional Flag1 propagation or Workspace1 forcing
can select the first case but cannot invalidate the identity.

Only the first five Addresses0..4 lack this full five-neighbor
in-colony inconsistency test. This explains precisely which part of
the clock argument remains open; it is not an assumption that bulk
clocks were correct during the damaged interpreter execution.

## 5. Five correct clocks imply bulk repair — proved conditionally

Let t_0=3Q+1. By §§2–3, all Flag2/Workspace are0 from this row throughL.
Suppose raw Age(x,T+t_0)=T+t_0 for x=0..4. Outside I the clocks are
correct by GAWN6. All following references to a correct old clock
mean the current common reference value; the increment then gives
the next reference value.

On the first update, x0 andx1 have at least three correct right voters
and all correct left voters, so they remain correct under either
selector. At x3 andx4, the left majority is correct. If the right
quorum is incorrect, respectively three or four in-colony left clocks
disagree with it, forcing computed Flag1=1 and the correct left vote.
If that quorum is absent, Flag1 is also forced1. If it is correct,
either selector is correct. Thus x3 andx4 stay correct. Sitex2 alone
may become incorrect. The bulk identity gives correct clocks at
x5,x6,x7, which have respectively five, four and three correct left
voters. The first-step guaranteed set is

    {0,1,3,4,5,6,7}.

On the second update, every site0..4 has at least three correct right
voters and at least three correct left voters, so either selector
is correct. Sites5..7 have at most one incorrect left voter (site2),
and sites8..10 have respectively five, four and three correct left
voters. The bulk identity therefore gives the correct prefix0..10.

Once a correct prefix has lengthm>=11, the boundary sites0..4 have
correct left and right majorities and stay correct. Every old correct
bulk site has a correct left majority. The next three sitesm,m+1,m+2
have at least five, four and three correct left voters, and become
correct simultaneously. Thus the prefix grows by at least three
sites per update without retreating.

All clocks in I, and hence all clocks globally, are correct after

    2+ceil((Q-11)/3)=1364

updates fromt_0. This proof allows arbitrary distinct incorrect clock
values and arbitrary Flag1 bits; it uses exact word quorums, not a
binary approximation to incorrect clocks.

## 6. Common clocks give the final Flag1 deadline — proved

With common clocks and canonical Address, every inconsistency source
is absent. Both Workspace fields are0. The actual Flag1 equation in
each true colony is now

    newF1 = (right-inside count>=3)
            or (oldSelfF1 and right-inside count>=2).

A guaranteed zero suffix cannot retreat. Its two preceding sites
have at most zero and one positive right-inside neighbor respectively;
both become0 under the displayed rule, regardless of their old self
bits. Starting with an empty suffix at the true right boundary, all
Q sites are therefore zero within ceil(Q/2)=2048 updates.
Every true colony clears simultaneously. In particular, the possible
Flag1 support in I and its left adjacent colony does not require
adding two sequential sweeps. Common clocks remain common under either
quorum during this sweep, and Flag2/Workspace remain0.

Combining the bounds gives full native equality by

    R = 3Q+1 + 1364 + 2048 = 15701,
    L-R = 683 > 0.

Thus the correct-first-five premise at rowT+3Q+1 suffices for GAWN6's
actual native recovery hypothesis. For Age/flags/Info faults retaining
all other SF, its complete-U encoding and normalized upper one-cell
argument give X_2U=F_2^(2U)(H_2), followed by all-tick equality.
Neither this composition nor the native proof verifies the five-clock
premise for arbitrary replacement payloads.

## Verification and status

The [checker](check_gawn7_flag_clock_reduction.py) records local native
cofactors for the h1 zero front, bulk clock identity and Flag1 suffix,
plus two actual full-kernel updates for selected prefix configurations
and actual Workspace-guard samples. These are finite transcription
supplements. The universal statements above are proved by the value
counts and inductions, not by interpreting the samples as all histories.
No evolving full-colony repair campaign, native quiet-row experiment
or complete2U physical simulation is performed.

| Step | Status |
|---|---|
| Actual initializer, canonical Address and native exterior | GAWN6's proved argument applies unchanged |
| Both actual Workspace fields zero by2Q+1 | Proved for every admitted payload |
| h1 Flag2 zero by3Q+1 | Proved for every admitted payload |
| Bulk clock identity at Address>=5 | Proved |
| First-five condition implies clock repair/Flag1 clearing/nativequiet15701 | Proved conditionally |
| Restricted complete2U repair from this condition | GAWN6's proved reduction applies |
| First five clocks correct at3Q+1 for every admitted payload | Unproved |
| Finite native/full-kernel transcriptions | Measured supplements |
| GF-changing/earlier/E0-surrounded/mixed/higher/iid reliability | Unproved |
| Faithful printed Gray/G17 counterexample, shorterU or global minimum fix | Unproved |
