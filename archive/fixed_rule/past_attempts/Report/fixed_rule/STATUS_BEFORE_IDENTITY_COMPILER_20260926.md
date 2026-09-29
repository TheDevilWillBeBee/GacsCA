# Fixed-rule agent status

Updated 2026-09-26. **Full Gacs/Gray goal active; not complete.** Please reply in
**Report/fixed_rule/MAIN_AGENT_NOTES.md**; this agent never edits that file. It
was absent at the latest check. No shared change is requested.

## Priorities and ownership

Correct actual fixed-rule self-simulation; practical two-level A100 execution;
measured error correction across levels. Optimize Q/U subject to correctness;
U<=128Q is not required. Host memory remains bounded. Coordinate substantial
GPU work with the main agent; the separate 8 GiB request remains pending/unused.
Only owned fixed_rule namespaces and this STATUS were edited. No GPU job,
shared source, CUDA artifact or historical dataset changed.

## Latest progress: physical skip-distance audit and execution cost

[BACKEND_DISTANCE_AND_COST.md](BACKEND_DISTANCE_AND_COST.md) audits the verbatim
CUDA flight-distance function in a private CPU build: 5223948 breakpoint cases
pass; overshoot and wrong-register mutations fail. The finite target/Address
argument is explicit. All eight phases, both directions and metadata value
classes are covered; no WAIT record exists in the fixed ROM. Unused target
registers are distinct in v2; the weaker tied-register v1 is preserved.
This validates distance only, not packet staging, driver clock guards or the
complete accelerated backend. No GPU run or CUDA rebuild occurred.

Exact replay counts 34526 instructions and 2802642834 controller-path ticks per
colony period. The current layout needs at least 30729 cells, so Q=32768 and
U=2^32 are already the smallest power-of-two sizes for this particular serial
layout. Shrinking margins alone cannot halve them. The current depth-two
per-instruction strategy entails 4859102522956054528 instruction occurrences.
This is work arithmetic, not a GPU time prediction or a universal lower bound.

The actual compressed full-ring allocation/staging estimate remains about
7.14 GiB (pending 8 GiB reservation); 338 GiB is the dense packed alternative.
The 256-worker event launch is a possible tuning target but cannot by itself
remove the billions of lower periods. No new GPU scheduling request was issued.

New owned sources: certify_small_holder_backend_distance.py,
certify_small_holder_backend_distance_independent.py,
measure_small_holder_execution_budget.py under experiments/fixed_rule;
BACKEND_DISTANCE_AND_COST.md; matching results/private CPU builds. v2 audit:
1.936501 s /60044 KiB RSS; exact budget: 1.481112 s /87400 KiB. Both used a
512 MiB virtual-memory cap and exited zero. Commands/hashes/limits are in the
report. MAIN_AGENT_NOTES.md remains absent; existing reservation is unused.

## Prior verified result: noiseless macrostep composition

[NOISELESS_MACROSTEP.md](NOISELESS_MACROSTEP.md) gives the certificate-assisted
physical induction for F^U(E(y)) subset E(G(y)), G=pi F iota, at complete word-
descriptor semantics. It covers arbitrary typed upper controllers, retained
physical scratch/Signals, both evaluations, actual packets, every quiet barrier,
flag clearing and commit; no extra reset is counted. Open-lattice dependence and
modulo-Q packet geometry extend the argument to every positive upper ring size.
Projection then gives G simulating G with the same alphabet and ROM at every
finite encoded depth. This is a mathematical proof using checked lemmas, not a
proof-assistant development or a new full-period/nested execution. Backend
agreement retains the scope of its existing differential audits.

New executable checks:

- Open Data flow: 45 access-disjointness checks, all 154 central outputs,
  2.107540 s /89704 KiB peak RSS.
- Period interfaces and alphabet closure, v2: six phases, all 154 output widths,
  ten guarded decrement refinements; 1.777067 s /94228 KiB.
- Fixed ROM/fallback typing: 229376 values; seven overwide mutations rejected;
  1.307523 s /58436 KiB.
- Seven focused tests passed in 2.704 s. They distinguish missing/wrong guards,
  incorrect routing, dependence on wrapped destination labels, overwide outputs
  and missing/late phase conditions.

Runs used a 512 MiB virtual-memory cap; all are terminal. Exact commands, files,
hashes, proof steps and caveats are in the report. The initial composition v1
failure and source snapshot remain preserved: a conservative bit bound could
not prove guarded decrement safe. The new abstraction proves its nonzero guard;
no physical rule, descriptor, alphabet, parameters or ROM changed. Temporary
approval timeouts interrupted the previous turn; command access worked again.

Owned new sources: experiments/fixed_rule/certify_small_holder_open_dataflow.py,
compose_small_holder_noiseless_period.py, small_holder_guarded_bounds.py,
certify_small_holder_rom_types.py; tests/fixed_rule/test_small_holder_noiseless_period.py;
Report/fixed_rule/NOISELESS_MACROSTEP.md and matching owned evidence artifacts.

## Remaining work

Next complete the event backend staging/clock/reconstruction audit, then implement and
measure practical full depth-two execution. Current Q=32768, U=2^32 costs remain
large: Q^2 sites require 338 GiB for one dense packed projected buffer, and a
depth-two decoded step represents 2^64 physical ticks. The proof does not make
that workload practical or authorize arbitrary host transition replacement.
No new substantial GPU allocation was used.

Cross-level error correction, noisy amplification and reliable finite-cap repair
remain unproved. Candidate-B Flag2, old-Signal D10, the printed Flag2/SimBit source
issues and the cap Address-defect witness remain explicit limits. Existing
physical evidence includes two one-link periods and limited nested windows,
not a complete upper work period at depth two. The last historical third-link
check found no process; this is not a completion audit. It was untouched.

[PERIOD_ENTRY_AND_TIMED_DATAFLOW.md](PERIOD_ENTRY_AND_TIMED_DATAFLOW.md) retains
entry/timed/query proofs; linked structural, mail, context/barrier and Signal
reports retain the local lemmas. Their historical stand-alone limitations are
not retroactively overwritten by the new composition argument.

The previous compact handoff is preserved in
[STATUS_BEFORE_NOISELESS_MACROSTEP_20260926.md](STATUS_BEFORE_NOISELESS_MACROSTEP_20260926.md).
Older history remains in STATUS_HISTORY_20260926_before_mail_factorization.md.

Preceding handoff preserved in STATUS_BEFORE_BACKEND_DISTANCE_20260926.md.
