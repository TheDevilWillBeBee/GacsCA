# GacsCA: executable Gács/Gray noise-robust cellular automaton — project report

Last updated: 2026-09-18 (evening). Sub-reports: [design_selfsim.md](design_selfsim.md),
[discrepancies.md](discrepancies.md), [level0.md](level0.md), [selfsim_stage1.md](selfsim_stage1.md),
[selfsim_stage2.md](selfsim_stage2.md).

## 0. Goal and status in one paragraph
Build, verify and experimentally study an executable version of Gács' one-dimensional
fault-tolerant cellular automaton in Gray's simplified presentation, up to finite-depth
hierarchical self-simulation. **Status:** the level-0 automaton (Gray Sec 5.2: Address/Age/Flags
majority repair, the part Masumori et al. implemented) is implemented three ways (literal scalar
spec, vectorized NumPy, CUDA/nanobind), cross-tested, and characterised on the GPU. The
self-simulation machinery is designed ([design_selfsim.md](design_selfsim.md)) and **stage 1 is
implemented and verified** ([selfsim_stage1.md](selfsim_stage1.md)): colonies of 256 cells
simulate level-1 cells (local structure) through timed mail streams, a bit-serial microprogram
computing the level-1 transition, and trickle-down; the decoded level-1 trajectory equals the
direct one; CUDA engine ≈2×10⁹ cell-updates/s. **Stage 2 is implemented and verified**
([selfsim_stage2.md](selfsim_stage2.md)): a three-level finite tower in which level-0 colonies
interpret the level-1 op table, so level-1 cells run the complete rule (tracks, mail streams,
bit-serial computation of the level-2 transition, trickle-down, update) and simulate level-2
cells; the decoded level-1 trajectory equals the direct level-1 engine in every phase. Hierarchy
experiments: the induced level-1 error rate scales as ≈QUε² (adjacent-pair channel); a
misaligned-colony island that level-0 rules cannot erode becomes a glider under trickle-down and
is eliminated at the next level-2 boundary (healed at period 80 on a 512-colony ring).

## 1. Sources and how they relate
- Gács 2001 (J. Stat. Phys. 103) — the full construction: media, block codes, amplifiers, robust
  media, a rule language, and the program (Secs 12–20). Nearest-neighbour, variable cell kinds.
- Gray 2001 — Reader's Guide: a simplified range-5 model with fields Address, Age, Flags,
  SimBit(5), Workspace, Mailbox; Q colony size, U = 128Q; Props 1–5.
- Masumori, Sinapayen, Ikegami 2024 — Java implementation of Gray's local structure only
  (no self-simulation), Q = 271, recovery vs error rate.

## 2. Model (level 0) — implemented
Ring of L = ncol·Q cells, neighbourhood N(x) = {x−5..x+5}. Fields: Address ∈ [0,Q),
Age ∈ [0,U), Flag1, Flag2 (+ Workspace.Flag1/2 read from the simulation structure).
Apparent colony C(x): the position v of x such that ≥3 of the five sites x+i (i=1..5) satisfy
(Address(x+i) − i) mod Q = v. Inconsistency (i)–(iv), Flag1 and Flag2 rules, and the Address/Age
majority votes are transcribed literally in `gacsca/level0_spec.py` (Gray pp. 20–22). Ambiguities
and Masumori's modifications are catalogued in [discrepancies.md](discrepancies.md); the main
finding is that two of Masumori's three "errors in Gray" are not errors (D2, D4).

Noise: each cell independently with probability ε per step is replaced by a uniformly random
state (Address uniform in [0,Q), Age in [0,U), flags uniform) — Gray's ε-perturbation with a
strictly positive ν.

Code: `gacsca/level0_np.py` (NumPy, batch×L), `gacsca/cuda/gacs_cuda.cu` (CUDA, one thread per
cell, hash-based reproducible noise), `gacsca/gpu.py` (torch front-end). Tests: `tests/`
(spec ≡ NumPy ≡ CUDA on random and near-ground configurations; noise statistics).

## 3. Level-0 results (details in [level0.md](level0.md))
- Qualitative reproduction of Masumori Fig. 7A: leftward Flag1 waves confined to colonies; after
  the noise stops, Flag1 clears in a wave from the right end at speed ≈ 2.7 (Gray: ≥ 1.75).
- Recovery threshold (500 noisy steps then 500 clean, Q=271, 4 colonies, 256 trials/point):
  P(Address fully recovered) = 1.00 up to ε = 0.34, 0.92 at 0.38, 0.27 at 0.40, ≈0 at ≥ 0.42.
  Masumori report failure only above ≈0.55–0.6; their noise protocol differs (D7). A corrected
  mean-field recursion c' = (1−ε)[c + (1−c)g(c)], g(c) = P(Bin(5,c) ≥ 3), gives ε_c = 0.334;
  spatial correlation (colony structure) pushes the real threshold up to ≈0.40.
- Q dependence: smaller colonies are less robust (Q=32: threshold ≈0.33; Q ≥ 271: ≈0.40).
  Larger systems fail slightly earlier (more colonies, more chances for one to fail).
- The Masumori rule variant (Flag1 (ii) counting all of R(x)) is slightly less robust.

![level-0 recovery](../figs/level0_recovery.png)

## 4. Self-simulation design (summary; full text in design_selfsim.md)
Uniform rule; simulated state laid out one bit per cell on the Info track; R-fold redundant
tracks; two timed mail streams retrieve all 10 neighbour colonies (sample MailL at t0+jQ);
three gathering stages with majority; an Age-scheduled microprogram (compiled from a Python
DSL into an op table) computes the simulated transition bit-serially; the same table is used to
interpret the simulated cell's own microstep (self-reference without an interpreter string).
Cost model: level-2 dynamics reachable for O(10–100) steps; level 3 static only.

## 5. Stage-1 results (summary; details in selfsim_stage1.md)
- Block simulation verified (decoded == direct). Work period 8010 steps (U = 8192), K = 210 bits.
- ε₁ ≈ c·QU·ε² (c ≲ 1): the simulation structure survives iid noise only for ε ≲ 3×10⁻⁴; the
  level-0 local structure survives up to 0.40. The hierarchy's benefit is against organised
  islands, which must be injected.
- Misaligned-colony island: fixed point for level-0 rules; with trickle-down it becomes a glider
  (erodes 3 colonies/period on the left, invades 3 on the right) until a level-2 boundary.

## 6. Stage-2 results (summary; details in selfsim_stage2.md)
- Tower: level 0 (Q=256, U=16384) → level 1 (Q=64, U=4096, full rule) → level 2 (Q=16, local-only).
- Interpretation phase: 1505 level-0 steps per period; `tower_acid.py` ALL OK on 7 phases × 4 periods.
- Self-reference boundary documented: a uniform rule needs one integer register pair per nesting
  depth; Gács's data-driven interpreter avoids it at a cost that forbids explicit multi-level runs.
- Cost: one level-2 step ≈ 6.7×10⁷ level-0 steps (≈1 h for one level-2 cell, hours for a ring).
- Injected islands: 1 misaligned colony heals at level 0; 2–3 misaligned colonies are level-0
  fixed points and heal at depth 1 (period 80); time-misaligned islands heal at depth 1 in 2
  periods; random bursts (up to 2000 cells × 500 steps) heal at level 0 within 3 periods.

## 7. Next concrete steps
1. Finish the full level-1 work period run (`tower_full_period.py`): decoded level-2 transition.
2. Depth-2 noise characterisation: level-1 error rate when level-1 cells carry tracks.
3. Depth-2 island experiment: a misaligned level-1 island (128 misaligned level-0 colonies) inside
   a 16-level-2-cell ring — repaired by level-2 trickle-down (overnight run).
4. Depth 3 (nested interpretation with a second register pair) if time permits.
5. Gray's Flag2 right-end reversal; lifetime vs ε at moderate noise for depth 0/1.
