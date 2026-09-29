# GacsCA — executable Gács/Gray fault-tolerant cellular automaton

Reports: [REPORT.md](REPORT.md) links to the main report and sub-reports in `Report/`.
This is an experimental finite tower; see the [source audit](Report/audit_20260920.md)
for fidelity gaps and the corrected single-fault and trickle-down defects.

## Layout
- `gacsca/level0_spec.py` — literal scalar transcription of Gray's level-0 rules (the specification).
- `gacsca/level0_np.py`, `gacsca/gpu.py` + `gacsca/cuda/gacs_cuda.cu` — vectorized NumPy and CUDA level-0 rule.
- `gacsca/microcode.py` — track registry, bit-serial state layout, microprogram DSL/compiler.
- `gacsca/trlocal.py` — microprogram computing the simulated cell's local-structure transition.
- `gacsca/workperiod.py` — the colony work period (mail streams, gathers, compute, signalling, trickle, update).
- `gacsca/gray_schedule.py` — five-stage Gray timing, independent histories, resets, and reset-safe upper-track interpretation.
- `gacsca/interp.py`, `gacsca/cuda/interp.cuh` — interpretation phase (level-0 colonies execute the level-1 op table).
- `gacsca/nested_eval.py` — locally transported nested instruction evaluation; finite third-link component.
- `gacsca/engine_np.py`, `gacsca/gpu_engine.py`, `gacsca/cuda/engine.cuh` — full-rule engines (NumPy reference, CUDA).
- `gacsca/build.py` — `make_system`, `make_tower` (two links), and `make_simulation_layer` (explicit finite extension).
- `experiments/` — reproducible experiment scripts; `figs/` — outputs.

## Build / test
```
pip install --user numpy torch matplotlib pymupdf pytest nanobind
bash gacsca/cuda/build.sh            # needs nvcc (CUDA 12.x), cmake, nanobind
python -m pytest -q                  # default suite (includes lengthy NumPy interpreter tests)
python -m pytest -q -m slow          # long acid tests
PYTHONPATH=. python experiments/tower_acid.py   # depth-2 tower, decoded == direct
PYTHONPATH=. python experiments/redundancy_noise.py  # matched R=3/R=5 GPU noise sweep
python experiments/plot_redundancy_noise.py figs/redundancy_noise_20260920.json
python -m experiments.tower_checkpoint --output figs/my_tower_run  # full upper period, atomic checkpoints
python -m experiments.tower_checkpoint --output figs/my_tower_run --resume
python -m experiments.gray_protocol --output figs/my_gray_protocol  # full-Q four-scenario protocol test
python -m experiments.gray_protocol --output figs/my_gray_protocol --resume
python -m experiments.gray_faults --output figs/my_gray_faults  # localized physical faults, two periods
python -m experiments.gray_faults --output figs/my_gray_faults --resume
python -m experiments.plot_gray_faults figs/my_gray_faults.npz
```

The noise sweep refuses to overwrite results; pass `--output <new-path.json>` for a
new run. It measures simulated Address/Age/Flags transition errors, not logical
memory lifetime. Confidence intervals resample independent rings, preserving
correlations between cells and periods within a ring.

Noise generator version 2 is now the default. Pass `--noise-version 1` to replay
historical sweep semantics. `CleanGraphRunner` accelerates **noiseless only** runs;
captured noisy steps would repeat counters and are deliberately not exposed.
The tower validator accepts `--R 5`; it checks all upper fields/raw track copies
each period, saves exact physical state, and refuses to resume under different
parameters or source/binary fingerprints. Its default terminal ring has one cell,
so full neighborhood diversity requires a larger `--ncol0` (at least 704).

`make_system(Q=8192,U=1048576,R=5,D=1,schedule="gray",Qs=16,Us=2048)`
selects the new five-stage schedule with full-register encoding. A Gray tower
can be compiled with `make_tower(Q0=8192,U0=1048576,Q1=8192,U1=1048576,
ncol0=8192,R=5,D=1,schedule="gray")`: 67,108,864 physical cells for one upper
colony. One complete lower work period now passes at this geometry, matching
all 504 encoded bits of every upper cell. A complete upper work period remains
unvalidated. See [validation and remaining fidelity gaps](Report/gray_schedule.md).

For the finite third-link implementation, construct a two-link `middle, top =
make_tower(ncol0=1)`, then `outer = make_simulation_layer(middle, Q=1024, U=65536)`.
Every middle instruction is retained; this wraps a whole middle colony in 262,144
physical cells. The compact R=3 configuration has now completed a full middle
work period (268 million physical steps), with independent CPU replay; its
one-cell top ring is aliased. Noisy depth scaling remains unverified. This is not a uniform
encoded-program interpreter. See [component and integration evidence](Report/nested_interpreter.md).

Checkpointed compact third-link execution uses
`python -m experiments.third_link_initialized --output figs/my_third_link --certified-skip`.
This supplies the compressed schedule's required initial input caches; the
historical cold-cache driver is preserved but is not the canonical initializer.
See the [eight-error counterexample and correction](Report/cache_initialization.md).
Add `--stop-after 16` for a pilot, and `--resume` to continue the same run.
This runner uses full-register encoding at every layer and checks each decoded
middle transition. Its default has 11 top cells (distinct radius-five neighbors);
`--middle-colonies 64` gives a whole top colony. See [geometry and exact validation scope](Report/third_link_execution.md).

The printed Flag2 rule has a source-confirmed isolated-error persistence
counterexample. Defaults preserve that rule. Research candidates are explicit:
`Variant(flag2_healthy_erase="at_most_one")` (or `"no_ones"`), passed as
`variant=` to the engines/factories. To compare physical faults, run
`python -m experiments.gray_faults --output figs/my_candidate --flag2-erase at_most_one`.
Neither candidate is claimed to be Gray's intended correction;
see [D8 evidence and limitations](Report/flag2_recovery_gap.md).

For exact **noiseless** acceleration, `experiments.gray_protocol` accepts
`--certified-skip`. It skips only instruction-free intervals whose physical
state passes the documented fixed-point checks; noisy steps are never skipped.
The full-size Gray transition validator is `python -m experiments.gray_tower_checkpoint
--output figs/my_full_gray --certified-skip` (67 million cells; a long GPU run).
Use the same arguments plus `--resume` after interruption. `--fork-from <checkpoint>`
creates a separately archived executor migration, requiring identical physical
rules and preserving its parent. See [proof scope and bitwise comparisons](Report/exact_acceleration.md).

Persistent local phase-memory studies use `python -m experiments.phase_memory
--output figs/my_phase_run.json --steps 10000 --epsilon 0.30 0.32 0.34`.
These distinguish wrong-bit outputs, erasures and sampled first failures;
they do not implement Gács's arbitrary per-site payload memory.
`python -m experiments.phase_size --output figs/my_size_run.json` compares
whole-ring and fixed-Q-site observers on the same trajectories; their apparent
size dependence can differ. See [measurements and uncertainty](Report/memory_observables.md).
