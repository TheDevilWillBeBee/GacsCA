# GAWN19: early bounded-clock mixed bursts repair completely at current U

This is about **unchanged frozen GAWN2**, Q4096/U524288/radius8/
Word100/h1/own beta/lambda24/c104, with every previously flagged Gray
departure. No rule, ROM, constant, CURRENT or earlier frozen asset changes.
It proves a new restricted early fault class, not positive-rate reliability.

## Exact theorem

Let F, D, pi and E be those of GAWN2 and H_2 the actual recursively intact
initializer from GAWN4. Start with its actual noiseless row1, F(H_2).
Fix A=[b,b+w) within the true colony I=[0,Q), 1<=w<=104, and D0 in[0,103].
On any subset of physical rows1,...,1+D0, **after** the normal row update,
replace arbitrary cells in A. Each replacement retains its raw Address.
At physical row t its raw Age must lie in[t,t+104]. All four native flags
and all thirteen SF fields may otherwise be arbitrary legal values,
chosen adaptively. There are no other errors, including none later.
Let X_t denote the resulting raw rows and t_*=1+D0.

For every such history, all native fields recover globally by

    q=t_*+14337 <= 14441 < 32Q-1=131071.

At that row the voted logical Info may differ from its original value
only at logical positions inside A. As complete raw infinite rows,

    X_U = F^U(H_2),

and equality persists at every later tick. No eventual full-SF trajectory
or clean private work premise is assumed. The prescribed geometry alone
does not classify a fault set as real1; original-c104 real1 sets satisfying
these additional payload/timing restrictions are included.

The forward104 clock band and retained Address are essential hypotheses.
Arbitrary native Age, Address changes, continuing surrounding E0 errors,
multiple bursts and the higher-error induction remain unproved.

## 1. Canonical Address and an early clock band — proved

All adjusted Address candidates in both voters are canonical. Either
selector therefore returns x modQ, irrespective of clocks, native flags
or SF, and the raw-self Address wipe is false. Overwrites retain Address,
so this property holds on every row.

Every actual Age update selects an old raw Age by a whole-word majority
or self fallback, then adds1 modulo U. At row1 all raw Ages belong to
[1,105], including any overwritten cells. If every old raw Age is in
[t,t+104], every computed Age is in[t+1,t+105]; an after-row overwrite
at t+1 has the same allowed band. Induction gives

    all raw Ages at physical t lie in[t,t+104], 1<=t<=q.

This interval never wraps: q+104<=14545<U. Every computed Age on this
prefix is positive, below96Q and different from80Q-1. The actual
Workspace guard is globally closed, independently of SF. Both raw
Workspace outputs are zero on every normal update; overwrite rows may
reintroduce raw Workspace bits only inside A.

## 2. Closed native maintenance commutes with a clock translation — proved

Put Delta=(100Q+2)-1=409601. Given a legal native neighborhood with
canonical Address, translate each old raw Age by Delta modulo U, retaining
all other native fields. Whole-word Age quorums, quorum existence and
self fallback commute with this bijection. Equality/mismatch comparisons
also commute. Apparent-colony masks depend only on unchanged Address.
The only absolute old-Age predicate in the native scalar is the modulo16
Flag2 source for missing apparent colony; it is false because the Address
quorum exists. Thus computed Address/Flag1/Flag2 are unchanged and computed
Age is translated by Delta modulo U. This is a word-level proof over all
legal flag patterns, not a selected-clock enumeration.

To promote that scalar identity to the full physical native equations,
both executions must have their actual computed Workspace guards closed.
The early band in section1 supplies this on the early side. Its translated
band runs from at least409602 to at most424146, wholly above98Q=401408
and belowU. Hence the actual translated guard is closed too. Both return
zero without consuming any SF source. The native update then commutes
with translation even if the two executions' SF is entirely different.
Old raw Workspace values, including overwritten ones, are retained in
the comparison and still contribute their actual native predicates.

Construct the corresponding late history from the actual intact row
T0=100Q+2, with the same physical support and adaptive event sequence
shifted by Delta. Shift each overwritten Age by Delta and copy the four
overwritten flags. Any legal SF overwrites may be used; no late SF tape
is prescribed externally. The late replacement Ages lie in

    [409602,409809] subset [96Q-1,U-4Q-1]=[393215,507903].

Thus every history meets GAWN9's proved late native-repair premises.
Initially the two native configurations correspond: the actual intact
early and late rows have canonical geometry, common reference clocks
and zero flags. The closed-guard identity, plus corresponding overwrites,
proves native correspondence by induction through q. GAWN9's universal
14337-update native bound after the last possible fault therefore gives
the stated early native recovery. Its late full-SF confinement and
through-U native claims are **not** transferred: early SF scheduling and
the later Workspace window differ. The covariance proves only the needed
native prefix. GAWN18 handles the subsequent full physical execution.

## 3. Voted Info damage stays in A despite repeated overwrites — proved

Throughout the prefix, computed Address is canonical and matches raw self,
and computed Age excludes both Info write events0 and80Q-1. Hence each
physical Info holder receives exactly the old logical Info vote at its
own logical coordinate, regardless of its computed clock or Flag1. All
holders of a logical position receive the same word on every normal
update. Neither malformed Heads nor any other SF field can change this
Info equation; the early active Head windows are closed as well.

The five holders of logical y form {y-2,y-1,y,y+1,y+2}. If y lies outside
the integer interval A, at most two holders lie inside A. Starting with
the actual coherent Info of F(H_2), a normal update reproduces its current
logical vote coherently. A subsequent overwrite can change at most two
of the five holders of any y outside A, so its bitwise vote stays exactly
the original word. Induct over all normal updates and all after-row
overwrites. This proves logical Info equality outside A through q; inside
A arbitrary words are allowed. There is no spatial Info transport on this
prefix, so corrupted values cannot drift beyond A.

At q define dprime[g][i] to be the voted Info at gQ+P+i, for each of the
496 frame words. Use the remaining logical Info as an auxiliary Bprime.
All are legal Word100 values. Since A is within colony0, dprime differs
from cell_words(H_2) only at upper index0. Bprime may be arbitrary in
colony0, and raw Info need not be coherent at the premise row. All other
SF may be arbitrary. Native recovery and1<=q<=32Q-1 now give exactly the
premises of GAWN18 for E(dprime,Bprime).

## 4. One upper cell at the actual age0 initializer corrects completely — proved

Let v be any legal upper A_2 configuration equal to H_2 outside upper
physical site0. Each right/left five-native voter has at least four clean
neighbors. Adjusted Address and Age quorums therefore equal their clean
values, including at the damaged site. Apparent colony is canonical.
Left in-colony inconsistencies and Workspace counts are at most one;
the right Flag1 count is at most one, excluding both its three-on and
old-self/two-keep predicates. Thus computed Flag1 is zero everywhere.
Missing-colony and Workspace2 sources vanish. An old Flag2 one can occur
only at site0, where the h1 erasure predicate has left-inside count0<=1.
Every other site fails the four-left turn-on threshold. Computed Flag2
is therefore zero. Computed Age is globally1, so both Workspace outputs
are zero. There is no GF wipe because computed Flag1 is zero.

Every logical SF vote has at least four actual clean holder values. All
old logical operands consequently equal those of H_2, including arbitrary
packet/register/memory words of the damaged cell after legal decoding.
With the same computed native fields, the full physical SF equations
produce exactly F(H_2). This includes the actual age1 Mail load and central
History capture. Hence F(v)=F(H_2) as complete infinite raw configurations.
It is a one-cell result at the actual upper age0 initializer; no arbitrary
triple contraction identity is used.

For dprime in D, native projection pi changes only its potentially damaged
site0, and every SF representation word is unchanged. Its other records
are H_2. The same argument therefore proves

    F^D(dprime)=F(H_2).

## 5. Complete current boundary — proved using GAWN18

Apply the proved two-good-gather theorem at q with dprime and Bprime.
It derives both later physical gathers, all needed private preparation,
own early/late executions and the complete reset/old-Out commit from the
actual history. It gives X_U=E(F^D(dprime),0). Section4 identifies this as
E(F(H_2),0), and GAWN2's period theorem with H_2=E(cell_words(H_2),0)
identifies it as F^U(H_2). Determinism and no later errors give all-tick
equality after U. No native agreement across the later Workspace window
is presumed; the equality argument supplies the actual reference
execution there.

## Checks, statuses and limits

The checker supplies selected scalar/full-kernel clock-translation
cofactors, actual H_2 one-upper-cell output comparisons, interval/holder
confinement counts, and integer clock-band/deadline inequalities. They
are finite measured transcription supplements. The universal claims use
the word/quorum/holder/covariance inductions and antecedent native/period
proofs. No evolving full-SF14337-step or U-tick physical simulation is run.

| Step | Status | Scope |
|---|---|---|
| Canonical GF/no wipe/early clock band/closed Workspace | proved | Every admitted adaptive history |
| Native clock-translation covariance | proved | Canonical GF; both actual Workspace guards closed |
| Native quiet by14337 after last fault | GAWN9's proved native argument applies | New covariance supplies changed phase premises |
| Voted Info damage confined to A | proved | Actual normal updates and every after-row overwrite |
| Full one-upper-cell correction at H_2 age0, including D padding | proved | All legal replacement words |
| Two good gathers/complete current-U and later equality | GAWN18/GAWN2 proved arguments apply | Premises derived from actual early history |
| Scalar/kernel/holder/range checks | measured transcription supplements | No full evolving physical simulation |
| Error-class assignment from support alone | not made | Original real1 sets must independently satisfy the definition |
| Arbitrary GF/Age, other phases, surrounding E0, higher/iid/memory | unproved | No positive-rate reliability theorem |
| Faithful Gray/G17 refutation or minimum sufficient global fix | unproved | All GAWN2 departures remain |
| Rule/ROM/constants/CURRENT change or commit | none | Earlier frozen assets preserved |
