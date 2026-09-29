# Fixed-rule agent status

Updated2026-09-28. **Full Gacs/Gray goal active; not complete.** Please reply in
**Report/fixed_rule/MAIN_AGENT_NOTES.md**; this agent never edits that file.
Latest check found it absent. No shared-source interface change requested.

## Priorities and coordination

Correct actual fixed-rule self-simulation, practical complete depth-two GPU
execution, and measured correction/noise behavior across levels. Optimize Q/U
subject to correctness; U<=128Q is not required. User permits40GB total host RAM.
Main agent owns substantial GPU scheduling; old8GiB reservation unused. This
milestone used small private GPU builds/worlds,47,411,200explicit device bytes
per one-colony world; two-colony test allowed128MiB. Largest sampled host RSS
468672KiB. Driver/compiler memory excluded from explicit buffer counts. No shared
sources/jobs/data/builds changed. All owned jobs terminal; final GPU query empty;
third_link_initialized process query found only the query command itself.

## Latest: factorization, flag clearance, two failed actual macrosteps

[COMPACT16_CANONICAL_NOISE.md](COMPACT16_CANONICAL_NOISE.md) records the algebra,
proofs, exact commands, complete-state results and limitations. Physical rule
unchanged: Q16384/U2^30/radius7,154words4090bits, descriptor53f7adbf...fb846b,
ROM4d055889...f48b32. No depth parameter/register/ROM or host upper transition.

New compact16_holder_canonical_gpu.py/.cu accepts canonical Address/uniform legal
Age but arbitrary other typed fields, including incoherent replicas, flags/Wf,
Data/Signals/mail and multiple/missing heads. It votes each logical procedure,
computes its virtual zero-flag core clock once and scatters to five holders,
retaining holder-local mail clearing and all Signal/Wf exceptions. Every physical
tick executed. About1ms/tick versus16ms full-DAG backend. All154fields retained.

Fresh full-descriptor BDD:88independent bits(allAddress/Age+44primary flags/Wf),
47811nodes/0.821635s. Proves canonical geometry invariant and exact simplified
Flag1/Flag2 equations for arbitrary remaining fields; wrong threshold rejected.
Procedure/Signal/Wf factorization has documented algebra and backend parity;
not a universal compiler proof. Four testsPASS20.340s: arbitrary complete states
across clock events, two-colony seams, all8prior complete literal trajectories
32->128->511->512, and domain/width/metadata/budget rejection. Host evaluators
patched to fail during GPU evolution. Domain does not assume healthy controllers.

All8retained p=.1 failures continued16384more literal factored ticks, from520to
16904quiet ticks.2,415,919,104complete site transitions;150.665258s/watch151.128685s,
468672KiB sampled RSS,47,411,200explicit GPU bytes. Full saved checkpoints
1/512/2048/8192/16383/16384. All finalFlag1/Flag2/Wf planes zero, no full rejoin.
Final differing sites26,28,35,25,37,18,26,39; raw words125,40,125,90,150,100,80,135.
Primary Data differences7,8,8,8,8,3,8,15. Cases3/7 still have no head; case1retains
healthy head with only Data discrepancies; others retain wrong/displaced heads.
Healthy position12657/phase1/PC2217. Cases0/3/5/6/7retain Signal differences.

New compact16_holder_late_idle_gpu.py/.cu checks every raw idle premise on GPU:
zero head/control/mail/flags/Wf, coherent Data/Signals, matching canonical clock.
Host checks fixed late interval. Only Age changes in this domain; optimization
stops atU-1 and leaves commit to the literal kernel. Invalid state rejected
without mutation. Three testsPASS23.893s, native comparisons/clock boundaries,
long skip and complete-state rejection. No simulated transition supplied by host.

Idle core BDD:958independent bits,148358nodes,189operations after exact constant
propagation; all18procedure fields, arbitrary typed metadata/neighborhood Data,
alloldAges502000001..1073741822.0.994165s. Composition with canonical geometry,
coherent voting and no future Signal/Wf event gives full-holder idle identity.
Counterexample rejects crossing commit. Proofv1/v2 hit200000nodes constructing
an unnecessary union of64mutation bits after the actual equalities passed. V2
constant propagation alone did not fix it. V3 retains first differing bit as
sufficient mutation witness. All failed sources/logs/watchdogs preserved; no
physical source/results changed to pass. V3 successful watch1.420036s/94800KiB.

Cases3/7satisfy complete idle guard atAge508496235. Each advances565245588idle
ticks then executes the actual commit. Both produce incorrect decoded upper
states:49/154raw differences, still33/105projected differences after ignoring
metadata. All five physical Info copies agree on the wrong values. Decoded
Age0 versus intended502000101; Data/head/phase/PC/value/ALU andFlag1/Flag2 differ.
Both outputs word-width valid. Exact original top scalar transition agrees with
independently completed healthy fixture. This establishes TWO ACTUAL DECODED
MACROSTEP FAILURES for retained dense-noise histories, not merely deadline
nonrecovery. Other6macrostep outcomes remain open. No failure-rate/threshold claim.
Two-case run3.203463s/watch3.651636s/372156KiB,47,411,204explicit GPU bytes.

Independent auditPASS: all final raw ticks, counts/flags, complete idle premises,
precommit states, actual commits, every Info replica and projected decoding;
30277632raw words +340full scalar outputs(all154Info sites in both commits plus
32seams).9.352809s/watch9.737111s/228032KiB. Long factored trajectories not fully
independently replayed; scope stated explicitly. Seven tests and all production
experiment/audit/proof-v3 commands exit0.

Owned additions: canonical_gpu/late_idle_gpu py/cu, two test modules, canonical
geometry/idle-v1-v2-v3 proofs, canonical_noise/headless_macrostep/audit/seal
experiments, report/status archive, private builds and retained receipts.
Prior935sealed files/nine banks unchanged. New seal:
figs/fixed_rule/compact16_holder_canonical_noise_evidence_v1.json,
984files+9external banks. Seal6.466060s/52648KiB. Mutable STATUS and its own seal
log/watch excluded. No shared interface requested; MAIN_AGENT_NOTES unedited.

## Next concrete work and unresolved goal

Follow OTHER SIX actual states through commit using a justified accelerator for
arbitrary Signals and damaged head motion, then follow the next work period.
Use multiple simulated colonies so healthy simulated neighbors can exercise
upper-layer repair; the one-periodic-top fixture here cannot establish that.
Broaden stochastic support/time and cross-level sampling with failures retained.
The existing coherent/localized-Signal shortcuts must not discard these states.
Coordinate substantial GPU work. Literal canonical backend is a useful reference,
not yet a practical full noisy U~10^9executor on its own.

Two failures expose a real limit of implemented protection. They do not contradict
the sparse two-tick lemma: dense continuing-noise histories violate its premises.
General correction/amplification, arbitrary malformed code/geometry recovery,
reliable finite caps, broader top rings, sustained depth-two top arithmetic and
depth3 remain open. Candidate-B Flag2, voted-old-Signal D10, printed Flag2
persistence/SimBit timing and cap Address-defect persistence remain qualifications.
Gray31–32 specialized hard-wiring and Gacs9.2–9.3 modified self-correcting
simulation remain architectural basis. Full project goal stays active.

## Preserved milestones

[COMPACT16_LITERAL_GPU_NOISE.md](COMPACT16_LITERAL_GPU_NOISE.md): complete G
CUDA arbitrary geometry, prior512tick continuation,100925440native checked words.
[COMPACT16_REPAIR_THEOREM_AND_NOISE.md](COMPACT16_REPAIR_THEOREM_AND_NOISE.md):
conditional distributed two-tick repair, full-width geometry BDD,12tests and
unfiltered pilot p=.005/.02/.1(recovered8/8,8/8,0/8 by8quiet ticks).
[COMPACT16_TIMED_REPAIR.md](COMPACT16_TIMED_REPAIR.md): actual middle controller,
4/6/9-bit literal prefixes,10/15-bit lower pulses;56then0bank differences;
all339345408bank words recomputed, complete physical rejoin.
[COMPACT16_ENDPOINTS.md](COMPACT16_ENDPOINTS.md): conditional complete C/B
identity/two retained depth-two endpoints11.176365s;113115136bank words recomputed.
No literalU^2 replay or universal backend proof.
[COMPACT16_GPU_BACKEND.md](COMPACT16_GPU_BACKEND.md):31-colony one-link active
READ_B->WRITE->FETCH over two actual periods29.970498s.
[Previous status](STATUS_BEFORE_COMPACT16_CANONICAL_NOISE_20260928.md) preserves
all prior compact/retimed history. Retimed results remain separate pending fresh
compact validation.
