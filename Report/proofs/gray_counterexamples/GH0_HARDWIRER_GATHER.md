# GH0/GH1: an interior hardwirer before a raw first snapshot

This is a concrete **component** completion at Q=8192,
U=128Q=1048576, lambda=24 and c=104. It closes the hardwire/read/snapshot
dependency for an explicit physical transport and preliminary layout.
It does not supply a complete Gray automaton, an own programme of at most
Q bits, or a reliability theorem. The accepted GT0, GMW0–3 and conditional
I,N,S,G,R results retain their separate scopes and immutable sources.

Sources: [hardwirer](gray_layout_hardwirer.py),
[delayed gathering](gray_hardwired_gather.py),
[checker](check_gray_layout_hardwirer.py),
[certificate](../../../figs/gray_counterexamples/GH0_hardwirer_gather_certificate.json),
[GH0 emitted graph](../../../figs/gray_counterexamples/GH0_transitions.json),
[GH0 C equations](../../../figs/gray_counterexamples/GH0_transitions.c),
[GH1 emitted graph](../../../figs/gray_counterexamples/GH1_transitions.json)
and [GH1 C equations](../../../figs/gray_counterexamples/GH1_transitions.c).

## Specification and premises

Gray pp31–32 gives an illustrative three-step hardwirer: read the
simulated Address, read the ProgrammeBit at that Address, then overwrite
the simulated ProgrammeBit. The first bit and Address positions there
are illustrative. His pp33–35 later require an interior represented strip
and reserve primaries3 and Q−3 for flag delivery. GH0 explicitly relocates
the thirteen simulated Address inputs to the existing GT0 interior strip.
No claim is made that these particular coordinates or courier microcode
are printed by Gray. The component realizes the stated hardwire operation
under the premises below.

Fix an arbitrary beta of at most Q bits, extended by zero to Q. Beta is
correct for a hypothetical completed rule **as a premise**. No beta for
GH0/GH1, let alone that completed rule, has been compiled. The random beta
in the receipts is reproducible test data, not a certified own programme.
There is no64K instruction ROM and no host/whole-rule transition call.

The projected ProgrammeBit at physical holder j, copy offset t, is the
finite local function

    PB_t(j) = beta[(rawGF(j)+t) mod Q].

These are ghost input values in the emitted interface, not mutable fields
of the projected alphabet. Their values use the **actual raw holder** GF,
including when that holder is corrupted. A programme fetch at logical y
votes the five values PB_t(y−t). A repaired head-centre Address is not
substituted into those five reads. Projecting this redundant version is
an explicit extension of Gray's p32 projection argument: the ghost values
are each a function of that physical cell's Address, so eliminating them
does not enlarge the neighbourhood. A mutable-ProgrammeBit extension may
instead pass arbitrary five physical inputs, but integrity of such inputs
must then be proved separately.

Native computed Address, Age and wipe are explicit ports. GH1 also has
computed Flag1, two early flag-result ports and five final-write pairs.
For the operational theorems require canonical Address x modQ, a common
clock increasing from0 without wrap, computed Flag1=wipe=0, and stable
coherent simulated Address bits during the early hardwire. Before96Q,
the native/pulse composition that supplies these controls is a stated
completion requirement. The printed native rule gives them on the
sole SimBit-error trajectory below, where no native flag is corrupted.
For arbitrary native E0 replacements, h1 Flag2 erasure is an **explicit
correction**, with a separate quiet-control proof below. No late computed
SimBit/Workspace rule is silently replaced with a current-value rule.

## Finite alphabet, total equations and locality — proved for component

Append five copies of an18-bit logical courier to GT0's240 data bits.
The courier has present1, mode3, accumulated Address13 and value1.
Native Address13, Age20 and four one-bit flags add37, so the preliminary
projected frame has367 bits. Its injective layout retains every GT0
primary3958..4234 and appends ninety courier-bit primaries4235..4324.
Simulated Address stays at3958..3970; the chosen History1-bit primary y
stays4010. The simulated SimBit primaries remain3995..3999. Primary0 is
the unrepresented simulated ProgrammeBit;3 and Q−3 are unused here.

The six defined modes are COLLECT, HOME, SCAN, BACK, DONE and ERROR;
in active transport the two remaining three-bit modes become ERROR.
Missing active-transport candidates become zero. Rest votes and retains
the complete word, even a raw word with present0 and nonzero metadata.
Candidate precedence is stationary self, incoming from left, then
incoming from right. Multiple incoming packets produce a stationary
ERROR packet retaining the first candidate's Address/value and perform
no write. Thus collisions and all invalid raw-state words have defined
outputs; head uniqueness is a reachable-state theorem, not a raw-state
precondition for evaluating the map.

Every source packet/SimBit/programme word is a bitwise3-of5 vote. At a
receiving holder x and copy s, the controller's service Address is
(computedGF(x)+s) modQ. Reusing the receiving holder's native computed
word is an explicit raw-state control convention. It does not read the
source cell's computed native word. The controller is reset at each stage
start. At computed Age2 it births a COLLECT packet only at logical
Address3958 and captures Address bit0. During2<Age<16Q it transports and
updates incoming packets one site per tick. Outside that interval it
votes and retains its current packet. A one-time transition to DONE at
Address0 writes the returned bit to SimBit0. DONE does not keep writing.
Native wipe zeros all courier/SimBit outputs. GH1's data map computes its
ordinary SimBit first, then GH0 overrides it only on that one-time write.

In COLLECT, at logical Address3958+b for0<=b<13, replace accumulated
bit b by the voted SimBit; after b12 switch to HOME. A COLLECT packet
outside that strip becomes ERROR. HOME moves left to0; when its Address
is zero, either fetch ProgrammeBit0 and finish if accumulated A=0, or
switch to SCAN. SCAN moves right until logical Address=A, fetches its
ProgrammeBit there, then switches to BACK. Overshooting becomes ERROR.
BACK moves left to0 and writes the fetched bit. DONE/ERROR are stationary.
These case equations coincide with the emitted Boolean mode comparisons,
selection, less-than comparison, bit replacements and write predicate.
Their disjoint cases give universal scalar/netlist equivalence; the
finite random backend comparisons are separate measured evidence.

For logical y=x+s an incoming packet at y+d, |d|<=1, reads holders
y+d−t, |t|<=2. Hence |s+d−t|<=5. SimBit and ProgrammeBit votes use
|s−t|<=4. All native controls at x have radius5. The projected ghost
ProgrammeBits introduce no additional read. Therefore the component is
radius5 on **every raw state**, with its native/future ports counted as
locality obligations. This is not a radius theorem for an unspecified
whole-rule completion: the accepted GT0/p41 final-computed-SimBit radius
obstruction and order audit still apply to their stated interfaces.

## Quiet execution and source identity — proved conditionally

Let a colony's thirteen stable represented Address bits be a word A.
After birth at Age2 and Address3958, twelve right-moving ticks collect
the other bits. At Age14 the head is at3970, HOME and contains exactly A.
After3970 left-moving ticks it reaches0 at Age3984. If A=0 it fetches
and writes there. Otherwise it moves A ticks right, fetches at A, then
A ticks left and writes at0. In every case

    completion_age(A)=3984+2A <=20366 <16Q.

For a coherent packet at p, every output holder of the next logical
position p+d sees that packet in its correct directional candidate and
sees zero in the other candidates. The five packet votes equal the
same packet. At a canonical raw holder y−t,

    (rawGF(y−t)+t) modQ = y modQ.

Consequently all five actual ProgrammeBit inputs agree with beta[y modQ],
including when y=0 and the backup holders straddle a colony boundary.
The collected Address inputs likewise vote to their stable represented
bits. Induction over the mode phases proves exactly one packet per colony,
all five stored copies agree, no packet crosses a colony boundary, and
the eventual SimBit0 write equals beta[A]. Initially incorrect SimBit0
does not affect collection or the controller. Rest makes the coherent
DONE packet and all coherent data stutter.

The receipt checks the bound for all8192 A. It additionally retains every
actual five-holder update for A0 and8191 in
[physical traces](../../../figs/gray_counterexamples/GH0_physical_courier_traces.npz).
Those121730 scalar physical checks corroborate the universal induction;
they do not replace its arbitrary-beta/source-reference proof.

## Whole-cell E0 and raw-holder programme access — conditional local proof

At most two arbitrarily replaced physical holders in a logical five-holder
vote leave three copies equal to the correct finite word. This holds
bitwise for every packet bit, GF-derived ProgrammeBit, SimBit and data
word; the checker exhausts all102 Boolean support/payload cases. An E0
row in a diameter-ten source cone cannot contain three distinct points:
distinct printed local groups are separated by24 in space or time, while
each same-tick group is a singleton or adjacent pair. Thus every helper
vote reconstructs its logical input. One-site motion restores all five
copies on the next clean transition; it has the full-vote margin absent
from the rejected unpaused three-site transport.

Under canonical native geometry/common clock and at most two complete-cell
replacements in the radius-five input, right adjusted-GF and Age word
votes still have three correct values. Left inconsistencies number at
most two. The Flag1 and Workspace source thresholds cannot be met; a
corrupted current Flag1 has at most one other corrupted neighbour and
erases. Under h1, a corrupted current Flag2 similarly has at most one
other left Flag2, so its <=1 erasure predicate holds. An uncorrupted
Flag2 has no four-bit creation source. Therefore computed GF/Age are
correct and computed flags/wipe are0, even if replacement words have
arbitrary legal20-bit Ages, both Workspace bits and raw GF. This quiet
one-step native argument is specific to the explicit h1 correction.
The literal printed Flag2 predicate has the separately certified flaw.

Combining that native fact with voted source transparency gives exact
GH0/GH1 local output agreement whenever the reference SF copies are
coherent and the native/pulse interface remains quiet. Continuing pure
E0 yields the same early-prefix induction if the completion supplies
the stated quiet Workspace outputs. No damaged-native, real1-controller,
later-pulse, or whole-period E0 theorem is claimed here. The10050 finite
whole-cell replacement checks, with arbitrary packet/SimBit contents
and raw-native replacements, are measured corroboration of this universal
local argument, not an exhaustive test of the finite alphabet.

The retained [raw-holder lookup witness](../../../figs/gray_counterexamples/GH0_raw_holder_programme_witness.json)
and its [exact beta](../../../figs/gray_counterexamples/GH0_raw_holder_witness_beta.bin)
make this source distinction explicit. A prepared HOME packet at1 with
A0 completes at3984. A single physical E0 overwrite at(0,3983) changes
raw GF0 to1. Choose beta0=1,beta1=0. In S order(0,−2,−1,1,2) the five
actual ProgrammeBit reads are(0,1,1,1,1), so all five auxiliary outputs
are1. A head-centre-only lookup would incorrectly return0. This is a
positive repair certificate for a prepared component frame, not a
counterexample to Gray, an intact hierarchy or memory retention.

## Delayed first snapshot, full gathering and retention — proved conditionally

GT0's original first snapshot at Age1 precedes GH0's worst completion;
it cannot be justified as a fresh hardwired-programme snapshot for a
general initial auxiliary bit. GH1 is a **named schedule change**:
snapshot stage1 at20367, one tick after every GH0 write. Stage1 remote
capture is20368+|off|Q. Stages2/3 still snapshot32Q+1 and64Q+1 and use
the original captures. U, all five stage endpoints, active/rest halves,
flag-source delivery and update windows are unchanged. No shorter U
is inferred.

Mailboxes reset at the stage start and remain zero until the delayed
snapshot. At load L, both snapshot the old coherent primary D, and the
own lane snapshots D. At time L+d the logical Mailbox.Right/Left values
are D(x−d)/D(x+d). Capturing the input mailbox at update
L+1+|off|Q therefore stores exactly D(x+off Q), at the same within-colony
coordinate, for all eleven raw-neighbour lanes. The furthest first
capture is20368+5Q=61328<16Q; stage3's last capture565250 is before
the special flag-source write80Q−1=655359. All33 actual coordinates
are certified. Thus the concrete hardwired ProgrammeBit is already
available for every stage1 raw record, not only for its offset0 lane.

The universal GH1 data-routing checker uses the complete20-bit computed
Age partition (including every changed load/capture and successor),
all special-source Address classes, and independent symbolic logical
data/native masks/future ports. It verifies every emitted data route.
During rest, the routes are unchanged current votes. After capture,
History g votes itself and only resets at starts of stages1..g. Therefore
stage2 records survive all of[48Q,64Q), independent of older banks.
These G/R facts close the physical component obligations; they do not
prove that Gray's missing own programme or late interfaces realize GH1.

## Intact preliminary hierarchy and one shared real1 footprint

Let ell be the367-bit preliminary layout and S=(0,−2,−1,1,2). Define the
primary Info D on integers by Euclidean x=iQ+a,0<=a<Q:

    D(iQ)=beta[i modQ];
    D(iQ+ell(Address,b))=bit_b(i modQ);
    D(iQ+ell(SimBit,q))=D(i+S[q]);
    every other represented or unused primary is0.

The five SimBit primaries are3995..3999, so each recursive dependency
strictly reduces |x| (the possible |i+S[q]|<=|i|+2 is smaller than
|iQ+a| at those interior a). It terminates for positive and negative x.
Define H(x) to have GF=x modQ, native Age/flags0, five SimBit copies
D(x+S[q]), and all other physical fields0. Substitution in each ell
field case proves H in E(H), at every level. Auxiliary primary0 equals
beta of the represented cell's Address; special/unused primaries take0.
The courier field's represented primaries are0 and its raw initial
banks are0. This is an intact **preliminary** all-level encoding with
correct ProgrammeBits conditional on the existence of the own beta.
Adding future private-zero fields may preserve the strip3958..8053 for
K<=4096, but actual final K, beta and full-rule encoding remain unproved.

As in GT0 choose y4010, initially0. All initial Info primaries in
y±14 are0 irrespective of beta. At time1 overwrite only the stored
copies of logical SimBit y at physical holders4009,4010,4011. This
single shared physical history is original real1 (extent3 by1), with
E0 empty; no upper error or nearby earlier lower history is supplied.
The full emitted GH1 map at the first clean update Age2 is certified in
thirty cofactors/9900 output assertions, leaving actual ProgrammeBit
inputs and all future ports free. Exactly the five copies of y become1.
The delayed mailbox/history snapshots have not occurred; the local
head banks stay0 because birth at3958 is outside this cone.

The courier reads SimBits only during COLLECT at3958..3970. It may pass
4010 during SCAN/BACK, but those modes do not consume SimBit there.
Hence the error never changes any packet, accumulated A, fetch address,
programme vote or auxiliary write. Native fields are untouched and,
with the published pre96Q Workspace pulse restriction, stay canonical
and quiet by the accepted common-clock native closure. The printed
Flag2 defect/h1 alteration do not matter on this trajectory: Flag2 is
always0. Before56Q all flag-result/final-write ports are gated off.
Hardwiring in intact H writes the already correct beta[i modQ], so it
causes no reference SimBit change.

Consequently stage1 and stage2 both snapshot D' differing only at y,
and the new head service never acts as a control for gathering. At
T56Q=458752, stage2 History at−4182/lane+1 and12202/lane−1 equals1
instead of0, while SimBit4010 remains1. Captures270338<48Q precede T,
and History2 retention extends to64Q. These simultaneous actual-field
disagreements are in colonies−1,0,1. No single printed two-colony box
[jQ,(j+2)Q) contains them. Thus every whole-rule completion that retains
these exact early GH1 equations and the stated native/pulse contract
inherits the temporary-field footprint.

This is a conditional early-prefix compatibility obstruction for the
**explicit GH1 implementation**. It does not close the final programme,
layout, full GF/Workspace/SimBit-order refinement, or all-raw interface
requirements that would attribute it to Gray's actual Proposition4.
It is neither a decoded-boundary failure nor an iid memory counterexample.

## Validation status and remaining construction work

The JSON graphs emit every gate/input/output. C assignments preserve the
same topological nodes/opcodes and binder indices; programme binders
explicitly use gf[actual_holder]+copy_slot. This correspondence is proved
structurally. The192 arbitrary raw/component-port frames for each map,
compared with independent scalar equations and GCC output, are **measured
only**; full inputs and outputs are retained as
[GH0](../../../figs/gray_counterexamples/GH0_backend_inputs.npz) and
[GH1](../../../figs/gray_counterexamples/GH1_backend_inputs.npz).

| Obligation | Status |
|---|---|
| Total GH0 controller, actual raw-holder programme source, radius5 | proved for component |
| Arbitrary-A completion before delayed snapshot, five-copy source identity | proved under quiet native/stable Address premises |
| Arbitrary whole-cell E0 local transparency with h1 controls | proved conditionally; finite checks measured separately |
| GH1 exact full-raw gathering/local records/rest retention | proved under coherent data/correct controls |
| Preliminary H in E(H), all levels, arbitrary correct beta | proved conditionally |
| Sole real1 first56Q temporary three-colony footprint | proved for component under native/pulse contract |
| Actual correct self-programme beta<=Q, evaluator runtime and final K | unproved |
| Complete radius5 final-computed-SimBit/native/wipe/order integration | unproved; existing specified-interface obstructions remain |
| Faithful whole-Gray simulation or Proposition4 counterexample | unproved |
| Boundary-decoded recovery or iid reliability/failure | unproved |

Reproduce with python3
`Report/proofs/gray_counterexamples/check_gray_layout_hardwirer.py`.
No active rule/compiler is modified and no GPU experiment is needed.
