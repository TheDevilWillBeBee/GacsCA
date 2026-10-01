> **Note (2026-10-01, after the repository restructure).** This prompt is kept as it was given to the two auditors, so its paths refer to the layout of the time. Today: `gacsca/fixed_rule/design_optimization/` → `gacsca/`, `tests/…` → `tests/`, `experiments/…` → `experiments/`, `Report/fixed_rule/design_optimization/` → `Report/`, `figs/fixed_rule/design_optimization/` → `figs/`, and the audits themselves are in `Report/audits/` (mapping in `Report/audits/README.md`). For a third audit, use the new paths; the U20 material it mentions is in `archive/u20/`.

# Independent audit of the design-optimization work (R1 → G13)

You are an independent auditor working in `/scratch/Ehsan/Projects/GacsCA`.
Another agent (the "design-optimization agent") built a family of fixed-rule
self-simulating cellular automata, their compiler, CPU/GPU simulators, tests
and error experiments. Your job is to find out whether that work is correct
and whether its evidence supports its claims. **You decide what to read, what
to run and what to check.** Do not trust the reports, the test names or the
docstrings; treat every claim as something to verify against the code and
against executed evidence.

## The goal of the project

The target is faithful hierarchical self-simulation, in the style of Gács's
reliable cellular automaton as explained in Gray's reader's guide, under
**one fixed, finite-state local transition rule**:

- A colony of Q cells simulates one cell of the level above. U ticks of the
  colony (one work period) implement one tick of the upper cell.
- The *same* physical rule runs at every level. Hierarchy depth may appear
  only in initial or boundary data. It may not appear in the kernel, the
  state width, the register count, or a host-side recursive interpreter.
- The rule must process its own encoded controller and evaluator state:
  - local communication (gathering neighbour colonies' data);
  - computation (evaluating the rule's own transition on the upper cell's
    encoded neighbourhood);
  - encoding and decoding;
  - colony maintenance (Address/Age structure);
  - repair of the simulated layer.

  No host-side oracle may supply upper-level information that the physical
  rule does not compute itself. This includes the upper cell's instruction
  word, which must be fetched physically.
- Milestones: one level, then two, then ideally three explicit levels,
  checked by successive decoded macrosteps.
- A lower Q and U than the earlier Q=8192, U=2^20 candidate, without
  weakening the scientific claim.
- Error correction in Gray's sense is a separate claim that needs its own
  evidence:
  - level-0 errors: 1–2 sites, separated;
  - level-1 errors: a burst inside a 200×200 space-time box;
  - the upper level correcting colony-scale damage.
- Universality is not required. GKL is out of scope.

The original task statement is `FIXED_RULE_DESIGN_OPTIMIZATION_PROMPT.md`.
The sources are in `papers/`, with text extracts in `papers_txt/`:
- Gray's reader's guide, especially §5 and pp. 27–41;
- Gács 2001, especially §§9.2–9.3.

## What was built

- **Code:** `gacsca/fixed_rule/design_optimization/`
  - `netlist.py`, `rule.py` (family R), `rule_g.py` (family G): the rule as a
    Boolean netlist plus a hard-wired instruction table Pi[address][psel].
  - `maintenance.py`: Gray §5.2 colony structure.
  - `compiler.py`: single-front compiler.
  - `multifront.py`: several-front ("comb") compiler.
  - `codec.py`: encoding of an upper state into colonies, and decoding.
  - `machine.py`: NumPy reference and generated C kernel.
  - `gpu.py`: generated CUDA simulator.
  - `candidates.py`: candidate recipes and cached ROMs.
- **Tests:** `tests/fixed_rule/design_optimization/`
- **Experiment drivers:** `experiments/fixed_rule/design_optimization/`
  (closure checks, two- and three-level runs, error experiments, level-1
  campaign, sizing searches).
- **Reports:**
  - `Report/fixed_rule/design_optimization/REPORT.md` (the claims);
  - `Report/fixed_rule/design_optimization/STATUS.md`.
- **Receipts:** `figs/fixed_rule/design_optimization/` (git-ignored but
  present on disk), including JSON receipts and logs of the level-1
  campaign.

Candidates in scope run from R1 to G13; G14 is G13 re-sized.

- **R1:** smallest, one front.
- **G1–G8:** add Gray's mechanisms one by one:
  - fivefold storage;
  - three voted gathers;
  - the early Flag program and special procedure;
  - trickle-down;
  - a fivefold front;
  - the colony margin;
  - Workspace clearing.
- **G9–G12:** shrink Q and U:
  - G9: exact non-power-of-two Q;
  - G10: front confined to the working cells, with a flag courier;
  - G11: compact front, one register slot per cell holding a copy of the
    unique nearby front;
  - G12: single front step, plus proportional layout.
- **G13:** a comb of five fronts moving in lockstep. The comb overhangs the
  working cells, and fronts are no-ops there.

The report's summary lists what the author says each one establishes.

## What to audit

The author asks for an honest, adversarial review. At minimum, form your
own judgement on these points, and go beyond them wherever the code
suggests a problem.

1. **Is the construction what it claims to be?**
   - One fixed rule, with no depth-dependent behaviour anywhere.
   - The declared neighbourhood radius is respected.
   - The same state width at every level.
   - Every raw field is encoded.
   - The upper instruction word is really fetched by the physical match
     pass, not supplied by the host.
   - The table Pi is a fixed function compiled from the rule's own netlist,
     with no hidden oracle or leakage of upper state.
   - The three simulators implement the same rule.
   - Specific to G13/G14:
     - the multi-front geometry, arrival and front index;
     - the no-op overhang and the match gating;
     - the argument that a level-1 burst cannot reach two colonies' front
       state.
2. **Do the tests test what they are intended to test?**
   - Look for tests that could pass vacuously:
     - all-zero or trivially symmetric data;
     - comparisons of a component against itself or a shared code path;
     - references computed by the code under test;
     - skipped branches;
     - tolerances or `any`/`all` mistakes;
     - checks that never reach the interesting phase of a work period.
   - Past experience in this project: an acid test run on all-zero data hid
     a dropped-operation bug. Checks on nonzero data plus review found it.
   - Where it helps, perturb the code or data yourself to see whether a test
     fails when it should. Do this in scratch copies or by monkeypatching,
     never by editing existing files.
3. **Do the self-simulation claims hold?**
   - Closure: the decoded state after a work period equals the rule applied
     upstairs.
   - Successive decoded macrosteps.
   - The two- and three-level results.
   - The abstract program replay in `multifront.py`: its limits and its
     independence from the scheduler it checks.
4. **Do the error experiments measure what they say?**
   - Error injection: the level-0 separation, box sizes, and determinism.
   - Error levels as Gray §5.1 defines them.
   - The meaning of "contained", "repaired" and "identical".
   - Whether the reference ring is independent.
   - The slice rings with an Address jump.
   - The phase timings used to place bursts.
   - Whether the reported counts match the receipts.
5. **Source fidelity.**
   - Check the claims that a candidate "carries Gray's mechanisms" against
     the papers.
   - Say which deviations are documented, which are undocumented, and which
     matter.
6. **The numbers.**
   - Q, U, QU, bits per cell, gates and pass counts in the report, against
     the recipes and cached candidates.

## Ground rules

- **Independence.** Choose your own methods. You may write new tests,
  scripts or small tools.
- **Read-only.** Existing files are read-only to you: code, tests, reports,
  root files, `archive/`, and every other agent's namespace. Put your own
  files only in new namespaces:
  - `tests/fixed_rule/design_optimization_audit/`
  - `experiments/fixed_rule/design_optimization_audit/`
  - `Report/fixed_rule/design_optimization_audit/`
  - `figs/fixed_rule/design_optimization_audit/`
- **Git.** Do not switch branches, reset, clean, stage or commit. The user
  decides about commits.
- **Shared machine.** Other agents may be running jobs, including
  long-running level-1 campaigns on the GPU.
  - Keep your host RAM use below 40 GiB.
  - Check `nvidia-smi`, `uptime` and `ps` before heavy runs, and pick idle
    CPU cores. The design-optimization agent mainly uses cores 24–63, and
    another agent uses 8–15.
  - Never stop or alter a job you did not start.
- **Honesty.** Separate confirmed defects, each with a reproducing command
  and its output, from suspicions and from untested areas. Do not
  overstate. If something is correct, say so briefly, with the evidence
  you gathered.

## Deliverable

Write `Report/fixed_rule/design_optimization_audit/AUDIT.md` containing:

- A short verdict: is the construction a genuine one-rule hierarchical
  self-simulator as claimed, and is the error-correction evidence sound?
- Findings ranked by severity. For each:
  - where it is (file and line);
  - what is wrong;
  - how you established it;
  - what it invalidates;
  - a suggested fix. Describe the fix; do not apply it to existing files.
- Every claim in the report's summary marked as verified, partially
  verified, unverified or contradicted, with pointers to your evidence.
- The commands you ran, and where their outputs are.

---

# Second audit (appended 2026-10-01): the changes since the first audit

A first audit was done on 2026-09-30. It read the state at commit `7caedb2`,
plus the then-uncommitted compiler work later committed as `7c0061f`.
- Its report: `Report/fixed_rule/design_optimization_audit/AUDIT.md`.
- Its scripts: `experiments/fixed_rule/design_optimization_audit/` and
  `figs/fixed_rule/design_optimization_audit/`.
- Those files are uncommitted and belong to the user. Read them, but do
  not edit or delete them.

The author then responded to that audit and did new work. Audit everything
from `7caedb2` to `HEAD`:

```
git log --oneline 7caedb2..HEAD
git diff --stat 7caedb2 HEAD
```

The same goal, sources, ground rules and independence apply as in the
first audit above. **You decide what to read, run and check.** Treat the
new report sections (`REPORT.md` §§24–26) and the new test names as claims,
not as evidence.

## What changed since the first audit

1. **Compiler work after G14** (REPORT §24, commit `7c0061f`).
   - A rule option `sel_front` (select, then vote), in `rule.py` and
     `rule_g.py`. It is claimed to compute the same function with 14% fewer
     gates.
   - `flow.py`, a position-driven scheduler reported as a negative result.
   - New `multifront.py` options. No variant is claimed to beat G14.
2. **The response to the first audit** (REPORT §25).
   - **Error classes.**
     - `gray_errors.py` classifies finite error sets by Gray §5.1
       (conditions i–iv), with shortcuts for large dense sets: a window
       argument for extents ≤ 104, an approximate `_level0_dense`, and
       `_separated_witness`.
     - The campaign generates and labels "certified" level-1 errors: dense
       100×100 boxes, and sparse clusters (`--shape sparse`).
   - **Seeds and reruns.** Noise seeds are now derived from the scenario's
     identity. The G8 commit-time bursts were rerun with their original
     faults (`G8_b*_commit_rerun_sameseeds.json`).
   - **Full-state checks and Proposition 4.**
     - `level1_campaign.py` samples the full physical state every Q ticks.
     - It splits Proposition 4 into "time" (every field equal after the
       two-period box) and "SimBits" (stored upper-state bits confined to
       two colonies). It also records "strict" (every field confined), which
       the author argues cannot hold for Gray's construction either.
     - `prop4_fields.py` gives a field-by-field table.
     - `gather_vote_check.py` tests what Gray's three-gather vote does and
       does not fix.
   - **Adversarial values.** `gpu.py` gives error sites a value by mode:
     `random`, `zero`, `one`, `invert`, `freeze`, `copy` (the state of the
     same Address one colony away).
   - **Cache integrity.** `manifest.json` holds digests of fresh builds of
     all 17 recipes. `candidates.load()` rejects a cache that differs from
     it. `build_candidates.py` rebuilds and compares.
   - **A new candidate, G15.** G15 is G14 plus `stage_wipe` in `rule_g.py`:
     history lanes and mail are cleared at the commit, and Hold at Age E0−1.
     Its sizing comes from a seed search (order and owner seed 5). It is
     claimed to meet both parts of Proposition 4 for every tested error set.
   - **Level-0 errors.** `level0_one_tick.py` claims 0 visible errors one
     tick later, out of 48,000 injected in healthy colonies. It also claims
     a two-tick footprint where the upper level raises Flag1, which follows
     Gray's second special rule.
   - **Report-wide claims.**
     - "Undamaged colonies always make the correct level-1 transition."
     - "At level 1 every tested error looks like a level-0 error": one
       level-1 time, one cell or two adjacent ones.
     - Both are claimed over all campaign receipts (G8–G15, 2,324 error
       rings).
3. **Three levels and larger errors** (REPORT §26, commit `7c8e993`).
   - **`three_level_g.py`** runs four commands:
     - `phases`: a physical three-level ring (two level-2 cells, 524,288
       sites), checked after each level-1 step against the level-1
       automaton and the level-2 state, across a level-2 commit;
     - `closure2`: level-2 macrosteps on the *level-1 automaton*, i.e. the
       same rule run on the decoded level-1 ring;
     - `repair2`: physical wipes of k whole colonies in a slice of the
       level-1 ring, handed off to the level-1 automaton after four
       level-1 steps, then compared at level-2 boundaries;
     - `copy2`: k level-1 cells overwritten with the cells at the same
       positions in the next level-2 colony, injected directly on the
       level-1 automaton.
     - Options: `--level2-age` (a "data-rich" level-2 colony), `--target
       front|field`, `--e0` (physical noise), `--level1-e0` (noise applied
       to the level-1 automaton).
     - Headline claim: of 61 errors with k ≥ 3, 52 are gone at the first
       level-2 boundary. In the other 9, only the damaged level-2 cell is
       wrong for one level-2 step.
   - **`level1_campaign.py`** gains `--wipe k`, `--e0-all`, `--height`, and
     a new SimBit verdict.
     - "SimBits" is now the *represented* check: the majority of the five
       copies of each logical cell that holds an upper-state bit.
     - Per-copy checks are kept as `info_slots` (by holding site) and
       `info_slots_logical`.
     - The new batches are b81, b82 (level-1 errors with dense E0 noise),
       b91–b93, b95 and b96 (colony wipes and a 1000×1000 box).
   - **`gpu_level2_bench.py`** times the GPU at level-2 scale. Claims:
     104 µs/tick for one level-2 cell, 15.3 days per physical level-2 step,
     6.8 s per level-2 step on the level-1 automaton.
   - **Tests.** `test_front_candidate.py` grew from 37 tests at `7caedb2`
     to 44 (one opt-in). The new ones cover `sel_front` equivalence, cache
     integrity, the Gray classifier and value modes.

## Where the evidence is

All under `figs/fixed_rule/design_optimization/` (git-ignored, present on disk):
- `level1_campaign/G14_b7*`, `G15_b6*`, `G15_b8*`, `G15_b9*`, `G8_b*_commit_rerun_sameseeds.json`, `G9_b*`, `G15_prop4_fields_*.json`, with logs `b*.log` and launch scripts `run_*.sh`.
- `three_level/G15_*.json`, with logs `*.log` and launch scripts `run_g15_*.sh`.
- `level0/`, `gpu/G15_level2_bench.json`, `receipts/candidates.json` and `receipts/build/`.

Things that will look odd and should be checked, not assumed:
- **Different SimBit checks across batches.** The SimBit attribution changed twice during the session:
  - b81 used the holding site;
  - b82 used the logical cell;
  - b91–b96 used the represented majority, with the other two kept as extra verdicts.
  - `G15_b91_full_wipe1_holder_attribution.json` and `..._logical_attribution.json` are the earlier runs of b91 under the older checks.
- **Renamed receipt.** `G15_rich_midpass_front4.json` was renamed from a run labelled front 3. Its own `note` field says why: the comb was split by register-holding cells, and an all-zero front shifted the split.
- **Fields missing from older receipts.** Earlier `repair2` receipts lack fields the driver gained later: the destroyed level-2 bits, the hand-off residue split, and per-step level-1 fields.
- **No code version in receipts.** The `three_level` receipts do not record a source digest or commit, so which driver version produced each one must be inferred from the fields present and from timestamps.
- **Machine restart.** A restart on 2026-10-01 around 10:15 UTC killed some batches. They were relaunched, and some logs were overwritten by the relaunch.
- **Shared-GPU benchmark.** `gpu/G15_level2_bench_shared_gpu.json` is the earlier benchmark, taken while the GPU was shared.

## What to audit this time

At minimum, form your own judgement on these points:

1. **Were the first audit's six findings resolved as REPORT §25 says?**
   - Check each fix in the code and in a receipt.
   - Say for each: resolved, partially resolved, or not resolved.
2. **G15 and `stage_wipe`.**
   - Is G15 still one fixed rule with radius 5, and does it close over successive periods?
   - Is the wipe really what Gray's stage wipes do?
   - Can it wipe something the program still needs? Look at the Hold wipe at E0−1 and the commit-time wipe of histories and mail.
   - Do G15's numbers (U, gates, passes, QU) match a fresh build and the manifest?
   - Does `sel_front` compute exactly the same function?
3. **The Gray classifier.**
   - Is `gray_errors.py` a correct reading of §5.1?
   - Are the shortcuts sound?
   - Are the "certified level-1 errors" in the campaign receipts really level-1 errors?
   - Construct counterexamples if you can.
4. **The Proposition 4 verdicts.**
   - Check the box test (`prop4_check`).
   - Can sampling every Q ticks miss a violation?
   - With dense E0 noise, sites hit in the previous tick are excluded. Can that hide a persistent difference?
   - Is the "represented SimBit" check a fair reading of Gray's SimBit field, or does it hide real differences?
   - Is the author's argument that "strict" cannot hold for Gray's construction right? Check it against the reader's guide, around p. 35.
5. **Value modes and level-0 claims.**
   - Do `invert`, `freeze`, `copy` and the other modes do what is claimed, in the generated CUDA? Does the unit test check them meaningfully?
   - Are the one-tick level-0 numbers and the Flag1 footprint explanation right?
6. **The three-level hybrid. This is the newest and least reviewed part.**
   - **The hand-off from physical to the level-1 automaton.**
     - Is it valid that the decoded difference is applied to the full level-1 ring, which then continues on the level-1 automaton instead of the physical rule?
     - What exactly does the per-step closure check (away from the slice ends) establish, and what doesn't it?
     - Is the hand-off residue really confined to Info slots that hold no upper-state bit?
     - Can you find a case where a physical continuation and the level-1 automaton continuation would differ? Short physical continuations past the hand-off are feasible on the GPU.
   - **The slice construction.** Look at the 64–192 level-1 cells, the wrap at the slice ends, and the assertion that damage never reaches them.
   - **The level-2 ring.** Is the data-rich level-2 colony healthy? Does the 32-cell level-2 slice's wrap affect the middle within the steps compared?
   - **`phases`.**
     - Are the stage ages right?
     - Does the run really cross a level-2 commit?
     - Is the level-2 reference (`cand.step_numpy`) independent of the GPU kernel?
   - **`closure2`.** Is it independent evidence, or the one-level closure test again on different data?
   - **`copy2`.** Is overwriting level-1 cells directly a legitimate model of some physical error?
   - **Destroyed level-2 bits.** Is `wiped_level2_bits` correct? Check it against `codec.encode` and the copy offsets.
   - **The headline.** Recount "52 of 61 gone at the first boundary, 9 with one wrong level-2 cell for one step" from the receipts.
   - **Errors ruled out of scope.** Some wipes are called "level-2 errors that level 1 is not expected to repair" (b93, the straddling halves of b92, b95 and b96). Is that classification right, and is §26.5 actually evidence that level 2 removes those particular errors?
7. **Overclaiming.**
   - Check the summary and §26.6 ("established" and "not established") against what was run.
   - Check the CUDA timing method and the level-2 extrapolations.
   - Check every count against the receipts.

## Practical notes

- **Machine.** When this section was written, the design-optimization agent had no jobs running and the GPU was idle. Check `nvidia-smi` and `ps` anyway.
  - That agent mostly uses CPU cores 24–112.
  - Cores 56–59 are unavailable since the restart.
  - Keep host RAM below 40 GiB, and never stop or alter a job you did not start.
- **Run times.**
  - The test suite takes about 1–3 minutes.
  - A whole-upper-colony campaign batch (262,144 sites, 10 rings, 4 upper steps) takes 12–25 minutes on the GPU.
  - A `repair2` run takes 3–9 minutes, and a `copy2` run about 3 minutes.
- **Where your files go.** Put new files only in the audit namespaces, in a `round2/` subfolder of each:
  - `experiments/fixed_rule/design_optimization_audit/round2/`
  - `tests/fixed_rule/design_optimization_audit/round2/`
  - `figs/fixed_rule/design_optimization_audit/round2/`
- **Git.** As before, do not stage or commit.

## Deliverable for the second audit

Write `Report/fixed_rule/design_optimization_audit/AUDIT2.md`. Do not overwrite `AUDIT.md`. It should contain:
- A short verdict on the changes since `7caedb2`. In particular: does G15, with the §26 evidence, support the claim that the construction behaves as Gray's hierarchy predicts for the tested error classes?
- A table of the first audit's six findings: resolved, partially resolved, or not resolved, with evidence.
- New findings ranked by severity. For each: file and line, what is wrong, how you established it (a command and its output), what it invalidates, and a suggested fix. Describe the fix; do not apply it.
- Every claim in REPORT §§24–26 and in the updated summary marked verified, partially verified, unverified or contradicted, with pointers to your evidence.
- The commands you ran, and where their outputs are.
