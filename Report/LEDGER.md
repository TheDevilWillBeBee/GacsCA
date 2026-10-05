# The claims, and what each one rests on

Started 2026-10-05. This is the theoretical backing of the current candidate, written as a ledger: every statement that the construction's reliability depends on, with its status.

- **proved**: a proof exists, in Gray's text or in this repository, and it applies to the candidate as it is.
- **argued and measured**: an argument exists but is not a proof (an unreviewed argument of this repository, or a sketch of Gray's), and its prediction has been checked by experiment.
- **measured only**: no argument; finite, seeded evidence.
- **assumed**: used and not checked.

The candidates are G16 (Q = 512, U = 25,920, sized for a 200-cell burst) and G17 (Q = 384, U = 20,736, sized for a 73-cell burst; [REPORT.md](REPORT.md) §33). The constants are λ = 24 (Gray's) and c = 16 in condition (iii) (Gray: 104; [GRAY_CONSTANTS.md](GRAY_CONSTANTS.md)). With them a level-1 error is at most 62 sites wide and long; seen one level up, a level-n error is at most 70 level-(n−1) cells wide.

## A. The error classes (Gray §5.1)

| | statement | status | where |
|---|---|---|---|
| A1 | Every error above level n−1 lies in a candidate level-n error, for every separation c ≥ 1 | proved (this repository, unreviewed) and checked by brute force on 15,000 random sets | GRAY_CONSTANTS.md §3.1, §3.4 |
| A2 | A level-n error fits into a (c + 2λ + 4)-box at scale n−1; a level-1 error is at most c + 2λ − 2 = 62 wide | proved (this repository); attained by the classifier | GRAY_CONSTANTS.md §3.2; `gray_errors.py` |
| A3 | ε_n ≤ (QU·ε_(n−1))², hence ε_n ≤ (Q²U²ε)^(2^n): errors of high level are rare when ε < (QU)^(−2) | proved (Gray, Proposition 1); independent of c and λ | Gray p. 19; GRAY_CONSTANTS.md §3.3 |
| A4 | With probability 1 every error belongs to a level-n error for some n | proved (Gray, from A1 and A3) | Gray p. 19 |
| A5 | Distinct level-n errors are (λQ^n, λU^n)-separated; a level-n error is that far from every higher error | proved (definition (iv)) | Gray p. 17 |

What the threshold means: (QU)^(−2) is 5.7·10^(−15) for G16 and 1.8·10^(−14) for G17. It is the threshold of the bookkeeping, not a measured noise threshold of the rule.

## B. The rule against level-0 errors

| | statement | status | evidence |
|---|---|---|---|
| B1 | In a healthy colony a level-0 error (one site, or two adjacent sites, any values) is gone one tick later | measured only: 0 of 12,000 (G16), 0 of 12,000 (G17) | `level0_one_tick.py`; REPORT §29 |
| B2 | Two level-0 errors repair in one tick when at least 9 clean sites lie between them at the same tick, or at any distance on different ticks | measured only (G16, 14,784 pairs) | ERROR_LEVELS.md §2.2 |
| B3 | Where Flag1 is raised, a hit on the stored Address has a two-tick footprint; the Flag2 erasure front shifted by a hit carries a one-bit difference to the colony end | measured, and read from Gray's rules | REPORT §25 (finding 6), §29 |

B2 is what the self-similarity (D2) needs: footprints one level up are (λ−2, λ−1) = (22, 23)-separated, and the rule tolerates far less.

## C. The rule against level-1 errors

| | statement | status | evidence |
|---|---|---|---|
| C1 | Local structure: the damage island of a level-1 error is eroded, and nothing outside the two damaged colonies changes | argued (Gray, Proposition 2, with the island estimate replaced by the race of REPORT §32) and measured | REPORT §32: five thresholds predicted and met on G16; three on G17 (§33) |
| C1a | The race condition: a block of shifted Addresses survives only if the burst holds it for at least (5/6)(Q − w) ticks; for a square burst, B ≥ (5/11)Q | argued and measured (G16: 232 repaired, 240 not; G17: 250 repaired, 300 not for a block with 42 cells in the burst, limit 285) | REPORT §32, §33 |
| C1b | Level-1 errors are below that limit: 62 against 233 (G16) and 175 (G17); the 73-cell design burst against 175 (G17) | follows from A2 and C1a | |
| C2 | Recovery of the local structure takes less than the rest between gathers, so at most one gather of a work period is disturbed | argued (Gray p. 35: 2Q + 5.5B) and measured: worst repair 490 ticks on G16 against a rest of 3,588; on G17 the Addresses are correct within 232 ticks of a 200-cell shifted burst against a rest of 1,924 | ERROR_LEVELS.md §4.4; REPORT §33 |
| C3 | Simulation structure (Gray, Proposition 4): after a level-1 error the decoded upper state is wrong in at most two adjacent colonies, at one upper time, and every field of every colony is exact again by the second period boundary | measured only: 656 certified errors on G16 and 128 on G17 plus 896 design and larger bursts on G17, all contained and bit-identical; the errors that hit while the upper colony's Flag1 is raised take two upper steps (15 of 64 on G16, 11 and 13 of 64 on G17) | REPORT §27, §29, §33 |
| C3a | Boundary bursts damage one colony only for random, stuck, inverted, frozen and copied values; a block of shifted Addresses can damage two adjacent colonies | measured (G16; on G17 one of 64 shifted blocks of the design width damaged two colonies) | REPORT §31, §33 |
| C4 | A burst wider than the margin is sized for can reach the data of two colonies directly; bursts longer than the race limit become level-2 errors | follows from the construction and C1a | REPORT §32 |

## D. Self-similarity: what level n sees

| | statement | status | evidence |
|---|---|---|---|
| D1 | The level-1 system is the same rule (same netlist, same instruction table) on the decoded colonies: closure | measured, and exact by construction of the compiler: closure over successive periods for every candidate; two full physical level-2 steps of G16 and one of G17 | REPORT §§29–30, §33 |
| D2 | A level-1 error looks like a level-0 error to the level-1 system: a footprint of at most two adjacent cells at one time, (λ−2, λ−1)-separated from other footprints | footprint: C3 (measured); separation: proved from A5 (GRAY_CONSTANTS.md §6); tolerance of the reduced separation: B2 | |
| D3 | A level-n error (n ≥ 2) looks like a level-(n−1) error one level up | measured only, for n = 2: wipes of 3–27 colonies and shifted level-1 cells are removed by level 2 (G16: 9 of 12 gone at the first level-2 boundary, 3 leaving one level-2 cell wrong once; G17: 10 of 12 gone, 2 leaving one level-2 cell wrong once) | REPORT §26, §29, §33 |
| D4 | The race of C1a one level up: a level-2 error cannot leave a misaligned level-2 cell | argued and measured: on the level-1 automaton the thresholds are (5/6)(Q − w) level-1 steps with the speeds of level 0 (G17: 250/300, 200/250, 150/200 for w = 42, 106, 170, as at level 0; G16: 300/450, 300/450, 150/300); a level-2 error lasts at most 70 level-1 steps against at least 262 (G17) and 368 (G16) needed | REPORT §33 |
| D5 | The damage island is a glider of the maintenance rule: adjacent cells whose Age lags by one step move right at 3 cells per step with Flag1 behind them, die at the colony's right end, and the flags fall back at 2 per step; the Addresses are untouched | measured at level 0 (G17: 3, 4 and 6 cells, two Ages) and at level 2 (the level-1 automaton, one-colony and two-colony rings), and read from the rule (`maintenance.py`) | REPORT §33 |

## E. Higher levels (Gray, Proposition 5)

| | statement | status | evidence |
|---|---|---|---|
| E1 | Trickle-down of Flag1 restarts the erosion of a misaligned level-1 cell | measured: a misaligned colony left by a long burst is erased in the trickle-down window of its period (G16, G17), and a misaligned level-2 cell in the window of its level-2 period (the level-1 automaton, G16 and G17); what is left one level up is 5 blank cells, whose repair starts the glider of D5, and 7 cells with wrong Info | REPORT §32, §33 |
| E2 | The right end of an island is pushed back by Flag2 trickle-down faster than higher errors push it out: needs λ > the Flag2 period 16 | assumed (Gray's "just enough", p. 40); the rule has the period, λ = 24 | GRAY_CONSTANTS.md §5 |
| E3 | Level-3 errors and several level-2 errors close together are corrected | not tested | |
| E4 | A noise threshold of the rule | not established | |

## What would raise a status

- C3 and D3 from "measured only" to "argued": a proof of Proposition 4 for this construction would have to follow the Mailbox and Workspace wipes through the five stages; Gray sketches it on pp. 35–36.
- E2 to "argued": the Flag2 trickle-down speeds are measurable on the level-1 automaton (2–5 s per level-2 step for one or two level-3 cells), as the Flag1 speeds of D4 were.
- E3: level-1-automaton runs with two level-2 errors within 24 level-2 cells, and with a level-3 error; and the level-3 period that should restore the 7 Info cells of E1 (13 hours).
