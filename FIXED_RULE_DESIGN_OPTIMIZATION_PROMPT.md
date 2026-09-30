# Agent 2: independently improve the fixed-rule Q/U design

You are working in `/scratch/Ehsan/Projects/GacsCA` concurrently with an agent
validating dense GPU execution. This is a **shared working tree**. Your task is
to investigate and implement a better fixed-rule Gács/Gray self-simulation
candidate, seeking lower colony size Q and work period U without weakening
the scientific claim. **Choose the optimization ideas yourself.** This prompt
deliberately supplies no preferred method or route. Continue beyond a list of
suggestions: build and test the most promising candidate you can justify.

## Project and sources

The final target is faithful hierarchical self-simulation under **one fixed,
finite-state local transition rule**. Hierarchy depth belongs in initial and
boundary data, not in the kernel, state width, hardware register count, or a
host-language recursive interpreter. The same physical rule must process its
own encoded controller and evaluator state, local communication, computation,
encoding/decoding, colony maintenance, and eventually simulated-layer repair.
Initially one, then two, then ideally three explicit levels are milestones;
they do not license a maximum-depth tower. Universality or arbitrary user
programs are not required. Do not work on GKL.

Begin with [the current research index](Report/fixed_rule/README.md),
[the Q8192/U2^20 candidate](Report/fixed_rule/DUAL_PASS_U20.md),
[the macrostep audit](Report/fixed_rule/U20_MACROSTEP_AUDIT.md),
[the dense executor report](Report/fixed_rule/DENSE_GPU_EXECUTOR20.md), and
[the current status](Report/fixed_rule/STATUS.md). Inspect the active code in
`gacsca/fixed_rule/`, its tests and experiments, and the earlier attempts under
`archive/fixed_rule/past_attempts/` so that old failures are not rediscovered
as new results. Read Gray pp. 27–34, especially pp. 31–32 on hard-wiring and
ProgramBit projection, and Gács §§9.2–9.3 plus the relevant correction and
amplification machinery. PDFs are in `papers/`; extracts are in
`papers_txt/gray_readers_guide.txt`, `papers_txt/gacs_2001.txt`, and
`papers_txt/masumori.txt`. Gray's numerical parameters and the current
candidate's timings must be treated as claims to audit, not assumed fit
certificates. Source-fidelity questions such as printed Flag2 persistence and
computed-SimBit timing remain open.

The current candidate uses Q=8192, U=2^20, radius seven, a 6,465-bit physical
alphabet, and a 14,830-operation description of its complete local F. It has
substantial local and event-composed validation, but no continuous full-U
physical colony run, successive decoded upper macrosteps, closed two-level
ring, or noise-robustness result. Preserve this distinction when comparing any
new candidate. A changed Q, U, radius, or alphabet defines a **new fixed
candidate**, never a hierarchy-depth selector.

## Your work and evidence standard

Independently identify the binding resource costs and mathematical obligations.
State alternatives where the papers leave behavior underspecified, with tests
that distinguish them. Quantify candidate Q, U, physical width, neighborhood,
description size, route/workspace capacity, schedule margins, encoded memory,
and measured CPU/GPU cost. Compare improvements to the current candidate using
the same definitions; do not optimize a component in isolation and count it as
a complete self-simulator.

Implement the strongest justified successor under **one fixed local rule**.
Represent simulated controller state as encoded data and include the evaluator's
own transition in its self-description. Check raw encoding/decoding, active
computation, local dependencies, phase timing, state identity across requested
depths, and nontrivial decoded dynamics over successive work periods. If a
complete physical period or two-level run is not yet feasible, give a bounded
executable vertical slice and a measured explanation of what prevents it.
Address-derived ROM initialization alone, an opcode inventory, or an
event-composed oracle is not closure. Finite-depth termination must arise from
initial/boundary data consistent with the same rule, not a special top kernel.
Maintain the longer-term correction objective, while separating proven
healthy-path behavior from damaged-state repair and noise robustness.

Write tests that would fail if rule identity or state width varied with depth,
a transition read outside its declared neighborhood, raw controller fields
were omitted from the encoding, dynamics stopped after initialization, or a
depth-specific interpreter were substituted. Preserve informative failed
approaches in your report. Make no claim stronger than the executed evidence.

## Parallel ownership and communication

Create and edit **only new files** in your namespaces:

- `gacsca/fixed_rule/design_optimization/`
- `tests/fixed_rule/design_optimization/`
- `experiments/fixed_rule/design_optimization/`
- `Report/fixed_rule/design_optimization/`
- `figs/fixed_rule/design_optimization/` for ignored receipts and private builds

Add package `__init__.py` files as needed. Existing active modules, tests,
reports, root files, `archive/`, and the GPU agent's namespaces are read-only
to you. If a shared interface would help, put a concrete proposed patch and
reason in your own `STATUS.md` and keep working with a namespaced successor.
Do not switch branches, reset, clean, stage, or commit the shared tree.
Keep generated data and builds inside your ignored figure namespace.

The GPU agent follows [its prompt](GPU_DENSE_VALIDATION_PROMPT.md) and writes
`Report/fixed_rule/gpu_validation/STATUS.md`. Maintain your own
`Report/fixed_rule/design_optimization/STATUS.md` with approach, source basis,
owned files, commands and exact results, validated versus unproved claims,
resource measurements, requests, and next steps. Read the GPU agent's status
regularly. Put requests to that agent in **your own** status and read its reply
in its status; never edit the other's. The GPU agent coordinates substantial
A100 runs. Work on CPU first, keeping shared host RAM below 40 GiB. If you
need the 80 GiB A100, request a specific bounded window in your status and
wait for the GPU agent to acknowledge it there; check `nvidia-smi` before use.
Do not stop or alter another job.

Deliver code, tests, reproducible receipts, and a concise source-grounded
report in your own folders. Prioritize a correct fixed-rule construction and
practical two-level simulation; treat measured cross-level error correction as
a later claim that needs its own evidence.
