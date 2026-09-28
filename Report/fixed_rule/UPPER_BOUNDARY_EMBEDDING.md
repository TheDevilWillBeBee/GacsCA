# Complete-upper-colony repair and the window boundary gap

2026-09-27. The measured decoded defect also repairs in the complete saved
32768-cell upper colony after two G steps. However, the old periodic 17-cell
upper window is **not** an exact restriction of that colony: its boundary
effects reach every window cell by that time. This distinguishes recovery of
the defect from equivalence of the surrounding trajectories.

The new result is a diagnostic upper-layer embedding. It does not execute a
larger lower lattice or establish that the lower noise burst has the same
decoded effect there. The actual lower execution remains the contextual
experiment in [CONTEXTUAL_UPPER_REPAIR.md](CONTEXTUAL_UPPER_REPAIR.md).

## Complete-colony comparison

The input is the complete saved active upper NAND state at Age 1232619428,
bound to the contextual burst receipt and its raw arrays. One native G step
computes the healthy full-colony successor. At position 9566, the diagnostic
copies the complete measured defective decoded record from the actual lower
commit, applying the fixed hard-wiring projection to its ROM metadata. All
other full-colony cells retain their healthy successor values.

Both full colonies then execute three native G steps. Scalar G independently
checks every potentially differing output and every 17-cell contextual-window
output, including all raw controller fields. Outside the radius-seven
neighborhood of the preceding difference set, equality follows from locality;
the full native arrays are nevertheless computed and retained.

| Subsequent upper steps | Different full-colony cells | Different lifted raw words | Window cells differing from full-colony restriction |
|---:|---|---:|---:|
| 0 | 9566 | 23 | 6 |
| 1 | 9566 | 11 | 12 |
| 2 | None | 0 | 17 |
| 3 | None | 0 | 17 |

The last column counts the same boundary discrepancies in the healthy and
defective trajectories. The damaged-versus-healthy field masks agree between
the window and full colony at every recorded time. These observations do not
make the window's absolute raw states correct. In particular, matching repair
times alone cannot establish a full lower-colony embedding.

The 23-word initial discrepancy is measured after hard-wiring normalization of
the actual all-zero decoded record; it includes ROM metadata derived from its
wrong Address. It is a different comparison from the earlier 26 raw-word
unprojected commit discrepancy. No mutable field is discarded or repaired by
this projection.

`audit_retimed_holder_upper_embedding.py` completes in **7.542955 s**, with
**602168 KiB** process peak RSS (602544 KiB sampled). It evaluates 229376 full
native output states and checks 143 complete scalar outputs. All source and
artifact hashes are verified before use. The result and saved arrays are
`figs/fixed_rule/retimed_holder_upper_embedding_v1.json/.npz`.

## A sufficient halo for the next lower experiment

For four upper steps, a central 17-cell target requires a radius-only halo of
7*4=28 cells on each side. A **73-cell upper window** therefore suffices for
that target. This is a sufficient geometric bound, not a claim of minimal
state-dependent support. It changes the number of colonies in an experiment;
it does not change Q, U, the physical alphabet, neighborhood, ROM or kernel.

`certify_retimed_holder_upper_halo.py` starts from those 73 cells of the saved
full upper configuration. After the first native step, it conditionally inserts
the measured defect at the same upper position. It then executes the three
subsequent steps with the unchanged G. The safe interior widths are 59, 45,
31 and 17. At every step, all 154 raw fields of both trajectories in the safe
interior match the full-colony arrays. In particular, the central 17 cells stay
correct through the entire comparison. Another 102 complete scalar outputs
are checked.

The halo check completes in **2.843270 s**, with **189168 KiB** process peak
RSS (185076 KiB sampled). Artifacts:
`figs/fixed_rule/retimed_holder_upper_halo_v1.json/.npz`.

The geometric argument concerns G on the upper cells. It does **not** bound
the physical influence of a lower burst during a work period by seven lower
colonies. That separate transfer claim must account for actual mail, head
transport, flags, malformed encoded fields and retained nonMEM Data.

## Reproduction and remaining obligation

Both runs are CPU-only, terminal with return code zero, and use existing private
native binaries. No GPU scheduling or shared source changes were needed.
The complete commands are recorded in the watchdog receipts; reruns require
fresh output names.

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_upper_embedding_v1_watch.json --seconds 120 --rss-mib 2048 -- python -m experiments.fixed_rule.audit_retimed_holder_upper_embedding --output figs/fixed_rule/retimed_holder_upper_embedding_v1.json
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_upper_halo_v1_watch.json --seconds 60 --rss-mib 1024 -- python -m experiments.fixed_rule.certify_retimed_holder_upper_halo --output figs/fixed_rule/retimed_holder_upper_halo_v1.json
```

Evidence index: `figs/fixed_rule/retimed_holder_upper_embedding_evidence_v1.json`.
The preceding contextual evidence remains unchanged.

Next establish the lower transfer in the larger context: execute a wider
physical burst/recovery/commit with actual inherited banks, or prove a checked
physical boundary relation for the existing trajectory. A wider run should
retain at least the 73 upper positions identified here, preserve all complete
lower controller and nonMEM fields, and continue successive lower periods.
The long interacting-head suffix currently uses a CPU event executor; an
audited private CUDA implementation would make repetition cheaper. Substantial
GPU scheduling remains with the main agent.

The full goal stays active. Complete noisy depth-two evolution, general
amplification and stochastic robustness, robust finite caps, Q/U optimization,
depth three and the existing Flag2/SimBit source-fidelity issues remain open.
