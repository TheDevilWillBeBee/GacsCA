# Evaluator / maintenance budget gate

The regenerated computing candidate executes the intended full controller, but
its schedule cannot be used as Gray's colony work period. The exact schedule
breakdown is in `figs/fixed_rule/regeneration_budget_v1.json`.

| Stage | Instructions | Literal ticks | Approximate ticks / Q |
|---|---:|---:|---:|
| Retrieve two raw neighboring words | 388 | 9,368,262 | 776.03 |
| Travel guard | 2 | 101,504 | 8.41 |
| Evaluate complete transition | 4,345 | 121,250,779 | 10,043.97 |
| Stage full Hold word | 388 | 18,736,132 | 1,552.03 |
| Regenerate program record | 1,242 | 29,986,793 | 2,484.00 |
| Commit full Info word | 388 | 28,098,744 | 2,327.60 |
| Return to period boundary | 1 | 23,754 | 1.97 |

Total U = 207,565,968 = 17,194 Q for Q = 12,072. Gray pp.31,34 permits
128Q for the complete work period and 8Q for the fifth stage's active computation
and distribution. Even one retrieval round here exceeds Gray's full period.
Missing radius-five communication and three retrieval rounds would add cost.

## Why padding the current layout is not a solution

The current head uses the colony boundaries as its reflecting computation
boundaries. Instructions lie after the memory bank; after fetching a NAND or
LOAD instruction, the head must return through the boundary before reading a
memory operand. Each such return contains a traversal of essentially the whole
colony. More padding lengthens those traversals along with the available 128Q
budget. The number of traversals does not disappear. The metadata query's two
full scans make the same dependence explicit.

Even the counterfactual in which all current 207,565,968 compute ticks remained
unchanged while padding Q would fail inside the existing 16-bit Address capacity:
128 * 65,536 = 8,388,608 ticks. A larger Q alone is therefore neither an implemented
fix nor a credible budget certificate for this candidate.

## Alternatives to distinguish before full maintenance integration

1. **Separate computation extent from colony extent.** Keep a compact working
   region whose size depends on the rule description and word lengths, while
   allowing the physical colony to be much longer. Distinguish computation-head
   reflection from colony boundaries used by mail. Pipeline neighbor retrieval;
   do not perform a whole-colony round trip for each operand. Local metadata
   access outside the active program region needs a declared default record and
   explicit treatment of boundary records. Recompute the complete description
   after adding these rules. Choose one alphabet and geometry once, independent
   of hierarchy depth, then verify the actual circuit and timing inequalities.

   A future bound of the form `T <= c Q + poly(log Q)` would permit Gray's large-Q
   argument; the current `T = C Q` with C=17,194 does not. That bound is a design
   requirement, not a measured property. Existing 16-bit capacities cannot be
   silently stretched. Any wider fixed word choice must be recorded as a new
   construction revision and included in its own description.

2. **Use a specialized compact rule evaluator.** Describe field operations and
   maintenance control directly rather than fetching one NAND gate at a time.
   This does not require a user-program platform. The evaluator still needs a
   complete description of itself, including parsing/dispatch, local bit reads,
   counters, communication and reset. An opcode list or host reference function
   does not close this obligation. Before implementing a large instruction set,
   compare the complete descriptor size and literal tick cost with alternative 1.

3. **Change the maintenance schedule.** Gács §9.3 treats U as a constrained
   parameter and §9.2 allows suitably modified self-simulation. This is permission
   to analyze another schedule, not evidence that arbitrarily increasing U leaves
   the repair argument valid. A proposal must rederive the clock/rebuilding,
   flag, communication, error-island and amplification conditions. Label any
   resulting Gray discrepancy. Do not simply set U to the current evaluator's
   runtime and report faithful repair.

The next bounded experiment should separate the two reflecting boundaries and
measure a local computation window plus pipelined mail, with every added
controller field represented. Use its measured closure cost to decide whether
to implement a compact evaluator. Preserve the existing complete-controller
candidate as a correctness fixture. Actual Address repair, Age evolution,
workspace resets, spatial voting, temporal voting and simulated-layer feedback
remain necessary before a faithful hierarchy can be claimed.

## Separate correctness issues

The known printed Flag2 persistence counterexample remains a source-level issue;
faster computation does not fix it. Our post-evaluation program regeneration
also differs from Gray's early-work-period overwrite and does not settle the
computed-SimBit timing ambiguity. Keep those alternatives and their distinguishing
tests separate from the evaluator's performance problem.
