# Unregistered SP30 period-regeneration argument: not yet a theorem

Historical working draft. The finite actual-history composition is now
proved separately in [SP30_FINITE_REGENERATION.md](SP30_FINITE_REGENERATION.md)
for6<=p<TF, with H_TF obtained at the boundary. The unresolved assembly
claims below record this draft's earlier status; they do not supersede
that finite proof. Permanent recurrence, p>=TF and general noise remain
unproved. This draft itself is not a certificate.

This is a working argument for the unchanged frozen F30, not an
accepted proof or receipt. J210 proves the new left local contract;
J208 proves the right local contract and J207 the translating pulse.
The uniform physical execution/store lemmas below still require
review. No infinite glider, finite long-history theorem, general
eroder failure, Gray counterexample or iid conclusion is claimed.

## Proposed finite theorem

Use exactly J191's intact clock0/native17Q overwrite and arbitrary
original upper Info on Z, with no later errors. Define

    K_p = 128-6p, R_p = K_p+6,
    H_p at computed time pU, Q=1024, U=475136, TF=278401.

Aim to prove H_p for 6<=p<TF, and therefore actual pulse endpoints
T(K_p-6,K_p) at pU+TF+6144 throughout that finite range. Each
endpoint would have wrong GF interval

    [(K_p-6)Q-512, K_p Q), width6656.

It would move through negative colony indices without assuming
concrete periodic upper data. This horizon stops before the upper
Workspace1 time window: extending it to all time is a different
problem. Such a finite lifetime still would not by itself disprove
an iid reliability theorem or a specified real-error shadow bound.
Those quantifiers would need their own comparison.

H_p consists of actual physical properties, not re-encoded states:

* Native T(K_p,R_p) at lower Age0; all807 reset bits zero.
* The foreign GF source bank B(K_p,R_p), i.e. all five Info copies
  of jQ+571..580 for K_p-1<=j<=R_p-1, is zero.
* All five Info copies of every physical alias3/509/515/1021
  moduloQ are zero. This is an additional explicit boundary
  invariant; native T and private807 reset alone do not imply it.
* Normal GF/Age/F1/Workspace1 Info holders are canonical GF jmodQ,
  age_code(p),0,0 for all j<=K_p-3. At j=K_p-2 only canonical
  GF and F1zero are required; its other fields are free.
* Normal GF Info holders are zero for K_p+6<=j<=K_p+28.
  Their Age, F1, Workspace1 and every other field are free.
* Every other Info/private value is left as its actual history value.

Age uses radix928/position10bits/512blocks. It is incorrect to
substitute ordinary contiguous increment or age_code(p)=p once
p>=928. Only monotonicity, legal increment and nonzero code(p)
for0<p<U are needed below.

## Bootstrap to review

J205/J206 give T(92,98), reset and B(92,98) at6U. The sixth-boundary
source proof in J206 gives full native words through89, GF/F1
at90, zero GF at104..120 and recovered zero GF at98..103.
Thus K6=92, full left<=K6-3, edgeK6-2, right98..120=K6+6..K6+28.
Review the actual stored-holder bridge, not just the raw cofactor
summaries, before accepting this as the full H6 bootstrap.
The actual A30 commit identities also supply the alias invariant:
both possible GF phases and every holder slot exclude those aliases.

## Signal supply proposed from H_p

Quiet T and fresh reset should let each complete true and foreign
frame run the same own programme before TF. Its three actual
gathers use the two persistent F1 strips. A local lemma is enough:
every unmentioned captured bit can remain arbitrary, so no complete
upper-data reconstruction or old damaged private trajectory is needed.

The alias condition above was made explicit during the next review.
Without it, arbitrary initial MF509 in true/partial frames is not
forced to0 by the native/private-reset hypotheses. It must come
from the actual previous commit, not from a newly chosen encoding.

On the left J210 gives F1zero for j<=K-6, F1one atK-4,-3,-2
and a free bit atK-5. The corner condition is satisfied by K=128-6p:
K is even, KmodQ0 iff p=192mod512, and code(p) is nonzero.
At p<TF the needed Workspace1 output remains0.

On the right J208, R=K+6 and B=K+28 give GF0/F1one at
K+6..K+23. This uses only the right zero-GF source prefix and
the erasing strip [(R-1/2)Q,RQ), not a shared upper Age or
GF-selector assumption.

J195's bank/own-programme bridge should supply MF509oneK..K+5.
The actual A30 commit mask and virtual509 carry identity should
make MF509zero elsewhere and MF1021zeroK-1..K+5, including
both partial aliases. Complete true frames write their actual
F1 signals at MF1021 before TF. Consequently J207's prescribed
80-colony window is supplied; all farther right and left signals
outside that window may be free and correlated.

**Open physical obligation A:** prove that the actual reset/head,
three gathers, Hold output and courier argument used for the
sixth/seventh period localizes uniformly to this quiet T(K,K+6)
start, with arbitrary other Info, for every K and every legal
captured A. The programme is branchless and its lower clock/timing
is unchanged under integer Q translations, but this alone is not
a proof of the damaged-boundary localization. Check partial-frame
arrivals, five-holder source stabilization and actual store-before-load
ordering. This is the chief reason this document remains unregistered.

The separate [conditional physical protocol](SP30_QUIET_FRAME_PROTOCOL.md)
now proves the gather/evaluator/early-courier/Match implication from
actual global quiet-native geometry/clock/keep, fresh reset and actual
own ROM. It allows arbitrary initial raw Info votes. All26 Match
word bits are handled; the22 key bits are a different count. A's
remaining obligation is to discharge that protocol's native-history
and reset premises from H_p, not to assume them as a new encoding.

## Pulse and source renewal arithmetic

Conditional on A, J207 gives the actual pulse T(K-6,K).
Its all-row GF support hull is

    [KQ-7616, (K+6)Q].

Every full true frame j<=K-9 has SF holder footprint [jQ+1,jQ+1023]
strictly left of that hull. The new edge j=K-8 only needs early
GF59..68 and F1phase88 Hold groups; all five holders plus radius37
end by (K-8)Q+127, giving449 sites of clearance before KQ-7616.

J210 already computes canonical GF/code(p+1)/F1WF1zero
for all j<=K-6. If the actual full-period head/store bridge survives
on the protected full frames, this supplies the new full prefix
j<=K-9=(K-6)-3. The protected edge's early GF/F1 is enough
for (K-6)-2=K-8; no late Age/Workspace1 is needed there.

The recovered true colonies K..K+5 start foreign. Their normal
GF/F1 holders have Hold0 after the old boundary reset. The unique
normal-phase stores finish before TF in a frame whose phase is
then shifted512, while their opposite-phase stores issue after
TF+6144, after they have become true. There is no eligible store
during the pulse. The existing single-pending-kind proof is essential:
listing clocks alone do not exclude invented stores. Thus their
normal GF/F1 Hold should remain0 through commit.

The old true receivers K+6..K+23 compute GF0 before TF by J208.
Their normal GF holders plus radius37 lie strictly to the right
of the hull, with the smallest coordinate (K+6)Q+20. These zero
Holds should survive and commit0. Union with the recovered cohort
gives zero GF on K..K+23. For new K'=K-6, trim this to
K'+6..K'+28=K..K+22, which is exactly the next23-colony source
prefix. One spare zero source remains; growing uncertainty boxes
are unnecessary.

**Open physical obligation B:** recheck all22 GF/F1 normal and
opposite-phase ROM destinations, pending-kind/keep rules and the
zero-preserving Hold argument for the entire recovered six-colony
cohort and for protected early holders. Explicitly exclude every
later same-phase Hold write despite altered scratch/selector payloads.
Review how a partially wiped true working frame affects its earlier
protected Hold values. J206 proves this for one preceding pulse;
the uniform implication must be stated and proved.

The separate [conditional pulse-store lemma](SP30_PULSE_STORE_PROTECTION.md)
now supplies this destination exclusion uniformly: it rechecks all22
phases/90112 keys, the common-clock/binary-phase pending-kind argument,
330 recovered zero copies and protected stored-value preservation.
Its native-history/initial-reset premises and correct pre-TF stores
are explicit. It does not discharge A or C or supply those stores;
the full recurrence still remains unproved.

J195's conditional bank theorem applies with L=K,R=K+6,
L'=K-6,R'=K: L'<R', L'<=L and R'<=R-1. J207 supplies
binary GF/common clock/endpoint premises. Quiet template persistence
and actual commit identities should give T(K',R') at Age0,
807 reset bits zero and B(K',R')zero at the next boundary.

**Open physical obligation C:** check the template's pre-TF and
post-pulse persistence, corrected refined-self wipe and simultaneous
all-site native/commit premises, without treating an encoded clean
global configuration as the actual damaged one. A complete uniform
bank/reset implication can be reused only after its precise hypotheses
are discharged. Ordinary Info on both sides need not be restored.

## Status

The local signal calculations, corner arithmetic, pulse implication,
protected-holder inequalities and right-prefix trimming are supported
by already proved exact contracts. The new all-period physical
premise-supply argument A/C, assembly of B's conditional hypotheses,
and the bootstrap assembly are
**unproved** in this draft. No iteration is accepted until they are
discharged. No new experiment, rule change, receipt rewrite or commit.
