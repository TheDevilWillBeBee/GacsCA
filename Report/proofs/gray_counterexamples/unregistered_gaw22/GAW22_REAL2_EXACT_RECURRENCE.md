# GAW22: the same real2 repairs exactly at U²

This is a result about the unchanged, explicitly changed **GAW2R** rule
R: Q=8192, U=128Q=1,048,576, lambda=24 and original error separation104.
It follows [GAW21's actual intact-start fifteen-point
history](../unregistered_gaw21/GAW21_TWO_RECORD_REPAIR_THREE_RECORD_WITNESS.md)
through every subsequent row, rather than supplying another tape or
command history. No rule, schedule, ROM or constants are changed. Full
Word100 words, including every native and interpreter field, are retained.

The result is **eventual full raw repair** of this one original real2.
It does not establish general real2 recovery or refute Gray/Gacs/iid bit
memory. A separate temporary-field envelope failure for a transplanted
Proposition4_R is stated below with its exact different scope.

## Statement and time conventions

Use the terminating, recursively intact initializer H from
[GAW4](../unregistered_gaw4/GAW4_INTACT_REAL1_MAIL.md), with the actual
GAW2R Programme, zero unused/special Info, and H in E(H,0). Write
C_t=R^t(H) for the **noiseless raw upper history**, where t is an integer
number of upper ticks. Let W be exactly the three changed records at
upper row1 in GAW21: C_1 with the Info-copy words209,206,208 at records
-1,0,1 respectively changed from0 to1; all other words remain unchanged.
These are three holders of the same logical upper Info group y=0. Define
D_1=W and D_t=R^(t-1)(W) for t>=1.

On the physical lower line, start at H at row0. The only errors occur
**after the computed update to physical row U**, at the shared set

`{-4137,-4136,-4135,-4134,-4133,4052,4053,4054,4055,4056,12246,12247,12248,12249,12250} x {U}`.

Use GAW21's complete whole-cell replacements: each changes exactly one
Info bit and leaves all other fields actual. The faulted physical row is
exactly E(W,0). GAW21 certifies that this whole history is one original
real2 with no actual E0/E1 points. There are no later errors.

**Theorem.** This exact physical history satisfies, for every integer
t>=1,

`actual row tU = E(D_t,0)` and `shadow row tU = E(C_t,0)`.

Every D_t has legal native widths; no native padding is projected. For
1<=t<U, D_t and C_t differ as described in the exact recurrence below.
At t=U, D_U=C_U as complete raw configurations, and equality persists
for every later upper tick. On the lower physical line, full raw equality
first returns **after the fault** at row

`U² = 1,099,511,627,776`,

an elapsed time U²-U after row U. Throughout the half-open physical
interval [U,U²), logical lower primary4054 has five coherent Info copies
equal to1, whereas its shadow copies are0. Thus this particular trace
really has that finite lifetime; it is not merely an upper bound obtained
by checking some boundaries. All native GF, Age, F1/F2 and Workspace
fields agree with the shadow throughout this history.

This is a proof by exact recurrence and physical-period composition, not
an experiment running a trillion ticks.

## Actual clean bank and local-field contracts

Keep the actual Q8192 frame P=3848 through4343, 496 represented words,
five copy offsets S=(0,-2,-1,1,2), and 17 gather lanes. Let I(y) be H's
logical Info word. For a normal primary y=gQ+P+i, the terminating
self-encoding identity gives, for every d=-8..8,

`I(y+dQ) = word_i(H(g+d))`.

At an unused primary, including every y congruent to0 moduloQ,
I(y)=0. This includes y=0 and both special primaries3 and Q-3.

The legal physical period and all-phase own-programme contracts are the
frozen ones checked by
[GAW20's validator](../unregistered_gaw20/validate_gaw20_all_phase02.py).
Their legal-upper quantifier permits all SF words and packet states; it
does not require a canonical upper clock or coherent upper work. It
**does** require the six native words to be within their declared widths,
with zero high padding in their Word100 representation. Every actual
upper state here meets that requirement, so only the genuine legal-native
theorem is used. No malformed-native quotient or GAW20/21 raw-record
contraction theorem is invoked for D_t.

For canonical/common lower native geometry, every logical field is the
five-holder vote followed by the same operator at all its holders. In
the present upper history those votes become coherent after row2. The
canonical GF/common-clock native closure and raw-GF wipe equality then
permit the ordinary exact logical equations. They are checked against
the actual frozen `local_transition`, not a selected native projection.

The three gather starts are S_1=0, S_2=32Q, S_3=64Q. A stage resets Mail
at S_g, loads old Info at S_g+1, and shifts from S_g+2 through
S_g+16Q-1. Thus its travel distance at computed row t is

`d_g(t) = min(t-S_g-1, 16Q-2)`

while S_g+1<=t<S_(g+1), with the last stage holding until96Q. At lane
j=d+8, History capture is S_g+1 when d=0, otherwise S_g+2+abs(d)Q;
the capture reads **old** Info or Mail. The captured source is exactly
I(y+dQ), with full100-bit word retention. The preceding row's moving
distance is therefore abs(d)Q, not abs(d)Q+1.

For normal y, every such source retains residue P+i. It cannot equal0.
The disturbance at unused logical Info0 can pass a normal frame in Mail
between capture times, but cannot enter any normal represented History
lane. Heads read held Mem, Out, Scratch and Programme, not Mail directly.
This distinction is essential; there is no claim that Mail stays correct
inside the normal frame at all intermediate times.

Consequently every **actual** normal bank is the unchanged bank

`B(y) = sum_{d=-8}^8 I(y+dQ) 2^((d+8)100)`.

Both early and late Mem reloads use the actual bitwise temporal majority
of all three histories, which agree at normal primaries. Every normal
head therefore follows exactly its own unchanged emission on H(g-8..g+8)
and writes R(H)(g). This is universal in receiver g by the self-encoding
identity and the legal own-programme theorem, not an extrapolation from
the concrete runs retained in the receipt. Early completion is at most
213 updates; late completion at most141557, below147455 available
updates. All targets remain in[3848,4343] and the five actual holders in
[3846,4345]. No head visits any residue0 primary, and no heads from
different colonies interact.

Normal early Flag1/Flag2 outputs are0. Actual seeds, guarded flag
couriers, and the special Info writes at80Q-1 are therefore0. At the
96Q<=Age<98Q Workspace source window, computed-primary reads at3 and
Q-3 are0. Source neighbourhoods may overlap *physical holders* of
logical Info0; they access different copy indices and thus reconstruct
the unrelated logical special words, which remain0. With WF0, the
canonical/common GF/Age rows and zero native flags close. After98Q the
Workspace guard is closed. This derives every future command from the
same history and supplies the native/wipe premise throughout; it does
not prescribe silence as an external tape.

## Exact all-row difference recurrence

Differences below are full-word XOR differences of **logical fields**.
Each listed logical word y has identical differences at its five actual
holders x=y-s in the appropriate copy slot s. Unlisted fields and sites
are exactly equal to C_t.

At row1, the three raw changed Info copies are those of GAW21. At row2,
3/5 voting makes logical Info0=1 at all five holders. This coherence
persists until the upper commit at row U.

For 2<=t<U:

| field | exact logical XOR differences |
| --- | --- |
| Info | word1 at y=0 |
| History1 | none |
| History2 | at y=-dQ, bit `2^((d+8)100)` once `t>=capture(2,d+8)`, d=-8..8 |
| History3 | at y=-dQ, bit `2^((d+8)100)` once `t>=capture(3,d+8)`, d=-8..8 |
| MailL, MailR | words1 at y=-d_g(t), +d_g(t), respectively, during stage2 or3 after its LOAD; none at other stages |
| Mem | at y=-dQ, bit `2^((d+8)100)`, d=-8..8, during `[72Q+3,96Q)` and `[102Q+1,U)` |
| every native field, Head, Out, Scratch, Programme, both couriers | none |

History1 remains equal because the first LOAD and its zero-lane capture
were computed on row1 **before** the Info-only error was applied. Its
other lanes use Mail loaded from that same uncorrupted snapshot. The
second and third LOADs reconstruct the changed coherent Info word. Their
Mail fronts travel one site per tick; at the exact capture times the only
changed lanes have y+dQ=0. The lane-bit formula follows. Those histories
hold until the row-U reset. Temporal majority `(0,1,1)` gives the stated
Mem lanes at both actual reloads; the 96Q reset removes the first copy.
The normal-bank argument above shows that these residue0 Mem words are
never used by an interpreter.

This is an induction on **every** row. Coherent copies make each vote
exact. Reset/LOAD/capture/birth/active/hold/commit cases are the literal
frozen local equations. Between their finite event times, Mail shifts or
holds and every other changed word holds, so the formula advances
algebraically. Native/source closure was derived above for the whole
window. The normal head traces are coupled to their shadow through the
identical bank; packets outside normal frames remain0. Arbitrary old
input words are not substituted at any induction step.

At row U, commit reads actual **old Out**. Every normal Out equals the
shadow's legal emitted R(H)(g); every unused/special Out is0. Therefore
all Info words, including logical0, now agree with the shadow. The same
update resets Mem, all three Histories, Mail, Head, Out, Scratch and
couriers; native GF/Age/flags and Programme agree. Thus D_U=C_U is full
raw equality, not a voted decoder equality. Since Info0 differs at every
row1..U-1, this is the first upper-row return to equality.

[The checker](check_gaw22_actual_recurrence.py) adds9,559 full496-word
actual local_R event cofactors at each changed group, its two outside
sites, and Workspace reader boundaries. These include all reset/load/
capture events, source opening/closing, birth and commit, and Mail
passing both sides of the normal frame. It retains17 snapshots with
every changed raw Word100 record and its full shadow. Four actual normal
bank executions are retained; the concrete late H-bank run halts in66185
updates. These finite checks verify the literal interfaces of the written
induction; they are not substituted for its all-row/unbounded-location
proof. Receipt fields explicitly state that separation.

## Physical lower composition and first full repair

GAW21 already gives the actual row U=E(W,0). Every D_t in the induction
is legal: native GF=xmodQ, Age=tmodU, native flags/Workspace0, and all SF
words within the actual Word100 alphabet. The legal global physical
period therefore applies at each boundary to the **actual** E(D_t,0),
with its actual gathered banks and derived controllers:

`R^U(E(D_t,0)) = E(R(D_t),0) = E(D_(t+1),0)`.

Its infinite-line local proof discharges all exterior, reset, three-
gather, early seed, source/quiet, late execution and old-Out commit
premises. There is no finite-domain boundary assumption. Applying it
inductively proves the stated boundary relation for every t; it does not
invoke an upper noise history chosen independently of the lower fault.
At t=U both encodings coincide, giving lower full equality at U².
Determinism then preserves full equality at every later physical tick.

For every boundary tU, 1<=t<U, the normal lower primary4054 encodes
word206 of upper record0, namely D_t(0).Info.copy0=1 rather than0.
Its five encoded Info copies are coherent. During each intervening lower
period this is a **normal** primary: it is never a special80Q-1 courier
write. Info is held until commit, and canonical native GF makes the raw
wipe false. The actual early repair flags remain0 by the already-derived
upper native outputs. Thus these five physical copies remain1 for every
integer physical row in[U,U²), and become0 at U². This gives the first
post-fault full raw repair time, including the ticks between boundaries.

The persistent bit is an **unused logical upper Info** word. Nothing
here proves that a represented higher memory bit is lost, and no positive-
rate conclusion is drawn from this finite adversarial history.

## Which printed Gray proposition is tested

Gray's primary source is [the reader's guide](../../../../papers_txt/gray_readers_guide.txt).
The exact relevant statements are on printed p36 (text lines1614..1622)
and p43 (lines1946..1951). We paraphrase their field scopes and hypotheses
here; existing [literal-stage envelope
audit](../GRAY_LITERAL_STAGE_ENVELOPE.md) and
[raw gather component](../GT0_RAW_GATHER.md) already discuss the separate
conditional Gray mechanism-level I/N/S/G/R obstruction.

**P5, Address only.** For each actual level-k error, Gray uses one spatial
box `[jQ^k,(j+2)Q^k)` with lifetime U^k/16, and claims preservation of all
level-n **Address** fields outside those boxes. It is part of the
initially intact hierarchy/trickle-down argument. This history never
changes any Address/GF. Its long Info lifetime and temporary banks do
not contradict that proposition, even when they outlast U²/16.

**P4, all simulation fields, level1 noise.** Gray's printed statement
allows one point box for each level0 error and one **fixed** two-colony/
two-period box `[jQ,(j+2)Q) x (kU,(k+2)U)` for each actual level1 error.
Outside their union it requires pointwise equality of all simulation-
structure fields with the deterministic system. The original physical
fifteen-point fault is real2, so that P4 level1-noise hypothesis does not
apply to it directly. Nor does P4 imply the failed three-record
one-period contraction conjecture of GAW21.

There is, however, a **separate exact transplanted P4_R failure** on the
same derived upper path. This path is also precisely an autonomous run
of R from H with the three genuine whole-cell replacements at upper
row1 and sites-1,0,1. Its rescaled shared support is one original-c104
real1: no E0 subset is isolated, its extent is3x1, its internal diameter2
precludes a separated pair of candidate1 subsets, and there are no other
errors. The checker classifies this complete support; no independent
future upper history or commands are prescribed.

At upper row `34Q+1 = 278529`, the second gather's travel distance is2Q.
Actual MailL.copy0 at x=-2Q and MailR.copy0 at x=2Q are both1 while their
shadow words are0. These are simultaneous discrepancies of ordinary raw
SF fields with spatial span4Q, which cannot lie inside any one fixed
two-colony box of width2Q. There are no E0 boxes to add. Thus the
transplanted literal pointwise **all-SF P4_R** is false for GAW2R. The
two sites are sampled in the full-raw receipt and also follow immediately
from the exact recurrence. This temporary envelope failure coexists with
the proved full eventual repair; it is not a decoded repair failure.

This is **not** a faithful Gray P4 counterexample. GAW2R retains the
printed Mail erase/three-gather ideas but changes the radius, alphabet,
own programme, controls, couriers and schedule. The accepted conditional
Gray observation in the earlier linked audit is not strengthened by
silently identifying those mechanisms with this complete implementation.

## Status, limitations and immutable replay

- **Proved:** exact D_t recurrence at every upper row1..U; actual normal
  capture/Mem/head coupling and source/native closure; full legal-width
  physical composition; first post-fault full raw repair at U² and the
  continuous encoded Info-bit persistence until then.
- **Proved for the changed rule:** the rescaled original-real1 path
  violates the transplanted literal all-SF P4_R spatial envelope.
- **Not contradicted:** Gray's Address-only P5, eventual repair of this
  actual real2, or bit memory.
- **Unproved:** arbitrary real1/real2/higher histories, continuing iid
  noise, a positive rate, or faithful Gray/Gacs whole-rule refinement.

Every prior departure remains explicit: corrected h1 erasure, radius8/
17 lanes, WORD100/FULLCOL, holder-computed control, native-only early
pass, guarded couriers and102Q late-start/rest departure. Immutable
storage is270349 bits; the direct beta is41162 bits with1049 dictionary
entries. This is not Gray's Q-bit Programme implementation. No shorter
U or new rule is proposed.

[validate_gaw22_actual_recurrence.py](validate_gaw22_actual_recurrence.py)
checks the frozen555-asset GAW21 ancestry, including the exact15 complete
original payloads and original shared real2 classifier, rebuilt actual
ROM/dictionary/listing, all legal compiler/helper/cost contracts, intact
H and legal physical-period proof. It then replays the new recurrence
receipt read-only and checks all source/dependency hashes again. The
manifest pins this proof, checker, receipt and completed issue log.
Registered main child/root documents, accepted GAW0..21 and active G17
are unchanged.
