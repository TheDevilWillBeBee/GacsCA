# Actual fixed-ROM symbolic data-flow certificate

2026-09-26. The actual immutable ROM now has an all-input symbolic data-flow
certificate covering retrieval, both metadata regenerations, the complete raw
self-description, Signal payloads, commit and scratch clearing. It is conditional
on completed-instruction semantics and the clock/transport schedule abstraction.
It is a diagnostic proof tool, not a physical executor or permission to replace
lower evolution with an upper-rule callback.

## What the checker reads and establishes

`certify_small_holder_rom_dataflow.py` reads the actual `base_rom()` records,
including entry words in the header, instruction identities and operands, memory
reset markers, and stopping instructions. It does not just check an opcode list
or compare the stored descriptor digest. It symbolically executes the fixed
program at the level of completed instructions, with unsigned 64-bit expression
terms and actual immutable-ROM queries.

Fifteen colonies have 2310 independent initial raw input words. Every input word
is retained as a symbolic variable with its declared width; no controller state
is specialized to an inactive fixture. Initial metadata may be inconsistent:
the actual LOAD/META instruction sequence must normalize it. Metadata queries
refer to this same ROM, including its fallback, rather than a test program.
The expression model uses only constants, input words, NAND/ADD/SHR/EQ/LT, and
this fixed lookup. Its algebraic reductions are constant arithmetic, commutative
operand ordering, addition/shift by zero and equality of identical terms.

For each phase, the checker follows the real instruction records and verifies:

1. Input metadata is normalized by executed LOAD/META operations, without
   changing the represented raw controller fields.
2. Each of the three complete histories has the correct normalized 15-cell
   neighborhood, in every one of its 154 fields. Actual SEND direction, target,
   source and hop count determine delivery. No destination is silently supplied
   by a host upper transition.
3. The three histories agree, so the existing bitwise temporal majority returns
   their exact common words. The third and final evaluations both produce the
   complete raw F result, followed by actual output metadata normalization.
4. The third evaluation supplies all five left and right Signal-buffer words
   with the intended output F2 and F1. The final evaluation sends no late Signal
   packets. The idle phase writes no Data.
5. Commit transfers Hold to Info, and the next reset leaves exactly the correct
   raw output in Info and zero Data elsewhere.

In notation from [SMALL_HOLDER_CLOSURE.md](SMALL_HOLDER_CLOSURE.md), this verifies
the program's normalized data result iota(pi(F(iota(x)))); it does not replace
that expression with the incorrect identity F iota = iota G. All raw evaluator
and controller outputs are included. The actual compiler's reusable workspace
addresses are followed, so an overwritten live word or lost output copy would
change the symbolic result.

The modeled network is a 15-colony periodic ring with independent inputs, which
contains one distinct input for every radius-seven neighbor. No general theorem
for arbitrary physical ring size is asserted here. A larger-ring physical
refinement still needs its communication locality/aliasing argument.

## Schedule and dependency checks, and their precise premise

The instruction schedule recipe is the current full-sweep head model. Each
arithmetic read/write, SEND, LOAD, META and stop contributes its specified travel
and event time. All packet arrivals must precede the phase deadline. Actual
same-track world-line intervals are grouped and checked for overlap. The checker
rejects duplicate delivery destinations and controller accesses to deferred
foreign-history targets. Prior histories must survive later reset masks.

| Modeled phase | Head stop | Last delivery | Deadline |
|---|---:|---:|---:|
| First gather | 163095355 | 163312990 | 201326592 |
| Second gather | 151483995 | 151699320 | 201326592 |
| Third gather | 151486307 | 151699321 | 201326592 |
| Third evaluation/delivery | 1168587340 | 1168589385 | 1241513984 to capture |
| Final evaluation | 1167972849 | No packets | 1207959552 |

These are model-relative ticks, not new GPU measurements. In particular, the
META duration recipe must be refined to the actual moving controller uniformly
for every query result. Correct output values from the earlier exhaustive
regeneration run are useful evidence but do not by themselves prove all physical
event times or collision exclusion for every input history.

At the completed-instruction abstraction, the check covers 517890 instruction
instances, 2205 metadata queries, 97170 packets and 96806 symbolic terms across
all five phases and both evaluations. It completes in 3.311505 s with 91864 KiB
host peak. No GPU work period or new kernel was run in this turn.

## Distinguishing tests and independent concrete audit

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.certify_small_holder_rom_dataflow --output figs/fixed_rule/small_holder_rom_dataflow_v1.json
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_rom_dataflow.py -v
# Five tests, 7.092 s, OK.
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_rom_dataflow --certificate figs/fixed_rule/small_holder_rom_dataflow_v1.json --output figs/fixed_rule/small_holder_rom_dataflow_audit_v1.json
# Passed, 4.374619 s, 92364 KiB host RSS.
```

Mutations retain supported instruction types but remove a raw PC output, change
an output META selector, misroute a gather, or erase Info with a reset marker.
All are rejected. The controller-output and metadata mutations reach the actual
computed-Hold comparison, rather than failing an up-front ROM-hash allowlist.
Additional tests check word overflow/shift behavior, the symbolic reductions
and ROM/fallback values.

The independent audit recomputes the certificate, instantiates all symbolic
terms on 16 randomly generated full projected rings, and compares 240 complete
raw outputs against independent scalar and native F followed by projection/lift.
Every controller field is randomized. This checks the symbolic rewrite and lookup
semantics against executable rules; it does not execute the lower program through
its physical ticks. The symbolic identity has all-input scope under its explicit
abstraction, while the randomized audit is finite implementation evidence.

## Remaining physical closure obligations

The source motivation remains Gray's specialized ProgramBit elimination and
Gacs sections 9.2–9.3's suitably modified self-simulation, as documented in the
existing closure audit. Those sources do not make a completed-instruction model
an automatic physical simulation theorem. This checker belongs only in the
proof/diagnostic namespace and is never called to evolve a physical world.

The next concrete step is a local-controller refinement certificate: actual
FETCH/READ/WRITE/TRANSMIT/LOAD/META/head-reflection events must implement these
instruction effects and scan durations for arbitrary encoded values. Particular
care is required for in-core versus fallback metadata queries, zero metadata
values, endpoint hits, and preservation of all stale control fields.

That refinement must then be joined with physical coherent evolution, packet
transport, Signal capture/flag clearing, and the proved full reset identity.
The current [reset encoding](RESET_ENCODING.md) plus this data-flow certificate
still falls short of the full arbitrary-input work-period relation. No nested
trajectory compression has been installed. Reconstruction at intermediate
physical times and departures from the clean family under faults remain separate
obligations. Full nested upper periods, terminal reliability, and general
cross-level noise suppression are still unfinished.

## Provenance and ownership

`figs/fixed_rule/small_holder_rom_dataflow_v1.json` SHA256: `191ff4eb3714c0c68bd8f4e4e5f1484d9cf17b7c78b71a781d052cb7e1668ffb`.

`figs/fixed_rule/small_holder_rom_dataflow_audit_v1.json` SHA256: `07b1e79b6a7993345d5accad178b2057339f010251975deeb8c6ddc5243b1e01`.

`figs/fixed_rule/small_holder_rom_dataflow_tests_v1.log` SHA256: `7dc776d00d51c6631dcc5b40ecbfdfccccc8128d66f375d626a95db9e5c1eaf0`.

Physical descriptor:
`af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`.
ROM bytes: `c59c72abe15729e4848ce549b31f1faec63465f16da2c717f0eb233fb1e7cbe4`.
Owned additions are the diagnostic certificate, its test and audit, this report,
and namespaced evidence. No construction, existing source or CUDA artifact was
changed. All own handles are terminal. MAIN_AGENT_NOTES.md remains absent and
the separate 8 GiB reservation request is pending. The full goal remains active.
