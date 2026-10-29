# GAWN27: a many-offset native eroder with periodic missing-quorum sources

This is a deterministic lemma for **unchanged frozen GAWN2**, not a new
rule. Q=4096, U=524288, Word100, radius8, h1, own beta, lambda24 and
separation104 retain every declared departure in J268. In particular h1
is not Gray's printed Flag2 erase predicate. G17 is unchanged. No positive
noise rate or faithful Gray counterexample is established here.

## 1. Exact theorem — proved with the following premises

Take GAWN4's actual intact H2 trajectory at row T0=100Q+2=409602. Its
native fields are canonical and quiet with the common correct Age.
Let A=[b,b+w) be any integer interval with 0<=b, 1<=w<=104, b+w<=Q.
Errors may overwrite arbitrary adaptive subsets of A after any of the
rows T0,...,L=T0+D, where 0<=D<=103. There are no other errors.

Every overwrite retains the actual correct Age. All four flags and all
thirteen SF fields may be replaced arbitrarily. Set

    S=L+1, c0=min(0,b-5(D+1)), dmin=9-c0.

The Address offset g(x)=(Address(x)-x) modQ at an overwritten site may
be any member of {0} union [dmin,Q-1]. It need not be uniform in space or
time, or share any quorum. Zero offsets are allowed. The only restriction
on its nonzero values is this displayed palette restriction.

Define

    R=S+Q-2,
    N=16 ceil((Q-c0+3)/12),
    B=R+N+Q/2 = L+4095+N+2048.

**Every actual native field is canonical and quiet by row B.** Actual
Address and Flag2 are already correct everywhere by R+N. These equalities
persist through the current U boundary. The worst bounds in this class
are dmin=529, N=6160, B<=L+12303<=422008<T0+4Q<U-1.

SF remains the actual evolving SF, possibly damaged; it is not assigned
a future command or a quiet value. The theorem does not assert SF repair,
an E-to-E reset map, 2U repair, arbitrary Age faults, palettes containing
all offsets, surrounding E0 errors, or an induction on noisy levels.
The palette restriction is sufficient for this proof and is not claimed
necessary for the rule. Width/duration alone do not classify an error set.

## 2. Exact native reduction and the right boundary

GAWN25's projection theorem applies verbatim, with common correct Age and
the actual computed Workspace guard closed. All computed clocks from
T0 through B are between100Q+2 and422008, outside [96Q,98Q). Until the
current U boundary they remain outside that guard as well. Therefore
computed WF1=WF2=0 independently of SF. Raw overwritten Workspace may be
nonzero before S; at S both Workspace bits are globally0. All later
native offsets are chosen from the displayed palette. Native dependence
has radius5. Its finite causal cone gives GF=Flag2=0 at x<c0 at S.

All native fields at x>=Q are quiet throughout. Indeed their right
Address quorum is0. In their true-colony left mask every eligible site
is also x>=Q, so Address/clock mismatch and Workspace sources vanish.
Their right Flag1 count is0, hence computed Flag1=0. The masked Flag2
left count is0; the untruncated left clause is disabled by Flag1=0.
The quorum is present, so the periodic source is absent. Selected
Address/clock are canonical. This induction starts at the actual intact
row and is unaffected by errors strictly below Q.

## 3. Combined Address/Flag2 prefix lemma

Suppose at an old row that GF=Flag2=0 for x<c and WF2=0 everywhere.
Consider new targets x<=c. All five of their old left GF and Flag2
values are0. The left Address quorum is consequently0. If x<=c-4,
at least three right GF values are0, so the right quorum is also0.

It remains to consider c-3<=x<=c. Denote the right quorum by delta,
its existence by e and its apparent phase by r=(x+delta) modQ.

* If e=0, computed Flag1=1 and the selector chooses left GF0. New Flag2
  is0 except possibly for the periodic source when the **new** Age is0
  modulo16: its five old left bits are0 even if old self Flag2 was1.
* If e=1 and delta=0, either selector returns0. The periodic source is
  absent. Both the masked and untruncated left Flag2 counts are0, so h1
  erases any old self1 and cannot create a new1.
* If e=1, delta!=0 and r>=3, at least three eligible left GF0 values
  disagree with delta. Computed Flag1=1. The five left Flag2 zeros erase
  any old self1, yielding Flag2=0 and hence selected left GF0.
* The remaining case r<=2 is equally resolved if three quorum witnesses
  to the right have Flag1=1 and lie in the apparent colony: the masked
  right Flag1 source forces computed Flag1=1, then the same erase and
  selector argument applies.

Arbitrary old Flag1 and WF1 can only add Flag1 sources; they invalidate
none of these arguments. No old self Address or Flag2 restriction is
needed at x=c. Missing left quorums are absent here because its five left
GF values are0, not because the global offset palette has two elements.

Thus, whenever the last low-phase quorum case has been resolved,
the new combined zero prefix contains x<c+1 on a nonpulse update.
On an update with new Age0 mod16 it contains x<c-3: three right zeros
ensure a present zero quorum at all x<=c-4. A missing right quorum can
create Flag2 in the remaining three sites, so a pulse cannot be ignored.

## 4. A phase-dependent prefix while the tags form

For S<=t<=R set

    h(t)=c0-max(0,3-(Age(t) mod16)).

Then GF=Flag2=0 for x<h(t). The initial claim follows from h(S)<=c0.
At every critical target h(t)-3<=x<=h(t), one has c0-6<=x<=c0.
For every nonzero allowed delta,

    3 <= x+delta <= Q-1.

There is no wrap and the mismatch case in section3 applies without a
tag. A nonpulse update can advance the prefix by1, at least to h(t+1).
A pulse changes h from c0 to c0-3 and the weaker pulse bound suffices.
This is a joint GF/Flag2 invariant, including arbitrary missing quorums
and their source. It does not assume the prefix has advanced during this
waiting interval.

## 5. Offset-specific positive-colony tags

For each nonzero allowed delta define s_delta=Q-delta. A site is
delta-tagged when g(x)!=delta **or** old Flag1(x)=1. We need these tags
only in [s_delta,Q), the part below Q of the positive delta colony.

All sites at x>=Q are tagged because g=0. In one update the three sites
Q-3,Q-2,Q-1 are tagged: their right zero quorum is present. If computed
Flag1=0, selected GF is that quorum0; if Flag1=1 the tag is automatic.

Now take any x in [s_delta,Q) whose five right neighbors are tagged.
If the right quorum is delta, its three delta witnesses have Flag1=1.
No such witness is at or beyond Q, since g=0 there. The witnesses all
lie in [s_delta,Q), hence in the apparent delta colony. The masked right
Flag1 count is at least3, forcing a tag at the new x. If the quorum
is missing, computed Flag1=1 again gives a tag. If the quorum is some
other value and computed Flag1=0, the selector chooses that other value;
otherwise the tag is already supplied by Flag1=1. All cases are covered.

A tagged suffix consequently expands left by at least one site per
update after its first three sites. For n>=1 ordinary updates after S,
every x>=max(s_delta,Q-n-2), x<Q, is tagged. The entire interval is
tagged by max(1,delta-2) updates. The conservative common wait Q-2
therefore supplies every allowed delta tag at R. They persist. Tags do
not require different colors to share a flag pattern or a quorum.

## 6. Uncapped erosion after R

Start c(R)=h(R). Until the global zero row is reached, let

    c(t+1)=c(t)+1, if new Age mod16!=0;
    c(t+1)=c(t)-3, otherwise.

For every phase, the minimum of this sequence is at least c0-3.
This uses the phase-consistent starting value h(R): starting instead
from c0-3 at an arbitrary phase would permit an extra immediate retreat.
Each complete16-update block has one pulse and net increase12.

In a critical target c-3<=x<=c below Q one now has x>=c0-6. Every allowed
delta satisfies x+delta>=3. If r=(x+delta) modQ<=2, a wrap is necessary
and x=s_delta+k with k=0,1,2. Thus x is in the positive delta colony.
Three right delta quorum witnesses lie in [s_delta,Q), are tagged by
section5, and have Flag1=1. This supplies the last case of section3.
For r>=3 the left mismatch source suffices as before. At x>=Q the
right-boundary invariant already supplies the required zero fields.
The prefix induction therefore holds for all phases.

Since N is a multiple of16,

    c(R+N)=h(R)+12(N/16) >= c0-3+12 ceil((Q-c0+3)/12) >= Q.

Together with the right boundary this gives global GF=Flag2=0 at R+N.
Their zero values persist, since all GF quorums are now0, all left Flag2
counts are0, and neither Workspace nor missing-quorum source exists.
Only Flag1 remains. On canonical GF it is the right threshold3/self
threshold2 rule in each true colony. Its zero suffix grows by two sites
per update, starting at the last two sites. After Q/2 more updates all
Flag1 is0. Common Age and zero Workspace have already been proved.
This proves the theorem, including all later rows through U.

## 7. Receipts and limits

[check_gawn27_prefix_eroder.py](check_gawn27_prefix_eroder.py) checks the
integer inequalities, all16 starting phases for every possible c0,
selected full physical kernels with arbitrary SF, and selected causal
infinite-line native histories. [audit_gawn27.c](audit_gawn27.c) includes
the unchanged pinned GAWN25 scalar kernel and checks the combined-prefix,
tag-suffix, palette, right-boundary and deadline invariants on each
retained row. Whole SF and U/2U histories are not simulated.
Adaptive arbitrary forcing is covered by the written proof, not by
the finite selected profiles. The measurements supplement the proof;
they cannot discharge the premises missing from a noise theorem.

| Step | Status |
|---|---|
| Actual H2 late native initialization | GAWN4 argument applies |
| Common-clock/closed actual guard/native equations and palette closure | GAWN25 argument applies |
| Right boundary and initial finite causal prefix | proved |
| Missing-quorum-aware combined prefix and capped pre-tag invariant | proved |
| Simultaneous many-offset tagged suffixes | proved |
| Low-phase wrap resolution, 12-per16 erosion and native deadline | proved |
| Retained finite kernel/campaign checks | measured supplements |
| Full native eroder with every legal offset or changing Ages | unproved |
| SF repair/U encoding/2U correction for this class | unproved |
| Open Workspace/multiple supports/surrounding E0/higher induction/iid | unproved |
| Positive epsilon, faithful Gray/G17 refutation or minimal global fix | unproved |
| Rule/ROM/constants/CURRENT change or commit | none |
