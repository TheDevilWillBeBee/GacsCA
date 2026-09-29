# Retimed noiseless macrostep

2026-09-26. The retimed fixed candidate now has a certificate-assisted
whole-period induction at complete word-descriptor semantics. The result is
F^U(E(y)) subset E(G(y)), with U=2^31, its own ROM, and all controller fields.
This closes the composition obligation left by [RETIMED_HOLDER.md](RETIMED_HOLDER.md).
It does not complete the project: practical complete depth-two execution,
backend equivalence at that scope, general noise correction and robust finite
termination remain open. This is a mathematical argument with executable finite
checks, not a proof-assistant development or a newly executed U-tick trace.

## Rule, domain and claim

F is the unsigned-64-bit word descriptor from retimed_holder_rule.self_description():

```
F descriptor 6e2f29f61bf281ec5d346cd58e717cf7e5b0afea263d2c17a18a58de295d8d23
own ROM      4dc026b976c541001421dd214df9c9e33f6f851053d4ba5f53dbbec925ba5645
Q = 32768, U = 2147483648, neighborhood = -7..7
```

Let pi remove the 49 metadata words and iota regenerate them from Address and
this single ROM. Define G=pi F iota, with neighborhood lifting pointwise. Raw F
has 154 words /4090 bits; G has 105 words /2704 bits. Their widths, neighborhood,
transition and ROM are independent of initialized depth. Scalar Python and
native CPU routines have their recorded differential checks; the theorem here
specifies descriptor semantics rather than assuming universal backend parity.

E(y) is the raw block relation in retimed_holder_period_relation.py. Its lower
configuration has canonical Address, uniform Age zero, fixed normalized
metadata, coherent Data, zero head/controller/mail/Flag1/Flag2/Wf, and zero
non-MEM Data. Info encodes all 154 raw fields of iota(y). Other MEM scratch and
physical Signals are arbitrary. Upper y is any typed G configuration; its
controllers may be active and its geometry may be noncanonical. In particular,
upper raw Age may have its high bit set, even though lower physical Age remains
in 0..U-1 along this relation.

On the infinite lattice, or an NQ-cell lower ring for any integer N>=1:

```
F^U(E(y)) is contained in E(G(y)).
```

All 154 outputs are proved to fit the fixed alphabet on every typed raw input.
The ten hop decrements use the explicit nonzero-guard argument from the
reference proof. ROM typing was checked across all Q addresses. No output is
truncated by the proof checker. Unrestricted oversized Info words outside their
represented field widths are not in E; repair of that domain is still open.

## Why the local lemmas transfer

The [reference proof](NOISELESS_MACROSTEP.md) supplies local head, procedure,
context, mail and quiet-barrier identities. Their symbolic inputs include
arbitrary metadata words, not just reference-ROM values. The current source
audit confirms that the coherent metadata variables are independent at each
logical site. Head/structure and mail lemmas retain their coherent-procedure,
zero/one-head premises; quiet barriers retain zero head/controller/mail premises.
The context lemma needs only canonical Address and uniform Age.

For each new legal Age a, the clock certificate selects an old legal Age b with
the same active/third-stage, reset-index, vote-index, capture, Wf-window and
commit predicates. For canonical Address, arbitrary other raw fields and every
a in its checked interval, all 153 non-Age outputs of F_new(x) equal those of
F_old(x with uniform Age replaced by b). The remaining output is proved exactly
Age'=(a+1) modulo U. Twenty-two intervals partition all 2^31 legal Ages.

Substitute each local lemma's admissible input into that identity. Its non-Age
conclusion follows for the new rule, with the matched clock predicates. The
separate Age identity preserves uniform legal geometry. This is a pointwise
argument, so b need not form an old trajectory as a increases. Context/mail
erasure maps occur only within identities; no erasure is inserted into the
physical trajectory. Actual paths and timing come from the new ROM certificates.

The transfer checker replays the complete clock identity, verifies all nine
head/image/mail cases, checks source/dependency hashes, and inspects the new
spatial structure. There is exactly one first marker at 0 and one last marker
at 27720. All 55442 directed core positions stay within the 27721-cell core.
The gap to the next core is 5047 cells, exceeding the eight-cell requirement
for the local zero/one-head cases. The new descriptor preserves all 49 static
wires; Data/head/controller/Wf outputs read old logical head/controllers only
at offsets -1,0,1 from their primary. Thus disjoint routing, coherent output
images and zero inactive controllers preserve the canonical structural domain
for every physical tick, with arbitrary raw mail, flags, Signals and Wf.

## Induction through one work period

1. **Entry and first reset.** E supplies the structural domain. At old Age zero,
   the quiet-reset identity clears marked scratch, retains Info and creates
   the unique first head with the actual first entry PC. Layout checks include
   the tail MEM cells, disjoint adjacent Info/Hold pairs, exact vote/Info marks,
   and preservation of all history operands across the late resets. A separate
   diagnostic validates all 32768 physical entry sites with nonzero scratch and
   Signals, decodes the complete parent, and checks 317 complete scalar/native
   first-reset outputs. The mathematical reset argument applies to all E inputs.

2. **Instruction and packet induction.** Starting with the first entry, use the
   new dispatch, ordinary and META refinements. They retain the entire controller
   and check actual ROM guards, read/write locations, emission and successor
   timing. Every actual META query is within the certified 15-bit domain. The
   transferred context identity permits arbitrary retained Signals; the raw-mail
   factorization accounts for each physical delivery and write/send priority.
   Packet-flight induction counts actual colony-boundary crossings. New schedule
   checks exclude same-track overwrites and all destination accesses at/after
   delivery. Timed symbolic reads/writes agree with the instruction calculation,
   so values and events advance together by mutual induction. Payload-independent
   path times, including padded META scans, maintain the synchronized schedule.
   The prefix has zero Wf and flags, so every live packet has zero masking Flag1.

3. **Three gathers and their barriers.** Each gather halts and consumes all
   packets before the next reset or vote. Inactive-controller closure and the
   packet formulas give zero complete controller/mail words, not just head or
   valid bits. Quiet evolution preserves Data until the next barrier. The three
   histories normalize and store the complete neighbor states. History marks
   preserve earlier copies; at the vote at old Age 430000000, equal histories
   vote to their common value and bootstrap the first evaluation. The open-lattice
   identity supplies independent neighbor inputs rather than assuming a fixed
   periodic ring size.

4. **Full self-evaluation and Signal capture.** The compiled program evaluates
   every output of F, including its own evaluator's next controller and transport
   state. Executed META reads of this same ROM normalize output metadata, giving
   Hold=iota(G(y)), including when the represented upper Address changes. Ten
   zero-hop sends distribute Flag1/Flag2 payloads to the two five-buffer groups.
   The source words remain unchanged between sends. All deliveries finish by
   Age 1220580247, strictly before capture's old Age 1223999999. No intervening
   reset/vote/commit, write or packet changes those buffers. Capture reads old
   corrected Data; subsequent Signal voting preserves the common bits.

5. **Forcing, clearing and final evaluation.** There is no live packet or SEND
   during or after Wf forcing. The precommit HALT can occur with nonzero flags:
   canonical geometry and the context lemma protect Data/controllers. Wf is zero
   at Age 1230065536; directed flag ancestry clears both flags by 1230098304,
   before the simultaneous final reset/vote at 1232000000. Voting uses old Data
   and overrides reset clearing; checked history marks preserve its operands.
   The second complete evaluation therefore returns iota(G(y)) again. It halts
   at Age 2022020768 with no packets. Quiet evolution retains Hold until commit.

6. **Commit and restored entry relation.** At old Age U-1, each Info cell copies
   its old adjacent Hold. Disjoint Info/Hold sets lie inside the colony, so all
   154 represented fields become exactly iota(G(y)). Age wraps to zero; canonical
   Address, fixed metadata and Data coherence persist. All heads/controllers,
   all mail words, flags and Wf are zero. Non-MEM Data remains zero because all
   reset/vote/commit marks, controller writes and packet targets use MEM cells.
   Remaining MEM scratch and Signals are permitted by E. This restores every
   entry constraint after exactly U transitions, without an additional reset.

The finite phase-interface check ensures there is no unaccounted reset, vote
or commit between each completed phase and its next barrier:

| Phase | Quiet from Age | Next barrier's old Age |
|---|---:|---:|
| Gather 0 | 147373066 | 150000000 |
| Gather 1 | 286894530 | 290000000 |
| Gather 2 | 426894531 | 430000000 |
| First evaluation | 1220580247 | 1230000000 |
| Precommit halt | 1230016977 | 1232000000 |
| Final evaluation | 2022020768 | 2147483647 |

The separate timing/Signal certificates allow the capture and forcing events
inside the quiet intervals; their Data/controller effects are supplied by the
quiet/context identities. A mere absence of instruction events would not
justify skipping those events in an execution backend.

## Arbitrary rings, repeated periods and depth

The open-lattice checker gives the central complete identity with independent
inputs at integer offsets -7..7. Gather programs never access foreign delivery
targets, so omitted deliveries cannot affect source computation. All subsequent
packets have zero colony hops. Translate the identity to colony k and substitute
y[(k+j) mod N] for each independent input. This substitution permits repeated
inputs for N<15. The modulo-Q collision check covers all translated emissions;
equal-PC packets remain Q-spaced, and hop counters count repeated ring crossings.
The same local argument covers the infinite lattice.

Along E trajectories metadata stays normalized, so iota pi is the identity.
Project the inclusion to obtain block simulation of G by the same G. Reapply
after each macrostep: arbitrary retained scratch/Signals mean that no external
cleanup is needed. Compose the block relation d times to obtain a decoded G
step after U^d physical ticks on Q^d blocks, for every finite d. This is a
consequence of the induction, not a measured nested execution.

Depth is initial encoded data. At a finite chosen top configuration the same G
continues to act; no top-specific transition kernel is introduced. This does
not prove a noise-stable or quiescent cap. Gray pp. 31–32 motivates the hard-wired
ProgramBit projection; Gacs sections 9.2–9.3 permits the modified self-correcting
rule family. The theorem here does not establish their full amplification
hypotheses. Candidate-B Flag2, voted-old-Signal D10 and the previously recorded
source ambiguities remain explicit.

## Reproduction and limits of the evidence

All commands used `ulimit -v 524288` and `OPENBLAS_NUM_THREADS=1`, from the repo
root, with matching log files. No GPU job, CUDA build or shared file was changed.

```
python -m experiments.fixed_rule.validate_retimed_holder_period_relation --output figs/fixed_rule/retimed_holder_period_relation_v1.json
python -m experiments.fixed_rule.certify_retimed_holder_local_transfer --output figs/fixed_rule/retimed_holder_local_transfer_v1.json
python -m experiments.fixed_rule.compose_retimed_holder_noiseless_period --output figs/fixed_rule/retimed_holder_noiseless_period_v1.json
python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_noiseless_period.py -v
```

| Check | Result | Seconds | Peak RSS, KiB |
|---|---|---:|---:|
| Entry relation | Full 32768-site ring, 317 complete reset outputs | 12.249412 | 56664 |
| Local transfer and new geometry | Full clock replay; 55442 directed positions | 4.066997 | 94668 |
| Period interfaces and typing | Six phases; 154 output widths; ten guarded decrements | 3.594932 | 123656 |
| Focused tests | Ten passed | 6.212 | Not separately measured |

Tests reject omitted clock intervals, incorrect clock modes, missing old phase
coverage, omitted raw outputs, restricted context, changed endpoints/static
wires, inadequate core gap, missing represented controllers, late computation,
invalid query widths and packets after forcing. Guarded-decrement tests include
exhaustive small inputs and missing/wrong-guard mutations. Scrambling diagnostic
wrapped destinations leaves the open-lattice identity intact; reversing actual
routing fails. All three manifests retain exact source/dependency hashes.

The new result certifies the noiseless relation at descriptor semantics. It
provides no general equivalence proof for the scalar, native or event backends.
The earlier literal tests and complete reference-ROM executions retain their
original scopes. The next task is retimed physical execution with a separately
validated backend and successive decoded periods. Practical complete depth-two
execution still faces U^2=2^62 ticks; further evaluator/layout improvement or
proved acceleration is necessary. General cross-level correction, noisy
amplification, malformed-encoding repair and robust cap behavior remain open.
