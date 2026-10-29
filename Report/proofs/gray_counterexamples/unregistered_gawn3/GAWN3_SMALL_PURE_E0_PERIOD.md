# GAWN3: continuing pure-E0 simulation by the frozen half-scale rule

This is a new **proof checkpoint for unchanged frozen GAWN2**, not a
new rule, ROM, schedule or constant revision. It uses Q4096/U524288,
lambda24/c104, native12/19 bits, radius8, Word100 and the actual beta_2.
The Word100/radius/immutable-ROM/h1/rest departures from Gray remain.
The theorem below is a restricted deterministic noise theorem. It does
not establish reliability at a positive iid noise rate.

The basis is the complete new-scale noiseless/compiler theorem in
[GAWN2](../unregistered_gawn2/GAWN2_HALF_SCALE_NOISELESS_PERIOD.md).
The two-section voting and native-front proof schema is that of
[GAW3](../unregistered_gaw3/GAW3_PURE_E0_PERIOD.md); its changed-scale
premises are proved here and its new scalar/word checks are rerun.
The [checker](check_small_E0_gawn3.py) never substitutes the older native
scalar, ROM or work-period schedule.

## Exact theorem, initialization and noise model

Let F be the frozen GAWN2 rule with fixed beta_2, and E(C,B) its E_2
canonical/common-clock/coherent/reset encoding. C is any infinite
configuration of its A_2 physical alphabet: all49035 bits per upper
cell are allowed, including arbitrary SF and invalid packet metadata.
B is arbitrary coherent auxiliary Word100 Info. There is no upper
geometry, upper clock, upper holder-coherence or recursive-intactness
premise. Correct lower encoding/reset is an initialization premise.

Let J be any set of physical error points on Z times the nonnegative
integers, consisting of singleton or spatially adjacent-pair groups
at one tick each. Distinct groups are (24,24)-separated: every pair of
points from different groups has spatial distance at least24 or temporal
distance at least24. This is Gray's original base E0 shape/separation;
new Q/U and original numerical c104 do not modify that base definition.
Groups and J can be infinite. At each point allow an arbitrary legal
whole A_2-cell replacement, including adaptive choices based on the past.
Rule/ROM constants are not state fields and cannot be overwritten.

Write J_t for row-t error sites, J_-1 empty. X_t is the row **after**
the row-t overwrites; Z_(t+1)=F(X_t), and row-t+1 replacements give
X_(t+1). Start with X_0 agreeing with E(C,B) outside J_0. The same
global J, including cross-period isolation, applies throughout.
Let N_D(V) mean all configurations agreeing with V outside D.
Let Delta_5 read the bitwise majority of the five raw Info holders at
each normal representation primary, for all496 words. On E it gives
exactly C; at covered noisy boundaries the native padding is zero and
the decoded record is in A_2.

**Theorem.** For every such C,B,J and replacement choice, for every n>=1,

    Z_(nU) = E(F^n(C),0),
    X_(nU) belongs to N_(J_(nU))(E(F^n(C),0)),
    Delta_5(X_(nU)) = F^n(C).

Delta_5(X_0)=C as well. Thus the smaller **same fixed rule** performs
exact upper evolution for all time under continuing pure-E0 histories.
The pre-overwrite boundary is a complete raw encoding, not merely a
correct vote of selected output bits. This theorem has no E1/real1 or
higher cluster in its hypothesis and no iid conclusion.

## 1. Capacity and native geometry — proved

The two-row radius8 cone has spatial diameter16 and temporal diameter1,
both strictly below24. It cannot meet two different error groups.
The **union** J_t union J_(t-1) therefore contains at most two distinct
sites in every such cone. Each group occupies one tick; counting two
sites independently in each row would give an incorrect four-site bound.

Actual five-holder coordinates are y-S[h], S=(0,-2,-1,1,2). Every
shifted SF read used by the physical rule has logical displacement
between-3 and3 and holder displacement between-5 and5. Computed-primary
native sources additionally use the radius8 cone. Five-word votes with
at most two corrupted operands restore the correct coherent word,
bit by bit, at all Word100/packed1700/packed2200 widths. Native equal-
value quorums likewise have at least three identical correct values.
These are word identities for arbitrary two replacement words, not
inferences from selected payload executions.

Induct that stored Address and Age equal x modQ and t modU outside
J_t. Both adjusted-GF candidate votes restore the canonical Address;
both Age candidates restore the common clock. Existence predicates
are true. At most two inputs can mismatch them, so no inconsistency
quorum turns on. Either direction selector gives the same Address/Age
successor. Thus computed geometry is correct **everywhere**, including
current overwrite sites, independently of old flags/WF/SF values.
Only fresh J_(t+1) creates the next geometry faults.

The mandatory SF wipe compares computed GF to raw old-self GF. It can
fire only at a point in J_t. A wipe wake has already repaired geometry
and cannot launch a new wipe merely by retaining wrong SF. The proof
uses the actual raw-self comparison, not a replacement refined-self
comparison or an assumed SF transparency.

## 2. Quiet flags and the new deadline — proved

Before a period's96Q, computed WF is0. A region with stored F1/F2/WF
zero outside J_t cannot acquire computed F1: its on source needs three
right positives, its keep term needs self plus two right positives,
and its WF source needs three positives. Two arbitrary sites cannot
supply any of them. The GF/Age inconsistency sources are absent by §1.
For h1 Flag2, on needs four left positives, keep needs self plus two
left positives, and WF2 needs three. Missing-GF source3 is false, and
the F1-gated source is disabled. Hence both computed flags stay0
through gathers, early execution and couriers, for arbitrary legal
native and SF replacement values. No SF wipe or Mail mask fires then.

Exact WF/F1/F2 agreement with the noiseless shadow is not asserted
during96Q..98Q. At the end of that window, allow arbitrary native flag
values. At computed Age98Q all computed WF is0 thereafter; raw current
WF exceptions lie in J_t only. A guaranteed F1 zero suffix cannot
retreat. If b is its first guaranteed-zero site, a row avoiding J_t
in[b,b+4] extends the guarantee to b-2. The two new target cells have
at most one uncorrupted positive right neighbour. Errors in their
other positions cannot create a three-site on/keep/WF source. On a
charged row conservatively extend by zero. This artificial boundary
moves only zero or two cells per row, even if actual clearing is faster.

If two charged rows have time gap d<=9, their error points differ by
at most2d+4<=22 in space and d<24 in time. They cannot be different
E0 groups, and one group cannot occupy two ticks. Therefore charged
rows are at least10 apart. In r rows at most ceil(r/10) are charged;
the suffix grows at least2(r-ceil(r/10)). For the **new** Q4096,

    2(2276-ceil(2276/10)) = 4096.

Within2276 updates computed F1 is0 globally and remains0 under E0.
Now use a guaranteed F2 zero prefix. If a is its last guaranteed-zero
site, an uncharged row with no J_t in[a-4,a] advances to a+2. At most
one uncorrupted positive left neighbour remains for those targets;
the h1 on/keep thresholds and the two-site capacity exclude activation.
Computed F1 is0; source3 is false. The same charge proof gives another
2276 updates. Thus both computed flags are quiet no later than

    98Q+4552 = 405960 < 100Q = 409600.

There are3640 updates of slack before the actual late reset100Q,
and flags stay quiet until the next WF window except for fresh raw
replacements. This is the changed-scale premise that the older4552-
update **per-sweep** value could not supply without recalculation.
The finite checker evaluates the actual new-Q/U h1 scalar at616
frontier/support/Address classes and119746 Flag/WF payload cofactors.
The word-majority and charge arguments supply arbitrary GF/Age payload
and arbitrary histories; those cofactors verify the native equations.

## 3. All physical SF and actual execution — proved

Let Y_t be the noiseless evolution from the matching E(C,B). Its five
SF copies remain coherent by logical site: both native geometry
candidates agree, all holders use computed service Address plus their
copy offset, the clock is common, and its raw-self wipe is false.
Before96Q, F1 is0. At96Q both Mail tracks globally reset to0. They
have no later load or movement in that period: all loads/captures and
gather shifts ended before80Q. Therefore any later F1 mask leaves0
and cannot break coherence in the noiseless trajectory.

Induct the following invariant for **all thirteen** five-copy physical
SF components: packed heads/registers, Mem, Out, Info, Scratch,
Programme, both couriers, both Mail tracks and all three History banks.

    X_t and Y_t agree in SF outside J_t union J_(t-1).

Whenever the update producing row t has computed F1=0 everywhere,
the SF support reduces to J_t. Native flags/WF are excluded from this
invariant. The initialization satisfies its base directly.

For the induction step, §1 restores every actual old SF vote despite
the coexistence of current replacements and previous wipe wakes.
This includes held values, moved Mail/couriers, packed candidate
heads, register/memory operands, histories and commit outputs. Correct
votes occur **before** packet unpacking and invalid-metadata decisions.
Thus all packet candidates, counts, movement, opcodes, pending IO and
immutable lookups equal the shadow's. No unvoted raw packet bypasses
the correction. Computed GF/Age give exactly the shadow's reset/birth,
service and special-write controls, even at a current raw GF fault.

There are only two remaining native-flag dependencies in these physical
SF equations. Before96Q neither fires. From96Q onwards physical Mail
is globally zero after correction: its reset produces0, no later load
or shift occurs, and either mask/wipe preserves0. Represented upper Mail
in readonly Mem is a different field and is still handled by the usual
upper evaluator. All retained History captures ended by72Q+2, so a
later physical Mail mask cannot erase them. The remaining SF wipe can
occur only in J_t. Hence computed SF disagreements lie in J_t;
fresh J_(t+1) adds the second section. This closes the invariant without
assuming WF or native flag equality during the pulse.

If computed F1=0, there is no SF wipe and all computed SF equals Y,
including current input-error sites. This holds before96Q and after
405960. In particular the actual100Q late reset and100Q+1 birth/reload
have exact shadow outputs before fresh overwrites. A birth-row overwrite
can damage at most two holders; the next vote restores the packet.
Changing one raw GF cannot suppress the corrected logical birth because
the physical service control uses computed GF.

The actual gathers therefore acquire the correct complete17-cell bank.
The221-update early execution,75Q seeds and bounded1800/2291-distance
couriers follow their corrected logical trajectories without noise delay.
During the source window all retained bank votes remain correct, even
where current SF suffers an allowed wipe wake. At the late reset/birth,
the bank and unique pc0 packet are derived from this physical history.
Every subsequent packet/operand/controller update equals the shadow.
The universal GAWN2 prepared proof then applies to the **actual** noisy
execution: all496 outputs complete within104572 updates, before127Q,
with the same6019 late-update margin. No prepared bank is supplied as
an external assumption, and no sampled noisy runtime proves this bound.

## 4. Full boundary and all-time iteration — proved

Before U, computed flags/WF are0 and geometry is canonical. All old
Out votes equal F(C) on normal representation positions and0 elsewhere.
At U, Info consumes those old voted outputs before every work reset;
Programme uses the correct beta_2 bit and no raw-self wipe fires because
computed F1=0. Thus the complete pre-overwrite row is E(F(C),0)
at every integer site. Only J_U can alter the raw boundary.

At each normal primary, at most two of five Info holders belong to J_U,
so Delta_5 returns every exact physical representation word of F(C).
This proves both the full raw current-error envelope and decoder claim.
The next period begins in N_(J_U)(E(F(C),0)); the same globally isolated
J includes the previous-boundary groups. Repeat the argument for every
n. Each local step uses finite cones, so infinite C and J require no
finite-ring boundary convention. This proves the theorem.

The preparation/word-copy argument also allows upper represented native
padding in D; the first output normalizes it using GAWN2's pi_2. The
displayed same-physical-rule theorem uses C in A_2 and needs no padded-
alphabet extension to interpret F^n.

## 5. Exact reachable E0 wake — proved finite witness, not a theorem failure

The [retained witness](../../../../figs/gray_counterexamples/unregistered_gawn3/GAWN3_E0_WF_witness.json)
starts from the actual global E(C,B) where C[g] has Address g modQ,
Age0/F1=1/all other fields0, and B is Word100_MASK. It is not claimed
to be recursively intact. Actual gathers and the new emitted early
entry derive F1=1/F2=0 commands near receivers-1,0,1; the real bounded
couriers deliver them before80Q-1. The unused residues in the witness
cone have three actual all-one History banks and no normal head frame.

At row t=96Q+1=393217, replace only native Address at x=Q-3=4093
by4094, keeping the actual other raw bits. This one point is an original
base E0 group with no other errors. The new actual local F restores GF
but computes F1=1 and performs the mandatory source SF wipe. Its final
computed-primary Info is0 rather than1. WF1 consequently differs from
the shadow at the five sites4091..4095, while the SF wake is supported
only at4093. Its voted Info is still1. On the next update all retained
SF and WF match the shadow again; transient F1 equality is not claimed.

This exact actual-prefix/local-equation witness rules out adding the
false premise that WF always equals the noiseless shadow under E0.
The two-section invariant tolerates it and the period theorem holds.
It is neither a decoded-period failure nor a Gray/iid counterexample.

## Remaining reliability obligations and status

For any positive iid error-location rate epsilon, disjoint triples of
adjacent sites at one tick are simultaneously faulty with probability
epsilon^3. The probability that none of m such disjoint triples is
faulty is(1-epsilon^3)^m, tending to0. Thus the global pure-E0
hypothesis cannot be assumed for positive-rate iid noise. The restricted
deterministic theorem does not provide a positive threshold by itself.
Higher clusters must be classified, confined/repaired and represented
as upper errors with uniform constants and an iteration valid at every
level. Those statements remain unproved for GAWN2.

| Step | Status | Scope |
|---|---|---|
| Two-row capacity/whole-word votes/geometry repair | proved | Continuing original-base pure-E0, arbitrary full-cell replacements |
| New2276-per-sweep/405960 quiet bound | proved | Actual new-Q/U h1 equations and separation24 charge bound |
| Two-section SF invariant/actual noisy gathered-bank and execution coupling | proved | All13 physical SF components, lower encoded initialization |
| Complete pre-overwrite encoding/raw boundary envelope/Delta_5/all-time iteration | proved | Same frozen Q4096/U524288 rule under pure-E0 |
|616 frontier119746 payload714 vote561 metric checks | exact finite supplements | Universal scope from the word/front/induction arguments |
| Actual one-site WF/SF-wake witness | proved finite execution with actual-prefix derivation | No period/refinement/Gray/iid failure |
| Gray/Gács noisy argument beyond this base | unproved | Rule/layout/ROM/rest/radius departures remain |
| General real1/higher repair, positive iid epsilon, memory, minimum sufficient fix | unproved | Active goal remains open |

Read-only command:
`python3 Report/proofs/gray_counterexamples/unregistered_gawn3/validate_small_E0_gawn3.py`.
No rule, constant, ROM or previously frozen artefact is changed. No commit.
