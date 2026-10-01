# Agent 4: audit and repair the Q=8192, U=2^20 fixed-rule implementation

You are working in `/scratch/Ehsan/Projects/GacsCA` concurrently with other
coding agents. This is a **shared working tree**. Your task is to bring the
current fixed-rule candidate `gacsca.fixed_rule.stream28_dual_pass20.local_step`
from a collection of locally certified components to an honestly executed
self-simulation:

- Fix the known defects.
- Find the unknown ones with a much stronger certification harness.
- Remove every host oracle from the simulation path.
- Run continuous physical work periods whose decoded upper states follow the
  same rule.

Implement and test. Do not stop at a plan or an inventory. Do not work on GKL.

The final target of the project is faithful hierarchical self-simulation under
**one fixed, finite-state local transition rule**. Hierarchy depth belongs in
initial/boundary data, never in the kernel, alphabet, register count or a
host interpreter. A changed Q, U, radius or alphabet is a new fixed
candidate, never a depth selector. Make no claim stronger than the executed
evidence.

## Audit of the current state (2026-09-29, design-optimization agent)

The facts below were checked in the code or taken from other agents' receipts.
Re-verify anything you rely on.

### What exists and what it establishes

- **The rule.** Q=8192, U=2^20, radius 7, a 6,465-bit alphabet in 421 typed
  raw words, and 119 represented evolving words per upper cell. One encoded
  8Q spatial evaluator runs twice per period: early for Flag1/Flag2 Hold,
  final for all Hold words.
- **Static fields.** Each cell stores 3,402 static bits: seven address slots
  `p0..p6` × seven holder metadata fields (`STATIC_OFFSETS = range(-3, 4)`),
  plus spatial circuit/route words.
- **Own-rule description.** The claimed complete description is the
  14,830-operation WordCode, digest `16bf88a1…6257`, documented in
  `Report/fixed_rule/DUAL_PASS_U20.md`.
- **Local structure.** The Gray §5.2 candidate-B maintenance
  (`stream28_holder_core.maintenance`) agrees with an independent Boolean
  netlist transcription on 3,000 random radius-5 neighborhoods at the
  core's Q=2^13, U=2^28. The regression is
  `tests/fixed_rule/design_optimization/test_front_candidate.py::MaintenanceTest`.
  This part is sound as written.
- **Evidence so far is component-level.** It includes:
  - literal/WordCode certificates on sampled neighborhoods;
  - two isolated 65,536-tick evaluator periods;
  - event-composed single upper macrosteps that skip packet flights using
    phase/distance invariants (`U20_MACROSTEP_AUDIT.md`);
  - a GPU Flag recurrence;
  - a dense CUDA executor at about 14 ms/tick for 31 colonies.

  The GPU agent's corrected dense pilot ran 65,516 uninterrupted physical
  ticks, which covers the first gather only. Its 761 central history words
  matched predictions, with host-prepared upper static words.
  `Report/fixed_rule/gpu_validation/STATUS.md` has the details.

### Defects and gaps, in priority order

1. **The own-rule description is not the physical rule.** In
   `stream28_dual_core_clock_description20.py:50` (and its predecessor
   `stream28_holder_core_clock_description.py:50`) the code computes
   `b.band(selected, b.const(abs(offset)))` with a Boolean 0/1 `selected`.
   This masks a seven-colony packet hop count to 1.

   The GPU agent traced the first raw divergence to old age 2392, site 2491,
   field 101 `s2_rp_remaining`: literal F computes 7, while WordCode and CUDA
   compute 1. So digest `16bf88a1…` describes a *different* F.

   Everything derived from it describes the wrong rule:
   - the Address-projected evaluator circuit ROM;
   - the native CPU and dense CUDA backends;
   - placement/schedule receipts;
   - any audit that used compiled F for whole-ring steps.

   The existing certificates (108 literal cases, 40 coherent neighborhoods,
   24 sampled combined endpoints) did not cover the branch. An isolated
   corrected successor exists under `gacsca/fixed_rule/gpu_validation/`
   (digest `232fa6b9…f88`, still 14,830 operations; re-placed with 14,851
   gate instances, all complete by evaluator tick 39,517). Treat it as a
   starting point to re-verify, not as certified.

   `grep` finds 134 `band(` uses in `gacsca/fixed_rule/*description*.py`.
   The same Boolean-masking pattern (0/1 selector combined bitwise with a
   multi-bit constant or word) may occur elsewhere.

2. **Upper static words come from a host oracle, not from the CA.** The
   represented upper neighborhood needs 390 rule-static input words:
   341 spatial circuit/route words and 49 holder metadata words. They are
   functions of the *upper* Address (ROM rows of upper addresses A−7..A+7).
   No physical transition obtains them.

   The host computes `experiments/fixed_rule/compact8_address_rom.py:
   project_all_dual_static(upper_address, …)` and injects the result into
   SOURCE Data:
   - `run_dual_capture20_events.py:62-73` (`initial_data=static_preload`);
   - `gpu_validation/initial.py:71`.

   Later calls, such as `run_dual_macrostep20_events.py:203` and
   `certify_dual_projection20.py:78`, compute *expected* values for
   assertions. The data retained from the initial injection then serves both
   evaluator invocations. `stream28_dual_projected20.py` itself says this "is
   not an implemented self-referential lookup mechanism".

   Gray pp. 31–32 require the colony to fetch the upper ProgramBit from the
   physical cell whose Address matches the simulated Address, steps (i)–(iii).
   Without that fetch there is no closed ring, and no depth-2 or deeper
   configuration can even be written down without the host.

3. **No continuous full-U execution and no successive macrosteps.** The
   macrostep audit composes events: it executes launches, receives and
   commits literally, and skips flights using checked invariants. It covers
   one upper neighborhood per run.

   Nothing has run all 2,283 gather routes, both evaluator invocations,
   fivefold holder heads/packets, Signal/Wf and the final reload in one
   retained world for U ticks, let alone at two consecutive boundaries. The
   SEND audit follows one symbolic head, so interference among fivefold heads
   or packets across a full colony is untested.

4. **Test configurations are only coherent/canonical.** A finite test ring of
   N colonies cannot be globally canonical modulo Q (the GPU agent tracks the
   seam). A self-simulation must compute upper F for *every* upper
   neighborhood, including arbitrary controller, mail and evaluator states and
   inconsistent Address/Age. Random upper states should be the default test
   input, with coherent states as a special case.

5. **Redundancy scope versus Gray's claims.** Fivefold copies cover the
   holder procedure fields (`s0..s4`), Wf (`w0..w4`) and Signal. The spatial
   evaluator's gate, route and mail state is single-copy and has no temporal
   vote, so a level-0 error during evaluation reaches the upper state.
   Gray's Proposition 4 needs procedures carried out with redundancy.

   The 3,402 static bits per cell are stored state. Nothing in the physical
   rule repairs them. Either project them away (compute from Address inside
   the rule, as Gray's projection does) or add a repair mechanism. Holder
   procedures take geometry from stored `center.address/age` rather than
   computed values. That is fine on the healthy path but should be stated.

6. **Source-fidelity questions remain open.** These are the printed Flag2
   persistence (candidate-B explicit erasure), and computed-SimBit timing
   versus the implemented Signal capture of `data & 1` at `CAPTURE_AGE`
   (Gray p. 35 overwrites SimBits at Addresses 3 and Q−3). The deviations
   from Gray's five-stage proportions (U/4, U/4, U/4, U/8, U/8 with
   active/rest halves) should be listed and justified.

7. **Scale limits.** A two-level ring needs Q² = 67M cells: 50.5 GiB per
   bit-packed full state, or 23.9 GiB for the projected evolving state. It
   also needs U² = 2^40 ticks per level-2 step. Two-level closure is
   therefore not executable at this Q/U with present hardware. The
   realistic goal here is **one-level closure**: consecutive continuous U
   periods on a closed ring, with successive decoded macrosteps.

8. **Reports overstate some items.** "Complete own-rule WordCode" and
   "literal certificates" in `DUAL_PASS_U20.md` and `README.md` refer to the
   defective description. Record corrections in your own report. Do not edit
   theirs.

For contrast only: `Report/fixed_rule/design_optimization/` describes an
independent bit-level successor family (Q=128, U=2^14–2^15). It fetches the
upper instruction by a physical match pass and has executed closed one-level
and two-level runs. It is a different fixed candidate, not a fix for this
one. Reuse ideas if useful, but your deliverable is the U20 candidate or its
explicitly justified successor.

## Your work

Items are roughly in priority order. The decisive results are (a) a
description provably equal to the physical rule, and (b) a continuous
oracle-free physical period whose decoded upper state equals upper F.

1. **Freeze and inventory.**
   - Record source hashes of the active rule, descriptions, ROM builders and
     backends.
   - List every artifact derived from WordCode `16bf88a1…`: ROMs,
     placement/timing receipts, native/CUDA builds, and audit receipts that
     used compiled F. Mark each "must be regenerated" or "unaffected".

2. **Make description equivalence a checked invariant, not a sample.**
   - Fix the hop-count masking in a namespaced successor. You may start from
     the GPU agent's corrected copy, re-verified.
   - Audit all description builders for the same Boolean-versus-word misuse
     and for other width/typing errors.
   - Build a differential harness comparing literal Python F, WordCode, native
     C and CUDA on all 421 raw output words for:
     - random *typed* neighborhoods;
     - generators targeted at every branch: each route offset ±1..±7, each
       opcode, each stage boundary and age class, packet wrap, head
       creation/HALT, fivefold commits, Info/Hold reload, Flag/Signal/Wf
       conditions;
     - neighborhoods sampled from continuous trajectories.
   - Report branch/opcode coverage.
   - Where feasible, add a formal per-output-bit equivalence check, for
     example bit-blasting both sides into a SAT or BDD check. `pip install
     --user` is allowed.
   - Then recompile the evaluator circuit ROM and schedule for the *final*
     corrected F and re-certify all route and timing bounds.

3. **Close the upper static-word lookup physically.** Check whether an agent
   is already working from
   `Report/fixed_rule/gpu_validation/ROM_SELF_FETCH_AGENT_PROMPT.md` (look
   for `Report/fixed_rule/rom_self_fetch/STATUS.md`).
   - **If yes:** do not duplicate it. Coordinate through your statuses,
     consume its results, and own items 2, 4, 5 and 6 here.
   - **If no:** implement it per that prompt's specification. Any
     finite-radius protocol is acceptable if it:
     - obtains all 390 words from represented Address by physical
       transitions before both evaluator captures;
     - handles an Address change at a work boundary;
     - is included in the rule's own description.

   If it cannot fit Q=8192/U=2^20, give a counted obstruction and a coherent
   successor candidate.

4. **Oracle-free initializer and continuous periods.**
   - The initializer may assign canonical lower ROM by each *physical*
     site's own Address. It may not call `project_all_dual_static` or any
     equivalent with an upper Address. Upper SOURCE Data starts empty or
     deliberately wrong.
   - Use varied random upper states and several upper Addresses on a small
     closed ring (aliasing is allowed but must be stated).
   - Run consecutive full U periods with the same F at every site and tick:
     no event skips, no host transitions, no reinitialization at
     boundaries.
   - Decode all 119 words at each boundary and compare with upper F applied
     to the previous decoded ring.
   - CPU native first. Coordinate any substantial GPU use (below). Preserve
     the first divergence with physical age, site and field. Classify it as
     construction defect, description defect or executor defect.

5. **Fidelity items.** For items 5–6 of the audit, implement fixes where they
   are cheap, for example projecting static ROM away and computing it from
   Address. Otherwise document each deviation with a test that distinguishes
   the alternatives. Keep healthy-path claims separate from damaged-state
   repair and noise robustness.

6. **Tests that would fail if:**
   - the host supplies any upper static word;
   - a compiled description or backend differs from literal F on any
     exercised branch;
   - a backend drops or narrows a raw field;
   - a transition reads outside radius seven;
   - rule identity or width changes with depth;
   - raw controller fields are missing from the encoding;
   - dynamics stop after initialization;
   - an event-composed or depth-specific substitute replaces physical
     transitions.

## Parallel ownership and communication

Create and edit **only new files** in these namespaces:

- `gacsca/fixed_rule/u20_repair/`
- `tests/fixed_rule/u20_repair/`
- `experiments/fixed_rule/u20_repair/`
- `Report/fixed_rule/u20_repair/`
- `figs/fixed_rule/u20_repair/` for ignored receipts and private builds

Add package `__init__.py` files as needed. Everything else is read-only to
you: existing active modules, tests and reports, root files, `archive/`, and
the `design_optimization/`, `gpu_validation/` and `rom_self_fetch/`
namespaces. If a shared interface must change, write the exact proposed patch
and reason in your own `STATUS.md` and continue with a namespaced successor.
Do not switch branches, reset, clean, stage or commit this shared tree. Do not
overwrite historical receipts or rebuild shared build artifacts. Compile into
your own `figs/` namespace.

Maintain `Report/fixed_rule/u20_repair/STATUS.md` with:
- approach and source/rule identities (hashes);
- owned files;
- commands with exact results and durations;
- first divergences;
- validated versus unproved claims;
- resource use, requests and next steps.

Read the other agents' statuses regularly: `design_optimization/`,
`gpu_validation/`, and `rom_self_fetch/` if present. Put requests to them in
**your own** status and read their replies in theirs. Never edit another
agent's files or stop another agent's process.

Resources:
- Keep shared host RAM below 40 GiB.
- Long CPU jobs should pin a bounded core set (e.g. `taskset`) and say so in
  your status.
- The design-optimization agent currently runs multi-hour jobs on cores 0–7
  and 40–47.
- The A100 is shared. Before any substantial GPU run, publish a bounded
  window and VRAM estimate in your status and obtain an acknowledgement from
  the agent coordinating GPU use (currently the GPU validation agent). Check
  `nvidia-smi` and running processes first.

Deliver executable code, tests, reproducible receipts and a concise
source-grounded report in your own folders. Record source hashes, state
hashes, ages, durations and resource use for trajectories. Report separately
what is established for:
- description equivalence;
- physical self-description lookup;
- one continuous period;
- successive macrosteps;
- damaged-state repair;
- noise robustness.
