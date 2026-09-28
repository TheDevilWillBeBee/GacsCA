# Compact fixed-rule GPU execution

2026-09-27. The unchanged compact candidate now executes two successive physical
periods on the A100 with sustained represented-controller arithmetic. The full
Gacs/Gray objective remains active. This is a one-link execution milestone; it is
not a complete upper work period at depth two or an error-correction experiment.

## Construction and scope

Physical Q=16384, U=1073741824, radius7, 154 raw words/4090 bits, projected105
words/2704 bits. Physical descriptor and own-ROM hashes remain respectively
53f7adbf7c34df6b17897b20a0d0654108f23a9c064defb89bb3c6d1a7fb846b and
4d055889959a880f189539dc213801780f8e2efa3daa7cb31e72cb3003f48b32.
Nothing depends on requested hierarchy depth. The source basis and qualifications
remain [the noiseless relation](COMPACT16_NOISELESS_MACROSTEP.md): Gray31–32's
specialized hard-wiring/ProgramBit projection and Gacs9.2–9.3's suitably modified
self-correcting rule, not a general-purpose platform requirement.

New private resident CUDA modules retain all mutable coherent controller words,
actual MEM/tail Data, both shifted Signal patterns, and exact packed flags.
Coherent storage is an execution representation, not a new physical alphabet.
Generated local procedure expressions and local controller events evolve state;
host scalar G/F, native-local wrappers and Program.evaluate are forbidden during
advance. Host upper evaluation only supplies independent diagnostic expectations.
One physical state survives both periods without resetting histories or scratch.
Actual packets gather the three histories; both computations, capture, forcing,
flags and commit execute. Protected mail targets come from the compact sparse
layout's 1786 actual targets, not the old dense-history index formula.

The nine-case reduction check covers zero/one head in every phase, all16384
canonical addresses and all2^30 normalized Ages. All28 compared outputs per case
are identical symbolic expressions: procedure fields including mail, geometry,
static fields and Signal. Physical flags/Wf are factored separately using the
previous complete-context certificate and literal packed flag recurrence.
This is conditional coherent-domain algebra, not a proof of the whole CUDA
implementation or arbitrary defective geometry. During nonzero flags/forcing,
mail is rejected; independent packet batches also reject protected controller
accesses. Capacity guards are execution limits, not maximum hierarchy depth.

## Executed results

| Fixture | Physical sites | Periods | GPU evolution | Explicit device bytes bound | Sampled child RSS |
|---|---:|---:|---:|---:|---:|
| CPU comparison, 3 colonies |49152|2|22.151055 s|2415150|166060 KiB|
| Sustained arithmetic, 31 colonies |507904|2|29.970498 s|6335430|171048 KiB|

Each run advances2147483648 physical ticks. Allocations above count backend data
buffers, including both flag buffers and extra event storage; CUDA context,
graphs, runtime/driver allocations are excluded. They are not measured total GPU
process-memory peaks. Both runs use32MiB base/32MiB extra allocation limits,
90s wall/512MiB sampled child-RSS watchdogs. All jobs are terminal. GPU query after
execution is empty. Total host use stayed far below the user's40GB allowance.
The main agent retains substantial GPU scheduling; the older8GiB request is
pending/unused. No shared job, source, dataset or CUDA build was changed.

The3-colony result matches every CPU MEM/tail Data word at both boundaries;
remaining physical Data is zero. Complete represented Info, controllers/mail,
both complete shifted Signal patterns and cleared flags agree. Its upper
controller is correctly cleared by bad geometry: it is not sustained arithmetic.

The31-colony result executes READ_B at15 -> WRITE at16 -> FETCH at17/PC24,
writing18442167835445667631. Represented controller changes are70 then65;
complete projected word changes124 then133. All4774 raw Info words match at each
boundary. Its actual histories and both Hold results are checked. The run records
23035746 logical event evaluations,8711662 colony literal ticks,8458 independent
batches, zero rejected batches, and98306 literal packed flag ticks. Both Signal
sides vary between colonies and between periods. This upper ring still has a
geometry seam; arithmetic remains active away from it. It does not establish
arbitrary-duration healthy upper geometry.

Independent saved-state audit compares scalar F with its complete descriptor at
every upper cell and checks all stored raw Info/controller/Signal data. It passes
in1.127465s. It is independent output validation, not a second physical trajectory.

Seven tests pass: five GPU/native parity tests(4.125s) cover actual WRITE and
intercolony mail, reset/vote/capture, both Signal sides, arbitrary packed flags
and forcing, and atomic protected-access rejection; two CPU audit tests(1.334s)
check sustained arithmetic and reject erased raw-controller Info or Signal bits.
These complement, rather than replace, previous identity/locality/encoding tests.

## Preserved failures

The first reduction checker exhausts its200000-node BDD budget, without a
counterexample. V2 compares interned expressions first and uses separate BDDs
only when needed; every compared expression is identical, so none needs BDDs.
The first GPU period driver reaches its boundary but incorrectly asserts that
the five Signal words are identical. The actual representation is shifted bits
16,8,4,2,1. V2 checks that pattern and also fixes explicit flag-buffer accounting.
Both failed sources/logs/watch receipts remain. No physical rule or kernel changed
to resolve these failures.

## Reproduction and ownership

All modules, tests, reports, binaries and artifacts are private fixed_rule files.
New implementation: compact16_holder_records/packed/prefix_description/flag_profile,
resident_period/independent/mixed/gather/general, and flags_gpu (.py and relevant
.cu). Existing compact CPU and physical-rule sources remain sealed and unchanged.

Commands below use fresh output names; existing evidence intentionally rejects
overwriting. Wrap with `python -m experiments.fixed_rule.bounded_cuda_probe
--output WATCH.json --seconds LIMIT --rss-mib RSS -- COMMAND`.

* `python -m experiments.fixed_rule.build_compact16_holder_gpu --output OUT.json`
  (180s/1024MiB):37.048253s; compiler-child peak194584KiB; no GPU evolution.
* `python -m experiments.fixed_rule.certify_compact16_holder_gpu_reduction_v2 --output OUT.json`
  (120s/768MiB):PASS9cases/252expression identities,1.634043s.
* `FIXED_RULE_GPU_TESTS=1 python -m unittest tests.fixed_rule.test_compact16_holder_gpu -v`
  (90s/1024MiB):5PASS.
* `python -m experiments.fixed_rule.run_compact16_holder_gpu_periods_v2 --reference figs/fixed_rule/compact16_holder_cpu_periods_v1.json --output OUT.json`
  (90s/512MiB):3-colony comparison PASS; total23.171943s.
* Same driver without `--reference` (90s/512MiB):31-colony arithmetic PASS;
  total31.766028s.
* `python -m experiments.fixed_rule.audit_compact16_holder_gpu_periods --execution figs/fixed_rule/compact16_holder_gpu_periods_v2.json --execution figs/fixed_rule/compact16_holder_gpu_active_v1.json --output OUT.json`
  (60s/512MiB):bothPASS.
* `python -m unittest tests.fixed_rule.test_compact16_holder_gpu_audit -v`
  (60s/512MiB):2PASS.

Receipts/logs/watch files use compact16_holder_gpu_{build_v1,reduction_v1,
reduction_v2,tests_v1,periods_v1,periods_v2,active_v1,audit_v1,audit_tests_v1}.
Final integrity seal: compact16_holder_gpu_evidence_v1.json, extending the702-file
CPU execution seal. MAIN_AGENT_NOTES.md remains the main agent's reply channel;
this agent did not edit it. No shared interface change requested.

## Next work

Transfer the complete-state endpoint reasoning to this compact candidate and
measure a practical depth-two run without host replacement of simulated
transitions or loss of scratch/Signal/controller state. Then execute compact
encoded-controller defects and local in-period repair with distinguishing
negative controls. The31-cell ring needs31*Q lower colonies at depth two, so its
cost cannot be inferred from this507904-site one-link run. Ordinary literal
U^2=2^60 evolution remains impractical. General amplification, malformed geometry
and encoding repair, robust finite caps, depth3, printed Flag2 persistence and
computed-SimBit timing qualifications remain unresolved.
