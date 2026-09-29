# Parallel-agent handoff: fixed-rule Gács/Gray self-simulation

You are joining an ongoing research project in `/scratch/Ehsan/Projects/GacsCA`.
Another coding agent is working concurrently in this same directory. This is a
shared working tree, not an isolated checkout.

## Your goal

Develop a faithful executable implementation of Gács/Gray hierarchical
self-simulation using **one fixed, finite-state local transition rule**.

Hierarchy depth must be encoded in the initial configuration. Increasing depth
must not require recompiling the transition rule, expanding the physical state
alphabet, adding another hardware register pair, or selecting a different kernel.

Initially target one, then two, then ideally three explicit hierarchy levels.
These are experimental milestones toward the fixed-rule construction—not
permission to hard-code a maximum-depth tower.

**Universality is not the goal.** Self-reference is a construction technique.
You may specialize the evaluator and rule-description language to the Gács/Gray
rule family. The construction should simulate an appropriately modified version
of its own rule; arbitrary user-program support is unnecessary.

Retain the larger scientific objective: faithful colony maintenance, local
communication, computation, encoding/decoding, simulated-layer repair, and
ultimately experimentally measured noise robustness. Do not work on GKL.

## Read before implementing

Inspect the existing project and supplied papers, especially:

- `Report/REPORT.md` and its linked audits.
- `Report/design_selfsim.md`, treating its early uniformity claims as historical
  proposals, not established results.
- Gray, pp. 27–34, particularly the hard-wiring and ProgramBit projection on
  pp. 31–32.
- Gács, §§9.2–9.3, followed by the relevant correction and amplification machinery.
- Paper extracts in `papers_txt/gray_readers_guide.txt`,
  `papers_txt/gacs_2001.txt`, and `papers_txt/masumori.txt`.

Gray explicitly describes a specialized self-simulator after eliminating
ProgramBit. Gács permits simulation of an identical or suitably modified
self-correcting rule. Do not equate self-reference with a requirement to build a
general-purpose programming platform.

## Existing evidence and limitations

The current code implements level-specific finite simulation towers with
substantial NumPy/CUDA validation. These are valuable reference fixtures, but
**do not satisfy your fixed-rule goal**.

A GPU run of `experiments.third_link_initialized` was last confirmed active,
writing:

- `figs/third_link_initialized_R3_20260924.npz`
- `figs/third_link_initialized_trace_20260924.npz`

Recheck its status rather than assuming completion. Do not stop, restart,
overwrite, or modify its dependencies.

Known source-fidelity issues remain, including the printed Flag2 persistence
counterexample and computed-SimBit timing ambiguity. Read the reports; do not
describe the baseline as completely verified.

## Architectural requirements

1. Fix the physical alphabet, local neighborhood, transition implementation, and
   hard-wired description independently of requested depth.
2. Represent simulated controller state as encoded data processed using fixed
   physical workspace. Avoid recursive host-language interpretation or
   depth-specific hardware cases.
3. If logical parameters vary by level, implement that variation through the
   fixed rule's encoded data and local computation—not external level dispatch.
4. Account for the evaluator's own state and transition in the self-description.
   A test ROM, recursive initializer, or supported-opcode inventory is not
   self-reference closure.
5. Establish an explicit encoding/decoding relation and test decoded macrosteps
   against the intended self-simulated rule, including controller fields, active
   computation, and successive work periods.
6. Define finite-depth termination through initial/boundary data consistent with
   the fixed rule, not a special top-level transition kernel.
7. Measure space and time requirements. Do not assume the existing colony size or
   work-period budget accommodates the new controller.
8. Keep all evolving dependencies genuinely local. Host-side initialization and
   diagnostic decoding are permitted; host-side replacement of simulated
   transitions is not.

Resolve underspecified mathematics through documented alternatives and
distinguishing tests. Work autonomously within your ownership area.

## Cooperation and file ownership

The other agent owns:

- Existing `gacsca` modules and CUDA backend.
- Existing tests and experiment drivers.
- Current GPU jobs and historical datasets.
- Root `REPORT.md`, `Report/REPORT.md`, and shared README integration.
- Baseline fidelity, replication, and robustness investigations.

Your default ownership is **new files only** under:

- `gacsca/fixed_rule/`
- `tests/fixed_rule/`
- `experiments/fixed_rule/`
- `Report/fixed_rule/`
- `figs/fixed_rule/`

Check whether these paths already contain work before using them. Preserve all
existing changes. Do not reset, clean, switch branches, or commit the shared tree
without coordination.

Read and reuse existing modules where appropriate, but do not modify shared
modules without an explicit handoff. If a shared change is needed, document the
proposed interface or patch in your coordination file and continue independent
work.

Use `Report/fixed_rule/STATUS.md` as your asynchronous handoff to the other agent.
Maintain:

- Current approach and its source justification.
- Files owned or being edited.
- Commands and tests run, with exact results.
- Implemented behavior versus unproved claims.
- Dependencies or requested shared changes.
- Next concrete steps.

Ask the other agent to use `Report/fixed_rule/MAIN_AGENT_NOTES.md` for replies; do
not edit that file yourself. Neither agent should edit the other's status file.
The main agent will integrate your verified findings into the compact shared
report.

The main agent currently owns GPU scheduling. Start with CPU reference work and
small tests. Coordinate before launching substantial GPU jobs or rebuilding
shared CUDA artifacts. Put any independent build products in your own namespace.

## First deliverables

Produce a source-grounded architecture and an executable vertical slice that
advances toward actual fixed-rule closure. Explain precisely what remains missing.

Include tests that would fail if:

- Rule identity or state width changed with depth.
- A purported local transition read outside its neighborhood.
- Encoding omitted raw controller state.
- Only initialization worked while simulated dynamics were absent.
- Self-reference were replaced by another depth-specific interpreter.

Maintain a concise research report in your own namespace. Preserve failed
approaches when informative. Prioritize scientific correctness and inspectability
over attractive but narrower demonstrations.
