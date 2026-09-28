# A fixed Q=16384, U=2^30 candidate with unchanged state width

2026-09-27. The `compact16_holder` candidate actually uses **Q=16384 and
U=1073741824**, independent of initialization depth. Its complete self-description
and ROM have been regenerated and checked. The physical alphabet remains
154 raw words/4090 bits and105 mutable words/2704 bits, with radius seven.
This is a separate candidate, not a replacement for the frozen retimed execution
baseline. Its complete physical work period has not yet been executed.

## Fixed construction and costs

The sparse retrieval design retains all154 encoded Info/Hold fields, retrieves
689 mutable operands into three histories, and regenerates49 own-ROM operands
from the voted Address before each evaluation. Scratch capacity320 and the
low-address MASK optimization remain fixed compiler choices.

| Quantity | Retimed execution baseline | Compact16 candidate |
|---|---:|---:|
| Q | 32768 | 16384 |
| U | 2147483648 | 1073741824 |
| Core cells | 27721 | 16354 |
| Core MEM cells | 9911 | 3447 |
| Stored instructions | 17809 | 12906 |
| Optimized descriptor operations | 10450 | 10452 |
| Controller-path ticks | 2001129064 | 819159153 |
| Raw / projected bits | 4090 /2704 | 4090 /2704 |

There are25 unused cells between the core and the five tail cells. The complete
ROM schedule's six phase checks fit their fixed budgets. These schedule checks
remain conditional on physical instruction/transport refinement; the old
new-ROM path catalog does not automatically transfer to this new physical rule.

```text
RESET_AGES = (0, 28000000, 56000000, 500000000, 502000000)
ACTIVE_ENDS = (27000000, 55000000, 499000000, 501000000, 950000000)
VOTE_AGES = (84000000, 502000000)
CAPTURE_AGE = 496000000
WF_START = 500000000
WF_END = 500032768
```

For one top cell encoded twice, physical site count falls from2^30 to2^28 and
ticks per top transition from2^62 to2^60. That is a sixteenfold reduction in
literal site-update volume, **not a measured runtime improvement**. A dense
packed projected buffer still needs84.5GiB. A single canonical MEM bank would
need452460544 bytes (about431.5MiB); that compressed representation requires
its own domain and backend validation for this candidate. No such full-ring
allocation or GPU execution was made in this turn.

## Preserving the wider physical alphabet

Address remains15bits although Q uses14. Age remains32bits although U uses30.
The new scalar rule uses the new moduli; two description helpers now explicitly
use log2(Q) for modular Address arithmetic rather than the raw field width.

Every input/output ROM regeneration query is masked to Q-1, including the
zero-offset query. Without that last change, a legal raw Address above16383
would query a fallback record instead of the projected cell's actual own ROM.
The independent normalization used by the checker was changed consistently.
The checker proves computation on arbitrary **typed** raw inputs, including
these excess Address/Age values; it does not silently restrict the alphabet.

Tests explicitly reject using the15-bit alphabet width as the Q modulus and
bypassing the zero-offset query mask. The tests also check high Address/Age
states through scalar, complete descriptor and privately compiled native
transitions. A homogeneous damaged configuration can retain an excess Address
when no adjustment vote exists; the construction does not assert that all raw
Addresses normalize after one step. Uniform cap Ages do wrap modulo the new U.

## Complete self-reference and direct local evidence

The complete optimized description equals the new physical descriptor on
arbitrary typed inputs. Symbolic execution of the actual new ROM compares all
154 raw outputs, including every controller copy, with that descriptor and
the candidate's own ROM projection. It includes retained histories, both
evaluations, metadata regeneration, Signal payloads, commit and reset. This is
conditional instruction data flow, not a host replacement for physical dynamics.

The new physical descriptor is
`53f7adbf7c34df6b17897b20a0d0654108f23a9c064defb89bb3c6d1a7fb846b`;
ROM is
`4d055889959a880f189539dc213801780f8e2efa3daa7cb31e72cb3003f48b32`.
Both are fixed across depth. Depth1–3 tests retain complete controller fields,
check the new Q^d initial geometry, and confirm identical rule identity. These
are initialization/encoding checks, not completed depth-three evolution.

The regular-clock local controller identities were **reproved directly against
the new descriptor**. 116 event families across seven regular active intervals
give812 passing symbolic cases and1125432 complete raw output-word identities.
They cover945999993 legal clock values without clock sampling, canonical
Address geometry over all16384 positions, coherent controller/Data copies,
symbolic metadata and the stated event hypotheses. FETCH, operand reads/writes,
SEND birth, metadata hit/fallback and reflection are included. The domain has
one head or quiet state, zero flags/Signal/Wf and no incoming mail; reset, vote,
capture, commit and other nonregular times are excluded. This is not a proof
for arbitrary faulty geometry or an entire work period.

Six tests pass, including24 seeded arbitrary raw neighborhoods, boundary and
high-clock cases, native/scalar/descriptor comparisons, active controller copies,
complete own-ROM computation, fixed identity and negative mutations. The private
native build is under `figs/fixed_rule/build/compact16_holder_native_*`; no shared
CUDA artifact or historical execution binary was modified.

## Ordinary finite-depth terminal data

The complete homogeneous terminal orbit was independently checked for all2^30
normalized Ages, including its six necessary head/PC pulses and all154 raw
fields. Twelve geometry proofs also preserve the permanent single-Address
defect, quantifying all2^32 raw Ages, all32768 typed replacement Addresses and
22 independent workspace bits. Thus ordinary terminal data remains available,
while this cap still lacks single-bit Address repair. Composing it through
arbitrary depth still depends on the new candidate's unfinished block relation.

## Resources, reproduction and limits

All jobs exited0. No GPU was allocated or rebuilt. The existing watchdog used
512MiB thresholds for ROM/boundary checks and768MiB for event proofs/tests.
Its measurements cover the direct Python child; native compiler subprocess
memory is not included in those sampled figures. All work used small CPU
allocations, within the user's40GB task limit.

| Check | Internal seconds | Process peak KiB | Watch seconds / sampled KiB |
|---|---:|---:|---:|
| Complete own-ROM / description | 4.274011 | 62000 | 4.626157 /62832 |
| 812 direct regular-clock cases | 175.615730 | 141312 | 175.925145 /144640 |
| Six tests | 16.334 | Not separately recorded | 16.689682 /71828 |
| Complete cap /12 defect cases | 2.198926 | 51020 | 2.518674 /52140 |

```sh
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_holder_rom_v1_watch.json --seconds 60 --rss-mib 512 -- python -m experiments.fixed_rule.certify_compact16_holder_rom --output figs/fixed_rule/compact16_holder_rom_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_holder_clock_events_v1_watch.json --seconds 240 --rss-mib 768 -- python -m experiments.fixed_rule.certify_compact16_holder_clock_events --output figs/fixed_rule/compact16_holder_clock_events_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_holder_tests_v1_watch.json --seconds 120 --rss-mib 768 -- python -m unittest discover -s tests/fixed_rule -p test_compact16_holder.py -v
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_holder_boundary_v1_watch.json --seconds 60 --rss-mib 512 -- python -m experiments.fixed_rule.prove_compact16_holder_boundary --output figs/fixed_rule/compact16_holder_boundary_v1.json
```

The source basis remains Gray's specialized ProgramBit projection and Gacs's
modified-rule self-simulation, discussed in [SPARSE_RETRIEVAL.md](SPARSE_RETRIEVAL.md).
The candidate-B Flag2 and computed-SimBit/Signal qualifications remain. No general
noise amplification or threshold claim follows from this parameter reduction.

Next reprove/combine the remaining physical path, incoming-mail and barrier
identities for the smaller rule, then port and validate a private execution
backend and run successive complete periods. Whole-period closure, noisy
cross-level behavior and practical full depth-two execution remain required.
Only owned namespaces and STATUS were changed; main-agent notes, shared sources,
jobs and historical data remain untouched. The full project goal remains active.
