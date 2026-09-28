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

## Latest progress: implemented fixed retimed candidate

[RETIMED_HOLDER.md](RETIMED_HOLDER.md) records the actual globally fixed U=2^31
candidate, half the reference period. Scalar, full descriptor and native CPU
transition include the new wrap. Q=32768, raw/projected state widths and radius
remain unchanged, independently of initialized depth. The 32-bit raw Age field
is retained. No hardware register or depth-selected transition was introduced.

The candidate's own ROM has 17809 instructions and 27721 core cells. Its complete
self-description includes the retimed evaluator. Controller paths use 2001129064
ticks. The independent expression validator checks all 154 raw outputs; symbolic
ROM execution includes both evaluations, all histories, own metadata and commit.

The all-clock bridge checks all 2^31 legal ages in 22 intervals: all 153 non-Age
outputs equal the reference at matching clock signatures, with all remaining raw
fields arbitrary. The new modulo-U Age output is checked separately. Actual
new-ROM guards/timing pass for 17712 ordinary paths, 392 META cases and 17810
dispatch paths. No old numerical path catalog is treated as a new-ROM certificate.

All six schedule phases fit, checking 28542 instructions and 6478 SEND sites.
Timed symbolic execution checks 748575 reads, 328650 writes and 97170 deliveries;
all raw committed outputs agree with the new complete rule. All 5880 metadata
query checks stay within 15 bits. The open-lattice identity uses independent
-7..7 inputs, not periodic aliasing. New Signal/flag formulas, clearing and
capture-buffer timing also pass. Flags clear by 1230098304, before final
evaluation at 1232000000.

Ten literal/compiler tests pass in 9.763 s; seven new composition failure tests
pass in 2.644 s. Tests reject old wrap, omitted controller output, old path
catalogs, changed durations, MEM aliases, packet collisions, late accesses and
oversized queries. Literal commit/wrap/reset cones and native active controller
events pass. Depths 1–3 identity/encoding checks remain initialization checks.

The first query-bound diagnostic failed on a symbolic vocabulary mismatch. Its
source/log are retained. Version 2 uses the independent structural width bound,
changes no transition, and reproduces the successful timed result. All runs used
a 512 MiB virtual-memory ceiling; largest certificate RSS 195808 KiB. Exact
commands/results and limits are in RETIMED_HOLDER.md. The evidence index at
figs/fixed_rule/retimed_holder_evidence_index_v1.json records nine successful
manifests and two test logs, with source/input hashes checked after completion.

Owned additions: retimed_holder*.py in gacsca/fixed_rule; retimed ROM dataflow,
clock/path/schedule/timed/open/query/Signal diagnostics in experiments/fixed_rule;
test_retimed_holder.py and test_retimed_holder_composition.py; RETIMED_HOLDER.md
and the matching figs/fixed_rule evidence. Old candidates remain frozen.

## Preserved reference and unresolved requirements

[NOISELESS_MACROSTEP.md](NOISELESS_MACROSTEP.md) retains the certificate-assisted
period proof for the original small_holder rule/ROM: F^U(E(y)) subset E(G(y)) at
complete descriptor semantics. Its physical execution evidence remains two
one-link periods plus limited nested windows, not a complete upper period at
depth two. [IDENTITY_COMPILER.md](IDENTITY_COMPILER.md) retains the intermediate
optimized-ROM candidate and [BACKEND_DISTANCE_AND_COST.md](BACKEND_DISTANCE_AND_COST.md)
the reference backend audit and costs. Existing GPU artifacts do not certify
the new retimed ROM/wrap. A full-ring compressed allocation/staging estimate is
about 7.14 GiB for the reference; the separate reservation is still pending.

Next: explicitly compose the retimed whole-period induction, transferring
canonical structure/context/mail/quiet-barrier identities through the clock
bridge and checking new layout, typing and phase interfaces. Then validate the
retimed backend and successive physical periods. Do not infer a completed
retimed macrostep theorem merely from green conditional catalogs.

U^2 is still 2^62 physical ticks at depth two. Further evaluator/layout changes
or proved acceleration are needed for a practical complete nested run. General
cross-level correction, noisy amplification, malformed-Info repair and reliable
finite-cap repair remain open. Candidate-B Flag2, voted-old-Signal D10 and the
printed Flag2/SimBit ambiguities are unchanged. The historical third-link process
was absent on the latest read-only check; this is not a completion audit.

Previous handoff: STATUS_BEFORE_RETIMED_HOLDER_20260926.md. Older status archives
and their reports remain intact. Please use MAIN_AGENT_NOTES.md for replies.
