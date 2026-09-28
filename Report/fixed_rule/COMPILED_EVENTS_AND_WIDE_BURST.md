# Faster physical events and an audited 73-colony burst

2026-09-27. The complete previously audited noisy suffix now executes in
**68.831488 s**, versus 547.916526 s for the original Python scheduler. Every
saved complete checkpoint and every event interval agrees. A new physical
burst in the required **73-colony window** also completes and passes its
independent full-state audit. Its subsequent quiet recovery and noisy commit
have not yet executed.

These are steps toward the larger lower-layer transfer experiment identified
in [UPPER_BOUNDARY_EMBEDDING.md](UPPER_BOUNDARY_EMBEDDING.md). They do not yet
establish complete-colony noisy depth-two evolution or a robustness threshold.

## Compiled scheduling, unchanged physical rule

`retimed_holder_compiled_events.py/.cc` moves the existing active-interval event
loop and raw-neighborhood reconstruction into C++. Every literal event calls
the **same native full-F evaluator binary** used by the old implementation.
The full 15-cell physical neighborhood and all 154 lifted words are reconstructed
from the complete global state. Each logical procedure retains all 18 words,
including every controller and packet field, and all Q Data words per colony
remain stored, including nonMEM Data.

The existing guarded transport plan, conservative head-interaction bound and
simultaneous literal updates are preserved. Generated constants describe the
fixed schema and ROM; there is no depth argument, upper-rule interpreter or
depth-specific kernel. G's fixed hard-wiring projection is unchanged. Full-ring
native G still executes commit/reset transitions through the existing global
executor. Compilation products are confined to `figs/fixed_rule/build/`.

The inherited execution domain requires canonical coherent geometry, common
legal Age, fixed ROM, zero flags/Wf, no mail, bounded live controllers inside
each ROM core and no non-head controller residue. Forcing intervals reject.
Transport and local-event compression rely on the same restricted-domain
arguments as the previous executor. This is not a universal backend-equivalence
proof or an arbitrary-fault executor. A rejected literal tick is left uncommitted;
the preceding valid physical state remains available.

Five tests pass in **10.224 s**, including complete-native comparisons of
collisions/reflection, full controller preservation through transport, global
copy rejection, omitted-controller rejection, commit/reset with nonMEM Data,
and valid-state retention after an event-budget stop. Sampled peak RSS is
393104 KiB. The existing frozen tests and modules were not edited.

The full suffix comparison starts at physical time 1232635846 and ends at U+1.
It matches all six complete stored procedure/Signal states, all metrics, and
all **210578 event intervals** of the independently scalar-audited trajectory:

- 100444 literal ticks;
- 792263710 transport ticks;
- 122483647 quiet ticks;
- two complete clock transitions;
- 6231583 full native local output evaluations.

The new comparison takes **68.831488 s** including input validation, checkpoint
comparisons and artifact writing, with 1176984 KiB process peak RSS and 1179680
KiB sampled RSS. The roughly eightfold end-to-end improvement is not an isolated
kernel benchmark. Exact trace and checkpoint agreement supplement the focused
tests and inspected implementation; they do not prove equivalence for every
possible admissible input.

## Actual wider burst

`retimed_holder_wide_burst.py` starts from the complete retained depth-two
checkpoint banks for upper positions 9529–9601. Center colony 36 corresponds
to the actual upper NAND head at 9565. It uses the same fixed GPU rule and the
same unfiltered seed-2026092713 burst: 8404 full-state marks over 32 ticks,
followed by two quiet ticks.

All 2310 gathered raw input words in each of the central 17 colonies (indices
28–44) equal the intended complete upper radius-seven neighborhoods. The
run ends at local time **1232619462**, absolute nested physical time
**2647030067069732806**, with **118 discrepant sites /189 raw words** in colony
36. These include 99 Flag1 sites, five primary Data defects and two extra
primary heads. No error symbol is substituted at an upper layer.

The run takes **29.217253 s**, using a checked explicit GPU bound of **66034424
bytes** (below 64 MiB). Process/sample peak RSS is 508212/510524 KiB. The GPU was
idle before this bounded private run; no shared job, CUDA artifact or source
was changed, and the separate substantial GPU reservation remains unused.
The historical third-link process was not present on the process check;
this is not a claim that its historical experiment completed successfully.

`audit_retimed_holder_wide_burst.py` independently verifies inherited banks,
the real upper checkpoint, all central gathered inputs and the exact noise
sample. It replays all 34 ticks in both full native causal trajectories, with
padding covering the complete possible fault support. All complete exception
sets agree. It checks **2276300 output states /350550200 raw words**, plus
596 full scalar-source outputs, in **31.859397 s** with 353476 KiB process RSS.

The saved-state comparison with the old 17-colony burst also passes:

- All shared initial inherited banks are identical.
- The same complete unfiltered replacement records are used.
- All 34 complete exception sets agree after translation by 28Q physical sites.
- The old central three colonies (7–9) have identical complete background
  banks, active controllers, counts and Signals at the checkpoint and every tick.
- The other 14 old-window background banks already differ at the checkpoint.

This last observation matters: matching local damage does not make the remote
background states interchangeable. The wider continuation must keep its own
actual banks. It must not reuse a narrow-window endpoint or simply insert the
old measured decoded error into a healthy wider fixture.

## Reproduction and next execution

Exact commands, limits, hashes and terminal return codes are in private receipts.
All accepted jobs are terminal with return code zero. Use fresh names for reruns.

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_compiled_events_tests_v1_watch.json --seconds 120 --rss-mib 2048 -- python -m unittest tests.fixed_rule.test_retimed_holder_compiled_events -v
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_compiled_events_audit_v1_watch.json --seconds 180 --rss-mib 4096 -- python -m experiments.fixed_rule.audit_retimed_holder_compiled_events --output figs/fixed_rule/retimed_holder_compiled_events_audit_v1.json
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_wide_burst_v1_watch.json --seconds 180 --rss-mib 4096 -- python -m experiments.fixed_rule.retimed_holder_wide_burst --output figs/fixed_rule/retimed_holder_wide_burst_v1.json
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_wide_burst_audit_v1_watch.json --seconds 120 --rss-mib 2048 -- python -m experiments.fixed_rule.audit_retimed_holder_wide_burst --input figs/fixed_rule/retimed_holder_wide_burst_v1.json --output figs/fixed_rule/retimed_holder_wide_burst_audit_v1.json
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_wide_burst_comparison_v1_watch.json --seconds 60 --rss-mib 1024 -- python -m experiments.fixed_rule.compare_retimed_holder_wide_burst --output figs/fixed_rule/retimed_holder_wide_burst_comparison_v1.json
```

Evidence index: `figs/fixed_rule/retimed_holder_compiled_wide_burst_evidence_v1.json`.
The source report and preceding evidence stay frozen.

The new `retimed_holder_wide_recovery.py` is prepared but **not run**. Next use
it to continue these actual 73-colony states through flag clearing and incoming
head motion, then use the compiled executor through the noisy commit/reset.
Audit wider recovery with correct colony indices; the old scalar recovery
auditor's diagnostic crossing probes are hard-coded to colony 9 and require a
new owned adapter for colony 37. Preserve the three nonMEM Data words. Subsequent
lower periods must start from the actual wider endpoint. Their central decoded
states can then be checked against the full upper-colony trajectory using the
proved upper halo, subject to establishing the lower physical transfer.

The full project goal remains active. General amplification, thresholds, robust
finite caps, Q/U optimization, depth three and Flag2/SimBit source questions
remain open.
