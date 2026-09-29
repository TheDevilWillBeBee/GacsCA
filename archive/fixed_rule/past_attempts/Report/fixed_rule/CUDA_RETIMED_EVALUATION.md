# Retimed CUDA final-evaluation phase

2026-09-26. **A GPU execution milestone, not completed depth-two self-simulation.**
The unchanged retimed fixed rule/ROM now has a private CUDA execution adapter
checked against the complete CPU state for its final computation phase. All
histories are supplied in the initial fixture. Gathering, capture, commit, a full
GPU work period, and a complete depth-two trajectory were not executed here.

## Measured result

| Colonies | Represented physical ticks | CPU evolution | GPU evolution | Explicit device peak | Sampled host RSS peak |
|---|---:|---:|---:|---:|---:|
| 1 | 790020767 | 2.476783 s | 4.669128 s | 2865368 bytes | 174480 KiB |
| 15 | 790020767 | 32.947347 s | 4.760917 s | 6137112 bytes | 190128 KiB |

The 15-colony phase is about 6.92 times faster on GPU; the one-colony phase is
slower. These are single-run observations on an idle A100, not statistical
benchmarks. Both use guarded event scheduling, not one kernel per physical tick.
The GPU timing includes the before-last snapshot and first independent-library
load. GPU initialization took 0.358416 s and 0.267870 s respectively. The full
15-colony process, including the CPU reference, took 38.699690 s.

The 15-colony execution performed 1067538 colony event ticks and 2775116 logical
local evaluations. The head was still present immediately before the predicted
last tick, then every controller field became zero. Every actual Data-bank word
and every active controller/location matched the CPU state before and after
execution. The final 2310 raw Hold words match both independent scalar and
complete-descriptor upper-rule evaluations, and the frozen earlier CPU output
hash. This includes the evaluator/controller outputs; it is not an opcode test.

## Rule identity, representation, and acceleration

Q=32768, U=2147483648, physical radius seven, raw 154 words/4090 bits, projected
105 words/2704 bits. No alphabet, physical transition, encoded rule, parameter,
or depth-dependent case was added. The descriptor is
`6e2f29f61bf281ec5d346cd58e717cf7e5b0afea263d2c17a18a58de295d8d23`;
the ROM is
`4dc026b976c541001421dd214df9c9e33f6f851053d4ba5f53dbbec925ba5645`.

New `retimed_holder_resident_period`, `retimed_holder_resident_independent`,
`retimed_holder_prefix_description`, and `retimed_holder_packed` files adapt the
older owned small-holder backends. Retimed parameters regenerate the local
expression and CUDA constants. The distance function is byte-for-byte identical
to the function audited for this retimed ROM by the CPU distance certificate.
That transfer covers the distance function only; it does not certify every
ported CUDA code path.

Twenty-five coherent logical fields and lossless bit packing are backend storage,
not a new physical alphabet. Five adjacent logical procedure records reconstruct
all physical replicas. The initialized domain requires canonical geometry,
coherent replicas, zero Signals/flags/Wf, zero mail, at most one controller per
colony, and zero non-MEM Data. A single GPU worker per colony evaluates the actual
specialized physical expression at local events. Checked travel skips stay
inside a regular clock interval. Emitted mail and unsupported controller shapes
reject the entire staged batch. CUDA does not evaluate a decoded upper rule.

The host bridge only transfers an already-existing physical initial state.
The new snapshot API reads all actual MEM/tail Data and all valid sparse records;
it does not read uninitialized allocation slots. Under the declared domain,
these arrays plus common Age and fixed metadata determine the complete physical
configuration. Unrepresented non-MEM Data is identically zero. Raw snapshot
record Age/Data can be stale storage fields; physical reads derive them from
common Age/the actual bank, and comparisons explicitly use those authoritative
values. No evolving physical state is omitted from the comparison.

The complete-F CPU oracle finishes before GPU evolution. `Program.evaluate`,
`f.local_step`, and `r.local_step` are monkeypatched to throw during GPU batches.
This is a check against accidental host substitution, not a general proof of all
possible backend implementations. The inherited period backend also contains
other communication/flag-profile paths; this milestone does not validate their
complete retimed execution merely because the port compiles.

## Validation and artifacts

All outputs are under `figs/fixed_rule/`; their hashes and source inventory are
in `retimed_holder_cuda_evidence_v1.json`.

- Build: `retimed_holder_cuda_build_v1.json`, both private shared objects built
  in 7.296933 s. Parent peak RSS 42084 KiB; child peak 190500 KiB. Build logs and
  generated headers are in private hash-addressed directories.
- CPU contracts: four tests, 1.024 s. Packing checks every field width. The
  specialized expression matches complete native-F dynamic outputs over
  controller phases, core endpoints, all seven META selectors, and retimed clock
  boundaries with zero context. The initial test fixture used the wrong Wf
  attribute prefix; its failure and source are preserved as `...contract_v1.log`
  and `...contract_failed_v1.py.txt`. Corrected mapping uses `w2_wf*`; no rule
  or GPU transition was changed in response.
- GPU cone/rejection tests: four tests, 2.264 s. Twenty-two controller cases
  compare all 154 raw fields at three outputs after three literal radius-seven
  ticks. SEND, event-budget, device-budget, and clock-boundary rejections preserve
  the complete stored physical state and clock.
- Independent saved-state audit: 0.738216 s, 64324 KiB peak RSS. Checks every
  Data word, complete initial/final controllers, all raw Hold words, descriptor
  and ROM identity, source/artifact hashes, and the previous CPU Hold hash.
- Audit rejection tests: five tests, 0.681 s. Missing controllers, absent active
  initial computation, residual GPU controllers, and unrelated Data corruption
  fail; the intact receipt passes.

Exact invocations (output/log names distinguish pilot, full1, and full15):

```sh
ulimit -v 1048576
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.build_retimed_holder_cuda --output figs/fixed_rule/retimed_holder_cuda_build_v1.json
```

CPU tests/audit use `ulimit -v 524288` and `OPENBLAS_NUM_THREADS=1`:

```sh
python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_cuda_contract.py -v
python -m experiments.fixed_rule.audit_retimed_holder_cuda --input figs/fixed_rule/retimed_holder_cuda_full15_v1.json --output figs/fixed_rule/retimed_holder_cuda_audit_v1.json
python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_cuda_audit.py -v
```

GPU probes use a separate shell without RLIMIT_AS because CUDA reserves virtual
address space. The watcher samples physical RSS every 20 ms and kills only its
own direct child on threshold/time violation; this is not an instantaneous OS
RSS cap. Every probe completed normally, well below its limits.

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_cuda_full15_watch_v1.json --seconds 60 --rss-mib 512 -- python -m experiments.fixed_rule.probe_retimed_holder_cuda --colonies 15 --full --output figs/fixed_rule/retimed_holder_cuda_full15_v1.json
FIXED_RULE_GPU_TESTS=1 OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_cuda_events_watch_v1.json --seconds 60 --rss-mib 512 -- python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_cuda_events.py -v
```

The pilot omits `--full` and uses 100000 ticks; full1 uses `--full` without
`--colonies 15`. Explicit device allocations are capped at 32 MiB for the base
world and 32 MiB for staged Data. Driver/context allocations are additional.
The A100 had no compute processes before the probes or at the final check.
No shared CUDA artifacts, existing GPU jobs, or historical datasets were changed.
The main agent's separate substantial-run reservation remains unused.

## Remaining work

Port/check actual packet gathering and physical clock boundaries against the
frozen full-period CPU trajectory. Carry both Signal sides and literal defects
before claiming GPU correction experiments. The current GPU result accelerates
one component; it does not solve U-squared cost for a full depth-two work period.
Practical depth two still requires construction/layout improvement or justified
additional acceleration. General cross-level correction and amplification,
malformed-Info repair, source ambiguities, and reliable finite-cap behavior remain
open. The full project goal stays active; U<=128Q is not imposed.
