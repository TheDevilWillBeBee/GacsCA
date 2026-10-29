This follow-up resolves the locality choices for the p33/p41 interface
in the isolated GT0 component. Q=8192, U=128Q, lambda24 and c104 remain
the baseline. The accepted GT0 sources, proofs and receipts are retained
unchanged. This is not a full faithful Gray compilation or an iid theorem.

**What the primary specification fixes.** Gray defines a deterministic
cellular automaton by a single state replacement Tr(S^N) (p2, extracted
lines95-105), and chooses N=[-5,5] (p14, lines612-617). On pp21-22 he
explicitly defines each computed native value as the value produced by
its stated transition rules (lines938-940,953 and987-988). On p33,
lines1480-1483, the special native-dependent wipe demands that every
simulation-structure bit at a site become0 when its computed Flag1 is1
and its computed Address differs from its current Address. SimBit is a
simulation-structure field, so its final state bit is included. The same
page specifies replacement of each five-copy SimBit group by its majority
at each tick (lines1488-1494). The p41 Workspace equations read a
computed primary SimBit at a nearby site (lines1852-1859,1874-1881).

The paper does not separately define a pre-wipe SimBit variable, nor print
the complete SimBit transition table on every damaged raw state. It says
that most simulation transitions are implicit (p32, lines1459-1465).
Thus “computed” naturally denotes the final replacement value, consistent
with the explicit native definitions. This is an inference from those
definitions, not a separately printed SimBit evaluation-order definition.
Reading it instead as a distinct
intermediate is an interpretation change that must be stated. The source
text does not prove that this interpretation is impossible, or uniquely
determine every fallback transition on arbitrary damaged raw states.
It would be too strong to promote GT0's component obstruction to
nonexistence of every Gray completion.

There is also a priority issue at the reader itself. The p33 mandatory
wipe includes Workspace.Flag1, so it must override an ordinary WF1 birth
when both apply. WF2's p41 birth requires computed Flag1=0, so its reader
wipe cannot apply simultaneously. The local obstructions below use WF2
with reader Flag1=0 and therefore do not depend on choosing that WF1
priority. The changed component explicitly gives p33 the priority.

**Final computed source: lower radius bound8 for GT0.** The accepted
GT0_RADIUS_INTEGRATION.md witness is unchanged. Two raw states differ
only in Address8. Reader0 has computed Address0, Age96Q+1 and Flag1=0
in both. At source3 the native wipe is false versus true, giving GT0
computed SimBit3=1 versus0 independently of every future programme port.
The literal WF2 outputs at0 differ. A radius7 neighbourhood at0 is
identical in the two states, proving the necessary radius lower bound8
for this component set. No intact-context reachability is claimed.

**Removing only the wipe is insufficient.** A new witness keeps every
raw Address canonical. Ages at sites[-5,5] are96Q, while Ages6 and7
areU-1. Age8 is96Q in A andU-1 in B. Raw Flag2 is1 at sites[-2,2]
and0 elsewhere; all Flag1 and Workspace flags are0. All current SimBit
copies are1; all NextBit copies are0. Every other raw field is identical
in A and B. Exact literal native evaluation gives computed
Address0=0, Age0=96Q+1, Flag1(0)=0 and Flag2(0)=0 in both.
At site3, A has computed Address3, Age96Q+1 and Flag1=Flag2=0;
B has computed Address3, Age0 and Flag1=Flag2=1. The Age vote uses
the right majority in B because its computed Flag2=1. Address3 remains
the raw Address3, so there is no mandatory wipe in either state.

GT0's actual scheduled source equation at3 therefore returns the current
majority1 in A and commits old NextBit0 in B. It still does so if its
wipe input is forcibly0 and all future ports are symbolic. The literal
reader0 WF2 output changes1 to0 even though only Age8 differs. This is
a second exact radius>=8 obstruction, now for the scheduled pre-wipe
intermediate. Merely renaming final SimBit “pre-wipe computed SimBit”
does not give a radius5 local implementation on all raw states. Both the
printed Flag2 predicate and the h1 correction give the same relevant
native outputs here; the obstruction is independent of that correction.

**Current primary is local but does not correct source-copy errors.** If
the p41 source is replaced by raw current primary SimBit, its displacement
is only[-2,2] for WF1 and[-1,3] for WF2. Together with the reader's
radius5 native controls this is a radius5 interface. However, take a
canonical native state at Age96Q, all flags0 and a zero five-copy
logical SimBit3. Overwrite only its primary copy at holder3 to1 at that
raw state. This singleton is E0 under the original classifier. At the
next tick the SimBit vote reconstructs0, while current-primary reading
would nevertheless output WF2=1 at readers0,...,4. Those later outputs
are outside the singleton E0. This proves a local E0 copy-transparency
failure of that changed interface. Reaching the whole pre-pulse snapshot
from the actual compact self-programme remains a separate obligation;
the local result alone is not an intact-hierarchy or iid counterexample.

**GV0: voted CURRENT source, an explicit component change.**
gray_workspace_voted_current.py replaces each p41 source with the majority
of the five current copies of that logical SimBit. It excludes every
source-site transition, including age-wrap commits and the source wipe.
It retains the reader's computed Address/Age/Flag1, and the mandatory
reader wipe for WF1. This changes the rule; it is not a compiler ordering
trick or a proof that Gray's printed final-value read was secretly local.

The source displacements are[-2,2] for WF1 and[-1,3] for WF2. The five
holders add[-2,2], so the current source data are in[-4,4] and[-3,5],
respectively. The native computed controls and reader wipe use[-5,5].
Hence the emitted per-cell interface has radius at most5 on every raw
state, including arbitrary legal Age words and native flags. On a
coherent source group the vote equals its primary value. With at most
two incorrect source holders it still equals the correct value; the
checker covers every holder subset of size0,1,2 and every replacement
pattern. This is local copy transparency under unchanged reader controls,
not a whole-rule E0 theorem. Sixty-six symbolic routing identities cover
the complete computed-clock/address predicate partition, with every raw
copy and reader Flag1/wipe left free. The source and intermediate comparisons in
both radius witnesses differ from literal final/scheduled reads, while
GV0 gives the same output in the two states. On the singleton current-
primary example, GV0 outputs0 at every reader.

This is the smallest stated interface edit we have proved sufficient
for radius5: replace the source expression with a voted current value.
“Smallest” refers to one source-expression change, preserving the native
rule, data transition and schedule. It is not a proof of minimal alphabet,
gate count, edit distance or global repair. Delaying a final computed
SimBit by one tick or caching it is another rule/state change; its
arbitrary-state locality, initialization and timing require their own
proofs. None is supplied here.

**Enlarging the radius: dependency upper bound and lost refinements.** If
the final source SimBit transition is genuinely radius5, a literal
Workspace read can be emitted by evaluating that transition at each
eligible target and using the reader's radius5 computed controls.
The WF1 targets shift[-2,2], so their source dependencies lie[-7,7].
The WF2 targets shift[-1,3], so their dependencies lie[-6,8]. The union
is[-7,8], contained in radius8. Thus radius8 is both necessary and
sufficient for this specified source/reader composition, assuming a
radius5 complete source transition, including every programme port.
It is not a completed radius8 automaton: GT0's programme ports still
have no actual transition or self-programme fit certificate. An
asymmetric neighbourhood[-7,8] also suffices for this composition; the
same radius lower bound follows from the site8 witness.

An enlarged range changes the number of upper neighbours needed for
self-simulation. A symmetric radius8 rule has17 source cells rather
than11; the asymmetric choice[-7,8] has16. GT0's11-lane gather cannot
simulate either without changing its record fields and interpreter.
For17 lanes, gathering offsets[-8,8] takes8Q+2 ticks, which still fits
inside16Q. Three History banks and the voted bank gain24 logical bits,
or120 five-holder physical bits per site: the preliminary frame grows
277 to397 bits, before any interpreter. This arithmetic establishes a
transport window and frame count only; actual beta length, last-stage
runtime, hardwirer/layout and period composition need new certificates.
Gray's unpublished constants in the last-stage bound cannot be borrowed
unchanged for the enlarged input neighbourhood.

The lambda24/c104 definitions and probabilistic location-set geometry
on pp16-19 do not mention the CA radius. Their classification and
purely geometric steps remain unchanged, subject to their existing
proof obligations. A one-tick radius8 cone has spatial diameter16<24;
the union for five output holders has diameter20<24. Each can meet at
most one same-time E0 group, hence at most two sites. Nevertheless a
two-tick radius8 cone has diameter32 and may meet two different E0
groups, whereas the single-output two-tick radius5 cone has diameter20.
The retained finite example demonstrates this difference. It does not
prove that actual error influence survives the first correcting tick.

Five-holder voting itself remains correct against two overwritten
holders; it does not automatically prove the larger full transition's
control/wipe/flag E0 induction. Nor do radius-independent classification
facts justify borrowing deterministic confinement, Mailbox obstruction,
wave transient estimates, trickle-down direction reversal, or a
multi-level decoded noise map unchanged. The native equations still
have radius5 and their autonomous algebra is unchanged, but the
Workspace forcing and full self-simulation interface must be audited
again. This receipt proves no higher-noise, decoded-memory or iid claim.

The emitted GV0 component retains the printed native predicate, including
its independently certified Flag2 issue. Changing it to h1 would be an
additional explicit rule correction. Neither this source-expression edit
nor an enlarged radius establishes that correction's global sufficiency.
