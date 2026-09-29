# Exact noiseless acceleration by checked fixed points

The whole Gray lower ring contains 67,108,864 physical cells. Brute-force
prefix timing suggested about 20 hours per lower work period. Much of that
period is instruction-free, so executing every identical repair step is avoidable
when the actual state satisfies a restrictive, checked invariant.

## Certificate and scope

`experiments/quiescent.py` wraps the existing **noiseless** CUDA graph runner.
For a proposed old-Age interval [a,a+n), it requires:

1. Uniform physical Age a, whole-colony ring length, and exact phase-zero
   Address geometry. Every physical Flag and Workspace-flag bit must be zero.
2. No scheduled instruction anywhere in the interval; no integer-register
   repair-control window; no Workspace-flag window at computed Age; no rollover.
3. One full CUDA transition leaves **every packed non-clock word unchanged**,
   including raw backup copies, integer registers and inactive storage padding,
   while every clock advances exactly once.

Why this suffices for the audited rule: healthy geometry guarantees that the
apparent colony exists, disabling Flag2's Age-divisibility clause. Uniform clocks
and zero flags preserve the local structure. Outside the excluded windows,
the remaining register and track repairs do not depend on Age. The checked
non-clock state is therefore a fixed point of the same map throughout the
interval. By induction, n transitions change only Age to a+n. The executor
performs that update in place, retaining the graph's buffer addresses.

If any condition fails, ordinary microsteps execute instead. Mixed active/quiet
execution splits at the conservative guard boundaries. No simulated-transition
oracle, artificial repair, noise suppression, or reduced cell count is used.
This reasoning depends on the documented current transition rules and immutable
engine tables; it must be re-audited when clock-dependent rules change. It is
not a machine-checked formal proof and does not authorize skipping noisy steps.

## Evidence and provenance

Fourteen tests pass, comparing every packed word against ordinary execution at
R=3 compressed and R=5 Gray settings. Tests include mixed active/quiet spans,
subsequent graph replay, rejection without state mutation for five damage types,
and rejection at clock-dependent boundaries.
[Tests](../tests/test_quiescent.py), [record](../../../figs/legacy_tower/quiescent_20260921.xml).

The optional second control pair has an additional fixed-point witness in
[test_nested_controls.py](../tests/test_nested_controls.py): a repairable
extra-cache fault rejects certification without mutation, then ten certified
steps after a real repair match direct execution in every packed word. Its
repair has the same excluded load window and no additional Age dependence,
so the above induction applies to the extended schema as well.

A complete four-scenario Gray protocol comparison finished with explicit
`--certified-skip`. Its identity includes the executor's source hash and its
checkpoint records every certificate and skipped-step count. **All 9,961,472
packed words, all protocol events and all five rest hashes are exactly equal**
to the completed ordinary trajectory. It skips 647,847 of 1,048,576 steps in
23 certified intervals. Measured wall times are 490.50 s certified versus
1505.72 s direct; differing shared-GPU load makes that an observational timing
comparison, not a controlled speedup benchmark.
[Checkpoint](../../../figs/legacy_tower/gray_protocol_certified_skip_20260921.npz),
[verified archive](../../../figs/legacy_tower/gray_protocol_certified_skip_sources_20260921.tar.gz),
[bitwise comparison](../../../figs/legacy_tower/quiescent_protocol_parity_20260921.json).

The whole-colony validator also supports an explicit `--fork-from` operation.
It preserves the parent checkpoint and records its hash, original identity and
step count. Every physical-rule/backend dependency must match; only the driver
may change. The direct upper reference is recomputed and checked. The new
executor gets a separate checkpoint and source archive; normal `--resume` still
requires exact identity. A full-geometry fork from step 237824 completed a
16-step certified pilot. It was then advanced another 8176 certified steps in
a read-only comparison process: **all 1,342,177,280 packed words equal the
direct run's state at step 246016**. The comparison refuses ordinary fallback
steps that could hide an incorrect skip by subsequent repair.
[Full-geometry parity record](../../../figs/legacy_tower/quiescent_full_geometry_parity_20260921.json).
This validates a quiet interval at full scale, not a whole lower or upper period.

The certified fork **completed all 1,048,576 lower steps**. Every one of the
504 encoded bits of each of the 8192 upper cells matches its direct transition:
zero mismatches in all fields and all 87×5 raw track copies. All sampled physical
Address/Age checks pass. It certified 657,947 skipped steps after the inherited
prefix. Recorded continuation time is 15,790.43 s (about 4.39 hours), excluding
the direct prefix's 18,234.11 s and the final checkpoint save. This is **one upper
microstep**, not a complete upper period, and not a noisy robustness result.
An independent CPU decoder subsequently checked all **4,128,768 encoded bits**
directly from saved packed words, without the GPU Info decoder. Every field
matches a freshly recomputed upper transition; all five Info copies agree at
the encoded positions. Source/archive hashes and final physical Address/Age
also pass. [Independent verification record](../../../figs/legacy_tower/gray_whole_colony_independent_check_20260921.json).
[Checkpoint](../../../figs/legacy_tower/gray_whole_colony_certified_20260921.npz),
[separate source archive](../../../figs/legacy_tower/gray_whole_colony_certified_20260921_sources.tar.gz).
Its elapsed time excludes the inherited direct prefix, whose time and identity
remain in `forked_from`; skipped steps are recorded separately from total
physical time represented by the state.

The duplicate direct process was deliberately stopped after the certified fork
saved step 262416 with zero structure damage. SIGINT did not stop its queued
CUDA work; SIGTERM was sent only to the command-line-verified process, which
exited with code 143. Its **246016-step checkpoint and original source archive
are retained**. The old checkpoint's internal `running` label predates this
external stop and is not evidence of a live job. No completed work period is
claimed for that direct run; the certified continuation subsequently completed
successfully. Neither process is still running.

Next: extend checked execution beyond one upper microstep and measure noisy
hierarchy behavior. Persistent iid-noise and arbitrary hierarchy acceleration
remain separate work.
