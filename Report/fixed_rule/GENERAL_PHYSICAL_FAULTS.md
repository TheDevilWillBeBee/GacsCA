# Full physical faults during general flag dynamics

2026-09-26. Full projected physical exceptions now work with the general-Signal
resident executor. A combined experiment retains six early physical Info bit
faults, later replaces two complete projected physical states, and deletes a
Flag1 front bit. It executes a complete work period, observes the front delay,
and rejoins a separately evolved healthy physical world at U+1. This is targeted
recovery through one simulation link, not a stochastic threshold or a completed
nested upper period.

## Exact representation and unchanged rule

New `gacsca/fixed_rule/small_holder_general_faults.py` reuses the frozen full
exception descriptor, packing, causal-frontier, compaction and Data-rebase code.
Its generated CUDA adapter reconstructs the reference's actual packed Flag1/Flag2
and all derived Wf backups. It borrows the general flag engine's GPU pointer,
checks its colony count and physical Age, and binds it before each read or
mutation. It neither owns nor frees that buffer. Allocation/clearing boundaries
are tested, including release of the reference flag buffer while an exception
exists.

The actual state X is a general resident reference B plus complete exception
records. Both G(X) and G(B) are evaluated on the radius-seven expansion of the
exception set; only complete-state differences survive. Outside that expansion,
old neighborhoods are identical. Every mutable physical controller, geometry,
mail, Signal and flag field remains present. Program metadata remains derived
from each holder's own Address, as in G=project(F(lift(.))). Faults in the older
raw-F metadata alphabet remain a separate experiment class.

The physical alphabet, neighborhood, transition, descriptor and fixed program
are unchanged. The adapter changes only the execution representation. GPU
exception buffers still occupy 18579456 bytes, with an 8192-site frontier cap;
overflow rejects before the tick changes state. The general reference remains
bounded by its existing canonical/coherent/mail-free domains and resource limits.
Actual exceptions can violate geometry and coherence without being discarded.
This is not an unrestricted dense noisy-world executor.

## State-preserving flag rebase

A physical flag defect can leave a one-site front delay for many ticks. Keeping
it as an exception would force full descriptor evaluation at every tick even
though the exact packed flag engine can evolve that actual trajectory cheaply.
`absorb_flags()` therefore changes the reference representation at the same time:

- A primary Flag2 bit can enter the reference directly; its full physical holder
  already retains the actual value. It changes no derived Wf field.
- A primary Flag1 bit enters only if every actual backup of its derived Wf2 has
  the value implied by that bit, the unchanged reference Signal and physical Age.
  Otherwise the rebase rejects that bit and keeps the exception.
- All other physical fields remain in complete exception records. Exact full-state
  normalization removes only records already equal to the new reference.

For a changed Flag1 at logical position a, its Wf2 backups are fields
`w{2-d}_wf2` at a+d, d=-2,...,2. If the rebase changes a derived backup value,
that holder must already be an exception with exactly the new value: a nonexception
would equal the old reference and fail the consistency test. Thus the actual
state is unchanged everywhere. Different primary positions affect distinct
backup fields; packed primary-bit updates use atomic operations to preserve
simultaneous updates in the same 64-bit word.

Rebasing never means recovery. The test deliberately retains a wrong flag front
with zero exceptions and compares it to a literal exception trajectory. Rebase
is allowed only through the forcing cutoff. Later absorption could introduce a
new defect too late for the reference's existing clearing deadline, so those
cases remain explicit exceptions. The reference asserts actual zero flags before
releasing its buffer; it does not install the predicted zero state.

The controller/flag factorization from GENERAL_FLAGS.md still applies to the
reference after this change: its geometry and Signals are canonical/coherent,
and its suffix mail is absent. The packed engine admits arbitrary primary flag
bits. Faulty geometry/controller fields remain in the full local exception path.
The healthy comparison world is separate and never used as a replacement state.

## Tests

With `OPENBLAS_NUM_THREADS=1`, Python unittest discovery/TextTestRunner ran
`test_small_holder_general_faults.py`:

| Revision | Result | Test time | Runner time | Host RSS |
|---|---|---:|---:|---:|
| Initial adapter | 4 passed | 1.922 s | 2.058966 s | 175940 KiB |
| Adapter plus exact flag rebase | 7 passed | 18.115 s including private build | 18.254711 s | 181048 KiB |

Logs are `small_holder_general_faults_tests_v1.log` and `..._v2.log` under
`figs/fixed_rule/`. The second run includes the first four cases plus rebase tests.

Tests randomize all 105 mutable physical fields and compare three complete
shrinking causal-cone steps against independently evaluated native G, including
forcing entry, active forcing, cutoff and flag-buffer destruction. They check
interior geometry/procedure repair, wrong-Data rebase with nonzero Flag2, type and
external-clock guards, rejection of inconsistent Wf backups, exact state retention
after consistent rebase, 64 simultaneous packed-bit changes, and the late-rebase
guard. A 256-tick delayed-front test compares the accelerated result with literal
exception evolution and confirms it still differs from the healthy reference.
Host evaluator/raw/projected/native transition calls are forbidden during GPU
advance in the distinguishing cases.

## Combined temporal-fault experiment

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_temporal_repair --output figs/fixed_rule/small_holder_temporal_repair_v1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_temporal_repair --input figs/fixed_rule/small_holder_temporal_repair_v1 --output figs/fixed_rule/small_holder_temporal_repair_audit_v1.json
```

Both exited zero. The fixture contains the complete upper WRITE controller and
has computed left/right Signals equal to one. Its lower ring has 15 colonies,
491520 physical sites. Two independently evolving general resident worlds are
allocated: the damaged state and its healthy comparison.

At time zero, six one-bit faults change three lower Data holders for each of two
upper value replicas. The first lower local majority spreads each wrong bit into
five holders; exact Data rebase preserves it. The decoded upper state remains
wrong through capture, while Hold already contains the fully corrected upper
transition. No repaired value is supplied by the host.

At physical time 2147483748 (=WF_START+100), the experiment replaces all 105
mutable fields at adjacent sites 229476 and 229477 with seeded random values.
It also changes Flag1 from one to zero at front site 261839. The resulting
metadata changes are derived from the faulty Addresses, not extra raw-metadata
faults. The two full-site deviations disappear after the next complete local
transition. One delayed-front flag remains, and exact flag rebase preserves it
in the reference's packed state.

After 256 ticks, the damaged and healthy trajectories still differ in one
physical Flag1 bit. Their Flag2 planes agree. Both flag trajectories subsequently
clear through literal GPU evolution. At U, all 154 decoded fields agree with the
healthy intended upper transition. At U+1, after the ordinary next reset, every
physical core/tail/gap row matches the separately evolved healthy world. The
entire damaged world was never replaced, reset by the host or reinitialized.

GPU advance wall time, including the healthy comparison: 34.354987 s. Total:
49.222678 s. Host max RSS: 577768 KiB. Exception buffers: 18579456 bytes in addition
to the two small resident states and temporary flag/controller storage. No GPU
process peak was sampled during this run. Final GPU query was empty.

The independent audit passed in 1.036061 s, with 62200 KiB host RSS. It verifies
the early fault mapping, complete decoded repair by scalar/native/descriptor
evaluation, actual late projected-state replacements, and 31 complete saved
first-tick physical causal-cone outputs. It also checks the retained one-bit
front difference at 256 ticks. Complete physical rejoin is a runtime assertion in
the hashed driver; the small archive does not reconstruct that entire trajectory.

Artifact SHA256:
`4cf4630dc3fe4bef9af6d79309f46a609d0e9cdfd1259cb01df623f31de1762a`.
Fault backend binary SHA256:
`03ba1212a9a6baa24aa7f23fcc526457e9273163141ea99e84af6e12410cdfa5`.
The full descriptor remains
`af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`.
Source and comparison-controller hashes are recorded in the manifest.

## Ownership and next steps

Owned additions: `small_holder_general_faults.py`, its generated private CUDA
build, `test_small_holder_general_faults.py`, the temporal-repair experiment and
audit, this report and namespaced evidence. STATUS.md is updated. Frozen backends,
shared source/reports, historical jobs and data were not modified. Main-agent
notes remain absent; the 8 GiB whole-Q pilot is still pending coordination.

Next: generate reproducible sparse random physical space-time faults over whole
work periods, report the actual rate/volume/counts and complete decoded outcomes,
and retain failure/capacity cases. That would begin stochastic evidence; these
selected faults establish no threshold. General faulty-geometry recovery bounds,
robust finite-depth termination, actual full nested macrosteps and practical
nested trajectory cost remain open. U²=2^64 is still a central obstacle. The goal
remains active with Q/U optimization independent of a ratio constraint of 128.
