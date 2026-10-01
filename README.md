# GacsCA: a fixed-rule, self-simulating cellular automaton

One fixed, finite-state, one-dimensional local rule whose configurations simulate themselves level by level, in the style of Gács's reliable cellular automaton as explained in Gray's reader's guide. A colony of Q cells simulates one cell of the level above, and U ticks of the colony make one tick of that cell. The same rule runs at every level, with no depth parameter anywhere, and errors of each level are removed by the level above.

## The current candidate: G15

| Q | U | U/Q | QU | bits per cell | gates | radius |
|---:|---:|---:|---:|---:|---:|---:|
| 512 | 112,608 | 220 | 2^25.78 | 260 | 17,100 | 5 |

- **The rule.** It is a Boolean netlist plus a hard-wired instruction table (Gray's projection, p. 32).
- **What a colony does.** It gathers its neighbours' states three times and votes. It then evaluates the rule's *own* netlist on the upper neighbourhood with a comb of five register-file fronts; the upper cell's instruction word is fetched physically, by a match pass. Finally it commits the upper cell's new state.
- **Redundancy.** Every stored bit is held fivefold and re-voted every tick.

**Established, on finite seeded tests** (see [Report/STATUS.md](Report/STATUS.md)):
- **Self-simulation.** NumPy, C and CUDA backends agree bit for bit. Closure holds over successive periods. Three-level rings are exact across a level-2 commit, and level-2 macrosteps are exact.
- **Level-0 and level-1 errors.** Level-0 errors vanish in one tick. Gray-certified level-1 errors leave at most one upper cell wrong for one upper step. Checked at every tick, they keep every stored copy of the upper state's bits inside two colonies and two periods, and every field is exact after that.
- **Colony-scale errors.** Errors of 3–64 colonies are removed by level 2.

**Not established:** a noise threshold, proofs for all configurations, level-3 errors, and a full physical level-2 step (about 15 GPU-days).

## Where to look

| | |
|---|---|
| [Report/REPORT.md](Report/REPORT.md) | The full account, R0 → G15: design, every measurement and its receipt, failed approaches, and the responses to both audits (§§25, 27) |
| [Report/STATUS.md](Report/STATUS.md) | Current status, open problems, next steps |
| [Report/audits/](Report/audits/) | Two independent audits of this work, with their scripts and logs |
| [docs/OVERVIEW.md](docs/OVERVIEW.md) | The construction in one page |
| [docs/CODE.md](docs/CODE.md) | Module map, and which driver produced which result |
| [docs/RUNNING.md](docs/RUNNING.md) | Tests, building candidates, simulating, the main experiments |
| [docs/prompts/](docs/prompts/) | The task statement and the audit prompt |
| [papers/](papers/) | Gray's reader's guide, Gács 2001, and Masumori's simulation (text extracts in `papers_txt/`, git-ignored) |
| [archive/](archive/) | Earlier work: the Q=8192, U=2^20 candidate and its repair and GPU validation, earlier fixed-rule attempts, the level-specific tower, and dead ends of the G line |

## Quick start

```sh
OPENBLAS_NUM_THREADS=1 python -m unittest -q tests.test_front_candidate     # 47 tests, about 1 minute
```

The code is in `gacsca/`, the tests in `tests/`, and the drivers in `experiments/`. Generated receipts go to `figs/`, which is git-ignored.
