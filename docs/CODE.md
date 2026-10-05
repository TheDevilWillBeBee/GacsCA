# Code map

Everything runs from the repository root, with the root on `PYTHONPATH`.

## `gacsca/`: the construction and its simulators

| module | role |
|---|---|
| `netlist.py` | Hash-consed Boolean netlists (AND, OR, XOR; NOT is XOR with 1) with local simplification, word helpers, `Compiled` (topological gate list), and scalar/NumPy evaluators. |
| `maintenance.py` | Gray §5.2 local structure (Address, Age, Flag1/Flag2, with candidate-B Flag2) as a netlist, for Q = 2^k or an exact Q. |
| `rule.py` | The R family and the parts shared with G: `Params`, the field schema, the front's timing (passes, dwell, arrival), the instruction format, and the netlist of one physical step. |
| `rule_g.py` | The G family, which adds Gray's redundancy and mechanisms on top of `rule.py`: fivefold storage with copy slots, three voted gathers, the early Flag program, special procedure and trickle-down, the colony margin, Workspace clearing, the confined, compact and fivefold front, the comb of fronts (`fronts`, `delta`), `sel_front`, and `stage_wipe` (G15). |
| `compiler.py` | Compiles the rule's own netlist into the single-front program, the table Pi[Address][page]: scheduling, register allocation, the layouts of upper bits over the colony (default, proportional, and `end_aware_layout` for signed skews), and the abstract replay. |
| `multifront.py` | The comb compiler: partitions the program over several fronts moving in lockstep, and the seeded schedule search used for G14/G15. |
| `jobsched.py` | The job scheduler (G16): the three programs as one pool of gates; fronts claim sub-cones, load inputs as they pass them, park values for each other in scratch, fold associative trees in arrival order; the match-pass protocol; `replay`. |
| `machine.py` | `Candidate`: netlist plus ROM plus layout; the NumPy reference step (`step_numpy`); a generated C kernel (scalar and AVX2, bit-sliced); the build cache in `figs/build/`. |
| `gpu.py` | The batched CUDA simulator, generated from the same netlist. It has block mode (one block per ring) and grid mode (cooperative, one large ring). Error injection follows Gray's classes: an E0 grid, boxes, value modes (random, zero, one, invert, freeze, copy). `track()` records exact per-tick differences between rings. |
| `gpu_roles.py` | A faster CUDA kernel for one large ring of a comb candidate, compared with `gpu.py` bit for bit in the tests: several threads per word (`Partition` decides which thread evaluates which gate, and when), and the comb's logic skipped in blocks no front arrives at (`check_guard` verifies the claim behind the skip at every build). No error injection. `RoleSim` is its simulator. |
| `codec.py` | Encode an upper configuration into colonies (fivefold SimBit copies, healthy Address and Age) and decode it back; colony health. |
| `candidates.py` | The recipes R0–G17 (parameters, layout, compile settings), `CURRENT` (the candidate the drivers default to: G17); `build`, and `load` with its cache in `figs/candidates/`. Loading is checked against the tracked `manifest.json` of fresh-build digests and recipe digests. |
| `gray_errors.py` | Gray §5.1 error classes for finite error sets: exact level-0 points, level-1 conditions (i)–(iv), an exact decision of (iii) for large sets, and bursts inside noise. |
| `manifest.json` | Trusted digests (ROM, layout, netlist, recipe) of fresh builds of all 18 recipes. |

## `tests/`

- `test_front_candidate.py`: 59 tests. Nine need a CUDA GPU, and one slow G8 test runs only with `GACSCA_SLOW=1`. They cover:
  - the netlists and compiler;
  - closure for several candidates;
  - backend parity: NumPy, C, CUDA, the GPU modes and the tracker;
  - the role kernel: its partition, the claim behind its skip (with a negative control), and equality with `gpu.py` on random states, mixed rings and every stage of the period;
  - error injection and value modes;
  - the comb and `sel_front` (with a mutation control);
  - the job scheduler: G16's ROM is the schedule's listing, replay with a mutation control, the key in front 0's registers at the match pass, the signed skews, physical closure;
  - cache integrity against the manifest, including a recipe change;
  - the Gray classifier.
- `reference_candidate_b.py`: a frozen copy of the independent U20 maintenance code that `maintenance.py` is checked against.

## `experiments/`: drivers that produce the report's evidence

Each driver writes JSON receipts under `figs/` (git-ignored); the report cites them by name.

| driver | what it runs | REPORT |
|---|---|---|
| `build_candidates.py` | Rebuilds recipes, compares with the cache, writes the manifest | §§3, 25, 27 |
| `run_g_period.py` | Continuous work periods and closure of G candidates, with probes | §§16–18 |
| `run_two_level.py`, `run_three_level_slice.py` | R1 two-level rings and a three-level vertical slice | §6 |
| `gpu_check.py` | GPU parity and closure for one candidate | §12 |
| `spacetime.py` | Space-time pictures | §13 |
| `noise_probe.py`, `error_levels.py`, `recovery_time.py` | Level-0 and burst probes on one level | §§7, 14 |
| `two_level_errors.py` | Errors on two-level rings | §15 |
| `sweep_front.py`, `sweep_comb.py`, `search_comb.py` | Sizing U for front and comb configurations; the seeded search behind G14/G15 | §§17–24 |
| `size_jobs.py` | Sizing a job-scheduled candidate: probe, then compile with fixed NPe/MP/NP until the schedule uses what the rule declares; picks the best of several settings (G16) | §29 |
| `upper_wipe_check.py` | One wrong cell in a colony at several Ages: one tick, or two inside the trickle-down window (Gray's wipe rule) | §29 |
| `misaligned_block.py` | Bursts that hold a block of shifted Addresses across a colony boundary: how long the Addresses stay wrong, whether a whole misaligned colony survives, and the upper state at the next four boundaries | §32 |
| `misaligned_block2.py` | The same race one level up, on the level-1 automaton: bursts of shifted level-1 cells across the boundary between two level-2 cells; `--n2 384` or `768` follows a block that survives through a complete level-2 colony (one or two level-3 cells) | §33 |
| `replay_structured.py` | Replays the job scheduler's listing on neighbourhoods taken from a running colony (fronts arriving, the match pass), where random inputs exercise little | §29 |
| `level2_single_ring.py` | Random level-1 damage in a ring of one level-2 cell, for two candidates: shows why that ring is not a test of level 2 | §29 |
| `level1_campaign.py` | The error campaign: errors at every stage of the work period, Gray-classified, all fields compared. Options: `--track` (per-tick checks), `--continue-level2` (follow errors to level-2 boundaries) | §§19, 23, 25–27 |
| `level0_one_tick.py` | Gray's one-tick property for level-0 errors | §25 |
| `prop4_fields.py`, `gather_vote_check.py` | Proposition 4 field by field; what the gather vote fixes | §25 |
| `three_level_g.py` | Three levels: `phases`, `closure2`, `repair2` (physical errors followed to level 2, with `--verify-handoff`), `copy2` | §§26–27 |
| `gpu_level2_bench.py`, `gpu_kernel_study.py` | CUDA cost at level-2 scale; where the kernel's time goes | §§26, 28 |
| `gpu_roles_bench.py` | `gpu.py` against `gpu_roles.py` on one and two level-2 cells, during the gathers and during the program | §30 |
| `level2_physical.py` | A full physical level-2 step: a ring of level-2 cells run for U² ticks, checked against the level-1 automaton and the reference kernel on the way and against the rule at the end; checkpoints and resumes | §30 |
| `campaign_census.py`, `reclassify_receipts.py` | Census of the campaign receipts (`Report/campaign_census.json`); re-certification of every error's Gray class | §27 |
