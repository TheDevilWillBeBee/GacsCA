# Towards Gács's version: stored program, amplifiers and error-correcting codes

A feasibility study, written 2026-10-02 by a separate agent that had read access to the repository at G15
(commit 722ab2c) and worked on a private copy. It answers two questions from the project owner: can the
construction move towards Gács's own version (a stored, self-reproducing program and error-correcting codes
in place of fivefold majority), and would that lower Q or U?

**Read this first.**
- Every number for "G15" and for the three-copy variant below was measured with the compiler G15 used.
  G16 (REPORT §29) has since cut the work period to 25,920 with a new compiler and no change of redundancy;
  the study's remark that the compiler is the larger lever (A2 in §9) is what G16 did.
- The three-copy variant recompiled with G16's scheduler is reported in REPORT §29 ("Options not taken").
- `exp/` in the text is [`gacs_route_exp/`](gacs_route_exp/): the agent's scripts, logs and receipts. They ran
  against a patched private copy of `gacsca/` at G15 (`patch3.py` is the patch); the compiled candidates
  (`cand_*.npz`) and that copy are not kept.
- Its own list of unverified claims is §10.

**Legend.** `[S]` read from a source, with section and page. `[M]` measured from the repository code, or from a
patched copy of it in `exp/`. `[E]` my estimate or inference; error bars are stated where I can give them.

**Which Gács paper.** `papers/Reliable Cellular Automata with Self-Organization.pdf` is the author's printing dated
24 January 2024, "a corrected and strengthened version of the journal article" (abstract, p. 1). Its sections are
numbered differently from the 2001 journal version that Gray cites. By content, Gray's "Sections 7.3 and 7.4"
(the programming language) are §§9.1–9.3 here, Gray's "first part of Section 9" (parameters) is §11, and Gray's
"Lemma 8.4" is Lemma 10.5. All Gács citations below are to the 2024 printing (section, page). Gray's page numbers
are the article's own (1–44). Gács's 1986 paper is not in `papers/`; everything said about it is second-hand.

---

## 0. Verdict in one page

1. **Gács 2001 does not use a stored program.** It hard-wires the program into the rule, as Gray does, because
   in Gács's words "the written program is exposed to errors" (§9.2, p. 82; §5.5, pp. 51–52). What Gács has and the
   repository lacks is an *interpreter* (a universal automaton on a work track that executes a rule-language
   text which every cell can recite), level-dependent parameters, and the self-organizing "robust medium".
   None of these is needed for a fixed rule that simulates itself reliably, and each would raise Q·U by orders
   of magnitude at our sizes (§6, §7).
2. **Gács's error-correcting code and Gray's fivefold storage are not two implementations of one thing.** They
   sit at different scales and assume different error models.
   - Gács: a Reed–Solomon code along the colony, refreshed once per work period, with the computation run three
     times and voted. It corrects one burst of at most 5 cells per window of about 5 colonies × 5 periods.
   - Gray: five copies on five adjacent cells, re-voted every tick. It corrects a 1–2-cell error in every
     24 × 24 space-time box.
   - Replacing the per-tick redundancy by a colony-level code would end the repository's measured property that
     level-0 errors vanish in one tick. It would also make U larger, not smaller: my estimate is 2–5× (§5.4).
3. **The useful coding idea is a better per-tick code.** Three copies on cells two apart (x−2, x, x+2) correct
   every Gray level-0 error, because two adjacent sites never hold two copies of the same bit. This is a
   2-interleaved repetition code; it meets the Reiger bound for 2-cell bursts and is, by my argument, the best
   rate reachable at radius 5 (§5.1).
4. **Measured on a patched copy of the code** (§5.2): K 260 → 193 bits per cell, gates 17,100 → 9,988,
   Q 512 → 448, U 112,608 → 73,024, QU 2^25.78 → 2^24.96 (1.76× smaller).
   - The candidate closes over two periods and removed 8,000 of 8,000 injected level-0 errors in one tick.
   - In a small level-1 probe, 13 of 13 dense 100 × 100 bursts left at most one upper cell wrong for one upper
     step, and the ring was bit-identical to the error-free one by the second boundary.
   - It has **not** been through the full level-1 campaign, the per-tick Proposition 4 check, the margin and
     front tests, the GPU backend or the three-level checks.
   - The price is code distance 3 instead of 5. Two single-site errors 2 or 4 cells apart at the same tick are
     no longer corrected: 2,000 of 2,000 such pairs survived a tick. Gray's level-0 class does not contain such
     pairs, so his argument is unaffected, but the tolerable i.i.d. noise rate drops by my estimate about 25×.
5. **Coding cannot shrink Q below 448 (three copies) or 384 (no redundancy at all).** The two margins take 244
   of the 512 cells, and they come from Gray's burst width of 200, not from the storage code (§2).

Ranked recommendations are in §9, and the claims I could not verify in §10.

---

## 1. What the three papers are

| | Gács 1986 (second-hand) | Gács 2001 (2024 printing) | Gray 2001 | Masumori et al. 2024 |
|---|---|---|---|---|
| What it is | First 1-D reliable CA; discrete time; hierarchical initial configuration | Full construction, 228 pages: asynchronous, self-organizing, positive capacity | "A simplified version" of Gács's model (p. 13), about 30 pages of mechanism | A simulation of Gray's automaton |
| Implemented? | no | no | this repository (G15) | local structure only: "we report preliminary results without implementing the self-simulation part", Q = 271, 293 bits per cell |

Masumori et al. also list defects in Gray's printed rules (appendix: the Address adjustment, a circular definition
between Age and Flag2, and the Workspace.Flag rule reading a site out of range). As far as these sources show,
nobody has implemented Gács's codes, interpreter or amplifier.

---

## 2. Where G15's Q, U and bits go `[M]`

Numbers from `exp/baseline.py` and `exp/g15_base.py`, run on a copy of `gacsca/` taken with `git archive HEAD`.
The copy rebuilds G15 to the digests in `gacsca/manifest.json`.

**Bits per cell, K = 260.**

| part | fields | bits | share |
|---|---|---:|---:|
| local structure, one copy, protected by Gray §5.2 votes | addr 9, age 18, f1, f2, wf1, wf2 | 31 | 12% |
| fivefold simulation structure: 33 logical bits × 5 | info 1, hold 1, mr 1, ml 1, h1 10, h2 10, scr 4, pend 1, pkind 3, pval 1 | 165 | 63% |
| compact front register slot (one of five spatial copies) | reg 64 | 64 | 25% |

- The four extra copies are 132 of the 260 bits.
- With no storage redundancy at all, K would be 31 + 33 + 64 = 128.

**Colony, Q = 512.**

| part | cells | share |
|---|---:|---:|
| two margins of 122 | 244 | 47.7% |
| working area W = [122, 390) | 268 | 52.3% |

- The working area holds one upper bit per cell: 260 bits, plus the two reserved courier cells.
- How an upper bit is represented `[M: codec.py, rule_g.info_copies]`: upper bit b is the logical Info bit of
  one working cell `layout[b]`, stored as five copies on cells `layout[b]−2 … layout[b]+2`. There is **no
  redundancy across the colony**. A burst three cells wide can outvote an upper bit.
- The rule for Q `[M: rule_g.check, compiler.default_layout]`: W ≥ K + 2, W + H a multiple of 16 (H = 20 is the
  comb's overhang), Q a multiple of 64, and margin ≥ 122 from the exposure bound 2·margin − 2H − 3 ≥ 200.
  That gives the staircase below.

| K at most | W | Q |
|---:|---:|---:|
| 266 | 268 | 512 |
| 202 | 204 | 448 |
| 138 | 140 | 384 |

- So removing *all* redundancy (K = 128) would reach Q = 384 and no lower. The margins are a floor of 244 cells.
- The margin is the repository's reading of Gray p. 33 ("Q ≥ 2K … SimBits … placed so as not to be near the
  colony boundaries"). Its size comes from Gray's level-1 burst width of 200 (p. 19), and from the repository's
  stricter aim that a boundary burst reaches the data of one colony only. Gray's Proposition 4 allows two
  (REPORT §16).

**Work period, U = 112,608 = 391 blocks of 288 ticks.**

| part | blocks | ticks | share |
|---|---:|---:|---:|
| three gathers (Ages 0, 12Q, 24Q) up to E0 | 57 | 16,416 | 14.6% |
| evaluation: early 26, phase A 73, match 1, final 233 passes | 333 | 95,904 | 85.2% |
| last block, with the commit at Age U−1 | 1 | 288 | 0.3% |

**Rule netlist, 17,100 gates.** The 616 five-way majorities take 7,392 gates (12 each), which is 43% of the
netlist. The colony must evaluate all of them on itself.

**Program.** 32,835 instructions of 24 bits: 788 kbit. The table Pi has 512 × 4,096 entries (50.3 Mbit), of which
32,835 are non-zero. The colony's entire state is Q·K = 133 kbit, so the program is 5.9 times larger than
everything the colony can store.

---

## 3. Inventory of differences

"Needed" means needed for this project's goal: one fixed rule, reliable hierarchical self-simulation, a good
initial configuration.

| # | Feature | Gács 2001 `[S]` | Gray `[S]` | Repository `[M]` | Needed? |
|---|---|---|---|---|---|
| 1 | Neighbourhood | nearest neighbour (Gray p. 14) | radius 5 (p. 14) | radius 5 | — |
| 2 | Time | continuous, variable period (§1.3 p. 7; §7.4; §8) | discrete (p. 2) | discrete | no |
| 3 | Code on the represented state | Reed–Solomon over GF(2^l), 2t check symbols for t symbol errors (Ex. 5.15, pp. 47–49; §19.1, p. 178) | none; a 5-bit SimBit field per cell (p. 15, p. 33) | none; one upper bit per working cell | no (§5) |
| 4 | Protection between upper steps | none per step for information; "locally maintained" constant tracks and structure are repaired at once (§13.1, p. 121) | fivefold copies voted every tick (p. 33) | same, extended to the front | yes, in some form |
| 5 | Protection of the computation | decode → compute → encode three times, majority into Hold (Alg. 19.7, p. 189; §12.4, p. 120) | three gathers and a vote, every step done fivefold (p. 34) | three gathers; fivefold front | yes, in some form |
| 6 | Hold, then commit | Hold track, `Finish` at Age U−1 (Alg. 19.12, p. 193) | "distributed … into the Workspace", SimBits updated at the next period (p. 34) | Hold, commit at U−1 | present |
| 7 | Program | hard-wired text `My-rules`, written to a track and interpreted by a universal automaton `Univ` each period (Def. 9.14, p. 88; Alg. 9.7, p. 95; Alg. 19.5, p. 188) | ProgramBit as a function of Address, projected out (pp. 31–32) | Pi[Address][page], compiled straight-line program, one physical fetch | present (§6) |
| 8 | Parameters | `Param_i` strings; level `Height` and `Frame`; "uniform program" (Def. 11.5, p. 108; §19.3, p. 186) | constants of size a·log(QU) (p. 31) | constants in the netlist | no |
| 9 | Level-dependent sizes | Q_k = R^(k+1), U'_k = R·Q_k/w_k, w_k = 1/(R·k²) (11.9, p. 110) | fixed Q ≥ 2^13, U = 128Q (p. 15) | fixed Q, U | no (§7) |
| 10 | Capacity | one bit per site: aggregated Payload, packets (§5.4; §19.1, pp. 179–180) | log₂Q bits in total (p. 16) | not attempted | no |
| 11 | Error bookkeeping | damage, islands, robust medium (Def. 10.3, p. 97; Lemma 10.5, p. 99) | explicit level-n errors (pp. 16–19) | Gray's classes (`gray_errors.py`) | — |
| 12 | Structure repair | kill, create, heal, decay, purge; cell "kinds" and strengths (§12.1, §14, §15) | Flag1/Flag2, directional votes (§5.2); Flags "a simplified version of the Kind field" (p. 15) | Gray's | Gray's suffices |
| 13 | Misaligned colonies | communicate through channel arms (§18, p. 171) | cannot communicate, "the way it was done in Gács's 1986 version" (p. 37) | Gray's | no |
| 14 | Self-organization | germs, colours, birth, lifting (§21; §19.4) | none | none | no |
| 15 | Trickle-down | of the payload, and of structure by regrowth | of Flag1/Flag2 (§5.5) | Gray's | present |
| 16 | Randomness | a coin per cell, for symmetry breaking (§20.3, p. 203) | none | none | no |

**What Gray says he changed.** "I will describe a simplified version of Gacs's model. In many of the details, my
version will not agree with his version," because he does not prove all of Gács's results and because some things
are easier to present another way (pp. 13–14). The explicit points are rows 1, 2, 10, 11, 12, 13 and 14 above
(pp. 2, 11–12, 14, 15, 16, 19, 37). He does *not* say that fivefold storage replaces Gács's code; he simply
introduces it (p. 33). That reading is mine.

**Gács 1986, as reported.**
- The initial configuration had an infinite hierarchy, so it was not self-organizing (Gács §3.1, p. 21).
- It communicated between adjacent neighbours only, and protected colonies by "growth in a zigzag pattern"
  (Remark 10.1, p. 97).
- Misaligned colonies did not communicate (Gray p. 37).
- Its result needed a decoding step, and its input encoding depended on the size of the computation
  (after Theorem 6.1, p. 59).
- I could not check what code or program mechanism the 1986 paper used.

---

## 4. Two redundancies, two error models

This is the centre of the question, so I state it carefully.

**Gács's ladder: one rung per level.** `[S]`
- The unit of noise at a level is an *island*: damage that fits in a box of 15 cell-widths × 15 dwell periods
  and is "too far" from all other damage, meaning no box of 5 colonies × 5 work periods contains both
  (Def. 10.3 with γ = 5, β = 15, pp. 97–98).
- An island directly affects at most Δ = 5 consecutive cells ((13.4), p. 125).
- The colony absorbs one island completely. A code symbol "stretches over Δ cells", so the island damages at
  most two symbols, "for which 4 error check symbols suffice" (Def. 19.1, p. 178).
- The computation is protected by repetition: "The time of the damage may fall into at most one of the three
  iterations" (§20.1, p. 196).
- **The upper cell is never wrong because of one island.**
- Two islands close together are, by definition, damage of the next level: ε_(k+1) = c·(Q_k·U'_k·ε_k)²
  ((11.8), p. 110; Lemma 10.5).
- Refresh happens once per work period: `Legalize(Util)` at the start of `Compute`, and `Refresh-payload` once
  in `Proc-payload` (Alg. 19.7, 19.8, 19.11, pp. 189–192).
- Between refreshes nothing corrects information bits. A second island in the same period defeats the code.

**Gray's ladder: two rungs per level.** `[S]`
- A level-0 error is one site, or two adjacent sites, at one tick, (24, 24)-separated from all other errors
  (p. 17). Fivefold storage removes it at the next tick (p. 33).
- A level-1 error is a cluster fitting in 200 × 200 (p. 19), (24Q, 24U)-separated from the others.
  - It can disturb one of the three gathers; the vote removes that (p. 35).
  - It can leave the damaged colonies' SimBits wrong at the next boundary: "in the level-1 simulation, this is
    treated just like a level-0 error in the original system" (pp. 35–36).
- **The upper cell may be wrong for one upper step.** The fivefold storage one level up repairs it.
- The recursion is the same: ε_n ≤ (QU·ε_(n−1))² (Proposition 1, p. 19).

**Consequences.**

| | Gács | Gray and the repository |
|---|---|---|
| Smallest fault a colony must absorb with no upper error | one burst of ≤ 5 cells (island ≤ 15 × 15) | none: fivefold absorbs 2-cell errors below the colony level |
| Largest fault a level handles | the same island | a 200 × 200 cluster, by letting the upper cell be wrong once |
| How often | one per about 5Q × 5U | level 0: one per 24 × 24. Level 1: one per 24Q × 24U |
| Redundancy of the represented state along the colony | Reed–Solomon check symbols, a fraction δ_k = R·w_k/Q_k (p. 109) | none |
| Redundancy per cell | none | 5× |
| Upper cell wrong after one "allowed" fault | never | possibly, for one upper step |

- The colony-level code is what lets Gács's cell carry no local copies and reach rate → 1 (Proposition 5.17,
  p. 50).
- The fivefold code is what lets Gray dispense with a colony-level code: an upper error is somebody else's
  level-0 error.
- Gray's level-1 burst (200 cells) is far beyond what any code inside a 268-cell working area could correct.
  Gács's burst (5 cells) is far below what the repository's campaigns inject. A colony-level code therefore
  cannot be added "on top" to make Gray's level-1 errors invisible upstairs.

---

## 5. Error-correcting codes instead of fivefold storage

### 5.1 The best per-tick code at radius 5 is three copies at stride 2 `[E]`

The per-tick code must correct what Gray's level-0 class contains: arbitrary corruption of one site or two
adjacent sites, at an unknown position.

- **Reiger bound.** A linear block code that corrects every burst of length b needs n − k ≥ 2b check symbols.
  Here a symbol is a cell and b = 2, so n − k ≥ 4.
- **Reach.** A holder must recompute its symbol every tick from corrected values of the logical cell and of
  that cell's two logical neighbours (mail shifts and the front moves one cell per tick). If everything that
  encodes logical cell x lies within a cells of x, the rule needs radius a + 1 + a. For fivefold storage that
  is 2 + 1 + 2 = 5, which is why "radius 5 is exactly enough" (REPORT §2). So at radius 5, a ≤ 2: each logical
  cell must be recoverable from the five cells around it.
- **Within those five cells,** two adjacent cells may be bad. Copies survive that only if no two of them are
  adjacent, and a majority needs three. The only such placement is {x−2, x, x+2}.
- **As a code.** Over two adjacent logical cells these copies form a [6, 2] code with n − k = 4. It meets the
  Reiger bound with equality, at rate 1/3 instead of 1/5.
- **Codes that mix several logical cells** in one codeword (parity or Reed–Solomon across cells) need the
  holder of a check symbol to see every data cell of its codeword, and each of those cells' neighbours. That
  takes radius 7 or more.
- I therefore believe three copies at stride 2 is the optimum at radius 5. This is my argument, not a source's.
- **Its distance is 3, not 5.** Fivefold corrects *any* two bad cells among five. The stride-2 code fails when
  two bad cells at the same tick are 2 or 4 apart.

Rates above 1/3 need a larger radius. Two interleaved [4, 2, 3] codes over GF(4) reach rate 1/2 at radius 7 or
more; the Gallager bound for burst codes allows up to about 0.8 with guard space 24, at radius about 24.

### 5.2 Experiment: G15 with three copies at stride 2 `[M]`

- `exp/patch3.py` changes 12 lines of a copy of `rule_g.py`: `SLOTS = (-2, 0, 2)`, three copies instead of five
  in the schema and the slot indices, three-way majority. With five copies the patched file still gives G15's
  netlist digest.
- `exp/search3.py` sizes the program as `experiments/search_comb.py` does. `exp/validate3.py` runs the C kernel.
- Nothing else was changed: same comb of five fronts, 64 registers, margin 122, gathers, wipes and compiler.

| | G15 | three copies, stride 2 | change |
|---|---:|---:|---:|
| bits per cell K | 260 | 193 | −26% |
| Q | 512 | 448 | −12.5% |
| working cells W / pass length | 268 / 288 | 204 / 224 | −22% |
| gates | 17,100 | 9,988 | −42% |
| of which majorities | 7,392 (616 × 12) | 2,224 (556 × 4) | |
| instructions | 32,835 | 23,214 | −29% |
| passes: NPe / MP / NP | 26 / 99 / 333 | 36 / 109 / 261 | −22% |
| blocks before E0 (gathers) | 57 | 64 | |
| **U** | **112,608** | **73,024** | **−35%** |
| U/Q | 220 | 163 | |
| **QU** | **2^25.78** | **2^24.96** | **1.76× smaller** |
| (QU)², the cost of a level-2 step | 2^51.6 | 2^49.9 | 3.1× smaller |

- **Seeds.** Seeds 5, 10 and 0 gave U = 73,024, 75,264 and 73,024. The five-copy search over 12 seeds that
  produced G14 ranged from 110,880 to 148,608 (REPORT §23), so the gain is well outside the seed scatter.
- **Gray's inequality.** Q ≥ 2K holds again (448 ≥ 386). It fails for G9–G15 (REPORT §16).
- **Using the freed bits for registers instead does not pay.** At Q = 512 with three copies, L = 96 gave
  U = 77,184 (QU = 2^25.24) and L = 128 gave U = 88,704 (QU = 2^25.44), one seed each.

**Checks passed** (`exp/vlog_c3_q448_s5.txt`):
- every phase of the compiled program replayed against the netlist: 0 mismatches;
- closure on the C kernel, two successive periods, 6 random and 6 coherent upper states: decoded ring equal to
  the rule applied upstairs, special procedure and Workspace-flag window correct, all copies agree, flags 0;
- level-0 errors on a slice of a healthy upper colony, one site or two adjacent sites, at 20 times of the
  period: **0 of 8,000 survive one tick** (2,000 each with random, inverted, all-zero and all-one values).

**Negative control:** two sites hit at the same tick, with random values, on a healthy slice.

| distance between the two sites | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|
| three copies, C kernel, 10 times across the period: not gone after one tick | 0 of 1,000 | 1,000 of 1,000 | 0 of 1,000 | 1,000 of 1,000 |
| three copies, NumPy stepper, Ages 2–4 | 0 of 330 | 330 of 330 | 0 of 330 | 329 of 330 |
| G15 (five copies), NumPy stepper, Ages 2–4 | 0 of 378 | 0 of 376 | 0 of 376 | 0 of 377 |

- Scripts: `exp/negctl.py` (C kernel) and `exp/negctl_np.py` (NumPy).
- The G15 row covers only the first ticks of the period. Its C kernel did not finish compiling in 11 minutes
  here, so I used the NumPy reference stepper and stopped the compile.

**Small level-1 probe** (`exp/level1_mini.py`, `exp/l1log_c3_q448_s5.txt`).
- Setup: a ring of 24 colonies, a slice of one healthy upper colony. One dense box of 100 cells × 100 ticks,
  every site random at every tick, in the middle colony. The ring is compared with the error-free ring at the
  next period boundaries: decoded upper state, and every physical bit.
- Nine phases with the box in the middle of the working area: first gather, between gathers, third gather,
  early program, phase A, just before the match pass, early and late final program, and across the commit.
  Four of them repeated with the box centred on the colony's left boundary.

| | bursts | upper cells wrong at the first boundary after the burst | wrong at the next boundary | physical bits differing at the second boundary after the burst |
|---|---:|---|---:|---:|
| box in the working area | 9 | none (3 bursts), the target cell only (6 bursts) | 0 | 0 |
| box on a colony boundary | 4 | none | 0 | 0 |

- This is the behaviour REPORT §25 and §27 record for G15: contained to one upper cell, repaired in one upper
  step, every field exact by the second boundary.
- Its limits: 13 bursts, random values only, one upper state, a slice rather than the whole upper colony, no
  run of the `gray_errors.py` classifier, and comparison at boundaries only, not at every tick.

**Not checked:** the full level-1 campaign (sparse certified errors, adversarial values, the whole upper colony),
Proposition 4 at every tick, the margin and compact-front tests, the GPU backend, two-level rings with noise,
three-level rings, more than three seeds.

### 5.3 Non-repetition codes decoded every tick `[M]` for gate counts, `[E]` for the rest

`exp/rs_gates.py` builds decoders with `gacsca/netlist.py` and checks them exhaustively.

| per-tick decoder | gates per data bit | corrects | radius needed |
|---|---:|---|---:|
| 3-way majority | 4 | 1 of 3 symbols | 5 (stride 2) |
| 5-way majority | 12 | 2 of 5 | 5 |
| [4, 2, 3] MDS over GF(4), 32 gates per block | 8 | 1 of 4 | ≥ 7 with interleaving |
| [6, 2, 5] Reed–Solomon over GF(8), 374 gates per block | 62 | 2 of 6 | ≥ 7 |

- The Reed–Solomon decoder is a plain Peterson–Gorenstein–Zierler circuit, verified on all 49,792 patterns of
  at most two symbol errors. A tuned circuit might be 2× smaller.
- A [6, 2, 5] code has the rate of three copies (1/3) and the distance of five. Substituting it for the 616
  majorities would add about 616 × (62 − 12) ≈ 31,000 gates: the netlist would grow from 17,100 to about
  48,000, and the program with it. It also does not fit radius 5.
- Verdict: for 2-cell bursts, algebraic codes buy nothing over spaced repetition and cost 5–15× the gates.

### 5.4 A colony-level code with no per-tick copies (Gács's scheme transplanted) `[E]`

Take away all copies and protect the colony the way Gács does.

| quantity | estimate | basis |
|---|---|---|
| K | 128 | 31 + 33 + 64 |
| Info code | Reed–Solomon over GF(32), symbol = 5 adjacent cells, 26 data symbols, 4 check symbols per block, one or two blocks | Def. 19.1, 19.3; one info bit per cell |
| W | ≥ 128 + 20…40 + 2 = 150…170, so W = 204 on the staircase | §2 |
| **Q** | **448: no better than three copies** | margins unchanged |
| netlist | about 4,000–6,000 gates | R1 has 4,144 gates at K = 107 with no redundancy |
| one evaluation | about 110–135 passes | 10–13k instructions at the 96 instructions per pass of §5.2 |
| three evaluations and vote (Alg. 19.7) | 330–400 passes | ×3 |
| one decode | about 5,000 instructions, about 50 passes | 1,500 syndrome XORs; about 1,400 for the error locator over GF(32); about 2,300 for 26 symbol positions |
| decodes per period | 12 if each of the 11 gathered states and the own state is decoded once; 36 as in Alg. 19.7 | radius-5 rule has 10 neighbours |
| **U** | **about 210k (12 decodes) to 500k (36 decodes)** | (350 + 600…1,800) passes × 224 |
| **QU** | **2^26.5 to 2^27.7, against G15's 2^25.78** | |

- The U estimate is good to a factor of about 2. Even at the low end it loses to G15 and by 3× to the
  three-copy variant.
- The decoders dominate because Gray's rule has ten neighbours where Gács's has two.
- `Legalize` (two rounds of three decode–encode cycles per retrieved track, Alg. 19.2) is left out. It would
  add 132 more codec runs. It is not needed here, because every bit string is a legal state.
- **The repository has already been here.** G3 and G4 ran the evaluation three times into Hold copies A, B, C
  and voted (`tmr=True`). REPORT §8 explains why that was dropped: one run lasts tens of thousands of ticks, and
  Gray's level-0 model allows an error in every 24 × 24 box, so a run is hit thousands of times.

### 5.5 Answers to the four sub-questions

**(i) Bits per cell and minimum Q.**
- Three copies: K = 193, Q = 448 `[M]`.
- No copies: K = 128, Q = 384 at best, and 448 once check symbols are stored `[E]`.
- Below that, Q is set by the 244 margin cells.

**(ii) Netlist size.**
- Three copies: −7,112 gates (−42%) `[M]`. Of this, 5,168 gates are the cheaper and fewer majorities. The other
  1,944 come mostly from updating three slots per cell instead of five.
- Algebraic per-tick code: about +31,000 gates `[E from M]`.
- Colony-level code: the netlist shrinks to about 5,000 gates, but the decoders move into the *program*
  (about 5,000 instructions per decode) `[E]`.

**(iii) Time for decode and encode passes.**
- Per-tick codes: none.
- Colony-level code: about 50 passes per decode, 600–1,800 passes per period `[E]`.

**(iv) Tolerance.**
- A per-tick code keeps "a level-0 error is gone one tick later". A colony-level code cannot: errors accumulate
  until the next decode, and Gács's answer is to allow one burst per colony per period and call anything denser
  the next level's problem (Def. 10.3).
- Rough rate of escalation to level 1, per colony per period, under independent noise of rate ε per site and
  tick. Each line counts only the storage code's own failure mode.

| scheme | fails when | rate per colony-period | ε giving 1% |
|---|---|---|---:|
| five adjacent copies (G15) | 3 of 5 holders hit at one tick | ≈ 10·ε³·QU = 5.8e8·ε³ | 2.6e-4 |
| three copies, stride 2 | 2 of 3 holders hit at one tick | ≈ 3·ε²·QU = 9.8e7·ε² | 1.0e-5 |
| colony code, refreshed per period | 2 faults in one period | ≈ (QU·ε)²/2, QU ≈ 3.3e7 | 4e-9 |

- These are not thresholds of the hierarchy; the provable bound is ε < (QU)^−2 ≈ 10^−15 in every case
  (Gray p. 19), and the repository has no measured threshold.
- They do show the ordering: three copies cost about 25× in ε against five, and a per-period code costs
  about another 2,400×.

---

## 6. Stored program and "true" self-simulation

### 6.1 What Gács 2001 does `[S]`

- §5.5 (pp. 51–52) lists "Program change" among the disruptions and answers: "our solution will be that the
  simulation will not use any 'program' or, in other words, we 'hard-wire' the program into the transition
  function of each cell."
- §9.2 (p. 82): "it seems redundant to give U its own program, and actually it is better not to, since the
  written program is exposed to errors."
- The mechanism (Remark 9.4, p. 82; Def. 9.14, pp. 88–89):
  - the rules are written in a small language;
  - a special parameter `My-rules` is "the string that is the sequence of all the rules", and a cell can
    produce its j-th symbol through the access function `Param_i(j)`;
  - each work period, `Eval` writes the interpreter, `My-rules` and the parameters onto the `Cpt` track,
    copies in the arguments, and runs the universal automaton `Univ` there (Alg. 9.7, p. 95; Alg. 19.5,
    p. 188).
- So the text exists on a track only for the duration of one evaluation, and is regenerated from the rule
  each time. The three repetitions cover a burst during an evaluation.
- Costs (Theorem 9.2, p. 89; Condition 9.20, pp. 95–96):
  - time: interpr-coe · (|P| + 1)² · ‖S‖;
  - Q ≥ interpr-coe · (‖S₂‖ + |Trans-prog₂| + log U + 1);
  - U ≥ 3Q + interpr-coe · (|Trans-prog₂| + 1)² · ‖S₂‖.

### 6.2 How this maps to the repository

| | Gács 2001 | Gray pp. 31–32 | Repository |
|---|---|---|---|
| Where the program lives | in the rule: symbol j of `My-rules` at the cell that asks for it | in the rule: ProgramBit = f(Address) | in the rule: Pi[Address][page] |
| Shape | a text of O(log QU) bits with loops | the same text, one bit per cell | a straight-line program, 32,835 instructions |
| Executed by | an interpreter, cell-parallel over the whole colony | "an interpreter … built into the transition function" | five sweeping fronts, one instruction per visit, no interpreter |
| What the upper level needs | the text again, recited by the colony | one ProgramBit per period, fetched by steps (i)–(iii) | one Pi word per period, fetched by the match pass |
| Must fit in the colony? | yes: Q ≥ c·(|P| + ‖S‖) | yes: "less than Q bits" (p. 30) | no |

The repository is already Gray's and Gács's hard-wired design. It differs only in indexing the table by
(Address, page) rather than by Address alone, which removes the requirement that the program fit in Q cells.

### 6.3 Would a stored program change Q or U? `[E]`

- **Compiled program stored in the cells.** 788 kbit over 512 cells is 1,539 bits per cell for one copy, 4,617
  with three copies, 7,696 with five. K becomes roughly 1,800–8,000, and by Q ≥ 2K, Q becomes roughly
  3,600–16,000. This is the archived U20 design: 3,402 static bits per cell, K = 6,465, Q = 8,192, U = 2^20,
  QU = 2^33 (REPORT §1). That is 150× worse than G15. The projected table was the repository's largest single
  gain.
- **Program on a track, streamed past the cells.** The stream still has to be stored somewhere in the colony:
  the same 788 kbit. A track one instruction wide holds 512 instructions, 1.6% of the program. Streaming changes
  who moves, not how much must be stored. It does not remove the registers either.
- **A short looped text plus an interpreter (Gács's actual route).** The netlist is regular (33 logical bits ×
  5 slots), so a rule-language text might be a few thousand bits; I have not written one.
  - With Gács's bounds and interpr-coe = 1, |P| = 1,000 bits and ‖S‖ = 193 give U ≥ 1.9 × 10^8 and Q ≥ 1,200.
    With |P| = 5,000, U ≥ 4.8 × 10^9.
  - That is 1,700 to 43,000 times G15's U.
  - The bounds are upper bounds on Gács's own interpreter and are surely not tight. But the front machine would
    also need a program counter, loop counters and indexed addressing in the cell state and rule. That is a
    different machine, and nothing suggests it would beat a compiled table.
- **Repair of a stored program from neighbouring colonies.** I found no such mechanism in the 2001 paper. Its
  only treatment of program damage is hard-wiring (§5.5).

**What in Gács does bear on U** is not the stored program. It is that `Univ` runs on every cell of the colony
at once, which is where Gray's "3Q + a·log₂Q + b" for the update stage comes from (p. 34). G15 executes five
instructions per tick in a colony of 512. The repository's equivalent lever is the scheduler: the slot bound is
22 passes on four fronts against about 230 used (REPORT §23).

---

## 7. Level-dependent parameters (the amplifier)

**What Gács chooses** `[S]` ((11.9), p. 110): w_k = 1/(R·k²), Q_k = R^(k+1), U'_k = R·Q_k/w_k = R^(k+3)·k²,
Cap_k = B_k·(1 + δ_k), with B_k = ∏_(i<k) Q_i.

**Why the sizes grow** `[S]`:
- *Capacity.* The level-k cell carries the whole payload of the B_k base cells under it (aggregation,
  Def. 4.9; Theorem 3.3, pp. 21–22: "storing one symbol per cell").
- *Bounded overhead.* All other tracks must have relative widths w_k with ∑ w_k < ∞, so that the base cell is
  finite (Proposition 5.17, p. 50; §19.1, p. 179).
- *Counters.* The narrow tracks must still hold numbers of size log U_k: w_k·Cap_k ≥ R·log U'_k ((11.13),
  p. 111). With w_k shrinking, Cap_k and Q_k must grow.
- *Error bound.* The growth is not needed for it. The recursion ε_(k+1) = c·(Q_k·U'_k·ε_k)² tolerates
  growth, because ε_k falls doubly exponentially ((11.10), (11.17)).

**Does fixed (Q, U) suffice?** Yes, for Gray's theorem `[S]`.
- Proposition 1 (p. 19) needs only ε < (QU)^−2 with one Q and one U at all levels.
- What is remembered is the Address phase, log₂Q bits (pp. 15–16). Gray contrasts this with Gács's "one bit per
  site" on p. 16.

**Cost of adopting it** `[E]`:
- Level k and level k+1 would run different rules. The colony would have to *compute* the next level's layout,
  page ranges and instruction table from k, instead of fetching one word of its own table. A compiled Pi cannot
  do that; it needs the interpreter of §6.
- Gács's U'_k/Q_k = R²·k² grows with the level and is at least R².
- Gray guesses R₀ ≥ 2^18 for the journal version's constant, with ε ≤ R₀^−40 (p. 10). If that is the R of
  (11.9), then Q₁ = R² ≥ 2^36. Gács's parameters are a proof device, "no attempt was made … to optimize"
  (Gray p. 10), and say nothing useful about small Q and U.

---

## 8. Self-organization, robust media, asynchrony

- These make up most of the 2001 paper: §§10, 12–18, 20–21, about 100 pages of rules and lemmas.
- They serve Theorems 3.1, 3.2 and 3.4: homogeneous initial configurations, continuous time, and computation
  whose hierarchy grows as needed (pp. 20–24).
- Gray's version does without all of them and still disproves the conjecture. The repository states the same
  assumption: a good initial configuration (REPORT §16).
- They add state (Kind, Dying, Depth, Frozen, Healing, Color, Rand, channel and growth cells with addresses in
  [−Q, 2Q)), and each addition is something the colony must then simulate. Gray warns of exactly this loop
  (p. 27).
- I see no route by which any of them lowers Q or U.

---

## 9. Ranked recommendations

### (a) Practical now, and reduces Q·U

**A1. Three copies at stride 2 instead of five adjacent copies.** Measured: QU 1.76× smaller (§5.2).

Design change, by module:
- `gacsca/rule_g.py`
  - a parameter for the copy geometry (five adjacent, or three at stride 2), replacing the module constant
    `SLOTS`;
  - `schema`, `copy`, `lv` (majority of the right width), the `new[...]` slot indices in `build`,
    `_five_front`, `_mux_front`, `_sel_front`, and `info_copies`;
  - `exp/patch3.py` is the complete list of the 12 places for the `mux_front` path. `_sel_front` builds but was
    not exercised.
- `gacsca/compiler.py`: only `default_layout(interleave=True)` divides by 5. It is unused by G15.
- `gacsca/codec.py`, `gacsca/machine.py`, `gacsca/multifront.py`: no change. The C kernel generator worked
  unmodified.
- `gacsca/gpu.py`: not tried.
- `gacsca/candidates.py`: a new recipe. The one validated here is G15's parameters with q = 448, m = 17,
  nb = 326, NPe = 36, MP = 109, NP = 261, order and owner seed 5 (`exp/cand_c3_q448_s5.npz`).
- Tests and drivers: `CompactFrontTest` flips two register copies at once, which three copies cannot outvote
  unless the two cells are adjacent. `level0_one_tick.py` needs no change.

Expected, with the assumptions that the present compiler and margin are kept:

| | K | Q | gates | instructions | passes | U | QU |
|---|---:|---:|---:|---:|---:|---:|---:|
| G15 | 260 | 512 | 17,100 | 32,835 | 333 | 112,608 | 2^25.78 |
| A1 | 193 | 448 | ≈ 10,000 | ≈ 23,300 | ≈ 260–270 | 73,000–76,000 | 2^24.96–2^25.0 |

Risks:
1. **Distance 3.** Two simultaneous single-site errors 2 or 4 cells apart defeat it (measured). This is outside
   Gray's level-0 class and inside his level-1 class, so the hierarchy is meant to handle it, but level-1 events
   become about 25× more frequent in ε terms (§5.5).
2. **Thinly validated above level 0.** Thirteen bursts behaved as on G15 (§5.2). The level-1 campaign, both
   parts of Proposition 4 at every tick, the margin and wipe behaviour and the three-level checks must be
   rerun. During recovery from a burst a bit now needs two good copies of three rather than three of five.
3. **A deviation from Gray's text** (p. 33 says five), though not, as far as I can see, from his argument.

A side benefit: the netlist is 42% smaller, so the kernels do less work per site as well.

**A2. The compiler** remains the larger lever on U. This is unchanged by this study, and the Gács papers offer
nothing for it beyond the observation in §6.3.

### (b) Practical, neutral or negative for Q·U, of value for fidelity

- **B1. A rule-language statement of the fixed point.** Writing down, in Gács's terms, that Pi is `My-rules`
  indexed by (Address, page) and that the match pass is Gray's steps (i)–(iii). Documentation only.
- **B2. Gács's "safe age" retrieval** (§19.2, pp. 184–185): accept neighbour data only when the sender's Age is
  in a safe interval. It guards against reading a neighbour during its commit. The repository's fixed gather
  times already avoid this in aligned colonies; it would matter only with misaligned ones.
- **B3. A colony-level checksum on Info, used only for detection,** so that a damaged colony raises its upper
  flag at once. It costs a few passes. I have not found a place where the hierarchy needs it.

### (c) Impractical, or harmful to Q·U

| feature | effect on Q·U | reason |
|---|---|---|
| Stored compiled program | about 150× worse | 788 kbit against a 133 kbit colony (§6.3); it is the U20 design |
| Program streamed along a track | same | storage, not motion, is the limit |
| Rule language and interpreter | ≥ 10³× worse in U | Theorem 9.2's quadratic interpretation time |
| Reed–Solomon along the colony replacing per-tick copies | U 2–5× worse, Q no better than A1 | §5.4; also loses the one-tick property |
| Algebraic per-tick code | netlist about 2.8× larger | 62 gates per bit against 12; needs radius ≥ 7 |
| Three evaluations and a vote | U about 3× worse | tried as G3/G4, dropped (REPORT §8) |
| Level-dependent Q_k, U_k | not expressible with a compiled table | needs the interpreter; buys capacity, which is not a goal |
| Self-organization, robust medium, asynchrony | more state to simulate | serves theorems the project does not target |

### What would reduce Q further

Not coding. The margins are 244 of 448 cells after A1. They follow from Gray's constants (24 and 104, hence a
burst of 200) and from the repository's one-colony containment. Changing them means re-deriving Gray's
Proposition 1 with other constants, or accepting his own allowance of two damaged colonies. Either is a change
to the error model, and I have not analysed it.

---

## 10. What I could not verify

1. **Gács 1986.** Not in `papers/`. Its code, program mechanism and parameters are unknown to me; the statements
   in §3 are from Gray and from Gács 2001.
2. **Section correspondence** between the 2024 printing and the journal version Gray cites: matched by content,
   not checked against the journal text.
3. **Gács's constants.** R, K, interpr-coe and c_Dam are never given numbers. Identifying Gray's R₀ with the R
   of (11.9) is my guess; the exponents agree roughly ((11.17) gives ε ≤ R^−35 at level 1, Gray says R₀^−40).
4. **The optimality of three copies at radius 5** (§5.1) is my argument from the Reiger bound and the reach
   constraint, not a result from the sources.
5. **That Gray's proof survives three spaced copies.** His level-0 class is exactly one or two adjacent sites,
   and p. 33 uses nothing else, but I have not gone through Propositions 2, 4 and 5 line by line.
6. **The three-copy candidate above level 0,** beyond the 13 bursts of §5.2. See "Not checked" there. Its
   program was sized on three seeds.
7. **The negative control on G15 itself** covers Ages 2–4 only, with the NumPy stepper (§5.2).
8. **All numbers marked `[E]`:** the colony-level-code estimate (factor of about 2), the noise rates in §5.5
   (independent noise, first-level escalation only), the interpreter estimate (|P| is a guess), and the
   Reed–Solomon gate count's distance from an optimized circuit.
9. **`gpu.py` and `_sel_front`** with three copies: not run.

---

## Appendix: files in `exp/`

| file | what it is |
|---|---|
| `gacsca/` | copy of the package from `git archive HEAD`, with `rule_g.py` patched (`GACS_COPIES=5` reproduces G15's digest) |
| `patch3.py` | the patch |
| `baseline.py`, `g15_base.py` | G15 bit, gate and instruction counts; manifest check of the copy |
| `search3.py`, `slog_*.txt`, `search_*.json` | seeded sizing of the three-copy variant |
| `cand_c3_q448_s5.npz` | the validated candidate (ROM, layout, parameters) |
| `validate3.py`, `vlog_c3_q448_s5.txt` | closure and level-0 one-tick checks |
| `level1_mini.py`, `l1log_c3_q448_s5.txt` | the 13-burst level-1 probe |
| `negctl.py`, `negctl_np.py` | error pairs at distance 1–4: C kernel (three copies), NumPy stepper (G15 and three copies) |
| `rs_gates.py` | gate counts of the majority, [4,2,3] and [6,2,5] decoders |
| `stats3.py` | schema and majority counts of the three-copy netlist |

To rerun the main result (about five minutes, one core):

```sh
cd exp
GACS_COPIES=3 python3 search3.py 448 122 5 c3_q448_s5
GACS_COPIES=3 python3 validate3.py cand_c3_q448_s5.npz 2 2000
```
