# SP30: exact native refinement on a canonical half-line

This lemma concerns the unchanged frozen F30 refinement, Q=1024 and
four block centres -30,-10,10,30. It changes no rule or constants.
It does not assert that a noisy trajectory maintains a canonical
half-line, or establish general recovery or an iid noise threshold.

[Checker](check_sp30_half_line_refinement.py) and
[certificate](../../../figs/robustness/unregistered_half_line_refinement/certificate.json)
retain the algebraic interface checks and source hashes.

Fix an integer b and one raw Age word A. Suppose every physical
site x>=b has raw native GF=x modQ and Age=A. All raw native and
private fields to the left of b may be arbitrary. Then the actual
four-block joint refinement of the self GF/Age pair at every reader
x>=b is exactly (x modQ,A).

The same conclusion holds on x<=b if the left half-line is canonical.
More generally, at a reader having canonical raw self pair C, two
of the four existing block outputs equal to C suffice to force the
joint refinement to C, regardless of the other two block outputs
and their existence predicates.

## Proof for complete words, including arbitrary Age

Let C be any w-bit word. The literal block quorum first constructs
the bitwise threshold-three word B from four block words, and then
tests whether at least three existing block results equal B. It
returns B when that predicate holds and the raw default otherwise.
Assume two block words are C, both with existence true; the other
two words and existence bits are unrestricted; the default is C.

If B=C, both return branches equal C. If B!=C, the two specified
existing blocks fail the equality-to-B test, leaving at most two
possible matching existing blocks. The threshold-three predicate
is false, so the result is the default C. These are all cases. This
argument is independent of w, C and the bitwise threshold formula;
it uses the literal final equality/existence test. In particular,
the bitwise candidate cannot force a hybrid GF/Age pair here.

At any x>=b, the five sites in each positive-centre block are all
on the canonical half-line: their offsets are8..12 and28..32.
Subtracting each offset moduloQ from its GF gives x modQ, and
every Age is A. The whole-word five-way majority therefore returns
the pair C=(x modQ,A) with existence true in each positive block.
Raw self is also C. The preceding two-block argument now gives
exact refinement C; the negative blocks may be arbitrary. For
x<=b the two negative-centre blocks instead supply C. Integer
translation and GF wrap introduce no exception because adjustment
is moduloQ. This proves the stated universal lemma.

## Conditional physical consequence at the pulse's right edge

Consider a no-error F30 pulse whose actual native clock is common
and whose all-row raw/computed wrong-GF support is confined to
(-infinity,RQ), as independently checked in a pulse certificate.
Every raw pair at x>=RQ is canonical with that common Age. The
lemma makes refined self canonical there, too. Since actual computed
GF is canonical at those same sites, the literal wipe predicate
F1_new AND(computedGF!=refined_self_GF) is false there, even if
its native input footprint reaches left into the defect.

Consequently keep=1 at every actual SF reader x>=RQ. Together with
the common clock, actual fixed ROM, the prefix's coherent captures
and reset, this supplies the remaining native/keep premise of the
[quiet-frame late protocol](SP30_QUIET_FRAME_PROTOCOL.md) for the
entire true frame with origin RQ, and every frame to its right.
Its SF holder footprint is[RQ+1,RQ+1023], wholly on that half-line.
The compact-register and data operands of that protocol are inside
this footprint. No additional37-site native-footprint clearance is
needed for this particular implication: the lemma already proves
the exact refined self at the reader despite arbitrary left inputs.

Thus, under those actual pulse/prefix premises, the edge frame R
stores all31 native GF/Age/F1/WF1 output bits from its actual captured
assignment at commit, with the same arbitrary coherent Match word
allowed in the existing protocol. This consequence is conditional;
the lemma alone does not supply a pulse hull or an actual capture.

## What the checker establishes

The checker exhausts the actual Boolean block_quorum function for
word widths1..4, all defaults C, arbitrary other two words, and all
four choices of their validity bits. It also checks the actual
whole-word majority function on five identical symbolic pair words,
and the physical half-line/modulo geometry at every GF residue.
These are transcription and interface checks. The displayed
two-existing-block argument proves the result at arbitrary word
width, including the actual29-bit pair; the finite small-word checks
are not represented as exhaustive29-bit enumeration.

| Step | Status | Scope |
| --- | --- | --- |
| Two canonical existing blocks force the raw canonical default | proved | Every finite word width and arbitrary other blocks |
| Canonical half-line supplies those two blocks | proved | Every integer boundary and arbitrary raw exterior |
| Edge-frame late storage | proved conditional implication | Actual common clock, prefix captures/reset/ROM and pulse hull required |
| Actual multi-period bootstrap or general noisy recovery | unproved here | Requires its separate physical-history composition |
| Positive iid reliability, Gray/G17 refutation or minimum change | unproved; not claimed | This is one local lemma for frozen F30 |
