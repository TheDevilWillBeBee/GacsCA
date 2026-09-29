# Continuation: fivefold interpretation and trustworthy long experiments

Subsequent source-timed work: [five-stage Gray compiler and reset integration](gray_schedule.md).

## What changed

**Fivefold tower.** `make_tower(R=5,D=1,Q0=512,U0=32768,U1=8192)` now
interprets all five raw copies of each of 61 upper tracks. K₁=343 bits;
lower schedule length 27337, upper length 5365. The repair circuit uses two
full adders: if the first three bits give sum s₁ and carry c₁, and s₁ plus
the last two give s₂,c₂, the total is s₂+2(c₁+c₂), so majority is
`(c₁ & c₂) | ((c₁ ^ c₂) & s₂)`.
All 32 input patterns are tested, across all tracks, against NumPy and CUDA.

Fivefold spatial repair leaves only one site of transport reach under a
radius-five rule: `D + R − 1 ≤ 5`. The old IINIT copy at offset ±2 would
violate this after repair/redistribution; these copies now route through two
ordinary one-site shifts before local initialization. The GPU constructor
rejects out-of-range SHIFT/RSHIFT and unrouted IINIT instructions.

`tests/test_fivefold_interp.py` checks repair, every emitted IINIT against
NumPy, and two complete lower periods from upper ages spanning every op kind,
concurrent mailbox receives, trickle, and commit. Inputs have inconsistent raw
copies and damaged upper clocks, addresses, Workspace flags, and ordinary flags.
Every upper field and track copy is compared, not merely primary Info.
This is transition-level evidence, not yet a whole upper-period R=5 result.

**Noise version 2.** The old seed packing `(t<<40)^(batch<<28)^site`
aliased times separated by 2²⁴ and batch 4096 with an adjacent time. The
new generator uses SplitMix64 with separate sequential mixing of seed and
unsigned 64-bit time, then a disjoint 32-bit batch/site pair. Fault selection
uses `(word >> 11)/2^53 < epsilon` in double precision; the old 24-bit draw
could overproduce extremely rare faults. This is deterministic pseudorandom
noise, not a proof of probabilistic independence.

`tests/test_noise_counter.py` compares both CUDA backends to a scalar oracle
at times through 2⁶⁴−1, tests the removed time/batch aliases, chunk/restart
equality, and an engineered probability-resolution witness at ε=2⁻³⁰.
Version 1 remains selectable for reproducibility. Historical JSON files
without a noise-version field used version 1 and are not rewritten.
[Noise/backend record](../../../figs/legacy_tower/noise_counter_v2_20260920.xml).
The matched redundancy sweep was repeated under version 2: at ε=0.001,
R=3/R=5 errors are 628/0 of 2048 cell-periods; at ε=0.003, 1977/44.
There are 16 independent rings, not 2048 independent observations.
[Trial data](../../../figs/legacy_tower/redundancy_noise_v2_20260920.json).

**Exact clean acceleration.** Full-engine configuration is now host-resident,
eliminating a device-to-host synchronization each microstep; kernel launches
respect the active CUDA stream. `CleanGraphRunner` captures an even number of
noiseless microsteps and owns stable double buffers. It handles odd tails and
state reloads without changing the rule. It intentionally has no noise input:
replaying captured time arguments would repeat faults. A small 4096-step
R=3 benchmark improved from 0.202 s before the host-config change to 0.132 s
afterward, and 0.082 s with graph replay; these are single-run measurements,
not a general throughput guarantee.

## Resumable evidence

`experiments/tower_checkpoint.py` checks **each** decoded upper transition,
every local field and raw track copy, plus physical Address/Age structure.
At each complete upper period it checks every terminal field against the
terminal NumPy local rule via both decoding routes. The default one-cell
terminal ring is explicitly marked as neighborhood-aliased; a larger ring
is required for spatially varied top-layer validation.

Checkpoints are compressed numeric NPZ plus JSON metadata, loaded without
pickle, written via fsync and atomic replacement. They include the physical
packed state, upper reference, terminal initial state, exact progress, all
period diagnostics, parameters, source and binary hashes. Resume rejects
changed identities or a failed run. Unexpected termination may lose work
since the last checkpoint but cannot turn an incomplete file into a success.

Ten graph/checkpoint tests pass ([record](../../../figs/legacy_tower/checkpoint_graph_20260920.xml)),
including simulated replacement failure that preserves the old checkpoint.
A real GPU restart probe (2+2 periods) is bit-identical in all 18 arrays and
all diagnostics to an uninterrupted four-period run:
[resumed](../../../figs/legacy_tower/tower_resume_probe_20260920.npz),
[continuous](../../../figs/legacy_tower/tower_continuous_probe_20260920.npz).
These probes do not complete an upper work period.

Combined RNG, fivefold interpreter, damaged-control, graph, and checkpoint
regressions: **50 passed in 53.44 s**
([record](../../../figs/legacy_tower/continuation_regressions_20260920.xml)).

Completed run: `figs/tower_checked_R3_20260920.npz`, **4096/4096** lower
periods = 67108864 physical microsteps. Every upper transition matches in all
fields/raw track copies, physical Address/Age damage is zero, and the terminal
transition matches via both decode routes in every field. Wall time 1637.36 s
with concurrent GPU jobs; this is not an isolated throughput benchmark.
The exact pre-Gray-schedule source and binary for this run are preserved in
[this archive](../../../figs/legacy_tower/tower_checked_R3_sources_20260920.tar.gz); all files listed
in its checkpoint identity have been hash-verified against the archive. As the
current tree has advanced, a restart must use the archived source in a separate
directory, not bypass identity checking or overwrite the current worktree.
The process (PID 8717, session 25387) exited successfully. This validates the
corrected compressed R=3 rule on the deliberately small, one-terminal-cell ring,
not the new Gray schedule, a spatially varied top ring, or hierarchy robustness.

## Fidelity priority

Gray [pp.34–35](../../../papers_txt/gray_readers_guide.txt) specifies five stages
with boundaries `0,U/4,U/2,3U/4,7U/8,U`, each half active and half resting.
Scratch/Mailbox reset at each stage, retaining needed earlier gathered data;
stage five votes the three gathered records and computes the next state.
The third stage also computes flag signals for the fourth stage. The current
two-record in-place gather vote and early computation are not that schedule.
Separate storage, explicit reset masks, and separately scheduled flag/full
computations are the next compiler changes, not just moving the trickle window.

An executable clean trajectory at physical Q=8192,U=1048576,R=5 confirms
the mismatch (terminal rule remains reduced Q*=16,U*=2048). The third gather
at old Age=131077 changes simulation tracks at 23 cells, during Gray's first
rest `[131072,262144)`, with healthy physical Address/Age and no noise.
Actual trickle is `[210142,226526)`, versus prescribed `[786432,802816)`.
The initial witness selection mistakenly assumed gather two lay in that rest;
inspection of compiled ages corrected it to gather three. The period-boundary
commit is not counted as a rest violation: it produces the next period's Age=0.
[Raw audit](../../../figs/legacy_tower/gray_schedule_audit_20260920.json).

A second witness isolates the missing reset: set one scratch primary `BF0[100]`
to 1, with all R consistent holder copies, just before the period boundary.
The island occupies only R neighboring cells. It survives transitions to Ages
0,1,2 with healthy physical structure. Gray's first-stage Workspace reset must
erase it. Both R=3 at Q=256 and R=5 at Q=8192 reproduce this
([tests](../tests/test_schedule_gaps.py), [record](../../../figs/legacy_tower/schedule_gap_witnesses_20260920.xml)).
These two passing witness tests document nonconformance of the compressed rule;
they must not be counted as tests certifying Gray fidelity.

![Source versus implemented timing](../../../figs/legacy_tower/gray_schedule_audit_20260920.png)

Gács [Algorithms 19.5–19.8, pp.188–190](../../../papers_txt/gacs_2001.txt) additionally
repeats decode/evaluate/encode three times, votes the results, and separately
refreshes payload packets. Three input gathers plus one evaluation do not
implement this mechanism. Keep this distinction visible when extending Gray's
simplification toward Gács, rather than attributing all variants to both papers.

Subsequent work implements the five stages, wide registers and reset-safe
interpretation; see [current evidence and remaining limits](gray_schedule.md).
Still unresolved: computed-SimBit timing (D10), damaged-address signal placement,
complete Gray-tower execution, arbitrary logical payload/memory,
noise/island/lifetime scaling across hierarchy depths, and a third simulation
link or a uniform data-driven interpreter.
