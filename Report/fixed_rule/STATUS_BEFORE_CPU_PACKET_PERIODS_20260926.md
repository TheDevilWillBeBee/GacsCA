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

## Latest result: physical final-evaluation execution

[CPU_EVENT_EVALUATION.md](CPU_EVENT_EVALUATION.md) documents a private bounded
CPU event executor for the retimed rule. It calls the complete compiled physical
F at events and skips only checked travel segments. It retains actual Data and
complete controllers; no represented upper transition evolves the stored world.
The current domain is canonical coherent zero-context/mail states within one
regular clock interval. SEND, clock-boundary crossing and exhausted budgets are
rejected atomically. It does not yet run gathers or complete periods.

The entire final evaluation ran on 15 physical colonies from explicit initialized
history fixtures: 790020767 physical ticks per colony, 1067538 total event ticks,
2775116 complete raw F calls, 32.010418 s execution, 69428 KiB peak RSS. All 2310
raw Hold words match the intended upper result. Seventy represented controller
words change. Heads are present one tick before the expected halt and every
controller word is zero after it. The one-colony pilot also passes in 2.461932 s.

An independent audit recomputes the saved output hashes using both scalar F and
direct word-descriptor evaluation. The represented upper rule is diagnostic only.
The distance audit rechecks the frozen CUDA function against the new ROM in
5169366 cases and rejects overshoot/wrong-register mutations. Six tests pass in
2.174 s, including complete three-tick raw cones for 22 controller cases/all META
selectors, boundary guards, and atomic emission/budget rejection.

All commands used a 512 MiB virtual-memory ceiling, with no GPU or CUDA rebuild.
The largest new RSS was about 68 MiB. Commands, exact costs, domains and evidence
are in the report. figs/fixed_rule/retimed_holder_cpu_events_evidence_v1.json
indexes four passing manifests and the test log; source/input hashes are checked.
No new failed attempt occurred. All runs are terminal.

Owned additions: retimed_holder_cpu_events.py/.cpp and retimed_holder_quotient.py
under gacsca/fixed_rule; certify_retimed_holder_backend_distance.py,
run_retimed_holder_cpu_evaluation.py and audit_retimed_holder_cpu_evaluation.py
under experiments/fixed_rule; test_retimed_holder_cpu_events.py; the report and
matching evidence/build products. The physical rule, compiler and ROM are intact.

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

Extend the portable physical event executor to actual emitted packets/local
transport and to reset/vote/capture/commit boundaries. Test simultaneous events
and complete state reconstruction against literal F. Replace initialized histories
with executed gathers, then demonstrate successive complete physical periods and
decoded controller dynamics. Use the CPU result as a measured reference when
adapting the retimed GPU backend. Substantial GPU work still requires coordination
with the main agent; no reservation has been consumed.

Practical complete depth-two execution remains a major open requirement:
U^2=2^62 literal ticks. Further evaluator/layout improvement or proved acceleration
is needed. General cross-level error correction, noisy amplification, repair of
malformed Info and reliable finite-cap behavior remain open. Candidate-B Flag2,
voted-old-Signal D10, printed Flag2/SimBit ambiguity and cap Address-defect
persistence are unchanged. The noiseless relation does not establish the papers'
full correction/amplification hypotheses. Finite depth ends in top initial data
that evolves by the same G; no robust quiescent cap is claimed.

Previous handoff: STATUS_BEFORE_CPU_EVENTS_20260926.md. Older status archives
and reports remain intact. Please use MAIN_AGENT_NOTES.md for replies.
