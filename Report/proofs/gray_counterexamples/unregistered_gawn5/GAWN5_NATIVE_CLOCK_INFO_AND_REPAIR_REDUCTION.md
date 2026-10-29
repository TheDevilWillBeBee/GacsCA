# GAWN5: native clock damage with actual Info supply, at the smaller scale

This checkpoint concerns the **unchanged frozen GAWN2** rule:
Q4096, U524288, radius8, Word100, native12/19-bit fields, beta_2,
100Q reset/100Q+1 late birth, lambda24 and integer c104.
Its existing departures from Gray remain explicit in
[GAWN2](../unregistered_gawn2/GAWN2_HALF_SCALE_NOISELESS_PERIOD.md).
No rule, ROM, schedule or constant is changed.

There are two different results here. A native/Info projection and a
full-period **reduction conditional on a native history** are proved
below. Sixteen executions of that projection are retained as finite
experimental receipts. They include genuine native-changing original-real1
faults and positive actual Workspace supply. They are not an arbitrary
real1, continuing mixed-noise, higher-error or positive-iid theorem.
A complete two-period physical simulation was not run.

## Actual initialization and fault

Let H_2 be the infinite recursive initializer proved in
[GAWN4 §1](../unregistered_gawn4/GAWN4_LATE_SF_BURST_REPAIR.md):
H_2=E_2(H_2,0), with the frozen own beta and coherent five-holder Info.
Use its actual noiseless physical history until row

    T=100Q+2=409602.

The noiseless period theorem gives canonical GF, AgeT and zero native
flags at that row. At every normal represented primary, Info still holds
the corresponding H_2 representation word. Both special margin
primaries3/Q-3 contain0: the actual early upper flag calculation on H_2
gives0 and the old couriers deliver0. All Mail tracks are0 after96Q.

For each f in0..15, make exactly one after-update overwrite at every
physical site x=0..103 on rowT. Retain Address and every SF field, except
the five Info-lowbit holders specified next. Set

    Age=A=96Q-1=393215,
    (Flag1,Flag2,Workspace1,Workspace2)=the four bits of f.

For h with slot s_h in(0,-2,-1,1,2), replace bit0 of Info[h] at
physical holder x=3-s_h by1. These five holders are1..5, all already
inside the burst. Retain every other bit, including their actual
pre-fault SF words. This is a coherent logical Info-lowbit change at3,
not an assigned future Workspace command. No later errors occur.

The support S={(x,T):0<=x<104} is one original-c104 real1: all sites
actually change Age, no singleton/adjacent pair is isolated from the
other sites, there are disjoint linked candidate0 pairs, all coordinates
fit one104-by1 box, and all candidate1 subsets are c-linked.
The exact repository classifier receipt verifies these conditions.
This family is not a generic150-wide real1 cluster.

## 1. Projection theorem — proved

For the first L=4Q=16384 updates, the complete native trajectory depends
only on the six native fields and the fixed special Info-lowbit function

    J(gQ+3)=1 if g=0, otherwise0;
    J(gQ+Q-3)=0 for every integer g.

Other SF bits may evolve arbitrarily through the actual rule.

First, GF stays canonical. Every adjusted left and right GF word equals
x modQ, so either native voter gives that word, regardless of clock and
flags. The raw-self GF wipe is always false.

Second, every raw clock at relative rowt is either T+t or A+t.
This follows by induction: a whole-word majority, or its self fallback,
selects one old class, then adds1. There is no modular wrap withinL.
Every such value is strictly above80Q-1 and belowU. Thus neither Age0
commit nor the special80Q-1 Info write can occur in this interval.
The actual SF Info equation is consequently just its five-holder vote.
The initial full Info words are coherent, including the changed bit at3;
the vote therefore preserves them at all five holders independently of
their possibly different clocks. This proves that J is the **actual**
computed-primary lowbit, even when the source's native Flag1 is positive:
GF wipe is absent and the two exceptional write ages are excluded.

Consequently Workspace1 is0 on every update, since its own Q-3 source
is0. Workspace2 is precisely

    1_{96Q<=newAge<98Q} * 1_{newGF<=4} *
    1_{computedFlag1=0} * 1_{true colony is0}.

This is the actual source equation, including its computed reader guard.
It is not chosen externally.

The emitted C projection is a direct transcription of the remaining
native equations. Canonical GF makes apparent C exist and every GF
mismatch predicate false. With inside(j) meaning0<=GF+j<Q, it uses
the actual right Age quorum/fallback, left Age quorum/fallback,
left inside Age disagreement, right inside Flag1 count, old native
Workspace quorums and the h1 Flag2 branch. Missing-C Flag2 source3 is
identically false. The final Age selector is right iff computedF1=0
or computedF2=1. These reductions follow algebraically from
small_rule_gawn2.scalar_native and _physical_transition.

The C module is a **projection of this existing rule**, not a new CA
and not a full SF simulator. Its420 random full-local-kernel comparisons
use canonical GF, both clock classes, arbitrary old native flag bits,
coherent special lowbits and arbitrary other legal SF payloads. Those
comparisons are measured transcription supplements, not the proof of
the above quantifiers.

The six-colony domain has origin-3Q. Its omitted exterior is the actual
canonical clock/zero-native-flags reference. The run rejects any changed
native value within20 sites of either boundary. Radius5 native
dependence plus the proved constant source permits the recorded domain
to be lifted to the infinite line by induction; no periodic wrap is used.

## 2. What the sixteen finite executions show — measured

Each case runs the closed projection to its first all-native quiet row.
The retained integer event rows and final native arrays report:

* maximum first Age equality:2566 updates;
* maximum first full native equality:4095 updates;
* every wrong-Age position stays inside true colony[0,Q);
* the wrong-Age union reaches4095 in several cases;
* the largest instantaneous wrong-Age count/span is2799;
* the largest native flag support is5534 sites;
* cases with an actual supplied Workspace2 have167 site-updates of it.

The f=0 case gives the largest Age excursion: despite an original
104-site fault, wrong Age reaches the right end of the colony and
passes through the ordinary computation frame[P,P+496), P1800.
A proof cannot assume that late native errors remain inside an empty
margin or that this computation continues with the clean clocks.
The f=1 case transports a narrow clock defect across that frame too.

The first measured quiet rows precede4Q=U/32, but these16 cases do not
prove that bound for arbitrary native payloads or surrounding E0 noise.
No GF-changing error is included.

Files: [source](gawn5_clock_info_projection.c),
[checker](check_gawn5_clock_info_projection.py),
[receipt](../../../../figs/gray_counterexamples/unregistered_gawn5/GAWN5_actual_clock_Info_probe.json).
The initial receipt/checker and terminal log are retained separately.

## 3. A complete-boundary repair reduction — proved conditionally

Here is the precise additional use of such a native history. Suppose
the above actual fault history satisfies, up to some T+r<U:

1. GF stays canonical, and native Age outside true colony0 stays at
   the correct global clock.
2. Every computed Age before recovery lies in[96Q,U), so there are
   no gathers, moving couriers, special Info writes or commits.
3. At T+r all six native fields equal their clean values everywhere,
   with T+r>100Q and beforeU. No further errors occur.

The projection proves item1 for GF and item2 for the entire certified
prefix. The sixteen receipts supply the remaining finite native
confinement and quiet-row evidence. The conclusion under these
hypotheses is

    X_U=E_2(dprime,Bprime),
    dprime[g]=cell_words(F_2(H_2)[g]) for g!=0,
    X_2U=F_2^(2U)(H_2).

It is complete raw equality at2U, conditional on the stated actual
native history, and needs no legal-native-padding premise atU.

Proof. Both Mail tracks start0 and remain0: every admitted clock is
after all gather movement/snapshot windows; reset and Flag1 erasure
also give0. The other native flag variation can only affect SF through
the raw-self GF wipe, which is absent. No courier movement is selected;
old couriers are0, resets preserve0.

Packet endpoint protection also survives different holder clocks.
Initially no forbidden outward movement bit is present at either
logical endpoint. At a reset/birth the bit is0; at a holding update
the old five-holder vote preserves0; at every active update the total
step_packet target<Q guard gives0 at the corresponding endpoint.
Collisions and invalid instructions give stationary ERROR. This is
the same total packet argument as GAWN4 §3, now applied separately to
each computed holder. Therefore no head can cross a true colony edge.

For a logical site outside colony0, at least three of its five holders
are also physically outside that colony. They have correct computed
clock and GF, no wipe and zero Mail. Assuming the old logical votes
match the clean run outside colony0, their outputs match as well:
all non-head SF operations are local to that logical site; head
incoming across the sole edge from colony0 is blocked by the endpoint
movement invariant. Programme is always the correct beta bit.
The other at most two holders cannot change the next majority.
Induction gives clean logical SF votes outside colony0 for the whole
prefix. This includes logical sites immediately adjacent to its edges,
although individual physical backup copies there may disagree.

At recovery all raw Ages agree with the global clock. Every computed
holder thereafter uses that same clock and its canonical logical
service Address. Each complete SF update now has five coherent copies:
the only Flag1-dependent SF field is Mail, already0, and the wipe is
absent. Thus every SF field rejoins coherence on the next update.
Native flags stay0 untilU because the common clock is past the
Workspace pulse and no further source is open.

The ensuing old-Out commit atU and actual global resets give E_2
of an arbitrary raw496-word upper record in colony0, with arbitrary
coherent auxiliary Info Bprime. Records outside0 are the exact clean
C1=F_2(H_2). AtU the native boundary fields are canonical/zero and
the own Programme is correct. Padding in the one damaged upper
record is permitted by D; no new reset/encoding is imposed.

Let Cprime=pi_2(dprime). It differs from C1 in at most the single
upper physical cell0. C1 has coherent SF copies, canonical GF, common
Age1 and zero native flags/Workspace. Four unchanged native voters and
four unchanged SF holders restore every quorum/vote; computed Flag1
is0, so no wipe occurs, and computed Age2 leaves the Workspace guard
closed. Hence F_2(Cprime)=F_2(C1)=C2. This is the same arbitrary-value
quorum argument proved in GAWN4 §5, with one rather than two bad cells.

The universal D-period theorem of GAWN2 then gives

    F_2^U(E_2(dprime,Bprime))=E_2(F_2(Cprime),0)=E_2(C2,0).

The clean two-period row is also E_2(C2,0). This proves the reduction.
It does not identify the actual damaged first Out words and it does
not require the disrupted late interpreter to finish correctly.

## Status

| Step | Status |
|---|---|
| Actual recursive H_2, own beta and pre-fault rowT | Proved previously; GAWN2/GAWN4 apply |
| Original-c104 real1 support and exact replacement recipe | Proved |
| Canonical GF, two clock classes and actual Info/Workspace projection | Proved |
| Sixteen native trajectories/recovery times | Measured finite integer executions |
| Endpoint shield, exterior logical votes, coherent U boundary and2U reduction | Proved under the explicit native-history hypotheses |
| Complete2U instantiation for these16 histories | Argued and measured by the projection receipts and proved reduction; no full2U physical simulation |
| Arbitrary native-changing real1/E0 surroundings/higher/iid threshold | Unproved |
| G17/Gray counterexample, shorter U or globally sufficient minimal change | Unproved; no such claim |
