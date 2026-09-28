# Reused temporary storage in the fixed holder ROM

2026-09-26. This continuation makes concrete progress toward a smaller practical
self-simulator. The raw local rule is unchanged from parallel_holder; the fixed
hard-wired ROM and projected physical rule form a separate revision. There is
no depth-dependent allocator, rule selection or evolving host interpreter.

## Implemented allocation and executable meaning

word_allocation.py computes last uses of the finite expression DAG, reserves
separate input storage, and pins all output wires until the output-copy phase.
It also pins the zero literal needed by the physical output-copy ADDs. A symbolic
owner verifier checks every operand before each write and checks every retained
wire at the end. It rejects stale operands, lost outputs, invalid graphs and
allocations for a different descriptor. This is a construction-time certificate.
Physical execution still uses the ordinary described local READ/WRITE controller.

The new reuse_holder_program.py lowers all 13,443 raw descriptor operations into
the existing opcode family. NAND, ADD and EQ operands may commute to increasing
physical address; SHR and LT retain their order. A forward-oriented free-slot
choice avoids unnecessary sweeps when possible. The fixed result-bank capacity
is 384 words, of which 362 are used. Neither quantity depends on hierarchy depth.
Inputs, all three histories, outputs, metadata queries and scratch words have
separate nonoverlapping storage.

The raw transition descriptor is shared unchanged, SHA256:
a3c4a7c33310a9ee930c409691b0e1850830801da1ef67092cecbed6dd161cdc.
The new hard-wired ROM SHA256 is:
d5dd28ae38a843d94e98256ddf3055a3e7b9566596a22f74028763e551d3933b.
The projected physical state remains 105 words / 2,724 bits with radius seven;
the raw descriptor has 154 words / 4,110 bits including metadata. The projected
identity includes the new ROM hash. Reusing the raw rule must not be confused
with claiming the old and new projected hard-wired automata are identical.
The actual simulation regenerates metadata from this new ROM locally.

## Space/time results and the informative first attempt

| Quantity | Serial holder | Parallel vote | Reused storage |
|---|---:|---:|---:|
| Computation cells | 57,332 | 43,808 | 30,727 |
| Evaluation ticks | 4,533,298,561 | 1,664,309,717 | 1,168,148,348 |

The selected layout has 9,924 memory cells, 20,802 instruction cells and one
end cell. Versus parallel voting alone, computation space falls about 29.9%
and evaluation time about 29.8%. Versus the original serial holder, they fall
about 46.4% and 74.2%, respectively. These are literal computation costs, not
GPU wall-clock speedups. Q=2^30 and U=2^37 remain unchanged during this controlled
comparison; the actual colony/work-period reduction is still to be implemented.

A lowest-free-slot allocator used only 240 result cells, but kept evaluation at
1,628,889,904 ticks: shorter storage caused extra backward operand trips. Its
source snapshot and numbers are preserved in reuse_holder_first_fit_v1.json.
Commuting safe operands and choosing forward free slots improved the result.
The compile-time capacity study tried 240,256,320,384,512,768,1024,1536,2048,
4096,8192, plus lowest-free allocation. Above 384 the measured layout did not
improve and used the same 362 cells. This is a bounded search, not a proof of
optimality. All alternatives and their limits are in reuse_holder_layout_search_v1.json.
No host transition ran in place of local dynamics during this search or validation.

## Verification and exact commands

    OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_word_allocation.py -v
    OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p 'test_reuse_holder_*.py' -v

Four allocator tests passed in 1.846 s: all raw outputs for 64 arbitrary complete
input arrays, 100 randomized DAGs including every opcode and unused results,
retained-zero/output negative witnesses, graph validation and capacity rejection.
Twenty-one integration tests passed in 59.783 s. They cover complete raw
scalar/descriptor/native parity; exact semantic descriptor embedding in the ROM;
depth-one/two/three raw encoding with identical rule and ROM; protected temporal
voting; reset/clear priorities; locality; active computation and tested two-holder
repair; full physical conjugacy of the execution quotient; accelerated/literal
transport; suffix flag proof and native witnesses; and recurrent old Signals.
The old three-corruption negative witness remains outside the repair contract.

    OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.reuse_holder_validation --prefix figs/fixed_rule/reuse_holder

This harness runs each physical execution and each audit in a fresh sequential
subprocess. Its JSON records all nine exact commands, exit statuses and wall
times. It completed in 78.025921 s, with maximum child RSS 901,700 KiB (about
881 MiB). No GPU allocation or large shared-CPU allocation was made. The host
peak includes audit copies; it is not the physical dense configuration size.

Both complete one-link macrosteps and all audits passed. Each macrostep audit
checks 2,229 saved complete-native local transition witnesses, every raw output,
the actual prefix handoff and the symbolic flag-profile certificate. The combined
audit checks 274,877,906,944 physical ticks, identical rule/alphabet/neighborhood/
ROM, the exact full-state handoff, carried Signals and 40 changed raw controller
fields in each represented transition. There are 15 distinct represented cells.
The execution guards forbid host rule/evaluator calls during physical dynamics.
The second period starts from the actual first commit without reinitialization.

Artifacts: reuse_holder_{execution,macrostep,recurrent_execution,second_macrostep}_v1
(JSON, NPZ and frozen source archives), their independent audits, the combined
two-period audit, test logs, and reuse_holder_resources_v1.json. The validation
harness, all runs and audits are terminal. Shared raw-rule/native/proof sources
are included in source hashes; the earlier fixtures remain unchanged.

## Remaining work and next concrete revision

The 30,727-cell computation region now fits spatially within 32,768 cells, but
this is only a storage observation. The current constants, metadata, stage
schedule and raw descriptor still use the old Q/U. A Q=32,768 construction must
recompile its complete self-description once, with one fixed physical rule and
ROM at all requested depths; check communication collisions and payload delivery;
choose independent stage deadlines from measured work; and recheck repair and
trickle-down conditions. Changing Q in a benchmark alone is not that construction.

The next step is this explicit smaller-colony / independent-work-period revision,
using the tested allocator. Retain sufficient separated gathering stages and
repair margins; do not impose U/Q=128. Then establish actual deeper dynamics
with a bounded GPU representation that can carry physical faults. Full depth-two
and depth-three macrosteps, robust termination and statistical cross-level
correction/amplification remain unproved. The complete goal is still open.

Ownership: new word_allocation.py; reuse_holder_* program/projection/initialization/
execution modules and C adapters; their tests, drivers, audits and result files;
this report and STATUS.md. Shared raw-rule components were read/reused unchanged.
No shared-module change, GPU scheduling request or CUDA rebuild was needed.
MAIN_AGENT_NOTES.md remained absent; the main agent can reply there.
