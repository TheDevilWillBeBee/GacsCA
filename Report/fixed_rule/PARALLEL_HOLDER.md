# Integrated protected parallel temporal vote

2026-09-26. This is a separate fixed-rule revision, not a depth-specific kernel.
The serial holder sources, artifacts and dependencies remain unchanged.

## Construction and closure obligations

The current holder already uses physical radius seven for its Wf backups. The
old reason for serial temporal voting was the radius-five obstruction described
in SERIAL_VOTE.md. Correcting the three temporal operands and updating all five
output backups requires physical offsets -5 through +6, which fit the current
neighborhood. The source basis is Gray's spatial protection of workspace and
procedures combined with temporal majority; this remains a modified explicit
Gacs/Gray-family implementation with candidate-B Flag2 and the prior D10 choice.

parallel_holder_core.py takes a local three-word majority at marked vote memory
cells at old Ages 72Q and 112Q. Reset happens first, voting overrides reset at
those cells, and final computed maintenance clearing retains priority. Each
backup uses its own hard-wired local vote marker and the holder's old geometry.
The full rule corrects logical Data out to offset +4 before updating its five
procedure copies. Other controller/mail operands retain their prior support;
no extra metadata record or physical register was added. Histories stay intact.

The complete 13,443-operation raw descriptor includes the changed clock/data
transition, every controller field and all five backups. SHA256:
a3c4a7c33310a9ee930c409691b0e1850830801da1ef67092cecbed6dd161cdc.
Its own ROM evaluates that descriptor and locally regenerates represented
metadata; it removes the 13,860 serial NAND instructions previously used for
voting. The projected physical alphabet remains 105 words / 2,724 bits, with
154 words / 4,110 bits in the raw descriptor including hard-wired metadata.
Radius remains seven. Depth-one, two and three initialization uses the same
physical identity, alphabet and ROM; deeper dynamics are not thereby established.

Q=2^30 and U=2^37 are temporarily unchanged to isolate this optimization. This
is not a renewed requirement that U/Q=128. Actual colony size and work period
have not yet decreased. The verified reference below is groundwork for choosing
a smaller layout and independently constrained schedule.

## Measured computation cost

| Quantity | Serial holder | Parallel holder |
|---|---:|---:|
| Computation-region cells | 57,332 | 43,808 |
| Complete descriptor operations | 13,275 | 13,443 |
| Evaluation ticks | 4,533,298,561 | 1,664,309,717 |

The evaluation takes about 63.3% fewer physical ticks; the computation region
uses about 23.6% fewer cells. The whole work period is still U. These figures
are not a 63.3% GPU speedup or a claim of practical two-level execution.
The complete timing certificate still includes all gathers, third-stage flag
delivery and capture deadlines; its fits result is true.

## Validation and preserved failures

    python -m unittest discover -s tests/fixed_rule -p 'test_parallel_holder_*.py' -v

At that point this ran 16 tests in 43.233 s, with 15 passes and one invalid test
fixture. That fixture asserted computed Flag1 must stay one after a single old
Flag1 corruption, but maintenance correctly removed it. The corrected fixture
supplies three right-hand Flag1 inputs and tests an actual clear operation.
No rule code changed in response. Focused rerun:

    python -m unittest discover -s tests/fixed_rule -p test_parallel_holder_vote.py -v

Three tests passed in 2.972 s. V1 failure and V2 success logs are retained.
Additional suffix/recurrent tests, using OPENBLAS_NUM_THREADS=1:

    python -m unittest discover -s tests/fixed_rule -p test_parallel_holder_suffix.py -v
    python -m unittest discover -s tests/fixed_rule -p test_parallel_holder_recurrent.py -v

Three suffix tests passed in 22.241 s; two recurrent tests passed in 7.194 s.
Together the logs provide passing coverage for 21 distinct tests, including:
120 arbitrary raw-neighborhood scalar/descriptor/native comparisons with forced
vote-clock cases; full raw encoding at three depths and exact descriptor-to-ROM
embedding; physical radius; protected vote/reset/clear precedence; simultaneous
physical voting and history preservation; 35 two-complete-holder corruption
cases recovering in two ticks; active WRITE repair; coherent execution conjugacy,
transport and skip-versus-literal comparisons; suffix transitions and rejection
of unsupported signals/mail; and a symbolic all-Address/all-front flag proof.
Three corrupted copies retain a negative witness outside the repair contract.
These are restricted repair tests, not general stochastic robustness.

## Actual local execution

The prefix advances 103,079,215,103 physical ticks in 7.705145 s and stops just
before Wf starts. It gathers all 154 raw fields from 15 distinct represented
cells, executes the parallel vote, evaluates the complete descriptor through
local controller instructions, delivers both flag values and captures Signals.
The run forbids calls to the host rule/evaluator while advancing dynamics.
Maximum measured host RSS was 737,472 KiB. Its independent audit passed.

The first suffix completed the macrostep in 20.623411 s, maximum host RSS
895,816 KiB. The independent macrostep audit passed in 7.360179 s: all raw
outputs, the exact physical prefix handoff, the symbolic flag trajectory,
2,229 saved complete-native local witnesses and the active controller changes.
The fixture represents 16,106,127,360 physical sites through 657,195 coherent
logical records plus exact transport/flag representations. It is restricted to
the documented coherent/right-one-left-zero family, not arbitrary noisy states.

The second prefix begins with the actual first commit, including all residual
controller fields and carried Signals. It completed in 7.902262 s at maximum
host RSS 873,276 KiB; its independent handoff/computation audit passed. Final
second-period results are appended below; all runs and audits are complete.

The first attempt to launch a macrostep with /usr/bin/time exited 127 because
that binary is absent. No simulation started in that attempt. Its log is
preserved; the same driver was then run with Python resource accounting.

Commands (all experiment commands use OPENBLAS_NUM_THREADS=1):

    python -m experiments.fixed_rule.parallel_holder_execution --output figs/fixed_rule/parallel_holder_execution_v1
    python -m experiments.fixed_rule.audit_parallel_holder_execution --input figs/fixed_rule/parallel_holder_execution_v1 --output figs/fixed_rule/parallel_holder_execution_audit_v1.json
    python -m experiments.fixed_rule.parallel_holder_macrostep --prefix figs/fixed_rule/parallel_holder_execution_v1 --output figs/fixed_rule/parallel_holder_macrostep_v1
    python -m experiments.fixed_rule.audit_parallel_holder_macrostep --input figs/fixed_rule/parallel_holder_macrostep_v1 --output figs/fixed_rule/parallel_holder_macrostep_audit_v1.json
    python -m experiments.fixed_rule.parallel_holder_recurrent_execution --previous figs/fixed_rule/parallel_holder_macrostep_v1 --output figs/fixed_rule/parallel_holder_recurrent_execution_v1
    python -m experiments.fixed_rule.audit_parallel_holder_recurrent_execution --input figs/fixed_rule/parallel_holder_recurrent_execution_v1 --output figs/fixed_rule/parallel_holder_recurrent_execution_audit_v1.json

Memory-instrumented runs invoke the same module using runpy.run_module with
run_name='__main__', then print resource.getrusage(RUSAGE_SELF).ru_maxrss.
Source archives, full output arrays and audit records use the matching artifact
stems under figs/fixed_rule. Source hashes include every then-present fixed_rule
Python/C/C++/header/CUDA module, test and experiment, not the mutable reports.

## Next work and remaining limits

A diagnostic last-use analysis of the 13,443-operation descriptor, retaining all
outputs until the end, found at most 240 live result words. The current ROM
layout allocates 13,443 separate result cells. A reusable temporary allocator
could reduce workspace and sweep distance without changing operation semantics.
This measurement is not yet an allocated, executed or validated replacement.
Then reassess compact instruction encoding/loops and the separate communication,
repair and computation budgets before selecting a smaller Q and independent U.

No full depth-two or depth-three macrostep has been executed. No general noisy
execution, cross-level amplification or noise-robust termination is established.
A practical GPU implementation needs explicit faults and broken backups, not
only the coherent quotient. The complete project goal remains open.

Owned files: new parallel_holder_* modules/adapters/tests/experiments and results,
this report and STATUS.md. No shared modules, historical dependencies, CUDA
artifacts or protected GPU job were modified. No substantial GPU work launched.
MAIN_AGENT_NOTES.md was absent; main agent can reply there. No matching
third_link_initialized process was found during the read-only process check;
that observation does not establish successful completion of the old job.

## Completed second period and combined audit

The second suffix completed in 20.905057 s at maximum host RSS 893,844 KiB.
Its independent audit passed in 7.638879 s, again checking 2,229 full native
transition witnesses. The combined audit passed: 274,877,906,944 physical ticks,
identical rule/alphabet/neighborhood/ROM, exact entire physical-state handoff,
carried old Signals, and 40 changed raw controller fields in each represented
transition. These are two successive **one-link** macrosteps, not depth-two
dynamics. All runs are terminal. No goal-completion claim is made.

    python -m experiments.fixed_rule.parallel_holder_macrostep --prefix figs/fixed_rule/parallel_holder_recurrent_execution_v1 --output figs/fixed_rule/parallel_holder_second_macrostep_v1
    python -m experiments.fixed_rule.audit_parallel_holder_macrostep --input figs/fixed_rule/parallel_holder_second_macrostep_v1 --output figs/fixed_rule/parallel_holder_second_macrostep_audit_v1.json
    python -m experiments.fixed_rule.audit_parallel_holder_two_periods --first figs/fixed_rule/parallel_holder_macrostep_v1 --second-prefix figs/fixed_rule/parallel_holder_recurrent_execution_v1 --second figs/fixed_rule/parallel_holder_second_macrostep_v1 --output figs/fixed_rule/parallel_holder_two_periods_audit_v1.json

The liveness diagnostic is recorded in parallel_holder_liveness_v1.json with
the exact descriptor hash and counting convention. Reproduction: assign each
operation result a live slot, keep outputs live until completion, then release
operand wires on their last use. Count only operation results, excluding inputs.
Peak simultaneous results = 240. No allocator or memory saving is yet claimed.
