# Task: can the current construction be proved robust to noise?

This repository (`/home/ivrl/Ehsan/Projects/GacsCA`) holds one fixed, finite-state, one-dimensional cellular-automaton rule whose configurations simulate themselves level by level, in the style of Gács's reliable cellular automaton as explained in Gray's reader's guide. A colony of Q cells simulates one cell of the level above and U ticks make one upper tick; the same rule runs at every level. The current candidate is G17 (Q = 384, U = 20,736; `gacsca/candidates.py`, `candidates.CURRENT`). Its mechanisms are Gray's, but its constants are far smaller than his, and its error-class separation constant was changed from 104 to 16.

Start with `README.md`, `docs/OVERVIEW.md`, `Report/LEDGER.md` (every statement the construction's reliability rests on, with its current status: proved, argued and measured, measured only, or assumed) and `Report/REPORT.md` §§31–33. Gray's and Gács's papers are in `papers/` and as text in `papers_txt/`. The partial arguments already in the repository (`Report/GRAY_CONSTANTS.md`, REPORT §§32–33) are material to examine, not a route to follow.

## The goal

Determine whether this construction, as it is, can be **proved** reliable against random noise: a theorem of the kind Gács and Gray state, with an explicit noise rate ε > 0 below which the hierarchy is maintained (or a bit is remembered) for all time, under independent errors at every site and tick. Either

- give the theorem, its assumptions and a complete proof for G17 (reusing Gray's or Gács's steps where they apply verbatim, and proving every step that their arguments do not cover at these constants); or
- state precisely what cannot be proved for the construction as it stands, which step fails and why, and what the smallest change to the rule or to its constants would be that makes the proof go through.

## The deliverable

A document `Report/ROBUSTNESS.md`, written for the repository owner, containing the exact statement aimed at, the proof or the list of gaps, and for every step its status (proved / Gray's or Gács's argument applies / unproved). Update `Report/LEDGER.md` to match. No claim may be stronger than what is actually proved; where you rely on an experiment (the C and CUDA simulators and the drivers in `experiments/` are available, `python3` only, one RTX 4090), say so and keep the receipt in `figs/`. Do not change the rule without flagging it as a change. Do not commit.
