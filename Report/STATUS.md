# Status

Reliability status updated2026-10-11; work is **paused at the owner's
request**. [ROBUSTNESS.md](ROBUSTNESS.md) and [LEDGER.md](LEDGER.md)
supersede conflicting reliability arguments below. No complete iid
theorem, explicit proved positive noise rate or smallest globally
sufficient change is established. G17/CURRENT remains unchanged.
[ROBUSTNESS_HANDOFF.md](ROBUSTNESS_HANDOFF.md) records results through
J309/G285, implementation issues, open proof steps, receipts and the
interrupted unaccepted GBD7 draft. Individual new replays/preflight
passed; the full audit covers only J307 because automatic approval
review enforced the stop instruction before the pending J309 run.

The finite campaign summary below was last updated2026-10-05.
The full account, with every measurement and its
receipt, is [REPORT.md](REPORT.md); G16 is §29, the faster GPU kernel and
the physical level-2 steps §30, the margin study §31, the misaligned-colony
limit §32, G17 §33. The two independent
audits are in [audits/](audits/); both predate G16. Two studies by
sub-agents: the route to Gács's own construction
([GACS_ROUTE.md](GACS_ROUTE.md)) and Gray's error-class constants
([ERROR_LEVELS.md](ERROR_LEVELS.md)).

## Current candidate: G17

| | Q | U | U/Q | QU | bits per cell | gates | sized for a burst of |
|---|---:|---:|---:|---:|---:|---:|---:|
| **G17** | 384 | 20,736 | 54.0 | 2^22.92 | 258 | 17,013 | 73 cells |
| G16 | 512 | 25,920 | 50.6 | 2^23.66 | 258 | 16,767 | 200 cells |
| G15 | 512 | 112,608 | 220 | 2^25.78 | 260 | 17,100 | 200 cells |

G17 is one fixed local rule, with radius 5 and a hard-wired instruction
table (Gray p. 32). It has no depth input anywhere. A colony of 384 cells
simulates one cell of the level above:
- it gathers its neighbours' states three times and votes on them;
- it evaluates the rule's own netlist with a comb of five register-file
  fronts, fetching the upper cell's instruction word physically;
- it commits the result every U = 20,736 ticks.

Every stored bit is held fivefold and majority-corrected every tick.

**G17 is G16's rule with the colony margin sized for a 73-cell burst**
instead of 200, and the gathers 10Q apart (REPORT §33). The smaller box
comes from smaller geometric error boxes with16 in place of Gray's104.
The revised covering and probability lemmas are proved in ROBUSTNESS
§§3–4; the necessary deterministic recovery and noisy hierarchy are
not proved at these constants. The intended repair bounds and the
selected shifted-state race measurements in REPORT §§32–33 remain
separately scoped evidence. What each claim rests on is in
[LEDGER.md](LEDGER.md).

**The lineage.** R0 → R1 → G1–G8 → G9–G12 → G13/G14 → G15 → G16 → G17
(REPORT summary table).
- G1–G8 add Gray's mechanisms one at a time.
- G9–G17 shrink QU by 135× relative to G8.
- All 19 recipes rebuild bit for bit against the tracked manifest
  `gacsca/manifest.json`.

## What is established (finite, seeded evidence)

**For G17** (REPORT §33; the same suite as G16's, except the census):
- A full physical level-2 step of one level-2 cell (147,456 sites, 429,981,696 ticks, 1.7 hours on the role kernel): the level-2 state at the end equals the rule applied to the initial one; the decoded level-1 ring equalled the level-1 automaton at all 324 checks.
- Closure over 23 work periods on the C kernel; the CUDA kernels agree bit for bit; the compiled schedule replayed against the netlist on a running colony without a mismatch.
- Level-0 errors: 0 of 12,000 visible one tick later.
- Level-1 errors: 128 certified (dense 16 × 16 boxes and sparse clusters), 640 bursts of the design width (72 cells) at five stages of the upper colony and in six value modes including a block of shifted Addresses, 64 bursts of 200 × 200 and 32 on the whole upper colony: all contained, all bit-identical at the end; repaired within one upper step except while the upper colony's Flag1 is raised (two steps).
- The misaligned-colony limit measured at three settings, as predicted (REPORT §32), and **the same limit one level up** on the level-1 automaton, with the same thresholds in level-1 steps (REPORT §33): a level-2 error (at most 70 level-1 steps) is far below it (262).
- Colony-scale and level-2 errors: as for G16 (one or two colonies wiped 15/15; 10 of 12 level-2 errors gone at the first level-2 boundary, 2 leaving one level-2 cell wrong once; three-level checks 30/30 and 6/6).
- **The damage island is a glider** of Gray's maintenance rule: adjacent cells whose Age lags by one step move right at 3 cells per tick with Flag1 behind them, die at the colony's right end, and the flags fall back at 2 per tick; the Addresses are never touched (REPORT §33, measured at level 0 on G17 and G16 and at level 2 on the level-1 automaton).

**For G16** (REPORT §29):
- **Self-simulation.** Closure over 23 work periods on the C kernel; the
  CUDA kernels agree bit for bit. Physical three-level rings checked
  against levels 1 and 2 across the level-2 stages (30/30), and level-2
  macrosteps on the level-1 automaton (6/6).
- **Full physical level-2 steps** (REPORT §30). A ring of one level-2
  cell (262,144 sites) and a ring of two different ones (524,288 sites),
  each run for U² = 671,846,400 ticks with no hand-off to the level-1
  automaton. In both, the level-2 state at the end equals the rule applied
  to the initial one; on the way the decoded level-1 ring equalled the
  level-1 automaton at 405 of 405 checks, and 404 re-runs of a level-1
  step on the reference kernel were equal bit for bit. Two seeds, no
  errors.
- **The compiled schedule.** Replayed against the netlist on random data
  and on 359,744 neighbourhoods of a running colony, without a mismatch.
- **Level-0 errors.** In healthy colonies, 0 of 12,000 single errors are
  visible one tick later.
- **Level-1 errors.** 656 certified level-1 errors (Gray's class, 104),
  checked at every tick: all contained, all bit-identical at the end, 641
  repaired within one upper step and 15 within two (see below).
- **Colony-scale errors.** One or two whole colonies wiped: at most two
  adjacent upper cells wrong at one upper time (15/15).
- **Level-2 errors** (3–27 colonies wiped, level-1 cells overwritten): 9 of
  12 gone at the first level-2 boundary; 3 leave one level-2 cell wrong for
  one level-2 step. The hybrid hand-off was checked physically in 10 of 10
  rings.

**For G15 and earlier** (REPORT §§25–27; not repeated for G16): dense
level-0 noise together with level-1 and level-2 errors, the 49-batch census
(no undamaged colony ever made a wrong transition), and the per-field
tables for Proposition 4.

**Two footprints longer than one tick, both properties of the rule (G15
and G16 alike) and both needing an upper cell that raises a flag:**
- *Gray's wipe rule one level up.* A level-1 error that hits while the
  upper colony is inside its own trickle-down window takes two upper steps
  to repair instead of one (15 of 64 on G16, 17 of 64 on G15).
- *The Flag2 erasure front.* A level-0 error on the cell where a colony's
  Flag2 is being erased shifts that front by one cell; the one-bit
  difference disappears when the front reaches the colony's end, within
  Q/2 ticks.

## Not established

- A noise threshold, and a proof of any of the above for all
  configurations.
- The literal all-field form of Proposition 4. Mail and history lanes of
  neighbouring colonies differ within the window.
- Level-3 errors, and several level-2 errors close together.
- A physical level-2 step with errors, or of a ring with more than two
  level-2 cells.
- That level-0 rules repair every burst. A burst that holds a block of
  shifted Addresses across a colony boundary for more than (5/6)(Q − w)
  ticks (about 230 for a square burst on G16, 175 on G17) leaves a
  misaligned colony until trickle-down removes it (REPORT §§32–33). G17's
  level-1 class (62) and design burst (73) are below that limit by a
  factor of 2.4; a 200 × 200 burst of shifted states is above it on G17.
  What such a block does one level up was followed on the level-1
  automaton (§33): the wipe leaves 5 blank cells and 7 cells with wrong
  Info; the blank cells' repair starts the glider, confined to its colony;
  the restoration of the 7 Info cells at the next level-3 boundary (13
  hours on the level-1 automaton) was not followed.
- That a boundary burst damages one colony only. It holds for random,
  stuck, inverted, frozen and copied values; a burst that writes a block of
  shifted Addresses left two adjacent upper cells wrong for one upper step
  (REPORT §31). Proposition 4 allows that.
- Self-organization from arbitrary configurations.
- G16 and G17 have not been audited independently.

## Next steps

1. **Raise the status of the hierarchy step** (LEDGER.md D3, E2–E3). The
   race condition is written one scale up (D4); next are two level-2
   errors within 24 level-2 cells, a level-3 error, and the level-3 period
   that restores the Info left wrong by a block above the race limit, all
   on the level-1 automaton (2–5 s per level-2 step for a complete level-2
   colony).
2. **A physical level-2 step of two G17 cells** (the one-cell step is done) and, with
   the role kernel extended to inject errors, a level-1 error during a
   physical level-2 step.
3. **Repeat for G17** the noise-with-errors runs and the census of §27,
   and have the candidate audited.
4. **The gathers.** 34 of G17's 72 blocks pass before the evaluation
   starts; with the 73-cell box the recovery bound allows gathers 8Q
   apart (U about 19,000).
5. **The program's hand-over chains** (REPORT §29) and the GPU kernel's
   translated copies (REPORT §30) remain the open levers on U and on run
   time.
