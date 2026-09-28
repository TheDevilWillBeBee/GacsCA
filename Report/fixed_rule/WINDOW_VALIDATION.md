# Fixed-rule agent status

Updated 2026-09-25. **Full fixed-rule Gács/Gray goal active; not complete.**
Please reply in **Report/fixed_rule/MAIN_AGENT_NOTES.md**. This agent reads but
never edits that file; none was present at the latest check.

## Current approach / verified result

[WINDOW.md](WINDOW.md): separate a compact computation window from colony mail
boundaries, retaining complete controller self-reference and local program
regeneration. One **237-bit radius-one physical rule**, a complete **370-bit
represented rule**, and one compiled ROM serve every requested depth. There is
no runtime depth, program, or upper-transition callback. This construction
revision is not selected by hierarchy level; earlier candidates are preserved.

Gray pp.31–34 and Gács §§9.2–9.3 motivate compact local computation, specialized
self-description and local program reconstruction. The fixed rule includes WAIT,
packet transport, and all raw controller transitions. It uses 9,445 NAND gates,
a 27,522-cell computation window, Q=268,435,456, and U=1,370,086,072≈5.104Q.
That meets the computing-only comparison with Gray's 8Q active-update allowance.
It does **not** establish the full maintenance/repair budget or source schedule.

Two successive three-colony macrosteps were executed with distinct neighboring
words and an active NAND write at step 2. All raw states match. **One computing
self-simulation link; zero completed Gács/Gray hierarchy levels.** Address remains
static in this executed rule.

## Exact commands and results

Separate targeted runs; no aggregate full-suite claim:

- `python -m unittest discover -s tests/fixed_rule -p test_window_rule.py -v`:
  **7 passed in 5.104 s**, `figs/fixed_rule/window_rule_tests_v1.log`.
- `python -m unittest discover -s tests/fixed_rule -p test_window_world.py -v`:
  **6 passed in 1.316 s**, final `window_world_tests_v3.log`.
  Prior v1/v2 logs preserve checks before the dependency optimization and the
  strengthened nonaliased delivery fixture.
- `python -m unittest discover -s tests/fixed_rule -p test_window_initial.py -v`:
  **2 passed in 0.783 s**, `window_initial_tests_v1.log`.
- `python -m unittest discover -s tests/fixed_rule -p test_window_boundary_description.py -v`:
  **1 passed in 0.068 s**, its source hash is recorded separately because it was
  added after the macrostep experiment captured its source list.
- `python -m unittest discover -s tests/fixed_rule -p test_window_maintenance.py -v`:
  **2 passed in 0.260 s**, a separate printed-maintenance component/capacity check.

Completed CPU experiment:

`python -m experiments.fixed_rule.window_selfsim --output figs/fixed_rule/window_selfsim_v1`

- **2,740,172,144 represented physical ticks**, **506.0526903234422 s**.
- **2,223,120,652 literal core ticks** plus **517,051,492 exact WAIT/quiet skips**.
  Padding packets use exact world-lines; this is not an all-literal dense run.
- 805,306,368 physical cells represented; 82,566 explicit core cells, with a
  5,944,752-byte core array (not total process memory).
- Each macrostep: 6,730,133,697 local evaluations, no projected/lifted mismatches,
  valid boundary and no pending padding packets. Sources were archived as exact
  bytes before the run. No host output refill occurred.

Independent audit:

`python -m experiments.fixed_rule.audit_window --input figs/fixed_rule/window_selfsim_v1 --output figs/fixed_rule/window_audit_v1.json`

**Passed:** 63 archived/live sources, all 1,422 projected and 2,220 lifted
post-initial bits, complete scalar/native/NAND-description agreement, ROM/binary
identity, final physical-core decode and boundary, empty padding, active write.
Exact descriptors: `window_description_v1.json`, `window_program_v1.json`.

- ROM SHA-256: `c4ff8d6fb3c8900b0853e6df52a91be5e4a5e9c2146156dc0e3c1b532c3bfbd2`.
- Archive SHA-256: `2b01596e7c97643a5a3bccc7afd4bf637c761cc05e3fb61c45484e8f47a7187f`.
- Artifact SHA-256: `1e811f7d4ccd1936017d09d9a60a5190096dda6adcc455778f6b5597997211c1`.

## Representation limits and remaining work

The CPU representation evaluates the fixed local rule in cores and represents
canonical padding by its Address pattern plus packet trajectories. Tests cover
real boundary crossings, independent opposite tracks, local raw transitions,
WAIT versus literal execution, and rejection of noncanonical Address. It has no
representation for arbitrary damaged padding. Age/flag evolution and structural
faults require new representation invariants; do not silently reuse this shortcut
for maintenance or noise experiments.

Lazy initialization uses the same alphabet, description, ROM and kernel through
three depths. **No depth-two or depth-three dynamics were executed.** At depth
two, one top cell needs Q^2=72,057,594,037,927,936 physical cells and
1,877,135,844,688,389,184 ticks per top transition. Even explicit cores alone would
number 7,387,880,620,032. Resource estimates are not deeper execution evidence.

Missing: full local Address/Age/flag maintenance, stage clock/reset/commit timing,
radius-five communication, spatial/temporal redundancy, simulated repair, deeper
execution and noise robustness. Printed Flag2 persistence and computed-SimBit
ambiguity remain unresolved. Post-evaluation regeneration differs from Gray's
early-work-period overwrite and needs justification in the final schedule.

## Maintenance check / next concrete step

[MAINTENANCE_INTEGRATION.md](MAINTENANCE_INTEGRATION.md) records a new fixed-Q
printed-maintenance port: 67 bits, 26,799 gates, 35-bit Age, and the same Flag2
counterexample. It matches the scalar source component on 91 neighborhoods;
it is **not** integrated into the physical kernel.

`python -m experiments.fixed_rule.window_maintenance_capacity` produced
`window_maintenance_capacity_v1.json`. For literal unshared circuit concatenation,
the optimistic 77,809-cell evaluation window needs at least 5,640,063,174 gate-
traversal ticks, already above 8Q=2,147,483,648. It also exceeds the current uint16
ROM-constant capacity. This rejects that specified composition, not all possible
evaluators or geometry choices.

Next implement/evaluate a specialized field-word description **including actual
maintenance from the outset**, accounting for every interpreter field and
transition. Compare complete size/time against the NAND reference. Address the
35-bit Age representation, radius-five routing, computed-Flag1 clearing, clocked
stages and the padding invariant before claiming integrated self-simulation.
Increasing fixed Q is possible but worsens deeper experiments; it must not be a
substitute for evaluating a compact descriptor.

## Ownership and cooperation

Only authorized fixed_rule namespaces were edited. New modules:
`window_rule.py`, `window_core.c/.py`, `window_program.py`, `windowed.py`,
`windowed_native.c/.py`, `window_world.c/.py`, `window_initial.py`,
`window_maintenance.py`; five window test modules; `window_selfsim.py`,
`audit_window.py`, `window_maintenance_capacity.py`; owned reports/evidence/builds.
The capacity artifact records hashes of its read-only shared scalar oracle.

Earlier sources and evidence are preserved. Previous commands/results remain in
[REGENERATION_VALIDATION.md](REGENERATION_VALIDATION.md), [REGENERATION.md](REGENERATION.md),
[PROJECTION.md](PROJECTION.md), [BLOCK.md](BLOCK.md), and historical [REPORT.md](REPORT.md).
No shared module, main report, existing test, CUDA artifact or historical dataset
was changed. No GPU activity, process control, commit, reset or branch switch.
No shared-file handoff is currently needed.

## Environment / jobs

Authorized CPU/file operations use escalation because the normal sandbox cannot
create its bwrap namespace. No external blocker. All owned CPU jobs from this
continuation completed; the window experiment's progress file says complete and
its artifact audit passed. Main agent retains GPU scheduling. At the last shared
read-only check, no matching third-link job was visible; its checkpoint said
running at 51,118,080 physical steps with no top checks, and its trace ended at
period 3120. It was not treated as complete or modified.
