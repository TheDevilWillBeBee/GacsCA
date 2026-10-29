# GAW20: all-phase single raw-record repair for unchanged GAW2R

This is a conditional padding-congruence theorem and a global prepared
repair theorem for the **changed GAW2R rule**, followed by an all-time
intact-shadow corollary. It finds no counterexample to that extension.
Q8192/U128Q=1,048,576/lambda24/c104 and the frozen rule/ROM are unchanged.
Neither a generic malformed-record compiler quotient nor a Gray/iid
reliability theorem is asserted.

## Exact prepared theorem

Let R be frozen GAW2R with its complete immutable emitted ROM. Let C be
any legal infinite upper configuration satisfying:

1. C(x).GF=x modQ and C(x).Age=theta, for a common theta in[0,U).
2. All C's native F1/F2/WF1/WF2 are0.
3. Every five-holder SF logical group is coherent. This means that for
   every logical position y and each SF track, all five physical holders
   y-s, s in(0,-2,-1,1,2), contain the same logical value. It includes
   packed Head, all17 Mem/History words, Programme, Info, Out, Scratch,
   Mail and couriers. Their values may otherwise be arbitrary legal raw
   Word100 values, with arbitrary legal raw packet metadata.

Choose **any integer a** and **any w in Word100^496**. Replace just the
496-word record C(a) by w in the data array W. No native legality,
packet validity or internal holder coherence is imposed on w, and all
49,600 bits remain in the actual lower Info/banks. Encode W at normal
primaries gQ+3848+i, with zero unused Info, canonical/reset lower native
fields, reset work and the actual hardwired Programme. Call this legal
lower configuration E_raw(W,0); its represented native padding lies in
Word100 Info, not in the lower cells' native fields.

**Theorem. R^U(E_raw(W,0))=E(R(C),0).**

This is equality of all raw lower fields on the infinite line. The final
record is legal, all unused Info is0, and all work/native/Programme fields
have their literal reset values. No future error or supplied command
tape occurs during the period. Lower reset/coherence is an initialization
premise, separate from the arbitrary raw upper words. This is not a
repair theorem for arbitrary damaged lower work or geometry.

## A proof-only comparison, not an applied mask

Define pi(w) by masking only its six native words to widths13,20,1,1,1,1.
Leave all490 SF words exactly unchanged. Let C_pi be the legal upper
configuration equal to C except for record a=pi(w). This is a **comparison
object**: the actual E_raw(W,0), actual gathers and actual emitted
execution never mask those six words.

We prove two separate identities:

`emitted_beta(W[g-8..g+8]) = emitted_beta(C_pi[g-8..g+8])`

for every full emitted Out record and its execution/control deadline,
and

`R(C_pi)=R(C)`.

Only after proving the first identity do we apply the frozen legal-input
compiler theorem to C_pi. We do not apply it to W. The two statements
are specific to the canonical/coherent/zero-flag family above. Root's
[J246 padding obstructions](../unregistered_gaw_padding_quotient/PADDING_QUOTIENT_OBSTRUCTION.md)
remain valid outside those hypotheses.

## Literal native and SF absorption

Each adjusted native GF side and each native Age side has at least four
clean votes, regardless of a, theta and w. GF adjustments are modulo13
bits. The clean GF quorum therefore returns x modQ on both sides. The
clean Age quorum returns theta on both sides. At most one term in any
left mismatch test is wrong, which cannot meet its threshold3. All flag
and Workspace masks have at most one bad bit: neither source nor
propagation quorum can turn F1 on, including the old-self/right2 clause.
For F2, sources/quorums are absent; the h1 erase condition clears any
isolated old F2 because the left in-colony count is<=1 and computedF1=0.
Hence every native recipe returns correct GF, Age(theta+1)modU, F1=F2=0.
The raw-GF SF wipe is consequently false even at the malformed record.

This assertion concerns computed F1/F2, not final computed Workspace.
Arbitrary coherent C may contain special Info whose bit0 produces a
positive new WF1 or WF2 during its upper source window. Those computed
Workspace outputs are proved equal to R(C) below; they are not assumed
zero. The lower physical period's zero repair commands come from the
separately derived early F1/F2 outputs, not these upper WF outputs.

This argument applies at the central recipe and every computed-primary
source recipe used by Workspace. Their five-word sides are physical
subsets of the same one-bad-record history, not independently selected
neighborhoods. There are no no-quorum fallback cases.

Each SF logical group has at most one holder replaced by C_pi(a). Its
other four holders are the coherent C group. Bitwise3/5 therefore returns
exactly C's logical value, on every bit and on every track. Native
geometry/clock and computedF1 are the same as C's clean update. Every SF
equation in R uses these voted words, that logical service Address and
the common computed clock. Thus reset, capture, temporal vote, incoming
Head, virtual instruction/IO, courier and commit calculations equal
those in R(C). This includes invalid but legal Word100 metadata in C.

Workspace reads final computed-primary Info. At each source the same
native absorption gives F1=0, so no raw-GF wipe applies. Its old voted
Info/Out/courier word is restored by the four clean holders. Source Age
and service Address agree with C, so the final Info equation also agrees.
Therefore its bit0 and computedWF agree. This proves **R(C_pi)=R(C)** on
the full infinite line, rather than only at normal encoded primaries.

## Exact emitted padding congruence

[check_gaw20_padding_congruence02.py](check_gaw20_padding_congruence02.py)
checks actual decoded words of the frozen ROM, including operand-width
masking. It proves the following complete accounting of padding uses.

The seven central/source native recipes have exactly the same normalized
arithmetic. Their source offsets fit the actual17-lane bank. In a GF
READ5, high bits13..19 may differ before VADDINDEX, but the literal width13
mask after addition discards them. The step's low13 bits are the printed
plus/minus1 adjustment; this includes the encoded20-bit immediate for
-1. Age READ5 discards every bit>=20. READMASK/FULLCOL extract bit0 only,
so high flag padding disappears. Raw default GF/Age are full100-bit
loads, but occur solely as VMAJ fallback operands inside native arithmetic.
The four-clean quorums just proved make every one of those28 fallbacks
unused. Thus all native arithmetic/control results agree with the
explicit projection, except the still-retained raw-default registers
R12/R13, whose differences are accounted for below.

Every other full raw-native GF read is a guard comparing raw GF with
computed GF. There are exactly eight sites: central Workspace, central
main wipe and the six post-source-native guards. Each NE result is ANDed
with the corresponding computedF1=0 **before any branch or observable
write**. The result is0 on both executions. Source R12 is then overwritten
by its literal source-lane index; main overwrites R12 by logical Address
and R13 by its baseline-loop counter0 before body entry.

The checker performs a paired prefix exploration over actual opcodes.
Its abstract register T(value,equal) states whether the two concrete
executions agree, and optionally fixes their common constant. A full
raw-default load may be unequal. Deterministic ALU on equal used operands
stays equal; an AND with a known0 returns the same0 even if its other
operand differs. All other unresolved differences remain unequal.
Branches on unequal conditions, addresses/lanes on unequal registers,
or unequal observable Out/Scratch writes fail the proof. Equal unknown
branches fork **both** edges, so no phase/payload value is chosen.

Native blocks use the checked primitive congruence just established.
They return equal native outputs and retain only the dead R12/R13
differences. SF helper calls use the frozen exact86-instruction
three-of-five contract: all its SF operands are unchanged by pi, and
its preserved registers include the dead R13. Its loop/control, actual
operand targets, return and paired side effects consequently agree.
The helper call's typed field is checked>=6, with all five input words
inside the frame. This is a same-input helper contract, not a whole-rule
evaluation primitive.

The2139-state prefix exploration reaches51 body-entry states, with all
registers, Out and Scratch equal. No native-padding difference is live
as a controller there. Its phase branches include the zero/wrap,
special-Info, source-window and all other cases; this is a finite control
proof with phase-independent values, **not phase samples**. Every actual
full-pass raw LDX site is enumerated: fourteen defaults, eight GF guards,
and one SF helper site. After body entry, only the helper can read old
raw input, and the frozen compiler's typed contract confines its fields
to the unchanged490 SF words. All later instruction/data/control inputs
are therefore identical, including virtual mutable Programme and
packet/IO data. Induction proves identical remaining PC, pending travel,
operand lanes/targets and Out/Scratch observations.

This is an observational congruence; it does not claim the complete
temporary own Head-register or native-bank contents match pi. The dead
raw-default registers can differ during the early native-only pass,
and the actual readonly bank retains all padding throughout the period.
Those differences are neither supplied as controls nor observed by the
remaining SF body. They are cleared by the actual resets/boundary.

The appended early native pass is the same native prefix after branch
relocation, with HLT replacing its final jump to Workspace. Its output
and complete PC/operand-travel trace also agree with the legal comparison.
The initial checker accidentally compared that intentional HLT to the
central jump; the failed source/log are retained. Correcting the checker
did not change any emitted word. The subsequent actual-decoder check
passes against the byte-identical mathematical receipt.
The separate final02 receipt adds literal register-width13 checks, all
3726 actual instruction decodes, and both raw early input sites; the
earlier mathematical receipt and checker are retained unchanged.

The frozen legal-input emitted theorem now applies **only to C_pi**.
It supplies Out=words(R(C_pi)(g)), in-frame travel, and the universal
late bound141557. Congruence transfers those statements to the actual
unmasked emission. With the absorption lemma, its output is R(C)(g).
The late physical window has147455 updates after birth, leaving5898
slack. The early bound is213<24571, and its native F1/F2 seeds are0.
No numerically guessed schedule or shorter U is used.

## Actual global physical period

The physical argument uses actual W, never the comparison's projected
bank. Canonical lower GF/common clock make both native refinements equal
and every wipe false. Initially lower flags/Workspace are0. Guards are
closed before96Q, so native flags remain0 through the three gathers and
the early evaluator.

For each stage start0/32Q/64Q, the literal Mail reset, Info LOAD and
one-site shifts yield a captured source D(y+dQ) at the actual lane tick
s+1 for d=0 or s+2+|d|Q otherwise. These identities hold on all100 bits of
every malformed word. All three actual banks finish by72Q+2 and agree.
Their bitwise temporal majority loads the actual B at72Q+3 and102Q+1;
the later96Q Mail/Mem reset does not reset the held History banks.

Actual early reset/birth gives a coherent five-copy physical head and
the actual early entry. The congruence/native-output proof gives F1/F2
seed0 in every colony, including all banks containing W(a). Consequently
the literal75Q seed, route-gated couriers and80Q-1 special write produce0.
Both computed-primary Workspace sources are0 during96Q<=Age<98Q; the
half-open guards close at98Q. Thus native flags/Workspace remain0 for the
whole actual period. These are derived commands, not a selected tape.

At102Q reset and102Q+1 birth, Mem is reconstructed from those actual held
raw histories. At every coherent logical lower group, voting returns its
one packet/data value at all five holders. Holder-computed Address is
the logical Address; incoming routes the unique old one-site movement;
the literal step_packet receives the same bank, separate Out/Scratch,
Programme and clock. This gives the physical copy identity for arbitrary
coherent values, including unmasked representation padding. The exact
congruent legal execution has all targets in[3848,4343], so its holders
stay strictly inside the colony and independent heads cannot interact.
Induction lifts each complete emitted execution to this physical history.

Only receivers g with |g-a|<=8 have W(a) in their17-source bank. Exterior
banks are legal C banks and use the frozen legal theorem. Uncaptured
Mail may carry differences farther but is not read by late heads or
couriers; no finite ring/boundary assumption is used. All outputs are
R(C) by the same absorption/congruence reasoning. Out outside the normal
frame remains0 by global reset and typed target bounds. Outputs halt
before120Q and then hold. At Age0, old Out is committed into Info before
all work resets. This gives the claimed complete raw E(R(C),0), including
zero unused Info, reset histories/Mail/Head/Scratch/couriers and the
hardwired Programme. Current errors at this boundary are not permitted
by this noiseless theorem.

## Every later intact background satisfies the premises

Use the frozen explicit H and H in E(H,0) from
[GAW4](../unregistered_gaw4/check_gaw4_real1_mail.py), and the frozen legal
global period theorem from
[GAW2](../unregistered_gaw2/GAW2_THREE_GATHER_PERIOD.md). Put C_n=R^n(H).
Then for every n>=0, **C_n is canonical/common-clock, has all native flags
and Workspace0, and has coherent SF groups**. Here n is physical ticks
of that same fixed rule, not an independently chosen upper history.

Canonical GF/common Age=n modU hold at every tick independently of flags
and work: both native candidates are the same correct GF/Age, so either
selector yields them. The raw GF wipe is always false.

To prove all flags/Workspace0 without assuming that result circularly,
suppose tau is the first positive native flag or Workspace time anywhere
on the infinite line. Time is well ordered, so a nonempty set of such
times has a minimum even though there are infinitely many sites. A new
native F1/F2 cannot be the first: correct geometry/common clocks remove
inconsistency sources, and all old flags/Workspace were0. Hence the
first must be Workspace during a96Q..98Q window. Let q=floor(tau/U).

The noiseless legal period theorem, iterated from H in E(H,0), gives the
actual earlier boundary `R^(qU)(H)=E(C_q,0)` independently of any claimed
global zero flags. Since every earlier row before tau has zero flags,
the actual three gather/early-copy equations in this period apply. The
early native pass computes the flags of R(C_q)=C_(q+1). But **q+1<tau**:
the first possible source row is at least96Q, and U>1. By minimality,
those actual earlier-time flags are0 at every site. Thus the actual
courier seeds and80Q-1 special writes in this period are0. The unused
special Info was0 at its actual boundary; it remains0 until the source
window. Computed-primary Info at tau is therefore0, contradicting a
first positive Workspace. No such tau exists.

Finally H's SF groups start coherent. With common native clock/Address,
zero computedF1 and no wipe, each holder of logical y applies the same
logical vote, reset/capture/IO/courier equation at Address ymodQ. Thus all
five new holders agree. Induction proves SF coherence at every physical
time, for every track. No assumption of head validity or a finite line
is needed for this coherence identity.

Applying the prepared theorem with C=C_n proves, **for all n>=0, all
record locations a and all496-word raw replacements w**,

`R^U(E_raw(W_n,a,w,0))=E(C_(n+1),0)`.

If the prepared state is realized at physical time nU of the intact H
trajectory, full shadow equality holds at(n+1)U and every later clean
row. This extends GAW19's exact n=1/a=0 scope; its frozen evidence and
the historical GAW17 null statements remain unchanged.

## Realizability, status and limits

Every prepared member has a direct finite intact-start realization:
run H cleanly to nU and replace only the lower cells whose Info slots
actually change when normal record a is set to w. Retain all other
fields. The support lies in the500-site one-row holder interval around
aQ+3848..aQ+4343. Omit unchanged replacements, rather than count them as
errors. Its original class depends on the actual changed subset; **no
uniform real1/real2 classification is asserted here**. No selected future
tape or supplied Workspace is used. The already proved GAW19 all-M n=1
member remains an exact original-c104 real2 instance of this larger family.

- **Proved:** explicit conditional native-padding execution congruence;
  literal single-holder absorption; phase-parametric canonical/coherent
  prepared period with141557/213 deadlines and full raw boundary; all
  actual C_n satisfy the premises by the minimal-first-command argument.
- **Exact finite contract replay:** decoded seven native blocks, all23
  full-pass raw input sites,2139 paired prefix states and51 body cuts.
  The induction/conditional quorum and frozen helper/full-body contracts
  give the universal meaning. This is not an observed maximum over phases.
- **Unproved:** repair of arbitrary lower work/geometry faults, arbitrary
  multiple records, all original real1/real2/higher errors, continued
  random errors, positive iid rate and remembered bit.

The first J246 example has computedF1=1, so its padding guard cannot
cancel. The second lacks native quorums, so its raw fallback is used.
Neither meets this theorem's premises; their failures are preserved.
No unqualified native-padding quotient is introduced.

[The native category checker](check_gaw20_native_absorption.py) partitions
every in-colony boundary predicate, all sixteen single-record flag/WF
payloads, and GF/Age equality versus inequality. The four-clean-quorum
argument covers arbitrary numeric GF/Age values; its two concrete Age
endpoints check increment and wrap, not a sample-based phase theorem.
It separately checks a canonical/coherent input with Info1 and source
Age96Q-1 whose new F1/F2 are0 but whose new WF1 is1. This pins the distinction
between native repair-flag absorption and final Workspace equality.

All Gray departures remain: radius8/17 lanes, WORD100/FULLCOL, h1 erasure,
holder-computed controls, immutable code/dictionary, native-only early
pass, guarded couriers and102Q late reset/birth. Direct beta41162bits and
1049 dictionary entries, with270349 total immutable bits, do not fit
Gray's Q-bit programme/layout. No Gray-refutation or shortened-U claim
follows. This prepared-family contraction still leaves the actual
damaged-history/high-error proof of the changed rule open.

## Standalone replay and dependencies

[validate_gaw20_all_phase02.py](validate_gaw20_all_phase02.py) verifies the
frozen GAW19 manifest and every inherited source/receipt hash, then checks
the exact rebuilt ROM/dictionary and all3726 decoded instructions. It
replays both GAW20 contract certificates, the frozen seven-instance
native and86-instruction helper/body/data/courier structural contracts,
and all72 classes of the literal bounded cost DAG. Those classes are an
exact EQ/LT control partition; no upper payload or clock samples replace
the symbolic branch proof. It also rechecks the actual gather/source
coordinates, corrected couriers, native quiet recurrence and H's
terminating all-field self-encoding identities.

The inherited GAW2 legal period proof and receipt are explicitly pinned:
they provide the earlier `R^(qU)H=E(C_q,0)` identities used in the
first-positive-time argument. The replay does not substitute a separately
chosen upper history or demand that the earlier C_q already be proved
coherent. GAW20's induction proves that additional coherence/zero-flag
property. GAW19's historical exact-background and failure snapshots stay
unchanged; this new result supplies the broader written phase theorem.

The new manifest pins the proof, sources, both initial-checker snapshots,
the failed HLT-comparison log, successful decoder/final-contract logs,
native-category receipt, exact frozen main/active-rule ancestry and the
separate failure provenance. A final replay has no write path and checks
the same hashes again after it finishes. It never runs an emitter in
issue mode or rewrites any accepted ancestor receipt.

The initial manifest issuer ran while its stdout log was still being
written, so it pinned that log's initially empty hash. The first read-only
replay stopped at that provenance check before any mathematical replay.
The original issuer/manifest/log/replay are retained. The separately
named02 issuer pins the completed failed log and is run without a live
redirected log inside its scanned directory. This correction changes no
rule, ROM, mathematical receipt or accepted ancestor.
