# SP30: corrected native/Info factor and its actual first shrinking pulse

This concerns the **explicitly changed SP30** of J189, with its own ROM,
Q1024/U475136/TF278401 and force2048. No further rule, programme,
constant or compiler change occurs here. The new projection identities
are proved below before any old integer certificate is reused. This does
not transfer an SP29 whole-state trajectory or its later data arguments.

[New checker](check_signal_reservation1024_native_pulse.py),
[receipt](../../figs/robustness/SP30_native_pulse_certificate.json),
[new actual first signal](SP30_FIRST_SIGNAL.md),
[corrected refined-GF factor](SP29_REFINED_WIPE_FACTOR.md),
[unchanged native/header substitutions](SP28_SHORT_EPOCH_ENCLOSURE_GAP.md).

## Restricted factor theorem

At computed clock TF let every raw GF be either x modQ or(x+512)modQ,
with arbitrary binary labels L(x), a common legal native AgeTF and
arbitrary native Flag1/Flag2. Initially Workspace flags, packet/code
validities and backward pressure are zero; invalid header words, every
other private field, raw Info copies and instruction inputs may be
arbitrary. There are no subsequent errors. For6144 input rows the exact
native/header evolution is the already proved integer substitution in
SP28_SHORT_EPOCH_ENCLOSURE_GAP, items1–6, with duration2048 and actual
Workspace1. Define J(x,t) to be the four-block joint-refinement label,
and M(y,t) the old logical five-copy Info majority at y. Then

    K(x,t)=not(Flag1_new(x,t) and (L_new(x,t)!=J(x,t))),
    M(y,t+1)=M(y,t) and majority5(K(y-s,t), s=-2..2),
    WF1_new(x,t)= [computedGF(x,t)>=Q-5] [t-TF<2Q] M(y,t),
    y=x+Q-3-computedGF(x,t).

Only M at physical residues509/1021 can occur in the last line. Thus
these two M tracks and the stated native/header initial state determine
the projected trajectory, independently of the own programme's evolving
private fields. The comparison in K uses **refined old GF**, as the
actual rule does; the earlier unrefined-GF model is not reinstated.

**Proof.** The new checker builds SP29 and SP30 in a shared Boolean Net.
All73 native/Workspace/header/backward output nodes are exactly equal
on arbitrary raw inputs, including arbitrary instructions and private
fields. This is an unrestricted local-function identity. The changed
history-capture outputs are outside this projection. Consequently the
binary-GF/common-clock closure, native selectors, sole simultaneous
birth, counter ancestry, packet priority, code competition, expiry and
backward-window substitutions in the cited proof apply verbatim to
these native/header functions. This does not say the two full trajectories
or their later header inputs are equal; the closed projection induction
will establish the required header equality.

For the remaining Info outputs the checker builds the actual new rule
with a conditional controller. It keeps the actual refined self-GF word
symbolic, permits arbitrary computed GF/Flag1/Flag2, and all raw Info,
other work and instructions free. With both commit and special-write
controls false it proves all five literal outputs equal
K(x,t)*M(x+s,t). It also proves the literal old-M WF1 identity with no
reader keep multiplier. Four representative clock cofactors straddle
the WF1-window boundary. The universal extension to the entire interval
is by the exact source branch: its Info clock controls are only commit
and special write, and the WF1 clock control is only the stated window.
All6144 legal clocks avoid T_sig278400 and U-1=475135; the checked window
is true exactly in the first2048 rows. No other private clock branch can
enter these proved output formulas.

The source first installs distant joint refinement before binding its
self-cell and wipe comparison. Thus the old GF node in this identity is
precisely J, not raw L. Under two-phase closure the GF words have common
low nine bits, so GF inequality is exactly label inequality. All1024
old-copy/keep-mask Boolean assignments prove that voting the five new
copies gives the stated M recurrence, without a copy-coherence assumption.
All1024 reader phases and both labels give exactly ten guarded WF1
source cases, with offsets in[-2,2] and residues509/1021.

These identities close the same corrected native/Info/header recurrence
at every row. Info ones cannot grow. Its packet/code outputs and common
counts are determined by the same actual native data and sole TF birth,
so no omitted private input re-enters a later projected row. Induction
proves the restricted factor theorem on Z. QED.

## Actual first-pulse theorem

Use exactly the intact-start error history in SP30_FIRST_SIGNAL.md:
upper native GFcanonical/Age0/private0, arbitrary upper Info, lower
GF shifted512 on[130560,147456), lower Flag1 on its two preceding
512-site strips, and no later errors. At computed time

    TF+6144=284545

the actual lower GF is shifted512 exactly on[124416,139264),
canonical elsewhere. Native Flag1 is1 exactly on[123904,124416)
and[138752,139264); native Flag2/Workspace flags, packet/code
validities, counters/tags/positions and backward pressure are0.
The wrong-GF width has decreased from16896 to14848, by2Q.
The voted MF509 track has eight remaining ones and MF1021 is1 exactly
at colonies144/145/146. This is a finite native/projected theorem,
not full-state restoration or a general eroder.

**Proof.** J191 supplies exactly the factor's initial native/empty-header
premises and the actual MF509/MF1021 masks. The preceding universal
projection proof makes its subsequent recurrence identical to the
corrected duration2048/extra-true-sources case in the frozen
SP29_refined_wipe_certificate. Every one of its6145 rows is therefore
the new rule's projected row by induction, even though its private
simulation fields and programme differ. The new checker pins the
corrected C transition and wrapper, all-row log and final arrays; it
checks the complete row indices, arithmetic/support bounds, zero
active-majority disagreements and the actual endpoint masks. It does
not infer equality from the endpoint alone or rerun a whole CA.

The old integer certificate's infinite-line argument applies to this
same projected recurrence verbatim. Relative to the canonical evolving
Q-periodic reference, native GF grows outward at most3 per update,
other native/header differences at most8, and joint refinement is
covered by the37-site seed reserve. Info ones cannot grow. Every row
compares exterior values in

    [124Q-8(r+1)-37, 147Q+8(r+1)+37)

with that reference, protecting the quotient seam. At r6144 the
interval is[77779,199725), strictly inside the256Q array. The clean
reference, explicit cone and checked exterior comparisons lift the
retained integer identities to Z. There is no periodic full-state
hypothesis or independently prescribed future physical signal. QED.

## Scope

| Step | Status | Limit |
| --- | --- | --- |
| 73 unrestricted native/header output equalities | proved | Same raw local inputs, not equal full trajectories |
| New Info carry/wipe and old-M WF1 formulas | proved | Common legal pulse clock; refined old GF in wipe |
| Corrected closed pulse factor | proved | Two GF phases, sole TF birth/empty initial headers, no fresh errors |
| Actual first2Q shrinking pulse on Z | proved | J191's one specified intact-start history and new projection bridge |
| Boundary encoding, later signals and arbitrary error-island erosion | unproved here | Private data/clock/general-phase arguments are still required |
| Higher-error map and explicit positive iid noise rate | unproved | Restricted first pulse is insufficient |

No numerical whole-CA trajectory or sampled initial payload is used for
these conclusions. The frozen finite integer certificate is reused only
for a recurrence proved identical to the new projected rule. Active G17,
CURRENT, SP29, all previous proposals and all frozen sources remain unchanged.
