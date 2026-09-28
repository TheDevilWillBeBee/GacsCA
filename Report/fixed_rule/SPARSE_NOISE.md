# Reproducible sparse random-noise pilot

2026-09-26. Two preselected noise realizations completed two physical work periods
each. Their 221 and 240 uniform whole-cell replacements produced no decoded
errors at the four observed commits, and both worlds matched separately evolved
healthy physical references after eight noise-free settling ticks. Every sampled
fault cleared in one literal tick. This is very-low-rate isolated-fault evidence;
it establishes neither a noise threshold nor cross-level amplification.

## Noise model and source relationship

The unchanged projected physical rule G has 2704 mutable bits in 105 words.
After every deterministic local transition, independently at each physical site,
with probability p=2^-44, replace the complete projected state by a uniform state
of this alphabet. All controller, geometry, flag, Wf, mail and Signal fields can
change. The 49 hard-wired program metadata words are derived from the resulting
Address; they are not additional mutable physical noise coordinates.

The transition probability is

    P(s | neighborhood) = (1-p) 1{s=G(neighborhood)} + p / 2^2704.

Thus every local output has positive probability, and the probability of differing
from G is at most p. This is one special independent channel within the broader
perturbation model of Gács Definition 2.19 (supplied `gacs_2001.txt`, lines 932–966),
which permits more general conditional error distributions. Testing this channel
does not test all permitted perturbations or prove nonergodicity. Candidate-B
Flag2 and the old-Signal D10 choice remain explicit modified-rule assumptions.

The trial covers every cell update at times 1 through 2U on a 491520-site ring.
Faults occur after that time's local transition and before observations. Multiple
faults at one time would be installed simultaneously. Initial time zero is clean.
The subsequent eight ticks are explicitly noise-free settling, excluded from the
reported noisy space-time volume.

## Sparse sampling without a dense space-time allocation

`gacsca/fixed_rule/small_holder_noise.py` samples K from Binomial(N,p), then chooses
a uniform K-element subset of the N cell updates using Floyd sampling. For a
particular subset S of size k, its probability is

    Binomial(N,k) p^k (1-p)^(N-k) / Binomial(N,k)
    = p^k (1-p)^(N-k).

This gives the independent Bernoulli mask in the specified probability model.
It is not a fixed-count or event-conditioned noise model. PRNG/library versions
and split seeds are recorded; finite numerical implementations are used. The
replacement state draws are separate from event placement and cover every field
with its declared bit width.

Storage is proportional to realized event count, not N. The default cap is 2048
events. A draw beyond that limit is recorded as a resource rejection and is never
truncated or resampled. Execution failures likewise preserve the complete noise
archive, processed-event log, partial observations and failure description.
Predetermined seeds 2026092601 and 2026092602 were both run without filtering or
replacement. Their expected count was 240 each.

Three sampler tests passed in 0.026 s:

```sh
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_noise.py -v
```

They exhaust the small N=4,K=2 subset distribution; sample seven positions from
2^60 opportunities without dense storage; verify all time/site pairs at p=1,
zero-noise behavior, all 105 replacement words, deterministic reproduction and
immutable arrays; and require over-limit draws to fail without resampling.

## Physical execution and complete observations

`small_holder_sparse_noise.py` advances the full physical faulty and healthy worlds
to the next event or commit, never skipping across an event. Every replacement
is checked against a full physical read immediately after injection. Physical
advance forbids host descriptor/evaluator/local-rule calls. Host computation is
limited to the external noise realization and diagnostic reference calculations;
no healthy state or upper transition is installed into the damaged world.

At U and 2U, the decoder reads all 154 raw Info words directly, without majority
repair or masking. Invalid projected encodings are recorded as invalid rather
than normalized. A separately evolved healthy world is checked against the
independent expected rule at those boundaries. After settling at 2U+8, complete
physical equality includes controller/Data/flags, core, tail, gap and any remaining
exceptions. Equality is not inferred merely from an empty exception set.

Eight event indices, spaced through each saved schedule, have full physical
neighborhoods archived before noise, after noise, and after the next local
transition before any subsequent noise. These provide independent causal-cone
checks in addition to macrostep observations. Every event remains in the noise
archive and JSONL log, including events not selected for these larger snapshots.

## Commands and measurements

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_sparse_noise --seed 2026092601 --periods 2 --rate-exponent 44 --output figs/fixed_rule/small_holder_sparse_noise_seed1_v1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_sparse_noise --seed 2026092602 --periods 2 --rate-exponent 44 --output figs/fixed_rule/small_holder_sparse_noise_seed2_v1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_sparse_noise --input figs/fixed_rule/small_holder_sparse_noise_seed1_v1 --output figs/fixed_rule/small_holder_sparse_noise_seed1_audit_v1.json
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_sparse_noise --input figs/fixed_rule/small_holder_sparse_noise_seed2_v1 --output figs/fixed_rule/small_holder_sparse_noise_seed2_audit_v1.json
```

All four processes exited zero. Each trial has N=4222124650659840 cell updates,
p=5.684341886080802e-14 and 8589934592 noisy physical ticks. The actual realizations
have no simultaneous events and no events in forcing/clearing windows.

| Measurement | Seed 2026092601 | Seed 2026092602 |
|---|---:|---:|
| Whole-cell replacements | 221 | 240 |
| Realized replacements / cell update | 5.234331486766071e-14 | 5.684341886080802e-14 |
| Minimum time between events | 29225 ticks | 375648 ticks |
| Literal exception ticks | 221 | 240 |
| Data / flag rebases | 0 / 0 | 0 / 0 |
| Different decoded words at U / 2U | 0 / 0 | 0 / 0 |
| Complete physical equality at 2U+8 | yes | yes |
| GPU advance, including healthy reference | 71.445665 s | 71.001874 s |
| Total runtime | 86.891991 s | 87.625573 s |
| Host peak RSS | 375208 KiB | 376116 KiB |
| Sampled GPU process memory | 448 MiB | 448 MiB |

The identical event/literal-tick counts, nonempty injected exceptions and zero
rebases show one-tick physical recovery in these realizations. This observation
is not a universal one-tick theorem for arbitrary geometry, head interactions or
forcing phases. Two independent noise histories supplied four commit observations;
the four commits are not treated as four independent robustness trials.

Independent audits passed in 1.673382 s / 1.652116 s, using 67892 / 67872 KiB host
RSS. They reproduce every time, position and replacement word; check every logged
injection; verify 120 complete physical local outputs per trial against scalar,
native and descriptor evaluations; and check the complete decoded observations.
The audit accepts recorded failures as well as successes. Whole-physical rejoin
remains a runtime comparison in the hashed driver, not a reconstruction of the
entire physical trajectory from the small archive.

State artifact SHA256s:

- Seed 1: `17b16bb6e0b66caa2b021506566f5f9020f30ace3c32f1a8dc0acdc945e7ff15`.
- Seed 2: `3759499d5450dafb3f49ec8d211f331cddde4f5916671739e168d00f7450875a`.

Each manifest records its separate `.noise.npz`, `.events.jsonl`, source and binary
hashes. The physical descriptor remains
`af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`.
No physical rule, alphabet, ROM, neighborhood, frozen backend or shared file changed.

## What this adds, and what remains

This is the first recorded independent random whole-cell channel over complete
periods in the general physical-fault executor. The sampling and replay plumbing
is validated, and the low-rate runs preserve complete decoded dynamics. All faults
were temporally well separated and missed forcing/clearing windows. The pilot
therefore does not exercise interacting fault islands, require simulated-layer
repair, estimate a threshold, or measure amplification across levels. Earlier
correlated temporal-fault experiments supply different targeted evidence and
must not be substituted for those missing statistical results.

The full goal remains active. Priorities now include practical nested-trajectory
cost and actual second-link work periods, alongside stronger interacting-fault
measurements and robust finite-depth termination. More very-low-rate seeds alone
would not resolve these gaps. The whole-Q 8 GiB allocation/reset pilot remains
pending scheduling coordination; U²=2^64 remains the larger runtime obstacle.
Only the sampler, its tests, the pilot/audit drivers, this report, STATUS.md and
namespaced evidence are owned changes. All handles are terminal and the final GPU
query is empty; main-agent notes remain absent.
