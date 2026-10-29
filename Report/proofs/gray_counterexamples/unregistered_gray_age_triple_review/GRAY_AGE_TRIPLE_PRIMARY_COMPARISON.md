# Primary Gray comparison: three Ages across a colony boundary

The three-site fault does not reveal a missing printed Age-consistency
clause. Gray explicitly includes that clause, and it corrects the clocks
in the first update. The retained Flag1 packet refutes a stronger
one-update complete-native contraction shortcut; it does not contradict
Gray's Proposition 2. This note changes no rule or programme.

## Printed equations and scope

The primary source is Gray's [paper](../../../../papers/A%20Reader's%20Guide%20to%20Gacs's%20%60%60Positive%20Rates''%20Paper.pdf),
printed pp.20–22 and 26; the exact local copy is pinned in the receipt.
The [text](../../../../papers_txt/gray_readers_guide.txt) contains the
definitions at lines877–899, Flag1 at lines919–927, the clock selector at
lines982–986, and Proposition2 at lines1174–1181.

At p.20, inconsistency condition(iii) is failure of a right-five Age
quorum. Condition(iv) is a right-five Age quorum a together with at least
three left neighbors inside the apparent colony whose Ages differ from
a. It is not an Address-only test. Flag1 is set on this inconsistency
before choosing the Address/Age majority. At p.22, an existing apparent
colony and computed Flag1=0 or Flag2=1 select the right majority; otherwise
the left majority is used. Age is then incremented modulo U.

For the trajectory considered here, all Address fields are canonical,
all old Flag2 values are zero, and Workspace is zero. The printed and
corrected h1 Flag2 equations agree throughout: no source can create a
Flag2 one, so the disputed old-one erasure predicate is never evaluated
on an old-one state. That agreement is specific to this trajectory, not
a full-rule refinement assertion.

## Exact first update — proved

Let Q=8192 and U=128Q. At a common clock theta=1, keep canonical Address
and zero flags/Workspace everywhere. Change only the Ages at {-1,0,1}
from1 to2. Other SF may be the actual prior SF; no SF value is required
by this native calculation except the stated Workspace premise.

The right-five Age quorum is2 precisely at x=-4,-3,-2. Each of their five
left neighbors lies in the true preceding colony [-Q,0), has Age1, and
disagrees with that quorum. Printed inconsistency(iv) therefore sets
computed Flag1=1 at those three targets, selecting the left Age1 majority.
At every other target the right quorum is1 and no three in-colony left
neighbors disagree with it. The boundary excludes site-1 from the left
neighbors belonging to colony0; hence no spurious right-side source is
created. Consequently the next row has canonical Address and common
correct Age2 everywhere, Flag1 exactly at {-4,-3,-2}, Flag2=0.

The numerical supplement compares the actual maintenance scalar at
Q8192 and Q4096, retaining all34 target neighborhoods and output words.
It is a finite transcription check, not a full physical hierarchy replay.
The native argument itself follows directly from the printed equations.

## Subsequent native packet — proved with zero Workspace premise

As long as Workspace remains zero, both clock voters are now the common
correct clock. Flags cannot disturb Address or Age on canonical/common
geometry. Flag2 remains zero. With no remaining inconsistencies, Flag1
obeys its printed right-neighbor growth/retention rule.

At elapsed k>=1 from the overwrite, its exact support is the integer
interval

    [max(-Q,-1-3k), -2k],

interpreted as empty once the left endpoint exceeds the right endpoint.
The left front advances three sites per update until it reaches the
preceding colony boundary; the right edge erases two sites per update.
The last one is at -Q at k=Q/2, and all native fields are quiet at
k=Q/2+1=4097. The corresponding Q4096 time is2049.

In an actual completion with the printed 96Q<=computedAge<98Q Workspace
gate, starting at theta1, that gate is closed through these times. This
supplies the zero Workspace premise for the native prefix independently
of SF. It does not by itself specify Gray's own programme, full layout,
or a complete simulation-structure repair theorem.

## Error hypotheses and Proposition 2

A single shared same-tick location set E={(-1,t),(0,t),(1,t)} is an
original lambda24/c104 real1. No singleton or adjacent pair is isolated
from the remaining location, so E0 is empty. The set fits a Q-by-U box,
contains disjoint linked candidate0 subsets, cannot contain two
104-separated nonempty subsets, and has no external error locations.
This class statement is about that one physical history; it does not
assert that a chosen bad upper triple is realizable by some previously
restricted lower burst.

Proposition2 at printed p.26 permits a two-colony box of duration U/32
for Address/Age and duration U for Flags. Computed Address/Age in this
example are already correct at the first update. The Flag1 packet stays
inside the preceding colony and dies by4097, well before either allowance.
Thus no printed Proposition2 hypothesis excludes the small native fault;
instead its actual behavior is compatible with the proposition.

The arbitrary upper-triple one-update **complete** correction identity
fails because of the Flag1 bits. Gray does not state that shortcut here.
Native finite recovery also does not settle the packet's SF effects or
their eventual decoded recovery.

## Status

| Step | Status |
|---|---|
| Printed Age clause and computed-Flag1 selector order | Gray's argument applies; exact primary statement verified |
| First-update clock repair/three Flag1 outputs | proved |
| Conditional native Flag1 packet and finite quiet time | proved under zero Workspace, supplied by the early guard if implemented |
| Original-c104 real1 classification | proved |
| Proposition2 contradiction or missing printed Age clause | disproved for this proposed attack |
| Actual lower-burst realization of arbitrary upper triples | unproved |
| Full faithful Gray programme/layout/SF repair | unproved |
| Gray/Gacs/G17 or iid unreliability | unproved; no such claim |

The parent's initially proposed travelling-clock induction omitted
inconsistency(iv). Its rejected artifacts are preserved by the parent;
this comparison does not reuse that induction or mutate its history.
