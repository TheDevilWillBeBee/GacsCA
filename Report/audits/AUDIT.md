# Independent audit: R1 through G13, with G14 sizing

2026-09-30. I inspected the rule, compiler, codecs, backends, tests, experiment drivers, Gray's reader's guide, and the on-disk receipts. I ran new CPU checks on idle cores 0, 1, and 3. The GPU was occupied by other agents' campaigns; I did not run or disturb GPU jobs. All new files are in the audit namespaces. Existing source files were not edited by this audit.

## Verdict

**The construction is a genuine candidate for one-rule hierarchical self-simulation, with strong finite-run evidence, not a proof for all configurations or depths.** A candidate fixes one finite Boolean netlist and one finite instruction table; its physical transition has radius 5 and a constant state width at every level. The compiler compiles that netlist, including its controller and evaluator fields. The upper instruction word is fetched by the physical match pass. I independently observed nonzero successive one-level closure for R1, G2, G4, and G13, and one G14 period. The R1 two-level and three-level claims are supported by detailed receipts and driver code, but I did not repeat their very long runs. No G-family level-2 macrostep or level-3 macrostep has been run.

**The error evidence shows useful empirical recovery, but it does not establish Gray's error-correction claim.** The campaign's dense 200×200 masks are not, as whole sets, level-1 errors under Gray §5.1. “Repaired” tests decoded upper bits at work-period boundaries, not all simulation-structure fields. The six G8 longer “reruns” change the random fault values. No adversarial-value or all-pattern guarantee, rate threshold, or higher-level amplification theorem follows from these finite trials.

## Findings, in severity order

### 1. High — “level-1 error” is used for a box shape, not Gray's error class

**Where:** `experiments/fixed_rule/design_optimization/level1_campaign.py:14-21,153-185`; `experiments/fixed_rule/design_optimization/error_levels.py:8-16`; `gacsca/fixed_rule/design_optimization/gpu.py:18-24`; `Report/fixed_rule/design_optimization/REPORT.md:872-885`. Gray, `papers_txt/gray_readers_guide.txt:729-750,826-833`, makes 200×200 a *necessary bound* for a level-1 error, not a sufficient definition. A level-1 set must also pass linked-pair and isolation conditions, including condition (iii): it cannot contain two candidate level-1 errors separated by a 104×104 box.

The dense 200×200 mask in the G13 b34 receipt contains two disjoint two-site candidate level-1 subsets at x=16540–16541 and x=16690–16691, both at t=1536. Each pair contains two linked singleton candidate level-0 errors. The pairs are 149 sites apart, hence (104,104)-separated. The whole dense mask therefore fails Gray's condition (iii) for a *single* level-1 error. The same reasoning applies to every fully dense 200×200 scenario. Partial-density boxes are not classified by the driver either. The tests remain valid stress tests of bounded, seeded perturbations; the formal labels and any inference to *all* Gray level-1 errors are unsupported.

**Reproduction:** `checks.py` prints `gray_dense_box` with `linked_inside=True`, `separated_104=True`, and `within_box=True` in `figs/fixed_rule/design_optimization_audit/checks.log`. **Fix:** call these bounded-box bursts, and separately generate/classify sets using all of Gray's recursive conditions. Test several sparse placements and adversarial replacement values before stating a claim about the full class.

### 2. Medium — the six longer G8 runs are new faults, not reruns

**Where:** `level1_campaign.py:158-185` assigns `noise(seed + 50 + i)` by the scenario's index; `REPORT.md:894-897,926-932` says the six commit exceptions were rerun and became identical one step later.

Filtering `--phases commit` renumbers the three commit scenarios from indices 45–47 to 0–2. The original noise seeds were 102–104; the longer runs used 57–59. The boxes are at the same coordinates, but the replacement bits differ. The step-3 physical differences also differ (for b1: original 84/60/84 sites; longer run 96/0/108). Thus the longer receipts show that *other* commit bursts recovered by step 4. They do not establish when the original six did. G8 b3's three exceptions were not rerun.

**Reproduction:** `receipt_checks.py` prints all six seed and step-3 comparisons in `figs/fixed_rule/design_optimization_audit/receipt_checks.log`. **Fix:** derive each noise seed from a stable scenario identity, or persist and reuse the original `NoiseCfg`; compare the first three snapshots before extending the run.

### 3. Medium — “repaired” is narrower than full physical repair

**Where:** `level1_campaign.py:198-249`; `REPORT.md:882-887,926-932`. `repaired` is true when `wrong_upper_cells` is empty from step 2 (step 3 for a straddling burst). `healthy` in each step checks only Address and Age. The physical-state comparison is a separate `identical` flag at the final step. Gray Proposition 4, `papers_txt/gray_readers_guide.txt:1614-1622`, concerns the *simulation-structure fields* outside a bounded two-colony, two-period region.

For G8 b1's commit scenarios, all three are counted repaired, yet at step 3 their physical states differ from the reference at 84, 60, and 84 sites. The longer, different-seed runs also show physical residue at step 3. G13's fixed-rule b34 commit scenarios have 0 wrong upper cells by step 2 but still 180, 99, and 58 differing physical sites at that step; some remain at step 3. These receipts establish decoded recovery and eventual equality for the tested G13 cases, not the full fieldwise time bound of Proposition 4. The upper reference ring is separately checked exact, which is a useful guard.

**Reproduction:** read the named receipts or run the receipt inspection command listed below; `receipt_checks.log` records the G8 step-3 counts. **Fix:** report decoded recovery and full-state recovery separately; compare every simulation-structure field outside Gray's allowed space-time box and record the first exact tick, including straddling bursts.

### 4. Medium — cached candidate loading does not verify the recipe

**Where:** `gacsca/fixed_rule/design_optimization/candidates.py:164-178`; the claim is in that module's header and `REPORT.md:213-217`. `load()` checks the cached netlist digest, but does not compare cached ROM or layout with a fresh compile or trusted manifest. An altered ROM with the original netlist hash loads under the same candidate name.

**Reproduction:** `checks.py` copied R1's cache into a temporary directory, flipped one used ROM bit, redirected `candidates.CACHE`, and called `load('R1')`. Output: `accepted=True`, `same_netlist=True`, `same_rom=False`, `same_candidate_digest=False`. This affects cache integrity and the asserted loading guarantee, not the demonstrated behavior of the actual G13/G14 caches: `fresh_build.log` shows those two recipes rebuild to byte-identical ROMs and layouts. The published `receipts/candidates.json` contains R0–G8 only, despite the current blanket “every candidate” wording.

**Fix:** pin a trusted candidate digest per recipe or compare ROM and layout to a fresh build when loading in verification mode; publish a fresh all-candidate build receipt.

### 5. Low — two cost entries and a pass metric are wrong

**Where:** `REPORT.md:35-57,1179-1183`; `candidates.py:191-197`. Current G13 and G14 schemas each total **260 bits**, not the reported 262. Their Q, U, QU, and gate counts match the cached candidates. The report's per-phase ROM spans also match: G13 22/58/253 and G14 25/61/207. But `candidates.summary()['recipe_passes_used']` treats the packed front index as a page number and returns **2413** for G13 and **2354** for G14, although their last nonempty physical pages are 365 and 307 and their `NP` values are 379 and 327. The phrase that G9–G14 reduce QU by about 19× relative to G8 applies only to G14: G9 is about 2.62×, G13 about 16.66×.

**Reproduction:** `checks.log` gives Q/U/QU/width/gates and both pass metrics; `pass_spans.log` gives the per-phase spans. **Fix:** correct the width and speedup wording, and mask off front-index bits before computing a physical pass count. Keep packed selector width as a separate metric. There are 37 `test_` methods total, including the opt-in slow test; the summary's “37 plus 1” is also one too high.

### 6. Low — literal level-0 boundary equality is contradicted by the receipts

**Where:** `REPORT.md:568-579`. The G5 and G6 dense-E0 rings are described as physically equal to the reference at each boundary. Their receipts show physical-site differences `[0,0,3,6]` over four boundaries; G7/G8 show `[0,10,0]` over three. These can be fresh injections at a sampled boundary and do not by themselves refute one-tick correction. The experiment does not record each error's state exactly one tick later, so the stronger “every error is repaired in one tick” statement is not established by these boundary observations.

**Reproduction:** `receipt_checks.log` prints the four sequences. **Fix:** state the exact sampling condition, and track each injected site through the next tick (or stop noise and measure recovery after one tick) before claiming a one-tick bound.

## Construction and source fidelity

- **Fixed rule and fetch:** `rule_g.py:287-305,508-646` builds the G netlist from fixed parameters and radius-5 inputs. `compiler.py:1474-1545` and `multifront.py:780-897` compile its own output cones into the ROM. Phase A materializes the upper lookup key/selector; `rule_g.py:620-628` lets a matching physical cell load its fixed `I` word into front registers. The CPU and CUDA kernels (`machine.py:150-215`, `gpu.py:165-200`) compute their own local ROM keys; no depth or host-provided upper instruction was found in that path. `codec.py:14-47` maps every raw state bit to a distinct Info position and decodes fivefold Info by majority. These are positive code-trace conclusions, not exhaustive mathematical proofs.
- **G13/G14 comb:** `rule.py:175-247` derives front position and front index from local Age/Address. `rule_g.py:607-646` gates writes and matching outside the working interval. With margin 122 and overhang 20, the most extreme adjacent-colony front-state supports are 201 sites apart at their endpoints; a 200-site interval spans only 199 sites. `checks.log` records this bound. The three focused `CombTest` cases pass (`comb_tests.log`). These facts support the stated two-colony front-state exclusion for healthy or independently phased colonies; no general error-propagation proof was supplied.
- **Gray mechanisms:** G5 onward uses fivefold Info, Hold, mail, histories, scratch, pending writes, and a corrected front (`rule_g.py:38-39,213-235,339-353,417-476`). G6 separates three gathers by 12Q; G7 places represented bits and program slots inside margins; G8 clears scratch at the boundary. Early Flag stores, special SimBits, courier (G10 onward), and trickle-down are visible at `rule_g.py:439-490`. These are recognizable adaptations of Gray pp. 31–35 and 41.
- **Deviations and limits:** The report documents that Wf1/Wf2 are single-copy, stages have different timing, stage-start clearing is incomplete, and Gray's numerical proof assumptions do not hold (`REPORT.md:747-768`). A further explicit Gray p. 33 condition, Q ≥ 2K where K is the cell width, fails for G9–G14 (for example G13: Q=512, K=260, 2K=520), although their working intervals still fit all represented bits. This matters to source fidelity and transfer of Gray's proof, not to the observed closure. The report should state that deviation beside the margin claim.

## Report-summary claim ledger

“Verified” below means I confirmed the stated finite fact with source inspection and/or my own run. “Partially verified” means a receipt and driver support it but I did not repeat the full run, or the wording extends beyond the test. “Contradicted” denotes a concrete mismatch.

| Summary claim | Status | Evidence and limit |
|---|---|---|
| Each candidate is a fixed radius-5 rule; no depth input or changing width across levels | **Verified** | Netlist input offsets and candidate schema; `backend_checks.log` measures radius 5 for G13/G14; `codec.py` and same `Candidate` are reused. |
| Colony evaluates its own encoded controller/evaluator state and physically fetches the upper instruction | **Verified** | Code trace above; nonzero closure in `checks.log`. No external upper word appears in the physical driver. |
| Pi is compiled from the rule's own netlist with no hidden oracle | **Partially verified** | Compiler trace and fresh G13/G14 rebuild match; no formal all-state fixed-point proof. |
| Every candidate rebuilds bit-identically and all close on successive arbitrary upper states | **Partially verified** | Fresh R1/G13/G14 builds or receipts; my R1/G2/G4/G13/G14 closure runs; G9–G12 two-period receipts; all-candidate build receipt stops at G8. |
| R1 is the smallest listed candidate and has exact level-2 macrosteps | **Partially verified** | Table checked; `two_level/R1_n2_{1,2,3}_seed*.json` and driver show exact tested steps; U² runs not repeated. |
| G1–G4 add storage, gathers, flags, trickle-down and triple evaluation in G3/G4 | **Partially verified** | Source and focused tests; my G2/G4 two-period closure. Gray deviations below. |
| G5 fivefold front; G6 gather spacing; G7 margin; G8 clearing | **Verified** for mechanisms | Recipes and `rule_g.py`; numerical table in `checks.log`. Universal correction is separate. |
| G8 carries every audited Gray mechanism | **Partially verified** | Adaptations present, but single-copy Wf and altered stage/clearing rules remain. |
| G9 exact Q; G10 confined front/courier; G11 compact front; G12 single-step/proportional layout | **Partially verified** | Recipes, implementation, tests, and two-period `g_periods` receipts. I did not independently replay every program. |
| G13 five-front comb and G14 resizing, with 2.2× program speedup | **Partially verified** | Geometry, ROM phase spans and closure checked; G13/G14 width is 260, and speedup is pass-count arithmetic rather than an independent wall-time benchmark. |
| NumPy, C scalar/AVX2 and CUDA agree bitwise on arbitrary states | **Partially verified** | My G13/G14 NumPy/C checks pass at the match pass (`backend_checks.log`); GPU campaign references close, but I did not rerun arbitrary-state GPU parity while it was occupied. |
| R1 two-level rings and 24-step three-level slice are exact | **Partially verified** | Receipts internally match driver checks; slice has 24/24 equal and changing states. It is not a level-2 or level-3 step. |
| G5+ level-0 errors all disappear after one tick, with exact decoded state | **Unverified** as a universal/one-tick claim | Dense-E0 receipts support decoded accuracy; exact one-tick per-error recovery is not measured. Literal equality at every boundary is contradicted by Finding 6. |
| 662 first-batch “level-1 errors” all contained/repaired; 653 identical at last step | **Partially verified** | Receipt counts match exactly. “Level-1” is formally misclassified and “repaired” means decoded bits only (Findings 1 and 3). |
| The six G8 exceptions became identical one step later in reruns | **Contradicted** as evidence about those six | Finding 2: longer runs used different noise seeds. |
| G10 64, G11 full-colony 14, and G13 256 tested bursts all contained/repaired/identical | **Partially verified** | Counts match listed receipts; G13 b31–b33 (192) use the pre-fix identity. Fixed G13 b34–b36 provide a separate 192 successful cases. The G14 b41 receipt adds 64 successful age-0 cases. |
| Margin prevents a 200-site burst from hitting two colonies' front state | **Verified** as a geometric bound | 201-site endpoint gap for G13/G14 in `checks.log`; analogous layout check for G7–G12. |
| Upper level removes one- or two-colony wipes within one upper step | **Partially verified** | `two_level_errors/G6...` and `G8...` show decoded state exact by step 2; the physical state may lag. |
| 37 unit tests plus one opt-in slow test | **Contradicted** | There are 37 `test_` methods total, including the slow one. Three focused comb tests pass in `comb_tests.log`. |
| No threshold, level-k beyond colony scale, G-family level-2 step, or self-organization established | **Verified** as evidence limits | Drivers and receipts contain no such result. |

## Experiment interpretation

The CUDA error mask uses exact rectangular support (`gpu.py:239-255`) and deterministic replacement bits (`gpu.py:259-273`). Its dense E0 grid places one- or two-site errors at least 25 sites or ticks apart (`gpu.py:221-237`), which meets Gray's (24,24)-separation for those isolated events. The fault-free ring has its own zero-noise configuration (`level1_campaign.py:178-189`); it shares the same CUDA transition implementation, while the upper expected trajectory comes from the NumPy netlist evaluator. Thus it is independent of injection but not an independent specification of the rule.

The named phase formulae in `level1_campaign.py:44-65` use Q for gather timings and PL for program timings; for G13/G14 the match window and straddling commit box land where described. The slice runs compare the upper slice's rule trajectory to the full upper colony near the target (`level1_campaign.py:140-152`). The recorded wrap-effect distance is 29, 26, 23, then 20 upper cells across four steps. This supports target-local inference for the tested duration; the driver does not directly run the faulty full physical colony beside the slice. Counts and labels in the report should be read with that scope.

The R1 three-level run applies the same encode three times and checks 24 successive *level-1* macrosteps (`run_three_level_slice.py:35-67`). The level-2 receipts check 16,384 level-1 steps per full R1 upper work period (`run_two_level.py:76-123`). Those are meaningful hierarchical experiments. The three-level slice does not reach the next level's commit; the report explicitly acknowledges this.

`multifront.replay` (`multifront.py:900-959`) evaluates a listing against the same netlist on random 64-bit lanes. This is a useful algebraic and scratch-routing check. It reads the compiler's lane map and runs instructions in listing order; it does not model physical front timing, fivefold voting, match gating, courier, or maintenance. Physical closure and geometry tests are therefore essential independent checks of that abstraction. My G13/G14 CPU closure and the fixed G13 campaign receipts add such evidence, within their finite input coverage.

## Commands and outputs

Run from the repository root. All commands below completed successfully; their output is in `figs/fixed_rule/design_optimization_audit/`.

```sh
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=3 taskset -c 0,1,3 python -u experiments/fixed_rule/design_optimization_audit/checks.py > figs/fixed_rule/design_optimization_audit/checks.log 2>&1
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 taskset -c 0 python -u experiments/fixed_rule/design_optimization_audit/fresh_build.py > figs/fixed_rule/design_optimization_audit/fresh_build.log 2>&1
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=3 taskset -c 0,1,3 python -u experiments/fixed_rule/design_optimization_audit/backend_checks.py > figs/fixed_rule/design_optimization_audit/backend_checks.log 2>&1
PYTHONPATH=. OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=3 taskset -c 0,1,3 python -u experiments/fixed_rule/design_optimization_audit/closure_g2_g4.py > figs/fixed_rule/design_optimization_audit/closure_g2_g4.log 2>&1
PYTHONPATH=. python experiments/fixed_rule/design_optimization_audit/receipt_checks.py > figs/fixed_rule/design_optimization_audit/receipt_checks.log 2>&1
PYTHONPATH=. python experiments/fixed_rule/design_optimization_audit/pass_spans.py > figs/fixed_rule/design_optimization_audit/pass_spans.log 2>&1
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=3 taskset -c 0,1,3 python -m unittest -v tests.fixed_rule.design_optimization.test_front_candidate.CombTest.test_geometry_and_rom_columns tests.fixed_rule.design_optimization.test_front_candidate.CombTest.test_fronts_arrive_delta_apart_and_carry_in_the_overhang tests.fixed_rule.design_optimization.test_front_candidate.CombTest.test_overhang_ignores_the_fetched_word_even_in_the_match_pass > figs/fixed_rule/design_optimization_audit/comb_tests.log 2>&1
```

I also used read-only `rg`, `sed`, `git status`, `nvidia-smi`, `uptime`, `ps`, and small inline Python queries to inspect source, receipts, and machine load. The principal existing receipts are `figs/fixed_rule/design_optimization/{two_level,three_level,two_level_errors,error_levels,level1_campaign,g_periods}/`. The repo had concurrent uncommitted changes in `multifront.py` and a new `flow.py` from another agent during this audit; I did not edit them. The fresh G13/G14 builds matched the cached ROMs under the code present during the checks.
