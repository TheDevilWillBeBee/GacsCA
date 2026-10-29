# SP31: the current second-source enclosure does not imply a shrinking pulse

This is a conditional countercase to one proposed local lemma. It is
**not an actual error-history, Gray, G17 or memory counterexample**.
The isolated F31 rule, ROM, Q1024/U475136 and radius37 are unchanged.

## Exact result

Use the native/Info quotient proved in [J225](SP31_FIRST_PULSE.md),
with common legal clock TF+n, no new physical error or special Info
write in the following6144 ticks, and initial native template T(135,146).
The initial wrong GF interval is [137728,149504),11776 sites.
Set the Flag1 sources to [J229's actual pattern](SP31_SECOND_SOURCE_ENCLOSURE.md).
For this conditional calculation, assign all18 bits left free by J229
to1, and all other Flag2 sources to0. The logical Info votes initially
agree among all five holders. Subsequent Info erasures and all native
Flag2/Workspace fields evolve by the unchanged quotient equations.

**Conditional finite theorem.** At elapsed6144 the native state is
exactly T(133,149), with wrong GF on [135680,152576),16896 sites,
Flag1 on [135168,135680) and[152064,152576), and all native Flag2
and Workspace fields0. The wrong-GF width has **increased by5120=5Q**;
the left edge moved−2Q and the right edge+3Q. The common clock has
advanced6144 correctly. Consequently the assertion “every member of
J229's source enclosure gives a width-decreasing second pulse” is false.

Three other selected assignments — all0, only MF3(124)=1, or only
MF515(145)=1 — give T(142,149), width7680, a decrease4096=4Q.
These are separately conditional finite results. No quantified claim
about the other262140 masks or any mask's physical reachability follows.

## Why the finite calculation is a proof of this conditional result

The quotient of J225 section2 applies verbatim. It is an identity of
the F31 source equations on the binary adjusted-GF/common-clock
alphabet, not a statement restricted to J225's original two source
bits. Each odd five-GF vote exists and picks one of the two labels;
the distant four-block refinement either has three equal block words
or retains raw self. The native Age votes retain the common legal
clock. Thus this alphabet is closed and native source3 is false.
Both Workspace reads use the actual special voted Info and the literal
2048-tick guard, including the Flag1 condition for Workspace2.

For any primary y the actual Info quotient is

    M(y,n+1)=M(y,n)*majority(keep(y-slot,n): slot=-2..2),
    keep=not(newF1 and newGF!=refinedSelfGF).

It does not require coherence at later rows: all five new holders use
the same old vote before their own keep gate. The subsequent18 source
bits are not supplied independently; they undergo these actual erasures.
All private execution fields are irrelevant to this projection in the
stated no-special-write clock window. This is the earlier proved
closed-factor reduction, with a different initial source assignment.

[The wrapper](unregistered_sp31_second_pulse/sp31_second_enclosure_cases.c)
includes the byte-pinned frozen `sp31_two_flag2_sources.c`, renaming only
its old main. It supplies the new initial native segments and the
four source tracks. It changes no `local`, `refined`, `step`, Info
erasure or report equation. Its sorted Info list contains the exact
Flag1 pattern and selected Flag2 mask, not a driven boundary.

The same exact infinite-line event partition from J225 section3 applies.
Cuts include each native segment endpoint shifted by every offset
−37..37, and both GF phases' colony/inside boundaries shifted−8..8.
On each resulting interval every raw stencil tuple and inside predicate
is constant, and each guarded Info read refers to one fixed colony
primary. The frozen step checks endpoint stencil/guard/output equality
before accepting the interval. Cuts/segments are capacity checked;
the zero exterior is closed. This is a finite exact execution of the
quotient on Z, not sampled endpoints of a varying interval or a ring.

The retained four traces contain all6145 rows and their endpoint
segments/Info sets. The all-one run executes17,045,068 certified event
intervals, with at most110 stored native segments; it has two rows
with GF holes, which are not suppressed. Its final three segments are

    [135168,135680,2], [135680,152064,1], [152064,152576,3],

where bit0 marks wrong GF and bit1 Flag1. There are no other nonzero
native segments. This proves the stated endpoint and width arithmetic
under the supplied initial conditions. The read-only checker rebuilds
the unchanged diagnostic binary and independently replays the all-zero
and all-one traces byte for byte. The other two traces remain pinned
selected finite executions, not an all-mask proof.

## What this rules out, and what remains open

J229 proved a superset of the actual second sources, not that its bits
are independent or that the all-one assignment can arise. This result
therefore **does not prove that the actual J225 repair history expands**.
It proves that a uniform shrinking-pulse lemma cannot be deduced from
that enclosure alone. A proof can instead characterize the actual
Age/Workspace banks more closely, establish correlations excluding the
countercase, or use a multi-pulse argument allowing temporary growth.
No such argument is established here; no route is claimed necessary
for every possible reliability proof.

The native-only countercase does not determine its later simulation
banks. The width increase is not by itself a violation of Gray's
higher-error boxes, eventual repair or remembered-bit assertion. No
smallest rule/constant change or positive iid epsilon follows.

| Step | Status | Scope |
| --- | --- | --- |
| F31 native/Info quotient and binary/common-clock closure | prior proved argument applies verbatim | J225 source identities; changed initial source assignment |
| Four supplied source masks and exact event executions | proved conditional finite results | No physical source reachability asserted |
| All-one mask gives T(133,149), width+5Q | proved | Read-only all-row replay and endpoint arithmetic |
| Uniform shrinking-pulse implication from J229 enclosure | disproved | Countercase belongs to that conservative enclosure |
| Actual mask/correlations, actual second pulse and later banks | unproved | Requires same-history source characterization |
| Arbitrary eroder/higher map/Gray or G17 failure/iid/minimum change | unproved | No operational counterexample or reliability theorem |
