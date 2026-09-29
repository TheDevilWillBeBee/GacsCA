# Nonperiodic resident GPU computation through full self-description capture

2026-09-26. The GPU now executes the full computation prefix with distinct encoded
parent states, rather than requiring a repeating colony background. It completed
1,979,711,488 physical ticks through three gathers, temporal voting, evaluation
of the complete self-description, computed-flag delivery and Signal capture.
All 154 simulated raw output fields match the intended modified rule, including
an active simulated WRITE. A separate audit passed. This stops before Wf/repair
waves, later recomputation and commit; it is not a full new GPU macrostep or
nested depth-two execution.

## Fixed physical rule and representation

`small_holder_resident_prefix.{py,cu}` preserves the small_holder physical rule,
ROM, Q=32,768, U=2^32 and radius-seven neighborhood. Its complete physical
self-description remains
`af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`.
The source interpretation and explicit candidate-B/D10 deviations remain those
in [SMALL_HOLDER.md](SMALL_HOLDER.md); this backend does not resolve those source
ambiguities or establish a noise theorem for the altered schedule.

Each colony has its own GPU Data bank for 9,922 ordinary memory rows and five
tail memory rows. Distinct complete parent states are encoded into the raw Info
positions in bounded initialization chunks. No Data bank is mirrored densely on
the host. Up to 64 sparse logical records per colony retain all controller, mail
and Signal fields. Canonical Address and shared Age are reconstructed; fixed
program metadata comes from the same ROM as the scalar/descriptor implementations.
The coherent lift reconstructs all five procedure/Wf backups and all seven raw
metadata records. This changes execution storage, not the physical alphabet.

The backend's explicit domain is canonical geometry, uniform Age, zero physical
flags/Wf, zero non-MEM Data and old Age below WF_START-1. Noncanonical geometry,
incoherent physical faults and the Wf/suffix regime are rejected or outside the
interface; they are not silently projected away. The full-raw exception backend
from [PERIODIC_EXECUTION.md](PERIODIC_EXECUTION.md) remains a separate component.
Integrating the two representations is still required for noisy nonperiodic runs.

Sparse live-record capacity and device budgets are execution limits. Increasing
the number of colonies does not select a new physical rule or state width. Info
and sparse initialization use chunks of at most 128 colonies; callers may set a
bounded explicit device budget up to 8 GiB. All runs here stayed below the default
64 MiB explicit budget. No depth-two-sized allocation was made.

## Local evaluation, synchronous commits and exact skips

For each literal tick, the GPU marks radius-five logical neighborhoods of every
nonzero controller/mail/Signal record, including neighboring colonies. The
existing certified logical prefix transition is the coherent specialization of
the full radius-seven physical rule. Outside the marked set, only canonical Age
changes unless a clock boundary triggers an explicit bulk operation.

Resets and the protected temporal vote update the Data bank using the fixed ROM
masks. Reset/vote/capture control positions are included in the local evaluation
set. Vote destinations are checked not to overlap any vote's history operands,
so the bulk vote has no in-place read/write race. Literal outputs and new sparse
counts are staged before committing. Capacity failure leaves Data, controllers
and Age unchanged. Zero non-MEM Data remains invariant: local Data writes require
MEM metadata, and the initializer/domain checker enforce the initial condition.

Physical event skipping stops before a head operation or reflection, packet
arrival or colony crossing, clock reset/vote/capture boundary, or activity-phase
change. Free motion moves heads and packets simultaneously, merging disjoint
controller/mail fields at overlapping destinations. Data stays in its actual
bank. Inactive intervals preserve procedure state and advance canonical clocks.
Invalid inactive mail fields, multiple heads per colony or nonzero Signals veto
active skipping where the requisite invariant is unavailable. In particular,
nonzero Signals after capture currently prevent long jumps even when they have
settled; that performance limitation needs a stationary-Signal certificate.

The host computes no simulated transition during advance. GPU kernels execute
the local physical prefix procedure, and the host schedules bounded exact jumps.
Tests and experiments patch host rule/evaluator calls to fail during GPU advance.
Static event analysis and diagnostic CPU comparison do not replace the represented
upper rule's physical computation. The evaluator's complete raw state is encoded
in the Info/history/vote/Hold data and processed by the fixed colony program.

## Tests, failed horizon and communication evidence

Commands from repository root:

```sh
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_resident_prefix.py -v
# Initial literal implementation: 4 tests, 5.126 s, OK.
# Its sources are preserved in small_holder_resident_prefix_literal_source_v1.tar.gz.
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p 'test_small_holder_resident_*.py' -v
# Final literal + event backend: 6 tests, 5.450 s, OK.
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_resident_validation --output figs/fixed_rule/small_holder_resident_validation_v1
# Failed final pending-mail assertion: chosen horizon preceded the first SEND.
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_resident_validation_v2 --output figs/fixed_rule/small_holder_resident_validation_v2
# Passed at 30,814,700 physical ticks; 13.763650 s including full-state audits.
```

The six final tests cover every encoded raw controller field across distinct
parents; successive active writes and cross-colony mail; literal versus accelerated
head/packet motion, overlapping sources and gap flight; reset/vote/capture and
near-Wf boundaries against the full native physical rule; Signal fallback; field,
domain and budget rejection; and atomic active-record-capacity rejection.

The first validation selected 20 million ticks, before first SEND at 30,671,802.
All complete-state comparisons at 100,000, one million and 20 million ticks
passed, but the intended communication assertion was premature. The original
source/log/progress and a terminal `.failure.json` are preserved; its old progress
file saying running is not a live process. The corrected experiment derives its
last horizon from the first SEND of a nonzero metadata-index field plus 20,000
ticks. It verifies all 98,304 logical rows at four checkpoints. At the last point,
three packets have crossed colony boundaries with distinct payloads 99, 172 and
26. Combined GPU advance took 0.609312 s; audits dominate the 13.76-second run.
Observed GPU process memory was 422 MiB and maximum host RSS 263,404 KiB.

## Complete self-description computation on GPU

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_resident_capture --output figs/fixed_rule/small_holder_resident_capture_v1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_resident_capture --input figs/fixed_rule/small_holder_resident_capture_v1 --output figs/fixed_rule/small_holder_resident_capture_audit_v1.json
```

The run uses the existing active 15-parent fixture, with complete raw controller
backups and an intended simulated WRITE of `0x123456789ABCDEF0`. All three
physical gather histories equal the entire old raw neighborhood, including
metadata/controllers. The protected vote equals that neighborhood, and the
physically computed Hold values equal all 154 fields of the projected/lifted
full raw transition. All ten boundary Data buffers carry the computed flags;
the captured Signals match their expected physical bit layout.

| Measured result | Value |
|---|---:|
| Represented parents / physical sites | 15 / 491,520 |
| Physical ticks through capture | 1,979,711,488 |
| Literal ticks | 156,726 |
| Exact transport/quiet ticks | 1,979,554,762 |
| Logical local evaluations | 47,057,085 |
| GPU advance time | 73.703895 s |
| Total time including CPU/audits/artifact writing | 100.003527 s |
| Explicit GPU buffers/workspace | 5,116,680 bytes |
| Observed GPU process memory | 424 MiB |
| Maximum host RSS | 462,056 KiB |

The final GPU state was compared with the frozen CPU physical executor over all
491,520 logical positions. Equality of those complete coherent records lifts to
every raw physical field within the certified domain. The standalone audit checks
source/binary hashes, independently agrees scalar/native/expression evaluations,
checks all Hold fields, histories, vote, flags and Signals, and reconstructs the
complete-state stream hash from stored cores plus certified empty gaps. Source
and state evidence: [capture result](../../../../../figs/fixed_rule/small_holder_resident_capture_v1.json)
and [independent audit](../../../../../figs/fixed_rule/small_holder_resident_capture_audit_v1.json).

The validated private binary SHA256 is
`c4012d95a5b70286a5007336e9fb501a307e1003e78d332f063146788e669368`.
Compiler resource inspection of that exact binary reports zero stack bytes for
all kernels, including the arithmetic evaluator. The first resource command used
a glob matching both preserved builds and produced usage text; retain the valid
`small_holder_resident_kernel_resources_v2.log` instead. Total observed process
memory, rather than explicit allocations alone, remains the scheduling metric.

## Space fits sooner than independent schedules do

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_resident_scaling --output figs/fixed_rule/small_holder_resident_scaling_v1.json
# Passed, 1.191889 s; host RSS 161,540 KiB; at most 128 colonies allocated.
```

The measured allocation is 2,799,840 fixed bytes plus 154,456 bytes per colony.
For Q lower colonies, that estimates 5,064,014,048 explicit device bytes. This
is an estimate for this prefix backend, not an allocation or a complete noisy
hierarchy's memory bound.

A controlled physical READ_META fixture exposes the shared-time scheduler's
limitation. With 128 colonies querying the same address, 136 physical ticks need
one literal tick and 1,408 local evaluations (0.001649 s). With distinct query
addresses 0–127, they need 128 literal ticks and 180,224 evaluations (0.179414 s).
All resulting controller values are checked. Independent metadata events prevent
large common jumps, so the memory estimate cannot justify promising practical
Q-colony or nested runtime. This is not a measurement of a full depth-two run.
Evidence: [scaling result](../../../../../figs/fixed_rule/small_holder_resident_scaling_v1.json).

Next work should address independent colony/event times with correctly timestamped
local communication, or another exact batching method, before a large nested
run. It must preserve causal ordering and complete controller state, with no
host upper-transition substitution. Also needed: stationary-Signal skipping,
physical Wf/suffix/repair and later recomputation/commit, successive full GPU
macrosteps, composition with full-raw fault exceptions, genuinely nested initial
states and dynamics, and cross-level noise measurements. The U² horizon and the
physical evaluator's cost remain construction constraints, not just GPU capacity
questions. The final project goal remains active.

Owned files are the resident prefix wrapper/kernel; two resident test files;
validation v1/v2, capture, independent audit and scaling drivers; owned
figs/fixed_rule artifacts/private builds; this report and STATUS.md. No shared
modules or CUDA artifacts changed. All runs are terminal and the final device
process query was empty. Main agent retains substantial GPU scheduling; replies
belong in MAIN_AGENT_NOTES.md, which was not edited.
