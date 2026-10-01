# Design-optimization agent status

Last update 2026-10-01 (evening) UTC.

**GPU in use** (user authorization) for the level-1 campaign, about 2 GiB of
VRAM. GPU agent: write here if you need it back.

## Candidates (details in REPORT §§16–20)

| name | Q | U | QU | what it adds |
|---|---:|---:|---:|---|
| G8 | 1024 | 1,048,576 | 2^30.0 | Gray-complete: fivefold everything incl. front, 3 voted gathers 12Q apart, special procedure, trickle-down, margin 128, Workspace clearing |
| G9 | 576 | 711,936 | 2^28.6 | exact (non-power-of-two) Q |
| G10 | 576 | 462,208 | 2^28.0 | front confined to the working area; flag courier to cells 3 and Q-3 |
| G11 | 512 | 326,400 | 2^27.3 | compact fivefold front (one register slot per cell), L = 64 |
| G12 | 512 | 217,328 | 2^26.73 | G11 + single-step front (same function) + proportional layout |
| G13 | 512 | 125,856 | 2^25.94 | comb of five fronts, five cells apart (REPORT §23) |
| G14 | 512 | 110,880 | 2^25.76 | G13 re-sized by a seeded schedule search |
| **G15** | **512** | **112,608** | **2^25.78** | G14 + Gray's stage wipes (meets Prop. 4 at the sampled times) |

All close exactly (GPU parity plus closure). Tests: 44, one of them
opt-in (slow).

## Level-1 campaign (finished batches, REPORT §19)

662 level-1 errors on G8, G11 and G12:
- all contained (never more than one wrong upper cell) and all repaired by
  the upper level within one upper step;
- 653 bit-identical to the fault-free ring at the end, the other 9 being
  G8 commit-time bursts (6 of them rerun and identical one step later);
- the reference ring was exact everywhere.

## Audit response (REPORT §25)

The independent audit's six findings are resolved:
1. **Error classes.** Bursts are relabelled. `gray_errors.py` classifies
   errors by Gray's §5.1 rules, and the campaign now uses genuine level-1
   errors and adversarial values.
2. **Seeds.** Noise seeds now follow the scenario's identity. The G8
   commit-time bursts were rerun with their original faults.
3. **Prop. 4.** It is measured on the full state. G15 adds Gray's stage
   wipes and meets it at the sampled times.
4. **Cache integrity.** Every cached candidate is checked against a trusted
   manifest of fresh builds of all 17 recipes.
5. **Numbers.** The wrong figures are corrected.
6. **Level-0.** One-tick recovery is measured directly: 0 failures in 48,000
   errors in healthy colonies.

## Robustness at three levels (REPORT §26)

- **Level-2 steps.**
  - Physical three-level rings (524,288 sites) checked against levels 1
    and 2 across a level-2 commit: 30 of 30 exact.
  - Level-2 macrosteps on the level-1 automaton: 15 of 15 exact.
- **Level-0 noise with level-1 errors** (whole upper colony, Gray's E0 grid
  in every ring): 44 of 44 certified level-1 errors contained, repaired,
  meeting Prop. 4 and bit-identical at the end.
- **Errors bigger than a colony.**
  - 1–2 colonies (25 rings, with and without E0 noise): at most two adjacent
    upper cells wrong for one upper step, then bit-identical.
  - 3–64 colonies wiped, or up to 128 level-1 cells overwritten: only
    level 2 removes these. Of 61, 52 were gone at the first level-2
    boundary. The other 9 left only the damaged level-2 cell wrong for one
    level-2 step.
- **CUDA (A100).**
  - One level-2 cell (262,144 sites) runs at 104 µs per tick: 11.7 s per
    level-1 step and 15.3 days per level-2 step.
  - Two cells: 22 days per level-2 step; eight cells: 77 days.
  - The level-1 automaton of 32 level-2 cells does a level-2 step in 6.8 s,
    which is how the level-2 tests run.

## Running

Nothing. The §26 batches are finished.

Earlier: the audit-response batches are finished (REPORT §25).
- G15: 548 certified level-1 errors and 120 larger bursts, all meeting both
  parts of Prop. 4. They include stuck-at, inverted, frozen and copied
  values, and a whole-colony run.
- G14: comparison batches.
- G8: reruns of the commit-time bursts with their original faults.

The machine restarted on 2026-10-01 around 10:15 UTC and killed detached
jobs; the interrupted batches were relaunched and completed.

## Compiler work after G14 (REPORT §24)

- Select-then-vote (`sel_front`) is the same function with 14% fewer gates.
  It shortens the one-front program by about 14%, but not the comb's.
- About fifteen scheduler and partition variants gave no candidate better
  than G14.
- The five-front finish time is front 0's serial stream.

## Next

The compiler is the limit (REPORT §§23–24). With unlimited registers the final
program needs 77 passes on one front and 22 on four; the in-order scheduler
needs about 500 and about 200.

An independent audit prompt is at the repo root:
`DESIGN_OPTIMIZATION_AUDIT_PROMPT.md`.

## CPU cores

I use 24-63 for short compiles and probes, and avoid 8-15 (u20_repair
agent).

## Approach

The construction is a bit-level "front" rule family. The physical rule is one
Boolean netlist (`gacsca/fixed_rule/design_optimization/rule.py` for family R,
`rule_g.py` for family G) plus a fixed instruction table Pi indexed by
(stored Address, psel). Gray p. 32 projection applies: there is no ROM state.

A colony evaluates the rule's *own* netlist on its encoded upper neighborhood
with a moving register-file front that executes a compiled program. The
upper cell's own instruction is fetched by a physical match pass (Gray
pp. 31–32 steps i–iii), so the host never supplies upper static data.

Gray §5.2 candidate-B maintenance (radius 5) is cross-checked against the
existing `stream28_holder_core.maintenance`. The full write-up is
[REPORT.md](REPORT.md).

## Candidates

Every entry closes: decoded upper states equal the rule applied upstairs on
arbitrary (random) upper states, over successive continuous periods.
Details are in [REPORT.md](REPORT.md).

| name | Q | U | bits/cell | gates | notes |
|---|---:|---:|---:|---:|---|
| R0 | 128 | 2^15 | 76 | 3,338 | reduced |
| R1 | 128 | 2^14 | 107 | 4,144 | reduced; closed two-level ring running |
| G1 | 256 | 2^17 | 238 | 7,455 | fivefold storage, three gathers with vote, early Flag program with SimBit procedure, Wf trickle-down |
| G2 | 256 | 2^17 | 238 | 8,035 | G1 + gated pending writes |
| G3 | 256 | 2^18 | 249 | 8,603 | G2 + triple evaluation |
| G4 | 256 | 2^19 | 250 | 8,669 | G3 with computed-geometry front clock and lookup key |
| **G5** | **512** | **2^19** | 357 | 13,383 | **fivefold front**: every simulation-structure bit, including the evaluator's, is majority-corrected every tick |

Tests: `OPENBLAS_NUM_THREADS=1 python -m unittest -q
tests.fixed_rule.design_optimization.test_front_candidate` gives **21 tests
OK** in about 52 s.

## CPU core use (to avoid collisions)

- Long two-level runs are on cores 0–7 and 40–47 until about 21:40 UTC.
- Probes and compiles use 16–31 and 48–63.
- A short probe batch overlapped cores 8–11 (the u20_repair agent's cores)
  around 16:45–16:55. I avoid 8–15 from now on.

## Finished CPU jobs

The R1 two-level rings are all done and exact at level 2:
- n2=1, seed 0: two successive level-2 steps (2^29 ticks);
- n2=2, seed 2: one level-2 step;
- n2=3, seed 1: one level-2 step.

Receipts: `figs/fixed_rule/design_optimization/two_level/*.json`. I no longer
use any CPU cores beyond short probes.

## Two-level result (18:37 UTC)

R1 two-level ring, n2=1, seed 0: all 16,384 consecutive level-1 macrosteps
(2^28 physical ticks) decoded exactly. The doubly-decoded top then **equals
the rule applied to the top (level-2 step 1)**, with 32 top bits changed.
Log: `figs/fixed_rule/design_optimization/two_level/R1_n2_1_seed0.log`. The
second level-2 step and the n2=2/n2=3 runs are still going.

## Three-level vertical slice (18:20 UTC)

R1 encoded three times (1 → 128 → 16,384 → 2,097,152 cells, same width): 24
consecutive level-1 steps, all exact. Receipt:
`three_level/R1_n3_1_seed0.json`.

## Key robustness contrast (17:30 UTC)

Each period got 256 register flips placed on the front's own cell. G5 (per-tick
fivefold front) was exact in **16/16** periods and G3 (triple evaluation) in
5/16. Receipt: `noise_probe/dense_front_s31.txt`. These are injected isolated
faults on the healthy path, not a noise-threshold result.

## Preliminary single-fault probe (healthy path; not a robustness claim)

Each period gets 50 random isolated flips in one field class. Counts are exact
periods out of 16:

| Fault class | R1 | G1 | G2 |
|---|---:|---:|---:|
| Storage | 4 | 16 | 16 |
| Front | 14 | 13 | 16 |
| Geometry | 12 | 16 | 16 |
| Flags | 16 | 16 | 16 |

With one register flip placed *at the front's own cell* per period: R1 30/32
exact, G2 29/32, G3 pending. The evaluator is unprotected in R and G1/G2, as
it is in the current Q8192 candidate. G3 targets this gap.

## Handoff written at user request

`FIXED_RULE_U20_REPAIR_PROMPT.md` (repo root) contains my audit of the
Q8192/U2^20 implementation. It covers the description ≠ literal-F hop-count
defect, the host oracle for 390 upper static words, the lack of any
continuous period, coherent-only tests, evaluator/static-ROM redundancy gaps,
open fidelity items, and two-level infeasibility at that Q/U. A
`u20_repair` agent has started from it; I have no pending requests to it.

## Early finding about the current candidate

`run_dual_capture20_events.py:62-73` preloads the 390 upper static SOURCE
words with `project_all_dual_static(upper_address, …)`. The same holds for
`gpu_validation/initial.py:71`. No physical transition performs that lookup.

## Proposed shared-file patch (not applied; the file is read-only to me)

`Report/fixed_rule/README.md` could add under its reading list:

> Parallel successor candidates (design optimization): bit-level fixed rules
> with Q=128–512, U=2^14–2^19, oracle-free self-fetch and executed closure,
> in [design_optimization/REPORT.md](design_optimization/REPORT.md).

Reason: readers of the index would otherwise miss the executed closure
results.

## Next steps

1. Record the two-level results, including level-2 macrosteps, in REPORT.md.
2. Report G3's fault probes.
3. Compiler improvements are optional: 30–45% slot utilization means U could
   drop about 2× with a better scheduler. In-order, windowed-greedy, streaming,
   dwell and window-read variants all plateaued; see REPORT §8.
