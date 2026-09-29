# Fixed-rule handoff — 2026-09-29

## Current approach and source basis

The active Q=8192, U=2^20 candidate is `gacsca.fixed_rule.stream28_dual_pass20.local_step`: one fixed radius-seven, 6,465-bit physical rule with a 14,830-operation complete own-F description (SHA-256 `16bf88a1d4ff5496cd3b61a1200f8a809db1438472a9191fded26de3a0786257`). One encoded 8Q spatial evaluator runs twice per period, and Address projects the static description words. Gray pp. 31–32 motivates specialized hard-wiring after eliminating ProgramBit; Gács §§9.2–9.3 permits an identical or suitably modified self-correcting rule. These sources do not certify this candidate's full fixed point. See [the construction report](DUAL_PASS_U20.md) and [research index](README.md).

## Implemented behavior and limits

- The complete local rule has literal and WordCode parity certificates. The current code keeps all transitive modules needed by the rule, dense CUDA backend, and focused U20 checks.
- The clean-domain event-composed work-cycle audit decoded one nontrivial upper local transition, including all 119 represented words, in several Age/Flag contexts. It physically executes each 8Q evaluator invocation while analytically skipping documented quiet intervals. [Audit and exact limitations](U20_MACROSTEP_AUDIT.md).
- The dense CUDA executor evaluates the complete same F at every site and tick, with raw parity checks. On an active 31-colony fixture, 1,000 literal ticks took 14.036944 seconds (14.037 ms/tick); a four-U run projects to 16.35 hours. [Performance and memory report](DENSE_GPU_EXECUTOR20.md).
- **Unproved and unexecuted:** continuous full-U physical colony dynamics, successive decoded upper macrosteps, full two-level ring, dynamic ROM correction under faults, simulated-layer repair, finite-depth termination, and noise robustness. The current dense backend cannot fit a Q²-cell raw double buffer in 80 GiB VRAM.

## Ownership and repository layout

Following the user's 2026-09-29 cleanup request, active Q8192/U20 source, tests, experiments, and reports stay in the four `fixed_rule` namespaces. Earlier fixed-rule attempts and the separate level-specific tower are preserved under [`archive/`](../../archive/). Supplied PDFs are in `papers/`; generated figures, data, logs, and build products remain untouched in `figs/` and are excluded from new commits. The complete source-only pre-cleanup checkpoint is `bae5fd2`. The full previous rolling handoff is preserved at [STATUS_SNAPSHOT_20260929.md](../../archive/fixed_rule/past_attempts/Report/fixed_rule/STATUS_SNAPSHOT_20260929.md).

The main agent may reply in `Report/fixed_rule/MAIN_AGENT_NOTES.md`; I do not edit that file. No shared GPU experiment was running at cleanup time. Any substantial future GPU run still needs schedule coordination.

Figure cleanup follow-up: 306 legacy root-level outputs (997,849,663 bytes) were moved by same-filesystem rename to `figs/legacy_tower/`, with every inode and byte size checked after the move. `figs/fixed_rule/` remained in place. The entire `figs/` tree is now ignored; 39 previously tracked historical outputs were removed from Git's index without deleting their local files. Archived reports had 186 figure links repaired. Validation checked 1,890 relative Markdown links with zero missing targets, confirmed both output branches match `.gitignore`, and found zero files still tracked under `figs/`.

## Commands and next steps

The latest pre-cleanup dense-backend check was `OPENBLAS_NUM_THREADS=1 python -m unittest -q tests.fixed_rule.test_stream28_dual_dense_gpu20_tiled`: 4 PASS in 35.838 seconds, including compilation and raw parity. The 31-colony active benchmark was `OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.bench_dual_dense_tiled20 --colonies 31 --ticks 1000 --fixture active-evaluator --check-reference --output figs/fixed_rule/dual_dense_tiled20_bench31_active_workers262144_v1.json`: PASS, 14.036944 seconds for 1,000 ticks.

Cleanup validation: `python -m compileall -q gacsca/fixed_rule tests/fixed_rule experiments/fixed_rule` PASS; a direct import sweep loaded **137/137** retained non-package Python modules; `OPENBLAS_NUM_THREADS=1 python -m unittest -q tests.fixed_rule.test_stream28_dual_pass20 tests.fixed_rule.test_stream28_dual_dense_gpu20_tiled` ran **9 tests in 45.427 seconds, OK**; 1,890 relative Markdown links were checked with zero missing targets; `git diff --cached --check` PASS. `python -m pytest --collect-only -q tests/fixed_rule` could not run because `pytest` is not installed in this environment. No generated log, figure, or data file was staged.

Next: prepare a complete 31-colony initializer and checkpoint decoder, establish short dense parity against the event-composed audit, and then run a continuous full-U physical period when GPU scheduling permits. Decode all 119 controller/evaluator fields at successive work boundaries before claiming self-simulation. A packed evolving-state backend is needed for a full Q² physical ring.
