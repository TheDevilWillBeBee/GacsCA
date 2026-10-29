# GMW6: continuing pure-E0 coupling under quiet canonical geometry

This is a separate extension of the frozen
[prepared evaluator theorem](GMW6_TOKEN_WORD_EVALUATOR.md).
It concerns the unchanged, explicitly altered GMW6 rule, including its
59392-bit immutable stores, h1 predicate, computed-holder service controls
and fixed-zero native Workspace outputs. It is not a theorem about Gray's
physical protocol or higher-error repair. Sources:
[actual kernel](gray_token_word_v6.py),
[cofactor/checker](check_gray_token_word_v6_E0.py),
[read-only validator](validate_gray_token_word_v6_E0.py),
[receipt](../../../figs/gray_counterexamples/GMW6_E0_component_certificate.json).
No earlier source or receipt is modified.

## Exact noise and reference hypotheses

Write S=(0,-2,-1,1,2). A configuration X is in the quiet family C(tau)
when at every integer x its native GF is x mod8192, Age=tau in[0,1048576),
and all four native flags are0. Each SF field n has a logical value
W_n(y) at every integer y, with X_x.n[q]=W_n(x+S[q]) for all five slots.
These words can be arbitrary legal values: Head2200 bits, Mem1100 bits,
and Out/Info/Scratch/Programme100 bits. Head presence, metadata, registers
and the number of logical heads need not satisfy an execution invariant.
This is a coherent lower state, not a claim about a recursive hierarchy.

Let D be any set of integer sites such that every eleven consecutive
sites contain at most two points of D. Replace the entire cell at each
site in D by an arbitrary legal alphabet symbol. The adversary may change
every native field, every head/control word, every tape word and every
copy, and may adapt values to the entire history. The two immutable stores
are fixed constants of the transition, rather than mutable cell fields;
errors do not change the transition rule. No constraint is imposed on the
corrupted values beyond legal alphabet widths.

**One-step theorem.** If Z is obtained from X in C(tau) by these replacements,
then F6(Z)=F6(X), and F6(X) belongs to C((tau+1) modU).

**Continuing theorem.** Fix X0 in C(tau0). Let X_(t+1)=F6(X_t). Put
Z0=overwrite(X0,D0) and

    Z_(t+1) = overwrite(F6(Z_t), D_(t+1)).

Each row D_t obeys the eleven-site bound above, with independently arbitrary
whole-cell replacement values. Then F6(Z_t)=X_(t+1) for every t, and Z_t
differs from X_t only on the **current** row D_t. There is no retained
previous-row wake. Consequently each five-holder majority of any SF field
in Z_t equals the clean logical value in X_t.

This proves a deterministic coupling for any such history, not an iid
theorem. Gray's pure-E0 histories are a subclass: each E0 group is a singleton
or an adjacent spatial pair at one tick, separated from the rest of the
history by(24,24). At the same tick, points of different groups are at least
24 sites apart. An eleven-site row cannot intersect two groups; it has at
most two errors. Original lambda24 and c104 are retained. Since there are
no real1 groups here, c104 plays no role in the local correction argument.

## Native footprints and all-payload reduction

Fix an output holder x. Its native cone is[x-5,x+5], so it contains at most
two corrupted sites. In each five-site right or left GF vote, at least three
correct inputs adjust to x modQ. This remains true across colony boundaries
because the GF adjustment is moduloQ. Every whole-word majority exists and
equals the correct reference GF. Right and left Age votes likewise have at
least three copies of tau. Their central defaults, which may be corrupted,
are never used. This proves the geometry vote statements for **every** legal
13-bit GF and20-bit Age replacement; no sampled value assumption is used.

The in-colony predicate is therefore the correct one:0<=x modQ+j<Q.
Inconsistency tests count at most two incorrect left GF values or at most
two incorrect left Ages. The missing-majority predicates are false. Thus
inconsistency is0.

The Flag1 right front needs either three distinct positive right sites,
or old self Flag1 plus two distinct positive right sites. Its Workspace1
source needs three distinct sites in the entire in-colony native cone.
All positive inputs are corruptions of reference zeros. Each trigger would
need at least three different sites, while there are at most two. New Flag1
is0, including at a corrupted holder.

The missing-GF Flag2 source is0 because the right GF vote exists. The
Workspace2 source needs three different sites, so it too is0. Turning Flag2
on needs four positive left sites; it cannot occur. If old self Flag2 is1,
self is a corrupted site, leaving at most one positive left site. The h1
healthy erasure predicate (left-inside count<=1) therefore clears it. New
Flag2 is0. Both native Workspace outputs are identically0 in GMW6.

Native selection uses the correct right GF/Age, incrementing the latter
moduloU. In particular the raw-self-GF comparison in the wipe is harmless
here: its new Flag1 conjunct is0 even if old self GF is corrupted. The
wipe cannot erase a field at a previous or current error holder. This proof
does not assume the corrupted native metadata or service control is correct.

The checker exhausts all67 subsets of size at most two in[-5,5], all16
possible four-flag payloads per corrupted site, and all11 distinct in-colony
mask classes. The156827 exact native cofactors use the actual scalar native
function; the preceding three-correct majority reduction extends their
result to all GF/Age payloads and legal common clocks. Flag front and
source footprints are the full[-5,5] cone, not a narrower head-centre cone.

## SF reads, metadata/controller correction and family closure

For output slot s, the destination logical coordinate is y=x+s. Each old
field vote at y reads the five **actual** holders x+s-t, t in S, in an
interval of width five. At most two of them are corrupt. At least three
contain the exact same reference logical word. Bitwise3/5 voting therefore
returns that word, for every bit of every field, including all2200 bits of
Head, all1100 bits of Mem and all100 bits of its mutable Programme.

The three possible incoming heads are at y+d, d=-1,0,1. Their holders are
x+s+d-t; these lie in[x-5,x+5]. The same reconstruction applies to every
candidate, including arbitrary P/movement/mode/PC/target/args/register
values. Every candidate acceptance, collision, invalid-state guard,
instruction lookup, operand source/lane and write is consequently identical
to the reference transition. No assertion that a malformed corrupted
metadata word is safe is needed: it is reconstructed before interpretation.

All phase controls use the already corrected holder's new native Age.
Service Address is(newGF(x)+s)modQ=y modQ; it does not read the raw source
GF or another site's computed GF. This covers reset, birth, active, rest,
printed Programme and Age0 Info commit, including the explicit repair of
the earlier GMW0 raw-GF birth convention. The wipe is0. These are all ports
of the total kernel: no raw cell-state controller remains outside the
native votes or SF votes. Immutable CODE/BITCODE produce identical table
outputs in both trajectories. It follows that every output bit agrees.

For closure, evaluate the same formulas on X. Every destination logical y
has identical phase, service Address, incoming words and data at all five
holders. Thus its five output copies are equal. Native geometry and flags
remain quiet and canonical as proved above. This establishes F6(X) in
C(tau+1). It does not require a unique head or a special programme input.

The continuing claim now follows by induction: if the noisy input differs
from the clean reference only on D_t, the one-step theorem erases all of
those differences before the next row is overwritten. Only D_(t+1) remains.
The proof never unions earlier errors with the current row.

## Prepared evaluator consequence and limits

Apply this coupling to the preloaded, coherent, quiet initial lower state
of the frozen GMW6 prepared theorem. Its clean execution halts within47913
updates after birth, produces all191 correct Out words, retains them, and
commits them to Info at Age0. With continuing pure-E0 whole-cell overwrites,
the three-of-five Info decoder at that boundary produces exactly the same
raw upper transition. A current error may corrupt at most two holders, so
the conclusion concerns voted decoding, not equality of every raw holder.
No initially incoherent tape, a real1 core, or damaged native front is allowed.

| Step | Status |
| --- | --- |
| All-payload native correction, flags0, wipe0 | **proved under quiet-family and row-bound premises** |
| Actual native projected finite cofactors | **proved finite Boolean cases; GF/Age extension above is algebraic** |
| All SF/controller/metadata reads corrected and quiet-family closure | **proved** |
| Continuing-current-row coupling and five-holder decoder | **proved** |
| Prepared fifth-stage result with continuing pure E0 | **proved conditional extension** |
| Earlier gathers, hardwirer, native simulated-flag pulse and whole period | **unproved** |
| Real1/higher/intact hierarchy, Gray refinement, iid reliability | **unproved** |

Constant-zero Workspace is an explicit reason this quiet-family closure
does not transplant directly to Gray's protocol. Nothing here repairs
its missing native higher-error mechanism or justifies smaller U.
