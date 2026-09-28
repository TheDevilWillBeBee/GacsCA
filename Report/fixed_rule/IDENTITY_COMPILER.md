# Equivalent complete-description compiler and experimental ROM

2026-09-26. Compile-time identities reduce the complete descriptor from 13442
to 10449 word operations (22.27%). Independent symbolic normalization proves
all 154 outputs unchanged on every typed raw neighborhood, including active
controllers, damaged geometry and inconsistent replicas. A separate fixed ROM
built from this expression passes complete symbolic Data-flow checks and literal
local-event tests. It is experimental: the verified baseline ROM remains intact.

## What changed and what did not

`word_identity_optimization.py` emits only the existing NAND, ADD, SHR, EQ, LT
and literal operations. It removes double inversions, redundant masks on bounded
words, additions/shifts by zero and justified Boolean identities. Possible-one
and possible-zero masks supply conservative width bounds. No physical opcode,
register, input field, output field or neighborhood is added or removed.

`identity_holder_program.py` is a separate fixed compiler using that expression.
`identity_holder_projected.py` hard-wires its resulting ROM by Address, and
`identity_holder_initial.py` changes only initial encoded depth. None of these
transition/ROM functions dispatches on depth. They retain Q=32768, U=2^32, the
raw 154-word /4090-bit alphabet, projected 105-word /2704-bit alphabet and radius
seven. The raw physical descriptor F is unchanged. Its specialized projection
G_new=pi F iota_new uses a different, globally fixed hard-wiring from the old
candidate; experiments must not mix their metadata or transfer old manifests.

The optimized expression is **not** installed as a different physical rule.
It is the program the candidate's colonies execute using existing instructions.
The old physical descriptor, program, projectors, executors and datasets were
not edited. No CUDA build or GPU execution occurred.

## Equivalence and self-reference evidence

The independent validator extends the older algebraic normalizer with structural
width rules for AND/OR trees, addition and shifting. It uses neither the
optimizer's possible-bit masks nor its rewrite decisions. Both original and
optimized full expressions reduce to identical symbolic outputs for 2310
independent typed raw input words. This is an all-input expression identity,
not equality only on initialized or inactive states. The optimizer's elementary
identities and conservative bounds additionally admit a node-by-node induction.

An initial 32-neighborhood differential pilot passed. The first symbolic attempt
could not normalize Boolean widths in compound expressions. A second needed
the complement-of-constant case in OR-width reasoning. Both failed logs, and
the second attempt's source snapshot, are preserved. The optimizer and physical
rule were unchanged while fixing that independent normalization gap. The third
attempt and the final complete-ROM certificate pass.

The ROM diagnostic executes the actual compiled instruction list symbolically.
It gathers all three raw histories, votes them, evaluates the complete physical
rule twice, regenerates metadata by reads of **this new ROM**, supplies the
Signal buffers, commits and clears scratch at the following reset. It checks
428100 instruction occurrences across 15 symbolic colonies, 2205 metadata
queries and 97170 packet deliveries. All 154 raw outputs per colony agree with
iota_new(pi F iota_new(inputs)). Thus the optimized program still describes its
own evaluator's complete transition, rather than an initialization ROM or an
inventory of supported opcodes.

This Data-flow identity remains conditional on physical instruction/transport
refinement. Changing the ROM changes positions, scan times, metadata targets and
packet timing. The old candidate's completed physical period proof and execution
artifacts are not certificates for the new candidate. Current timing checks
show that the new paths fit the existing clock windows and check the compiled
gather collisions; full timed interleaving/path recertification remains next.

Equivalence assumes declared raw field widths. Arbitrary corrupt 64-bit Info
words can exceed the width of the represented field. No equivalence or repair
claim for such malformed encodings is made here; legalization/repair of that
domain remains part of the larger noise objective.

## Measured layout and clock savings

| Quantity | Verified baseline | Experimental optimized ROM |
|---|---:|---:|
| Complete descriptor operations | 13442 | 10449 |
| Stored program instructions | 20801 | 17808 |
| Computation-core cells | 30724 | 27720 |
| Controller-path ticks per period | 2802642834 | 2000945998 |
| Installed Q | 32768 | 32768 |
| Installed U | 4294967296 | 4294967296 |

Controller paths are 28.60% shorter. The core still needs Q=32768 under the
current power-of-two layout. The optimized controller cost is now below 2^31,
where the previous layout exceeded that value. This provides a concrete opening
for a halved work period; it does **not** itself halve the installed U.

The separate prospective budget checker fits the current optimized paths into
this proposed global schedule:

```
U = 2147483648
RESET_AGES = (0, 150000000, 290000000, 1230000000, 1232000000)
ACTIVE_ENDS = (149000000, 288000000, 1228000000, 1231000000, 2025000000)
VOTE_AGES = (430000000, 1232000000)
CAPTURE_AGE = 1224000000
WF_START = 1230000000
WF_END = 1230065536
```

It checks gather/packet deadlines, capture before forcing, quiet precommit,
flag-clearing margin and final completion before commit. All margins are positive.
This is **only a budget proposal**: clock constants and wrap semantics occur in
the self-description, so changing them changes the compiled program. The next
candidate must compile that changed rule, check its resulting geometry/timing
again, and reestablish physical recurrence. In particular, merely changing U
while leaving the existing 32-bit age-wrap implementation would be wrong.
Neither a host clock reset nor depth-dependent timing is an acceptable substitute.

## Tests and costs

Seven tests passed in 1.625 s. They distinguish a valid one-bit mask elimination
from an invalid elimination on a 64-bit input; cover arithmetic/shift edge cases;
reject dropping an actual controller output; and round-trip controller-bearing
initial data at depths one, two and three with identical rule/ROM identity.
Those depth tests are initialization checks, not nested execution.

The same suite compares 70 full raw scalar outputs with the unchanged complete
physical descriptor, using the new ROM's actual metadata. The fixtures include
FETCH, active NAND computation, actual SEND birth, and all seven META selectors
at the new core endpoint. The META head reads the new endpoint's records and
reflects with the complete controller state. These are literal physical local
events, not a full instruction path or work period.

The complete symbolic ROM/typing/timing certificate passed in 4.926805 s with
89860 KiB peak host RSS. Runs used `ulimit -v 524288` and
`OPENBLAS_NUM_THREADS=1`; all are terminal. The prospective budget check also
passed. No shared source, job, historical data or GPU artifact changed.

```sh
python -m experiments.fixed_rule.certify_identity_holder_rom --output figs/fixed_rule/identity_holder_rom_v1.json
python -m unittest discover -s tests/fixed_rule -p test_identity_holder_compiler.py -v
python -m experiments.fixed_rule.budget_identity_holder_half_period --output figs/fixed_rule/identity_holder_half_period_budget_v1.json
```

The unchanged physical descriptor digest is
`af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`.
The equivalent compiled expression digest is
`54efad62e59c3f8ac70608d91eb4842ab9d56c5395f810eb6ad118718f85fc42`.
The new ROM digest is
`aafa73dc577012b53a5886a1d1471650a4385f12de932fa0e0a7ed61a67cccbf`.

## Next steps and retained scope

Implement the proposed clock as one globally fixed candidate, preserving finite
state width and including its wrap/phase logic in its own compiled description.
Recompute layout and the full period relation, then validate physical paths and
successive periods. Keep the existing proved candidate as the reference while
that work proceeds. U<=128Q remains unnecessary.

These savings are useful but do not yet make complete depth-two execution
practical. The remaining billions of lower periods require further changes to
the evaluator/layout or a justified physical execution strategy. Full nested
periods, measured repair across levels, general noise amplification and the
finite-cap defect remain open. The candidate-B Flag2 and old-Signal D10 source
choices remain explicit. Gray pp.31–32 and Gacs sections 9.2–9.3 motivate the
specialized hard-wiring; no source noise theorem is transferred by this compiler
optimization. The project goal stays active.

Manifest SHA-256 values:

- `identity_holder_rom_v1.json`: `c75342a2d933220d1cab9ffa7345e10f5d775773c59ec5f75715d425cfc040e8`
- `identity_holder_half_period_budget_v1.json`: `d261fa77a4b407f131efd1a78d3b93e4d3d1d342cd803243bd444b60d833ec6c`
