# Timed repair at an actually executed evaluator checkpoint

2026-09-27. The unchanged fixed physical rule now has a non-vacuous timed
controller-fault experiment at a state reached by actual colony computation.
This extends the targeted initial-encoding experiments; the full project goal
remains active. No rule, ROM, alphabet, CUDA kernel or shared source changed.

## Executed behavior

One physical colony starts at the canonical encoding of `parents(1)` from the
existing CPU fixture. Its complete gathering, first computation, signal capture,
maintenance and final computation execute on the existing general GPU backend.
The checkpoint is Age **1232619428**, immediately before the operand-B read of
final-stage ROM instruction **7075**, `NAND(9564,9565)->9566`. The actual head is
at Address 9565 with phase READ_B. This state is not manufactured by assigning
controller registers. The top fixture is a periodic one-cell state; it is not a
canonical top colony or a robust cap.

Two physical bit faults change `s0_rb` at site 9567 and `s1_rb` at site 9566,
each by xor 1. These are two replicas of the same running controller's operand.
The full radius-seven GPU rule evaluates every affected output. After one tick,
all exceptions disappear and the complete physical state agrees with the
independently evolved healthy state. The actual head proceeds to WRITE and
carries the expected NAND result. The repaired trajectory then continues through
the rest of the work period; every bank word, active record, Signal and flag
matches at U=2147483648. No Data or flag rebase is used, and the healthy successor
is never installed in the damaged world.

The negative control additionally changes `s2_rb` at site 9565. The same literal
GPU transition leaves five exceptional physical holders and **15 different raw
output words**. The head retains READ_B with the wrong operand address. Thus the
experiment distinguishes actual repair from a discarded or unexecuted fault.

| Case | Physical bit faults | Affected output sites | Full local evaluations | Different output words |
|---|---:|---:|---:|---:|
| Two replicas | 2 | 16 | 32 | 0 |
| Three replicas | 3 | 17 | 34 | 15 |

Evaluations include the actual and counterfactual background transition. The
counterfactual state is not used as a replacement for the actual successor.

## Complete checkpoints and independent checks

`retimed_holder_active_snapshot.py` supplies read-only raw reconstruction and
exact checkpoint upload for the late, zero-flag, mail-free execution domain.
It retains every live controller and transport field. It validates widths,
sorted unique addresses, Data consistency, flags, localized Signals and clocks
before restoration. Earlier forcing epochs and nonempty mail are rejected by
the restore interface. The diagnostic renderer can retain arbitrary live mail;
this does not extend the backend's restoration domain.

The artifact retains full raw middle states at ages a-1, a, a+1 and a+2, along
with their complete storage snapshots, literal fault frontiers and both complete
terminal snapshots. Raw reconstruction is checked against GPU readback around
the active computation and all relevant storage interfaces. Exact restoration
is compared field for field before either fault case.

A separate native CPU execution of the complete F descriptor checks **every
154-word physical state at all 32768 sites** for three successive healthy ticks
and both faulty ticks: **25231360 raw output words** in total. All match. Its
whole-lattice fault checks also verify that outputs outside the causal frontier
are unchanged. At canonical geometry, the native F output metadata already
agrees with G=pi F iota. The independent scalar source transcription is checked
at all 33 affected outputs across the two fault cases in the GPU driver.
These checks establish backend parity for this trajectory, not an independent
proof of the descriptor's entire mathematical/source fidelity.

Four CPU tests cover complete live-field preservation through periodic
boundaries, malformed/incomplete snapshots, resource/clock guards, and rejection
of unsupported mail before GPU allocation. They passed in **1.719 s**.

## Commands and measured resources

From the repository root, with `OPENBLAS_NUM_THREADS=1`:

```sh
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_active_evaluator_faults_v1_watch.json --seconds 90 --rss-mib 1024 -- python -m experiments.fixed_rule.retimed_holder_active_evaluator_faults --output figs/fixed_rule/retimed_holder_active_evaluator_faults_v1.json
python -m unittest tests.fixed_rule.test_retimed_holder_active_snapshot -v
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_active_evaluator_audit_v1_watch.json --seconds 60 --rss-mib 1024 -- python -m experiments.fixed_rule.audit_retimed_holder_active_evaluator --input figs/fixed_rule/retimed_holder_active_evaluator_faults_v1.json --output figs/fixed_rule/retimed_holder_active_evaluator_audit_v1.json
```

All commands exit 0. Driver wall time **21.491857 s**, reported host peak
**425956 KiB**, sampled peak **408108 KiB**, conservative explicit GPU peak
**24232408 bytes**. Audit **5.984145 s**, reported host peak **397728 KiB**.
CUDA runtime uses sampled RSS rather than a virtual-address limit. The existing
private GPU binaries are reused; no new compilation or sanitizer run occurred.
These allocations are far below the user's 40 GB host ceiling and do not use
the pending substantial GPU reservation. No protected/shared GPU job was touched.

Evidence: `figs/fixed_rule/retimed_holder_active_evaluator_faults_v1.json`, its
NPZ, `retimed_holder_active_evaluator_audit_v1.json`, test/watch logs, and
`retimed_holder_active_evaluator_evidence_v1.json`.

## Source relation and remaining work

This tests the explicit five-replica procedure protection of the owned modified
rule. Gray pp. 31–32 justify specialized hard-wiring after ProgramBit projection;
Gacs 9.2–9.3 allow the identical or suitably modified self-correcting rule. Neither
source licenses calling this small deterministic experiment a proof of general
amplification. Candidate-B Flag2, voted-old-Signal timing, malformed encoding,
geometry/cap recovery and broader source-fidelity limitations remain as recorded
in the inherited reports. Q/U and the complete self-description are unchanged.

The new complete checkpoints support the next concrete cross-level experiment.
If M_j is the actually executed middle trajectory from E(top), the complete
noiseless bottom checkpoint at time aU is B(M_(a-1)), whose Info is M_a. Stream
that full bank with the already verified endpoint operator, apply explicit
physical bottom faults to its Info, and test the next lower period against the
actual healthy M_(a+1). This would place the encoded fault during real middle
computation, with inherited scratch, rather than restart from E(M_a). That
encoded-bottom experiment **has not run yet**. General timed stochastic noise,
full-alphabet recovery, depth three, nonaliasing top colonies and robust caps
remain open.
