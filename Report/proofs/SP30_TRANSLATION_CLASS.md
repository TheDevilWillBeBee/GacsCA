# SP30: a conditional width-preserving pulse with arbitrary exterior signals

This concerns the frozen, explicitly changed SP30 rule F30, with
Q=1024, U=475136, TF=278401, radius37 and force duration2Q. The theorem
below introduces no further rule change. It covers a prepared native
template and a finite window of prescribed Info majorities. It does not
prove a permanent travelling defect, a general eroder, full-data repair
or reliability under positive iid noise.

[Checker](check_signal_reservation1024_translation_class.py),
[certificate](../../figs/robustness/SP30_translation_class_certificate.json),
[prepared driver](unregistered_terminal/probe_sp30_translation_class_force.py),
[baseline receipt](../../figs/robustness/unregistered_translation_force2048/receipt.json),
[actual restricted projection](SP30_NATIVE_PULSE.md),
[primitive domain proof](SP29_THIRD_DOMAIN_PULSE.md), and
[previous infinite-domain lift](SP30_CONTROLLED_TERMINAL.md).
The driver receipts retain their finite prepared-equation scope. This
document supplies the infinite-line argument for the unchanged2Q case.

## Exact theorem

Fix an integer K and a nonnegative integer p. At computed time pU+TF,
suppose the actual full F30 configuration on Z satisfies:

* GF is canonical x modQ except on[(K-1/2)Q,(K+6)Q), where it is
  (x+512)modQ. Every native Age is TF.
* Native F1 is1 exactly on[(K-1)Q,(K-1/2)Q) and
  [(K+11/2)Q,(K+6)Q). Native F2 and Workspace flags, packet/code
  validities and backward pressure are0. Invalid header words,
  unrelated private fields and instruction inputs may be arbitrary
  under the restricted projection theorem.
* M509(j) and M1021(j) denote the actual logical five-holder Info
  majorities at physical sites jQ+509 and jQ+1021. M509 is1 exactly
  at K,...,K+5 and0 elsewhere. M1021 is1 at K-4,K-3,K-2 and
  K+6,...,K+23; it is0 at K-56,...,K-6 and K-1,...,K+5. Its value
  at K-5 and at every j outside[K-56,K+24) is arbitrary.
* Other Info majorities are arbitrary. The allowed bits may correlate;
  their raw five-copy holders need not be coherent. No physical error
  occurs during the following6144 updates.

At time pU+TF+6144, GF is shifted512 exactly on
[(K-13/2)Q,KQ), and is canonical elsewhere. Native F1 is1 exactly on
[(K-7)Q,(K-13/2)Q) and[(K-1/2)Q,KQ). Every native Age is the legal
clock TF+6144. F2 and Workspace flags, packet/code validities and
their active tags/positions, and backward pressure are0. In the
T(L,R) notation used for the actual histories, this is

    T(K,K+6) -> T(K-6,K).

Both boundaries move left by6Q. The wrong-GF width stays13Q/2=6656.
This conclusion holds for every allowed infinite signal assignment,
including nonperiodic assignments and arbitrarily correlated bits.
There is no assertion about full upper encoding or unobserved fields.

At the endpoint M509 is0 everywhere. M1021 remains1 at K+6,...,K+23,
is0 at K-56,...,K+5, and is unrestricted outside[K-56,K+24).
In particular the formerly unrestricted bit at K-5 has been erased.
The unrestricted exterior bits retain their initial majority values:
their keep masks are identically1 throughout the interval. These Info
statements concern logical majorities, not coherence of raw holders.

The80-colony controlled window is sufficient for this theorem. No
minimal-window or globally sufficient change is claimed.

## Reduction to the actual rule and sound domains

J192's restricted projection theorem applies verbatim: the initial
two-phase GF, common legal clock and empty native/header auxiliaries
are precisely its hypotheses. All6144 clocks avoid commit and special
Info write. The actual four-block refinement, native selection,
Workspace1, sole pulse birth, code/header/pressure equations and Info
recurrence consequently close independently of the private programme.
In particular,

    M_new(y)=M_old(y) AND maj5(keep(y-s), s=-2..2),
    keep(x)=NOT(F1_new(x) AND (new_GF_label(x)!=refined_GF_label(x))).

Workspace1 reads old M, and only residues509/1021 enter its guard.
The comparison uses refined old GF. The proof's1024 copy/keep cases
permit arbitrary raw holders, and its73 native/header equalities and
four conditional cofactors permit unrelated private fields and inputs.
We use that already proved factor, not a prescribed future signal.

J180's domain states0={0},1={1},2={0,1},1062 primitive set-image
checks and36 GF-selector cases also apply verbatim to the baseline.
Every abstract transition encloses every concrete transition, with no
independence assumption. GF stays scalar when its selector is fixed
or both alternatives agree; the implementation stops if it cannot
establish either condition. Packet and code state remains exact.

Take K=128. On Z, form the abstract initial state D0 with the stated
fixed native/header values, the pinned M509/M1021 values, and a
separate domain2 at every unrestricted M1021 coordinate. This is an
infinite product domain containing all allowed concrete configurations.
It does not identify the values of distinct free coordinates. Local
domain inclusion inductively encloses their projected trajectories.

## Infinite exterior and finite representation

Use the same Q-periodic abstract background B0 as J204: canonical GF,
zero initial native/header auxiliaries, M509zero and M1021domain2 at
each corresponding residue. The domain background B_r evolves by
the same local functions. Its GF remains canonical because its four
joint votes and both native alternatives are canonical even when a
Boolean selector is unknown. No concrete exterior assignment is fixed.

D0 differs from B0 only in I=[72Q,152Q). The J204 support argument
for equality of abstract states applies with this wider seed: GF can
advance at most3 sites past its hull per update, other flag/header/
pressure differences at most8, and joint refinement has reserve37.
Info has no transport, and outside changing GF its keep mask is1
even with free F1. These are properties of the identical projected
local functions. Thus D_r equals B_r outside

    I_r=[72Q-8(r+1)-37,152Q+8(r+1)+37).

The stored wrapper includes the frozen factor source unchanged. It
places D0's primary defect and pinned window in a256Q quotient with
B0 elsewhere, and checks all exterior domain coordinates against
the same-residue reference in[0,Q). For every0<=r<=6144, both that
reference and the seam's37-site neighbourhood lie outside I_r.
The final interval is[24531,204845), strictly inside[0,262144).
Every seam read therefore has the same abstract background value as
the corresponding infinite-line read. Induction identifies this
finite array with D_r in the protected interval and B_r outside it.

This is a lift of the abstract domain, before selecting concrete bits.
The actual concrete infinite exterior may be nonperiodic. Inclusion
in D_r, rather than equality to one periodic concrete configuration,
supplies the theorem on Z. Translation by(K-128)Q covers every integer
K. Repeated pulse-clock controls cover every nonnegative p.

## Finite certificate and endpoint

The baseline run completes6144 transitions without an unresolved GF
selector. Its6145 rows check1610874880 GF sites and804884390 exterior
domain equalities. The nonempty all-row GF hull is[123456,137216);
one intermediate hull has holes. No hull-contraction assertion is used.
The final arrays give GF1 exactly on[124416,131072), F1exactly on
[123904,124416) and[130560,131072), all other native/header planes0
and code0. These are the stated T(122,128) values.

M509 is0. M1021 has eighteen fixed ones134,...,151, and domain2 at
j<72 or j>=152 in the quotient. The bit123 has become0. The176
remaining domain2 entries are a finite representation count, not176
concrete ones or a bound on the infinitely many arbitrary exterior
signals. The exact Info recurrence and keep=1 in the unchanged
exterior preserve those exterior majority values. Source, factor,
all-row trace and endpoint hashes are checked; the deterministic
integer run is a finite recurrence certificate, not a noisy-CA sample.

Together the actual projection, domain inclusion, infinite lift and
singleton native endpoint prove the theorem. QED.

## Explicitly hypothetical longer-force equations

The same prepared driver separately replaces only the RF force
duration in the projected equations by3Q or4Q. It keeps the actual
Workspace1 window2Q and all other equations. These are **explicit
projection constant changes**. No complete own rule or programme was
constructed or compiled for either change; the full-rule identity and
infinite-line theorem above are claimed only for the unchanged2Q case.

The frozen finite recurrence results are:

| RF force duration | Updates | Prepared endpoint | Wrong-GF width | Status |
| --- | --- | --- | --- | --- |
|2Q |6144 |T(122,128) |6656 | proved conditional F30 pulse on Z above |
|3Q |7168 |T(119,125) |6656 | proved finite hypothetical domain recurrence only |
|4Q |8192 |T(116,122) |6656 | proved finite hypothetical domain recurrence only |

[3Q receipt](../../figs/robustness/unregistered_translation_force3072/receipt.json)
and[4Q receipt](../../figs/robustness/unregistered_translation_force4096/receipt.json)
retain every row, generated wrapper, endpoint, compiler and runtime
receipt. Their runs have no unresolved GF selector and exactly the
same eighteen fixed and176 free endpoint Info domains. Neither
longer force removes this prepared defect in its tested interval.
This rules out the proposed one-pulse cure for this case; it does not
rule out eventual repair, another complete rule change, or a proof
under different hypotheses. No minimum sufficient modification follows.

## What remains open

This pulse theorem cannot be iterated directly. At its endpoint the
next template's K'=K-6 would require M1021ones at K,...,K+17, but the
retained track is0 at K,...,K+5. The programme must generate a new
signal before another invocation. Canonical clock evolution and those
signals at arbitrarily many future work periods have not been proved.
Coarse Age/GF wrap and later higher-level activity must also be handled.

The actual seventh pulse in J206 satisfies the stronger pinned window
above after translation by36Q, so this theorem is consistent with that
already proved endpoint. It does not derive an eighth signal or replace
the actual-history source arguments. No permanent glider, actual
original-error failure for all time, general noisy repair, complete
upper restoration or positive iid epsilon is proved.

| Step | Status | Exact scope |
| --- | --- | --- |
| Actual F30 closed projection and primitive domains | proved previously; applies | unchanged2Q rule,6144 legal no-error updates |
| Infinite free-exterior domain lift | proved | every stated correlated infinite signal assignment |
| Conditional width-preserving F30 pulse on Z | proved | T(K,K+6) and the stated finite signal window |
|3Q/4Q hypothetical recurrence endpoints | proved finite recurrence only | explicit projection edits, no new full-rule compilation |
| Complete iteration/permanent defect/eventual repair/full data | unproved | new signal supply and higher activity are required |
| General eroder/higher error map/positive iid epsilon | unproved | no all-level noisy induction supplied |
| Gray/Gacs verbatim applicability/minimum globally sufficient change | unproved; not claimed | SP30 was explicitly changed earlier |

No active G17/CURRENT, frozen SP30, accepted-source or constant change
and no commit occurs here. The hypothetical projection changes are
stored separately and are labelled above.
