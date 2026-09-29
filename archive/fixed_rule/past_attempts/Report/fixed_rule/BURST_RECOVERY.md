# Quiet recovery after the higher-intensity physical burst

2026-09-27. The exact damaged state from [POISSON_BURSTS.md](POISSON_BURSTS.md)
has now run for another 16384 fault-free physical ticks. Flag1 clears completely
after 15453 ticks. At tick 16384, **19 sites /90 raw procedure words still differ**,
including five logical Data words and two extra heads. Complete-state recovery
has not occurred. Decoded macrostep effects and later work-period repair remain
untested; the full project goal is active.

## Same physical state, more efficient flag storage

The earlier burst ended with canonical Address/Age, zero Flag2 and Wf, and three
Flag1 intervals plus Data/controller defects. A new owned adapter transfers the
actual flag bits into the existing exact packed flag engine, at the same late
Age. It then removes only sparse rows identical to the newly represented state.

The transfer performs **zero physical transitions** and verifies equality of all
5046272 reconstructed raw words before and after. The sparse exception count
drops from 118 to 19, while all 99 flagged sites still exist. This is a change of
representation, not repair. Every nonflag exception remains in the complete
physical G evaluator. Neither the physical rule, ROM, alphabet nor existing
CUDA binary changes.

The adapter requires an unflagged, mail-free canonical reference after WF_END+Q,
actual canonical Address/uniform Age, and zero actual Wf. It uses the existing
flags engine's explicit late-Age/initial-plane API, not an extension or bypass
of the older forcing-only absorption operation. Its diagnostic renderer retains
all raw procedure fields and checks agreement between active-row flag values and
the complete flag planes. Four tests pass in **1.667 s**, covering controller
retention, arbitrary stored flags and rejection of inconsistent/domain-invalid
snapshots.

The continuation stays strictly before the period boundary. It does not implement
flag-owner rollover at U or claim to support arbitrary faulty geometry. These
limits must be respected by subsequent recovery or macrostep drivers.

## Observed physical dynamics

The initial state is exactly the saved higher-rate burst endpoint, Age 1232619462.
There is no fresh encoding, discarded defect or simulated successor replacement.
The full local GPU evaluator advances every remaining procedure exception on
every tick; the exact flag engine advances the actual flags on every tick. An
independently evolved healthy GPU world supplies complete-state comparisons.

| Additional quiet ticks | Actual Flag1 sites | Sites differing from healthy |
|---:|---:|---:|
| 0 | 99 | 118 |
| 128 | 483 | 502 |
| 1024 | 3171 | 3184 |
| 4096 | 5980 | 5999 |
| 8192 | 8233 | 8240 |
| 16384 | 0 | 19 |

The temporary flag front alone grows beyond the old sparse buffer's 8192-site
capacity. The new representation keeps the full front while requiring at most
19 sparse exceptions. Flag2 remains zero throughout. The surviving procedure
defects evolve, so this is not a static replay of the initial damaged rows.

The 128-tick pilot completes in **4.666738 s**. The long run completes in
**75.616714 s**, reported peak host RSS **406264 KiB**, explicit total device
allocation **24167922 bytes**. The flag sidecar adds only 16386 device bytes.
All new GPU jobs are terminal; no substantial reservation, shared CUDA rebuild,
shared-source edit or existing-job interruption was needed.

## Independent audit and its domain

The independent CPU audit first reconstructs the complete state and checks the
same-time flag transfer. Both full physical lattices are then evaluated with
native G for the first eight ticks: **524288 complete output states**, or
**80740352 raw words**. These match the GPU observations and the separate scalar
reference described below.

Every one of the 16384 quiet ticks is independently replayed using scalar core
procedure transitions and a Python-integer Flag1 recurrence. There are **163840
scalar core candidate evaluations** across healthy and damaged trajectories.
This is a diagnostic reference; it never supplies a successor to the actual
GPU run or replaces a simulated transition there.

The scalar reference is restricted to the checked domain:

- Actual and healthy geometry is canonical, all five procedure copies agree,
  Signals are the same stationary coherent pattern, and Wf/Flag2 start at zero.
- Every replayed Age is active and avoids reset, vote and commit events. No
  capture or forcing boundary is crossed.
- All initial and produced mail fields are zero, checked at every candidate
  output. Nonuniform physical Flag1 therefore cannot introduce differences
  between the procedure copies through mail clearing.
- In this interval, a site with no live head/control/mail record in its radius-one
  neighborhood keeps its Data and has zero other procedure fields. Every site
  in the radius-one expansion of the complete live support executes the scalar
  `_clock_step`; no raw controller register is omitted.

The integer flag reference evaluates the canonical source recurrence directly:
new Flag1 is the majority-of-five right neighbors, or old Flag1 with at least
two right neighbors. Colony boundaries exclude out-of-colony right flags.
With zero Flag2 and no forcing, Flag2 stays zero. Its first all-zero Flag1 state
occurs at **quiet tick 15453**. The reference compares every raw field at all
saved observation times, including the complete final procedure discrepancy.

This is a domain-restricted independent sparse replay, not dense native execution
of all 32768 sites for all 16384 ticks, and not a general sparse simulator proof.
The full-rule source, existing canonical flag factorization and explicit
quiescent-support argument are part of the trusted/evidential basis. The initial
full-lattice parity checks distinguish it from merely reproducing flag counts.

Pilot audit passes in **9.367848 s**, peak **584860 KiB**. Long audit passes in
**32.489308 s**, peak **585428 KiB**. Driver/test watchdogs allow 512 MiB and
audit watchdogs 768 MiB, both below the user's 40 GB RAM allowance.

## Reproduction and remaining work

All five bounded commands exit 0. Preserve accepted artifacts by choosing new
output names when rerunning. Watchdog JSON records retain commands and limits.

```sh
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_late_flags_tests_v1_watch.json --seconds 30 --rss-mib 512 -- python -m unittest tests.fixed_rule.test_retimed_holder_late_flags -v
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_burst_recovery_pilot_v1_watch.json --seconds 60 --rss-mib 512 -- python -m experiments.fixed_rule.retimed_holder_burst_recovery --ticks 128 --output figs/fixed_rule/retimed_holder_burst_recovery_pilot_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_burst_recovery_16384_v1_watch.json --seconds 240 --rss-mib 512 -- python -m experiments.fixed_rule.retimed_holder_burst_recovery --ticks 16384 --output figs/fixed_rule/retimed_holder_burst_recovery_16384_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_burst_recovery_pilot_audit_v1_watch.json --seconds 60 --rss-mib 768 -- python -m experiments.fixed_rule.audit_retimed_holder_burst_recovery --input figs/fixed_rule/retimed_holder_burst_recovery_pilot_v1.json --output figs/fixed_rule/retimed_holder_burst_recovery_pilot_audit_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_burst_recovery_16384_audit_v1_watch.json --seconds 240 --rss-mib 768 -- python -m experiments.fixed_rule.audit_retimed_holder_burst_recovery --input figs/fixed_rule/retimed_holder_burst_recovery_16384_v1.json --output figs/fixed_rule/retimed_holder_burst_recovery_16384_audit_v1.json
```

Owned additions: `retimed_holder_late_flags.py`, reconstruction tests, recovery
driver, independent auditor and this report. Evidence index:
`figs/fixed_rule/retimed_holder_burst_recovery_evidence_v1.json`.
The final background snapshot and every complete remaining exception are saved
for an exact continuation.

Next follow the surviving Data and extra controllers to a decoded macrostep and
the next reset. Long event acceleration must retain all extra heads, their
interactions and any Data outside the ordinary workspace; the healthy or
single-head transition cannot be substituted. Zero flags may be detached at
the same physical time only after checking complete-state equality, before
crossing U. Neither that continuation nor its macrostep result is implemented
or claimed here.

There is still no general noise threshold, hierarchical amplification result,
complete noisy depth-two period, robust-cap proof or depth-three execution.
Q/U optimization and source ambiguities remain open. Coordination stays in
STATUS.md and MAIN_AGENT_NOTES.md; no shared-source handoff is requested.
