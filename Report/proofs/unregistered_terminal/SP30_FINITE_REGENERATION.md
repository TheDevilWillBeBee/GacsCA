# SP30: finite actual regeneration before upper Workspace activity

This proof concerns unchanged frozen F30, Q1024/U475136/radius37,
TF278401 and S=TF+6144=284545. It composes previously proved local
and physical implications for the same actual history. No rule,
programme, layout, constant or G17 change occurs. The result is finite;
it does not assert a permanent travelling defect or positive iid failure.

[Checker](check_sp30_finite_regeneration.py),
[certificate](../../../figs/robustness/unregistered_finite_regeneration/certificate.json)
and [run](../../../figs/robustness/SP30_finite_regeneration_unregistered_run.log)
check the finite interfaces and arithmetic. The written induction below
supplies the physical-history composition. They do not simulate all
278395 full work periods. An initial checker accidentally subtracted an
extra four sites from the right reserve; its
[source](../../../figs/robustness/SP30_finite_regeneration_initial_checker.py.txt)
and [failed log](../../../figs/robustness/SP30_finite_regeneration_initial_run.log)
are retained. The correction agrees with J212's literal20-site reserve;
no premise, rule or earlier result changed.

Use exactly [J191's original history](../SP30_FIRST_SIGNAL.md): start
from E30(z) with upper GF(j)=jmodQ, Age0 and all fields other than
GF/Info0, arbitrary upper raw Info, and at lower clock0 shift GF512
on[128Q-512,144Q) and set F1 on[127Q,128Q-512) and[144Q-512,144Q).
Other fields are retained and there are no later errors. An intact
hierarchy is included. Its dense17Q error row is real3 at c16 and
real2 at c104 by the already pinned classifier result; we do not
silently assign it level2 at c16.

The dependencies are [J195](../SP30_GF_BANK_CLOSURE.md),
[J205](../SP30_SIXTH_SIGNAL.md), [J206](../SP30_SEVENTH_SIGNAL.md),
[J207](../SP30_TRANSLATION_CLASS.md),
[J208](../SP30_ZERO_GF_PREFIX.md), [J210](../SP30_LEFT_SOURCE_CONTRACT.md),
[J212](SP30_PULSE_STORE_PROTECTION.md) and
[J214](SP30_QUIET_FRAME_PROTOCOL.md). These are exact proofs and finite
reductions, with actual-history premises where specified. We discharge
those premises below; a conditional pulse endpoint is not simply
reused as its next assumed input.

## The finite theorem

Put K_p=128-6p and R_p=K_p+6. At every computed boundary pU,
6<=p<=TF, the actual physical state satisfies H_p:

1. Native T(K_p,R_p), common lower Age0, and all807 reset bits0.
2. All five Info copies of jQ+571..580 are0 for K_p-1<=j<=R_p-1.
3. All five Info copies of physical aliases3/509/515/1021modQ are0.
4. At normal native primaries, GF=jmodQ, Age=age_code(p), F1=WF1=0
   for every j<=K_p-3. At j=K_p-2 only GF=jmodQ and F1=0 are asserted.
5. Normal GF Info copies are0 for K_p+6<=j<=K_p+28.

All other Info values are their actual history values and unrestricted
in this invariant. No complete global re-encoding is assumed at pU.

For every6<=p<TF, at computed row pU+S, the actual native state is
T(K_p-6,K_p), with common legal lower clock S and empty projected
native/header/pressure auxiliaries. The wrong-GF interval is exactly

    [(K_p-6)Q-512, K_p Q), width6656.

These278395 successive pulse endpoints translate by-6Q each time.
The final proved endpoint is at p=278400. H_TF is obtained at the
next boundary, but applying the next signal argument at p=TF is
outside its upper-WF clock hypothesis. No extrapolation is made.

## Bootstrap H_6

J205 gives T(92,98), common boundary clock/reset and the zero
B(92,98) bank at6U. J206's actual sixth-boundary stored-word argument
gives GF/Age6/F1WF1zero on the full left prefix j<=89 and GF/F1
at edge90. It gives GF0 at104..120; its recovered cohort98..103
has all330 normal GF/F1 copies0. Union gives GF0 on98..120.
Thus these are precisely K6-3, K6-2 and K6+6..K6+28.

The stored-holder qualification matters: we use only GF/F1 at90,
whose late work can be lost. Its Age/WF1 circuit outputs alone would
not establish stored boundary values. Full left frames through89
have the native footprint reserve used in J214; the endpoint-holder
correction1022→1023 leaves540 sites of clearance. J206's protected
right GF Holds have their separate20-site reserve. No full right Age
word is needed here.

At that actual commit, GF is quiet in phases0/512 and computed GF
equals refined self GF. J189's literal A30 mask excludes the four
aliases in either phase at all five holders. Hence the alias copies
are0, independently of old Hold or ordinary-data values. These facts
give all of H6, with no newly selected initial state.

## From H_p to the actual signal

Assume6<=p<TF and H_p. J195's quiet-template argument applies to
T(K,K+6), K=K_p: its four geometry/flag boundaries are512 or more
apart, refinement preserves the raw GF/common clock, and the native
quiet cofactors preserve GF/F1 and F2zero. Empty service/header fields
cannot supply pressure. Epoch birth/force and WF1 guards are closed
at every legal lower clock0..TF-1. Thus induction supplies the
**actual** global quiet interface and keep1 before the pulse, with
common legal clock. This discharges J214's prefix native premise.
Initial807 reset is H_p, actual own ROM is fixed, and there are no
later errors. Arbitrary raw Info is permitted by J214.

All normal source values are consequently their H_p votes throughout
the three actual gathers. Completed captures and the actual evaluator
are those in J214, not inferred solely from a circuit cofactor.

For every true receiver j<=K-2, its native phases59..90 lie to the
left of the strip's right endpoint. Sources at col>=K-1 start in or
cross[(K-1)Q,(K-1/2)Q), and are erased. Sources at col<=K-3 have
canonical GF/common A=age_code(p)/F1WF1zero; edgeK-2 has GF/F1
correct and other fields free. Thus J210's complete local contract
applies to the actual captured assignment, with every other bit and
I free. It yields GFj throughout, F1zero for j<=K-6, F1one at
K-4,K-3,K-2, and unrestricted F1 atK-5. Its WF1 output is0 because
0<=A<age_code(TF). It yields Age=age_code(p+1) for j<=K-6.

The coordinate exception in the F1 atK-4 clause is discharged,
rather than ignored: K=128-6p is even; its only possible corner in
{1023,0,1} is0, occurring exactly when p=192mod512. A is nonzero
for every p in this range. Legal Age uses radix928/PB10/512 blocks;
its actual increment is age_code(p+1), not contiguous19-bit addition.

For true receivers K+6..K+23, apply J208 with R=K+6, B=K+28.
Every required captured GF source on the right is0 by H_p; a source
to the left crosses[(R-1/2)Q,RQ) and is erased. J214 supplies the
actual gather/evaluator/store bridge. GF0/F1one/WF1zero follows
independently of captured Age and all other upper raw fields.

For complete foreign frames hQ-512, h=K..K+5, all native GF
inputs are0: direct/unblocked sources inside the phase-shifted
interval are in H_p's B bank, and outside routes cross a512-site
F1 strip. This is J195's exact bank-route argument with L=K,R=K+6.
The new full-rule GF0 cofactor and actual J214 prefix give early
F1one and GF0, and their actual Hold/courier delivery.

Initial physical aliases are0. Before TS Info carries its old vote;
at TS a virtual509 primary still carries it because only3/1021
are special. All five holders of an alias are on one GF side:
each alias is3 or more sites from the0/512 geometry boundaries.
Consequently the actual special writes give the complete enclosure

    M509=1 exactly atK..K+5, 0 everywhere else;
    M1021=1 atK-4..K-2 andK+6..K+23;
           0 atK-56..K-6 andK-1..K+5;
           unrestricted atK-5 and outside[K-56,K+24).

In particular partial MF509 atK-1 and partial MF1021 atK+5
have virtual509 and remain0. Complete true/foreign courier ordering
is J214's actual store-before-load/travel proof. The enclosure may
have infinitely many correlated free exterior bits; J207 permits them.
Native WF/header/pressure auxiliaries are still0 at rowTF: their
first enabled input guard is TF, after the TS special write. Thus
every initial premise of J207 is supplied by this actual history.

## The pulse and boundary renewal

J207 now gives the actual6144-row projected pulse on Z, endpoint
T(K-6,K), common clock, empty auxiliaries, binary raw/computed GF,
and all-row GF hull[KQ-7616,(K+6)Q]. It gives its Info-majority
facts without assuming raw Info coherence. No unobserved private
trajectory is substituted. J195's closed suffix guards and quiet
native induction maintain that endpoint template/common legal clock
from S through commit. This supplies J212's full native-history
premises and the suffix part of J195's bank implication.

For full true frames j<=K-9, all SF holders1..1023 and native
reads-36..1060 are outside the hull, with at least540 sites of
clearance at the right edge. Common legal Age and canonical native
GF make both geometry choices and refined self GF correct, irrespective
of native flags/service/private values. Hence keep1 and relative
frame control persist. The normal Info special guards are false,
so the source snapshot persists; captures have ended. J214's late
physical induction therefore applies. Its actual coherent26-bit
Match word may be arbitrary: all31 GF/Age/F1/WF1 outputs have no
I dependency, and the remaining Match register values are irrelevant
by the registered post-Match definedness proof. J210 supplies the
desired GFj/age_code(p+1)/F1WF1zero. Complete Holds materialize,
are held in rest, and actually commit at these primaries.

At edgej=K-8, only early GF/F1 are needed. They have already
been correctly computed and stored before TF. J212's449-site
reserve and unique destination-kind argument preserve and commit
them, even if later frame work is lost. This establishes the new
full-left prefix j<=K-9=(K-6)-3 and new edgeK-8=(K-6)-2.

The old true right receivers K+6..K+23 have correctly stored GF0
before TF by the actual J208/J214 bridge. J212's20-site native
reserve preserves their Holds to commit. The recovered normal
cohort K..K+5 has330 GF/F1 copies0 by J212's destination exclusion,
without assuming any evaluator result in those damaged frames.
Union gives GF0 onK..K+23. For K'=K-6, trim one spare colony to
K'+6..K'+28=K..K+22: exactly the next23-colony right source prefix.

J195's bank implication has L=K,R=K+6,L'=K-6,R'=K.
Its inequalities L'<R',L'<=L,R'<=R-1 hold. Its initial B bank/reset
are H_p, its early zero stores are the actual foreign execution
above, and its binary/common-clock/displacement/end/suffix premises
are J207 and the quiet suffix. It therefore gives B(K',R')0 and
the next native template/reset at(p+1)U. Finally the actual A30
commit mask again zeroes every alias3/509/515/1021 in both phases
at every holder. This supplies the next alias invariant.

Every clause of H_(p+1) has now been supplied by the actual history.
Induction from H6 proves H_p through H_TF and all stated endpoints.
No part assumes an encoded fresh boundary except the original start.
QED for the finite theorem.

## What this does and does not decide

The finite regeneration closes the previous eighth/later-signal gap
for this particular error history and this explicit horizon. It does
not prove a permanent defect: at upper clock p=TF the left WF1zero
contract no longer applies, and later upper/native activity must be
analyzed separately. Arbitrary new physical errors are also excluded.

It is not a complete higher-error map or iid memory theorem. In
particular the initial core is level3 at c16, not level2. Its finite
travel should be compared to the correct class and operational
shadow envelope before declaring any reliability argument false.
No Gray/Gacs refutation or smallest globally sufficient rule change
is claimed. F30 and G17 remain unchanged and there is no commit.

| Step | Status | Exact limit |
| --- | --- | --- |
| H6 actual stored-holder/bootstrap and zero aliases | proved | J205/J206 actual history, correct protected fields only |
| Quiet actual prefix/suffix native history | previous argument applies | J195, empty reset/endpoint headers, closed legal guards |
| Physical captures/evaluator/Match/couriers and source enclosure | proved by composition | J208/J210/J214 with actual H_p sources |
| Actual pulse, protected source/bank/reset/alias renewal | proved by composition | J195/J207/J212, no later errors |
| Finite H_p and278395 pulse endpoints | proved above |6<=p<TF; H_TF boundary only |
| p>=TF/permanent defect/general eroder/full data/higher/iid | unproved | upper WF activity and arbitrary noise are outside the theorem |
