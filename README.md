# GacsCA: a fixed-rule, self-simulating cellular automaton

One fixed, finite-state, one-dimensional local rule whose configurations simulate themselves level by level, in the style of Gács's reliable cellular automaton as explained in Gray's reader's guide. A colony of Q cells simulates one cell of the level above, and U ticks of the colony make one tick of that cell. The same rule runs at every level, with no depth parameter anywhere. Repair by the hierarchy is the intended noisy behavior; it is not proved for independent noise.

**Reliability audit, paused 2026-10-11:** no all-time iid reliability theorem or explicit proved positive noise rate is available for G17 or an isolated replacement. [Report/ROBUSTNESS.md](Report/ROBUSTNESS.md) supersedes the earlier reliability arguments, including REPORT §§31–33 and GRAY_CONSTANTS where they conflict. Its restricted proofs and counterexamples have separate scopes; they do not refute corrected Gray/Gács reliability. The [handoff](Report/ROBUSTNESS_HANDOFF.md) records the last results, open gaps and validation limits. G17/CURRENT is unchanged; nothing was committed.

## The current candidate: G17

| | Q | U | U/Q | QU | bits per cell | gates | radius | sized for a burst of |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **G17** (default) | **384** | **20,736** | 54.0 | **2^22.92** | 258 | 17,013 | 5 | 73 cells |
| G16 | 512 | 25,920 | 50.6 | 2^23.66 | 258 | 16,767 | 5 | 200 cells |

- **The rule.** It is a Boolean netlist plus a hard-wired instruction table (Gray's projection, p. 32).
- **What a colony does.** It gathers its neighbours' states three times and votes. It then evaluates the rule's *own* netlist on the upper neighbourhood with a comb of five register-file fronts; the upper cell's instruction word is fetched physically, by a match pass. Finally it commits the upper cell's new state.
- **Redundancy.** Every stored bit is held fivefold and re-voted every tick.
- **G17 against G16.** The same rule with the colony margin sized for a 73-cell burst instead of 200 and the gathers 10Q apart. Taking16 instead of Gray's104 gives smaller geometric error boxes; it does not establish the deterministic repair or higher-level induction at these constants ([reliability audit](Report/ROBUSTNESS.md)). G16's program, compiled by a job scheduler (`gacsca/jobsched.py`), takes37 passes of the comb where G15's took333.

**Established, on finite seeded tests** (see [Report/STATUS.md](Report/STATUS.md)):
- **Self-simulation.** NumPy, C and CUDA backends agree bit for bit. Closure holds over successive periods (G16 and G17: 23 periods each on random and on coherent upper states). Three-level rings are exact across a level-2 commit, and level-2 macrosteps on the level-1 automaton are exact (G15 and G16). For G16 a ring of one level-2 cell and a ring of two were each run physically for a whole level-2 step (671,846,400 ticks): the level-2 state at the end equals the rule applied to the initial one. For G17 the one-cell ring was run the same way (429,981,696 ticks, 1.7 GPU-hours): exact.
- **Level-0 and level-1 errors.** Level-0 errors vanish in one tick. Gray-certified level-1 errors leave at most one upper cell wrong for one upper step, keep every stored copy of the upper state's bits inside two colonies and two periods, and every field is exact after that (G15: 548 errors; G16: 656, of which 641 within one upper step; G17: 128 certified with the smaller class, plus 896 bursts of the design width and larger, all contained). One exception, the same for both: while the upper colony is inside its own trickle-down window, Gray's wipe rule keeps a damaged upper cell wrong for a second upper step.
- **Colony-scale errors.** Errors of 3–64 colonies are removed by level 2 (G15: 61 errors; G16 and G17: 12 errors of 3–27 colonies each).
- **The misaligned-colony limit.** Gray's requirement Q > 30.7 × box is replaced by a race: a burst leaves a whole misaligned colony only if it holds a block of shifted Addresses across a colony boundary for (5/6)(Q − w) ticks (REPORT §32; measured at five settings on G16, three on G17), and the same condition holds one level up on the level-1 automaton with the same thresholds (§33). Level-1 and level-2 errors are below it by a factor of 2.4 or more; a 200 × 200 burst of shifted states is above it on G17.

**Not established:** a noise threshold, universal repair from damaged colonies, the required noisy higher-level induction, and level-2 steps with errors or differing level-2 neighbours. Three error-free physical level-2 steps were run: G16 on rings of one and two level-2 cells,2.5 and3.9 GPU-hours, and G17 on one cell,1.7 GPU-hours; all exact. The later reliability audit separately proves noiseless complete-encoding closure and identifies an unimplemented total ROM-output completion for arbitrary noisy raw states. What each claim rests on is listed in [Report/LEDGER.md](Report/LEDGER.md).

## Where to look

| | |
|---|---|
| [Report/REPORT.md](Report/REPORT.md) | The full account, R0 → G17: design, every measurement and its receipt, failed approaches, the responses to both audits (§§25, 27), the job scheduler (§29), the role kernel and the physical level-2 steps (§30), Gray's constants and the misaligned-colony race (§§31–32), G17 (§33) |
| [Report/STATUS.md](Report/STATUS.md) | Current status, open problems, next steps |
| [Report/GACS_ROUTE.md](Report/GACS_ROUTE.md) | A study of the route towards Gács's own version: stored program, error-correcting codes, level-dependent sizes |
| [Report/ERROR_LEVELS.md](Report/ERROR_LEVELS.md) | A study of Gray's error-class constants: where 24, 104 and 200 come from, and what a smaller level-1 box would do to the colony margin, Q and U |
| [Report/GRAY_CONSTANTS.md](Report/GRAY_CONSTANTS.md) | Gray's error classes with 24 and 104 as parameters: which lemmas use which constant, a proof of the covering lemma for any separation, and what the later propositions need |
| [Report/LEDGER.md](Report/LEDGER.md) | Every statement the construction's reliability rests on, with its status: proved, argued and measured, measured only, or assumed |
| [Report/ROBUSTNESS.md](Report/ROBUSTNESS.md) | Exact all-time noise target, reliability proof audit, restricted replacement results and remaining gaps |
| [Report/ROBUSTNESS_HANDOFF.md](Report/ROBUSTNESS_HANDOFF.md) | Paused work through J309/G285, receipts, validation limits and unreviewed draft |
| [Report/audits/](Report/audits/) | Two independent audits of this work, with their scripts and logs |
| [docs/OVERVIEW.md](docs/OVERVIEW.md) | The construction in one page |
| [docs/CODE.md](docs/CODE.md) | Module map, and which driver produced which result |
| [docs/RUNNING.md](docs/RUNNING.md) | Tests, building candidates, simulating, the main experiments |
| [docs/prompts/](docs/prompts/) | The task statement and the audit prompt |
| [papers/](papers/), [papers_txt/](papers_txt/) | Gray's reader's guide, Gács 2001, and Masumori's simulation, as PDFs and as extracted text (the report cites the text by line) |
| [archive/](archive/) | Earlier work: the Q=8192, U=2^20 candidate and its repair and GPU validation, earlier fixed-rule attempts, the level-specific tower, and dead ends of the G line |

## Quick start

```sh
OPENBLAS_NUM_THREADS=1 python -m unittest -q tests.test_front_candidate     # 59 tests, about 2 minutes once the kernels are built
python -c "from gacsca import candidates; c = candidates.load(candidates.CURRENT); print(candidates.summary(c))"   # G17, compiled on first use
PYTHONPATH=. python experiments/level1_campaign.py --upper-steps 4 --side 100 --track --tag mybatch              # a level-1 error batch on G17
```

The code is in `gacsca/`, the tests in `tests/`, and the drivers in `experiments/`; the drivers default to the current candidate, `candidates.CURRENT` = G17. Generated receipts go to `figs/`, which is git-ignored. See [docs/RUNNING.md](docs/RUNNING.md).
