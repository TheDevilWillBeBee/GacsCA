# Synchronous physical GPU evolution with a periodic background

2026-09-26. The new executor advances an entire represented ring synchronously,
retaining all raw physical deviations from an evolving periodic background.
The bounded-workspace backend passes six tests and an eight-tick active-computation
experiment. Observed total GPU process memory is 466 MiB; host RSS is 262,728 KiB.
The physical rule and its self-description are unchanged. Full nested macrosteps
and correction across levels remain open.

## Exact representation and update relation

Let B_t be a raw configuration of period P on a ring whose size N is divisible
by P. Store the actual state X_t as B_t plus a sorted set E_t of positions whose
complete raw state differs from B_t. The background has no healthy-state or
quiet-state assumption: its next state is computed by the same full local F.
The 154 raw fields occupy 4,090 bits, packed into 64 uint64 words per row.
Program metadata, every evaluator/controller backup, mail, geometry, clocks,
flags, Wf and Signal all remain present. Arbitrary in-range raw states, including
states outside the hard-wired projected subspace, are supported by this backend.

For a radius-seven rule, define C_t = {e-j mod N : e in E_t, j in [-7,7]}.
The GPU computes B_(t+1)=F(B_t) and computes F(X_t) at every position in C_t,
using only the old background and old exceptions. It retains a candidate exactly
when all its raw output fields differ from the new background in at least one
bit. The next exception positions are sorted and their full rows compacted on
GPU; the background buffers swap only after the computations complete.

This gives a direct locality argument. Outside C_t every input neighbor agrees
with B_t, so the output agrees with F(B_t). Inside C_t the full local transition
is evaluated explicitly. Exact packed-row comparison, including canonical zero
padding, therefore yields X_(t+1)=F(X_t) everywhere. Because F is translation
invariant and P divides N, the background remains P-periodic. No source theorem
about noisy amplification or colony repair is required for this representation
identity. It does not establish those separate scientific claims.

Physical rows stay on the GPU across ticks. The host constructs affected-site
indices and filters indices using GPU equality flags; it does not compute an
upper transition or physical output. A candidate-capacity failure occurs before
any background update or state commit. The implementation bounds P at 32,768,
candidates at 8,192 and diagnostic read batches at 256. These are execution
resource limits, not a maximum hierarchy depth or changes to F's alphabet.

The complete descriptor SHA256 is still:
`af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`.
The new fixed-DAG emitter is an accelerator implementation of that description;
it adds no evolving field or operation to the physical evaluator or its ROM.

## First implementation: correct outputs, excessive implicit GPU storage

`small_holder_periodic_cuda.{py,cu}` passed four tests and the active experiment.
However, counting explicit buffers alone was misleading. Its explicit allocation
was 42,338,304 bytes, but process memory rose from 458 MiB before execution to
31,216 MiB after the first transition. `cuobjdump --dump-resource-usage` reports
146,832-byte stacks for both transition kernels. The generated full expression
DAG and local neighborhood arrays create substantial per-thread storage.

That run is terminal and released the device. Its source, private binary, passing
results and measured resource failure are preserved. Do not use its explicit
buffer count as a total-memory bound or choose this backend for larger runs.
Artifact: [small_holder_periodic_validation_v1.json](../../figs/fixed_rule/small_holder_periodic_validation_v1.json).
The surprise was recorded immediately in STATUS.md and corrected before further
colony-sized experiments.

## Bounded-workspace revision

`word_workspace_source.py` uses the existing symbolic live-owner allocator and
verifier to assign reusable result slots for the identical expression DAG.
`small_holder_periodic_bounded_cuda.{py,cu}` uses 256 GPU workers and explicitly
allocated interleaved input, output and temporary rows. Workers process physical
positions in strides; the scratch is private per worker and reused between
positions and between the background and exception kernels. No output depends
on another worker's scratch. Every input/output field remains present.

Compiler-reported stack sizes fall to 760 bytes for background updates and
840 bytes for exception updates. Explicit buffers plus workspace total
47,876,096 bytes. The measured process GPU memory samples are 464 MiB before
execution and 466 MiB after the first and eighth ticks. These observed process
measurements include overhead beyond explicit arrays; they are samples, not a
universal peak guarantee for all CUDA contexts or future kernels.

The bounded private binary SHA256 is:
`f61ad9d6fb9e7dcbe3acf4f1bf78f8f2b0087c47ffa488a911fe3942bfc6d904`.
Both versions' compiler resource outputs are retained in
`figs/fixed_rule/small_holder_periodic*_kernel_resources_v1.log`.

## Validation and commands

All commands ran from the repository root:

```sh
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_periodic.py -v
# Original backend: 4 tests, 182.524 s including first build, OK.
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_periodic_bounded.py -v
# Bounded backend: same 4 cases, 21.061 s including first build, OK.
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_periodic_frontier.py -v
# 2 additional bounded-backend cases, 1.358 s, OK.
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_periodic_validation --output figs/fixed_rule/small_holder_periodic_validation_v1
# Original experiment: passed, 2.753237 s; total GPU process memory 31,216 MiB.
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_periodic_bounded_validation --output figs/fixed_rule/small_holder_periodic_bounded_validation_v1
# Bounded experiment: passed, 3.165902 s; host RSS 262,728 KiB; GPU 466 MiB.
```

The six bounded-backend tests cover all-field packing and width/padding rejection;
five successive whole-ring updates against dense native evolution for arbitrary
raw backgrounds of periods 1, 3 and 17, with independent scalar checks; complete
encoded-parent/controller initialization; organized Q-cell background updates
against the existing CPU prefix executor; two damaged procedure holders; atomic
capacity rejection; and empty-exception evolution. Additional frontier regressions
retain changed raw program metadata, process more than 256 candidate positions,
and require a moving head to create a deviation beyond the previous exception
support. These would fail if compaction compared only Data or the update forgot
to expand the affected set.

The standalone experiment uses N=Q²=1,073,741,824 represented sites, with a
Q-periodic initialized colony background and four exceptional holders in two
widely separated pairs. The background contains a complete encoded parent and
an explicit coherent active WRITE. The independent CPU physical prefix starts
from the same background. After each of eight literal GPU ticks, all 154 fields
at 17 probes agree with it (136 complete raw comparisons), all exceptions are
gone, and Data at the WRITE destination is 91 instead of 11. Host physical/upper
transition calls are forbidden during GPU advance.

This is an exact large periodic physical ring, **not a depth-two initialized
hierarchy**. Its two-level-sized site count is possible because the background
repeats. It neither demonstrates a nested macrostep nor replaces initialization
with a claim of hierarchy. The update evaluates 262,176 local transitions:
8Q background transitions plus 32 first-tick candidate transitions. The eight
physical ticks are far short of U, let alone U². The fault result concerns two
separated pairs of procedure-holder faults; it is not general geometry/program
repair, stochastic robustness, or correction across levels.

The bounded artifact contains source and binary hashes, metrics, limitations and
NPZ initialization/probe trajectories:
[small_holder_periodic_bounded_validation_v1.json](../../figs/fixed_rule/small_holder_periodic_bounded_validation_v1.json).
All runs are terminal. No shared code or CUDA artifacts were changed. GPU process
queries returned empty after the experiments. Main agent retains substantial GPU
scheduling; no ongoing device allocation remains.

## Remaining work and ownership

The previous shrinking-window backend could certify only an interior. This
executor now maintains an exact global configuration and synchronous commits,
including physical exceptions, over arbitrarily many steps within its resource
limits. However, it relies on a genuinely repeating background. A true nested
initialization generally has different encoded parent/controller data across
colonies; repeating one initialized colony does not supply that data. The dense
Data-bank representation must be integrated with explicit sparse controllers,
mail and physical exceptions, with a sound set of affected sites. Do not expand
all distinct memory data into full raw exception rows and assume the present
8,192-candidate limit will suffice.

Literal Q-background updates still cannot make the U²=2^64 horizon practical.
Next architecture work must combine exact event/transport skipping and better
physical-evaluator space/time costs with the nonperiodic encoded Data bank.
Passing local or eight-tick GPU checks is not a reason to launch an enormous
unjustified nested run. Actual successive nested macrosteps, mixed-Signal suffix
coverage, robust termination, altered-schedule repair/trickle-down arguments and
cross-level noise measurements remain open. The final goal stays active.

Owned new files: small_holder_raw_packed.py; small_holder_periodic_initial.py;
original and bounded periodic CUDA wrappers/kernels; word_workspace_source.py;
three periodic test files; original/bounded periodic validation drivers; private
builds/logs/results under figs/fixed_rule; this report and STATUS.md. Existing
frozen sources were preserved. No shared change is requested; replies belong in
Report/fixed_rule/MAIN_AGENT_NOTES.md.
