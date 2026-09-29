# Retimed GPU full-field faults and executed encoded-controller repair

2026-09-26. The fixed retimed rule now reproduces the CPU's targeted physical and
encoded-controller repair trajectory on GPU, including both physical Signal
sides and both flags. Fifteen nonaliasing colonies execute two complete lower
periods in a damaged trajectory and an independently evolved healthy trajectory.
The healthy reference is never installed in the damaged state.

This is targeted correction across one simulation link, not a stochastic
threshold, a general Gacs amplification theorem, or a complete upper work period
at depth two. The full project goal remains active.

## Executed repair

Six physical one-bit Data faults encode two wrong copies of an upper `rb`
operand. Their three damaged lower Data replicas spread to five wrong coherent
replicas during the first literal lower tick. A representation rebase retains
those wrong values; empty exceptions is explicitly not called recovery. The
raw Info still decodes to the damaged upper state.

Actual physical gathering and computation then produce the healthy complete
upper output in Hold at Age 1224000000, while Info remains wrong until commit.
A later pulse corrupts every procedure field at two physical holders around a
live lower controller at Age 1230000100. One complete local G tick repairs that
pulse, including controller and packet fields under the two-sided flag context.

At U=2147483648, all raw Info matches the repaired simulated transition, but
physical scratch Data still differs from the separately evolved healthy world.
The next actual scratch reset at U+1 makes **the complete physical states equal**:
all Data, live controllers/packets, Signals, both packed flags, geometry/clock
and derived Wf. Both trajectories remain equal at 2U. Neither trajectory is
reinitialized between periods. All 2310 raw simulated words are checked per
macrostep; 70 then 47 upper controller words change.

A three-copy upper `rb` corruption changes the intended output. That is an
independent diagnostic negative control, not a third full physical GPU run.
Initial faults, all saved raw probes, both physical boundary Data banks and
rejoin Data agree with the frozen CPU experiment in
[CPU_ENCODED_REPAIR.md](CPU_ENCODED_REPAIR.md).

## Mechanism and locality

New `retimed_holder_flags_gpu.py/.cu` carries the exact packed Flag1/Flag2
recurrence on canonical geometry with coherent fixed Signals. It assumes no
particular front shape. New `retimed_holder_resident_general.py` composes that
GPU recurrence with the already checked communication/controller executor under
the established mail-free forcing-domain factorization. Separate flag storage
is an execution representation, not additional physical state or per-level
hardware. The wrapper deliberately has a distinct type so a reference reader
that omits Flag2 cannot silently accept it.

New `retimed_holder_resident_faults.py/.cu`, `retimed_holder_general_faults.py`
and `retimed_holder_raw_packed.py` adapt the earlier owned full-state exception
engine. They store all 105 mutable projected physical fields, losslessly packed
with the 49 derived metadata fields. Every literal exception step evaluates the
complete radius-seven descriptor on GPU. Metadata is normalized from the actual
output Address after each tick, so geometry defects evolve as G=pi F iota.
Neither a healthy-domain rule nor a host upper transition substitutes for that
literal evolution.

Preparation evaluates actual and counterfactual background G on the affected
radius-seven outputs. Full-state equality alone permits exception removal. The
counterfactual background includes any wrong values already rebased into it; it
is distinct from the separately evolved healthy comparison world. Data rebasing
requires all five actual copies to agree. Flag rebasing preserves every derived
Wf copy before modifying the packed background. Tests retain wrong coherent Data
and wrong flag fronts after exception removal to distinguish representation
changes from repair.

The exception/frontier capacity is 8192, an execution resource bound, not a
hierarchy-depth bound or changed alphabet. Frontier overflow rejects before
state change. A new bounded literal budget stops at the exact current state.
The tests check owner-clock guards and a mutation outside radius seven that
cannot change a center output. Device preparation reads physical neighbors only;
reconstruction from coherent background storage is valid under its stated
representation relation.

The physical rule, ROM, Q/U, state width and neighborhood are unchanged. The
self-description still includes all evaluator/controller fields. No level
dispatch, new physical register pair, general-purpose platform, or recursive host
interpreter was introduced. The source choices remain the specialized hard-wiring
and complete-controller construction documented in
[RETIMED_NOISELESS_MACROSTEP.md](RETIMED_NOISELESS_MACROSTEP.md), with the existing
candidate-B Flag2 and voted-old-Signal D10 limitations.

## Measured resources and checks

The paired GPU trajectories used **57.610265 s** of evolution; the complete
experiment took 60.515820 s. Each trajectory advanced 4294967296 physical ticks.
The conservative simultaneous explicit allocation bound, including both worlds,
both flag stores, the exception engine and one staged controller batch, was
30178500 bytes (about 28.8 MiB). The exception engine itself uses 18579456 bytes.
Reported peak host RSS was 198244 KiB; the watchdog sampled 199804 KiB.

This experiment used a 90 s watchdog because it advances two independent
trajectories. Other probes used 60 s. All used the same 512 MiB sampled physical
host-RSS threshold. Builds used a 1 GiB per-process virtual-memory cap and private
hash-addressed artifacts; build time was 36.207369 s, child peak RSS 243792 KiB.
CUDA runtime does not use RLIMIT_AS because CUDA reserves a large virtual address
space. RSS sampling every 20 ms is not an instantaneous OS memory cap.

Nineteen focused tests pass:

- Seven full-state fault tests, 3.242 s: complete random projected faults across
  the flag lifecycle, interior geometry/procedure repair, wrong-Data preservation,
  Wf-consistent flag rebasing, packed atomic updates, wrong-front evolution and
  clock/type rejection.
- Five contract tests, 1.475 s: every raw field/width, arbitrary packed flags
  against the exact CPU recurrence at clock boundaries, literal-budget state
  retention, atomic frontier overflow and radius-seven locality.
- Two general-background tests, 2.887 s: full raw one-step transitions with both
  Signal sides and a live controller, repeated advances and sidecar clock/clearing.
- Five independent audit rejection tests, 4.585 s: intact receipt passes;
  premature fault erasure, omitted controller state, non-Data rejoin mismatch and
  a corrupted saved literal transition fail.

The independent audit took 1.558722 s at 75888 KiB peak RSS. It recomputes all
raw outputs through separately evaluated scalar F and the full descriptor,
followed by the fixed projection. The initial six faulty physical sites yield
34 checked outputs, ten different from their clean counterparts: the lower
corruption really survives. The late two-site pulse yields 17 checked outputs,
all equal to their clean counterparts. It also validates normalized active
records, complete Data banks, Signals and packed flags in saved damaged/healthy
rejoin snapshots. This strengthens the prior CPU saved audit, which retained
both full rejoin Data arrays but relied on runtime equality for other fields.

The broad CUDA memcheck of random full-field faults across all tested flag epochs
was stopped by the resource watchdog at sampled aggregate RSS **524724 KiB**,
just above the 524288 KiB threshold. It is not a passing memory check. Its log and
watchdog receipt are retained. A smaller full-state literal-transition/budget
check completed in 1.207 s with **zero memcheck errors**, at 231384 KiB aggregate
family RSS. This narrower result does not establish memory-check coverage of the
entire flag lifecycle. The memory ceiling was not increased.

## Artifacts and commands

Source/evidence hashes are in
`figs/fixed_rule/retimed_holder_cuda_repair_evidence_v1.json`. Primary execution
and snapshot: `retimed_holder_cuda_encoded_repair_v1.json/.npz`; independent audit:
`retimed_holder_cuda_encoded_repair_audit_v1.json`. All paths below are owned.
Use `OPENBLAS_NUM_THREADS=1` for all commands. CPU audits/tests additionally use
`ulimit -v 524288`; the build uses `ulimit -v 1048576` in its separate shell.

```sh
python -m experiments.fixed_rule.build_retimed_holder_faults_cuda --output figs/fixed_rule/retimed_holder_faults_cuda_build_v1.json
FIXED_RULE_GPU_TESTS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_general_fault_tests_watch_v1.json --seconds 60 --rss-mib 512 -- python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_general_faults.py -v
FIXED_RULE_GPU_TESTS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_fault_contracts_watch_v1.json --seconds 60 --rss-mib 512 -- python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_fault_contracts.py -v
FIXED_RULE_GPU_TESTS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_general_tests_watch_v1.json --seconds 60 --rss-mib 512 -- python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_resident_general.py -v
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_cuda_encoded_repair_watch_v1.json --seconds 90 --rss-mib 512 -- python -m experiments.fixed_rule.retimed_holder_cuda_encoded_repair --output figs/fixed_rule/retimed_holder_cuda_encoded_repair_v1.json
python -m experiments.fixed_rule.audit_retimed_holder_cuda_encoded_repair --input figs/fixed_rule/retimed_holder_cuda_encoded_repair_v1.json --output figs/fixed_rule/retimed_holder_cuda_encoded_repair_audit_v1.json
python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_cuda_repair_audit.py -v
FIXED_RULE_GPU_TESTS=1 python -m experiments.fixed_rule.bounded_cuda_process_tree --output figs/fixed_rule/retimed_holder_cuda_fault_memcheck_watch_v2.json --seconds 60 --rss-mib 512 -- /usr/local/cuda/bin/compute-sanitizer --tool memcheck --error-exitcode 99 python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_fault_contracts.py -k literal_budget -v
```

The retained resource-stopped memcheck uses
`test_retimed_holder_general_faults.py -k complete_random_faults` and v1 output
names. GPU availability was checked before the paired experiment and both memory
checks. Final GPU process query was empty. No substantial reservation, shared
CUDA build, shared source, existing job or historical dataset was changed.

## Implication for practical depth two

Equal decoded outputs do **not** determine the complete physical boundary state:
the damaged and healthy runs have identical repaired Info at U yet different
scratch histories, and only rejoin at U+1. Therefore the noiseless encoding
relation alone does not justify replacing a macrostep by decoded upper stepping
and an arbitrary fresh encoding. An exact shortcut must preserve/reconstruct the
actual scratch, Signal and controller state, including dependence on earlier
inputs. The newly saved paired states are a distinguishing fixture for such work.

Practical complete depth two remains open: U^2=2^62 represented ticks, and the
current nonaliasing 15-top-cell allocation projection exceeds the A100's memory.
Next priority is construction/layout cost reduction or a proved complete-state
macrostep accelerator, validated against these full trajectories. Do not add
external level dispatch or discard physical transcript state to obtain a faster
but different task. General stochastic robustness, arbitrary geometry recovery,
malformed Info repair, reliable finite termination/caps and full amplification
hypotheses remain unproved. Existing printed Flag2/SimBit ambiguities remain.
