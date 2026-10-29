# GAW13: actual gather faults, wide retained History and decoded recovery

This is a standalone audit of the **unchanged frozen GAW2R rule** at
Q=8192, U=128Q=1,048,576, lambda24 and c104. It adds no rule, ROM,
schedule or shortenedU, and changes no active G17 or registered artifact.
Three actual intact-start real1 histories produce a wide temporary SF
footprint. Two recover completely at U; the third sacrifices only one
upper record and recovers completely at2U. No operational, Gray/Gacs or
iid-memory counterexample is established.

The radius8/17-lane transport, WORD100 and padded native representation,
h1 Flag2 correction, computed-holder service Address, bounded couriers,
early native-only evaluator, immutable code/dictionary and102Q late start
remain explicit departures from Gray. The frozen direct beta occupies
41,162 bits, uses1,049 distinct dictionary words and270,349 immutable
bits, and exceeds beta<=8192/dictionary512. Its49,037-bit alphabet is
represented by496 words. These fit/refinement gaps remain open here.

## Exact history and results

Let F be the frozen [GAW2R local rule](../unregistered_gaw2/gray_three_gather_gaw2r.py)
with its exact emitted own ROM. Use the recursively intact infinite-line
H from [GAW4](../unregistered_gaw4/GAW4_INTACT_REAL1_MAIL.md), including
the real Programme bits, with H in E(H,0) at every level. Errors replace
raw cells of computed row t; the next update computes row t+1. All three
histories consist of exactly one dense sixteen-site row, with no later
errors:

    T = 64Q+1 = 524289,       B = [3841,3857).

T is the actual third-gather LOAD and centre-capture row, immediately
after the64Q reset. Retain every actual native GF/Age/F1/F2/WF1/WF2 field
and every SF track outside the explicitly replaced payload. With
M=2^100-1 and A=2^1700-1, the payloads are:

| Case | Each physical replacement at x in B |
|---|---|
| Mail | all five MailL and all five MailR slots equal M |
| Mail+Info | the same Mail replacements and all five Info slots equal M |
| Mail+Info+History | those replacements and all five slots of each History1/2/3 equal A |

Each replacement is a legal raw **lower** cell, including the full1700-bit
History fields. Every overwritten cell is genuinely changed. All16
complete old/replacement496-word records and the original classifier are
retained. Extent16x1 and diameter15 give no24-isolated singleton or
adjacent-pair real0 component. The linked dense row is one real1, with no
two nonempty candidate1 subsets104-separated. No upper error history is
chosen independently of this single physical fault.

**Selected-history theorem (proved).** At row72Q+2 the first two cases
have wrong retained History3 in sixteen noncentral colonies,
-8..-1 and1..8. The third additionally has locally corrupted retained
histories in colony0. Those physical SF differences cannot fit in a
single fixed adjacent pair. Nevertheless the temporal-voted normal Mem
banks are exactly clean everywhere for the first two cases and differ
only in colony0 for the third. The first two full raw configurations
equal their clean infinite-line shadow at U. In the third case the only
wrong normal upper record at U is receiver0, whose native words are

    (2^100-1, 0, 1, 1, 0, 0).

This record has illegal native GF padding and is outside literal legal
E(Cprime,Aprime), but its seventeen actual unmasked next-period banks
produce the complete2U shadow. All three histories remain equal to that
shadow thereafter by determinism.

This theorem quantifies these three exact histories. It does not prove
general SF16x16 real1 recovery, arbitrary earlier or mixed-control faults,
or a global noise theorem. A dense16x1 history is within the requested
burst family; no sixteen-row campaign is claimed.

## 1. Actual chronology and source equations — proved

[check_gaw13_gather_sf.py](check_gaw13_gather_sf.py) imports the frozen
kernel, full own ROM, terminating I/H initializer and actual physical
execution helpers. It never edits the transition or supplies future
commands/tapes. Its hash manifest inherits every frozen GAW12 asset,
including prior own-programme/period proofs and primary papers. The
read-only validator checks all hashes, exact emitted-ROM identity, prior
physical contracts and every new actual-history computation.

Put P=3848 and S=(0,-2,-1,1,2). A logical y has five physical holders
y-S[h]. At T the **actual** clean row has GF=x modQ, AgeT, flags0,
Head/Mem/Out/Scratch/couriers0, InfoI(y), Programme beta(y modQ), MailL
and MailR equal I(y), and

    H1(y)=H2(y)=sum_{d=-8}^8 I(y+dQ)*2^((8+d)*100),
    H3(y)=I(y)*2^(8*100).

The first two gathers and retained histories precede this row; the third
LOAD and centre capture have already happened. The actual reset/LOAD
equations applied to H give these values, with no evaluator premise or
preloaded bank. I is the recursively defined primary Info of H, not an
arbitrary chosen tape function.

After the physical replacement, a five-holder vote differs from that
clean logical value exactly for y in B. Inside B at least three holders
carry M/A; outside B at least three carry the old coherent value. The
first clean update computes identical logical values in all five copies:
their service Address is y modQ and their clock is common. Programme is
regenerated. The all-raw local_R is used at the original physical holder
coordinates, not replaced by a raw head-centre lookup.

Let L0(y)=R0(y)=M for y in B and I(y) otherwise. After the overwrite,
the actual third-stage Mail transport is, while its active shift holds,

    L(y,T+n)=L0(y+n),       R(y,T+n)=R0(y-n).

It stops at the stated16Q active-end branch. At the third capture of
lane8+d, d!=0, the computed clock is64Q+2+abs(d)Q; the old Mail clock
is64Q+1+abs(d)Q. The captured value is exactly

    L0(y+dQ)  for d>0,     R0(y+dQ)  for d<0.

The original centre lane was captured before the fault. In the third
case its directly overwritten History word is retained until a later
capture replaces that lane; the implementation applies only actual
future reset/capture events. History1 and2 are already retained and have
no further reset before U. This accounts for direct bank corruption
and the propagating carrier corruption in the same physical history.

All native fields remain canonical/common. No native flag can be born
before96Q: geometry/clock mismatch sources are absent, flags initially0,
and the actual Workspace guard is closed. The native Flag1 Mail erasure
therefore does not erase these third-gather pulses. There is no mandatory
SF wipe because newGF equals the retained raw GF at every holder.

The checker evaluates4420 full actual local_R cones per case at all ten
future capture/reset/first-update event rows. Each includes the entire
sixteen-site width and five-holder guard across all seventeen potential
colony copies. The intervening individual shift ticks follow the exact
algebra above, rather than a simulated ring or an unproved clean boundary.
These13260 full-kernel checks supplement the universal source identities.

## 2. Retained History footprint — proved counterexample to transplanted P4

Choose the normal native-GF primary y=P, whose clean Info is I(P)=0.
For each d in -8..-1,1..8, put y_d=P-dQ. The capture above stores M
in History3 lane8+d at all five holders y_d-S[h]. No later capture
rewrites that lane, and no History reset or SF wipe occurs before U.
Thus all sixteen values are simultaneously wrong at72Q+2 and remain
retained in the rest and late pass. The exact capture clocks, lanes,
five physical holders, actual and clean words are retained in the receipt.
The entire normal-bank scan verifies this same common-row support.

In particular the raw physical cells at P-8Q and P+8Q disagree with
their clean History3 words on the common row72Q+2. Their separation is
16Q. A single interval[jQ,(j+2)Q) cannot contain both, regardless of
the choice of j. There is no current error overwrite on this row and
no real0 component to supply additional boxes.

Precisely, transplant Gray's printed Proposition4 to this rule as follows:
**P4_R** asserts that, from H, for every original-c104 level1-only error
history one may associate one box[jQ,(j+2)Q)x(kU,(k+2)U) to each real1
component and its printed site/pair box to each real0 component, so that
at **every physical site and tick outside the union**, every raw SF field
(including retained History/Workspace, Info and Mail) equals its clean
F^t(H) value. For the selected histories there is exactly one real1
component and no real0 component, so only one such box is available.
**This literal transplanted printed property P4_R is false.**
Either the box misses the common time or its spatial interval misses
at least one of the two witnesses. This is a fully specified counterexample
to that literal pointwise-SF transplant for the changed implementation.

It is not a failure of a proved GAW2R noiseless, pure-E0 or operational
real1 lemma. The first two apply to different error assumptions, and a
general real1 operational theorem has not been asserted. The decoded
result below is positive. A corrected error relation that permits
incoming carrier/capture contamination in otherwise undamaged colonies
is not refuted by these temporary stored-input differences.

## 3. Actual temporal majority and evaluation — proved

For the first two histories, History1/2 remain the exact clean B(y)
everywhere. History3 may differ, including the carrier footprint, so

    majority3(H1(y),H2(y),H3(y)) = B(y)

at every normal operand and every other logical y. The Info overwrite
in case2 occurs after the third LOAD/centre capture, and no later gather
occurs in this period. Its persistent Info therefore does not alter the
two intact banks. Mail and Info errors do not become independently
selected evaluator inputs.

In case3, directly overwritten History1/2 differ only on B. Outside B
both remain B(y), so the temporal vote is still exactly clean. Inside B
both equal A; the voted Mem is A irrespective of later replacements
of History3 lanes. Since B intersects only receiver0's normal496-word
frame, only nine normal operand words (offsets0..8) are changed. Every
normal bank in every other receiver is exactly the intact H bank. The
checker scans all17x496 actual words and retains the changed-word list
and complete-bank hash. It does not treat a false temporal vote as an
arbitrary future upper history.

The actual72Q+3 early reset loads this voted bank and clears work. The
actual72Q+4 birth runs the own native-only entry on it. Case1/2 take150
actual updates and output F1=F2=0. Case3 takes152 updates and outputs
F1=F2=1. Those are actual packet/operand executions with all high bits
present; no virtual legal-cell theorem is invoked for case3's malformed
native inputs. Complete packets, head ranges, Out/Scratch and trace hashes
are retained. All other receivers have the clean normal bank and the
corresponding clean zero flag outputs.

The actual late reset/birth at102Q/102Q+1 runs the complete own programme
from cleared Head/Out/Scratch on the same retained temporal bank. Cases1/2
take66185 updates and output the full F(H)(0) record. Case3 takes72255
updates and outputs the recorded malformed GF/flags cell. Each selected
trace remains inside the496-word frame and finishes within the actual
147455 late updates. No prepared-only runtime bound is substituted for
these selected raw-bank executions.

## 4. Actual couriers, Workspace and reset shielding — proved

Case3's nonzero early flags are delivered by the original bounded routes:
at75Q, F2 seeds P+3 and F1 seeds P+2 in receiver0. Left/right couriers
stay in[3,P+3]/[P+2,Q-3] and hold their endpoints. Travel3848/4339 updates
finishes before the80Q-1 special Info write. All other colonies seed0.
The checker repeats176 full local_R courier/source cones per history,
528 total, including first travel, first left endpoint arrival, special
Info commit and hold across the boundary guard. The special sources are
derived as Info3=F2 and Info(Q-3)=F1, not prescribed command tapes.

The later Workspace is the actual frozen computed-SimBit equation:
WF1 may read the receiver's derived right source only in96Q<=Age<98Q;
WF2 may read its derived left source in that window only where computed
F1 allows it. We do not assume WF2 remains1 for the entire window. That
dependence and the native flag propagation are the exact local recurrence,
uniquely driven by the derived sources and original history. Only the
irrelevant numerical native-flag trace is replaced by a proved bound.

Canonical GF/common Age are invariant for arbitrary flag values: either
native selector obtains the same GF/Age refinements. Thus rawGF equals
newGF and no SF wipe occurs at any stage. Mail resets to0 at96Q before
these source effects, and there is no later gather or History capture.
The actual rule keeps the recorded histories; native Flag1 can erase
Mail but cannot change those histories, Mem or normal Info. At98Q the
half-open guard makes both new Workspace fields0. The frozen actual
native zero-strip lemma then removes all F1 and F2 by99Q, for arbitrary
flags at98Q. This is a universal property of the original native
equations, not a chosen future flag trajectory. It discharges the actual
102Q late-reset geometry/quiet premises, while retaining the derived
bank and actual Info. Early work is cleared and the PC0 late birth is
genuine; no future Head or tape is inserted.

## 5. Actual U and2U boundaries — proved selected instances

At U, common computed Age0 commits voted old-Out Info and resets every
work track/History/Mail/courier, with beta and native geometry exact.
The checker evaluates506 full core-frame commit cones per case. The
normal output outside receiver0 is exactly the clean one by actual bank
identity and quietness. The emitted programme writes only normal output
primaries, so all unrepresented Info, including the earlier altered
normal neighbourhood and the nonzero special sources, is0 at commit.

Hence cases1/2 equal the complete global clean state at U, including all
auxiliary fields; deterministic equality persists afterwards. Case3
has only receiver0's bad normal record. Its GF word2^100-1 has nonzero
native padding. That padding is represented, specified zero storage,
not ignored unrepresented Info. No legal13-bit upper GF can supply it
in E(Cprime,Aprime). An arbitrary raw-cell or legal-upper period theorem
must not be silently applied to this invalid record.

For each case the checker derives the next actual17-lane bank from the
first-U output record in receiver0 and the exact clean F(H) records
elsewhere. For all17 affected next receivers -8..8 it keeps every raw
input word, then executes the real early and complete late programmes.
No GF padding is masked by the host. All51 early executions output zero
flags and all51 complete late executions take65062 updates and output
the exact F²(H) records. Each retains all seventeen source records,
packet/head limits, full outputs and execution hash.

The physical lift follows the actual three quiet gathers/reset/births:
normal captures shift by integer-Q multiples, so each reads the derived
normal record at the same residue. First-U auxiliary Info is0, the actual
next early flags are0, bounded couriers write zero special sources, and
native flags/Workspace remain quiet. The three retained next histories
therefore agree with these actual banks, and the102Q reset/birth evaluates
them without SF wipes or erasures. At2U the full old-Out commit and reset
give the complete clean global boundary, including auxiliary Info0.
Outside -8..8 the radius8 upper operands are unchanged; their physical
evaluation and controllers are the same. This selected finite lift,
including its high-bit source data, proves recovery without a universal
malformed-record decoder/kernel completion.

## Gray attribution and proof status

The primary [Gray text pp34–36](../../../../papers_txt/gray_readers_guide.txt),
lines1530–1624, specifies three separate gathers and temporal voting.
Page35 explicitly admits incorrect incoming Mailbox information in
undamaged colonies and argues that undamaged state information remains
correct after voting. The first two actual histories illustrate that
distinction: wide stored-input contamination is present, while every
decoded output and U reset is correct. The literal all-SF box wording of
Proposition4 on p36 is stronger than that restricted decoded assertion.

The already accepted
[conditional literal-stage theorem](../GRAY_LITERAL_STAGE_ENVELOPE.md)
and [GT0 raw-gather component](../GT0_RAW_GATHER.md) distinguish those
same statements. Under the explicit I/N/S/G/R premises, the earlier
theorem uses a coherent wrong ordinary primary and raw-state gather/
retention to force Workspace differences in colonies-1 and1 as well as
the wrong primary in colony0. Its mechanism-level contradiction already
uses the original five-neighbour specification; it does not require
GAW2R's extra lanes. GT0 proves raw radius5 data transport/storage only
with its stated integration ports and completion premises. Those results
retain their original conditional/component scope; GAW13 neither supplies
their missing Gray own programme/layout nor presents that conditional
observation as new. The new result here is the fully specified intact-H
three-gather whole-rule instance, including actual temporal voting,
nonzero command delivery and complete boundary recovery.

Our P4_R counterexample does **not** independently instantiate every
premise of Gray's construction. Gray gathers five neighbours per side
and uses bit fields, while this rule gathers eight per side in WORD100
lanes with an enlarged code/layout and102Q late start. His exact physical
gather/capture/refinement has not been proved equal to this implementation.
The h1 correction is inert on this pre96Q trajectory (F2=0); the later
early pass, Workspace and102Q deadline cannot cause an earlier72Q+2
stored-input discrepancy. Those causal observations do not establish the
missing transport/storage refinement. No faithful-Gray counterexample
is inferred. Gray's unpadded bit layout also avoids the specific WORD100
high-GF encoding defect, without supplying a reliability proof for either
construction.

| Claim | Status |
|---|---|
| Actual intact H, one shared original-c104 real1 row and frozen source/ROM identity | proved |
| Exact physical LOAD, copy vote, transport and all actual capture/reset identities | proved;13260 full-kernel supplements |
| Simultaneous retained History outside every fixed adjacent pair | proved for these histories |
| Literal printed P4 all-raw-SF box property transplanted to this changed rule | false by the exact retained-History witness |
| Actual temporal majority confines normal input corruption to receiver0 | proved for these histories |
| Derived early flag outputs, couriers, sources and quiet-before102Q bridge | proved; actual traces and528 source kernels |
| Complete U recovery in cases1/2 and complete2U recovery in all three | proved by actual executions/physical composition |
| Literal legal E at U in case3 | false; native GF padding outside declared alphabet |
| General16x16 SF real1 recovery, other capture times, mixed native bursts | unproved |
| General malformed-record decoder, higher map, Gray refinement, iid or shorterU | unproved |

The run log, complete payloads, source/capture traces, record checks and
standalone read-only replay are retained. No failed CA or unsupported
chosen-tape factorization is discarded. No registered file or earlier
accepted receipt is changed.
