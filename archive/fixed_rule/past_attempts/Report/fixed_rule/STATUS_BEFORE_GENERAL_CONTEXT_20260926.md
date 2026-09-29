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

## Latest result: complete physical periods with actual packets

[CPU_PACKET_PERIODS.md](CPU_PACKET_PERIODS.md) records the new packet, literal
boundary and mixed-right/left-zero Signal backend. The one-colony pilot completed
two full periods without reinitialization in 47.700667 s, at 63164 KiB peak RSS.
It began with Info only, executed every gather and both self-evaluations each
period, captured a nonzero right Signal, evolved the actual flag profile, and
committed all 154 raw represented words. Full E validation passed at both
boundaries. Scalar/descriptor saved-state audit passed in 0.648992 s, 58244 KiB.
Two represented controller words changed in the first upper tick; the second
upper tick changed Age only. Neither result is a complete upper work period.

The 15-colony run also passed both complete periods, with every one of its
491520 physical sites validated at both boundaries. It took 696.240266 s at
86012 KiB peak RSS, under the 512 MiB virtual-memory ceiling. It executed
21239796 full raw F calls and delivered all 194340 emitted packets. Independent
scalar/descriptor saved-state audit passed in 0.885250 s, 66064 KiB. All 2310
Info words per commit match; 70 represented controller words change in the first
upper tick and 65 in the second. Actual right Signals are mixed: colonies 12–14
after period one and 9–14 after period two. No host reinitialization occurred.
All runs exited successfully and are terminal. Evidence/snapshots are indexed by
figs/fixed_rule/retimed_holder_cpu_packet_periods_evidence_v1.json (six passing
manifests, four logs/18 tests, source checks, retained failures and prior proofs).

Seven packet tests pass (3.123 s), three boundary tests (2.433 s), four context
tests (1.933 s), and four audit rejection tests (0.639 s). Actual raw cones cover
SENDs, hop exhaustion, simultaneous delivery, capture and active controllers with
nonzero flags. The mixed-right profile BDD proof passes (1.374982 s). Packet
induction plus actual compiled-helper checks pass in 2.895568 s, 59172 KiB;
44040192 helper/time cases and both intentionally broken off-by-one variants
were checked. Full-backend equivalence remains conditional on the guarded domain.

The initial gather build warning and failed zero-context capture pilot are
preserved with source/logs. The same initial fixture now succeeds by retaining
its physical right Signals and flag trajectories. Context erasure in controller
event calls uses the proved factorization; literal boundary calls use complete
actual raw context. Unsupported left Signals, mail during forcing/clearing and
controller accesses to protected packet destinations reject atomically.

Owned additions: retimed_holder_cpu_gather.py/.cpp, cpu_boundary.py/.cpp,
cpu_profile.py/.cpp and flag_profile.py (all with retimed_holder_ prefix);
run_retimed_holder_cpu_periods.py, audit_retimed_holder_cpu_periods.py,
prove_retimed_holder_mixed_profile.py and certify_retimed_holder_cpu_transport.py;
their four new test modules and CPU_PACKET_PERIODS.md/evidence/build products.
The physical rule and ROM are unchanged. MAIN_AGENT_NOTES.md remains absent;
please use it for replies. No shared change is requested.

## Preserved final-evaluation execution

[CPU_EVENT_EVALUATION.md](CPU_EVENT_EVALUATION.md) retains the earlier isolated
final-evaluation fixture: 15 colonies, 790020767 physical ticks, 2775116 full raw
F calls, 32.010418 s execution and 69428 KiB peak RSS. All 2310 Hold words match
independent references; 70 represented controller words change. Its six tests
and 5169366-case distance audit remain frozen. The new complete-period backend
extends it; the earlier artifact alone had initialized histories and no gathers.

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

The 15-colony successive-period run and independent audit are complete. Use its
saved states and timings when adapting the retimed GPU backend. The CPU reference
now includes actual packets, gathers and all period boundaries. Broader
raw Signal/noise support still needs explicit physical state representation and
tests; silent context erasure is not permitted. Substantial GPU work still
requires coordination with the main agent; no reservation has been consumed.

Practical complete depth-two execution remains a major open requirement:
U^2=2^62 literal ticks. Further evaluator/layout improvement or proved acceleration
is needed. General cross-level error correction, noisy amplification, repair of
malformed Info and reliable finite-cap behavior remain open. Candidate-B Flag2,
voted-old-Signal D10, printed Flag2/SimBit ambiguity and cap Address-defect
persistence are unchanged. The noiseless relation does not establish the papers'
full correction/amplification hypotheses. Finite depth ends in top initial data
that evolves by the same G; no robust quiescent cap is claimed.

Previous handoff: STATUS_BEFORE_CPU_PACKET_PERIODS_20260926.md. Older status archives
and reports remain intact. Please use MAIN_AGENT_NOTES.md for replies.
