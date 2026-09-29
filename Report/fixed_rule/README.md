# Current fixed-rule Q=8192, U=2^20 work

The active candidate is `stream28_dual_pass20.local_step`, one fixed
radius-seven transition with a 6,465-bit physical alphabet. Its complete
own-rule WordCode has 14,830 operations. The rule invokes the same encoded
spatial evaluator twice; hierarchy depth is absent from the transition.
The current work is a candidate, not a proof or an executed two-level tower.

Read these reports in order:

1. [DUAL_PASS_U20.md](DUAL_PASS_U20.md): construction, space/time budget,
   literal certificates, and missing closure obligations.
2. [U20_MACROSTEP_AUDIT.md](U20_MACROSTEP_AUDIT.md): clean-domain
   event-composed upper transition and the exact skip assumptions.
3. [DENSE_GPU_EXECUTOR20.md](DENSE_GPU_EXECUTOR20.md): complete-rule dense
   CUDA parity and measured throughput; no full-U run yet.
4. [STATUS.md](STATUS.md): current coordination, tested commands, and next work.

The 8Q spatial construction and optimization path are documented in
[COMPACT8_VERTICAL_SLICE.md](COMPACT8_VERTICAL_SLICE.md),
[OWN_RULE_DESCRIPTION_CAPACITY.md](OWN_RULE_DESCRIPTION_CAPACITY.md),
[INTEGRATED_SPATIAL_HANDOFF.md](INTEGRATED_SPATIAL_HANDOFF.md), and
[FULL_SPATIAL_DAG_SCHEDULE.md](FULL_SPATIAL_DAG_SCHEDULE.md).
These are supporting steps, not separate active depth kernels.

The active package also retains transitive predecessor modules used by the
current rule or its focused checks. Old serial evaluators, rejected layouts,
their tests, experiments, and status snapshots live in
[`archive/fixed_rule/past_attempts/`](../../archive/fixed_rule/past_attempts/).
The complete pre-cleanup source checkpoint is Git commit `bae5fd2`.
