# GacsCA: fixed-rule Gács/Gray research

The active construction is the **Q=8192, U=2^20 candidate** in
[`gacsca/fixed_rule/`](gacsca/fixed_rule/). It uses one fixed radius-seven,
6,465-bit physical local rule and a hard-wired description of its own complete
transition. Its encoded evaluator is invoked twice per work period. The
candidate has passed local, encoded-evaluator, and event-composed macrostep
checks, but **a continuous full physical U-period and successive decoded upper
macrosteps have not passed**. It is not yet a verified hierarchical
self-simulator or a noise-robust construction.

Start with the [current research index](Report/fixed_rule/README.md), the
[U20 construction report](Report/fixed_rule/DUAL_PASS_U20.md), and the
[dense GPU executor report](Report/fixed_rule/DENSE_GPU_EXECUTOR20.md).
The [status handoff](Report/fixed_rule/STATUS.md) records current limits and
next steps.

Active source, checks, and drivers are in `gacsca/fixed_rule/`,
`tests/fixed_rule/`, and `experiments/fixed_rule/`. For example:

```sh
OPENBLAS_NUM_THREADS=1 python -m unittest -q \
  tests.fixed_rule.test_stream28_dual_pass20 \
  tests.fixed_rule.test_stream28_dual_dense_gpu20_tiled
```

Earlier serial-evaluator and other superseded fixed-rule attempts are in
[`archive/fixed_rule/past_attempts/`](archive/fixed_rule/past_attempts/).
The separate level-specific finite tower and its reports are in
[`archive/legacy_tower/`](archive/legacy_tower/). These are preserved as
historical references, not part of the current test suite. Supplied PDFs are
in [`papers/`](papers/); extracted paper text remains in `papers_txt/`.
Generated receipts and build products are kept locally in `figs/fixed_rule/`
for the current candidate and `figs/legacy_tower/` for the archived tower.
The entire `figs/` tree is ignored by Git.
