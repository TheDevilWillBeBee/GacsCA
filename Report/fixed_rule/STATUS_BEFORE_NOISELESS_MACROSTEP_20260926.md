# Fixed-rule agent status

Updated 2026-09-26. **Full fixed-rule Gács/Gray goal active; not complete.**
Please reply in **Report/fixed_rule/MAIN_AGENT_NOTES.md**; this agent never edits
that file. It was absent at the latest check. No shared change is requested.

## Acceptance priorities and ownership

Correct actual fixed-rule self-simulation; practical two-level execution on the
A100 with measured Q/U costs; demonstrated error correction across levels.
Optimize Q and U subject to correctness. U<=128Q is not a requirement. Keep host
memory bounded and coordinate substantial GPU allocations with the main agent.
The separate 8 GiB scheduling request remains pending and unused.

This agent owns new files only in the fixed_rule namespaces and its STATUS.
No shared source, CUDA artifact, job or historical dataset was changed. No new
GPU run was launched in this milestone. All own CPU runs were checked terminal.

## Latest verified progress: entry relation and timed Data flow

Implemented a bounded-memory Age-zero encoding/validation/decoding relation.
It stores every raw upper controller field in the 154-word Info image (105 dynamic
projected words), permits retained Signals and arbitrary MEM scratch, and requires
zero physical controllers/mail/flags/Wf. Actual ROM checks show the next literal
reset clears all 9773 MEM scratch words while retaining Info. A full 32768-site
colony and 317 complete scalar/native first-reset probes passed in 12.154382 s
/58,452 KiB. The validator uses a 64-cell cache and streams decoded parents.

The new symbolic timed checker interleaves separate instruction reads/writes
and packet arrivals, comparing every operation with the batch ROM calculation.
928155 reads, 418410 writes and 97170 deliveries agree, with all Data compared at
six phase boundaries. Both full evaluations, capture payloads, commit and next
reset agree symbolically. Passed 6.171405 s /198,116 KiB. This is a diagnostic
proof under physical event refinements, not a substitute evolution backend.

An instrumented replay verifies all 5880 META lookups remain within the 15-bit
Address domain, including queries from computed outputs; its timed result is
unchanged. Passed 5.219202 s /213,904 KiB. Main runs used a 512 MiB virtual-memory
ceiling. Seven period tests passed in 1.062 s; three known-bit tests passed in 0.399 s.
Depths one through three use the same relation/rule identity in lazy initializer
checks; those checks are not multi-level dynamics. No failed run was superseded.

Commands, costs, complete entry definition, owned files and limitations:
[PERIOD_ENTRY_AND_TIMED_DATAFLOW.md](PERIOD_ENTRY_AND_TIMED_DATAFLOW.md). All new
source/input hashes were checked and all runs are terminal. No physical rule,
ROM, alphabet, GPU job, CUDA artifact, shared source or historical data changed.

[PROCEDURE_CONTEXT_AND_BARRIERS.md](PROCEDURE_CONTEXT_AND_BARRIERS.md) retains
arbitrary-context and quiet-barrier lemmas; [SIGNAL_FLAG_BOUNDARIES.md](SIGNAL_FLAG_BOUNDARIES.md)
retains Signal/capture/clearing results. [STRUCTURAL_INVARIANT.md](STRUCTURAL_INVARIANT.md),
[ALL_CLOCK_MAIL.md](ALL_CLOCK_MAIL.md) and [MAIL_FACTORIZATION.md](MAIL_FACTORIZATION.md)
retain structural, raw-mail and schedule proofs and their limitations/corrections.
The latest historical third-link check found no process; this is not a completion
audit. No job was stopped or restarted.

## Current limits and next work

Next: assemble the complete physical period induction from the entry relation,
local instruction/dispatch/packet refinements, timed memory identity, quiet
barriers and Signal/flag results. Prove the post-commit state lies in E(G(y))
without host scratch/Signal clearing, for G=pi F iota. Make the translation and
aliasing argument from 15 symbolic colonies to arbitrary ring lengths explicit.
This full macrostep theorem remains unproved; a list of checked dependencies
is not itself a proof of their composition.
Then validate complete upper work periods at depth two with practical GPU costs
and measure repair across levels. Full depth-two periods, reliable finite
termination and general noise suppression remain open. The known cap
Address-defect persistence and printed Flag2/computed-SimBit source limitations
remain; no claim of complete baseline fidelity is made.

Prior evidence includes two one-link physical work periods and limited nested
windows, plus targeted repair fixtures. The latest actual packet GPU run passed
384 SEND successors and 19,536 full-state probes in 8.27 s using 422 MiB, retaining
long-hop packets explicitly. See [PACKET_EVENT_REFINEMENT.md](PACKET_EVENT_REFINEMENT.md)
and [GATHER_AND_REPAIR.md](GATHER_AND_REPAIR.md); their limits still apply. The
earlier expanded mail-free dispatch run remains unverified and is distinct from
the successfully audited SEND run.

## Preserved history

The previous STATUS is preserved byte-for-byte in
[STATUS_HISTORY_20260926_before_mail_factorization.md](STATUS_HISTORY_20260926_before_mail_factorization.md).
Its latest entries link dispatch, ordinary/META paths, clock refinement, all earlier
experiments, failed approaches and coordination requests. This compact handoff
supersedes its next-step ordering; it does not discard historical evidence.
