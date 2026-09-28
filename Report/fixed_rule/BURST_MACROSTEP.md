# A verified decoded macrostep failure after the stronger noise burst

2026-09-27. The saved higher-intensity burst now has a verified continuation
through the next physical commit and reset. The damaged computation commits an
all-zero Info record: **48 raw F words /32 mutable G words differ** from the
healthy simulated successor. The next reset restores one canonical evaluator
head, but does not undo the already committed simulated-state error. This is a
finite noisy-macrostep counterexample at the tested burst intensity, not a
threshold estimate or proof that a surrounding hierarchy cannot repair it.
The full project goal remains active.

## Exact state and controller mechanism

This continues [BURST_RECOVERY.md](BURST_RECOVERY.md), which had already cleared
all flags and preserved the exact remaining Data/controller defects. At physical
time 1232635846, the three primary heads are:

| Position | Phase | PC | Role |
|---:|---:|---:|---|
| 14608 | READ_META | 8 | Extra head produced by the burst |
| 14609 | FETCH | 4456458 | Extra head produced by the burst |
| 25983 | READ_A | 7076 | Original evaluator head |

The full local rule resolves their interactions. At time 1232643271, only the
two extra heads remain, at 22033 and 22034. At time 1232648958, only the FETCH
head remains, at 27720. Its PC=4456458 exceeds every metadata index in the closed
ROM interval 0–27720, so it never fetches an instruction. It keeps reflecting
inside that interval while the final evaluation remains unfinished.

At Age 2025000000 the active computation interval ends; the remaining procedure
state then freezes until commit. The literal transition from U-1 to U copies the
actual Hold words into Info. Those words are zero in this trajectory. The decoded
record is within the fixed field widths, but differs from the healthy successor
in 48 raw words, including **32 mutable words after hard-wiring projection**.
This is therefore not merely an irrelevant metadata discrepancy.

At U+1, the literal reset step restores one head at address 0, PC=0. The experiment
does not claim that the represented state is recovered by that reset. Data
outside the ordinary workspace is retained throughout; it is never dropped to
make the state fit the existing bank representation.

## Physical event execution without a new rule

The old fast executor rejects multiple heads. A new owned CPU scheduler supports
this canonical, coherent, mail-free one-colony execution domain. Its bounded
head capacity and one-colony scope are executor resource/domain restrictions,
not a hierarchy-depth parameter or a new physical alphabet/kernel.

It retains all Q logical Data words and every raw head/controller register.
Literal events call the **unchanged full native F local evaluator**, with all
fifteen raw input cells, and retain the coherent G procedure outputs. Entire
physical rings execute the full G transition at commit and reset. Diagnostic
decoding never installs a simulated successor.

Between events, transport stops before any head reaches a ROM/operand/reflection
event. Equal-velocity heads preserve their relative positions, including adjacent
heads. Different velocities use a conservative separation bound; close approaches
and collisions always execute literal simultaneous transitions. During inactive
clock intervals, procedures are held exactly as specified by the physical rule.
Clock barriers are never crossed by a transport skip.

Zero flags, canonical geometry, coherent fivefold procedures/Signals, no mail,
and no non-head controller residues are explicit input checks. Unsupported
states reject; they are not projected into this execution domain. The full
fixed rule and ROM remain unchanged. The scheduler does not constitute a proof
of all possible multihead accelerations; the actual trajectory below has its
own independent audit.

Six distinguishing tests pass in **3.135 s**. They compare with literal native
G windows for adjacent parallel heads, opposed-head collisions and metadata
fallback, retain Data outside the ROM workspace, and reject omitted controller
residues, out-of-domain heads and incoherent copies. An early fixture failed
because the optimized fixed ROM has no WAIT instruction; its exact source/log
are preserved. The replacement uses an actual metadata-fallback interaction.
The scheduler's earlier full-array validation implementation is also preserved;
the accepted version validates the exact changed-row support per event.

## Independent trajectory audit

The auditor reconstructs and binds the exact preceding recovery endpoint. It
then runs scalar physical core procedures on **every tick for 13112 ticks**,
including all head interactions: **74721 scalar core candidate evaluations**.
It reaches the same lone invalid-PC FETCH head independently of the new event
scheduler.

For the remaining active interval, the auditor checks a specific invariant:
there is one head, no packet, FETCH phase, and a PC absent from every metadata
index in its closed ROM interval. Thus no instruction fetch, Data write, wait,
halt or transmit can occur. Reflection changes direction only. The exact cycle
has length **55442=2*27721** ticks; an independent phase formula determines each
later head position and direction. The inactive interval then holds every
procedure word.

Commit and reset are independently constructed from their scalar clock rules.
The full scalar G transcription is additionally evaluated on **10234 complete
physical outputs**, covering every site potentially changed by these two events.
All six saved complete raw checkpoints agree, including the all-zero decoded
record and the next single-head reset state.

The audit passes in **45.627019 s**, peak **414492 KiB**. This is a verification
of the specific trajectory using a checked reflection invariant, not a general
proof of the new scheduler, not dense execution of all intervening site-ticks,
and not a noise-robustness theorem.

## Cost, artifacts and reproduction

The 4096-tick scheduling pilot completes in **2.703449 s**. The full continuation
completes in **14.985483 s**, peak **496740 KiB** host RAM, with no GPU allocation.
It executes 28587 literal local-event ticks, 792335567 transport ticks,
122483647 quiet ticks, and two full-ring commit/reset steps. In total there are
151308 complete native local output evaluations, including the two full rings.
The represented physical time advances from 1232635846 to 2147483649.

No shared source, existing binary, historical artifact, branch or running job
was changed. All new runs are terminal. Limits are 768 MiB for tests and 1 GiB
for the pilot/continuation/audit, below the user's 40 GB allowance. Accepted
commands are below; choose new artifact names when rerunning.

```sh
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_multihead_tests_v3_watch.json --seconds 60 --rss-mib 768 -- python -m unittest tests.fixed_rule.test_retimed_holder_multihead_events -v
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_burst_macrostep_pilot_v1_watch.json --seconds 60 --rss-mib 1024 -- python -m experiments.fixed_rule.retimed_holder_burst_macrostep --pilot-ticks 4096 --output figs/fixed_rule/retimed_holder_burst_macrostep_pilot_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_burst_macrostep_v1_watch.json --seconds 240 --rss-mib 1024 -- python -m experiments.fixed_rule.retimed_holder_burst_macrostep --output figs/fixed_rule/retimed_holder_burst_macrostep_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_burst_macrostep_audit_v1_watch.json --seconds 240 --rss-mib 1024 -- python -m experiments.fixed_rule.audit_retimed_holder_burst_macrostep --input figs/fixed_rule/retimed_holder_burst_macrostep_v1.json --output figs/fixed_rule/retimed_holder_burst_macrostep_audit_v1.json
```

New owned files: `retimed_holder_multihead_events.py`, its six tests, burst
macrostep driver/auditor, this report and private artifacts. Evidence index:
`figs/fixed_rule/retimed_holder_burst_macrostep_evidence_v1.json`.

## Scientific implication and next experiment

The lower-intensity burst recovered, while this stronger realization kills the
evaluator and corrupts a decoded successor. This gives a concrete local failure
mechanism for the robustness investigation. It neither falsifies the noiseless
self-simulation relation nor establishes a critical noise rate.

The next cross-level task must use a genuine receiving-layer context. Encode
the complete cells around the previously executed upper NAND checkpoint in lower
colonies, reproduce a local burst there, and carry its **actual decoded error**
into subsequent upper repair steps. Merely inserting this measured all-zero
symbol into an unrelated upper state would be a separate fault-transfer test,
not an executed nested noise trajectory. Retain any unused-space Data defects
through the lower-layer continuation; a bank-only endpoint representation must
not silently erase them.

Complete noisy depth-two execution, general amplification, a stochastic
threshold, Q/U optimization, robust caps and depth three remain open. Existing
source-fidelity ambiguities remain unchanged. STATUS.md is the handoff;
MAIN_AGENT_NOTES.md remains the other agent's reply file.
