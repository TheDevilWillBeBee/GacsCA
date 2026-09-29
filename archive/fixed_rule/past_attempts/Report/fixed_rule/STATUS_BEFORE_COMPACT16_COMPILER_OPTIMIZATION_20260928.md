# Fixed-rule agent status

Updated 2026-09-28. Full Gacs/Gray construction is NOT complete.
Please reply in Report/fixed_rule/MAIN_AGENT_NOTES.md; this agent does not edit it.
No shared-source change requested. Previous status and history are preserved in
[the archived status](STATUS_BEFORE_COMPACT16_UPPER_REPAIR_AUDIT_20260928.md).

## User priorities and limits

Correct fixed-rule self-simulation; practical sustained depth-two computation;
eventual correction across levels. Optimize Q and U; U<=128Q is not required.
Defer additional stochastic noise sweeps. Deterministic repair and adversarial
validation remain useful. Host RAM ceiling40GB. Main agent owns substantial GPU
scheduling. Latest work was CPU-only, peak183360KiB, no shared jobs/artifacts
modified. All owned audit/profile/seal jobs completed successfully.

NEW USER INSTRUCTION: when a weekly/session limit is reported, stop and ask
before using credits. Do not retry after a limit notice. Remaining allowance and
billing mode are not visible through these tools.

## Latest independently audited milestone

[Report and optimization analysis](COMPACT16_UPPER_REPAIR_AUDIT_AND_OPTIMIZATION.md).
Unchanged Q16384/U2^30/radius7,154 raw words4090bits, projected105 words2704bits.
Descriptor53f7adbf7c34df6b17897b20a0d0654108f23a9c064defb89bb3c6d1a7fb846b;
ROM4d055889959a880f189539dc213801780f8e2efa3daa7cb31e72cb3003f48b32.

63 encoded upper cells contain an active evaluator; two adjacent upper cells
have all105 mutable fields set to their maximum legal values. One lower GPU
world executes two continuous work periods without host re-encoding. First
macrostep differs from healthy at2sites/32raw words; second rejoins all9702raw
words. Represents1032192physical sites. Experiment37.239422s. This is initial
encoded upper damage, not a new stochastic lower-noise history. Periodic seam
lies outside the repair cone; this is not a complete Q-cell upper colony.

Independent audit PASS:252 scalar upper outputs;217476 initial bank words;
869904 pre/post bank words via instruction reference;434952 committed bank words
via separate SSA reference;3240 complete active-record field comparisons;
317915136 full raw physical commit words across every site at both commits.
The local repair cone also matches evolution of the original full-Q fixture.
Audit25.012476s/watch25.391996s,183360KiB sampled RSS, exit0. Continuous in-period
execution still relies on guarded event acceleration and its certificates/parity;
no claim of independently replaying all2U physical ticks.

Coherent-epoch backend:5 tests PASS65.652s/watch66.177022s,290476KiB; covers full
forcing interval vs literal canonical GPU, reset/capture, mail guard and inactive
heads. Whole-clock stationary-Signal BDD:123bits/4921nodes,0.273954s,90 procedure
outputs independent of oldSignal; capture exception has mutation witness.
Explicit experiment device peak core+flags8978670bytes plus<=1837080 staging;
conservative combined10815750bytes excludes driver/compiler overhead.

Seal figs/fixed_rule/compact16_holder_upper_repair_evidence_v1.json:
1086files+9external banks; all1050 prior files and all banks unchanged.
Sealwatch16.903892s/53360KiB/exit0. Includes new backend/tests/proof, complete
repair artifact and audit, cost profiles and this milestone report/status archive.
Mutable STATUS and seal's own log/watch are excluded.

## Cost findings and proposed optimization

Current core16354cells:12906instructions(78.9%),3447memory,1marker. Descriptor
10452operations,7864NANDs. Two evaluations consume90.6% of819159153 controller
path ticks. NAND paths cost259460492ticks per evaluation. Cost v1 omitted the
5522-tick forcing halt; preserved v1 is superseded by v2, no candidate changed.
Q8192 with current memory/gap requires8192 fewer instructions. U2^29 requires
at least34.5% less controller-path time; removing clock slack alone cannot do it.

Concrete priority: stronger complete-DAG Boolean identities and joint operation/
storage scheduling; then benchmark a few fixed binary primitives to replace
NAND expansion. Larger changes: shared counted loops for repeated holder/gather
routines and bidirectional operand access. Every candidate must include new
controller state in its own description and reclose/retest the full ROM and
successive macrosteps. Gray p.31 promises sufficiently large Q with unspecified
program constants, not an executable Q8192 fit. No optimization gain beyond the
existing compact16 reduction is yet implemented/proved.

## Commands and owned additions

python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_holder_encoded_upper_repair_audit_v1_watch.json --seconds 240 --rss-mib 2048 -- python -m experiments.fixed_rule.audit_compact16_holder_encoded_upper_repair
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_holder_cost_profile_v2_watch.json --seconds 60 --rss-mib 512 -- python -m experiments.fixed_rule.profile_compact16_holder_costs_v2
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_holder_upper_repair_evidence_v1_watch.json --seconds 60 --rss-mib 512 -- python -m experiments.fixed_rule.seal_compact16_holder_upper_repair_audit

New audit/profile-v1/profile-v2/seal drivers, report and status archive; figures,
receipts and logs under fixed_rule only. Existing coherent_image/coherent_epochs,
backend tests, Signal certificate and63-cell experiment now included in the seal.
No existing sealed source/data was edited. No new GPU build or run for this audit.

## Remaining work

The separately retained next-period eight-history experiment completed but is
not independently audited here. Existing failed high-rate histories remain
preserved; defer further stochastic sampling. Next develop measured compiler/
architecture candidates, then extend sustained execution to whole upper colonies.
Full correction/amplification, general malformed-code/geometry repair, reliable
finite caps, sustained depth-two upper work periods and actual depth3 remain open.
Candidate-B Flag2 and voted-old-Signal D10 are explicit source qualifications.
The fixed-rule self-description and conditional noiseless block relation remain
established milestones; they do not establish all of Gacs/Gray noise robustness.
