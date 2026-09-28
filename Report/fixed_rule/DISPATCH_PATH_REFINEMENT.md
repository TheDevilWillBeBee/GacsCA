# Dispatch to the next matching FETCH

2026-09-26. The conditional dispatch catalog covers 20,802 routes: 20,796 live
instruction successors, five reset entries and one vote entry. Each preserves
the complete controller and Data until matching FETCH. This closes the travel
obligation left by [ordinary instruction paths](INSTRUCTION_PATH_REFINEMENT.md)
and [META paths](META_PATH_REFINEMENT.md), under mail-free hypotheses. It does not
establish whole-program composition with packet traffic.

## Relation and new local identity

Let M=9922 be the memory prefix length. A rightward FETCH head at h <= M+pc reaches
target instruction pc in exactly M+pc-h ticks, before executing that FETCH. All
eight controller fields, including stale operands/value/ALU fields, are retained.
Zero-distance dispatch is the identity; nonzero paths must fit inside one of the
seven certified regular clock intervals.

The checker splits memory and program flight and verifies actual ROM guards.
Program flight requires pc != index. FETCH on memory ignores even a matching
index, so reusing the older unequal-index flight lemma would reject valid entry
paths. The new MEM/FETCH identity checks all 154 raw output fields at nine holders
in each of seven regular clock intervals. Other hypotheses remain canonical
geometry, coherent static/procedure copies, one head, zero Signal/flags/Wf and no
incoming mail. The earlier descriptor-support certificate supplies the quiet
exterior. No physical rule, ROM, state width or GPU kernel changed.

The catalog derives successor positions from completed instruction contracts,
including the live IF_THIRD outcome. Every actual non-HALT instruction is
represented. It tags 6478 direct SEND successors as requiring packet composition.
**Every route assumes mail-free input.** A false `requires_mail_composition` tag
means only that the immediate predecessor is not SEND; it does not establish
absence of packets emitted earlier. SEND successors are conditional catalog
entries, not physical runs with their packets removed.

## Verified execution and audit

The physical pilot contains six initialized entry tasks and four continuous
non-SEND successor tasks, each with six Data/controller patterns: 60 dispatches.
Successors execute a predecessor, travel to the next instruction and execute
its FETCH in one GPU world without installing intermediate states. Initialized
entries are separate fixtures; they do not establish reset/vote production of
those states. Pilot successors are actual PCs 0 and 1 at Ages 1 and 738197505.

The expanded selected-site GPU run is **not verified**. Its first launch request
timed out in automatic approval before process creation. One retry returned no
recoverable completion result. A subsequent read-only check found no expanded
artifacts or dispatch process. No further launch was made.

The driver uses the unchanged physical event backend for flights and literal GPU
steps at instruction boundaries. Host evaluator, full-rule and primary controller
calls are disabled during evolution. CPU expected-state calculations are solely
diagnostics. Complete logical records are saved and selected complete raw records
are checked. This is not a full microstep replay or full-colony scan.

| Check | Result | Seconds | Peak host KiB |
|---|---:|---:|---:|
| Conditional catalog | 20,802 routes passed | 11.942461 | 78,848 |
| Focused tests | 6 passed | 1.906 | not recorded |
| Physical pilot | 60 dispatches, 942 full-state probes | 1.847032 | 215,612 |
| Independent CPU audit | passed | 1.398509 | 70,664 |

Tests cover matching memory index, stale controller retention, rejection of the
old unequal-index lemma and overshooting the matching instruction, zero-duration
paths, entry coverage and SEND accounting. Pilot GPU advance took 0.036166 s;
recorded process GPU memory was 422 MiB and explicit allocation 3,726,576 bytes.
No large allocation or CUDA rebuild was used.

The independent audit derives all routes directly from actual ROM instructions.
It checks 189 complete scalar/native outputs with matching memory indices, 40
complete scalar/native next-FETCH outputs, all 942 saved logical records and the
expected raw-probe digest. Input evidence, source and archive hashes are checked.
Actual GPU raw-probe assertions reside in the hashed driver; the audit does not
independently recover unsaved raw records.

## Completed commands

Existing outputs are protected from overwrite. Reproduction needs fresh names.

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.certify_small_holder_dispatch_paths --output figs/fixed_rule/small_holder_dispatch_paths_v1.json
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_dispatch_paths.py -v
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_dispatch_execution --pilot --output figs/fixed_rule/small_holder_dispatch_execution_pilot_v1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_dispatch_paths --certificate figs/fixed_rule/small_holder_dispatch_paths_v1.json --execution figs/fixed_rule/small_holder_dispatch_execution_pilot_v1 --output figs/fixed_rule/small_holder_dispatch_paths_pilot_audit_v1.json
```

SHA256 provenance:

- Catalog: `2b50084aaca44620740568e1033836aa3bb6d8d03049e83a23861ab2ea71b06d`.
- Pilot manifest: `4d807be665f46fffe929a6dc172702214217610d510555a2f0d379f30bb125e2`.
- Pilot archive: `315e1be2269d28549a3e2becc52fcfcb8faed2ec175dd80eb32893ec2a44997f`.
- Audit: `c5aeba818cdf18f78b5c67f36a5103e6fd6cf28035f5061af285f3d63d2cdf6b`.

The audit manifest records exact source and input hashes.

## Remaining work and coordination

Next: packet transport, crossings, delivery priority and flag guards composed
with actual ROM noninterference conditions; then clock/Signal/reset/rest joins
into a whole-period relation. Full upper depth-two work periods, reliable finite
termination and general cross-level noise suppression remain open. Gray pp.31–32
and Gacs sections9.2–9.3 remain the source target: specialized self-description
includes the evaluator's complete rule/state. No alternate evolution interpreter
was added by these diagnostic proofs.

Actual self-simulation, practical two-level GPU execution and measured cross-level
repair remain the acceptance priorities. Optimize Q/U subject to correctness;
U<=128Q is not required. Neither Q nor U changed here.

Owned additions: dispatch certificate/test/physical driver, independent audit,
this report and namespaced evidence. Only our STATUS handoff was edited among
existing reports. No shared module, job or dataset changed. MAIN_AGENT_NOTES.md
was absent; please reply there. The separate 8 GiB scheduling request remains
pending and unused. The historical third-link process was not observed; absence
is not an audit of experiment completion.
