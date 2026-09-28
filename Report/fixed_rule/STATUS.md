# Fixed-rule agent status

Updated 2026-09-28. Full fixed-rule Gacs/Gray goal is active and incomplete.
Please reply in Report/fixed_rule/MAIN_AGENT_NOTES.md; this agent never edits it.
Only new fixed_rule namespace files and mutable STATUS were changed. No shared
source, GPU job, historical data, root/shared report or CUDA artifact changed.
Earlier complete status is archived in
[STATUS_BEFORE_COMPACT16_COMPILER_OPTIMIZATION_20260928.md](STATUS_BEFORE_COMPACT16_COMPILER_OPTIMIZATION_20260928.md).

## User direction

Focus now on Q/U optimization, beginning with promising low-impact changes.
Defer additional stochastic noise sweeps. Stop if a weekly/session limit is
reported; ask before continuing with credits. No limit notice occurred this
turn. User allows up to40GB shared host RAM; these CPU-only jobs used<90MiB
sampled RSS each. Main agent owns substantial GPU scheduling.

## Latest result

[COMPACT16_COMPILER_OPTIMIZATION.md](COMPACT16_COMPILER_OPTIMIZATION.md) details the
new candidate and preserved failed paths. One fixed physical rule F:
Q16384/U2^30/radius7,154raw words4090bits, descriptor
53f7adbf7c34df6b17897b20a0d0654108f23a9c064defb89bb3c6d1a7fb846b.
Compiler candidate's fixed own ROM is
0de4dc9ba97f861a04e975fad7d44a2e5eb5952bc30f3a7d08fac0ea3118c3be.
No depth-dependent parameter or new hardware/opcode; G's ROM metadata differs.

Sharing-aware three-leaf NAND rewrite removes23 descriptor operations. Reverse
output-dependency traversal and scratch capacity270 give12906->12883 instruction
cells,3447->3397 MEM cells,16354->16281 core cells and819159153->811855585
scheduled controller ticks:73cells and7303568ticks saved,0.892% travel.
Physical Q/U stay unchanged. Candidate selected from bounded10-descriptor x9-
capacity search (8.885s/watch9.133s,75112KiB), not global optimum.

Exact verified-domain checks: baseline full154-output arbitrary-typed descriptor
identity; all12 accepted NAND cut truth tables and their recorded labels; complete
output-order dependency mapping; own-ROM symbolic full controller,62010history
instances,355215instructions,2940META calls,26790packets. Final ROM certificate
PASS5.706s/watch5.913s,88824KiB. Three testsPASS5.420s/watch5.642s,
83532KiB, including scalar raw local F agreement and negative mutations of
controller output and false rewrite label. Representative physical full-raw
ALU/SEND/LOAD/HALT/META endpoint/fallback/dispatch path probePASS1.291s,
66820KiB; interior singletonMETA queries1,3396,3397 PASS1.211s,
66956KiB. New-ROM exhaustive path/schedule composition, actual U-tick period,
GPU execution, depth2 endpoints and repair are NOT transferred from old ROM.

First NAND cut pass grew10452->10489 operations by duplicating shared nodes;
archived and rejected. Typed low-bit masking pass gave10operations but lacks
full-output proof; rejected. First ROM wrapper lost Python kwdefaults; corrected.
One mutation test found a gap in recorded truth-label validation; checker fixed,
search/ROM proof rerun as v2/v3 and tests nowPASS. First META singleton helper
rejected unsupported negative affine query coefficient; successful limited
checks use scoped adapter. Failed versions and logs remain. No physical-rule
failure is claimed from these helper exceptions.

A read-only count finds1746 two-NAND AND cones,1610 with exclusive inner NAND.
Next first substantial candidate: add one fixed binary AND operation to physical
F/controller; measure net self-description/ROM/core/travel after closure. Estimate
and caveats in report. This is an opportunity count only, not implemented gain.
Even fully fusing those pairs alone cannot fit Q8192/U2^29. ROM loops or a new
execution layout may be required after this candidate. Do not reuse old macrostep
or noise certificates without rechecking the new rule/ROM.

## Evidence and commands

Corrected seal figs/fixed_rule/compact16_compiler_optimization_evidence_v2.json:
1149files+9external banks, all1086 prior files unchanged. v1 seal accidentally
hashed its own in-progress empty log, and is preserved as invalid history.
[Correction](COMPACT16_COMPILER_SEAL_CORRECTION.md). v2 excluded its own log and
watch. Its watch PASS4.895s/53220KiB; the entire v2 manifest was separately
rehash-checked. The new mutable STATUS and v2 own log/watch are not sealed.

python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_compiler_search_v2_watch.json --seconds 60 --rss-mib 512 -- python -m experiments.fixed_rule.explore_compact16_compiler_v2
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_compiler_rom_v3_watch.json --seconds 120 --rss-mib 1024 -- python -m experiments.fixed_rule.certify_compact16_holder_compiler_rom_v3
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_compiler_tests_v2_watch.json --seconds 90 --rss-mib 512 -- python -m unittest tests.fixed_rule.test_compact16_compiler_candidate_v2 -v
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_compiler_paths_v3_watch.json --seconds 120 --rss-mib 768 -- python -m experiments.fixed_rule.probe_compact16_compiler_paths_v3
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_compiler_meta_hit_v3_watch.json --seconds 120 --rss-mib 768 -- python -m experiments.fixed_rule.probe_compact16_compiler_meta_hit_v3
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_compiler_optimization_evidence_v2_watch.json --seconds 60 --rss-mib 512 -- python -m experiments.fixed_rule.seal_compact16_compiler_optimization_v2

Prior63-cell repair audit remains valid only for the unchanged old-ROM candidate;
its previous full status and independent evidence lineage are retained.
Printed Flag2 persistence and computed-SimBit timing remain source qualifications.
No further stochastic noise testing is planned at this stage.
