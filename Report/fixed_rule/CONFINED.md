# Confined evaluators — active-goal milestone

The full fixed-rule Gács/Gray goal is active. This milestone removes the old
whole-ring harness's global workspace-label restriction. It does **not** yet
establish a block self-simulation, program projection, or noise correction.

The new candidate is one fixed **138-bit, radius-one rule**. A rightward head
executes tape instructions. Local `last` and `first` markers reflect it into a
leftward return traversal and then back into rightward execution. There is no
per-colony or per-depth transition dispatch. Arbitrary head collisions have an
explicit total extension: own reflection takes priority over an arrival from the
left, which takes priority over an arrival from the right. This is a computation
convention, not a claimed repair rule.

Every controller field, reflection marker, direction bit, and collision decision
is included in a **2,467-NAND-gate description**. The historical 135-bit rule is
preserved with all ten original v2 source hashes unchanged. The two versions are
construction revisions, not kernels chosen for different hierarchy levels.

Each current evaluation region has **5,351 cells**, including 2,883 memory
records. It performs its fixed description in **30,382,978 physical ticks**,
returning its head to the same local start phase. Regions have identical program
records and label ranges. Initializing 48 regions uses 256,848 cells without
expanding the 16-bit local labels; unlike the historical global harness, total
configuration size need not fit one label space. This is region-count invariance,
not a hierarchy-depth test.

## Tests and physical evidence

```bash
python -m unittest discover -s tests/fixed_rule -p test_confined.py -v
python -m experiments.fixed_rule.confined_regions --output figs/fixed_rule/NEW_NAME
```

**7 tests passed in 1.598 s**:
[log](../../figs/fixed_rule/confined_tests_v1.log).
They cover full raw encoding; scalar/NAND/native agreement on 228 random or
branch-targeted neighborhoods; radius-one exterior perturbations; sparse/dense
parity including colliding heads and one-/two-cell rings; repeated-label colony
isolation with active NAND computation; fixed identity across 1/48 regions; and
physical evaluation of the full self-description in two regions.

The [three-region experiment](../../figs/fixed_rule/confined_regions_v1.json)
executes two cycles without host refills. Each cycle performs 30,382,978 local
ticks and 273,446,802 local cell evaluations, taking 1.8023 s and 1.9083 s.
Both produce the correct full raw output for the **initial snapshot**.

The second output differs from the intended second simulated transition in
**6 raw bits**. This is a deliberately retained missing-feedback witness:
computation is real, but neighbor arguments remain snapshots and output is not
yet committed to a recursively valid Info representation. The source itself
asserts this mismatch is non-vacuous. Consequently **zero hierarchy levels** are
claimed. A future block simulator must eliminate this mismatch through its own
local transitions, not through host reinitialization.

[Raw tapes and outputs](../../figs/fixed_rule/confined_regions_v1.npz) ·
[Exact source archive](../../figs/fixed_rule/confined_regions_v1.tar.gz) ·
[Explicit full-rule description](../../figs/fixed_rule/confined_description_v1.json)

The backend evaluates all cells in the union of the old heads' radius-one
neighborhoods from the old state, then commits those outputs synchronously.
Head positions are an execution cache. Cells outside that set are proved fixed
points when their raw controller fields are zero. Entry validation rejects stale
headless controllers; dense evolution covers arbitrary raw states. There is no
skipping of physical ticks, global memory fetch, or simulated transition callback.

## Next concrete construction

Add directed local packets and a SEND operation to the same candidate physical
rule, then regenerate the **whole** self-description. A send reads an encoded
center-state bit and transports it one site per tick to the corresponding input
location in the adjacent colony. Packet targets and one-boundary crossing status
are finite encoded fields; receive/deposit and collision priorities must be
explicit radius-one functions and included in the rule description.

A fixed colony program should send the entire current raw state in both
directions, wait long enough for the final packets to arrive, evaluate the full
combined rule, stage all output bits, and commit them to the same center Info
bank. Program order and waiting time must be derived from actual route lengths;
no host input refills or synchronized global reads are allowed. Then repeat the
6-bit witness as a true two-macrostep test.

After local block encoding works, the remaining large obligations are unchanged:
ProgramBit projection/hard-wiring, Gray/Gács maintenance and redundant procedures,
finite-depth termination, complete depth-invariant resource accounting, and
simulated-layer repair/noise experiments. A good transport mechanism alone cannot
establish any of these.
