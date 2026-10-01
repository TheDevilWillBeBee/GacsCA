# Status

Last update 2026-10-01. The full account, with every measurement and its
receipt, is [REPORT.md](REPORT.md). The two independent audits are in
[audits/](audits/).

## Current candidate: G15

| | Q | U | U/Q | QU | bits per cell | gates |
|---|---:|---:|---:|---:|---:|---:|
| **G15** | 512 | 112,608 | 220 | 2^25.78 | 260 | 17,100 |

G15 is one fixed local rule, with radius 5 and a hard-wired instruction
table (Gray p. 32). It has no depth input anywhere. A colony of 512 cells
simulates one cell of the level above:
- it gathers its neighbours' states three times and votes on them;
- it evaluates the rule's own netlist with a comb of five register-file
  fronts, fetching the upper cell's instruction word physically;
- it commits the result every U = 112,608 ticks.

Every stored bit is held fivefold and majority-corrected every tick. G15 adds a
wipe schedule adapted from Gray's stage wipes to G14 (REPORT §§23, 25).

**The lineage.** R0 → R1 → G1–G8 → G9–G12 → G13/G14 → G15 (REPORT summary
table).
- G1–G8 add Gray's mechanisms one at a time.
- G9–G14 shrink QU by 18.9× relative to G8.
- All 17 recipes rebuild bit for bit against the tracked manifest
  `gacsca/manifest.json`.

## What is established (finite, seeded evidence)

- **Self-simulation.**
  - Successive one-level closure for every candidate.
  - R1 level-2 macrosteps.
  - For G15: physical three-level rings checked against levels 1 and 2
    across a level-2 commit (30/30), and level-2 macrosteps on the level-1
    automaton (15/15).
- **Backends.** NumPy, C and CUDA agree bit for bit.
- **Level-0 errors.** In healthy colonies, no error survives one tick: 0 of
  48,000 single errors, and none at any tick under dense noise in a whole
  colony.
- **Level-1 errors.** 548 certified level-1 errors on G15, all contained and
  repaired. Checked at every tick, each keeps every stored Info copy inside
  the two-colony box and restores every field after it: the two measured
  parts of Proposition 4 (REPORT §27).
- **At level 1 every error looks like a level-0 error.** For errors touching
  at most two colonies (2,387 rings; census in `campaign_census.json`), the
  upper state was never wrong (1,789) or wrong once in at most two adjacent
  cells (598).
- **Level-2 errors** (3–64 colonies wiped, or up to 128 level-1 cells
  overwritten).
  - Level 2 removes them: 52 of 61 are gone at the first level-2 boundary,
    and 9 leave one level-2 cell wrong for one level-2 step.
  - The hybrid hand-off was checked physically in 65 of 65 cases.

## Not established

- A noise threshold, and a proof of any of the above for all
  configurations.
- The literal all-field form of Proposition 4. Mail and history lanes of
  neighbouring colonies differ within the window.
- Level-3 errors, and several level-2 errors close together.
- A full physical level-2 step: about 15 days of GPU time per level-2 cell
  (REPORT §26.1).
- Self-organization from arbitrary configurations.

## Next steps

1. **The compiler.** U/Q is 220 against Gray's 128. With unlimited registers
   the final program would need 77 passes on one front and 22 on four, where
   the in-order scheduler needs about 500 and 200 (REPORT §§23–24). A spatial
   compiler that keeps values near their consumers is the largest open gain
   in QU.
2. **The CUDA kernel.** Skipping the logic that is idle away from the comb
   would give about 2× in batched runs (59% of the netlist is idle there;
   REPORT §28).
3. **More evidence.** Level-3 errors and repeated level-2 errors on the
   level-1 automaton, and a long run on the level-1 automaton under
   level-1 noise.
