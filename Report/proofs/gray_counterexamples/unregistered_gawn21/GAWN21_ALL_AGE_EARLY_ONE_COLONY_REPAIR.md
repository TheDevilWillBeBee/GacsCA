# GAWN21: arbitrary clocks in an early address-preserving damaged colony

This uses **unchanged frozen GAWN2**, Q4096/U524288/radius8/Word100/h1/
own beta/lambda24/c104, with all its declared departures from Gray.
No rule, ROM, constant, CURRENT or frozen prior asset is changed.
This is an arbitrary-value deterministic recovery theorem for one early
damaged colony. It is not a positive-rate iid reliability theorem.

## Exact statement

Start with actual row1 F(H_2) of GAWN4's recursively intact initializer.
Write I=[0,Q), and choose a last possible overwrite row L satisfying

    1 <= L <= 32Q-1-R = 120833,
    R=(2Q-2)+Q/2=10238.

On any subset of physical rows1,...,L, after the normal update, replace
any subset of cells in I, retaining their Address. Every other native
or SF field may be an arbitrary legal value, chosen adaptively. In
particular, Age may be any integer0..U-1, and clocks may wrap; all four
native flags and all thirteen SF tracks may change. There are no other
errors. The entire colony may be overwritten on every allowed row.

For every such history, at q=L+R<=32Q-1=131071:

* all native fields are canonical/correct/zero, globally;
* every voted Info word outside I equals its original intact value;
* Info inside I and every other SF field may be arbitrary.

Consequently, as complete raw infinite configurations,

    X_U=F^U(H_2),

and equality holds at every subsequent tick by determinism. This includes
the original104-site/104-row early burst geometry with every legal Age.
It also allows larger supports; no original error class is assigned from
geometry alone. Original-c104 real1 sets independently satisfying these
restrictions are included. Address-changing, multiple damaged colonies,
later phases, continuing surrounding E0/higher errors and iid closure
remain unproved. No epsilon or all-time noisy memory conclusion follows.

## 1. Actual native exterior — proved by GAWN6's one-step argument

Through q the correct outside successor clock is its physical row,
at most131071<96Q. GAWN6's one-step exterior proof therefore applies:
every adjusted Address vote is canonical; the wipe predicate is false;
outside I all Ages are correct and Flag2/both Workspace fields are0;
Flag1 is0 outside I and its left adjacent colony. Inside I every clock,
flag and SF value is allowed. Its outside-Age proof already permits
arbitrary distinct clocks and wrap. Every overwrite stays in I and
retains Address, so the invariant survives all earlier overwrite rows.

No global clock range, SF cleanliness or Workspace1-zero assumption is
made inside I. Raw clocks that would trigger age0 or80Q-1 are permitted.

## 2. Tagged states extinguish actual Workspace2 — proved

After the last possible overwrite let r=t-L. A raw site is tagged if
its Age is the correct clock on that row or its raw Flag1 is1.
GAWN8's tagged-suffix proof is unaffected by arbitrary clocks, wrap,
Workspace or SF. Five tagged right neighbors imply three correct clocks
or three eligible Flag1 ones; the latter force computed Flag1=1. In
the former case computed Flag1=0 selects the correct right clock vote,
and computed Flag1=1 supplies the tag. The right exterior is tagged,
with Flag1=0. At r=1 the last three sites are tagged; their suffix
persists and grows left by at least one site per row. It covers I by

    r0=Q-2=4094,

and persists through q. The common reference clock is still below32Q;
the correct-vote increment has its literal modulo-U semantics.

On every unoverwritten normal output row, a tagged site has **raw
Workspace2=0**, by the actual physical equation:

    Workspace2 can be nonzero only if
    96Q <= computed Age < 98Q, Address<=4, computed Flag1=0.

If the tag is supplied by correct Age, this guard is closed because
the correct physical row is at most131071<96Q. If supplied by Flag1=1,
the explicit Flag1 gate is false. This is independent of the Info bit,
any other SF schedule or Workspace1. Tag and Workspace2 are outputs
of the same normal update, so it is a statement about actual raw rows;
it is not inferred on an arbitrary just-overwritten row.

At r0 every inside site is tagged and every outside Workspace2 is0.
Thus **Workspace2 is globally0 from r0 through q**. Workspace1 inside
I can still be nonzero. A global closed Workspace-age guard has not
been assumed, and no lower bound on arbitrary replacement Ages is used.

## 3. Flag2 front and clock prefix — proved, using h1

Canonical Address makes the missing-colony Flag2 source false. Its
remaining source uses only old Workspace2, now proved globally0.
If all five left old Flag2 bits are0, computed Flag2=0 whatever the
old self bit, computed Flag1, clocks or SF. With old self0, both
four-left turn-on thresholds fail. With old self1, h1 erases it:
left-inside count0<=1 when computed Flag1=0, or all untruncated left
bits0 when computed Flag1=1. Workspace1 can affect computed Flag1,
but cannot invalidate either case. This is GAWN7's component proof;
its use of only Workspace2 is explicit here.

At r=r0+s the first min(s,Q) Flag2 bits are guaranteed0, for s>=0.
The clean left exterior starts this front; established zeros persist.
On row r0+3=Q+1=4097 the first three clocks are correct. At each
of Addresses0,1,2 at least three left clock witnesses are correct
exterior words. Computed Flag2 is0. All right neighbors are tagged,
so either three correct right clocks give the correct right majority,
or three eligible right Flag1 ones force the clean left selector.
The first three remain correct by this same argument.

For s>=3, suppose the first s clocks are correct at r0+s. On the next
row the Flag2-zero prefix includes the next site s. At centers3..s all
five old left clocks are correct and at least three are in-colony.
If the right clock quorum is missing, inconsistency forces Flag1=1.
If it exists but is wrong, those three correct left-inside words
disagree and again force Flag1=1. Computed Flag2=0 then selects the
correct left quorum. If the right quorum is correct, either voter
is correct. Additional Workspace1/propagation forcing only selects
that same clean left voter. The prefix persists and advances one
site per update, without any assumption on the other clock values.

Therefore all clocks and Flag2 are correct globally by

    r_clock=r0+Q=2Q-2=8190.

On that actual output row, every computed clock is the correct early
physical clock, so **both** raw Workspace fields are0 by their guards.
Correct common clocks and zero Flag2/Workspace persist. The remaining
actual Flag1 equation is

    (right-inside ones >=3) OR
    (old self1 AND right-inside ones >=2).

Every true-colony zero suffix grows left by at least two sites per
update and does not retreat. All affected colonies clear simultaneously
within Q/2=2048 rows, including the left adjacent colony. This proves
global native quiet by R=8190+2048=10238. The latest q=L+R=131071 is
still early. Subsequent behavior is supplied by the complete equality
argument below, rather than extending this early guard invariant.

## 4. Exterior Info and complete current-U repair — proved

For a logical y outside I, at least three of its five physical holders
are outside I. Those holders have correct computed clocks throughout
the prefix to q. Every such clock is positive and at most131071,
excluding0 and80Q-1; Address is canonical and wipe is false. Each
holder therefore writes its old voted Info at y, regardless of Out,
Head, Mail, History, courier or any malformed inside SF evolution.
The initial vote is intact. Each normal update has those three clean
witnesses, and any overwrite confined to I alters at most two holders.
Induction proves the exact voted Info outside I on every row to q.
It allows all special Info commits and arbitrary work transport inside
I. No raw-coherence or clean exterior private-work premise is needed.

At q the496-word frame describes some represented-D configuration
dprime equal to cell_words(H_2) outside upper index0. Its one record
may be arbitrary, including native representation padding. Auxiliary
Info Bprime is arbitrary. The actual native fields and logical Info
therefore satisfy GAWN18's two-good-gather hypotheses, with q<=32Q-1
and all other work arbitrary. In particular, the latest q still allows
the actual next32Q reset; no reset is supplied externally.

GAWN19 section4 proves universal one-upper-D-cell correction at the
actual age0 initializer: F^D(dprime)=F(H_2). Four clean native/holder
witnesses and h1 give complete one-update equality, including arbitrary
represented padding. Its proof is independent of the lower fault band.
GAWN18 then gives the actual current-U boundary

    X_U=E(F^D(dprime),0)=E(F(H_2),0)=F^U(H_2),

using GAWN2's represented-D period theorem. It derives actual work
preparation, two later good gathers, both Mem loads, own execution,
the later native Workspace window and boundary commit/reset. None
is imposed as a future command. No later errors gives full equality
at every tick after U.

## Checks, status and limits

Finite supplements check the actual tag-to-Workspace2 implication with
arbitrary SF and selected wrapping clocks, h1 fronts and the first-three/
prefix clauses with Workspace1 allowed, and exterior Info holders at
the latest early reference phases despite arbitrary inside clocks.
Positive Workspace2 controls inside its pulse check that the new
argument uses the actual Flag1 gate rather than a suppressed source.
Arithmetic checks cover every admitted last possible fault row and
every prefix step. Universal conclusions come from the word counts,
literal gate and inductions above. No full evolving10238-step SF or
physical-U simulation is performed.

| Step | Status | Scope |
|---|---|---|
| Canonical GF/no wipe/early native exterior | proved antecedent argument applies | GAWN6 one-step; any inside clock and SF |
| Tagged suffix and persistence | proved antecedent component argument applies | GAWN8; modulo clock updates, arbitrary Workspace |
| Actual raw Workspace2 zero byQ-2 | proved | Tagged normal output, literal Flag1 gate |
| h1 zero front/first3/prefix/all clocks8190 | proved | Only Workspace2 zero needed; Workspace1 arbitrary |
| Both Workspace zero/native quiet10238 | proved | Correct early clocks, simultaneous Flag1 sweeps |
| Exterior voted Info under continuing one-colony overwrites | proved | Three actual outside physical holders |
| One upper defect/full current-U/all-later equality | proved antecedent arguments apply | GAWN19/18/2; actual preparation derived |
| Cofactor/kernel/gate/arithmetic checks | measured transcription supplements | No complete evolving repair simulation |
| GF changes/multiple colonies/late phases/E0/higher/iid | unproved | No positive-rate or memory theorem |
| Faithful Gray/G17 refutation/minimum sufficient global fix | unproved | All GAWN2 departures remain |
| Rule/ROM/constants/CURRENT change or commit | none | Frozen prior assets preserved |
