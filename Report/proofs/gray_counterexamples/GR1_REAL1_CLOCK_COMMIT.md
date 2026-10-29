This is an exact finite real1 witness for the explicitly changed GR1 rule.
It is not a counterexample to the accepted pure-E0 encoded-period theorem,
corrected Gray, intact recursive initialization, or iid memory reliability.

Use the fixed GR1 rule F, Q=8192, U=1048576, its pinned ROM and the broad
encoding family E(s) defined in GR1_NOISELESS_PERIOD.md. Choose upper s_i
with Address i mod Q, Age0, all Flags0 and all other fields0. Choose every
unrepresented logical Info bit0. In lower colony0 every logical Info bit
is consequently0. The simulated upper system here is not an intact
recursive hierarchy: its upper simulation fields are0. This distinction
is part of the witness's scope.

Start noiselessly at time0. At time1 overwrite the five adjacent holders
3865,…,3869. Change only their Age to U−1 (the legal all-one20-bit word)
and their five Hold bits to1. Leave their Address, Info, native Flags and
all other fields at their correct values. This is one original real1
error: no point is E0, its width is5 and duration1, two of its singleton
candidate0 subsets are linked, condition(iii) with c104 holds by width,
and condition(iv) is vacuous. The exact classifier receipt confirms this.

**Local clock/commit result: proved.** At clean time2 the only incorrect
Age values are at3868,…,3872, and equal0. The computed Age0 branch commits
the corrected Hold values into Info even though the actual work period
has not ended. Primary Info becomes1 at3868 and3869. At time3 its five
copies are coherent and remain1. Info3868 represents upper Reg bit2;
Info3869 is unrepresented. The actual error never overwrites Info.

The complete literal GR1 netlist/ROM is evaluated for these first two
clean updates. All inputs and outputs are Boolean, with no numerical
approximation. The retained512-site array is only a way to evaluate a
finite dependency cone: its nearest boundary is254 sites from the errors,
while the first three updates have radius15. Every checked input ancestor
lies in lower colony0 of the stated global E(s) configuration. Periodic
wrapping cannot influence the witness. The source, full initial/error
states and cone frames are retained in the receipt and NPZ asset.

**Clock advection and recovery: proved.** Address remains canonical
regardless of the noncommon Ages: both directional Address votes equal
the canonical value, so either selected direction gives it. Thus the
GF-dependent simulation wipe is0. At time2 define a=3868. The Age island
is[a,a+4], carrying actual-time-minus2; the remaining clocks equal actual
time. Flag2 and both Workspace flags are0. Flag1 may be arbitrary to the
left of or within the island; it is0 to its right.

Every directional five-word clock list has only two unequal values.
Its whole-word vote selects the value occurring at least three times.
The Age inconsistency comparisons depend only on equality of those values.
The other possible Age predicate, the period16 condition d3, is disabled
by the existing canonical Address vote. Therefore the transition decisions
below hold for arbitrary unequal clock labels. Four concrete clock pairs
and all free left Flag1 bits certify620 literal native cofactors, including
the true-colony boundary cases.

For an interior length5 island[a,a+4], the first three positions choose
the correct clock. The five positions[a+3,a+7] have at least three wrong
left clocks, an inconsistency and computed Flag1=1; they choose the wrong
left clock and increment it. All later positions have at most two wrong
left clocks and stay correct, with Flag1=0. The island consequently moves
right3 sites per clean tick and keeps width5. At the true boundary Q,
left positions from colony0 are excluded from the next colony's apparent
colony, so no wrong clock or Flag1 passes into colony1. Every truncated
length1,…,4 case is checked; lengths at most2 have no wrong directional
majority and disappear in one tick. Thus all Ages are correct at

    2 + ceil((8192−3868)/3) = 1444 < U/32.

There is no second spurious clock wrap: after the first update the two
clock labels are t and t−2, both below96Q throughout this recovery. Both
Workspace outputs therefore remain0. Flag2 remains0 because its forcing
terms and left Flag2 inputs are0. Native canonical/common-clock closure
then preserves correct geometry. The previously proved clean flag-clearing
lemma clears any remaining Flags within another Q ticks, by9636<32Q.
This example supports, rather than refutes, native recovery at this scale.

**Three-colony simulation-field footprint: proved for GR1.** After time3
Info is coherent. A computed clock before its usual boundary cannot write
Info at3868 or3869: the only other intermediate Info writes have logical
Address3 or Q−3. Neither is this witness. The zero native wipe leaves Info
unchanged, even while native Flag1 repairs the clock island. Therefore
the Info difference persists until the usual period boundary.

At the second gather start32Q all Mailbox bits reset, with geometry
correct and all native Flags quiet. At32Q+1 Mailbox.L and Mailbox.R
snapshot the changed Info. Their exact five-copy route then shifts the
wrong bit one site left/right per active tick. At

    T=32Q+1+4325=266470 < 48Q

the same wrong bit originally at3868 occurs in Mailbox.L at−457 and
Mailbox.R at8193. Info3868 still differs at that tick. These positions
belong to colonies−1,0,1. Every claim about the later trajectory is an
explicit composition of the proved native recovery, clean flag-clearing,
selective reset, five-copy forwarding and stage-gated route identities;
it is not a sampled run out to T.

No fixed adjacent pair of colonies contains these simultaneous simulation
field differences. Therefore a GR1 analogue of Gray's literal Proposition4
pointwise all-simulation-fields two-colony envelope is false, for this broad
encoded context and one valid real1 error. This does not contradict any
accepted GR1 theorem, whose noisy hypothesis is pure E0. It also does not
show an incorrect decoded state at a period boundary.

**Printed Proposition4 audit: unproved for a faithful Gray completion.**
The proposition on primary PDF page36 / text lines1614–1623 speaks about
equality of the simulation structure fields at all points outside its
boxes. Those fields include Mailbox and Workspace, by pages32–34. Yet the
preceding argument on page35 / lines1589–1598 explicitly permits incorrect
Mailbox information in undamaged colonies and bases correct simulated
transitions on temporal voting. Equality of temporary transport fields
does not follow from equality of the simulated boundary states.

A faithful protocol that transmits a persistent wrong represented SimBit
to both neighboring colonies must account for this footprint as well.
That conditional observation is distinct from a proved counterexample to
a fully specified Gray rule: GR1 uses a different gather layout, a huge
two-index ROM, current corrected SimBit Workspace inputs, h1 correction
and a different damaged-state rest convention. Those refinement gaps remain.
The operational statement needed for reliability should specify its
decoder or permit temporary transport footprints; this audit proves no
smallest rule change that makes a complete iid proof succeed.

Reproduce with check_gray_staged_real1_clock_commit.py. The initial
exploratory checker wrongly required complete geometry recovery in24
ticks and wrongly guessed which primary would commit. Its source and
failure receipt are retained. The corrected proof uses the actual
advection and boundary law; no rule was changed. A second failed symbolic
node-identity check is recorded separately: the node simplifier does not
prove a four-to-one mixed-word majority by node identity, so universality
uses the explicit whole-word majority/count argument stated above. An
intermediate228-cofactor boundary claim is withdrawn and preserved: its
templates omitted the actual tail lengths4 and1. The final620-cofactor
certificate includes all near-edge full-length positions and every
truncated length1,…,4, so it covers the actual residue class of this island.
