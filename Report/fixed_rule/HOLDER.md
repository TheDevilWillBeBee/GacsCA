# Fixed redundant holder rule: implementation and evidence

This is a new, explicitly modified Gács/Gray-family construction. It keeps one
physical radius-seven rule, Q=2^30 and U=2^37 at every depth. It does not change
any frozen delivery, repair-B, or serial-vote revision. The full goal is open.

## Source interpretation and choices

Gray pp. 27–34 motivates five local copies of simulation fields and hard-wired
ProgramBit elimination; Gács §§9.2–9.3 permits a suitably modified rule. The
serial-vote predecessor removed an instantaneous radius-two computation that
would have broken a radius-five fivefold-correction implementation. The new
procedure uses a holder's own old geometry and seven hard-wired metadata records
to compute its five corrected procedure copies. A faulty primary's geometry is
not broadcast to every backup. Primary colony maintenance still uses radius
five. Each Wf backup uses the computed maintenance state at its logical target;
target offsets ±2 plus maintenance radius five require physical radius seven.
This choice is explicit and fixed, not a claim that Gray prescribes this radius.

The candidate-B Flag2 erasure change and the voted-old-Signal interpretation of
D10 remain explicit modifications. The printed Flag2 rule remains frozen and
has not been declared verified. See REPAIR_B.md and BOUNDARY_AND_REPAIR.md.

## Complete physical state and description

All Data, evaluator/head/controller/mail fields have five physical copies, as
do both Wf fields. Addr, Age, both flags and Signal retain their own raw fields.
Seven static metadata records describe logical offsets −3 through +3. The raw
alphabet has 154 words / 4,110 bits; after hard-wiring those records, the physical
alphabet has 105 words / 2,724 bits. The full 13,275-operation description includes
every replica and every evaluator transition, plus colony maintenance. The fixed
ROM executes six actual NAND instructions for each of its 2,310 raw input words,
then that entire description, and regenerates all 49 represented metadata words
using local address arithmetic, LOAD and META. It does not call an upper rule on
the host. Recursive host initialization is diagnostic/initial data only.

The fixed program has 57,332 computation cells. Third-gather completion is
7,798,840,153 ticks into its stage, below the 8Q deadline by 791,094,439 ticks.
Voting plus complete evaluation costs 4,533,298,561 ticks, below its 8Q budget by
4,056,639,031 ticks. Third evaluation starts at old Age 72Q; last flag delivery
has 1,908,063,063 ticks of margin before capture. These are complete instruction
schedule calculations, not yet a physical whole-program execution result.

Raw encoding tests follow every one of the 154 fields through depth-one,
two and three initial data with identical physical identity and width. They do
not establish any deeper dynamics.

## Executed repair evidence

Eight tests passed in 12.147 s with strict native compilation:

```
python -m unittest discover -s tests/fixed_rule -p 'test_holder_*.py' -v
```

This command ran before test_holder_prefix.py was added. Exact output is in
figs/fixed_rule/holder_tests_v2.log. Earlier v1 logs preserve a harmless missing
string.h compiler declaration warning; v2 includes the header and uses
-Wall -Wextra -Werror. No source from an earlier frozen revision was modified.

The tests include 100 arbitrary raw-neighborhood scalar/description/native
comparisons, the full raw encoding/ROM contract, and physical radius-seven
locality. In coherent canonical, zero-flag states:

* The prior single physical Info-bit fault is repaired in one tick.
* Two holders with arbitrary corruption of all procedure copies recover in one
  tick while a live WRITE produces the intended 64-bit output.
* Two arbitrary complete 105-field physical-cell faults recover in two ticks
  in 28 tested clock/address cases, including reset, computation, capture,
  forcing entry, final evaluation, and commit boundaries.
* Three corrupted copies give a retained negative witness outside that contract.

Each recovery compares the entire forward fault cone, reconstructed from an
initial patch large enough to contain its backward dependencies. Therefore the
saved-time equality is a global-state equality for these cases; locality implies
all later noiseless physical evolutions coincide. It is not a statistical noise
result or a proof for arbitrary flag waves/colony damage.

## Current physical execution work

holder_quotient.py and holder_prefix_world.* represent the coherent physical
manifold using one logical procedure record and recover all five physical copies
from neighboring records. This is an execution compression, not another physical
alphabet, self-description, or depth-specific kernel. It is restricted to
canonical geometry, zero flags/Wf and the prefix before computed Age 96Q. The
physical public cell accessor reconstructs all 105 fields. Signals, actual
controller motion, program execution and ballistic mail remain evolving state.

A new guarded free-flight optimization stops before any instruction/operand,
packet delivery, boundary crossing, padding entry, queued arrival or clock event.
Source removal and destination writes are simultaneous, so crossing heads and
packets cannot erase one another. Literal steps use a finite description of the
same restricted physical transition. Full-rule conjugacy and literal-versus-
accelerated checks are being run before any whole-program claim.

## Open work

Execute and independently audit the new physical program, then successive full
periods. The old cap identity does not automatically transfer: a backup at offset
+1 can carry a reset head pulse when the holder's own Addr is Q−1, so a full-state
termination family must include that pulse or use a different documented initial
boundary. Repair during nonzero Wf/flags and after broken geometry/coherence,
amplification, depth-two/three dynamics and measured noise remain open.

## Completed execution and exact suffix certificate

The CPU prefix completed **103,079,215,103 physical ticks in 10.450971794314682 s**.
It used 304,307 literal core ticks, 96,392,905,603 quiet ticks and 6,686,005,193
certified free-flight ticks, performing 12,285,915 local evaluations. All fifteen
radius-seven inputs are distinct represented cells. The independent audit passed
305 frozen/live source hashes, full scalar/native/description agreement, every
154-word raw gather, actual NAND vote, complete evaluator outputs, all ten flag
payload deliveries and captured signals. The active represented WRITE matches.
Artifacts: `figs/fixed_rule/holder_execution_v1.{json,npz,tar.gz}` and
`holder_execution_audit_v1.json`. The prefix archive SHA256 is
`55f76f8c26b0cd34a486fac3eb2503895948089367fd294675dbdbb7c9d1b58c`.

The first complete macrostep is now independently audited. The suffix took
23.291458098217845 s; prefix plus suffix advances **137,438,953,472 physical ticks**
on **16,106,127,360 physical cells**, represented by 860,055 logical records and
exact coherent backups. Audit: 314 frozen/live sources, 2,229 saved complete-native
local transition witnesses, exact prefix handoff, every raw committed field and
local stage-five recomputation. Audit time 7.649760420434177 s. This is an actual
one-link macrostep under the fixed holder rule, not yet a deeper hierarchy.
Artifacts: `holder_macrostep_v1.{json,npz,tar.gz}`, `holder_macrostep_audit_v1.json`.

For this experiment every upper output has Flag1=1, Flag2=0, so every lower colony
has right Signal one and left Signal zero. An exact ROBDD proof checks all
2^30 Addresses and all Q+1 possible flag-front positions in four exhaustive
clock regimes of this restricted family (entry, forcing, cutoff, erasure).
The proof selects the actual full physical descriptor's flag/geometry/Signal
outputs. It is not a sampled wave-shape fit. Starting at computed Age 96Q with
zero flags and right Wf, the next Flag1 suffix has eight sites and grows left
three sites/tick. At Age 98Q Wf is zero and Flag1 is all one; the remaining prefix
shrinks two sites/tick and is zero by 98Q+Q/2. Flag2 remains zero. This exact
physical trajectory is compressed by interval endpoints; the controller still
executes its local instructions and rejects any emitted mail in this suffix.
`holder_flag_profile_proof_v1.json` passed in 1.6311709731817245 s. No arbitrary
flag profile or noise claim follows from this restricted certificate.

Full suffix tests compare reconstructed 105-word physical cells against the
complete native rule at forcing, wave-front, clearing, reset, computation and
commit boundaries. They also reject unsupported signals, initial flags and mail.
Five prefix tests passed in 31.923 s, three suffix tests in 24.187 s, and two
recurrent-prefix tests in 8.155 s. The recurrent executor admits coherent old
captured signals; it neither re-encodes memory nor zeroes residues at a boundary.
A second physical period is currently being executed from the actual first
commit, to test recurrence rather than repeating initialization.

## Ordinary cap with complete backup controller

The earlier cap with only Age changing is incorrect for this revision. At old
reset/vote ages, the +1 virtual procedure has Address zero and sees its first
metadata record. Therefore a single backup head and its entry PC pulse for one
tick. The fivefold vote removes that single copy on the following tick.
`holder_boundary.py` includes these six clock-triggered pulses. An exact ROBDD
proof of **all 154 raw outputs for all 2^37 Ages** passes (5,129 nodes,
1.2382020838558674 s). Three tests pass in 1.277 s, including the explicit failure
of the age-only conjecture, native pulse/wrap checks, and rejection of omitted
raw outputs/forward description wires. Artifact: `holder_boundary_proof_v1.json`.
This cap is ordinary initial data under the same rule, but is not an organized
or noise-robust colony. It does not establish a physically executed second link.

Commands (all CPU, independent build products under figs/fixed_rule/build):

```
python -m unittest discover -s tests/fixed_rule -p 'test_holder_prefix.py' -v
python -m experiments.fixed_rule.holder_execution --output figs/fixed_rule/holder_execution_v1.json
python -m experiments.fixed_rule.audit_holder_execution --input figs/fixed_rule/holder_execution_v1.json --output figs/fixed_rule/holder_execution_audit_v1.json
python -m experiments.fixed_rule.prove_holder_flag_profile --output figs/fixed_rule/holder_flag_profile_proof_v1.json
python -m unittest discover -s tests/fixed_rule -p 'test_holder_suffix.py' -v
python -m experiments.fixed_rule.holder_macrostep --prefix figs/fixed_rule/holder_execution_v1.json --output figs/fixed_rule/holder_macrostep_v1.json
python -m experiments.fixed_rule.audit_holder_macrostep --input figs/fixed_rule/holder_macrostep_v1.json --output figs/fixed_rule/holder_macrostep_audit_v1.json
python -m experiments.fixed_rule.prove_holder_boundary --output figs/fixed_rule/holder_boundary_proof_v1.json
python -m unittest discover -s tests/fixed_rule -p 'test_holder_boundary.py' -v
python -m unittest discover -s tests/fixed_rule -p 'test_holder_recurrent.py' -v
```

No new GPU workload was needed: the exact packet-motion optimization removed the
observed CPU bottleneck. No shared CUDA artifact, source, report or job was changed.

## Second complete period and repair qualification

The recurrent prefix completed in 10.597321567125618 s; its independent audit
passes, including exact equality to the prior committed physical state. The
second suffix completed in 23.842412021011114 s and its independent audit passed
in 7.565617880783975 s with another 2,229 complete local witnesses.
`holder_two_periods_audit_v1.json` verifies **274,877,906,944 successive physical
ticks**, identical alphabet/rule/ROM, exact raw handoff, carried signals, and 40
controller-word changes in each represented step. Both are one-link periods.

The reusable macrostep auditor's `active_simulated_WRITE` label is too broad on
the second period: the first step executes WRITE, while the second retains that
value and moves the controller. `holder_controller_semantics_v1.json` explicitly
classifies the two inputs and corrects this interpretation without rewriting
frozen evidence. Both periods have active simulated controller dynamics.

`holder_wave_fault_v1` preserves a distinguishing negative result: delete the
first Flag1 one at Age 96Q+Q/6. After t=1,2,…,8 literal physical steps, the only
clean/damaged difference is Flag1 at relative position −3t. Thus unconditional
two-tick full-state recovery is false in nonzero waves, although every procedure
field agrees in this example. The independent audit checks 2,592 full physical
outputs and 139 source hashes (4.015015775337815 s). The all-front forcing proof
bounds rejoining by 178,956,970 ticks, before cutoff, for this specified family;
those later ticks are certified algebraically, not separately traced literally.
This is not a general noise result.

Additional exact commands:

```
python -m experiments.fixed_rule.holder_recurrent_execution --previous figs/fixed_rule/holder_macrostep_v1.json --output figs/fixed_rule/holder_recurrent_execution_v1.json
python -m experiments.fixed_rule.audit_holder_recurrent_execution --input figs/fixed_rule/holder_recurrent_execution_v1.json --output figs/fixed_rule/holder_recurrent_execution_audit_v1.json
python -m experiments.fixed_rule.holder_macrostep --prefix figs/fixed_rule/holder_recurrent_execution_v1.json --output figs/fixed_rule/holder_recurrent_macrostep_v1.json
python -m experiments.fixed_rule.audit_holder_macrostep --input figs/fixed_rule/holder_recurrent_macrostep_v1.json --output figs/fixed_rule/holder_recurrent_macrostep_audit_v1.json
python -m experiments.fixed_rule.audit_holder_two_periods --first figs/fixed_rule/holder_macrostep_v1.json --second-prefix figs/fixed_rule/holder_recurrent_execution_v1.json --second figs/fixed_rule/holder_recurrent_macrostep_v1.json --output figs/fixed_rule/holder_two_periods_audit_v1.json
python -m experiments.fixed_rule.holder_wave_fault --output figs/fixed_rule/holder_wave_fault_v1.json
python -m experiments.fixed_rule.audit_holder_wave_fault --input figs/fixed_rule/holder_wave_fault_v1.json --output figs/fixed_rule/holder_wave_fault_audit_v1.json
python -m experiments.fixed_rule.holder_controller_semantics --input figs/fixed_rule/holder_macrostep_v1.json figs/fixed_rule/holder_recurrent_macrostep_v1.json --output figs/fixed_rule/holder_controller_semantics_v1.json
```

All owned holder experiments are now terminal. The full goal is still active.
[NEXT_CLOSURE.md](NEXT_CLOSURE.md) identifies the all-state refinement, arbitrary
flag clearing, actual second-link execution and repair/noise obligations. No
shared change or GPU allocation is requested.
