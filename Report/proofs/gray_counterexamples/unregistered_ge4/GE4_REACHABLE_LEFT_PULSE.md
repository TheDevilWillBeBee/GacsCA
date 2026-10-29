# GE4: the first actual left command in the conditional GE1 history

This is an unregistered extension of the **conditional native-only GE1
component history**, not a new closed rule, a faithful Gray automaton or
a reliability result. Q=8192, U=128Q=1048576, lambda24 and c104 are unchanged.
No accepted source, receipt or main checkpoint is altered. The same
row0 Age-only real2 on[0,17Q), from GE0's conditionally intact recursive
initial configuration, is the only physical error. There is no independently
chosen upper history, no new error, and no prepared native input bank.

Sources are the frozen [GE1 writer](../gray_native_writeback_ge1.py),
[GE1 composition](../GE1_NATIVE_WRITEBACK_SECOND_BANK.md),
[accepted second prefix GE2](../GE2_SECOND_NATIVE_PREFIX.md),
[literal native scalar](../literal_maintenance.py),
[GT0 gather equations](../gray_raw_gather.py) and
[early physical native programme](../GE0_EARLY_NATIVE_FLAGS.md).
The new [event kernel](ge4_native_workspace_pulse.c),
[checker](check_ge4_reachable_left_pulse.py) and
[read-only replay](validate_ge4_reachable_left_pulse.py) retain the precise
inputs, compiled transitions, finite derivations and provenance.
The [new receipt](../../../../figs/gray_counterexamples/unregistered_ge4/GE4_reachable_left_pulse_certificate.json)
is not registered in the repository's main reliability ledger.

## Exact conditional result

Retain every GE1/GE2 completion premise: an own Q-bit beta with the actual
2346-bit native prefix at2929..5274, a final intact2462-bit layout, the
specified nonnative store ports, and literal final-computed-SimBit
Workspace equations composed with GT0's SimBit/wipe equations on these
prefixes. Own-beta existence, final layout and all-raw computed-source
locality are still **unproved**. GE1's native-only fifth writer remains
an explicit departure from Gray's full fifth evaluator.

Let Z_n(g) denote the actual committed native word from early evaluation n.
The frozen GE1/GE2 theorems supply Z1, Z2 and the complete second pulse.
Z1 has GF=g modQ, Age1, Flag1 on{-3,-2,-1,13..19}, and both Flag2 and
Workspace bits0. At the start of the third work period the lower native
state is quiet, with offset1 clocks on[0,23Q) and full Flag1 barriers in
colonies-1 and22. Every other native field is canonical/zero as specified
in GE2.

The same actual local equations then give:

| Early evaluation n | Actual old quiet clock interval | Derived Flag1 command colonies | Quiet interval after its late pulse |
| --- | --- | --- | --- |
| 3 | [0,23Q) | [-7,-1] union[7,25] | [0,26Q) |
| 4 | [0,26Q) | [-10,-1] union[4,28] | [0,29Q) |
| 5 | [0,29Q) | [-13,-1] union[1,31] | [0,32Q) |
| 6 | [0,32Q) | [-16,34] | **[7Q,35Q)** |

All interval endpoints in the command column are inclusive colony indices.
All native Flag2 commands are0. The Ages of Z_n are derived from the actual
erased banks; they are not assumed equal. For example Z_n(-1).Age stays1,
while the infinite far exteriors have Age n.

At physical row (n-1)U+100Q each quiet interval [LQ,RQ) in the last column
has exactly:

    GF(x)=x modQ;
    Age(x)=(physical row + 1[LQ<=x<RQ]) modU;
    Flag1=1 on[(L-1)Q,LQ) union[(R-1)Q,RQ);
    Flag2=Workspace1=Workspace2=0.

The quiet form persists through the fifth stores, commit and the next two
later gathers. In particular the sixth pulse has full barriers6 and34,
not-1 and34. Its normal native primaries commit the actual Z6 at physical
6U-1[7<=g<35]. From that single history the next actual History2/3 bank is

    B6(g,d)=Z6(g+d), if d=0 or the inclusive path g..g+d
                              meets neither6 nor34;
             all-zero native word otherwise.

The receipt derives the literal native outputs Z7 from this bank. It does
not claim a seventh late pulse, a positive Flag2 birth, or the later
h1-corrected dynamics.

The fixed-left sequence [0,(17+3n)Q) used in the earlier hypothetical
upper-bank probe is therefore false at n=6 for these actual conditional
equations. That probe's evaluation16 Flag2 prediction cannot be promoted
to reachable physical history. This is an obstruction to that proposed
recurrence, **not a refutation of a claim in Gray's paper**.

## Deriving each native bank, rather than preloading it

Suppose the previous pulse has proved a quiet offset interval[LQ,RQ),
with full predecessor Flag1 strips L-1 and R-1. GF is canonical. With
Workspace off, the exact native equations preserve this quiet form
through modulo-U wrap: at each aligned jump the left strip gets its
in-colony mismatch source; the right successor excludes that foreign
source and keeps its own directional clock. Each interior colony has
one phase. Here R-L>=28 for the sixth result, and the earlier widths
are at least23, so there is no one-colony overlap exception.

The actual old EarlyOut native copies from the early run only vote their
held values after that run. Throughout the late pulse and rest their
local Ages avoid its69Q reset/run window. Canonical GF makes the mandatory
raw-self-GF wipe false. Once the pulse is quiet, all five holders of every
native primary2865..2901 share the colony's actual phase. The GE1 service
Address equals the true logical primary, even if this phase differs from
that of the earlier run. At112Q Nextbit resets0; at112Q+1..120Q-1 it writes
the actual five-holder EarlyOut value. Later votes retain it. At local
Age0 SimBit commits **old voted Nextbit**, while Nextbit resets on that
same update. Thus Z_n commits at nU-e(g), e(g)=1[L<=g<R]. No presumed
common upper Age appears in this argument.

Next, for S=32Q or64Q, receiver g, native primary residue p and d!=0,
the actual History capture row is

    nU+S+2+|d|Q-e(g).

Its backward Mailbox route crosses the inclusive colony path g..g+d.
If that path contains a full strip, the nearest flagged coordinate
supplies a computed zero Mailbox after nU+S; no older snapshot bypasses
the erasure. If the path avoids both strips, it also avoids both clock
jumps. It has one phase and arrives at the actual source snapshot
nU+S+1-e(g+d), at the **same** primary residue p. That source is the
already committed Z_n(g+d). Self capture reads held Z_n(g) directly.
This proves the formula for the next bank. All captures finish by
nU+69Q+2; History2 and History3 are equal, and their temporal majority
therefore eliminates any arbitrary History1 bit.

The raw-holder/centre-clock GT0 factor is the one already proved in GE1:
at least three of the five holders of any logical coordinate have its
colony's phase and native flags, use identical voted inputs, and determine
its new logical vote. At each interior native primary all five agree.
It applies to the new barriers6/34 as well as the earlier barriers;
the proof uses actual colony controls, not an upper word chosen after
the fact. The checker invokes the actual GE1/GE0 capture equations at
both stages, all11 offsets, all five holders, six native field starts
and receiver classes on both sides of each actual jump. Its old-mail
fixtures are instruments of the proved route, not independent histories.

## Infinite upper state and the actual early computation

The finite state description stores exactly the deviations of Z_n from
the homogeneous native background

    GF=g modQ, Age=n, flags=Workspace=0.

Outside radius5 of an old deviation or a barrier, the next bank has
eleven actual homogeneous records. The literal native next state is the
next homogeneous background. Thus evaluating the finite union of those
radius-five sets, and retaining only deviations, defines the next state
on **every integer receiver**. No ring boundary or arbitrary exterior is
introduced. Null-record GF votes cannot create a wrong Address: every
nonnull adjusted word equals g, and null adjusted words -d are distinct.
An existing vote is g, or the native fallback is the self GF g. The
checker derives all native fields, actual noncommon Ages and every
Flag1/Flag2 source from this exact infinite description.

Each of these banks drives the unchanged real GE0 early evaluator. Its
reset and birth clear arbitrary old packets/outputs and give one head
per colony. Raw GF is still canonical, so the previously identified
raw-GF birth defect is not invoked. The head and all operand/write
footprints stay in residues2865..5274, strictly inside their colony.
Its three-history LOAD therefore sees the derived temporal majority;
the five-copy physical head lift applies with the colony's actual phase.
The emitted107 native instructions,2346 beta bits, generic register
contracts and input-independent34396-tick runtime are unchanged.
This proves native EarlyOut=Z_n for the new legal banks. The checker
also executes the emitted generic instructions on retained actual
banks, records their trace and checks every native output. It does
not substitute a host-rule instruction for that computation.

The real speed-one couriers and all-five special SimBit delivery use
the same actual flags and phase. Halt Age599648 is before seed75Q;
the last arrival619691 is before delivery80Q-1=655359. No later gather
or evaluator reinitialization occurs before the late Workspace window.
GF stays canonical throughout the subsequent pulse. In that window
computed Ages lie96Q-1..100Q+1, never0 or80Q-1. Hence coherent delivered
special copies are held by actual GT0 votes, with wipe false. Their
**final computed** SimBits on this trajectory are exactly the derived
sources. The all-raw final-source locality/whole-completion gap remains.

## Why the first three new pulses retain the left edge

For a quiet aligned interval[a,b), with a=LQ and old width at least13Q,
assume the coherent Flag1 source at the first offset colony L is0 and
Flag2 sources are0. Initially that first colony has Flag1=Workspace1=0.
If the old core stays clock1, every right clock vote inside that colony
is1. Every left **in-colony** old clock is1; foreign0 values are excluded.
All its right **in-colony** flags and Workspace inputs are0. Thus its
next Flag1 remains0, and it chooses the right1 vote. Its own Workspace
source is0. This simultaneously preserves that entire first colony.
For every other old core site, the left vote is1. Either the right vote
is1, or the site is in the final three before b, where the in-colony
mismatch source forces the left1 vote. This proves old-core clock
preservation by induction, independently of all commands in its other
colonies. The permanent left exterior remains clock0 even with arbitrary
Workspace1 forcing, as proved in the GE3 right-template certificate.

Evaluations3,4,5 have source0 in colony0. Their three newly commanded
right colonies are covered by the frozen
[GE3 local right template](../unregistered_ge3/GE3_RIGHT_TEMPLATE.md):
its old right-tail shield, uncommanded right exterior and exact three
colony computation give clock1 on the new colonies, with the new terminal
Flag1 strip. They finish clock capture at relative797352.

After computed Age reaches98Q the half-open Workspace gate is off. By
relative row98Q every Workspace1 is0. In a uniformly clocked colony,
without a mismatch or Workspace source, the Flag1 recurrence clears
from the right by at least two cells per update: its last two sites have
fewer than two in-colony right flags, then the same applies inductively
two sites farther left. After Q/2=4096 updates every such colony is0.
At a surviving aligned jump the last three predecessor cells are a
persistent mismatch source, and Flag1 fills left by three cells/tick;
the new terminal strip fills by797352+ceil(Q/3)<98Q. The old left strip
stays full. Consequently all three pulses are quiet by100Q. This proves
their whole m->m+3 shape before deriving the next actual bank; the shape
is not an assumption copied from the hypothetical probe.

At evaluation6 the derived source in colony0 is1. The preceding argument
does not apply, and the exact event calculation below supplies both
fronts instead. No fixed-left extrapolation is used beyond evaluation5.

## Exact sixth native/Workspace calculation

Canonical GF guarantees both adjusted Address votes, computed GF and
wipefalse for every old native flag value. With F2=WF2=0, the missing-GF
Flag2 source is absent and Flag2 stays0. Every clock is t or t+1 in this
late interval, with five-vote majority; the next clock has label0 or1.
The literal native factor is exactly

    L5/R5 = majority of the five left/right clock labels;
    I = number of left in-colony labels differing from R5;
    H = number of right in-colony old Flag1 values1;
    W = number of in-colony old Workspace1 values1;
    newF1 = I>=3 or H>=3 or W>=3 or(oldF1 and H>=2);
    newLabel = L5 if newF1 else R5;
    newWF1 = held_source(colony) and residue>=Q-5
             and 96Q<=newAge<98Q.

The native equation reads **old** Workspace, so this explicitly includes
the one-row source lag. Both printed and h1 predicates coincide here
because Flag2 never becomes1; no corrected positive wave is inferred.

The C kernel starts with actual quiet width32Q at relative96Q-2 and the
derived sources exactly in colonies-16..34. It updates every row to100Q.
The cut set contains each old segment endpoint shifted by each raw
offset-5..5, every colony boundary shifted by those offsets, and every
source strip start. All raw words, in-colony tests, next-label-dependent
source gates and transition outputs are constant on each resulting
interval. Updating one point per interval and merging identical adjacent
outputs therefore gives the exact infinite-line state by induction.
This is a proof by finite exhaustive event partition, not a sampled
trajectory or a noisy statistical experiment.

The represented finite domain contains the initial clock/Flag1 support
and every command colony with at least two empty guard colonies on each
side. Clock0 on the left of0 is a permanent invariant. On the right of
35Q every colony has right vote0, no in-colony mismatch/source/flags, so
stays clock0/Flag1=Workspace1=0. At the outer domain guards every input
clock is0 and any foreign flag/source is excluded. They and the entire
unrepresented exteriors remain0. Thus zero out-of-domain values are
derived from this infinite-line history, not prescribed boundary data.

The final sixth state is exactly

    clock0/flags0 below6Q;
    clock0/Flag1=1 on[6Q,7Q);
    clock1/Flag1=0 on[7Q,34Q);
    clock1/Flag1=1 on[34Q,35Q);
    clock0/flags0 above35Q;
    Workspace=Flag2=0 everywhere.

The checker separately reconstructs legal raw native inputs at both
endpoints of every retained event interval and calls the frozen actual
literal scalar. Consecutive retained rows are checked against those
computed outputs. Those cofactors supplement, rather than replace,
the all-row event-partition and infinite-exterior proofs. Compiler,
binary, all-row traces and exact final segments are pinned. The earlier
strict compilation rejected a misleading-indentation warning before any
execution; the [initial source and diagnostic](../../../../figs/gray_counterexamples/unregistered_ge4/GE4_initial_compile_failure_manifest.json)
are retained. That failure concerns our new C source, not the rule.

## Status and timing limits

| Step | Status |
| --- | --- |
| Single shared row0 real2 / conditional intact initialization | Previously proved conditional GE0/GE1/GE2 premises, reused |
| Native-only fifth writer and actual old-Nextbit commit | Proved frozen GE1 equations, reused |
| Quiet continuation and actual new History2/3 banks | Proved conditional physical routing/holder composition |
| Infinite native Z3..Z7 and noncommon Ages | Exact finite deviations plus proved homogeneous exteriors |
| Early native head/couriers on derived banks | Proved frozen universal native-prefix semantics/lift, with fresh emitted-code replays |
| Command-free first colony / whole third-through-fifth pulse shape | Proved native induction plus frozen right template |
| Sixth left erosion and new quiet form [7Q,35Q) | Proved conditional all-row exact native event partition |
| B6 from the actual sixth boundary | Proved conditional GE1 commit/gather composition |
| Seventh late pulse / later positive Flag2 / corrected h1 wave | Unproved |
| Full own beta<=Q, final K/layout, literal fifth evaluator and all-raw final-source order | Unproved; remain explicit premises |
| Whole faithful Gray theorem/counterexample, iid noise or bit-memory failure | Unproved; not claimed |

This certificate changes no stage endpoint or total U. The unchanged early
run has34396 ticks and14751 slack before75Q; its courier has35668 ticks
of delivery slack. The fifth reset112Q, writes112Q+1..120Q-1 and wrap
commit atU remain in the proof. A numerical reduction of U would change
that composition and requires a new schedule/transport/own-programme
certificate. No minimum U, shorter-U rule or complete faithful Gray
evaluation is established here.
