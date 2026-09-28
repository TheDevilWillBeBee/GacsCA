# First fixed-ROM compiler optimization

2026-09-28. A sharing-aware Boolean resynthesis plus dependency ordering and
scratch-capacity search produces a smaller, faster **fixed-ROM candidate** while
leaving the physical rule F, alphabet, radius, Q and U unchanged. This is a
compiler improvement, not a new Q/U pair or a complete physical macrostep for
this ROM. The scientific objective remains open.

## Result

| Measure | Previously executed compact16 ROM | New candidate |
|---|---:|---:|
| Physical Q/U |16384 / 2^30|16384 / 2^30|
| Raw state / neighborhood |154words,4090bits/radius7|same|
| Core cells |16354|16281|
| MEM cells |3447|3397|
| Instruction cells |12906|12883|
| Controller path ticks per period |819159153|811855585|
| Optimized descriptor operations |10452|10429|

The exact improvements are73core cells,23 instructions and7,303,568 scheduled
controller ticks (0.892%). The ROM changes from
4d055889959a880f189539dc213801780f8e2efa3daa7cb31e72cb3003f48b32 to
0de4dc9ba97f861a04e975fad7d44a2e5eb5952bc30f3a7d08fac0ea3118c3be.
F's complete descriptor remains
53f7adbf7c34df6b17897b20a0d0654108f23a9c064defb89bb3c6d1a7fb846b.
The new projected G is therefore a different fixed self-simulation candidate.
No depth selector or additional physical word/register/opcode is introduced.

The accepted configuration is: sharing-aware three-leaf NAND cut rewriting,
reverse traversal of output dependencies, original child order, and scratch
capacity270. Search across10descriptors x9capacities used bounded CPU time8.885s,
peak75,112KiB. This is one deterministic search over explicit candidates, not
an optimality claim. The result still fits the same reset, gather, capture,
forcing and evaluation windows; the complete timing certificate is in the
ROM receipt. Q8192/U2^29 are still out of reach. This is not a measured GPU
runtime improvement; the event backend can skip many controller-flight ticks.

## Verification and limits

The baseline optimized descriptor was previously established equivalent to all
154 raw F outputs for arbitrary typed neighborhoods. The new cut verifier checks
every rewrite by all eight Boolean assignments and checks its recorded truth
label. A separate dependency-order certificate ensures that every original
output remains present. The new own-ROM symbolic calculation processes complete
controllers, all62,010 history instances,355,215 instructions,2940 metadata
queries and26,790 packets on symbolic typed input colonies. It compares every
raw field via the two verified compiler transformations, including metadata
regeneration before each evaluation. Certificate5.706s/watch5.913s,
peak88,824KiB. Three focused tests pass in5.420s, including random and
clock-boundary scalar F agreement; mutating an output controller field or
rewrite label fails verification.

Representative full-raw physical event paths pass for ALU operations, SEND,
LOAD, HALT, endpoint/fallback META and dispatch. A separate singleton proof
passes interior META queries at addresses1,3396,3397. The existing affine
checker treats some other singleton endpoints as unequal even when they agree
at that singleton; those failed probes remain recorded. These checks are
**not** exhaustive path composition. In particular no new-ROM complete U-tick
physical period, two-level endpoint, repair or GPU speedup is claimed. All
older physical experiments retain the old ROM and cannot be transferred.
The next gate for promotion is complete new-ROM instruction/META/dispatch and
schedule composition, followed by actual continuous periods on a private GPU
build using this ROM.

The first three-leaf pass locally saved gates but increased the global DAG from
10452 to10489 operations by duplicating shared expressions; its source and
rejection receipt are retained. The sharing-aware pass keeps only12 of97
proposed rewrites, rejects85 and removes23 operations. A typed low-bit mask
rewrite gave only10operations and lacks an independent full-output certificate;
it was not selected. The first certificate wrapper lost a Python keyword
default; the corrected wrapper and all earlier failure logs remain. One mutation
test exposed that the cut checker originally ignored its recorded truth label;
this was fixed and the search/ROM certificate were rerun as v2/v3. Failed probe
versions are retained. No failures are silently counted as successful evidence.

## Next optimization target

The candidate descriptor contains1746 two-NAND AND cones,1610 of whose inner
NANDs are used solely by the outer inversion. A **fixed binary AND opcode**
could fuse those1610pairs into one instruction each; this is structural
opportunity count, not a measured gain. If all such pairs survived a new
self-description and controller implementation, the direct instruction savings
would be1610, substantially larger than this compiler-only result. There are
also690 OR cones but only16 have both inverse operands exclusive, so AND is
first. A naive estimate using the current average NAND path is about53million
controller ticks per evaluation; it excludes recompilation, changed travel and
new controller overhead. We must build a new fixed local rule, include that
opcode/controller in its own ROM, and rerun complete source and physical checks
before claiming any benefit. Even optimistic fusion alone cannot fit Q8192;
ROM loops or a different execution layout would still be needed.

Gray's p.31 program-size argument allows specialized routines and loops with
unspecified constants. Gacs9.2-9.3 permits a suitably modified self-correcting
rule. A new opcode is acceptable only if the resulting F/G and hardware remain
fixed across depth and account for the opcode in their self-description.

## Reproduction

```sh
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_compiler_search_v2_watch.json --seconds 60 --rss-mib 512 -- python -m experiments.fixed_rule.explore_compact16_compiler_v2
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_compiler_rom_v3_watch.json --seconds 120 --rss-mib 1024 -- python -m experiments.fixed_rule.certify_compact16_holder_compiler_rom_v3
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_compiler_tests_v2_watch.json --seconds 90 --rss-mib 512 -- python -m unittest tests.fixed_rule.test_compact16_compiler_candidate_v2 -v
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_compiler_paths_v3_watch.json --seconds 120 --rss-mib 768 -- python -m experiments.fixed_rule.probe_compact16_compiler_paths_v3
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_compiler_meta_hit_v3_watch.json --seconds 120 --rss-mib 768 -- python -m experiments.fixed_rule.probe_compact16_compiler_meta_hit_v3
```

All owned runs were CPU-only; no shared CUDA artifact, GPU job, source module,
historical dataset or main-agent note was modified. The user permits40GB RAM;
these runs used well below1GB each. Further statistical noise sweeps are deferred.
