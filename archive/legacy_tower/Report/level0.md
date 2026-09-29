# Level-0 (local structure) — implementation notes and results

## Rule transcription
`gacsca/level0_spec.py` is a scalar, literal transcription of Gray pp. 20–22. Conventions:
- votes for C(x): site x+i proposes v_i = (Address(x+i) − i) mod Q; C(x) exists iff some v is
  proposed ≥ 3 times; then x has position v in C(x) = [x−v, x−v+Q).
- L(x)∩C(x) = {x−i : v−i ≥ 0}, R(x)∩C(x) = {x+i : v+i ≤ Q−1}. N(x)∩C(x) = both plus x.
- Majority of 5: value with ≥3 votes, else current value; Age always incremented after the vote.
- Order of evaluation: C(x) → inconsistency → computed Flag1 → Age vote in L (only needed when C(x)
  does not exist) → computed Flag2 → Address/Age votes (direction from computed flags).

## Verification
`tests/test_level0.py`, `tests/test_gpu.py`: NumPy and CUDA implementations agree with the spec
on random configurations (3 rule variants) and on 40-step trajectories from damaged ground
states; ground state is a fixed point; a single damaged cell is repaired in one step.

## Experiments (GPU, `experiments/level0_sweep_gpu.py`, data in `figs/level0_sweep_gpu.json`)
Protocol: ground state; ε-noise for 500 steps; no noise for 500 steps; "recovered" iff every
Address equals x mod Q (and, for `full_rec`, every Age equals t mod U). 256 trials per point.

| ε | 0.30 | 0.34 | 0.36 | 0.38 | 0.40 | 0.42 | 0.44 |
|---|---|---|---|---|---|---|---|
| P(addr recovered), Gray | 1.00 | 1.00 | 0.996 | 0.92 | 0.27 | 0.01 | 0 |
| P(addr recovered), Masumori variant | 0.99 | 0.96 | 0.89 | 0.63 | 0.15 | 0.02 | 0 |
| fraction of correct Addresses during noise | 0.69 | 0.63 | 0.58 | 0.49 | 0.19 | 0.005 | 0.004 |

Space-time picture (Masumori Fig. 7 protocol, NumPy run): `figs/masumori_fig7_np.png`.

## Mean-field
Let c be the fraction of cells with the correct Address. A correct, un-hit cell stays correct
(random wrong values almost never form a 3-of-5 majority); a wrong un-hit cell is repaired iff
≥3 of its 5 voters are correct: c' = (1−ε)[c + (1−c) g(c)]. The nonzero fixed point disappears
at ε_c = max_c (1−c)g(c)/(c+(1−c)g(c)) = 0.334 (at c ≈ 0.48). Simulation: ≈0.40.

## Replication audit, 2026-09-20

Masumori Fig.7 explicitly specifies independent per-cell noise for 500 steps,
followed by a clean period. The discrepancy cannot simply be assigned to a
different noise rate. `experiments/masumori_noise_audit.py` tests two remaining
interpretation choices: uniform valid integers versus random full-width bit
strings (Q=271 is not a power of two), and whether noise can raise the Workspace
flags whose coupling was omitted from Masumori's local-only implementation.
Q=271, four colonies, 128 trials, seed 920, 500 noisy + 500 clean steps.

| Rule / replacement / Workspace noise | ε=0.4 original / any phase | ε=0.5 original / any phase | ε=0.6 original / any phase |
|---|---:|---:|---:|
| Gray / valid / on | 25 / 25 | 0 / 19 | 0 / 14 |
| Gray / bits / off | 2 / 49 | 0 / 21 | 0 / 13 |
| Masumori / valid / on | 14 / 14 | 0 / 18 | 0 / 14 |
| Masumori / bits / off | 2 / 54 | 0 / 21 | 0 / 14 |

Counts are out of 128 independent rings. "Any phase" means every address has
the same offset from x mod Q, which measures spatial order but not preservation
of the encoded phase memory. Across **all eight** rule/noise combinations,
original-phase recovery at ε=0.5 and 0.6 was zero. These alternatives do not
explain the published higher recovery threshold. Shifted ordered states do
appear, qualitatively consistent with Masumori Fig.8. Their distinction from
correct-phase recovery is essential for future lifetime measurements.
[All configurations and trial phases](../../../figs/legacy_tower/masumori_noise_audit_20260920.json).
