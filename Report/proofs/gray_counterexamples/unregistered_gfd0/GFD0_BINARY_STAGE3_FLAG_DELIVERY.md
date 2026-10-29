# GFD0: a binary stage-3 native-flag delivery refinement

GFD0 supplies a concrete **binary radius-five early procedure** for Gray's
special stage-3 Flag1/Flag2 delivery. It reads the actual three retained
gather banks, collects their raw native bits, evaluates the printed native
Boolean function, and forwards the resulting two bits to the two special
SimBit groups. There is no early-result oracle, Word100 representation,
instruction dictionary, assigned future command tape, or evaluation of a
whole-rule transition as a primitive.

This is a component refinement under the premises below, **not a complete
faithful Gray automaton**. In particular its hardwired finite Boolean
operation has not been described by a full own programme beta of at most Q
bits. Correct ProgrammeBits, hardwirer, final layout, fifth-stage interpreter,
all-raw computed-SimBit/Workspace composition, and continuing-noise refinement
remain open. No error counterexample or shorter period is claimed.

Q=8192, U=128Q=1048576, lambda=24 and the original integer c=104 are retained.
No existing rule, programme, accepted artifact, CURRENT or report is changed.
New files are the [component](gray_binary_flag_delivery.py),
[checker](check_gfd0_binary_flag_delivery.py),
[read-only validator](validate_gfd0_binary_flag_delivery.py), and
[receipt](../../../../figs/gray_counterexamples/unregistered_gfd0/GFD0_binary_stage3_certificate.json).
The receipt separates symbolic identities from finite numerical backend checks.

## Exact published contract and the proposed refinement

The primary source is Gray's [reader's guide](../../../../papers_txt/gray_readers_guide.txt),
pp31–35 and41–42. Text lines1401–1449 describe the programme-size dependence,
hardwirer and projected ProgramBit convention; lines1474–1494 prescribe
Mailbox erasure, the mandatory native-dependent simulation wipe and five-copy
SimBit voting; lines1525–1578 prescribe the stages and early special flags.
In particular p35 requires delivery “Before the active part of the third
stage is completed.” The target is the **computed** upper Flag2, rather
than raw upper Flag2, old lower SimBit, or the result of the later fifth pass.
The p41 Workspace2 equation reads the final computed special primary during
the interval96Q<=computed Age<98Q. It also requires zero computed reader
Flag1. A further update reads those Workspace2 bits into the native Flag2
birth clause.

Gray does not give a complete transition table for the early procedure or
say precisely which three-bank combination it uses. GFD0 explicitly chooses
an **early bitwise temporal majority** of the three retained banks. The
described fifth-stage vote still occurs at its original GT0 time; the early
vote does not overwrite any History bank. This choice implements an implicit
part of the stage contract; it is not attributed to a uniquely printed
early-vote equation. The packing fields and numerical within-stage times
below are also concrete implementation choices.

The native early output is the exact printed rule on pp20–22, including
its separately documented healthy Flag2-erasure defect. A separate native
graph compares the explicit h1 correction. When the raw central upper
Flag2 is0, both graphs are identically equal, since that erasure branch
is not selected. This supplies a first-positive-Flag2 refinement for
either reading. It supplies no corrected positive-wave dynamics.

## Statement proved for the component

Let each colony occupy[gQ,(g+1)Q). At the physical level suppose that:

1. Native Address is x modQ, Age is the common legal clock t modU,
   all physical native flags are0, and the Workspace flags stay0 before96Q.
   There are no physical errors during the certified prefix. At row0 the
   three History banks and the new packing/courier fields are0.
2. The five SimBit copies are coherent and the represented primary bits
   are stable through the three gathers. The native upper fields use the
   37 interior positions P..P+36, in the schema below. All raw native
   input words have their legal bit widths; their values, mutual coherence,
   upper clocks and upper flags are otherwise unrestricted.
3. The three gathers use frozen GT0's **actual** Mailbox/History equations,
   including computed-Flag1 Mailbox erasure and the p33 holder wipe. The
   GFD0 fields use the emitted equations here. Fifth-store and late
   Workspace ports are arbitrary but gated off during the early prefix.

More generally, the flag evaluation conclusion applies to any coherent
retained banks with those physical controls; they need not be equal. Let
C_g[j] be the raw37-bit native record obtained by bitwise majority of the
three banks of receiver g, at offset j=-5..5.

**Component theorem.** At row80Q-1, all five lower copies of the special
SimBit at gQ+3 equal printed-native-F2(C_g), and all five at(g+1)Q-3 equal
printed-native-F1(C_g). Their normal represented-state positions are
untouched. No receiver imports another receiver's early flag. From80Q
through the first relevant Workspace update, if the canonical native
controls and no-wipe premises continue and no age-wrap commit intervenes,
the final computed special primary equals the delivered flag.

This theorem quantifies every raw407-bit collected native input, not
only canonical or common-Age upper records. It is conditional on quiet,
coherent **lower execution**, not on quiet or coherent upper input.
There is no own-programme, global period, recursive intact noisy-history,
continuing E0, real1/real2 recovery, or iid conclusion.

## Actual state, transitions and locality

The component retains GT0's37 native bits and240 five-copy data bits:
SimBit, both Mailboxes, the three11-lane History banks, the11-lane Voted
bank and Nextbit. It adds a407-bit logical Pack and two logical couriers,
each with five physical copies. Thus the tracked frame count is

    K_component=37+240+5*(407+2)=2322; 2*K_component=4644<=8192.

This count includes every tracked data/control field. It is not a final
K after adding a full self-interpreter or ProgramBit machinery. Its
centred preliminary layout starts at P=2935 and ends at5256. The native
37 primaries occupy2935..2971; the collector R is2971. All represented
primaries and their backups are interior. Positions0,3 andQ-3 are unused
by this represented frame. Recentring after adding further state needs
a fresh layout and courier proof; the current count cannot justify that
unperformed integration.

For copy s at holder x, the logical coordinate is y=x+s. Every logical
source value is the majority of its five old physical holders y-h,
h in{0,-2,-1,1,2}. The source's service phase is(computed Address(x)+s)
modQ. No source site's computed Address is evaluated as a second native
transition. A shift reads y-1 ory+1, and therefore needs holder offsets
s+/-1-h in[-5,5]. Stationary votes need[-4,4]. The native Flag1/Flag2
circuit reads407 bits **already stored at the current logical source**,
not407 separate physical cells. It therefore does not enlarge the range.
The current holder's actual native computation and wipe use[-5,5]. All
data inputs of the emitted graph are checked against this bound.

The complete new data equations are defined on arbitrary raw copies,
not only coherent states. Stage starts reset Pack/couriers. At computed
Age69Q+3, the logical primary with phase P+k seeds Pack bit11k+lane from
the temporal majority of the actual three History bits at that primary.
Every other Pack bit is0. During the next36 updates, Pack moves one
site right within[P,R), and the collector R ORs incoming bits with its
old Pack. Other positions are0. Pack then retains its voted value until
a stage-start reset. Mandatory holder wipe overrides all these outputs.

At computed Age69Q+40, only logical phase R seeds the two couriers.
It feeds its **old voted Pack** into the emitted finite native Boolean
graph; the left courier gets computed F2 and the right gets computed F1.
There are no F1/F2 result ports. The graph consists only of ordinary finite
bit gates and the same published native comparisons, quorums, increment,
inside-colony and flag predicates. It does not fetch an immutable
instruction or invoke a host/native/whole-rule evaluator during a CA update.
The Python scalar native evaluator is used solely as an independent check
of the emitted circuit's finite test inputs.

After that row the left courier moves at speed one within[3,R] and holds
by OR at3. The right courier moves within[R,Q-3] and holds by OR atQ-3.
Every output outside the corresponding interval is0 during forwarding.
These explicit guards are the concrete implementation that prevents the
endpoint-hold-only neighbour-lineage defect of the earlier changed word
variant. They are not separately printed guards in Gray. At row80Q-1,
each special SimBit holder reads the five-copy vote of its **own logical
target courier**. There is no substitution of a head-centre coordinate
or a shared uncomputed programme answer. Other SimBit and GT0 fields
retain their frozen equations. At a stage start, the original reset rules
still retain necessary older History banks and clear the transient fields.

The emitted internal-native prefix includes the literal native transition
and raw-self-Address wipe; late Workspace outputs are named ports clock
restricted to96Q..98Q and masked by the wipe. They are not a supplied
early command. The five fifth-stage write pairs remain GT0 ports. This
is a finite transducer with late integration interfaces, not a total own CA.

## Why the computation and physical timeline are correct

GT0's first/second/third raw snapshots occur at S+1, S=0,32Q,64Q.
For offset j!=0, its actual capture row is S+2+|j|Q, reading the old
Mailbox after |j|Q speed-one shifts. The native bit at receiver position
gQ+P+k therefore comes from the native bit of receiver g+j; it has no
destination skew. The last third capture is69Q+2. The next row's Pack
seed reads these completed old records, rather than a not-yet-captured
new value.

For each Pack bit b=11k+lane there is exactly one origin P+k per colony.
After d shifts it is at P+k+d, until it reaches R after36-k shifts;
thereafter it is retained at R. Bits from separate k occupy separate
indices. OR-hold combines no two independent values of the same index.
The lower bound P and upper bound R stop all crossing between colonies.
At row69Q+39 all407 bits at R are precisely C_g's raw native bits and
every other Pack position is0. At the next row the native graph evaluates
this old word. The input decomposition is field-bit-major, then lane:
Address13, Age20, Flag1, Flag2, Workspace1, Workspace2; lanes-5..5.
It is injective and preserves the full native words. Native whole-word
majorities are never replaced by bitwise majority of the five **native
neighbour words**. The bitwise votes here concern physical backups or
the three temporal banks, as Gray prescribes.

The native circuit's Flag1 is the printed inconsistency/source/right-front
predicate. Its Flag2 uses the two left-front predicates, missing-colony
source at computed Age divisible by16, incoming Workspace2 quorum, and
the printed old-Flag2 keep branch. All inputs have their exact legal
widths, so additions/Address adjustment use mod8192 and Age increment
uses mod1048576. This is the same finite native function as the previously
proved native transcription. Both emitted graphs share Flag1; with old
central F2=0 their Flag2 outputs are structurally identical Boolean nodes.

Let E=69Q+40=565288. Courier first arrivals are E+(R-3)=568256
and E+(Q-3-R)=570506. Both precede delivery655359=80Q-1.
The remainder of the third active stage is ample slack; U has not been
shortened and none of Gray's stage endpoints or rests is moved. A tagged
symbolic forwarding induction proves that the endpoint in colony g contains
only g's flag, at every later forwarding row. The preceding zero gap
prevents any adjacent colony's signal from accumulating at its hold site.
Thus zero flags as well as positive flags are delivered correctly.

For coherent lower copies, each vote reduces to its logical source.
Every output holder of a logical copy uses the same canonical service
phase, common clock, bank and native circuit. The same word is therefore
reconstructed at all five holders, including the two backups on either
side of a special primary. This proves the physical lift of the logical
packing/courier induction. With canonical lower geometry, common clock,
zero native/Workspace flags and no errors, the printed native equations
give canonical computed Address, incremented Age and zero flags before
the pulse. The raw-self wipe is consequently absent, independently of
the gathered **upper** native values.

During third rest[80Q,96Q), all coherent tracked SF fields vote to their
unchanged values. At96Q the transient courier/Pack reset does not reset
the stored special SimBits. In this continuing quiet setting the ordinary
SimBit update holds those bits, has no wipe and has no Age0 commit.
Consequently its final computed primary equals the delivered flag at
the first Workspace read. This is a conditional equality at a quiet
pulse source, not a resolution of GI0's arbitrary-raw-state radius-eight
obstruction. If the computed reader controls meet Gray p41, a delivered
F2=1 seeds the five Workspace2 sites on that update and native Flag2 on
the next. Subsequent waves, source survival under damage and own-rule
continuation are outside the component theorem.

## Programme, order and reliability obligations that remain

The large hardwired gate graph is part of a finite local rule, rather
than counted as a beta string in a ProgrammeBit tape. The fact that such
a circuit has one CA tick of evaluation time **does not show** that a
physical own interpreter can describe and simulate it in eightQ ticks or
with8192 ProgrammeBits. No code-size bound is inferred from hardware
gate count, and no uncounted immutable instruction dictionary is introduced.
Gray's p31 sufficiently-large-Q argument gives unspecified constants;
it is not a numerical fit certificate for this added hardware atQ8192.

The projected ProgramBit convention and the p31 hardwirer still need
their full implementation. This preliminary centred native layout also
does not silently replace Gray's illustrative raw Address SimBit accesses
at positions1..13. A complete compatible layout/hardwirer must explicitly
reconcile those accesses, or declare a changed representation. GFD0
does not claim that correct beta or a final recursive own encoding exists.

The order is exact: old retained bank -> old collector word -> computed
upper flags -> moving couriers -> old endpoint votes at special write ->
held final primary at the later quiet Workspace read. In particular the
late fifth interpreter is not used for an early command. At arbitrary
damaged source clocks/wipes, final computed SimBit can differ from current
or pre-wipe SimBit; GI0's stipulated all-raw obstruction remains intact.
No voted-current shortcut is applied here. Full radius-five completion
of that source interface is still unproved; this component theorem only
uses equality when the source is proved quiet.

This procedure eliminates the GAW2R Word100/17-lane/radius8/dictionary
dependencies for this **early native flag operation**. It does not eliminate
them for GAW2R's whole rule or reinterpret GAW28's orbit as a Gray trajectory.
The early temporal vote, Pack organization, clock69Q+40 and confined
courier guards are explicit choices within the implicit stage procedure.
There is no claim that Gray printed those exact transitions.

| Step | Status |
| --- | --- |
| Printed target, stage windows, mandatory masks and copy convention | Primary specification identified |
| Actual eleven-lane three-gather coordinate/retention identities | Frozen GT0 proof applies to its stated quiet-control premises |
| All407-bit native-bank decomposition and printed early flag circuit | Proved finite equations and transcription |
| Printed/h1 equality for old upper central F2zero | Proved exact symbolic circuit identity |
| Radius-five data circuit and physical copy lift | Proved |
| Packing, speed-one lineage, delivery and third rest deadlines | Proved under stated lower execution premises |
| Final computed source equals installed flag at first quiet pulse | Proved conditionally; arbitrary damaged-source equality unproved |
| Full own beta<=Q, compatible ProgramBit/finalK and fifth deadline | Unproved |
| Continuing E0, real1/higher native repair and multilevel error map | Unproved |
| Faithful complete Gray automaton, theorem refutation or iid threshold | Unproved; no such claim |
| Any shorter U | Unproved; baseline unchanged |

The retained numeric raw-bank and C comparisons are **measured checks**,
not substitutes for the routing, dependency or copy proofs. The clock/
Address category audit includes all lower20-bit clock words and all8192
phases; the symbolic equality checks leave every relevant data bit and
wipe/Flag1 control free. Single-row two-holder majority cofactors are a
conditional algebraic check, not a continuing E0 proof for this component.

The first checker included the endpoint U as though it were a20-bit input
clock. Encoding that integer wraps it to0, while its independent scalar
test used the unencoded integer, so the symbolic assertion failed. The
failed checker source and complete log are retained. The corrected test
uses0<=Age<U and checks the exclusive endpoint only as a partition bound.
A second run stopped on an incorrectly named independent h1 scalar helper.
Its source and log are also retained. Both were checker/interface mistakes;
the emitted component equations and mathematical schedule did not change.
