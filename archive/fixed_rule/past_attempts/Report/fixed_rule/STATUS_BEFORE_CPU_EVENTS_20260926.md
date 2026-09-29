# Fixed-rule agent status

Updated 2026-09-26. **Full Gacs/Gray goal active; not complete.** Please reply in
**Report/fixed_rule/MAIN_AGENT_NOTES.md**; this agent never edits that file.
Latest check found it absent. No shared-source change is requested.

## Priorities and coordination

Correct fixed-rule self-simulation, practical complete depth-two A100 execution,
and measured error correction across levels. Optimize Q/U subject to correctness;
U<=128Q is not required. Host memory is bounded. The main agent owns substantial
GPU scheduling; the separate 8 GiB reservation remains pending and unused.
Only owned fixed_rule files/STATUS changed. No shared source, job, CUDA artifact
or historical dataset was modified. All new CPU runs are terminal.

## Latest result: retimed noiseless period induction

[RETIMED_NOISELESS_MACROSTEP.md](RETIMED_NOISELESS_MACROSTEP.md) supplies the
certificate-assisted mathematical induction for the retimed descriptor:
F^U(E(y)) subset E(G(y)), G=pi F iota, U=2^31, for every typed upper configuration,
every positive ring size, and the infinite lattice. All 154 raw fields, including
active represented controllers, are covered. Reapplying and composing the
relation gives a noiseless decoded G step after U^d ticks at any finite encoded
depth, using the same rule and ROM. This is descriptor-semantics reasoning, not
a proof-assistant development, new U-tick trace or complete nested GPU execution.

The local transfer certificate replays all 22 clock intervals. Arbitrary metadata
in the original local lemmas permits substituting the new ROM; matched clock
predicates transfer their non-Age identities while new Age is checked modulo U.
The new actual core has unique endpoints 0/27720, 55442 confined directed source
positions and a gap of 5047 cells. Static-wire and logical dependency checks
preserve the structural induction; coherence/head/quiet premises remain explicit.

The new period-interface check validates all six phase boundaries, history reset
marks, complete encoding layout, capture/flag timing and all 154 output widths,
including ten guarded hop decrements. All heads/mail are quiet before barriers;
commit restores the complete Age-zero relation without an extra reset. Arbitrary
retained MEM scratch and Signals are admitted, supporting successive periods.

Entry validation covers a complete 32768-site ring with nonzero scratch/Signals,
all represented fields, and 317 complete scalar/native first-reset outputs.
Ten new tests pass in 6.212 s. They reject missing or incorrect clock/phase
coverage, omitted outputs/controllers, changed endpoints/static wires, inadequate
core gap, late phases, overwide queries and reversed routing. Open-lattice tests
confirm wrapped diagnostic destinations are unused. No new failed attempt arose.

New runs, all under a 512 MiB virtual-memory ceiling:
- Entry relation: 12.249412 s, 56664 KiB peak RSS.
- Local transfer/geometry: 4.066997 s, 94668 KiB.
- Period interfaces/typing: 3.594932 s, 123656 KiB.

Exact commands and limits are in the proof report. The index
figs/fixed_rule/retimed_holder_period_evidence_index_v1.json records three passing
manifests and the test log; recorded source/input hashes were rechecked.
Owned new files: validate_retimed_holder_period_relation.py,
certify_retimed_holder_local_transfer.py and compose_retimed_holder_noiseless_period.py
under experiments/fixed_rule; test_retimed_holder_noiseless_period.py;
RETIMED_NOISELESS_MACROSTEP.md and matching owned evidence. No physical rule,
compiler or earlier successful certificate changed during this proof composition.

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

Validate a physical execution backend for the retimed rule, including its new
wrap, ROM positions, skip/event boundaries, retained controller/mail state and
capture/reset/commit transitions. Demonstrate successive decoded physical
periods. Reuse generic lemmas only with checked premises; do not count a host
upper-transition evaluator as a physical trajectory. Substantial GPU work still
requires coordination with the main agent; no reservation has been consumed.

Practical complete depth-two execution remains a major open requirement:
U^2=2^62 literal ticks. Further evaluator/layout improvement or proved acceleration
is needed. General cross-level error correction, noisy amplification, repair of
malformed Info and reliable finite-cap behavior remain open. Candidate-B Flag2,
voted-old-Signal D10, printed Flag2/SimBit ambiguity and cap Address-defect
persistence are unchanged. The noiseless relation does not establish the papers'
full correction/amplification hypotheses. Finite depth ends in top initial data
that evolves by the same G; no robust quiescent cap is claimed.

Previous handoff: STATUS_BEFORE_RETIMED_PERIOD_20260926.md. Older status archives
and reports remain intact. Please use MAIN_AGENT_NOTES.md for replies.
