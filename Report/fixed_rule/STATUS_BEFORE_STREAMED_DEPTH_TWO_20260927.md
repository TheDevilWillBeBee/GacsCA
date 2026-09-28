# Fixed-rule agent status

Updated 2026-09-27. **Full Gacs/Gray goal active; not complete.** Please reply in
**Report/fixed_rule/MAIN_AGENT_NOTES.md**; this agent never edits that file.
Latest check found it absent. No shared-source change is requested.

## Priorities and coordination

Correct fixed-rule self-simulation, practical complete depth-two A100 execution,
and measured error correction across levels. Optimize Q/U subject to correctness;
U<=128Q is not required. The user now permits up to 40 GB host RAM; use less when
sufficient. Existing small probes retain their 512 MiB limits. The main agent owns substantial
GPU scheduling; the separate 8 GiB reservation remains pending and unused.
Only owned fixed_rule files/STATUS changed. No shared source, job, CUDA artifact
or historical dataset was modified. All new jobs are terminal.

## Latest milestone: complete-state GPU endpoint operator

[GPU_ENDPOINT_OPERATOR.md](GPU_ENDPOINT_OPERATOR.md) implements the proved C/B
endpoint operators with the one fixed final ROM instruction stream. All state
computations occur on GPU; host rules/formulas are blocked during advancement.
Every terminal bank word is retained. Device width/metadata checks reject bad
encoded Info atomically; full-state import rejects live physical controller,
mail, flags/Wf or invalid distributed Signals. No rule/ROM/alphabet changed.

Four endpoints of the saved two-period random-state physical trace match in all
fields. Their retained GPU endpoint calls total 0.017185 s (physical trajectory
backend: 43.350940 s on that fixture). Healthy/damaged witness calls also match,
retaining 120 different scratch words with equal decoded outputs. Complete
validation: 3.221947 s, 4577324 explicit device bytes, 188156 KiB sampled host RSS.
Independent saved-state audit: 0.549088 s /53000 KiB. Six contract tests and two
width/locality tests pass; all 110 narrow raw fields reject overwide words without
mutation. CUDA memcheck of the six contract tests reports zero errors. Exact
commands, sources, limits and scope are in the report and endpoint evidence index.

This is a noiseless endpoint accelerator on E_loc, not a new physical transition
or a fault handler. Complete depth-two execution is still missing. The next
step is GPU reconstruction/composition B(C(y)) with full raw controller data and
full retained terminal banks, followed by successive decoded top steps. Streaming
a tile plus its halos could use a small GPU buffer and about 5.20 GB host RAM for
two complete one-top-cell depth-two banks. This proposal is unimplemented and
unmeasured; it fits the user's 40 GB ceiling. No large GPU reservation was used.

Owned additions: retimed_holder_endpoint_gpu.py/.cu; validate/audit endpoint GPU
experiments; two endpoint test files; GPU_ENDPOINT_OPERATOR.md, this status and
private build/evidence. No shared changes requested. All jobs are terminal and
GPU occupancy is empty. MAIN_AGENT_NOTES.md remains absent and is the reply
channel. Previous status: STATUS_BEFORE_GPU_ENDPOINT_20260927.md.

## Preserved milestone: complete terminal-state identity and fresh GPU validation

[TERMINAL_STATE_IDENTITY.md](TERMINAL_STATE_IDENTITY.md) accounts for every
terminal Data word, controller, mail, flag and distributed Signal bit. A finite
layout certificate covers all 9916 bank words/colony, 349 last-writer scratch
slots and all 154 raw outputs. Independent fixed-instruction and DAG diagnostic
formulas agree with seven prior saved GPU cases, retaining the 120 differing
scratch words between equal-decoded-output healthy/damaged trajectories.

Fresh 15-colony GPU execution passes two full periods from random complete typed
upper states and random physical scratch, retaining one physical world. All four
precommit/commit endpoints match completely. GPU evolution: 43.350940 s; full
experiment: 46.294618 s; explicit device bound 6406062 bytes; sampled host peak
198252 KiB. Independent audit passes in 2.144950 s/72644 KiB. Ten formula/layout/
snapshot tests and two full-image/literal-commit tests pass. Failed test-import
and initial Signal-checker runs/source are preserved and explained in the report.
No physical rule, ROM, prior CPU/CUDA backend or shared source changed.

The descriptor-semantics argument now gives complete images C(y) at U-1 and B(y)
at U on the localized-Signal noiseless entry domain, using the existing local/
period lemmas. Finite composition gives preterminal C^d(y) and terminal
B(C^(d-1)(y)) at U^d-1 and U^d, respectively. This is a mathematical endpoint
identity, not a new physical macrostep executor or measured depth-two run. All
new host formulas are diagnostics; their outputs are never installed. Arbitrary
outside-group Signals and in-period faults are excluded from this identity.

Owned additions: terminal_{reference,dag,checks,image}.py under gacsca/fixed_rule;
terminal layout certificate, reference auditor, fresh CUDA experiment and saved-
state auditor under experiments/fixed_rule; three terminal test files; this
report/status and private logs/receipts/snapshot. Exact commands and hashes:
TERMINAL_STATE_IDENTITY.md and retimed_holder_terminal_evidence_v1.json.

Next: implement the complete image operator on GPU against the four fresh
endpoints and equal-output/different-scratch witness, then validate depth
composition with fixed data-driven execution and full state reconstruction.
The proposed depth-two terminal bank alone is 2.42 GiB for one top cell; no such
allocation has run. Coordinate substantial GPU use; the prior 8 GiB reservation
is still pending/unused. No shared change requested. MAIN_AGENT_NOTES.md remains
the reply channel. All current jobs are terminal. Archive of previous status:
STATUS_BEFORE_TERMINAL_IDENTITY_20260927.md.

## Preserved milestone: GPU physical faults and encoded-controller repair

[CUDA_ENCODED_REPAIR.md](CUDA_ENCODED_REPAIR.md) reproduces the complete CPU repair
fixture on GPU with both Signal sides and both physical flags. Six lower bit
faults become two persistent wrong encoded rb copies; actual gathering/evaluation
repairs all 2310 raw Hold outputs. A later two-holder pulse repairs in one literal
G tick. Damaged/healthy states differ in scratch at U but rejoin in every field
after the actual U+1 reset and remain equal at 2U. Both GPU trajectories evolve
independently; no healthy state or host upper transition is installed. Controller
fields change 70 then 47 words. Three-copy negative control remains diagnostic.

Paired evolution: 57.610265 s; experiment: 60.515820 s; conservative combined
explicit GPU bound 30178500 bytes; reported host peak 198244 KiB. Nineteen focused
tests pass. Independent audit (1.558722 s, 75888 KiB) checks 34 initial raw-cone
outputs (10 still wrong), 17 late outputs (all healed), all raw macrostep outputs,
and every saved complete rejoin field. The new saved comparison includes flags,
Signals and controllers as well as Data. No rule, ROM, alphabet or Q/U changed.

Broad random-fault memcheck hit the unchanged 512 MiB aggregate RSS threshold
(524724 KiB sampled) and was terminated by its owned watchdog; it is incomplete,
not passing. Retained v1 log/receipt. A narrower literal-transition/budget memcheck
passes with zero errors at 231384 KiB aggregate RSS. The paired run used 90 s
because two trajectories execute; other probes used 60 s. All jobs are terminal
and final GPU process query is empty. The substantial 8 GiB reservation is unused.

Owned additions: retimed_holder_{flags_gpu,resident_general,raw_packed,
resident_faults,general_faults,cuda_general_snapshot} (.py plus flags/faults .cu);
experiments build_retimed_holder_faults_cuda, retimed_holder_cuda_encoded_repair,
audit_retimed_holder_cuda_encoded_repair; four new test files for general faults,
contracts, general resident state and repair audit; this report/status and private
build/evidence artifacts. Exact commands/results/hashes are in the report and
retimed_holder_cuda_repair_evidence_v1.json. No shared source/interface requested.

Next priority: reduce construction/layout/time costs or prove an exact complete-
state macrostep accelerator for practical depth two. Equal decoded outputs with
different scratch at U are a concrete rejection fixture against arbitrary fresh
re-encoding or decoded-only substitution. Retain actual transcript/controller/
Signal state. General stochastic correction, malformed Info and reliable finite
caps remain open; source-fidelity qualifications are unchanged.

## Preserved GPU milestone: two complete successive physical periods

[CUDA_RETIMED_PERIODS.md](CUDA_RETIMED_PERIODS.md) records actual communication,
capture/flags, computation and commit from Info-only initialization, retaining one
state for two work periods. Fifteen nonaliasing colonies pass in 32.609045 s GPU
execution / 33.557215 s experiment time, 6160272 explicit device bytes and
192168 KiB reported peak host RSS. The one-colony pilot passes in 25.688208 s GPU.
Both boundaries match every CPU Data word, controller, packet and persistent
Signal; all 2310 raw Info words match independent scalar/descriptor outputs.
Seventy then 65 upper controller words change. Three gathered histories per period
and both Hold results are checked. The prior initialized-history final-computation
milestone remains frozen in CUDA_RETIMED_EVALUATION.md.

A first complete-period pilot failed despite correct Data: right Signals were
lost because newly supported tail deliveries used physical instead of compact-bank
indices. Failed source, log, driver and old binary are preserved. The fix changes
only new gather-adapter destination mapping; rule/ROM and prior frozen backends
are unchanged. Five packet tests (3.631 s), three mixed-profile tests (22.613 s),
and five audit-rejection tests (1.014 s) pass. A focused corrected-tail CUDA
memcheck reports zero errors. Complete independent 15-colony audit passes in
1.053014 s at 73684 KiB; missing Signals and jointly corrupted raw operands reject.

All runtime probes had 60 s wall limits, 512 MiB sampled RSS thresholds and
<=64 MiB explicit device budgets. Sanitizer aggregate process-family RSS was
223116 KiB. Jobs are terminal; final GPU process query is empty. No shared source,
job or CUDA artifact changed; MAIN_AGENT_NOTES.md remains the reply channel.

Depth-space accounting now follows the actual allocation formula: one top cell
at depth two needs 7.181406 GiB explicit peak; fifteen top cells need 107.686777
GiB. This is algebraic only, not a large allocation or nested run. Current API
caps are recorded too. U^2=2^62 remains the time challenge; no practical complete
depth-two execution is claimed. The substantial 8 GiB reservation remains unused.

Owned additions/edits: retimed_holder_resident_mixed.py,
retimed_holder_resident_gather.py/.cu, retimed_holder_cuda_packets_bridge.py;
experiments build_retimed_holder_gather_cuda, bounded_cuda_process_tree,
retimed_holder_cuda_periods, audit_retimed_holder_cuda_periods,
retimed_holder_cuda_depth_cost; tests test_retimed_holder_cuda_{packets,profile,
period_audit}; this report/status and private evidence/build artifacts. Exact
commands/results are in the report and retimed_holder_cuda_periods_evidence_v1.json.
No shared interface change requested. Next: general-context/literal-fault GPU
execution against CPU repair evidence; reduce staging/layout and execution cost
for complete depth two without weakening the fixed-rule requirement.

## Latest work: literal defects and executed encoded-controller repair

[CPU_ENCODED_REPAIR.md](CPU_ENCODED_REPAIR.md) documents the new exact projected-G
exception layer and repair argument. Every mutable field is retained, and defects
advance only through complete native radius-seven G. Same-time Data rebasing is
checked to preserve actual wrong values; empty exceptions are not called recovery.
Default capacity is 1024 exceptions/4096 candidate outputs. Resource failures do
not discard faults. No physical rule, ROM or alphabet changed.

A complete-descriptor cut finds 119 actual five-copy majority gates protecting
all procedure inputs to all 154 raw outputs. Exhaustive gate checks establish
one-step correction of up to two damaged copies per coherent procedure field,
with unchanged nonprocedure inputs. A wrong Boolean threshold is rejected.
Certificate: 0.207937 s, 38028 KiB RSS. Geometry/Signal/Wf repair is outside it.
Six defect tests pass in 4.383 s and four audit rejection tests in 1.835 s.

The nonaliasing 15-colony experiment passed two complete physical periods in
947.670568 s at 86768 KiB peak RSS. Six physical bit faults became two persistent
wrong encoded rb operands after one lower tick. The actual evaluator repaired
all upper output fields in Hold at capture; a later two-holder procedure pulse
repaired in one literal tick. Complete physical rejoin with an independently
evolved healthy reference passed at U+1 after the real scratch reset. Every one
of 491520 physical cells passed E at both commits. No healthy state was installed.

Independent saved-cone/scalar/descriptor audit passed in 1.510689 s at 78116 KiB.
It checked 34 initial affected raw outputs (10 remain different from unperturbed)
and 17 late affected outputs (all repaired). All 2310 Info words match at each
commit; 70 then 47 represented controller words change. Saved Data rejoin matches;
all-array physical equality is additionally checked during execution. The exact
exception layer used two literal ticks/51 local F calls and rebased two actual
wrong Data words. All jobs are terminal, under the 512 MiB virtual-memory cap.
figs/fixed_rule/retimed_holder_cpu_encoded_repair_evidence_v1.json indexes three
passing manifests, snapshot, ten passing tests, retained failures and prior proof
artifacts. Successful sources remain frozen.

The first three-colony negative control was rejected before evolution because
geometry maintenance cleared its upper controller, making rb corruption vacuous.
The replacement 15-colony control retains the criterion: two bad rb copies repair,
three change 15 raw outputs, and the live controller performs READ_B to WRITE.
The failed source/log are retained. A separate failed defect test had incoherent
healthy Signal-capture buffers; correcting the fixture preserved its random
faults and needed no implementation change. Both failures are documented.

Owned additions: retimed_holder_cpu_faults.py; retimed_holder_cpu_encoded_repair.py,
audit_retimed_holder_cpu_encoded_repair.py, certify_retimed_holder_replica_repair.py;
two new test files, CPU_ENCODED_REPAIR.md and matching evidence. Existing successful
sources remain frozen. No shared changes requested. MAIN_AGENT_NOTES.md remains
absent; please use it for replies, and this agent will not edit it.

## Preserved general physical context

[CPU_GENERAL_CONTEXT.md](CPU_GENERAL_CONTEXT.md) retains both coherent Signal
sides and arbitrary canonical Flag1/Flag2 dynamics. Three colonies passed two
periods (137.951468 s, 67544 KiB RSS), 11 tests and independent output audit.
Its first upper controller changes were clearing, so this fixture is not operand
repair evidence. All 16 two-colony Signal patterns, 2016 selected full-F checks,
cross-colony Flag2 dependence and arbitrary-flag clearing passed (10.294260 s,
67924 KiB). The general-context backend and its proofs remain unchanged.

## Preserved nonaliasing one-link and computation evidence

[CPU_PACKET_PERIODS.md](CPU_PACKET_PERIODS.md) retains two complete periods on 15
colonies with mixed right Signals and zero left Signals: 696.240266 s, 86012 KiB
RSS, 21239796 full raw F calls and 194340 delivered packets. All 2310 raw words
per commit match scalar/descriptor references; 70 then 65 controller words change.
The one-colony pilot and 18 tests remain frozen. This is the current nonaliasing
full-period evidence, still only one link. [CPU_EVENT_EVALUATION.md](CPU_EVENT_EVALUATION.md)
retains the earlier initialized-history evaluation fixture and distance audit.

## Preserved retimed noiseless theorem

[RETIMED_NOISELESS_MACROSTEP.md](RETIMED_NOISELESS_MACROSTEP.md) supplies the
certificate-assisted descriptor-semantics induction F^U(E(y)) subset E(G(y)),
G=pi F iota, for every typed upper configuration, every positive ring size and
the infinite lattice. It includes all controllers and repeated finite encoded
depth. The full entry relation, new geometry/clock transfer, six phase interfaces
and all 154 output widths were checked; ten focused tests pass. This mathematical
result does not validate every backend or count as a measured depth-two run.

## Candidate identity and prior execution evidence

[RETIMED_HOLDER.md](RETIMED_HOLDER.md) records the initial shorter-period milestone.
Its former pending composition obligation is closed by the new proof above.
Q=32768, radius seven, raw 154 words/4090 bits and projected 105 words/2704 bits
remain fixed independently of depth. Age retains 32 physical bits; U=2^31.
The candidate has 17809 instructions, 27721 core cells and 2001129064 controller
path ticks. The earlier complete-expression, ROM-path, timed-memory, open-lattice,
query and Signal certificates remain unchanged. Seventeen earlier literal and
composition tests passed; the first query diagnostic's preserved vocabulary
failure was resolved without modifying a transition.

Physical descriptor: 6e2f29f61bf281ec5d346cd58e717cf7e5b0afea263d2c17a18a58de295d8d23
ROM: 4dc026b976c541001421dd214df9c9e33f6f851053d4ba5f53dbbec925ba5645

The original small_holder proof/executions remain frozen. Its measured trajectory
evidence is two one-link periods plus limited nested windows, not a complete
upper work period at depth two. Old GPU backend certificates do not automatically
cover the retimed ROM/wrap. [NOISELESS_MACROSTEP.md](NOISELESS_MACROSTEP.md),
[IDENTITY_COMPILER.md](IDENTITY_COMPILER.md), and
[BACKEND_DISTANCE_AND_COST.md](BACKEND_DISTANCE_AND_COST.md) retain those scopes.

## Next concrete work and incomplete objective

Use the exact exception layer for controlled geometry defects or predetermined
stochastic noise draws, retaining failed/resource-limited trajectories. Geometry,
Signal and Wf defects now have literal local evolution, but no general recovery
bound or scalable noisy-geometry backend is claimed. Continue retimed GPU
adaptation against saved CPU states; substantial GPU scheduling remains
coordinated with the main agent and no reservation has been consumed. Practical
nested execution also needs construction-cost improvement; faster diagnostics
alone do not address the U^2 physical cost.

Practical complete depth-two execution remains a major open requirement:
U^2=2^62 literal ticks. Further evaluator/layout improvement or proved acceleration
is needed. General cross-level error correction, noisy amplification, repair of
malformed Info and reliable finite-cap behavior remain open. Candidate-B Flag2,
voted-old-Signal D10, printed Flag2/SimBit ambiguity and cap Address-defect
persistence are unchanged. The noiseless relation does not establish the papers'
full correction/amplification hypotheses. Finite depth ends in top initial data
that evolves by the same G; no robust quiescent cap is claimed.

Previous handoff: STATUS_BEFORE_ENCODED_REPAIR_20260926.md. Older status archives
and reports remain intact. Please use MAIN_AGENT_NOTES.md for replies.
