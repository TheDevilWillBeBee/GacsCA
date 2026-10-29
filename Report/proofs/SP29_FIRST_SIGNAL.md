# SP29: the actual first signal and one shrinking pulse

This concerns the existing isolated SP29 own-ROM rule of J166. No rule,
constant, ROM or compiler is changed. The result supplies a **first-period**
damaged-history premise. It does not supply later replenishment, general
finite-island erosion, an upper error map or an iid noise threshold.

Let Q=1024, U=475136, TF=278401, a=128Q−512 and b=144Q. Start at
clock0 with the complete lower encoding E29(z), where upper z has
GF(j)=j modQ, Age0 and every field other than GF/Info0; its five raw
Info components may be arbitrary. Change lower GF to (x+512) modQ
on[a,b), and change lower Flag1 to1 on[127Q,a) and[b−512,b).
Every other initial field is retained. These changes are confined to
one17Q-site row[127Q,144Q). There are no subsequent errors.

An intact infinite hierarchy from J166 is an allowed z: its upper
GF/Age/private fields have this form. Thus the preparation can be made
by one physical error row at input time0 of an intact hierarchy. This
is the same dense error-location shape classified in J156 (real3 at
c16; real2 at c104), translated in time. Its specific overwrite payload
does not change its error class. This is not an iid failure witness.

For a logical physical primary y, write M(y,t) for the majority of its
five raw Info holders in computed state t.

**First-signal theorem.** At computed state TF, native GF/Flag1 are
still the prepared template, Age is the common legal TF clock and
native Flag2/Workspace flags/packet/code validities/backward pressure
are0. The exact retained signal tracks are

    M(jQ+509,TF) = 1 exactly for j=128,...,143;
    M(jQ+1021,TF) = 1 exactly for j=124,125,126,144,145,146.

Both are zero at every other primary of the corresponding residue.
This quantifies over every initial upper Info payload, not a measured
sample of the payload. The second line is essential: the actual signal
is not J165's prescribed all-zero true-phase track.

**Proof.** The quiet-template lemma in J156's
[SP28_FULL_ADDRESS_ISLAND.md](SP28_FULL_ADDRESS_ISLAND.md), using162
refinement and4258 native cofactors with common Age free, applies
before TF. SP29 and SP28 have identical native maintenance/refinement;
both epoch-force guards and their birth guards are closed on those
legal clocks. Literal WF1 is also0 before TF, independently of Info.
With empty initial headers no code/packet/backward source can arise
before that sole birth. The native template is therefore stationary,
the actual GF refinement equals the raw GF at every reader, and actual
keep is1. This is a native conclusion, not an assumed future boundary.
Info is its own old five-vote until the special signal write at
T_sig=TF−1; commit is later. In particular every logical Info value
used by the three gathers is constant.

Let S=[127Q,a) union[b−512,b) be the two stationary Flag1 strips.
The logical mail majority has an exact gated transport recurrence:
at a gather load it is the original Info majority times g(y), and
during each fast shift it is the previous logical majority at y±8
times g(y), where g(y)=1 if y is outside S and0 otherwise. Indeed each
new physical mail copy is the same old source majority times its
holder's quiet-Flag1 gate. Taking the five-vote gives source majority
times the majority of the five quiet gates. For these512-site strips
that gate majority is exactly g(y), including both boundaries. The
1024 old-copy/gate assignments and28 boundary checks certify this
identity. The protected Flag2 courier is closed during all gathers;
its later exception to ML gating has no bearing on these captures.

At offset d the capture path includes source (j+d)Q+phase and
destination jQ+phase, with |d|Q/8 successive eight-site shifts. It
returns the original Info bit iff none of those logical path positions
lies in S. The three gather loads restart the same path from the same
unchanged Info. Thus all three captured bits agree; the third gather's
majority and the subsequent history copies give that exact bit. SF
copy incoherence at a gate boundary does not invalidate the argument:
the recurrence is for the logical majority, and each capture votes
that majority before writing its five coherent history copies.

First consider complete foreign frames with origins jQ−512,
j128..143. Their virtual GF bits at phases59..68 read true physical
phases571..580, which are upper h2 bits139..148. Those encoded bits
are initially0 everywhere and stay0 before the signal. Mail clearing
also preserves0. Every direct and gathered virtual GF input of the
own programme is therefore0. A full-circuit cofactor proves native
Flag1 output1 and all computed GF bits0 when all virtual GF inputs
are0, leaving **every other circuit input free**, including I.

The working interpreter in each such full frame has canonical GF
relative to its shifted origin, a common clock, keep1, initially zero
private work, five coherent constant history inputs, and the certified
own ROM. All front centers38..985 and their radius37 footprints1..1022
lie in that full frame; Match/store/copy geometry is the same as J166.
The physical register/scratch/pending induction of J135/J166 hence
executes its own abstract programme. No correctness or consistent
upper configuration is required for the other input values: they are
fixed arbitrary circuit inputs. The proved early-output equality
therefore gives Flag1 Hold1 at virtual965. Its right courier travels
entirely through quiet native Flag1 before TF and writes virtual1021,
physical jQ+509. This creates exactly the sixteen stated ones.

Next consider complete true frames j<=126 and j>=144. Their native
Flag1 is0 throughout their own frame, and the same interpreter
induction applies. A gathered GF word at logical offset d is
(j+d) modQ if its physical path is not cleared, and0 otherwise.
This clearing predicate is identical for all ten phases59..68:
a512-site strip is longer than the eight-site path step, and each
path either crosses a whole strip or has an endpoint well inside it.
The arithmetic-progression checker verifies every relevant bit route,
rather than assuming a continuum path cannot jump over a boundary.

All virtual Age/native flags/Workspace flags/packet/code validities
and backward pressure inputs are0: their original encoded bits are0,
and clearing cannot create a1. The remaining circuit inputs may be
left free. The75 complete true-frame cofactors in j90..181 show that
the actual Flag1 output is1 precisely at124..126 and144..146.
For j<=89 or j>=182 no requested |d|<=37 path reaches S, so the
ordinary canonical-native induction gives output0. The courier in
each complete true frame is quiet and writes its actual Flag1 value
to jQ+1021 at T_sig. These are the six true-phase ones.

For j127..143 the physical1021 primary and all its holders have wrong
native GF, so that primary has virtual phase509. It is not a special
write and retains its initial unused Info0. Outside the wrong island,
the physical509 primaries have true native phase509, are also not
special writes, and retain upper h2 bit77=0. The primary127Q+509 is
three sites below a; all five holders lie below a, so the same argument
covers this boundary without assigning it to a foreign interpreter.
The primaries143Q+1021 have all holders below b and are likewise
covered. The only special signal writes just proved occur at the
listed complete-frame primaries. There is no missing partial-frame
signal case. The TF state has WF1=0 because its preceding input
clock is TF−1, when that guard is still closed. QED.

**First-pulse theorem.** At computed time TF+6144, the actual native GF
is canonical outside[124416,139264) and shifted by512 inside it. The
island's width is14848 instead of16896, a decrease of2Q. Its left/right
edges moved−6Q/−8Q. Native Flag1 is1 precisely on the two512-site
strips preceding those edges; Flag2/Workspace flags/packet/code
validities/backward pressure and code positions are0. Eight ghost
MF509 ones remain; MF1021 is1 at the three right-hand primaries
144Q+1021,145Q+1021,146Q+1021 and0 at the other true-phase primaries.
This is a finite-time native/projected conclusion, not full data repair.

**Proof.** The preceding theorem supplies exactly the initial premises
of J164's native/Info factor, including the actual extra six true-phase
ones. The factor permits arbitrary remaining private fields/I, so the
preceding actual own-programme history does not create an extra premise.
Its unchanged integer recurrence is checked for all6145 rows on the
N=256Q quotient. Every projected defect is confined initially to
I=[124Q,147Q). J165's binary-GF hull bound still gives outward speed
at most3; it allows arbitrary native flags and signal values.
Retained Info ones cannot grow, and other projected fields propagate
at most8 per update, with GF refinement's37-site seed reserve. The
same inductive support bound is therefore

    [124Q - (8(r+1)+37), 147Q + (8(r+1)+37)).

The checker compares every site outside this interval with the evolving
Q-periodic background at every row. That background has the actual
transient epoch flags/headers; it is not replaced by an always-quiet row.
At r6144 the interval is[77779,199725), strictly inside N262144. The
same seam argument as J165 lifts the exact quotient recurrence to Z.
The complete final native/code state equals J165's D2Q final state;
only the stated three extra Info primaries differ. This proves the
stated endpoint for the actual preceding physical history. QED.

The exploratory prepared-pattern C run is **measured only** and retained
separately. The first-signal proof uses full symbolic cofactors and the
physical copy/path/interpreter induction; the first-pulse proof uses
the exact integer certificate plus the explicit infinite-line support
argument. Neither proof samples initial upper payloads or asserts a
later signal pattern from this one endpoint.

| Step | Status | Limit |
| --- | --- | --- |
| Prepared template persists from clock0 until TF | proved | Same quiet native equations; headers initially empty, no later errors |
| Exact gated-mail source paths and full-circuit Flag1 cofactors | proved | Coherent initial encoding and fixed native strips |
| Actual own programme supplies both first MF tracks | proved | All initial upper Info payloads; prescribed native error at clock0 |
| One actual shrinking pulse on Z | proved | Exact supplied tracks, no later errors,6144-update certificate/lift |
| Whole simulation data restored, later signal replenishment, general eroder | unproved | The native endpoint alone supplies none of these |
| All higher errors/continuing noise and positive iid rate | unproved | One prepared first-period error is insufficient |

Receipts: SP29_first_signal_certificate.json,
SP29_first_pulse_certificate.json and their pinned dependencies in
figs/robustness. The exploratory run is
SP29_prepared_history_signal_pulse.json; no additional rule change occurs.
