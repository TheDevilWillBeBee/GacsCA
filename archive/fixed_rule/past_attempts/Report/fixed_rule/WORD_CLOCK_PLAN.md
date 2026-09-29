# Next construction: local stage clocks without a description-size cycle

This is an implementation design, **not an executed clocked self-simulator**.
The word macrostep run tests the preceding continuous evaluator. The complete
five-stage rule, its new description and its program must be constructed and
validated together before this design can inherit a self-reference claim.

Gray p.34 sets active intervals, in Q units, [0,16), [32,48), [64,80),
[96,104), [112,120), with rest in the remaining parts of the 128Q period.
Gather A/B/C separately; keep them through update. Reset mail and disposable
workspace at each stage start. Stage three also computes the flag signals;
stage four permits Wf1/Wf2 only during its first 2Q. Stage five votes, evaluates
and distributes Hold. Commit Info at the period boundary before the next
stage-one reset can clear Hold. Computed-SimBit timing remains an explicit source
alternative; refer to shared D10 rather than silently picking an interpretation.

## Measured failure of a literal voting composition

`experiments.fixed_rule.word_temporal_capacity` composes six NANDs for every
bitwise majority of three 64-bit raw field words, followed by the frozen complete
1,834-operation word description. All three 341-word histories are assumed
already gathered. The computation-only ROM omits retrieval, resets and clock
control. This specific arrangement has:

- 2,046 voting operations, 4,934 memory cells and 3,956 instructions;
- an 8,891-cell reflected-head core;
- **93,977,870 ticks**, above the 8Q=67,108,864 stage-five allowance by a factor
  1.40038.

The two component tests check bitwise majority (including three mutually
unequal words), correction with any one history replaced, and composed raw
outputs against the full descriptor. This is a capacity result for that
specified bank layout and instruction schedule, **not** a lower bound on every
voting implementation. It also does not describe the prospective stage controller
itself and therefore is not closure evidence. Source/prototype hashes are in
`figs/fixed_rule/word_temporal_capacity_v2.json`.

## Chosen implementation direction

Use local field operations for temporal voting and commit, with geometry encoded
in the same fixed program record that META already reconstructs. This avoids
adding a runtime level selector or omitting the scheduler from the description.
All affected operations must be transcribed into the new complete F descriptor.

1. **Interleave history locations.** For each raw input word, put A/B/C in three
   neighboring memory cells. At a locally clocked vote step, the middle cell can
   compute bitwise majority of its own data and its immediate neighbors. This
   fits inside the existing radius-five neighborhood. The evaluator's input
   wire addresses become the middle locations; the compiler maps logical wire
   numbers to physical addresses. It must not use majority of whole words.
   The single-step vote joins the actual physical rule and its self-description.
2. **Pair Info and Hold locally.** Lay out each Info word adjacent to its Hold
   word. Stage-five instructions write Hold, including regenerated program
   words. At the final old Age U−1, each marked Info cell takes its neighbor's
   Hold. At old Age 0, reset Hold while retaining Info. Both are synchronous
   local transitions, not a host boundary copy. Dirty controller/scratch states
   must be included in the next simulated raw state just like all other fields.
3. **Describe local reset masks as program data.** Program metadata marks
   which memory locations survive each stage reset. For example, stage two
   preserves Info and A; stage three preserves Info/A/B. Program memory may
   use existing static operand fields as finite masks where ALU operands are
   otherwise unused. META must regenerate every such field after Address repair.
   No host array mask may be consulted by the physical rule.
4. **Store stage entry PCs in the program record.** Do not put compiler-generated
   instruction offsets directly into F's implementation: that would introduce
   a cycle through the size of F's own description. A fixed boot record can hold
   five 32-bit PCs in its existing a/b/d fields (64+64+32 bits). The raw rule
   describes selecting one of these slots from local Age. The compiler emits
   their values after generating the entire new description. The hard-wired
   projection supplies the record exactly as it supplies all other ROM words.
   Protect this boot record from overlapping interpretations as a history mask.
5. **Use Age, including during damage.** Every gating/reset/commit decision is
   a local function of encoded physical fields. Preserve all simulation fields
   during rests except source-mandated flag/address clearing. Uniform-Age
   acceleration can only be reused after re-proving the new domain invariant
   and testing every stage boundary against the complete radius-five kernel.
   Its host event clock must never substitute for an unencoded CA Age.

Stage three's flag computation must have its own writable input/scratch region;
never overwrite the A/B/C histories that stage five will vote again. A faulty
single history versus two faulty histories must give different tested outcomes.
Signal locations use **computed** Address (Gray p.35; shared D14). The flag
signals and trickle-down recursion require the complete redundant representation,
not an isolated unprotected flag placeholder.

## Distinguishing tests before a clocked macrostep claim

- Every rest step preserves simulation data/controller/mail on healthy structure;
  an encoded Flag1/address-change witness still exercises the required clearing.
- Five resets preserve exactly the histories needed later, including their raw
  controller and program words; masks cannot depend on a host colony label.
- At the U−1 → 0 boundary Info receives old Hold, and the next reset cannot
  erase this result. An intentionally reversed order must fail.
- Corrupt exactly one temporal history, then two; compare all raw output fields.
- Repair Address during a simulated reset/commit/META phase and regenerate the
  **new** program record. A stale old-Address reconstruction must fail.
- Compile the actual expanded F including boot-PC selection, masks, voting,
  commit and stage gating; remeasure its ROM, state width, Q/U and stage bounds.
- Execute two complete 128Q periods without host refill. Verify all five rests,
  all three separately retrieved records, both evaluations, final raw records
  and recurring physical boundary state.

Fivefold spatial redundancy, detailed trickle-down/amplification and full
physical-noise tests remain separate mandatory obligations. The proposed local
layout is a way to make their eventual integration measurable; it does not
establish that the current Q or workspace is sufficient after they are added.

The v1 source bundle is preserved in its .tar.gz archive; v2 corrects a
miscounted explanatory comment (the executed composition used six NANDs in both).
