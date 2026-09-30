# Agent 1: validate and improve dense GPU execution of the fixed-rule CA

You are working in `/scratch/Ehsan/Projects/GacsCA` concurrently with a second
agent investigating design optimization. This is a **shared working tree**.
Your task is to establish whether a genuinely dense GPU simulation of the
current Gács/Gray fixed-rule candidate behaves as intended, improve the
executor where justified, and produce reproducible evidence. Continue the work;
do not stop at a plan or a short throughput benchmark.

## Project and current evidence

The scientific goal is hierarchical self-simulation using **one fixed,
finite-state local rule**, with depth represented by initial/boundary data.
Universality is unnecessary; Gray's specialized hard-wiring and ProgramBit
projection are relevant. The current candidate has Q=8192, U=2^20, radius
seven, a 6,465-bit physical alphabet, 421 typed raw state words, and a
14,830-operation complete own-rule description. The same encoded spatial
evaluator is invoked twice per work period. The active local transition is
`gacsca.fixed_rule.stream28_dual_pass20.local_step`. Do not work on GKL.

Read [the current index](Report/fixed_rule/README.md),
[the construction report](Report/fixed_rule/DUAL_PASS_U20.md),
[the macrostep audit](Report/fixed_rule/U20_MACROSTEP_AUDIT.md),
[the dense GPU report](Report/fixed_rule/DENSE_GPU_EXECUTOR20.md), and
[the current status](Report/fixed_rule/STATUS.md) before implementation.
Read Gray pp. 27–34 and Gács §§9.2–9.3 from the PDFs in `papers/` or the
extracts `papers_txt/gray_readers_guide.txt` and `papers_txt/gacs_2001.txt`.
The archived finite tower under `archive/legacy_tower/` is a reference fixture,
not the fixed rule. Its printed Flag2 persistence counterexample and the
computed-SimBit timing question remain source-fidelity caveats.

The current literal CUDA reference is
`gacsca/fixed_rule/stream28_dual_dense_gpu20.{py,cu}`; the faster backend is
`stream28_dual_dense_gpu20_tiled.{py,cu}`. The latter executes the complete
physical F at every site and tick. It passed short raw parity tests and measured
14.037 ms/tick on 31 colonies for 1,000 ticks; four U periods would take about
16.35 hours at that rate. That is a projection, **not** a full-period result.
Existing event-composed macrostep runs physically check selected endpoints and
both evaluator invocations, but skip quiet intervals. They are not evidence of
continuous all-fields U-tick evolution or successive decoded macrosteps.

## Your work

1. Map the complete physical state, valid initialization, phase schedule, and
   decoding relation. Build a reproducible initializer for a closed lower ring
   whose colonies carry varied, coherent represented upper states and the
   Address-projected static description. Establish which ring size avoids
   relevant neighborhood aliasing. Do not mistake the benchmark's repeated
   active-evaluator fixture for a full-period initializer.
2. Validate the dense executor against independent local-rule implementations
   on arbitrary typed neighborhoods, active computation, packet motion,
   boundary wrap, and sampled whole-ring transitions. Compare **all 421 raw
   words**, including controller, mail, heads, evaluator workspace, and static
   source fields where applicable. Verify the same rule description, physical
   alphabet, and kernel apply at every tick and represented depth.
3. Run uninterrupted dense physical trajectories from the valid initializer.
   Place read-only checkpoints on both sides of the known gather, evaluator,
   Holder, Signal/Wf, reset, and Info-commit boundaries derived from the rule
   constants and reports; also check U−1, U, U+1 and successive U boundaries.
   Check full-state hashes, selected raw states, physical invariants, and all
   decoded represented controller fields against independent predictions.
   Compare decoded macrosteps with the intended upper local F where the
   encoding relation applies. Do not insert an upper-state oracle, replace
   physical transitions on the host, skip ticks in a run called dense, or
   reinitialize at a work boundary. Start with bounded pilots; pursue at least
   one full U and then consecutive U periods when measured runtime and memory
   make them feasible. If a run fails, preserve the first divergence and trace
   it to a physical field and age before modifying the implementation.
4. Profile and improve the GPU executor as needed while preserving exact raw
   transition parity. Treat kernel changes as execution backends for the same
   fixed F, never as different physical rules. Measure actual seconds/tick,
   end-to-end checkpoint overhead, VRAM, and host RAM on relevant ring sizes.
   The machine has an A100 with 80 GiB VRAM; shared CPU RAM use must remain
   below 40 GiB. Report measured results separately from projections. Include
   tests that fail if a backend drops state fields, reads outside the radius,
   silently changes F, or substitutes event-composed transitions.

The result may reveal a construction defect rather than a GPU defect. Report
that distinction precisely. Do not claim self-simulation, repair, or noise
robustness from local parity or a single clean work cycle.

## Parallel ownership and communication

Create and edit **only new files** in your namespaces:

- `gacsca/fixed_rule/gpu_validation/`
- `tests/fixed_rule/gpu_validation/`
- `experiments/fixed_rule/gpu_validation/`
- `Report/fixed_rule/gpu_validation/`
- `figs/fixed_rule/gpu_validation/` for ignored receipts and private builds

Add package `__init__.py` files as needed. Existing active modules, tests,
reports, root files, `archive/`, and the other agent's namespaces are read-only
to you. If an existing interface truly needs changing, describe the exact
patch and justification in your own `STATUS.md`; continue with a namespaced
successor rather than editing shared files. Do not switch branches, reset,
clean, stage, or commit this shared tree. Do not overwrite historical receipts
or rebuild shared CUDA artifacts; compile variants in your own build folder.

The other agent owns `design_optimization/` folders and follows
[its prompt](FIXED_RULE_DESIGN_OPTIMIZATION_PROMPT.md). Maintain
`Report/fixed_rule/gpu_validation/STATUS.md` with current approach, commands
and exact results, source/rule identities, validated versus unproved claims,
GPU jobs and expected finish times, requests, and next steps. Read
`Report/fixed_rule/design_optimization/STATUS.md` for requests. Reply in **your
own** status file; never edit the other's. You coordinate substantial A100
jobs: check `nvidia-smi` and running processes before launch, publish the
schedule and memory estimate in your status, and avoid overlapping the other
agent's agreed GPU use. The design agent should remain CPU-only unless you
acknowledge a GPU window in your status. Use bounded pilots before long runs,
preserve checkpoints, and do not stop or alter another process.

Deliver executable code, tests, receipts, and a concise report in your own
folders. Record exact commands, source hashes, state hashes, durations,
resource use, failures, and what a continuous run does or does not establish.
