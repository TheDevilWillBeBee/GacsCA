# Fixed-rule agent status

Updated2026-09-28. **Full Gacs/Gray goal active; not complete.** Please reply in
**Report/fixed_rule/MAIN_AGENT_NOTES.md**; this agent never edits that file.
Latest check found it absent. No shared-source interface change requested.

## Priorities and coordination

Correct actual fixed-rule self-simulation, practical complete depth-two GPU
execution, and measured correction/noise behavior across levels. Optimize Q/U
subject to correctness; U<=128Q is not required. User permits40GB total host RAM.
Main agent owns substantial GPU scheduling; previous8GiB reservation unused.
This milestone used sequential small GPU worlds, explicitly52,363,264bytes each;
peak sampled host RSS525392KiB. GPU context/compiler storage is not included in
explicit buffer counts. No shared CUDA artifacts/sources/jobs/data changed.
All owned jobs terminal; final GPU/third_link_initialized query empty (only the
query process matched its own command). Only fixed_rule namespaces edited.

## Latest: literal complete CUDA and longer noise recovery

[COMPACT16_LITERAL_GPU_NOISE.md](COMPACT16_LITERAL_GPU_NOISE.md) records design,
source basis, exact commands, results and limits. Full G=pi F iota has unchanged
Q16384/U2^30/radius7,154words4090bits, descriptor53f7adbf...fb846b and
ROM4d055889...f48b32. Same full hard-wired descriptor each tick; no depth parameter,
extra physical register or host replacement of a simulated transition.

New compact16_holder_dense_gpu.py/.cu applies complete F to15raw neighbors and
projects metadata on GPU. It supports arbitrary typed mutable geometry, flags,
Data, mail, controllers and multiple/missing heads. Two full state buffers and
reusable evaluator workspace; no coherent or zero-flag premise. Four testsPASS
in15.567s: complete native parity on1/17/257-site arbitrary rings, saved damaged
states over successive ticks, radius-seven isolation, width/metadata/budget
rejections. Host evaluator entry points patched to fail during GPU evolution.

Continued every one of the eight retained p=.1 local-noise failures. Restore at
same clock24 with full healthy complement checked by24native CPU ticks; retained
401-site window contains the entire radius-seven possible fault support. No
fault discarded, clock reset, fresh encoding, or transition shortcut. Each full
Q-site colony runs512additional literal GPU ticks, checkpoints1/2/8/32/128/511/512.
All complete states retained losslessly as differences against saved healthy
states.75,890,688complete GPU site transitions;85.869481s, watchdog86.338474s,
525392KiB peak sampled host RSS;52,363,264explicit device bytes.

At520total quiet ticks, none of eight trials fully rejoins. Final differing-site
counts631,667,629,646,599,618,600,668; raw-word counts695,679,714,701,702,685,654,754.
All Address/Age agree, all retain Flag1/Data differences, six Flag2, five Signal,
two right-mail. Primary Data differs at7,8,8,8,8,3,8,15positions. Healthy head is
position3666/phase0/PC2217. Cases3/7 have no head; case6 hasPC2473 at3666;
other cases include extra/displaced heads. These are actual raw computation
errors at a nonterminal clock; eventual decoded macrostep/permanent failure
has not been established. No general stochastic robustness claim.

Independent native audit replays first32ticks/all8trials, checks final511->512,
and compares complete saved states1/2/8/32/512:655360outputs/100925440raw words.
64additional full scalar frontier/seam outputs and all saved counts/metadata
PASS. Audit50.526545s/watch50.876347s/210664KiB. Intermediate128/511GPU trajectory
not independently replayed in full; finite tests are not universal CUDA proof.
Exact controller/Data diagnosis saved separately. All commands/tests exit0.

Owned additions: dense GPU py/cu, dense_noise/audit/diagnose/seal experiment
modules, dense GPU test module, report, status archive, private build/header/
binary and receipts. Prior911sealed files/nine external banks unchanged.
New seal: figs/fixed_rule/compact16_holder_dense_noise_evidence_v1.json,
935files+9external banks. Seal5.699358s/52860KiB. Latest seal does not include
its own watchdog/log or mutable STATUS. No failed new scientific tests.

## Next concrete work and unresolved goal

Literal full-colony G costs roughly16ms/tick: useful reference but far too slow
for U~10^9. Build/justify compact acceleration that preserves nonzero flag fronts,
arbitrary Data/Signals and multiple/missing controllers. Validate any skip rule
against these retained literal trajectories. Follow damaged states through the
next controller-reset/retrieval epoch and compare decoded macrosteps. Existing
coherent/noiseless endpoint shortcuts cannot silently replace these states.
Then broaden noise support/time and cross-level sampling, retaining all failures.
Coordinate substantial GPU work with main agent.

Full correction/amplification, arbitrary malformed-encoding/geometry recovery,
reliable finite caps, broader top rings, sustained depth-two top arithmetic and
depth3 remain open. Candidate-B Flag2, voted-old-Signal D10, printed Flag2
persistence/SimBit timing and cap Address-defect persistence remain qualifications.
Gray31–32 specialized hard-wiring and Gacs9.2–9.3 modified self-correcting
simulation remain source basis. Full project goal stays active.

## Preserved milestones

[COMPACT16_REPAIR_THEOREM_AND_NOISE.md](COMPACT16_REPAIR_THEOREM_AND_NOISE.md):
conditional distributed two-tick repair, quantified full-width geometry proof,
12tests and unfiltered pilot (p=.005/.02/.1 recovered8/8,8/8,0/8 by8quiet ticks).
That theorem does not cover current dense histories/nonzero flag fronts.
[COMPACT16_TIMED_REPAIR.md](COMPACT16_TIMED_REPAIR.md): actual middle controller,
4/6/9-bit literal prefixes and10/15-bit lower pulses;56then0retained bank
word differences; all339345408bank words recomputed; complete physical rejoin.
[COMPACT16_ENDPOINTS.md](COMPACT16_ENDPOINTS.md): conditional complete-state C/B
identity and two retained depth-two endpoints in11.176365s; all113115136bank
words recomputed. No literal U^2 replay or universal backend equivalence claim.
[COMPACT16_GPU_BACKEND.md](COMPACT16_GPU_BACKEND.md): sustained31-colony one-link
READ_B->WRITE->FETCH, two actual periods29.970498s.
[Previous status](STATUS_BEFORE_COMPACT16_DENSE_NOISE_20260927.md) preserves
prior compact/retimed history. Retimed context/noise results remain separate
until freshly validated for compact16. MAIN_AGENT_NOTES absent and unedited.
