# Physical third-link execution

This experiment extends the [nested interpreter](nested_interpreter.md) from
isolated and short consecutive transitions toward one **complete middle work
period**. It is a finite, level-specific table interpreter, not Gray's encoded
universal-program fixed point. No noisy depth-scaling result is established.

## Geometry and state alphabet

The compact outer geometry passed all-family transition tests at both R=3/5
([two tests, 14.20 s](../figs/third_link_compact_20260923.xml)). Those first fixtures
retained the historical narrow inner encoding. The long-run configuration instead
sets `full_registers=True` at **every** layer, preserving all 16 bits of each own
simulated Age/Address register. This matters for faulty states, even when normal
control values occupy fewer bits. Keeping the old top work periods failed the
compiler budgets: 4873 > 4096 steps (R=3) and 9164 > 8192 (R=5). Enlarging only
those periods gives:

| Configuration, one middle colony | Outer Q/U | Middle Q/U | Top Q/U | Physical / middle / top cells | Encoded bits outer / middle / top |
|---|---|---|---|---|---|
| R=3, D=3 | 256 / 16384 | 256 / 16384 | 64 / 8192 | 65536 / 256 / 1 | 241 / 238 / 51 |
| R=5, D=1 | 512 / 32768 | 512 / 32768 | 64 / 16384 | 262144 / 512 / 1 | 365 / 361 / 51 |

The single top cell is a periodic, aliased test ring, **not a whole top colony**.
`--middle-colonies 64` gives one whole top colony (4,194,304 physical cells at
R=3; 16,777,216 at R=5). The local-only terminal layer is not advanced by this
experiment until a full top work period, which is outside its first target.

## Checks and reproducibility

`experiments/third_link_checkpoint.py` encodes an arbitrary top state (including
high register bits) in healthy middle colonies, then encodes the middle state in
healthy physical colonies. All subsequent physical evolution uses local CUDA
transitions. A separate NumPy middle trajectory is used **only for comparison**;
it is never installed in the physical state.

After each physical outer period, decode every middle field and raw track copy,
compare against one NumPy middle transition, and check physical Address/clock
geometry. At a middle-period boundary, independently advance the top state and
compare it with decoding through both the physical and reference middle states.
With N middle transitions, physical time is

\[
t_{physical}=N U_{outer};\qquad
N=U_{middle}\Rightarrow t_{physical}=268435456\text{ steps at R=3}.
\]

Checkpoints are atomic and pickle-free. They retain the exact packed physical
state, middle and top references, per-period mismatch counts, geometry, source
fingerprints and a non-overwriting source/backend archive. Resume rejects a
different identity; completed runs do no further work. Failed states are retained
and cannot be resumed as successes. Optional certified skipping advances only
instruction-free physical fixed-point intervals, using the existing audited
[certificate](exact_acceleration.md); noisy steps are never skipped.

Validation before the long trajectory:

- [Six full-alphabet tests pass](../figs/third_link_full_alphabet_20260923.xml)
  (19.63 s): R=3/5 compact all-family execution, exact direct-versus-certified
  checkpoint/restart parity, idempotent completed resume, overwrite/identity
  rejection and invalid geometry. The earlier narrow pilot's four tests are
  retained separately and do not support the full-alphabet claim.
- [Two independent middle-period tests pass](../figs/third_link_middle_period_20260923.xml)
  (2.99 s): execute a complete middle work period **directly at the middle layer**
  and compare all decoded fields/raw copies with the direct top transition,
  including controls 65535 and 43210. This tests the endpoint expected by the long
  run, not its physical realization through the third link.

The current unified [12-test execution/decoder run](../figs/third_link_execution_verified_20260923.xml)
passes in 88.17 s. The read-only diagnostic recorder passes
[three additional tests](../figs/third_link_recorder_20260923.xml) in 1.42 s:
irregular sampling without invented intermediate frames, completed resume,
source identity changes and backward-progress rejection. Its live output is
`figs/third_link_trace_20260923.npz`; each sampled actual decoded middle state
includes all raw track copies, actual period/physical time, and mismatch/structure
counts. Sampling began after the run started; missing early frames are explicit.

## Completed middle period and independent replay

The first full-alphabet R=3 physical run uses
`figs/third_link_R3_full_alphabet_20260923.npz` and certified execution. Its
**16-period pilot passed**: 262,144 physical steps, zero decoded mismatches or
physical Address/clock errors, 84,304 skipped steps through 96 certificates,
13.23 s elapsed. The [source/backend archive](../figs/third_link_R3_full_alphabet_20260923_sources.tar.gz)
has 26 verified members and SHA-256
`80441ebf620cdc80b1d35c16073260fa68c8f733befe913b590f98d1f97c1b22`.
The same physical trajectory **completed all 16,384 middle transitions**:
268,435,456 physical steps, zero per-period field/raw-copy mismatches and zero
physical Address/clock errors. Runtime was **16,230.83 s (4.51 h)**, including
62,618,396 skipped idle steps certified by 71,309 fixed-point probes. No host
reference transition was installed in the physical state. Both the physical
and direct middle states decode to the expected single top-cell transition.
[Completed packed-state audit](../figs/third_link_complete_audit_20260923.json).

An [independent CPU audit of the saved 128-period prefix](../figs/third_link_prefix_audit_20260923.json)
checks **61,696 encoded bits**, zero mismatches, zero Info-copy disagreements,
zero physical Address/clock errors and source/archive hashes. It pins the exact
checkpoint bytes (SHA-256 recorded) despite live atomic replacements. Its direct
packed-word decoder is separate from the GPU Info decoder and passed
[two fault-injection tests](../figs/third_link_independent_decoder_20260923.xml):
a minority of damaged holders preserves the decoded bit, while a majority flip
is detected. This compares with the saved NumPy reference, **not a fresh replay
of the entire trajectory**. The later completed-run replay below provides a
separate stronger check; the prefix audit alone does not establish completion.

The later **384-period prefix** (6,291,456 physical steps) is retained as an
[immutable checkpoint](../figs/third_link_prefix_snapshot_20260923.npz) and also
[passes independent CPU decoding](../figs/third_link_snapshot_audit_20260923.json).
Its exact bytes, the current sources/backend, 15 passing verification cases and
recorder are [archived together](../figs/third_link_execution_sources_20260923.tar.gz)
with [verified fingerprints](../figs/third_link_execution_identity_20260923.json):
39 members, SHA-256 `2ede3272011762344901ec30ce69054c9a1b817cb54525aefc5f82fc3479d4e2`.
This saved prefix remains separate from the completed final checkpoint.

The final checkpoint SHA-256 is
`ec9858af2553613ec38bdd67279d6c2311204a14808c6a6d3f78cf854c7c68ee`.
A [fresh CPU replay](../figs/third_link_fresh_replay_20260923.json), rebuilt from
the seed and initial-state prescription, independently executes all **16,384
middle steps**, checks all **252 actual recorded frames** (12,321,792 state
elements), and matches the final packed physical decoding and saved reference.
Independent second-stage decoding matches a newly computed top transition,
including all full-register fields and raw track copies. Replay took 43.74 s;
it is a verification calculation, not a replacement for physical execution.

The physical trace contains every 64-period checkpoint from 320 to 16384;
earlier frames were not recorded. Nonzero middle and physical flags appear even
without injected noise because the top input is arbitrary and its one-cell
ring is not a whole colony. These flags also match the fresh reference; they
are not counted as Address/clock errors. Physical cells with any flag (including
Workspace flags) peak at 52.73%, explaining why the no-flags skip certificate
does not remain applicable throughout the trajectory.

![Actual sampled hierarchy evolution](../figs/third_link_space_time_20260923.png)

This establishes **one full middle work period and one top microstep** in the
reduced, level-specific third link. It does not establish a full top work period,
non-aliased top geometry, the full Gray three-link schedule, a universal encoded
interpreter, or hierarchy-depth noise scaling.

The completed physical data, independent replay, both burst boundaries and their
analysis/plots are [frozen together](../figs/third_link_completion_sources_20260923.tar.gz)
with [verified fingerprints](../figs/third_link_completion_identity_20260923.json):
67 members, SHA-256 `581e71dfdff7b8361173f566b4a43b5212c7451aea93e4ef894012611129ca01`.
The archived nested-evaluation backend separately passes all **340 default tests**
(one slow test deselected, 4007.00 s); later experiment tests are recorded separately.

## Non-aliased top-ring continuation

**Update 2026-09-24:** this cold-cache continuation was stopped at its saved
192-period prefix after the [initialization counterexample](cache_initialization.md).
It has zero per-middle-transition mismatches, but its CPU endpoint misses eight
top track copies. Its run/trace remain intact. Use the separate
`experiments.third_link_initialized` driver for initialized-cache experiments.
The earlier one-cell top witness has no changed top track bits and does not
expose this defect; its full middle-trajectory match remains valid.

An **11-top-cell** R=3 configuration (11 middle colonies, 2816 middle cells,
720,896 physical cells) passes a 16-period pilot with zero mismatches/physical
Address-clock errors in **105.66 s**. Radius-five top neighborhoods have distinct
cells; the ring still does not contain a whole Q=64 top colony. The same checkpoint
was originally continued toward a full 16,384-transition middle period:
`figs/third_link_R3_nonaliased_20260923.npz`, checkpointed every 16 periods, with
read-only trace `figs/third_link_nonaliased_trace_20260923.npz`. Pilot timing suggests
roughly 30 hours or more for the full target; later phases/concurrent work can
change this. **The independently checked saved prefix is 192 periods**, not completion.

```bash
python -m experiments.third_link_checkpoint --output figs/my_third_link \
  --certified-skip --stop-after 16 --checkpoint-every 4
python -m experiments.third_link_checkpoint --output figs/my_third_link \
  --certified-skip --resume
```

Next: validate non-aliased top neighborhoods/colonies and additional middle
periods. A [24-trial transient-island pilot](third_link_faults.md) now demonstrates
specific decoded higher-layer repair while exposing residual physical Flag2.
Full encoded-program uniformity and D8/D10 source discrepancies remain separate
unresolved requirements.
