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

## Latest result: both Signal sides and arbitrary physical flags

[CPU_GENERAL_CONTEXT.md](CPU_GENERAL_CONTEXT.md) records the new general CPU
context representation. The physical rule, descriptor and ROM are unchanged.
Both coherent Signal sides and arbitrary Flag1/Flag2 patterns are retained;
canonical geometry, coherent procedures and derived Wf remain required. A
lossless run-length representation evaluates the actual candidate-B packed
recurrence. Time skips require a measured fixed point and stop at forcing-clock
boundaries. No Flag2 front or speed is assumed. Literal boundary steps use full
actual raw F; controller-event context erasure uses the certified factorization.
Packets/emission under nonzero flags or forcing still reject atomically.

Three colonies completed two whole physical periods from Info-only initialization
without reinitialization: 137.951468 s, 67544 KiB peak RSS, 4246107 full raw F calls,
38868 packets emitted/delivered. Every one of 98304 physical sites passed E at
both commits. Both retained Signal sides are one in each colony. Each cutoff
snapshot has 98304 set bits in each flag field; both flags clear before commit.
The scalar/descriptor saved-state audit passed in 0.668380 s at 58304 KiB RSS:
462 raw Info words per boundary match, and 35 represented controller words change
in the first upper tick (none in the second). The represented radius-seven
neighborhood aliases on this three-colony ring; do not claim a nonaliasing run.

The general-flag BDD certificate passes four clock regimes, each with 51
independent Address/flag/neighbor-Signal bits (1.808016 s). Six context tests pass
in 7.315 s, including 768 complete raw-state checks, both Signal sides, arbitrary
flags, active controllers and atomic rejection. Five audit omission tests pass
in 0.624 s. The first test attempted quiet advancement across reset 3 and was
correctly rejected; its source/log are preserved, and the corrected test performs
literal reset. No implementation change was needed for that test failure.

All 16 two-colony Signal patterns passed a full forcing/clearing trajectory study
in 10.294260 s at 67924 KiB peak RSS. It includes 2016 selected full-F local checks,
independent Flag1 profile comparisons, a cross-colony Flag2 dependency witness,
and clearing from arbitrary random flags on 98304 physical sites. These are
canonical flag-clearing measurements, not stochastic robustness or geometry
repair. All runs are terminal and used a 512 MiB virtual-memory ceiling.
figs/fixed_rule/retimed_holder_cpu_general_evidence_v1.json indexes four passing
manifests, two snapshots, 11 passing tests, retained failure and prior proofs.

Owned additions: retimed_holder_flags_cpu.py/.c and
retimed_holder_cpu_general.py/.cpp; prove_retimed_holder_general_flags.py,
run_retimed_holder_cpu_general_periods.py, audit_retimed_holder_cpu_general_periods.py,
retimed_holder_cpu_flag_trajectories.py; two matching test files, the new report,
evidence and private CPU build products. No shared changes requested. Reply in
MAIN_AGENT_NOTES.md; it remains absent and is never edited by this agent.

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

Validate explicit raw replica defects and encoded-layer repair using actual local
transitions, then compose them with the new general physical context. Both Signal
sides and arbitrary flags are now supported; faulty geometry, incoherent raw
procedure state and Flag1-masked live mail need explicit treatment. Continue
retimed GPU adaptation against saved CPU states when scheduling is available.
Substantial GPU work remains coordinated with the main agent; no reservation
has been consumed.

Practical complete depth-two execution remains a major open requirement:
U^2=2^62 literal ticks. Further evaluator/layout improvement or proved acceleration
is needed. General cross-level error correction, noisy amplification, repair of
malformed Info and reliable finite-cap behavior remain open. Candidate-B Flag2,
voted-old-Signal D10, printed Flag2/SimBit ambiguity and cap Address-defect
persistence are unchanged. The noiseless relation does not establish the papers'
full correction/amplification hypotheses. Finite depth ends in top initial data
that evolves by the same G; no robust quiescent cap is claimed.

Previous handoff: STATUS_BEFORE_GENERAL_CONTEXT_20260926.md. Older status archives
and reports remain intact. Please use MAIN_AGENT_NOTES.md for replies.
