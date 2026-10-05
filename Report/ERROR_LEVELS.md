# Gray's error-level constants, the 200-wide level-1 box and the colony margin

Written 2026-10-02 by a sub-agent, for the owner's question: *are 24, 104 (or 108) and 200 arbitrary, and can
they be changed so that the colony margin, Q and U shrink?* Nothing in the repository was edited. Everything
produced is under `errlevels/` (= the directory of this file); `errlevels/repo/` is a private copy of `gacsca/`
at the working tree of 2026-10-02 with three small patches (§7). No GPU was used.

**Read this first** (added by the main session when the study was filed).
- `errlevels/` in the text is [`error_levels_exp/`](error_levels_exp/): the agent's scripts, its result files
  (`results/`), the sizing sweeps (`sweeps/`, called `repo/figs/sweep/` in the text) and the image of Gray's
  p. 17. Its logs, its private copy of `gacsca/` and the compiled variants are not kept. The two patches of that
  copy are described in §7; I compared the copy with the repository and found nothing else changed.
- Nothing proposed here is adopted. G16 is unchanged.
- Two of its claims were checked again by the main session, on the repository's own code and the C kernel:
  - four points spanning 150 sites and ticks are one level-1 error for `gray_errors.classify`, and spanning 151
    they are not (§2.1);
  - on G16, a 200 × 200 burst that writes a block of shifted states and reaches 10 cells into the right-hand
    colony left two adjacent upper cells wrong at the next boundary at two of three Ages tried; the same box
    with random values left one. All six rings were bit-identical to the error-free ring one period later
    (§4.3). REPORT §31 records this.
- Not checked again: the repaired proof step for a smaller c (§2.2, the agent's own argument), the sizing
  sweeps, and the burst and closure runs on the Q = 384 variants.
- Its remark on REPORT §29 ("191 upper bits") was right; the report now says 258.
- "18 settings" per sizing row: in three of the rows (`q384_g10`, `q384_g12`, `q448_g12`) one setting did not
  converge, so those figures are over 17.
- The check by the main session is `error_levels_exp/shiftcheck_main_session.py`, with its output in `results/`.

**Legend.** `[S]` read from a source, with page or section. `[M]` measured here; the command and the output
file are in §7 unless given in place. `[E]` my estimate or inference. A tag at the end of a sentence, bullet or
table row covers that whole item; a tag in a table header covers the column.

**Terms.** λ = 24 is Gray's link and isolation distance. c = 104 is the separation in his condition (iii).
B is the side of the box that holds one level-1 error. The *exposure* of a candidate is 2·margin − 2H − 3, the
number that `ParamsG.check` requires to be at least 200: a burst up to that wide cannot directly hit the front
state or working data of two neighbouring colonies.

---

## 0. Verdict

**Yes, the constants can be changed, and the change that matters costs nothing in Gray's sparsity argument.
It takes the margin from 122 to 58 cells and Q from 512 to 384. With the gather spacing that the smaller box
justifies, U goes from 25,920 to about 19,300–20,700.**

1. **What Gray prints.** 24, 104 and 200; "108" is nowhere in the guide. He calls only 24 "a convenient
   choice" (p. 17). The rest is a chain: 26 = 24 + 2, 52 = 2·26, 104 = 2·52, 130 = 104 + 26, and
   26 + 130 = 156, which he rounds to 200 ("fits easily"). `[S]` for the numbers, `[E]` for the chain (§1).
2. **200 is already too big by Gray's own definitions.** A level-1 error is at most 104 + 2·24 − 2 = 150
   sites wide and 150 ticks long; at higher levels 156 units. `[M]` for 150 (search, and the repository's own
   classifier), `[E]` for 156 (§2.1).
3. **104 is free.** It is used once, to make one sentence of a proof immediate. Condition (iii) works with any
   c ≥ 1, the level-1 box becomes c + 2λ − 2, and Proposition 1 (the bound ε_n ≤ (QU·ε_(n−1))², threshold
   (QU)^(−2), exponent 2^n) does not contain c or λ at all. With **c = 16** a level-1 error is at most 62 wide,
   and a level-n error at most 68·Q^(n−1). `[E]` for the proof step, which is mine; `[M]` for the box formula
   (§2.2).
4. **24 should stay.** It is the spacing the rule is promised between errors, and Gray's higher-level argument
   needs it above the Flag2 period of 16, which is built into the rule. Lowering it is not needed. `[S]`, `[E]`
5. **What it buys.** Q moves in steps of 64, so only two targets exist: exposure ≤ 137 gives Q = 448, and
   exposure ≤ 73 gives Q = 384. Nothing between 73 and 9 helps, and Gray's corrected 150 gives nothing. `[M]`

   | | Q | margin | gathers | U best of 18 settings | U median | QU best | status |
   |---|---:|---:|---|---:|---:|---:|---|
   | G16 | 512 | 122 | 12Q | 25,920 | 27,648 | 2^23.66 | validated `[S]` |
   | margin 58, nothing else changed | 384 | 58 | 12Q | 22,176 | 23,904 | 2^23.02 | sized; closes on the C kernel `[M]` |
   | margin 58, gathers 10Q | 384 | 58 | 10Q | 20,736 | 22,752 | 2^22.92 | sized; closes on the C kernel `[M]` |
   | margin 58, gathers 9Q | 384 | 58 | 9Q | 19,296 | 21,888 | 2^22.82 | sized; closes on the C kernel `[M]` |

   The scheduler's scatter is ±4 passes (±1,150 ticks); read the medians, or the fixed part: 52 blocks before
   the evaluation for G16 against 39, 34 and 31.
6. **The cost to the claim.** The sentence "a burst up to 200 cells wide directly hits the data of at most one
   colony" becomes "up to 73 cells wide". Bursts of 74–200 cells across a boundary can then hit two colonies,
   which Gray's Proposition 4 allows and the upper level's fivefold storage absorbs. That is the whole cost,
   and it is smaller than it looks:
   - The margin rule is the repository's, not Gray's. Gray's p. 33 gives no distance, and his level-1 box
     "can touch at most two colonies" (p. 22). `[S]`
   - **On G16 itself the rule does not keep the damage to one colony when the values are chosen.** A 200-cell
     burst that writes a block of consistent but shifted Addresses, placed with 10 of its cells in the
     right-hand colony's margin and the rest in the left-hand colony, left two adjacent upper cells wrong in
     5 of 5 runs. A 72-cell burst of that kind lying entirely inside the two
     margins left the right-hand upper cell wrong in 9 of 11. This is Gray's damage island (p. 25) crossing
     the right-hand colony. With random values none of this happens. `[M]` (§4.3)
7. **Evidence here for the Q = 384 rule** (C kernel only; three variants built, with gathers 12Q, 10Q and 9Q
   apart): all three close for 6 work periods each; 0 of 26,000 level-0 errors visible after one tick; 617
   bursts of 40–200 cells (random, shifted and copied values, 11 phases, 7 placements): never more than two
   adjacent upper cells wrong, never a wrong cell after the next upper step, all 617 bit-identical to the
   error-free ring at the second boundary. The local structure was back within 380 ticks in the worst case,
   against a rest of 1,545 ticks between gathers at 9Q and 1,929 at 10Q. `[M]` (§4)
8. **Against the options already on the table.** `[S]` for their numbers (REPORT §29), `[M]`/`[E]` for mine.
   - *Gathers 10Q apart* (U 23,904): the same lever as the gather rows above, and it stacks.
   - *Three copies instead of five* (Q 448, U 21,056, QU 2^23.17): similar QU to "margin 58" alone (2^23.02),
     but it weakens the storage code from distance 5 to 3. The margin change weakens nothing in the code and
     reaches a smaller Q. The two stack: three copies with margin 58 is Q = 320 and U about 15,500 by
     arithmetic `[E]`.
   - So it is worth it: it is the largest reduction of Q that keeps both the fivefold storage and a
     direct-hit margin (dropping the margin rule altogether gives Q = 320, §3.4), and it turns the 9Q or 10Q
     gather spacing from a loss of slack into something Gray's own bound supports.
9. **Not done.** GPU kernel, the Gray-classified two-level campaign, upper-colony stages other than Age 0,
   three levels. The candidate would need the full validation of REPORT §29 (§5).

**Recommendation.** Record c = 16 as a deviation from Gray beside the existing ones, make the exposure a
recipe parameter, and validate the candidate "Q 384, margin 58, gathers 10Q" (U 20,736). Take 9Q as a second
step.

---

## 1. Gray's constants, traced

Page numbers are the article's own (1–44), as in `papers_txt/gray_readers_guide.txt`. I checked the disputed
number against the page image of p. 17 (`gray_p17-17.png`): Gray prints **104**. "108" occurs nowhere in the
guide. `[S]`

### 1.1 The error-class definitions (§5.1, pp. 16–19)

Below, μ = λ + 2 = 26.

| constant | where | what Gray says `[S]` | where it comes from | status |
|---|---|---|---|---|
| 1–2 adjacent sites, one tick | p. 16 | a candidate level-0 error fits in [x, x+1] × [t, t] | It is the footprint a level-1 error leaves one level up: its box "can touch at most two colonies" (p. 22), and Proposition 4's box (kU, (k+2)U) holds one multiple of U (p. 36). `[E]` | forced, given B ≤ Q |
| **24** (λ) | p. 17 | "The number 24 is simply a convenient choice that makes later estimates work out well." | The estimates: level-0 errors slow a wave by "much less than 1/4 cell per time step" (p. 23); level-n errors come "once every 24 work periods" against the Flag2 trickle-down "once every 16" (pp. 38, 40). | free, but bounded below by the rule: λ > 16 |
| 24Q^(n−1), 24U^(n−1) linking; 24Q^n, 24U^n separation | p. 17, (ii), (iv) | the same number at every level | Linking at level n is the complement of isolation at level n−1, and the level-1 automaton is the same rule. `[E]` | derived from λ |
| 25 | p. 18 | points "(25Q^(n−1), 25U^(n−1))-linked" to (x₁, t₁) | λ + 1: what is λ-linked to S₁ is 25-linked to (x₁, t₁), since S₁ is at most 26Q^(n−2) ≤ Q^(n−1) wide. `[E]` | derived |
| **26** (μ) | p. 17 | a minimal candidate "fits into a 26Q^(n−2) × 26U^(n−2) box" | λ + 2: two candidates one level down, each in a unit box, sharing a λ-box. `[E]` | derived |
| 52 | p. 18 | a point "(52Q^(n−2), 52U^(n−2)) separated from (x₁, t₁)" gives a disjoint second candidate | 2μ. `[E]` | derived |
| **104** (c) | p. 17 (iii), p. 18 | "S does not contain two candidate level-n errors that are (104Q^(n−1), 104U^(n−1)) separated"; "Otherwise, S fits inside a 104Q^(n−2) × 104U^(n−2) space-time box … Clearly, S satisfies condition (iii)" | 4μ = 2·52: everything within 52 of one point fits in a 104-box, and a set inside a c-box satisfies (iii) trivially if c ≥ 104. That sentence is the only use of the value. `[E]` | a proof convenience; free (§2.2) |
| 130 | p. 18 | "any point in S∖S₁ must be (130Q^(n−1), 130U^(n−1))-linked with S₁" | c + μ. `[E]` | derived |
| **200** (B) | pp. 18–19, Prop. 1 | "every level-n error S actually fits easily into a 200Q^(n−1) × 200U^(n−1) space-time box" | With S₁ at the leftmost point: μ + (c + μ) = 156. "Easily" is the step from 156 to 200. For n = 1 the exact maximum is c + 2λ − 2 = 150. `[E]`, `[M]` (§2.1) | derived, then rounded up by 28–33% |
| (QUε)², ε < (QU)^(−2) | p. 19 | ε_n ≤ (QU·ε_(n−1))², hence ε_n < (Q²U²ε)^(2^n) | van den Berg–Kesten: a candidate level-n error contains two disjoint candidates one level down. Neither 24, 104 nor 200 appears. | depends only on QU |

### 1.2 Constants of the construction that depend on them

| constant | where | what Gray says `[S]` | where it comes from | status |
|---|---|---|---|---|
| radius 5, "at least three" of five | pp. 14, 20–21 | N = {−5…5}; apparent colony from three consistent Addresses in R(x) | A level-0 error spoils two adjacent cells; a one-sided vote that survives two bad cells needs five. `[E]` | forced by the 2-site error |
| five copies on x−2…x+2, voted every tick | p. 33 | "To take care of level-0 noise, I use a five-fold redundancy" | Two adjacent sites spoil at most two of five copies on adjacent cells. `[E]` | forced by the 2-site error |
| speeds 3, 2.75, 2, 1.75, 1, ½, ¼ | pp. 21, 23–26 | Flag1 wave 3 (≥ 2.75 with noise); Flag2 block 2; damage spreads at 3 (< 4 with noise); erosion 1 (≥ ½ after two "transient effects" below ¼); Flag1 returns at ≥ 1.75 | The 3-of-5 and 4-of-5 thresholds of the Flag rules; the losses come from λ = 24. `[E]` | forced by the rule; losses derived from λ |
| 16 | pp. 21, 24, 38, 40 | Flag2 is set where no apparent colony exists "and the computed value of Age … is divisible by 16"; "only once every 16 work periods"; "just enough" (p. 40) | Must be below λ so that reversals outpace level-n errors. In the repository: `maintenance.py` (`(age_l + 1) % 16 == 0`), `ParamsG.check` (`R % 16 == 0`). `[M]` | free, tied to λ |
| 800, 1000, 500, 2000, 400, 1600 | p. 25 | island grows "at most 800 cells"; "no leftward-moving wave of 1's needs to cover more than 1000 cells"; "less than 500 time steps"; "another 2000"; "at most 400 time steps"; "1600 cells" | 4B; B + 4B; 1000/2; 4·500; B/½; 4·400. `[E]` | derived from B = 200 |
| island < Q/2, < 3Q/4; **Q ≥ 2^13** | pp. 15, 25 | "since Q ≥ 2^13, the damage island has size less than Q/2"; "remained below 3Q/4" | 3000 < Q/2 and 4600 < 3Q/4 need Q > 6133; 2^13 is the next power of two. In general Q > 30.7·B. Gray does not say this. `[E]` | derived from B = 200 |
| 200 + 500 + 2(Q + 200) | p. 26 | "the island gets completely eroded within 200 + 500 + 2(Q+200) time steps" | B_t + (B_x + 4B_t)/2 + 2(Q + B_x) = 2Q + 3B_t + 2.5B_x. `[E]` | derived from B |
| U/32; **U = 128Q** | pp. 15, 26, 34–35 | recovery "much less than U/32"; three stages of U/4 and two of U/8, each half active, half rest; a gather is active for U/8 = 16Q; the update needs 3Q + a·log₂Q + b within U/16 = 8Q | U/32 = 4Q > 2Q + 1100 needs Q > 550. The rest between gathers, 16Q, is four times the recovery bound; a gather needs about 5Q. About 40Q would meet every stated need. `[E]` | free, about 3× slack |
| at most one active stage disturbed | p. 35 | "This time period can touch at most one of the active stages" | rest between gathers ≥ recovery bound | forced, given three gathers and a vote |
| Q ≥ 2K; SimBits "not … near the colony boundaries" | p. 33 | no distance is given | The repository reads this as a margin sized by 200 (§3). Gray does not connect the two. | free |
| cells 3, Q−3; [0, 4], [Q−5, Q−1]; 2Q; 3U/4 | pp. 35, 41 | special SimBits; Workspace.Flag cells; trickle-down window | within reach of the radius-5 votes | forced by the radius, except 2Q |
| boxes 2Q × U/32, 2Q × 2U, 2Q^k × U^k/16 | Props. 2, 4, 5 | | consequences of the above | derived |

**Gács's own constants, for comparison.** `[S]` In Gács's paper (2024 printing, Definition 10.3, pp. 97–98) the
unit of noise is an *island*: damage covered by a box of β = 15 cell widths × 15 dwell periods and "too far"
from the rest, meaning no box of γ = 5 colonies × 5 work periods meets both. β = 2γ + 5 is what his probability
argument needs (proof of Lemma 10.5, pp. 99–100). The recursion is ε_(k+1) = c_Dam·(Q_k U'_k ε_k)² ((11.8),
p. 110). So the paper Gray simplifies has a burst of 15 where Gray has 200, and an isolation of 5 where Gray
has 24. I did not trace β through Gács's later sections.

**Masumori et al.** `[S]` implement Gray's local structure only, with Q = 271 and U = 128Q, and inject errors
at a rate per cell per step; they do not use the error classes or any of the constants above
(`papers_txt/masumori.txt`, "Results").

---

## 2. The chain that ends at the 200-wide box

### 2.1 What makes a level-1 error up to 200 wide

A level-1 error S is a set of error points, none of them a level-0 error, with `[S, p. 17]`: (i) S fits in a
Q × U box; (ii) S contains two candidate level-0 errors within 24 of each other in both coordinates; (iii) S
contains no two candidate level-1 errors that are (104, 104)-separated; (iv) every other error that is not a
level-0 error is (24Q, 24U)-separated from S.

The width comes from three links in a row `[E]`:

1. The leftmost point p of S is not a level-0 error, so another error q lies within λ − 1 = 23 of it in both
   coordinates. {p, q} is a candidate level-1 error, and q ∈ S by (iv).
2. The same holds for the rightmost point p′, with a partner q′.
3. By (iii) the two pairs are not (c, c)-separated: a point of one is within c − 1 = 103 of a point of the
   other.

So S spans at most (λ − 1) + (c − 1) + (λ − 1) + 1 = **c + 2λ − 2 = 150** sites, and the same in ticks.
Growth during the repair plays no part: 200 bounds the error set, not the damage. The damage is bounded
separately (the 800, 2000 and 1600 further cells of p. 25).

- **The bound is attained.** The four points (0,0), (23,23), (126,126), (149,149) are one level-1 error for
  the repository's `gray_errors.classify` and for an independent brute-force classifier with λ and c as
  parameters; one site wider is not. The two classifiers agree on 400 random sets. `[M]`
  (`results/gray_param.json`)
- **The formula holds for other constants.** Exhaustive search over all point sets on a line for 22 pairs
  (λ, c) with λ ≤ 6, both c ≥ λ and c < λ, and random search in the plane for 7 pairs, found the maximum
  exactly c + 2λ − 2 every time. `[M]` (`results/gray_param.json`, `results/gray_param_small_c.json`)
- **At higher levels** a candidate one level down is up to a unit wide, and the same three links give
  (c + 2(λ + 2))·Q^(n−1) = **156·Q^(n−1)**: Gray's 26 + 130 (p. 18). `[E]`
- **200 is 156 rounded up.** Nothing later in the guide needs the extra 44. `[E]`

A dense w × w box is one level-1 error only for w ≤ c. The repository's certified dense 100 × 100 boxes are
level-1 errors and its 200 × 200 bursts are not (REPORT §25). But a rule that tolerates *every* error set
inside a B × B box with B ≥ c + 2λ − 2 tolerates every level-1 error, because an error may leave a value
unchanged (Gray p. 4). The number that matters for the margin is the extent, 150, not the dense-box limit, 104.

### 2.2 Which constants can move

**c is free.** `[E]` The value 104 is used once: "Clearly, S satisfies condition (iii)" (p. 18), inside the
proof that every point outside E_(n−1) lies in a small candidate level-n error. With a smaller c the sentence
can fail, and the proof is repaired in one line. If the cluster T of all points near (x₁, t₁) violates (iii),
then T contains two separated, hence disjoint, candidates one level down inside one 104Q^(n−2)-box, so **T
itself is a candidate level-n error containing (x₁, t₁)**. This is Gray's own remark on p. 17: "if condition
(iii) fails … then S qualifies as a candidate level-(n+1) error". The candidate is no longer "minimal" (2^n
points), but it is still at most 26 units wide, and that is all the size bound uses. Then:
- the size bound is c + 2λ − 2 at level 1 and (c + 2λ + 4)·Q^(n−1) above, for any c ≥ 1;
- Proposition 1 is unchanged: its estimate never mentions c;
- a cluster that a smaller c rejects as a level-1 error becomes a candidate level-2 error. It is then owed
  only the treatment of a level-2 error, which is weaker than what it physically needs.

What is checked: the level-1 formula and the classifier (`[M]`, above). The repaired step is my own argument,
at the rigour of Gray's sketch. It inherits a looseness already in Gray's text: his second candidate is found
among points 25Q^(n−1)-linked to (x₁, t₁), while a candidate needs 24Q^(n−1)-linked parts.

**λ is not free in the same way.** `[E]` It is the spacing the rule is promised:
- level-0 errors at least λ apart (the wave-speed losses of p. 23);
- level-n errors at one place at least λ work periods apart, against a Flag2 reversal every 16 (p. 40).

A smaller λ shrinks B by 2 per unit (6 per unit if c = 4(λ + 2) is kept), and asks more of the rule. The
repository's noise evidence is all at Gray's spacing (the "E0 grid", G = 50; REPORT §14, §26 `[S]`).

**What this rule needs at level 0.** `[M]` (G16 on the C kernel, healthy colonies, random values;
`results/pair_G16.json`, `results/pair_G16_w2_K48.json`.) Two errors of one or two sites each:
- on different ticks (1, 2 or 3 apart), at any distance including touching: the state is bit-identical to
  the error-free run one tick after the second error, in 12,480 of 12,480 trials;
- on the same tick: bit-identical after one tick whenever at least 9 clean sites lie between them (2,304 of
  2,304); after two ticks with 8 clean sites; with 3–7 clean sites 5–49% are still different 48 ticks later
  (Flag1 and mail); with 2 or fewer, the fivefold vote is beaten and the damage stays.

So at level 0 the rule needs (10, 1)-separation where Gray's class promises (24, 24). The slack is real, but
λ cannot be lowered to 10 without changing the Flag2 period, and it does not need to be (§3.1).

### 2.3 The smallest box the argument supports here

| choice | λ | c | level-1 extent c + 2λ − 2 | level-n extent, units of Q^(n−1): c + 2λ + 4 | what changes |
|---|---:|---:|---:|---:|---|
| Gray as printed | 24 | 104 | "200" | "200" | — |
| Gray's definitions, not rounded | 24 | 104 | 150 | 156 | only the number the margin is sized for |
| c reduced, to fit Q = 448 | 24 | ≤ 84 | ≤ 130 | ≤ 136 | (iii) |
| **c reduced, to fit Q = 384** | 24 | **16** | **62** | **68** | (iii) |
| c at its floor | 24 | 1 | 47 | 53 | (iii): a level-1 error is then a cluster whose linked pairs all share a point |
| λ reduced as well, Flag2 period kept | 17 | 1–16 | 33–48 | 39–54 | (iii) and every promise of isolation |
| Gray's proof kept verbatim, c = 4(λ + 2) | 10 | 48 | 66 | 72 | λ below the Flag2 period: the rule must change |

All rows `[E]`; the level-1 column is the verified formula.

- Without touching the rule's promises, the defensible minimum is **λ = 24 and any c from 1 to 20: a box of
  53 to 72 units**. In that range c has no effect on Q (§3.1). I take c = 16, which leaves four cells of
  slack against the exposure of 73.
- Below about 50 needs a smaller λ. At λ = 17, as far as the Flag2 period allows, the box is 39–54, and Q
  does not change.

### 2.4 What the amplification step needs, and the price

**Probabilistic half (Proposition 1).** `[S]` ε_n ≤ (QU·ε_(n−1))², threshold ε < (QU)^(−2), exponent 2^n. None
of 24, 104, 200 enters. The exponent is 2^n because a level-n candidate needs two candidates one level down;
no choice of these constants changes that.

A sharper count shows where λ would enter `[E]`: a Q^n × U^n box holds QU boxes one level down, and the second
candidate must fall within λ of the first, in about 4λ² places. So ε_(n+1) ≈ 2λ²·QU·ε_n², with threshold
ε* ≈ 1/(2λ²·QU).

| | QU | Gray's bound (QU)^(−2) `[S]` | sharper count 1/(2λ²QU), λ = 24 `[E]` |
|---|---:|---:|---:|
| G16 (Q 512, U 25,920) | 1.33·10^7 | 5.7·10^−15 | 6.5·10^−11 |
| Q 384, U 19,296 | 7.41·10^6 | 1.8·10^−14 | 1.2·10^−10 |

- **Reducing c costs nothing** in either count. The clusters that move from level 1 to level 2 are those with
  two linked pairs between c and 104 apart. They add a relative (104/24)²/QU ≈ 10^−6 to the rate of level-2
  candidates. `[E]`
- **Reducing λ lowers the counted rate** (∝ λ²): the bookkeeping threshold rises as 1/λ². The price is
  mechanical: the rule must then remove errors that close together. `[E]`
- **Reducing Q and U raises both thresholds**, by (QU)² in Gray's bound: 3.2× for the last row. `[E]`
- These are thresholds of the bookkeeping. The real noise threshold of the rule is not established
  (STATUS.md).

**Mechanical half.** For a box of side B and isolation λ the rule must deliver:

| obligation | Gray `[S]` | evidence | effect of a smaller B |
|---|---|---|---|
| L0: an isolated 1–2-site error leaves no trace | Prop. 4, level 0 | `[S]` STATUS: 0 of 12,000 on G16; `[M]` 0 of 26,000 on the Q = 384 variants | none |
| L1a: an error set inside a B × B box damages at most two adjacent colonies | p. 22; needs B ≤ Q | `[S]` campaigns at 100 and 200; `[M]` §4.2 | easier |
| L1b: local structure repaired before the next gather | p. 26: 2Q + 3B_t + 2.5B_x ≤ rest | `[M]` §4.4 | easier |
| L1c: the damaged colonies' SimBits wrong at one boundary only | Prop. 4 | `[S]` campaigns; `[M]` §4.2 | none |
| self-similarity: the footprint upstairs is 1–2 adjacent cells at one upper time; footprints are λ apart | p. 27, asserted | `[E]` follows from B ≤ Q and (iv) | none |
| higher levels: Flag2 period < λ | p. 40 | 16 < 24 | none |

Nothing in the amplification argument asks for a *large* level-1 box. Reducing c makes L1a and L1b easier
and leaves the rest alone.

---

## 3. What it would buy

### 3.1 The margin and Q as functions of the box

`[M]` From `rule_g.ParamsG.check`, `compiler.end_aware_layout` and `RECIPES['G16']`:

- **Exposure rule.** The comb overhangs the working cells by H = 20. The cells of two neighbouring colonies
  that hold front state or working data are 2·margin − 2H − 3 apart, and `check()` asserts this is at least
  200. For a box of B cells: **margin ≥ ⌈(B + 43)/2⌉**.
- **Working cells.** W = Q − 2·margin holds one cell per upper bit plus two courier cells: W ≥ K + 2 = 260
  (K = 258 for G16), and W + H must be a multiple of 16 (the Flag2 rule), so **W = 268**. *REPORT §29 says the
  working cells hold "191 upper bits"; G16's layout has 258 (`cand.W`). 191 is the cell width of the
  three-copy variant.*
- **Q = 268 + 2·margin, and Q must be a multiple of 64** (`check()`: `q % 64 == 0`; REPORT §18: "for the
  bit-packed kernels". The rule needs only the multiple of 16 in the Age radix.)

| box B (cells) the margin is sized for | margin needed | Q if any Q were allowed | Q with Q ≡ 0 mod 64 | margin then | boxes that Q covers |
|---:|---:|---:|---:|---:|---|
| 200 (Gray as printed; G16) | 122 | 512 | **512** | 122 | B ≤ 201 |
| 157 (Gray's own 156, plus one cell: a footprint is counted in whole colonies) | 100 | 468 | 512 | 122 | |
| 137 | 90 | 448 | **448** | 90 | 74 ≤ B ≤ 137 |
| 100 | 72 | 412 | 448 | 90 | |
| 73 | 58 | 384 | **384** | 58 | 10 ≤ B ≤ 73 |
| 60 | 52 | 372 | 384 | 58 | |
| none: margin only for the overhang (H ≤ margin − 2) | 22 | 312 | **320** | 26 | B ≤ 9 |

`[E]` (arithmetic on the `[M]` rules.) Three things follow.

1. **Correcting 200 to Gray's real 150 or 156 buys nothing**, because of the step of 64. It would buy 44
   cells if Q could be 468.
2. **B = 100 and B = 60 land on the same steps as 137 and 73.** The useful targets are 137 and 73.
3. **Q = 384 is the floor for this route.** Q = 320 needs B ≤ 9, which no λ and c give. It is reachable only
   by dropping the exposure rule (§3.4).

Which constants reach which step (level-n extent plus one cell, §2.3) `[E]`:

| step | condition, λ = 24 | example |
|---|---|---|
| Q = 448, margin 90 | c ≤ 84 | c = 64: level-1 errors up to 110 wide |
| **Q = 384, margin 58** | **c ≤ 20** | **c = 16: level-1 errors up to 62 wide, level-n up to 68·Q^(n−1)** |

### 3.2 The gather spacing as a function of the box

`[M]` Geometry (`ParamsG.capture_age` with G16's skews): a gather starts at Age g·Q and its last lane is
captured 5Q − 4 ticks later. With gathers s·Q apart the rest between two gathers is **(s − 5)·Q + 4**:
3,588 ticks for G16 (s = 12). (With a doubled skew scale it is 5 ticks more.)

`[E]` Gray's recovery bound (p. 26) written out for a square box: T = B + (B + 4B)/2 + 2(Q + B) =
**2Q + 5.5·B**. One error must not disturb two gathers (p. 35), so the rest must be at least T:

**s ≥ 7 + (5.5·B − 4)/Q.**

| Q | B | Gray's bound 2Q + 5.5B (ticks) | smallest s | rest at that s (ticks) | blocks before the evaluation, ⌈(2s + 5)·Q/288⌉ |
|---:|---:|---:|---:|---:|---:|
| 512 | 200 | 2,124 | 10 | 2,564 | 45 |
| 512 | 150 | 1,849 | 9 | 2,052 | 41 |
| 448 | 137 | 1,650 | 9 | 1,796 | 36 |
| 384 | 200 | 1,868 | 10 | 1,924 | 34 |
| 384 | 72 | 1,164 | 9 | 1,540 | 31 |
| 384 | 62 (the level-1 extent for c = 16) | 1,109 | 8 | 1,156 | 28 |
| 320 | 200 | 1,740 | 11 | 1,924 | 30 |

- 2Q dominates: erosion at half a cell per tick across a whole colony. The box contributes 5.5·B. Going from
  200 to 72 removes 704 ticks, 1.4 to 1.8 colony lengths per gather gap. `[E]`
- G16's 12Q has two colony lengths of slack even at B = 200. That slack is the "gathers 10Q apart" option
  already on the table. `[E]`
- **The measured repair is 3 to 8 times faster than the bound** (§4.4): at most 488 ticks on G16 and 380 on
  the Q = 384 variants, with the worst values I tried. `[M]`

### 3.3 Sized variants

`[M]` Each row is a run of `experiments/size_jobs.py` on the private copy, with the 18 settings of G16's own
sizing (3 skew scales × 6 option sets). Output `repo/figs/sweep/<tag>.json`, log `logs/size_<tag>.log`. The
last-but-one column is arithmetic `[E]`: the period at G16's pass count, (blocks before E0 + 38) × 288.

| variant (tag) | Q | margin | exposure | gathers | blocks before E0 | passes NP: best / median | U best | U median | U at NP = 37 | QU best |
|---|---:|---:|---:|---|---:|---|---:|---:|---:|---:|
| G16 (repository's `g16_e29`) | 512 | 122 | 201 | 12Q | 52 | 37 / 43 | 25,920 | 27,648 | 25,920 | 2^23.66 |
| gathers 10Q (repository's `g16_v2_gather10`, 12 settings) | 512 | 122 | 201 | 10Q | 45 | 37 / 42.5 | 23,904 | 25,488 | 23,904 | 2^23.54 |
| `q512_g9` | 512 | 122 | 201 | 9Q | 41 | 37 / 42 | 22,752 | 24,192 | 22,752 | 2^23.47 |
| `q448_g12` | 448 | 90 | 137 | 12Q | 46 | 39 / 43 | 24,768 | 25,920 | 24,192 | 2^23.40 |
| `q448_g9` | 448 | 90 | 137 | 9Q | 36 | 39 / 42.5 | 21,888 | 22,896 | 21,312 | 2^23.23 |
| `q384_g12` | 384 | 58 | 73 | 12Q | 39 | 37 / 43 | 22,176 | 23,904 | 22,176 | 2^23.02 |
| **`q384_g10`** | **384** | **58** | **73** | **10Q** | 34 | 37 / 44 | **20,736** | 22,752 | 20,736 | **2^22.92** |
| `q384_g9` | 384 | 58 | 73 | 9Q | 31 | 35 / 44 | 19,296 | 21,888 | 19,872 | 2^22.82 |
| `q384_g8` | 384 | 58 | 73 | 8Q | 28 | 37 / 43 | 19,008 | 20,736 | 19,008 | 2^22.80 |
| `q320_g12` (no exposure rule) | 320 | 26 | 9 | 12Q | 33 | 39 / 42 | 21,024 | 21,888 | 20,448 | 2^22.68 |
| `q320_g9` (no exposure rule) | 320 | 26 | 9 | 9Q | 26 | 39 / 40 | 19,008 | 19,296 | 18,432 | 2^22.54 |

- **The margin alone** (same gathers): Q −25%, U 25,920 → 22,176 (−14%; medians 27,648 → 23,904). QU falls
  1.56×.
- **With the gathers at 10Q**: U 20,736, QU 1.67× below G16. At Q = 384 this spacing meets Gray's bound even
  for a 200-wide box (1,924 ≥ 1,868).
- **With the gathers at 9Q**: U 19,296 best (a lucky 35 passes; 19,872 at 37), median 21,888; QU 1.79× below
  G16. Gray's bound is met for the 72-cell box, not for 200.
- **8Q** gains almost nothing over 9Q (the scatter of the scheduler is larger) and meets the bound only for
  B ≤ 62.
- A level-2 step costs (QU)²: 2.8× less than G16 for `q384_g10`, 3.2× for `q384_g9`; about 2.7 and 2.3 hours
  against 7.4 on the RTX 4090. `[E]` (scaled from REPORT §29; not measured.)
- U does not fall in proportion to Q, because a pass still sweeps the 268 working cells (288 ticks). Only
  the blocks before the evaluation shrink: 52 → 39 → 34 → 31.

### 3.4 The other reading: no exposure rule

The repository's rule is stricter than Gray. `[S]` Gray's level-1 box "can touch at most two colonies" (p. 22),
Proposition 4's box is two colonies wide, and a level-0 error is "one or two adjacent sites" for that reason.
REPORT §16 says so itself ("Gray's Prop. 4 allows two, so this is stricter"). G5 and G6, which had no margin,
were contained with one or two adjacent wrong upper cells (REPORT §14, §15).

Without the rule the margin only holds the comb's overhang: 22 cells, Q = 320 (rows `q320_*`). No constant of
Gray's changes. With B still 200 the gathers need 11Q at that Q (table in §3.2), so U is about 19,600 at 37
passes `[E]`; `q320_g12` is the sized row that respects it. Any boundary burst wider than 9 cells can then hit
the data of both colonies. I did not build or test this variant.

### 3.5 Stacking with the options already on the table `[E]`

- **Gathers 10Q apart** is the lever of §3.2; it is in the rows above.
- **Three copies at stride 2** (REPORT §29: Q 448, U 21,056) has K = 191, so W = 204 and Q = 204 + 2·58 =
  **320**, a pass of 224 ticks, and U = (⌈23·320/224⌉ + 36)·224 = 15,456 at its 35 passes with gathers 9Q
  apart (17,472 at 12Q). Arithmetic only; not sized; it assumes the same comb.

---

## 4. CPU evidence for the reduced margin `[M]`

All on the C kernel, in the private copy. The three variants built are the best settings of `q384_g9`,
`q384_g10` and `q384_g12` (recipes `V_q384_g9`, `V_q384_g10`, `V_q384_g12`): 258 bits per cell; 16,981, 17,013
and 16,979 gates (G16: 16,767).

### 4.1 Closure and level-0 errors

- **Closure** (`run_g_period.py`): for each variant, a ring of 12 random upper cells and a ring of 16 coherent
  ones, 3 work periods each. In all 18 periods the decoded ring equals the rule applied upstairs, the special
  procedure and the Workspace-flag windows are as Gray specifies, and the colonies are healthy at the
  boundary. (`repo/figs/g_periods/V_q384_*.json`)
- Every burst run below also checks two periods of closure on its 32-colony reference ring: 11 of 11 runs.
- **Level-0 errors** (`level0_one_tick.py --healthy`): 0 of 26,000 single errors visible one tick later
  (`V_q384_g9`: 8,000 random and 6,000 inverted; `V_q384_g10`: 6,000 and 6,000). (`repo/figs/level0/`)

### 4.2 Bursts, random values

`burst_cpu.py`: a ring of 32 colonies that are consecutive cells of one healthy upper colony (upper Age 0).
One burst per run replaces every site of a w × w box by random bits at every tick. 11 phases of the work
period (gathers 1–3, two rests, early evaluation, special procedure, trickle-down window, match pass, final
program, across the commit). Places relative to the boundary b between the two middle colonies: *mid* (the
left colony's middle), *edge* (centred on b), *edgeL* / *edgeR* (the box stops one cell short of the left /
right colony's front state). The upper state is decoded at the first boundary U and the second, 2U, and
compared with the error-free ring.

| rule | width | place | runs | wrong upper cells at U: none / one / two adjacent / other | wrong at 2U | bit-identical at 2U |
|---|---:|---|---:|---|---:|---:|
| G16 (margin 122) | 72 | edge | 11 | 11 / 0 / 0 / 0 | 0 | 11 |
| G16 | 200 | edge | 11 | 11 / 0 / 0 / 0 | 0 | 11 |
| G16 | 72, 200 | mid | 22 | 6 / 16 / 0 / 0 | 0 | 22 |
| `V_q384_g9` (margin 58) | 72 | edge, edgeL, edgeR | 33 | 33 / 0 / 0 / 0 | 0 | 33 |
| `V_q384_g9` | 137 | edge, edgeL, edgeR | 33 | 14 / 17 / 2 / 0 | 0 | 33 |
| `V_q384_g9` | 200 | edge, edgeL, edgeR | 33 | 9 / 18 / 6 / 0 | 0 | 33 |
| `V_q384_g9` | 72, 137, 200 | mid | 33 | 9 / 24 / 0 / 0 | 0 | 33 |
| `V_q384_g10` (margin 58) | 72 | edge, edgeL, edgeR | 33 | 33 / 0 / 0 / 0 | 0 | 33 |
| `V_q384_g10` | 200 | edge, edgeL, edgeR | 33 | 9 / 18 / 6 / 0 | 0 | 33 |
| `V_q384_g10` | 72, 200 | mid | 22 | 6 / 16 / 0 / 0 | 0 | 22 |
| `V_q384_g12` (margin 58) | 72 | edge, edgeL, edgeR | 33 | 33 / 0 / 0 / 0 | 0 | 33 |
| `V_q384_g12` | 200 | edge, edgeL, edgeR | 33 | 9 / 19 / 5 / 0 | 0 | 33 |
| `V_q384_g12` | 72, 200 | mid | 22 | 6 / 16 / 0 / 0 | 0 | 22 |

- **The 72-cell design burst at a boundary never reached the upper state** on any variant (99 of 99), as
  the 200-cell burst does not on G16 (11 of 11; this reproduces REPORT §19 and §29 on the CPU).
- **Wider bursts on the variants** leave one upper cell wrong, or two adjacent ones in 19 of 132 boundary
  runs. That is the predicted cost.
- **Every wrong cell was gone one upper step later, and all 352 rings were bit-identical to the error-free
  ring at 2U.**
- With the SimBits and front state of the colony one further (`--mode copy`: right Address and Age, wrong
  data), 88 more bursts on `V_q384_g9` gave the same picture: 72 at a boundary 33 / 0 / 0, 200 at a boundary
  11 / 18 / 4, nothing wrong at 2U.

### 4.3 Bursts with a shifted block: the margin does not bound the damage to one colony, on G16 either

`--mode shift`: every site of the box takes the state of the site Q/2 + 7 cells to its right. The block's
Addresses agree with each other and not with their place: a misaligned partial colony, the case Gray's damage
island is about (p. 25). Extra places: *in10* (the box lies inside the right colony, starting 10 cells after
its left end), *leftm* (inside the left colony, ending at b), *reachL* (10 cells in the right colony's margin,
the rest in the left colony).

| rule | width | place | runs | wrong at U: none / one / two adjacent / other | Address/Age wrong up to … sites right of the box | wrong at 2U | identical at 2U |
|---|---:|---|---:|---|---:|---:|---:|
| G16 | 72 | edge (all in the two margins) | 11 | 2 / **9** / 0 / 0 | 476 | 0 | 11 |
| G16 | 200 | edge (all in the two margins) | 11 | 2 / **9** / 0 / 0 | 412 | 0 | 11 |
| G16 | 72 | in10 (right margin only) | 5 | 0 / **5** / 0 / 0 | 430 | 0 | 5 |
| G16 | 72 | leftm (left margin only) | 5 | 5 / 0 / 0 / 0 | 0 | 0 | 5 |
| G16 | 150 | reachL | 5 | 0 / 4 / **1** / 0 | 502 | 0 | 5 |
| G16 | 200 | reachL | 5 | 0 / 0 / **5** / 0 | 502 | 0 | 5 |
| G16, random values | 200 | reachL | 5 | 0 / 5 / 0 / 0 | 0 | 0 | 5 |
| `V_q384_g9` | 72 | edge, edgeL, edgeR | 33 | 6 / **27** / 0 / 0 | 348 | 0 | 33 |
| `V_q384_g9` | 40 | reachL | 5 | 1 / 4 / 0 / 0 | 374 | 0 | 5 |
| `V_q384_g9` | 72 | reachL | 5 | 0 / 5 / 0 / 0 | 374 | 0 | 5 |
| `V_q384_g9` | 200 | edge, edgeR, reachL | 27 | 4 / 3 / **20** / 0 | 374 | 0 | 27 |
| `V_q384_g10` | 72 | edge, in10, reachL | 33 | 7 / **26** / 0 / 0 | 374 | 0 | 33 |
| `V_q384_g10` | 200 | edge, reachL | 22 | 4 / 3 / **15** / 0 | 374 | 0 | 22 |

(Other rows of the same runs are in `results/burst_*shift*.json`: 310 shifted bursts in all.)

- **A burst lying entirely in the margins damages the right-hand colony when its values form a shifted
  block**, on G16 (9 of 11 at both widths) as on the variants. The wrong Addresses spread through the whole
  right-hand colony (up to 502 sites past the box) and stop at its end; Gray's second special rule wipes what
  they cross. The left-hand colony is never touched this way (*leftm*: 5 of 5 clean).
- **So two colonies are lost as soon as the burst also hits the left colony's data**: 5 of 5 on G16 at 200
  cells, 1 of 5 at 150. G16's exposure of 201 does not prevent this. The same box with random values damages
  one colony.
- In every one of the 310 runs the damage was at most two adjacent upper cells for one upper step, and the
  ring was bit-identical at 2U. This is what Gray's Proposition 4 promises, no more and no less.
- The existing GPU campaigns could not see this: none of their value modes (random, zero, one, invert,
  freeze, copy; REPORT §25) writes a block of consistent, misplaced Addresses. `[S]` for the modes, `[E]` for
  the conclusion.

What the margin does guarantee, by these runs `[E]`: one colony at most for any values when the burst cannot
both reach the left colony's data and enter the right colony, which needs B ≲ margin − 19. That is about 100
cells for G16 and about 40 for margin 58. With c = 16 the level-1 box is 62: between the two.

### 4.4 Repair times

Ticks from the end of the box until the last difference from the error-free ring (sampled every 4 ticks).

| rule (Q) | values | widths | Address and Age: worst | Address, Age and both Flags: worst | Gray's bound 2Q + 5.5B for B = 72 / 200 | rest between gathers |
|---|---|---|---:|---:|---|---:|
| G16 (512) | random | 72–200 | 32 | 308 | 1,420 / 2,124 | 3,588 |
| G16 (512) | shifted block | 72–200 | 232 | 488 | 1,420 / 2,124 | 3,588 |
| `V_q384_g9` (384) | random | 72–200 | 48 | 244 | 1,164 / 1,868 | 1,545 |
| `V_q384_g9` (384) | shifted block | 40–200 | 188 | 380 | 1,164 / 1,868 | 1,545 |
| `V_q384_g10` (384) | random | 72–200 | 48 | 244 | 1,164 / 1,868 | 1,929 |
| `V_q384_g10` (384) | shifted block | 72–200 | 188 | 380 | 1,164 / 1,868 | 1,929 |
| `V_q384_g12` (384) | random | 72–200 | 48 | 244 | 1,164 / 1,868 | 2,692 |

- Random values never made the Address/Age island leave the box. A shifted block made it run to the end of
  the right-hand colony, and it was still gone within 232 ticks.
- The worst repair is 0.95·Q on G16 and 0.99·Q on the variants. Gray's bound is 2Q + 5.5B. By measurement a
  rest of 2Q would do (gathers 7Q apart); by Gray's bound 9Q or 10Q. I recommend staying with the bound.

---

## 5. What would have to be re-validated, and what is at risk

A candidate with margin 58 is a new rule (its netlist contains Q, the margin and the gather Ages), so it needs
everything REPORT §29 lists for G16. Below are the items whose *content* changes.

### 5.1 Claims that become different

| today (STATUS.md, REPORT §§16, 19, 23, 25, 29) `[S]` | with margin 58 and c = 16 `[E]` |
|---|---|
| "A 200-cell burst can reach the front state or SimBits of at most one colony" (`check()`, REPORT §23) | "A 73-cell burst …". A random-valued burst of 137 or 200 cells across a boundary damaged two adjacent upper cells in 19 of 132 runs (§4.2). |
| "656 certified level-1 errors", most of them dense 100 × 100 boxes | Under (iii) with c = 16 a dense 100 × 100 box is a candidate level-2 error. The certified class becomes dense boxes up to 16 wide and sparse clusters up to 62 wide. The physical test that covers the class is the dense 72 × 72 burst. |
| 200 × 200 bursts: 64 of 64 contained, at most one upper cell wrong | "at most two adjacent upper cells wrong for one upper step" (§4.2: no exception in 308 random-valued bursts on the variants). |
| Deviations from Gray (REPORT §16): Q < 2^13, U ≠ 128Q, Q < 2K | One more: (iii) with c = 16 instead of 104, hence a box of 62 (68 above level 1) instead of 200. Gray's proof of Proposition 2 needs Q > 30.7·B; Q/B improves from 2.6 to 5.6 and still misses it. |
| Rest between gathers 3,588, above Gray's bound 2,124 | At 10Q: 1,924, above the bound for a 200-wide box (1,868). At 9Q: 1,540, above the bound for the new box (1,164) only. |

The noise claim does not weaken: Proposition 1 is unchanged and its bound improves with QU (§2.4). And one
existing sentence should change whatever is decided: boundary bursts inside the margins do reach the upper
state of the right-hand colony when their values form a shifted block (§4.3, measured on G16).

### 5.2 Tests to re-run, and with what

| test (driver) | for the new candidate |
|---|---|
| build, manifest, older recipes unchanged (`build_candidates.py`) | as for G16 |
| closure on the C kernel (`run_g_period.py`); CUDA parity and closure (`gpu_check.py`) | as for G16. Here: 18 periods on the C kernel only. |
| schedule replay (`jobsched.replay`, `replay_structured.py`) | as for G16; not done here |
| unit tests | `ColonyMarginTest` asserts margins ≥ 100 and `CombTest` asserts exposure ≥ 200: both become the recipe's box (73). `gray_errors.py`, its tests and `level1_campaign.py` have 24 and 104 as literals: they take λ and c as parameters. |
| level-0 errors (`level0_one_tick.py --healthy`) | as for G16. Here: 26,000 on the C kernel. |
| level-1 campaign (`level1_campaign.py`, with `--track`) | `--side 72` in place of `--side 100` (mid, left, right); `--side 16` dense and `--shape sparse` certified with c = 16; `--side 200` kept as the beyond-design case with the criterion "≤ 2 adjacent upper cells at one upper time"; all value modes; the five upper Ages of REPORT §29 (0, trickle-down window, pre-match and final program with the upper front hit, commit); the whole-colony batch |
| value modes | add a shifted-block mode to `gpu.noise` (§4.3). It is the only mode that exercises the damage island, and it should be run on G16 too. |
| boundary placements | add the tight placements (box ending one cell before the neighbour's front state) and the reaching one (a few cells into the right colony): with a 72-cell free zone the centred box is the only one that avoids both colonies |
| gather vote and recovery (`gather_vote_check.py`, `recovery_time.py --side 72` and `--side 200`) | needed if the gathers move: bursts at the end of a rest, and bursts whose repair runs into the next gather, with shifted values |
| colony wipes, 1 and 2 colonies (`level1_campaign.py --wipe`) | as for G16; this test carries the two-colony case |
| three levels (`three_level_g.py phases`, `closure2`, `repair2`, `copy2`) | as for G16. The level-2 colony's margin is now 58 level-1 cells: add wipes of up to 72 level-1 cells across a level-2 colony boundary. |
| noise with errors, census, per-field Proposition 4 | not repeated for G16 either: same gap |

### 5.3 Risks

1. **The repaired proof step for small c is mine** (§2.2). If it is wrong, the fallback inside Gray's own text
   is c = 104, B = 156, Q = 512: no gain. The empirical results of §4 do not depend on it.
2. **The margin may do more than the exposure rule says.** It also keeps the comb's overhang, the couriers
   and the flag cells away from the neighbour: the overhang ends 36 cells from the colony end instead of 100.
   The variants close and survive the bursts of §4, but only with the upper colony at Age 0, and nothing here
   tests the same geometry one level up.
3. **Bursts between 74 and 200 wide** lose the direct-hit protection. If the claim is meant to be "a
   200-wide burst directly hits one colony only", the margin must stay. If it is meant to be "a 200-wide burst
   damages one colony only", §4.3 shows it is already false on G16 for chosen values.
4. **9Q rests on Gray's bound for the smaller box.** 10Q keeps the bound for 200-wide bursts and costs three
   blocks (864 ticks).
5. **The CPU runs are small**: one seed, one upper state, slices of 32 colonies, three value modes, error
   boxes rather than Gray-classified sets, no per-tick Proposition-4 tracking.

---

## 6. What I could not verify

- The repaired step of Gray's proof for c < 104 (§2.2), and the level-n bound c + 2λ + 4: my arguments, not
  checked by anyone, and built on a sketch that has its own gap (24 against 25 on p. 18).
- That Gray's "Q ≥ 2^13" comes from 4600 < 3Q/4: he does not say where it comes from.
- Self-similarity (a level-n error looks like a level-(n−1) error one level up): asserted by Gray (p. 27). I
  checked only that footprints of two level-1 errors stay 24 upper cells apart in space.
- The "+1 cell" I add to the level-n extent for footprints counted in whole colonies.
- Where the owner's "108" comes from. Gray prints 104.
- Gács's β = 15 and γ = 5 beyond Definition 10.3 and the proof of Lemma 10.5.
- The level-2 step time of the variants (scaled, not run) and the stacked three-copy number (arithmetic).
- Anything about the variants on the GPU, at upper Ages other than 0, or at level 2.
- The pair experiment (§2.2) used random values, 192–384 trials per cell, and at most 48 ticks.
- REPORT §29's "191 upper bits": I believe it is a slip for 258; I did not ask.

---

## 7. Files and commands

All paths are relative to `errlevels/`. Repository code was run only from the private copy:
`cd errlevels/repo && GACS_BURST=0 PYTHONPATH=. python3 …`.

**The patches in the private copy.** (1) `gacsca/rule_g.py`: the literal 200 in `ParamsG.check` is read from
the environment variable `GACS_BURST` (default 200). (2) `gacsca/candidates.py`: the best setting of every
sweep `repo/figs/sweep/<tag>.json` is registered as the recipe `V_<tag>`. (3) `experiments/level0_one_tick.py`:
2 kernel threads instead of 4. `diff` against the repository shows nothing else in the files copied
(`gacsca/*.py`, `experiments/size_jobs.py`, `run_g_period.py`, `level0_one_tick.py`), as copied at 12:16 on
2026-10-02. None of my commands wrote into the repository. Files that changed there while this study ran
(`gacsca/gpu_roles.py`, `experiments/level2_physical.py`, `gpu_level2_bench.py`, the tests and docs) belong to
the concurrent GPU session, and the private copy does not contain them.

| what | command | output |
|---|---|---|
| sizing (§3.3) | `run_sizing.sh`; `q384_g8` is the last line of `run_bursts2.sh` | `repo/figs/sweep/<tag>.json`, `logs/size_<tag>.log` |
| classifier and box formula (§2.1) | `python3 gray_param.py`, `python3 gray_param_small_c.py` | `results/gray_param.json`, `results/gray_param_small_c.json` |
| pairs of level-0 errors (§2.2) | `../pair_cpu.py --candidate G16 --workers 2 --times 48 --per 4`; `… --times 96 --gaps 2,…,11 --dts 0,1 --K 48 --width 2 --seed 5 --tag G16_w2_K48` | `results/pair_G16.json`, `results/pair_G16_w2_K48.json` |
| build of the variants | `../build_variant.py V_q384_g9` (and `V_q384_g12`, `V_q384_g10`) | `logs/build_*.log`, `repo/figs/candidates/` |
| everything for `V_q384_g10` | `run_g10.sh` | `logs/*V_q384_g10*`, `results/burst_V_q384_g10*.json` |
| closure (§4.1) | `experiments/run_g_period.py --candidate V_q384_g9 --colonies 12 --periods 3 --seed 0 --threads 2`; `… --colonies 16 --seed 1 --coherent` | `repo/figs/g_periods/`, `logs/period_*.log` |
| level-0 errors (§4.1) | `experiments/level0_one_tick.py --candidate V_q384_g9 --healthy --trials 6000 --times 300 --mode random` (and `invert`) | `repo/figs/level0/`, `logs/level0_V_q384_g9.log` |
| bursts (§4.2–4.4) | `../burst_cpu.py --candidate … --mode … --widths … --places …`; the exact lines are in `run_bursts2.sh`, `run_bursts3.sh` and, for the first two runs, `--candidate G16 --widths 72,200 --places edge,mid` and `--candidate V_q384_g9 --widths 72,137,200 --places edge,edgeR,edgeL,mid` | `results/burst_*.json`, `logs/burst_*.log` |
| tables | `python3 summarize.py [sweeps|bursts|pairs]` | stdout |

`gray_p17-17.png` is the top of Gray's p. 17 rendered from the PDF, showing 104.
