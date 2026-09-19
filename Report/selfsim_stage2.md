# Stage 2: colonies of colonies — level-1 cells running the full rule (finite tower)

## What was built
`gacsca/interp.py` (NumPy semantics + compiler) and `gacsca/cuda/interp.cuh` (CUDA, bit-identical)
add an **interpretation phase** to the level-0 work period. After Tr_local has computed the new
local fields of the simulated level-1 cell, the colony computes the new *simulation-structure
tracks* of that cell — and of its two neighbours, for the copies it must hold — by executing the
level-1 op table (`prog_up`) at the level-1 age and address held in two integer registers of every
level-0 cell (`simage`, `simaddr`; colony-local majority repair, suspended during the load window).

Mechanism (per period, 1505 level-0 steps for Q₀=256, D=3):
1. For each neighbour offset o = −4..4: rebuild the repaired level-1 tracks of cell o from the
   ARG tracks (`VT = MAJ3(shift(ARG_{o+1},+1), ARG_o, shift(ARG_{o−1},−1))`), then move `VT` along a
   bus track in both directions (D cells/step). Every level-0 cell knows which level-1 bit it is the
   writer for (track t, copy slot r ⇒ simulated cell c = r−h) and latches, at the computed pass
   step, exactly the bits that the active level-1 op needs from offset o (sources, token/carry of
   the sweep hypotheses k = 1..D, broadcast candidates, shift sources, Info bits for the
   Workspace-flag rules). Carry chains through intermediate cells are advanced after each pass.
2. `IEVAL` (one step per op slot): writer cells compute the op result (CONST/MOV/BITOP/SHIFT/
   RSHIFT/SWEEP_INIT/SWEEP/BCAST_INIT/BCAST/BUSLATCH_INT) and write `Hold`.
3. Level-1 holder-side wipes (Mailbox if F1*, everything if F1* and address change),
   level-1 Workspace flags (`IWF`), then a bus pass loads the level-0 registers from the new
   level-1 AGE/ADDR fields (`BUSLATCH_INT`), and `Info := Hold` at age U−1.

The **tower**: level 0 (Q₀=256, U₀=16384, K₁=220 bits, program 10 894 steps) simulates level-1
cells (Q₁=64, U₁=4096, program 3550 steps, no interpretation phase) that simulate local-only
level-2 cells (Q₂=16, U₂=2048, K₂=21 bits). Each level is a finite CA; each simulates the next
exactly. Track registries are identical at all levels; the levels differ in (Q, U) and in whether
they carry an interpretation phase.

## Verification
| test | result |
|---|---|
| `tests/test_interp.py` — interpreted Hold tracks (3 simulated cells) vs `apply_ops` of the level-1 rule on a level-1 ring, 15 level-1 ages covering every op kind, 3 address settings | pass |
| `tests/test_gpu_engine.py::test_gpu_tower_matches_numpy` — CUDA vs NumPy over the whole interpretation phase on random states | pass (bit-identical) |
| `experiments/tower_acid.py` — decoded level-1 trajectory (all 220 bits: local fields, registers, 61×3 track copies) vs the direct level-1 engine, 4 periods from 7 starting ages (period start, gather 2, compute start/mid, signalling, trickle, update) | **ALL OK** |
| `experiments/tower_full_period.py` — one complete level-1 work period (4096 level-0 periods = 6.7×10⁷ level-0 steps, 69 checkpoints of all 220 bits × 64 cells), decoded level-2 transition vs the level-2 rule | **OK**: every checkpoint matches; level-2 state (5, 778, 1, 1) identical via level-0 decode, direct level-1 engine, and the level-2 rule (53 min on the A100) |

Two bugs found by the acid test are worth recording: (1) integer registers repaired by the plain
5-voter majority *leak across colony boundaries* (the last cells of a colony vote from the right,
i.e. entirely inside the next colony) — the Address field does not leak only because its votes are
position-adjusted; fixed with a colony-local rule (voters restricted to R∩C / L∩C, fallback to the
other side, else keep). (2) A temp-track lifetime error made a broadcast reuse the track holding the
latched Info bit for the Workspace-flag rule.

A third bug was found by an independent code review after the acid tests had passed: the
interpreter truncated the level-1 op list to three ops per age, while gathers run four concurrent
ops (two stream shifts + two receives), so the left-neighbour receive was silently dropped. It was
invisible because the level-2 test states encoded to all-zero Info bits. Fixed (per-resource-class
latch slots, up to four ops per age, compile-time assertion); the unit and acid tests now use
nonzero level-2 states and include the receive ages. The same review found a nearest-neighbour
priority inversion for rightward broadcasts (fixed) and fragile temp-track lifetimes (documented).

The first full-length run (one complete level-1 work period with nonzero level-2 states) exposed two
more defects that the phase-wise acid test could not see because its initial states never carried the
F1*/F2* signal bit: Tr_local still had Gray's Flag conditions (iii)/(iv) (Workspace.Flag1/2 of the
neighbours) hard-wired to 0 from stage 1, so level-2→level-1 trickle-down never raised the level-1
Flag1; and the interpreted "wipe everything on Flag1 + address change" used the equality bit
inverted. Both fixed; the acid test now includes a signalled-trickle case (all 8 phases OK) and the
Tr_local spec test uses random workspace flags. The decoded level-2 transition after a full level-1
period matched the level-2 rule even in the defective run (the level-2 fields are computed before
the defects act), i.e. the colonies-of-colonies computation itself was already correct.

## The self-reference boundary (why the tower and not a single uniform rule)
Interpreting a level-1 op requires knowing *which* op is active, i.e. a table lookup keyed by the
level-1 age. Here that lookup is a primitive of the cell (the table is part of the transition
function; the key is the `simage` register). If level-1 cells themselves ran an interpretation
phase (a depth-3 tower, or a uniform rule), the level-0 colony would have to reproduce *their*
lookup, keyed by the level-2 age — one more integer register per nesting depth. A uniform rule
would therefore need unboundedly many registers. Gács avoids this because in his construction the
program counter is *data* on the `Cpt` track processed by a universal medium interpreting `My-rules`
(Secs 9.2–9.3), at the price of an interpreter cost ∝ (|program|+1)² per simulated step that makes
explicit multi-level runs infeasible. The finite tower is the executable compromise: depth d needs
d−1 register pairs (22 bits each), is a single well-defined CA rule at each level, and reproduces
every mechanism of the hierarchy (colonies encoding cells, work periods, mailboxes, computation,
encoding/decoding, redundancy repair, trickle-down) at every level.

## Depth-2 noise (`experiments/depth2_noise.py`)
Level-1 error rate per cell-period (a level-1 cell is wrong if *any* of its 220 decoded bits differs
from the direct level-1 engine's one-step prediction), 64 level-1 cells, 8 periods:

| ε | 1e-5 | 3e-5 | 1e-4 | 3e-4 |
|---|---|---|---|---|
| ε₁ (full level-1 rule, 220 bits) | 0 (of 512) | 0 (of 512) | 0.034 | 0.17 |
| ε₁ (stage 1, 28-bit level-1 cells) | 4e-4 | 1.2e-3 | 4.9e-3 | 3.2e-2 |

The usable regime of the simulation structure is ε ≲ 10⁻⁴ (≈ 400 hits per colony per period).

## Cost (measured)
One level-1 step = U₀ = 16384 level-0 steps; 64 colonies (16 384 cells) run at ≈1 s per level-1
step on the A100. One level-2 step = U₀·U₁ = 6.7×10⁷ level-0 steps ≈ 70 min for 64 colonies
(one level-2 cell), ≈ 2–9 h for a 1024-colony ring (16 level-2 cells, a level-2 ground state).

## Depth-2 island (running; `experiments/depth2_island.py`)
A misaligned *level-1* island (two full level-1 colonies = 128 level-0 colonies, shifted by 20
colonies) inside a 1024-colony ring (16 level-2 cells = one level-2 colony); level-0 structure intact.
- Before the first level-2 trickle window the island grows at the level-1 rules alone from 131 to 172
  level-1 cells (its right end invades the level-1 cells whose level-1 L∩C contains it) and then stays
  constant: the level-1 layer alone cannot remove it (the level-1 analogue of the level-0 fixed point).
- Each level-2 trickle window (once per level-2 step = 4096 level-0 periods ≈ 3.3 h) erodes it from
  the left by 128–190 level-1 cells and its right end advances by the same amount: [148,319] →
  [276,511] → [466,701]. The right end crossed the level-2 *cell* boundary at 512 because the level-2
  cells beyond it have a level-2 inconsistency (their level-2 L∩C contains the damaged level-2 cells)
  and receive level-2 Flag1 — the same glider mechanism observed one level down. It can only be
  stopped by a level-2 *colony* boundary (level-1 cell 1024 ≡ 0 on this ring), i.e. by the next level
  of organisation, exactly as Gray's argument requires (p. 38–40).
- Level-0 damage stays 0 throughout: level-2→level-1→level-0 trickle-down acts only through the
  Flags and never corrupts the level-0 local structure.
Follow-up: place the island immediately left of the level-2 colony boundary to observe its erosion
within two level-2 steps.
