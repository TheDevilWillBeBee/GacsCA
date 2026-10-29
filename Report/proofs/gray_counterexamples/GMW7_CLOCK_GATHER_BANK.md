# Actual GMW7 gathering on the intact stationary clock island

This proves an actual **first-gather bank lemma for unchanged GMW7**,
Q8192/U128Q/lambda24/c104. It uses the intact X and single shared
clock-only real2 row in the [accepted clock proof](GMW7_WF0_CLOCK_ISLAND.md),
not a preloaded input bank or independent upper error history. It does
not prove Gray's literal gathering protocol, a Flag2 repair wave, a later
period, decoded memory or iid reliability. GMW7's immutable dictionary,
word IO, single gather and fixed-zero Workspace departures remain.

The [checker](check_gray_clock_gather_bank.py),
[read-only validator](validate_gray_clock_gather_bank.py) and
[receipt](../../../figs/gray_counterexamples/GMW7_clock_gather_bank_certificate.json)
pin the actual [F7 transition](gray_token_gather_v7.py), intact initializer
and accepted native orbit. No existing rule, programme, source or
certificate is changed.
The initial read-only validator compared Python tuple path segments with
JSON lists and failed after the mathematical replays had passed. Its
[source](../../../figs/gray_counterexamples/GMW7_clock_gather_bank_initial_validator.py.txt)
and [failure](../../../figs/gray_counterexamples/GMW7_clock_gather_bank_initial_validator_failure.txt)
are retained. The comparison now uses JSON-normalized regenerated data;
this was a validator serialization defect.

## Actual history and voted-Mem factor

At physical row0 overwrite only Age1 on[0,B), B=17Q. There are no later
errors. Put e(x)=1_[0,B)(x). The accepted native theorem gives canonical
GF and Age(x,n)=(n+e(x)) mod U for every output row n. Its native Flag1
fills colonies-1 and16 by2731; Flag2/Workspace remain zero. SF wipe
never fires because computed GF equals raw GF. Through the first gather
all Info copies remain the intact logical words A(y).

For a logical coordinate y and lane d=-5..5 let M_d(y,n) be the bitwise
majority of its five Mem words at physical row n, taking holders y-s
with s=(0,-2,-1,1,2). It is not assumed that those raw copies are
coherent at clock boundaries. They start zero in X.

**Lemma.** Throughout this first-gather prefix these actual voted words
satisfy

    z = n + e(y) - 32Q;
    M_d(y,n) = A(y)                       if z=0;
             = M_d(y+sign(d),n-1)         if d!=0 and 0<z<=|d|Q;
             = M_d(y,n-1)                 otherwise.

Here n is an output-row number. For lane0 only the load and hold clauses
apply. All expressions refer to actual raw-holder votes in F7.

To prove the factor, each holder x=y-s uses its own computed Age n+e(x)
and computed service Address (GF(x)+s) mod Q=y mod Q. Its Mem output
reads the same old voted logical Mem/Info groups as every other holder,
then applies the F7 load/move/hold operation for that clock. There are
only two possible candidate outputs, one for e(x)=0 and one for e(x)=1.
At least three of the five holders have e(x)=e(y): a symmetric five-site
window on this wide interval step has the centre's label as its majority.
Those three identical complete bank words determine every bit of the new
vote. This gives exactly the displayed centre-clock recurrence, for
arbitrary old raw Mem values. No five-copy coherence invariant is used
at the clock boundaries.

The far raw read for a moved copy is at holder offset s+sign(d)-t,
s,t in{-2,-1,0,1,2}; its radius is at most5. Thus the recurrence follows
from the actual raw local accesses, not from a head-centre oracle. The
checker compares whole1100-bit voted banks against five actual F7
holder transitions on boundary and stage-control classes. Repeating
three identical output words proves the arbitrary-word extension.

## Exact source of every normal-primary capture

Let p range over all191 normal primary residues4001..4191 and y=gQ+p.
Let d be a lane, D=|d|Q, sigma=sign(d), and let e_s=e((g+d)Q+p).
The actual lane finishes at physical output row

    n_c = 32Q + D - e(y).

Its five copies there are coherent, because all five normal-primary
holders have the same clock label. The lane stays fixed afterwards
through the first evaluator: every later update is a voted hold, and
there is no SF wipe or second gather in that interval.

**Capture theorem.** At that row the word is

    M_d(gQ+p,n_c)
       = A((g+d)Q + p + sigma*(e_s-e(y))).

For d0 the shift is zero. For every nonzero lane, backtrack the recurrence
from n_c. In a constant-clock interval, every step moves by sigma and
decreases n by one until the local load row is reached. At a clock jump
only e changes by one. The eventual number of spatial steps is
D+e_s-e(y), since the source load row is32Q-e_s. The resulting coordinate
has residue p+sigma*(e_s-e(y)), which differs from p by at most one and
lies strictly inside its claimed source colony. It has the claimed e_s.
All preceding steps are in the moving interval: the normal receiver and
unshifted target are at least4001 sites from a clock boundary, and the
shifted source is at least4000 sites away. Each crossed boundary
is consequently thousands of steps from either endpoint. There is no
extra hold or uninitialized-bank read on these paths. A lane of length
at most5Q cannot cross both edges of the17Q island.

The checker implements exact constant-clock path compression. At each
segment it jumps either to the local load time or the next crossed clock
boundary and proves that all intervening updates have moving controls.
It then checks the load coordinate and all source words. For integer
g outside[-5,21], no route can cross an island edge, so the same uniform
path proof applies. Testing g=-6..22 covers all interface classes plus
both uniform exterior representatives; the formula and normal-residue
arithmetic prove it for every integer g. No finite ring or sampled time
evolution supplies this theorem.

## The actual flagged-colony bank

At g16, every right lane d1..5 crosses into the outside clock0 region;
its source residue is p-1. Every left lane and the self lane remains in
clock1 and has source residue p. Consequently the actual decoded right
input words are

    C'[d].word[w] = A((16+d)Q+4000+w), d=1..5, w=0..190.

Its right Address inputs use w0, and A at residue4000 is zero. They are
therefore **all five zero**. Its right Age inputs use w1 and are17,18,19,20,21.
Its five left raw Address inputs are15,14,13,12,11 and its five left raw
Ages are zero. Its own Address/Age are16/0. All incoming native Flag2
and Workspace2 bits are zero. These records have legal widths and are
derived from the actual lower Info recursion; they are not chosen upper
states.

Thus the first clause of the
[conditional flag contract](GRAY_FLAG_COMMAND_CONTRACT.md) applies with
A0: the computed upper GF is16, Age1, Flag1 one and Flag2 zero. The
missing-GF source is real, but the divisible-by16 source is false during
this first evaluation. The native lower colony16 is complete and Flag1
one everywhere by this gathering time. Its left-end Flag1 gate would
also prevent a Workspace2 command there even if a source bit were one.

At g15, right lane1 correctly reads Address16; right lanes2..5 have
Address0 because they cross the same clock boundary. This is an actual
**four-null right bank** in a different complete colony whose native
Flag1 remains zero. Its left Age words are likewise zero, so its computed
upper Flag2 is also zero during the first evaluation. This distinguishes
an eligible lower pulse-reader colony from a Flag1-set one without
asserting any later upper Age progression or early source installation.

The omission of Mailbox-on-Flag1 erasure is material. GMW7 gets these
null GF words from the one-tick stagger in its actual load clocks. Gray's
literal gathering additionally clears Mailbox where computed Flag1 is
one and uses three gathers/retained histories. This bank lemma must not
be attributed to that different physical protocol.

| Step | Status |
| --- | --- |
| Intact X, shared single actual-real2 history and all native clocks | **proved in pinned accepted sources** |
| Actual voted-Mem factor without boundary copy coherence | **proved by majority of identical holder updates** |
| Every normal-primary capture formula and retention through the first evaluator | **proved coordinate/control theorem** |
| Fully Flag1-set colony16 has five null right Address words | **proved actual first-bank lemma** |
| Unflagged colony15 has four null right Address words | **proved actual first-bank lemma** |
| Native upper Flag2 triggered during the first evaluation | **false for these banks: computed upper Age1** |
| Later upper Age progression, authentic early flag store and repair wave | **unproved** |
| Gray-faithful three-gather bank, decoded-memory or iid counterexample | **not established** |
