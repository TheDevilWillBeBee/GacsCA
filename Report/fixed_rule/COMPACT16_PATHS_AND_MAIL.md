# Compact16: physical controller paths and communication

2026-09-27. The actual Q16384/U2^30 ROM now has directly checked controller
paths and regular-clock mail composition. This connects its complete symbolic
self-computation to the new rule's physical instruction and transport behavior.
It does not yet establish the whole-period block relation or execute a complete
physical work period.

The physical descriptor and ROM remain those in
[COMPACT16_CANDIDATE.md](COMPACT16_CANDIDATE.md):

```text
F   53f7adbf7c34df6b17897b20a0d0654108f23a9c064defb89bb3c6d1a7fb846b
ROM 4d055889959a880f189539dc213801780f8e2efa3daa7cb31e72cb3003f48b32
```

No rule, alphabet, parameter, ROM or backend changed in this turn. New diagnostic
modules explicitly bind the smaller geometry and clock; they do not reuse an
old-Q conclusion by changing its label. In particular, the inherited proof-term
ROM lookup would have used the old fallback boundary for constant tail queries.
The new `Words.basic_lookup` uses the actual compact16 fallback for constants
and symbolic lookup terms. Tests exercise both constant and interval tail queries.

## Controller paths and packet schedule

The previous812 direct regular-clock cases are checked for descriptor identity,
source hash and complete case coverage. The new proof adds84 complete local
identities: last-cell leftward flight, MEM FETCH flight, and ten non-MEM
flight/reflection cases over each of the seven regular intervals. Each checks
all154 raw outputs at nine holders. A syntactic dependency check justifies the
quiet exterior under the stated coherent one-head hypotheses.

The actual ROM then passes:

| Check | Count |
|---|---:|
| Ordinary instruction paths, including both IF_THIRD branches | 12809 |
| META paths across four complete query domains | 392 |
| Reset/vote entry and successor dispatch paths | 12907 |
| Instruction occurrences in the six-phase schedule | 23727 |
| Actual SEND sites | 1786 |
| MEM addresses, including the tail | 3452 |

Paths include all stale controller registers and aliased memory operands. Flights
check their actual ROM guards and preserve complete controller state. META query
domains cover0..16383, including the endpoint,25-cell fallback gap and five tail
cells. Fourteen-bit proof variables represent these bounded physical positions;
the unchanged physical Address alphabet still has15bits.

| Phase | Head stopped at Age | Last packet delivery | Margin |
|---|---:|---:|---:|
| Gather0 | 25745335 | 25859266 | 1140734 |
| Gather1 | 53746026 | 53859264 | 1140736 |
| Gather2 | 81746717 | 81859263 | 2140737 |
| First evaluation | 455121322 | 455121353 | 40878646 |
| Precommit halt | 500005522 | none | 994478 |
| Final evaluation | 872794231 | none | 77205769 |

The schedule checks same-track collision exclusion, unique destinations, MEM
target identity, protected destination access ordering, and clock boundaries.
It uses actual new-ROM path durations and independently generated schedule
times. Mutating an ordinary duration or dispatch duration fails these checks.

## Communication identities

Complete-descriptor support analysis establishes that all45 raw head/controller
outputs are independent of every old mail field, without a coherence or clock
assumption. Other non-Data/non-mail outputs have the same independence, and
packet outputs separate by track. This does not imply that delivered Data cannot
affect a later controller read.

The regular-clock composition proof handles all eight controller phases plus
quiet state across seven intervals:63 cases,78694 complete raw output-word
identities. It permits arbitrary coherent packet words, direction, metadata and
Data; the domain still requires canonical geometry, a uniform regular active
clock, zero flags/Signal/Wf and at most one head. It proves the controller/mail
separation formula directly from the new F, including simultaneous delivery,
right-track priority and WRITE override.

An exact BDD induction covers each hop count0..7, every source Address and target
coordinate, and262144 elapsed values. Each case quantifies46 independent bits
and checks19 relations for position, validity, delivery and remaining hops.
Leftward propagation follows by coordinate reflection. Payload is copied
unchanged. The actual MEM target, no-collision and protected-access premises are
supplied by the separate schedule checks; the algebra alone would not supply
those premises.

## Literal execution and distinguishing tests

Six new tests pass. Three eight-tick packet trajectories execute the full native
physical rule: rightward across a colony edge, leftward across an edge, and a
zero-hop internal delivery. Each delivers at tick4 and retains the delivered
Data thereafter. Seven boundary outputs are cropped per step from a padded
window, so artificial array-wrap effects cannot enter the checked causal cone.
Selected full raw outputs are independently compared to the scalar local rule
at every tick. Two further literal transitions verify simultaneous left/right
delivery priority and WRITE overriding delivered Data.

Other tests recheck schedule hashes/coverage, reject altered path durations,
verify new-Q tail lookup, and show that dropping the non-MEM premise invalidates
the corresponding flight identity. These short native trajectories are local
physical dynamics, not decoded upper-rule replacements. They are not complete
colony periods or noise-recovery experiments.

## Resources and reproduction

Both proof jobs ran concurrently with768-MiB child RSS thresholds; the sum of
their sampled child peaks was below150MiB. Tests used512MiB. These are watchdog
samples, not instantaneous OS memory caps or measurements of every parent
process. All work stayed well within the40GB task RAM allowance. No GPU was
allocated or rebuilt, and the previously sealed private native binary was reused.

| Check | Internal seconds | Process peak KiB | Watch seconds / sampled KiB |
|---|---:|---:|---:|
| Extra leaves, paths and schedule | 42.354959 | 77848 | 43.496495 /91172 |
| Mail composition and packet induction | 31.098395 | 61244 | 32.001683 /62148 |
| Six tests | 1.728 | Not separately recorded | 2.678628 /65988 |

```sh
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_holder_paths_v1_watch.json --seconds 180 --rss-mib 768 -- python -m experiments.fixed_rule.certify_compact16_holder_composition --part paths --output figs/fixed_rule/compact16_holder_paths_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_holder_mail_v1_watch.json --seconds 120 --rss-mib 768 -- python -m experiments.fixed_rule.certify_compact16_holder_composition --part mail --output figs/fixed_rule/compact16_holder_mail_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_holder_composition_tests_v1_watch.json --seconds 90 --rss-mib 512 -- python -m unittest discover -s tests/fixed_rule -p test_compact16_holder_composition.py -v
```

All three jobs are terminal with exit0. Only new files in the owned namespaces,
the archived handoff and STATUS changed. Main-agent notes remain absent and
unedited; shared sources, jobs, CUDA artifacts and historical data were untouched.

## Remaining composition

These results cover regular instruction/communication behavior, not the
reset/vote/capture/forcing/commit interfaces. Next reprove those smaller-rule
identities, connect them to the complete self-ROM data flow, and establish the
entry relation across successive work periods. Then validate a private execution
backend and run full periods and cross-level faults. The original source
qualifications concerning Flag2 and computed SimBit remain. General robustness,
finite-horizon terminal reliability and depth-three execution are still open.
The full project goal remains active.
