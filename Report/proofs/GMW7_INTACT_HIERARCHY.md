# GMW7: an explicit intact infinite hierarchy and its restricted all-time theorem

This is a corollary of the changed-rule period theorem in
[GMW7_SINGLE_GATHER_PERIOD.md](gray_counterexamples/GMW7_SINGLE_GATHER_PERIOD.md).
It uses that exact frozen F7, Q=8192, U=1048576, radius5, Word100 alphabet,
single32Q snapshot, extra immutable dictionary, h1 and fixed-zero Workspace
outputs. It changes no rule, programme, constant or active G17 source.
It does not reconstruct Gray and does not prove reliability under iid noise.

## Initial configuration on the whole line

Let S=(0,-2,-1,1,2), p=4001, W=191. In the actual raw-cell word listing,
the five Info words have indices176,...,180. Define a logical Info word
A(y) for each integer y as follows. Write y=gQ+r, 0<=r<Q, with Euclidean
division, and put w=r-p.

* If w=0, put A(y)=g mod Q.
* If w=176+i for some i in0,...,4, put A(y)=A(g+S_i).
* Otherwise put A(y)=0.

All words belong to0,...,Q-1, hence are legal Word100 values. The recursion
is well founded. A recursive residue is one of4177,...,4181, so |y|>=4011
on the infinite line, including negative colonies. Its parent satisfies

    |g+S_i| <= |y|/Q + 3 < |y|.

The final strict inequality holds for every |y|>=4011 at Q8192. Induction
on the natural-number rank |y| defines a unique A everywhere. This is a
definition on Z, not a finite-ring boundary condition or a limit chosen
by experiment.

Define X as follows at physical site x:

    Address=x mod Q, Age=0, all four native flags=0;
    Info copy i=A(x+S_i);
    all Head, Mem, Out, Scratch and Programme copies=0.

Each SF field is coherent in precisely the rule's holder convention: slot
i at x stores the logical value at x+S_i. Head0 is a legal absent packet;
all native fields have their legal widths. Initial Programme0 is permitted
by the broad E7 relation; actual instruction execution uses the immutable
stores and the rule prints mutable Programme data later.

## Self-encoding and an intact hierarchy

The actual `cell_words(X_g)` listing has:

    word0 = g mod Q;
    words176+i = A(g+S_i), i=0,...,4;
    all other words =0.

For each represented primary gQ+p+w, its logical Info is A(gQ+p+w).
The preceding definition gives exactly `cell_words(X_g)[w]`, for every
integer g and every w=0,...,190. Other logical Info and private values are
legal, coherent and permitted by E7. Therefore

    X belongs to E7(X), and D(X)=X.

Taking the same X at every level provides an explicit intact infinite
hierarchy. There is no unproved inverse-limit existence assumption and
no auxiliary-primary alias requirement. Native GF/Age/flags and all SF
copy conventions are satisfied simultaneously at every level. This is
an intact initializer for the explicitly changed GMW7 family only.

## All-time noiseless hierarchy

The cited period theorem proves, for every legal raw upper configuration C
and every Y in E7(C),

    F7^U(Y) belongs to E7(F7(C)), D(F7^U(Y))=F7(C).

We also need its intermediate-time consequence. In the quiet lower
trajectory, computed Age goes0,1,...,U-1,0 and logical Info is unchanged
until the actual Age0 boundary commit. Therefore for every0<=r<U,

    D(F7^r(Y))=C.

All represented Info words remain legal upper raw words because they
are still the original C words. No claim that the intermediate physical
configuration itself has boundary Age0 is needed. The logical SF/native
quiet family remains coherent throughout, as proved in the period argument.

Inducting on completed periods gives, for every t>=0,

    D(F7^t(X)) = F7^(floor(t/U))(X).

Here the induction starts with X in E7(X), and every boundary configuration
is again in the E7 relation with its actual next upper state. Applying
the same identity to the right-hand configuration and using
floor(floor(t/U^n)/U)=floor(t/U^(n+1)) proves, for every n>=1 and t>=0,

    D^n(F7^t(X)) = F7^(floor(t/U^n))(X).

Every decoder invocation is on an image with legal represented native
words; no arbitrary-state total decoder is being assumed. The equation
specifies one fixed rule at all levels and maintains the full hierarchy
for all time without noise. Spatial scale is Q per level and time scale
is U per level. All assertions hold pointwise on Z.

## All-time coupling under a row-density restriction

Let R_t be any set of physical sites such that each interval of eleven
consecutive sites contains at most two points of R_t. At each t allow
arbitrary legal whole-cell replacements on R_t. Starting Y_0=X, define

    Z_t = overwrite(Y_t,R_t),  Y_(t+1)=F7(Z_t).

The cited universal quiet-family coupling theorem is

    F7(overwrite(Y,R))=F7(Y)

for every quiet coherent Y and every such R. Its proof uses the actual
five distinct holders within radius five, corrected native/control/service
votes, coherent SF closure, and no previous-error wake. It covers load,
transport, head execution, resets and commit, with arbitrary legal error
payloads. It is not inferred from the finite replay payloads.

Quiet-family closure and induction now give Y_t=F7^t(X) at every t, even
for an infinite support R_t satisfying the local restriction: equality
at a site reads only its finite radius-five neighbourhood. The first
decoder on Z_t votes five distinct holders in a radius-two interval,
which has at most two replacements, and exactly recovers D(Y_t).
Subsequent decoders act on that recovered clean upper configuration.
Consequently, for every n>=1 and t>=0,

    D^n(Z_t) = F7^(floor(t/U^n))(X).

In particular this holds for continuing original Gray pure E0 errors,
since lambda24-separated singleton/spatial-pair groups imply the row bound.
Separation c104 is retained in the classifier but is not needed for this
local condition. The row-density restriction is broader than pure E0 and
still does not include arbitrary real1/higher error sets.

## Exact limits and evidence

For iid site/tick errors with any positive rate, the required row-density
restriction does not hold almost surely. Already at one tick, infinitely
many disjoint three-site blocks have probability epsilon^3 of all being
errors; their independence makes at least one such block occur almost
surely. A fully faulty three-site block violates the eleven-site bound.
Thus this theorem supplies no positive iid threshold. It also supplies
no all-time fixed-site bit decoder or bit-memory theorem. The initializer
here encodes a structural hierarchy, rather than selecting a remembered bit.

The companion [checker](check_gmw7_intact_hierarchy.py) verifies the actual
field/word/slot contracts and retains finite initializer, holder and
large-coordinate recursion checks. Those checks supplement the universal
rank, self-encoding, period and coupling inductions above; they do not
replace them. It pins the frozen changed rule, programme builder, period
proof/certificate, prepared and bound receipts, and ancestor coupling proof.
No whole-CA numerical trajectory or random-noise experiment is used.
The initial root checker failed before any checks because the repository
root was absent from its module search path. Its source/log/failure receipt
are retained; adding that path fixes the import without changing F7 or
the initializer equations. The agent independently reviewed the rank,
word contracts, held-Info lemma and shared-history decoding argument.

| Step | Status | Scope |
| --- | --- | --- |
| Terminating legal logical Info on all Z | proved | Strict absolute-coordinate rank at all recursive residues |
| X in E7(X), simultaneous intact initialization at every level | proved | Exact actual191-word/slot contracts; changed GMW7 only |
| D^n(F7^t(X))=F7^floor(t/U^n)(X) | proved | Period theorem plus Info persistence and induction |
| D^n(Z_t) same under row-density errors/pure E0 | proved | Universal arbitrary-payload quiet coupling/current decoder |
| Faithful Gray/G17, real1/higher repair, positive iid rate, bit memory | unproved | The noise hypothesis fails almost surely under positive iid errors |
