# Bit-level "front" successors to the Q=8192, U=2^20 fixed-rule candidate

2026-09-29, design-optimization agent.

- Code: `gacsca/fixed_rule/design_optimization/`
- Tests: `tests/fixed_rule/design_optimization/`
- Drivers: `experiments/fixed_rule/design_optimization/`
- Receipts (ignored): `figs/fixed_rule/design_optimization/`
- Coordination: [STATUS.md](STATUS.md)

## Summary

*Updated 2026-09-30.*

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
| current U20 | 8192 | 2^20 | 128 | 2^33 | 6,465 | 14,830 word ops | reference; upper static words host-supplied |
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
| G13 | 512 | 125,856 | 246 | 2^25.94 | 262 | 16,981 | **comb of five fronts**, each with its own program and register file (§23) |
| **G14** | **512** | **110,880** | **217** | **2^25.76** | 262 | 16,966 | G13 re-sized by a seeded schedule search (§23) |

G9–G14 keep all of G8's Gray mechanisms. They reduce QU by 2^4.2 ≈ 19×
relative to G8.

**What is tested:**
- **Self-simulation.**
  - One-level closure for every candidate.
  - R1 two-level rings: all level-1 steps exact, and every level-2 step
    tested exact (n2 = 1 twice; n2 = 2 and n2 = 3 once each).
  - An R1 three-level vertical slice: 24 consecutive level-1 steps exact.
- **Backends.** NumPy reference, C (scalar and AVX2) and CUDA (`gpu.py`,
  block and grid modes) agree bit for bit on arbitrary states.
- **Level-0 errors** (whole-state randomization, the densest pattern
  Gray's definition allows): every error in G5 and later is gone after one
  tick, and the decoded upper state stays exact (§§13–14).
- **Level-1 errors** (200×200 bursts at 16 phases × 3 placements, random
  bursts, partial-density bursts, linked pairs of level-0 errors), on
  two-level rings whose upper colony is healthy and at several stages of
  its own work period (§19):
  - **662 errors on G8, G11 and G12, every one contained** (never more
    than one upper cell wrong at any step; 494 of the 668 rings, reruns
    included, never changed the upper state at all) **and repaired** by the
    upper level within one upper step. Later batches add G10 (64), G11
    (14 in full colonies) and G13 (256): all contained, repaired and
    bit-identical (§§19, 23).
  - 653 of the first 662 ended bit-identical to the fault-free ring. The other 9 are G8
    commit-time bursts: the 6 rerun for longer were identical one step
    later (dead data flushed by the next commit), and the 3 in G8's
    pre-commit batch were not rerun.
  - With the colony margin (G7+), a burst on a colony boundary can damage
    at most one colony.
- **Colony-scale errors** (one or two colonies wiped) are also removed by
  the upper level within one upper step (G6/G8 full two-level rings, §15).
- **Unit tests:** 37 (`test_front_candidate.py`), plus 1 opt-in slow GPU
  test.

**Not established.**
- A noise threshold (Gray's bound ε < (QU)^-2 is out of reach).
- Level-k errors beyond colony scale.
- A G-family level-2 macrostep (U² ticks).
- Self-organization from arbitrary configurations.

**Several fronts (§23).** A comb of five fronts, five cells apart, runs
the program about 2.2× faster than one front. G14 (U = 110,880,
U/Q = 217) is the result; it closes on the GPU and G13's level-1 batches are
clean.

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
   (`run_dual_capture20_events.py:62-73`, `gpu_validation/initial.py:71`).
   A physical fetch of 390 words is itself a large routing problem.
3. **Scale.** Two levels need Q²·U² = 2^66 site-ticks per level-2 step. A
   bit-packed Q² state is 50.5 GiB per buffer.

My full audit is in the root prompt `FIXED_RULE_U20_REPAIR_PROMPT.md`. It
includes the WordCode ≠ literal-F hop-count defect found by the GPU agent,
since confirmed and patched by the u20_repair agent.

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
skews), not on Pi's contents; Pi is the compiled program. Loading a cached
candidate fails if the netlist digest changed. `build_candidates.py` rebuilds
every candidate from its recipe bit-identically (`receipts/candidates.json`).

**Backends (`machine.py`).**
- A NumPy reference with a full Pi lookup at every site.
- A generated bit-sliced C kernel (scalar, and AVX2 via GCC vectors). It
  looks Pi up only where `arrive` is set and runs in one persistent OpenMP
  region.
- A batched CUDA simulator (`gpu.py`, §12) generated from the same
  netlist, bit-exact against the C kernel. (The earlier single-block
  `cuda_backend.py` is superseded.)

## 3. Measured costs

Measured on an AMD EPYC 7543 (Zen 3, AVX2) with pinned cores.

| | current U20 | R1 | G3 | G5 |
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
- **R0, G1, G2, G4:** full numbers are in `receipts/candidates.json`.

## 4. Tests

`OPENBLAS_NUM_THREADS=1 python -m unittest -q
tests.fixed_rule.design_optimization.test_front_candidate` runs 33 tests, all
OK in about 40 s. Four of them need a CUDA GPU and are skipped without one.
A slow G8 GPU closure test runs with `GACSCA_SLOW=1` (about 3 minutes). The
suite would fail if:

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
- **A margin leaked** (G7–G12). Represented SimBits or any instruction slot
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

`spacetime.py` writes PNGs to `figs/fixed_rule/design_optimization/spacetime/`
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
`figs/fixed_rule/design_optimization/error_levels/*.json`.

| pattern | R1 (64×64 boxes) | G5 | G6 |
|---|---|---|---|
| E0 dense, 4 periods | all 8 upper cells wrong | **exact; physical state = reference at each boundary** | **exact; = reference** |
| E0 for 2 periods, then off | wrong (no redundancy) | exact | exact |
| E1 mid-colony, after gather 1 | 1 cell wrong, closure exact afterwards | 1 cell wrong in the period of the burst | same as G5 |
| E1 across a colony boundary | 1 cell | 1–2 adjacent cells | 1–2 adjacent cells |
| E1 during gather 1 or just before gather 2 | 1 cell | all 8 cells wrong in that period, closure exact afterwards | same |
| colony wipe(s) | 1–2 cells | 1–2 cells | 1–2 cells |

- **Level-0 errors vanish completely in G5/G6.** Every error is repaired in
  one tick, and the decoded upper state and the whole physical state equal
  the fault-free ones.
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
    boundary once the noise stops, and between fresh errors while it runs.
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

## 19. Level-1 campaign (G8, G11, G12)

`level1_campaign.py` runs two-level rings on the GPU.
- **Upper colony:** one healthy colony encoding a random top cell,
  optionally advanced with the rule into any stage of its own work period.
- **Physical ring:** encodes either the whole upper colony (Q² sites) or a
  64-upper-cell slice centred on the target cell.
  - A slice's ends meet at an Address jump. The script checks that its
    influence stays at least 23 upper cells away from the target over all
    tested steps, so the target behaves as in a full colony.
- **Errors:** every ring except the reference gets one level-1 error, a
  200×200 box in which every site's whole state is randomized at every
  tick, during upper step 1.
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
  - *repaired*: no upper cell is wrong from the next upper step on;
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
| G13 | b34 | its own gathers (+ E0 ring), after the fix | 64 | 64 | 64 | 64 |

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
(`G8_b2_commit_5steps.json`).

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
- **Level-1 campaign on G13** (§19): 256 bursts at 16 phases × 3
  placements, plus random bursts, on two-level slice rings with the upper
  colony in its gathers, in phase A with its front hit, and in its final
  program with its front hit.
  - All 256 were contained and repaired, and ended bit-identical.
  - The reference ring was exact at every step.
  - 192 of these ran before the match-gate fix. Batches b35 and b36 (after
    the fix) are still running.
