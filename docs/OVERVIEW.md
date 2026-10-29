# Overview: what is being built

**Audit status, paused 2026-10-11.** G17 remains the active candidate.
Complete noiseless encoding results and restricted repair lemmas have
been proved, but no explicit positive iid noise rate or all-time
reliability theorem is proved. The geometric error-box argument alone
does not justify the smaller colony margin or the noisy hierarchy.
[ROBUSTNESS.md](../Report/ROBUSTNESS.md) supersedes conflicting earlier
claims; [LEDGER.md](../Report/LEDGER.md) gives their exact statuses.
The [paused handoff](../Report/ROBUSTNESS_HANDOFF.md) records the last
accepted results and the incomplete post-J309 validation.

**The goal.** One fixed, finite-state, one-dimensional local rule whose configurations simulate themselves hierarchically, in the style of Gács's reliable cellular automaton as presented in Gray's reader's guide (`papers/`):
- a *colony* of Q cells simulates one cell of the level above;
- a *work period* of U ticks implements one tick of that upper cell;
- the same rule runs at every level;
- errors of each level are removed by the level above.

**The constraints.** The construction must:
- use one rule at every level, with no depth parameter anywhere (not in the rule, the state width, or a host interpreter);
- have every level-specific quantity live in the initial configuration only;
- compute everything the upper level needs physically: gathering neighbours, evaluating the rule, decoding and encoding, maintaining the colony structure, and repairing the simulated layer. This includes fetching the upper cell's instruction word.

The original task statement is [`docs/prompts/FIXED_RULE_DESIGN_OPTIMIZATION_PROMPT.md`](prompts/FIXED_RULE_DESIGN_OPTIMIZATION_PROMPT.md).

## The construction in one page

**A cell.** A physical cell carries a few hundred bits (258 for G16 and G17):
- **local structure:** Address, Age and the flags of Gray §5.2;
- **SimBits:** the bits of the upper cell's state that this colony represents;
- **Workspace:** Hold for the upper cell's next state, gathered histories, scratch, and the front's registers;
- **Mailbox:** two mail tracks.

Every simulation-structure bit is stored fivefold, across the cell and its neighbours within two sites, and re-voted every tick.

**The rule.** It is defined once, as a Boolean netlist (`gacsca/rule.py`, `gacsca/rule_g.py`), plus a hard-wired instruction table Pi[Address][page]: Gray's projection, p. 32. The table holds the program that evaluates *the same netlist* one level up. It is part of the rule, not of the cell state.

**One upper tick, inside a colony** (one work period; the Ages are G17's, with G16's in brackets):
1. **Gather.** Three gathers, at Ages 0, 10Q and 20Q (G16: 0, 12Q, 24Q), copy the neighbour colonies' SimBits into history lanes, and a vote combines them (Gray p. 35). The last lane is captured just before Age 25Q (29Q), and the evaluation starts there.
2. **Evaluate.** A comb of five register-file *fronts* sweeps the working cells pass by pass and executes the compiled program: one instruction per cell visit, fetched from Pi by the cell's own Address. The fronts read SimBits, histories and scratch, and leave the upper cell's next state in Hold. The program is one pool of gates with three deadlines:
   - **the flags.** The upper cell's new flags are computed first. The special procedure and trickle-down move them to cells 3 and Q−3 (Gray pp. 33, 41);
   - **the match pass.** Next comes the fetch key. In the match pass the one Address-dependent instruction word the upper computation needs is fetched physically (Gray pp. 31–32). Everything that does not depend on that word is computed before or after it, wherever a front has time;
   - **the end.** Every output is in Hold.
3. **Commit.** At Age U−1, Hold is copied into the SimBits. Histories and mail are wiped there, and Hold at the start of the evaluation window.

G1–G15 ran three separate programs instead (early Flag program, phase A up to the match pass, final program); G16 and G17 compile them together (REPORT §29).

**The colony margin.** The cells near the colony ends hold no simulation data, so that a burst of errors across a colony boundary cannot reach the data of two colonies at once. G16 sizes the margin (122 cells) for Gray's 200-cell level-1 box; G17 sizes it (58 cells) for the 70-cell box that follows from taking 16 instead of 104 in Gray's condition (iii) ([`Report/GRAY_CONSTANTS.md`](../Report/GRAY_CONSTANTS.md), REPORT §§31–33).

**Reading it back.** `gacsca/codec.py` encodes an upper configuration into colonies and decodes it back. "Closure" means that decoding after U ticks gives exactly the rule applied to the upper configuration.

## The candidates

The full table is in the [report summary](../Report/REPORT.md).

| | adds | Q | U |
|---|---|---:|---:|
| R0, R1 | Gray §5.2 local structure, one front, no redundancy; R1 closes over two levels | 128 | 2^15, 2^14 |
| G1–G8 | Gray's mechanisms one at a time: fivefold storage, three voted gathers, the early Flag program and special procedure, trickle-down, a fivefold front, the colony margin, Workspace clearing | 256–1024 | 2^17–2^20 |
| G9–G12 | Smaller colonies and periods: an exact non-power-of-two Q, a confined and compact front, a single-step front, a proportional layout | 512–576 | 711,936 → 217,328 |
| G13, G14 | A comb of five fronts moving in lockstep, and a seed-searched schedule | 512 | 125,856, 110,880 |
| G15 | G14 plus a wipe schedule adapted from Gray's stage wipes | 512 | 112,608 |
| G16 | G15's rule compiled by the job scheduler: one pool of gates, fronts as interchangeable workers, signed lane skews, evaluation from Age 29Q | 512 | 25,920 |
| **G17** | G16's rule with the colony margin sized for a 73-cell burst (Gray's constant 104 replaced by 16) and the gathers 10Q apart; the current candidate (`candidates.CURRENT`) | **384** | **20,736** |

## How the claims are checked

- **Exactness of execution.** NumPy, C and CUDA backends are generated from the same netlist and agree bit for bit. Every recipe rebuilds bit for bit against `gacsca/manifest.json`.
- **Self-simulation.**
  - One-level closure over successive periods.
  - Two-level rings (R1: level-2 macrosteps).
  - Three-level rings checked physically against levels 1 and 2 across a level-2 commit.
  - Level-2 macrosteps on the *level-1 automaton*, i.e. the same rule run on decoded level-1 rings.
- **Errors, using Gray's classes (§5.1).** `gacsca/gray_errors.py` classifies finite error sets.
  - *Level-0 errors* (one or two sites at one tick): must vanish in one tick.
  - *Level-1 errors* (linked clusters of level-0 errors within a c × c window, c = 104 for Gray and G16, 16 for G17, isolated from everything else): must leave at most one or two adjacent upper cells wrong for one upper step. Every stored Info copy must stay inside a box of two colonies × two periods, and every field must be exact after it. These are the two measured parts of Gray's Proposition 4.
  - *Larger errors* (whole colonies wiped, 3–64 at a time): must be removed by level 2. They are followed physically to a hand-off, then on the level-1 automaton; the hand-off itself is checked physically.
  - *Bursts across a colony boundary*: the race condition of REPORT §32 says how long a burst may hold a block of shifted Addresses before a whole misaligned colony is left behind; it is measured at level 0 and, on the level-1 automaton, one level up (§33).
- **Full physical level-2 steps.** Rings of one or two level-2 cells run for U² ticks with no hand-off (REPORT §30, §33).

The results, their scope, and what is *not* established are in [`Report/STATUS.md`](../Report/STATUS.md) and [`Report/REPORT.md`](../Report/REPORT.md). The two independent audits and the responses to them are in [`Report/audits/`](../Report/audits/) and REPORT §§25, 27.
