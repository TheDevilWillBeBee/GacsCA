# Gray's error classes with 24 and 104 as parameters

Written 2026-10-02 by the main session, after the sub-agent study [ERROR_LEVELS.md](ERROR_LEVELS.md). The question: Gray's error classes use two constants, 24 and 104. If they are changed, do the lemmas and propositions that follow still hold, and can the two be chosen independently?

Page numbers are those of Gray's guide (`papers_txt/gray_readers_guide.txt`). What is quoted is Gray's; the proof in §3 and the audit in §5 are mine and have not been checked by anyone else. The brute-force check is `error_levels_exp/lemma_bruteforce.py`.

## 1. Answer

- **As printed, the two are not independent.** 104 is 4 · (24 + 2). Every other number of §5.1 follows from 24 in the same way: 25 = 24 + 1, 26 = 24 + 2, 52 = 2 · 26, 130 = 104 + 26, and 26 + 130 = 156, which "fits easily" into 200.
- **104 can be decoupled.** It is needed in one step of one proof (p. 18). With a different argument for that step the lemma holds for every separation c ≥ 1, whatever λ is (§3). So c is a free parameter. The size of a level-n error becomes (c + 2λ + 4) · Q^(n−1), and c + 2λ − 2 at level 1.
- **24 cannot be chosen freely.** Nothing in §5.1 constrains it, but the later propositions do, from below: the wave-speed estimates of Proposition 2, and above all the last step of Proposition 5, which needs λ larger than the Flag2 period of 16 that is built into the rule (§5). Raising λ is always safe; lowering it means changing the rule.
- **Every later use of the box size is an upper bound.** Propositions 2, 4 and 5 use "a level-n error fits into a 200 Q^(n−1) box" only in inequalities that get easier when the box shrinks. None needs the box to be large. So reducing c breaks nothing downstream.
- **What the rule must tolerate.** One level up, a level-n error must look like a level-(n−1) error. Its footprint is up to two cells wider than its box, so the rule has to handle bursts of c + 2λ + 6 cells: 158 for Gray's constants (he says 200), **70 for c = 16**. The margin of 58 cells of ERROR_LEVELS.md covers 73.

## 2. The definitions with parameters

λ replaces 24 and c replaces 104; Q and U are the colony size and the work period.

- A and B are (m, n)-*linked* if a box [x, x+m) × [y, y+n) holds a point of each, and (m, n)-*separated* otherwise.
- Candidate level-0 error: one error, or two errors on adjacent sites at one tick. Level-0 error: a candidate S with S and E∖S (λ, λ)-separated. E_0 is their union.
- Candidate level-n error: a set S ⊆ E∖E_(n−1) that (i) fits in a Q^n × U^n box and (ii) contains two disjoint candidate level-(n−1) errors that are (λQ^(n−1), λU^(n−1))-linked.
- Level-n error: a candidate that (iii) contains no two candidate level-n errors that are (cQ^(n−1), cU^(n−1))-separated, and (iv) is (λQ^n, λU^n)-separated from E∖(S ∪ E_(n−1)). E_n is E_(n−1) with all level-n errors.

Below, "a-box at scale k" means a box of aQ^k sites and aU^k ticks, and μ = λ + 2.

## 3. The three facts of §5.1

### 3.1 Every error above level n−1 lies in a candidate level-n error

**What Gray proves (pp. 17–18).** Every point of E∖E_(n−1) lies in a *minimal* candidate level-n error (2^n points). His step for level n takes a minimal candidate S1 one level down around the point, collects the nearby points, and distinguishes two cases. In the second case all nearby points lie within 52 of the point, so together with S1 they fit into a 104-box; "clearly, S satisfies condition (iii)", so the set would be a real level-(n−1) error, which is impossible. *This sentence is the only use of the value 104*: a set inside a 4μ-box cannot contain two c-separated subsets if c ≥ 4μ.

So Gray's proof needs **c ≥ 4(λ + 2)**. (It also has a small gap of its own: the second candidate is chosen (λ+1)-linked to the point, but a candidate needs λ-linked parts.)

**Lemma A (any c ≥ 1).** Let Q, U ≥ 6(λ + 2). For every n ≥ 1, every point of E∖E_(n−1) lies in a candidate level-n error that fits into a μ-box at scale n−1.

*Two remarks used below.* (a) If R is a real level-k error and a point r of E∖E_(k−1) is (λQ^k, λU^k)-linked to R, then r ∈ R: this is (iv). (b) Hence a set A ⊆ E∖E_(k−1) that fits into a λ-box at scale k is either inside E_k or disjoint from it.

*Level 1.* Let p ∈ E∖E_0. {p} is a candidate level-0 error and not a level-0 error, so some other error q is (λ, λ)-linked to p. If q were in a level-0 error R, then p would be linked to R and so in R, by the definition; then p ∈ E_0. So q ∈ E∖E_0, and {p, q} is a candidate level-1 error inside a λ-box.

*Level n ≥ 2, assuming the lemma for n−1.* Let p ∈ E∖E_(n−1), and let S1 ∋ p be a candidate level-(n−1) error inside a μ-box at scale n−2. By (b), S1 ⊆ E∖E_(n−1). Let N be the points of E∖E_(n−1) within 2μ of p at scale n−2 (in both coordinates); S1 ⊆ N.

- *Case I: a point q of E∖E_(n−1) outside N is λ-linked at scale n−1 to S1.* Take a small candidate S_q ∋ q from the lemma; S_q ⊆ E∖E_(n−1) by (b). S1 lies within μ of p and S_q within μ of q, and q is at least 2μ from p, so they are disjoint. S1 ∪ S_q is then a candidate level-n error containing p, at most λQ^(n−1) + 2μQ^(n−2) wide.
- *Case II: there is no such q.* N contains S1 and fits into a 4μ-box at scale n−2, so N is a candidate level-(n−1) error. It is not a real one, because p ∉ E_(n−1).
  - *N fails (iii).* Then N contains two c-separated candidate level-(n−1) errors. Separated sets are disjoint, and both lie in a box smaller than Q^(n−1), so they are linked at scale n−1. **N itself is a candidate level-n error containing p.** (This is the case Gray excludes with c = 104; it is his own remark on p. 17 that a candidate failing (iii) is a candidate one level up.)
  - *N satisfies (iii).* Then it fails (iv): some q ∈ E∖(N ∪ E_(n−2)) is λ-linked at scale n−1 to some t ∈ N. By (a), q ∉ E_(n−1) (otherwise t would be in E_(n−1)). Take small candidates S_t ∋ t and S_q ∋ q. If they met, q would be within 2μ of t and within 4μ of p at scale n−2, hence λ-linked to p at scale n−1, and Case I would hold. So they are disjoint, and S1 ∪ S_t ∪ S_q is a candidate level-n error containing p, at most λQ^(n−1) + 5μQ^(n−2) wide.

In every case the candidate fits into a (λ+1)-box at scale n−1, because 6μ ≤ Q. ∎

The proof does not use c at all, and it closes Gray's 24-against-25 gap by using S_t.

### 3.2 The size of a level-n error

**Lemma B.** A level-n error fits into a (c + 2λ + 4)-box at scale n−1; a level-1 error is at most c + 2λ − 2 sites wide and ticks long.

*Proof.* Let p, p′ be points of a level-n error S, with small candidates C_p, C_p′ from Lemma A. Their points are λ-linked to S at scale n, so by (iv) they belong to S. By (iii) C_p and C_p′ are not c-separated at scale n−1: a point of one is within c of a point of the other. With μ on either side, p and p′ are less than c + 2μ apart. At level 1 the candidates are pairs at most λ − 1 apart, which gives c + 2λ − 2. ∎

For Gray's constants this is 156 and 150: his "200" is a rounding. The level-1 bound is attained (four points at 0, 23, 126, 149).

### 3.3 The probability bound

Proposition 1's bound ε_n ≤ (QU · ε_(n−1))², with threshold ε < (QU)^(−2), uses one thing: a candidate level-n error contains two disjoint candidates one level down. That is condition (ii), which involves neither c nor the level-n errors themselves. **The bound does not depend on c**, and a smaller λ only makes candidates rarer. With Lemma A, the Borel–Cantelli step ("every error belongs to a level-n error for some n") goes through unchanged.

A smaller c moves clusters from level n to level n+1 (those with two linked pairs more than c apart). They are then counted, and handled, as level-(n+1) errors; the bound for that level already covers them.

### 3.4 Brute-force check

`error_levels_exp/lemma_bruteforce.py` computes E_0 and E_1 exactly from the definitions for random clustered error sets and checks Lemma A at levels 1 and 2 and Lemma B. Output in `error_levels_exp/results/lemma_bruteforce.txt`.

| λ | c | 4(λ+2) | sets | sets with level-1 errors | points above level 1 | Lemma A violated | widest level-1 error / bound |
|---:|---:|---:|---:|---:|---:|---:|---|
| 3 | 20 | 20 | 2,500 | 1,451 | 2,451 | 0 | 23 / 24 |
| 3 | 5 | 20 | 2,500 | 1,281 | 3,291 | 0 | 9 / 9 |
| 3 | 2 | 20 | 2,500 | 1,223 | 3,724 | 0 | 6 / 6 |
| 3 | 1 | 20 | 2,500 | 1,193 | 3,701 | 0 | 5 / 5 |
| 4 | 3 | 24 | 2,500 | 1,162 | 5,108 | 0 | 9 / 9 |
| 4 | 24 | 24 | 2,500 | 1,325 | 3,978 | 0 | 28 / 30 |

It is a check on small constants (Q = U = 40 or 48), not a proof. The level-2 size bound was never approached by the random sets, so that part of Lemma B is untested.

## 4. Where each printed number comes from

| Gray | in parameters | role |
|---:|---|---|
| 24 | λ | isolation of an error from the rest (iv); linking of the two halves of a candidate (ii) |
| 25 | λ + 1 | a point λ-linked to a small candidate is (λ+1)-linked to any of its points |
| 26 | λ + 2 = μ | size of a minimal candidate, in units one level down |
| 52 | 2μ | two minimal candidates this far apart are disjoint |
| 104 | 4μ | a set within 52 of a point on all sides; makes (iii) automatic in Gray's proof |
| 130 | c + μ | reach of a level-n error from one of its minimal candidates |
| 156, "200" | c + 2μ | size of a level-n error |

## 5. The later propositions

"B" is the box size, 200 in Gray. "Easier" means that the inequality has more room when the quantity changes in the direction named.

| where | what is used | condition in parameters | λ | c, B |
|---|---|---|---|---|
| Prop. 2, p. 22 | the box "can touch at most two colonies" | B ≤ Q | | smaller B easier |
| p. 22 | other level-1 errors are (24Q, 24U)-separated; the damage is repaired inside 2Q × 2U | λQ, λU well above 2Q, 2U | λ ≥ about 4 | |
| p. 23 | level-0 errors are (24, 24)-separated, so a wave loses "much less than ¼ cell per time step" | loss per error / λ ≪ ¼ | **lower bound on λ** | |
| p. 24 | Flag2 condition every 16 steps: another loss of at most ¼ | fixed by the rule | | |
| p. 25 | island grows 800, waves cover 1000, 500 steps, 2000 more, 400 steps, 1600 more | 4B, 5B, 2.5B, 10B, 2B, 8B | | smaller B easier |
| p. 25 | island < Q/2, then < 3Q/4 ("since Q ≥ 2^13") | 15B < Q/2 and 23B < 3Q/4, i.e. Q > 30.7 B | | smaller B easier |
| p. 26 | eroded within 200 + 500 + 2(Q + 200) ≪ U/32 | 2Q + 5.5B below the rest between gathers | | smaller B easier |
| Prop. 4, p. 35 | "at most one of the active stages" is disturbed | the same recovery bound | | smaller B easier |
| p. 35 | the damaged colonies are "treated at level 1 like a level-0 error" | footprint of at most two adjacent cells at one level-1 time, isolated from other footprints | **the rule must tolerate (λ−2, λ−1)-separated level-0 errors** | B ≤ Q |
| Prop. 5, p. 37 | damage of a level-k error within 2Q^k × U^k/32; other level-k errors too far to matter | as for Prop. 2, one scale up | | smaller B easier |
| p. 38 | island "several hundred times Q²" must stay below a level-3 cell | (c + 2λ + 4) · 23 < 3Q/4, the same Q > 30.7 B | | smaller B easier |
| p. 38 | left end: reversals by level-1 errors "once every 24 work periods", Flag2 delays "once every 16"; average erosion at least ½ | a/λ + b/16 ≤ ½ for losses a, b that Gray does not give | **lower bound on λ** | |
| p. 40 | right end: the Flag2 reversal "occurs every 16U² time steps", level-2 errors "once every 24U²", "just enough" | **λ > 16**, the Flag2 period | **lower bound on λ, tied to the rule** | |
| Prop. 5 | each level-k error in a box [jQ^k, (j+2)Q^k) × [t, t + U^k/16) | B Q^(k−1) ≤ Q^k | | smaller B easier |

Three things follow.

1. **c appears nowhere after §5.1 except through B**, and B only in upper bounds. A smaller c cannot break a later step.
2. **λ appears in lower bounds that come from the rule itself.** The period 16 is in the transition rule for Flag2 (p. 21) and in the repository (`maintenance.py`: the computed Age divisible by 16; `ParamsG.check`: `R % 16 == 0`). λ must exceed it for the right end of an island to be pushed back faster than level-k errors push it out (p. 40), and Gray calls 24 against 16 "just enough". A smaller λ would need a smaller Flag2 period as well, and a smaller period costs more delay at the left end (p. 38), where Gray gives no numbers. I see no way to certify a λ below 24 from the text.
3. **Lowering λ would buy nothing here anyway.** It reduces the box by 2 per unit. With c = 16 the rule must tolerate 70 cells at λ = 24 and 56 at λ = 17. Both give Q = 384; the next step, Q = 320, needs 9 (ERROR_LEVELS.md §3.1).

## 6. What the rule must tolerate, and the footprint

Self-similarity (p. 27: "level-n noise will appear as level-(n−1) noise to the simulated system") is asserted, not proved, by Gray. Two points matter for the constants.

- **Size.** A level-n error is up to c + 2λ + 4 units wide at scale n−1. It touches one colony more than its width, and its damage reaches one colony further to the right (the island ends in the right-hand damaged colony). Seen one level up it is a cluster of up to **c + 2λ + 6** cells. The same rule runs at every level, so the rule has to handle error sets inside a box of that size: 158 for (24, 104), 70 for (24, 16). Gray's 200 has 42 cells of slack over 158; a margin sized for 73 has 3 over 70. For the margin of 58 cells the largest admissible c is 19.
- **Isolation.** Two level-1 errors are (λQ, λU)-separated, but their footprints are only (λ−2, λ−1)-separated in level-1 units. So the rule must really correct level-0 errors that are a little closer than λ. This is in Gray's argument for any λ, and it is a reason not to lower λ. The measured tolerance has room: on G16 two level-0 errors at the same tick are repaired in one tick when 9 clean sites lie between them, and errors on different ticks at any distance (ERROR_LEVELS.md §2.2).

## 7. What is not covered

- Gray's Propositions 2 and 5 need Q > 30.7 B. That is 6,133 for B = 200, hence his Q ≥ 2^13, and 2,150 for B = 70. The repository's Q (512, or 384) satisfies neither. REPORT §32 explains what the assumption is for (a level-1 error must not leave a complete shifted colony), replaces it for Proposition 2 by a race condition, about Q > 2.4 B, and confirms that condition by experiment on G16. For Proposition 5 the gap stays.
- Propositions 3 to 5 are sketches in Gray's text ("You will have to trust me here"). This note checks only that their stated uses of the constants survive, not the propositions.
- Lemma A and Lemma B are my proofs. The brute-force check supports Lemma A at levels 1 and 2 and Lemma B at level 1.
