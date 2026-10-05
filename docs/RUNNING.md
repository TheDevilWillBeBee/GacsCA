# Running things

All commands run from the repository root (`python` is Python 3; on systems without that name use `python3`). Requirements:
- Python 3 with NumPy;
- GCC, for the generated C kernel;
- for the GPU parts, the CUDA toolkit (`/usr/local/cuda/bin/nvcc`, `sm_80`) and an NVIDIA GPU. The development machine has an A100 80 GB.

Generated kernels, candidate caches and receipts go to `figs/`, which is git-ignored.

## Tests

```sh
OPENBLAS_NUM_THREADS=1 python -m unittest -q tests.test_front_candidate     # 59 tests, about 2 minutes
GACSCA_SLOW=1 OPENBLAS_NUM_THREADS=1 python -m unittest -q tests.test_front_candidate.G8SlowTest
```

Without a GPU, the GPU tests are skipped. The first run builds every candidate and its C kernel in `figs/` (GCC needs up to ten minutes per kernel), so it takes much longer.

## Candidates

```sh
python -c "from gacsca import candidates; c = candidates.load(candidates.CURRENT); print(candidates.summary(c))"   # G17
PYTHONPATH=. python experiments/build_candidates.py --only G17     # fresh build, compared with the cache
PYTHONPATH=. python experiments/build_candidates.py                # all 19 recipes, then figs/receipts/candidates.json
PYTHONPATH=. python experiments/size_jobs.py --tag mysweep --params '{"E0q": 29}'   # size a job-scheduled candidate (18 settings)
```

- **First load.** `candidates.load(name)` compiles a candidate on first use (seconds for R1, about 15 s for G16 and G17, about a minute for G15) and caches it in `figs/candidates/`.
- **Checks on loading.** The cache is checked against the recipe and against `gacsca/manifest.json`.
- **Changing a recipe.** Rebuild it, then re-pin with `build_candidates.py --combine --write-manifest`, which writes the manifest only if every fresh build reproduces its cache.

## Simulating

```python
import numpy as np
from gacsca import candidates, codec, gpu
c = candidates.load('G17'); C = c.c_backend()
upper = codec.random_upper(c, 8, np.random.default_rng(0))       # 8 upper cells
X = codec.encode(c, upper)                                        # 8 colonies of 384 sites
sim = gpu.GpuSim(c, 1, 8)                                         # 1 ring of 8 colonies
sim.set_state(C.pack(X)); sim.run(c.p.U)                          # one work period
assert (codec.decode(c, C.unpack(sim.state()[0], sim.N)) == c.step_numpy(upper)).all()
```

- **Without a GPU.** `C.run_packed_scalar(packed, ticks)` runs the same rule on the CPU.
- **One large ring, fast.** `gpu_roles.RoleSim(c, colonies)` (a multiple of 32 colonies) has `set_state(packed)`, `run(ticks)` and `state()` like `GpuSim`, for one ring and without error injection. It is three times faster on a level-2 cell's worth of sites (REPORT §30).
- **Errors.** `gpu.noise(seed, e0_grid=50, boxes=[(x0, w, t0, h, p)], mode='random')` and `sim.set_noise([...])` inject Gray-style errors, one configuration per ring.
- **Comparing rings.** `sim.track(rows)` records, at every tick, where each ring differs from ring 0.

## The main experiments

```sh
# the level-1 error campaign: a 64-colony slice, every stage of the period, per-tick checks
PYTHONPATH=. python experiments/level1_campaign.py --upper-steps 4 --side 100 --e0 --track --tag mybatch   # the current candidate, G17
# whole upper colony, colony-scale wipes followed to two level-2 boundaries
PYTHONPATH=. python experiments/level1_campaign.py --candidate G15 --slice 0 --wipe 3 --height 200 \
    --places mid,left --random 0 --track --continue-level2 2 --tag mywipes
# three levels: phases across a level-2 commit, level-2 macrosteps, errors only level 2 can clear
PYTHONPATH=. python experiments/three_level_g.py phases --n2 2 --steps 6
PYTHONPATH=. python experiments/three_level_g.py closure2 --n2 8 --steps 6 --healthy
PYTHONPATH=. python experiments/three_level_g.py repair2 --n2 32 --level2-age 60000 --slice 128 --wipe 7,27 \
    --target front --level1-age 62640 --verify-handoff 2
# bookkeeping
PYTHONPATH=. python experiments/campaign_census.py        # -> Report/campaign_census.json
PYTHONPATH=. python experiments/reclassify_receipts.py    # -> figs/level1_campaign/reclassified.json
```

**Typical times.**

| run | G15 on an A100 | G16 on an RTX 4090 |
|---|---|---|
| a level-1 step, one level-2 cell's worth of sites (262,144) | about 12 s | about 1 s |
| a 64-colony campaign batch, 66 rings × 4 upper steps | | about 85 s |
| a whole-colony campaign batch of 10 rings × 4 upper steps | 15–25 min | 1.5–2 min |
| a `repair2` run | 3–9 min | 10–20 s |
| a level-2 step on the level-1 automaton, 32 level-2 cells | about 7 s | about 1 s |
| a level-2 step on the level-1 automaton, a complete level-2 colony (384 or 768 level-2 cells of G17, two rings) | | 2.3 or 5 s |
| a physical level-2 step, one level-2 cell | about 15 days (REPORT §26.1; not run) | 6.9 hours on `gpu.py` (estimate), 2.5 hours on `gpu_roles.py` (run; REPORT §30); G17: 1.7 hours (run; §33) |
| a physical level-2 step, two level-2 cells | | 10 hours on `gpu.py` (estimate), 3.9 hours on `gpu_roles.py` (run) |

A full physical level-2 step (checkpointed; `--resume` continues):

```sh
PYTHONPATH=. nohup python experiments/level2_physical.py --candidate G17 --n2 1 --seed 0 > level2.log 2>&1 &
```

The drivers default to `candidates.CURRENT` (G17); for another candidate pass `--candidate` and Ages below its U (G16: 25,920; for example `--level2-age 21888 --level1-age 22176` for the front-targeted `repair2`).
