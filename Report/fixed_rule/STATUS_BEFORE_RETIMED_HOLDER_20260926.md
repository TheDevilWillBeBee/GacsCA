# Fixed-rule agent status

Updated 2026-09-26. **Full Gacs/Gray goal active; not complete.** Please reply in
**Report/fixed_rule/MAIN_AGENT_NOTES.md**; this agent never edits that file.
Latest checks found it absent. No shared-source change is requested.

## Priorities and coordination

Correct fixed-rule self-simulation, practical two-level A100 execution, and
measured error correction across levels. Optimize Q/U subject to correctness;
U<=128Q is not required. Host memory is bounded. The main agent owns substantial
GPU scheduling; the separate 8 GiB reservation remains pending and unused.
Only owned fixed_rule files/STATUS changed. No shared source, job, CUDA artifact
or historical dataset was modified. All new CPU runs are terminal.

## Latest progress: equivalent compiler and smaller experimental ROM

[IDENTITY_COMPILER.md](IDENTITY_COMPILER.md) documents an actual compile-time
reduction of the complete descriptor: 13442 ->10449 operations (22.27%). An
independent structural normalizer proves all 154 outputs equal on every typed
raw neighborhood, including controllers and damaged geometry. Physical F,
alphabet, radius and opcodes remain unchanged.

A separate fixed hard-wiring in identity_holder_program/projected/initial uses
that expression and its own ROM. Complete symbolic Data flow passes through
three histories, both full evaluations, own-ROM metadata regeneration, Signal
payloads and commit: 428100 instruction occurrences, 2205 META queries, 97170
packet deliveries. This remains conditional on physical instruction/transport
refinement; old-ROM certificates are not silently transferred.

Measured change: stored instructions 20801 ->17808; core cells 30724 ->27720;
controller-path ticks 2802642834 ->2000945998 (28.60% shorter). Installed Q=32768
and U=2^32 are unchanged. The new cost admits a prospective 2^31-period budget,
checked in identity_holder_half_period_budget_v1.json. It is only a proposal:
clock constants/wrap occur in the self-description, so the retimed rule must be
compiled and recertified before claiming an actual halved U. Changing U alone
would leave the old 32-bit wrap incorrect.

Seven tests pass in 1.625 s. They reject untyped mask removal and missing raw
controller output, check arithmetic edge cases and fixed identity at initializer
depths 1–3, and compare 70 complete physical scalar/descriptor outputs during
FETCH, active ALU, SEND and all META selectors at the new ROM endpoint. No full
new-ROM period or depth-two run was executed. The symbolic ROM certificate
passed in 4.926805 s /89860 KiB RSS under a 512 MiB virtual-memory ceiling.

The first two symbolic normalization attempts failed because their width rules
were insufficient; logs and the v2 source snapshot are retained. Neither failure
required a change to the optimizer or physical rule. The successful normalizer,
compiler and artifacts are frozen. Equivalence assumes represented field widths;
malformed oversized Info words still require future legalization/repair work.

Owned additions: word_identity_optimization.py; identity_holder_program.py,
identity_holder_projected.py and identity_holder_initial.py under gacsca/fixed_rule;
small_holder_identity_validation.py, certify_identity_holder_rom.py and
budget_identity_holder_half_period.py under experiments/fixed_rule;
test_identity_holder_compiler.py; IDENTITY_COMPILER.md and matching evidence.
Exact commands, hashes and limits are in the report.

## Preserved verified candidate and execution findings

[NOISELESS_MACROSTEP.md](NOISELESS_MACROSTEP.md) retains the certificate-assisted
period proof for the original small_holder ROM at descriptor semantics:
F^U(E(y)) subset E(G(y)), G=pi F iota. It includes all raw controllers, retained
scratch/Signals, physical packets, barriers, flags and commit for all ring sizes.
It is not a proof-assistant development or a complete nested execution. The
original rule, ROM and execution artifacts remain intact.

[BACKEND_DISTANCE_AND_COST.md](BACKEND_DISTANCE_AND_COST.md) retains the verbatim
CUDA distance audit (5223948 cases, overshoot/wrong-register mutations rejected)
and exact old-ROM work cost. Distance alone does not certify staging/clock/state
reconstruction. The full-ring compressed allocation/staging estimate is about
7.14 GiB; 338 GiB describes a dense packed buffer. The 256-worker launch is a
possible tuning target, but tuning alone cannot remove billions of lower periods.

## Next concrete work and unresolved requirements

Implement a globally fixed retimed candidate, including correct clock wrap and
its own full description. Recompute its ROM/timing, establish the period relation
and validate physical paths/successive periods. Keep the original proved
candidate as the reference. Further evaluator/layout improvements or justified
physical acceleration are still needed for practical complete depth-two work.

Cross-level error correction, noisy amplification and reliable finite-cap repair
remain open. Candidate-B Flag2, voted-old-Signal D10, the printed Flag2/SimBit
ambiguities and cap Address-defect witness are unchanged. Existing executed
hierarchy evidence is two one-link periods plus limited nested windows, not a
complete upper work period at depth two. The last historical third-link check
found no process; that is not a completion audit, and the job/data were untouched.

Previous handoffs are preserved in STATUS_BEFORE_IDENTITY_COMPILER_20260926.md,
STATUS_BEFORE_BACKEND_DISTANCE_20260926.md and STATUS_BEFORE_NOISELESS_MACROSTEP_20260926.md.
Earlier history remains in STATUS_HISTORY_20260926_before_mail_factorization.md.
