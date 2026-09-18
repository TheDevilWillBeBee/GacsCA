# GacsCA — executable Gács/Gray fault-tolerant cellular automaton

Reports: `Report/REPORT.md` (entry point) and sub-reports in `Report/`.

## Layout
- `gacsca/level0_spec.py` — literal scalar transcription of Gray's level-0 rules (the specification).
- `gacsca/level0_np.py`, `gacsca/gpu.py` + `gacsca/cuda/gacs_cuda.cu` — vectorized NumPy and CUDA level-0 rule.
- `gacsca/microcode.py` — track registry, bit-serial state layout, microprogram DSL/compiler.
- `gacsca/trlocal.py` — microprogram computing the simulated cell's local-structure transition.
- `gacsca/workperiod.py` — the colony work period (mail streams, gathers, compute, signalling, trickle, update).
- `gacsca/interp.py`, `gacsca/cuda/interp.cuh` — interpretation phase (level-0 colonies execute the level-1 op table).
- `gacsca/engine_np.py`, `gacsca/gpu_engine.py`, `gacsca/cuda/engine.cuh` — full-rule engines (NumPy reference, CUDA).
- `gacsca/build.py` — `make_system` (stage 1) and `make_tower` (depth-2 tower).
- `experiments/` — reproducible experiment scripts; `figs/` — outputs.

## Build / test
```
pip install --user pymupdf pytest nanobind
bash gacsca/cuda/build.sh            # needs nvcc (CUDA 12.x), cmake, nanobind
python -m pytest -q                  # fast tests (CUDA == NumPy == spec)
python -m pytest -q -m slow          # long acid tests
PYTHONPATH=. python experiments/tower_acid.py   # depth-2 tower, decoded == direct
```
