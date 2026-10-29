# SP30: a left-source contract with arbitrary shared Age

This concerns the frozen, explicitly changed SP30 rule F30,
Q1024/U475136/radius37. No rule, ROM, layout or constant is changed here.
It proves a complete local-function contract and a conditional gather
corollary. It does **not** supply the actual sources, controls and
store/commit bridge in every later period.

[Checker](check_signal_reservation1024_left_source_contract.py),
[certificate](../../figs/robustness/SP30_left_source_contract_certificate.json),
[own-rule theorem](SP30_OWN_RULE.md),
[right-prefix contract](SP30_ZERO_GF_PREFIX.md), and
[conditional translating pulse](SP30_TRANSLATION_CLASS.md).

## Exact local statement

Fix integers K and j<=K-2. Write r=K-j. The following assumptions
concern captured **raw input words** for the complete local function,
at every input offset on which the indicated fields depend. Write
col=j+d for the input at offset d.

* If col<=K-3, its GF is col modQ, Age is one common raw19-bit word A,
  F1 is0 and Workspace1 is0.
* If col=K-2, its GF is col modQ and F1 is0; its Age X and
  Workspace1 are completely free.
* If col>=K-1, its GF, Age, F1 and Workspace1 are0.

Every other raw field and instruction input is free, including F2,
Workspace2, private fields, Info and service controls. A and X are
initially arbitrary bit patterns, including unused Age words.

The literal complete-function outputs satisfy:

1. GF_new=j modQ for every r>=2.
2. If r>=6, F1_new=0, Age_now=A and Age_new=inc928,512(A).
3. If r=2 or3, F1_new=1, Age_now=A and the same Age increment holds.
4. If r=4, F1_new=1 whenever K modQ is outside {Q-1,0,1}, or A!=0.
   No fixed Age_new is asserted for r=4 or5, and F1_new for r=5
   is unrestricted.
5. If 0<=A<age_code(TF), Workspace1_new=0 for every r>=2.

Here TF=278401. The actual packed Age has radix928, position width10
and512 blocks; **it is not ordinary increment modulo U in a contiguous
19-bit integer code**. inc928,512 is the actual mixed-age increment on
all raw words. For legal A=age_code(p), p<U-1, it gives age_code(p+1).
The Age_now clauses are statements about the actual maintenance
intermediate used by the complete function, not additional outputs.

The exceptional A=0 case is real. At r=4, K modQ=0 and A=X=0,
F1_new=0 for every setting of the other free fields. Thus omitting
the nonzero-A or coordinate condition would give a false local lemma.
This is a prepared local example, not an actual later fault history.

## Why distant refinement leaves the captured pairs unchanged

For each refined logical offset u in[-5,5], the four five-word
refinement blocks have centres u-30,u-10,u+10,u+30. Inside the block
centred at u+c, its member at u+c+v, v=-2,...,2, has GF adjusted by
-(c+v)modQ. A non-erased member therefore has GF (j+u)modQ.
The erased members have the distinct adjusted GF residues -(c+v)modQ.
Since Q=1024>4, at most one erased member can have the canonical GF.
There is at most one edge member carrying X.

Any three-member quorum of GF/Age pairs must consequently have
canonical GF, and it must include a strict-left member carrying A.
Its Age is therefore A too. This reasoning holds when A or X is0,
when A=X, and when they differ; it assumes no numeric payload value.
Any valid block result is exactly ((j+u)modQ,A).

If j+u<=K-3, that result is already the raw pair. The joint3/4
quorum either substitutes that same pair or retains it. If j+u>=K-2,
both blocks to its right consist entirely of erased members and have
no GF quorum. At most two blocks are valid, so joint3/4 retains the
raw pair, including the edge's arbitrary X or the erased pair(0,0).
Thus refinement leaves **every** relevant raw GF/Age pair unchanged.

The checker exhausts the1024 possible K residues, r=2,...,43,
eleven offsets and four blocks. It checks the cohort counts used by
the argument, without choosing an Age or private payload. At r>=43,
even the rightmost source j+37 is<=K-6, so all refinement words are
strict-left. This supplies the remaining infinitely many distances
by the same canonical/common-pair argument. Integer Q translations
cover all K, including negative colony indices.

## The native vote and the complete outputs

The five adjusted native left GF words are all j modQ and their
five Ages are A. Their left majorities exist with those values.

For r>=6, at least the first three right neighbours are strict-left,
so their adjusted GF and Age majorities are j modQ and A. Three
right raw pairs also satisfy the actual joint and quiet-joint checks.
Every captured F1 is0, and at most one captured Workspace1 is free;
all inconsistency, flag and Workspace1 quorum terms are consequently0.
Both geometry/clock choices coincide, regardless of F2 and service
force. This gives GF_new, Age_now, Age_new and F1_new as stated.

For r=2, all five right GF words are erased and their adjusted
residues are distinct. For r=3, one right GF is canonical and the
other four are distinct erased residues; none can form a three-word
quorum. In either case exists_right=0 forces F1_new=1 and forces
the actual selector to the valid left GF/Age pair, irrespective of
F2 or other free inputs.

For r=4, the first two right adjusted GF words equal j modQ;
the other three are -3,-4,-5 modQ. A right GF quorum exists precisely
when j modQ equals one of those residues, namely when K modQ is
1,0,Q-1. When it exists, its GF equals the left GF. There are at
least three right Ages0, so the right Age majority is0. At all three
coordinate corners, each of the five left neighbours is inside the
actual vote's non-wrapping colony range. If A!=0, at least three
left Age mismatches force F1_new=1. Outside the corners the missing
right GF quorum does so. With A=X=0 the corner quorums and quiet
checks pass and the sole free edge Workspace1 cannot form a quorum;
F1_new=0. This proves the claimed exception as well.

For r=5, three right adjusted GF words are canonical, so both
GF choices still equal j modQ. Their Ages are A,A,X,0,0. Any
three-word Age quorum is A or0; otherwise the actual default is
self Age A. Hence Age_now belongs to {A,0}. The same is true
at r=4. At r=2,3 or r>=6, Age_now is A. Therefore, under
0<=A<age_code(TF), Age_now is always below the complete rule's
Workspace1 time window, whose lower endpoint is age_code(TF).
The actual Workspace1 output is0, regardless of Info and the
GF end guard. No conclusion is drawn about its other outputs.

The checker invokes the actual maintenance function with all Age,
F2, Workspace2, service-force and edge-Workspace1 bits symbolic.
It exhausts all K residues and the seven native boundary types
r=2,...,8. It verifies GF, the fixed F1 values and the claimed
mixed Age increment structurally. The three coordinate corners
are covered for every nonzero A by19 overlapping cofactors, each
fixing just one A bit to1 and leaving the other18 free. It also
checks representative complete netlist cofactors, leaving all
unmentioned native/private/Info/instruction bits free. These checks
supplement the preceding algebraic proof; they are not sampled
whole-automaton trajectories.

The checker's additional absorption identities are
AND(a,OR(a,b))=a and OR(a,AND(a,b))=a. Each is verified on all
two-input Boolean cases. They preserve the actual Boolean function
and do not change the rule or its retained compilation.

## Conditional actual gather corollary

Consider a true receiver j<=K-2 in a frozen SP30 work period.
Assume its actual normal-phase captures, own-programme controls,
uncontested routes and output-store/commit bridge have the already
proved protocol. Assume the source Info holders used for GF, Age,
F1 and Workspace1 are canonical/common-A/zero/zero at col<=K-3;
at col=K-2 assume only canonical GF and F1zero. Assume the
physical F1 strip[(K-1)Q,(K-1/2)Q) is present throughout every
crossing capture. No constraint is needed on source words farther
right, as long as no competing arrival replaces the certified route.

All indicated normal phases59,...,90, including their five holders,
lie strictly to the left of the strip's right endpoint inside the
colony K-1. A source with col>=K-1 either starts inside the strip
or crosses its512 sites en route to the receiver. Stride8 cannot
skip the strip. Actual Mailbox clearing erases the captured bit to0.
Sources with col<=K-2 and their receiver lie to its left and their
routes do not cross it. Thus the captured inputs have exactly the
local form above. The own-programme theorem supplies the computed
outputs, and its assumed store/commit bridge supplies stored words.
This proves the corollary with its premises explicit.

The checker verifies the route predicate at every actual dependency
offset for these fields, every relevant normal phase, five holders,
and r=2,...,38. For larger r all sources are left of the strip.
All integer translations follow from the affine route arithmetic.

For the proposed actual translating sequence K=128-6p, p>0,
K is even. Its sole possible corner is K modQ=0, where
p=192 mod512. Legal A=age_code(p) is nonzero whenever
0<p<U. Thus the r=4 signal is covered throughout that range.
Workspace1 is covered only while p<TF. This arithmetic verifies
a condition **if that sequence and its source words are supplied**;
it does not prove the sequence or ignore higher-level activity.

## What remains

The source and strip premises, lower programme controls, captures,
private resets, partial-colony aliases, Hold timing and commit
protection still require an actual-history induction. In particular,
J207's conditional pulse output cannot simply be fed back as its
next input: six required right commands must be regenerated by
the programme. The present left contract and J208's right contract
make that induction more explicit; neither supplies it alone.

| Step | Status | Limit |
| --- | --- | --- |
| Raw-pair refinement identity and complete local GF/F1/Age contract | proved | exact captured half-plane assumptions; raw Age and other fields free |
| Workspace1zero extension | proved | 0<=A<age_code(TF) |
| Actual gather and stored-word corollary | proved conditional | stated sources/strip/routes/control/store premises |
| Coordinate-corner arithmetic for K=128-6p | proved conditional | p>0 and legal nonzero Age; no history supplied |
| Supply for every actual later period or permanent travelling defect | unproved | compositional physical induction remains |
| Full decoded data/general noisy repair/higher map/positive iid epsilon | unproved | no all-level noisy induction |
| Gray/Gacs verbatim applicability or smallest globally sufficient change | unproved; not claimed | SP30 is a separately changed rule |

The earlier prepared probes with
[plain constant folding](../../figs/robustness/unregistered_symbolic_left_clock/receipt.json)
and [absorption](../../figs/robustness/unregistered_symbolic_left_absorption/receipt.json)
are retained. Their unresolved nodes were not concrete counterexamples.
The theorem above does not infer a universal statement from those55
prepared probes. No active G17/CURRENT or frozen SP30 change and no commit.
