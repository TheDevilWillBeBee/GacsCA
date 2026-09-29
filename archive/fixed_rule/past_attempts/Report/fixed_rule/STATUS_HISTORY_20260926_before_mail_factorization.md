# Fixed-rule agent status

Updated 2026-09-26. **Full fixed-rule Gács/Gray goal active; not complete.**
Please reply in **Report/fixed_rule/MAIN_AGENT_NOTES.md**; this agent never edits
that file. None was present at the latest check. No shared change is requested.

## Current acceptance priorities

User refinement of the active goal: (1) correct actual fixed-rule self-simulation,
(2) practical two-level execution on the A100, with measured colony size and work
period costs, and (3) demonstrated error correction across levels. Optimize Q and
U subject to correctness; U <= 128 Q is not an acceptance constraint. Keep shared
host-memory use bounded and coordinate substantial GPU allocations. These refine
the existing active goal; none of the three final outcomes is claimed complete.

## Latest milestone: full-raw packet events and actual SEND continuation

Previous goal turn was verified dispatch progress. New local certificates passed
938 cases (134 families x seven regular clock intervals), covering MEM and all
non-MEM kinds, both tracks, edge hop/drop behavior, delivery/WRITE priority,
old-Data reads/SEND and selected head interactions. Complete raw state is checked.
Native/scalar audits passed 25,326 complete outputs. Ten focused tests passed,
including mutations of priority, edge decrement and the non-MEM hypothesis.

Actual GPU execution passed 384 uninterrupted SEND-to-next-FETCH trajectories:
32 actual sites, all16 direction/hop tags, six patterns and two Ages. It retained
real packets and checked 19,536 complete logical/raw probes. At final checkpoints
24 packets had delivered and360 remained live. Total8.271291 s; GPU advance
0.375047 s; host182,668 KiB; process GPU422 MiB; explicit allocation3,726,576 B.
Independent checkpoint audit passed9.754163 s /71,376 KiB, including1598 full
scalar/native boundary outputs and all saved records/raw digest.

Two failed attempts are preserved: symbolic decrement normalization, and a GPU
batch guard rejecting live packets outside its protected-target domain. The final
driver uses the existing device-guarded transport/literal API after packet birth;
no rule, ROM, kernel or guard changed. No large GPU job or CUDA rebuild occurred.
The earlier mail-free expanded dispatch attempt remains separately unverified.

Exact commands, costs, assumptions, failed attempts, ownership and hashes:
[PACKET_EVENT_REFINEMENT.md](PACKET_EVENT_REFINEMENT.md). Owned additions: two
packet certificates, two native audits, SEND driver/audit, three tests and report/
evidence. All own runs terminal, MAIN_AGENT_NOTES.md absent; please reply there.
No shared change requested; separate8GiB scheduling request still pending/unused.

Next: join full-raw transport to ballistic packet paths and occupancy/collision
invariants; establish controller/mail noninterference for arbitrary used relative
positions, then flag and clock/Signal/reset/rest joins into a whole-period
relation. Full upper two-level periods, reliable finite termination and general
cross-level noise suppression remain open. Original goal and priorities active.

## Previous milestone: conditional FETCH dispatch and audited physical pilot

The checker covers 20,802 actual-ROM routes: 20,796 live successors, five reset
entries and one vote entry. Complete controller/Data are preserved until matching
FETCH, with exact travel counts. Seven new full-raw MEM/FETCH leaves allow matching
indices in memory. Catalog passed 11.942461 s / 78,848 KiB; six tests passed 1.906 s.
All contracts assume mail-free input. The 6478 direct SEND successors are tagged
conditional; absence of that tag does not establish absence of earlier mail.

Physical pilot passed 60 dispatches: six initialized entry tasks and four
uninterrupted predecessor-to-next-FETCH tasks, each with six patterns. It checked
942 complete logical/raw probes; total 1.847032 s, GPU advance 0.036166 s, host
215,612 KiB, process GPU 422 MiB, explicit allocation 3,726,576 B. Independent CPU
audit passed 1.398509 s / 70,664 KiB: all routes, 189 matching-index scalar/native
full outputs, 40 next-FETCH boundary outputs, all saved records and raw digest.

The expanded GPU launch is not verified: automatic approval timed out before its
first process was created; one retry has no recoverable completion result.
Read-only recheck found no expanded artifacts or active dispatch process. No
further launch was made. CPU audit completed normally. No shared source or frozen
rule/ROM/kernel changed. The separate 8 GiB request remains pending/unused.

Exact commands, ownership, provenance and limitations:
[DISPATCH_PATH_REFINEMENT.md](DISPATCH_PATH_REFINEMENT.md). Owned additions are the
dispatch certificate/test/physical driver/audit, report and evidence. Please reply
in MAIN_AGENT_NOTES.md; that file remains absent. Next: packet transport,
delivery/collision/flag guards, then clock/Signal/reset/rest composition. Full
upper two-level periods and general cross-level noise suppression remain open.
The full goal remains active with the acceptance priorities above.

## Previous milestone: all ordinary fixed-ROM instruction paths

Previous goal turn was verified progress (META path composition). The new checker
covers20703 non-META sites and both IF_THIRD branches:20704 conditional full-
controller/Data/packet contracts with physical scan durations1..163318 ticks.
Memory is shared by Address, retaining alias semantics. Ten new non-MEM flight/
reflection families across seven regular clock intervals (70 full-raw cases)
allow harmless matching indices outside memory. Full catalog passed59.562966 s
/76616 KiB. It starts at matching FETCH and SEND ends at packet birth.

Six tests passed2.506 s, including aliasing, all16 SEND tags and mutations losing
packets, stale ALU or timing. Physical pilot120 completions passed. The selected
65-site run passed780 instructions (six data patterns, two clock phases), with
22686 saved complete logical records and selected full raw probes. GPU advance
0.724007 s; total10.077379 s; host186720 KiB; GPU422 MiB; explicit3726576 B.
Independent audit passed16.258178 s /79416 KiB: all20704 catalog paths,1890 new-leaf
and1456 event-boundary scalar/native outputs, all saved records and probe digest.
No packet continuation, full-period or nested/noisy claim follows from these runs.

Exact commands, evidence, source scope and hashes are in
[INSTRUCTION_PATH_REFINEMENT.md](INSTRUCTION_PATH_REFINEMENT.md). Owned additions:
ordinary certificate/test, physical driver/audit, report/evidence. Prior clock/
META and new manifest sources all match. No physical rule/ROM/kernel or shared
file changed. All own handles terminal; notes absent and separate8GiB request
pending/unused. Please reply in MAIN_AGENT_NOTES.md.

Next: close travel to the next matching FETCH (including MEM sites with matching
indices), then incoming transport, delivery/collision/flag guards, and clock/
Signal/reset composition into a whole-period relation. SEND's emitted mail
prevents blindly composing mail-free instruction contracts. Full upper depth-two
periods and general cross-level noise suppression remain open; full goal active.

## Latest milestone: complete conditional META paths and physical checkpoints

Previous goal turn was verified progress (regular-clock/FETCH refinement). The new
composition instantiates full-controller leaf templates, checks actual ROM and
loop hypotheses, and proves one Data write plus D=4L+d-m+1 for all98 actual META
sites and every valid query Address:392 symbolic paths,3.115732 s /62376 KiB.
Composition exposed the missing last=1 first-leftward-step case; seven additional
full-raw leaf proofs close it. A backward descriptor support check finds738 used
raw input words and logical procedure offsets-3..4, justifying the quiet exterior
outside the checked nine holders under the same coherent/canonical hypotheses.

Eight tests passed (paths6 /3.129 s; support2 /0.061 s). Actual GPU execution passed
3822 META instances:98 sites x13 queries x3 initial clock phases, six reflection/
write checkpoints each,22932 saved full head records and114660 selected complete
raw probes. GPU advance1.418373 s; total94.407349 s; host259980 KiB; GPU424 MiB;
explicit allocation4807768 B. Independent audit passed37.782466 s /73792 KiB:
229376 lookup values,189 new-leaf and3528 reflection/write scalar/native outputs,
all saved heads and expected raw-probe digest. This is not a full-colony scan at
each checkpoint, a whole period, arbitrary noise or a nested trajectory.

Early/late pilots and audits passed. The first expanded driver stopped after26
completions when its existing prefix initializer rejected late Age; its terminal
failed record/log are preserved. A separate driver uses the existing validated
from_stored initializer for late initial data. No kernel/guard changed. A v1
composition class-name collision and source snapshot are also preserved.

See [META_PATH_REFINEMENT.md](META_PATH_REFINEMENT.md) for exact commands, proof
domain, derivation, counts, failures and hashes. Owned additions: path/support
certificates/tests, physical drivers/audit, report/evidence. Prior clock and new
manifest sources match. All own handles terminal; no shared change requested;
notes absent; separate8GiB reservation remains pending. Reply in MAIN_AGENT_NOTES.md.

Next: derive ordinary-instruction durations via the physical 2L scan cycle, then
incoming transport, Signal/flag and clock-override composition into a whole-period
relation. Full upper depth-two work periods and general cross-level noise
suppression remain missing. Goal active and full scope/user priorities unchanged.

## Latest milestone: regular-clock and arbitrary-operand FETCH refinement

Previous goal turn was verified progress (position/scanner identities). The new
interval checker covers116 event families across seven regular active intervals:
812 full-descriptor cases, 1125432 raw output words, quantifying3154116601 old
Ages. It adds FETCH for every used ROM kind plus LOOP, ordinary/right-end sites,
arbitrary instruction operands/index and both IF_THIRD clock branches. Domain is
still canonical coherent, zero flags/Signal/Wf, one head/quiet and no incoming
mail. Reset/vote/capture/commit transitions and rest intervals need separate proofs.

An initial pilot exposed a real boundary distinction: capture uses UPDATED Age,
so the excluded old Age must be CAPTURE_AGE-1. The failed source/log are preserved;
a concrete scalar/native test verifies Address3/Data1 changes Signal0 to4 there.
Corrected full certificate passed172.547991 s /187972 KiB host. Six tests passed
10.814 s. Independent audit checked21924 full scalar/native outputs at both ends
and a random Age in every interval/event family, with all hypotheses validated:
passed75.710566 s /59868 KiB. No GPU run or physical rule/ROM/kernel change.

See [CLOCK_EVENT_REFINEMENT.md](CLOCK_EVENT_REFINEMENT.md) for exact commands,
intervals, source scope, hashes and remaining obligations. Owned additions:
clock certificate, test/audit, report/evidence. Previous position/scan and current
audit source hashes all match. All own handles terminal; no shared change needed;
notes absent and separate8GiB reservation pending. Please reply in MAIN_AGENT_NOTES.md.

Next: compose local events into actual META and ordinary-instruction scan paths
and exact durations, retaining clock-domain hypotheses; then incoming transport,
Signal/flag and override composition into a whole-period relation. The actual ROM
has98 META instructions; existing all-query physical timing covered seven chosen
ones. Full upper depth-two periods and general cross-level noise suppression are
still missing. The complete goal remains active; user priorities above unchanged.

## Latest milestone: position-independent events and conditional scanner identities

Previous goal turn was verified progress (local events and exact META timing).
New symbolic canonical geometry covers all 32768 base Addresses and coherent
arbitrary surrounding metadata/Data. Position certificate: 49 cases, all 154 raw
outputs at nine holders per case (67914 words), 8.143864 s, 59456 KiB host.
The separate scan certificate replaces particular nonmatching operands with
explicit word-disequality hypotheses and adds endpoint reflections/fallback:
43 cases, 59598 words, 8.324450 s, 58420 KiB. Both still use one active Age,
zero flags/Signal/Wf and no incoming mail. No complete scan/period theorem.

Nine tests passed (position4 /8.614 s; scan5 /9.217 s). Dropped hypotheses,
controller/geometry/packet mutations and incomplete output schema are rejected.
A concrete matching WRITE disproves unqualified flight. Independent audits check
2646 +2322 complete scalar/native outputs, with wrap, overflow and fallback
boundaries; passed9.343873 s /58116 KiB and8.177528 s /58472 KiB. The failed v1
fallback-expression normalization and exact source snapshot are preserved; v2
changes only the diagnostic expression. No physical rule, ROM or kernel changed.

Exact commands, source scope, results and hashes are in
[POSITION_EVENT_REFINEMENT.md](POSITION_EVENT_REFINEMENT.md). Owned additions:
position/scan certificate, audit and test files; report and evidence. Previous
local-event and new audit source hashes all match. All own handles terminal;
no GPU run; no shared change requested; notes absent and separate8GiB scheduling
request still pending. Please reply in MAIN_AGENT_NOTES.md only.

Next: extend to active clock intervals and arbitrary FETCH sites; compose exact
scan durations and incoming transport, then join ROM data flow, Signal/flags and
reset into a whole-period relation. Full upper depth-two periods and general
cross-level noise suppression remain open. User priorities above still apply;
U<=128Q is not required; final goal active and incomplete.

## Latest milestone: physical local events and exact META write timing

Previous goal turn was verified progress (conditional ROM data-flow certificate).
New full-descriptor word identities cover 67 stated local event cases with
arbitrary operands, stale controller fields and surrounding MEM Data. All 154 raw
outputs checked at nine holders each: 92862 output words, 8.344888 s, 57400 KiB.
Four mutation/rewrite tests passed in 8.667 s. Domain remains coherent canonical,
zero flags/Signal, no incoming mail, at the stated actual ROM positions/Ages.
This is not yet an all-position/clock or complete-period refinement theorem.

Actual GPU META timing: all 32768 valid query Addresses and seven selectors at
seven real output-regeneration instructions (229376 completions). Full records
immediately before/after the write and at the old instruction site match; exact
D=4L+d-m+1=101557 ticks for these pairs, including zero results and fallback.
GPU advance 7.749542 s; total102.630788 s; host172408 KiB; GPU442 MiB. Pilot91
completions also preserved. Independent audit checked1809 full scalar/native
physical outputs and all229376 saved META values/durations; passed7.299437 s,
62672 KiB. See [LOCAL_EVENT_REFINEMENT.md](LOCAL_EVENT_REFINEMENT.md) for commands,
proof domain, hashes, timing derivation and remaining obligations.

Owned additions: certify_small_holder_local_events, test, META timing driver,
local-event audit, report/evidence. No frozen/shared source or kernel changed.
All handles terminal; notes absent; separate8GiB reservation remains pending.
Next: generalize event identities over actual positions/clock intervals, prove
ordinary flight/right reflection and total scan timing, and compose with incoming
mail under real guards before joining data-flow and reset into a period theorem.
Full nested execution and general cross-level robustness remain open; goal active.

## Latest milestone: actual ROM symbolic data-flow certificate

Previous goal turn was verified progress (complete reset encoding/handoff).
New diagnostic checker reads the actual ROM operands, entries and reset markers.
For 15 independent symbolic raw parent states (2310 input words), it checks all
three gathers, both full raw F evaluations, input/output self-metadata queries,
Signal payloads, commit and scratch clearing. All 154 outputs include the full
controller. Coverage: 517890 instruction instances, 2205 META queries, 97170
packets, 96806 symbolic terms; 3.311505 s, 91864 KiB host. This is an all-input
DATA-FLOW identity conditional on the completed-instruction/timing abstraction,
not physical execution or a whole-period theorem.

Five tests passed in 7.092 s, including rejected missing-PC, wrong-self-query,
gather-route and Info-reset mutations. Independent term-semantics audit matched
240 complete outputs on 16 randomized full-controller rings against scalar/native
G; passed 4.374619 s, 92364 KiB. No new GPU run, runtime interpreter or physical
kernel. See [ROM_DATAFLOW.md](ROM_DATAFLOW.md) for commands, deadlines, source
scope, hashes and explicit premises. Owned additions are certify_small_holder_rom_dataflow,
its test/audit, report/evidence. No frozen/shared source changed. All handles
terminal; notes absent; separate 8 GiB reservation still pending.

Next concrete work: refine actual physical FETCH/read/write/send/LOAD/META and
reflection events to these semantics for arbitrary operands, especially META
scan timing and fallback; then compose with transport, Signals/flags and reset.
The 15-colony symbolic network is not a proof for arbitrary physical ring sizes.
No nested shortcut is authorized by these conditional results. Full nested
execution, terminal reliability and general cross-level robustness remain open;
goal active.

## Latest milestone: complete reset encoding and actual period handoff

Previous goal turn was verified progress (cap obstruction and physical failure
control). New C(x; L,R) encoding includes every raw parent word, actual reset
head/controller, physical geometry and retained fivefold Signals. It is used
only for initialization/diagnostics, never to replace evolving state. Complete
raw local reset identity proved over 1983 bits: all Addresses, nine Data words,
all seven complete static records, six neighbor Signals, all 154 outputs.
Proof v2: 128995 BDD nodes, 1.158850 s, 115820 KiB. Narrower v1 metadata proof
and exact source snapshot preserved. Four tests passed in 1.744 s.

Two continuous GPU reset-to-reset cycles from alternating old Signals and an
active upper WRITE/Address fault match every physical coherent row at all five
checkpoints (491520 rows each). At both commits all decoded words match G;
Address 30000 repairs to107; Data clears then restores 0x123456789ABCDEF0.
GPU 40.158518 s; complete-row verification 33.928519 s; total75.883395 s;
host174996 KiB; GPU424 MiB. Independent audit re-proved reset, enumerated all
32768 ROM/fallback markers, rebuilt three complete clean hashes, checked30
full decoded outputs and210 raw probes: passed2.184582 s,115872 KiB.

See [RESET_ENCODING.md](RESET_ENCODING.md) for exact commands, hashes, domain and
remaining obligations. Owned: small_holder_reset_encoding, its proof/test, reset
handoff driver/audit and evidence/report. No frozen/shared source changed.
All handles terminal; notes absent; separate8GiB reservation still pending.
The reset theorem plus finite trajectories is NOT an all-input whole-period
simulation theorem or permission for an upper-rule callback. Next concrete work:
certify fixed-ROM retrieval/instruction/communication trace and timing for
arbitrary encoded inputs, then consider fault-aware nested composition. Full
nested execution and general cross-level robustness remain unfinished; goal active.

## Latest milestone: exact cap geometry obstruction and encoded failure control

Previous goal turn was verified progress (3.92x physical event compilation).
This turn proves that one arbitrary Address defect in the ordinary homogeneous
cap persists forever: all 2^32 Ages, all 32768 replacement Addresses, arbitrary
primary Wf and unrestricted remaining controller/Data/Signal fields. Twelve
complete-descriptor geometry cases quantify 69 bits each; max 2698 BDD nodes,
0.503721 s, 36936 KiB host. Four mutation/native/scalar tests passed in 1.155 s.
The cap remains valid noiseless termination data, but is not an eroder of finite
Address defects. Enlarging U or waiting longer cannot fix this invariant.

Actual lower execution distinguishes two physical Info-copy bit faults (repair
in one tick; correct full commit) from three (wrong encoded Address 32766 versus
32767 survives two successive periods). Strict decode initially rejects stale
metadata; the physical ROM regenerates it. Every one of the 154 committed raw
fields matches the intended G, including the unfavorable cap behavior. Three
periods total across the two cases: GPU 55.569326 s, total 58.649576 s, host
180440 KiB, sampled GPU 442–444 MiB. Initial pre-execution syntax failure is
preserved as v1 log; successful evidence is v2. Independent audit re-proved the
invariant and checked 30 full local plus 45 full decoded outputs in 1.519051 s.

See [CAP_DEFECT.md](CAP_DEFECT.md) for exact commands, source scope, hashes and
three distinct boundary alternatives. Owned additions: prove_small_holder_cap_defect,
its test, small_holder_encoded_cap_defect and audit modules, report/evidence.
No frozen/shared source or kernel changed. All handles terminal; notes absent;
8 GiB allocation reservation still pending. Full goal active. Next work must
address a justified terminal reliability relation and full nested-period cost;
noiseless cap consistency must not be conflated with cap error correction.

## Latest milestone: exact physical event compiler, 3.92x faster

Previous goal turn was no progress (status confirmation only); this continuation
implemented and verified an execution improvement. New scalar expression output
slicing retains all18 consumed controller/Data/mail fields (1564of1785 operations).
A second backend gathers the exact70 referenced input words instead of352.
Physical rule/ROM/depth relation, event timings, guards and fallback are unchanged.
Both complete periods match all154 decoded fields, every core/tail/gap row and
all event/accounting metrics of the frozen baseline.

GPU advance: old37.209585s, scalar22.000456s, supported-input9.483492s (3.923616x).
Supported whole run24.337732s, host564068KiB, GPU424MiB. Three scalar tests passed
in16.789s; four supported tests passed in16.800s. Initial source-guard/alias test
failures are preserved in the v1 log, corrected in v2. Independent structural-DAG
and emitted-C audit passed2048 comparisons in1.473235s,64452KiB. No host upper
transition during evolution. See [EVENT_COMPILATION.md](EVENT_COMPILATION.md) for
exact commands, compiler spill costs, hashes and full scope of comparisons.

Owned: small_holder_register_events.py, small_holder_supported_events.py, their
new tests, register/support period drivers, event-emission audit and private build/
evidence files. Frozen/shared sources and general flag/fault backends unchanged.
All own handles terminal. MAIN_AGENT_NOTES absent;8GiB reservation still pending.
U remains2^32; this constant-factor gain does not make a full nested upper period
practical. Next concrete work must address certified nested trajectory composition
or construction-level cost reduction, retaining full physical controller state;
full nested execution, finite-depth termination and general amplification remain
unfinished. Full goal active.

## Latest milestone: first sparse random-noise whole-period pilot

Previous goal turn was verified progress (combined temporal faults and recovery).
New small_holder_noise.py samples independent uniform whole-cell replacement noise
by Binomial count plus O(count) uniform subset selection, then every projected
field. Noise follows each local transition; no draw is resampled or truncated.
Three sampler tests passed in 0.026 s, including an exhaustive small subset law.

Two predetermined seeds, 2026092601/2026092602, ran two full work periods each at
p=2^-44 (5.684341886080802e-14) per cell update, with N=4222124650659840 updates
per trial. They produced 221/240 replacements, no decoded differences at all four
commits, and complete physical equality to separately evolved healthy worlds at
2U+8 after eight explicitly noise-free settling ticks. Each fault cleared in one
literal tick; zero Data/flag rebases. GPU advance including comparison took
71.445665/71.001874 s; totals 86.891991/87.625573 s; host 375208/376116 KiB;
sampled GPU 448 MiB. Both complete noise archives and injection logs are retained.

Independent audits reproduced all 461 events and checked 240 complete physical
local outputs plus all decoded fields; passed in 1.673382/1.652116 s. Important
limit: minimum event gaps were 29225/375648 ticks, with NO forcing/clearing events.
This is very-low-rate isolated-fault evidence, not interacting-island statistics,
a threshold or cross-level amplification. Four commits are not four independent
noise histories. See [SPARSE_NOISE.md](SPARSE_NOISE.md) for source definition,
exact commands, provenance, failure policy and resource measurements.

Owned additions: sampler, test_small_holder_noise.py, small_holder_sparse_noise.py,
audit_small_holder_sparse_noise.py, that report and namespaced evidence. No frozen
or shared source/rule change. All handles terminal; final GPU query empty. Main
agent reservation reply remains absent; no large allocation. Full goal active.
Next priorities: actual nested trajectory cost/second-link execution and stronger
interacting-fault evidence; more isolated low-rate seeds alone will not close them.

## Latest milestone: full physical faults with general flags

Previous goal turn was verified progress (general-Signal flags and two periods).
New small_holder_general_faults.py combines complete projected physical exceptions
with the actual GPU flag reference, including every backup Wf. Binding validates
colony count/clock and safely crosses flag allocation/clearing. Exact Data and flag
rebases preserve actual state; Flag1 rebase requires all derived Wf2 copies to
agree, packed updates are atomic, and late flag rebases are refused. Empty
exceptions means coherence with the current reference, not healthy recovery.

Seven tests passed in 18.115 s including private build (host 181048 KiB). They cover
complete random physical cones across the flag lifecycle, geometry/controller
repair, wrong Data retention, Wf/clock/type guards, packed updates, and a delayed
front whose accelerated 256-tick state equals literal exception evolution while
still differing from healthy. Extra device buffers remain 18579456 bytes.

A full-period combined temporal-fault experiment passed: six early physical Info
bit flips corrupt two upper value replicas; the encoded rule repairs them. Later,
two adjacent complete projected-site replacements recover after one local tick,
while a deleted Flag1 front bit persists as a one-site delay after 256 ticks.
Exact flag rebase retains that damage. At U all 154 decoded fields match; at U+1
every physical core/tail/gap row rejoins a separately evolved healthy world.
Both computed Signals are one. GPU advance including comparison 34.354987 s,
total 49.222678 s, host 577768 KiB. Independent fault-map/full-rule/31-site physical
causal-cone audit passed in 1.036061 s, host 62200 KiB.

Targeted ONE-LINK recovery only; no random-noise threshold or full nested work
period. No fixed rule, ROM, alphabet, neighborhood or frozen/shared source changed.
Exact scope, commands, ownership and evidence:
[GENERAL_PHYSICAL_FAULTS.md](GENERAL_PHYSICAL_FAULTS.md).
All handles exited zero; final GPU query empty. Main-agent reservation reply remains
absent; no large allocation. Next: reproducible sparse random physical space-time
faults over whole periods, with measured rates/counts and failure retention, while
resolving nested trajectory cost and robust termination. Full goal remains active.

## Latest milestone: arbitrary coherent Signals and exact Flag2 transients

Previous goal turn was verified progress (Address-repair closure/domain audit).
New small_holder_flags_gpu.{py,cu} executes every canonical flag tick in packed
GPU bit fields, with coherent arbitrary neighboring left/right Signals. No wave
shape is assumed. A four-regime BDD certificate matches selected complete physical
descriptor outputs for all 51 independent Address/flag/Signal bits; largest BDD
63030 nodes, 1.836706 s. Four local/graph/factorization tests passed in 1.820 s.

New small_holder_resident_general.py combines exact flags with the unchanged
mail-free controller. Canonical geometry disables address-change clearing; zero
old/new mail makes flag mail-erasure irrelevant. Only the obsolete accelerator
Signal guard is widened in private generated sources. Full physical local tests
and old right-only regression passed: two tests, 6.556 s including private build.
The old physical-exception backend rejects this incompatible representation.

All 16 two-colony Signal patterns completed 98305 physical forcing/clearing ticks,
plus a random-flag clearing case. GPU 2.774712 s, total 3.569017 s, host 146568 KiB,
explicit flag buffers 49158 bytes. Cross-colony Flag2 dependence is demonstrated.
Two full successive one-link periods with BOTH computed Signals one also passed:
all 154 pre/post-regeneration/decoded fields match. All 491520 physical sites have
both flags one at cutoff, then clear by actual local evolution. Upper Address
30000 repairs to 107 and controller Data restores on period two. GPU 37.980548 s
including 0.367051 s flags; total 39.505978 s; host 176352 KiB. Independent complete
transition/profile/provenance audit passed in 0.856253 s, host 64444 KiB.

No physical rule, ROM, alphabet, neighborhood or frozen/shared source changed.
The left-zero limitation is removed only on the stated canonical/coherent/mail-free
suffix domain. Faulty geometry, general-flags plus physical exceptions, complete
nested work periods, robust termination and stochastic amplification remain open.
Exact commands, owned files, proof scope and evidence: [GENERAL_FLAGS.md](GENERAL_FLAGS.md).
All handles exited zero; final GPU query empty. Main-agent reply remains absent;
the 8 GiB whole-Q pilot is still pending, no large run. Full goal remains active.

## Latest milestone: explicit projected closure through Address repair

Previous goal turn was verified progress (individual physical faults and exact
Data rebase). This turn inspected the fixed ROM: input/output metadata regeneration
already exists. The earlier clean fixture changes three ring-boundary Addresses;
its regeneration was not missing. New evidence explicitly distinguishes raw F
output from locally regenerated iota(G(x)). No rule/ROM/backend change.

Two full successive physical periods with upper holder 7 Address=30000 repair it
to107. Before/after regeneration checkpoints match every raw word; 77 metadata
words change in period1,42 in period2. Center primary Data clears under geometry
repair, then restores 0x123456789ABCDEF0 from surviving replicas in period2.
GPU36.445883s,total37.987277s,host176324KiB. The same evolving physical world is
used throughout; no host simulated transition/refill. All checkpoints passed.

Actual local regeneration then passed for ALL32768 encoded Addresses, seven
wrapped offsets/all seven selectors, including gap/tail fallback. 256 batches
of128 colonies check1605632 metadata words and5046272 complete Hold words.
GPU20.187524s,total111.298448s,host197200KiB,explicitdevice32735456B,
sampledGPU442MiB. A nine-boundary-address pilot also passed. Independent audit of
both artifacts passed0.919370s,80632KiB, including scalar/native/descriptor full
transitions and an independent total-ROM table. Missing regeneration has an
observed failing counterexample (raw F output != lifted projected output).

This is exhaustive CLEAN SUBROUTINE coverage plus two ONE-LINK macrosteps,
not full nested dynamics or a general noise theorem. The conditional self-reference
argument and remaining domains are in [SMALL_HOLDER_CLOSURE.md](SMALL_HOLDER_CLOSURE.md).
New owned drivers: small_holder_geometry_closure.py,
small_holder_regeneration_domain.py,audit_small_holder_geometry_closure.py,
matching namespaced evidence and that report. No frozen/shared sources changed.
All handles exited zero. The 8GiB whole-Q reset pilot reservation is still pending;
no large allocation. Next priorities: broader flag/Signal suffix domain and
physical evaluator/nested-trajectory cost, alongside the noisy boundary relation.
Full goal active; Q/U remain optimization targets without a128 ratio constraint.

## Latest milestone: individual projected faults and exact Data rebase

New small_holder_resident_faults.{py,cu} retains full physical exceptions on GPU
above the nonperiodic resident state and executes the fixed radius-seven projected
G=project(F(lift(.))). All 105 mutable controller/geometry/flag fields are covered;
49 metadata words are derived from each holder's own Address. Full-state equality
prunes deviations; an exact coherent-Data rebase preserves wrong Data and residual
exceptions. Empty exceptions means coherent representation, not healthy state.
Extra device storage 18,579,456 bytes; frontier cap 8192, atomic overflow rejection.

Six independent causal-cone/rebase/repair/guard tests passed (1.541 s; host
174560 KiB). Four unchanged raw-description/three-depth identity/controller/locality
tests passed (2.163 s; host 65824 KiB). Full-period GPU experiment: six initially
incoherent physical bit flips spread into two wrong upper controller replicas,
then the encoded rule repairs them. Nine flips in three upper replicas fail as
expected. Wrong words survive all three gathers and vote; all 154 decoded outputs
match the intended transition, and the positive case fully rejoins at U+1.
GPU advance 35.900505 s, total 51.693960 s, host 569976 KiB, sampled GPU 444 MiB.
Independent initial-fault/first-tick/scalar/native/descriptor/decoded audit passed
(1.304527 s; host 60484 KiB). No healthy state was installed into the damaged run.

ONE LINK/TWO SCALES and targeted initial faults only. Arbitrary upper-geometry
projection closure, robust termination, complete nested work period and stochastic
noise threshold remain unproved. Raw-F metadata fault fixtures are distinct from
this projected physical alphabet. Exact commands, source interpretation, proof
obligations and ownership: [RESIDENT_FAULTS.md](RESIDENT_FAULTS.md).
New files: backend pair, test_small_holder_resident_faults.py,
small_holder_incoherent_repair.py, audit_small_holder_incoherent_repair.py,
RESIDENT_FAULTS.md and namespaced evidence. No frozen/shared sources changed.

All handles exited zero; final GPU query empty. Main-agent notes/reservation reply
remain absent. The requested 8 GiB whole-Q allocation/reset pilot remains pending;
no large job was launched. Next: overlapping/time-separated faults, geometry
frontier/repair behavior, broader reference domains, and nested-period cost.
Full goal remains active; U/Q=128 is not an acceptance constraint.

## Latest milestone: exact communication and targeted simulated-layer repair

Previous goal turn was verified progress (nested streaming/guarded dynamics).
New small_holder_resident_gather.{py,cu} retains actual SEND payloads, birth times,
ballistic tracks, hop counts, drops and ordered delivery. Controller accesses to
foreign-history destinations, same-track collisions and capacity failures reject
atomically into the frozen synchronous path. Head events still use the same local
expression; physical rule/ROM/alphabet are unchanged. Five tests passed in
24.232 s. An eight-case BDD packet-induction proof passed in 0.254090 s, covering
all Addresses/coordinate targets/elapsed assignments and all hop counts.

Two full periods still match both complete frozen physical checkpoints, with
GPU advance reduced to 37.209585 s (8.636828x original synchronous; previous
independent version 133.103585 s). Total 52.386922 s; host RSS 563896 KiB; sampled
GPU 424 MiB. The 62-colony guarded nested fixture passed in 45.023646 s GPU /
46.912644 s total, versus prior 224.434556 s GPU. Its archive is identical to the
previous result; independent causal-cone/full-description audit passed. Host RSS
167592 KiB, GPU 432 MiB. Scaling through 257 colonies passed; no Q-sized allocation.

TARGETED REPAIR: ten physical one-bit faults (two five-holder Info clusters)
corrupt two simulated controller-value replicas. They survive the first lower
tick, all three gathers and temporal vote, but the encoded upper majority restores
all 154 decoded fields to the healthy result. At U+1 the entire physical state
rejoins the healthy checkpoint through the next local reset, with no reinitialization.
A fifteen-flip/three-replica control produces the wrong WRITE as expected. Both
cases passed in 36.404843 s GPU / 50.864089 s total, host RSS 567360 KiB. Independent
fault-map/scalar/native/descriptor audit passed in 0.812063 s.

This is correlated initial-fault repair through ONE LINK/TWO SCALES, not a random
noise threshold or full nested work period. General geometry/metadata repair,
full-raw fault integration and cross-level amplification remain open. Source
Flag2/D10 deviations remain explicit. Evidence, exact commands, domain obligations
and owned files: [GATHER_AND_REPAIR.md](GATHER_AND_REPAIR.md).

All handles exited zero; final device query empty. No shared source, existing
CUDA artifact, report or protected job changed. MAIN_AGENT_NOTES.md still absent;
the 8 GiB whole-Q allocation/reset pilot reservation request below is pending.
No large run was launched. Continue with whole-period cost/structure and broader
repair while coordinating full-ring execution. U squared remains 2^64 and the
full goal stays active. Historical third-link job absence is not completion.

## Latest milestone: real nested input, mixed Signals and guarded dynamics

Previous goal turn was verified progress (independent scheduling speedup).
New streaming initialization preserves all 154 raw words at every depth and uses
128-row chunks. All Q=32768 immediate parents of a genuine depth-two initializer
streamed/hashed in 0.752524 s with 57940 KiB host RSS; 512 rows match the scalar
initializer and all top fields decode exactly. No full bottom allocation yet.

The four-case full-descriptor BDD certificate now admits independent neighboring
right Signals (all eight assignments, every Address/front), with left Signals
zero. It passed in 1.260221 s. The new mixed resident backend changes only that
accelerator guard in private generated sources. Frozen physical rule, ROM,
alphabet and previous source files are unchanged. Five tests passed in 12.634 s,
including three-depth encoding, complete raw-controller preservation, invalid
stream rejection and mixed-wave/full-native/controller comparisons.

Two successive lower macrosteps completed on 62 guarded-window colonies sampled
from the actual depth-two initial data (2,031,616 physical cells). All 154 decoded
fields match the executed window's full rule. Separate true-upper-ring causal
cones match 34 interior cells after one step and six after two. Upper controller
reset/motion and an encoded top raw controller value are verified. Computed right
Signals are mixed (12/24 ones); capture/waves/commit/recurrence execute on GPU.
Independent scalar/native/descriptor/source audit passed in 1.403208 s.

GPU advance 224.434556 s; total 226.296005 s. Explicit peak buffers 17,299,904 bytes;
sampled GPU process 432 MiB; host RSS 166,240 KiB. All handles exited zero; device
query empty. These are GUARDED WINDOWS and TWO UPPER PHYSICAL TICKS, not the full
Q-squared bottom trajectory or an upper work period/top macrostep. The guards
establish decoded upper causal-cone matches, not physical equivalence to the
unexecuted full bottom ring. No stochastic correction claim.

Full evidence, exact commands, proof domain and ownership:
[NESTED_WINDOWS.md](NESTED_WINDOWS.md). Artifact stems under figs/fixed_rule:
small_holder_mixed_right_proof_v1, small_holder_stream_measure_v1,
small_holder_nested_windows_v1 and small_holder_nested_windows_audit_v1.

MAIN AGENT COORDINATION REQUEST: reserve up to 8 GiB GPU for the concrete whole
Q-colony allocation/reset pilot in NESTED_WINDOWS.md. Required explicit peak is
7,666,317,536 bytes, plus context. The driver is implemented and passed at depth
one (0.760723 s); depth-two has NOT been launched. It verifies every raw uploaded
word and every head after eight bottom ticks, not a macrostep. Please place the
scheduling decision in MAIN_AGENT_NOTES.md; that file is still absent.

While reservation is pending, communication scaling and the U-squared=2^64
horizon remain independent work. Whole nested macrosteps, finite-depth boundary
verification, full-raw fault integration and cross-level correction remain open.
The full goal stays active. No shared patch requested or shared source/job
changed; protected historical job absence is not evidence of its completion.

## Latest milestone: independent local GPU events, exact full-period speedup

Previous goal turn was verified progress (two complete GPU periods and audit).
New small_holder_resident_independent.{py,cu} gives colonies independent event
times between common physical barriers. Literal operations call the SAME local
expression. Guarded head flight/WAIT skips preserve locality; all evolving Data
and controllers stage until every colony accepts. Mail emission/domain or event
budget rejection is atomic. Full advance falls back to the frozen synchronous
backend for communication and barriers. No rule/ROM/alphabet changed.

Seven tests passed in 32.733 s, covering actual ROM operations, complete-state
comparisons, raw-native events, suffix Flag1 plus active WRITE, stable Signals,
atomic rollback, communication fallback, resets/inactivity and clock wrap.
Distinct-query scaling passed at 1,8,32,128,257 colonies. At 128 distinct queries,
independent execution took 0.580 ms versus synchronous 161.050 ms; at 257 it took
0.709 ms versus 615.365 ms. These are single warm fixture timings, not nested
runtime predictions. The 257 case exercises reuse of the 256 worker workspaces.

Two successive full periods on one resident GPU state passed again, with both
complete decoded/raw and 491,520-site physical checkpoints identical to the
frozen audited evidence. GPU advance fell from 321.372800 s to 133.103585 s
(2.414456x). Total with full-state comparisons: 148.720661 s. Explicit peak buffers
6,307,920 bytes; sampled GPU process 424–426 MiB; host RSS 560,020 KiB. 158 batches
accepted, 32 atomically rejected into synchronous fallback. Provenance/accounting
audit passed, including unchanged descriptor and ROM. Exact independent kernel:
220 registers, 48 stack bytes/thread. All handles exited zero; final GPU query empty.

Evidence/commands/domain proof/owned files: [INDEPENDENT_INTERVALS.md](INDEPENDENT_INTERVALS.md).
Artifacts: small_holder_independent_{scaling,two_periods}_v1 and
small_holder_independent_evidence_audit_v1.json under figs/fixed_rule.
No nested run or large allocation yet. The full fixed-rule goal stays active;
this is two periods at ONE LINK, not depth-two dynamics or noisy amplification.

Next: actual nested encoding with bounded streaming and measured communication
scaling; coordinate any Q-colony allocation with the main agent. Then integrate
nonuniform Signals and full-raw faults for cross-level correction. U squared
remains 2^64; independent computation alone does not establish a practical nested
macrostep. No shared change requested. Reply only in MAIN_AGENT_NOTES.md (absent).
The protected historical third-link job was not seen; absence is not completion.

## Latest milestone: two complete successive GPU work periods

User priorities remain (1) actual fixed-rule self-simulation, (2) practical
nested two-level GPU execution, (3) correction demonstrated across levels.
U/Q=128 is not a design constraint. The full goal is active and unfinished.

New small_holder_resident_period.{py,cu} composes the unchanged controller with
the certified physical Flag1 profile and the zero-Signal invariant. Data,
controllers and Signals persist through final commit/clock wrap in one GPU world.
Suffix guards require zero mail, coherent left-zero Signals and uniform right
Signal zero or one; unsupported patterns and newly emitted mail are rejected.
No physical rule/ROM/schema changed. This is a restricted coherent execution
backend; arbitrary faults and nonuniform suffix Signals remain unsupported.

Ten tests passed in 31.298 s. A 15-colony run completed two consecutive physical
periods: 8,589,934,592 ticks on 491,520 sites. Both complete physical checkpoints
match the independent CPU chain. All 154 decoded fields match the complete
self-description at both steps, with 45/41 raw procedure-field changes. Active
simulated WRITE, physical waves, recomputation, commit and restart are exercised.
A separate artifact/source audit passed, including every history/vote/Info/Hold,
carried Signals and full stored/gap hashes. These are TWO PERIODS AT ONE LINK,
not two nested hierarchy levels or a noisy amplification result.

GPU advance: 321.372800 s; whole experiment: 362.424160 s. Explicit GPU buffers:
5,116,680 bytes; observed total GPU process: 424 MiB. Host RSS: 841,980 KiB.
All twelve private CUDA kernels report zero stack/local bytes. Audit: 1.425622 s,
330,516 KiB host RSS. Commands, exact evidence, owned files and proof limitations:
[RESIDENT_PERIOD.md](RESIDENT_PERIOD.md). Authoritative artifact stem:
figs/fixed_rule/small_holder_resident_two_periods_v1; independent audit:
small_holder_resident_two_periods_audit_v1.json.

All run/audit handles exited zero; device query empty. The historical protected
third-link job was not seen, which does not prove its completion. No shared files,
old artifacts or shared CUDA builds changed. No shared patch requested; please
reply only in MAIN_AGENT_NOTES.md (still absent at latest check).

Next: independently timed local execution/exact batching for nonuniform colonies,
then real nested initialization and dynamics; integrate full-raw exceptions and
nonuniform maintenance before cross-level noise tests. Large GPU scheduling
remains with the main agent. The earlier prefix-only limits below are historical;
this milestone resolves full GPU periods for the stated restricted domain.

## Latest milestone: nonperiodic GPU self-description computation through capture

Previous turn was progress (synchronous periodic physical evolution). This turn
adds resident nonperiodic per-colony Data banks, complete sparse controllers/mail/
Signals, streamed raw parent encoding and certified physical event skipping.
Six tests pass (5.450 s), including distinct parents, active writes/mail, bulk
clock boundaries against full raw F, and atomic domain/capacity rejection.

GPU execution completed 1,979,711,488 physical ticks on 15 distinct encoded parent
states: all three gathers, protected vote, the complete self-description, computed
flags and Signal capture. All 154 Hold outputs agree with scalar/native/descriptor
oracles, including the simulated WRITE 0x123456789ABCDEF0. An independent source/
state audit passed; the entire 491,520-position coherent state agrees with the
frozen CPU physical executor. GPU advance took 73.703895 s; total run/audits
100.003527 s. Host RSS 462,056 KiB; explicit VRAM 5,116,680 bytes; observed total
GPU process memory 424 MiB. Exact binary kernels report zero stack bytes.
Full evidence, commands, source limits: [RESIDENT_PREFIX.md](RESIDENT_PREFIX.md).

This stops at capture: physical Wf/suffix, later recomputation/commit, successive
complete GPU macrosteps, incoherent faults and nested execution remain open.
No physical rule/ROM/alphabet changed. The backend requires canonical coherent
zero-flag prefix states; it rejects unsupported data instead of discarding it.

A first 20-million-tick validation matched all states but failed a premature
pending-mail assertion (first SEND is at 30,671,802). Its terminal failure evidence
is preserved. The corrected 30,814,700-tick run passed all complete-state checks
and observed distinct cross-colony payloads 99, 172 and 26.

Next scaling issue is measured: 128 shared metadata queries need one literal
tick, while 128 distinct query addresses need 128, for the same 136-tick physical
interval. Estimated explicit storage for Q lower colonies is 5,064,014,048 bytes,
but no such allocation was launched. Independent local event scheduling or exact
batching needs work before a large nested run; memory capacity alone is insufficient.
Stationary-Signal skipping and full physical suffix/fault integration also remain.

All runs terminal; GPU query empty afterward. No shared changes/rebuild or
substantial new allocation. Main agent retains GPU scheduling; reply only in
MAIN_AGENT_NOTES.md. The full fixed-rule/cross-level-correction goal stays active.

## Latest milestone: exact synchronous GPU background + raw exceptions

Previous turn was progress (compact snapshots and shrinking physical windows).
New periodic GPU execution maintains a whole represented ring across synchronous
commits. The same full raw F advances its periodic background and every site in
the radius-seven expansion of its physical deviations. Only equality of all 154
raw fields removes exceptions. All state rows persist on GPU between ticks.

Six bounded-backend tests pass: four core tests (21.061 s including private build)
and two frontier regressions (1.358 s). Arbitrary full raw rings agree with dense
native evolution; an organized Q-cell colony agrees with the frozen CPU prefix.
Tests require persistent metadata differences, newly reached head positions,
multiple worker rounds, active writes, two-holder repair and atomic capacity
failure. The original backend passed the same four core cases in 182.524 s.

An eight-tick physical experiment passed 136 full-raw probe comparisons, an active
WRITE and two separated pairs of procedure-holder faults. The represented Q²-site
ring repeats one Q-cell background; this is NOT a depth-two initialized hierarchy
or macrostep. The bounded run took 3.165902 s, host RSS 262,728 KiB, explicit GPU
buffers/workspace 47,876,096 bytes, observed total GPU process memory 466 MiB.
Details, exact commands and proof relation: [PERIODIC_EXECUTION.md](PERIODIC_EXECUTION.md).

Resource correction: the first correct-output backend concealed 146,832-byte
per-thread stacks behind its 40.4 MiB explicit buffers, reaching 31,216 MiB total
GPU process memory. That run finished and released the device; its sources and
measurements are preserved. The bounded revision uses verified temporary reuse
and 256 workers with explicit interleaved workspace; stacks are now 760/840 bytes.
Use measured total process VRAM, not explicit buffers alone, for future scheduling.

All runs terminal; device compute queries empty afterward. No shared changes or
shared CUDA rebuild. Main agent retains substantial GPU scheduling. Next work:
integrate genuinely nonperiodic encoded Data/controller state with exact sparse
physical evolution and event skipping; address evaluator cost and U² horizon.
Whole nested macrosteps, robust termination and cross-level correction remain
open. No shared patch requested; reply in MAIN_AGENT_NOTES.md.

## Latest milestone: fault-capable compact storage and full-rule CUDA

Previous turn completed the smaller-colony report/handoff (progress). This turn
adds executable compact storage, complete raw CUDA transitions and literal
multi-tick physical windows. New small_holder_bank.py and bank_cuda.{py,cu}
retain dense MEM Data plus sparse logical and arbitrary raw field overrides.
All 154 raw fields survive, including independent backups, geometry, controllers,
mail and metadata. The unchanged full descriptor drives GPU evaluation.

Eight new tests pass: four storage/full-rule tests (171.152 s including private
CUDA compilation), three successive-physical-tick/repair tests (1.019 s), and one
locality test (0.829 s). Four-tick GPU trajectories agree with literal native
updates during an active WRITE and boundary mail. Two damaged procedure holders
recover to the clean trajectory in the three-tick targeted experiment. Host
transition/evaluator replacement is prohibited during GPU advance.

Standalone validation passed in 1.022534 s, host RSS 164,420 KiB and peak explicit
VRAM 2,208,656 bytes plus context. A separate audit passed all 154 fields at 71
archived complete-macrostep witnesses (1.126509 s, RSS 225,352 KiB, explicit VRAM
4,741,520 bytes). All runs terminal; device process queries empty after tests.
Details, exact commands, evidence and owned files: [COMPACT_BANK.md](COMPACT_BANK.md).

These are bounded resident snapshots and shrinking physical windows, not a
whole-colony GPU commit executor or a depth-two macrostep. Raw program overrides
also cover states outside the hard-wired projected subspace; no recovery of
arbitrary program damage is claimed. Targeted two-holder procedure repair is
not stochastic/cross-level robustness. Next: synchronous compact GPU commits and
certified base-plus-physical-exception evolution, then efficient nested execution.
U²=2^64 still blocks naive tick-by-tick practicality. Explicit VRAM remains capped
at 64 MiB; no substantial allocation, shared changes or shared CUDA rebuild.
Main agent retains substantial GPU scheduling; reply in MAIN_AGENT_NOTES.md.

## Latest milestone: smaller colony and independent schedule validated

Current priorities: (1) correct actual fixed-rule self-simulation, (2) practical
two-level GPU execution, (3) error correction across levels. U/Q=128 is not a
constraint. The final goal remains active and is not achieved by this milestone.

New small_holder_* revision fixes Q=32,768, U=2^32 and T=2^25, independently
of depth. Its 30,724-cell core fits with 39,986,703 ticks of evaluation margin
and 72,924,599 ticks before capture. Three gathers have positive margins and
no same-track packet collision; forcing remains 2Q. Q is 32,768 times smaller
and U 32 times shorter than the previous fixture. Earlier revisions are frozen.

All 29 distinct tests pass (21 integration, two schedule, three cap, three CUDA).
Two successive complete one-link macrosteps and all nine execution/audit stages
pass: 2U physical ticks, exact state handoff, 40 raw controller changes each,
2,232 complete-native local witnesses per macrostep. Validation took 81.982341 s;
maximum child RSS 901,524 KiB. The ordinary cap has an all-2^32-Ages certificate.
Details, exact commands, source interpretation and owned files:
[SMALL_HOLDER.md](SMALL_HOLDER.md).

The private local CUDA tests passed 200 CPU/GPU and 40 full-physical comparisons.
The bounded resource call used 1,874,144 bytes explicit VRAM plus context and
167,928 KiB host RSS. All runs are terminal; device process queries were empty
before and after. No shared CUDA rebuild or substantial GPU allocation occurred.
Main agent retains substantial GPU scheduling; reply in MAIN_AGENT_NOTES.md.

Next: implement and certify a compact resident representation retaining actual
controller/mail state, then genuine depth-two dynamics and physical faults.
Dense depth-two buffers still need 738.7 GB per top cell. A hypothetical Data
bank alone needs 2.6 GB per top cell, excluding controller/mail/faults; it is not
an implemented executor. U²=2^64 physical ticks remains a runtime obstacle.
General noisy repair, robust cap, full depth-two dynamics and goal completion
remain open. No shared change is requested.

## Latest continuation: compact ROM with verified temporary reuse

Previous goal turn was progress (integrated parallel vote plus two audited
macrosteps). This continuation adds a static allocator with symbolic live-owner
verification, safe operand reordering and a fixed 384-slot cap (362 used).
The raw parallel-holder rule/descriptor is reused unchanged; reuse_holder has
its own fixed ROM/projection, identical at every initialized depth. Computation
cells fall to 30,727 and evaluation to 1,168,148,348 ticks. Q/U are still unchanged
for this controlled comparison. The initial lowest-free allocator's poor time
tradeoff is preserved with the subsequent capacity search.

Four allocator tests and 21 integration tests pass. Two complete one-link periods
and all nine execution/audit stages pass, with exact state handoff and 40 raw
controller changes each. The sequential validation took 78.025921 s; maximum
child RSS 901,700 KiB. All runs are terminal; no substantial GPU work. Details,
commands, ownership and limits: [REUSE_HOLDER.md](REUSE_HOLDER.md).

Next: implement a fixed smaller-colony schedule with independent Q/U, using this
allocator. Q=32,768 can hold the measured core but is not yet a validated rule
choice. Recheck full self-description, communication collisions, deadlines,
repair and trickle-down. Then actual depth-two GPU dynamics and physical faults.
No full depth-two macrostep, general cross-level noise correction or goal
completion is claimed. Existing fixtures/dependencies remain preserved.

## Active continuation: integrated parallel-vote self-description and macrosteps

Previous goal-status-only turn was no progress; this continuation changes code
and supplies new execution evidence. New parallel_holder_* files implement the
protected vote in the full fixed local rule and its own descriptor/ROM. Radius,
physical width and Q/U are unchanged for the controlled comparison. Evaluation
falls from 4,533,298,561 to 1,664,309,717 ticks; computation cells fall from 57,332
to 43,808. See [PARALLEL_HOLDER.md](PARALLEL_HOLDER.md) for tests, failed-fixture
explanation, exact commands, resources and remaining obligations.

All 21 distinct integration/suffix/recurrent tests have passing evidence. The
first complete macrostep passed an independent audit, including all raw fields,
2,229 complete-native witnesses and a new flag-profile certificate. The second
prefix also passed from the actual first commit; second complete macrostep and combined audit have now passed: 2U ticks,
40 raw controller changes in each upper transition, identical rule/ROM and exact
entire-state handoff. All runs are terminal. Host runs stay below 1 GiB measured RSS per process; no substantial
GPU allocation. Existing holder sources and evidence remain frozen. Next space
optimization: descriptor result storage reuse (diagnostic peak live words 240
versus 13,443 allocated), followed by a smaller-Q/independent-U schedule analysis.
No depth-two dynamics or general cross-level noise-correction claim is made.

## Latest optimization finding: protected parallel temporal vote fits radius seven

User priorities are actual self-simulation, practical two-level GPU execution,
and cross-level correction; 128 is no longer a design constraint. Gray does
not give a numerical full-self-simulation construction at Q=8192: his later
program and time bounds require sufficiently large Q with unspecified constants.
See [PRACTICAL_SELF_SIMULATION.md](PRACTICAL_SELF_SIMULATION.md).

Measured current temporal voting accounts for 2,383,873,806 / 4,533,298,561 ticks
per evaluation (52.586%). An independent parallel_vote_probe uses existing raw
fields and support [-5,+6], inside current radius seven. Four tests passed in
0.360 s, including full raw descriptor parity, all pairs of two damaged holders,
exact locality and radius-five/three-fault negative witnesses. This is a tested
primitive, not an integrated rule or self-reference claim. New full-rule gating,
priority, ROM/descriptor and resource validation remain necessary. Current holder
sources and evidence are unchanged. The cost-study uses about 61 MiB host RAM;
no GPU job or large allocation was launched. Commands, files and limits are in
the linked report. Next work: integrate this optimization in a separate fixed
revision before an expensive GPU port, then optimize remaining serial sweeps.

## Architectural clarification: colony size versus work period

The user asked whether large colonies merely preserve U<=128Q. The holder uses
U=128Q; 128 is Gray's schedule choice, not a universal self-simulation bound.
The billion-cell Q principally accommodates our serial evaluator under that
schedule. See [COLONY_SIZE_TRADEOFF.md](COLONY_SIZE_TRADEOFF.md) for source uses
and alternatives. Compare smaller colonies with a reanalyzed longer schedule
and/or a faster specialized evaluator before a substantial GPU port. This is
an architectural review, not a verified replacement. Only this note and STATUS
were edited; no tests or jobs were launched. Frozen holder evidence is unchanged.

## Latest execution result: bounded CUDA kernel validated

The user's shared-CPU-memory constraint is now explicit. No large CPU allocation
will be restarted. The old causal-window process and session are absent; its
initialization-only artifacts are preserved, with exit cause undetermined.

Three new CUDA/packing tests pass (1.415 s): 160 GPU/CPU local comparisons and
32 full physical holder comparisons, with every controller/mail field retained.
The measured small GPU call used 179,684 KiB maximum host RSS and 3,364,192 bytes
of explicit device allocation (CUDA context additional). The packed two-state
estimate for 3,601 colonies is 33.0 GB instead of 82.6 GB. The complete resident
GPU event executor remains to be implemented and audited; no large allocation
or new depth-two execution claim has been made. See [GPU_MEMORY.md](GPU_MEMORY.md).

Owned additions: holder_packed.py, holder_cuda_local.{py,cu}, their tests and
resource driver. All build products are private. The existing fixed physical
rule, alphabet and ROM are unchanged. CPU staging target <1 GiB; substantial
GPU scheduling remains coordinated through this file and MAIN_AGENT_NOTES.md.
All small CUDA checks are terminal; latest device check returned to 5 MiB used.
The full goal remains active; actual depth-two/three macrosteps and general
noise robustness are still outstanding.

## Current steering: bound CPU memory and move execution to GPU

User explicitly corrected CPU memory use: host RAM is shared. The 3,601-colony
CPU attempt is **not running**: its process and exec session are absent, and only
an initialization log/source archive exist. The exit cause is not established.
`holder_depth2_causal_v1.stop.json` preserves the observation; there is no completed
causal-window result. Do not restart that dense CPU allocation. The effective
current CPU cgroup limit is 48 GiB, despite much greater host-wide free RAM.

New work will use bounded host staging and packed GPU-resident physical state.
The projected coherent-state record can be packed without changing the fixed
physical rule/alphabet; a CUDA implementation must be checked against the full
physical descriptor before larger execution. Initial GPU checks will use only
small batches. No substantial GPU allocation is running. The A100 was idle at
the latest read-only check (5 MiB used, no compute PID).

GPU coordination: the user has now requested GPU-oriented execution. Main agent,
please record scheduling constraints in MAIN_AGENT_NOTES.md before a substantial
new run; this agent is preparing/testing isolated kernels and will record their
explicit memory budget here. No shared CUDA files/build products will be changed.
Runtime host staging target is below 1 GiB; initial validation VRAM below 64 MiB.

## Active continuation: certified physical window inside depth two

Previous turn classification: **progress** (two audited one-link periods and
repair/cap evidence). The goal remains active, with no external blocker.
No MAIN_AGENT_NOTES.md reply or matching protected third_link_initialized PID
was present on recheck. All previously frozen holder source dependencies are
preserved; current additions use new files only. Status/report snapshots in old
source bundles remain historical snapshots, not freezes on this handoff file.

A true physical causal-window run is now active:
`holder_depth2_causal_v1`, using 3,601 lower colonies and 16 CPU threads, no GPU.
It starts from the actual recursively encoded depth-two configuration. Its
radius-seven physical light cone covers two full lower work periods plus a
whole-colony margin at each artificial seam. The target is two decoded ticks of
the next-level controller (reset and motion), **not** a full depth-two top
macrostep. Physical horizon 274,877,906,944; the complete depth-two top macrostep
still needs U^2 ticks. The initializer and runtime rule/ROM are unchanged.

New `holder_suffix_mixed` admits independent right Signal bits with zero left
Signal, justified by an exact 64-variable all-front proof including three
adjacent colonies. Three mixed-profile/OpenMP tests pass (22.793 s). The private
OpenMP kernels parallelize independent evaluations of the same local formula;
serial state/counter comparisons pass. Two lossless endpoint-snapshot tests pass
(4.477 s). Snapshots preserve actual Data/Signal and reject any omitted nonzero
controller/mail/flags; they never re-encode represented upper states.

A fifteen-colony driver benchmark completed two periods in 23.001243256 s. It is
explicitly marked **not physically causally embedded**, and is used only to
validate the driver before the larger run. Watch
`figs/fixed_rule/holder_depth2_causal_v1.progress.json` and its actual process.
The full run will need an independent initialization, light-cone, raw-state and
continuity audit before any depth-two dynamic-prefix claim.

## Current result: two complete redundant-holder periods

**Two successive one-link macrosteps are independently audited:** 274,877,906,944
physical ticks with one fixed radius-seven rule, 2,724-bit projected alphabet,
complete 154-word self-description and unchanged ROM. All fifteen radius-seven
inputs are distinct represented cells. Actual raw controller/memory/signal state
passes between periods; 40 controller words change in each represented step.
The first performs WRITE; the second moves the controller and retains its result.
See [HOLDER.md](HOLDER.md), `holder_two_periods_audit_v1.json` and the explicit
`holder_controller_semantics_v1.json` classification of the reused WRITE label.

The first/second CPU prefixes took 10.450972/10.597322 s; suffixes took
23.291458/23.842412 s. All four component runs and their independent audits pass.
Each suffix includes 2,229 saved complete-native checks. Twenty-one focused tests
pass across holder rule/repair, prefix, suffix, cap and recurrence files. The
restricted flag-profile and complete cap-controller identities have exact ROBDD
proofs. No deeper dynamics, organized robust cap or noise threshold is claimed.

A preserved nonzero-wave counterexample prevents overstating repair: one Flag1
bit deletion delays the front through eight literal ticks while every procedure
field remains correct. Independent audit checks all 2,592 local outputs. For this
specific family, the certified recurrence bounds later rejoining by 178,956,970
ticks. General repair during mail/geometry damage remains open.

All owned holder jobs are terminal. No GPU job or shared artifact was touched;
exact CPU motion skipping sufficed. Read-only check again found no matching
third_link_initialized PID; that does not establish shared completion. Please
reply in MAIN_AGENT_NOTES.md, which remains absent. No shared change is requested.
The goal remains active with no external blocker. Next concrete obligations are
in [NEXT_CLOSURE.md](NEXT_CLOSURE.md): general physical-to-program refinement,
arbitrary flag suffixes, actual second-link histories, then fault/noise scaling.

The sections below retain earlier checkpoints; the current result above
supersedes their under-test/running statuses.

## Latest verified holder execution

See [HOLDER.md](HOLDER.md). One complete redundant-holder macrostep is now
independently audited: **137,438,953,472 physical ticks**, 15 nonaliased represented
cells, every raw replica/controller/metadata output, actual local computation,
flag delivery, exact physical waves, recomputation and commit. Prefix 10.450972 s;
suffix 23.291458 s. The suffix audit checks 314 immutable/live sources and 2,229
full-native transition witnesses. This remains one-link execution, not depth two.

The restricted right-one/left-zero flag-profile acceleration has an exact all-
Address/all-front ROBDD certificate. The ordinary cap now includes backup-head
reset/vote pulses; all 154 raw outputs are proved for all 2^37 clock values.
Five prefix, three suffix, three cap and two recurrent-prefix tests pass, in
addition to the eight holder rule/repair tests. Sources captured by each run are
frozen; new extensions use new files only. No GPU work was needed.

The recurrent physical prefix is currently running from the actual first commit
(`holder_recurrent_execution_v1`). It carries all controller/memory residues and
old Signal. Next: audit a second full period, then extend repair beyond coherent
zero-flag states and tackle deeper physical execution. No external blocker; the
fixed-rule goal remains active. MAIN_AGENT_NOTES.md remains the reply channel.

## Current continuation: fivefold physical controller and repair

The fixed-rule goal is active. New owned `holder_*` files implement one radius-seven
redundant physical revision with Q=2^30, U=2^37, complete 154-word self-description,
105-word projected physical alphabet, and seven hard-wired metadata records.
See [HOLDER.md](HOLDER.md) for source choices, exact resource bounds and limits.
All earlier construction sources remain frozen. No shared change is requested.

Strict native compilation and eight rule/repair tests pass (12.147 s; exact log
`figs/fixed_rule/holder_tests_v2.log`). The prior one-Info-bit physical fault now
recovers in one tick. Two arbitrary complete physical-cell faults recover in two
ticks in 28 tested coherent zero-flag clock/address cases; whole fault cones are
compared. Live WRITE/controller and a three-copy negative witness are included.
This is finite-case repair evidence, not a general robustness theorem.

Current edits are restricted to new `holder_*` modules and
`tests/fixed_rule/test_holder_*.py`, this report and HOLDER.md. An exact coherent
physical-prefix executor is under test, including complete state reconstruction
and guarded simultaneous packet/head free flight. Its compressed records are not
another physical alphabet. A complete self-program execution, full periods,
ordinary full-controller termination data, nonzero-flag repair and deeper dynamics
remain next. Depth-three encoding is not depth-three execution.

No GPU work this continuation. MAIN_AGENT_NOTES.md remains absent; please use it
for replies. A read-only check found no matching third_link_initialized PID;
no completion claim or dataset change follows. The main agent retains GPU
scheduling. No external blocker and no shared dependency change.

## Current continuation: boundary proof and locality prerequisite for repair

Previous goal turn: **progress**; this turn has produced new exact identities,
a physical fault counterexample and a new described local-voting revision.
No external blocker. MAIN_AGENT_NOTES.md is still absent. No GPU work this turn.

See [BOUNDARY_AND_REPAIR.md](BOUNDARY_AND_REPAIR.md): an exact ROBDD check proves
the ordinary zero-payload candidate-B cap for every one of its 2^30 Ages. A failed
arbitrary-payload conjecture exposed a one-tick Signal pulse and is preserved.
The corrected family proof covers 745 independent input bits. The cap is ordinary
initial data under the same rule, but is neither an organized colony nor a robust
boundary. No deeper physical execution follows from its algebraic consistency.

`cap_fault_execution_v1` completes two physical periods with exactly one Info-bit
flip at physical address 8,390,034. The erroneous represented Data survives both
periods; all three temporal gathers read the same bad bit. Independent audit
passes 251 sources and the complete raw-state handoff. This is direct evidence
that the current temporal redundancy cannot replace Gray's spatial protection.

See [SERIAL_VOTE.md](SERIAL_VOTE.md): a radius-five indistinguishability witness
rules out naively correcting fivefold inputs before the existing radius-two
instantaneous vote. New `serial_vote_*` files replace that vote with 2,112 actual
NAND instructions on the existing local controller. The fixed revised constants
are Q=2^25, U=2^32, raw/projected width 792/594, radius five, 2,618-operation complete
self-description, 9,969-cell core. Voting plus evaluation costs 133,614,496 ticks
and fits the measured budget. Four new rule tests and two locality tests pass.
A separate BDD proof covers all 2^32 clock values of its ordinary cap.

The eleven-cell nonaliased serial-vote prefix completed **3,221,225,471 physical
ticks in 291.733692901209 s**. Its independent audit passed 275 frozen/live sources,
all raw gathers, actual NAND votes, full evaluator state, computed flag delivery,
and capture. Nine additional flag/clock/composition/commit tests pass (4.965 s).
The actual physical suffix completed in **151.4977057473734 s**. Its independent
audit passed: 276 source files, 438,856 stored-site checks, 909 full-native local
comparisons, complete scalar/native/self-description agreement and zero flags
at commit. **One complete 4,294,967,296-tick serial-vote macrostep is now audited.**
Fivefold controller protection is still absent: the change removes a concrete
locality obstacle, but does not fix the demonstrated Info-bit fault.
`serial_vote_resources_v1.json` records all costs. All owned experiments in this
continuation are now terminal; the last process check found none running. No
matching third_link_initialized process was present; shared datasets are untouched
and no shared completion claim is inferred.

The symbolic proof contract now explicitly rejects missing/extra raw outputs,
unknown operations and forward DAG references. Three additional tests pass
(0.662 s); both complete cap descriptors pass the stricter front-end. This avoids
relying on a zip loop's known-input length when testing mutated descriptions.

Owned additions this turn: word_bdd.py, serial_vote_* modules/executors, proof
and cap-fault drivers/auditor, their tests, and the reports above. All earlier construction files remain frozen. No shared
change or GPU allocation requested. A new immutable source/report/evidence bundle
is `continuation_sources_v3.{json,tar.gz}`.

Next: implement the holder-local redundant controller described (but not yet
validated) in [REDUNDANCY_NEXT.md](REDUNDANCY_NEXT.md). Explicitly resolve Wf and
raw-geometry coupling, include every replica and static lookup record in the
self-description, and measure the enlarged fixed program before choosing Q/U.
Then rerun the single-physical-bit witness plus controller/mail/geometry faults.
Deeper physical dynamics and the amplification/noise objective remain open.

## Active continuation: bounded literal history and explicit repair candidate

Previous goal turn: **progress**. No external blocker. Only owned new files are
being added; no shared module, CUDA dependency, dataset or GPU process was changed.

The literal delivery rule remains frozen. `flag_byte_profile.cpp` and its two
CPU diagnostic drivers identify actual `bad_alloc` growth (11,744,052 nodes in
6.601196786388755 s at a 1 GiB bound with one BLAS thread). The earlier 2 GiB probe
was below NumPy's approximately 2.6 GiB default virtual footprint; one-thread
baseline is 107,484 KiB. This distinction is preserved in both records.

`flag_byte_stream*` now advances the same physical recurrence in bounded chunks,
checks every accepted query using complete-native truth tables, verifies periodic
input reconstruction, then garbage-collects obsolete history. Five focused tests
pass (1.685 s). A variant retaining prior verified query certificates also passes
five tests (1.914 s), but saves less than two percent on the actual case. That
owned CPU run was deliberately stopped after preserving its **1,015,696-tick**
accepted state; see `flag_stream_cache_stop_v1.json`. The plain 1,048,576-tick run
completed in 871.8716364456341 s: all 2,084,150,597 accepted temporal queries were independently checked before collection. The final age is 823,132,160; F1/F2 counts are 94,371,840 / 72,627,515. Only 1/240 of the literal suffix was advanced; full literal commit remains open.

The separately named `repair_b_*` construction explicitly fixes healthy Flag2
erasure to at most one in-colony left one, following the documented candidate-B
repair contract. **This changes the construction revision, never the rule by
depth.** The printed rule/evidence are preserved. Source justification, differing
claims and the unforced clearing proof are in [REPAIR_B.md](REPAIR_B.md).

Candidate B retains radius 5, raw 788 bits and projected 590 bits. Its complete
self-description has 2,648 operations; the 7,913-cell core and 56,601,678-tick
complete evaluator fit the fixed Q/U budget. The 28-test initial suite and three
new recurrent-prefix tests pass; no depth-two dynamics are claimed. An explicit
counterfactual flag-data probe verifies clearing by 99Q and reaches U in
21.712381306104362 s; it is not a continuation of the literal trajectory.

The actual candidate-B prefix completed 805,306,367 physical ticks in
510.10821578931063 s; its independent audit passed all 224 archived/live sources.
The first complete physical macrostep then reached U in 63.699842274188995 s
of suffix execution. `repair_b_macrostep_audit_v2.json` passed: 225 source files,
728,456 stored-site checks, 1,688 full-native local comparisons, full raw-controller
vote/Hold/commit and scalar/native/self-description agreement. The v1 audit log
preserves a parser/module-name collision, corrected only in the new auditor.
The first recurrent driver was deliberately stopped after discovering its stale
zero-Signal assertion; see `repair_b_recurrent_stop_v1.json`. Its corrected v2
prefix completed in 517.4365741014481 s, then the physical suffix completed in
67.40795897878706 s. Both independent audits passed, including exact prior stored
state and carried Signal. The second macrostep audit checks 728,456 stored sites
and 1,693 full-native local transitions. **The two-period chain audit passes:
2,147,483,648 physical ticks, two complete applications of the same G, active
controller changes in both periods, no upper reinitialization.** Full details and
exact commands are in [REPAIR_B.md](REPAIR_B.md); final evidence is
`repair_b_two_periods_audit_v1.json`. No depth-two dynamics are claimed.

User explicitly suggested CUDA acceleration. Isolated CUDA 12.6 / sm_80 builds
live only under `figs/fixed_rule/build`. Four basic tests passed (5.250 s); the
complete 1,048,576-tick endpoint matches the independently checked CPU DAG at all
192,937,984 sites. GPU time 4.923756510950625 s; full spatial-DAG comparison
0.8771763443946838 s. The independent final audit passed 160 source files,
every F1 bit against its derived prefix, and 358 complete-native comparisons.
See [STREAM_CUDA.md](STREAM_CUDA.md) for proof, commands and performance limits.

A separately named local fixed-point optimization passed five tests (4.859 s),
after correcting a false test assumption about a persistent defect at Address 0.
A 60-second-capped actual-state probe completed in 52.59678079839796 s at
4,194,368 ticks after cutoff: F1=0 everywhere, F2 count 59,665,313. Complete CPU
checks rejected stationarity and any return within 64 further steps. **No long
skip or full literal suffix is claimed.** The endpoint is saved and needs no GPU
restart from cutoff. Later million-tick blocks took 10.91, 16.91 and 22.74 s;
do not extrapolate the first-million timing. All owned jobs in this continuation
have completed or were deliberately stopped with records. No shared GPU job or
CUDA artifact was touched. The last read-only check found no matching
`third_link_initialized` process; original outputs remain untouched and this
absence is not a completion audit.

**GPU scheduling request:** main agent retains scheduling. Please use
`MAIN_AGENT_NOTES.md` to coordinate a substantial literal-suffix allocation, if
wanted. Only small capped pilots and focused tests were run here. No shared
source change is requested. Source-preservation audit checked seven manifests,
243 distinct source files, with zero mismatches.

Please reply only in `Report/fixed_rule/MAIN_AGENT_NOTES.md`; it remains absent.
Owned work: new stream/diagnostic/candidate-B code, matching tests/experiments,
these reports, and new isolated flag CUDA accelerator files. No shared change.
Next: establish an inspectable execution representation for deeper dynamics;
close organized finite-depth termination and full controller/data redundancy;
coordinate any substantial GPU continuation of the preserved literal suffix.
The exact depth-1/2/3 resource arithmetic is in `repair_b_resources_v2.json`.
The end-of-continuation source/report bundle is `continuation_sources_v2.tar.gz`,
with hashes and evidence inventory in `continuation_sources_v2.json`.
Do not report initial nesting as deeper dynamical closure or the two-field local
repair contract as full noise robustness.

## Previous continuation: complete physical state through 98Q; controller commit audited

The delivery physical rule/ROM remains unchanged: radius 5, projected 590 bits,
raw 788 bits, 2,680-operation self-description. New CPU execution representations
are in `delivery_control_*`, `delivery_composed_world`, `flag_words`,
`flag_blocks`, `flag_*hash`, and `flag_byte_native.{py,cpp}`. They process fixed
physical transitions; they never evaluate upper controllers or dispatch on depth.
The delivery prefix and both completed suffix source manifests remain unchanged.
A broader scan found four legacy v1 live-hash mismatches, in files not edited by
this continuation; see the preservation note in SUFFIX.md.

`delivery_forcing_execution_v1` now composes **actual flags** with the controller
quotient through the entire forcing window: **16,777,217 additional physical
ticks**, from 96Q−1 to **98Q**, in **90.09758451394737 s**. It reproduces the saved
cutoff exactly and checks **1,721 complete native neighborhoods** at six frames.
All 192,937,984 physical sites are represented by core/tail arrays plus complete
flag runs and canonical padding. Final counts are **125,829,120 Flag1** and
**78,320,307 Flag2** bits; Wf1/Wf2 are zero. These residues are retained.
The earlier prefix plus this run reaches 822,083,584 ticks; **30Q remain**.
`delivery_forcing_audit_v1.json` passes with 151 archived/live sources, all
183,586 stored sites checked bit-for-bit against the physical flag runs, raw
Info preserved, and an exact controller replay (0.9483850188553333 s).

`delivery_control_execution_v1` independently executes stage-five evaluation
and Info commit through U, with all mail fields guarded zero. Its **268,435,457**
physical controller ticks take **2.4161268267780542 s**. Independent
`delivery_control_audit_v1.json` passes: **147 archived/live sources**, five
complete saved controller frames replayed, every raw vote/Hold word checked,
scalar/native/description agreement, active WRITE of `0x123456789ABCDEF0`, and
690 native factorization neighborhood pairs. It is a **controller quotient**,
not a completed full-state macrostep: later physical flags are not yet known.

Preserved resource failures: 64-site repeated-word compression fragments after
the forcing cutoff; nine-word blocks improve some profiles but still fragment on
the actual mixed case. Both long runs were deliberately stopped with checkpoints.
64-site Python light cones, 8-site Python light cones, and compact native light
cones did not finish the full 251,658,240-tick suffix under their resource bounds.
The native catch-all failure does not identify its exception; do not call it a
proved memory-only failure. See `SUFFIX.md` and failure/stop records.

A bounded native **65,536-tick** suffix succeeds in **0.24369460251182318 s**.
Its saved derivation independently passes `audit_flag_byte`: **2,893 queries**,
**1,152 complete-native local truth-table checks**, 180 distinct leaf triples,
and 1,971 periodic initial subblocks. The recursive DAG represents physical
space/time light cones, not simulated controller interpretation. A larger **1,048,576-tick** request also failed under the 6 GiB bound; no
state/proof is claimed for it. All owned CPU jobs are now finished. Exact
commands, results, and the next steps are in [SUFFIX.md](SUFFIX.md).

Current ownership additions include the above code; matching tests; suffix,
forcing and proof experiment/audit files; this status/report; and owned evidence.
No shared interface change is required. Main-agent notes remain absent; please
reply in `Report/fixed_rule/MAIN_AGENT_NOTES.md`. No GPU work was started.

## Previous milestone: computed-flag delivery prefix completed and audited

[DELIVERY.md](DELIVERY.md) describes new `delivery_*` files: one complete fixed
ROM with a described IF_THIRD branch, 70Q stage-three vote, ten local SENDs of
computed upper flags, and five physical MEM buffers per boundary. Tail META
fallback is in F. Physical projected width is **590 bits / 25 words**; raw F is
**788 bits / 32 words**, radius five. All depths use that same rule/ROM. No deeper
dynamics or complete new-rule macrostep is claimed.

The unpruned 3,050-operation description failed both budgets. Pure unreachable-
wire elimination, checked against complete scalar/unpruned/native outputs,
leaves **2,680 operations**, with no restriction of input alphabet. Core size is
7,977 cells; evaluation takes 57,793,354 ticks. Final stage-three delivery arrives
66,333,537 ticks after 70Q, leaving 9,163,935 ticks before capture. Both failed
and successful timing artifacts are preserved; actual final-packet arrival is
checked one tick before and at the predicted tick.

Commands, both completed successfully:

- `python -m experiments.fixed_rule.delivery_execution --output figs/fixed_rule/delivery_execution_v1`
- `python -m experiments.fixed_rule.audit_delivery_execution --input figs/fixed_rule/delivery_execution_v1 --output figs/fixed_rule/delivery_execution_audit_v1.json`

The run completed **805,306,367 physical ticks** on **23 represented cells**
in **524.7449483852834 s**. Three full raw retrievals, majority vote, complete
self-described evaluation, output-program reconstruction, an active simulated
WRITE, ten actual computed-flag packet deliveries, five-copy signal capture and
rest all passed. No driver-installed capture payloads; Python expression and
upper-transition callbacks were disabled during physical evolution.

Counts: 22,684,427 literal core ticks + 709,777,043 exact quiet ticks + 72,844,897
guarded head-scan ticks; 1,149,204,177 local evaluations. 192,937,984 physical
sites represented, 183,586 explicitly stored core/tail sites. The independent
audit verifies **142 archived/live source files**, scalar/native/description
agreement, every saved raw history/vote/Hold/payload/Signal array and the complete
final stored state. It ends at Age **96Q−1, before Wf starts**. At this earlier milestone no stage-five recomputation or commit had run.
The continuation above now verifies the controller quotient through commit.

22 focused tests passed (each uses `python -m unittest discover -s tests/fixed_rule -p NAME -v`):

| NAME / pattern | Passed | Seconds |
|---|---:|---:|
| test_delivery_*.py at initial rule/program-only capture | 7 | 2.010 |
| test_delivery_prefix.py (final v2) | 5 | 1.401 |
| test_delivery_closure.py | 4 | 0.241 |
| test_delivery_packet_timing.py | 2 | 0.334 |
| test_delivery_factorization.py | 2 | 0.431 |
| test_flag2_bits.py | 2 | 0.101 |

The first glob command ran before the other delivery test files existed; it is
not a claim of a current all-delivery suite run. The retained v1 prefix test
failure was a test-only unwrapped periodic address; v2 passes. Closure tests
follow every raw word through actual Info/Data paths at depths 1–3, compare all
description instructions/output-copy targets, and verify native locality.

The cap now requires zero payload: the new tail MEM reset erases a nonzero
payload. A zero-payload flagged homogeneous Age-periodic orbit passes source
event-boundary tests, but is not an organized robustness boundary. D8/D10 remain.

A tested domain factorization preserves canonical Address/Age with arbitrary
flags. Controller/Data/Signal outputs are flag-independent; mail must still be
cleared by computed Flag1 and Wf2 gated by it. The continuation above now uses this lemma in a guarded composed
physical executor. `flag2_bits` and `flag2_profile_probe_v1.json` supply an exact
one-sided, no-Flag1 physical projection for 65,536 ticks (0.12675732001662254 s).
Support ends at 836 with 837 ones at that sampled time; intermediate profiles
have holes. It is neither a rigid wave nor the full coupled 2Q trickle window.

**Next:** execute actual physical signal/flag evolution through stage four,
retain its mail coupling, then stage five and commit and a second period under
this same G. The current prefix executor explicitly rejects crossing 96Q. Full
workspace/controller redundancy, organized termination, deeper dynamics and
noise robustness still remain. All owned runs/audits are now finished.

## Verified self-simulation milestone

[EARLY.md](EARLY.md) is the latest completed macrostep construction. One fixed
585-bit / 24-word physical alphabet, radius five, Q=8,388,608 and U=128Q;
complete raw F has 783 bits / 31 words and 2,484 described operations. A single
fixed ROM serves all initialized depths. Complete evaluator state is encoded;
no runtime level dispatcher, recursive upper interpreter or host refill is used.

Gray pp.31–32 motivates early current-Address program overwrite and projection;
Gács §§9.2–9.3 supports complete field descriptions/block simulation. The fixed
14-instruction prefix repairs all seven encoded static words before retrieval.
Output reconstruction still uses newly computed Address, a distinct operation.
Three histories, local votes, two evaluations, five rests and commit are clocked.

**Two successive full U periods completed and independently audited.** All 161
initially corrupted program words (4,554 raw bits) repair. Decoded raw fields
match complete F, including active NAND write, simulated vote/commit and
Address/Age repair. Nine output program records require regeneration. Printed
Flag2 persists. One experimental clocked simulation link; no full Gray hierarchy
level or depth-two/three dynamics is claimed.

Commands (both passed):

- `python -m experiments.fixed_rule.early_selfsim --output figs/fixed_rule/early_selfsim_v1 --steps 2`
- `python -m experiments.fixed_rule.audit_early --input figs/fixed_rule/early_selfsim_v1 --output figs/fixed_rule/early_audit_v1.json`

2,147,483,648 physical ticks in 521.0846257265657 s; 41,205,043 literal core ticks,
1,879,725,896 exact quiet ticks and 226,552,709 guarded head-scan ticks.
2,086,802,374 local evaluations; 192,937,984 represented sites, 172,362 explicit
core sites / 33,093,504 bytes. Independent audit verifies 107 archived/live
sources, full raw states, saved early-repair/history/vote/Hold arrays and all ten
pairs of raw rest endpoints. Initial raw program corruption is saved explicitly.
[Exact evidence and hashes](EARLY.md).

Focused tests used `python -m unittest discover -s tests/fixed_rule -p NAME -v`:

| NAME | Passed | Seconds |
|---|---:|---:|
| test_early_repair.py | 4 | 0.935 |
| test_early_nesting.py | 1 | 0.280 |
| test_early_convergence.py | 1 | 0.341 |
| test_canonical_flags.py | 3 | 0.773 |
| test_canonical_clock.py | 2 | 0.857 |
| test_canonical_flag_world.py | 3 | 4.980 |

These are 14 focused cases, not a new full-suite run. Nesting checks follow all
31 raw fields through actual Info/Data paths at depths 1–3. Full physical-state
convergence is checked for initial program-only damage, not general noise.

## New signal candidate, separate from the frozen macrostep rule

[SIGNAL.md](SIGNAL.md) documents new `signal_rule`, `signal_description`,
`signal_native`, `signal_world` and `signal_resources`. This candidate adds one
five-bit signal field, giving a complete **788-bit / 32-word** unprojected rule,
radius five, and a **2,825-operation** complete description. This revision is
fixed independently of depth but **has no compiled self-simulation ROM/projected
rule or macrostep run yet**. It does not supersede the audited early result.

Implemented: five-copy majority, computed-Address capture at proposed computed
Age 79Q, source boundary/time masks for Wf, computed-Flag1 gating/erasure, and
actual physical flag-wave initiation from signals. Signal receives its capture
payload from local Data. Upper computation/delivery into those Data locations is
not implemented. Signal protection is not whole-workspace/controller redundancy.

D10 is now distinguished by a concrete locality witness: two inputs identical
through center radius five have different fully updated target signals because
repair at target +3 reads offsets +6…+8. The candidate explicitly chooses a voted
old signal before remote clearing. This agrees on canonical geometry in the Wf
window, but is not asserted source-equivalent on damaged geometry. D8 remains.

The CPU signal-prefix experiment starts with initialized local payloads, captures
signals, then generates Wf and both physical flag waves. Each case represents
142,606,593 ticks (258 literal, 142,606,335 guarded quiet), including a 256-tick
window prefix. Final both-edge counts: Flag1=770, Flag2=41, Wf1=Wf2=5.
This is a constrained complete-state physical family, not simulated transitions,
upper delivery, the entire 2Q trickle window or a noise-robustness experiment.

- `python -m experiments.fixed_rule.signal_prefix --output figs/fixed_rule/signal_prefix_v1.json` passed in 4.684136750176549 s.
- `python -m experiments.fixed_rule.audit_signal_prefix --input figs/fixed_rule/signal_prefix_v1.json --output figs/fixed_rule/signal_prefix_audit_v1.json` passed: 211,797 complete native local comparisons across both cases, every literal tick and saved frame checked, in 64.22559570427984 s.

Additional focused tests (same unittest command format): `test_signal_rule.py`
5 passed / 1.439 s; `test_signal_world.py` final v2 4 passed / 0.746 s;
`test_signal_resources.py` 1 passed / 0.023 s. Raw controller/Signal encoding,
scalar/description/native parity, computed Address, fivefold signal repair,
actual Wf initiation, locality and quiet-proof rejection cases are included.

**Resource failure found:** enlarged transcript has 8,256 cells and evaluation
62,836,416 ticks. Starting at 72Q misses 79Q capture before delivery. A 70Q vote
has positive gather margin and 4,273,924 ticks left after the current evaluation
and rightward flight, but delivery/control/core-growth costs remain uncounted.
This is a proposed schedule, not an established complete budget certificate.
`signal_resources_v2.json` qualifies the bound; v1's overly broad label is retained.

## Next concrete work and remaining limits

1. Use the immutable, now audited 98Q checkpoint to finish the remaining 30Q
   physical flag suffix. Both RLE and light-cone resource failures are preserved;
   consider adaptive spatial compression or bounded-memory causal evaluation,
   with local certificates, rather than assuming the flags have disappeared.
2. Compose the completed flag suffix with the audited controller commit, then
   execute a second full period with every raw field and all physical residues.
   Current suffix executors intentionally reject crossing into the next period.
3. Implement all required spatial redundancy/repair and organized termination;
   resolve D8/D10 alternatives with distinguishing tests. Do not select a Flag2
   variant silently to improve execution cost. The zero-payload flagged cap is
   not an organized robustness boundary.
4. Validate deeper **dynamics**, then measured physical noise. Depth-three raw
   initialization/encoding tests are not hierarchy execution. U² is about
   1.153e18 physical ticks per depth-two top transition. Recheck space/time after
   every additional mechanism; no per-depth alphabet or kernel changes.

## Ownership, preservation and coordination

Only owned fixed_rule code/tests/experiments/reports/results/builds were written.
Frozen projected/regenerated/window/word/clock/early/delivery manifests match all
33/46/63/81/95/107/142 live source files. Earlier approaches and negative results are
preserved. Main-agent notes were absent. No shared report/module/test/dataset,
CUDA artifact or GPU dependency was modified; no commits/resets/branch changes.

No matching third_link_initialized process was found at the latest read-only
check. Last read metadata remained running at 51,118,080 steps, no top checks;
trace sampling at 3120. This does not establish completion. The main agent
retains GPU scheduling. CPU/file operations use approved escalation because
ordinary bwrap namespace creation fails. There is no external blocker.

The prior delivery-prefix CPU runs and audits are finished. See the latest
continuation above for new CPU work.
The signal source archive/manifest
contains 16 files and hashes its experiment, audit, resource records and test logs.
No GPU work was started. The full goal remains active.

The completed delivery archive contains 142 source files; nine post-capture
sources and focused test/artifact hashes are preserved in
`figs/fixed_rule/delivery_supplemental_v1.{json,tar.gz}`.

Current continuation evidence is frozen separately in
`figs/fixed_rule/suffix_sources_v1.{json,tar.gz}`. The focused tests total 24
passes across nine files; exact commands and individual timings are in SUFFIX.md.
Those earlier jobs are finished; the active continuation above lists new CPU
work. The goal has no external blocker and is not
marked complete: the remaining physical flag suffix, successive periods,
repair/termination and deeper dynamics require further work.
