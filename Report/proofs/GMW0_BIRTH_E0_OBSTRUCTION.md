# GMW0: one E0 Address overwrite suppresses an entire computation head

This is a counterexample to extending the **changed GMW0 primitive** to
E0-transparent native-prefix execution. It does not contradict its quiet
[native-prefix theorem](gray_counterexamples/GMW0_PHYSICAL_NATIVE_PROGRAMME.md),
which assumes an already present coherent head. It is not a counterexample
to G17, Gray's completed construction, or iid memory. GMW0's frozen kernel,
programme and proofs are unchanged.

Sources: [GMW0 kernel](gray_counterexamples/gray_moving_word_kernel.py),
[checker](check_gmw0_birth_e0.py),
[certificate](../../figs/robustness/GMW0_birth_E0_certificate.json),
[complete local witness inputs/outputs](../../figs/robustness/GMW0_birth_E0_witness.json).
Q=8192, U=1048576, lambda=24 and c=104 are retained.

## Exact statement and witness (proved)

Prepare a quiet physical row at common Age112Q−1. Address is x modQ;
all four native flags, heads, Out and Info are0. Coherent input tapes in
every colony contain the eleven simulated native words

    C[j].Address = j modQ; C[j].Age = 0;
    C[j].Flag1 = C[j].Flag2 = C[j].Workspace.Flag1/2 = 0.

Apply the clean GMW0 update producing Age112Q, which resets heads/Out
and retains this tape. At this row, time1, replace only the Address at
physical site3024 by3025; all its other fields are retained. There are
no later errors. The error-location set is the singleton{(3024,1)}, an
actual E0 set with no real1 error at Gray's original constants.

**Theorem.** On the next update, all physical native fields are again
canonical/quiet, but colony0 has no logical computation head. It stays
headless through the update producing Age0. Its native-prefix Out and
then Info remain0, whereas the clean native-prefix execution commits
simulated Age1. In particular logical Info column2973, the low Age bit,
is0 in the faulty history and1 in the clean history.

This is a native-prefix boundary-output failure of the precisely defined
primitive from a prepared coherent tape. The preparation is not claimed
to be an intact recursively encoded whole GMW0 hierarchy: GMW0 has no
emitted whole own programme or gathering construction yet.

## Proof

At the birth update a singleton wrong raw Address cannot change the
right or left adjusted Address majority at any physical cell: at least
four of its five inputs are correct. Right/left clocks are common. The
inside-left inconsistency count is at most1, below3, and every flag and
Workspace source is0. The literal native transition therefore returns
canonical Address, Age112Q+1 and Flag1/2=0 everywhere. Its SF wipe is
absent. These statements use the explicit native equations, without any
published damaged-colony recovery lemma.

For a holder x and copy displacement s, GMW0's birth equation is

    head_s(x) = initial_packet if old_raw_Address(x+s) == 3024 else ZERO.

The only site with canonical Address3024 in colony0 was3024 itself;
its raw Address was overwritten by3025. No site in that colony now
satisfies the predicate. Thus **all five copies** of its would-be head
are0, including holders x=3024−s for every s in{0,−2,−1,1,2}.
Bit-voting head copies cannot repair this: the rule has written the
same missing-head value to all five copies. The input tape/Out/Info
are unchanged on this update.

There is no further birth before the boundary at Age0. An active
update with no incoming head returns ZERO and makes no Out write;
rest holds voted ZERO; reset also returns ZERO. All coherent tapes
persist. The unaffected neighbouring colonies' heads stay within
their own colonies by GMW0's quiet execution theorem, so no incoming
head crosses either boundary. Native fields remain canonical/quiet,
and the SF wipe remains absent. Induction over these clock classes
therefore gives zero heads and Out throughout colony0 until commit.
At Age0, Info reads old voted Out0 before Out resets, so the claimed
Info bits are0.

For the clean history, automatic birth supplies exactly the coherent
head assumed by GMW0's quiet theorem. The prepared C inputs have
right/left adjusted Address vote0, common Age0, and all sources and
flags0. Literal native evaluation returns Address0, Age1, Flag1/2=0.
The clean programme thus writes low Age bit1 at column2973 and commits
it to Info. This establishes a real output discrepancy, not merely a
missing transient internal head.

## A sufficient local birth-predicate change (proved conditionally)

For logical y, let a(y) be a full-word majority, with an existence bit,
of the five adjusted old raw Addresses

    (old_raw_Address(y+d) − d) modQ,  d = −2,−1,0,1,2.

Replace the raw birth comparison by `exists(a(y)) && a(y)==3024`.
This is an **explicit proposed equation change**, not applied to GMW0.
When the computed birth clock is correct, the computed SF wipe is absent,
and the old geometry is canonical apart from at most two arbitrary Address overwrites in
this five-site window, at least three adjusted words equal y modQ.
Their full-word majority exists and equals that value. Every holder
therefore installs precisely the correct birth head; faulty values
cannot create another head. A holder uses inputs x+s+d∈[x−4,x+4], so
the whole component still fits radius5. A fixed default when no majority
exists completes the proposal on other raw states, without claiming
their recovery.

This proves correction of **this birth predicate under its stated
geometry/clock/no-wipe premises**. It is not a smallest sufficient reliability
change. Noisy service-position reads, computation, collisions, gathering,
own-programme fit and higher-error recovery remain separate obligations.

| Step | Status | Limit |
| --- | --- | --- |
| Singleton is an admissible E0 set | proved | Original lambda24/c104; one site/time |
| Native fields repair, but all five head copies are absent | proved | Exact raw-GF birth equation and singleton majority argument |
| No head/no write until commit; wrong simulated low Age bit | proved | Prepared coherent tape; no later errors; no whole hierarchy |
| Retained complete local input/output comparisons | measured checks | Reproducible witness, not the basis of the induction |
| Five-site adjusted-GF birth vote corrects up to two corruptions | proved conditionally | Correct birth clock/canonical surrounding geometry/no SF wipe; explicit unimplemented change |
| GMW0 quiet theorem, G17 or Gray/iid reliability refuted | unproved; not claimed | This witness excludes only the proposed E0 extension of GMW0 |
