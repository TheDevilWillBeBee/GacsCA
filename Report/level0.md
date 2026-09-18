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
