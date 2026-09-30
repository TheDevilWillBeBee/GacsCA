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
