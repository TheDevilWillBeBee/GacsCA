# Fixed-rule hierarchical self-simulation: the bit-level front construction (R0 → G15)

Started 2026-09-29 as a successor to the Q=8192, U=2^20 fixed-rule candidate
(now archived in [`archive/u20/`](../archive/u20/)); last updated 2026-10-01.

- Code: [`gacsca/`](../gacsca/)
- Tests: [`tests/`](../tests/)
- Drivers: [`experiments/`](../experiments/)
- Receipts (git-ignored, kept locally): `figs/`
- Current status and next steps: [STATUS.md](STATUS.md)
- Independent audits: [audits/](audits/)
- Overview and how to run things: [docs/](../docs/)

## Summary

*Updated 2026-10-01.*

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

G9–G15 keep all of G8's Gray mechanisms; G15 adds the two-time wipe schedule. QU
relative to G8: G9 2.6× smaller, G12 9.6×, G13 16.7×, G14 18.9×,
G15 18.4×.

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
  - With the colony margin (G7+), a burst on a colony boundary can damage
    at most one colony.
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
- **Unit tests:** 47 in `test_front_candidate.py`, one of which (a slow
  G8 GPU test) runs only on request.

**Not established.**
- A noise threshold (Gray's bound ε < (QU)^-2 is out of reach).
- Level-3 errors (three or more adjacent level-2 colonies damaged), and
  several level-2 errors close together.
- A full physical level-2 step: it would take weeks on the GPU (§26.1).
  Level-2 steps are checked on the level-1 automaton and physically across
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

**Next.** The compiler, not the machine, is now the limit. With unlimited
registers the same program needs 77 passes on one front and 22 on four, but
the in-order scheduler needs about 500 and about 200 (§23). A scheduler that
keeps registers for values needed near the front's current position would
be the next large gain.

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
