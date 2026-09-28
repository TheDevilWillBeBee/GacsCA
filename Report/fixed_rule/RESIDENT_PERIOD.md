# Two complete successive GPU work periods

2026-09-26. One resident GPU state completed two physical work periods through
one simulation link. All 154 decoded fields, including active controller changes,
match two successive applications of the complete self-described physical rule.
Both complete coherent physical checkpoints match the existing CPU executor.
This advances the earlier capture-only GPU result through maintenance waves,
recomputation, commit, clock wrap and restart. It does not establish nested
hierarchy execution or general noisy repair.

## Construction and supported domain

New `small_holder_resident_period.{py,cu}` preserves the physical rule from
[SMALL_HOLDER.md](SMALL_HOLDER.md): Q=32768, U=4294967296, radius seven,
154 raw words/4090 bits, and the same hard-wired ROM. The complete description is
`af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`.
The controller specialization retains digest
`6c96c7b7299f68fa0f1880521215c50cf0ab32cc65f6ca3315ae0c19dfee550f`.
This execution backend is independent of encoded depth. It adds no physical
state fields or new physical instructions. The frozen prefix backend is unchanged.

As in [RESIDENT_PREFIX.md](RESIDENT_PREFIX.md), each colony keeps its actual Data
bank and sparse controller/mail/Signal records on GPU. Canonical geometry and
coherent backup fields are reconstructed. The suffix composes this controller
with the existing physical Flag1/Wf1 recurrence, whose four-regime symbolic
certificate is checked against the complete physical descriptor. It also accepts
uniform right Signal zero, where all physical flags/Wf stay zero; boundary tests
check that case against the full native rule. It rejects mixed right Signals,
left Signal one, broken five-copy Signal layouts and any nonzero suffix mail.
This is an explicit restricted family, not a representation of arbitrary faults.

The composition is justified by the physical rule's coupling: Flag1 clears mail,
and clears procedures/Data only if the Address changes. Canonical geometry keeps
Address unchanged, and the suffix requires every mail field to be zero. Any
computed suffix mail is rejected before commit. Thus the four flags may be
factored out of controller computation on this domain. Physical reads reconstruct
the actual wave at the requested Age and Address. Wave evolution is accelerated
using its local-recurrence certificate, not by evaluating a simulated transition
on the host. Arbitrary flag patterns cannot enter this backend through restoration.

Stationary Signal patterns now survive exact transport and quiet-time skips.
Skips still stop at physical operations, delivery/crossing, resets, capture,
phase changes and final commit. All five reset phases and the second temporal
vote are included. Vote history inputs are disjoint from vote destinations;
Info destinations are disjoint from adjacent Hold sources, avoiding in-place
bulk-operation races. Final commit copies actual Hold to Info and wraps Age.
Data, controllers and Signals stay in the same allocated world for the next
period. The host neither re-encodes parents nor replaces simulated transitions.

`World.from_stored` restores full coherent core/tail records, including every
controller field and actual Data. It validates geometry, widths, flags and the
suffix domain. Gap rows have the canonical zero-procedure representation; this
interface does not restore arbitrary nonzero gap state. `World.decode` reads all
154 Info words and verifies all seven metadata records against the fixed lift.
These interfaces are for initialization/checkpoint diagnostics, not evolution.

The source interpretation remains explicit: candidate-B Flag2 maintenance and
old-Signal D10 timing are modified-rule choices. Gray pp.31–32 and Gacs 9.2–9.3
motivate the specialized complete self-description; they do not supply a theorem
for this altered schedule. The user priorities and the reason U/Q=128 is not a
constraint are recorded in [PRACTICAL_SELF_SIMULATION.md](PRACTICAL_SELF_SIMULATION.md).

## Verification and measured result

Commands from repository root:

```sh
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p 'test_small_holder_resident_period*.py' -v
# 10 tests, 31.298 s, OK.
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_resident_two_periods --output figs/fixed_rule/small_holder_resident_two_periods_v1
# Passed, 362.42415993474424 s total.
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_resident_two_periods --input figs/fixed_rule/small_holder_resident_two_periods_v1 --output figs/fixed_rule/small_holder_resident_two_periods_audit_v1.json
# Passed, 1.4256222564727068 s, 330516 KiB maximum host RSS.
```

The ten tests include six prefix/event regressions and four period tests. They
check the symbolic profile certificate; full-raw native comparisons at wave,
reset and commit boundaries; every raw encoded parent field across clock wrap;
restart with carried Signals; rejected suffix profiles; and atomic rejection of
newly computed mail. Event tests compare literal evolution with skipping, including
transport, writes and cross-colony packets. Frozen physical identity/locality and
self-description tests remain the separate evidence from SMALL_HOLDER.md.

The experiment uses 15 distinct encoded parents, covering 491520 physical cells.
There is one GPU World and one set of buffers throughout 8589934592 physical ticks.
The CPU chain separately evolves the initial prefix, physical suffix and recurrent
prefix from its actual committed checkpoint. Seven checkpoints per period compare
210 full-raw physical samples each. At both commits, all core/tail records and
all omitted gap cells agree with the CPU execution. Host evaluator/rule entry
points are patched to raise during GPU advance; host upper-rule calculations
occur only as independent diagnostics.

| Measurement | Result |
|---|---:|
| Successive work periods at one link | 2 |
| Literal physical ticks | 500150 |
| Certified transport/quiet ticks | 8589434442 |
| Local logical evaluations | 188417025 |
| Combined GPU advance wall time | 321.372800 s |
| Whole experiment with CPU checks/artifact writing | 362.424160 s |
| Explicit device buffers | 5116680 bytes |
| Observed total GPU process memory | 424 MiB |
| Maximum host RSS | 841980 KiB (822.25 MiB) |
| Changed raw procedure fields, first / second step | 45 / 41 |

The active simulated WRITE produces `0x123456789ABCDEF0`. The independent audit
checks scalar/native/complete-description agreement at both upper steps, all
154 decoded outputs, every gather history, protected vote, Info/Hold word,
carried Signal, canonical clock/flags, and stored/gap hashes. It verifies all
22 recorded source hashes, the binary and artifact hashes. Snapshots alone do
not prove trajectory provenance: the one-allocation/no-host-transition claim
comes from the separately hashed execution driver and its runtime checks.

Binary SHA256:
`b801bc221f4e4c7752654e35630c8376e56f343c177679b9c79209d513403596`.
Artifact SHA256:
`55bcb2cdb7c709abeac934bc7c0dcd1c0e2a0a2856ffa68c7833974a98541768`.
`cuobjdump --dump-resource-usage` on that private binary reports zero stack and
local-memory bytes for all twelve kernels; its output is preserved in
`figs/fixed_rule/small_holder_resident_period_kernel_resources_v1.log`.

## Remaining work and ownership

The main practical obstacle is still genuinely nested execution. Q lower
colonies have an estimated explicit storage cost of about 5.06 GB, but no such
allocation/run has been made. Distinct metadata queries remove much of the
shared-time skipping benefit, as measured in RESIDENT_PREFIX.md. Independent
local event scheduling or exact batching needs an explicit causal argument and
comparison tests before a large nested run. The U squared physical horizon is
2^64; memory availability alone cannot make a literal simulation practical.

The coherent resident representation still needs integration with the existing
full-raw exception backend to retain faults and support nonuniform Signals.
Actual finite-depth boundary dynamics, general maintenance/Flag2 profiles,
simulated-layer repair and measured cross-level noise amplification remain open.
The deterministic Flag1 wave here is not evidence of stochastic noise robustness.

New owned files: `gacsca/fixed_rule/small_holder_resident_period.{py,cu}`;
`tests/fixed_rule/test_small_holder_resident_period{,_prefix,_events}.py`;
`experiments/fixed_rule/{small_holder_resident_two_periods,audit_small_holder_resident_two_periods}.py`;
this report, STATUS.md, and the named logs/results/private build under
`figs/fixed_rule/`. No shared source, existing datasets or shared CUDA artifacts
were changed. All experiment/audit handles exited zero and the device query was
empty afterward. The protected historical third-link job was not seen; its
absence is not evidence of successful completion. The main agent retains GPU
scheduling and should reply in MAIN_AGENT_NOTES.md. No shared patch is requested.
