# Compact physical storage with raw faults and full-rule CUDA execution

2026-09-26. This continuation adds a compact resident physical snapshot and
literal multi-tick GPU causal windows. Eight new tests pass, including active
WRITE, boundary mail, locality and two damaged procedure holders. The unchanged
full raw rule also matches 71 witnesses from the archived complete macrostep.
This advances physical execution and fault representation; it does not execute a
full GPU colony macrostep or a nested depth-two macrostep.

## Representation and exactness

`small_holder_bank.py` stores one uint64 Data value per ordinary MEM row per
colony (9,922 rows), plus sorted sparse absolute field values. A logical sparse
entry can override any of the 25 coherent fields, including Data outside ordinary
MEM rows, controller/mail, Address, Age, flags, Wf and Signal. Unspecified geometry
is canonical with a shared initial Age; unspecified dynamics are zero. All bank
and sparse values are validated against the fixed field widths.

The coherent layer reconstructs five procedure/Wf copies from adjacent logical
records and seven metadata records from the fixed ROM. A second sparse map can
then override **any of the 154 complete raw fields at any physical holder**.
It retains incoherent backups and corrupted raw geometry/controller/metadata;
zero overrides remain distinguishable from an absent override. No repair is
performed by decoding or by the storage layer. Complete raw metadata overrides
also allow comparisons outside the hard-wired projected subspace; this does not
establish recovery of arbitrary program corruption or a new projected-rule noise
theorem. All scalar/native/GPU comparisons here use the same full raw F.

One can encode any finite raw configuration by overriding all fields at all sites,
subject to the reference implementation's explicit allocation cap. Compression
quality depends on the state; dense faults can defeat it. The storage format is
not an enlarged physical alphabet or a depth-dependent evaluator. It leaves the
small_holder rule, neighborhood, ROM and state schema unchanged. Full descriptor:
`af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`.

`small_holder_bank_cuda.{py,cu}` uploads the bank, sparse indices/values and fixed
ROM once per resident object. GPU threads reconstruct each of the fifteen raw
neighbors using the bank and sparse maps, then execute the **complete** raw
self-description. This kernel has no healthy-prefix restriction: arbitrary
in-range raw overrides, flags, clocks and all work-period ages are supported.
The host provides positions and state data, not computed simulated transitions.
A batch returns all 154 next fields; repeated calls preserve the resident input.
Individual outputs are not committed in place, so batches use one synchronous
input snapshot. Each object is capped at 64 MiB explicit device storage, with
at most 256 outputs per call; CUDA context/compiler resources are additional.

`small_holder_bank_cone.py` composes this local kernel into actual successive
physical ticks. To return an interval after t updates, it starts with its full
7t halo. Each update evaluates the interval with seven cells removed from each
end, stores every resulting raw field, and uploads that snapshot for the next
tick. The newly stored raw values cover all neighbors used by the following
step. This is a finite-propagation argument for the valid interior; exterior
state is stale and explicitly not exposed as a current global configuration.
The initial window is limited to 4,096 distinct ring sites. No host physical or
upper-rule transition is called during this GPU advance, as checked by tests.
Fresh uploads each tick are currently deliberate reference behavior, not an
optimized whole-colony commit implementation.

## Validation and measured costs

Exact commands (repository root):

```sh
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_bank.py -v
# 4 tests, 171.152 s, OK; includes first private full-descriptor CUDA compilation.
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_bank_cone.py -v
# 3 tests, 1.019 s, OK.
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_bank_locality.py -v
# 1 test, 0.829 s, OK.
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_bank_validation --output figs/fixed_rule/small_holder_bank_validation_v1
# Passed, 1.022534 s, maximum host RSS 164,420 KiB.
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_bank_fixture --input figs/fixed_rule/small_holder_macrostep_v1 --output figs/fixed_rule/small_holder_bank_fixture_audit_v1
# Passed, 1.126509 s, maximum host RSS 225,352 KiB.
```

The storage-only test was also run while CUDA compiled (one test, 0.505 s, OK).
It is included in the four-test result, not an additional distinct test. The
new eight tests are separate from the earlier small_holder 29-test milestone;
existing frozen code was not edited or needlessly retested.

The four main tests check every logical/raw field, non-MEM Data, zero overrides,
immutable input ownership, invalid keys/widths/budgets, resident lifetime and
batch bounds. Sixty full-rule cases across reset, temporal vote, capture,
forcing and clock wrap compare GPU reconstruction and transition with both the
independent scalar rule and native descriptor. They include arbitrary local
flags/Wf, noncanonical geometry/clocks and damaged backups/metadata. Five more
local outputs exercise an active WRITE with a damaged holder.

The cone tests compare four successive GPU physical ticks with literal native
updates, both near an active WRITE and across the periodic colony boundary with
mail. They forbid CPU/upper-rule evaluator calls during GPU advance. Two corrupted
procedure holders have all procedure copies replaced by maximal words; after
three literal ticks, the nine certified output cells equal the clean trajectory,
including the successful Data write from 11 to 91. This is targeted local procedure
repair, not arbitrary geometry repair, stochastic robustness or cross-level
correction. The locality test changes complete raw states at offsets beyond
radius seven and a remote logical state, confirming unchanged local output.

The standalone validation repeats twenty reconstruction/transition comparisons
and the three-tick clean/damaged comparison (69 local evaluations per cone):

| Measured resource | Bytes |
|---|---:|
| Initial compact snapshot | 82,384 |
| Resident explicit GPU allocation | 2,120,368 |
| Maximum explicit GPU allocation during cone | 2,208,656 |
| Final certified-window snapshot | 101,680 |

Its NPZ includes initial bank/exception arrays and physical before/after/reference
states. JSON contains source hashes, descriptor identity, binary hash, timing and
limitations: [small_holder_bank_validation_v1.json](../../figs/fixed_rule/small_holder_bank_validation_v1.json).
Private CUDA binary SHA256:
`e90ce5993d1664a5b5e23e0ef3052256245987bbfd995a68a0d888abe876572b`.

The archived-macrostep audit first checks the frozen NPZ hash and descriptor
identity. It selects 71 local witnesses with uniform and explicit controller/flag
activity coverage, relocates each complete raw neighborhood into the bank, and
compares every output field with the archived expected output. The resulting
2,703,536-byte snapshot uses 4,741,520 bytes explicit GPU allocation. This is
local parity with a previously executed macrostep, not execution of that full
macrostep on GPU. Evidence: [small_holder_bank_fixture_audit_v1.json](../../figs/fixed_rule/small_holder_bank_fixture_audit_v1.json).

All runs are terminal. Device compute-process queries were empty before and after
these small checks. No matching protected third_link_initialized process was seen;
absence is not proof of successful completion of its old run. No shared CUDA
artifacts were rebuilt and no substantial GPU allocation was launched.

## Remaining implementation obligations

The actual Data-bank representation now exists, with explicit raw exceptions,
but its scalable whole-colony evolution does not. A dense raw override for every
site at every tick would erase the memory savings; extending the small cone in
that way is not the next intended approach. Implement synchronous GPU commits of
ordinary memory/controller/mail, retain physical deviations from a certified
base, and prove a sound set of affected sites before using sparse updates.
A correct base trajectory and radius-seven expansion of its physical differences
can support that scheme; no unproved coherent projection may discard faults.

The current dense bank itself would take 2.6 GB per top cell at depth two, before
controller/fault/index storage. Its present 64 MiB reference cap intentionally
prevents that allocation. Coordinate substantial device scheduling through
STATUS.md/MAIN_AGENT_NOTES.md before larger runs, and bound host staging.
The U²=2^64 horizon still requires certified quiet/transport skipping or further
rule/evaluator optimization. Literal local kernels alone do not make two-level
macrosteps practical.

Full depth-two/three dynamics, successive nested macrosteps, mixed-Signal suffix
coverage, noise-robust termination, altered-schedule repair/trickle-down arguments
and experimentally measured correction across levels all remain open. The final
project goal remains active.

Owned additions: the bank, CUDA and cone modules; three test_small_holder_bank*
files; small_holder_bank_validation.py and audit_small_holder_bank_fixture.py;
private builds/results under figs/fixed_rule; this report and STATUS.md. No shared
change is requested. The other agent should reply only in MAIN_AGENT_NOTES.md.
