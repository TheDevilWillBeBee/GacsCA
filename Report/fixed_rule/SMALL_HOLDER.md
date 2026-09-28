# Smaller colonies with an independent fixed schedule

2026-09-26. This milestone implements Q=32,768 and U=2^32, validates two
successive **one-link** macrosteps, and checks a bounded CUDA local kernel.
Full depth-two dynamics, practical top-level runtime and error correction across
levels remain open. The project goal remains active.

## Source basis and construction scope

The user prioritizes actual fixed-rule self-simulation, practical two-level GPU
execution, and demonstrated correction across levels; U/Q=128 is no longer a
constraint. Gray p.15's Q>=8192 maintenance assumption does not certify complete
self-simulation at that size. His pp.31–32 hard-wiring/ProgramBit projection and
p.34 computation argument require sufficiently large Q with unspecified program
constants. Gács §§9.2–9.3, especially Condition 9.20 / Theorem 9.3, separate
communication/computation time requirements from storage. These readings and
precise extract locations are recorded in [PRACTICAL_SELF_SIMULATION.md](PRACTICAL_SELF_SIMULATION.md)
and [COLONY_SIZE_TRADEOFF.md](COLONY_SIZE_TRADEOFF.md).

The new small_holder revision retains the protected parallel vote and verified
static temporary allocation from [PARALLEL_HOLDER.md](PARALLEL_HOLDER.md) and
[REUSE_HOLDER.md](REUSE_HOLDER.md). It changes colony size, clock widths and
schedule together, then describes the resulting complete raw transition in its
own ROM. This is a new construction revision, with one fixed rule, alphabet,
neighborhood and ROM at every initialized depth. Earlier revisions are preserved;
identity across those different research revisions is not claimed.

Candidate-B Flag2 maintenance and the old-Signal D10 timing interpretation remain
explicit source deviations. The altered schedule does not inherit a general
repair or amplification theorem merely by satisfying isolated time inequalities.

## Fixed parameters and measured budgets

The constants live in `gacsca/fixed_rule/small_holder_parameters.py`:

| Quantity | Fixed value |
|---|---:|
| Colony Q | 32,768 |
| Time placement quantum T | 33,554,432 |
| Work period U | 4,294,967,296 |
| Reset ages | 0, 8T, 16T, 64T, 68T |
| Active ends | 6T, 14T, 60T, 66T, 104T |
| Temporal vote ages | 22T, 68T |
| Computed-flag capture | 59T |
| Wf forcing interval | [64T, 64T+2Q) |
| Physical neighborhood | [-7,+7] |
| Complete raw state | 154 words / 4,090 bits |
| Program-projected state | 105 words / 2,704 bits |
| Coherent execution record | 25 words / 584 bits |
| Memory / instruction / end cells | 9,922 / 20,801 / 1 |
| Total computation cells | 30,724 |
| Complete raw descriptor operations | 13,442 |

Address and Age have 15 and 32 bits. Spatial addressing, packet flight, forcing
and flag fronts still use Q. Phase placements use T. This separation is present
in the scalar transition, full descriptor, native/event implementations and
symbolic certificates, rather than being a host-selected level schedule.
U/Q=131,072. Relative to the earlier Q=2^30, U=2^37 fixtures, Q falls by 32,768
and U by 32. The computation footprint plus five tail cells leaves 2,039 cells.

The three gather delivery margins are 38,013,602; 49,627,272; and 49,627,271
ticks. The final evaluation takes 1,167,972,849 ticks within a 1,207,959,552-tick
budget (39,986,703 spare). Including final delivery leaves 72,924,599 ticks
before capture. Same-track packet collision checks pass. Minimum rest is
67,108,864 ticks; Gray's local estimate 2Q+1100 is 66,636. Wf forcing remains
65,536 ticks, and the certified restricted flag front clears before the fifth
reset. These are checked construction inequalities, not a new noise theorem.

Complete descriptor SHA256:
`af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`.
Fixed ROM SHA256:
`13a54f15cde074f02f01407343ed7b618cd66c93aa76c47b29fe77651428248c`.

## Execution and distinguishing tests

The ROM evaluates the complete raw rule, including its evaluator/controller
fields. Program projection supplies fixed local program metadata; it does not
omit raw evolving controller state. Tests compare scalar, descriptor and native
transitions, require identical rule/ROM/schema at initialization depths 1–3,
guard neighborhood reads, exercise an active WRITE, and reject lost raw fields.
The accelerated physical executors have literal/native transition comparisons;
advance paths forbid host upper-rule/evaluator substitution. These checks and the
macrostep audits are evidence within their stated certified family, not a proof
of all possible initial configurations or arbitrary noisy histories.

The second work period starts from the first period's exact entire physical
state, carrying old Signals. The combined audit reports 8,589,934,592 physical
ticks (=2U), 15 represented cells, identical rule/alphabet/neighborhood/ROM and
40 changed raw controller fields in each decoded transition. Each complete
macrostep audit includes 2,232 local full-native transition samples. The represented
15 lower colonies occupy 491,520 physical sites. This is two successive periods
through one simulation link; it is not two nested links executing a top macrostep.

An ordinary homogeneous cap has a symbolic certificate for all 2^32 Ages and all
154 raw outputs (4,380 BDD nodes). Its Address is Q-1 and F1=F2=1, with zero
other dynamics except Age and required one-tick backup head/PC pulses after
reset/vote. This is an orbit of the ordinary rule, not a top-specific kernel.
It is neither an organized colony nor a noise-robust termination construction.

Exact commands and results (all from repository root):

```sh
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p 'test_small_holder_*.py' -v
# At this invocation, six integration files existed: 21 tests, 47.897 s, OK.
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_schedule.py -v
# 2 tests, 0.498 s, OK.
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_boundary.py -v
# 3 tests, 1.090 s, OK.
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_cuda_local.py -v
# 3 tests, 7.220 s, OK. Total: 29 distinct passing tests.
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_validation --prefix figs/fixed_rule/small_holder
# All nine execution/audit subprocesses exit 0; 81.982341 s wall time.
# Largest child RSS: 901,524 KiB. All terminal.
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.prove_small_holder_boundary --output figs/fixed_rule/small_holder_boundary_proof_v1.json
# Passed, 1.063948 s.
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_resources --output figs/fixed_rule/small_holder_resources_v1.json
# Passed, 1.223126 s; host maximum RSS 167,928 KiB.
```

The original wildcard invocation predates the three later test files; rerunning
it now collects all 29. Exact nine-stage subprocess commands, return codes and
wall times are in [small_holder_validation_v1.json](../../figs/fixed_rule/small_holder_validation_v1.json).
The terminal combined result is [small_holder_two_periods_audit_v1.json](../../figs/fixed_rule/small_holder_two_periods_audit_v1.json).
Execution archives include source snapshots and physical arrays; audit and test
logs retain the matching `small_holder_*_v1` stems under `figs/fixed_rule/`.

## CUDA and two-level resource limit

The private CUDA local kernel passes 200 CPU/GPU comparisons and 40 reconstructed
full-physical comparisons. Lossless packing retains all 25 coherent controller
fields in ten uint64 words; padding, field widths and domain restrictions are
checked. The kernel's domain is canonical coherent geometry with zero flags/Wf
before WF_START-1. It is not a full resident executor or a fault-capable state
representation. The resource driver performs a further bounded batch and records
1,874,144 bytes explicit VRAM (CUDA context additional), source/binary hashes and
167,928 KiB host RSS. No shared CUDA artifacts were rebuilt. Device compute-process
queries were empty before and after these small tests.

[small_holder_resources_v1.json](../../figs/fixed_rule/small_holder_resources_v1.json)
records the following estimates, not allocations:

| Depth-two cost per represented top cell | Amount |
|---|---:|
| Physical sites Q² | 1,073,741,824 |
| Physical ticks per top transition U² | 18,446,744,073,709,551,616 |
| Two dense projected-state buffers | 738,734,374,912 bytes |
| Hypothetical memory-cell Data bank only | 2,600,992,768 bytes |

For 15 top cells, Data alone would occupy 39,014,891,520 bytes. It excludes
controller, mail, exceptions/faults and event indices. This compact representation
has not been implemented or certified. Dense execution exceeds the A100's
capacity, and even fitting state would not make U² ticks practical. Future
horizon counters must also accommodate 2^64, beyond a uint64 scalar.

## Ownership and next concrete work

Owned additions are `small_holder_*` modules (Python, private C/CUDA), matching
`test_small_holder_*` tests, execution/audit/proof/resource drivers, their artifacts,
this report and STATUS.md, all within the authorized fixed_rule namespaces.
Existing sources and frozen fixtures remain unchanged. No shared patch is needed.
Main agent retains substantial GPU scheduling and should reply only in
`Report/fixed_rule/MAIN_AGENT_NOTES.md`.

1. Build a lossless execution representation with memory-cell Data, explicit
   controller/mail and certified implicit geometry/ROM. Test full physical
   reconstruction and local equivalence on active and recurrent states before
   allocating a large GPU state. Broken physical backups must remain representable
   for noise experiments; coherent packing alone cannot supply that property.
2. Develop periodic depth-two execution to avoid the old huge causal-window CPU
   allocation. Extend the suffix certificate beyond its current restricted
   Signals. Preserve exact physical transitions; executing the upper rule directly
   on the host is not evidence for nested physical execution.
3. Validate actual successive nested macrosteps with full controllers. A few
   decoded reset/head ticks do not constitute a full top-level work period.
   Obtain measured GPU time and memory; investigate certified event skipping and
   further evaluator optimization for the U² horizon.
4. Inject physical faults, measure recovery and failures at each decoded level,
   and distinguish targeted two-holder repair from stochastic robustness and
   Gács-style amplification. Reestablish the altered schedule's repair/trickle-down
   obligations and a robust termination construction before stronger claims.
