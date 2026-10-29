# Full SP28 also has a travelling Address defect

This concerns the existing isolated SP28 rule, Q1024/U475136/TF278401,
with its actual own ROM. No rule, constants, compiler or backend is
changed. Unlike J154's clock island, this orbit keeps the native clock
correct and has wrong native Addresses forever somewhere on the line.
It refutes fixed finite higher-error Address confinement and a finite
native Address eroder for SP28. It is not a G17, faithful Gray/Gacs or
iid counterexample. Each fixed site eventually recovers its Address;
no subsequent random errors are included in the trajectory.

## Exact theorem

Let delta=Q/2=512, a=128Q-delta, b=144Q. At time0 set

    raw Address(x) = (x+delta) modQ on[a,b), x modQ elsewhere;
    raw Age(x) = 0 everywhere;
    raw Flag1(x) = 1 on[127Q,a) and[b-delta,b), 0 elsewhere;
    raw Flag2, Workspace flags, packet/code headers and backward pressure = 0.

All other private simulation fields and instruction inputs may be
arbitrary. Apply the full actual SP28 rule with no further errors.
At every nU, the native Address/Flag template is the initial template
translated by -12nQ, the clock is again0, and all auxiliary fields named
above are empty. Therefore there are16Q+delta=16896 wrong Addresses
at every such boundary. Their high Address bit is the opposite of the
canonical value. Actual private fields need not be periodic.

The state can be realized at physical time U from an intact recursive
hierarchy with exactly one dense17Q-site error row. It is actual real3
at c16 and actual real2 at c104, under the original recursive error
definitions. Restoring104 does not remove the orbit.

## Two Address phases and a common clock

Assume at some time t every raw GF is either x modQ or(x+delta) modQ,
and every raw Age is the common legal clock t modU. Assign labels0,1
to those GF phases. In a distant refinement block, displacement correction
converts every sampled GF into one of the two words at the reader.
The Age components are all equal. Its five-word vote therefore has
a three-word majority and selects one label. The three-of-four joint
vote selects1 for at least three1 blocks,0 for at most one1 block, and
the raw self-label on a two/two split. Its whole-word acceptance test
cannot introduce a third GF word. The Age remains common.

After refinement each directional adjusted-GF five-vote has a supported
majority of one label. Both Age votes have the common value. The native
selector returns either the right or the left GF word and increments
that common Age. Its fallback is inactive because the left GF exists.
This proves alphabet/common-clock closure, irrespective of flags,
auxiliary fields and the actual programme. Legal mixed increment was
already checked on all U clocks in the existing SP28 native certificate.
The full native/auxiliary wiring is pinned by J152's73 identities.

Inside predicates in the native maintenance use the right-voted GF

    v=(x+delta*RF_label) modQ.

The only nonzero mismatch diagnostic counts left refined labels unequal
to RF. The joint-right vote exists. Its quiet count uses right labels
equal to RF whose raw Flag1 is0. This gives the exact substitutions
in native_address_island_auxiliary_bounds.c. Native Age is a conclusion
of the full-rule induction, not an externally prescribed control.

## All packet/code/backward forces are redundant here

Both RF clock and existence are common/correct at every reader. Thus
the actual epoch force is1 everywhere on[TF,TF+4096) moduloU and0
elsewhere. Packet births can occur only in input rows TF+nU.

The counter-ancestry proof of J152 does not require spatially canonical
GF: every birth count is0, each valid nonbirth output inherits one
eligible count and increments it, and eligibility requires count<1791.
Commit can erase a record but cannot reset a surviving nonbirth count.
Initial headers are empty and batches are U apart. Hence valid packet/
code records and raw WF2 are gone by state TF+1793; even the unchecked
expired-packet cohort force ends at input TF+1792. Computed backward
force is clock-gated through TF+1792, with raw backward pressure gone
by TF+1794. All these possible native sources lie within the global
4096-row epoch. Their spatial origins, payloads and minimum-counter
competitions are immaterial for this inclusion.

Within that epoch, new native Flag2 is already1 because of the epoch
OR, so raw WF2 and packet/code/backward forcing change no native output.
Outside the epoch those sources are0. Thus omitting their computation
from this native projection changes neither a selected GF nor either
native Flag. This is unlike externally setting nonzero header outputs
to0: the actual headers evolve under the actual full equations, and
their ancestor/window bounds prove native redundancy. At U they are empty.

The remaining unspecified source is actual raw WorkspaceFlag1. Its
literal output is bounded between0 and the selected-GF last-five-site
guard times the common-clock window[TF,TF+2Q). It is0 from state
TF+2Q+1 until the next pulse. The projection propagates this upper guard
and allows every signal value independently within it. It consequently
includes all actual private simulation histories, including wipes caused
by an output GF differing from the reader's raw GF.

## Quiet template and monotone enclosure

More generally let a+delta and b be multiples of Q, with two edges
separated by more than74 and both partial Flag1 strips of length at
least16. Put phase1 on[a,b) and Flag1=1 on

    [a-(Q-delta),a) and[b-delta,b),

with Flag2/auxiliary inputs0. On every force-free row this native GF/
Flag template is fixed. Each sharp GF edge is preserved by distant
refinement: the two outward blocks exclude a wrong three-block quorum,
and the tie keeps the raw phase. The common clock still increments.

At the left edge a, the right phase's apparent GF starts at0; at the
right edge b, the right phase's apparent GF also starts at0. On the
three preceding readers, left-GF mismatch raises Flag1 and selects the
left phase. On the three following readers the in-colony left mismatch
is too small and the quiet/right tests give Flag1=0, selecting the right
phase. The flag support extends left within the appropriate apparent
colony: the phase0 partial colony preceding a, and the phase1 partial
colony preceding b. It stops at each apparent colony start. Uniform
regions keep their phase and have Flag1=0. With no GF-existence failure,
workspace source or existing Flag2, new Flag2=0 everywhere.

The checker verifies162 exact literal refinement cofactors and4258
literal maintenance cofactors, covering both edges, the partial strip
endpoints and all GF residues, with a free common clock word. These
finite identities plus the uniform-region argument prove the quiet
template on the integer line. They do not assume a prescribed Flag1.

For an active row, retain lower/upper arrays for Flag1/Flag2. With the
GF labels fixed, the inside predicates are fixed and A<=B for the
in-colony/full-left Flag2 counts. J154's monotonicity proof applies
verbatim to Flag1 and Flag2, with d3=0; its3072 literal assignments and
13824 upward edges check the same unchanged Flag2 fragment. If right
and left voted labels differ, the full interval selects RF when
upperFlag1=0 or lowerFlag2=1, and LF when lowerFlag1=1 and upperFlag2=0.
Otherwise the kernel stops instead of choosing a label. A certified
common selected label also supplies the next upper WF1 guard. Induction
therefore encloses all full-rule native histories on every computed row.

## Exact pulse, infinite line and all periods

The quiet theorem advances the initial template from0 toTF. Compute
every site/update of rows TF,...,TF+6144-1 on256Q periodic cells with
the universal flag bounds. All73728 distinct RF/LF Address-quorum
obligations have a common output; there is no ambiguous choice.
At TF+6144 both bounds equal the quiet template with

    a'=116Q-delta, b'=132Q,

and Flag2/WF1=0. The actual other auxiliary fields have expired by their
bounds. Quiet invariance advances to U, giving the initial native
template translated by -12Q. The full native-netlist corner comparisons
are supplementary checks; the universal projection/enclosure is proved
above rather than inferred from these sampled inputs.

The computation lifts to Z. Outside the current phase1 interval two
outward distant blocks contain only phase0, so refinement cannot extend
phase1 there. A reader more than3 beyond the interval has at least three
phase0 words in either five-direction vote. Thus GF support expands at
most3 per computed row. Relative to the uniform phase0 Q-periodic lower/
upper reference, flag discrepancies propagate at most8 per row; the
new WF1 guard differs only within the newly bounded GF support. In6144
rows this requires at most48Q extra margin. Both periodic-array margins
exceed48Q, so no wrapped input affects the exceptional computation.
The reference bounds may differ during the pulse but collapse to0 at
its endpoint. Arbitrary actual private signals need not be periodic.
Quiet jumps add no exceptional support.

Q-site translations preserve both GF phases and all native predicates.
The common legal clock/epoch schedules repeat every U. At U the native
template and empty auxiliary conditions are exactly reestablished at
shifted endpoints, while private inputs are still arbitrary. Induction
gives the orbit for every n. At intermediate times its GF support stays
within that shifted finite interval enlarged by48Q. Each fixed site
therefore eventually lies to its right forever, although the island
never disappears and has no fixed finite space-time envelope.

## One actual physical error from intact initialization

Use J154's integer-recursive H with H∈E28(H) at every level. Noiseless
physical simulation gives E28(F(H)) at U, with canonical GF, Age0,
native Flags0 and empty auxiliary fields. At that row change only GF
on[a,b) to the shifted phase and Flag1 on the two partial strips to1.
Every site of[127Q,144Q) is actually altered, and there are no other
physical errors. All unaltered simulation fields are allowed by the
universal native theorem, so this realizes the exact orbit.

The complete error-location set is the same dense17Q-site row classified
in J154. Its connected unit-link graph excludes real0 and proper real1/
real2 subsets by isolation. The whole row is too wide for candidate1,
is candidate2, and at c16 its first/last four-point candidate2 witnesses
violate real2 separation condition(iii). Their next-scale linkage and
the total diameter give an actual real3. At c104 the whole candidate2
already satisfies(iii) and is actual real2. This is the original recursive
classification, not just a burst-width label.

## Consequence for a reliability design

The fixed finite Address-envelope/finite-native-eroder step is false for
SP28, not merely unproved. An Address-only variant of the final probability
argument cannot assume that step for this rule. This also identifies a
necessary change: changing only the own ROM or private simulation updates,
while preserving these native equations, WF1 guard and auxiliary-force
time bounds, cannot remove the orbit, because the theorem already permits
all such private histories. Restoring an upper-command condition only
on packet births, with their forces still contained in the unchanged
global epoch, cannot affect this native projection either.

Some native/control interface must change, or a different probabilistic
argument must allow travelling defects. No particular sufficient change,
minimal change, iid failure or positive threshold is proved here. The
actual GF bit differs forever somewhere, but eventually recovers at each
fixed site. Continuing iid errors and island interactions remain uncovered.

| Step | Status | Limit |
| --- | --- | --- |
| Two-GF-phase/common-clock closure and auxiliary-force redundancy | proved | Initially empty auxiliary fields; no further errors |
| Quiet template, universal flag enclosure and exact pulse | proved | Specified half-Q phase and template; all private inputs allowed |
| Infinite-line/all-period native orbit and intact error realization | proved | One dense17Q row; not whole-state periodicity |
| Fixed finite higher-error Address confinement/finite native eroder | refuted | Wrong high Address bit travels forever |
| ROM/private-only cure with the same projection/interface | excluded | Native/interface changes or a different probability argument needed |
| G17/Gray/Gacs or iid failure; explicit ε; smallest sufficient change | unproved | Pointwise eventual recovery and later random errors not covered |

The exploratory kernel/log are retained separately as measured-only
pre-proof evidence. The final checker pins its source, quiet identities,
monotonicity dependency, full native wiring, pulse states, original error
classification and the written infinite-line argument. No GPU/noisy
full-state experiment is used for this theorem.
