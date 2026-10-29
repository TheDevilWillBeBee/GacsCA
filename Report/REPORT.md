# Fixed-rule hierarchical self-simulation: the bit-level front construction (R0 → G17)

Started 2026-09-29 as a successor to the Q=8192, U=2^20 fixed-rule candidate
(now archived in [`archive/u20/`](../archive/u20/)); last updated 2026-10-05 (§33).

**Reliability audit notice, 2026-10-11:** [ROBUSTNESS.md](ROBUSTNESS.md)
and the updated [LEDGER.md](LEDGER.md) supersede conflicting proof-status
claims here, especially §§31–33. Smaller error boxes and measured races
do not prove deterministic noisy recovery or the higher-level induction.
No complete iid theorem or explicit proved positive noise rate has been
established. Work is paused at the owner's request; the
[handoff](ROBUSTNESS_HANDOFF.md) records the final accepted results,
implementation issue, unfinished draft and validation limits.
The historical measurements below are retained. G17 is unchanged.

- Code: [`gacsca/`](../gacsca/)
- Tests: [`tests/`](../tests/)
- Drivers: [`experiments/`](../experiments/)
- Receipts (git-ignored, kept locally): `figs/`
- Current status and next steps: [STATUS.md](STATUS.md)
- Independent audits: [audits/](audits/)
- Study of the route to Gács's own construction: [GACS_ROUTE.md](GACS_ROUTE.md)
- Study of Gray's error-class constants and the colony margin: [ERROR_LEVELS.md](ERROR_LEVELS.md); the constants as parameters, lemma by lemma: [GRAY_CONSTANTS.md](GRAY_CONSTANTS.md)
- Overview and how to run things: [docs/](../docs/)

## Summary

*Updated 2026-10-05 (G17, §33). The evidence listed under "What is tested" is G15's and earlier unless it names G16 or G17; the two audits (§§25, 27) predate both. What every claim rests on is listed in [LEDGER.md](LEDGER.md).*

**The construction.** Each candidate is one fixed local rule (radius 5),
defined once as a Boolean netlist plus a hard-wired instruction table (Gray
p. 32 projection, no stored ROM).
- A colony evaluates that same netlist on its encoded upper neighbourhood,
  using a register-file *front* that executes a compiled program of the
  rule's own netlist.
- The upper cell's controller, the evaluator's registers, mail, histories
  and workspace are all ordinary encoded data.
- The one Address-dependent word the upper computation needs is fetched by
  a physical match pass (Gray pp. 31–32); no host oracle supplies it.
- No module takes a depth input: hierarchy depth lives only in the initial
  configuration.

**Candidates.** Each is rebuilt bit-identically from its recipe
(`build_candidates.py`), and all close: the decoded ring equals the rule
applied upstairs, over successive continuous work periods and on
arbitrary upper states.

| | Q | U | U/Q | QU | bits/cell | gates | what it adds |
|---|---:|---:|---:|---:|---:|---:|---|
| U20 (archived) | 8192 | 2^20 | 128 | 2^33 | 6,465 | 14,830 word ops | starting point; upper static words host-supplied |
| R0 | 128 | 2^15 | 256 | 2^22 | 76 | 3,338 | Gray §5.2 local structure only |
| **R1** | 128 | 2^14 | 128 | 2^21 | 107 | 4,144 | smallest; **level-2 macrosteps exact** (two-level rings, §6) |
| G1–G4 | 256 | 2^17–2^19 | | | 238–250 | 7.5k–8.7k | fivefold storage, 3 voted gathers, early Flag program, special procedure, trickle-down; G3/G4 triple evaluation |
| G5 | 512 | 2^19 | 1024 | 2^28 | 357 | 13,383 | **fivefold front**: every stored bit, the evaluator's included, majority-corrected every tick |
| G6 | 512 | 2^19 | 1024 | 2^28 | 357 | 13,372 | gathers 12Q apart (Gray's level-1 recovery bound) |
| G7 | 1024 | 2^20 | 1024 | 2^30 | 359 | 13,611 | Gray's colony margin (p. 33) |
| **G8** | 1024 | 2^20 | 1024 | 2^30 | 359 | 13,631 | + Workspace clearing (p. 34): **carries every audited Gray mechanism** (§16) |
| G9 | 576 | 711,936 | 1236 | 2^28.6 | 360 | 14,394 | exact (non-power-of-two) Q |
| G10 | 576 | 462,208 | 802 | 2^28.0 | 359 | 14,492 | front confined to the working cells; flag courier to Gray's cells 3 and Q−3 |
| G11 | 512 | 326,400 | 638 | 2^27.3 | 262 | 19,675 | compact fivefold front (one register slot per cell), 64 registers |
| G12 | 512 | 217,328 | 424 | 2^26.73 | 261 | 16,619 | single-step front (same function) + proportional layout (§21) |
| G13 | 512 | 125,856 | 246 | 2^25.94 | 260 | 16,981 | **comb of five fronts**, each with its own program and register file (§23) |
| **G14** | **512** | **110,880** | **217** | **2^25.76** | 260 | 16,966 | G13 re-sized by a seeded schedule search (§23) |
| **G15** | **512** | **112,608** | **220** | **2^25.78** | 260 | 17,100 | G14 + a wipe schedule adapted from Gray's stage wipes (histories and mail at the commit, Hold at E0−1): every field is exact again by the second period boundary after a level-1 error (§§25, 27) |
| **G16** | **512** | **25,920** | **50.6** | **2^23.66** | 258 | 16,767 | G15's rule compiled by a **job scheduler**: the five fronts claim work from one pool and run it out of order; 37 passes instead of 333 (§29) |
| **G17** | **384** | **20,736** | **54.0** | **2^22.92** | 258 | 17,013 | G16's rule with the **colony margin sized for a 73-cell burst** instead of 200 (Gray's condition (iii) with 16 in place of 104: a level-1 error is then at most 62 wide) and the gathers 10Q apart (§§31–33) |

G9–G17 keep all of G8's Gray mechanisms; G15 adds the two-time wipe schedule,
and G16 and G17 keep it. QU relative to G8: G9 2.6× smaller, G12 9.6×,
G13 16.7×, G14 18.9×, G15 18.4×, G16 81×, G17 135×.

**What is tested:**
- **Self-simulation.**
  - One-level closure for every candidate.
  - R1 two-level rings: all level-1 steps exact, and every level-2 step
    tested exact (n2 = 1 twice; n2 = 2 and n2 = 3 once each).
  - An R1 three-level vertical slice: 24 consecutive level-1 steps exact.
- **Backends.** NumPy reference, C (scalar and AVX2) and CUDA (`gpu.py`,
  block and grid modes) agree bit for bit on arbitrary states.
- **Level-0 errors** (one site or two adjacent sites, whole state replaced;
  measured directly in §25):
  - In a healthy colony, every injected error is gone one tick later:
    0 of 48,000 errors on G8, G12, G14 and G15, with random, inverted,
    all-zero and all-one values.
  - Where an emergency flag (Flag1) is raised, Gray's own wipe rule gives a
    hit cell a two-tick footprint.
  - Under dense level-0 noise, the decoded upper state stays exact
    (§§13–14).
- **Bursts and level-1 errors** on two-level rings whose upper colony is
  healthy and at several stages of its own work period (§§19, 23, 25).
  - *200×200 dense bursts.* Under Gray's definition each is a union of
    several level-1 errors, not one.
    - 662 on G8, G11 and G12, plus G9 (128), G10 (64), G11 (14 in full
      colonies), G8 (8 in full 1M-site colonies), G13 (384) and G14 (192).
    - Every one was contained (at most one upper cell wrong) and repaired in
      the decoded upper state within one upper step.
    - 653 of the first 662 ended bit-identical, and every later one did.
    - The 9 exceptions are G8 commit-time bursts. Reruns of six of them (b1,
      b2) with their original faults are bit-identical from step 4; the b3
      rerun is still running (§25).
  - *Genuine level-1 errors* (certified by `gray_errors.py`): 548 on
    G15 (dense 100×100 boxes and sparse clusters), and 128 on G14 (§25).
    All keep their certificate under the corrected classifier (§27).
    - All were contained and repaired, and all ended bit-identical.
    - **G15 has the two measured parts of Proposition 4**, checked at every
      tick in §27: every field of every colony is equal again by the second
      period boundary, and the stored Info copies never differ outside two
      adjacent colonies. The literal all-field statement does not hold:
      mail and history lanes of other colonies differ within the window
      (§25). G14, without the wipe schedule, keeps history-lane residue one
      period longer.
    - G15 also passes with adversarial values (stuck-at zero, inverted,
      frozen, and plausible states copied from another colony), and on the
      whole upper colony (262,144 sites).
  - With the colony margin (G7+), a burst on a colony boundary damaged at
    most one colony for every value mode the campaigns used. A burst that
    writes a block of consistent but misplaced Addresses can damage both:
    two adjacent upper cells wrong for one upper step, which Proposition 4
    allows (§31).
  - **Undamaged colonies always make the correct level-1 transition** (Gray
    p. 35), for errors that touch at most two colonies. Across the 49
    campaign batches listed in `campaign_census.json` (G8–G15; 2,387 such
    error rings, 9,255 upper steps; census rule and receipt digests in that
    file, §27), no colony outside those touched by the error ever had a
    wrong upper state. Errors touching three or more colonies (25 rings)
    are level-2 errors and are reported separately (§26.4).
    - Each colony's new state always equals the rule applied to the previous
      decoded ring, including the damaged colony's wrong state. That wrong
      state is outvoted like a level-0 error.
    - Wrong states occurred only in the damaged colonies: one, or two
      adjacent ones once, in G9. They were repaired in the next upper step.
  - **At level 1, every error looks like a level-0 error**, which is what
    Gray's amplification argument uses (p. 36).
    - Of those 2,387 error rings, 1,789 never changed the decoded upper
      state.
    - Each of the other 598 changed it at exactly one level-1 time (one
      multiple of U), in one cell or two adjacent ones inside the touched
      colonies, never at two times.
    - The transient differences in neighbours' Mailbox and Workspace (§25)
      lie below the level-1 state and never reached it.
- **Colony-scale and larger errors** (§§15, 26).
  - *One or two colonies wiped* (G15, whole upper colony, 25 rings,
    with and without dense E0 noise): at most two adjacent upper cells are
    wrong at one upper time, the next upper step repairs them, and the
    physical state is bit-identical by the second boundary.
  - *Three to 64 colonies wiped, or up to 128 level-1 cells overwritten
    with another level-2 colony's cells.* Level 1 alone cannot remove
    these; level 2 does, through the hybrid of §26.5 (physical up to a
    hand-off that §27 checks physically, then the level-1 automaton).
    - Of 61 such errors, 52 were gone at the first level-2 boundary.
    - In the other 9, only the damaged level-2 cell was wrong at that
      boundary, and everything was exact from the next one.
    - At level 2, that is a level-0 error.
- **Three levels** (§26).
  - Physical three-level rings checked against levels 1 and 2 across a
    level-2 commit: 30 of 30 exact.
  - Level-2 macrosteps on the level-1 automaton: 15 of 15 exact.
- **Noise together with larger errors** (§26).
  - Dense level-0 noise together with a dense 100×100 burst on the whole
    upper colony: 44 of 44 contained, repaired and bit-identical, with
    random and copied values. With the noise counted, the burst plus its
    linked noise hits is one Gray level-1 error in 4 of 22 placements and a
    higher-level error in the other 18 (§27). In the ring with the noise
    alone, no difference survived a tick.
  - Noise at both lower levels together with a level-2 error: same outcome
    as without the noise.
- **G16** (§29), the current candidate, on its own evidence:
  - Closure over 23 work periods on the C kernel, GPU parity, and the
    scheduler's listing replayed on 359,744 neighbourhoods of a running
    colony without a mismatch.
  - Level-0 errors in a healthy colony: 0 of 12,000 visible one tick later.
  - 656 certified level-1 errors: all contained and bit-identical at the
    end; 641 repaired within one upper step. The other 15 hit while the
    upper colony was inside its own trickle-down window and took two upper
    steps: Gray's wipe rule one level up, which G15 shows too (47 of 64 in
    one step in the same batch).
  - Three levels: 30 of 30 physical checks across the level-2 stages, and
    12 level-2 errors (3–27 colonies), 9 gone at the first level-2 boundary
    and 3 leaving one level-2 cell wrong for one level-2 step.
  - **Full physical level-2 steps** (§30): a ring of one level-2 cell
    (262,144 sites) and a ring of two different ones (524,288 sites), each
    run for U² = 671,846,400 ticks with no hand-off. In both, the level-2
    state at the end equals the rule applied to the initial one, and the
    decoded level-1 ring equalled the level-1 automaton at all 405 checks
    on the way. Two seeds, no errors.
  - Not repeated for G16: the noise-with-errors runs, the census and the
    per-field Proposition-4 tables.
- **G17** (§33), the current candidate: the same suite as G16's except the
  census. A full physical level-2 step of one cell (429,981,696 ticks,
  1.7 hours), exact at the end and at all 324 checks on the way; closure
  over 23 periods, GPU parity, the schedule replayed on 357,000 neighbourhoods of
  a running colony, 0 of 12,000 level-0 errors visible after a tick, 128
  certified level-1 errors of the smaller class and 896 bursts of the
  design width and larger all contained and bit-identical at the end,
  10 of 12 level-2 errors gone at the first level-2 boundary and 2 leaving
  one level-2 cell wrong once, three-level checks 30 of 30 and 6 of 6.
  The misaligned-colony limit of §32 was measured at three settings and
  is where the race predicts it; the design burst is below it by 2.4×.
  The same race holds one level up, on the level-1 automaton, with the
  same thresholds in level-1 steps (G16 and G17), so a level-2 error
  cannot leave a misaligned level-2 cell; the damage island itself is a
  glider of the maintenance rule, confined to its colony (§33).
- **Unit tests:** 59 in `test_front_candidate.py`, one of which (a slow
  G8 GPU test) runs only on request.

**Not established.**
- A noise threshold (Gray's bound ε < (QU)^-2 is out of reach).
- Level-3 errors (three or more adjacent level-2 colonies damaged), and
  several level-2 errors close together.
- A physical level-2 step with errors, or of a ring with more than two
  level-2 cells. Two error-free steps have been run (§30); otherwise
  level-2 steps are checked on the level-1 automaton and physically across
  a level-2 commit.
- Self-organization from arbitrary configurations.

**Several fronts (§23).** A comb of five fronts, five cells apart, runs
the program about 2.2× faster than one front. G14 (U = 110,880,
U/Q = 217) is the result; it closes on the GPU and G13's level-1 batches are
clean.

**Compiler work after G14 (§24).** Many scheduler and partition variants
were measured; none beats G14. A netlist change, select-then-vote,
computes the same function with 14% fewer gates and shortens the
one-front program, but not the comb's.

**The job scheduler (§29).** The limit after G14 was the compiler's issue
discipline, not the machine: each front issued its gates in a fixed order
and waited. G16's scheduler lets the fronts claim work from one pool and
execute it in any order, with scratch bits as the only channel between
them. The program fell from 333 passes to 37 and U from 112,608 to 25,920,
with the rule's mechanisms unchanged.

**Next.** The gathers are now the larger part of the work period (52 of 90
blocks), and the program is bound by hand-overs between fronts, not by its
instruction count. Three further reductions were measured and not taken,
because each changes more than the compiler (§29): gathers 10Q apart
(U = 23,904), three stored copies instead of five (Q = 448, U = 21,056,
weaker code), and three-input instructions. A study of the route to Gács's
own construction (stored program, error-correcting codes;
[GACS_ROUTE.md](GACS_ROUTE.md)) found that neither lowers Q or U.

**The colony margin (§§31–33).** Gray's 200-wide level-1 box comes from a
constant (104) that his proof uses once, for convenience. With 16 in its
place a level-1 error is at most 62 wide, the margin falls from 122 to 58
cells and Q from 512 to 384; with gathers 10Q apart U is 20,736. That is
G17, validated in §33 and now the current candidate. The price: the margin
protects against boundary bursts up to 73 cells wide instead of 200, and a
burst of shifted states longer than about 175 ticks leaves a misaligned
colony, which trickle-down wipes; what the wipe leaves one level up (a
glider with Flag1 in the upper colony, 7 cells of wrong Info) is in §33.

**The GPU (§30).** A kernel that skips the comb's logic where no front
arrives and splits a word's work over six threads is three times faster on
a level-2 cell's worth of sites. A full physical level-2 step of G16 takes
2.5 hours with it.

## 1. Binding costs of the current candidate

1. **Word-level cells.** 119 represented 64-bit words, fivefold procedure
   words, and seven address slots of static metadata per cell (3,402 static
   bits) give a 6,465-bit cell. That needs a 14,830-operation word
   description, placed as 14,849 gate copies on 4,969 sites. This drives
   Q to 8192.
2. **The upper evaluator's configuration is upper data.** The upper
   neighborhood needs 390 static words (341 circuit/route, 49 holder) that
   depend on the upper Address. The host preloads them
   (`archive/u20/experiments/fixed_rule/run_dual_capture20_events.py:62-73`,
   `archive/u20/gacsca/fixed_rule/gpu_validation/initial.py:71`).
   A physical fetch of 390 words is itself a large routing problem.
3. **Scale.** Two levels need Q²·U² = 2^66 site-ticks per level-2 step. A
   bit-packed Q² state is 50.5 GiB per buffer.

My full audit of that candidate is in
`archive/u20/prompts/FIXED_RULE_U20_REPAIR_PROMPT.md`. It includes the
WordCode ≠ literal-F hop-count defect found by the GPU validation work, since
confirmed and patched by the U20 repair work (both archived in
`archive/u20/`).

**The design response:**
- *Bits, not words.* Cells are 76–357 bits.
- *A register-file front instead of a configured spatial circuit.* The
  evaluator's configuration becomes one instruction word per (Address, page).
- *A projected ROM* (Gray p. 32). The instruction table is part of the rule,
  not cell state, so there is no static ROM to store or repair.

## 2. Construction

**Rule = netlist.** `netlist.py` builds hash-consed AND/OR/XOR netlists, and
`rule.py` (family R) and `rule_g.py` (family G) build the rule.
- Inputs: the fields of cells −5..5 and the instruction word `I`.
- Outputs: new fields, the lookup selector `psel`, a diagnostic `arrive`,
  and (G4/G5) the lookup key `laddr`.
- The netlist digest is the rule identity.

**Projected ROM (Gray p. 32).** The rule computes `I = Pi[key][psel]` from a
fixed table Pi. Pi has an entry for every Address and every `psel` value. The
key is the stored Address (R, G1–G3) or the computed Address (G4, G5).

**Local structure (Gray §5.2).** `maintenance.py` transcribes candidate-B
maintenance (radius 5, Q=2^k, U=2^m). It equals the independent
`stream28_holder_core.maintenance` on 3,000 random neighborhoods, plus a
600-case regression test.

**Retrieve (Gray pp. 28–29; Gács §9.3).**
- At computed Age 0 the mail tracks load Info, then shift one cell per tick.
- Lane j captures at Age |j|Q+1±skew_j, so lane j at cell x holds neighbor
  j's bit at address x−skew_j.
- The skews are rule constants that spread reads to ≤4 needed bits per cell
  (11 without them).
- G runs three gathers (Ages 0, 8Q, 16Q) and votes the third arrival against
  the two stored histories.

**Evaluate: the front.**
- An L-bit register file sweeps the colony boustrophedon, one cell per tick.
- On each arrival it executes the cell's instruction `op | kind | a | b | d`:
  - two sources, drawn from registers, the cell's lanes, Hold, scratch and
    constants;
  - one of AND, OR, XOR, ANDN;
  - a destination: a register, Hold or scratch.
- The program is a straight-line compile of the rule's own netlist
  (`compiler.py`).

**Self-fetch (Gray pp. 31–32 steps i–iii; Gács Remark 9.4 `MyText`).**
1. Before match pass MP, the program leaves the upper lookup key in R[0:k]
   and the upper `psel` in R[k:k+PW].
2. In MP, the physical cell whose key equals R[0:k] loads its own Pi entry
   for that `psel` into R[k:k+IW].
3. The remaining passes compute every upper output into Hold.
4. Hold is committed to Info at Age U−1 (Update).

In G3/G4 this repeats three times, into Hold copies A/B/C.

**Family G (Gray §§5.4–5.5).**
- Every stored simulation-structure bit is fivefold. Copy slot s at cell y
  belongs to logical cell y+s−2, and every copy is recomputed from
  majority-corrected values using holder-local geometry.
- An early Flag program writes the upper *new* Flag1/Flag2 into Hold at Q−3
  and 3. The special procedure copies them into the SimBits at T_sig
  (p. 35).
- Wf1/Wf2 follow p. 41 during [T_sig+1, T_sig+1+2Q).
- Front writes pass through a one-tick pending buffer.

**G5's fivefold front.**
- The register file and pending buffer are also fivefold.
- Each holder executes the front step of each of its five logical cells from
  majority-corrected register files. For each logical cell it uses its own
  computed Age, and computed Address plus the slot offset, as that cell's
  clock and lookup key.
- The front occupies one logical cell at a time, so each physical cell does
  **one** Pi lookup. The front cell's five holders each do their own lookup,
  so there is no single point of failure.
- The upper cell likewise needs one fetched word per period.
- Radius 5 is exactly enough: corrected register files at logical offsets
  ±3 read copies at ±5.

**Fixed point.** The netlist depends only on constants (Q, U, pass layout,
skews), not on Pi's contents; Pi is the compiled program.
- Loading a cached candidate fails if the netlist built from its parameters
  has a different digest.
- Since the audit (§25), loading also fails if the cached ROM, layout or
  netlist differs from the trusted manifest
  (`gacsca/manifest.json`). The manifest was
  written from fresh builds of all 17 recipes.
- `build_candidates.py` rebuilds every candidate from its recipe; all 17
  rebuild bit-identically (`receipts/candidates.json`, 2026-10-01).

**Backends (`machine.py`).**
- A NumPy reference with a full Pi lookup at every site.
- A generated bit-sliced C kernel (scalar, and AVX2 via GCC vectors). It
  looks Pi up only where `arrive` is set and runs in one persistent OpenMP
  region.
- A batched CUDA simulator (`gpu.py`, §12) generated from the same
  netlist, bit-exact against the C kernel. (The earlier single-block
  `cuda_backend.py` is superseded and archived in `archive/g_family/`.)

## 3. Measured costs

Measured on an AMD EPYC 7543 (Zen 3, AVX2) with pinned cores.

| | U20 (archived) | R1 | G3 | G5 |
|---|---:|---:|---:|---:|
| Q · U | 2^13·2^20 | 2^7·2^14 | 2^8·2^18 | 2^9·2^19 |
| bits/cell (upper bits / usable cells) | 6,465 | 107/128 | 249/254 | 357/510 |
| description | 14,830 word ops | 4,144 gates | 8,603 gates | 13,383 gates |
| front registers L / scratch S | — | 64 / 4 | 64 / 4 | 32 / 4 (×5) |
| instruction bits / ROM entries used | — | 24 / 6,120 | 24 / 45,138 | 21 / 42,553 |
| passes used / window | — | 110/121 | 905/980 | 927/999 |
| upper data fetched per period | 390 words, host | 1 word, physical | 3 (one per run) | 1 |
| site-updates/s, 1 thread | — | 9.3e7 | 3.5e7 | 1.1e7 |
| site-updates/s, A100 dense | 1.8e7 | — | — | — |
| site-ticks per upper step, Q·U | 2^33 | 2^21 | 2^26 | 2^28 |
| site-ticks per level-2 step, Q²·U² | 2^66 | 2^42 | 2^52 | 2^56 |

- **R1 two-level ring:** 128 colonies run at 26.5–31 µs/tick on 8 pinned
  cores.
- **G one-period wall time** for 12 colonies on 8 cores: about 4.5 s
  (G1/G2), 9 s (G3), 26–32 s (G4) and 37–47 s (G5).
- **All candidates:** full numbers are in `receipts/candidates.json`.

## 4. Tests

`OPENBLAS_NUM_THREADS=1 python -m unittest -q tests.test_front_candidate`
runs 47 tests, all OK in about 60 s (updated 2026-10-01). Six of them need a
CUDA GPU and are skipped without one. One of the 47, a slow G8 GPU closure
test, runs only
with `GACSCA_SLOW=1` (about 3 minutes). Later additions are listed at the end
of this section. The suite would fail if:

- **Depth or identity varied.** An entry point takes a depth or level
  argument, the width or rule changes across levels, or the cached ROM
  differs from a fresh compile of the netlist.
- **The radius were exceeded.** A netlist input lies beyond radius 5, or a
  far-field perturbation of a real state changes a cell.
- **The encoding were incomplete.** encode/decode is not a bijection, a raw
  field (registers, scratch, lanes, mail, Hold, flags) is unencoded, or G
  fails to write all five Info copies.
- **Backends disagreed.** C scalar, C AVX2 and NumPy must agree on arbitrary
  states, including G4's computed lookup key and G5's fivefold front, and the
  ROM must cover every `psel` value.
- **Closure failed.** Three successive decoded macrosteps on random upper
  states must equal the rule upstairs, and the ring must keep changing.
- **The ROM were not really executed.** A single corrupted used ROM bit must
  break closure.
- **G's mechanisms broke.**
  - G's special-procedure SimBits must be right.
  - G3's commit must be a majority: one corrupted run is outvoted, two are
    not.
  - A flipped stored copy of a G5 front register must be fully corrected
    within a tick.
- **The GPU disagreed** with the C kernel (block and grid mode, snapshots),
  failed one-period closure, broke the level-0 separation of its E0 grid or
  the exact shape of error boxes, or was non-deterministic.
- **A margin leaked** (G7–G15). Represented SimBits or any instruction slot
  lies inside a margin of at least 100 cells, apart from G7/G8's two special
  cells in the early program; scratch appears in a margin; or, for an
  unconfined front, the margin changes the rule.
- **Workspace clearing failed.** G8–G12 must clear scratch at the commit
  tick; G7 must not.
- **Exact-Q maintenance** (Addresses mod Q, packed Age) differed from the
  integer reference `maintenance_scalar` on 1,500 structured neighbourhoods,
  including both wraps. Power-of-two candidates keep their netlists, which
  is checked by the digest test.
- **The compact front failed to self-correct** (G11, G12): flipping register
  bits in one or two of the five copies near the front mid-evaluation must
  leave the ring bit-identical three ticks later.
- **The single-step front were a different function** (G12 against the
  five-step netlist), on random inputs and on inputs forced to make the
  front arrive, including match passes.

## 5. One-level evidence

- **R0:** 3 seeds × 5 successive periods on 13 colonies, all exact.
- **R1:** 3 seeds × 3 periods, all exact. Every level-1 step checked in §6 is
  also a one-level R1 macrostep on 128 or 384 colonies.
- **G checks** (`run_g_period.py`, receipts in `g_periods/`). Each period
  checks:
  - the decoded ring is exact and all five Info copies agree;
  - at T_sig+1, the SimBits at Q−3/3 equal the new upper Flag1/Flag2;
  - Wf1 is set in the five right-end cells exactly where the new upper Flag1
    is 1;
  - Wf2 is set in the five left-end cells exactly where the new upper Flag2
    is 1 and the physical Flag1 is 0;
  - physical flag waves occur and have decayed by the boundary.
- **G results:**
  - G1: 3 random seeds × 3 periods, plus coherent upper states on 16 colonies
    × 3 periods. Colonies with upper Flag1=0 get no Wf1 and no wave.
  - G2: 2 periods, exact.
  - G3: 2 random seeds × 3 periods, plus coherent × 3 periods; all checks
    pass.
  - G4: 2 periods, exact.
  - G5: 2 random seeds × 2 successive periods via `run_g_period`, all checks
    pass (receipts `g_periods/G5_c12_s*.json`).

## 6. Closed two-level ring (R1)

`run_two_level.py` runs a closed two-level ring:
- The top ring is n2 random cells. Level 1 = `encode(top)` and level 0 =
  `encode(level 1)`, with the same function and rule.
- The C kernel evolves level 0 only.
- Every U ticks the level-0 ring is decoded and compared with the NumPy rule
  applied to the previous level-1 ring.
- Every U level-1 steps the level-1 ring is decoded again and compared with
  the rule applied to the top ring.

**Result, n2=1 (16,384 physical cells, seed 0):**
- All **16,384 consecutive level-1 macrosteps** (2^28 physical ticks)
  decoded exactly.
- At the end, the doubly-decoded top cell **equals the rule applied to the
  top cell**: level-2 step 1, 32 top bits changed, level-1 colony geometry
  healthy. The top-state SHA-256 is
  `57421592f3d278514df7abf9cf5e2d1f878f57a0456dd2e282e880a69b432c57`.
- Physical time was about 2.7 h on 8 pinned cores (≈30–45 µs/tick).
- Log: `two_level/R1_n2_1_seed0.log`.

**Level-2 step 2 (21:10 UTC) is also exact.** All 32,768 consecutive
level-1 steps (2^29 physical ticks) decoded exactly, and the doubly-decoded
top equals F²(top). 2 top bits changed; top SHA-256 `12e4e1e4de6b55a4…`.

**Two more rings, one level-2 step each, both exact:**
- n2=2 (32,768 cells, seed 2): 16,384 level-1 steps exact; the level-2 step
  equals F(top), with 113 top bits changed (`56ae7915…`).
- n2=3 (49,152 cells, seed 1): 16,384 level-1 steps exact; the level-2 step
  equals F(top), with 83 top bits changed (`0c81179a…`).

Receipts: `two_level/R1_n2_{1,2,3}_seed*.json`. On the GPU a level-2 step
takes about 40 minutes for one ring (§12).

### Three-level vertical slice (R1)

`run_three_level_slice.py` encodes one random top cell three times with the
same function:
- 128 level-2 cells,
- 16,384 level-1 cells,
- 2,097,152 physical cells, all with the same 107-bit width.

It asserts that each level decodes to the one above. It then evolves the
physical ring with the C kernel and, after every U ticks, compares the
decoded level-1 ring with the rule applied to the previous level-1 ring.

This checks that the physical ring correctly simulates a level-1 ring that
itself encodes two further levels. It is *not* a level-2 or level-3
macrostep: those need U² and U³ physical ticks, about 19 days and far longer
at 88–101 s per level-1 step on 16 cores.

**Result: 24 consecutive level-1 steps, all exact.** Between 17,376 and
83,136 level-1 bits changed per step, covering the level-1 colonies' gathers
and the start of their evaluation. The wall time was about 36 minutes.
Receipt: `three_level/R1_n3_1_seed0.json`.

## 7. Preliminary injected-fault probe

`noise_probe.py` evolves one continuous period and applies isolated physical
bit flips between kernel calls. It then compares the decoded ring with the
fault-free rule. Entries are exact periods / trials.

| Fault class (flips/period) | R1 | G1 | G2 | G3 | G4 | G5 |
|---|---:|---:|---:|---:|---:|---:|
| Storage (50) | 4/16 | 16/16 | 16/16 | 32/32 | | 16/16 |
| Front fields at random cells (50) | 14/16 | 13/16 | 16/16 | 32/32 | | |
| Geometry Address/Age at random cells (50) | 12/16 | 16/16 | 16/16 | 32/32 | | 16/16 |
| Flags (50) | 16/16 | 16/16 | 16/16 | 32/32 | | 16/16 |
| Register bit at the front's cell (1) | 30/32 | | 29/32 | 32/32 | | |
| same (8) | | | 11/32 | 32/32 | | |
| same (256) | | | | 5/16 | | **16/16** |
| Age at the front's next cell (4; G5: 16) | 7/32 | | | 32/32 | 16/16 | 16/16 |
| Address at the front's next cell (4; G5: 16) | 2/32 | | | 32/32 | 16/16 | 16/16 |
| Age at the cell just left, or during gathers (4) | 32/32 | | | | | |

What this shows:
- **Storage.** Fivefold storage absorbs isolated storage faults: R1 is 4/16,
  G is 16/16.
- **Stored-field clock.** A front clocked and indexed by *stored*
  Age/Address (R1) is corrupted by single geometry faults on its next cell. A
  computed clock and key (G4) is not.
- **Triple evaluation.** G3 absorbs every tested front and geometry pattern
  up to 8 targeted flips per period.
- **Dense faults.** At 256 targeted front faults per period, G3 fails in
  11/16 periods, consistent with at least two of its three runs being hit.
  G5 stays exact in 16/16, as expected if each flip is outvoted at the next
  tick.

These are isolated injected faults on the healthy path. The probe does not
measure noise thresholds, level-1 bursts, trickle-down repair or
amplification.

## 8. Why per-tick evaluator protection matters (G3 versus G5)

Gray's level-0 model allows an error in every (24, 24) space-time box.
- **G3.** One evaluation run lasts about 60,000 ticks, so at that worst-case
  density the front's cell could be hit about 2,500 times per run. Triple
  evaluation, which tolerates one corrupted run per period, cannot meet that
  density.
- **G5.** Every front bit is recomputed each tick from a majority of five
  copies on five cells, like all other simulation structure. A 2-site error
  corrupts at most two copies, and they are restored at the next tick.
- **Current Q8192 candidate.** Its spatial evaluator's gate, route and mail
  state is single-copy for 65,536 ticks per invocation, the same gap as G1–G4.

## 9. Deviations from the sources, and alternatives

- **Front clock and lookup key.** Stored Age/Address in R and G1–G3, as in the
  current holder clock. Computed Age/Address in G4/G5, closer to Gray's
  "computed values". §7 separates the two.
- **Holder-local geometry.** Fivefold copy procedures use the holder's own
  geometry, and Mailbox clearing uses the holder's computed Flag1.
- **Wf1/Wf2 are single copies**, recomputed each tick from corrected
  SimBits. Gray files them under Workspace, which is fivefold. A flipped Wf
  lasts one tick, and Flag1 needs three of eleven.
- **Stage timing.** Three gathers at 0/8Q/16Q with the vote on arrival, then
  the early program, the SimBit procedure, the trickle-down window and the
  final program(s).
  - Gray's proportions are U/4 ×3 and U/8 ×2. His 8Q update stage assumes a
    looped program of size a·log(QU) and Q ≥ 2^13.
  - My straight-line programs need about 110Q (R1) and up to about 900Q (G5).
    R1 nonetheless has U = 128Q.
- **Candidate-B Flag2 erasure** is kept verbatim. Gray's printed Flag2
  persistence question stays open.

## 10. Failed and superseded approaches

**Compiler.** In-order issue of a depth-first order, with lane prefetch and
Belady replacement, fills 30–45% of slots.
- For R1, 4,364 of 7,246 idle slots wait for a lane at another cell, and
  2,503 wait for a value spilled elsewhere.
- The pass count stays at about 100–110 across Q ∈ {128, 256} and
  L ∈ {64, 96, 128}. The limit is pass depth (about 100 blocking events),
  not registers.
- None of these beat it: a windowed greedy scheduler (it serialized or
  thrashed), streaming order (worse), dwell under in-order issue (worse), 128
  random orders (best 112 passes), relaxed out-of-order issue (110), K-way
  interleaved streams (113), and window reads of x±1/x±2 (105, with larger
  netlists).
- Placement-based scheduling or richer instructions are the next options.

**Real bugs caught by closure tests:**
- The ROM was narrower than the `psel` range, so the C kernel read another
  row.
- The codec wrote only one of G's five Info copies (988 mismatches).
- G5's first build recursed infinitely in its corrected-value helper.

**Register limits:**
- G with L=32 cannot reserve its 17-register fetch key.
- G5 places the fetch key after computation instead (late placement). One
  sweep configuration failed that final placement; the edge case is open.

**Superseded designs:**
- G4 needs U=2^19 because every run recomputes the upper maintenance before
  its match pass.
- G5's per-tick fivefold front supersedes triple evaluation (G3/G4).

## 11. Not established

- Noise thresholds. Gray's ε < (QU)^-2 is about 1e-17 for G7.
- Level-k errors for k ≥ 2 beyond a colony-scale burst in one upper step.
  Gray's level-2 errors fit in 200Q × 200U, far beyond these runs.
- Trickle-down *repair* of a whole damaged upper colony (Gray Prop. 5):
  the mechanism is implemented and exercised, but not stressed by errors.
- A G level-2 macrostep (2^38 ticks) and three-level runs of any candidate.
- Self-organization from arbitrary configurations (Gács); not attempted.

## 12. GPU simulator (`gpu.py`)

The CUDA kernel is generated from the candidate's netlist. It is an
execution backend for the same fixed rule, and `GpuBackendTest` checks it
bit for bit against the C kernel.

- **Word layout.** 32 sites per 32-bit word, one thread per word. Gates are
  emitted in DFS post-order from the outputs, input bits are loaded at first
  use, and each output is stored as soon as it is defined. Pi is looked up
  only where `arrive` is set, between the key cone and the rest.
  - With `__launch_bounds__(256, 1)`, R1 compiles with no spills and G5/G6
    with about 5 KB of local-memory spills.
  - Per-tick latency went from 23 → 7.5 µs (R1) and 179 → 66 µs (G5).
- **Block mode:** one block per ring and `__syncthreads()` per tick. It serves
  many independent rings of the same length, e.g. one fault-free reference
  ring plus one ring per error pattern.
- **Grid mode:** a cooperative launch with `grid.sync()` per tick, spreading
  every word of every ring over the whole GPU. It serves two-level rings.
- **Errors (Gray §5.1).** An error replaces a site's whole state with random
  bits. The error pattern is a function of (config seed, site, tick) only.
  - **E0 grid:** space-time is cut into G×G cells, each holding one 1–2-site
    error. Any two errors are at least 25 apart in space or time
    (Chebyshev, ring wrap included), so every error is a level-0 error;
    G=50 is near the densest such pattern.
  - **Boxes:** Bernoulli(p) per site-tick; p=1 randomizes the whole box.
  - `GpuSim.error_masks` returns the exact error sites. A test checks the
    separation and the box shapes.

Measured on an A100-SXM4-80GB:

| candidate | ring | mode | µs/tick | site-updates/s |
|---|---|---|---:|---:|
| R1 | 8 colonies | block, 1 ring | 7.5 | 1.4e8 |
| R1 | 8 colonies | block, 864 rings | 12.8 | 6.9e10 |
| R1 | two-level, 16,384 sites | grid, 1 ring | 9.1 | 1.8e9 |
| R1 | two-level, 16,384 sites | grid, 8 rings | 9.6 | 1.4e10 |
| G5/G6 | 8 colonies | block, 1 ring | 66 | 6.2e7 |
| G5/G6 | 8 colonies | block, 864 rings | 1,172 | 3.0e9 |
| G5/G6 | two-level, 262,144 sites | grid, 1 ring | 171 | 1.5e9 |

Consequences:
- An R1 level-2 macrostep (2^28 ticks) takes about 40 minutes on one GPU,
  versus about 2.7 h on 8 CPU cores.
- A G5/G6 upper step of a full two-level ring (2^19 ticks on 262,144 sites)
  takes about 90 s. G two-level runs of several upper steps are therefore
  feasible, though a G level-2 macrostep (2^38 ticks) is not.

## 13. Space-time pictures

`spacetime.py` writes PNGs to `figs/spacetime/`
(time runs downward).

- **`R1_period.png`: one fault-free work period.** Left: the whole period,
  with the front shown in gray and writes in color. Middle (stride 1): the
  three-way mail streams shifting one cell per tick, lane captures at their
  skewed capture ages, then the boustrophedon front from Age 768. Right
  (stride 1): the last passes, the commit of Hold into Info at Age U−1, and
  the next period's gathers.
- **`R1_defects.png` and `R1_e0_zoom.png`: R1 with errors**, compared with a
  fault-free reference ring from the same initial state.
  - A single whole-state error has its Address/Age/flags repaired in 1 tick.
  - Its simulation fields stay wrong, as a vertical line: R1 keeps one copy
    of Info, lanes and scratch.
  - Mail and the front then carry the wrong bit diagonally.
  - Bursts and colony wipes are regrown structurally (the black Flag1/Flag2
    band is visible).
  - Dense E0 noise corrupts all upper cells every period.
- **`G6_defects.png` and `G6_e0_zoom.png`: the same experiments on G6.**
  - A single-site or two-site whole-state error, including one 40 ticks
    before the commit, is gone after **one tick**: the next state equals the
    reference bit for bit.
  - Under dense E0 noise (G=50) the decoded upper state stays exact in every
    period.
  - The burst panels use *random* upper states. There, a wrong upper cell's
    new state is gathered by its upper neighbours in the next period, so
    the difference spreads at the upper level. With a healthy upper colony
    the upper level removes it instead (§15).

## 14. Gray's error levels on one-level rings (`error_levels.py`)

**Setup.** 8 colonies with random upper states. Ring 0 has no errors. The
other rings get one pattern each:
- dense E0 (G=50) for all periods, or for 2 periods and then none;
- a 200×200 box (p=1) at one of nine phases of the period, placed mid-colony
  or across a colony boundary;
- colony wipes.

After every period the script records the wrong upper cells (vs F^k(upper0)),
the "closure-bad" cells (vs F(previous decoded ring)), and physical
differences from ring 0. Receipts are
`figs/error_levels/*.json`.

| pattern | R1 (64×64 boxes) | G5 | G6 |
|---|---|---|---|
| E0 dense, 4 periods | all 8 upper cells wrong | **decoded state exact**; physical differences at the 4 boundaries: 0, 0, 3, 6 sites | same as G5 |
| E0 for 2 periods, then off | wrong (no redundancy) | exact | exact |
| E1 mid-colony, after gather 1 | 1 cell wrong, closure exact afterwards | 1 cell wrong in the period of the burst | same as G5 |
| E1 across a colony boundary | 1 cell | 1–2 adjacent cells | 1–2 adjacent cells |
| E1 during gather 1 or just before gather 2 | 1 cell | all 8 cells wrong in that period, closure exact afterwards | same |
| colony wipe(s) | 1–2 cells | 1–2 cells | 1–2 cells |

- **Level-0 errors.** The decoded upper state stays exact under dense level-0
  noise.
  - The boundary samples here do not measure one-tick repair. The few
    differing sites at a boundary can be errors injected at that very tick.
  - *Correction (audit, §25):* the earlier wording "every error is repaired
    in one tick, and the whole physical state equals the fault-free one" went
    beyond this experiment.
  - The direct measurement is in §25:
    - In a healthy colony, every injected level-0 error is gone one tick
      later.
    - In a colony whose upper cell raises Flag1, Gray's own wipe rule gives
      the hit cell a two-tick footprint.
- **The gather-1 case is not a gather-vote failure.** The diagnostic
  (16 colonies) shows the burst wiping all five Info copies in a 200-site
  stretch. Upper cell 3's *own* state is therefore wrong from Age ≈3Q on.
  Gathers 2 and 3 deliver that wrong state to every neighbour, and the vote
  faithfully agrees on it. Upstairs this is an upper-level error at (cell 3,
  start of the step), and F spreads it to radius 5 by definition. Whether the
  upper level then removes it can only be seen with a healthy upper colony
  (§15).
- **Random upper rings cannot show upper-level correction.** Their upper
  Address/Age are random, so the upper maintenance, and with it the upper
  majority votes, does not act as in a healthy colony. Still, several
  mid-colony E1 rings return to 0 wrong upper cells after one more period,
  by the upper fivefold vote.

**Local-structure recovery after bursts** (`recovery_time.py`, G5/G6 at
Q=512). The time from the end of the box until the last tick at which any
Address/Age/Flag differs from the reference:

| burst | R1 (Q=128) | G5 / G6 (Q=512) |
|---|---:|---:|
| 200×200 mid-colony (R1: 64×64) | 57 | 209 / 210 |
| 200×200 across a colony boundary | 84 | 308 / 307 |
| whole colony, 200 ticks | 84 | 340 / 336 |
| two colonies, 2Q ticks | 128 | 516 / 512 |
| Gray's level-1 bound 200+500+2(Q+200) | 1,356 | 2,124 |
| rest between gathers | — | 1,475 / **3,523** |

G5's gather rest (1,475 ticks) exceeds every measured recovery time but not
Gray's bound. G6 (gathers at 0, 12Q, 24Q) satisfies Gray's bound as well.

## 15. Two-level rings with errors: the upper level removes the damage

`two_level_errors.py` builds the ring top → upper = encode(top) → physical =
encode(upper). For G6 that is one healthy upper colony of 512 upper cells
over 262,144 physical sites, with the same rule at both levels.
- Grid-mode GPU, one error-free ring plus one ring per pattern.
- Each error is placed in upper step 1.
- After every upper step the script compares the decoded upper ring with
  F^k(upper0), which is computed by the NumPy evaluator.

**G6, n2=1** (receipt `two_level_errors/G6_n2_1_main_seed5.json`):

| pattern (physical) | wrong upper cells after step 1 | after steps 2, 3, 4 | physical sites ≠ reference after step 3 / 4 | level-2 state |
|---|---|---|---|---|
| 200×200 burst mid-colony, during evaluation | [256] (6 bits) | **none** | **0 / 0** | intact |
| 200×200 burst across a colony boundary | [257] (3 bits) | **none** | 23 / 23 | intact |
| colony 256 randomized for 200 ticks | [256] (8 bits) | **none** | **0 / 0** | intact |
| colony 256 randomized for 200 ticks **during gather 1** | **none** | none | 14 / 14 | intact |
| colonies 256–257 randomized for 2Q ticks | [256, 257] (17 bits) | **none** | 10 / 10 | intact |
| dense E0 (G=50) throughout + colony wipe | [256] (8 bits) | **none** (E0 still on) | 285 / 315 (fresh E0) | intact |

The run was stopped after upper step 4 to free the GPU.
- In two rings the *physical* state became bit-identical to the fault-free
  ring: the error vanished at both levels.
- The constant residue in three other rings is in scratch only (see the
  one-level receipts). These are scratch slots that the program never
  writes: a burst leaves random values there and the fivefold vote keeps
  them. They are dead (never read), but G5–G7 lack Gray's clearing of the
  Workspace at the start of the work period (p. 34). **G8** adds it (§16).

This is the behaviour Gray's Proposition 4 describes, observed rather than
assumed:
1. A physical level-1 error, or a colony-scale error, leaves at most 1–2
   adjacent wrong upper cells at the next upper step. The lower level's
   structure recovers (§14), and it simulates F exactly from then on.
2. That damage is a level-0 error of the upper level. The upper level, which
   is the same rule, removes it in one upper step through its own fivefold
   majority and maintenance, exactly as the physical level removes physical
   level-0 errors.

In the gather-1 case the upper votes absorbed the damaged upper cell within
step 1 itself. The random-ring result (all 8 cells wrong) was an artifact of
random upper structure.

**G8, n2=1**: 1,024 upper cells over 1,048,576 sites, grid mode, 4 rings
(receipt `two_level_errors/G8_n2_1_main_seed5.json`):

| pattern (physical) | after upper step 1 | after step 2 | after step 3 | level-2 state |
|---|---|---|---|---|
| 200×200 burst mid-colony, during evaluation | [512] (1 bit) | **none** (120 sites differ) | **none; physical state = reference (0 sites)** | intact |
| 200×200 burst across a colony boundary | **none** | **none** (132 sites) | **none; physical state = reference (0 sites)** | intact |
| colonies 512–513 randomized for 2Q ticks | [512, 513] (5 bits) | **none** (607 sites) | **none; physical state = reference (0 sites)** | intact |

With the margin, the boundary burst never reaches the upper state, even at
the first upper step. After upper step 3, all three rings are
**bit-identical to the fault-free ring** on all 1,048,576 physical sites.
The damage vanished completely at both levels: the upper level removed it,
and the Workspace clearing flushed the dead leftovers.

**R1 two-level runs** (128 upper cells over 16,384 sites; the partial
receipt is `two_level_errors/R1_n2_1_level2_partial_seed5.json`):
- **Bursts.** A 64×64 burst, mid-colony or across a colony boundary, has
  vanished by upper step 1,024: 0 wrong upper cells, and the level-2 state
  is intact.
  - The mid-colony ring is physically identical to the reference.
  - The boundary ring differs in 1 site, a dead scratch bit.
  - Both stay that way through upper step 3,072.
- **Colony wipes** (during gather 1, or during evaluation) leave the same 10
  upper cells (13 bits) wrong from upper step 1,024 through 3,072, and the
  level-2 state is corrupted. R1 keeps one copy of Info at every level, so
  nothing can restore it.
- **Dense E0** corrupts every upper cell.
- The reference ring stayed exact.
- The full level-2 macrostep (16,384 upper steps) was paused at upper step
  3,072 to give the GPU to G8. It was restarted at 22:26 UTC (ETA about
  23:55); its receipt is `two_level_errors/R1_n2_1_level2_seed5.json`.

## 16. Does G contain Gray's mechanisms? (G5 → G6 → G7)

**Present in G5 and later:**
- **Local structure (§5.2).** Apparent colony C(x), conditions (i)–(iv), and
  Flag1/Flag2. Address/Age take a *directional* majority vote over R(x) or
  L(x), GKL-style, then Age is incremented. This is candidate-B maintenance,
  also in R1.
- **Hard-wiring (p. 31 steps i–iii) and projection (p. 32).**
- **Fivefold redundancy (p. 33)** of SimBit (Info), Workspace (Hold,
  scratch, histories) and Mailbox, majority-corrected every tick. It is
  extended to the evaluator's register file and pending writes.
- **Three information-gathering stages (p. 34)** with a majority vote over
  the three gathered copies, stored in separate locations.
- **Mailbox clearing** where Flag1 is set, and wiping of simulation structure
  where Flag1 is set and the Address changes.
- **The special procedure (p. 35):** SimBit at Q−3 := new upper Flag1 and at
  3 := new upper Flag2.
- **Trickle-down (§5.5, p. 41):** Workspace.Flag1/Flag2 during the first 2Q
  ticks of the trickle-down window.

**Gaps found and fixed:**
- **Gather separation.** G5's gathers at 0/8Q/16Q leave about 1,475 ticks of
  rest, less than Gray's level-1 recovery bound of about 2,124 ticks. G6
  uses 0/12Q/24Q (3,523 ticks), and closure plus the G checks are exact.
- **Colony margin (Gray p. 33).** Gray assumes Q ≥ 2K and places the needed
  SimBits away from the colony boundaries; the ends hold only the special
  SimBits and the Workspace.Flag cells.
  - G5/G6 have K=357 > Q/2 and put the represented bits in cells 0–357, with
    workspace anywhere.
  - **G7** (Q=1024, U=2^20, K=359) places every represented SimBit and every
    instruction slot, hence all Hold and scratch storage, in cells
    [128, 896).
    - The only margin cells with instructions are 3 and Q−3, during the
      early Flag program: 19 register-to-register operations of the front
      while it passes cell 3, plus the two Hold stores of the new upper
      flags, which is what Gray places there.
    - A burst up to 256 wide at a colony boundary can then reach the live
      simulation data of at most one colony, the one whose front it may
      hit. Gray's Prop. 4 allows two, so this is stricter.
    - G7 one-level result: all nine 200×200 bursts centred on a colony
      boundary, at every phase, left **no** wrong upper cell. In G5/G6 the
      same bursts left 1–2.
- **Workspace clearing (p. 34).** **G8** = G7 + scratch cleared at the
  period boundary, so scratch slots the program never writes cannot keep
  burst garbage (§15). G8: 13,631 gates, 43,163 instructions, 977 of 991
  passes. Closure is exact on the GPU (2 rings) and in the CPU G checks
  (coherent upper states, 2 periods, special procedure and Wf window OK).
- **G8 one-level result** (`error_levels/G8_main_seed3.json`, 3 periods):
  - The dense-E0 rings are physically identical to the reference at every
    boundary once the noise stops. While it runs, the boundary samples show
    0, 10, 0 differing sites, which may be errors injected at that very tick
    (see §25 for the direct one-tick measurement).
  - None of the nine colony-edge bursts damaged any upper cell. By the end
    of period 3, eight of those nine rings are **bit-identical to the
    fault-free ring**.
  - The ninth, at the commit, still differs in 80 dead history bits. Its
    garbage entered unused Hold after the boundary and is committed, then
    zeroed, one period later.
  - Mid-colony bursts damage the one upper cell they hit. These are random
    upper rings, so the upper level does not repair it here; §15 shows the
    repair with a healthy upper colony.

**Remaining deviations:**
- Wf1/Wf2 are single copies recomputed each tick, where Gray's Workspace is
  fivefold. A Wf error acts like a Flag1 error on local structure, and
  Flag1 needs 3 of 11.
- Workspace clearing (p. 34):
  - G5–G7 clear Hold at the commit, registers wherever the front is not,
    histories by the next gather, and mail by its reload at each gather
    start.
  - They never clear scratch, so dead scratch slots keep burst garbage (§15).
    **G8** = G7 + scratch set to 0 at the period boundary.
  - Gray also clears at every *stage* start; ours rewrites every value before
    reading it within a period.
- Stage proportions differ: gathers of about 6Q each, then an evaluation of
  about 950 passes, instead of Gray's U/4 ×3 and U/8 ×2 with active/rest
  halves.
- Candidate-B's Flag2 erasure is used as transcribed.
- Gray's proofs need Q ≥ 2^13 and U = 128Q. Ours use Q = 512–1024 and
  U = 1024Q, so every robustness statement here is empirical.
- **Q ≥ 2K (Gray p. 33) fails for G9–G15**, for example G13: Q = 512,
  K = 260, 2K = 520 (found by the audit, §25).
  - The purpose of the condition is to keep the needed SimBits away from the
    colony ends. G9–G15 serve that purpose with an explicit margin of at
    least 100 cells (122 in G13–G15) on each side, inside which every
    represented SimBit and all workspace lie.
  - Gray's proof assumes the inequality itself, which these candidates do
    not satisfy.
- **Beyond Gray, from Gács:** error-correcting codes instead of repetition,
  self-organization from arbitrary configurations, and variable-period
  amplification are not attempted. Like Gray's version, G assumes a good
  initial configuration.

## 17. Where G8's work period goes (input to the next Q/U optimization)

G8 needs U = 2^20. Its constraints split as follows:
- The gathers need 32 of the 1,024 passes a period allows (E0 = 32Q).
- The compiled program needs 977 passes. The compiler, not the amount of
  work, sets this count.

An instrumented recompile of G8 (in-order issue with lookahead 300 and
out-of-order window 32), with 768 working cells per pass:

| program part | passes | instructions | idle: next gate waits for a lane at another cell | idle: waits for a value spilled at another cell |
|---|---:|---:|---:|---:|
| early Flag program | 85 | 4,149 | 42,113 | 14,159 |
| phase A (fetch key) | 193 | 8,597 | 68,456 | 63,270 |
| final program | 655 | 30,417 | 222,913 | 215,964 |

- The final program issues about 46 instructions per 768-slot pass, a 6%
  fill; R1's program fills 43%.
- At full use, the 43,163 instructions would fit in about 57 passes.
- The front carries 32 registers, while the live working set is far
  larger. Values spill to scratch at the current cell, and inputs sit in
  lanes at fixed cells. Almost every stall is a wait for the front to come
  back to one of those cells.

The largest lever on U is therefore the scheduler (list scheduling over the
sweep, or planning each pass as a unit), with register count L and scratch
S as secondary levers. Q is bounded below by K = 359 bits plus two margins
of at least 100 cells, so Q = 512 would need K ≤ 312.

## 18. Smaller colony and work period: exact Q (G9)

**Observation.** The pass count barely depends on colony width: G5 needed
927 passes on 510 working cells and G8 977 on 768. Since U ≈ (E0q +
passes)·Q, QU grows like Q², and Q was a power of two only because the rule
assumed one.

**Exact-Q mode** (`q`, `nb` parameters of the G family; power-of-two
candidates are unchanged and their ten netlist digests are re-verified):
- Addresses are taken mod Q (`w_add_const_mod`).
- Age is stored packed, as (tick mod Q in the low k bits, tick // Q above),
  with a carrying increment (`mixed_age_increment`). U = nb·Q.
- On a backward pass the front arrives at cell Q−1−pos
  (`w_sub_from_const`).
- The Gray flag rule `(Age+1) % 16 == 0` reads the low 4 bits of the
  position, so Q must be a multiple of 16. Q is also a multiple of 64 for
  the bit-packed kernels.
- The maintenance netlist in this mode equals the integer reference
  `maintenance_scalar` on 1,500 structured neighbourhoods, including both
  wraps (`ExactQMaintenanceTest`).

**Sweeps** (`sweep_front.py`). Each configuration is compiled once with
generous budgets to measure what each program part needs, then recompiled
with the tightest NPe/MP/NP and the smallest period.

| configuration | K | passes needed | Q | U | QU |
|---|---:|---:|---:|---:|---:|
| G8 (power of two, margin 128) | 359 | 958 | 1024 | 1,048,576 | 2^30.0 |
| L = 64, margin 128 | 519 | 606 | 1024 | 1,048,576 | 2^30.0 |
| **G9: exact Q = 576, margin 100, window 16** | 360 | 1,162 | **576** | **711,936** | **2^28.6** |
| same, window 24 | 360 | 1,146 | 576 | 702,720 | 2^28.6 |
| exact Q = 704, L = 48 | 440 | 849 | 704 | 643,456 | 2^28.75 |

Other settings made no real difference: scratch S ∈ {2, 8, 16},
interleaved or spread layouts, zero skew, dwell 2, and lookahead or
out-of-order windows between 8 and 512 (receipts in
`figs/.../sweep/`). With this scheduler, QU is nearly flat in L, because a
larger register file raises K and therefore Q.

**G9** = G8's mechanisms (fivefold everything, three voted gathers,
special procedure, trickle-down, Gray's margin of at least 100 cells,
Workspace clearing) at exact Q = 576, U = 711,936.
- It has 14,394 gates, 42,923 instructions, and uses 1,167 of its 1,203
  passes.
- QU is 2^28.6, 2.6× smaller than G8. G5 had QU = 2^28 but lacked the
  margin, the wider gather spacing and the Workspace clearing.
- Checks passed:
  - bit-exact GPU parity with the C kernel;
  - one-period closure on GPU;
  - CPU G checks (random and coherent upper states, 2 periods each:
    special procedure, Wf windows, Info copies agree, healthy geometry);
  - margin and clearing tests.
- Its level-1 campaign is in §19.

**Next levers**, not done:
1. **Confine the front to the working area.** A pass would then take W = Q −
   2·margin ticks instead of Q, making U about 1.5× smaller. It needs
   another way to deliver the new upper flags to the special cells 3 and
   Q−3, which sit in the margins by Gray's design.
2. **A new scheduler.** G9's program fills about 10% of its slots, and
   nearly every stall is the next gate waiting for the front to return to a
   cell holding a lane input or a spilled value.

## 19. Burst campaign (G8, G11, G12; first called "level-1 campaign")

*Correction (audit, §25).*
- **The bursts are not single level-1 errors.** The bursts below are dense
  200×200 boxes. Under Gray's §5.1 definition, a dense box of side at most
  104 is one level-1 error, but a dense 200×200 box contains two
  (104,104)-separated linked pairs. It is therefore a union of several
  level-1 errors, not one, and the results below are for such bursts. §25
  adds genuine level-1 errors (dense 100×100 boxes and sparse clusters
  checked by `gray_errors.py`) and adversarial error values.
- **"Repaired" is decoded only.** It refers to the decoded upper state.
  Full-state recovery is reported separately ("identical", and §25's
  Proposition-4 measurements).

`level1_campaign.py` runs two-level rings on the GPU.
- **Upper colony:** one healthy colony encoding a random top cell,
  optionally advanced with the rule into any stage of its own work period.
- **Physical ring:** encodes either the whole upper colony (Q² sites) or a
  64-upper-cell slice centred on the target cell.
  - A slice's ends meet at an Address jump. The script checks that its
    influence stays at least 23 upper cells away from the target over all
    tested steps, so the target behaves as in a full colony.
- **Errors:** every ring except the reference gets one burst, a 200×200
  box in which every site's whole state is randomized at every tick, during
  upper step 1.
  - Named phases: gathers 1–3 (middle and end), the rests between them,
    the start of the evaluation window, the early Flag program, the special
    procedure, the trickle-down window, phase A, the match pass, the final
    program, the end of the program, and the commit.
  - Each named phase gets three placements: the target colony's middle, its
    left boundary and its right boundary.
  - Plus random (site, tick) placements overlapping the target colony.
- **Criteria** (Gray §5.1, Prop. 4):
  - *contained*: after the burst's step, at most 2 adjacent upper cells
    next to the target are wrong;
  - *repaired* (decoded): no upper cell is wrong from the next upper step
    on;
  - *identical*: the physical state finally equals the fault-free ring bit
    for bit.

**Results** (receipts `level1_campaign/*.json`; "identical" means
bit-identical to the fault-free ring after the last upper step):

| candidate | batch | upper colony stage | errors | contained | repaired | identical |
|---|---|---|---:|---:|---:|---:|
| G8 | b1 | its own gathers (+ dense E0 ring) | 64 | 64 | 64 | 61 at step 3 (+3 at step 4, rerun) |
| G8 | b2 | mid-evaluation, target holds the upper front | 64 | 64 | 64 | 61 at step 3 (+3 at step 4, rerun) |
| G8 | b3 | just before its commit | 64 | 64 | 64 | 61 at step 3 (commit-time 3 not rerun) |
| G8 | b4 | partial-density boxes (p = 0.02, 0.1, 0.5) and 24 linked pairs of level-0 errors | 43 | 43 | 43 | 43 |
| G11 | b11 (seed 17) | its own gathers | 64 | 64 | 64 | 64 |
| G11 | b11 | its own gathers (+ dense E0 ring) | 64 | 64 | 64 | 64 |
| G11 | b12 | mid-evaluation, upper front hit | 64 | 64 | 64 | 64 |
| G11 | b13 | just before its commit | 64 | 64 | 64 | 64 |
| G11 | b15 | partial-density boxes and linked pairs | 43 | 43 | 43 | 43 |
| G12 | b21 | its own gathers (+ dense E0 ring) | 64 | 64 | 64 | 64 |
| G12 | b22 | mid-evaluation, upper front hit | 64 | 64 | 64 | 64 |
| **total (first report)** | | | **662** | **662** | **662** | **653** |
| G11 | b14 | full 262,144-site colonies, upper front hit | 14 | 14 | 14 | 14 |
| G10 | b16 | its own gathers | 64 | 64 | 64 | 64 |
| G13 | b31–b33 | gathers (+ E0 ring), phase A with front hit, final program with front hit (before the match gate fix, §23) | 192 | 192 | 192 | 192 |
| G13 | b34–b36 | the same three stages, after the fix | 192 | 192 | 192 | 192 |
| G14 | b41–b43 | the same three stages | 192 | 192 | 192 | 192 |
| G8 | b5 | full 1,048,576-site colonies, upper front hit | 8 | 8 | 8 | 8 |
| G9 | b6 | its own gathers (+ E0 ring) | 64 | 64 | 64 | 64 |
| G9 | b7 | mid-evaluation, upper front hit | 64 | 64 | 64 | 64 |

The reference ring was exact at every step of every batch. G8–G9
full-colony batches and G10/G11 extras were still queued when this was
written (logs in `level1_campaign/b*.log`).

- **Damage.** Most bursts leave no wrong upper cell at all. The upper votes
  absorb the corrupted colony within the same step: 53 of 64 in b1 and 42
  of 64 in b2. The rest damage only the target upper cell.
- **Boundary bursts.** Of 64, one damaged the upper state. In b2 a
  right-boundary burst during the final program left upper cell 33 wrong,
  the neighbour across the boundary (11 bits).
  - The burst lies entirely in the two margins. All colonies' fronts sit at
    the same relative Address, so at most one front can be inside such a
    burst; here it was colony 33's front, crossing its left margin.
  - That single-colony case is exactly what the margin design allows, and
    the upper level repaired it at step 2.
- **The three exceptions** in each batch are the bursts at the commit,
  which straddle the period boundary.
  - Their upper state is exact from step 2 on.
  - Their remaining differences are dead data: garbage in unused Info, then
    in mail and history lanes loaded from it.
  - For b1 a 5-step rerun shows them bit-identical from step 4 on
    (`G8_b1_commit_5steps.json`).
    - *Correction (audit, §25):* that rerun drew new random values for the
      same boxes. Its noise seeds depended on the scenario's position in the
      filtered list.
    - The driver now derives each seed from the scenario's identity. A rerun
      with the original faults reproduces the original steps exactly and is
      bit-identical from step 4 (`G8_b1_commit_rerun_sameseeds.json`).

Still running: b3 (upper colony just before its commit), b4 (partial-density
boxes and linked pairs of level-0 errors), and b5 (full 1,048,576-site
colonies with the upper front targeted). Then the same set for G9.

## 20. Second stride: confined front (G10), compact front (G11), scheduler attempts

| candidate | Q | W (front sweep) | U | U/Q | QU | change |
|---|---:|---:|---:|---:|---:|---|
| G8 | 1024 | 1024 | 1,048,576 | 1024 | 2^30.0 | Gray-complete baseline |
| G9 | 576 | 576 | 711,936 | 1236 | 2^28.6 | exact Q (§18) |
| **G10** | 576 | **368** | 462,208 | 802 | 2^28.0 | front confined to the working area; flags reach cells 3 and Q−3 by courier |
| **G11** | **512** | 272 | **326,400** | 638 | **2^27.3** | G10 + compact fivefold front, L = 64 |

**Confined front (G10).**
- The front sweeps only the working cells [margin, Q − margin), so a pass
  takes W = Q − 2·margin ticks.
- Age is packed with radix W, and the evaluation window starts at a whole
  W-block (E0 = ⌈32Q/W⌉·W).
- **Courier.** Gray keeps the special SimBits at cells 3 and Q−3, inside
  the margins the front no longer visits.
  - The early program stores the new upper Flag2 in Hold at the left
    working-area end (cell lo), and Flag1 at the right end (hi − 1). Both
    cells are reserved from the layout.
  - At Age T_sig − lo + 2, cell lo puts its Hold on the fivefold left mail
    track; at Age T_sig − (Q − 2 − hi) − 1, cell hi − 1 puts its Hold on the
    right mail track.
  - The bits arrive at cells 3 and Q−3 exactly in the state of Age T_sig,
    where the special procedure now takes the SimBit from the mail rather
    than from Hold.
  - The early program ends one pass early, so both sources are final
    before the couriers load.
- **Upper cells with margin Addresses** never see the upper front, so their
  fetched instruction word is irrelevant. Closure on random upper states,
  which include such cells, confirms it.
- **Checks passed:**
  - GPU parity with the C kernel, and one-period closure on GPU;
  - CPU G checks on random and coherent upper states, 2 periods each: the
    special procedure (courier-delivered flags equal the new upper flags at
    T_sig + 1), the Wf windows, Info copies, and geometry;
  - margin and clearing tests.

**Compact fivefold front (G11).**
- In G5–G10 each cell stores five register-file slots, 5L bits, one per
  logical neighbour. But there is one front per colony, so at most one slot
  is ever non-zero.
- G11 keeps one L-bit slot per cell: "my copy of the front within two
  cells". The front's register file is the majority of the five slots
  around it.
  - Any window within two cells of the front still sees at least three
    copies, so the fivefold front step is unchanged.
  - Every tick, the cells within two of the new front position store the
    new register file, and all other cells clear their slot.
  - The pending-write fields stay fivefold.
- This frees 4L bits per cell. At L = 64 and Q = 512, K is 262 bits, against
  G10's 359 at L = 32.
- **Checks passed:**
  - GPU parity and closure;
  - CPU G checks on random and coherent upper states;
  - margin and clearing tests;
  - `CompactFrontTest`: flipping register bits in one copy, or in two copies
    at once, near the front mid-evaluation leaves the ring bit-identical to
    the unfaulted run three ticks later.

**Scheduler attempts** (approach 2):

| attempt | effect |
|---|---|
| out-of-order window 8–512, lookahead 200–1000 | flat (±5%) |
| interleaving 2 or 4 output cones, lookahead 600 | up to 7% fewer passes (used in G11) |
| interleaving 8 cones, or streaming order | fails (the program does not finish) |
| new location-aware list scheduler (`run_sweep`: global ready set; at each cell store, compute, load or spill whatever is most useful there) | correct (R1 closure exact) but worse: 166–212 passes on R1 against the in-order 110; on G10 it stalls |

**Why U/Q is still about 640 against Gray's 128.**
- Gray gives the transition 16Q ticks, 8Q of them active. The whole colony
  computes in parallel, and his argument lets Q grow far beyond the size of
  the transition program (Q ≥ 2^13, program about a·log Q).
- Here a single front executes one instruction per tick, so one cell in Q
  works at a time, and the scheduler fills only 10–18% of the slots it
  sweeps past (G10: 42,017 instructions in 1,121 passes × 368 cells; G11:
  51,906 in 1,053 × 272).
- Each output's cone has a median of about 3,100 gates and draws inputs from
  a median of 132 cells spanning the working area.
  - With 32–64 registers, the front must return to those cells repeatedly.
  - At full slot use, G11's program would need 191 passes instead of 1,053.
  - Register capacity, not the amount of work, is what costs U.
- **Next directions:**
  - A structure-aware compiler: compute the shared values once (computed
    Age/Address, flags, control decodes), place copies where they are
    consumed, then stream through the outputs.
  - Several fronts working in parallel. They cost no extra bits per cell,
    since a cell holds at most one front, but fronts reversing at the
    colony ends must not collide.

### Level-1 results for the smaller candidates

**G8 batch b3** (upper colony just before its own commit): 64/64 contained
and 64/64 repaired from upper step 2. 61/64 were physically identical at
step 3; the three commit-time bursts behave as in b1/b2. The b2 commit cases
were rerun for 5 steps: 3/3 identical by step 4
(`G8_b2_commit_5steps.json`). That rerun also drew new random values; the
reruns of b2 and b3 with the original faults are in §25.

**G11** (receipt `level1_campaign/G11_b11s17_age0_mid.json`: seed 17, upper
colony in its gathers, 4 upper steps):
- 64/64 bursts contained, 64/64 repaired, 64/64 bit-identical to the
  fault-free ring by upper step 4. The reference ring was exact at every
  step, and dense E0 caused no damage.
- Colony-boundary bursts never damaged the upper state. This includes the
  special-procedure phase, when the flag couriers cross the margins.

**Script bug, found in this run.** `phases()` in `level1_campaign.py` and
`error_levels.py` placed evaluation-window bursts at E0 + passes·Q. For a
confined front a pass takes W ticks, not Q.
- In the G11 batch above, the "final program" and "program end" bursts
  therefore landed in period 2. Their upper cell was wrong after step 2 and
  repaired at step 3. The "early program", "phase A" and "match pass"
  bursts landed elsewhere in period 1.
- All bursts are still valid level-1 errors, and all were contained and
  repaired; only the phase labels were wrong.
- Both scripts now use the pass length. G8/G9 are unaffected, since their
  pass takes Q ticks.
- The queued G10/G11 batches use the corrected times.

## 21. Structure-aware compilation (G12)

**Diagnosis on G11** (`struct_analysis.py`, `store_profile.py` in the
session scratch; numbers from the instrumented compiles):
- The final program has 19,199 gates for 262 outputs.
  - A shared core of about 2,450 gates is used by at least 160 outputs. It
    is Gray's local-structure maintenance plus the controls derived from
    the computed Age and Address; its 37 boundary values depend only on
    the Address/Age/flag fields.
  - The fivefold front step (about 11,100 gates) is used only by the
    register and pending-write outputs.
  - Each output's own local work is about 50–120 gates.
- Store timeline: the core alone took about 110 passes. All its inputs,
  and the scratch it spilled into, sat on the first 42 working cells, which
  the front passes for only 42 ticks of each 272-tick pass.
- Loads were 52% of all instructions: each of the 1,897 inputs was loaded
  about 11 times.

**What worked:**
1. **Data placement: `proportional_layout`.** Every field is spread evenly
   over the working cells, so every stretch of the colony holds a sample of
   every field and the front meets needed data throughout each pass.
   - Spreading only the Address/Age/flag bits took passes from about 1,100
     to 794; spreading all fields took them to 722.
2. **Single-step front: rule option `mux_front`, the same function.** The
   five candidate slots have pairwise distinct Addresses, so at most one
   "arrive" holds for any input. The OR of five gated front steps then
   equals one step on the arriving slot's selected inputs.
   - 19,675 → 16,732 gates (G11 parameters).
   - Checked equal on 32,768 random and 24,576 forced-arrival input
     vectors (`MuxFrontEquivalenceTest`).
3. **Scheduler settings:** 4-way interleaving with lookahead 1,500.

| | G11 | **G12** |
|---|---:|---:|
| gates | 19,675 | 16,619 |
| instructions | 51,906 | 42,739 |
| passes | 1,053 | 695 |
| U | 326,400 | **217,328** |
| QU | 2^27.32 | **2^26.73** |
| U/Q | 638 | **424** |

**What did not help:**
- Rebuilding associative trees into sweep-ordered chains (`reassoc`): at
  most 2% (−7% on R1). It helps slightly only together with the
  proportional layout.
- Layouts that put the five copies of a fivefold bit next to each other:
  worse (923 passes), because five lane reads then fall on one cell.
- Window reads within radius 5 (±1 cell) would save 10% (675 → 610
  passes, measured by letting the compiler assume them); ±2 would save 31%
  but needs radius 6.

**Why 23% fill is the practical ceiling for one front.** Each working cell
holds about 11 lane inputs, and one front executes one instruction per
visit with 64 registers. In the final program, 75% of idle slots are the
next gate waiting for a lane input at another cell. Several fronts
multiply both read bandwidth and register capacity; that is the next
stride.

**G12 validation:**
- GPU parity with the C kernel and one-period closure; CPU G checks.
- `CompactFrontTest` (register-copy faults), margin and clearing tests.
- Level-1 campaign batches b21/b22, running at the time of writing.
- 33 tests pass.

## 22. Several fronts: first estimate

*Correction (see §23).* Two statements below were wrong:
- The lanes of a register bit do not all sit on one cell: G12's skews
  (4, 7, 5, 4, 8, 1, 8, 0, 2, 6) spread them over about nine cells.
- "About 11 passes per register bit" does not explain the critical path.
  With unlimited registers and slots, the whole final program has a
  dataflow depth of about 10 passes; the limit is the scheduler (§23).

The folded match table proposed at the end was not needed: the comb's
overhang is made a no-op instead (§23).

**The comb.** F fronts spaced Δ = 8 cells apart sweep and turn together, so
they never meet, and at most one front is ever within two cells of a given
cell (needed by the compact front).

**Geometry.** If the fronts stay inside the working area, front j reaches
only W − (F−1)Δ cells. With the proportional layout, every output needs
inputs from the whole working area, so no front can finish any output.
The comb must overhang into the margins by (F−1)Δ cells (24 for F = 4), so
that every front covers the whole working area.
- A pass then takes W + (F−1)Δ ticks.
- Fronts now enter the margins, so a colony-boundary burst could hit the
  fronts of both neighbouring colonies. G10–G12 guarantee at most one.

**Estimate on G12** (`multifront_est.py` in the session scratch). Each
front compiles its share of the final program, recomputing the shared core
itself, with the existing scheduler. Final-program passes:

| fronts | front 0: upper front step (register/pending outputs, 89) | other fronts |
|---:|---:|---:|
| 1 | 571 (everything) | — |
| 2 | 502 | 157 |
| 4 | 502 | 104–120 |
| 8 | 502 | 73–90 |

**The upper front's register-file update is the critical path.**
- It needs the incoming register file, 64 bits. Each bit is a fivefold
  majority over up to seven offset windows, drawn from 11 gathered lanes
  that all sit on the bit's own cell.
- A front reads one value per visit, so each register bit costs about 11
  passes of visits. The operand selection then ORs over all 64 bits.
- The lanes cannot be skewed apart: the layout fills the working area, and
  a skewed lane would land in a margin the confined front never visits.

Several fronts help only if this update is itself split. Front j would
compute the incoming bits and partial operand ORs for 64/F of the
registers, and the partial results would be combined through scratch
before the ALU result is broadcast back. That is a compiler transformation
(splitting large associative reductions across fronts) plus the rule
changes for the comb (per-front arrival, front id in the instruction
selector, and a folded match table so front 0 can fetch every Address).

## 23. Several fronts: the comb (G13, G14)

**Result.** Five fronts moving together cut the program from about 650
passes to about 270, at the cost of a pass 20 ticks longer.

| | fronts | Q | pass (ticks) | NPe / MP−NPe / NP−MP−1 (passes used by early / A / final) | U | U/Q | QU |
|---|---:|---:|---:|---|---:|---:|---:|
| G12 | 1 | 512 | 272 | 47 / 118 / 571 | 217,328 | 424 | 2^26.73 |
| G13 | 5 | 512 | 288 | 33 / 78 / 267 (22 / 58 / 253) | 125,856 | 246 | 2^25.94 |
| **G14** | 5 | 512 | 288 | 32 / 67 / 227 (25 / 61 / 207) | **110,880** | **217** | **2^25.76** |

### Design (`rule.py`, `rule_g.py`; active only when `fronts > 1`)

**Geometry.** F fronts, Δ cells apart, move in lockstep.
- In a forward pass, front j is at lo − H + t + jΔ, where H = (F−1)Δ and
  t = 0 … W+H−1. A backward pass is the same motion reversed in time.
- Every front therefore visits every working cell once per pass, and a pass
  lasts W + H ticks.
- The comb overhangs the working cells by H at both ends. There it only
  carries its registers: register writes, Hold and scratch stores, and the
  match pass are all gated by lo ≤ Address < hi.

**Arrival and program selection.**
- A cell sees front j arrive when Address − (front 0's cell) = jΔ.
- The front index goes into the instruction selector:
  psel = page + (j << logNP).
- Each front therefore runs its own program with its own register file.
- Every front starts at position 0 of the first pass, and stays in place
  (turns) at position 0 of every later pass.

**Why the compact front still works.** With Δ ≥ 5, at most one front is
ever within two cells of a cell. So G11's single register slot per cell and
the fivefold pending writes carry over unchanged.
- Each front's register file is still held on five consecutive cells and
  majority-voted every tick.
- CompactFrontTest shows that one or two corrupted register copies of a G13
  front are outvoted.

**Level-1 exposure.** Front state lies within two cells of a front, and the
comb reaches H cells into each margin.
- The right-hand colony's front state therefore starts 2·margin − 2H − 3
  cells after the left-hand colony's.
- With margin 122 and H = 20 this gap is 201 cells. A 200-cell burst can
  reach the front state or SimBits of at most one colony, as in G7–G12.
  `check()` asserts this.
- The margin is 122 rather than 120 so that the Age radix W + H = 288 is a
  multiple of 16, which Gray's flag rule needs.

**Fetch.** Only front 0 holds the lookup key (phase A leaves it there). Its
cells are [lo − H, hi − 1], which cover every working Address.

**Fix found by review.** In the first G13 build, a non-lead upper front
crossing the right overhang during the match pass could still match its
leftover key against that cell's Address. Front 0 one level down never
reaches that Address, so the colony could not reproduce the fetched word.
- Now only working cells answer the match pass, so overhang cells never
  depend on I.
- A test builds exactly this situation, with front 4 in the overhang, its
  key equal to its Address and I flipped. It fails without the gate.
- The tests, the closure runs and batches b31–b33 had not triggered the
  bug. All G13/G14 numbers below are from the fixed rule, except b31–b33.

### Compiler (`multifront.py`)

- **Partition.**
  - Upper bits are dealt to fronts by the rank of their layout cell
    (interleaved), and every lane of a bit belongs to the bit's owner.
  - A gate reading lanes of one owner goes to that owner.
  - A gate feeding a single Hold root goes to the root's owner.
  - Gates derived only from the fetched instruction go to the front that
    consumes them.
  - The remaining combining gates go to an operand's front.
- **Reduction.** Associative trees are regrouped by owner. Each front folds
  its own share of, for example, the 82-way operand selection, and the
  partial results are combined at the end.
- **Issue.** Each front issues in order: the depth-first order restricted to
  its own gates, with lane prefetch and Belady replacement.
- **Communication.** A value another front needs is written to scratch at
  the producer's current cell. The consumer reads it when it visits that
  cell.
  - In a forward pass, lower-index fronts visit a cell Δ ticks per index
    after higher-index ones; the order reverses in a backward pass.
- **Checks.**
  - Every phase is replayed abstractly on random data against the netlist.
  - The physical checks are GPU closure and the level-1 campaign.
- **Sizing.**
  - `sweep_comb.py` sizes the page ranges.
  - `search_comb.py` searches seeds (the depth-first order and the
    owner permutation) and refits the ranges.

### Estimates on G12's netlist (all three programs, replay-checked)

| fronts | pass (ticks) | early / A / final passes | total | total ticks |
|---:|---:|---|---:|---:|
| 1 | 272 | 38 / 100 / 509 | 649 | 176.5k |
| 2 | 277 | 28 / 115 / 340 | 485 | 134.3k |
| 3 | 282 | 28 / 77 / 256 | 363 | 102.4k |
| 4 | 287 | 24 / 75 / 236 | 337 | 96.7k |
| **5** | 292 | 26 / 50 / 191 | **269** | **78.5k** |
| 6 | 297 | 24 / 48 / 193 | 267 | 79.3k |
| 8 | 307 | 24 / 60 / 176 | 262 | 80.4k |

Five fronts is the knee.
- Beyond five, the program shortens very little.
- More fronts also need a wider overhang: the exposure bound allows
  H ≤ 20 at margin 122, which is F = 5 at the minimum Δ = 5.

Single compiles vary by about ±15% with the seed and with the rule
constants. The seeded search over 12 seeds on G13's own netlist gave U
from 110,880 to 148,608 (median about 118,000); G14 is the best.

### Ideas that did not help

Numbers are passes, in the same model. The baseline is the table above
(F = 4: 236 final, F = 5: 269 total).

| idea | result |
|---|---|
| Control cut: values mixing several owners are broadcast, not owned (F = 4) | final 385–601 |
| Address, Age and flag lanes unowned, control broadcast from front 0 (F = 4) | 309–335 |
| Each front recomputes the control cone itself (9,644 cloned gates, F = 4) | 339–367 |
| Owners in contiguous blocks instead of interleaved (F = 4) | 279 |
| Combining gates on front 0 instead of spread (F = 4) | 240 (no change) |
| ASAP issue order (sorted by earliest possible visit) | deadlock: registers fill |
| Issue order = execution order of the previous schedule, iterated (F = 5) | 191 → 197–253, no gain |
| Lookahead 150/600/1000, OOO window 16/64 (F = 5) | 285–341 total, worse |
| Window reads ±1 (scheduler only, F = 5) | 279 total (no gain) |
| Window reads ±2 (scheduler only, F = 5) | 228 total, but needs radius 6 |
| 32 registers per front (F = 5) | 429 total |
| Q = 576 (wider working area), or Q = 576 with 8 scratch bits (F = 5) | 329 / 367 passes of 356 ticks |
| More registers in the rule, one front: L = 96 / 128 (Q = 576) | final 601 / 809 (the netlist grows too) |
| Location-aware list scheduler `run_sweep`, admission 4–1024, reserve 2–8 (one front) | final 585–1685 |

### Where the limit is now

Three measurements on G12's final program (16,364 gates):

| | one front | four fronts |
|---|---:|---:|
| dataflow depth (unlimited registers and slots) | 10 passes | 7 |
| slot bound (one instruction per visit, unlimited registers) | 77 | 22 |
| in-order scheduler, 64 registers per front | 509 | 225–236 |
| same scheduler, 128 / 256 registers (scheduler only) | 371 / 333 | 141 / 137 (F = 5) |

- The machine could run the final program 6–10× faster than the
  scheduler does.
- Most of the gap is the in-order issue: more registers help, then
  saturate.
- In the one-front schedule the registers are nearly full (60 of 64 on
  average), mostly with values needed soon, while the head waits for a lane
  or spill at a cell the front has not reached.
- A scheduler that places work by the front's position under a register
  budget is the next large gain, for one front and for the comb alike.
  The attempts listed above (ASAP order, list scheduling, reordering) did
  not achieve it.

### Validation of G13 and G14

- **GPU (`gpu_check.py`).** Bit-exact parity with the C kernel on arbitrary
  states, and closure after one full work period on random upper states:
  G13 2/2 rings, G14 2/2 rings.
- **Tests (37).**
  - CombTest:
    - geometry and ROM columns per front;
    - arrivals exactly at the five comb positions, in a forward and in a
      backward pass;
    - the overhang/match-gate invariant;
    - replay of the comb scheduler.
  - G13 and G14 are also in ColonyMarginTest and CompactFrontTest.
- **Level-1 campaign on G13** (§19): bursts at 16 phases × 3 placements,
  plus random bursts, on two-level slice rings with the upper colony in its
  gathers (with a dense level-0 ring), in phase A with its front hit, and in
  its final program with its front hit.
  - Before the match-gate fix (b31–b33): 192 of 192 contained, repaired
    and bit-identical.
  - After the fix (b34–b36): the same, 192 of 192.
  - The reference ring was exact at every step of all six batches.

## 24. Compiler work after G14

**Goal.** Shorten the program further without changing the machine.
**Result.** No candidate beats G14.
- One netlist change (select-then-vote) shortens the one-front program.
- The comb's scheduler has plateaued.
- All numbers below are on G12's netlist with generous page budgets. Every
  compiled program was replayed against the netlist (0 mismatches).

### What the measurements say

**One front, final program (509 passes).**

| value class | intervals | never read | register-ticks | mean hold (ticks) |
|---|---:|---:|---:|---:|
| computed values | 16,364 | 0 | 3.92M | 240 |
| prefetched lanes | 3,833 | 1,729 | 2.53M | 1,204 |
| reloaded spills | 1,634 | 709 | 1.29M | 1,392 |

- **Register capacity.** Registers are nearly always full: 7.7M of 8.7M
  register-ticks are used.
- **Stalls.** There are 5,979 stalls. They are short (median 3 ticks,
  mean 19) and frequent: the in-order head waits for the front to reach the
  next lane cell.
  - Of 94k idle ticks spent waiting for lanes, 54k were for lanes never
    prefetched and 40k for lanes prefetched and evicted before use.
- **Critical chain.** The last outputs are simply late in one serial
  stream, so one front is throughput-bound.
- **Registers are needed.** The greedy that reaches the 77-pass slot bound
  keeps on average 1,241 computed values live (at most 2,347), about 20× the
  register file.

**Five fronts (185 passes).** Front 0's serial stream sets the finish time.
- Front 0 executes 6,870 gates and 4,988 loads.
- Fronts 1–4 idle 80–86% of the time, mostly (60–68%) waiting for front 0's
  values.
- Along the critical chain, 81 passes are same-front waits on front 0 and
  6 are cross-front transfer.
- About 1,600 of front 0's gates are the upper cell's Address/Age
  maintenance and arrival logic. About 900 are per-register-bit gates pulled
  onto front 0 because they combine a control signal with a register lane.

### Netlist co-design: select, then vote (`sel_front`)

**Mode 1, select then vote.** At most one front arrives at a cell. So
instead of voting the five register copies for each of the seven possible
source windows and then selecting, the rule selects the arriving front's
five copies with a one-hot selector and votes once. Lane sources are
treated the same way.
- SelFrontEquivalenceTest checks that the state transition is identical to
  `mux_front`. It uses random inputs and forced comb arrivals, including
  match passes. A negative control was missing until the second audit
  pointed it out (§27): the test now also mutates single gates of the new
  netlist (one AND, OR or XOR replaced by another) and requires the same
  comparison to catch every mutant of a gate driving a register output (8
  of 8) and most mutants of random gates (13 and 16 of 20, for the two
  modes).
- G14's netlist shrinks from 16,966 to 14,601 gates (−14%), and the
  register lane reads per bit drop from about 77 to 35.

**Mode 2, vote then select once.** The seven lane-only votes are kept, and
one 7-way select replaces the per-slot selects and the pick: 15,044 gates.

| netlist | one front: early / A / final (total) | five fronts: total |
|---|---|---:|
| G12 (mux_front) | 38 / 100 / 509 (649) | 269 |
| mode 1 | 38 / 85 / 436 (561) | 457 |
| mode 2 | 38 / 109 / 510 (659) | 267 |

- **One front.** Mode 1 helps: −14% passes.
- **Five fronts.** Mode 1 hurts. The selectors feed every register gate
  directly, so the partition either pulls whole register slices onto
  front 0 (9,922 of 14,601 gates) or, when balanced, makes every slice
  wait for the selectors from front 0 (304–445 final passes).
- **Mode 2** gives no gain on either.
- Candidates keep `mux_front`. `sel_front` stays as a tested rule option.

### Scheduler variants

| variant | result |
|---|---|
| Just-in-time prefetch (load at the cell's last visit before the head needs it, from a measured issue rate) | 3–4× worse: a low rate means fewer prefetches, which lowers the rate further |
| Position-driven scheduler (`flow.py`, archived in `archive/g_family/`): run whatever can run at the current cell, park values at their consumer's cell, depth-first admission window | best 583 (one front); deadlocks with wide windows |
| Issue order from a sequential model of the front | 529–643 (one front) |
| Out-of-order window 32–512, free-register floor, lookahead 300–800 (one front, mode 1) | 295–587; the best setting gives 357 and 549 with other depth-first seeds |
| The same grid on five fronts | 185–230 (default 191) |
| Interleaved depth-first streams, K = 2–16 (one front) | 333–540, one deadlock |
| Controls recomputed on every front, partitions following owned operands (five fronts) | 193–425 |
| Each front first does work needing fewer cross-front hops (five fronts) | 243–349 |
| The cone of values needed by several fronts issued first (five fronts) | 196–445 |
| 24 more seeds for G14 with lookahead 800 and free-register floor 4 | best U 111,744 (G14: 110,880), median 124,272 |

**Conclusion.**
- Per-front in-order issue with prefetch and Belady replacement is
  saturated. Its results swing about ±30% with the depth-first seed, which
  is a sign of unstable dynamics rather than a tunable optimum.
- The remaining gap to the slot bound (77 passes on one front, 22 on
  four) needs a different kind of compiler.
- **What that would look like:** a spatial one, in the style used for
  coarse-grained reconfigurable arrays:
  - give every gate a home cell;
  - route values along the sweep, in registers only while they travel;
  - schedule each cell's gates across passes, with scratch holding values
    between passes.
- The measurements above give its targets:
  - keep register lifetimes short;
  - keep front 0's control work off the critical path;
  - keep per-register-bit work next to its lanes.
- Not attempted yet.

## 25. Independent audit and response (2026-10-01)

An independent agent audited R1–G13/G14 against the code, the receipts and
Gray's reader's guide. Its report is [audits/AUDIT.md](audits/AUDIT.md),
with its scripts and logs in [audits/](audits/).
- **Construction.** It confirmed the construction claims: one fixed
  radius-5 rule, no depth input, the same width at every level, the
  physical fetch, and the comb geometry.
- **Closure.** It reran closure itself: R1, G2, G4, G13 and G14 are exact
  over successive periods, and G13/G14 rebuild bit-identically.
- **Findings.** It found six problems. Each is resolved below; the receipts
  are in `figs/` (ignored).

### Finding 1: the "level-1 errors" were bursts, not Gray's level-1 class

**The audit was right.**
- Gray §5.1 defines a level-1 error as a cluster of linked candidate
  level-0 errors in which no two such linked pairs are (104,104)-separated.
- A dense box of side at most 104 satisfies this. A dense 200×200 box
  contains two linked pairs 150 sites apart, so it is a union of several
  level-1 errors.
- **Relabelled.** §19's results are now labelled 200×200 bursts.

**New tools.**
- `gray_errors.py` classifies finite error sets by Gray's definitions. Its
  tests cover:
  - a dense 100×100 box: one level-1 error;
  - a dense 200×200 box: not one, with an explicit witness pair;
  - isolation condition (iv);
  - generated clusters.
- `level1_campaign.py` now:
  - generates genuine level-1 errors (`--side 100`, or `--shape sparse`:
    clusters of linked pairs, each kept only if the classifier certifies
    it);
  - records the classification of every scenario;
  - gives error sites adversarial values (`--mode`, implemented in
    `gpu.noise`, with a unit test):
    - `random`: seeded random bits;
    - `zero` / `one`: stuck-at;
    - `invert`: the correct new state, inverted;
    - `freeze`: the old state kept;
    - `copy`: the state of the same Address one colony further, as it was
      at the previous tick, which is plausible but wrong (its Age is one
      tick behind a healthy updated state; second audit).

### Finding 2: the six G8 "reruns" drew new faults

**The audit was right.** The noise seed was derived from the scenario's
position in the filtered list. The driver now derives it from the
scenario's identity (phase, place, or random index):
- unfiltered runs keep their old seeds;
- filtered runs reproduce the unfiltered run's faults.

Reruns with the original faults (5 upper steps) reproduce every original
step exactly and are bit-identical from upper step 4.

| batch | original faults, physical sites differing at steps 1–3 | rerun, steps 1–5 | decoded |
|---|---|---|---|
| G8 b1 (mid / left / right) | 695,139,84 · 693,5,60 · 689,67,84 | same, then 0, 0 | contained, repaired |
| G8 b2 | 695,367,84 · 693,5,60 · 689,67,84 | same, then 0, 0 | contained, repaired |
| G8 b3 | 695,139,84 · 693,5,60 · 689,67,84 | same, then 0 (stopped after step 4 by a machine restart) | contained, repaired |

The last difference is at tick 3,163,136, shortly after the third period
boundary. These bursts straddle the first boundary, so G8 exceeds
Proposition 4's two-period box by that much (Finding 3).

### Finding 3: "repaired" was decoded-only; Proposition 4 is about all fields

**The audit was right.**
- Proposition 4: for each level-1 error there is a box
  [jQ, (j+2)Q) × [kU, (k+2)U) outside which every simulation-structure field
  equals the error-free run.
- The campaign now samples the full physical state of every ring every Q
  ticks and records two verdicts:
  - **time:** no difference in any field of any colony after (k+2)U;
  - **SimBits:** Info differences only within two adjacent colonies of the
    box.
- **Strict variant.** The all-field spatial variant ("strict") is recorded
  too. We argue it cannot hold for a design in which neighbouring colonies
  read the damaged colony's state while that state is wrong. The second
  audit points out that this is an argument from Gray's informal prose, not
  a proof that his full construction fails it (§27).
  - Gray describes exactly this (p. 35): undamaged colonies receive
    "possibly incorrect information about the states of the damaged
    colonies", and "the only lasting effects of the level-1 error are in the
    SimBit fields".
  - We therefore measure two properties weaker than the literal
    proposition: the stored SimBit fields (every Info copy) are confined to
    the box, and every field is restored after it. "Meets Proposition 4"
    below means these two properties, not the literal statement.
  - Per-field diagnostic on G15: one dense 100×100 level-1 error late in
    period 0, compared with the error-free ring during period 1.
    - The damaged colony's Info differs, as allowed.
    - The history lanes of the colonies within 5 of it hold its wrong
      state.
    - The mail tracks carry those bits around the ring, up to 22 colonies
      away.
    - For an error early in a period, the neighbours' front registers and
      scratch also differ while they compute with the damaged data.
    - Everything is identical at 2U.

**Proposition 4 field by field** (`prop4_fields.py`). Gray (p. 15) names
six fields:
- Address and Age are the local structure;
- SimBit, Workspace and Mailbox are the "simulation structure", the fields
  Proposition 4 constrains;
- Flags lies between them, and Workspace.Flag1/2 belong to Workspace.

The run uses G15 with 48 genuine level-1 errors: dense 100×100 boxes at
every phase × 3 places, random values, full state sampled every Q ticks.

| Gray's field | ours | differs outside the two-colony box during the two-period window | differs after the window |
|---|---|---|---|
| SimBit | info | 0 / 48 | 0 / 48 |
| Workspace | hold; pending write (pend, pkind, pval); Workspace.Flag1/2 (wf1, wf2) | 0 / 48 | 0 / 48 |
| Workspace | gathered histories h1, h2 | 38 / 48, 42 / 48 (up to 6 colonies away) | 0 / 48 |
| Workspace | scratch; the front's registers | 10 / 48; 16 / 48 (up to 5 colonies away) | 0 / 48 |
| Mailbox | mr, ml | 47 / 48, 48 / 48 (up to 32 colonies away, the whole ring) | 0 / 48 |
| Flags; local structure | f1, f2; addr, age | 0 / 48 | 0 / 48 |

**What the table shows.**
- **SimBits.** Confined to the box in space and time at every sample; the
  per-tick checks of §27 confirm it at every tick.
- **Mailbox and part of Workspace.** Only the time bound holds. Within the
  window they differ in colonies outside the box, and everything is
  restored when it ends.
- **Workspace part (inherent).** Undamaged neighbours within interaction
  range hold, and compute with, information about the damaged colony; Gray
  says so on p. 35. We read that as saying the literal statement does not
  hold for his construction either, his argument establishing only the
  SimBit part and the restoration. The second audit disputes that this
  follows (§27); we claim only the two measured properties.
- **Mailbox part (G15's design).** It spreads around the whole ring because
  G15 wipes the mail at the period boundary, not at each stage start as
  Gray does. Data loaded at a gather keeps circulating until the commit.

**Gray's gather vote (p. 35)** is implemented as three gathers at Ages 0,
12Q and 24Q, the third arrival voted against the two stored histories.
`gather_vote_check.py` shows it does exactly what Gray claims, and no more.
For every differing history bit it records the colony holding it and the
colony whose data it carries. The errors are dense 100×100 boxes on G15,
with damaged colony 32.

| error | voted lanes (h1) after the three gathers | raw gather-2 copy (h2) |
|---|---|---|
| in transit only: colony 32's margin during gather 2 | **no difference** | data about colonies 31 and 32, held by colonies 27–36, until the period-end wipe |
| at the source: colony 32's working cells late in the period; during the next period | data about colony 32, held by colonies 27–31 and 33–37 | the same |
| both: colony 32's working cells during gather 2 | data about colony 32 held by colonies 27–31; data about colony 31 held only by colony 32 | data about 31 and 32 |

- **When the vote suffices.** It repairs everything that one disrupted
  gather corrupts in transit. Undamaged colonies always hold correct
  information about other undamaged colonies.
- **When it cannot.** It cannot repair information whose source is wrong:
  all three gathers deliver the damaged colony's same wrong values. Gray's
  next sentence says these remain and are "treated at level-1 in the same
  way that a level-0 error is handled". The upper level's fivefold majority
  outvotes them: no undamaged upper cell was ever wrong in the campaigns.
- **Avoidable differences.** The raw gather copy and the circulating mail
  keep in-transit garbage until the period-end wipe. Gray wipes Mailbox and
  Workspace at every stage start, so wiping h2 after the vote and the mail
  after the last capture would remove them.
- **Unavoidable differences.** The neighbours' voted information about the
  damaged colony is what the literal all-field reading of Proposition 4
  cannot allow.
  - It is unavoidable only *during* the period after the error, and only in
    the sense of where it sits: outside the two-colony box.
  - It lives in Workspace: history lanes, and transiently scratch and the
    front's registers, which exist only around the front. G15 wipes all of
    it at the period boundary, so it never outlasts two work periods: every
    field of every colony is identical from the second boundary on, in
    668 of 668 error sets.
  - So the literal reading fails in space within the time box, never in
    time.

**Measured on G14** (no wipes):
- History lanes and Hold keep a burst's garbage for one period too long:
  - neighbours' histories hold copies until the next gather;
  - garbage written into unused Hold after a boundary is committed into Info
    one period later.
- So the time part fails for most bursts at the end of a period (e.g.
  dense 100×100 boxes: 11/64 pass).

**G15 = G14 + a wipe schedule adapted from Gray's stage wipes.**
- Histories and mail are cleared at the commit (Age U−1), Hold at the start
  of the evaluation window (Age E0−1), and scratch at the commit
  (`clear_ws`), via `stage_wipe`.
- This is an adaptation, not Gray's rule: Gray wipes Mailbox and Workspace
  at *each* stage start. G15 wipes at two fixed times, chosen so that no
  stage still needs what is wiped. The early program's Hold stores come
  after E0−1, the special courier arrives at Age 23,904, and the last
  evaluation pass ends before the commit at 112,607 (second audit,
  finding 6; checked by successive closure and by the physical hand-off
  continuations of §27, not proven for every damaged state).
- Cost: 134 gates; U = 112,608, sized by a 20-seed search.
- G15 passes GPU parity, one-period closure, and the margin and compact-front
  tests.

**Results** (64-cell slices of a healthy upper colony, 4 upper steps, full
state sampled every Q ticks; b69 is the whole upper colony, 262,144 sites,
3 upper steps). Every receipt has an exact reference ring.
- *Errors* are placed at 16 phases of the work period × 3 places (target
  colony middle, left and right boundary), plus random placements.
- *Gray class* is the classifier's verdict on each error set.
- *Values* are the error-site values (`gpu.noise` modes).

| candidate | batch | errors | Gray class | values | decoded contained / repaired | Prop. 4 time | Prop. 4 SimBits | strict (all fields) | identical at end |
|---|---|---|---|---|---:|---:|---:|---:|---:|
| G14 | b72 | 64 dense 100×100 | level-1 (64) | random | 64 / 64 | 11 | 62 | 0 | 64 |
| G14 | b73 | 64 sparse clusters | level-1 (64) | random | 64 / 64 | 64 | 64 | 61 | 64 |
| G14 | b71 | 64 dense 200×200 | union of level-1 | random | 64 / 64 | 11 | 62 | 1 | 64 |
| **G15** | b62 | 64 dense 100×100 | level-1 (64) | random | 64 / 64 | **64** | **64** | 0 | 64 |
| **G15** | b63 | 64 sparse clusters | level-1 (64) | random | 64 / 64 | **64** | **64** | 61 | 64 |
| **G15** | b64 | 64 dense 100×100, upper front hit in phase A | level-1 (64) | random | 64 / 64 | **64** | **64** | 0 | 64 |
| **G15** | b65 | 64 dense 100×100, upper front hit in its final program | level-1 (64) | random | 64 / 64 | **64** | **64** | 0 | 64 |
| **G15** | b66 | 4 × 56 dense 100×100 | level-1 (224) | zero / invert / freeze / copy | 224 / 224 | **224** | **224** | 3 | 224 |
| **G15** | b67 | 56 dense 100×100, upper front hit in its final program | level-1 (56) | copy | 56 / 56 | **56** | **56** | 1 | 56 |
| **G15** | b61 | 64 dense 200×200 | union of level-1 | random | 64 / 64 | **64** | **64** | 0 | 64 |
| **G15** | b68 | 56 dense 200×200 | union of level-1 | invert | 56 / 56 | **56** | **56** | 1 | 56 |
| **G15** | b69 | 12 dense 100×100, whole upper colony (no slice), front hit | level-1 (12) | random | 12 / 12 | **12** | **12** | 0 | 12 |

- **G15.** Every error set tested (all certified level-1 sets, plus 120
  bursts that are unions of level-1 errors) has both measured properties
  at the sampled times: every field restored after the two-period box, and
  every stored Info copy confined to its two colonies. §27 repeats the
  main batches with exact per-tick checks. The literal all-field
  proposition does not hold (strict: 0/64 for b62).
  - Damage to the upper state stays at one cell or none.
  - The upper level repairs it within one upper step.
  - Every field of every colony is exact again by the second period
    boundary.
  - This holds for every value mode, including adversarial copies of a
    neighbouring colony's state.
- **G14.** Most bursts in the second half of a period leave history-lane
  residue in neighbouring colonies, and commit-straddling ones leave Info
  residue, until one period later.
- **Partial-density boxes.** 200×200 partial-density boxes (G8 b4, G11 b15)
  also contain separated pairs, so they too are unions of level-1 errors;
  the driver now classifies their realized error sets.
- **Level-0 ring.** The campaign's dense level-0 ring is checked tick by
  tick in the same runs: every sampled difference must have been injected
  one tick earlier.
  - In the healthy middle colonies there are 0 violations, in every batch
    with that ring (b61, b62, b68, G14's b71).
  - The whole-colony run b69 has 0 violations anywhere.
  - A few violations occur only in colonies near the slice's Address jump,
    where the upper level raises Flag1 (Finding 6).

### Finding 4: cached candidates were not checked against the recipe

**The audit was right**: a cache with one flipped ROM bit loaded under the
same name.
- `manifest.json` (tracked) holds the ROM, layout and netlist digests of
  fresh builds of all 17 recipes.
- `candidates.load()` rejects any cache that differs, and a test reproduces
  the audit's one-bit tampering.
- `build_candidates.py` builds candidates in parallel; all 17 rebuild
  bit-identically (`receipts/candidates.json`).

### Finding 5: wrong numbers

All corrected:
- G13/G14 are 260 bits per cell, not 262.
- QU reductions are now stated per candidate.
- The test count is now 44, one of them opt-in.
- `candidates.summary()` masks the front index out of the pass count
  (G13: 365 passes, G14: 307, G15: 329).
- The audit also noted that Gray's Q ≥ 2K fails for G9–G15; this is now
  listed in §16 beside the margin.

### Finding 6: level-0 errors and one tick

**Corrected.** The old statement "every level-0 error is repaired in one
tick, physical state equal at every boundary" went beyond the experiment.

`level0_one_tick.py` now measures it directly. It injects single level-0
errors (one site or two adjacent sites, the whole state replaced) at 300
times across the work period, runs one tick, and compares every field of
every site with the error-free run.

**In a healthy colony** (a slice of a healthy upper colony, errors in its
middle colonies), every error is gone one tick later:

| candidate | values | errors | still visible one tick later |
|---|---|---:|---:|
| G8 | random | 6,000 | 0 |
| G12 | random | 6,000 | 0 |
| G14 | random / invert / zero / one | 4 × 6,000 | 0 |
| G15 | random / invert | 2 × 6,000 | 0 |

**When the upper cell raises Flag1** (an unhealthy upper state, such as
the two random upper cells of the earlier tests, or the colonies next to a
slice's Address jump):
- The trickle-down window raises the computed Flag1 of the physical cells.
- Gray's second special rule (p. 33) then zeroes all simulation-structure
  bits of a cell whose stored Address differs from its computed one.
- So a level-0 error that hits the stored Address leaves a two-tick
  footprint at that one site. Its five-fold copies restore it one tick
  later, and there is no spread.
- Measured rate: about 0.4% of errors.
- The GPU campaign's dense level-0 ring shows the same: 0 one-tick
  violations in the healthy middle colonies, and a few in the colonies
  within reach of the slice's Address jump.
- This follows Gray's rules as written, so the literal level-0 part of
  Proposition 4 does not hold in Flag1 regions, for Gray's construction as
  for ours.

### Remaining limits

The audit's other caveats stand:
- All of this is finite seeded evidence: no threshold, no all-pattern
  guarantee. (At the time of the audit there was no G-family level-2
  macrostep; §26 adds level-2 steps on the level-1 automaton and a physical
  crossing of a level-2 commit.)
- `multifront.replay` checks the compiler's listing, not the physical
  machine; physical closure is the independent check.
- Gray's proof assumptions (Q ≥ 2^13, U = 128Q, Q ≥ 2K) do not hold for
  these candidates.

## 26. Bigger errors, noise at two levels, and three levels (2026-10-01)

The user asked for more robustness tests before moving on:
- level-0 noise together with level-1 errors;
- errors bigger than a colony;
- level-2 steps, and errors that only level 2 can clear;
- what simulating level 2 costs on the GPU.

Everything below is G15.

**New tools.**
- `three_level_g.py` runs the three-level experiments:
  - `phases`: physical ring against levels 1 and 2;
  - `closure2`: level-2 macrosteps;
  - `repair2`: physical errors followed one level up;
  - `copy2`: errors injected one level up.
- `gpu_level2_bench.py` measures GPU throughput at level-2 scale.
- `level1_campaign.py` gains `--wipe k` (every site of k adjacent colonies randomized for 200 ticks), `--e0-all` (Gray's E0 grid in every error ring) and a represented-SimBit check (§26.4).

Receipts are in `figs/{gpu,three_level,level1_campaign}/` (ignored).

### 26.1 What a level-2 step costs

A level-2 cell is a colony of colonies: Q² = 262,144 physical sites. A level-1 step is U = 112,608 ticks, and a level-2 step is U² ≈ 1.27·10^10 ticks.

Measured on the A100 in grid mode, with the GPU otherwise idle (`gpu/G15_level2_bench.json`; the same numbers as an earlier run on the shared GPU):

| physical ring | sites | µs per tick | site updates per second | one level-1 step | one level-2 step |
|---|---:|---:|---:|---:|---:|
| 1 level-2 cell (its own neighbour) | 262,144 | 104 | 2.5·10^9 | 11.7 s | 15.3 days |
| 2 level-2 cells | 524,288 | 150 | 3.5·10^9 | 16.8 s | 21.9 days |
| 4 level-2 cells | 1,048,576 | 304 | 3.4·10^9 | 34 s | 44.6 days |
| 8 level-2 cells | 2,097,152 | 522 | 4.0·10^9 | 59 s | 76.6 days |
| 16 independent rings of 1 level-2 cell | 16 × 262,144 | 926 | 4.5·10^9 | 104 s (all 16) | 136 days (all 16) |

- One ring of one level-2 cell uses only part of the GPU.
  - Its kernel is bound by the per-tick grid synchronization, not by gate throughput.
  - So larger or batched rings get up to 1.8× more site updates per second.
- G15's 17,100 gates run at about 2.5–4.5·10^9 site updates per second, i.e. about 4–8·10^13 single-site gate evaluations per second.

- **Why the tests below are hybrids.** A level-2 step of even the smallest ring that can take one on its own needs weeks of GPU time.
  - So these tests run the physical level only as long as needed, up to six level-1 steps.
  - They then continue on the **level-1 automaton**: the same rule, run on the decoded level-1 ring.
- **Why the hand-off is exact.** It is exact wherever physical → level-1 closure holds.
  - Closure has held for arbitrary level-1 states in every test so far.
  - It is checked again at every physical level-1 step below.
- **Cost on the level-1 automaton.** A ring of 32 level-2 cells (16,384 level-1 cells) runs at 60 µs per tick, with one ring or three. A level-2 step there takes 6.8 s instead of weeks.

### 26.2 Level-2 steps

**Physical three-level ring** (`phases`, two random level-2 cells).
- The cells are encoded twice: 1,024 level-1 cells over 524,288 sites.
- The level-1 automaton is advanced to five stages of the level-2 work period.
- From each stage, the physical ring runs six level-1 steps (675,648 ticks).
- After every level-1 step:
  - the decoded level-1 ring must equal the level-1 automaton;
  - the twice-decoded ring must equal the level-2 state, or F(level 2) once the level-2 commit has passed.

| stage of the level-2 period | level-1 ages | level 1 exact | level 2 exact |
|---|---|---:|---:|
| gathers | 1,062–1,067 | 6/6 | 6/6 |
| early program | 17,292–17,297 | 6/6 | 6/6 |
| match pass | 45,025–45,030 | 6/6 | 6/6 |
| final program | 56,454–56,459 | 6/6 | 6/6 |
| commit | 112,606–112,611 | 6/6 | 6/6; F(level 2) from 112,608 |

**Level-2 macrosteps on the level-1 automaton** (`closure2`). After each U ticks, decode(level-1 ring) must equal F(level-2 ring). This is the one-level closure test run one level up, on level-1 cells: it shows level-2 macrosteps of the same rule, not new physical evidence. The reference F is `cand.step_numpy`, a separate evaluator of the same netlist (not an independent specification).
- 4 random level-2 cells: 3 of 3 exact;
- 8 random level-2 cells: 6 of 6 exact;
- 8 consecutive cells of a healthy level-2 colony: 6 of 6 exact.

### 26.3 Level-0 noise together with level-1 errors

The ring is the whole upper colony: 512 colonies, 262,144 sites, three upper steps.
- **Error rings (22).** Each has a dense 100×100 burst at 9 phases × 2 places, plus 4 random placements. Alone, each burst is a Gray level-1 error.
  - The noise changes that classification (second audit, §27). Classified against the full realized error set, the burst alone fails Gray's isolation condition (iv) in 22 of 22 cases, because noise hits within 23 sites of it are not level-0 errors.
  - Together with the hits linked to it, it is one level-1 error in 4 of 22 cases. In the other 18, a two-site noise hit just outside the burst forms a small cluster at least 104 from the burst's far side, so by Gray's definition the set is a union of linked level-1 errors, i.e. a higher-level error.
- **Noise.** Each error ring also has Gray's E0 grid (G = 50) for the whole run: about 3.5·10^7 level-0 errors per ring, including inside and around the level-1 error.
- **Control.** One more ring has the E0 grid alone.

| batch | values at the burst | contained / repaired | Prop. 4 time / SimBits | bit-identical at the end |
|---|---|---:|---:|---:|
| b81 | random | 22 / 22 | 22 / 22 | 22 |
| b82 | copy of the colony one further | 22 / 22 | 22 / 22 | 22 |

- **Reference and decoded state.** The reference ring was exact at every upper step.
  - Wrong upper cells occurred only in the damaged colony: one cell at one upper time, as without noise (b81: 9 of 22; b82: 3 of 22).
  - None of them survived the next upper step.
- **Strictness.** The SimBit check here is the per-copy one: every stored Info copy, with fresh noise hits excluded.
- **Noise-only ring (b81).** At 660 samples, every site that differed had been hit in the previous tick: 0 one-tick violations.

### 26.4 Errors bigger than a colony

At level 1, a wipe of k colonies makes k adjacent level-1 cells wrong at one level-1 time, or k+1 if it straddles a colony boundary.
- **k ≤ 2.** This is a level-0 error of the level-1 automaton. The level-1 rule removes it in one level-1 step, as the physical rule removes a level-0 error in one tick.
  - `repair2` confirms this: after 2-colony wipes in the level-2 gathers and the final program, no level-1 cell differs one level-1 step later.
- **k ≥ 3.** This is a level-1 error of the level-1 automaton, and only level 2 removes it (§26.5).

The table covers the whole upper colony, five phases × two places, four upper steps.

| batch | error | contained / repaired | time / Info copies / represented bits | bit-identical at the end |
|---|---|---:|---:|---:|
| b91 | 1 colony wiped | 10 / 10 | 10 / 9 / 10 | 10 |
| b92 | 2 colonies wiped, aligned with the colonies ("mid") | 5 / 5 | 5 / 3 / 5 | 5 |
| b92 | 2 colonies' width, straddling: touches 3 colonies ("left") | level-2 error (§26.5) | — | — |
| b96 | as b92, with the E0 grid throughout: aligned | 5 / 5 | 5 / 3 / 5 | 5 |
| b96 | as b92, with the E0 grid throughout: straddling | level-2 error (§26.5) | — | — |
| b95 | dense 1000×1000 box: over 2 colonies ("left" placements) | 5 / 5 | 5 / 5 / 5 | 5 |
| b95 | dense 1000×1000 box: over 3 colonies ("mid" placements) | level-2 error (§26.5) | — | — |
| b93 | 3 colonies wiped | level-2 error (§26.5) | — | — |

- **1–2 colonies.** At most two adjacent upper cells are wrong, at one upper time, and none at the next. The physical state is bit-identical to the error-free ring by the second boundary, including under dense E0 noise (b96).
- **3 colonies** (b93; the "mid" placements of b95; the straddling placements of b92 and b96).
  - Level 1 alone does not repair these, as expected.
  - The wrong level-1 cells grow from 3–4 (9–10 for wipes in the gather phases) to 16–22 by the fourth upper step.
  - §27 follows these particular errors to the next level-2 boundaries (finding 4 there); §26.5 tests similar wipes in a different, healthy level-2 setting.

**SimBit checks** (sampled every Q ticks; these wipes are not level-1 errors, so Proposition 4 does not formally apply to them).
- "Info copies" is the check of Gray's stored SimBit fields: every Info copy, attributed to the site that holds it, must differ only inside the two-colony box. It is the primary SimBit verdict (second audit, finding 3).
- "Represented bits" votes the five copies of each logical cell that holds an upper-state bit. It is a decoder-level check and is reported only as an extra.
- They disagree near a wiped colony. The neighbours hold copies of the wiped colony's two edge cells, which are margin cells holding no upper-state bit, and those copies differ for up to a period. So the stored fields leave the box in 1 of 10 one-colony wipes and in 2 of 5 aligned two-colony wipes, although no represented bit does.

### 26.5 Errors that only level 2 can clear

**Method** (`repair2`).
- **Starting state.** A healthy level-2 colony (an encoded random level-3 cell). In the data-rich runs it is first run for 60,000 level-2 ticks. Its cells then hold gathered histories, scratch and Hold: about 65 nonzero bits per cell, against about 6 for a fresh encoding.
- **Level-1 ring.** 32 consecutive level-2 cells are encoded into 16,384 level-1 cells. The level-1 automaton advances them to the chosen stage of the level-2 work period.
- **Physical slice.** 64–192 level-1 cells around the target are encoded physically (32,768–98,304 sites).
  - The slice runs four level-1 steps with and without the wipe.
  - Physical health and level-1 closure are checked at every step.
- **Continuation.** The decoded difference is applied to the full level-1 ring. Both rings then continue on the level-1 automaton across two or more level-2 boundaries.
- **Comparison.** At each level-2 boundary, the level-2 states and every field of every level-1 cell are compared with the error-free ring.
- **Hand-off check.** At the hand-off, the wiped slice differs from the error-free one only in Info.
  - Apart from the encoding of the level-1 difference, at most 410 Info bits differ. In the 12 wiped rings that record it, none of them is in a slot that holds a represented SimBit.
  - That alone does not prove the continuation exact: G15 reads the Info of its reserved cells (3, Q−3, lo, hi−1), which hold no upper-state bit (second audit). §27 therefore checks the hand-off physically: each faulty slice and the plain encoding of its decoded state run on side by side.

**Which level-2 bits a wipe destroys.**
- Each level-2 bit lives in one level-1 cell, with copies in the four cells next to it.
- A wipe of k colonies destroys outright only the bits whose five copies all lie inside it: none for k = 3, 3 for k = 7, 23 for k = 27, 60 for k = 64.
- Each run records these bits and their values. In the data-rich colony, the 64-colony wipe destroys 10 bits that are 1.

**What a wiped colony becomes.** Gray's second special rule zeroes a cell whose stored Address differs from the computed one. So a wiped colony comes back as a blank level-1 cell: Address 0, Age 1, everything else 0.

**Plausible wrong values one level up** (`copy2`).
- k level-1 cells of the middle level-2 colony are replaced by the cells at the same positions in the next level-2 colony.
- They keep the same level-1 Address and Age, so no special rule fires. They now carry another level-2 cell's SimBits, histories, scratch and front registers.
- Physically, this is an error that overwrites k colonies with copies of colonies 262,144 sites away.

**Results.** 61 level-2 errors in all: 44 physical wipes of 3–64 colonies and 17 copies of 5–128 level-1 cells. They cover every stage tested, the comb's fronts, fresh and data-rich colonies, and noise at both lower levels.

| stage | level-2 colony | where | k | level-2 bits destroyed (of them 1) | first level-2 boundary | all fields exact from |
|---|---|---|---:|---|---|---|
| level-2 gathers | fresh | middle | 3, 5 | — | clean | boundary 1 |
| level-2 gathers | rich | middle | 3, 5 | ≤ 1 (0) | clean | boundary 1 |
| level-2 gathers | rich | middle | 64 | 60 (10) | clean | boundary 1 |
| start, during both levels' gathers | rich | middle | 3, 4, 3 | 0 | clean | boundary 1 |
| final program, pass start | fresh | middle; comb | 3, 5; 3, 5, 7 | — | clean | boundary 1 |
| final program, mid-pass | fresh | comb fronts 0, 1, 2, 4 | 5, 7 | — | clean | boundary 1 |
| final program, mid-pass | fresh | comb front 3 (live registers) | 5, 7 | — | **cell 0 wrong** (mail copy slots) | boundary 2 |
| same, with E0 (G = 50) physically and on the level-1 automaton | fresh | comb front 3 | 7 | — | **cell 0 wrong** (mail copy slots) | boundary 2 |
| final program, mid-pass | rich | middle | 3, 7 | ≤ 3 (0) | clean | boundary 1 |
| final program, mid-pass | rich | comb fronts 3, 4 | 5, 7 | ≤ 3 (front 3: 2) | clean | boundary 1 |
| same, with E0 at both levels | rich | comb front 3 | 7 | 3 (2) | clean | boundary 1 |
| final program, mid-pass | rich | whole comb | 27 | 23 (2) | clean | boundary 1 |
| final program, mid-pass | rich | level-2 Age, h1, Info bits | 7, 27 | ≤ 23 (≤ 6) | clean | boundary 1 |
| final program, mid-pass | rich | middle | 64 | 60 (10) | **cell 0 wrong** (Age) | boundary 2 |
| match pass | rich | whole comb | 27 | 23 (2) | **cell 0 wrong** (Address, Flag1, Info, h1, h2, scratch) | boundary 2 |
| straddling the commit | fresh; rich | middle | 3, 5, 7; 3, 7 | ≤ 3 (0) | clean (also just after the commit) | first boundary |
| *copy* mid-pass | rich | comb | 5, 7, 27 | ≤ 23 (5 changed) | clean | boundary 1 |
| *copy* mid-pass | rich | middle | 7, 27, 64 | ≤ 60 (20 changed) | clean | boundary 1 |
| *copy* mid-pass | rich | middle | 128 | 124 (29 changed) | **cell 0 wrong** (Info, h1, h2) | boundary 2 |
| *copy* gathers | rich | middle | 7, 27, 64, 128 | ≤ 124 (29 changed) | clean | boundary 1 |
| *copy* match pass | rich | comb | 7, 27 | ≤ 23 (4 changed) | clean | boundary 1 |
| *copy* 8 level-1 steps before the commit | rich | middle | 7 | 3 (0 changed) | clean | boundary 1 |
| *copy* 8 level-1 steps before the commit | rich | middle | 27, 64, 128 | ≤ 124 (≤ 29 changed) | **cell 0 wrong** (Info, h1, h2, scratch) | boundary 2 |

"clean" means every field of every level-1 cell equals the error-free run; in the rows with noise on the level-1 automaton, the cells that noise hit in the last two level-1 ticks are excluded. "cell 0" is the damaged level-2 cell. The level-2 part is a hybrid: four physical level-1 steps, then the level-1 automaton (`copy2` starts there directly). §27 checks the hand-off physically.

**Findings.**

1. **Level 1 alone does not remove an error of three or more colonies.**
   - The level-1 cells that differ from the error-free run spread by about three cells per level-1 step on each side.
   - They differ in Flag1, Age, histories, scratch and registers, and also in mail during the level-2 gathers.
   - A burst at level 0 behaves the same way.
2. **Level 2 always removes it.**
   - 52 of the 61 errors were gone at the first level-2 boundary: every field of every level-1 cell was exact.
   - In the other 9, the damaged level-2 cell, and only it, was wrong at the first boundary, and everything was exact from the second.
   - That is a level-0 error at level 2: one cell at one level-2 time. The level-2 rule removes it in one step through its own fivefold storage, as the physical rule removes a level-0 error in one tick.
   - This is Gray's amplification one level further up. It is observed through the hybrid: physically up to the hand-off, then on the level-1 automaton, with the hand-off itself checked physically in the cases of §27.
3. **When the damaged cell is wrong for one step.** It happens when the error disrupts the level-2 computation itself, so that the colony commits a wrong new state:
   - the comb's live registers destroyed mid-pass;
   - the whole comb destroyed during the match pass;
   - an eighth of the colony wiped mid-pass;
   - a quarter of the colony overwritten mid-pass;
   - 27 or more cells overwritten just before the commit.
4. **Destroyed level-2 bits are not enough.** Wipes that destroyed all five copies of up to 60 level-2 bits (10 of them ones) during the gathers, and up to 23 bits mid-pass, were gone at the first boundary. The damaged cell's new state is computed from majority-corrected inputs: each level-2 field's copies in the neighbouring level-2 cells outvote the lost ones.
5. **Noise at both lower levels changes nothing.**
   - The setup combines a front-3 wipe with Gray's E0 grid (G = 50) in the physical rings and applied to the level-1 automaton. The latter means level-1 errors everywhere, at the densest level-0 pattern one level up: about 6.5 per level-1 tick in the 16,384-cell ring.
   - The outcome is the same as without the noise.
   - After the first boundary, the only level-1 differences are cells hit in the last two level-1 ticks.
   - A ring with the noise alone never had a wrong level-2 cell.

### 26.6 What this establishes, and what it does not

**Established for G15, on the cases tested.**
- Every error class tested is removed by the level whose job it is, and leaves at most one wrong cell, or two adjacent ones, for one step at the next level up.
- The classes tested:
  - level-0 errors, alone and as dense noise;
  - certified level-1 errors, alone and under dense noise;
  - wipes of one or two colonies;
  - wipes of 3–64 colonies and overwrites of up to 128 level-1 cells, at every stage tested.
- Level-2 steps are exact, physically across a level-2 commit and on the level-1 automaton over several level-2 steps.

**Not established.**
- A noise threshold.
- A level-3 error: damage to three or more adjacent level-2 colonies.
- Several level-2 errors close together.
- The hand-off to the level-1 automaton rests on physical → level-1 closure. Closure is checked at every physical step and has held in every closure test, and in every case of §27 the faulty physical state became identical to the plain encoding of its decoded state one level-1 step after the hand-off. It is not proven for every residual state.
- A full physical level-2 step was not run: it would take weeks of GPU time.

## 27. Second independent audit and response (2026-10-01)

A second independent agent audited everything from `7caedb2` to `b3cdabe`, which covers §§24–26. Its report is [audits/AUDIT2.md](audits/AUDIT2.md), with its scripts and logs in [audits/](audits/).

**What it confirmed.**
- G15 is still one fixed radius-5, 260-bit rule with its own compiled instruction table. A fresh build matches the cache and the manifest.
- Its own nonzero rings closed at three successive physical periods.
- The `phases` run really crosses a level-2 commit.
- The headline counts of §26 match the receipts.
- It continued two faulty physical rings past a `repair2` hand-off; both stayed on the level-1 automaton.

**Its verdict on the errors.** "Qualified empirical support for Gray-like amplification", with the formal error labels and the literal Proposition 4 claim overstated.

**First-audit findings, as it graded them.**
- Resolved: the G8 reruns with their original faults, and the corrected numbers.
- Resolved for the finite trials run: one-tick level-0 recovery.
- Partially resolved: the Gray error classes (finding 2 below), "repaired" versus Proposition 4 (finding 3) and cache integrity (finding 5). The fixes below complete them.

It made six new findings. All six are right; the responses follow.

### Finding 1 (high): the summary's all-receipt claims were stale

- **The problem.** The summary said that across *all* campaign receipts no undamaged colony was ever wrong, and that every error looked like one level-0 error upstairs (2,324 rings). That was written before §26 added the wipes of three colonies, which are level-2 errors and behave differently at level 1 by design.
- **The fix.** `campaign_census.py` recounts over an explicit rule. Every receipt is included except smoke tests, non-batch analyses, and reruns of the same faults. It writes `Report/campaign_census.json` (tracked), with the rule, the excluded files and why, and the sha256 of every receipt counted.

| errors touching | error rings | upper steps | never wrong | wrong at one upper time, ≤ 2 adjacent cells, inside the touched colonies | other |
|---|---:|---:|---:|---:|---:|
| at most two colonies | 2,387 | 9,255 | 1,789 | 598 | 0 |
| three or more colonies | 25 | 100 | 0 | 0 | 25 |

- The summary now states the claim for errors touching at most two colonies, with these counts. The 25 larger errors are level-2 errors; their fate at level 2 is below (finding 4).

### Finding 2 (high): classifier bugs, and "certified" errors under noise

**Two real bugs in `gray_errors.py`, both fixed.**
- `classify(S)` silently dropped isolated single errors from S and could then certify S. Gray takes level-1 errors inside E minus E0, so such an S is now rejected. The rest of S is classified separately, under `core`.
- The fast path for large sets missed isolated *pairs* of adjacent errors as level-0 errors. `level0_points` is now exact for any finite set: a point is level-0 when the single site, or one of the two adjacent pairs containing it, is (24, 24)-separated from the rest. A bucket grid keeps it fast.

**Condition (iii) on large sets is now decided exactly, where the window argument alone left it undecided.**
- Separated sets have separated subsets, so (iii) fails exactly when two 2-point minimal candidates are (104, 104)-separated.
- A pair with a point inside a 104 × 104 window R is linked to all of R. So in any separated configuration, one pair lies outside R.
- The decision therefore only needs the linked pairs outside R, each checked against the points far from it.

**New tests.** They reproduce the auditor's counterexamples (an isolated site inside S; an isolated pair next to a dense cluster) and the burst-in-noise cases.

**Re-certification of every campaign error** (`reclassify_receipts.py`, output `reclassified.json`).
- Every standalone certificate is unchanged:
  - G15: 548 errors (dense 100×100 boxes and sparse clusters);
  - G14: 128;
  - dense 200×200 boxes stay unions of level-1 errors.
- **b81/b82 (a burst under dense E0 noise).** The auditor is right. Classified against the full realized error set (the kernel's own masks), the burst alone fails isolation (iv) in 22 of 22 placements: noise hits within 23 sites of it are not level-0 errors.
  - With its linked hits, the burst is one level-1 error in 4 of 22 placements.
  - In the other 18, a two-site noise hit lands next to the burst. By Gray's literal definitions that pair is itself a minimal candidate (two linked single sites), at least 104 sites from the burst's far side. So the set is a union of linked level-1 errors, i.e. a higher-level error.
  - All 44 runs (b81 and b82, the same placements) were contained at one upper step and repaired. §26.3 and the summary now use these labels.
- The campaign driver now classifies every noisy burst against its realized error set (`gray_full_set` in the receipt).

### Finding 3 (medium): sampled and majority-based Proposition 4 verdicts

**Wording.** The literal Proposition 4 (every simulation-structure field equal outside the box) does not hold for G15: the all-field check gives 0/64. §25 and the summary now say so. They claim only two measured properties:
- every field is equal again after the two-period box;
- every stored Info copy (Gray's SimBit fields, per copy, attributed to the site holding it) differs only inside the two-colony box.

We still read Gray's p. 35 as saying that the literal form fails for his construction too, but that is an argument, not a proof.

**Exact per-tick checks** (`GpuSim.track`, CUDA).
- **What is recorded.** After every tick, for every ring and colony: the first and last tick at which the ring differs from the reference, in the Info copies and in any field.
- **What is excluded.** Only the sites that the ring's own noise corrupted in that same update. A persistent difference at a site hit again is therefore missed at most for that one tick.
- **Test.** The tracker is checked against states downloaded after every single tick (GPU tests, 7 of 7 pass).
- **Rerun batches.** The main batches were rerun with `--track`, with the same faults as the originals:

| batch (rerun of) | errors | values | rings | contained / repaired | Info copies confined, every tick | every field restored, every tick | all fields confined, every tick | bit-identical at the end |
|---|---|---|---:|---:|---:|---:|---:|---:|
| b62t (b62) | dense 100×100 level-1 errors, 16 phases × 3 places + 16 random | random | 64 | 64 / 64 | **64** | **64** | 0 | 64 |
| b63t (b63) | sparse level-1 clusters | random | 64 | 64 / 64 | **64** | **64** | 61 | 64 |
| b65t (b65) | dense 100×100, upper front hit in its final program | random | 64 | 64 / 64 | **64** | **64** | 0 | 64 |
| b66t (b66) | dense 100×100 | copy | 56 | 56 / 56 | **56** | **56** | 1 | 56 |
| b81t (b81) | dense 100×100 burst under the E0 grid, whole colony | random | 22 | 22 / 22 | **22** | **22** | 0 | 22 |
| b92t (b92) | 2 colonies wiped, aligned, whole colony | random | 5 | 5 / 5 | 0 | **5** | 0 | 5 |
| b96t (b96) | the same under the E0 grid | random | 5 | 5 / 5 | 0 | **5** | 0 | 5 |
| b95t (b95) | dense 1000×1000 over 2 colonies, whole colony | random | 5 | 5 / 5 | **5** | **5** | 0 | 5 |

- **Level-1 errors.** For all 248 certified level-1 errors and the 22 noisy bursts, the stored Info copies never left the two-colony box at any tick. Every field was equal again after the box at every tick. The sampled verdicts of §25 are confirmed exactly.
- **Two-colony wipes** (not level-1 errors, so Proposition 4 does not formally apply).
  - The Info copies outside the box are in the two neighbouring colonies only, and only while the wipe lasts: ticks t₀+2 to t₀+201 for a 200-tick wipe from t₀, and up to about 80 ticks longer under noise, during healing.
  - The neighbours' two edge sites hold copies of the wiped colony's edge cells, which are margin cells holding no upper-state bit. A level-1 burst never reaches a colony's far edge, so this cannot happen for level-1 errors.
- **Noise-only rings, every tick.** No difference survived a tick in the middle colonies of the slice (b62t, 450,432 ticks) or anywhere in the whole colony (b81t, 337,824 ticks). In the slice, survivors occur only at its two ends, where the upper level raises Flag1 at the slice's Address jump (finding 6 of the first audit).
- **What is not done again here.** The 200×200-burst batch (b61) was not rerun per tick. Its sampled verdicts (§25) stand.

### Finding 4 (medium): the level-2 results rest on a hybrid hand-off

**Wording.** §26 now states the boundary plainly.
- Each `repair2` case is physical for four level-1 steps, then continues on the level-1 automaton.
- `copy2` is a direct level-1 injection, a model of an adversarial error and not a physical run.
- The particular b92–b96 errors had not been followed to level 2.

**The hand-off checked physically.** `repair2 --verify-handoff 2`, and the campaign's new `--continue-level2`, run each faulty physical ring next to a canonical twin for one or two more level-1 steps. The twin is the plain encoding of the ring's decoded state.

- **Coverage.** 11 `repair2` configurations, rerun with the same faults:
  - every physical case that left a wrong level-2 cell: front 3 mid-pass, with and without noise; the whole comb in the match pass; the 64-colony wipe mid-pass;
  - both 64-colony wipes, which have the largest residues;
  - wipes straddling the level-2 commit, at the start of the period, and on the level-2 field bits;
  - the whole comb mid-pass.
  - That is 18 wiped rings plus one noise-only ring.
  - Every rerun reproduced its earlier level-2 outcome.
- **Result.** In all 19, the faulty slice was physically identical to its twin one level-1 step after the hand-off, and still identical a step later. In both steps the decoded states followed the level-1 automaton away from the slice ends.
- **What follows.** From one level-1 step after the hand-off, the faulty physical run *is* the canonical one. Continuing on the level-1 automaton is then exact up to closure of canonical encodings, which every closure test checks. The residue before that step (at most 410 Info bits, none in a slot that holds an upper-state bit) is overwritten within one level-1 step.
- **What does not follow.** This is not a proof for every residual state: a residue in the Info of a reserved cell could in principle change the step in which it is overwritten. The auditor's own probe of that case changed five flag sites for a while, and they were gone by the period boundary.

**The b92–b96 errors followed to level 2.** `level1_campaign.py --continue-level2 2` does this for whole-colony runs:
1. after the physical steps, it records the hand-off residue by kind, including the reserved cells whose Info the rule reads (3, Q−3, lo, hi−1);
2. it checks the hand-off physically, as above;
3. it continues every ring on the level-1 automaton across two level-2 boundaries.

- **2-colony wipes, b92t** (5 aligned, 5 straddling three colonies). All 10 are clean at both level-2 boundaries.
  - At the hand-off, the residue of the straddling ones lies only in Info slots of the reserved cells: 55–60 bits, none in a represented slot.
  - Every hand-off check passes: decoded states equal F, and the physical ring is identical to its twin after one level-1 step.
- **3-colony wipes, b93t** (10).
  - Seven are clean at both level-2 boundaries.
  - Three change the level-2 state from the first boundary on: final program "left", commit "mid" and commit "left", i.e. wipes late in the first level-1 step of a level-2 period. They change Age, Flag2, Info, Hold, histories and scratch.
  - They are still wrong at the second boundary. This setting is a ring of *one* level-2 cell, a random state that is its own neighbour, so every level-2 copy of its bits is held by the damaged cell itself and nothing can outvote it. The rule's level-2 redundancy has nothing to work with.
  - Every hand-off check passes here too (residue 55–100 bits, all in reserved Info slots).
- **The same timing with real level-2 neighbours** (`repair2 --level1-age 0`, 32 level-2 cells, wipes of 3 and 4 colonies at physical ticks 112,508 and 78,624, data-rich and fresh colonies). All 6 rings are clean at four successive level-2 boundaries. The level-2 commit is never affected, and every hand-off check passes.
- **b95t and b96t:** all 10 boxes of b95t, including the five over three colonies, and all 10 wipes of b96t under the E0 grid, including the five straddling ones, are clean at both level-2 boundaries; their hand-off checks all pass.
- **Counts.** 65 hand-off checks in all (25 `repair2` rings, 40 campaign rings), every one identical to its twin one level-1 step after the hand-off.

### Finding 5 (low): the manifest pinned the artifact, not the recipe

- **Manifest.** It now also pins a digest of each recipe (parameters, layout and compile settings), written from fresh builds of all 17 recipes. All 17 reproduced their caches bit for bit, so only the recipe digests were added.
- **Loading.** `load()` refuses a cache whose parameters differ from the current recipe. `verify()` refuses one whose recipe digest differs, which catches changed compile settings too.
- **Test.** Changing G15's `stage_wipe`, or its scheduler seed, makes the load fail.

### Finding 6 (low): wording of the wipe schedule; a missing negative control

- **Wipe schedule.** G15's wipes are now described as what they are: a schedule *adapted* from Gray's stage wipes. Histories and mail are cleared at the commit, Hold at E0−1, scratch at the commit. Gray clears at every stage start.
- **Negative control.** §24 claimed one for the `sel_front` test, but the test had none. It now mutates single gates of the new netlist and must catch every mutant of a gate driving a register output (8 of 8) and most random ones (13 and 16 of 20 for the two modes).

### Smaller points from the ledger

- **`copy` mode.** It copies the neighbouring colony's state from the *previous* tick, so its Age is one tick behind; the wording is fixed.
- **Noise case in §26.5.** "Clean" there excludes the cells that the level-1 noise hit in the last two ticks.
- **`closure2`.** It is the one-level closure test run one level up: level-2 macrosteps of the same rule, not new physical evidence. Its reference, `cand.step_numpy`, is a separate evaluator of the same netlist.

**Tests:** 47, one opt-in. The new ones are the per-tick tracker, the classifier counterexamples and the recipe check; the `sel_front` test gained its negative control.

## 28. Where the CUDA kernel's time goes (2026-10-01)

A study of the G15 grid-mode kernel (`experiments/gpu_kernel_study.py`, receipt `figs/gpu/G15_kernel_study.json`). Nsight Compute cannot read the GPU's performance counters in this environment, so the numbers are compiler statistics and timings.

**The kernel as generated.**
- One thread handles a 32-site word.
- Per word per tick it executes about 17,800 SASS instructions:
  - 9,300 LOP3 for the logic;
  - about 5,400 for address arithmetic and the shifts that assemble neighbours;
  - 830 global loads;
  - about 1,040 local-memory spill loads and stores.
- It uses 255 registers and spills 2.2 KB per thread.
- It issues about 0.5 instructions per cycle per SM out of 4: it stalls more than it computes.
- The code is about 285 KB, far beyond the instruction cache.

**Fewer registers make it slower.** `__launch_bounds__` overrides `-maxrregcount`, so the limit was set through the launch bounds:

| registers per thread | spill per thread | µs per ring per tick, 16 rings |
|---:|---:|---:|
| 255 (current) | 2.2 KB | 58 |
| 128 | 5.4 KB | 78 |
| 64 | 9.3 KB | 128 |

**Shared memory would help little.** Memory traffic is not the bottleneck, and the spill set does not fit in shared memory at a useful occupancy.

**Idle logic is the lever.** When no front of the comb can arrive at a word's sites, 59% of the netlist is dead: the register and pending-write outputs are constant. Forcing the five per-slot arrival signals to 0 leaves 7,053 of 17,100 gates.

A prototype kernel built from that reduced netlist:

| kernel | instructions per word | spill | µs per ring per tick, 16 rings | µs per tick, 1 ring |
|---|---:|---:|---:|---:|
| full | 17,834 | 2.2 KB | 57.8 | 115 |
| no front within reach | 10,092 | 0.6 KB | 24.7 | 36.8 |

**How to use it exactly.**
- Compute the arrival cone (2,955 gates) first, then branch on whether any site of the warp's words has an arriving front.
- Both paths come from the same netlist, so the result is bit-exact by construction and checked by the parity tests.
- The branch must be warp-uniform. Storing the words so that one warp holds the same word position of 32 colonies makes about 88–94% of warps take the short path in a healthy ring, because the comb sits at the same place in every colony.

**Expected gain.** About 2× in batched runs, and less for a single small ring, where the warps holding the front set the time per tick.

**Other notes.**
- Fixing the ring size at compile time made the kernel 17–26% slower.
- Even 3× would leave a physical level-2 step at days.

## 29. A job scheduler for the comb: G16 (2026-10-02)

**Result.** G16 is G15's rule with a new compiler. The program takes 37 passes where G15's takes 333, and the work period is 4.3 times shorter.

| | Q | pass (ticks) | NPe / MP / NP | blocks before E0 | U | U/Q | QU | bits per cell | gates | instructions |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| G15 | 512 | 288 | 26 / 99 / 333 | 57 | 112,608 | 220 | 2^25.78 | 260 | 17,100 | 32,835 |
| **G16** | **512** | 288 | 12 / 21 / 37 | 52 | **25,920** | **50.6** | **2^23.66** | 258 | 16,767 | 23,807 |

(NPe: the page by which the two flags are stored; MP: the match pass; NP: all passes.)

- The rule's mechanisms are G15's: fivefold storage, three voted gathers 12Q apart, the early Flag program with the special procedure and trickle-down, the fivefold compact front, the comb of five fronts, the colony margin, the stage wipes. Three things changed: the lane skews, the first block of the evaluation window, and the page constants NPe, MP, NP.
- The cell is two bits narrower because Age needs 16 bits instead of 18.
- QU is 4.3 times smaller than G15's and 81 times smaller than G8's. A level-2 step costs (QU)², 19 times less than for G15.
- U/Q is now below Gray's 128. Gray's proof assumptions (Q ≥ 2^13, Q ≥ 2K) still do not hold.

### What was wrong with the old scheduler

§§23–24 found that the comb's in-order scheduler filled 9% of its slots and that the slot bound was ten times lower. Two measurements on G15's netlist, with generous page budgets, show that the limit was the issue discipline and not the machine:

| change to the in-order comb scheduler | early / A / final passes |
|---|---|
| none (G15's settings) | 28 / 152 / 258 |
| a prefetch may load every wanted lane of the cell in one instruction (a machine G15 does not have) | 28 / 120 / 237 |
| the same, with all lanes of a bit on one cell (skew 0) | 48 / 137 / 344 |

- Giving the front unlimited read bandwidth saved 8%. The fronts were not short of read ports.
- They were waiting. Each front issued its gates in one fixed depth-first order, and the head of that order waited about half a pass every time its next lane lay elsewhere; the other fronts waited for the first one's exports.

### Design (`gacsca/jobsched.py`)

The early Flag program, phase A and the final program are compiled together, as one pool of gates with three deadlines.

- **Claims.** A front with little to do claims work: the largest unclaimed sub-cones, 500 nodes in all, of the first unfinished target. Targets are the two flags, then the fetch key, then the Hold outputs. Sub-cones that depend on nothing another front has in progress are preferred. Any front can claim anything: there is no partition of the gates among the fronts.
- **Queue and wishes.** The claimed nodes form the front's queue, in depth-first order. The loadable inputs of the first 300 runnable nodes are *wished*. The front loads a wished value when it passes the value's cell, and executes a node as soon as its operands are in its registers, in any order. Nothing waits for the head of the queue.
- **Scratch is the only channel.** A value with a consumer outside the claiming front is parked in a scratch bit of the cell the front is at, usually as the destination of the gate that computes it, which costs no extra instruction. Any front loads it from there. A node whose operand another front is still computing waits for that front to park it.
- **Registers go to the head of the queue.** When they are full, an input of the first 100 runnable nodes displaces the value whose next use lies farthest ahead: that value is dropped if it can be loaded again, and parked otherwise.
- **Associative trees are folded in arrival order.** Maximal AND, OR and XOR trees with single-use inner nodes become n-ary nodes (1,454 of them, 3,757 folds). A partial result that its front has no further leaf for is parked, and absorbed by whichever front holds another partial result when it passes. The operand selection of the upper front (two 82-way ORs) is folded this way by all five fronts.
- **The match pass.** When the key is complete, front 0 gives back its unfinished claims, parks what other work still needs, and in the last page before the match pass loads the key from scratch into R[0 : k+PW]. The other fronts work on until late in that page and then do the same. Nobody executes in the match pass, and afterwards every register is treated as empty except front 0's fetched instruction. Front 0 first computes what depends on the instruction alone (its decoders).
- **Work that does not depend on the fetched instruction is done before the match pass**, whichever output it belongs to. G15 computed the upper maintenance three times, once per program; G16 computes it once.

**Lane skews (`compiler.end_aware_layout`).** Lane j is captured j ticks early or late, so that it holds the neighbour's bit of address x − j: a signed skew, which `ParamsG.check` now allows. The eleven lanes of an upper bit then sit on eleven consecutive cells, and one front loads them all in one sweep. G15's skews put three pairs of them on the same cell, and a front loads one value per visit. The layout is the proportional one, except near the colony ends, where a bit is placed only if all its used lanes stay inside the working cells.

**The evaluation window starts at block 52 instead of 57.** The last lane is captured at Age 29Q − 4. G15 started the evaluation at 32Q; nothing happens in between, so G16 sets E0q = 29. The three gathers are where they were.

**Correctness of the schedule.** The schedule computes the netlist gate for gate, except that associative trees are folded in schedule order.
- `jobsched.replay` runs the listing on data and compares every value written to a register, a scratch bit or Hold with the netlist node it stands for. It checks the key in front 0's registers at the match pass, and it fails on any read of an empty register or scratch bit.
- On random inputs the replay exercises little of the rare-event logic (flags, wipes, the match). `experiments/replay_structured.py` therefore replays on neighbourhoods taken from a running colony: 359,744 neighbourhoods at 5,621 Ages over the whole evaluation window (two seeds), 96,175 of them with a front arriving and 2,675 inside the match pass. No mismatch (`figs/replay/G16_structured*.json`).
- A negative control in the unit tests flips one gate of the listing to XOR at 12 places; the replay must catch at least 10.
- The physical check is closure of the rule on encoded colonies (below).

### How the page count came down

All on G15's netlist with generous page budgets; every schedule replayed without a mismatch.

| step | passes (flags / match / total) |
|---|---|
| G15's comb scheduler | 26 / 99 / 333 |
| pool of small startable jobs (at most 30 inputs each), everything through scratch | 13 / 35 / 63 |
| large claims with a sliding wish window; values shared by many folds loaded once | 15 / 31 / 50 |
| signed skews, one cell per lane of a bit | about 11 / 25 / 42 |
| fronts stop late in the last page before the match pass | about 11 / 23 / 38 |

- 22,800–24,600 instructions in all, of which about 16,700 gates and folds, 4,700 loads and 1,100 parks.
- 48% of the slots are used. The rest is mostly fronts waiting to pass a cell they wish a value from.

**The outcome is chaotic.** Settings that should be equivalent give totals between 36 and 46 passes. So a variant is compared over several skew scales and option sets, never on one run.

**Sizing (`experiments/size_jobs.py`).** NPe, MP and NP are constants of the netlist, so a schedule compiled for one triple is not the schedule for another. The driver probes with a free match pass, rebuilds the rule with the pages the probe used, compiles with the match pass fixed, and repeats until the compiled schedule uses what the rule declares.
- G16 is the best of 18 settings (three skew scales × six option sets; `figs/sweep/g16_e29.json`): U from 25,920 to 29,952, median 27,648.
- With the evaluation still starting at 32Q, the best of 30 settings was U = 27,360.

### What did not help

| idea | result |
|---|---|
| Continuation: a front claims the consumers of its own nodes as soon as all their operands are claimed | 54–64 passes, or a stall: the claimed work waits in the queue and its inputs fill the registers |
| Hold roots that do not depend on the fetched instruction ordered before the others | 39–53 |
| Near the end, a front claims at most a fifth of what is left | 36–43 against 37–46: inside the scatter |
| Separate window and frontier sizes before and after the match pass | 45–58 |
| Reserves of 800 nodes | 55–58 |
| A frontier of 24 nodes instead of 100 | 42–49 |
| Fronts 1–4 compute only the key before the match pass | match pass at 15–17, but 42–46 passes in all |
| A front tries four wishes per cell instead of one | inside the scatter |

### Validation of G16

Everything below was run on the final G16 (candidate digest `3ce1a6fe…`, the one in the manifest). A fresh build equals the cache and the manifest, and the 17 older recipes still rebuild bit for bit.

**Closure and backends.**
- C kernel, continuous work periods (`run_g_period.py`): three rings of random upper cells (16, 16 and 12 colonies; 4, 4 and 3 periods) and three coherent rings (16 colonies, 4 periods each). In all 23 periods the decoded ring equals the rule applied upstairs, the special procedure and the Workspace-flag windows are as Gray specifies, and the colonies are healthy at the boundary.
- CUDA kernel: bit-exact parity with the C kernel on arbitrary states, and closure (`gpu_check.py`).

**Level-0 errors** (`level0_one_tick.py`). In a healthy colony, 0 of 6,000 random and 0 of 6,000 inverted single errors were visible one tick later.

**Level-1 errors** (`level1_campaign.py`; a 64-colony slice of a healthy upper colony unless noted, checked at every tick):

| batch | Age of the upper colony | errors | certified level-1 | contained | repaired in one upper step | bit-identical at the end |
|---|---:|---:|---:|---:|---:|---:|
| dense 100×100 boxes | 0 | 64 | 64 | 64 | 64 | 64 |
| the same, upper colony inside its trickle-down window | 19,333 | 64 | 64 | 64 | **49** | 64 |
| upper pre-match program, upper front hit | 19,782 | 64 | 64 | 64 | 64 | 64 |
| upper final program, upper front hit | 22,853 | 64 | 64 | 64 | 64 | 64 |
| upper commit | 25,770 | 64 | 64 | 64 | 64 | 64 |
| sparse clusters | 0 | 64 | 64 | 64 | 64 | 64 |
| values zero / inverted / frozen / copied | 0 | 4 × 48 | 192 | 192 | 192 | 192 |
| whole upper colony (262,144 sites) | 0 | 16 | 16 | 16 | 16 | 16 |
| 200×200 bursts (not level-1 errors) | 0 | 64 | 0 | 64 | 64 | 64 |

- 656 certified level-1 errors: all contained, all bit-identical at the end, 641 repaired within one upper step.
- **The 15 others took two upper steps.** In that batch the upper colony is inside its own trickle-down window, so its cells (the level-1 cells) have Flag1 raised. A damaged colony is then a level-1 cell with a wrong stored Address under raised Flag1, and Gray's second special rule (p. 33) wipes it: the two-tick footprint of §25 (finding 6), one level up. It is a property of the rule, not of G16:
  - `upper_wipe_check.py` on one colony inside that window: 199 of 200 hit cells are wrong for a second tick on G16, and 200 of 200 on G15; none for a third.
  - The same batch on G15 (`G15_ctl_trickle_front.json`): 47 repaired in one upper step, 17 in two.
  - Earlier G15 batches did not place the upper colony inside that window, so §§25–27 did not see it. Proposition 4's time bound, as measured there, is "by the second boundary" outside that window and "by the third" inside it.
- Dense level-0 noise in a parallel ring: no error visible after one tick in the healthy middle colonies, except in the batch above, where Flag1 is raised everywhere.

**A second footprint longer than one tick, found by the same driver.** After the trickle-down window a colony's Flag2 is erased by a front that sweeps the colony at two cells per tick. A level-0 error on the cell at that front shifts the front by one cell. The difference is one Flag2 bit; it travels with the front and disappears when the front reaches the colony's end, at most Q/2 ticks later. Measured: 1 of 200 hits on G16 and 6 of 200 on G15, in a colony whose upper cell raises Flag2. Like the wipe above, it needs an upper cell that raises a flag.

**Whole colonies wiped** (the whole upper colony, 262,144 sites, five stages × two places):
- One colony: 10 of 10. At most two adjacent upper cells are wrong at one upper time; everything is physically identical from the second boundary.
- Two colonies, the box inside two colonies: 5 of 5, the same.
- Two colonies' worth touching three colonies, and three colonies: the damage grows at level 1 (9 to 22 level-1 cells after four steps). These are level-2 errors, as for G15 (§26.4).

**Three levels** (`three_level_g.py`):
- `phases`: a physical ring of two level-2 cells (524,288 sites) at five stages of the level-2 work period, six level-1 steps each: 30 of 30 exact at levels 1 and 2.
- `closure2`: 6 of 6 level-2 steps exact on the level-1 automaton.
- **Level-2 errors** (rings of 32 level-2 cells; hybrid with the hand-off checked physically in all 10 rings):

| error | when | at the first level-2 boundary |
|---|---|---|
| 3, 5, 7, 27 colonies wiped | level-1 Age 0 | gone (4 of 4) |
| 3, 5, 7, 27 colonies wiped | level-1 Age 16,000 | gone (3, 5, 7); for 27, one level-2 cell wrong, exact from the next boundary |
| 7, 27 colonies wiped on the level-2 front | level-2 final program | one level-2 cell wrong, exact from the next boundary |
| 3, 5 level-1 cells overwritten with another colony's | level-1 Age 0 | gone |

  - 12 level-2 errors: 9 gone at the first level-2 boundary; 3 leave one level-2 cell wrong for one level-2 step. G15 gives 4 of 4 on the first row (`G15_ctl_repair2_a.json`).
- **A ring of one level-2 cell is not a test of level 2.** The `--continue-level2` option of the campaign driver uses such a ring, and there G16 kept a wrong level-2 Hold bit where G15 mostly did not. That cell is its own ten neighbours, so nothing can outvote it. `level2_single_ring.py` puts the same random damage into that ring for both rules: damage during the gathers survives equally often (71 of 100 at width 9, 98 of 100 at width 21, for both), and damage during the program survives less often on G16 (39 against 63 of 100 at width 9).

**What a physical level-2 step costs now** (`gpu_level2_bench.py`, RTX 4090, `figs/gpu/G16_level2_bench.json`). U² = 6.7·10^8 ticks.

| physical ring | sites | µs per tick | one level-2 step |
|---|---:|---:|---:|
| 1 level-2 cell (its own neighbour) | 262,144 | 39.5 | 7.4 hours |
| 2 level-2 cells | 524,288 | 51.5 | 9.6 hours |
| 4 level-2 cells | 1,048,576 | 184 | 34 hours |
| 8 level-2 cells | 2,097,152 | 390 | 3.0 days |

For G15 the first row was 15.3 days on an A100 (§26.1). A full physical level-2 step has not been run; it is now a one-night job. On the level-1 automaton a level-2 step of a 32-cell ring takes 0.9 s.

**Unit tests:** 53, one opt-in. The new ones cover the job scheduler: the schedule fits its pages and reproduces the cached table; replay on random data with the negative control; replay on neighbourhoods of a running colony; the key in front 0's registers at the match pass; signed skews on distinct working cells; closure on random cells and on cells under the upper comb.

**Not repeated for G16:** the noise-together-with-errors runs of §26.3 and §26.5, the 49-batch census of §27, and the per-field Proposition-4 tables of §25.

### Where the limit is now

- **The gathers.** 52 of G16's 90 blocks pass before the evaluation starts. The program is 37 blocks.
- **The program.** At full use of the slots it would need 18 passes. The remaining factor of two is waiting: a value parked by one front reaches a front that has already passed the cell only on that front's way back, and the fetch key and the upper ALU result each sit at the end of a chain of such hand-overs.
- **The colony.** 244 of the 512 cells are margin (Gray p. 33). The 268 working cells hold the 258 bits of the upper cell, one per cell.

### Options not taken

Each of these changes the rule beyond its compiler, so each needs the owner's decision and the full validation above.

| option | Q | U | QU | status | what it changes |
|---|---:|---:|---:|---|---|
| G16 | 512 | 25,920 | 2^23.66 | validated | |
| gathers 10Q apart, evaluation from 25Q | 512 | 23,904 | 2^23.54 | sized only (best of 12 settings; median 25,488; `figs/sweep/g16_v2_gather10.json`) | the rest between gathers falls from about 3,500 to about 2,500 ticks; Gray's level-1 recovery bound is 2,124 (§14) |
| three stored copies at stride 2 instead of five | 448 | 21,056 | 2^23.17 | built in a scratch copy of the repository; closes on the GPU for 3 periods; nothing else tested | code distance 3 instead of 5: Gray's level-0 errors (one site, or two adjacent) are still corrected, two single errors 2 or 4 cells apart at one tick are not; 9,744 gates, 191 bits per cell |
| three-input instructions | 512 | — | — | estimate only | a greedy pairing removes 34% of the gate instructions (16,707 → 11,030) |

- **Fewer instructions no longer mean fewer passes.** The three-copy rule has 42% fewer instructions than G16 and needs 35 passes against 37. The program is bound by the hand-over chains, not by the slot count. So three-input instructions would buy little by themselves.
- The first option is the cheapest: no new mechanism, 8% of U.

### The route to Gács's own construction

A separate study ([GACS_ROUTE.md](GACS_ROUTE.md), scripts and logs in `gacs_route_exp/`) asked whether the features of Gács's 2001 construction that Gray's version leaves out would be practical here, and whether they would lower Q or U. It was done by a sub-agent from the papers and a private copy of this code at G15. Its measurements were made with G15's compiler; the three-copy row above is my re-run with the job scheduler. Its estimates (marked `[E]` there) are not checked, and its own list of unverified claims is its §10.

| feature of Gács 2001 | practical here? | effect on Q and U |
|---|---|---|
| A program stored in the cells and interpreted, instead of the hard-wired table | yes, but Gács 2001 does not do it either: it hard-wires the program into the rule, as Gray does, "because the written program is exposed to errors" | a stored compiled program is the archived U20 design: QU = 2^33, about 650 times G16's |
| An error-correcting code over the colony (Reed–Solomon style), instead of five copies per cell | implementable | loses the one-tick repair of level-0 errors; U 2–5 times worse by the study's estimate; Q no better than with three copies, because the margins (244 of 512 cells) come from Gray's burst width, not from the storage code |
| Three copies at stride 2 instead of five (a weaker repetition code) | yes; built and closed (table above) | Q 448, U 21,056; code distance 3 instead of 5; the study estimates a 25 times lower tolerable i.i.d. noise rate |
| Level-dependent parameters, self-organization, the "killing and creation" machinery | not needed for a fixed rule with an initial hierarchy | none on Q or U; much larger rule |

- **Verdict.** Moving towards Gács's version does not lower Q or U. The one coding change that does is the weaker repetition code, and it trades error tolerance for size.
- The fivefold storage is already an error-correcting code, the repetition code [5,1,5]. It is expensive in bits but free in time: it is decoded by every cell at every tick, which is what gives the one-tick repair. A block code over the colony saves bits and pays in time.

## 30. A faster CUDA kernel and a full physical level-2 step (2026-10-02)

**Result.**
- `gacsca/gpu_roles.py` runs the same rule three times faster than `gpu.py` on a ring of one level-2 cell (2.8 times on two), and is equal to it bit for bit in every test.
- With it, a ring of one level-2 cell of G16 (262,144 sites) and a ring of two (524,288 sites) were each run for a whole level-2 step, U² = 671,846,400 ticks, with no hand-off to the level-1 automaton. In both, the level-2 state at the end equals the rule applied to the initial one, and every check on the way was exact.

All timings are on this machine's RTX 4090 (24 GB), G16, GPU otherwise idle.

| ring | kernel | µs per tick, gathers | µs per tick, program | µs per tick, whole period | one level-2 step |
|---|---|---:|---:|---:|---:|
| 1 level-2 cell, 262,144 sites | `gpu.py` | 35.3 | 38.7 | 36.7 | 6.9 h |
| | `gpu_roles.py` | 8.4 | 18.2 | 12.4 | 2.3 h |
| 2 level-2 cells, 524,288 sites | `gpu.py` | 52.7 | 54.6 | 53.5 | 10.0 h |
| | `gpu_roles.py` | 15.5 | 24.8 | 19.3 | 3.6 h |

(`experiments/gpu_roles_bench.py`, receipt `figs/gpu/G16_roles_bench.json`: both kernels run the same 2,000 ticks from the same state, and the states are equal. The program is 41% of the work period. The full run below took 2.47 hours with its checks. For G15 the first row was 15.3 days on an A100, §26.1.)

### What limits `gpu.py`'s kernel

One thread handles a 32-site word and executes the whole netlist for it: 19,071 instructions, of which 9,417 LOP3 (the gates), 2,672 IMAD and 1,268 IADD3 (address arithmetic), 2,277 SHF (assembling neighbours), 852 global loads, 929 spill loads and stores.

| measurement, one level-2 cell | µs per tick |
|---|---:|
| the kernel | 36.6 |
| only the grid synchronization | 1.0 |
| only the 774 loads of a word, results XOR-ed | 8.8 |
| only the 258 stores | 4.2 |
| 258 times a load and a store that depends on it | 31.6 |
| only the logic (inputs synthesized, outputs XOR-ed into one store) | 32.0 |
| the kernel with 64 blocks of 128 threads, or with 32 blocks of 256 | 36.6 / 37.3 |

- **The kernel is bound by the latency of one warp, not by the GPU's throughput.** A ring of one level-2 cell is 256 warps. Each executes its 19,000 instructions one after the other, at about five cycles per instruction, whether it shares its multiprocessor with one other warp or with seven. Three quarters of the GPU's 128 multiprocessors are idle.
- A load whose value is waited for costs about 100 ns (the state is in the L2 cache, not in L1); loads issued together cost 11 ns each.
- The grid synchronization is cheap. §26.1's remark that it bounds the kernel was wrong.

**What a multiprocessor does with several warps** (a synthetic kernel, 3,000 three-input gates per pass on 48 values, no memory traffic):

| active warps per block, one block per multiprocessor | all warps run the same code | every warp runs different code |
|---:|---:|---:|
| 1 | 2.4 µs per pass | 2.5 |
| 2 | 2.4 | 4.0 |
| 4 | 2.4 | 10.1 |
| 8 | 4.8 | 24.9 |

- Up to four warps that run the same code run in parallel at full speed: 0.8 ns per gate.
- Warps that run different code get in each other's way. Four different streams take four times as long as one, so they gain nothing; two gain a little.
- So the unit of parallelism on this GPU is "the same instruction stream on many words", and a stream should be short.

### Design (`gacsca/gpu_roles.py`)

**Skipping the comb's logic where no front arrives.**
- Let Z be the gates outside the cone of the non-front outputs and of `arrive`: operand selection, the ALU, the register update, the Pi key. Z is 10,158 of G16's 16,767 gates.
- With `arrive` = 0 the front outputs (reg, pend, pkind, pval) are the constant 0. `check_guard` verifies this by constant propagation every time a kernel is built, and a unit test checks that the same test rejects a field that is not a front field.
- A block computes `arrive` for its 32 words. If it is zero in all of them, the block evaluates no Z gate and stores zeros in the front fields; otherwise it evaluates everything. Both sides are the netlist's own gates, so nothing depends on the state being healthy: a ring of random bits is computed as exactly, only without the saving.
- The decision is taken per block, and all threads of the block take the same branch. (A decision per word would split warps.)

**The layout that makes the skip pay.** The state is stored as [row][word position in the colony][colony]. The 32 lanes of a block then hold the same word position of 32 colonies. In a healthy ring the comb is at the same place in every colony, so a block is either all "no front" or all "front". The host permutes on upload and download.

**Several threads per word.** A block is 32 lanes × 6 roles, one warp per role; lane i of every warp works on the same word.
- `Partition` gives every gate one or more *homes* (roles that evaluate it) and a *stage*. A value that another role needs is written to a shared-memory slot during its stage and read from the next stage on; stages end with a block barrier. Slots are reused when their last reader has passed (220 slots).
- Role 0, the core, evaluates every gate that depends only on the Address, Age and flag fields: the computed Address and Age, `arrive`, and all the control signals (3,460 gates). It publishes 88 of them.
- Roles 1–3 evaluate the fivefold fields, divided by field: info, hold, mail, scratch and the pending-write votes; the history lanes with negative offset; those with positive offset. Each stored row is then read by one role.
- Front work is homed by its inputs. A Z gate that depends on the registers of one role only lives there; so each role votes its own registers, selects their sources, and folds its own part of the two 82-way operand ORs. The gates above that (the top of the ORs, the ALU) are few and are duplicated.
- No role recomputes light logic for the front's sake: Z work reads such values from slots.
- Five stages: (1) control signals, votes; guard known. (2) Pi key and lookup; register votes. (3) source selection, operand ORs. (4), (5) ALU, register update.

**Compiled for one ring size.** With the number of words a compile-time constant, a load needs no address arithmetic. The kernel has 13,554 instructions for both branches together, 217 IMAD among them.

**Correctness.** Every gate of the netlist is evaluated as it stands; only who evaluates it, and when, is chosen. The unit tests check the partition (every live gate has a home, no light gate depends on Z, every operand is available at its gate's stage) and compare `RoleSim` with `GpuSim` bit for bit: on random states; on a ring that is half random and half healthy colonies, so that blocks disagree; on healthy colonies with coherent and with random upper states, 300 ticks from each of five stages of the period; and through a whole work period (closure).

### How the time came down (one level-2 cell)

| step | gathers | program |
|---|---:|---:|
| `gpu.py` | 35.3 | 38.7 |
| eight roles, no skip | 31 | 31 |
| the same with the loads of a role issued together | 23 | 23 |
| skip; three light and four front roles | 12.2 | 22.8 |
| front work homed by its inputs; no light logic recomputed for the front | 11.7 | 19.6 |
| ring size compiled in | 9.05 | 18.5 |
| light roles by field, so that each row is read once | 8.4 | 18.5 |

**What did not help.**

| idea | result (gathers / program) |
|---|---|
| One thread per word with the skip (one stream, no slots, no barriers) | 16.0 / 29–35: 2 KB of spills |
| Two or three roles | 9.2–9.5 / 22–30 |
| Eight to ten roles | spills (fewer registers per thread); 13–21 / 21–23 |
| 64 lanes per block, one block per multiprocessor | no change |
| Heavy blocks spread so that no multiprocessor holds two | no change |
| Stores collected at the end of a role, or in groups | no change, or worse (spills) |
| Instructions re-ordered so that an operand is at least 2–8 instructions old | no change |

**Where the time goes now.** A block's six roles are six different instruction streams. Alone, each takes 2–3 µs; together they take about as long as one after the other, as in the table above. The light path is 3,460 + 3,329 gates in four streams (8.4 µs); a block with a front runs 17,472 gates in six (16–18 µs).

### A full physical level-2 step

`experiments/level2_physical.py`: random level-2 cells are encoded twice, and the physical ring is run on `RoleSim` for U level-1 steps of U ticks.
- Every 64 level-1 steps the decoded level-1 ring is compared with the level-1 automaton (the same rule on the 512 level-1 cells, run on the C kernel), and the health of the physical colonies is checked.
- At the same points the next level-1 step is run a second time from the same state on `gpu.py`'s kernel, and the two physical states are compared bit for bit.
- At the end the twice-decoded level-2 state is compared with the rule applied to the initial level-2 state.

**Result** (`figs/three_level/G16_level2_physical_n1_s0.json`; seed 0, one level-2 cell, 2.47 hours, 12.7 µs per tick).
- All 25,920 level-1 steps were run physically: 671,846,400 ticks of 262,144 sites.
- The decoded level-1 ring equalled the level-1 automaton at all 405 checks, and the colonies were healthy at each.
- At 404 of those points the next level-1 step was run again on `gpu.py`'s kernel: the physical states were equal bit for bit every time.
- At the end the twice-decoded level-2 state equals the rule applied to the initial level-2 state: 0 bits wrong, where the step changes 89 bits of the level-2 cell.

**A ring of two level-2 cells** (`figs/three_level/G16_level2_physical_n2_s1.json`; seed 1, 524,288 sites, 3.87 hours, 19–20 µs per tick). The two cells are different random states, so each has a neighbour that differs from itself.
- All 25,920 level-1 steps were run physically: 671,846,400 ticks.
- The decoded level-1 ring (1,024 cells) equalled the level-1 automaton at all 405 checks, and the colonies were healthy at each.
- At 404 of those points the next level-1 step was run again on `gpu.py`'s kernel: equal bit for bit every time.
- At the end both level-2 cells equal the rule applied to the initial level-2 ring: 0 bits wrong, where the step changes 210 bits.

**What the two runs do and do not show.**
- They are the first executions of a level-2 step by the physical rule alone, for any G candidate: no host transition, no level-1 automaton in the loop.
- In the two-cell ring a cell's ten neighbours are itself and the other cell, alternating. A level-2 cell with ten different neighbours has not been run physically.
- Two seeds, without errors.

### Left open

- **Translated copies.** 6,670 of the 16,767 gates compute a function that another gate computes at a neighbouring site (the votes for the seven logical cells around a holder are one vote, translated). Computing each once per word and reading the neighbours' results would leave 11,834 gates and 1,369 input bits instead of 2,862, at the price of a second grid-wide phase. Not built.
- **One efficient stream.** By the synthetic test a single stream with no stalls would run the light path in about 6 µs and the full path in about 15. The one-thread kernel is far from that because of its spills and of loads that are waited for.
- **Errors.** `RoleSim` has no error injection; the campaigns stay on `gpu.py`.

## 31. Gray's error-class constants and the colony margin (2026-10-02)

A study by a sub-agent, on the question whether Gray's constants (24, 104, 200) can be changed so that the level-1 box, and with it the colony margin, shrinks. The full text, with every statement marked as read, measured or inferred, is [ERROR_LEVELS.md](ERROR_LEVELS.md); its scripts and results are in `error_levels_exp/`. It used the C kernel only. **Nothing of it is adopted; G16 is unchanged.**

**Where the numbers come from.**
- Gray prints 24, 104 and 200. Only 24 is called "a convenient choice" (p. 17). The others follow: 26 = 24 + 2, 104 = 4 · 26, 26 + 104 + 26 = 156, which "fits easily" into 200.
- By Gray's own definitions a level-1 error is at most 104 + 2 · 24 − 2 = **150** sites wide and 150 ticks long. Checked here with the repository's classifier: four points spanning 150 are one level-1 error, spanning 151 they are not.
- **104 is used once, as a convenience in a proof** (p. 18). The study argues that condition (iii) works with any separation c ≥ 1: the level-1 box becomes c + 2 · 24 − 2, and Proposition 1 (the bound ε_n ≤ (QU · ε_(n−1))²) contains neither constant. With c = 16 a level-1 error is at most 62 wide. That argument is the sub-agent's and is not checked by anyone else.
- **24 should stay.** It is the spacing between errors that the rule is promised, and Gray's higher-level argument needs it above the Flag2 period of 16, which is built into the rule.

**Do the later lemmas survive, and are the two constants independent?** Worked out by the main session in [GRAY_CONSTANTS.md](GRAY_CONSTANTS.md).
- As printed they are tied: 104 = 4 · (24 + 2), and Gray's proof that every error above level n−1 lies in a candidate level-n error needs c ≥ 4(λ + 2) in one step.
- That lemma is proved there for every c ≥ 1 (the case Gray excludes with 104 is the case in which the cluster is already a candidate one level up). The size of a level-n error is then (c + 2λ + 4) Q^(n−1), and Proposition 1's probability bound does not contain c. A brute-force check on 15,000 random error sets with small constants found no violation.
- After §5.1 the box size appears only in upper bounds (two colonies touched, the island estimates, the recovery time against the rest between gathers). A smaller c cannot break them.
- λ appears in lower bounds that come from the rule: the wave-speed losses of Proposition 2, and Proposition 5's last step, where a level-k error every 24 periods must be rarer than the Flag2 reversal every 16. So c is free and λ is not.
- Seen one level up, a level-n error is up to c + 2λ + 6 cells wide: the rule must tolerate bursts of 70 cells for c = 16 (158 for Gray's constants). The margin of 58 covers 73, so c can be at most 19.

**What a smaller box buys.** The margin is sized so that a burst of B cells on a colony boundary cannot directly hit the front state or the data of both colonies: margin ≥ (B + 43)/2. The working cells are 268, and Q must be a multiple of 64.

| box the margin is sized for | margin | Q |
|---:|---:|---:|
| 200 (G16) | 122 | 512 |
| 74–137 | 90 | 448 |
| 10–73 | 58 | 384 |

- Correcting 200 to Gray's 150 gains nothing: Q stays 512.
- Gray's recovery bound is 2Q + 5.5B ticks, and the rest between gathers must exceed it. With Q = 384 gathers 10Q apart meet it even for B = 200; 9Q meets it for the 72-cell box.

Sized on the CPU with G16's own sizing sweep (18 settings per row; best, and median in brackets):

| | Q | gathers | U | QU | status |
|---|---:|---|---:|---:|---|
| G16 | 512 | 12Q | 25,920 (27,648) | 2^23.66 | validated |
| margin 58 | 384 | 12Q | 22,176 (23,904) | 2^23.02 | closes on the C kernel |
| margin 58 | 384 | 10Q | 20,736 (22,752) | 2^22.92 | closes on the C kernel |
| margin 58 | 384 | 9Q | 19,296 (21,888) | 2^22.82 | closes on the C kernel |

**Evidence for the Q = 384 variants** (the sub-agent's runs, C kernel, upper colony at Age 0 only):
- Closure for 6 work periods each; 0 of 26,000 level-0 errors visible after one tick.
- 617 bursts 40–200 cells wide, with random, copied and shifted values: never more than two adjacent upper cells wrong, never a wrong cell after the next upper step, all bit-identical to the error-free ring at the second boundary.
- A 72-cell burst on a boundary never reached the upper state with random values (99 of 99). Wider ones left one upper cell wrong, or two adjacent ones in 19 of 132.
- The local structure was repaired within 380 ticks in the worst case; the rest between gathers is 1,929 ticks at 10Q.

**A correction to an earlier claim, for G16 as well.** The summary said that with the margin a burst on a colony boundary can damage at most one colony. (§16 says that it can *reach* the data of at most one, which stays true.) The stronger sentence holds for the value modes the campaigns used. It does not hold for a burst that writes a block of consistent but misplaced Addresses (Gray's damage island, p. 25):
- The sub-agent found, on G16: such a burst lying entirely inside the two margins damaged the right-hand colony in 9 of 11 runs, and a 200-cell one reaching 10 cells into the right-hand colony left two adjacent upper cells wrong in 5 of 5.
- Checked again by the main session on the repository's code (`error_levels_exp/shiftcheck_main_session.py`): at two of three Ages the shifted 200 × 200 burst left the two adjacent upper cells wrong at the next boundary, where the same box with random values left one. All six rings were bit-identical to the error-free ring one period later.
- This is within Gray's Proposition 4, which allows two adjacent colonies. The summary's sentence is corrected. The GPU campaigns have no such value mode; adding one is listed in STATUS.

**The price of the smaller margin.** "A burst up to 200 cells wide directly hits at most one colony" becomes "up to 73 cells wide". Wider boundary bursts can hit two colonies, which the upper level absorbs like any two adjacent wrong cells. The certified level-1 class changes with c: with c = 16 a dense 100 × 100 box is no longer one level-1 error.

**Not done:** GPU runs, the classified campaign, upper Ages other than 0, three levels. A margin-58 candidate is a new rule and needs everything §29 lists for G16.

## 32. Why Gray needs Q > 30.7 × box, and what G16 does without it (2026-10-02)

**The question.** Gray's Propositions 2 and 5 assume Q ≥ 2^13. Written with the box size B in place of 200, his estimates need Q > 30.7 B (§31, [GRAY_CONSTANTS.md](GRAY_CONSTANTS.md)). G16 has Q/B = 2.6. What is the assumption for, what happens without it, and can the argument be repaired?

**What the assumption is for** (Gray pp. 24–26).
- After a level-1 error, the cells with wrong Address or Age form a *damage island*. Its left end is eroded: the leftmost cell sees left neighbours that contradict its apparent colony, raises Flag1, votes from the left and takes the correct values.
- The right end grows. A cell with three wrong left neighbours inside its apparent colony also raises Flag1 and votes from the left, so the island's pattern spreads to the right at three cells per tick, until the left end of the next undamaged colony.
- **The one exception.** If the leftmost cell of the island sits at the left end of its own apparent colony, it has no left neighbours inside that colony, sees nothing wrong and keeps Flag1 = 0. It is then eroded only if a wave of Flag1 arrives from an inconsistency further right in the same apparent colony.
- So a block of Q cells with Addresses that agree with each other but are shifted has no inconsistency inside, and its left end looks like an ordinary colony boundary. **No level-0 rule removes it.** This is the "misaligned level-1 cell" that Gray reserves for level-2 errors (p. 37).
- Gray excludes it by size: the island is at most 5B after the error, 15B when Flag1 has spread (must be < Q/2), 23B when the left colony is repaired (must be < 3Q/4). 23B < 3Q/4 is Q > 30.7 B. His estimate lets the island grow at speed 4 for the whole time and does not use the colony boundary that stops it.

**Without the assumption the island does fill a colony.** On G16 a 200-cell burst of shifted states makes the Address wrong in up to 702 sites: the 200 of the box and the whole right-hand colony (§31). Gray's proof does not cover this case.

**A sharper condition: a race.** A shifted block starting at cell e (apparent Address 0) can only become a quiet, complete colony [e, e+Q) if
1. the burst holds at least a few cells on both sides of a colony boundary, with e in the left colony (the pattern cannot enter the right colony by itself: its first cells vote from the right);
2. the front reaches e + Q: (Q − w)/3 ticks, if w cells of the block lie inside the box;
3. the Flag1 bits that the front raised inside the block have all returned to 0. They do so in a wave from the right at 2 cells per tick: (Q − w)/2 more ticks;
4. the burst still holds the left end of the block at that moment. Otherwise the Flag1 wave reaches the left end, the exception is passed, and the erosion sustains itself (three correct left neighbours are then inside the apparent colony).

So the block survives only if **the burst lasts at least (1/3 + 1/2)(Q − w) = (5/6)(Q − w) ticks.**

**Measured** (`experiments/misaligned_block.py`, receipts `figs/level0/G16_misaligned_block*.json`). A 32-colony slice of a healthy upper colony; the burst rewrites a box across a colony boundary with the states of the cells 2Q + shift further right (plausible states, Addresses off by `shift`), every tick.

| shift | box width | cells of the block in the box, w | (5/6)(Q − w) | longest burst that is repaired | shortest that leaves a block |
|---:|---:|---:|---:|---:|---:|
| 32 | 48 | 42 | 392 | 350 | 400 |
| 96 | 200 | 106 | 338 | 330 | 340 |
| 160 | 200 | 170 | 285 | 280 | 290 |
| 192 | 208 | 202 | 258 | 256 | 272 |
| 224 | 240 | 234 | 232 | 232 | 240 |

- The prediction holds in all five cases.
- **Below the threshold** the Addresses are correct again 210–310 ticks after the burst (erosion runs at three cells per tick, not at Gray's one half). At the next boundary no upper cell is wrong if the burst fell in the gathers, and two adjacent ones if it fell after them; the ring is bit-identical to the error-free one from the second boundary on.
- **Above it** a block of at least Q − 10 wrong Addresses stays for about 16,900 ticks: until the trickle-down window of its own work period, when the misaligned colony's upper Flag1 comes down and erases it, as Gray describes for level-2 damage (p. 38). The upper state is then wrong in 8 cells at the first boundary, 14, 17 and 12 at the next three. **The burst has become a level-2 error.** Whether level 2 clears it, as it clears colony wipes (§29), was not tested here; §33 follows it on the level-1 automaton in a ring that holds a complete upper colony: the growing count is a glider of the maintenance rule with its Flag1 trail, confined to the upper colony, plus 7 cells of wrong Info.
- Random values never leave a block: the Addresses are correct 8–32 ticks after a 200 × 500 burst.
- A burst that does not reach into the right-hand colony cannot make a block (16-cell bursts of any length: repaired within 54 ticks).

**For a square burst** of side B the condition B ≥ (5/6)(Q − B) is **B ≥ (5/11) Q**. If level-0 errors push the front to Gray's upper bound of 4 cells per tick it is B ≥ (3/7) Q.

| | Q | a block can survive from B = (no noise / front at 4) | level-1 errors (Gray, c = 104) | level-1 errors with c = 16 | the 200 × 200 burst |
|---|---:|---:|---|---|---|
| G16 | 512 | 233 / 219 (measured: 232 repaired, 240 not) | 150: safe | 62–70: safe | safe, by 10–15% |
| margin-58 variant (§31) | 384 | 175 / 165 (formula only) | 150: marginal | 62–70: safe, by a factor of 2.4 | **not safe** for a shifted block |

**Answers.**
- **Can the proof be saved for Q = 512?** For Proposition 2, yes: replace Gray's size estimate by the race. The condition is that a level-1 error is shorter than (5/6)(Q − w) ticks, about **Q > 2.4 B** instead of Q > 30.7 B. G16 meets it for Gray's level-1 errors and, narrowly, for 200 × 200 bursts. The argument is mine; it is confirmed by the five thresholds above and not checked by anyone else.
- **Proposition 5** makes the same estimate one scale up ("several hundred times Q²" against a level-3 cell). Its speeds come from trickle-down, and Gray gives no numbers for them, so the race cannot be written down from the text. The evidence there remains the three-level runs.
- **Is a rule change needed?** Not for the level-1 class. No local rule can remove a complete shifted colony: its left end and the left end of a healthy colony next to damage look the same, and the colony boundary that stops the island is the same mechanism that protects the block. Deciding which side is wrong is what the hierarchy is for. A rule change could only move the threshold: a Flag1 that falls back at one cell per tick instead of two would give B ≥ (4/7) Q, at the price of a two-tick footprint for some level-0 errors and of every timing in the trickle-down. A smaller box does more, and changes no rule.
- **For the margin-58 variant** this adds a cost that §31 did not have: at Q = 384 a shifted 200 × 200 burst is above the threshold, so the variant may only claim bursts up to about 165. Its level-1 class (c = 16, at most 70 wide) is further from the threshold than G16's.

## 33. G17: the colony sized for the smaller level-1 box (2026-10-05)

**Decision.** The owner chose the plan of §§31–32: keep λ = 24, take c = 16 in Gray's condition (iii), size the margin for the box that follows, and keep five copies. The level-1 box is then at most 62 sites (Lemma B of [GRAY_CONSTANTS.md](GRAY_CONSTANTS.md)); seen one level up, a level-n error is at most 70 level-(n−1) cells wide. The margin is sized for 73.

| | Q | U | U/Q | QU | bits/cell | gates | instructions | passes | margin | sized for a burst of | gathers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| G16 | 512 | 25,920 | 50.6 | 2^23.66 | 258 | 16,767 | 23,807 | 37 | 122 | 200 | 12Q |
| **G17** | **384** | **20,736** | 54.0 | **2^22.92** | 258 | 17,013 | 22,863 | 35 | 58 | 73 | 10Q |

- G17 is G16's rule with three constants changed: the margin (58), the gather spacing (10Q), and the lane skews (scale 2). The evaluation starts at 25Q (block 34 of 72). The compiler and every mechanism are G16's.
- QU is 1.67× smaller than G16's; a level-2 step costs 2.8× less.
- The rest between gathers is 1,924 ticks against Gray's recovery bound 2Q + 5.5·73 = 1,170 (and 1,868 for a 200-cell burst, which the rest still meets).
- The code: `ParamsG.burst` (default 200, so every older recipe is unchanged) replaces the literal 200 in the margin check; `gray_errors` takes the separation `sep`; `level1_campaign.py` takes `--sep` and, for the shifted-block value mode of §32, `--shift`. The manifest has 19 entries and all 18 older recipes rebuild bit for bit.

### Validation

Everything below is on the final G17 (candidate digest `23a14aab…`), with the drivers and criteria of §29. The receipts are the `G17_*` files under `figs/`.

**Closure and backends.** C kernel, continuous work periods: three rings of random upper cells (16, 16, 12 colonies; 4, 4, 3 periods) and three coherent rings (16 colonies, 4 periods): 23 periods, all exact, special procedure and Workspace-flag windows as Gray specifies, colonies healthy. CUDA kernel: bit-exact parity with the C kernel on arbitrary states, and closure.

**The compiled schedule.** `jobsched.replay` on random data (unit test), and on neighbourhoods of a running colony: 356,288 neighbourhoods at 5,567 Ages over the whole evaluation window (two seeds), 102,575 of them with a front arriving and 2,750 inside the match pass, no mismatch.

**Level-0 errors.** 0 of 6,000 random and 0 of 6,000 inverted single errors visible one tick later in a healthy colony. One wrong cell in a colony inside its trickle-down window: 199 of 200 wrong for a second tick (Gray's wipe rule, §25), none for a third; after the window the Flag2 erasure front carries a difference in 3 of 200 (§29).

**Level-1 errors** (64-colony slice of a healthy upper colony unless noted; every tick tracked; classification with c = 16):

| batch | Age of the upper colony | errors | certified level-1 | contained | repaired in one upper step | bit-identical at the end |
|---|---:|---:|---:|---:|---:|---:|
| dense 16 × 16 boxes (the certified class) | 0 | 64 | 64 | 64 | 64 | 64 |
| sparse clusters, certified | 0 | 64 | 64 | 64 | 64 | 64 |
| **72 × 72 bursts: the design burst** | 0 | 64 | — | 64 | 64 | 64 |
| 72 × 72, upper colony in its trickle-down window, upper front hit | 14,245 | 64 | — | 64 | **53** | 64 |
| 72 × 72, upper colony in its Flag1 return wave, upper front hit | 14,413 | 64 | — | 64 | **51** | 64 |
| 72 × 72, upper pre-match program after the wave, upper front hit | 14,800 | 64 | — | 64 | 64 | 64 |
| 72 × 72, upper final program, upper front hit | 18,052 | 64 | — | 64 | 64 | 64 |
| 72 × 72, upper commit | 20,586 | 64 | — | 64 | 64 | 64 |
| 72 × 72, values zero / inverted / frozen / copied | 0 | 4 × 64 | — | 256 | 256 | 256 |
| 72 × 72, a block of shifted Addresses across a boundary (`--shift 2Q+32`, §32) | 0 | 64 | — | 64 | 64 | 64 |
| 200 × 200 bursts, beyond the design | 0 | 64 | — | 64 | 64 | 64 |
| 72 × 72 on the whole upper colony (147,456 sites) | 0 | 32 | — | 32 | 32 | 32 |

- 128 certified level-1 errors: all contained, repaired in one upper step and bit-identical at the end. For the certified class with c = 16 the dense boxes are 16 wide; the 62-wide maximum of the class is sparse.
- The design burst (72 cells, random values) never damaged two colonies: 46 of 64 left no upper cell wrong, 18 left one.
- Two adjacent upper cells wrong at one upper time, repaired next step: in 21 of 64 of the 200 × 200 bursts (the margin is no longer sized for them), in 1 of 64 shifted blocks, in 1 of 64 zero-valued and 1 of 64 frozen bursts.
- The two-step repairs are Gray's wipe rule one level up (§29): the upper colony's Flag1 is raised during its trickle-down window and, as the wave returns, until about Age 14,500; the batch at 14,413 is inside that wave (the receipt was overwritten by the run at 14,800; its numbers are in the run log).
- Dense level-0 noise in a parallel ring (`--e0`): no violation of the one-tick repair in the healthy middle colonies, except where the upper Flag1 is raised.

**Whole colonies wiped** (the whole upper colony, five stages × two places): one colony 10 of 10, two colonies inside two colonies 5 of 5, at most two adjacent upper cells wrong at one time and identical from the second boundary; a two-colony box touching three colonies is a level-2 error, as for G16.

**Three levels** (`three_level_g.py`, 32 level-2 cells for the error runs):
- `phases`: 30 of 30 exact at levels 1 and 2 across the five stages (two level-2 cells, 294,912 sites).
- `closure2`: 6 of 6 level-2 steps exact.
- `repair2`: 3, 5, 7 and 27 colonies wiped at level-1 Age 0 and at Age 12,000: all 8 gone at the first level-2 boundary. 7 and 27 colonies wiped on the level-2 front: one level-2 cell wrong at the first boundary, exact from the next. The hand-off was checked physically in all 10 rings.
- `copy2`: 3 and 5 level-1 cells overwritten with another colony's: gone at the first boundary.

**Unit tests:** 59, one opt-in. New: the classifier with the separation as a parameter (the 62-wide maximum is attained, one more site is not level 1, a dense box wider than c is a union). The margin and comb tests take the burst width from the recipe.

**A full physical level-2 step** (`level2_physical.py --candidate G17 --n2 1 --seed 0`, receipt `G17_level2_physical_n1_s0.json`, the role kernel of §30): one level-2 cell, 147,456 sites, U² = 429,981,696 ticks, 1.73 hours at 11.9 µs per tick on the shared GPU. The level-2 state at the end equals the rule applied to the initial one (89 bits changed, 0 wrong); the decoded level-1 ring equalled the level-1 automaton at all 324 checks (every 64 periods), the colonies were healthy at each, and the 323 re-runs of a level-1 step on the reference kernel were equal bit for bit.

**Not repeated for G17:** the noise-with-errors runs of §26 and the census of §27.

### The limits that come with the smaller colony

**The misaligned-colony limit** (`misaligned_block.py`, §32, on G17):

| cells of the shifted block inside the burst, w | (5/6)(Q − w) | longest burst repaired | shortest that leaves a colony |
|---:|---:|---:|---:|
| 42 | 285 | 250 | 300 |
| 106 | 232 | 200 | 250 |
| 170 | 178 | 150 | 200 |

- The race of §32 holds on G17 with the same speeds. A block left behind survives about 11,800 ticks (to the trickle-down window of its period, or 19,800 when the burst falls after it) and the burst then acts as a level-2 error, as on G16.
- For a square burst the limit is about 175 ticks; the design burst (73) is below it by a factor of 2.4, G16's level-1 class (150) would be marginal, and a 200 × 200 burst of shifted states is above it. G17 therefore claims bursts up to 73 cells, and 200 × 200 bursts only with the value modes of the campaigns.
- A 72-cell burst cannot hold a block with its boundary more than 36 cells into the left colony; with the boundary 32 cells in, every burst up to 250 ticks was repaired.

### The race one level up

**The level-1 automaton** (`misaligned_block2.py`, receipts `figs/three_level/<cand>_misaligned_block2*.json`). The same rule on a ring of level-1 cells: 32 level-2 cells of a healthy level-3 colony, 32Q level-1 cells, one level-1 step costing what one tick costs on as many sites. The burst replaces a box of level-1 cells across the boundary between the two middle level-2 cells by the level-1 cells 2Q + shift to the right, for `height` level-1 steps (the construction of §32 one level up); the Address rows are compared with the error-free ring every 8 steps, the decoded level-2 state at the next five level-2 boundaries.

| | w | (5/6)(Q − w) | level 1: longest burst repaired / shortest that leaves a block | level 0 (§32, §33) |
|---|---:|---:|---|---|
| G17 | 42 | 285 | 250 / 300 | 250 / 300 |
| G17 | 106 | 232 | 200 / 250 | 200 / 250 |
| G17 | 170 | 178 | 150 / 200 | 150 / 200 |
| G16 | 42 | 392 | 300 / 450 | 350 / 400 |
| G16 | 106 | 338 | 300 / 450 | 330 / 340 |
| G16 | 170 | 285 | 150 / 300 | 280 / 290 |

(G16 at level 1 was run with bursts of 10, 30, 70, 150, 300 and 450 steps only; G17 with 10, 30, 70, 150, 200, 250 and 300.)

- The speeds are those of level 0 in level-1 units: the right end of the island advances 3 level-1 cells per level-1 step until the end of the level-2 cell, the left end follows at 3 per step once the burst stops, and below the threshold the Addresses are correct again 144–234 steps after the burst (G17; on G16 188–236 after the 300-step bursts, the shorter ones were first sampled later).
- So the race condition of §32 holds one level up with the same constants. A level-2 error can leave a misaligned level-2 cell only if it holds a shifted block for (5/6)(Q − w) level-1 steps: at least 262 on G17 and 368 on G16 for the widest block a level-2 error can hold (w ≤ 70), against the 70 level-1 steps a level-2 error lasts at most. This is ledger item D4; it is an argument confirmed by the thresholds, not a proof.

**A block that does survive** — a burst of 200–450 level-1 steps, which at the scale of level 1 is larger than any level-2 error. As at level 0, the misaligned level-2 cell stays until the trickle-down window of its level-2 period (11,900 level-1 steps on G17, 16,900 on G16) and is wiped there. At the next level-2 boundary 8 level-2 cells are wrong: 5 blank ones (Address 0, Age 0) where the block and the piece of the next cell were, Flag1 in 3 cells to their left, the Mailbox cleared in all 8. These are the "8, 14, 17 cells" of §32, read there as damage that spreads. Followed in a ring that holds a complete level-2 colony (`--n2 384`: one level-3 cell, 147,456 level-1 cells, 2.3 s per level-2 step on the shared GPU) it is this:

- The Addresses are correct from the second boundary on. The Info of 7 level-2 cells [−1, 5] stays wrong (5 cells in the two-colony ring below): the maintenance rule does not repair data within a work period. Wipes and copies of 3–27 cells were restored at the next boundary in §29 (`repair2`, `copy2`, one level down); whether the commit of the level-3 period restores these 7 was not followed (20,736 level-2 steps, 13 hours).
- The repaired blank cells come out with their Age one step behind, and **three or more adjacent cells whose Age lags by one step are a glider of Gray's maintenance rule** (`maintenance.py`, Gray's §5.2). Each step the three cells to the right of the group see three or more left neighbours with the wrong Age, raise Flag1, vote from the left and take the lagging Age; the three leftmost cells of the group vote from the left too and catch up (one or two lagging cells are repaired in one step: their right neighbours see at most two mismatches). The group keeps its width, moves right at 3 cells per step with the Addresses untouched, and leaves Flag1 raised behind it: Flag1 propagates to the left at 3 cells per step and falls back from the right at 2 per step only once no flagged cells feed it. The Mailbox is cleared wherever Flag1 is up. In the level-2 colony this went on for 64 level-2 steps, 3 cells per step, the flagged region growing by 3 at both ends, until the glider reached the colony's right end.
- In the one-colony ring the glider then crossed into the ring's only neighbour, the same colony, already flagged, and circled for ever: an artefact of that ring. In a ring of two level-3 cells (`--n2 768`, 294,912 level-1 cells, 5 s per level-2 step, 301 boundaries) the glider dies at the colony's right end at boundary 64–65, Flag1 stays inside the colony (its left end at Address 0) and falls back at 2 cells per step, gone at boundary 256: Q/6 + Q/2 level-2 steps for a glider born in the middle of the colony, (5/6)Q at most. The neighbouring colonies' Address, Age, flags and data are never touched. What does cross the colony boundaries, at one cell per step, is the mail: the stream that carries the colony's state to its neighbours was cleared while Flag1 was up and carries the wrong Info (5 cells in this ring) after; it is the neighbours' view of a wrong level-3 cell, not damage to them.
- The same glider at level 0 (G17, ring of 32 colonies; 3, 4 or 6 adjacent cells set one tick back in Age, 100 cells into a colony, at Ages 2000 and 6000): it moves right at exactly 3 cells per tick with Flag1 raised behind it over the whole colony, dies at the colony's right end at tick 94–95 (the cell at Address Q − 1 has no right neighbours inside its colony; once its left neighbours have caught up its Flag1 falls and it votes from the right), and the flags recede at 2 cells per tick and are gone at tick 285. On G16 (4 cells, Ages 2000 and 15,000) the glider dies at tick 137–138 and the flags are gone at tick 393. No Address is ever wrong. The repair times of §32 and of this section fit this clock: the Addresses of a block below the threshold are correct within (Q − x)/3 ticks of the burst's end, and the flags need up to Q/2 more, (5/6)Q in all: 320 ticks on G17 and 427 on G16, within the rest between gathers (1,924 and 3,588).

**What this adds to the ledger.** D4 (a level-2 error cannot leave a misaligned level-2 cell) is argued by the race one level up and confirmed by the thresholds. A burst above the race limit is outside the claims; what it does one level up is now known: 5–7 level-2 cells with wrong Info, left for the level-3 period to restore, and in the level-2 colony a glider with Flag1 for at most (5/6)Q level-2 steps, confined to that colony; the neighbouring colonies see it only through the mail. The glider itself is a property of the maintenance rule at every level and the reason the damage island moves at 3 cells per tick.

### The ledger

[LEDGER.md](LEDGER.md) lists every statement the construction's reliability rests on, with its status: proved, argued and measured, measured only, or assumed.
