# Physical flight audit and the depth-two execution budget

2026-09-26. The frozen GPU event backend's controller-distance function has a
new CPU audit against an independent actual-ROM event oracle. A separate exact
schedule count shows why GPU tuning alone will not make the present depth-two
macrostep practical. The rule, alphabet, ROM and all GPU binaries are unchanged.

## What the existing backend actually executes

The independent/gather kernels call the unchanged local controller expression
at physical events. They retain actual Data and full controller fields, sample
SEND payloads from physical source Data, and stage packet delivery. The host
advances clocks and launches these kernels; it does not supply an upper-rule
result. The noiseless macrostep proof does not permit replacing this execution
with a host call on decoded cells.

`independent_distance` is shared by independent and gather execution. It jumps
leftward heads toward Address zero, and rightward heads toward the next possible
instruction/operand/query event or the last core cell. The surrounding driver
caps the jump at a clock boundary. Communication and flag domains have their
own guards and are not proved by the distance calculation.

## Exact function under test and finite argument

The new audit extracts the original C++ function verbatim from
`small_holder_resident_independent.cu`, adds only its actual ROM accessor and
constant/field definitions, and compiles a private CPU shared object. No CUDA
build or device allocation occurs. The independent oracle constructs event
positions from every actual ROM record: matching non-MEM instruction indices,
matching MEM operand indices, metadata-query Addresses and the endpoint.
It does not reuse the function's memory-prefix address formula.

The v2 run passed **5223948 breakpoint cases**: all eight phases, both directions,
both zero/nonzero metadata-value classes, and all 32768 target values plus four
out-of-range representatives. Unused target registers have distinct values.
The oracle checks endpoints and both sides of each possible event position.
It rejects both an extra skipped tick and substitution of RB for RA.

Why these finite classes suffice for the inspected function's distance:

- There is no WAIT record anywhere in the fixed ROM, as explicitly checked.
  Its special counter-decrement branch is therefore unreachable in this domain.
- A leftward head returns its Address, independently of other controller words.
- For a rightward head, each phase selects at most one target register. Other
  registers do not affect that branch. Phase-six value is used only as a
  zero/nonzero condition. All out-of-range targets select the endpoint.
- With those quantities fixed, the only remaining Address comparison is whether
  the selected target is ahead of the head. Both the inspected function and
  actual-ROM oracle are affine between the tested target/endpoints. Checking
  each interval's endpoints supplies the intervening Addresses as well.

This is a source-inspected finite argument plus a compiled audit, not arbitrary
sampling promoted into a theorem about uninspected future C++ source. The
recorded function, generated-source and binary hashes identify its exact scope.
The controller-flight lemmas establish that no Data/control action occurs in
these open intervals. Arbitrary-context/mail lemmas extend those leaves under
their stated canonical and noninterference premises. Driver clock guards,
packet staging/order, compressed-state reconstruction and suffix handling still
need their own complete backend composition. This audit does not prove those
operations or execute a new full work period.

The earlier v1 audit remains preserved. It tied several target registers to the
same value, which could hide wrong-register reads. V2 separates unused registers
and adds that mutation. V1 was not a failed physical run; its test discrimination
was weaker. No frozen successful source was edited.

## Work volume and what can be optimized

`measure_small_holder_execution_budget.py` replays the verified dispatch and
instruction catalogs against every phase of the actual ROM. For one colony and
one period it finds:

| Quantity | Count |
|---|---:|
| Instructions executed | 34526 |
| Dispatch travel ticks | 420219476 |
| Instruction-body ticks | 2382423352 |
| Controller paths, including six entry ticks | 2802642834 |
| Ticks outside those controller paths | 1492324462 |

The last row includes live packet flight and flag evolution; it is not an idle
budget that may simply be deleted. Instruction-body ticks themselves include
long physical scans, which the current event backend already accelerates.

For the **present layout**, the 30724-cell computation core plus five tail cells
requires Q>=30729. Q=32768 is the smallest power of two that fits. Likewise,
2802642834 sequential controller-path ticks already exceed 2^31, so U=2^32 is the
smallest power-of-two period accommodating even those paths. Thus merely removing
unused margins does not halve either parameter while retaining this layout,
controller and power-of-two clocks. These are construction-specific facts, not
requirements of Gray/Gacs or a justification for U<=128Q.

For one top cell encoded twice, the current per-instruction strategy entails

```
32768 lower colonies * 4294967296 lower periods * 34526 instructions
= 4859102522956054528 instruction occurrences.
```

This is exact work-volume arithmetic for that strategy, not a runtime estimate
or a lower bound on every possible accelerator. A complete nested run must
change that execution cost fundamentally, or use a more efficient globally fixed
construction. Removing self-reference or evaluating decoded upper transitions
on the host would change the task rather than solve this cost.

Memory is less prohibitive than a dense-state estimate suggests. A dense packed
projected buffer costs 338 GiB, but one actual MEM Data bank for the same ring is
2602303488 bytes. The existing guarded resident representation has a previously
computed total allocation-plus-staging estimate of 7666317536 bytes (about
7.14 GiB), documented in [NESTED_WINDOWS.md](NESTED_WINDOWS.md). That full-ring
allocation pilot has not been run; its separate 8 GiB reservation remains pending.
Representation compression and its supported canonical domain must remain
explicit rather than being mistaken for arbitrary noisy-state storage.

One concrete GPU tuning opportunity remains: the resident source fixes WORKERS
at 256, launching eight 32-thread blocks for these event kernels. Larger worker
counts could expose more colony parallelism; no speedup is established until
measured. This can improve one-link/full-ring experiments but does not remove
billions of lower periods. Any such variant must preserve the same physical
expression, clock boundaries and packet guards, use private build products, and
coordinate its memory with the main agent.

## Validation, ownership and next work

| CPU check | Seconds | Peak host RSS (KiB) |
|---|---:|---:|
| Independent-register distance audit, including two rejected mutations | 1.936501 | 60044 |
| Exact schedule work count | 1.481112 | 87400 |

Both ran under a 512 MiB virtual-memory cap with OPENBLAS_NUM_THREADS=1 and exited
zero. The C++ compiler inherited that cap. Files and generated binaries are in
our fixed_rule namespace; no shared CUDA artifact, running job or historical
data was changed. Read-only approval timeouts were retried; the final runs are
terminal and no retry duplicated a live experiment.

```sh
python -m experiments.fixed_rule.certify_small_holder_backend_distance_independent --output figs/fixed_rule/small_holder_backend_distance_v2.json
python -m experiments.fixed_rule.measure_small_holder_execution_budget --output figs/fixed_rule/small_holder_execution_budget_v1.json
```

Use fresh output names when rerunning. Frozen v1 sources/results and all mutation
builds are retained. The successful private audit source and binary are hashed
in its JSON; it requires only the host C++ compiler, not nvcc.

Next close the event backend's staging/clock/reconstruction interface against
[NOISELESS_MACROSTEP.md](NOISELESS_MACROSTEP.md), and evaluate a concrete strategy
for the instruction-volume obstacle. A worker-count benchmark is useful for
smaller physical experiments but is not a depth-two solution. Complete upper
work periods, repair across levels, general noisy amplification and the known
finite-cap defect remain open. The full project goal stays active.

Evidence SHA-256 values:

- `small_holder_backend_distance_v1.json`: `54c9ae554d059cbd296131ca968092310cafdefc1f2c5b9f7bd95769a74f080d`
- `small_holder_backend_distance_v2.json`: `0c2fe64bc430e7a85db8b127f73d8258a369df4d11d13a5d3845e3a06ba0c313`
- `small_holder_execution_budget_v1.json`: `7acaf2fa8fadb0043be9d12f67fa47238dbf0ae55943e0797aa86f312f2a4577`
