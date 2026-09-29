# Fixed-rule agent status

Updated2026-09-27. **Full Gacs/Gray goal active; not complete.** Please reply in
**Report/fixed_rule/MAIN_AGENT_NOTES.md**; this agent never edits that file.
Latest check found it absent. No shared-source interface change requested.

## Priorities and coordination

Correct actual fixed-rule self-simulation, practical complete depth-two A100
execution, and measured error correction across levels. Optimize Q/U subject to
correctness; U<=128Q is not required. User allows40GB total host RAM. Main agent
owns substantial GPU scheduling; older8GiB reservation remains pending/unused.
Only small GPU probes ran, each under64MiB explicit buffers/90s watchdog. Runtime/
context/graph allocations are excluded; total GPU process peaks were not measured.
No shared source/job/dataset/build changed. All owned jobs terminal; final GPU and
third_link_initialized/owned-probe process checks empty. No job was stopped.

## Latest: complete compact terminal identity and executed depth-two endpoints

[COMPACT16_ENDPOINTS.md](COMPACT16_ENDPOINTS.md) records exact domains, mathematical
composition, code, commands and evidence. Physical Q16384/U2^30/radius7,
154words4090bits and own ROM unchanged. Descriptor53f7adbf...fb846b,
ROM4d055889...f48b32; full hashes in report/seal. No depth-specific transition,
ROM, register set or evaluator. Gray31–32 specialized hard-wiring and Gacs9.2–9.3
modified self-correcting rule remain the basis, with existing qualifications.

Complete terminal bank has3447MEM+5tail words:2067history,689vote,154Info,154Hold,
49regenerated input metadata,320result,6query and8reserved. Reserved6=MASK, not0.
Final10821instructions include98metadata queries; every15-bit Address query is
folded to14bits, includingzerooffset. Structural certificatePASS; independent
instruction/DAG formulas match every word in four earlier physical GPU boundaries.
A corrected raw s0_value replica bit gives identical decoded output but28different
retained bank words. Both CPU/GPU preserve these; fresh re-encoding is rejected.

Conditional E_loc noiseless complete identities: G^(U-1)(E_loc(y))={C(y)},
G^U(E_loc(y))={B(y)}, G(C(y))=B(y), B(y) in E_loc(G(y)). Complete-state induction
then gives depth-d precommit C^d(y), committed B(C^(d-1)(y)). Uses compact sealed
clock/path/mail/query/period lemmas, full last-writer accounting and localized
Signals. This is certificate-assisted mathematics, not proof-assistant assurance
or general CUDA equivalence. No arbitrary faults may be skipped.

Fresh3-colony physical run: random typed upper states, arbitrary scratch and
localized Signals, two retained periods/four precommit+commit states. Every bank,
controller/mail/Signal record and flags matches formula and GPU endpoint. Physical
22.927559s; endpoint calls0.013243s; explicit buffers3848426bytes;
watch28.951972s/169264KiB. Same state retained; no host transition during evolution.

Tiled depth-two run:1periodic random top,268435456physical sites,2complete retained
endpoints representing2305843009213693952ticks. Every lower bank saved; following
top decoded from actual GPU output. Top raw words change77then1. Total11.176365s,
GPU calls2.696662s, explicit device peak25220232bytes, watch11.710063s/610580KiB.
56557568bank words/452460544bytes per endpoint;2523136complete intermediate raw
words checked each time. Not literal U^2 replay, arbitrary-time evolution or
sustained top arithmetic; the one-cell periodic top is aliased.

First independent auditPASS8.408104s: complete initialization/all intermediate/top
raw fields, bank integrity and28complete scratch rows. Additional exhaustive SSA
recomputationPASS17.881877s: all113115136bank words and every Signal across both
endpoints. Uses512-row batches, retaining all SSA values independently of physical
allocation reuse. Watch18.211468s/602056KiB. Total host use far below40GB.

13testsPASS:5terminal4.674s,2endpointGPU2.106s,6tiledGPU8.097s. Reject changedmask,
controller omissions, wrongallocation, scratch loss, bad raw widths/ownmetadata,
incomplete collection/partial freeze/badbudgets.317complete native-F commit sites.
Full halos, image access and device decode tested. No failures in this milestone.

Owned additions: compact16_holder_terminal_reference/dag/checks/image,
endpoint_gpu/tiles(.py/.cu),endpoint_image_array; terminal/layout/endpoint/depth2/
all-scratch audit/seal experiments; three test modules; COMPACT16_ENDPOINTS.md,
archivedSTATUS and private CUDA/evidence artifacts. Only fixed_rule namespaces.
Final seal figs/fixed_rule/compact16_holder_endpoints_evidence_v1.json verifies
831files and3external banks; all775prior files and old2.6GB bank unchanged. New
external banks are the two452MB complete compact depth-two outputs.

## Next concrete work and limitations

Implement compact physical encoded-controller and in-period defect evolution;
require negative controls and complete-state rejoin before endpoint acceleration.
Then broader top rings, sustained top arithmetic at depth two, and cross-level
noise experiments. Reuse prior retimed ideas only after compact-domain validation.
Small probes remain available; coordinate before substantial GPU scheduling.

Arbitrary faults inside skipped intervals, general full-alphabet correction/
amplification, malformed geometry/Info repair, reliable finite caps and depth3
remain open. Candidate-B Flag2, voted-old-Signal D10, printed Flag2 persistence,
computed-SimBit ambiguity and cap Address-defect persistence remain qualifications.
The project goal is active; noiseless endpoint execution does not establish the
papers' stochastic hypotheses or error correction across levels.

## Preserved history

[COMPACT16_GPU_BACKEND.md](COMPACT16_GPU_BACKEND.md): two actual31-colony physical
periods with READ_B15->WRITE16->FETCH17/PC24;29.970498s,507904sites,70then65
controller changes, both Signal sides,7tests. This is sustained one-link arithmetic.
[COMPACT16_EXECUTION.md](COMPACT16_EXECUTION.md): CPU full-F event reference.
[COMPACT16_NOISELESS_MACROSTEP.md](COMPACT16_NOISELESS_MACROSTEP.md): complete
compact descriptor relation and its conditional proof/certificate obligations.
[Previous status](STATUS_BEFORE_COMPACT16_ENDPOINT_20260927.md) preserves earlier
compact milestones and links to retimed depth-two/repair history. Those results
remain separate; no retimed noisy theorem was silently transferred to compact16.
MAIN_AGENT_NOTES.md is the other agent's reply channel and remains unedited.
