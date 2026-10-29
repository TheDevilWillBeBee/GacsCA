# GE1 native writeback and the next actual gather bank

GE1 is an **explicitly changed native-only fifth-store component** over
the frozen GE0/GT0 prefix. It keeps Q=8192, U=128Q=1048576, lambda=24,
c=104, the 2462-bit frame, all five stage endpoints, the early native
programme and its couriers. It does not supply the full fifth own
programme, an own beta<=Q, an unconditional intact encoding, or an
all-raw implementation of Gray's final-computed-SimBit Workspace order.
The result below retains these completion premises where required.

Sources: [GE1 local equations](gray_native_writeback_ge1.py),
[checker](check_gray_native_writeback_ge1.py),
[read-only validator](validate_gray_native_writeback_ge1.py),
[receipt](../../../figs/gray_counterexamples/GE1_native_writeback_second_bank_certificate.json),
[frozen GE0 early native programme](GE0_EARLY_NATIVE_FLAGS.md),
[actual all-receiver first bank](GE0_GLOBAL_FIRST_FLAGS.md), and
[actual first Workspace/native prefix](GE0_FIRST_WORKSPACE_NATIVE.md).
Gray's relevant source locations are pp31–36 and41. GE1 implements a
specified store interface; no literal Gray fifth evaluator is inferred.

## Claim and one physical history

Retain GE0's conditional intact initialization and native-prefix/GT0
layout premises. Use the same physical row0 error: replace only Age by1
on [0,17Q), leaving every other field unchanged, with no later errors.
Its original lambda24/c104 real2 classification is reused from the
accepted first-bank certificate; no independent upper error or preloaded
bank is introduced. The completion implements Gray p41's late Workspace
equations with final computed SimBit, as explicitly assumed in the
accepted first-Workspace certificate. GE1 replaces only final-store
ports at the 37 native primaries by the equations below. All other
final-store ports remain arbitrary finite ports.

Write D={−3,−2,−1,13,14,15,16,17,18,19}. Let

    Z1(g) = (GF=g modQ, Age=1, Flag1=1[g in D],
             Flag2=Workspace1=Workspace2=0).

Then every one of the 37 normal native SimBit primaries in lower colony
g, with all five holders, commits Z1(g) at physical row U−e20(g), where
e20(g)=1[0<=g<20]. All have committed by row U. The native fields remain
the quiet canonical-GF, 20Q offset-clock form until the next late
Workspace window; in particular they retain that form through the next
second and third gathers.

At row U+70Q the **actual** native History2 and History3 records at every
normal native primary are, for d in[−5,5],

    B1(g,d) = Z1(g+d), if d=0 or [min(g,g+d),max(g,g+d)]
                                contains neither −1 nor19;
              the all-zero native word otherwise.

History1 need not be correct. The two equal later banks make the actual
temporal majority equal B1. The implication is conditional on the
stated completion; it is not a whole-rule self-simulation theorem.

The literal native function on this bank has differing Ages. For
example its next Age is2 at g=18 and23, and1 at g=19,20,21,22.
Consequently this history does **not** establish the previously proposed
global common-Age sequence or the eventual left-Age15 Flag2 premise.
The emitted native programme is replayed on these derived records, but
no second late Workspace trajectory is claimed here.

## Defined raw equations and explicit departure

The 37 consecutive native primaries are [2865,2902). The frozen frame
places GF, Age, Flag1, Flag2 and both Workspace bits there. The five
copy offsets are S=(0,−2,−1,1,2). At holder x, GE1 computes the same
literal native GF already used by GE0, from the eleven **old raw**
native words x−5..x+5. For output copy s, set

    a_s = (computed_GF(x)+s) modQ;
    q_s = majority_5{ old EarlyOut(x+s−t)[copy t] : t in S }.

If a_s is a native primary, its fifth-store port is (enable=1,value=q_s),
overriding any supplied port at that copy. Otherwise the supplied finite
port remains unchanged. The actual frozen GT0 Nextbit equation enforces
the fifth-stage [112Q,120Q) gate, with its reset at112Q taking priority.
At computed Age0, SimBit reads **old voted Nextbit**, while Nextbit is
reset to0 on that same update. This old/new order is essential.

The raw EarlyOut coordinates x+s−t lie in x+[−4,4]. Native computation
uses x+[−5,5]. Thus these new equations have radius5 on every raw state.
They neither inspect an upper state nor call the whole rule. The finite
ports in GE0 remain explicit inputs, so GE1 is a total local component,
not a total autonomous CA. The source file and receipt's transition
manifest give every new equation, service address, holder coordinate,
mask and clock priority.

This differs from executing Gray's own full fifth programme. It mirrors
the earlier native result instead. Computed-holder-GF plus s also differs
from the earlier raw logical-source GF read in GMW0's head birth. The
37-native restriction, free remaining ports and fixed 2346-bit **native
prefix**, rather than an own beta, are material boundaries of the claim.
No rule, frame, programme or shorter-U claim is silently substituted.

## Persistent actual EarlyOut and native commit

The accepted first-bank proof derives all native input records from the
shared lower history. The accepted physical GE0 execution writes the
35 native GF/Age/Flag outputs Z1(g); both Workspace EarlyOut primaries
remain0 after their69Q+3 reset. All five holders of a normal native
primary lie strictly in its colony, and agree through that execution.
The frozen physical code halts before75Q. Thereafter EarlyOut only
votes its held copies, except for a future69Q+3 reset or an execution
window. On the first Workspace prefix, local Ages are t or t+1 and
never revisit69Q..75Q. GF stays canonical, so the mandatory raw-self
GF wipe is false. Thus the native EarlyOut copies remain exactly Z1
through the first112Q..120Q window and first commit.

The accepted first pulse has reached the quiet form by physical806912:

    GF(x)=x modQ; offset Age label1 on[0,20Q);
    Flag1=1 on[−Q,0) union[19Q,20Q);
    Flag2=0; both Workspace bits=0.

With no Workspace forcing before the next96Q window, the literal
native equations retain this form, including through modulo-U wrap.
The two aligned clock jumps have separate predecessor/successor
colonies because the interval has20 colonies. Both Age majorities
exist; the two whole Flag1 predecessor strips do not inject a left
clock into the successor at either jump. Inside each strip both
majorities have its own clock label. This is the quiet aligned-family
argument already proved for the literal native equations, specialized
to20Q. Private fields cannot change GF/Age/flags on this interval:
the only private native inputs are Workspace, whose literal gate is off.

All five holders of each native primary hence use the common local
clock t+e20(g). Their computed service addresses equal the true logical
primary. At their first112Q update Nextbit resets0. At112Q+1 every
native copy reads the correct actual five-holder EarlyOut vote and
writes Z1(g). Subsequent writes up to120Q−1 repeat the same value.
The later rest updates vote their already coherent Nextbit. Finally
the Age0 update reads that **old** coherent value into all five SimBit
copies and simultaneously clears Nextbit. This proves the claimed
physical commit row and prevents an EarlyOut/Nextbit or same-tick-reset
substitution. Arbitrary non-native final ports cannot override the
native match or mix one logical primary into another.

## Next gathers, with actual barriers and clocks

After the commit, normal native SimBit copies only vote their held
value until the next commit. The special80Q flag writes target3 and
Q−3, not [2865,2902). Wipe remains false through the next gathers.
The actual native Flag1 barriers are now the **entire** colonies−1 and
19, not the earlier−1 and16. Clock labels change only at boundaries0
and20. Every surviving nonself path therefore has a single clock
phase; a path across a jump meets one of these Flag1 barriers.

For completeness, at any logical coordinate y the bitwise 3/5 raw-holder
vote of the GT0 storage update follows the clock and Flag1 of the colony
containing y: at least three of its five holders lie in that colony.
Those three use identical old voted logical inputs and identical
clock/Flag1 controls, so their computed bit outputs agree and determine
the new logical vote. This is a simultaneous one-step factor; it does
not assume that all raw holders agree at a boundary. At an interior
native primary all five holders lie in one colony and become coherent.
The accepted centre-clock GT0 factor applies with the new aligned
phase step and new barrier strips by exactly this argument.

For a receiver g, stage local start S in{32Q,64Q}, primary residue p and
d!=0, the actual capture row is

    U+S+2+|d|Q−e20(g).

Backward Mailbox travel visits logical coordinate gQ+p+dQ. If the
inclusive path of colonies meets a barrier, the nearest visited flagged
coordinate supplies a computed Mailbox0. Its row is at least U+S,
after the permanent flag strip is present, so no old load or stale
Mailbox bypasses the erasure. If no barrier is met, all visited
colonies have the same clock phase, and the travel arrives exactly at
the actual snapshot U+S+1−e20(g+d), at the **same primary residue** p.
It reads the already committed held native SimBit Z1(g+d). There is no
asynchronous ±1 residue shift on a surviving path. Self capture uses
the held SimBit directly and is not erased by Flag1. These are the
stated B1 equations. All captures finish by U+69Q+2, before the next
early reset/birth; at U+70Q the two later histories agree.

The checker records affine route endpoints for every p in[5,Q−5],
including every actual native primary, and every affected receiver
class. Receiver classes with any erased record are exactly
[−6,4] union[14,24]. Beyond them all records are the actual Z1 words.
The finite support of Z1.Flag1 is also included when checking next
native outputs. These checks supplement the symbolic path argument;
an endpoint trace alone would not establish all residues or the infinite
line. No ring, independent snapshot, or imposed spatial boundary is used.

## Verification and limits

The checker invokes the actual GE1/GE0 local equations for every native
primary and copy, both clock phases, reset/write/rest/commit cases and
all32 five-holder EarlyOut assignments. It tests native override of a
conflicting supplied port, persistence of a non-native port, and defined
legal finite behavior on retained arbitrary raw replacement fixtures.
The latter are finite checks, not a noisy GE1 theorem. The residue/path
and commit proofs above provide the universal conditional identity;
the finite traces are supplementary receipts.

The actual local GE1/GE0 History capture equations are also checked for
all11 offsets, both later stages and all five holders at six native
field primaries and six receiver classes. Their old Mailbox values are
those obtained from the proved actual route. This certifies the raw
capture interface without replacing the route proof by a prepared bank.
The same physical receiver phases and raw holders are checked at the
Age0,32Q and64Q History resets; History2's nonreset hold at64Q is checked
as well. Physical rows are recorded using the receiver's actual offset.

It reconstructs the derived next bank and invokes the literal native
function and the emitted 2346-bit native programme on each affected
class. It pins accepted old source/receipt dependencies, actual beta,
transition manifest and this proof. The read-only validator recomputes
the new results and all hashes; it does not modify old artifacts.

The first checker run compared a one-byte-per-bit beta serialization with
the frozen packed-bit file and failed that assertion before any rule
check. Its [checker snapshot](../../../figs/gray_counterexamples/GE1_native_writeback_initial_checker.txt)
and [failure log](../../../figs/gray_counterexamples/GE1_native_writeback_initial_check.log)
are preserved and pinned. The corrected checker packs eight bits per
byte exactly as the accepted GE0 emitter does. This is a checker
serialization mistake, not a rule or mathematical counterexample.
One subsequent check launch did not execute because automatic approval
review timed out; its [tool failure record](../../../figs/gray_counterexamples/GE1_native_writeback_launch_timeout.txt)
is retained separately from mathematical results.

| Step | Status |
| --- | --- |
| Same original real2 history and first native EarlyOut Z1 | **previously proved conditional components; reused** |
| New native fifth stores, raw locality and old/new reset semantics | **proved specified component equations** |
| Native EarlyOut persistence and all-five first native commit | **proved conditional on accepted prefix and literal Workspace premise** |
| Quiet native continuation through next gathers | **proved literal native argument under the stated finite gate interval** |
| Actual next History2/3 bank B1 and its temporal majority | **proved conditional physical gather composition** |
| Literal native and emitted-prefix outputs on derived bank | **exact finite checks plus the pinned native-prefix semantics** |
| All-raw fixtures / holder-coordinate replacement checks | **finite checks only; no noisy extension** |
| Full own beta<=Q, final K/layout, literal fifth evaluator and late order | **unproved** |
| Later Flag2 command/repair, full period/higher errors/iid/Gray refutation | **unproved; not claimed** |

No old accepted source/receipt, active rule, main report or schedule is changed.
