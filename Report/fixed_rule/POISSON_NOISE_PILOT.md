# Independent space-time noise through successive physical work periods

2026-09-27. A reproducible unfiltered noise pilot now executes the unchanged fixed
rule through two complete lower work periods, with an independently evolved
healthy comparison. All 118 realized full-state replacements repair after one
physical tick. Both complete physical boundary states and every decoded raw
simulated field agree. This is a low-rate finite experiment across one simulation
link, not a threshold estimate or a complete noisy depth-two work-period run.
The full project goal remains active.

## Noise model and exposure

There are N=491520 physical sites (15 colonies) and H=4294967296 physical ticks
(two periods). Each discrete site-time independently receives Poisson marks at
rate rho. At a marked coordinate, the entire 105-word projected G state is
replaced by an independent uniformly sampled typed state. The 49 hard-wired
metadata fields are derived from its actual Address. Noise is applied **after**
the physical transition into integer time t, for t=1,...,H.

The sampler draws K~Poisson(lambda), then K independent uniform coordinates in
the N by H box, with independent full-state replacement words. By Poisson
splitting, this is the stated independent site-time law with rho=lambda/(NH).
Multiple marks at a coordinate are retained in original draw order; the last
replacement wins. Thus the probability of at least one replacement at a given
site-time is 1-exp(-rho), evaluated with `expm1` to avoid rounding this small
probability to zero. No spatial/temporal spacing condition is imposed and no
sample is rejected or resampled because it is inconvenient. A resource overflow
would stop and preserve evidence rather than choose another realization.

| Quantity | Value |
|---|---:|
| Seed | 2026092711 |
| Expected marks lambda | 128 |
| Realized marks / distinct event times | 118 / 118 |
| Space-time volume NH | 2111062325329920 |
| Poisson mark rate rho | 6.063298011819522e-14 |
| Nonempty site-time probability | 6.063298011819337e-14 |
| Minimum realized gap between event times | 140965 ticks |

All events in this realization satisfy the clean-context hypotheses of the
conditional two-tick theorem. No interacting/forcing-phase noise was realized.
That spacing/context is an observed property of this sample, not a generator
filter. Previous targeted experiments cover forcing and interacting encoded
faults separately; this pilot does not replace them or establish their occurrence
probabilities under this low rate.

## Actual evolution and observations

Both trajectories start from the canonical encoding of `parents(15)`, including
an active represented READ_B/NAND controller. The actual resident GPU executor
performs colony communication, computation, maintenance and both commits.
Scheduled replacements enter the actual complete physical states. While an
exception exists, the full radius-seven G evaluator computes its affected outputs.
Both actual and healthy trajectories are observed over the next two ticks, without
crossing a scheduled event or period boundary. No repaired/healthy successor is
installed in the noisy world.

Every event rejoins after its first observed physical tick. Complete snapshots
include all Data, active controller/packet records, Signals, flag planes, clocks
and reconstruction of Wf. The experiment performs **zero Data or flag rebases**.
Noiseless intervals can use the previously validated physical event executor
because they contain no scheduled noise; this is not an endpoint substitution
for an unresolved faulty interval.

At each of U and 2U:

- all 2310 decoded raw fields agree with the intended next G step, including
  represented controller fields;
- all 148740 physical bank words and the complete remaining physical snapshot
  agree with the independently evolved healthy trajectory;
- no raw physical exception remains.

The next period starts from the actual preceding physical state. The rule,
physical alphabet, ROM, neighborhood and transition implementation are identical
throughout; the noisy trajectory is never reinitialized.

## Independent audit

The auditor regenerates the exact sampled coordinates and all replacement words,
checks draw order and the unfiltered count, and verifies the actual injection
readbacks. It then independently executes the scalar physical G rule throughout
every saved local causal cone: **16992 complete raw output states**, each with
154 fields. Both actual and healthy outputs match at every probe. These local
couplings, the realized event gaps and locality justify the complete rejoin
between successive events.

For each full period, an independent DAG last-writer evaluation recomputes the
entire terminal Data bank, Signals and canonical endpoint snapshot. Those match
both GPU trajectories, not merely their decoded values. Scalar upper G also
checks all decoded words. The audit passes in **52.191715 s**, peak **73448 KiB**.
It is a finite trajectory/source parity check, not a universal proof of the
execution backend or the complete Gacs construction.

Four sampler tests pass in **0.054 s**. They check exact reproducibility and
Poisson count generation, all raw field widths, retained colliding marks and
stable draw order, the zero-rate case, and stopping without resampling when a
capacity guard rejects a draw. NumPy version is recorded as 2.2.6; all realized
coordinates/replacements are retained independently of future library versions.

## Cost and reproduction

Total experiment time is **69.882367 s**. Reported host peak is **219992 KiB**;
sampled watchdog peak is 226500 KiB. Conservative explicit GPU peak is
**30178500 bytes**, below 64 MiB. The run represents 4294967296 actual physical
ticks per site using certified event acceleration between literal fault steps.
It does not execute every site-tick densely. No CUDA rebuild or substantial GPU
reservation was needed. All jobs are terminal; shared source/jobs/data were not
modified.

From the repository root, with `OPENBLAS_NUM_THREADS=1`:

```sh
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_poisson_noise_v1_watch.json --seconds 180 --rss-mib 1024 -- python -m experiments.fixed_rule.retimed_holder_poisson_noise --output figs/fixed_rule/retimed_holder_poisson_noise_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_noise_schedule_tests_v1_watch.json --seconds 30 --rss-mib 512 -- python -m unittest tests.fixed_rule.test_retimed_holder_noise_schedule -v
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_poisson_noise_audit_v1_watch.json --seconds 180 --rss-mib 1024 -- python -m experiments.fixed_rule.audit_retimed_holder_poisson_noise --input figs/fixed_rule/retimed_holder_poisson_noise_v1.json --output figs/fixed_rule/retimed_holder_poisson_noise_audit_v1.json
```

All exit 0. The artifact includes the full noise ledger, old/injected local states,
both physical causal-cone trajectories, and complete paired period/final snapshots.
The evidence index is `figs/fixed_rule/retimed_holder_poisson_noise_evidence_v1.json`.
The driver's stop path retains the exact background plus raw exceptions if a
resource/domain guard interrupts execution; incomplete runs are not scored as
successful or failed noisy dynamics. That path was not needed in this pilot.

## What remains and the next useful step

The rate is deliberately very small. One successful realization with isolated
faults cannot justify a stochastic threshold, extrapolation to larger rates,
general amplification, or arbitrary noisy caps. The known source ambiguities and
homogeneous-cap Address persistence remain unchanged. This pilot adds an actual
independent space-time-noise execution to the prior deterministic repair tests.

The next proof target is a space-time version of the local repair invariant:
allow new faults on consecutive ticks while retaining only procedure discrepancies
at the most recent faulty holders, under explicit current/previous local sparsity
and healthy-context premises. If certified, it could avoid paying a full event
round-trip for every isolated mark at higher rates while keeping exceptional
clusters and forcing contexts explicit. It is not yet proved or installed as an
execution shortcut. Q/U optimization, noisy depth-two execution, robust boundary
termination and full correction/amplification remain open.
