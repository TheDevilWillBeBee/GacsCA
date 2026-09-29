# Compact16 complete noiseless period

2026-09-27. The compact candidate now has a certificate-assisted mathematical
induction at complete word-descriptor semantics:

```
F^U(E(y)) is contained in E(G(y)),  G = pi F iota.
Q = 16384, U = 1073741824, physical radius = 7.
```

This establishes the noiseless block relation for the smaller fixed rule and
its own ROM, including active simulated controllers and repeated work periods.
It is an induction supported by executable finite checks, not a proof-assistant
development or a newly executed U-tick trace. Practical depth-two physical
execution and general cross-level noisy correction remain open. The frozen
retimed execution baseline is not replaced by this proof milestone.

## Rule and encoded domain

F is the complete compact16 word descriptor, with unsigned 64-bit arithmetic:

```
descriptor 53f7adbf7c34df6b17897b20a0d0654108f23a9c064defb89bb3c6d1a7fb846b
own ROM    4d055889959a880f189539dc213801780f8e2efa3daa7cb31e72cb3003f48b32
F: 154 words / 4090 bits; G: 105 words / 2704 bits
```

The projection pi removes 49 metadata words. Iota regenerates them from the
represented Address modulo Q and this same ROM. G is the fixed projected local
rule pi F iota. Neither physical fields nor transition/ROM selection depend on
depth. The evaluator's complete next controller, Data and mail state are among
the outputs computed by its own compiled program. Physical META scans read its
own ROM to supply projected metadata; no arbitrary-program platform is needed.
This follows Gray's hard-wiring/ProgramBit construction on pp. 31–32 and the
modified-rule option in Gacs sections 9.2–9.3. The candidate-B Flag2 and voted-old-
Signal choices remain explicit modifications, with the source qualifications
recorded in the earlier reports. No full amplification theorem is inferred.

E is the relation implemented in `compact16_holder_period_relation.py`. At a
boundary, physical Address is position modulo Q and Age is zero. Metadata is
the fixed ROM; Data copies are coherent; heads, all controllers, all mail words,
flags and Wf are zero. Non-MEM Data is zero. Every colony's 154 Info fields encode
iota(y); other MEM scratch and physical Signals may be arbitrary. The upper y
is any typed G configuration, including active controllers and noncanonical
upper geometry. Upper Address remains 15 bits and Age 32 bits; their high bits
are admitted. Only lower canonical geometry uses a 14-bit address and 30-bit clock.

All raw F outputs are checked to fit their declared physical widths on all typed
raw inputs. Ten guarded hop decrements use the existing unsigned nonzero-guard
bound, rather than discarding overflowing bits. ROM fields are checked at every
one of the Q addresses. These are alphabet-closure checks, not evidence for
repair of arbitrary oversized or otherwise malformed Info encodings.

## Structural induction, proved again for the smaller rule

New descriptor checks cover all 2^30 normalized physical Ages; no old-Q clock
transfer is used. Nine cases (quiet and eight active phases) establish routing,
zero inactive controllers, and the five-copy output image. They use coherent
static/Data/controller inputs and at most one head locally; mail replicas,
physical flags, Signals and Wf are arbitrary. The raw-mail factorization keeps
actual majority correction and per-holder Flag1 masking explicit.

There is one first marker at 0 and one last marker at 16353. The finite endpoint
check covers all 32708 directed positions in the 16354-cell core. Heads reflect,
wait or halt inside it. The gap between neighboring cores is 30 cells, exceeding
the required eight. Full-descriptor support checks preserve all 49 static wires
and bound logical head/controller dependencies by one site. Thus every local
head case applies, disjoint routing keeps at most one head per core, and the
output-image identities restore coherent Data/controllers. Resets and the first
vote introduce a head only at the unique first record. These facts inductively
preserve the structural domain for every physical tick.

An additional complete-descriptor context identity applies even to arbitrary raw
procedure fields: removing physical flags/Signals/Wf leaves Data and controller
outputs unchanged; mail outputs are masked by actual computed holder Flag1.
The remaining context outputs follow the independently checked boundary formulas.
This extends the zero-context instruction paths to retained arbitrary Signals.
The erasure is a mathematical comparison map, never a physical operation.

Counts: 365 head-routing identities, 95995 inactive-controller bit implications,
324 coherent five-replica groups, 1080 masked-mail-copy identities, nine complete
raw-mail cases, and the full 154-output context factorization. These are local
identities plus a spatial induction, not a trace sampled over physical Ages.

## Induction through one complete period

1. **Entry and reset.** E supplies the structural premises. The quiet reset
   identity clears all 3298 MEM scratch locations and retains every Info word,
   creating the initial head and PC from the actual ROM header. Layout checks
   include tail cells. The entry diagnostic validates all 16384 sites with
   nonzero scratch and arbitrary retained Signals, decodes all fields of a seeded
   complete parent, and compares 317 full scalar/native first-reset outputs.
   The mathematical reset argument uses the all-clock quiet/context identities
   for all E inputs, not only these concrete witnesses. The separate stationary-
   Signal reset BDD is supplementary and is not misapplied to arbitrary E Signals.

2. **Sparse gathers and actual physical events.** The compact instruction,
   dispatch and META path certificates from [the path report](COMPACT16_PATHS_AND_MAIL.md)
   justify complete controller paths with arbitrary operands under their guards.
   Raw-mail and context identities handle physical delivery, write priority and
   retained Signals. Packet flight and the actual schedule establish elapsed
   arrival times, MEM targets, no interfering accesses and collision exclusion.
   There are no forcing flags in the gather/evaluation prefix. Each actual read,
   write, emission and delivery can therefore be identified by induction with the
   corresponding symbolic event. The new timed checker verifies all 671760 reads,
   326070 writes and 26790 deliveries in its fifteen-symbolic-colony presentation.
   Event ordering gives exactly the same operands and results as the actual ROM
   instruction calculation. These diagnostics do not execute physical evolution.

3. **Sparse histories and votes.** Only 689 mutable input operands used by the
   complete optimized descriptor need histories. There are 2067 history words
   and 689 vote cells. All 154 Info fields remain present and unchanged during
   gathering; unlike the older dense layout, unused input metadata is not rewritten.
   Each collected operand has three equal copies from the intended neighbor.
   Both late resets preserve these operands, and votes use old Data and override
   simultaneous reset. After each gather, every head/controller/mail word is zero
   before the next barrier; quiet evolution retains Data. The first vote at old
   Age 84000000 bootstraps evaluation from these voted operands.

4. **Complete self-evaluation.** Forty-nine required metadata operands are
   regenerated by executed reads of the same ROM using the voted represented
   Address. The complete optimized descriptor is equivalent to F on every typed
   raw input, including every controller field. Output metadata is regenerated
   from the computed Address, so Hold equals iota(G(y)). All 7350 symbolic lookup
   calls in the timed proof have a possible query mask at most 16383, including
   zero-offset queries and computed output Address; values are checked, not
   truncated by the checker. The padded physical META paths have the required
   address-independent duration, keeping colonies synchronized.

5. **Capture, forcing and second evaluation.** Ten zero-hop sends fill the two
   five-holder Signal buffer groups. Checked destination/source access ordering
   preserves their equal low bits until capture at old Age 495999999. The minimum
   delivery margin is 40878646 ticks. Subsequent majority voting preserves the
   captured primary bits. All packets have ended before forcing; no late SEND can
   be lost to holder masking. Arbitrary old Wf is replaced by zero at Age 500032768;
   directed flag ancestry clears both flags by 500049152. The precommit HALT is
   valid despite intermediate flags by context independence. At old Age 502000000
   reset/vote uses the preserved histories, and the second evaluation again returns
   exactly iota(G(y)). It halts at 872794231 with no pending mail. Quiet evolution
   preserves Hold until commit. See [the barrier report](COMPACT16_BARRIERS.md).

6. **Commit and the entire restored relation.** At old Age U-1 each Info copies
   its adjacent Hold. Info/Hold are disjoint and internal to the colony, so all
   154 fields become iota(G(y)). Age wraps to zero; canonical Address and fixed
   metadata persist. Coherent Data, zero complete controllers/mail, zero flags/Wf
   are restored. Non-MEM Data stays zero: resets, votes, commits, actual writes and
   delivery targets only affect MEM cells, and the first record is MEM. Scratch
   and Signals are permitted by E. Consequently the next state belongs to E(G(y))
   immediately at commit; no host cleanup or additional physical reset is inserted.

The finite checker verifies all intervening clock interfaces, including absence
of an unaccounted reset/vote/commit between quiescence and the next barrier:

| Phase | Quiet from Age | Next barrier old Age |
|---|---:|---:|
| Gather 0 | 25859266 | 28000000 |
| Gather 1 | 53859264 | 56000000 |
| Gather 2 | 81859263 | 84000000 |
| First evaluation | 455121353 | 500000000 |
| Precommit halt | 500005522 | 502000000 |
| Final evaluation | 872794231 | 1073741823 |

Capture and forcing can occur inside these quiet intervals. Their physical effects
are supplied by the context/barrier identities; inactivity of the program alone
would not justify skipping them in an execution backend.

## Ring size, repetition and depth

The open-lattice checker uses independent source labels -7 through 7. It checks
45 source-access disjointness conditions: omitted incoming gather deliveries
cannot affect source program reads or writes. It delivers 1776 foreign messages
to the central histories and then only ten local Signal messages. Both central
evaluations and commit equal the full normalized descriptor output. It never
uses the diagnostic periodic destination. Substituting y[(k+j) mod N] for each
independent source establishes the same value identity for every N>=1, including
repeated inputs when N<15. Packet collision checks are modulo Q; equal-PC emissions
remain Q-spaced, and finite hop counts include repeated ring crossings. Translation
also gives the infinite-lattice result.

Thus F^U(E(y)) is contained in E(G(y)) on an NQ-cell ring for every N>=1 and on the
infinite lattice. Canonical lower metadata remains normalized at every tick,
so iota pi is the identity there and projection gives simulation of G by G itself.
All typed upper states are allowed. Reapplying the relation gives successive
macrosteps, including active upper computation, without reinitialization. Nesting
the same relation d times yields a decoded G step after U^d physical ticks on
Q^d blocks for each finite d. Depth changes the initial encoded configuration,
not the physical alphabet, ROM, registers, neighborhood or transition.

Finite-depth termination may use the previously checked compact boundary orbit
as top data, under the same G. This remains a noiseless boundary construction;
the permanent Address-defect examples preclude calling it robust. No special
top kernel or host replacement of simulated dynamics is part of this argument.

## Evidence, commands and outstanding work

All new proofs are CPU diagnostics. No GPU job/build, shared source, prior sealed
source or historical dataset changed. The old evidence chain is verified by the
new sealer. The former execution baseline remains separate.

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_holder_structural_v1_watch.json --seconds 180 --rss-mib 768 -- python -m experiments.fixed_rule.certify_compact16_holder_period_foundations --part structural --output figs/fixed_rule/compact16_holder_structural_v1.json > figs/fixed_rule/compact16_holder_structural_v1.log 2>&1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_holder_semantic_v1_watch.json --seconds 180 --rss-mib 768 -- python -m experiments.fixed_rule.certify_compact16_holder_period_foundations --part semantic --output figs/fixed_rule/compact16_holder_semantic_v1.json > figs/fixed_rule/compact16_holder_semantic_v1.log 2>&1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_holder_period_entry_v1_watch.json --seconds 180 --rss-mib 512 -- python -m experiments.fixed_rule.validate_compact16_holder_period_relation --output figs/fixed_rule/compact16_holder_period_entry_v1.json > figs/fixed_rule/compact16_holder_period_entry_v1.log 2>&1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_holder_noiseless_period_v1_watch.json --seconds 120 --rss-mib 768 -- python -m experiments.fixed_rule.compose_compact16_holder_noiseless_period --output figs/fixed_rule/compact16_holder_noiseless_period_v1.json > figs/fixed_rule/compact16_holder_noiseless_period_v1.log 2>&1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_holder_period_tests_v1_watch.json --seconds 120 --rss-mib 768 -- python -m unittest tests.fixed_rule.test_compact16_holder_noiseless_period -v > figs/fixed_rule/compact16_holder_period_tests_v1.log 2>&1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.seal_compact16_holder_period
```

| Check | Result | Check seconds | Watch seconds / sampled child KiB |
|---|---|---:|---:|
| Structural invariant | All nine raw-mail/head/image cases and context | 16.662432 | 17.633084 / 113812 |
| Timed/open semantics | Complete own-ROM output, queries, types/layout | 7.331231 | 8.232546 / 157376 |
| Entry | 16384 sites, 317 scalar/native resets | 11.603002 | 11.890838 / 43836 |
| Period interfaces | All six phase joins | 1.424176 | 2.395688 / 75624 |
| Focused tests | Eight PASS | 5.727 | 6.656530 / 167240 |

All exit zero; watchdogs sampled direct children and exclude parents. Structural
and semantic checks overlapped, with combined sampled peaks below 300 MiB. Other
checks ran afterward. Total task memory stayed far below 40 GB.

Mutation tests reject a missing phase/controller output, late halt, old clock,
inadequate core separation, missing independent-mail premise, overwide metadata
query/output, changed static alias, removed endpoint, erased history, changed ROM
literal and reversed routing. Scrambling unused periodic destination labels still
passes the open identity. The existing guarded-decrement checker/tests remain
unchanged; this candidate reruns complete output bounds on the new descriptor.

Next is validated compact physical execution and successive decoded periods,
then depth-two GPU runs and cross-level faults. U^2=2^60 remains too large for
literal dense stepping; this proof is not a measured runtime improvement or a
general acceleration license. A private execution backend must preserve the
actual local dynamics and discharge its own reduction/parity obligations.
General amplification, malformed-encoding repair, boundary reliability, depth
three and the source-fidelity qualifications remain unresolved. Full goal active.
