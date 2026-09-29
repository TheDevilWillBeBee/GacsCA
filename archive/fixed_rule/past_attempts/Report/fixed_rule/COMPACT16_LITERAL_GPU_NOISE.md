# Complete literal CUDA and longer noise recovery

2026-09-27. The fixed-rule goal remains active. This milestone adds a GPU
implementation of the **complete** projected physical rule G and continues all
eight high-rate failures from the preceding unfiltered noise experiment.
No transition, alphabet, ROM, Q or U changed.

## Implementation and validity domain

`gacsca/fixed_rule/compact16_holder_dense_gpu.{py,cu}` compiles the existing full
F description using reusable interleaved workspace. Every output uses exactly
15 complete neighboring cells (radius seven). Each tick computes all 154 fields,
then applies the fixed pointwise ProgramBit/metadata projection defining G.
The 105 mutable G fields include every raw controller and backup field. Invalid
canonical geometry, nonzero flags, multiple heads, mail and arbitrary typed
controller words are supported; coherent-state fast-path premises are absent.
Metadata must initially match the fixed projection; mismatches are rejected.

Two GPU arrays hold successive full physical states. Every physical tick launches
the same kernel. The host swaps array pointers and schedules tick counts; it does
not evaluate, repair, re-encode or replace transitions. Workspace reuse and the
512 backend workers do not add physical registers or select rules by depth.
The fixed descriptor remains 53f7adbf...fb846b, ROM 4d055889...f48b32,
Q=16384, U=1073741824, F=154 words/4090 bits. Source justification remains Gray
pp.31–32 specialized hard-wiring/ProgramBit projection and Gács §§9.2–9.3
simulation of an identical or suitably modified self-correcting rule. This new
executor supplies no missing amplification theorem.

Four opt-in GPU tests passed in15.567s: arbitrary complete typed states on
1/17/257-site periodic rings for successive ticks; two saved damaged states with
flags/controllers for four ticks; radius-seven isolation; rejection of bad state
width, metadata and allocation budget. GPU calls run with host evaluator entry
points patched to fail. These checks supplement existing depth/ROM/controller
closure tests; finite parity tests are not a proof of general CUDA equivalence.

## Experiment

The prior experiment applied unfiltered Bernoulli whole-G-state replacements on
65 sites for16ticks, then8quiet ticks. Its p=.1 trials all retained damage. Here
the complete healthy colony is evolved literally for24ticks on GPU and checked
against24native CPU ticks. Its retained401-site window must exactly equal the
prior healthy window. Each actual saved window then replaces the same positions
at the same clock. Radius-seven support bounds establish that the complement
is healthy. This is exact restoration, not a fresh encoding or clock reset.

All eight actual full-colony states are then independently continued for512
literal GPU ticks without additional faults. Checkpoints are1,2,8,32,128,511,512.
Healthy complete checkpoints and sorted actual differences retain every raw word
losslessly. This diagnostic compression is never used to implement transitions.
The GPU run evaluated75,890,688 complete site transitions in85.869481s; watchdog
86.338474s, peak sampled host RSS525392KiB. Only one GPU world exists at a time;
its explicitly allocated buffers total52,363,264bytes (driver/context excluded).
No substantial GPU reservation or shared CUDA rebuild was used.

## Results after520total quiet ticks

| Trial | Differing sites | Differing raw words | Primary Data differences | Primary computation heads |
|---|---:|---:|---:|---|
|0|631|695|7|extra head plus healthy head|
|1|667|679|8|healthy head retained|
|2|629|714|8|two extra heads plus healthy head|
|3|646|701|8|no head|
|4|599|702|8|two displaced heads|
|5|618|685|3|one displaced head|
|6|600|654|8|expected position, wrong PC|
|7|668|754|15|no head|

The healthy head is at3666, phase0, PC2217. Trial6 has PC2473 there.
All eight agree with healthy Address/Age. All retain Flag1 and Data differences;
six retain Flag2, five Signal differences, and two right-mail differences.
The final flagged region has557–610 differing Flag1 sites. Thus these are real
raw-computation disturbances, not just metadata or diagnostic discrepancies.
Nevertheless this is a nonterminal clock: none of these observations establishes
permanent failure or the eventual decoded macrostep result. The earlier two-tick
repair lemma does not cover these dense continuing-fault histories/flag fronts.

An independent native audit replays the first32ticks of every trial and checks
the last transition511→512. Complete saved comparisons at1/2/8/32/512 cover
655360outputs,100925440raw words. Another64complete scalar outputs check residual
frontiers and periodic seams. All saved difference counts/field classifications
and projected metadata are checked. Audit50.526545s, watchdog50.876347s,
210664KiB peak sampled RSS. The native/scalar checks pass. The intervening
128/511 trajectory remains GPU-only; no universal backend-equivalence claim.

## Commands and evidence

All commands below exit0. Their `.log` and `_watch.json` receipts share the output
stem. The test watchdog bounds were120s/768MiB; continuation240s/2048MiB;
audit180s/1024MiB. The host RAM allowance is40GB; these runs stay far below it.

```sh
FIXED_RULE_GPU_TESTS=1 python -m unittest tests.fixed_rule.test_compact16_holder_dense_gpu -v
python -m experiments.fixed_rule.compact16_holder_dense_noise --output figs/fixed_rule/compact16_holder_dense_noise_v1.json
python -m experiments.fixed_rule.audit_compact16_holder_dense_noise --output figs/fixed_rule/compact16_holder_dense_noise_audit_v1.json
python -m experiments.fixed_rule.diagnose_compact16_holder_dense_noise
```

The new evidence manifest is `figs/fixed_rule/compact16_holder_dense_noise_evidence_v1.json`.
It preserves all911previously sealed files and nine external banks, and binds
the new sources, complete-state artifact, receipts, private generated header and
binary. The noisy trajectories are preserved as regression inputs.

## Next work and limits

Literal execution measured about16ms per complete colony tick, useful for
damaged local evolution but far too slow for an entire U≈10^9work period. A
practical noisy depth-two simulation needs a justified accelerator that retains
nonzero flag fronts, arbitrary Data/Signals, and multiple or missing controllers.
The existing coherent/noiseless endpoint shortcuts cannot replace these states.
Next distinguish propagating flags, stable stored errors and actual computation
repair through the next reset/retrieval epoch, then inspect the decoded output.
Any new skip rule must be checked against this literal backend.

General amplification, arbitrary malformed-encoding recovery, reliable finite
caps, sustained depth-two top arithmetic and depth3 remain unresolved. This
bounded local-noise continuation is neither a threshold estimate nor a
cross-level stochastic experiment. Known Flag2/SimBit source qualifications
remain as documented in the preceding reports.
