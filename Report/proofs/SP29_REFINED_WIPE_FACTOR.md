# Correction: Info wipe uses the refined old GF

The old general factor assertion in SP28_INFO_NATIVE_FACTOR.md is false.
Its C recurrence used unrefined old label L in the simulation wipe, while
the actual generated rule first replaces the local native GF/age inputs
by the joint refinement. This is an analysis-model correction, with no
rule, programme, constant or active G17 change.

## Exact finite counterexample to the old general factor

At common clock TF278401 let raw GF be x modQ except at508/509/510,
where it is(x+512)modQ. Put native Flag1=1 everywhere, Flag2/Workspace
flags/packet/code validities/backward pressure0. Give logical Info
primary509 five copies1; all other Info is0. These satisfy J164's
stated arbitrary-binary-GF/arbitrary-Flag1 factor premises. Other private
data and I can be0, or left free in the cofactor.

The four distant five-votes see the canonical GF word at every relevant
reader, so refined old GF is canonical. Native Flag1 remains1 and the
epoch force selects canonical GF. Actual new GF therefore equals the
refined old GF: keep=1 at all five holders507..511, and all five new
Info copies at509 are1. The old recurrence wipes three of those copies
because new label0 differs from the unrefined old1 at508/509/510;
it falsely predicts Info majority0. Five full-circuit constant cofactors
certify the actual result with all other private inputs/I free.

This is a counterexample to our factor proof, not to SP29 reliability
or Gray. Selected earlier native/Info cofactors do not cover this pattern.

## Corrected exact factor

Let J(x,t) be the joint-refinement label computed from the four five-votes
of raw binary GF labels. It equals1 if at least three block votes are1,
0 if at most one is1, and the raw self-label when exactly two are1.
The two-GF/common-clock closure and all native/header equations of J164
are unchanged. Replace only its simulation keep by

    K(x,t) = NOT(F1_new(x,t) AND (L_new(x,t) != J(x,t))).

The corrected Info recurrence is

    M(y,t+1) = M(y,t) AND [sum_{s=-2}^2 K(y-s,t) >= 3].

WF1 still reads the old M at the computed-GF509/1021 primary, with no
reader keep multiplier. The other source/sole-birth/native/header
arguments remain unchanged. Equal low GF bits compare new GF with
the refined self-word, exactly as the corrected formula states.
The1024 copy/keep-mask majority identities apply verbatim. Thus this
is the exact closed factor under J164's original restricted pulse
premises, including arbitrary binary GF labels and raw Flag1/2.

The checker generates a separate C factor by replacing that one
comparison in the frozen source. It retains the original C source,
receipts and proof for provenance. It also records a comparison with
the old keep on every retained-primary holder and every row.

## Particular pulse bridge and limits

The corrected checker repeats three complete6144-update cases:
the old prescribed asymmetric masks at force durationsQ and2Q, and
the actual first J167 mask (six additional true-phase ones) at2Q.
Each row verifies the support/background cone and the exact GF hull
bound. The completed receipt determines whether the old and corrected
majority transitions agree at every row; this cannot be inferred from
an unchanged endpoint or the earlier selected cofactors.

When the recorded active-majority disagreement count is0, the two
projected recurrences have identical histories from their same initial
data, by induction: every native/header update is unchanged, and each
actual Info majority update equals its old counterpart. The independently
verified corrected histories then establish the stated pulse for the
actual rule. The final arrays and all row summaries are compared with
the accepted earlier receipts, explicitly preserving their limited
particular-input scope. No old general-factor claim is reinstated.

The same infinite-line lift remains valid: Info ones cannot grow; GF
support grows outward at most3; native flags/headers propagate at most8.
The corrected keep reads the joint refinement within32 of a GF holder,
covered by the37-site seed reserve. All-row exterior/background checks
in I enlarged8(r+1)+37 therefore still enclose the projected differences
and protect the quotient seam. There is no claim that arbitrary private
simulation data is spatially confined by that projected cone.

J167's pre-TF source theorem is unaffected because its quiet template
has joint-refined GF equal to raw self-GF. J169's Hold/pending/timing
argument is also unchanged; its native endpoint premise must be supplied
by this corrected first-pulse bridge. Its boundary/next foreign-signal
claim does not assert a correct full upper successor or second pulse.

| Step | Status | Limit |
| --- | --- | --- |
| Old unrefined-GF general Info factor | refuted | Exact three-site GF/five-holder Info cofactor |
| Corrected refined-old-GF factor | proved | Same restricted two-GF/common-clock/sole-birth pulse premises |
| Historical finite pulses apply to the actual rule | proved only with completed corrected all-row bridge | Receipt must certify zero active-majority disagreements and the endpoint/lift |
| Original-history first signal and the Hold timing/pending lemmas | proved unchanged | Their own scope; first endpoint uses the corrected bridge |
| General eroder, higher error map and positive iid rate | unproved | Correcting an analysis recurrence does not supply these |

Reproductions: check_short_force1024_refined_wipe.py,
figs/robustness/SP29_refined_wipe_certificate.json, and separately named
generated C/log/state assets. No active transition is modified.
