# SP28: a real1 core defeats an unrestricted two-colony upper-step map

This is a counterexample for the unchanged isolated SP28 artifact,
Q=1024, U=475136. It is not a modification of G17 or SP28. The initial
lower state is a complete E28(z), but its upper configuration z is not
an intact recursive encoding. No iid memory failure or refutation of
Gray's intact-hierarchy theorem is claimed.

## The statement excluded

Let D be the computed normal decoder of the actual lower state at U,
after starting from E28(z) and applying one actual real level-1 core.
The unrestricted proposed map would say that there is a fixed adjacent
upper pair A and a configuration y agreeing with z outside A such that

    D agrees with F28(y) outside A.

This even allows arbitrary replacements in that pair both before and
after the upper transition. The example below excludes every adjacent
pair A, including pairs not containing the physical core. Thus it also
excludes a single E0 upper event and any stronger fixed-pair input/output
coupling for every upper z. It does not exclude a map with larger boxes,
more events, or suitable operational/intact-upper hypotheses.

## Initial state and the only error

At the upper level, let GF(j)=j mod1024, Age(j)=0 and all fields other
than Info be zero. For each logical upper Info primary P in {-2,-1,0,1,2},
its five raw holders are j=P-2,...,P+2. Set the source holder j=0's copy
to zero; among the other four holders set exactly two copies to one and
two to zero. Concretely, choose the two smallest nonzero holders as the
ones. Every other Info primary is zero. These prescriptions use different
physical Info slots, so there is no conflict. Initially each affected
logical upper Info vote is zero, with two ones and three zeros.

This upper Info is deliberately incoherent. Its lower E28 encoding is
nevertheless a complete valid encoding of an arbitrary upper state, as
allowed in J138/J144. The five raw upper Info bits of source cell0 have
lower normal primaries a=92,93,94,95,96. They are all initially zero.

Use the raw input at lower tick t*=10Q+1=10241, immediately after the
second gather's load at input clock10Q. At the nine sites90,...,98,
replace the Info and right-mail copies of those five primaries by one,
and leave their left-mail copies zero. Specifically, for each primary a
and each holder x=a-2,...,a+2, set Info and MR slot(a-x+2) to one and
ML in that slot to zero. Leave every other bit unchanged, including
GF/Age/all flags, the histories and the interpreter fields. There are
exactly nine overwrite locations at one tick, of spatial diameter8.
They form one actual real1 set at lambda24/c16, with no E0 points and
no higher errors. The classifier and direct small-diameter argument
both establish this. There are no later errors.

The error changes only one lower colony's five represented upper bits.
It simultaneously changes one of the already loaded mail snapshots.

## Physical effect of all three gathers

All lower raw GF/Age remain canonical/common at every tick: the only
overwrite leaves them unchanged, and both native directions agree.
Before T_wf, lower Flag1 stays zero, because the actual error changes
no flags or geometry and WF1's clock guard is closed. After the pulse
begins, its signal source is also zero: each upper input tuple differs
only in Info, while upper native GF/Age/flags are still canonical/zero,
so the own programme's early upper Flag1 result is zero. Packet/service
pressure cannot change lower GF/Age or create Flag1 in these conditions.
Hence lower keep is one and mail is never masked in this example.

Immediately before the error, both mail tracks hold the second gather's
old Info. The injection replaces all five copies of each target primary.
On the next actual transition, five-vote correction gives Info=1 at a
and MR=1 at a+8, while ML remains its old zero reference. Exact full-rule
cofactors at all25 relevant readers check those outputs with all unrelated
work and instruction inputs free. Subsequent coherent-copy transport
preserves the modified MR ray and the unmodified ML ray. The actual
corrected fast window and all capture controls through distance37 are
the pinned J138 interfaces, not an idealized speed assumption.

For a receiver colony j>0, an input from source upper cell0 has negative
offset -j and is taken from right mail. Its three histories are old0,
modified-middle1 and new-last1. Their vote is one. For receiver j<0,
that source has positive offset and is taken from left mail. Its three
histories are old0, old-middle0 and new-last1. Their vote is zero.
At j=0, direct Info during evaluation is its new one. The last load
at20Q samples the now changed Info, so its value is one in both directions.
All other upper input fields and source cells are unchanged.

Every relevant lane has a unique physical reference and every copy
controller is correct. The actual own-ROM certificate therefore executes
F28 on precisely these local input tuples: a receiver j<0 sees source0's
five Info bits as zero, while j>=0 sees them as one. These tuples need
not be restrictions of one common upper configuration. They remain
constant for that receiver's early and final programme. All other inputs,
register/scratch invariants, Match and actual lookup identities are those
of the complete-start proof. The error occurs before evaluation and
changes no work field, so it introduces no additional programme premise.
The literal commit/reset identities give the complete decoded boundary
D. This is a physical composition proof for the finite adversarial case,
not a sampled U-tick campaign.

In particular, the actual five output copies for each upper logical
Info primary P, listed by holders P-2 through P+2, are

| P | Actual decoded output copies |
| --- | --- |
| -2 | 0,0,0,0,1 |
| -1 | 0,0,0,1,1 |
| 0 | 0,0,1,1,1 |
| 1 | 0,1,1,1,1 |
| 2 | 1,1,1,1,1 |

The checker independently evaluates the literal compiled upper F28
netlist on all nine actual receiver tuples and its real ROM lookup,
and verifies all25 values. The universal programme certificate then
lifts these tuple outputs to the actual lower boundary.

## Why no fixed adjacent pair works, even with independent input/output pairs

For any adjacent pair A, take any y agreeing with z outside A, with
arbitrary complete replacement words inside A. The upper one-step
native theorem applies to these two faults in the canonical/common
upper native state. All refined GF/Age inputs are correct, so keep is
one at every upper holder, even if a replaced raw GF is wrong. Upper
input clock0 is neither commit nor signal. Consequently F28(y) replaces
each logical Info primary by the same five-copy majority at all five
holders. Its Info outputs are fully coherent for every such y.

D's primary0 output has two zeros at holders -2,-1 and three ones at
0,1,2. Agreement with any coherent output outside a two-site adjacent
pair requires excluding both zeros: excluding all three ones is
impossible with two sites. Thus the only possible pair is A={-2,-1}.

For that pair, however, every raw holder of logical Info primary2 is
at0,...,4, outside A. Those original five input copies vote zero.
The literal Info update and repaired native controllers therefore make
every F28(y) output copy of primary2 zero. All corresponding D copies
are one, and all are outside A. This is a contradiction. No adjacent
pair A and no replacement y satisfy the stated map. QED.

In fact, let the input replacement pair P and the output exception pair
R be independent. The same native argument makes all F28(y) Info groups
coherent for every y=z outside P. Primary0 again forces R={-2,-1}.
But the actual primary-1 copies at holders-3,-2,-1,0,1 are0,0,0,1,1.
Outside this R, holder-3's zero and holders0/1's ones remain. They
cannot agree with one coherent F28(y) group, irrespective of P or its
payload. Thus no adjacent P,R and no y=z outside P can have D=F28(y)
outside R. Allowing singleton rather than pair exceptions is weaker
and is excluded as well.

## Scope and the missing reliability implication

The example proves failure of the unrestricted map for the actual SP28
boundary from arbitrary upper states. It is stronger than observing a
wrong intermediate mailbox or a hypothetical inconsistent tuple. It
does not invalidate J138/J144/J145, which allow only E0 errors. It does
not invalidate J125's native E0+real1 theorem: native fields remain
correct throughout this example.

Most importantly, z's incoherent upper Info is not an intact upper
encoding. The example gives no proof that this entire context can be
reached near an isolated real1 core from an intact noisy hierarchy.
Initial full hierarchy and actual error-class isolation may exclude it.
A valid reliability proof must establish and use the needed operational
upper-state restrictions, or prove a different simultaneous map. It
cannot use the excluded arbitrary-upper-state fixed-pair assertion.

The three-snapshot scheme alone does not ensure a shared upper input:
when the first and last source values differ, corruption of the middle
mail in one direction decides opposite majority outcomes. Any proposed
rule change must close this input-agreement issue and the other native/
higher confinement gaps. No smallest sufficient reliability change,
positive iid threshold, or iid unreliability theorem is established here.

The initial checker used slot2-x instead of4-x in its final check of
primary2's original vote. That assertion actually examined primary0.
The failed source and receipt are retained; correcting this slot index
changes neither the rule nor the stated witness or its physical output.
