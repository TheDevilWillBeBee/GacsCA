# Denser independent physical noise at an active checkpoint

2026-09-27. Two unfiltered Poisson bursts now exercise the same fixed physical
rule at an actual running NAND checkpoint. The lower-intensity realization
recovers completely; the higher one retains Flag1, Data and controller defects
after two quiet ticks. Every physical lattice output is independently replayed.
These are 32-tick burst measurements, not full-period noise experiments, threshold
estimates, or proof of permanent damage. The full project goal remains active.

## Exposure, rule and initial state

Both runs start from the archived physical checkpoint in
[ACTIVE_EVALUATOR_REPAIR.md](ACTIVE_EVALUATOR_REPAIR.md): one complete colony,
Q=32768, Age 1232619428, an actual READ_B/NAND controller at address 9565. All
Data, controller/mail copies, Signals, flags, clocks and fixed metadata are kept.
The physical alphabet, radius seven, complete descriptor and ROM are unchanged.

For t=1,...,32, independent Poisson marks replace the entire 105-word projected G
state at each marked site after the transition into t. The 49 raw metadata words
are regenerated from the sampled Address by the same fixed G projection.
Poisson splitting samples the complete discrete site-time box with volume
32768*32=1048576. Repeated marks retain draw order; the last replacement at a
coordinate wins. No spatial or temporal spacing filter, repair condition or
resampling is applied. Two subsequent physical transitions contain no new noise.

| Quantity | Lower intensity | Higher intensity |
|---|---:|---:|
| Expected marks | 2048 | 8192 |
| Realized marks | 2154 | 8404 |
| Poisson rate per site-time | 0.001953125 | 0.0078125 |
| Probability of a nonempty site-time | 0.0019512188925 | 0.0077820617398 |
| Final discrepant sites | 0 | 118 |
| Final discrepant raw words | 0 | 189 |
| GPU experiment wall time | 4.433656 s | 13.670022 s |

Both use seed 2026092713. These reproducible samples at different intensities
are not independent replications for statistical inference. No confidence
interval or transition-rate threshold is inferred from two outcomes. In
particular, the earlier full-work-period pilot has a vastly longer exposure;
these larger burst rates cannot be extended over its entire duration from the
present evidence.

## Literal evolution and recovery observations

The existing sparse GPU executor computes the complete physical G transition
at every causal exception output. Its canonical background executes the actual
physical controller transition on every tick. There are no endpoint substitutions,
healthy-state installations, or representation rebases. Complete background
snapshots and every exceptional raw row are saved before and after each injection.
Together they represent the entire lattice exactly, including defects outside
the ordinary computation workspace.

The lower-intensity sample has one transient set of 14 controller discrepancies
before injection at tick 24. All input contexts satisfy the conditional
[consecutive-fault repair invariant](CONSECUTIVE_FAULT_REPAIR.md), using the actual
verified procedure-residual support. Complete equality holds after the quiet
suffix: recovery includes raw controller state, not merely decoded Info.

The higher-intensity sample first leaves that proved domain at tick 2. Its
sample contains interacting triples, including sites 30960–30962. At the following
transition, flags remain around that cluster and two other clusters. This is
not a certificate failure: the required local sparsity is false. The experiment
continues with the literal full transition, retaining the actual flags and all
other defects instead of treating an ineligible input as repaired.

At the end of the 32 noisy and two quiet ticks, Address and Age match the healthy
trajectory. Flag2 has cleared, but three Flag1 intervals remain:
8915–8935, 9998–10034 and 30864–30904. There are wrong Data words and extra
controller/head fields; primary Data differs at 6996, 6997 and 30960–30962,
and extra primary heads occur at 30992 and 30993. The complete saved exception
state contains 118 sites and 189 different raw words.

Two quiet ticks are insufficient for this realization. They do not establish
permanent failure, loss of the simulated state, or a decoded macrostep error.
The evolving flag fronts and controller defects must be followed through a
longer quiet suffix and subsequent work periods before making those claims.

## Independent verification and resources

Each auditor reproduces the exact Poisson count, coordinates, draw order and
every replacement word. It reconstructs the complete initial state, then applies
the independent native full G rule to **every site on every tick** for both
healthy and damaged trajectories. Each saved background, exception support,
exception value and injected state must match this dense replay.

Per run this checks **2228224 complete output states**, or **343146496 raw words**.
Selected outputs near the live head, boundary and actual discrepancies are also
checked with the scalar source transcription: 716 in the lower run and 732 in
the higher. Thus every output has GPU/native parity; the additional scalar
checks are probes, not a claim that all outputs were independently evaluated
with the scalar transcription. The shared rule/descriptor/compiler remains
part of the trusted/evidential chain.

Both audits pass, including exact reproduction of the higher run's unrepaired
state. Lower audit: **27.223712 s**, peak **297020 KiB**. Higher audit:
**27.426616 s**, peak **301568 KiB**. The two GPU runs report **192324 KiB** and
**221428 KiB** host RSS, respectively. Explicit device allocation is
**21365496 bytes** in each run. The watchdogs cap host RSS at 512 MiB; all measured
peaks remain below that limit and far below the user's 40 GB allowance.

The same existing private GPU binary is reused. No CUDA rebuild, substantial
GPU reservation, physical rule change, shared source edit or existing-job
interference was needed. All new jobs are terminal. Failure to recover is a
recorded scientific outcome, distinct from an incomplete/resource-stopped run.

## Reproduction and next steps

All four bounded commands exit 0. Use new output names for reruns so the accepted
artifacts remain immutable. Exact commands and limits are also in their watchdog
JSON files.

```sh
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_poisson_burst_2048_v1_watch.json --seconds 180 --rss-mib 512 -- python -m experiments.fixed_rule.retimed_holder_poisson_burst --expected-marks 2048 --output figs/fixed_rule/retimed_holder_poisson_burst_2048_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_poisson_burst_8192_v1_watch.json --seconds 180 --rss-mib 512 -- python -m experiments.fixed_rule.retimed_holder_poisson_burst --expected-marks 8192 --output figs/fixed_rule/retimed_holder_poisson_burst_8192_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_poisson_burst_2048_audit_v1_watch.json --seconds 180 --rss-mib 512 -- python -m experiments.fixed_rule.audit_retimed_holder_poisson_burst --input figs/fixed_rule/retimed_holder_poisson_burst_2048_v1.json --output figs/fixed_rule/retimed_holder_poisson_burst_2048_audit_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_poisson_burst_8192_audit_v1_watch.json --seconds 180 --rss-mib 512 -- python -m experiments.fixed_rule.audit_retimed_holder_poisson_burst --input figs/fixed_rule/retimed_holder_poisson_burst_8192_v1.json --output figs/fixed_rule/retimed_holder_poisson_burst_8192_audit_v1.json
```

New owned sources are the burst driver and its independent auditor. Existing
noise-sampler tests and fixed-rule identities are unchanged. Evidence index:
`figs/fixed_rule/retimed_holder_poisson_burst_evidence_v1.json`.

Next resume the exact saved higher-intensity state, extend the quiet recovery
window, and then inspect decoded macrosteps. Sparse raw exceptions alone may
become expensive as Flag1 fronts grow. The existing flags engine accepts an
explicit late Age and initial packed flag planes; a new owned adapter can move
those exact flag bits into that representation only after proving same-time
equality of every raw state field. It must preserve all nonflag exceptions and
must not reuse the old forcing-only absorption guard outside its domain. This
adapter/recovery continuation is not implemented here.

General cluster repair, ongoing noise throughout complete work periods, noisy
depth-two execution, Q/U optimization, robust caps and depth three remain open.
The known source-fidelity ambiguities are unchanged. No shared interface change
is requested; coordination remains through STATUS.md and MAIN_AGENT_NOTES.md.
