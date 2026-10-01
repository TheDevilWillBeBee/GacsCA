# Research archive

Earlier and abandoned work, kept for inspection and reproduction. Nothing here
is part of the current code, tests or reports, and none of it is maintained.
Archived code keeps its original import paths, which belong to the commits
named below.

| folder | what it is | last active commit |
|---|---|---|
| [`u20/`](u20/) | The Q=8192, U=2^20 fixed-rule candidate (word-level cells, a two-pass encoded evaluator, host-supplied upper static words), plus its GPU validation and repair work. Also: its reports, the task prompts of those efforts, and the former root README and REPORT. The current construction (G15) started as a successor to it (see `Report/REPORT.md` §1). | `8a7bd81` |
| [`g_family/`](g_family/) | Dead ends of the G15 line. `flow.py`, a position-driven scheduler that never beat the in-order compiler (REPORT §24). `cuda_backend.py`, the first single-block CUDA backend, superseded by `gacsca/gpu.py`, with its benchmark `gpu_bench.py`. Old notebook checkpoints, git-ignored. | `8a7bd81` |
| [`fixed_rule/past_attempts/`](fixed_rule/past_attempts/) | Earlier fixed-rule candidates, chiefly serial-evaluator constructions, with their reports, tests and experiments. | `bae5fd2` |
| [`legacy_tower/`](legacy_tower/) | The separate level-specific finite-tower implementation and its reports. | `bae5fd2` |

**Generated outputs (git-ignored, kept locally).**
- The archived work's receipts and build products are under
  `figs/archive/fixed_rule_u20/` (formerly `figs/fixed_rule/`) and
  `figs/archive/legacy_tower/` (formerly `figs/legacy_tower/`).
- Archived code that writes to `figs/fixed_rule/` refers to the first of
  these.
