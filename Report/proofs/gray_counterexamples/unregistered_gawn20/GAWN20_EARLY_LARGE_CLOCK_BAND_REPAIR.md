# GAWN20: a larger early clock band and complete current-period repair

This uses **unchanged frozen GAWN2**, Q4096/U524288/radius8/Word100/
h1/own beta/lambda24/c104, with all its existing departures from Gray.
No rule, ROM, constant, CURRENT or prior frozen asset is changed.
It extends a restricted fault class; it is not an iid reliability theorem.

## Exact theorem

Start with the actual noiseless row1 F(H_2), where H_2 is GAWN4's
recursively intact initializer. Fix an integer interval A within true
colony I=[0,Q), of width1..104, and D0 in[0,103]. On any subset of
physical rows1,...,1+D0, after the normal update, replace arbitrary
cells in A, retaining Address. Allow every replacement Age in the
absolute interval

    [0,B],  B=96Q-(104+R)=382876,
    R=(2Q-4)+Q/2=10236.

All four native flags and all thirteen SF fields may otherwise be
arbitrary legal values, chosen adaptively. There are no other errors.
Write t_*=1+D0 for the last possible fault row and X_t for actual rows.

For every such history:

1. Native Address is canonical globally; clocks are correct outside I;
   Flag2/Workspace are zero outside I; Flag1 is zero outside I and its
   left adjacent colony, through the needed prefix.
2. All raw clocks recover by t_*+8188, and all native fields by
   q=t_*+R<=10340<32Q-1. At that row every voted Info word outside I
   equals its original word. Info inside I and every other SF field
   may be arbitrary.
3. X_U=F^U(H_2) as complete raw infinite configurations. All later ticks
   agree too, by determinism and no later errors.

Age zero, backward clocks and far-forward clocks are included. This
strictly includes GAWN19's Age[t,t+104] class at these fault rows and
improves its native bound. Ages382877..524287, Address changes, other
phases, continuing surrounding errors and higher/iid closure remain
unproved. A box geometry alone is not an error-class assignment; actual
original-c104 real1 sets satisfying these restrictions are covered.

## 1. Early native exterior and closed Workspace — proved

The canonical-GF/exterior one-step argument of GAWN6 uses only that
the correct outside successor clock is outside the Workspace window.
It permits arbitrary inside native/SF values. Here outside reference
clocks are the physical rows through q<=10340<96Q. All its one-step
premises therefore hold. Repeated overwrites stay inside I and retain
Address, so induction gives item1. In particular, every site to the
right of I has correct Age and Flag1=0. Every site to its left has
correct Age and Flag2/Workspace=0, even where Flag1 can differ.

Every clock update selects an old whole word or self fallback, then
adds1 modU. Every selected initial or overwritten clock is in[0,B],
with origin row at least1. Thus, on the prefix through q, all raw clocks
are nonnegative and at most B+(t-1). Every normal computed clock is
at least1 and at most B+(t-1) on its output row t. This bound includes
raw zero clocks freshly reintroduced on later overwrite rows. There
is no wrap, since

    B+q-1 <=382876+10339=393215=96Q-1<U.

The actual Workspace guard is closed on every normal update of this
prefix, regardless of SF. After the last fault, both raw Workspace
fields are globally zero from elapsed row1 onward. Missing-colony
sources are false under canonical Address. The same range excludes
every computed-age0 Info commit. It does **not** exclude80Q-1, Head
execution, Mail transport, gathers or couriers inside I; their actual
effects are allowed.

## 2. Flag2 clears behind a one-site front — proved, using h1

Use elapsed r=t-t_* after the last possible fault. At r=1 both raw
Workspace fields are zero globally. Flag2 is zero outside I. From
that row, a site whose five left old Flag2 bits are zero has computed
Flag2=0, regardless of its old self bit, clocks or computed Flag1.
With old self0, neither four-left turn-on threshold is met. With
old self1, h1 erases it: left-inside count0<=1 if computed Flag1=0,
or all untruncated left bits0 if computed Flag1=1. Neither source
can override erasure.

Thus the guaranteed zero prefix inside I at elapsed r has length
at least min(max(r-1,0),Q). It persists and extends one site each
update from the clean exterior. All Flag2 is zero by r=Q+1=4097.
This is GAWN7's proved front argument with its raw Workspace-zero
starting row derived here as1, rather than8193. Gray's printed
healthy-erasure clause is not substituted for this proposal's h1.

## 3. The tagged suffix and first three clocks — proved

Call a raw site tagged when its Age is the current correct clock or
its raw Flag1 is1. This is an analytical disjunction, not a new field.
The right exterior is tagged and has Flag1=0. The two implications
proved in GAWN8 hold here unchanged:

* Three correct right clocks give the correct right Age majority.
  Computed Flag1=0 then selects it; computed Flag1=1 supplies the tag.
* Three eligible right Flag1 ones force computed Flag1=1.

Five tagged right neighbors imply one of these cases: at least three
correct clocks, or at least three Flag1 ones. In the latter case the
ones are inside I, because the right exterior has Flag1=0. They are
eligible under canonical geometry. Thus five tagged right neighbors
force a tagged next state, with arbitrary old Flag2/Workspace/SF.

At r=1 the last three sites of I have at least three correct exterior
right clocks and become tagged. The tagged suffix persists and grows
left by at least one site per update. It covers I by r=Q-2=4094 and
remains there through the prefix.

On the next update, Addresses0,1,2 each have a correct left majority
from at least three exterior clocks. Their computed Flag2 is zero:
the front in section2 already covers them. If at least three right
clocks are correct, both majorities are correct. Otherwise at least
three tagged right neighbors have Flag1=1, forcing computed Flag1=1
and the clean left selector. Therefore the first three clocks are
correct at r=Q-1=4095. They remain correct under the same reasoning;
their left majority always has at least three correct exterior words.

## 4. Clocks follow, then Flag1 clears — proved

For r>=Q-1 suppose the first m=3+(r-(Q-1)) clocks are correct, capped
at Q. The Flag2 zero prefix on the next row covers the next site m:
until it reaches Q, its length is at least r, while m=r-Q+4<r for
Q4096. All five left clocks at any center3<=x<=m are correct; at
least three of them lie inside its true colony.

If the right Age majority is missing, computed Flag1=1. If it exists
but is wrong, the three correct left-inside clocks disagree with it,
again forcing Flag1=1. In both cases computed Flag2=0 selects the
correct left majority. If the right majority is correct, either
selector is correct. Old prefix sites persist and the next becomes
correct. The first three persist by section3. This proves a correct
clock prefix growing one site per row, hence all clocks globally
correct at

    r=(Q-1)+(Q-3)=2Q-4=8188.

Flag2 is already zero, and both Workspace fields are zero. With common
clocks and canonical GF, the remaining actual Flag1 equation is

    (at least3 right-inside ones) OR
    (old self1 AND at least2 right-inside ones).

A zero suffix in each true colony grows left by at least two sites
per update and does not retreat. Every affected colony clears
simultaneously within Q/2=2048 rows. Correct clocks persist under
either voter during that sweep. Native quiet therefore holds at
R=8188+2048=10236. Every argument fits inside the closed-guard prefix
proved in section1. Later native behavior is supplied by the full
physical equality argument below, not by extending this guard claim.

## 5. Info outside I remains exact — proved

The broad clock band admits the special80Q-1 Info write and arbitrary
other SF schedule branches inside I. GAWN19's global old-Info-only
argument is therefore not reused. Instead consider logical y outside I.
At least three of its five physical holders are outside I. Their computed
native clocks are the correct physical row t<=q, excluding0 and80Q-1.
Their GF is canonical and wipe is false. Each of these holders therefore
writes precisely the old voted Info at y, independently of any Out,
Head, Mail, History, courier or other SF corruption.

Initially the vote equals the actual intact word. Induct over every
normal update: the three outside holders preserve that word in the
next vote. An after-row overwrite in A subset I can alter at most two
holders of y, so the vote is still unchanged. This proves exact voted
Info outside I through q. It allows SF transport or malformed Head
effects elsewhere and never assumes outside work is clean. Inside I,
all Info may be treated as arbitrary.

At q the actual496-word frame therefore describes some D configuration
dprime equal to cell_words(H_2) outside upper index0. All other logical
Info becomes arbitrary auxiliary Bprime; every remaining SF field is
allowed to be arbitrary. Native control is canonical/correct/zero and
q<32Q-1. The actual history satisfies GAWN18's full hypotheses.

## 6. Full current-U correction — proved using antecedent contracts

GAWN19 section4 proves, for every arbitrary D replacement of upper cell0
at actual H_2 age0, F^D(dprime)=F(H_2). Four clean native/holder witnesses
give exact complete one-update correction, including padding projection
and the h1 old-Flag2 erasure. That result does not depend on its early
fault clock band, so its unchanged word proof applies here.

Apply GAWN18's two-good-gather theorem at actual row q with dprime and
Bprime. It derives the later banks, own execution preparation and final
commit/reset, giving X_U=E(F^D(dprime),0)=E(F(H_2),0)=F^U(H_2).
No SF repair at q is assumed and no future command is imposed. The
reference equality includes the actual later Workspace window. No later
errors then gives complete raw equality at every tick after U.

## Checks and limits

Finite supplements check tagged/right-front/first-three/prefix native
implications, full-kernel native outputs with arbitrary SF at selected
admitted control phases, and exterior-holder Info retention despite
different inside clocks and arbitrary other SF. Arithmetic checks cover
all104 possible last-fault rows and the bound393215. Universal claims
come from the word counts and inductions above. No full evolving10236-
step SF trajectory or physical-U simulation is performed.

| Step | Status | Scope |
|---|---|---|
| Early native exterior/no wipe | GAWN6's proved one-step argument applies | Correct outside clocks have closed Workspace |
| All admitted clocks/actual closed Workspace prefix | proved | Age0..382876, every adaptive overwrite |
| h1 Flag2 front/tagged suffix | GAWN7/8 proved component arguments apply | Changed starting row supplied explicitly |
| First-three persistence/one-site clock prefix/8188 clock bound | proved | Arbitrary distinct wrong clock words |
| Final Flag1 clearing/native quiet10236 | proved | Common clocks; simultaneous true-colony sweeps |
| Voted Info outside I despite active SF inside | proved | Three actual outside holders; repeated overwrites |
| Upper one-cell correction/complete U and all-later equality | GAWN19/18/2 proved arguments apply | Actual preparation premises derived |
| Kernel/cofactor/holder/arithmetic checks | measured transcription supplements | No complete trajectory simulation |
| Ages382877..524287/GF-changing/other phases/E0/higher/iid | unproved | No positive-rate or memory theorem |
| Faithful Gray/G17 refutation/minimum sufficient global fix | unproved | All GAWN2 departures remain |
| Rule/ROM/constants/CURRENT change or commit | none | Prior frozen assets preserved |
