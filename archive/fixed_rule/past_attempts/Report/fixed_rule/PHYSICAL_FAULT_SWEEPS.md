# Full-field fault sweeps and exact flag-front recovery

2026-09-27. The unchanged fixed rule now has 296 literal fault-cone experiments
covering Address, Age, Flags/Wf, Signals, procedures and complete projected
physical states. Most repair in one or two ticks. Four forcing-front disturbances
retain one Flag1 difference after twelve ticks; actual GPU flag evolution later
repairs all four. No unrepaired state is admitted to a noiseless endpoint
shortcut. The full self-simulation/amplification goal remains active.

## Exact bounded physical execution

`retimed_holder_literal_cone.py` executes the complete physical G=pi F iota on
both actual and comparison configurations. Each starts from an immutable actual
checkpoint plus explicit replacements of one or two physical sites. The CPU
native evaluator runs the full descriptor. The 49 metadata fields are regenerated
from the **actual output Address**, as required by the fixed G projection; every
one of the 105 mutable fields remains present.

For a t-tick deadline, the initial window extends 14t cells beyond the fault
span. Every tick discards seven cells at each edge after local evolution. Thus
artificial periodic-boundary inputs cannot reach any retained state, while the
retained window still contains the entire possible radius-7t fault cone. Complete
equality in that window establishes equality everywhere: outside the cone,
initial neighborhoods and their causal histories agree. Aliasing/oversize
windows reject before evolution. No host simulated transition substitutes for a
physical transition.

The complete-bank image accessor retains inherited scratch, all five Data copies,
localized Signals and all fixed metadata. It accepts only canonical terminal
images at Age 0 or U-1. For nonterminal forcing/controller states, the experiment
reads actual complete raw cells from the general GPU executor instead.

Four tests pass in **1.816 s**. They compare the image accessor with independent
vector reconstruction, shrinking windows with full-ring physical evolution,
explicit nonzero controller propagation, and resource/domain rejection. The
first test revision used a negative physical Address in a fixture and failed
before evolution. Its source/log are preserved; the corrected fixture uses a
valid interior controller. This was not a physical-rule failure.

## Actual depth-two checkpoint: 160 pulses

The bottom checkpoint is the complete B(M_(a-1)) bank from
[TIMED_DEPTH_TWO_REPAIR.md](TIMED_DEPTH_TWO_REPAIR.md), at aU during a real running
middle evaluator. One or two adjacent bottom sites are replaced at eight anchors:
colony edge/Signal groups, an encoded controller word, and memory/program
interfaces. The sweep includes 16 cases each of Address, Age, Flags/Wf, Signal,
procedure-only and all-ones replacement, plus 64 seeded complete projected-state
replacements. Seeds, exact old/injected states and every trace are retained.

**All 160 rejoin completely**: 111 after one tick and 49 after two. This includes
all controller fields, not just Info or a decoded projection. Since these states
rejoin the exact healthy checkpoint trajectory, subsequent noiseless depth-two
endpoints agree by determinism. This does not say every later noisy trajectory
repairs, nor does it test arbitrary fault times or independent space-time noise.

## Actual forcing/clearing/controller phases: 136 pulses

A physical colony starts from the canonical encoding of `parents(1)` and runs
on the existing GPU backend to three actual checkpoints:

| Age | Context | Flag1 sites | Localized Signal bits |
|---:|---|---:|---|
| 1230000100 | Active forcing/front propagation | 305 | left 0, right 1 |
| 1230065636 | Clearing after forcing ends | 32568 | left 0, right 1 |
| 1232000100 | Active final evaluator | 0 | left 0, right 1 |

Address, Signal, random complete-state and all-ones pulses replace one/two sites
near boundaries and the first Flag1-front site. Unwrapped -1 and Q-1 also exercise
periodic addressing; these trials are not all independent statistical samples.
Of 136 cases, **108 rejoin in one tick and 24 in two ticks**. Four cases remain
different at the twelve-tick deadline, each in exactly **one physical Flag1 bit**.
They are forcing-context cases 18, 19, 23 and 30 near Addresses 32462/32463.
A finite deadline is not used to claim permanent failure.

The GPU continuation reexecutes each initial checkpoint, injects its exact saved
raw replacement, and executes twelve literal full-G ticks. Every surviving raw
exception matches the CPU sweep. An exact representation rebase puts the wrong
Flag1 into the actual packed flag plane; it does not repair it. Complete snapshots
still differ from the healthy reference in precisely that one bit. All other
stored fields agree.

The existing exact GPU flag recurrence then evolves the actual wrong front,
alongside its actual controller state, to Age **1230012000**. All four complete
physical states match an independently evolved healthy state there: **rejoin by
11900 ticks after injection**. This is an upper bound, not an earliest-rejoin
measurement. The damaged state is never replaced by a healthy successor and no
noiseless endpoint shortcut is used during the flag discrepancy.

The authoritative continuation is v2. The first run also passed, but unnecessarily
constructed the empty exception owner before advancing its background and manually
synchronized its clock. The exact v1 source/results are preserved. v2 creates the
owner after the initial checkpoint is reached and uses the ordinary clock guard
throughout; no guard bypass remains in the accepted driver.

## Independent audit and measurements

The scalar source transcription checks **22256 complete physical outputs**,
each with all 154 fields: every output in every possible fault cone, on every
executed tick, for both actual and comparison trajectories across all 296 cases.
It matches the native descriptor, every recorded trace and every retained final
exception. Four finite-deadline non-rejoins remain explicit in that audit and
are linked separately to the full GPU continuation. This is a trajectory audit,
not a universal mathematical or stochastic recovery theorem.

| Experiment | Wall seconds | Reported host peak KiB |
|---|---:|---:|
| 160 checkpoint-boundary pulses | 7.217314 | 68144 |
| 136 forcing/clearing/controller pulses | 10.944380 | 187172 |
| Independent scalar-source audit | 79.295521 | 72092 |
| Four exact GPU front continuations, v2 | 39.158591 | 177788 |

The continuation's conservative explicit GPU peak is **24265180 bytes**. No
physical rule, ROM, alphabet, fixed descriptor, CUDA source, shared module or
historical artifact changed. Existing private GPU/native binaries are reused.
The user's 40 GB host ceiling is respected by large margins. All jobs are terminal.

## Commands and evidence

From the repository root, with `OPENBLAS_NUM_THREADS=1`:

```sh
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_literal_cone_tests_v2_watch.json --seconds 30 --rss-mib 512 -- python -m unittest tests.fixed_rule.test_retimed_holder_literal_cone -v
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_boundary_fault_sweep_v1_watch.json --seconds 120 --rss-mib 1024 -- python -m experiments.fixed_rule.retimed_holder_boundary_fault_sweep --output figs/fixed_rule/retimed_holder_boundary_fault_sweep_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_forcing_fault_sweep_v1_watch.json --seconds 120 --rss-mib 1024 -- python -m experiments.fixed_rule.retimed_holder_forcing_fault_sweep --output figs/fixed_rule/retimed_holder_forcing_fault_sweep_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_fault_sweeps_audit_v1_watch.json --seconds 180 --rss-mib 1024 -- python -m experiments.fixed_rule.audit_retimed_holder_fault_sweeps --output figs/fixed_rule/retimed_holder_fault_sweeps_audit_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_forcing_front_recovery_v2_watch.json --seconds 120 --rss-mib 1024 -- python -m experiments.fixed_rule.retimed_holder_forcing_front_recovery --output figs/fixed_rule/retimed_holder_forcing_front_recovery_v2.json
```

All accepted commands exit 0. Failed/superseded v1 source and logs remain available.
The evidence index is `figs/fixed_rule/retimed_holder_fault_sweeps_evidence_v1.json`.

## Next mathematical question and remaining gaps

The two-tick behavior suggests a useful general lemma: from canonical geometry,
uniform legal Age, zero primary flags/Wf, coherent procedure backups and coherent
Signals, arbitrary replacements at at most two physical sites should fully
repair within two ticks. Fivefold voting repairs operands immediately; geometry
repair may leave wrong procedure outputs at those holders for one tick, which
the next vote removes. This is a **candidate proof target**, not a theorem
established by these finite sweeps. The flags/Wf hypotheses matter: the measured
forcing-front cases show why they cannot be dropped.

Next certify the geometry and majority subclaims against the complete descriptor,
then determine the precise clock/coherence hypotheses needed by the full
statement. General stochastic amplification, simultaneous distributed faults,
robust caps, nonaliasing top colonies and depth three remain open. The known
homogeneous-cap Address persistence and printed Flag2/computed-SimBit ambiguities
remain explicit; none is resolved by these experiments. Gray's specialized
hard-wiring and Gacs's suitably modified self-correcting rule remain the source
basis, without a new U<=128Q requirement.
