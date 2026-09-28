# Compact16 successive physical periods

2026-09-27. A private CPU event executor completed two successive compact-rule
periods on three colonies (49152 physical sites), retaining one evolving state.
Both decoded results match scalar G and its complete descriptor, and every
physical site satisfies the full entry relation after each commit. Physical
time is 2147483648 ticks; measured evolution took 36.673080 s. Initialization,
diagnostics and full-ring validation bring the run to 101.193252 s.

This is an accelerated physical execution on a checked canonical domain, not
2U dense synchronous sweeps. It is also not a complete depth-two work period.
The small upper ring has noncanonical geometry: its first simulated transition
clears the initially active controller. Sustained active upper computation is
not demonstrated by these two periods; the next fixture addresses that limitation.

## Executor and what actually evolves

Rule, ROM, alphabet, radius, Q=16384 and U=2^30 are unchanged from
[the compact period argument](COMPACT16_NOISELESS_MACROSTEP.md). Private new
`compact16_holder_cpu_events`, `_cpu_gather`, `_cpu_boundary`, `_cpu_general` and
`_flags_cpu` sources were adapted from the frozen retimed execution references.
Build products stay under `figs/fixed_rule/build/compact16_*`. The quotient module
reuses only immutable record-schema constants, exporting no old-rule evolution.

The execution representation stores each colony's Data bank, complete head and
controller/location, actual packets, both coherent captured Signal bits, and
every physical Flag1/Flag2 bit. Full raw cells are reconstructed locally with
fixed metadata, canonical Address/Age, coherent procedure copies, and the
derived Wf fields. These are execution-domain restrictions, not a smaller
physical alphabet or a depth limit. Its colony-count bound is a resource limit.

Every nontrivial controller event calls the complete native F compiled from the
current descriptor. The independent flight-distance check covers 2557336
breakpoint cases for the new ROM, all eight phases, both directions and independent
target registers; overshoot and wrong-register mutations fail. The actual ROM
has no WAIT. Between these breakpoints the inspected distance and next-event
oracle are affine in Address. Regular-clock guards prevent flight across a
reset, vote, capture or commit boundary. This check is not a universal backend
equivalence proof, but supplies the distance obligation for the recorded domain.

Packet payloads come from actual F outputs. Packets move with their physical
direction/hop count and deliver at computed arrival times. Deferred delivery is
permitted only at protected MEM locations; any controller read/write there in
the staged interval rejects atomically. Colliding emissions and capacity failures
also reject. Both Signal buffer groups and the sparse foreign history slots are
protected: exactly 1786 unique destinations, equal to the actual SEND targets.
The old dense address formula is incorrect for this layout and was replaced by
a table derived from the fixed sparse layout. Info, Hold, votes and local history
operands are excluded; the table never depends on initialized depth.

Every clock boundary streams the full local F over every physical site from
the old state. Flags advance by the exact packed radius-five recurrence with
candidate-B Flag2 and both Signal sides. Run compression is lossless; temporal
skips require an observed fixed point and stop at forcing-window boundaries.
No assumed front speed is used. The context factorization justifies evaluating
procedure events independently of retained flags/Signals. Mail during nonzero-
flag/forcing intervals is unsupported and rejects; the tested period schedules
have none. Malformed geometry, incoherent procedure copies, arbitrary controller
residues and general noisy executions require another representation.

During every physical advance, Python `f.local_step`, projected `r.local_step`,
`native.local_step`, and `Program.evaluate` are patched to raise. Actual C calls
to the native full-rule symbol remain available. Expected upper transitions are
computed only outside evolution, for diagnostics. Initial histories are zero;
the engine fills them by actual gather dynamics. No boundary is reinitialized.

## Results and scope of the fixture

Each gather checks every collected history operand, and both evaluations check
all 154 Hold fields. Commit checks all raw Info fields and runs the complete
49152-site entry validator. Both Signal sides become [1,1,1] and are retained
across periods; all physical flags clear before commit. Saved bank/Signal/flag
arrays and final controller/mail are audited without rerunning the executor.

| Quantity | Result |
|---|---:|
| Represented physical ticks | 2147483648 |
| Complete native local evaluations | 3012954 |
| Controller event ticks, summed over colonies | 842388 |
| Controller travel ticks, summed over colonies | 4914112494 |
| Actual emitted / delivered packets | 10716 / 10716 |
| Dropped / remaining packets | 0 / 0 |
| Explicit packed-flag ticks | 54624 |
| Packed flag-word evaluations | 1386714 |
| Changed represented words, period 1 / 2 | 59 / 6 |
| Changed represented controller words, period 1 / 2 | 35 / 0 |

The upper fixture starts at Addresses 0,1,2 on a three-cell ring, with one READ_B
controller and Flag2=1. Its geometry is not a full Q colony. Scalar/descriptor
diagnostics agree that the first step changes Addresses to Q-3,Q-2,Q-1 and clears
the procedure state; the second step continues geometry/clock dynamics. This is
a valid arbitrary-typed-upper self-simulation test and exercises physical
two-sided capture/forcing, but it is not sustained upper arithmetic or a noise
repair experiment. No robustness inference is made from the clearing.

`compact16_holder_active_fixture.py` preflights the next 31-cell upper ring,
with a larger canonical neighborhood around its central active head. Diagnostic
G steps give READ_B at 15, WRITE at 16 with value18442167835445667631, then FETCH
at17/PC24 while Data at16 receives that value. Its lower representation will have
507904 sites. This is initialization and diagnostic planning only: zero physical
periods have yet been executed for that fixture. A compact GPU backend is the
next target for that run and later depth-two work.

## Checks and resources

Twenty-one tests pass: twelve controller/general-context cases, seven packet
cases and two sparse-target/artifact mutation cases. They include full raw literal
cones for controller events, every bit in selected packed words at colony edges
and interiors, both captured Signals, active control under arbitrary flags,
fixed-point skip versus literal flag recurrence, all hop counts/directions and
repeated ring laps, right-delivery priority, SEND birth, segmented live packets,
and atomic domain/budget/collision rejection. Mutations reject missing raw PC,
wrong represented metadata, either wrong Signal, residual flags, non-MEM Data and
truncated snapshots. These tests complement, rather than replace, the documented
domain argument; they do not prove general parity for every raw neighborhood.

| Check | Result | Seconds | Watch seconds / sampled child KiB |
|---|---|---:|---:|
| Distance audit and mutations | PASS | 2.581596 | 2.943031 / 43060 |
| Controller/context tests | 12 PASS | 10.534 | 10.839210 / 50692 |
| Packet tests | 7 PASS | 2.923 | 3.526022 / 45692 |
| Two physical periods | PASS | 101.193252 | 101.582434 / 51556 |
| Independent snapshot audit | PASS | 0.403373 | 0.648958 / 43608 |
| Guard/artifact tests | 2 PASS | 0.326 | 0.791330 / 42620 |

All jobs exit0. The main run's self peak is50880 KiB; watchdog samples exclude
parents and compiler subprocess peaks. CPU usage stayed far below the40GB task
allowance. The 5502-byte compressed snapshot is small because most boundary
Data is zero; this is not the runtime allocation size. No GPU was used or CUDA
artifact rebuilt. Initial read-only process/GPU checks found no third-link or
fixed-rule jobs and no GPU compute process; no shared job was stopped or changed.

Commands, from the repository root (each preserves existing outputs):

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_holder_backend_distance_v1_watch.json --seconds 120 --rss-mib 768 -- python -m experiments.fixed_rule.certify_compact16_holder_backend_distance --output figs/fixed_rule/compact16_holder_backend_distance_v1.json > figs/fixed_rule/compact16_holder_backend_distance_v1.log 2>&1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_holder_cpu_tests_v1_watch.json --seconds 180 --rss-mib 768 -- python -m unittest tests.fixed_rule.test_compact16_holder_cpu_events tests.fixed_rule.test_compact16_holder_cpu_general -v > figs/fixed_rule/compact16_holder_cpu_tests_v1.log 2>&1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_holder_packet_tests_v1_watch.json --seconds 120 --rss-mib 768 -- python -m unittest tests.fixed_rule.test_compact16_holder_cpu_gather -v > figs/fixed_rule/compact16_holder_packet_tests_v1.log 2>&1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_holder_cpu_periods_v1_watch.json --seconds 240 --rss-mib 768 -- python -m experiments.fixed_rule.run_compact16_holder_cpu_periods --colonies 3 --periods 2 --output figs/fixed_rule/compact16_holder_cpu_periods_v1.json > figs/fixed_rule/compact16_holder_cpu_periods_v1.log 2>&1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_holder_cpu_period_audit_v1_watch.json --seconds 60 --rss-mib 512 -- python -m experiments.fixed_rule.audit_compact16_holder_cpu_periods --execution figs/fixed_rule/compact16_holder_cpu_periods_v1.json --output figs/fixed_rule/compact16_holder_cpu_period_audit_v1.json > figs/fixed_rule/compact16_holder_cpu_period_audit_v1.log 2>&1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_holder_execution_audit_tests_v1_watch.json --seconds 60 --rss-mib 512 -- python -m unittest tests.fixed_rule.test_compact16_holder_execution_audit -v > figs/fixed_rule/compact16_holder_execution_audit_tests_v1.log 2>&1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.compact16_holder_active_fixture --output figs/fixed_rule/compact16_holder_active_fixture_v1.json
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.seal_compact16_holder_execution
```

Next: private compact GPU implementation and validation, the preflighted sustained
upper-computation fixture, then practical initialized depth two and cross-level
faults. Large dense U^2 stepping is still impractical. General amplification,
damaged-encoding repair, robust boundary termination, depth three and source
qualifications remain open. Full project goal active; no shared changes requested.
