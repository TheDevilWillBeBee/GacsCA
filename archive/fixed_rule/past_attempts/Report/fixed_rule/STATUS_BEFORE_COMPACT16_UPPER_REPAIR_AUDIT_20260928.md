# Fixed-rule agent status

Updated2026-09-28. **Full Gacs/Gray goal active; not complete.** Please reply in
**Report/fixed_rule/MAIN_AGENT_NOTES.md**; this agent never edits that file.
Latest check found it absent. No shared-source interface change requested.

## Priorities and coordination

Correct actual fixed-rule self-simulation, practical complete depth-two GPU
execution, and measured correction/noise behavior across levels. Optimize Q/U
subject to correctness; U<=128Q is not required. User permits40GB total host RAM.
Main agent owns substantial GPU scheduling; old8GiB reservation unused. Only
small private GPU worlds/builds used; event buffers2097776bytes plus27616staging
per one-colony run; literal reference47.4MB. Peak sampled host RSS961284KiB.
Explicit device counts exclude driver/compiler overhead. No shared modules,
CUDA artifacts, datasets or jobs changed. All owned jobs terminal. Final GPU
query empty; third_link_initialized/owned-job process query empty.

## Latest: ALL EIGHT retained high-rate macrosteps resolved

[COMPACT16_ALL_NOISE_MACROSTEPS.md](COMPACT16_ALL_NOISE_MACROSTEPS.md) records
source/domain arguments, exact commands, all outcomes, tests and limitations.
Physical construction unchanged: Q16384/U2^30/radius7,154words4090bits,
descriptor53f7adbf...fb846b, ROM4d055889...f48b32. No depth parameter, new physical
register/opcode, replacement upper transition or host simulated computation.

Final combined result for original p=.1 local-noise histories: case1computes the
correct complete154-word upper state; cases0/2/3/4/5/6/7fail. Every history reached
an ACTUAL COMMIT with all five Info replicas retained and agreeing. This changes
the interpretation of earlier raw nonrecovery: case1had residual lower scratch
errors but a correct decoded macrostep. Not a new random sample or threshold.

Cases0/2/3/4/5/7 differ in49raw/33projected words, including decodedAge0 instead
of502000101. Their raw metadata also fails projection consistency. Case6differs
in19raw/19projected words and commits Signal32212254792 to a5bit field. The
projected decoder rejects it; artifact preserves the unmasked value. Other
case6errors include Age502131225 instead of502000101, Data/PC/value and flags.
Do not silently mask malformed encodings or count only metadata discrepancies.

## New execution domains and validation

compact16_holder_late_events.py: same-time complete raw restoration into sparse
resident bank/records, checked by full reconstruction. Canonical Address/uniform
legal late Age, zero flags/Wf, coherent procedures/Signals, no mail, zero non-MEM
Data,64records/colony. Widen only stationary-Signal guard beyond colony ends;
unchanged local and controller-event source. BDD:123bits/5458nodes/0.274874s,
alllateAges502000001..1073741823, allAddresses, coherent arbitrary Signals/Data.
All90complete F procedure outputs have zero old-Signal dependencies. Five tests
PASS9.206s: saved states, clock boundaries, Signal seams, two heads, rejection.

compact16_holder_late_multi_events.py: retain individual event distances; add
pair bound max(0,floor((gap-2)/(vleft-vright))) for closing heads. Transport stops
before local interactions; full local ticks handle reflections/instructions/
collisions. Same/diverging velocities preserve separation during event-free
transport. Three testsPASS33.700s:2/3heads, odd/even gaps, adjacent parallel
motion, reflections, actualcase4 over16384literal ticks. Omitting pair bound
leaves2heads where literal rule leaves1; unsafe build retained as negative test
only. Pair bound conservatively applies even during inactivity; opposing frozen
heads can reduce acceleration. No correctness impact on these outcomes.

First all-case attempt timed out240s atcase4 because old transport rejects
multiple heads. Watch returncode-9/wall-time exceeded, source/log retained;
confirmed terminal before retry. No complete artifact published for that run.
V2 with multiple-head bound completed7cases in38.079468s/watch38.532642s,
961284KiB RSS. Its passed:false is intentional incomplete coverage, despite
exit0. Each case/checkpoint/journal saved immediately. Case4stopped at exact
Age514889820 when next transition emitted mail outside that backend domain.
No state was discarded to continue.

compact16_holder_late_mail_events.py: removes two late mail-rejection guards;
unchanged complete packet dynamics and edge/delivery distances. Independent
batches still reject packets, synchronous sparse kernel handles them. All mail
widths/copies validated and uploaded; temporary zero-mail allocation/validation
scaffold is never evolved. Full raw equality checked before transition. Three
testsPASS43.805s: actual emission+32768ticks vs complete literal, cross-colony
packets/delivery/write priority, invalid residue and bad replicas/widths.

Case4resumed from its saved exact clock, emitted real lp packet at2862(target1568,
Data15386914758072594124,remaining1), and reached actual commit in24.277152s/
watch24.694809s,388340KiB RSS. Output wrong49raw/33projected words. This finishes
the last history rather than relabeling the partial V2receipt as successful.
All variants remain bounded coherent late-period accelerators, not arbitrary
noisy-state kernels. All entry points stop after current commit.

Independent auditPASS: active/inactive and precommit boundaries, complete commits
for all8cases, packet emission, all5Info copies and every physical Info scalar
output;68124672raw words+1232complete scalar outputs. Cases3/7match earlier
separately guarded headless endpoints word-for-word. Invalid projected width
explicitly rejected.12.383913s/watch12.675508s/182824KiB. Long event intervals
not entirely independently replayed; domains/algebra and finite parity support
them, not a universal event/compiler-equivalence proof. Eleven testsPASS overall.

Owned additions: late_events/late_multi_events/late_mail_events, three test modules,
stationary-Signal certificate, all-case-v1/v2 and case4-resume/audit/seal drivers,
report/status archive, private builds and receipts/checkpoints. All984prior files
and9external banks unchanged. Seal:
figs/fixed_rule/compact16_holder_all_macrosteps_evidence_v1.json,
1050files+9banks. Seal6.631656s/52744KiB. Includes timeout, partial receipt and
negative-control build; excludes mutable STATUS and own seal log/watch.

## Next concrete work and unresolved goal

Follow committed states into the next work period with invalid encodings
explicitly preserved/rejected. Use multiple simulated colonies to test repair
by healthy simulated neighbors; the one-periodic-top fixture cannot establish
that. Then broaden stochastic support/time/cross-level sampling, retaining all
failures. Remove conservative inactive frozen-head performance restriction if
needed; do not bypass controller interactions or packet deliveries. Coordinate
substantial GPU work. For large depth-two restoration, stream coherent bank/
records rather than allocating full raw physical arrays beyond40GB host RAM.

General correction/amplification, malformed-code/geometry repair, reliable finite
caps, broader top rings, sustained depth-two top arithmetic anddepth3 remain
open. Sparse two-tick repair lemma remains conditional; dense histories here
violate its premises. Candidate-B Flag2, voted-old-Signal D10, printed Flag2
persistence/SimBit timing and cap Address-defect persistence remain qualifications.
Gray31–32 specialized hard-wiring and Gacs9.2–9.3 modified self-correcting
simulation remain source basis. Full project goal stays active.

## Preserved milestones

[COMPACT16_CANONICAL_NOISE.md](COMPACT16_CANONICAL_NOISE.md): full canonical
factorization, arbitrary flags/controllers,16x literal acceleration, quantified
geometry/idle identities, all8flag-clearing trajectories, two first macrostep
failures.984-file previous seal includes bounded failed proof attempts.
[COMPACT16_LITERAL_GPU_NOISE.md](COMPACT16_LITERAL_GPU_NOISE.md): complete G
CUDA arbitrary geometry,512tick continuation,100925440native checked words.
[COMPACT16_REPAIR_THEOREM_AND_NOISE.md](COMPACT16_REPAIR_THEOREM_AND_NOISE.md):
conditional distributed two-tick repair, full-width geometry BDD,12tests and
unfiltered p=.005/.02/.1 pilot(recovered8/8,8/8,0/8 by8quiet ticks).
[COMPACT16_TIMED_REPAIR.md](COMPACT16_TIMED_REPAIR.md): actual middle controller,
4/6/9-bit literal prefixes,10/15-bit lower pulses;56then0bank differences;
339345408bank words checked, complete physical rejoin.
[COMPACT16_ENDPOINTS.md](COMPACT16_ENDPOINTS.md): conditional complete C/B
identity/two retained depth-two endpoints11.176365s;113115136bank words checked.
No literalU^2 replay or universal backend proof.
[Previous status](STATUS_BEFORE_COMPACT16_ALL_MACROSTEPS_20260928.md) preserves
prior compact/retimed history. Retimed results remain separate pending fresh
compact validation. MAIN_AGENT_NOTES absent and unedited.
