# SP30: a conditional terminal native eroder with infinitely many free signals

This concerns the frozen, explicitly changed SP30 rule F30,
Q=1024/U=475136/TF=278401, radius37 and force duration2Q. No new
rule, programme, layout or constant is introduced. The theorem below
has a **finite signal-window premise**. Its application to the original
J191 error after the later shrinking pulses remains unproved, as do
full-data recovery, general eroder and positive iid noise reliability.

[Checker](check_signal_reservation1024_controlled_terminal.py),
[certificate](../../figs/robustness/SP30_controlled_terminal_certificate.json),
[prepared-domain driver](unregistered_terminal/probe_sp30_half_colony_controlled_left_signal.py),
[driver receipt](../../figs/robustness/unregistered_terminal_controlled/receipt.json),
[actual closed projection](SP30_NATIVE_PULSE.md),
[sound one-step domain proof](SP29_THIRD_DOMAIN_PULSE.md).
The prepared driver retains its finite, conditional scope. This document
supplies the infinite-line domain argument separately.

## Exact theorem

Fix an integer K and a nonnegative integer p. At computed time pU+TF
assume on Z:

* Native GF(x)=x modQ except on[(K-1/2)Q,KQ), where it is
  (x+512)modQ; every native Age is TF.
* Native F1=1 exactly on[(K-1)Q,KQ); F2 and Workspace flags are0.
  Packet/code validities and backward pressure are0. Invalid header
  words, unrelated private fields and instruction inputs may be free
  as in the restricted projection theorem.
* Let M509(j), M1021(j) be the actual logical five-holder Info
  majorities at jQ+509 and jQ+1021. M509 is0 everywhere.
  M1021=1 at K-4,K-3,K-2; it is0 at every K-56<=j<=K-6 and at K-1.
  The bit at K-5 and every bit outside[K-56,K) is arbitrary.
  No independence, periodicity or raw-copy coherence is assumed.
* Every other Info majority is free, and no further physical error
  occurs during the6144-update interval.

Then at pU+TF+6144 the native GF is globally canonical, native Age is
the common legal clock TF+6144, and F1/F2/Workspace flags, packet/code
validities and their active tags/positions, and backward pressure are0.
No assertion about complete upper encoding, unobserved private fields
or all Info bits is made. Every arbitrary infinite signal assignment
satisfying the finite premise is covered, including correlated bits.

In fact GF is already canonical at relative row2490 and remains so
through6144. If the noiseless continuation persists after6144, GF
remains canonical and Age remains the common legal clock for all later
ticks. Future native flags may become active again; their values and
the private simulation/data trajectory are not part of this invariant.

The56-colony window is a sufficient premise of this theorem. No
minimal-window, minimal-rule-change or globally sufficient reliability
claim is implied.

## Reduction to the actual closed factor

J192 proves the restricted native/header/Info factor for arbitrary raw
Info copies and unrelated private fields, under precisely these two
GF phases, common legal pulse clock and initially empty validities.
All6144 clocks avoid commit and special Info write. The literal Info
majority recurrence uses refined old GF, not unrefined old GF:

    M_new(y)=M_old(y) AND maj5(keep(y-s),s=-2..2),
    keep(x)=NOT(F1_new(x) AND (new_GF_label(x)!=refined_GF_label(x))).

WF1 reads old M; only residues509/1021 can enter its guard. The actual
four-block joint refinement, native selections, single pulse-clock
birth, code transport, expiry and pressure equations therefore close
on this projection for the whole interval. The proof includes all1024
old-copy/keep-mask cases; coherent raw Info copies are unnecessary.
No simulated private field or later instruction can re-enter the
closed factor. Thus the full rule's projection is a concrete solution
of the frozen equations, whatever its unobserved work trajectory.

## Pointwise domain enclosure

Use domains0={0},1={1},2={0,1}. J180 proves1062 exact primitive
set-image checks and36 GF-selector cases. NOT/AND/OR/MUX and bounded
threshold sums enclose every concrete tuple, including tuples with
correlations or repeated coordinates. GF is kept scalar only when its
selector is fixed or both GF alternatives coincide; an unresolved
selector stops the run. Packet/code state stays exact because its
closed equations depend on the exact native labels and time.

Translation by an integer multiple ofQ preserves residues and the
projected local functions. Take K=128. Define an abstract initial state
D0 on the entire integer line. GF/F1 and other native/header variables
are the fixed initial values in the theorem. M509 is0. M1021 is0
at72..122 and127,1 at124..126, and domain2 at123 and at every j<72
or j>=128. Other Info is outside the closed projection.

This domain state contains every allowed concrete signal assignment on
Z. Domain2 does not designate one shared bit, and it does not force
an assignment to repeat at spatial period256Q or any other period.
Inductively apply the sound local domain transition at every integer
site. Whenever GF stays scalar, this produces D_r enclosing the
actual full-rule projection at row r for every allowed assignment.
We now identify D_r with a verified finite representation, rather
than assuming periodicity of the concrete trajectories.

## Periodic domain exterior and the Z lift

Let B0 be the Q-periodic **domain background** with GFlabel0,
all initial native/header auxiliaries0, M509zero and M1021domain2
at each corresponding residue. Its local domain evolution B_r is
Q-periodic. Its GF remains exactly0: four-block refinement gives0,
both adjusted GF votes are0, and even an unknown selector has equal
alternatives. No concrete signal value is chosen in B.

D0 differs from B0 only in I=[72Q,129Q). The difference includes
the pinned left-signal window and the initial GF/F1 defect. The usual
projected support argument applies also to equality of abstract states:

* Outside the scalar GF support hull, joint refinement retains label0.
  At least two of its four blocks lie outside that hull; two remaining
  positive votes use the raw0 fallback. Native GF cannot acquire a1
  farther than3 sites beyond that hull in one update, irrespective of
  possibly free flags.
* Flag/header/pressure propagation reaches at most8 sites per update.
  The37-site joint-refinement reserve covers GF-dependent substitutions.
  WF1 reads a guarded primary at distance at most2. Info has no transport:
  outside the changing GF region its keep test is identically1, even
  for free F1, so its initial abstract background value is preserved.

These are the same actual closed equations and support bounds used in
J192/J180; Boolean domains change neither dependency coordinates nor
the equal-alternative GF case. Induction gives D_r=B_r outside

    I_r=[72Q-8(r+1)-37,129Q+8(r+1)+37).

The separate wrapper includes the frozen domain factor unchanged. It
places exactly D0's primary copy inside a256Q quotient, B0 elsewhere.
At every row it checks all sites against the evolving reference at
16Q with the same residue outside I_r. Throughout r<=6144 the reference
period and its neighbourhood are strictly outside I_r, as is the seam
neighbourhood. At the final row I_r=[24531,181293), strictly inside
[0,262144). The output is therefore a finite representation of D_r
on Z: all quotient seam reads equal the periodic **domain** background
reads, and the primary protected region has the same local transition
as D_r. Induction identifies these abstract states row by row.

This argument lifts the domain state before selecting any concrete
bits. Arbitrary concrete exterior signals need not form a Q-periodic
trajectory. Pointwise inclusion in the infinite domain D_r supplies
the concrete Z conclusion, and never identifies their exterior with
one particular finite-ring realization.

## The finite certificate and terminal state

The source, unchanged factor, compiler/binary receipt, all-row trace
and final arrays are pinned by the checker. The wrapper changes only
the prepared template, abstract signal window, protection interval and
output names; it uses no unsupported hull-contraction bound.
The deterministic6144-update run has no unresolved selector.

The initial certificate checker requested a nonexistent projection
receipt field and stopped before producing a theorem certificate.
Its [exact source and failure manifest](../../figs/robustness/unregistered_terminal_controlled/initial_checker_failure.json)
are retained. The corrected checker verifies the existing73 output
equalities,1024 copy/keep cases,6144 legal clocks and four conditional
cofactors explicitly. No domain equation, result or rule was changed.

All6145 rows check262144 GF sites:1610874880 GF checks and949611430
exterior domain equalities. All GF labels stay singleton throughout.
The nonempty all-row GF hull is[123456,131072]; one nonempty row has
holes. GF first becomes empty at2490 and stays empty. For an empty
support, the recorded pair[262144,0] is a sentinel, not an interval;
the negative diagnostic hull size is ignored.

At row6144 every native/header domain is0 and code is0. The stored
arrays verify every site and field, including tags omitted from the
printed summary. The actual projection enclosed in D6144 consequently
has precisely the claimed quiet native state. Only Info domains remain
free; the200 free entries in the quotient are not a count of concrete
ones and do not assert all-data restoration. The201 free initial
quotient entries are a finite representation detail, not a bound on
the number of arbitrary signal bits on the infinite line.

Translation by(K-128)Q gives every integer K, and the pulse's legal
clock controls repeat every U, giving every p. The full-rule restricted
projection then proves the stated conditional native repair theorem.

## Subsequent native geometry and remaining bridges

With canonical GF and a common legal Age at the endpoint, the native
joint votes and both selection modes have the same canonical GF and
next legal Age, regardless of flags, Info, other private words or
instruction. The actual native interfaces and all475136 legal clock
increments were proved in the SP30 native certificate used by J189.
Induction therefore preserves GF and the common clock for every later
noiseless tick. No fresh-private start is needed for this native-only
invariant; no self-simulation or stored-data recovery follows from it.

The original J191 history is currently proved only through its fifth
shrinking pulse and next bank. Its sixth/eighth pulses and terminal
signal-window premise have not been supplied. This theorem cannot be
applied to that history merely by extrapolating T(L,R) displacements.
The all-free terminal domain's earlier unresolved selector is still
an abstraction failure, not a counterexample; this proof uses a tighter
explicit premise. Continuing E0 noise, arbitrary GF phases/widths,
clock/private defects, complete upper restoration, higher-error map
and positive iid noise rate remain unproved.

| Step | Status | Limit |
| --- | --- | --- |
| Actual restricted projection and primitive domains | **proved previously; apply** | Same frozen SP30/factor, no fresh errors during6144 clocks |
| Finite controlled-window domain run | **proved finite recurrence certificate** | All6145 rows, every GF site, final native singletons |
| Infinite-line domain inclusion and translation | **proved** | Every correlated infinite signal assignment with the stated56-colony premise |
| Conditional terminal native repair and later noiseless GF/Age invariant | **proved** | Half-colony512-phase defect with specified signal/native start |
| Actual original-error terminal history/all-data restoration/general eroder | **unproved** | Later signals/pulses and the window premise must be derived |
| Higher map/positive iid epsilon/minimum global change | **unproved** | Native repair of this class does not supply all-level noisy quantifiers |
| Gray/Gacs verbatim applicability to SP30 | **unproved; not claimed** | The rule was explicitly changed earlier |

No active G17/CURRENT or accepted-source change, numerical whole-CA
trajectory, hidden rule modification or commit occurs here.
