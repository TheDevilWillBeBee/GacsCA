# SP28 native/epoch subsystem has a finite travelling clock island

This concerns a precisely reduced operator, not the autonomous full
SP28 rule. No rule, constants, ROM or compiler is changed. Canonical GF
is fixed; Age and the two native Flags evolve by the actual SP28 native
maintenance and epoch equations, including the distant joint GF/Age
refinement. At every input, Workspace flags, packet/code/service fields
and backward pressure are constrained to zero. Thus service forcing is
only the actual right-epoch force. The full rule has additional dynamics
on the excluded fields; an all-time full-rule realization is unproved.
The final native Flag2 commit reset is retained. It does not change this
orbit: both active pulse segments avoid either clock's wrap, and Flag2
is already zero on the force-free segments containing the wraps.

Under these assumptions, finite native damage need not disappear.
The construction below is an exact finite computer-assisted orbit proof
for this reduced operator, composed with two elementary invariants.
It is not an iid experiment or a full-rule counterexample.

## Exact binary reduction

Use Q1024, U475136, TF278401 and epoch length4096. Raw GF is x modQ.
At time t, each raw Age is either the legal clock t modU or the legal
clock (t+TF) modU. Represent its phase by a bit l(x) in {0,1}. The two
clocks are always distinct, and legal increment preserves their labels.

In each five-holder joint GF/Age block, all adjusted GF words coincide.
The whole-word vote therefore selects the phase occurring at least three
times. All four block existence bits are true. The joint three-of-four
vote selects label1 if at least three block votes are1, label0 if at most
one is1, and the raw self-label if the votes split two/two. This is the
literal refinement, not an approximation of mixed-radix clock arithmetic.

After refinement, both native GF directions are canonical and exist.
Each directional five-clock vote is a three-of-five binary vote. Let r
and l be the right/left voted labels. The only remaining Age-dependent
Flag1 diagnostic counts in-colony left labels unequal to r. The native
joint-right predicate is always true. Its quiet-joint predicate counts
right labels equal to r whose raw Flag1 is zero. Keep the actual eight
right Flag1 inputs, the self/two-support term, the guarded quiet failure,
the candidate-B Flag2 erasure/on predicates and the epoch force unchanged.
The d3 source is false because canonical GF exists; both Workspace sources
are zero by the reduction's hypothesis. The left-Age fallback is inactive
because the left GF exists. These substitutions give exactly the Boolean
operator in native_clock_island_reduced.c. Epoch forcing is enabled for
label k precisely when (t+k*TF) modU lies in [TF,TF+4096).

The C loop performs only these Boolean/count operations. There is no
floating arithmetic. The checker additionally compares a retained first
update to the full literal SP28 netlist at the corresponding zero-auxiliary
inputs. That finite comparison is a supplementary check; universality of
the reduction rests on the substitutions and whole-word/count argument.

## Force-free aligned template

Let a<b be multiples of Q, b-a at least Q and at least74. Set label1 on
[a,b), label0 outside it, native Flag1=1 on the complete colonies
[a-Q,a) and [b-Q,b), and native Flag2=0 everywhere. This template is
fixed in label/Flags on every row when neither clock label enables epoch
forcing. The two legal clocks still increment.

For one clock edge, the distant refinement preserves every raw label:
on the good side two entire sample blocks have that side's label, so
a wrong three-block quorum is impossible and the correct raw default
is kept; on the other side the same argument uses its two other blocks.
All refined GF words remain canonical. At a true colony start the left
clock mismatches are outside the apparent colony. At the preceding
colony's last three sites the right majority differs from the left clock,
so inconsistency makes Flag1=1 and selects the left clock. Within that
preceding colony the Flag1 self/support and quiet-failure terms maintain1;
in the following colony the right quiet majority maintains0. Flag2 has
no positive input or source. Thus neither edge nor the native flags move.

The checker pins150 literal refinement cofactors and4130 actual native
maintenance/epoch cofactors at both edge orientations, including every
GF phase and both endpoints of the preceding Flag1 colony. The general
transfer to any two unequal legal clock labels follows because all
remaining clock decisions use only equality/multiplicity; the successor
map is a bijection on the U legal clocks. Two edges separated by16Q
have disjoint exceptional neighborhoods. Uniform regions obey the same
identities, so this proves the infinite template invariant.

## Finite pulse computation and the infinite-line lift

Initialize the template with a=128Q, b=144Q at time0. Use the exact
binary operator on a256Q periodic array and retain every boundary state.
Evaluate rows0,...,6Q-1; at time6Q the template is

    a'=117Q, b'=132Q, width15Q, Flag2=0.

Both phase labels have epoch force zero throughout [6Q,TF), so the
proved template invariant advances exactly to TF. Evaluate rowsTF
through TF+6Q-1; at timeTF+6Q the template is

    a''=105Q, b''=121Q, width16Q, Flag2=0.

Both forces are zero through the remaining rows up to U, so the template
invariant gives this same label/Flag state at U. It is the initial
template translated by -23Q, with both absolute clocks returned to their
initial values. The finite computation checks every output site/row of
both6144-row pulse segments; it does not sample intermediate times.

The ring computation equals the stated infinite-line computation.
Relative to the entirely label0 uniform reference, a label outside the
current label1 support interval cannot acquire label1 through refinement:
its two outward sample blocks are label0, so a wrong quorum is impossible
and its raw0 is retained. An output outside that interval enlarged by3
has at most two potentially wrong refined clocks in either five-clock
vote. Consequently the label support grows by at most3 per evaluated row.
Outside this label envelope, Flag discrepancies propagate at most8 per
row: their only nonlocal native inputs are the eight right or five left
Flag inputs, while local clock diagnostics and force predicates see only
the five refined clocks. The force-free jumps introduce no new support.
Initial Flag support lies in [127Q,144Q). There are12288 evaluated rows,
and8*12288=96Q. Both array margins exceed96Q, so no wrapped input can
affect the exceptional state. Uniform regions have the exact periodic
GF/Flag reference. This is an actual influence bound, not a generic
radius37*U causal-cone assumption.

The operator is translation invariant under Q-site translations and its
two force schedules have period U. Therefore induction gives the same
finite wrong-clock island translated by -23nQ at every nU, for all n>=0.
It never vanishes. Each fixed site nevertheless eventually lies to its
right forever, so this orbit is compatible with pointwise eventual
recovery. Thus pointwise native recovery does not imply a finite eroder.

## What this does and does not rule out

The reduced native/epoch mechanism has no unconditional finite-island
eroder theorem under the stated zero-auxiliary hypotheses. A proof for
full SP28 must use additional facts about workspace/simulation/service
evolution or establish a different confinement mechanism. It cannot
derive extinction from the reduced equations or pointwise recovery alone.

For the full rule, Workspace flags and packet/code outputs are generally
nonzero even when their current inputs are zero. Holding them zero on
every row is an external constraint, not a legal noiseless full trajectory
and not an allowed isolated iid error history. No all-time full-rule
realization, iid failure, Gray/Gacs refutation or sufficient rule change
is established. The existing SP28 global E0/real1 native theorem and
right-half-line recovery theorems are not contradicted.

The first root provenance validation failed because its proposal-source
lookup expected the exact label SP28, whereas the new receipt used
SP28 native/epoch reduction. The original receipt and failure are retained;
the corrected receipt uses SP28 plus a separate reduced-operator label.
This metadata correction changes no rule, orbit or proof conclusion.
