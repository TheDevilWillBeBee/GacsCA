# Local signal capture and physical flag initiation

This is a new candidate-rule component, **not a completed self-simulation
revision**. The frozen early-program rule and its two-period evidence remain
unchanged. The signal candidate has a complete local transition description,
but no compiled self-simulation ROM, projected rule or macrostep executor yet.

## Source choices and finite locality

Gray p.33 replaces five copies of each SimBit by their majority every tick.
Page 35 reserves the primary bits at computed Addresses 3 and Q−3 for computed
upper Flag2 and Flag1, also updating their four secondary copies before stage
three ends. Pages 41–42 generate Wf from those bits, computed Address/Age, and
(for Wf2) computed Flag1. See the supplied `papers_txt/gray_readers_guide.txt`.
The earlier specialized self-simulation construction remains based on pp.31–32
and Gács §§9.2–9.3; no general user-program platform is required.

`signal_rule.py` appends one five-bit Signal word to the complete clock rule:
788 raw bits / 32 words, radius five, the same Q=8,388,608 and U=128Q. Slot d+2
at a holder x represents the primary bit at x+d, for d=−2…2. Voting a primary
bit at x+j reads holders x+j−2…x+j+2. Updating all five local slots therefore
needs radius four. Wf2's furthest target offset is +3, so its vote needs radius
five; Wf1's target offsets are −2…2. No global access or recursive transition
call supplies the target bit.

At **computed Age 79Q**, the local Data low bit replaces each Signal slot whose
computed logical Address is 3 or Q−3. This is a proposed fixed capture time,
not a certified delivery deadline. It uses computed Address even if the old
Address was wrong. Voting continues in rest periods, consistent with p.33;
correctly replicated signals remain unchanged. Stage-four workspace reset does
not erase these reserved SimBits. Computed Flag1 plus an Address change clears
Signal and Wf with the source's final erasure priority.

Wf is generated during computed Ages [96Q,98Q), with the source boundary masks
and the Wf2 computed-Flag1 condition. It can be generated at the stage-four reset
because it is the output of the current local signal computation. Old physical
Wf then drives the printed maintenance equations on the next tick. Printed
Flag2 behavior is preserved, including its persistence counterexample.

## D10: a distinguishing radius witness

The implemented candidate reads the **majority of old signal copies, before
remote structural erasure**. This choice agrees with the remote updated primary
signal on canonical geometry during the Wf window: capture is over, the vote is
the signal update, and Address does not change. It does not settle the phrase
“computed SimBit” on damaged geometry.

The test constructs two configurations identical at center offsets −5…5. Both
have the target primary at +3 stored in its five copies. Changing only the
Addresses at +6,+7,+8 changes the target's right Address vote; its Address repairs
from 3 to 4 while computed Flag1 is one, clearing its updated signal. The two
center outputs are necessarily identical under a radius-five rule, but the
remote post-transition primary bits differ (1 versus 0). Thus the interpretation
that directly reads the target's **entire post-transition value under the current
maintenance/erasure semantics** is not radius five. This is a concrete witness,
not a theorem ruling out a different staged construction or a larger fixed
neighborhood. The chosen local alternative remains explicit and provisional.

## Complete transition and tests

`signal_description.py` describes every raw output, importing the complete clock
evaluator/controller equations and adding capture, five-copy voting and Wf.
It has **2,825 operations**, SHA-256
`431555bbcc700a798247369d582a3dfcab902eaa49f9a7a30b4ba31d328b6f13`.
`signal_native.py` compiles it in its own CPU build namespace. All 32 raw words,
including the evaluator and Signal, participate in encoding/decoding.

The five rule tests pass in 1.439 s: 240 complete scalar/description/native raw
neighborhood comparisons (including all controller fields and source event
boundaries); all ten pairs of damaged signal holders recover by one fivefold
vote; computed-Address capture; Wf timing/priority; and the nonlocal-interpretation
witness. This is protection of Signal only, not fivefold protection of the
whole simulation/controller state.

## Physical capture-to-wave experiment

`signal_world.py` implements an exact constrained full-state family: canonical
Address, uniform Age, constant LOOP metadata, no head/mail, and immutable one-bit
Data at explicitly initialized local sites. On this domain the flags and signals
are closed, and all other raw fields have known fixed values apart from Age.
Four tests pass in 0.746 s, checking complete native outputs, capture from zero
signals/flags, wave initiation, and quiet-jump rejection guards.

`signal_prefix_v1.json` starts at Age 79Q−2 with Data=1 at the five holders of one
or both reserved bits. **Those payloads are initial data, not delivered computed
upper flags.** Two literal ticks capture them. A checked stable signal profile
and zero flags permit an exact quiet jump within [79Q,96Q−1], which crosses no
capture/reset/Wf event and cannot change LOOP controller or Data. At the next
tick the local rule creates five Wf bits per requested boundary; another tick
begins the physical maintenance waves. All sparse dependency sites are updated,
including initially zero sites affected by capture payloads.

Each case represents **142,606,593 physical ticks**, comprising 258 literal ticks
and 142,606,335 guarded quiet ticks on a Q-site ring. The saved Wf-window prefix
is 256 ticks, not the entire 2Q trickle interval. Results at its end:

| Initial local payload | Flag1 | Flag2 | Wf1 | Wf2 | Local evaluations |
|---|---:|---:|---:|---:|---:|
| Right signal holders | 770 | 0 | 5 | 0 | 101,000 |
| Both signal holders | 770 | 41 | 5 | 5 | 110,114 |

Runtime was 4.684136750176549 s, with 13 source hashes and native binary hash
recorded. `audit_signal_prefix.py` independently compares complete native raw
outputs at every literal tick and checks each saved frame and quiet guards.
The independent audit passed: **211,797 complete native local checks** across
516 literal ticks and 285,212,670 guarded quiet ticks in the two cases, taking
64.22559570427984 s. All 13 source hashes and the binary hash match.
The experiment JSON SHA-256 is
`9b3e3cec38c12ff8196e95e3f49f1bd5056c6acfb080a605b691319b4baee7bd`.

## Measured schedule failure and next integration

`signal_resources.py` compiles an instruction transcript for resource accounting.
It includes all 32-word histories, complete enlarged F evaluation, early program
repair and output program reconstruction. It is **not** a self-simulation ROM:
upper-flag delivery, stage-three-only control, receiving buffers and their static
metadata handling are still missing. A targeted test passes in 0.023 s and
requires actual Signal gathers/output-copy instructions.

The transcript occupies 8,256 cells: 4,306 memory cells and 3,949 instructions
plus the final reflector. Early repair costs 348,200 ticks; the third gather's
last arrival is 48,300,297 ticks after its stage starts. Evaluation costs
**62,836,416**, leaving 4,272,448 ticks below the 8Q stage-five budget.

Starting evaluation at 72Q ends at **666,816,192**, later than capture at
79Q=662,700,032, even before delivery. This is a failed inherited schedule and
must not be hidden by reusing the old timing certificate. A 70Q vote would leave
2,031,351 ticks after the last gather arrival and 4,273,924 ticks after the
current evaluation plus the rightward flight distance before capture. Those
figures omit delivery instruction execution and any enlarged core/control code.
They apply to delivery appended after the current evaluation; sending flags
earlier would be a different transcript. `signal_resources_v2.json` uses this
qualified naming; v1's “earliest delivery” field is preserved but was too broad.

Next compile the stage-three-only delivery and buffer machinery, describe its
own transition, measure the complete schedule again, and integrate physical
signals/flags with packet clearing. The old zero-flag macrostep executor cannot
be reused unchanged. Full spatial redundancy, organized boundary termination,
source ambiguity resolution, noise experiments and depth-two/three dynamics
remain outstanding. There is no additional complete hierarchy-level claim.
