# Retimed GPU packet communication and successive complete periods

2026-09-26. The unchanged fixed retimed rule now executes **two complete
successive work periods on 15 nonaliasing physical colonies**, starting with only
Info initialized. Actual physical SEND events gather every history; temporal
voting, both computations, Signal delivery/capture, restricted flag evolution,
commit and rollover occur in one retained device state. No state is reinitialized
between periods. This establishes two macrosteps at one simulation link, not a
complete work period of the next hierarchy level.

## Results and scope

| Physical colonies | Complete periods | Represented physical ticks | GPU evolution | Whole experiment | Explicit device peak |
|---|---:|---:|---:|---:|---:|
| 1 | 2 | 4294967296 | 25.688208 s | 26.376896 s | 2866912 bytes |
| 15 | 2 | 4294967296 | 32.609045 s | 33.557215 s | 6160272 bytes |

The 15-colony process reported peak host RSS 192168 KiB; the watchdog sampled
190892 KiB. All processes stayed below the 512 MiB sampled threshold and 60 s
wall limit. The previous CPU reference took 696.240266 s. That is useful practical
context, not a controlled hardware speedup: the CPU experiment also performed
complete raw per-site boundary transitions/entry validation, while this GPU
comparison uses the coherent physical representation and checks complete saved
states. Both backends already skip justified travel/quiet intervals.

All three actually gathered histories are checked at each gather completion.
The first and final Hold values agree with the intended full raw simulated
transition. All five right Signal-buffer inputs and the left-zero capture input
are checked before capture. At both commits every actual MEM/tail Data word,
controller, packet and persistent Signal record equals the frozen CPU state.
Canonical Address, common Age and the fixed metadata/replica representation
complete the physical-state comparison; this is not merely decoded Info equality.
The CPU reference's full entry-relation validation covers 491520 physical sites
at each boundary. The GPU audit independently checks the complete compact state
that reconstructs the same physical configuration, rather than dumping all raw
replicas again.

Independent scalar and complete-descriptor oracles agree with all 2310 raw Info
words at each 15-colony commit, including raw evaluator/controller fields.
Seventy upper controller words change in the first step and 65 in the second.
The one-colony pilot has only two then zero controller changes and is not used
as nonaliasing active-controller evidence.

The 15-colony run used 10928 accepted event batches, zero rejected batches,
5180388 colony event ticks, 13376664 logical local evaluations, 18 synchronous
boundary ticks and 256967292 synchronous quiet/travel ticks. The total accounting
sums to exactly 2U. Every stored word survives between calls. Host scalar/full
rule evaluation and `Program.evaluate` throw if invoked during GPU evolution.
Oracles and diagnostic decoding operate outside that evolution.

## Implementation and retained failure

New `retimed_holder_resident_mixed.py` uses the previously established mixed-right,
left-zero coherent flag family. New `retimed_holder_resident_gather.py/.cu` retains
actual packet births, values, locations, tracks and hop counts. Deferred deliveries
are allowed only into protected foreign histories or Signal buffers; conflicting
controller accesses and same-track birth collisions reject the staged batch.
The right track wins a simultaneous receive tie. A bounded 15-colony source halo
covers at most seven consumed hops. Both modulo-small rings and a 17-colony ring
are tested. The existing retimed period/independent kernels and full physical
rule/ROM remain frozen.

The first whole-period pilot failed the complete-state check although its final
Data and computed output were correct: five persistent Signal records were absent.
Isolating literal capture, mixed flag fronts, active flagged controllers and wrap
showed those transitions matched full F. The added Signal-buffer packet support
had retained the old history-only destination indexing. It wrote to physical
address `target` in a compact bank, instead of `bankrow(target)`. For example,
Q-3=32765 is outside the 9916-word one-colony bank; the valid compact index is
9913. This was a new execution-adapter error, not a change to the rule or ROM.

The corrected delivery maps every protected destination through `bankrow` and
rejects an invalid mapping. Tests now complete actual arrivals at 1, 3, 5, Q-5,
Q-3 and Q-1 from both directions, including a wrapped hop. Earlier short SEND
checks only observed packets before those arrivals. The failed pilot log,
watchdog receipt, original adapter/driver/test sources, and old compiled library
are preserved. Successful old packet tests do not establish the expanded domain.
A focused CUDA memcheck of the corrected arrivals reports **zero errors**; that
memory check is scoped to those arrival cases, not all possible CUDA executions.

## Validation and exact runs

The evidence/source index is
`figs/fixed_rule/retimed_holder_cuda_periods_evidence_v1.json`.

- Five actual-GPU packet tests: 3.631 s. Complete Data/live-state comparison with
  CPU plus literal raw-F cones; every hop count/direction, repeated laps, receive
  priority, SEND payloads, Signal-buffer arrivals, segmentation, collision and
  protected-access rejection.
- Three GPU profile tests: 22.613 s. Complete raw literal capture, forcing/front
  cutoff and clearing, wrap, and active controller under a nonzero flag profile.
- Independent period audits: one colony 0.553394 s/59556 KiB; fifteen colonies
  1.053014 s/73684 KiB. Both scalar and descriptor references, complete compact
  physical checkpoints, decoded identities, source/binary/artifact hashes pass.
- Five audit rejection tests: 1.014 s. Lost Signals with correct Info, residual
  controllers, unrelated Data corruption and a raw rb fault inserted into both
  GPU and CPU stored outputs are rejected. The last case distinguishes the
  independent upper-rule oracle from simple backend agreement.
- CUDA memcheck: one focused test, 1.545 s, zero errors. Entire owned sanitizer
  process family peaked at sampled 223116 KiB; 2.112669 s wall time.

Private builds use `ulimit -v 1048576`; CPU-only audits/tests use
`ulimit -v 524288`. All use `OPENBLAS_NUM_THREADS=1`. CUDA runtime shells do not
use RLIMIT_AS because device virtual-address reservations are large. Watchdogs
sample physical RSS every 20 ms, which is not an instantaneous OS memory cap.
The sanitizer watcher includes its child process family. Explicit device budgets
are 32 MiB resident plus 32 MiB staging; driver/context overhead is additional.

```sh
python -m experiments.fixed_rule.build_retimed_holder_gather_cuda --output figs/fixed_rule/retimed_holder_gather_cuda_build_v2.json
FIXED_RULE_GPU_TESTS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_cuda_packets_watch_v2.json --seconds 60 --rss-mib 512 -- python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_cuda_packets.py -v
FIXED_RULE_GPU_TESTS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_cuda_profile_watch_v1.json --seconds 60 --rss-mib 512 -- python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_cuda_profile.py -v
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_cuda_periods1_watch_v2.json --seconds 60 --rss-mib 512 -- python -m experiments.fixed_rule.retimed_holder_cuda_periods --reference figs/fixed_rule/retimed_holder_cpu_periods_pilot_v2.json --output figs/fixed_rule/retimed_holder_cuda_periods1_v2.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_cuda_periods15_watch_v1.json --seconds 60 --rss-mib 512 -- python -m experiments.fixed_rule.retimed_holder_cuda_periods --reference figs/fixed_rule/retimed_holder_cpu_periods_15_v1.json --output figs/fixed_rule/retimed_holder_cuda_periods15_v1.json
python -m experiments.fixed_rule.audit_retimed_holder_cuda_periods --input figs/fixed_rule/retimed_holder_cuda_periods15_v1.json --output figs/fixed_rule/retimed_holder_cuda_periods15_audit_v1.json
python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_cuda_period_audit.py -v
FIXED_RULE_GPU_TESTS=1 python -m experiments.fixed_rule.bounded_cuda_process_tree --output figs/fixed_rule/retimed_holder_cuda_tail_memcheck_watch_v1.json --seconds 60 --rss-mib 512 -- /usr/local/cuda/bin/compute-sanitizer --tool memcheck --error-exitcode 99 python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_cuda_packets.py -k actual_tail -v
python -m experiments.fixed_rule.retimed_holder_cuda_depth_cost --output figs/fixed_rule/retimed_holder_cuda_depth_cost_v2.json
```

The one-colony audit substitutes `...periods1_v2.json` and
`...periods1_audit_v1.json`. Every receipt/log is retained; reruns must use new
output names. Private builds live in hash-addressed `figs/fixed_rule/build` paths.

## Depth cost and remaining objective

Q=32768, U=2^31, radius seven, raw 154 words/4090 bits and projected 105
words/2704 bits remain unchanged. The new adapters introduce no depth dispatch,
self-description replacement or extra physical registers. The complete descriptor
and ROM identities remain those in [RETIMED_HOLDER.md](RETIMED_HOLDER.md).

The actual allocation formulas, checked against measured allocation counters,
are 2631672 fixed bytes plus 154368 bytes per physical colony and at most 80872
staged bytes per colony. For two encoded levels, one top cell gives 32768 lower
colonies and **7.181406 GiB** explicit peak; fifteen top cells give 491520 lower
colonies and **107.686777 GiB** peak. These are algebraic projections, not new
allocations or measured nested execution. CUDA overhead and other jobs need
additional headroom. Current API caps also reject allocations above 8 GiB per
base/staging request. The historical hand calculation is retained as depth-cost
v1; reproducible v2 additionally records API caps and its source hash.

A complete upper work period still requires U^2=2^62 represented physical ticks.
The new one-link timings must not be multiplied into an asserted practical
nested-runtime result. Reduce layout/staging costs and establish further exact
acceleration or a cheaper construction before claiming practical depth two.
The separate 8 GiB substantial-GPU reservation remains pending and unused.

General both-sided Signal/flag trajectories and literal faults have CPU reference
support but are not yet ported here. GPU cross-level error-correction experiments,
noise amplification, malformed-Info repair and reliable finite-cap behavior are
still open. Candidate-B Flag2, voted-old-Signal D10 and printed-source ambiguities
remain explicit limitations. All private runs are terminal and the A100 had no
compute processes at the final check. No shared sources, GPU jobs or historical
artifacts were modified. The full project goal remains active.
