GT0 implements raw gathering and record retention with explicit emitted
transitions. It is a new isolated transport/storage component consistent
with the corresponding Gray stage description. It is not a complete
Gray cellular automaton. Native computed controls, early flag results and
final interpreter writes are named integration ports; no self-programme
or late Workspace-flag rule has been supplied. This proof does not change
the scope of the accepted conditional I,N,S,G,R theorem.

Use Q=8192, U=128Q=1048576, the original lambda24/c104 error classes and
the five printed stages. GT0 deliberately retains this U. No GR1 source,
front, instruction ROM or gather-skew formula is used. The concrete
choice is to gather whole primary words at equal within-colony positions,
rather than rearranging data to interpreter-front coordinates. Gray
does not print this precise physical schedule; it is an explicit new
implementation of the raw-gather specification.

**Storage and emitted transitions.** The tracked logical data fields are
SimBit1, Mailbox.Right1, Mailbox.Left1, three History banks of11 bits,
Voted11 and NextBit1. Each has five physical holders, giving240 tracked
bits per site. The primary copy is first; the other four correspond to
logical offsets−2,−1,+1,+2, as in Gray's SimBit description. A preliminary
frame also includes Address13, Age20, two native Flags and two Workspace
flags, totaling277 bits. This is a frame count, not the final alphabet:
adding an interpreter, its service state or another programme representation
requires a new count, layout and self-programme proof.

gray_raw_gather.py gives the Boolean transitions. GT0_transitions.json
contains every live input, two-input gate and output node. The emitted
GT0_transitions.c has a Boolean byte interface in that exact input/output
order. Only data inputs at distances at most5 are read. Native Address13,
Age20, Flag1 and wipe are computed-control ports. The early Flag1/Flag2
results are two further ports used solely by the selected special-source
write at computed Age80Q−1. Five final write-enable/value pairs are used
only during the active fifth stage. These ports are not an upper-level
callback in a claimed completed CA: a full rule must compute them from
local state and its actual programme. They are unused during the early
prefix certified below.

All data sources are five-holder votes. Mailbox outputs are additionally
zero when computed Flag1=1; all tracked outputs are zero when native
wipe=1. The intended native wipe is computed Flag1=1 together with a
change of Address from its current value, matching Gray p33. Those
special masks are built into the component. The native equation itself
is an integration obligation; the printed-native certificate supplies
the healthy-control closure used here.

At each stage start, Mailbox, NextBit and Voted reset. History bank g
resets at starts of stages1,...,g and is retained at every later stage
start. Thus the three snapshots remain independent and old records are
not consulted as controls of later gathering. At computed Age112Q+1,
Voted takes the bitwise majority of the three History banks. During the
fifth active stage a final interpreter port can write NextBit. At Age0,
SimBit consumes old corrected NextBit before NextBit resets. These are
explicit component interface equations, not a proved own-programme
implementation or a period theorem.

At Age80Q−1, the logical primary at Address3 receives the early Flag2
result, and the primary at AddressQ−3 receives the early Flag1 result;
their backups receive the corresponding value. Choosing that exact tick
is an implementation decision within Gray's described end-of-third-active
interval. Availability and coherent delivery of the two results are
unproved ports here. The computed-SimBit Workspace equation on p41 has
not been replaced with current SimBit; it is not implemented at all by
this data component.

**Universal local route and rest proof.** A physical holder at x stores
copy s of a logical field bit at x+s. To compute a logical value at z,
the circuit votes the five holders z−s. A Mailbox source at x+s±1 reads
holders out to distance |s±1|+2<=5; every other data source has distance
at most4. Thus the emitted data radius is5. Substituting a radius-five
native computed control at the current site does not extend that radius.
No claim is made about the unimplemented programme result ports' radius.

For coherent data, all five inputs to each helper vote are the same
independent symbolic bit. The compiled helper reduces to that bit.
The checker partitions the complete20-bit computed-Age range by every
stage boundary, snapshot, capture, special flag delivery and vote event,
including each event's successor. Address classes include every solution
of Address+s=3 or Q−3 modQ. Within each product class all control
predicates are constant. On each class, every output is checked against
an independent scalar routing equation, with every logical data bit,
native Flag1/wipe, early flag result and final-write port left free.
This covers arbitrary older History data, including no dependence of
later gathering on it. It covers all clock words and Address phases,
not a sampled set of operational clocks.

During any rest interval, every scalar data route is its unchanged
current logical value. Final write ports and special-result ports are
clock-gated off. Therefore all coherent tracked fields stutter when
Flag1=wipe=0. In particular no programme port or old-bank content can
change the completed stage2 History records during [48Q,64Q). Damaged
incoherent copies can still vote to a repaired value; a claim of stuttering
on every arbitrary damaged raw state is not made. The full Workspace
flags and any future interpreter/service fields are outside this
tracked rest theorem.

The checker also evaluates all80 two-fault majority cofactors: each
holder pair, each correct Boolean value and each pair of arbitrary
replacement values. With unchanged controls and at most two damaged
holders, every helper vote reconstructs the correct logical input.
This is conditional copy transparency; it is not a noisy native or
complete E0 period theorem.

**Full raw gathering G: proved for this component under correct controls
and stable coherent SimBits.** Let S_g be0,32Q or64Q. Mailboxes reset
at S_g. At computed Age S_g+1, both Mailboxes snapshot the corrected
current logical primary word D. History g's offset0 lane snapshots D
at the same update. Each subsequent active tick moves Mailbox.Right
one cell right and Mailbox.Left one cell left, with five voted backups.
Thus at raw time S_g+1+d, the Mailbox values at x are respectively
D(x−d) and D(x+d). The output History capture at computed Age

    S_g+2+|off|Q, for off in {−5,...,−1,1,...,5},

reads those input Mailboxes after d=|off|Q shifts. Hence its value at
logical x is exactly D(x+off Q). There is no destination skew. The last
capture is S_g+5Q+2<S_g+16Q. Every one of the33 snapshot/offset coordinate
identities is retained in the certificate. Stage3's captures also finish
before the chosen flag-source write at80Q−1.

For any injective represented-state layout ell and any source bit b,
receiver i's record at logical primary x=iQ+ell(b), lane off, therefore
equals the raw bit of source cell i+off. Its storage and five backup
holders are inside the receiving colony for an interior ell. This is
an exact unfiltered copy of every raw represented bit, including private
Workspace bits; no simulated upper majority or omission of unused
transition inputs is performed. Since every raw state bit is copied,
the complete record is injective. Copying the whole primary word also
copies any unrepresented marker/auxiliary primaries, which does not
invalidate the raw-state record. This closes the raw/full/local-storage
parts of G for GT0. It does not establish that Gray's unspecified actual
programme implements this particular component.

**Record retention R: proved for this component under correct controls
and coherent records.** After capture, History g only votes its own
five-holder copies except at the stipulated earlier-stage resets. In
the stage2 rest interval all banks use their unchanged current values.
Flag1=wipe=0 makes those votes exact identities. Stage1 data can be
arbitrary and cannot influence History2's captures or retention. This
proves the precise G/R semantics on the earlier-error trajectory below,
not merely on the completely noiseless initial trajectory.

**Recursive data frame and one shared real1 history.** The emitted
preliminary layout places all277 bits at distinct primaries3958,...,4234.
It excludes0,3,Q−3 and lies well inside the colony. It is explicitly
preliminary: it will not automatically remain a compatible layout after
a complete interpreter is added. Define D on integers by the same
terminating recursion as the conditional stage proof: Address primaries
encode their parent's Address; each SimBit-slot primary refers to its
parent's logical offset; all other represented primaries are0. Unused
primaries are0 except auxiliary primary0, which encodes an arbitrary
correct programme beta(parent Address). The five represented SimBit
primaries are interior, so each recursive call strictly reduces |x|.
Every field case then gives an all-level H in E(H), with canonical
Address, Age/flags/private0 and five coherent Info copies. Correct
ProgramBits need not be zero. This is a combinatorial initialization
for the data frame, not a compiler proving beta exists for a completed
GT0 automaton at this Q. Finite large-coordinate checks corroborate
the universal terminating-recursion argument rather than replacing it.

Choose y=4010, the primary representing upper History1 raw bit0,
initially0. At physical time1 overwrite only the copies of logical
SimBit y at holders4009,4010,4011. Leave every native, Workspace,
Mailbox and other SimBit bit untouched. This complete three-point set
is one original lambda24/c104 real1, with E0 empty. No independent
upper fault or earlier physical error is supplied. At time2 the three
wrong copies vote to coherent1. With canonical native controls, no
wipe, no further errors and no age wrap, the wrong primary stays1
through T=56Q=458752. The final-write and early-flag integration ports
have no influence before T, so their missing implementations do not
enter this finite data-prefix coupling.

The first clean update is also checked against the complete emitted
netlist in30 local cofactors, with7200 output assertions. Every enumerated
logical data input, including unused emitted input slots, is within y±14,
where this recursive frame's
initial primaries are0. At time1 Mailbox and own-History snapshots
therefore also contain0; all other local private fields are still0.
Only the designated stored SimBit copies are changed. All future
programme ports are symbolic and unrestricted; their clock gates
remove them. Exactly the five copies of logical y become1 at time2,
while every other local data output remains its reference value0.

To supply these native controls, assume a completion uses the printed
native equations and the published Workspace pulse restriction. Before
96Q all Workspace flags are0, and the error never overwrites them.
The accepted all8192 literal native cofactors and common-clock induction
therefore supply the correct Address/Age and both native flags0. The
raw-GF simulation wipe is false. Neither the printed Flag2 typo nor
the later computed-SimBit equation changes this early prefix. This
native condition is still an explicit completion requirement: GT0's
data transducer does not manufacture those native/WF outputs itself.

Stage2 resets Mailbox, snapshots D' and gathers its raw bits. At T the
actual History2 primary at x=−4182, lane+1, is D'(4010)=1; the one at
x=12202, lane−1, is also1. Their noiseless values are0. Info4010 still
differs in colony0. These are simultaneous data-field differences in
colonies−1,0,1 from the all-level initialization and the sole shared
physical real1 history. The conclusion is a proved early-prefix coupling
of this concrete component under the supplied native condition, with
G/R implemented rather than assumed. Every whole-rule completion that
retains these early-prefix equations and that native condition inherits
the pointwise footprint. Existence of a faithful self-simulating Gray
completion with those interfaces remains unproved. No decoded boundary
or iid failure follows from this temporary footprint.

**Emission and validation scope.** The JSON netlist is the actual
compiled straight-line Boolean map. In the C source every node is assigned
once in topological order, each gate uses the same AND/OR/XOR opcode,
inputs are masked to one bit, and outputs use the same node indices.
This source-level mapping is structurally checked. GCC's compiled shared
library is compared with NumPy on every clock/address partition using
reproducible arbitrary raw data and ports; these backend comparisons are
measured evidence and their full inputs/outputs are retained in NPZ.
They are separate from the universal routing proof. No million-tick
trajectory or GPU experiment is used for the prefix theorem.

**Late interface conflict.** The separate GT0_RADIUS_INTEGRATION.md proof
evaluates this component's actual primary SimBit equation at computed
Age96Q+1 with all future ports symbolic. Combining it with the literal
native rule and the p41 computed-SimBit Workspace.Flag2 read requires
radius at least8 on raw states. Thus these particular component equations
cannot all survive a radius5 whole-rule integration unchanged. This does
not alter the early-prefix theorem, and it neither supplies an intact
error history for the radius witness nor excludes every Gray completion.

The remaining obligations are a complete native/SF transition function,
the literal computed-SimBit Workspace equation, an actual compact beta
programme and interpreter, a compatible final state/layout/hardwirer,
early flag production/delivery, last-stage runtime and a complete period
composition. Neither faster U, full Gray refinement, higher noise nor
an explicit iid noise threshold is established by this component.
