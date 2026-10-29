# GMW7: a changed single-gather rule with a complete encoded period

This rule keeps Q=8192, U=128Q=1048576, lambda=24 and c=104. It is an
**explicitly changed construction**, not a reconstruction of Gray. The
theorems below close input preparation and period composition for this
particular finite rule. They do not close Gray's three-gather/early-flag
protocol or its higher-error repair proof.

Sources: [total local rule](gray_token_gather_v7.py),
[full own-programme emitter](build_gray_token_gather_v7.py),
[prepared execution checks](check_gray_token_gather_v7.py),
[execution-bound checker](check_gray_token_gather_v7_bound.py),
[actual gather/cofactor checker](check_gray_token_gather_v7_period.py),
[read-only validator](validate_gray_token_gather_v7.py).
Receipts: [prepared execution](../../../figs/gray_counterexamples/GMW7_prepared_execution_certificate.json),
[bound](../../../figs/gray_counterexamples/GMW7_execution_bound.json),
[period](../../../figs/gray_counterexamples/GMW7_single_gather_period_certificate.json).
Actual emitted stores: [beta](../../../figs/gray_counterexamples/GMW7_token_beta.bin),
[dictionary](../../../figs/gray_counterexamples/GMW7_dictionary.json),
[listing](../../../figs/gray_counterexamples/GMW7_token_listing.json).

## Changes and storage

GMW7 inherits GMW6's h1 Flag2 erasure, holder-computed native Address controls,
100-bit Info/Out/Scratch/Programme words, eleven-word Mem bank, twenty-two-word
head, and constant-zero native Workspace.Flag1/2 outputs. Its immutable
instruction access is a nine-bit token lookup followed by a fixed dictionary
lookup. Programme fields are mutable and voted on explicit reads; executing
instructions uses the immutable tables. These remain substantial departures
from Gray, especially the omitted simulated-flag Workspace repair pulses.

The new rule loads **one snapshot at computed Age32Q**. Lane j=0..10 then
travels one site per update for |j-5|Q updates, towards the source colony
j-5, and freezes. All lanes are ready by37Q. There is no three-snapshot
majority or early simulation for flags. This schedule is explicitly changed;
the total U, reset/birth/last-stage endpoints remain unchanged.

The only new ALU primitive is MADD5(a,b)=(5a+b)mod2^100. It is ordinary
finite arithmetic, used to combine field-index and copy-index addressing.
The full emitted programme has863 instructions and15 data words:878 tokens
and7902 used beta bits, padded to8192. The separate dictionary has512 entries
of100 bits,425 used. Total immutable capacity is **59392 bits**; unpadded
used stores take7902+42500=50402 bits. This is not a Q-bit Gray evaluator.
The physical alphabet remains18537 bits; its raw cell frame remains191
Word100 rows at primaries4001..4191.

## Exact encoding relation and statements

Let F7 be the pinned total rule and let C=(C_g)_(g in Z) be **arbitrary legal
raw F7 cells**. For row w=0..190 put p_w=4001+w. Define E7(C) as the family
of lower configurations with the following properties:

* Native Address at x is xmodQ, common Age0, and all four native flags0.
* Each SF field has coherent five-copy logical values: slot s in holder x
  stores the logical value at y=x+s, for S=(0,-2,-1,1,2).
* Logical Info at gQ+p_w is `cell_words(C_g)[w]`.
* Other logical Info values and the logical Head, Mem, Out, Scratch and
  Programme values are arbitrary legal values. They need not equal represented
  upper fields or the immutable programme.

This broad encoding imposes no alias between unrepresented primaries and
represented upper fields. Define D at a boundary by voting the five Info
holders of each represented primary and assembling those191 words. D is
used only on the family and noisy images in the theorem, where its native
components have their legal widths; it is not an arbitrary-state decoder.

**Noiseless period theorem.** For every X in E7(C),

    F7^U(X) belongs to E7(F7(C)); D(F7^U(X))=F7(C).

Here F7(C)_g uses the actual radius-five upper neighbourhood C_(g-5..g+5).
No upper geometry, flag or private-field coherence is required. The lower
gathers, evaluator, own-programme and commit are actual F7 equations; there
is no preloaded-tape premise in this theorem.

**Continuing pure-E0 period theorem.** Let X_0 in E7(C), and let
Z_t=overwrite(X_t,B_t), X_(t+1)=F7(Z_t), where every B_t is an arbitrary
whole-cell replacement on an error support D_t. Suppose the shared
space-time error set consists entirely of Gray E0 singleton/spatial-pair
groups, isolated by the original lambda24 convention. Then

    X_U=F7^U(X_0) belongs to E7(F7(C)); D(Z_U)=F7(C).

The same statement composes over consecutive periods, provided the history
continues to be pure E0. This does not prove the required theorem with real1
and higher classes, nor an iid hierarchy or memory theorem: iid noise has
higher-class events. c104 is retained in the classifier but is not needed
for a history containing only E0.

## Full own-programme semantics (proved by contracts)

The [GMW6 register/field proof](GMW6_TOKEN_WORD_EVALUATOR.md) describes
the unchanged native prefix, raw invalid-state guards, candidate order,
fourteen instruction cases, all four SEEK kinds, reset/birth/rest/commit
order and old-Programme read. These proofs apply **verbatim to those blocks**
after reassembling label values. They are proofs for our explicit variants,
not applications of Gray's reliability argument. The new static emission
independently decodes every instruction, token, dispatch target and constant.
The following proves every changed block.

**Index arithmetic.** Register rows, Mem rows and copy addressing use
MADD5(index,copy), replacing the old two shifts and additions. On their
asserted ranges index0..15 or0..10 and copy0..4 this is exactly5index+copy,
without modular overflow. ALUX in the simulated RUN block invokes the same
total primitive for arbitrary100-bit arguments and function22. Invalid
function numbers still return2^99. Thus this optimisation changes the
physical rule's instruction set but introduces no intrinsic F7 evaluation.

**Gather phase.** At copy entry R12=5+S[copy], the input lane of its logical
source. R10 holds new native Age minus32Q modulo2^100. New Age is a legal
20-bit word. If it is below32Q, the result is a large wrapped positive
number, greater than5Q; all Mem lanes are therefore stationary. Otherwise
this word equals the nonnegative delta used in the kernel. A zero delta
votes old Info, caches it in R9 and writes it to all eleven Mem rows. The
vote helper preserves R9 and R10, including through intervening Head rows.
Every copy gets its own actual logical Info vote.

For Mem field row index f=22..32, the lane is j=f-22 and its centre index
is27. The branch computes threshold=|f-27|*8192. For f<27 it decrements
R12 while voting that Mem row, and restores R12 afterwards; for f>=27 it
increments R12 and restores it. If threshold<delta it uses the stationary
vote instead. With delta>0 the centre's threshold0 always selects the
stationary path. Hence exactly the lanes with delta<=|j-5|Q move, with
the kernel's sign. At delta>5Q all lanes are stationary. At delta0 the
cache branch handles all lanes before these comparisons.

R11 is the first raw row of each field. Every voted path advances it by5;
the cached path explicitly advances it by5. The store address is
4001+(R11-5+copy), and R13 increments once per field. Thus no path skips,
duplicates or aliases a represented output word. The largest logical
source is y=3 and the smallest -3. The actual old input is C_(y-t), slot t;
its lane y-t+5 is always0..10. These are raw-holder inputs, not head-centre
surrogates.

**Active IO timing.** New Mem values differ from old voted Mem only at
computed Ages32Q..37Q. Active packet execution uses112Q+2..120Q. Therefore
the kernel's packet step reads old voted Mem throughout the active interval,
as does the unchanged emitted SEEK implementation. The two intervals are
disjoint on every legal raw input, even if native Age is damaged; both tests
use the same newly computed Age. Wipes still zero all SF fields after the
stage calculation. These contracts exhaust the differences from GMW6 and
prove the full emitted programme equals F7 on **every legal raw radius-five
upper neighbourhood**.

The97 retained prepared comparisons are additional measured checks. They
include the previous malformed/head/opcode cases and six gather-clock cases;
maximum observed execution is47085 ticks. They are not this universal proof.

## Universal deadline and physical machine (proved)

The fresh bound checker has the hardened GMW6 interval/finite-set semantics,
including invalidation of stale comparison facts on every source-register
write. MADD5 evaluates finite Cartesian sets exactly; otherwise, if
5max(a)+max(b)<=2^100-1, it returns the inclusive interval between the two
endpoint sums; crossing a wrap returns the full domain. This overapproximates
all modular outcomes. New gather branches are evaluated by the same sound
zero/nonzero, LT/EQ domain splitting; readonly input words remain arbitrary.
All branch paths and all physical instruction fetch/operand travel are
included. No lower loop count depends on an unknown raw upper value.

The five enlarged copy-entry bounds are9990,9869,9748,9627,9565 updates.
Their sum48799 plus269 native/main/tail overhead gives **49068**; the separate
wipe path is1364. The physical budget is65535 updates after the birth row,
leaving16467. The finite abstract certificate visits1522930 states. It is
an overapproximation proof, not the observed maximum.

Canonical lower native GF/common legal Age/flags0 close under h1 and increment
Age modulo2^20=U, so no raw-GF wipe occurs. All SF equations use the same
logical votes and calculated phase at all five holders; their service
Address is corrected holder GF+s. Thus coherent copies stay coherent.
Reset at112Q clears Head/Out/Scratch everywhere. Birth at112Q+1 makes one
head at4001 in each colony. Execution moves at most one site per update,
never leaves4001..4191 and performs actual local IO. The unchanged unique-head
and five-holder induction from GMW6 lifts the emitted instruction execution
to F7 without external preloading or a host evaluator. Halting Head/Out
persist through the rest of the period.

## Physical gather and boundary composition (proved)

Info is voted unchanged whenever new Age!=0. From initial Age0 through
new AgeU-1 it is therefore the initial logical Info. In particular the
32Q snapshot sees the represented C words, regardless of arbitrary initial
Mem/Out/Head values. For every logical coordinate y and lane j, write
d=j-5 and let I(y) be initial logical Info. The actual gather equations give

    Mem_j(y, Age32Q+delta) = I(y+sign(d)*min(delta, |d|Q)),
    0<=delta<=5Q.

At delta0 the load equation proves the identity. For a moving lane the
old source is y+sign(d); applying the induction hypothesis at delta-1
advances the argument by exactly one. For a stationary lane the capped
argument is already |d|Q. Thus the identity holds at every tick, not just
the retained sampled clocks. The checker certifies450571 lane/tick arithmetic
identities. At a holder x's output slot s the old lane vote reads actual
holders x+s+step-t, t in S, at distance at most5. The75 route cofactors
and full-kernel comparisons retain these actual inputs.

For p_w=4001+w, after capture at32Q+|d|Q the source is
gQ+p_w+dQ=(g+d)Q+p_w. All2101 word/lane routes therefore contain exactly
`cell_words(C_(g+d))[w]`. Every represented primary and its five holders
are within the owning colony. Last capture37Q precedes reset112Q and birth
112Q+1; all lanes retain their values through execution. There are no
simulated Workspace sources in F7 and no native wipes in this trajectory.

The full own-programme theorem now applies to this **physically gathered**
tape, giving all191 Out words of F7(C)_g by at most49068 execution updates.
Only frame primaries receive interpreter Out writes; reset had made all
other Out values0. At the update producing Age0, old voted Out is committed
before reset. It gives the correct represented Info and makes other logical
Info0. Head/Out/Scratch reset; Mem remains coherent; Programme has been
printed from the pinned beta using corrected service Address. The broad
E7 definition permits these private values. This proves the noiseless
period theorem and avoids an auxiliary-alias assumption.

## Current-row noise and decoder (proved for pure E0)

F7's native equations and all head/source/reset/commit equations except the
new Mem branch are identical to the frozen
[GMW6 coupling proof](GMW6_E0_COMPONENT_COUPLING.md). Its universal argument
applies: on canonical geometry/flags0, at most two arbitrary replacement
cells per eleven consecutive sites cannot change adjusted GF or Age votes,
create a native Flag1/2 source, or cause a wipe. All new native fields and
control phases are exact. That proof covers all whole-cell payloads, not
only changed Info bits, and leaves no previous-error wake.

The new Mem destinations likewise vote five distinct actual raw holders,
inside the same radius-five cone. Load reads old Info at x+s-t; moving
lanes read old Mem at x+s+sign(d)-t. With at most two bad physical cells
each bit has at least three correct votes. Stationary lanes use the original
five holders. The calculated phase and service Address are already correct,
so every output word equals its clean output. Coherent SF closure holds
also during loading and lane transport. Consequently F7(overwrite(X,D))=F7(X)
for every quiet coherent X and every such current-row support D, with
arbitrary legal whole-cell payloads.

Distinct Gray E0 groups at a common tick are separated by more than24;
each group has at most two sites. Thus every eleven-site interval contains
at most two errors. Induction on t proves the claimed clean recurrence
X_(t+1)=F7(X_t), despite continuing adversarial overwrites in Z_t. At a
boundary, each represented five-holder Info vote in Z_U still has at least
three correct values and recovers F7(C). This proves the pure-E0 theorem.
The retained finite full-cell checks across snapshot/transport/freeze
boundaries supplement the universal majority proof; they are labelled
measured, not substituted for arbitrary-payload reasoning.

## Status and remaining goal

| Step | Status |
| --- | --- |
| Total raw radius-five rule and invalid-state behavior | **proved changed rule** |
|7902-bit token beta plus separately counted51200-bit dictionary | **proved static emission** |
| Full all-raw own-programme/native/word/head/gather semantics | **proved register and field contracts** |
| Universal49068 execution bound at unchanged last-stage endpoints | **proved interval overapproximation** |
| Physical speed-one capture of all191 by11 input words | **proved route induction** |
| Broad Info noiseless encoded period | **proved changed rule** |
| Arbitrary-payload continuing pure-E0 period and majority decoder | **proved changed rule, original E0 convention** |
| Retained finite execution and gather checks | **measured supplementary evidence** |
| Gray Q-bit mutable programme, three gathers/early flags/simulated repair pulses | **unproved; explicit departures** |
| Real1 and higher repair, intact-hierarchy finite counterexample, iid memory | **unproved** |

No faster U is inferred. This supplies an actual own-programme with physical
input/output for an explicitly changed Gray-scale variant; it neither proves
the original reliability goal nor refutes Gray.
