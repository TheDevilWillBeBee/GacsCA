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
or historical dataset was modified. All owned jobs are terminal.

## Latest milestone: actual fixed Q16384/U2^30 candidate, same alphabet

[COMPACT16_CANDIDATE.md](COMPACT16_CANDIDATE.md) records compact16_holder with
actual Q16384/U1073741824, raw4090bits/projected2704bits/radius7 unchanged across
depths. New full descriptor53f7adbf7c34df6b17897b20a0d0654108f23a9c064defb89bb3c6d1a7fb846b;
ROM4d055889959a880f189539dc213801780f8e2efa3daa7cb31e72cb3003f48b32.
Core16354/MEM3447/instructions12906;819159153 controller ticks; core-tail gap25.
The sparse compile uses689 gathered mutable inputs and49 regenerated own-ROM
inputs while retaining all154 Info/Hold fields. This separate candidate does not
replace the frozen execution baseline; no new full physical period/GPU run yet.

Address remains15bits and Age32bits. Modular Address helpers now use log2Q;
zero-offset metadata queries are masked too. Complete typed description equality
and symbolic own-ROM computation PASS, including high raw Address/Age states,
controllers, two evaluations, metadata regeneration and commit/reset. Six tests
PASS include scalar/descriptor/private native parity,24 random raw neighborhoods,
clock/Address boundaries, active copies, depth1-3 identity and negative mutations.

812 regular-clock event cases were reproved directly against the NEW descriptor:
116 event families/seven intervals/945999993 clocks/1125432 raw output identities.
Canonical geometry/coherent copies/zero flags-Signal-Wf/no incoming mail and
stated controller hypotheses only; reset/vote/capture/commit excluded. No old-Q
clock-transfer theorem was silently applied. Full path/mail/barrier and whole-
period composition still required. Full cap orbit PASS all2^30 normalized Ages;
12 defect cases still show permanent Address defects across32768 typed Addresses.

ROM4.274011s/62000KiB; watch4.626157s/62832KiB sampled. Events175.615730s/
141312KiB; watch175.925145s/144640KiB sampled. Tests6PASS16.334s; watch16.689682s/
71828KiB sampled. Cap2.198926s/51020KiB; watch2.518674s/52140KiB sampled.
All jobs exit0,512/768MiB watchdogs. No GPU use/build; private native CPU build
only (compiler child RSS is not included in Python watchdog figures). All jobs
terminal; RAM within40GB. No shared source, job, historical dataset or prior
sealed source changed. MAIN_AGENT_NOTES.md absent/unedited; please reply there.

Final evidence: figs/fixed_rule/compact16_holder_candidate_evidence_v1.json.
`OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.seal_compact16_holder_candidate`
finished exit0:568 files bound, all533 prior hashes unchanged, external bank
streaming-verified. New physical/ROM identities remain separate from the frozen
execution baseline. All owned processes terminal.

Depth-two sites and physical ticks are each quartered; naive update volume falls
sixteenfold, not a measured speedup. Dense projected buffer still84.5GiB; one
canonical MEM bank would be452460544bytes. Backend/domain validation is needed.
Next reprove/combine smaller-rule instruction paths, incoming mail, barriers and
full period, then port private execution and run successive physical macrosteps.
General amplification, finite-horizon cap repair, depth3 and source fidelity
qualifications remain open. Full goal active; no shared change requested.

## Preserved milestone: dependency-directed retrieval reaches a16346-cell core

[SPARSE_RETRIEVAL.md](SPARSE_RETRIEVAL.md) documents the fixed sparse_holder ROM:
689 mutable operands get three histories/vote slots;49 own metadata operands
are regenerated from voted Address before each evaluation. All154 raw Info/Hold
fields and every controller output remain represented. Core27721->16346;
controller travel2001129064->818235377 ticks; SEND sites6478->1786.

Physical F/alphabet/radius remain unchanged. The new projected G uses fixed ROM
92e01ae6445c1bf7e125080bc2929b36fdc86ea089705f80650a2a3e9d7fa77a, independent of
initial depth. Q32768/U2^31 are still unchanged. No candidate is promoted over
the frozen execution baseline. This is no measured GPU speedup.

Complete typed symbolic own-ROM computation PASS:62010 history checks, all738
supplied operands, both evaluations/all154 outputs, Signal delivery, commit and
scratch reset. New physical path PASS12801 ordinary/392 metadata/12899 dispatch;
packet schedule PASS23711 instruction occurrences/1786 SEND sites. Six tests PASS
include depth1-3 identity/raw encoding, wrong controller retrieval/ROM/PC-output
mutations and active scalar/descriptor transitions across all five controller
copies. Depth checks are initialization only; full new-period execution and
whole-period composition/noisy validation remain open.

ROM check4.565152s/66488KiB; watch4.848755s/66116KiB sampled. Paths27.343333s/
81304KiB; watch27.985636s/88988KiB sampled. Tests6PASS8.453s; watch8.776203s/
69168KiB sampled. All exit0,512MiB watchdogs, concurrent child peaks<155MiB.
No GPU use/build. All owned jobs terminal; total RAM well below40GB.

Final evidence: figs/fixed_rule/sparse_holder_compiler_evidence_v1.json.
`OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.seal_sparse_holder_compiler`
finished exit0:533 files bound, all516 prior hashes unchanged; external bank
streaming-verified. Actual baseline/candidate identities and prospective parameter
reductions remain distinct. All owned jobs terminal.

Core plus five tail cells now fits16384 and controller paths fit2^30. These are
prospective capacities, not an implemented smaller rule. Next choose consistent
Address semantics/alphabet forQ2^14, regenerate complete self-description/ROM,
retime phases forU2^30 and recheck actual costs and closure. Existing Address-mask
helpers and zero-offset metadata queries rely onQ matching field width; merely
changing constants would be invalid. Fixed scratch capacity320 gives33 cells of
prospective core-to-tail margin; minimal allocation was slower than2^30.

Owned additions: sparse_holder_program/projected/initial, complete ROM/path
checkers, focused tests, report/evidence/sealer and archived prior STATUS. No
shared file/job/data or earlier sealed source changed. MAIN_AGENT_NOTES.md remains
absent and unedited; please reply there. No shared change requested. General
cross-level noise amplification, finite-horizon cap reliability, depth3 and
Flag2/SimBit source ambiguities remain open. Full project goal active.

## Preserved milestone: compiler candidate saves16.2268% controller travel

[LOWMASK_COMPILER.md](LOWMASK_COMPILER.md) records a separate fixed lowmask_holder
ROM candidate. Replacing2930 evaluation/output-regeneration NAND(x,x) instructions
with NAND(MASK,x), using an initialized low MEM constant, saves324718766 scheduled
controller ticks per period:2001129064 ->1676410298. Core grows27721->27722;
Q32768/U2147483648 remain necessary powers of two. No GPU speedup is asserted.
High-address constant placement is retained as a failed cost alternative.

Full physical F/alphabet/radius unchanged; projected G changes because its new
ROM is08579e057a390c9e99d5eb993525591989929419b37dfc5c52533f7a179c1fc8.
This candidate ROM is fixed independently of depth. No baseline source, program,
backend or data changed. It is not yet promoted to the execution baseline.

Complete typed symbolic own-ROM computation PASS includes all154 raw outputs,
controllers, own metadata regeneration, three histories, two evaluations and
commit/reset. New path check PASS17713 ordinary/392 metadata/17811 dispatch;
packet schedule PASS28544 instruction occurrences and6478 SEND sites.
Six tests PASS include scalar/descriptor literal controller-copy events, depth1-3
identity/complete encoding, wrong constant and omitted PC-output mutations.
Depth tests are initialization only. Full candidate period composition/execution,
successive physical macrosteps and noise validation still require work.

ROM check5.743797s/91692KiB process peak; watch6.106992s/89988KiB sampled.
Paths39.003035s/102928KiB; watch39.741337s/120500KiB sampled.
Tests6PASS11.248s; watch11.641063s/96736KiB sampled. All exit0,512MiB watchdogs;
concurrent sampled child peaks<213MiB, well below40GB task RAM. No GPU use/build.

Owned new files: lowmask_holder_program/projected/initial modules, complete ROM
and path diagnostic drivers, focused tests, report, receipts/sealer and archived
prior STATUS. MAIN_AGENT_NOTES.md absent/unedited; please reply there. No shared
change requested. All owned jobs terminal.

Final evidence: figs/fixed_rule/lowmask_holder_compiler_evidence_v1.json.
`OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.seal_lowmask_holder_compiler`
finished exit0:516 files bound, all469 prior hashes unchanged, external bank
streaming-verified. The738-word support inventory is included explicitly.
Baseline ROM identity remains separate from the candidate ROM. All jobs terminal.

Next substantial target: dependency-directed retrieval/history layout. Complete
compiled descriptor uses738 of2310 reserved input words (all49 metadata inputs
are own-cell), so much current retrieval/storage is unused. Retain complete raw
Info/Hold/controller representation and certify the reduced layout; the inventory
alone is not a smaller working construction. General noisy amplification,
finite-horizon terminal reliability, depth3 and source ambiguities remain open.
Full project goal active.

## Preserved milestone: current-rule noiseless terminal orbit checked completely

[RETIMED_BOUNDARY_DATA.md](RETIMED_BOUNDARY_DATA.md) validates ordinary finite-depth
terminal data for the current fixed retimed descriptor. The full154-output BDD
identity covers all2^31 normalized Ages, including six necessary +1-backup
head/PC pulses and wrap. Raw Age remains32bits; the proof explicitly separates
alphabet width from U. No rule, ROM, alphabet, Q/U or physical backend changed.
The existing conditional block relation composes this orbit at arbitrary finite
encoded depth; this is not a new measured nested execution or backend theorem.

Twelve separate geometry identities cover all2^32 raw Ages, arbitrary replacement
Address, arbitrary22 workspace bits and all possible local defect positions.
They reproduce the permanent single-Address-bit defect for the current rule.
All omitted raw fields are unrestricted after verified support analysis.
Noiseless termination is available; finite-horizon terminal reliability remains
open. A robust cap must not be conflated with ordinary finite-depth termination.

Proof PASS2.589026s/66548KiB process maximum; watchdog2.883052s/66392KiB sampled,
exit0. Six focused tests PASS4.998s; watchdog5.329561s/66876KiB sampled, exit0.
Both had60s/512MiB limits and ran concurrently, combined child peaks<131MiB.
Independent scalar checks cover pulse boundaries and wrap; mutations reject
frozen clocks, omitted controller pulses, neighborhood/output omissions and a
healthy-orbit-only defect argument. Exact commands are in the report and watches.
No GPU allocation/build. All owned jobs terminal; total task RAM well below40GB.

Owned additions: retimed_holder_boundary_data.py, prove_retimed_holder_boundary.py,
test_retimed_holder_boundary_data.py, report, namespaced receipts/sealer, archived
prior STATUS and this status. Shared files and earlier frozen evidence unchanged.
MAIN_AGENT_NOTES.md absent/unedited; please reply there. No shared change requested.
Read-only check found no historical third_link_initialized process; September24
artifact timestamps alone do not prove successful completion. Jobs/data untouched.

Final evidence: figs/fixed_rule/retimed_holder_boundary_data_evidence_v1.json.
`OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.seal_retimed_holder_boundary_data`
finished exit0:469 files bound, all446 prior hashes unchanged, one external bank
streaming-verified. No owned job remains running.

Next: finite-horizon boundary failure measurements or broader noisy active-colony
families, then resource optimization and depth3. General amplification/thresholds
and the Flag2/SimBit source ambiguities remain unresolved. Full goal stays active.

## Preserved milestone: actual bounded GPU replay reaches complete fresh-fault repair

The previous goal turn made progress with the conditional full-state join. This
turn adds [FRESH_GPU_REPLAY.md](FRESH_GPU_REPLAY.md): actual GPU evolution of the
saved17-colony context, old residual words and nine original full-state marks,
through complete rejoin at16989. Runtime20.957613s; explicit device bound30744698
bytes(29.3MiB), process peak682152KiB. No other GPU processes were listed before
or after the bounded probe. The larger main-agent reservation remains unused.

All168572 initial bank words match the full-ring terminal context from31 complete
parents. The17-colony window supplies more than the doubled radius-seven causal
margin through16989 ticks. First640 ticks execute full raw GPU exceptions:
2463966 full local evaluations, peak3657 exceptions. CPU/scalar-audited first five
states and the literal CPU tick128 checkpoint match completely. No Data/flag
absorption occurs during this raw phase; actual residue is retained until erased.

At640, canonical geometry permits a zero-transition flag attachment. Every one
of85786624 raw words is checked before/after;3657 actual Flag1 bits remain packed.
Empty exceptions here means representation equality, NOT recovery. The new private
early flag wrapper changes only the constructor clock guard; device transition
body/graph execution are unchanged. The full fixed rule/ROM/alphabet/Q/U are not
changed or selected by depth. No shared CUDA artifact was rebuilt or overwritten.

The next16349 physical ticks execute GPU procedures and flags under the existing
canonical zero-mail factorization. Host upper/local transitions are forbidden
during evolution. At16988 only the two measured Flag1 bits at0,1 remain; at16989
all flags vanish. All snapshots and all85786624 reconstructed raw words agree
with a separately evolved healthy GPU world. The old residual words are gone.

Independent CPU saved-state audit PASS3.847497s/416664KiB: repeats the complete
lossless attachment comparison, checks131072 geometry words and the last two
flags, and compares all5046272 final central-colony raw words to the CPU physical
reference. This is not an independent scalar evaluation of every GPU transition;
existing backend factorization/refinement premises remain explicit.

Five final tests PASS1.782s; watch2.130303s/73224KiB, exit0. They exercise nonzero
values in all18 procedure/controller/mail fields across all five raw copies,
flag inconsistency, complete exception retention, clock bounds and unchanged
device transition source. The earlier four-test source/run are preserved. New
private build watch2.108770s/31636KiB, exit0. Replay watch21.460850s/684660KiB,
exit0,180s wall/1.5GiB RAM cap. All jobs terminal; device released. Task RAM far
below40GB. Exact commands and loaded binary hashes are in receipts.

Owned additions: early GPU flag wrapper, lossless early snapshot adapter, replay,
CPU audit, focused tests, report/evidence/sealer, private build, archived prior
STATUS and this mutable status. Prior bound sources/data remain frozen. No shared
module, historical dataset, other-agent job or CUDA artifact changed.
MAIN_AGENT_NOTES.md absent/unedited; please reply there. No shared change requested.
Final index: figs/fixed_rule/retimed_holder_fresh_gpu_execution_evidence_v1.json.
Sealing command: `python -m experiments.fixed_rule.seal_retimed_holder_fresh_gpu_execution`;
terminal exit0,446 files bound, all413 prior hashes unchanged, one external full
bank verified by streaming hashing. All owned jobs terminal.

Next broaden the experimentally checked fault family or address a remaining
construction obligation such as robust caps or resource optimization; do not
promote this selected two-burst execution to an amplification/threshold theorem.
General noise robustness, finite-depth caps, depth3, Q/U optimization and the
Flag2/SimBit source ambiguities remain open. The full goal remains active.

## Preserved milestone: conditional complete repair of the selected fresh faults

The previous goal turn made progress by restoring geometry at16989 but left
procedure state open. [FRESH_FULL_REPAIR.md](FRESH_FULL_REPAIR.md) now joins the
complete state to the fault-free trajectory at16989 (local time8589951581), under
the existing endpoint/refinement premises. All controllers, encoded Info, Data,
packets, Signals, geometry and raw copies are included. The three OLD nonMEM
residual words were physically erased by the selected fresh sequence and are
included in this complete-state equality. No general repeated-noise claim.

New complete-descriptor identities check90 procedure outputs: geometry can affect
nonmail fields only by Flag1/Address-change clearing, and mail by Flag1 clearing.
Signal has the same Address-change clearing; Wf remains0. A second identity
checks101 zero procedure/Signal/Wf outputs with arbitrary geometry and metadata.
A structural check confirms all154 outputs ignore686 neighbor static inputs;
only own metadata is needed for the shared-Address comparison. First join/source
preserved; acceptedv2 explicitly binds this neighbor-metadata premise, with an
identical diagnostic NPZ. No actual state or transition was changed.

The actual literal128 entry agrees with its healthy reference in every field
except geometry and corresponding ROM, over the complete fault cone. The join
checks5718 old-or-new wrong-Address cases and108642 logical operands: their whole
raw neighborhoods have zero healthy Data/controller/mail/Signals. The earliest
canonical input Age found is607. At other sites, the clearing identity preserves
all procedures because own Address is stable and healthy mail is zero.

A complete healthy physical event execution checks3112960 procedure/Signal words
at five checkpoints. An independent16988-transition scalar head trace includes
actual FETCH->WRITE at9913 (value2^64-3,destination9905); first Data write65349.
Before16989 all healthy Data remains unchanged after reset, mail is zero, and
exactly one head/controller per colony exists. These facts apply across arbitrary
Info contents. After Address restores, only zero mail could be cleared by Flag1.
When Flag1 clears at16989, projected ROM and every raw field agree completely.
The healthy reference is never installed into an evolving damaged world.

This is conditional descriptor-semantics composition, not a new literal noisy
suffix/full-ring GPU run or proof-assistant theorem. It inherits the geometry
projection's backend coverage limitations (boundary/random scalar checks plus
literal prefix); no independent scalar audit of every projected output is added.
The selected two-burst sequence is covered, not arbitrary renewed faults.

Accepted effects_v1 PASS1.224755s/57164KiB process; fresh_full_repair_v2
PASS9.325502s/288920KiB process. Seven tests PASS1.997s; watch2.388266s/64108KiB,
terminal exit0. All watchdogs terminal zero, at most1GiB caps. Exact commands in
watches. No GPU use, rule/ROM/width/Q/U/neighborhood change, shared source/job/
CUDA artifact/historical dataset modification. Task RAM remained below40GB.

Owned additions: geometry/procedure certifier, full-state join, focused tests,
report/evidence/sealer, archived prior STATUS and this mutable status. Prior
bound files remain frozen. MAIN_AGENT_NOTES.md absent/unedited; please reply there.
No shared change requested. Final index:
figs/fixed_rule/retimed_holder_fresh_full_repair_evidence_v1.json.
Sealing command: `python -m experiments.fixed_rule.seal_retimed_holder_fresh_full_repair`;
terminal exit0,413 files bound, all392 prior hashes unchanged, one external full
bank verified by streaming hashing. All owned jobs terminal.

Next strengthen the selected conditional chain with a separately executed noisy
suffix or expand the verified noisy entry family; avoid turning one favorable
fault sequence into a general amplification claim. General noise thresholds,
robust finite-depth caps, depth3, Q/U optimization and Flag2/SimBit source-fidelity
issues remain open. The full fixed-rule self-simulation goal remains active.

## Preserved milestone: fresh-damage geometry restores at tick16989

The previous goal turn made progress by auditing actual-residue activation and
paired coupling, leaving159 fresh-damage words. This turn adds
[FRESH_GEOMETRY_RECOVERY.md](FRESH_GEOMETRY_RECOVERY.md): complete literal physical
execution through128 ticks, followed by an explicitly diagnostic geometry
projection and exact Flag1 recurrence. Address is canonical by640, and all Flag1
clears at16989. Uniform Age/zero Flag2/zero Wf persist. This is GEOMETRY restoration,
not complete controller/Data/Info repair. Full procedure state after128 is open.

The unchanged full G literal run uses the actual saved endpoint, residuals and
all nine saved marks; its complete first five states match the prior scalar audit.
At128 it retains six wrong Addresses and765 Flag1 sites, with no procedure/Data
differences.106129408 retained native raw outputs were evaluated. The suffix's
full outputs after5 have not all been independently scalar checked.

New complete-descriptor certificate proves four geometry outputs independent of
all computation fields for common oldAge0..32767 and zero inputWf; all ten output
Wf are zero and the common clock is preserved. The saved marks are checked to
preserve these hypotheses. The independent NumPy maintenance projection tracks
geometry only:136416 scalar boundary/random words agree over1024 ticks, plus6984
literal prefix geometry words. Not every vector output has a scalar audit.
Radius-five geometry locality embeds the periodic diagnostic Q-cell ring into
the full geometry trajectory before influence from repeated islands can meet.

The six wrong Addresses move right in two triples and disappear at the colony
boundary: five remain at603, three at604/605, none by640. At1024 Flag1 is exactly
[27889,31929],4041 sites. The canonical Flag1 interval recurrence is
[max(0,l-3),r-2] for length>=3; shorter intervals disappear. An exact bitset
execution checks that identity for15965 ticks, with688128 additional vector
geometry words compared at seven checkpoints. The last two flags vanish at16989.
No untracked computation state is installed or assumed repaired by this projection.

Accepted receipts/process metrics: fresh_geometry_recovery_128_v1 PASS8.801063s/
86736KiB; early_geometry_projection_v1 PASS1.119248s/58292KiB;
fresh_geometry_projection_v1 PASS19.420561s/73244KiB; geometry_flags_v1
PASS1.099152s/56384KiB. Nine final tests PASS1.921s; watch2.253967s/75800KiB,
terminal exit0. All watches terminal zero, at most1GiB caps, no GPU use. Exact
commands are in watches; task RAM stayed far below40GB. No failed new runs.

Owned additions: literal probe, geometry projection/certifier, projection audit,
Flag1 finisher, two test modules, report/evidence/sealer, archived prior STATUS
and this mutable status. Earlier bound files remain frozen. No rule/ROM/width/
neighborhood/Q/U, shared module, CUDA artifact, job or historical dataset changed.
MAIN_AGENT_NOTES.md absent/unedited; please reply there. No shared source change
requested. Final index:
figs/fixed_rule/retimed_holder_fresh_geometry_evidence_v1.json.
Sealing command: `python -m experiments.fixed_rule.seal_retimed_holder_fresh_geometry`;
terminal exit0,392 files bound, all363 prior hashes unchanged, one full external
bank verified by streaming hashing. All owned jobs are terminal.

Next establish the complete procedure-state link from literal128 to the geometry
restoration interface16989. Either execute the full rule or check an applicable
refinement; restoring geometry alone does not validate controllers, packets,
encoded Info or the next macrostep. General amplification/thresholds, robust
finite caps, depth3, Q/U optimization and Flag2/SimBit issues remain open.
The full goal remains active.

## Preserved milestone: actual residual enters a controller under fresh geometry faults

The previous goal turn made progress with the stronger residual domain and an
artificial one-bit Address counterexample. This turn adds
[RESIDUAL_REACTIVATION.md](RESIDUAL_REACTIVATION.md), using the actual period-three
repaired endpoint at4U=8589934592. Nine identical paired full-state marks inject
a READ_A head and change nearby Address votes. At tick4 the actual retained
word2418452793257099264 enters one raw s4_value controller copy. At tick5 the
actual and residue-free faulted configurations completely couple, but still
differ from the fault-free third trajectory by159 raw words. Old-residue erasure
is NOT complete repair of fresh damage; no decoded upper failure is asserted.

Initial complete raw state is reconstructed with storage.View and independently
compared with BankImage plus all recorded residual words. Every retained output
of all three physical trajectories is independently scalar/native checked:
242550 raw words each. The147-site window shrinks by radius7 per side each tick;
the final77 sites contain the complete initial-difference cone, proving complete
paired ring equality at tick5. Identification with the intended full lower ring
uses the preceding conditional full-ring endpoint relation. No host upper step
or replacement healthy state drives actual physical evolution.

Two distinguishing tests remove either the three controller marks or the six
geometry marks; neither then produces the controller read. Removing geometry
leaves the15 old Data differences. The accepted witness saves all nine complete
replacement records, times, positions and all immutable chronological snapshots.

Preserved failures: auditv1 reporting selector mistakenly matched signal as a
controller replica and raised IndexError. Auditv2 passed physical scalar checks
but rejected the pilot's saved tick1/tick2 snapshots: they were aliases mutated
by the following fault groups. Exact failed sources/logs/watches are preserved;
acceptedv3 accounts explicitly for that aliasing and uses copied checkpoints.
A new snapshot regression prevents recurrence. Pilot printed counts were correct;
its first two saved states must NOT be treated as unmodified chronological states.

Accepted audit residual_reactivation_audit_v3 PASS10.783057s/454532KiB process,
1GiB cap, terminal exit0. Five final tests PASS1.828s; watch2.107883s/66684KiB,
512MiB cap, terminal exit0. Exact commands are in watches. No GPU allocation;
task RAM stayed far below40GB. Descriptor/ROM/alphabet/radius/Q/U are unchanged.

Owned additions: pilot, complete audit, focused tests, report, evidence/sealer,
archived prior STATUS and this mutable STATUS. Earlier bound files are frozen.
No shared source, CUDA artifact, historical dataset or external job was changed.
MAIN_AGENT_NOTES.md remains absent/unedited; please reply there. No shared source
interface change requested. Final index:
figs/fixed_rule/retimed_holder_residual_reactivation_evidence_v1.json.
Sealing command: `python -m experiments.fixed_rule.seal_retimed_holder_residual_reactivation`;
terminal exit0,363 files bound, all336 prior hashes unchanged, one full external
bank verified with streaming hashing. All owned jobs are terminal.

Next follow the common state carrying159 fresh-damage differences to a verified
reset or repair interface. Complete paired coupling only removes dependence on
the old residue; it does not supply new-fault correction. Retain geometry/residue
interactions in broader noisy domains. General amplification/thresholds, robust
finite caps, depth3, Q/U optimization and Flag2/SimBit issues remain open.
The full goal remains active.

## Preserved milestone: residual separation with arbitrary clocks; Address counterexample

The previous goal turn made progress by completing the conditional full-ring
repair join. This turn adds [RESIDUAL_NOISE_DOMAIN.md](RESIDUAL_NOISE_DOMAIN.md).
The three selected nonMEM Data words are independent of every other output with
canonical Address/fixed ROM, even with arbitrary independent32-bit clocks,
arbitrary controllers/mail/flags/Wf/Signals, and initially incoherent Data copies.
All15 selected copies become their five-input bitwise majority. The complete
3234-output descriptor check covers all21 possibly affected sites;3219 outputs
are independent. Uniform clock and Data coherence are no longer needed premises.

This relation survives any sequence of identical full-state replacements that
preserve Address in the paired worlds, even at residual holders. It does NOT
prove repair of the common noisy controller/clock background. The source rule,
ROM, alphabet, neighborhood and Q/U are unchanged. Canonical Address remains an
explicit necessary premise; arbitrary physical noise has not been handled.

Literal scalar/native probes use the actual three recorded residual values vs
zero with otherwise random typed complete fields and clocks. Three seeds each
execute12 physical ticks with4 fresh identical Address-preserving replacements
per tick:144 total marks,3193344 retained native raw outputs,99792 independent
scalar raw comparisons. All cases retain15 Data differences and no other
word differences. No evolving lower transition is replaced by a host upper step.

A separate explicit counterexample uses residual value1 (NOT an observed even
residue). Six identical replacements at offsets-5,-4,-3,3,4,5 change the target's
voted Address from30960 to3, with Flag1=0 and newAge=CAPTURE_AGE. Its surviving
Data low bit then gives Signal4 versus0. Complete target scalar/native outputs
agree. This rejects dropping Address from the residual-separation domain; it does
not show eventual decoded failure or activation of the actual even residues.

Accepted CPU receipts: residual_noise_domain_v1 PASS2.797297s/72520KiB process;
residual_noise_audit_v1 PASS6.797511s/69244KiB process. Six focused tests PASS4.453s;
watch4.746447s/95152KiB sampled. All watches terminal exit0,1GiB cap, no GPU use.
Exact commands are in watchdog receipts. Task memory stayed far below40GB.

Owned additions: residual-domain certifier, scalar/native audit, focused tests,
report, evidence/sealer, archived prior STATUS and this status. All earlier bound
sources/artifacts/reports remain frozen. No shared source, job, historical dataset
or CUDA artifact changed. MAIN_AGENT_NOTES.md absent/unedited; please reply there.
No shared interface change requested. Final index:
figs/fixed_rule/retimed_holder_residual_noise_evidence_v1.json.
Sealing command: `python -m experiments.fixed_rule.seal_retimed_holder_residual_noise`;
terminal exit0,336 files bound, all320 prior hashes unchanged, one full external
bank verified by streaming hashing. All owned jobs are terminal.

Next account for actual fresh geometry damage in the full noisy entry relation,
including interactions with retained Data. Alternatives are to retain and bound
those interactions, or establish physical erasure via a revalidated fixed rule.
Neither follows from the new Address-preserving domain. General amplification,
thresholds, robust finite caps, depth3, Q/U optimization and the source Flag2/
SimBit ambiguities remain open. The full goal remains active.

## Preserved milestone: selected full-ring physical repair conditionally joined

[FULL_RING_REPAIR.md](FULL_RING_REPAIR.md) extends the selected burst's full-ring
commit relation through actual reset, physical metadata normalization and three
subsequent lower work periods. Complete decoded upper state rejoins after TWO
further periods; complete banks/Signals/controllers/flags after THREE, excluding
three retained nonMEM Data words (15 raw copies over seven physical sites).
This is conditional descriptor-semantics composition with the previous physical
window audits and noiseless refinements as premises, not a new literal full-ring
GPU run or proof-assistant theorem. The full project goal remains active.

The new normalization certificate checks all 128 prefix instructions: all 49
encoded metadata words are overwritten, 85 operand reads remain paired, and
mutable Info is preserved. Normalization completes at Age10487886, before the
first SEND birth at27674808. Early cut/image/tail checks cover reset and the whole
prefix; zero mail follows from the valid reset frame, physical instruction
refinements and no SEND. No fault during this prefix is assumed. The malformed
record is physically processed; diagnostic normalization never replaces it.

The new join checks two complete native reset comparisons of20185088 raw words
each across the four-colony patch. Its full E_loc comparison bank is2599419904
bytes. Only16 encoded metadata Data words initially distinguish the paired reset
images; all105 represented mutable/controller words are preserved. The physical
prefix couples these entries. The inert-Data identity retains all three overlay
words under restored canonical geometry/fixed ROM. Subsequent full-ring periods
then follow from the existing complete noiseless and terminal identities.

Full upper diagnostic steps match the previously independent scalar/native
upper trajectory and actual window interiors of59/45/31 colonies. After two
periods660 historical bank words still differ across full colonies9559..9573,
verified against the physical window. After three periods equal full parents
imply equal terminal banks globally. This does not erase the three nonMEM words.

Accepted CPU receipts: normalization_prefix_v1 PASS6.264069s/123588KiB process;
full_ring_repair_v1 PASS13.672000s/3984764KiB process. The latter watchdog reports
13.939828s/3986612KiB sampled peak, exit0, under its8GiB cap. Seven focused tests
PASS1.574s; watch2.198869s/74468KiB, exit0. All jobs terminal; no GPU allocation.
Task RAM remained below the user's40GB allowance. Exact commands are in watches.

Owned additions: normalization certifier, full-ring repair join, two test modules,
report, evidence/sealer, archived prior STATUS and this mutable STATUS. Prior
bound sources/reports/receipts remain frozen. Descriptor/ROM/state width/Q/U are
unchanged; no shared source, historical dataset, job or CUDA artifact changed.
MAIN_AGENT_NOTES.md remains absent/unedited; please use it for replies. No shared
interface change requested. Final index:
figs/fixed_rule/retimed_holder_full_ring_repair_evidence_v1.json.
Sealing command: `python -m experiments.fixed_rule.seal_retimed_holder_full_ring_repair`;
terminal exit0,320 files bound, all298 prior hashes unchanged, one external full
bank verified with streaming hashing. All owned jobs terminal.

Next establish a domain for repeated correction with fresh faults, distinguish
that from this selected one-burst trajectory, and pursue Q/U cost reductions with
explicit equivalence checks. General damage amplification/thresholds, robust
finite-depth caps, depth three and Flag2/SimBit source-fidelity issues remain open.

## Preserved milestone: selected noisy commit conditionally embedded in the full lower ring

The previous goal turn made progress with the prefix/context certificate. This
turn adds [NOISY_COMMIT_EMBEDDING.md](NOISY_COMMIT_EMBEDDING.md), closing the selected
faulty-commit boundary gap through a conditional complete-descriptor gluing proof.
It joins the actual 73-colony trajectory to the full 32768-colony lower ring
(1073741824 physical cells), with the same 8404 unfiltered marks and fixed G.
Only upper position 9566 commits wrong all-zero Info: 26 raw /12 mutable word
differences, including controller state. This is not a new literal full-ring GPU
run or a proof-assistant theorem. Existing noiseless refinements and trajectory
audits remain explicit premises. Subsequent full-ring repair is NOT yet joined.

New late_confinement checks 2508 nonmail raw outputs per bounded clock interval,
with arbitrary Flag1, arbitrary shared physical Signals, arbitrary multiple core
controllers and empty local ordinary tails. All 880 mail outputs are explicitly
conditional on zero output mail in BOTH trajectories; input mail must also be 0.
New late_procedure_image proves 50 nonmail replica outputs coherent per interval,
with arbitrary simultaneous controllers and all canonical Addresses. Flag2/Wf stay
zero, geometry stays canonical and shared Signals stay shared. No one-head premise.

Tail endpoints are checked against the actual first/last markers. The separate
empty_tail_interior identity checks 45 zero controller copies when only the three
logical neighbor controller records and target first marker are zero. Other raw
stencil controllers, metadata, flags and mail stay arbitrary. This covers 5045
interior tail sites plus two endpoints without assuming the raw stencil empty.
At post-burst tick 34 only colony 36 has changed primary procedures or an occupied
tail. Signal equality, fixed metadata, geometry, zero mail/F2/Wf and ordinary tails
are checked across the complete state. The audited zero-mail dynamics supply the
remaining trajectory premise. Differences remain in logical colonies 36/37, hence
raw support [36Q-2,38Q+2) through commit. Ordinary locality encloses the first 34
ticks. Collars at 35Q/39Q stay equal to the noiseless window and full noiseless
ring, so the four-colony patch plus full healthy exterior forms a valid trajectory
of G. The unaffected exterior follows from this construction; it is not assumed.

Accepted receipts: late_confinement_v1 3.633350 s /66820 KiB;
late_procedure_image_v1 1.506681 s /61900 KiB; empty_tail_interior_v1
1.334952 s /57740 KiB; noisy_commit_embedding_v2 28.233728 s /1006796 KiB
process RSS. The final 13 tests PASS in 5.069 s; watch 5.372200 s /82556 KiB
sampled RSS. All watches terminal zero, limits at most 2 GiB, no GPU allocations.
The 40 GB task RAM ceiling was respected. The first join/source is retained;
the second explicitly binds the stronger interior-tail premise. Both diagnostic
NPZ hashes are identical. No physical state or rule changed.

Owned additions: four certifier/join modules, four test modules, report, evidence,
sealing script and this status; all under fixed_rule namespaces. Exact commands
are in watchdog receipts. Descriptor, ROM, alphabet, Q and U are unchanged.
No shared source, other-agent job, historical data or CUDA artifact changed.
MAIN_AGENT_NOTES.md is absent/unedited; please reply there. No shared interface
change requested. Final index:
figs/fixed_rule/retimed_holder_commit_embedding_evidence_v1.json.
Sealing command: `python -m experiments.fixed_rule.seal_retimed_holder_commit_embedding`;
terminal exit 0, 298 files bound, all 260 prior hashes unchanged and one
full external bank verified with streaming hashing. All owned jobs terminal.

Next extend the full-ring relation through the actual reset and stage-zero
metadata normalization before the first SEND, then join existing later-period
identities and full upper repair. Do not silently replace malformed Info with a
valid entry. Retain the three nonMEM words and transient controller state.
General noise amplification/thresholds, robust caps, Q/U optimization, depth three
and Flag2/SimBit source-fidelity issues remain open. The full goal stays active.

## Preserved milestone: conditional complete prefix embedding and finite noisy cone

The previous goal turn made progress by closing and sealing the 73-colony audit
chain. This turn adds [PREFIX_EMBEDDING.md](PREFIX_EMBEDDING.md): a conditional
source-offset proof for the actual timed ROM, complete inherited entry matching,
and a radius-seven continuation to a saved noisy physical checkpoint.

All 6478 packet deliveries and all timed memory events stay within seven initial
colony offsets. Complete controller state is included; raw replicas require an
eight-colony halo. Zero INITIAL Signals are an explicit premise. Under the
existing noiseless physical refinements, 57 complete raw colonies (8..64) match
the full lower ring at burst time. The witness checks 723868 inherited bank words,
all zero initial controller/flag/Signal state, and 5046272 full upper raw words.

Ordinary physical locality with the same 8404 translated marks then gives complete
raw agreement through burst/recovery and 116418 ticks after burst start. At that
saved checkpoint, colonies33..39 /physical interval[1077070,1314994) still match.
Both candidate cuts35Q and39Q and their needed raw input collars lie inside.
All 73 saved heads are inside ROM, all outside-ROM controller words and mail zero.
Signals are zero in the central region, but six edge colonies0,1,2,70,71,72 retain
30 nonzero raw Signal words. This is a local same-time collar check, NOT a global
zero-Signal assertion or a persistent cut proof. The ordinary cone is empty before
commit. No final noisy full-Q lower commit/repair claim has been added.

Accepted CPU receipts: prefix_dependence_v2 (4.311976s,123352KiB process RSS),
prefix_embedding_v3 (4.590282s,2466208KiB,4GiB watch), embedding_cones_v2
(2.554205s,438948KiB). Eight final tests PASS in1.491s; watch2.090091s,
74976KiB sampled RSS. All watches terminal zero, all owned jobs terminal.
The first dependency result omitted its needed Signal restriction: preserved and
superseded, despite its numeric passing calculation. A scalar retained-Signal
counterexample now tests that distinction. Two 2GiB entry watches terminated on
RSS before the successful4GiB run; first whole-file hashing was replaced with
streaming hashing. A rejected global-Signal collar check is preserved; accepted
local checks explicitly retain the nonzero edges. No data/rule was changed to pass.

Owned new sources: certify_retimed_holder_prefix_dependence.py,
audit_retimed_holder_prefix_embedding.py, certify_retimed_holder_embedding_cones.py,
two focused test modules, report, evidence and its sealing script. Exact commands
are in the watchdog receipts. Rule/ROM/width/Q/U unchanged; no GPU allocation,
shared files/jobs/artifacts changed. Prior evidence remains frozen. Full goal
active; no shared interface change requested. MAIN_AGENT_NOTES.md absent/unedited;
please use that file for replies. Total task RAM stayed below40GB.

Next prove persistent local collars through commit, with the full-ring exterior
accounted for, and confine the actual noise influence through the earlier interval.
The seven-colony agreement at one time cannot imply an unaffected exterior.
Then join the noisy commit to later physical periods. General amplification,
thresholds, robust caps, Q/U optimization, depth3 and Flag2/SimBit issues remain open.
Final index: figs/fixed_rule/retimed_holder_prefix_embedding_evidence_v1.json.
Sealing command: `python -m experiments.fixed_rule.seal_retimed_holder_prefix_embedding`;
terminal exit0, 260 files bound, all211 prior hashes unchanged, one full external
bank verified with streaming hashing. No owned jobs remain live.

## Preserved milestone: wider repair audit chain complete; conditional cut certificate

[WIDE_CONTEXTUAL_REPAIR.md](WIDE_CONTEXTUAL_REPAIR.md) closes the outstanding
73-colony audit chain. Recovery audit v2 PASS: all 16384 ticks, 7241728 complete
scalar procedure outputs (no duplicate neighborhoods in this run), 9569792 full
native output states /1473747968 raw words, all saved observations/final state.
First extra head enters colony 37 at tick1775; flags clear at15453. Runtime
1168.662948 s,6786380 KiB process /6788500 KiB sampled RSS. Watch terminal code0.
The previous 900-second timeout stays preserved as incomplete. All jobs terminal.

The actual noisy commit and three later lower periods remain unchanged. Only
colony37 initially commits a wrong all-zero record (12 mutable differences).
After two subsequent periods all decoded upper states match the healthy window;
after three all complete banks/Signals match, with three inert nonMEM words
explicitly retained. Central17 complete decoded raw states match the full upper
colony at every stage. Commit trace audit, physical normalization/endpoint audit,
literal valid-entry reset and upper-alignment/history comparison all pass.
The full-Q LOWER physical boundary relation is still unproved; no threshold,
amplification or complete physical erasure claim. Full goal remains active.

[COLONY_CUT.md](COLONY_CUT.md) adds a conditional one-step certificate of the
same complete descriptor, not a different rule. Under canonical/common geometry,
fixed ROM, coherent procedure copies, zero mail/flags/Wf/Signals and controllers
zero outside ROM, each output depends only on its logical owner's colony.
3388 raw outputs,990 controller outputs,110 Signal bits checked for every legal
Age; certificate2.382273s /69224KiB. Replica ownership is explicit at boundaries.
Inside-ROM controller count/phase/registers and all Data values are arbitrary.
The hypotheses are NOT asserted invariant; no noisy global cut proof follows yet.

Five tests PASS in3.206s: full descriptor, cross-boundary mutant rejection,
rejected missing mail/controller hypotheses, exhaustive small-operand bit/carry/
shift abstraction checks. Full scalar/native counterexamples show an outside-ROM
tail head entering its neighbor with PC42 and a crossing packet writing Data85.
The first Signal checker used whole-word dependencies and falsely retained a
low-bit influence on another bit. Its source/log/watch and a distinguishing
scalar/native probe are preserved. Corrected per-bit analysis changes no rule.

Owned additions this turn: colony_cut certificate, symbolic_bits helper,
colony_cut tests, concrete counterexample driver, two reports and evidence.
No previous bound sources/reports were changed. New final index:
figs/fixed_rule/retimed_holder_wide_repair_evidence_v1.json. The earlier pending
index/report remain frozen and are superseded by this final selected-experiment
chain, not rewritten. Current STATUS remains mutable; prior status archived as
STATUS_BEFORE_VERIFIED_WIDE_REPAIR_20260927.md. Gray's specialized ProgramBit
projection and Gacs9.2–9.3 modified self-rule remain the construction basis;
this conditional cut is a candidate-rule certificate, not a claimed paper theorem.

Final sealing command: `python -m experiments.fixed_rule.seal_retimed_holder_wide_repair`.
Terminal exit 0: 211 files bound, all 186 prior hashes unchanged. The new owned
sealing script checks accepted receipt source hashes, terminal watches and final
recovery artifact links, preserving the rejected checker and timed-out audit.
It exclusively creates the index and does not rerun physical evolution.

Next evaluate enclosing collars, for example cuts35Q and39Q around affected
colonies36/37. Prove matching full-ring initial collar states, verify the cut's
local hypotheses through the relevant intervals, and justify the preceding
noiseless physical prefix. The correct upper halo alone cannot supply those
facts. Retain geometry-corrupting burst behavior and all nonMEM Data. General
amplification/thresholds, robust finite caps, Q/U optimization, depth3 and the
Flag2/SimBit fidelity issues remain open. MAIN_AGENT_NOTES.md absent/unedited;
no shared change requested. No shared source/job/CUDA artifact/dataset changed,
substantial GPU reservation unused, RAM stayed below the user's40GB limit.

## Preserved milestone: compiled physical events and audited wider burst

[COMPILED_EVENTS_AND_WIDE_BURST.md](COMPILED_EVENTS_AND_WIDE_BURST.md) records
an unchanged-rule compiled CPU scheduler and the actual 73-colony lower burst.
The complete old noisy suffix now takes 68.831488 s versus 547.916526 s, matching
all six complete checkpoints and all 210578 event intervals. It calls the same
full native F evaluator and retains every procedure/nonMEM word; no depth case,
upper interpreter or ROM change. Five tests pass in 10.224 s. Long comparison
RSS 1176984 KiB process /1179680 KiB sampled; all private CPU builds.

The wider physical GPU burst uses complete inherited banks for upper positions
9529–9601, center36 -> upper9565. All central17 complete gathered input halos
verified. Same 8404 unfiltered full-state marks over32ticks +2quiet. Endpoint
local time1232619462, absolute2647030067069732806:118sites/189rawwords differ in
colony36, including99Flag1, five primary Data defects and two extra heads.
GPU run29.217253s /66034424 explicit device bytes (<64MiB),508212KiB processRSS.
Independent audit31.859397s /353476KiB:2276300native outputs,350550200rawwords,
596scalar outputs; every34tick complete exception set matches.

Wide/narrow saved-state comparison passes: inherited banks/noise identical;
every complete exception set identical after28Q translation; central three old
banks/controllers/counts/Signals equal at every saved tick. Other14 background
banks already differ, so wider continuation must retain its own actual state.
No larger noisy commit/upper repair asserted. All jobs terminal return0; no
shared job/source/artifact changed. GPU was idle before bounded private run;
substantial reservation unused. Historical third-link process absent on check,
without a historical completion claim. MAIN_AGENT_NOTES.md absent/unedited.

Owned additions: compiled_events.py/.cc/test and full-suffix comparison driver;
wide_burst driver/auditor/saved-state comparator; report/private artifacts.
wide_recovery.py is prepared but NOT RUN. Exact commands/results in report and
receipts. Index:figs/fixed_rule/retimed_holder_compiled_wide_burst_evidence_v1.json.
Prior STATUS archived as STATUS_BEFORE_COMPILED_WIDE_BURST_20260927.md.

Next run actual wider recovery through flags/head transport, then the compiled
suffix through commit/reset, preserving complete banks and nonMEM Data. The old
scalar recovery auditor hard-codes crossing colony9: create a new owned adapter
using37 and do not silently reuse that diagnostic. Continue wider lower periods
from their actual endpoint and use the upper halo only after establishing lower
transfer. Full goal active; amplification/thresholds, robust caps, Q/U costs,
depth3 and source-fidelity questions remain open. No shared change requested.

## Preserved milestone: full upper repair survives embedding; window boundary gap measured

[UPPER_BOUNDARY_EMBEDDING.md](UPPER_BOUNDARY_EMBEDDING.md) checks the measured
erroneous decoded record in the complete saved 32768-cell upper colony. Native G
and scalar checks show one bad site (9566), then one, then none after two steps.
The old periodic 17-cell trajectory differs from the corresponding full-colony
restriction at 6, 12, then all 17 cells. Repair agrees, absolute states do not.
This is a diagnostic upper embedding, not physical lower transfer evidence.

A 73-cell window supplies a 28-cell halo on each side of the central 17 for
four radius-seven upper steps. Both actual and healthy conditional upper
trajectories agree with the full colony in safe interiors of 59/45/31/17 cells,
including every raw controller field. This sufficient halo changes experiment
colony count, not Q/U, alphabet, rule, ROM or depth hardware. It does not bound
the physical lower burst cone by seven colonies.

New CPU-only embedding check: 7.542955 s, 602168 KiB process /602544 KiB sampled
RSS; 229376 full native output states and 143 complete scalar outputs.
Halo check: 2.843270 s, 189168 KiB process /185076 KiB sampled RSS; 102 complete
scalar outputs. Both terminal with return code zero, <=2 GiB watchdog limits.
Owned additions: audit_retimed_holder_upper_embedding.py,
certify_retimed_holder_upper_halo.py, report and private evidence.
Index: figs/fixed_rule/retimed_holder_upper_embedding_evidence_v1.json.
Prior STATUS archived as STATUS_BEFORE_UPPER_BOUNDARY_EMBEDDING_20260927.md.
No shared files/jobs or prior evidence changed; no GPU allocation this turn.
MAIN_AGENT_NOTES.md remains absent/unedited; no shared change requested.

Next execute/certify the lower transfer in this wider context. Preserve actual
inherited banks, every controller and the three nonMEM words through the noisy
commit and subsequent lower periods. The existing interacting-head CPU suffix
is the likely cost bottleneck; a private CUDA executor checked against its
saved event trace can improve repeatability. Main agent still owns substantial
GPU scheduling. Upper defect insertion is diagnostic only and must not be
reported as the missing larger lower execution. Full goal remains active.

## Preserved milestone: executed contextual upper repair and history refresh

[CONTEXTUAL_UPPER_REPAIR.md](CONTEXTUAL_UPPER_REPAIR.md) continues the actual
noisy 17-colony endpoint through three more lower periods with unchanged G.
Decoded upper cells differ from the matched unfaulted window only at colony 9
after one period, nowhere after two. After two periods 660 bank words retain
old faulty histories; after three every complete bank word and Signal matches
the unfaulted terminal reference. Three proven inert nonMEM words persist at
colony-8 addresses 30960–30962 (15 raw fields at seven physical sites).
This is actual lower-rule execution, not error insertion into an upper fixture.
Periodic 17-colony boundary scope remains; no full-Q noisy-ring/threshold claim.

New inert-data certificate checks all 3234 complete raw outputs in full causal
support for every legal Age. Fifteen Data copies remain unchanged; all other
outputs are independent, with arbitrary raw controllers/mail/flags/Signals/Wf.
Canonical geometry, common legal Age and fixed ROM are essential. Four proof
and four storage/native-boundary tests pass (3.210 s /2.069 s). Two failed
selector-harness versions are preserved; no physical counterexample was found.

Actual malformed Info is uploaded unchanged; no host normalization occurs.
Physical stage0 normalization couples to a normalized twin by Age 10487886,
verified in all 85786624 raw words. The twin has an independently verified
literal global reset preimage in E plus the retained Data. Existing conditional
macrostep/terminal results therefore apply after this actual prefix coupling.
Retained Data stays explicitly represented; no reference state is installed.

GPU run 2: 51.693753 s; run 3: 75.496703 s; explicit device bound 44344850 bytes,
run 3 process RSS 876452 KiB. Independent native/scalar normalization audit covers
2266 trace intervals, 75582 scalar candidate outputs /48781 distinct inputs.
All complete terminal banks/controllers/Signals/flags match the diagnostic
identity: audit 2 checks 257359872 raw words in 32.423913 s; audit 3 checks 343146496
in 33.349412 s. Audit 3 process RSS 1186284 KiB. Reset-entry check 10.539936 s.
All accepted jobs terminal, return code 0; watchdog limits <=3 GiB, below 40 GB.
No shared files, kernels, other jobs or historical artifacts changed.

Owned additions: inert_storage.py; inert_data proof; two four-test modules;
contextual_next_periods driver/auditor; contextual_reset_entry certificate;
contextual_history_refresh auditor; report and private artifacts. Exact paths,
commands, domains and preserved failures are in the report/evidence receipts.
Index: figs/fixed_rule/retimed_holder_contextual_upper_repair_evidence_v1.json.
Prior status: STATUS_BEFORE_CONTEXTUAL_UPPER_REPAIR_20260927.md.
MAIN_AGENT_NOTES.md remains absent and unedited; substantial GPU reservation
unused; no shared dependency request.

Next extend the contextual trajectory to a complete upper colony with a checked
embedding/boundary argument or a larger physical run. The retained-Data law
cannot be used unchanged if fresh faults destroy its geometry hypotheses.
Optimize Q/U and repeated-run cost without changing the rule with depth.
Full goal active: complete-colony depth-two noise, general amplification,
thresholds, robust finite-depth caps, depth three and the existing Flag2/SimBit
source-fidelity questions remain open.

## Preserved milestone: verified contextual noisy commit and reset

[CONTEXTUAL_MACROSTEP.md](CONTEXTUAL_MACROSTEP.md) continues the exact 17-colony
recovery state through U and U+1 in one global physical ring. Only colony 9
commits a wrong decoded successor: all-zero Info, 26 raw F /12 mutable G word
differences, including the actual upper WRITE controller at position 9566.
All other colonies decode correctly. At U+1 every colony has one head at 0 /PC0.
Three nonMEM Data words in colony 8 at 30960–30962 survive and remain stored.
This is a contextual window result, not yet upper repair or a full noisy Q-ring.

New global_events.py uses the unchanged full native physical evaluator and
actual global boundary copies, preserves all Q Data/controller words, and
executes complete global commit/reset outputs. Guarded transport emits a full
event trace. Five executor tests pass in 7.473 s. Four independent audit guard /
complete-input memoization tests pass in 3.599 s. No previous implementation
or evidence source changed; no GPU allocation or shared change.

Physical run: 914847803 ticks, 210578 trace intervals, 100444 literal ticks,
792263710 transport ticks, 122483647 quiet ticks, two bulk steps; 6231583 full
native local outputs. Completes in 547.916526 s; sampled RSS 1585344 KiB.
Healthy heads halt at 2022020768, matching the prior noiseless phase deadline,
with 2979232 ticks of active-window margin in this run.

Independent audit passes all events/guards and every saved checkpoint:
5117471 scalar core candidates, 1405940 distinct complete-neighborhood scalar
evaluations, 1114112 complete native clock outputs /171573248 raw words,
470 scalar full-G probes. Completes in 302.611631 s /832028 KiB sampled RSS.
All new jobs terminal with return code zero; watchdogs <=4 GiB, below 40 GB.

Owned new files: global_events module/test, contextual_macrostep driver/auditor,
macrostep_audit tests, report and private artifacts. Exact commands in report.
Index: figs/fixed_rule/retimed_holder_contextual_macrostep_evidence_v1.json.
Prior status archived as STATUS_BEFORE_CONTEXTUAL_MACROSTEP_20260927.md.
MAIN_AGENT_NOTES.md remains absent/unedited; no shared dependency request.

Next execute the next lower periods from the actual damaged U/U+1 state and
check receiving-layer repair. The frozen entry relation does not automatically
admit malformed Info metadata, rogue Age0 heads or surviving nonMEM Data.
A promising checked extension must prove the three out-of-bank Data words are
inert through every clock/communication phase while retaining them, and prove
actual stage0 Info normalization before using a noiseless endpoint identity.
Do not discard these words or substitute insertion of the measured zero symbol
into a separate upper fixture for physical continuation. Batch/GPU acceleration
of the now-audited global scheduler remains worthwhile for repeated runs.
Full goal active: noisy depth-two closure, upper repair, amplification,
thresholds, Q/U optimization, robust caps and depth three remain open.

## Preserved milestone: verified physical head transport into the next colony

[CONTEXTUAL_RECOVERY.md](CONTEXTUAL_RECOVERY.md) continues the exact 17-colony
burst endpoint for 16384 quiet physical ticks. Both extra heads enter lower
colony 9, at ticks 1775/1776. Their initial colony 8 retains its original head
and five Data defects; colony 9 has its original evaluator plus the incoming
READ_META PC8 and FETCH PC4456458 heads. No decoded-macrostep conclusion yet.

New contextual_flags.py restores complete banks/controller state and packs the
actual flags with zero transitions and equality of all 85786624 raw words.
118 exceptions become 19 while 99 Flag1 sites remain in the packed plane.
All final flags clear at independently verified tick 15453; final time 1232635846
has 19 discrepant physical sites /90 raw words across colonies 8 and 9. Unused
workspace Data at addresses 30960–30962 is retained alongside 6996/6997.

Physical run passes: 103.157817 s /461440 KiB sampled host RSS /29369874 explicit
GPU bytes; 1998848 full local exception evaluations. Five view/representation
tests pass in 1.969 s /258036 KiB. Independent scalar audit passes every tick
in all 17 colonies: 1736704 core evaluations, 2229760 additional complete native
outputs /343383040 raw words including crossing windows; all complete saved
observations and final state agree. Audit 322.789562 s /1811324 KiB sampled RSS.
All jobs terminal with return code 0; limits <=3 GiB RAM, below user 40 GB.

Owned new files: contextual_flags module/test, contextual_recovery driver/auditor,
CONTEXTUAL_RECOVERY.md and private artifacts. No frozen source/evidence modified.
Commands and limitations in report. Index:
figs/fixed_rule/retimed_holder_contextual_recovery_evidence_v1.json.
Previous status archived as STATUS_BEFORE_CONTEXTUAL_RECOVERY_20260927.md.
MAIN_AGENT_NOTES.md remains absent and unedited; no shared change requested.
Historical third_link_initialized process was not present on process recheck;
no restart, modification or historical completion claim. GPU reservation unused.

Next continue both affected colonies through commit and reset, preserving all
Data and incoming-head interactions. Colony 9 now has the same controller phases
as the earlier one-colony failure, but actual context differs; do not reuse its
decoded result without executing/auditing this state. If factoring by colony,
check global boundary-copy equivalence and closed-ROM/no-mail conditions rather
than silently wrapping physical copies. The original noiseless endpoint domain
excludes arbitrary damaged Info, nonMEM Data and rogue reset-time heads; prove
an extension or execute an admissible physical prefix before using it.
Then carry actual decoded errors into subsequent receiving-layer repair.
No full noisy nested macrostep, upper repair, amplification or threshold claimed.
Q/U optimization, robust caps and depth three remain open. Full goal active.

## Preserved milestone: audited lower burst in the actual upper NAND context

[CONTEXTUAL_BURST.md](CONTEXTUAL_BURST.md) records a 17-colony physical run
using complete inherited depth-two banks for actual upper positions 9557–9573.
At the lower NAND checkpoint, all 2310 gathered raw input words in each of
colonies 8 and 9 equal the actual upper radius-seven neighborhoods. Outer
window boundaries are periodic and are not asserted globally equivalent.

Unfiltered seed 2026092713 /expected 8192 gives 8404 full-state marks over
32 physical ticks in colony 8, followed by two quiet ticks. The exact endpoint
has 118 discrepant sites /189 raw words, including five primary Data words,
two extra heads and 99 Flag1 sites. No host successor or Data/flag rebase.
The extra heads are at addresses 30992/30993; their subsequent possible entry
into the next colony is not yet executed. This cannot be inferred from the
earlier one-colony periodic macrostep failure.

Independent audit passes: 2276300 complete native output states /350550200 raw
words, 596 full scalar-source probes, every saved global exception set checked.
Complete inherited banks, upper context and gathered inputs independently bound.
Run 24.871759 s, audit 31.954896 s; peak sampled RSS 338624/350880 KiB.
Explicit GPU bound 57389816 bytes. Four bounded-view tests pass in 1.536 s,
including all raw controller fields, actual cross-colony copies and rejected
inconsistent Data. All three watchdog receipts return zero, <=1 GiB RAM.

Owned additions: live_window.py, four tests, contextual burst driver/auditor,
CONTEXTUAL_BURST.md and private artifacts. Exact paths/commands/results in report.
Evidence index: figs/fixed_rule/retimed_holder_contextual_burst_evidence_v1.json.
Previous status archived as STATUS_BEFORE_CONTEXTUAL_BURST_20260927.md.
No shared-source change or substantive GPU reservation; other agent should
reply in MAIN_AGENT_NOTES.md. That file remains absent and unedited.

Next continue this exact 17-colony endpoint through flag clearing and possible
cross-colony head transport. Validate any packed representation by complete
same-time raw equality, retaining unused-space Data. Then execute the noisy
commit and subsequent receiving-layer repair. Damaged Info metadata/extra heads
may violate frozen noiseless endpoint hypotheses; do not silently project them
away or substitute a fault-transfer test for the actual nested trajectory.
No complete noisy nested macrostep, upper repair or threshold is claimed here.
Q/U optimization, robust caps, amplification and depth three remain open.

## Preserved milestone: verified burst-induced decoded macrostep failure

[BURST_MACROSTEP.md](BURST_MACROSTEP.md) continues the exact three-head recovery
endpoint through U and U+1. Literal collisions remove the original evaluator;
at time 1232648958 only an invalid-PC FETCH head remains (PC 4456458, outside all
ROM indices). The actual commit produces all-zero Info: 48 raw F words /32 mutable
G words differ from the healthy successor. Next reset restores one head at 0 / PC 0,
but does not undo the committed simulated-state error. This is one finite noisy
macrostep failure, not a threshold or failure of surrounding hierarchical repair.

New bounded multihead event executor retains all Q Data words and every raw
controller field. Full native F/G handles literal local events and whole-ring
commit/reset; guarded transport skips stop at head events/interactions. No new
physical rule/ROM/alphabet. Six tests pass in 3.135 s (adjacent heads, collisions,
metadata fallback, outside-workspace Data, rejected omissions). Failed WAIT-ROM
fixture and pre-optimization source preserved; the fixed ROM has no WAIT row.

Macro continuation: 14.985483 s /496740 KiB, no GPU; 914847803 physical ticks,
28587 literal events and two full-ring clock steps. Independent audit passes
45.627019 s /414492 KiB: 13112 scalar collision-prefix ticks, 74721 core evaluations,
then a checked 55442-tick invalid-PC reflection invariant, six complete raw
checkpoints, and 10234 full scalar G commit/reset outputs. Healthy baseline and
32 mutable decoded differences independently bound in the evidence index.
All jobs terminal; limits <=1 GiB, below 40 GB. No shared files/jobs changed.

Owned additions: multihead_events.py, six tests, burst_macrostep driver/auditor,
report and private evidence. Exact filenames/commands/results in BURST_MACROSTEP.md.
Index figs/fixed_rule/retimed_holder_burst_macrostep_evidence_v1.json; prior status
archived as STATUS_BEFORE_BURST_MACROSTEP_20260927.md.

Next reproduce a local burst in lower colonies initialized from a real receiving
upper NAND configuration, then carry the actual decoded error into upper repair.
Do not call injecting this measured all-zero symbol into an unrelated upper
fixture an executed nested noise trajectory. Preserve unused-space Data defects
through any bank/endpoint representation. The current scheduler is a restricted
executor with trajectory-specific audit, not a general multihead proof.
Noisy depth-two execution, amplification, Q/U optimization, caps, thresholds and
depth three remain open. Full goal active; MAIN_AGENT_NOTES.md is the other
agent's reply channel and has not been edited. No shared change requested.

## Preserved milestone: exact burst recovery; flags clear, procedure defects remain

[BURST_RECOVERY.md](BURST_RECOVERY.md) resumes the exact higher-intensity burst
endpoint for 16384 quiet physical ticks. New late_flags adapter transfers the
actual flags into the existing packed engine with zero transitions and equality
of all 5046272 raw words checked. 118 sparse exceptions become 19 while all 99
initial Flag1 sites remain represented; no repair/projection occurs at transfer.
Same physical rule/ROM/alphabet/private binary. Canonical late geometry, zero Wf
and mail-free reference required; no U rollover is implemented by the adapter.

Flag1 grows to 8233 sites at quiet tick 8192, beyond the old sparse capacity,
then clears at tick 15453 (independent exact recurrence). At tick 16384, 19 sites
/90 raw procedure words still differ, including five Data words and two extra
heads. This is neither complete recovery nor a decoded-macrostep failure claim.
Long GPU run: 75.616714 s, 406264 KiB host RSS, 24167922 explicit device bytes;
maximum remaining sparse exceptions 19. All jobs terminal.

Independent long audit replays every quiet tick using scalar core procedures and
integer flags in a checked coherent/canonical/mail-free active interval: 163840
core evaluations, all saved complete physical observations equal. Both full
lattices also execute native G for the first eight ticks: 524288 states /80740352
raw words. Audit passes 32.489308 s /585428 KiB. Four reconstruction/domain tests
pass 1.667 s. 128-tick pilot and audit also pass. Full endpoint provenance and
saved final representation independently bound in the evidence index.

Owned additions: late_flags.py, tests, burst_recovery driver and auditor, report
and artifacts. Exact filenames/commands/limits are in BURST_RECOVERY.md.
Index figs/fixed_rule/retimed_holder_burst_recovery_evidence_v1.json; old status
archived as STATUS_BEFORE_BURST_RECOVERY_20260927.md. Driver/test caps512 MiB;
audit cap768 MiB, below the user's40 GB. No shared change or substantial GPU
reservation. MAIN_AGENT_NOTES.md remains the reply channel, never edited here.

Next carry the exact saved remaining Data and extra heads to a decoded macrostep
and the next reset. Any acceleration must retain multiple-head interactions and
Data outside the usual workspace. Detach zero flags only by checked same-time
identity before crossing U. No such macrostep continuation/result is claimed yet.
Full-period noise, noisy depth-two execution, Q/U optimization, caps, amplification
and depth three remain open. Full project goal active.

## Preserved milestone: denser unfiltered GPU bursts with complete-lattice audits

[POISSON_BURSTS.md](POISSON_BURSTS.md) records two independent-site-time Poisson
bursts at the actual active READ_B/NAND checkpoint, Q=32768, Age=1232619428.
Noise lasts 32 physical ticks followed by two quiet ticks; every complete raw
state remains represented. Same physical rule/ROM/alphabet/private GPU binary.
No resampling, filtering, endpoint replacement or Data/flag rebase.

Expected 2048 marks: realized 2154, per-site-time occupancy probability
0.0019512188925, complete recovery; GPU 4.433656 s. Expected 8192: realized 8404,
probability 0.0077820617398, 118 sites /189 raw words still differ after two quiet
ticks; GPU 13.670022 s. The higher sample contains actual interacting clusters
and leaves the proved sparse domain at tick 2. Its final Address/Age agree;
Flag1 intervals, wrong Data and extra controllers persist. This is not yet a
permanent-failure or decoded-macrostep claim. Both use seed 2026092713, not
independent statistical replications or a threshold estimate.

Each independent CPU audit executes both full lattices on every tick:
2228224 output states /343146496 raw words per run, plus 716/732 scalar-source
probes. Both pass, including reproduction of the high-rate damage, in
27.223712/27.426616 s. Explicit GPU allocation 21365496 bytes; maximum reported
host RSS 301568 KiB. All jobs terminal; no substantial reservation used.

Owned additions: retimed_holder_poisson_burst.py and its independent auditor,
POISSON_BURSTS.md and private evidence. Exact commands/results in the report and
watchdogs. Evidence index figs/fixed_rule/retimed_holder_poisson_burst_evidence_v1.json.
Prior status archived as STATUS_BEFORE_POISSON_BURSTS_20260927.md.

Next resume the exact high-rate saved state and follow the quiet recovery suffix,
then decoded macrosteps. Growing Flag1 fronts may exceed sparse capacity; the
existing flags engine accepts explicit late Age/initial planes. A new owned
adapter must verify same-time equality of all raw fields while transferring those
actual bits, preserve other exceptions, and avoid bypassing the old forcing-only
absorption guard. Not implemented yet. Full-period persistent noise, noisy
depth-two execution, Q/U optimization, caps and amplification remain open.
MAIN_AGENT_NOTES.md remains the reply channel; no shared change requested.

## Preserved milestone: consecutive-fault repair invariant and literal active-controller tests

[CONSECUTIVE_FAULT_REPAIR.md](CONSECUTIVE_FAULT_REPAIR.md) extends the conditional
base repair lemma to consecutive noise ticks. Before a step, permit arbitrary
procedure-only residuals at P; inject arbitrary complete G states at D. With
clean healthy geometry/flags/Wf/coherent procedures and Signals, at most two D
per eleven sites, and at most two P union D per five sites, the next discrepancy
is confined to procedure fields at D. Complete raw metadata/nonprocedure outputs
agree. The healthy-context premises must be checked each time; forcing/capture
closure is not asserted. New certificate validates the 55 geometry BDD cases and
replays full DAG/algebra/majority cuts: pass 1.808048 s, 64096 KiB.

Two literal streams at the actual active NAND checkpoint inject faults on eight
consecutive ticks (moving single holder: 8 faults; repeated pair: 16). Each has
seven new fault times overlapping surviving controller discrepancies. All raw
state rejoins after the first quiet tick. A two-then-one Data control has sparse
individual pulses but violates the union bound: five wrong Data copies persist
through two quiet steps. This demonstrates why isolated-pulse repair alone does
not justify continuing-noise correction.

Native driver passes 1.839228 s /128020 KiB; independent scalar replay checks every
retained output in both trajectories, 8960 full states /1379840 raw words, passing
19.859934 s /104188 KiB. Four domain tests pass 0.546 s, including 10000 independent
window comparisons. All work is CPU-only with 512 MiB watchdogs. No physical rule,
ROM, alphabet, existing executor or shared artifact changed. All jobs terminal.

Owned additions: spacetime_domain.py, certificate, consecutive-fault driver,
independent auditor, four tests and this report/evidence. Exact full filenames,
commands and limitations are in the report. Evidence index:
figs/fixed_rule/retimed_holder_spacetime_repair_evidence_v1.json.
Prior status archived as STATUS_BEFORE_CONSECUTIVE_FAULT_REPAIR_20260927.md.

Next organize independent fault cones at higher rates using the proved invariant;
keep interacting clusters and forcing contexts exact. No new execution shortcut
is installed. General amplification, noisy depth-two periods, Q/U optimization,
robust caps and depth three remain open. Full goal active. MAIN_AGENT_NOTES.md is
the reply channel; this agent does not edit it. No shared change requested.

## Preserved milestone: unfiltered independent space-time noise pilot

[POISSON_NOISE_PILOT.md](POISSON_NOISE_PILOT.md) runs paired actual GPU trajectories
for 15 colonies through two complete lower periods under independent full-state
Poisson marks. Seed 2026092711, expected 128 marks, realized 118, no resampling or
spacing filter. Exposure 2111062325329920 site-ticks; replacement probability
6.063298011819337e-14 per site-time. Noise occurs after each marked transition.

All 118 events rejoin after one physical tick. Both complete period snapshots
(148740 bank words plus controllers/Signals/flags) and all 2310 decoded raw fields
match at U and 2U. Zero Data/flag rebases; no healthy successor installed.
The realized event gap is at least 140965 ticks and all contexts meet the existing
clean-context theorem. This sample has no interacting/forcing-phase noise and
is explicitly a low-rate pilot, not a threshold or noisy depth-two-period claim.

Independent audit reproduces the exact sample and replacement words, executes
16992 complete scalar physical outputs, and recomputes both complete terminal
banks/snapshots via the independent DAG diagnostic. Pass 52.191715 s /73448 KiB.
GPU experiment 69.882367 s /219992 KiB, explicit device peak 30178500 bytes.
Four sampler tests pass 0.054 s. All jobs terminal; same rule/ROM/alphabet/private
CUDA binaries, no shared changes or substantial GPU reservation.

Next certify a space-time sparse-fault invariant allowing consecutive noise ticks
under explicit current/previous local sparsity and clean-context hypotheses.
Use it only after proof to reduce isolated-mark execution cost at higher rates;
keep exceptional clusters/forcing contexts exact. General amplification, noisy
depth-two work periods, Q/U optimization, robust caps and depth three remain open.
MAIN_AGENT_NOTES.md remains the reply channel; still absent. Full goal active.

Owned additions: noise_schedule.py; GPU pilot and independent auditor; four sampler
tests; POISSON_NOISE_PILOT.md and private evidence. Exact commands/limits in the
report; evidence index retimed_holder_poisson_noise_evidence_v1.json. Prior status
archived as STATUS_BEFORE_POISSON_NOISE_20260927.md.

## Preserved milestone: certified conditional two-tick complete-state repair

[TWO_TICK_REPAIR_THEOREM.md](TWO_TICK_REPAIR_THEOREM.md) establishes G^2(damaged)
=G^2(healthy) with canonical Address, uniform legal Age, zero healthy flags/Wf,
coherent procedures/Signals, and at most two faulty sites in every eleven-site
interval. Any total number of full mutable-site replacements is allowed under
that local condition. There are no head-count or inactive-controller restrictions.
No further faults may occur during the two repair ticks. This is conditional
pulse recovery, not general forcing-phase/stochastic amplification.

The exact geometry proof covers all 55 local defect-position pairs, every healthy
Address/clock and both full-width faulty geometry/flag/Wf records (148 symbolic
bits per pair). BDD peak 34309 nodes; pass 6.574527 s /57976 KiB. Complete-descriptor
cuts identify 20 geometry, 119 procedure and 10 Signal groups, prove all nonprocedure
outputs equal, confine first-tick procedure discrepancies to faulty holders, and
prove unrestricted healthy output-copy coherence. Full-output majority replay
then yields the second-tick equality. Structural pass 1.854099 s /62752 KiB.

Seven mutation/domain certificate tests pass 2.602 s; four sparsity/physical tests
pass 1.388 s. Six clock contexts repair 16 simultaneous complete-state replacements;
a three-copy negative control survives. The cyclic sparsity predicate matches all
8192 subsets of a 13-site ring. Failed v1 checker/source preserved: it incorrectly
expected an unused Signal vote removed by pruning. Accepted v2 checks exact roots
and rejects every uncut raw dependency. No physical rule/ROM/alphabet changed.

All jobs terminal; CPU only, below 512 MiB watch limits. No shared source, GPU job,
CUDA build, historical dataset or pending reservation touched. Please reply in
MAIN_AGENT_NOTES.md; still absent. Full goal active, with source ambiguities,
continuing noise/amplification, robust caps and depth three still open.

Next build a reproducible space-time fault experiment that uses this lemma only
under its explicit premises, evolves unsupported clusters/forcing defects exactly,
and retains failures. Longer-term connect exceptional clusters to simulated-layer
repair and amplification. Commands/proof steps/TCB in the report; evidence index
retimed_holder_two_tick_repair_evidence_v1.json. Prior status archived above.

Owned additions: geometry prover, structural/composition certificates, pulse-domain
predicate, two test files, TWO_TICK_REPAIR_THEOREM.md and private evidence.

## Preserved milestone: full-field pulses and actual flag-front recovery

[PHYSICAL_FAULT_SWEEPS.md](PHYSICAL_FAULT_SWEEPS.md) adds a bounded literal physical
G cone executor retaining every raw field and actual-Address metadata. Four tests
pass, including full-ring parity and live-controller retention. The first fixture
had an invalid negative Address; its failed source/log are preserved and corrected.

At the actual depth-two complete checkpoint, all 160 selected/seeded one/two-site
pulses (geometry, flags/Wf, Signal, procedures and complete states) rejoin within
two ticks. Another 136 pulses use actual GPU forcing/clearing/evaluator states:
132 rejoin within two ticks, four retain exactly one Flag1 bit after twelve ticks.
Independent scalar-source auditing checks all 22256 complete physical outputs
in every possible fault cone on every executed tick; all match.

All four lingering cases are continued through actual GPU dynamics. Twelve full-G
ticks match the CPU defects; a same-state flag rebase retains the wrong front.
Complete physical rejoin occurs by Age 1230012000, 11900 ticks after injection.
No healthy successor installation or unsupported endpoint shortcut is used.
Accepted continuation v2 constructs the exception owner only after its background
reaches the checkpoint. Superseded v1 passed but manually synchronized an empty
owner's clock; its exact source/results are preserved separately.

Boundary sweep 7.217314 s /68144 KiB; forcing 10.944380 s /187172 KiB;
scalar audit 79.295521 s /72092 KiB; GPU continuation 39.158591 s /177788 KiB.
Continuation explicit GPU peak 24265180 bytes. All jobs terminal; unchanged
physical rule/ROM/alphabet/private CUDA binaries. No shared change or substantial
GPU reservation needed. MAIN_AGENT_NOTES.md remains the reply channel.

Next: certify a general two-site/two-tick repair lemma with explicit canonical
geometry, zero flags/Wf and coherent procedure/Signal hypotheses. The finite
sweeps do not prove it; forcing-front cases distinguish the missing assumptions.
General stochastic amplification, robust caps, depth three and source ambiguities
remain open. Goal active. Exact commands/limitations in the report; evidence index
retimed_holder_fault_sweeps_evidence_v1.json. Prior status archived above.

Owned additions: literal_cone.py; boundary/forcing sweep drivers, scalar audit,
GPU front continuation; four tests; PHYSICAL_FAULT_SWEEPS.md and private evidence.

## Preserved milestone: timed cross-level correction with inherited scratch

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
