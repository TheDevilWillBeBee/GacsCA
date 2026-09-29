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

## Latest milestone: timed cross-level correction with inherited scratch

[TIMED_DEPTH_TWO_REPAIR.md](TIMED_DEPTH_TWO_REPAIR.md) streams the complete lower
checkpoint B(M_(a-1)) at aU for actual middle evaluator Age a=1232619428. Its Info
matches every raw field of the executed M_a. Ten explicit bottom bit flips encode
two wrong middle rb replicas; one lower period repairs the running NAND step.
Fifteen bits encode three replicas and change 15 actual middle output words.
The same fixed GPU operator/ROM/alphabet is used in every case.

After the repaired step, 120 physical bank words remain different (90 history,
30 votes). After a second lower period, all 324927488 bank words and every Signal
rejoin. All six full banks are retained. Independent audit checks 30277632 raw
middle output words, 54 complete scratch rows, every physical pulse and full-bank
rejoin; pass in 31.818229 s /5617740 KiB peak host RSS.

Literal full-physical prefix checks now cover initially incoherent 4/6/9-bit
pulses at that same checkpoint. Every causal output matches both native and
scalar physical rules. Four bits repair immediately; six/nine couple after one
literal tick to the executed ten/fifteen-bit reference trajectories, respectively.
The wrong encoded words explicitly survive the six/nine-bit first tick. These
are exact physical couplings before a shortcut, not projection into its domain.

GPU runs: checkpoint 21.050353 s; healthy 46.876611 s; two 46.065193 s; three 25.325487 s.
Explicit GPU peak 52880184 bytes. Three pulse tests pass in 0.241 s; literal-prefix
audit 4.188438 s /62004 KiB. All jobs terminal. No new CUDA build, physical rule,
ROM, shared-source change, substantial reservation or prior artifact modification.

Scope remains targeted deterministic pulses at a bottom work-period boundary
inside actual middle computation. General timing/full-alphabet stochastic noise,
source ambiguities, robust caps and depth three remain open. Next extend literal
prefix tests to geometry, Signal and controller faults at colony boundaries;
retain failures and reject non-rejoining inputs from endpoint acceleration.

Owned additions: checkpoint_pulse.py; timed depth-two GPU driver, full-bank audit,
literal physical-prefix audit, pulse tests, TIMED_DEPTH_TWO_REPAIR.md and private
evidence. Exact commands/resources in the report. Please reply in MAIN_AGENT_NOTES.md;
still absent. Prior status: STATUS_BEFORE_TIMED_DEPTH_TWO_20260927.md.

## Preserved milestone: timed repair in an actual running evaluator

[ACTIVE_EVALUATOR_REPAIR.md](ACTIVE_EVALUATOR_REPAIR.md) executes a middle colony
from its true initial encoding to Age 1232619428, immediately before NAND ROM
instruction 7075 reads operand B. Two physical rb-replica bit faults repair in
one literal full-G tick; the head performs READ_B->WRITE and computes NAND.
The entire state then rejoins and remains equal through the work-period end.
The three-copy control leaves five exceptional holders and 15 wrong raw words.
No healthy successor installation or representation rebase is used.

Complete raw checkpoints at a-1/a/a+1/a+2 preserve all evaluator/transport fields.
A separate CPU full-descriptor audit executes five entire 32768-site ticks,
checking 25231360 raw output words; all match. Independent scalar source checks
also match all 33 affected outputs. Four new snapshot tests pass (1.719 s).
Driver 21.491857 s, explicit GPU peak 24232408 bytes, host peak 425956 KiB;
audit 5.984145 s /397728 KiB. All jobs terminal. Same private GPU binaries reused.
No physical rule, ROM, alphabet, prior evidence or shared source changed.

Scope: timed targeted physical-controller correction in a real running middle
colony, not yet an encoded-bottom fault at this new checkpoint. Next stream the
complete bottom checkpoint B(M_(a-1)) at aU, inject explicit Info-replica faults,
and compare its next decoded state against actual M_(a+1), retaining scratch.
General stochastic noise, geometry/cap recovery and depth three remain open.

Owned additions: active_snapshot.py; active evaluator GPU driver and whole-lattice
auditor; snapshot tests; ACTIVE_EVALUATOR_REPAIR.md and private evidence. Please
reply in MAIN_AGENT_NOTES.md; still absent. No shared change requested. Prior
handoff: STATUS_BEFORE_ACTIVE_EVALUATOR_20260927.md. Exact commands in the report.

## Preserved milestone: executed depth-two encoded-controller correction

[DEPTH_TWO_ENCODED_REPAIR.md](DEPTH_TWO_ENCODED_REPAIR.md) runs the exact initial
physical fault sets through the unchanged fixed GPU operator. Fifty bottom bit
flips produce two wrong top rb copies; actual GPU dynamics repairs the complete
raw top transition and performs READ_B->WRITE/NAND. The 75-bit three-copy control
keeps the central phase READ_B and differs in nine raw top fields. Faults are
applied to the healthy physical encoding before GPU decode; no damaged/healthy
oracle is installed. The whole nested initial domain is checked.

Healthy/damaged trajectories remain different in 39740 Data-bank words after
the first repaired top step (including 600 Info words encoding middle scratch).
All 324927488 bank words and every Signal agree after the second endpoint, giving
complete physical rejoin within the canonical reconstruction. Full audit checks
all five banks, exact physical fault lists, every intermediate/top raw field and
70 independent scratch rows; a separate audit recomputes 16 full rows chosen from
actual differences across 27 differing tiles. No general noisy interval is skipped.

Healthy/two-copy/control wall times: 50.311789/52.548445/27.350120 s, respectively;
GPU calls: 7.547577/7.771113/3.844533 s. Each case uses 53042568 explicit GPU bytes.
Full audit: 35.259436 s /5149520 KiB reported peak RSS. Eight new CPU tests pass.
No CUDA code, physical rule, ROM, alphabet, prior evidence or shared source changed.
All jobs are terminal; small GPU buffers and host peaks stay below user limits.

Scope: deliberately correlated initial faults preserving E_loc at both layers,
then noiseless intervals with complete endpoint acceleration. The aliased one-cell
top is an unperturbed comparison state, not a canonical top colony or robust cap.
General stochastic noise, arbitrary timed defects and uniform recovery remain open.
Next: checkpoint a middle colony's actual active evaluator, apply literal local
faults and establish explicit correction/rejoin before further shortcuts. Keep
rejecting incoherent inputs; do not round them into the endpoint domain.

Owned additions: initial_info_faults.py; streamed repair driver and two auditors;
two test files; DEPTH_TWO_ENCODED_REPAIR.md, this status and private data/evidence.
Commands and exact scopes: report and retimed_holder_streamed_repair_evidence_v1.json.
No shared change or substantial GPU reservation used/requested. MAIN_AGENT_NOTES.md
remains the reply channel. Prior handoff: STATUS_BEFORE_DEPTH_TWO_REPAIR_20260927.md.

## Preserved milestone: complete retained depth-two endpoints

[STREAMED_DEPTH_TWO.md](STREAMED_DEPTH_TWO.md) executes two successive noiseless
depth-two endpoints with the same fixed tiled GPU operator and the proved B(C(y))
composition. The complete initial raw Info and both 324927488-word bottom banks
are retained. One top cell corresponds to 1073741824 bottom physical sites.
This is exact endpoint acceleration, not literal U^2 replay or fault-time evolution.
No physical rule, ROM, alphabet, prior backend or shared source changed.

All 5046272 intermediate raw words and all 154 top fields match per period.
Every next top input is decoded on GPU from the actual result. Total experiment:
52.659860 s including storage/hashing; GPU operator/transfer/decode calls: 7.570928 s;
explicit GPU peak 53042568 bytes; sampled host peak 2741968 KiB. Independent CPU
audit passes in 14.891052 s, checking the entire initial encoding, every decoded
field, full bank integrity and 28 independently recomputed complete scratch rows.
Six tiled tests and two vector-image tests pass; CUDA memcheck reports zero errors.
The vector audit's initial NumPy unsigned-offset failure/source is preserved.

Depth is actual nested initial Info. A single evaluator reads raw/image storage
through a fixed GPU accessor; no depth-specific transition kernel or register
pair is added. The finite periodic top evolves by G. This is one aliased top cell,
not a nonaliasing 15-top-cell run or a noise-stable cap. The scalar top changes
77 raw words then one; sustained active-controller repair is separate work.

The next active-controller fixture is already verified: READ_B with rb=99 and
NAND, two copies flipped to 98 repair while three change the transition. Exact
physical initial fault sets contain 50/75 bottom bit flips (10/15 middle raw
word changes). Every affected physical cell matches direct depth-two damaged
initialization. Preparation only: no faulty depth-two GPU trajectory yet.
Next, apply these faults to actual initial Info, decode on GPU, execute paired
complete endpoints and the three-copy control, retain scratch and check rejoin.

Owned additions: endpoint_tiles.py/.cu, endpoint_image_array.py; streamed depth2
driver/audit and repair-fixture preparation; two test files; STREAMED_DEPTH_TWO.md,
this status and private build/data/evidence. Exact commands and limitations are
in the report; index retimed_holder_streamed_depth2_evidence_v1.json. Large bank
hashes were independently audited; no scratch recomputation of every bank word
or universal CUDA parity proof is claimed. All jobs are terminal. Probes used
under 64 MiB explicit GPU storage and under 8 GiB sampled host limits, within the
40 GB ceiling. Substantial GPU reservation remains unused; no shared changes
requested. Please reply in MAIN_AGENT_NOTES.md, still absent. Previous handoff:
STATUS_BEFORE_STREAMED_DEPTH_TWO_20260927.md.

## Preserved milestone: complete-state GPU endpoint operator

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

The exact 50/75-bit depth-two encoded-controller experiment is now executed and
audited, including the negative control and complete rejoin. Its faults preserve
a nested canonical entry domain; it does not cover general in-period errors.
Next use the actual running middle evaluator as a checkpoint, evolve local faults
with the complete physical rule, and verify correction/rejoin before applying
an endpoint shortcut. The existing literal exception engines and complete-rule
replica certificate can support this, subject to their recorded domains.

Practical complete noiseless depth-two endpoints now run for one periodic top
cell. Broader top rings, depth-three execution, arbitrary intermediate times and
general noisy-depth execution still need work. The physical rule/ROM/alphabet
remain fixed. Coordinate substantial GPU scheduling; the separate 8 GiB
reservation is unused. The user permits up to 40 GB host RAM; latest peak was
about 5 GiB during full paired-bank comparison.

General full-alphabet stochastic correction/amplification, malformed Info repair,
robust finite caps and source-fidelity qualifications remain open. Candidate-B
Flag2, voted-old-Signal D10, printed Flag2 persistence/SimBit ambiguity and cap
Address-defect persistence are unchanged. Endpoint identities and targeted initial
errors do not establish the papers' complete noise hypotheses. Finite periodic
tops evolve by the same G; no robust quiescent top kernel is claimed.

Historical handoffs and successful evidence remain archived. Please use
MAIN_AGENT_NOTES.md for replies; this agent never edits that file.
