# Third-link physical islands and observed higher-layer repair

## Protocol and limits

Start from the immutable, independently audited **384-period** R=3 checkpoint
of the [full-alphabet third link](third_link_execution.md): 65,536 physical cells,
256 middle cells, one periodic top cell. Four independent version-2 RNG trials
per condition, plus a clean control, receive one-step whole-cell replacements
over widths 1, 21 or 101 inside physical colony 128. Replacement occurs after
the local transition at relative time 16 (early) or U−2 (late), U=16384.
Absolute physical time—including the source checkpoint offset—is used by the
counter RNG. Every state field, including the second control pair, is replaced.
Two complete outer periods are executed; no noisy step is graph-captured or
certifiably skipped.

The represented middle ages are **384→385→386**, during mail shifts. This does
not yet test physical faults during nested evaluation, a full middle period
under noise, multiple hierarchy depths, persistent iid noise, or arbitrary
logical-memory storage. Four trials per condition support a pilot, not a failure
probability curve. Top-neighborhood aliasing remains explicit.

[Experiment](../experiments/third_link_faults.py),
[completed state/data](../../../figs/legacy_tower/third_link_islands_20260923.npz),
[quantitative summary](../../../figs/legacy_tower/third_link_islands_verified_20260923.json).
Runtime: **165.34 s** for 25 rings and 32,768 physical steps.
[Six protocol/plot tests pass](../../../figs/legacy_tower/third_link_islands_verified_20260923.xml)
in 5.88 s: box placement, raw-copy versus repaired-Info observables, full-state
injection and large absolute counters, sampled recovery censoring and plots.
Exact source/backend, both boundary checkpoints and analyses are included in the
[completed third-link evidence bundle](../../../figs/legacy_tower/third_link_completion_sources_20260923.tar.gz),
with [verified hashes](../../../figs/legacy_tower/third_link_completion_identity_20260923.json).

## Results

All 24 faulty rings recovered physical Address/clock structure by the sampled
delays below. Every decoded middle field/raw copy matched the clean trajectory
after period 2. But **physical Flag2 remained set in 21/24 rings**, including
5/8 one-cell trials: decoded recovery is not full physical-state recovery.
This finite persistence agrees with the separate [printed-rule D8 problem](flag2_recovery_gap.md);
it does not prove infinite persistence in this particular coupled trajectory.

| Physical fault | Trials with decoded errors after period 1 | Raw middle track-copy errors in affected trials | Sampled sustained Address/clock recovery delay | Final physical Flag2 count |
|---|---:|---:|---|---|
| Early, width 1 | 0/4 | 0 | (0,1] steps | 0–1 |
| Early, width 21 | 0/4 | 0 | (1,16] | 62–67 |
| Early, width 101 | 0/4 | 0 | (16,64] | 58–71 |
| Late, width 1 | 0/4 | 0 | (0,1] | 0–1 |
| Late, width 21 | 4/4 | 5–9 | (1,16] | 55–66 |
| Late, width 101 | 4/4 | 42–48 | (16,64] | 66–70 |

Recovery intervals bracket observations, not exact first-passage times. No
decoded structural fields or majority-repaired middle Info bits differed at
either period boundary. Middle Info here is an encoded working state, not an
implemented arbitrary logical payload.

![Physical recovery and retained flags](../../../figs/legacy_tower/third_link_islands_verified_20260923_recovery.png)

![Sampled spatial recovery](../../../figs/legacy_tower/third_link_islands_verified_20260923_space_time.png)

## Direct inspection of the repair mechanism

The first boundary was replayed with identical seed, batch indices and absolute
counters, then retained [separately](../../../figs/legacy_tower/third_link_islands_first_boundary_20260923.npz).
Its entire first commit reproduces the original result. An
[independent CPU audit](../../../figs/legacy_tower/third_link_islands_repair_20260923.json) decodes
both physical boundaries directly from packed words and checks source archives.

In all eight damaged cases, **only middle holder 128** has incorrect raw track
copies; all non-track fields are unchanged. Raw primary errors are nonzero
(1–4 at width 21, 13–22 at width 101). Yet repaired track bits agree everywhere:

\[
V_t(x)=\operatorname{Maj}_{r=-1}^{1}X^{(r)}_t(x-r),\qquad
V_{damaged}=V_{clean}.
\]

Each logical bit has at most one corrupted holder among its three copies.
A fresh NumPy middle transition from that damaged state matches both the
independently decoded second physical boundary and the clean next state in
every field/copy. The active middle operations are only MAILL/MAILR shifts;
the damaged ARGA/ARGB/HOLD/temporary tracks are already repaired before those
operations. This witnesses repair through the represented layer, not merely a
vanishing mismatch counter or an overwrite of the damaged tracks by mail shifts.
It is a concrete finite witness, not a general robustness theorem.

![Decoded errors and subsequent repair](../../../figs/legacy_tower/third_link_islands_verified_20260923_decoded.png)

Figures were visually checked; initial plots with misleading negative/near-zero
autoscaled axes were retained under the older `...analysis...` prefix, and corrected
figures use `...verified...`. Shading/error bars show the four-trial min–max range,
not confidence intervals.

Next: repeat at middle interpretation/rollover phases, broaden fault placement
to control and encoded-Info fields, remove top aliasing, then introduce persistent
noise and matched-depth comparisons. Preserve the printed Flag2 baseline and
label any correction hypotheses explicitly.
