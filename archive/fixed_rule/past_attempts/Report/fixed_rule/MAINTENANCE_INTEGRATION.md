# Next integration gate: maintenance must be in the complete rule

The compact-window computing rule passes its full macrostep checks, but adding
maintenance cannot be treated as a small scheduler patch. A new fixed component
port, `window_maintenance.py`, uses the current Q=2^28 and Gray's U=128Q=2^35.
It has 28-bit Address, 35-bit Age, four flag bits, and **26,799 NAND gates**.
Ninety-one clean/damaged/boundary neighborhoods agree with the read-only scalar
printed-rule oracle. The singleton Flag2 witness still persists across rollover.
These are component tests, not evidence that maintenance is coupled into the
237-bit physical rule.

## Measured rejection of direct circuit concatenation

`experiments.fixed_rule.window_maintenance_capacity` records an optimistic cost
for literal, unshared concatenation of the two existing circuit descriptions.
With 39 added Age/flag bits, this assumes a 409-bit represented state and 36,244
gates. Eleven input words, gate wires and output banks need 41,564 memory cells.
Even **omitting every mail, staging, regeneration and commit instruction** from
the instruction-region length, the evaluation window is at least 77,809 cells.

Between consecutive gate fetches, the current head must visit memory before the
next instruction. Each such visit costs at least one complete reflected
traversal. Thus this particular concatenation needs at least

`2 × 77,809 × (36,244 − 1) = 5,640,063,174 ticks`

for those traversals alone, exceeding the current 8Q=2,147,483,648 update budget.
The window also exceeds the current uint16 ROM-constant capacity. The compiler
has a guard against silently truncating those constants. This is a rejection of
one specified architecture, **not** a lower bound on optimized circuits, larger
fixed geometry, or specialized evaluators. No full concatenated simulator was
compiled or executed by this estimate; the component descriptions themselves
were constructed and checked.

## Concrete next design decision

Evaluate a **specialized field-word description** including the maintenance
component from the start. Gács §9.2 describes field operations; the user explicitly
permits specialization to this rule family. A 32-bit word operation should not
require dozens of separately fetched bit gates if its physical local transition
can perform that operation directly. Read/write complete raw fields as encoded
data, and include the evaluator's opcode, operand, phase and arithmetic state
in its own word-level description. Restrict the operation set to what the complete
controller and maintenance rule actually require; arbitrary user programs are
unnecessary. Compare actual descriptor size and execution time before replacing
the verified NAND reference.

A larger *fixed* Q is another mathematical possibility, but it further worsens
explicit deeper-level experiments. The current depth-two initialization already
has Q^2=72,057,594,037,927,936 physical cells per top cell, and even omitting padding
would leave 7,387,880,620,032 lowest-level core cells. Increasing Q is not a
practical substitute for evaluating the compact-description option.

## Obligations that must accompany the evaluator

- **Real structural state.** Age needs 35 bits at the present Q, exceeding a
  uint32 storage column. Add a fixed representation for the whole field; do not
  substitute the simulator's host clock for an unrepresented CA register.
  Address's source domain is 28 bits, whereas the current computing prototype
  uses a total 32-bit Address field. Choose and test either the exact source
  domain or an explicitly documented extension for out-of-range values.
- **Radius-five local transitions.** Include all eleven raw neighborhood states
  in the description and decoder relation. The current one-crossing packet
  protocol cannot retrieve five colonies away. Extend its encoded routing data
  and total transition, including drops and collisions, with no level dispatch.
- **Coupling and time.** Gray p.33 clears mail on computed Flag1 and clears all
  simulation structure on computed Flag1 plus Address change. These branches,
  the five active/rest stages, local reset, and commit timing need a complete
  description, not a host schedule. Gray's 128Q clock is distinct from the
  current computing cycle of about 5.104Q.
- **Representation validity.** Current implicit padding assumes static Address,
  zero flags and no Age field. It is not a valid acceleration for general
  maintenance. A uniform Age may be represented lazily only after proving its
  local increment rule on the quiet domain. Damaged Address/Age/flags and
  interactions with packets must be represented explicitly or rejected. Tests
  must compare physical local trajectories across those boundaries.
- **Source discrepancies and correction.** Preserve the printed Flag2 invariant.
  Test any candidate correction as an explicit alternative; do not describe it
  as the printed rule. The computed-SimBit and post-evaluation regeneration
  timing choices also remain to be resolved in the stage schedule.

After these obligations are met, re-evaluate the full description, space/time
inequalities, successive macro-boundary relation, and fault experiments. Source
fidelity, simulated-layer repair, and noise robustness cannot be inferred from
the computing-only timing improvement.
