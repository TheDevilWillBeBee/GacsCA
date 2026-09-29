# Local temporal voting as a prerequisite for spatial protection

`serial_vote_*` is a new fixed construction revision. It preserves the earlier
candidate-B and literal rules and their evidence. All requested depths within
this revision use the same alphabet, radius, Q/U, implementation and complete
hard-wired description. The changes below are **not per-depth hardware**.

## Why a naive fivefold extension fails at radius five

The previous instantaneous temporal vote reads Data at offsets -1,+1,+2. Suppose
every primary Data bit has the five backups prescribed by Gray. To update the
backup at physical x for logical x+2 after correcting all operands, the last
operand is at logical x+4; its holders extend to physical x+6. This dependency
cannot generally be removed while tolerating two bad physical holders.

`test_redundancy_geometry.py` gives an exact indistinguishability witness. Set the
first two temporal operands to 0 and 1. For the last operand, visible holders
x+2,x+3 contain 0 and x+4,x+5 contain 1. The hidden holder x+6 decides its five-way
majority. Either assignment is within two faulty holders of a valid repetition
encoding. The entire radius-five input at x is identical, but the required output
backup differs. Thus this specific **correct-then-instantaneous-vote** design
needs radius six. The test is an impossibility witness for that design, not for
Gray's construction.

Wrapping the entire old radius-five rule with overlapping fivefold correction
would in general require radius nine and still leave an old inner ROM that
describes the unwrapped rule. That is not closure. A different option is to
change memory layout or add staging tracks, but it must preserve the independent
histories needed for both evaluations; simply overwriting one history is not an
adequate implementation argument.

## Implemented choice: use the existing physical evaluator

The new rule removes the clock's direct three-word Data vote. At both evaluation
entries the ordinary moving controller executes **six NAND instructions per raw
input word**, writing the temporal majority to its existing vote cell. All three
histories remain unchanged. This adds 2,112 ordinary instructions, with five
reused scratch words. It introduces no new opcode or runtime interpreter. The
same description still includes the evaluator's own state and transitions.

This moves the temporal vote into local read/compute/write procedures. On the
canonical healthy domain, structural dependency analysis of the complete clock
procedure descriptor now finds only offsets -1,0,+1. Overlapping fivefold operand
correction of a radius-one procedure fits radius five. Maintenance and Signal
remain separate radius-five components; this does **not** yet prove a redundant
implementation of their coupling or full noisy-state behavior.

Fixed constants for the new revision are Q=33,554,432 and U=4,294,967,296. The
physical radius stays five; raw width is **792 bits / 32 words**, projected width
**594 bits / 25 words**. Only the fixed Address/Age widths grew to accommodate the
larger schedule. The complete self-description has **2,618 operations**, SHA-256
`4c7770662bce9e1f3e1059f6d46648ba969c9953f15b252be41588b781f6bf8e`.
ROM SHA-256:
`9762e75a6172d48937baa7691f6d57fb233a8994352e46f7062d2aa4bab42fc2`.

| Quantity | Physical ticks or cells |
|---|---:|
| Core cells | 9,969 |
| Temporal voting plus complete evaluation | 133,614,496 ticks |
| Evaluation budget | 268,435,456 ticks |
| Evaluation margin | 134,820,960 ticks |
| Last stage-three flag delivery, after 70Q | 167,358,351 ticks |
| Capture margin | 134,631,537 ticks |
| Third gather margin before 70Q | 25,878,165 ticks |

The old Q is not silently assumed sufficient. The enlarged fixed capacity is
measured once for this revision and never selected by hierarchy depth.

## Current evidence and limits

Four focused tests pass in **2.459 s**: 250 arbitrary raw neighborhoods agree
between scalar, complete descriptor and native code; actual physical NAND voting
matches random independent 64-bit history words and preserves histories; the
entire description is embedded at the correct program position; and initialization
at depths 1–3 retains exactly the same rule identity and all raw fields. At the old
voting clock tick, vote Data now stays unchanged until the controller writes it.
Two geometry/support tests pass in 0.004 s.

The same exact cap checker also proves the revised descriptor's ordinary
zero-payload boundary orbit for all **2^32** Ages. Its noiseless consistency is
not a noise-robustness claim.

The eleven-cell nonaliased physical prefix completed **3,221,225,471 ticks in
291.733692901209 s**. Its independent audit passes 275 frozen/live sources, active
simulated WRITE, all raw gathers, actual local NAND vote, full evaluation, ten
flag deliveries and capture. Nine additional physical-flag, clock-boundary,
complete-state composition and stage-five commit tests pass in 4.965 s. The
actual whole-ring flag/control suffix then completed in **151.4977057473734 s**.
This reaches one complete **4,294,967,296-tick physical macrostep**, with ordinary
local NAND voting in both evaluation stages, complete raw Info commit and zero
physical flags at commit. `serial_vote_macrostep_audit_v1.json` passes in
5.387206516228616 s: 276 source files, 438,856 stored-site checks, 909 complete
native local comparisons, controller replay, and scalar/native/self-description
agreement for all 352 decoded raw words. The long flag trajectory uses the
separately tested packed executor; the audit does not independently replay it. Exact resources and the 63,164,999-tick temporal-voting
cost are recorded in `serial_vote_resources_v1.json`.

The newly demonstrated single-Info-bit failure is **not repaired by this change**.
Full fivefold storage, mail, controller and procedure redundancy still need to
be implemented, included in the complete description, and given fault tests and
new resource certificates. Deeper execution and amplification remain open.

## Commands

Use `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`.

```sh
python -m unittest tests.fixed_rule.test_serial_vote -v
python -m unittest tests.fixed_rule.test_redundancy_geometry -v
python -m experiments.fixed_rule.prove_serial_vote_cap --output figs/fixed_rule/serial_vote_cap_proof_v1.json
python -m experiments.fixed_rule.serial_vote_execution --output figs/fixed_rule/serial_vote_execution_v1
```

Additional commands (same one-thread environment):
```sh
python -m unittest tests.fixed_rule.test_serial_vote_flags tests.fixed_rule.test_serial_vote_composed tests.fixed_rule.test_serial_vote_control tests.fixed_rule.test_serial_vote_boundaries -v
python -m experiments.fixed_rule.audit_serial_vote_execution --input figs/fixed_rule/serial_vote_execution_v1 --output figs/fixed_rule/serial_vote_execution_audit_v1.json
python -m experiments.fixed_rule.serial_vote_macrostep --input figs/fixed_rule/serial_vote_execution_v1 --output figs/fixed_rule/serial_vote_macrostep_v1
python -m experiments.fixed_rule.audit_serial_vote_macrostep --input figs/fixed_rule/serial_vote_macrostep_v1 --output figs/fixed_rule/serial_vote_macrostep_audit_v1.json
```

The next concrete state/description design and unresolved Wf/geometry coupling
are in [REDUNDANCY_NEXT.md](REDUNDANCY_NEXT.md). Its provisional field counts are
not an implemented alphabet or a timing certificate.
