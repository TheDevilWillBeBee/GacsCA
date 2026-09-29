# Executed wider repair; final quiet-recovery audit pending

2026-09-27. The actual 73-colony lower trajectory now reaches a faulty decoded
commit and then repairs the decoded upper state after two more lower periods.
Every raw field in the central 17 decoded cells matches the corresponding
complete-upper-colony trajectory. A third period refreshes the lower histories.
Three explicitly retained inert nonMEM words persist.

**Verification status:** the independent noisy-commit trace audit, subsequent
endpoint audit, literal reset-entry check and upper-alignment comparison pass.
The full every-tick quiet-recovery audit is still running in version 2. Version 1
hit its 900-second wall limit after reporting tick 10240 without a mismatch.
Do not treat this interim report as an independently audited complete chain.

The full-Q lower physical embedding remains unproved. The upper halo fixes the
earlier narrow-window contamination of the central decoded comparison; it does
not by itself establish physical equivalence outside the 73 lower colonies.
No general amplification, stochastic threshold or complete physical erasure is
claimed. The full project goal remains active.

## Actual physical trajectory

The starting point is the audited 73-colony burst in
[COMPILED_EVENTS_AND_WIDE_BURST.md](COMPILED_EVENTS_AND_WIDE_BURST.md), using
complete inherited depth-two banks and the real upper NAND context. Its state
is continued unchanged, without inserting a decoded error into a new fixture.

The GPU executes 16384 quiet physical ticks in **176.831657 s**, ending at
local time 1232635846. Flags are zero; 19 sites /90 raw words differ from the
matched healthy trajectory, across colonies 36 and 37. The two extra heads are
at global physical positions 1227024/1227025. Complete banks, controllers,
Signals, flags and nonMEM Data remain represented. Explicit GPU allocation is
47576706 bytes; process peak RSS is 630524 KiB.

The compiled physical scheduler then reaches U and U+1 in **252.522558 s**.
Only colony 37 commits a wrong decoded record: the complete raw record is zero,
with 12 mutable-field differences. Every other colony decodes the intended
transition. Reset creates one head at address zero in each of the 73 colonies.
Three nonMEM Data words remain in colony 36 at addresses 30960–30962.

An independent scalar event-trace audit passes in **874.295199 s**. It checks
all 213322 intervals, 22574855 scalar candidates through 3865839 distinct
complete scalar neighborhoods, all six complete saved checkpoints, 4784128
native clock output states /736755712 raw words, and 1371 full scalar G probes.
The receiving-colony probes use colony 37. This audit verifies 103188 literal
ticks, 792260966 transport ticks, 122483647 quiet ticks and two whole-ring clock
transitions. Process peak RSS is 3321568 KiB. The physical scheduler run itself
peaks at 6185600 KiB.

## Subsequent periods and upper context

Three subsequent actual lower periods execute in **106.504515 s** on the same
GPU rule. No comparison state is installed into the evolution. The malformed
Info initially differs from a separately normalized twin in 16 bank words;
the physical stage-zero program makes them agree before gathering. Retained
Data uses the existing complete-descriptor inertness certificate, with its
canonical-geometry and fixed-ROM hypotheses.

| Subsequent lower periods | Incorrect decoded upper cells | Bank words differing from the matching healthy terminal |
|---:|---|---:|
| 1 | Colony 37 /upper position 9566 | Not separately measured |
| 2 | None | 660, in lower colonies 30–44 |
| 3 | None | 0; Signals also equal |

The final endpoint is at local time 4U=8589934592 relative to the inherited
lower-period entry. These are three lower periods, not a depth-three result.
The explicit GPU bound is 62551682 bytes, below 64 MiB; process peak RSS is
2418140 KiB.

The independent endpoint audit passes in **144.734491 s**. Its native compiled
normalization prefix and independent scalar replay agree over 5010 intervals,
925494 scalar candidates and 570490 distinct scalar neighborhoods. It checks
**1473511424 complete raw words** across normalization and all three endpoints,
including all 723868 bank words per endpoint. Its process peak RSS is
3753380 KiB. The endpoint identity is conditional on its proven entry domain;
the audit does not literally replay every one of the intervening billions of
physical ticks.

That entry domain is checked separately. A literal global reset of a valid
encoded entry, with the certified retained-Data overlay, equals the normalized
twin in all **368377856 raw words**. The reset check passes in **39.510738 s**,
with 4040528 KiB process RSS. Combined with the actual physical normalization
coupling, this justifies the conditional terminal identity for this trajectory.

The upper-alignment check passes in **3.453203 s**. It binds the actual wider
parents and all four decoded stages to the previously verified 73-cell upper
halo witness. The central 17 cells match all 154 lifted fields of the complete
upper colony at every stage. It also verifies the 660-to-zero history difference
and preserves the three exact nonMEM values. This is an output comparison of
the actual lower run, not replacement of lower transitions by an upper oracle.

## Storage limit and preserved failures

The first wider continuation failed before evolution: the old diagnostic view
budgeted a whole-ring raw reconstruction against a fixed 2 GiB ceiling. The new
`retimed_holder_wide_inert_storage.py` assembles logical diagnostics four colonies
at a time, using the unchanged validation and exact World evolution. It retains
all procedure fields and uses the actual global ring for physical copies.
The physical alphabet, ROM, neighborhood, Q/U and transition implementation did
not change. Three tests pass, including all 73 colonies, cross-tile raw copies,
high controller bits, and rejection of truncated fields or nonzero late-tile flags.
The failed run's log, watch and exact driver source are preserved.

Two scalar-replay adapter tests pass in 6.356 s. An earlier test incorrectly
expected four isolated Flag1 cells to persist. Native and scalar states already
agreed; those isolated flags legitimately cleared. The preserved failed fixture
was corrected by adding an interior flag cluster. Neither the physical rule nor
the replay adapter changed in response to that test failure.

The recovery audit memoizes only identical complete procedure neighborhoods
within one tick and independently evolves the exact late Flag1 recurrence on
every tick. Its version-1 timeout is preserved as an incomplete audit, not a
passing result or a physical mismatch. Version 2 uses the same source and
12 GiB RAM cap with a longer 1800-second wall limit.

## Reproduction and handoff

Exact commands and resource limits are retained in each `_watch.json`; all
accepted completed jobs have return code zero. The pending recovery audit must
be polled by its live process/session or terminal watch, not inferred complete
from artifact names. The following are the principal receipts under
`figs/fixed_rule/`:

- `retimed_holder_wide_recovery_v1.json` and pending `..._recovery_audit_v2.json`.
- `retimed_holder_wide_macrostep_v1.json` and `..._macrostep_audit_v1.json`.
- `retimed_holder_wide_next_periods_3_v2.json` and `..._next_periods_audit_v1.json`.
- `retimed_holder_wide_reset_entry_v1.json` and `..._upper_alignment_v1.json`.

The pending-evidence index is
`retimed_holder_wide_repair_pending_recovery_evidence_v1.json`. It binds completed
artifacts and preserved failures; it does not label the whole chain verified.
The separate active recovery-audit log is intentionally not frozen while it is
still growing. No shared source, historical dataset or other job was modified.
The substantial GPU reservation remains unused; these GPU probes stay below
64 MiB. Combined simultaneous watchdog RAM caps stayed below the user's 40 GB.

Next finish the full quiet-recovery audit and update the evidence chain. Then
establish the lower physical boundary relation to a complete upper colony,
or execute a complete lower-Q ring in a suitable exact representation. The
current upper halo alone cannot supply that missing physical relation. General
amplification, thresholds, robust finite caps, Q/U optimization, depth three
and the existing Flag2/SimBit source-fidelity issues remain open.
