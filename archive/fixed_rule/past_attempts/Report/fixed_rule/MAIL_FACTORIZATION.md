# General mail factorization and fixed-ROM schedule joins

2026-09-26. This closes a broader local coupling obligation than the positional
packet examples in [PACKET_EVENT_REFINEMENT.md](PACKET_EVENT_REFINEMENT.md).
The full physical descriptor has no old-mail dependency in any of its 45 next
head/controller outputs. A separate full-state reduction handles arbitrary
incoming packet words throughout a coherent neighborhood, and the actual ROM's
schedules pass collision and destination-access checks for every SEND site.
These are conditional composition results, not a closed work-period theorem.

## Two distinct claims

The support checker traces every output through the complete 13,442-operation
DAG. All outputs except Data and packet fields are independent of old mail;
each packet track depends only on old mail from its own track. This is an exact
syntactic dependency statement for every raw finite-alphabet neighborhood,
including damaged replicas, flags and geometry. It is not a claim that mail can
never affect future control: delivery changes Data, which later reads may use.

The stronger factorization has a narrower domain. Let E erase only old packet
fields, retaining old Data and controller state. Evaluate F(E(x)) as a baseline.
At each represented primary, replace that baseline's Data and packet fields by
explicit receive/decrement/drop/delivery/write/send formulas applied to x. The
checker proves the resulting complete raw tuple equals F(x).

This quantifies arbitrary incoming target, payload, remaining-count and valid
words at every nearby primary simultaneously. It permits arbitrary coherent
metadata, Data, stale controller fields at the head and head direction, with each
of the eight phases covered. Other primaries have zero head/controller fields.
There is either no head or one head; the nine checked
holders cover that head's complete support, and the no-head case supplies the
exterior. Canonical Address, uniform regular active Age and zero old
flags/Signal/Wf remain assumptions. All seven regular clock intervals are covered.

The baseline F(E(x)) is deliberately reused. This is a reduction from mail-bearing
execution to previously checked controller behavior plus explicit transport; it
is not an independent proof of the baseline or an execution backend. No host
transition is substituted into the physical hierarchy. The local formulas retain
right-track delivery priority, WRITE priority, old-Data reads/SEND and same-track
SEND overwrite, now with arbitrary nearby traffic rather than isolated packets.

The proof needed one additional algebraic normalization: a sum of repeated copies
of the same Boolean term crosses a threshold between 1 and its multiplicity iff
that Boolean is one. The simplifier checks the one-bit width and avoids overflow.
Tests enumerate Boolean truth values and verify that two-bit inputs do not receive
that rewrite. Independent scalar/native checks do not use this simplification.

## Conditional schedule join

`certify_small_holder_mail_schedule.py` checks actual fixed-ROM metadata and joins
existing ordinary/META duration catalogs to entry/successor dispatch routes. All
34,526 instruction occurrences across six entries agree exactly with the separate
ROM schedule calculation. Each whole dispatch/body segment fits a certified
regular active clock interval, and the corresponding physical head stops at the
expected instruction. META query domains have identical total duration.

The metadata check enumerates all Q Addresses. Exactly 9927 are MEM: the prefix
and five tail cells. Every MEM index equals its Address. Thus a valid actual SEND
target has precisely the coordinate-hit interpretation used by the existing
packet-flight induction; non-MEM cells cannot absorb it. That induction is replayed
for all eight hop counts (49 independent bits per case). Leftward coordinates are
the reflection of the rightward relation. Payload is unchanged during flight.

All 6478 actual SEND sites are covered. Source and target are actual MEM cells,
tags fit direction plus three-bit hops, and every delivery distance is positive.
Every birth-to-delivery interval stays inside a regular clock interval. Within
each phase, destinations are unique and all controller Data accesses to each
destination precede its delivery. This conservatively excludes simultaneous reads
as well, although those read old Data. It permits prior initialization/access to
a destination, which matters for the final ten signal deliveries.

For same-track collision checks, group packets by direction and
(source Address - signed velocity * birth time) modulo Q. Overlapping lifetimes
on one such line are rejected. The modulo-Q check is conservative across all
colony translations, so it covers synchronized copies of the program without
assuming one particular ring length. This uses the common schedule as a premise;
it is not a proof of arbitrary asynchronous damaged colonies.

| Entry | Instruction occurrences | Packets | Head-stop tick | Last-delivery tick | Deadline margin |
|---|---:|---:|---:|---:|---:|
| Gather 0 | 2440 | 2156 | 163095355 | 163312990 | 38013602 |
| Gather 1 | 2312 | 2156 | 151483995 | 151699320 | 49627272 |
| Gather 2 | 2312 | 2156 | 151486307 | 151699321 | 49627271 |
| Precommit halt | 1 | 0 | 16988 | — | 67091876 |
| Third evaluation | 13736 | 10 | 1168587340 | 1168589385 | 72924598 |
| Final evaluation | 13725 | 0 | 1167972849 | — | 39986703 |

Ticks in this table are relative to the entry's reset/vote old Age. The third
evaluation deadline is CAPTURE_AGE-1, so its margin is one tick smaller than the
older capture-budget table. This explicit choice excludes the physical old Age
whose updated Age triggers capture. No parameter or schedule changed.

The schedule join assumes canonical coherent zero-flag/Signal/Wf entries with
empty initial mail, the stated head geometry and regular-clock invariance. It
checks the timing, metadata and noninterference obligations needed for an
inductive physical interpretation. It does not establish the entry-production,
Signal/flag invariants or the complete global induction across work periods.

## Validation and resources

| Check | Result | Seconds | Peak host KiB |
|---|---:|---:|---:|
| Factorization pilot | 9 cases passed | 4.538820 | 65,592 |
| Full factorization | 63 cases, 78,694 raw word identities | 27.907496 | 65,292 |
| Independent semantic audit | passed | 25.924176 | 64,628 |
| Complete schedule join | 34,526 occurrences / 6478 SEND sites | 1.436940 | 88,416 |

Six factorization tests passed in 4.541 s and five schedule tests in 2.046 s.
Mutations introducing mail-dependent control, cross-track dependency, discarded
deliveries, aliased MEM indices, same-track overwrite, destination access at
delivery or a changed instruction duration are rejected.

The independent audit compares 3563 complete mail-bearing outputs and 3563
complete mail-erased baseline outputs against both scalar F and its native
compiled description. It reconstructs the full factorization result and checks
all 154 fields. The sample includes 2030 dense-delivery outputs, every SEND tag,
both Address wrap boundaries, all-ones words and random values. These are finite
semantic checks of the symbolic relation, not a trajectory replay. All runs were
bounded CPU work; no GPU process, large allocation or CUDA rebuild was launched.
No failed attempt preceded the successful factorization or schedule results.

## Commands

Existing evidence is protected from overwrite; use fresh output names to repeat.

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.certify_small_holder_mail_factorization --pilot --output figs/fixed_rule/small_holder_mail_factorization_pilot_v1.json
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.certify_small_holder_mail_factorization --output figs/fixed_rule/small_holder_mail_factorization_v1.json
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_mail_factorization.py -v
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_mail_factorization --certificate figs/fixed_rule/small_holder_mail_factorization_v1.json --output figs/fixed_rule/small_holder_mail_factorization_audit_v1.json
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.certify_small_holder_mail_schedule --output figs/fixed_rule/small_holder_mail_schedule_v1.json
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_mail_schedule.py -v
```

## Remaining obligations and coordination

The new factorization removes the need to enumerate every nearby head/packet
position in the canonical one-head domain. Next, express the global occupancy and
controller/Data induction explicitly, and extend the relation to retained Signals
and the flag/clock overrides actually encountered across periods. Join it to
reset, vote, capture, commit and rest transitions. Physical maintenance and
simulated-layer repair cannot be inferred from ordinary transport correctness.

Gray pp.31–32 specialized hard-wiring/projection and Gacs sections9.2–9.3 modified
self-correcting simulation remain the source target. The physical alphabet,
local neighborhood, complete evaluator self-description, ROM and transition
implementation are unchanged. Q/U optimization, practical two-level execution,
reliable finite termination and general cross-level noise suppression remain
unfinished. U<=128Q remains unnecessary; the original goal stays active.

Owned additions: the factorization and schedule certificates, native audit, two
test files, this report and evidence. Only our STATUS handoff is updated among
existing reports. Prior status history is preserved in a new archive linked from
STATUS. No shared source/job changed, no main-agent notes were present, and the
separate 8 GiB scheduling request remains pending/unused. Please reply in
MAIN_AGENT_NOTES.md. Absence of the historical third-link process is not an audit
of experiment completion.

## Evidence SHA256

- `small_holder_mail_factorization_v1.json`: `c1048017aeabcda5ecc5773ebf6920f0eae6d781d4b3efb3bf97c0ac23bff474`.
- `small_holder_mail_factorization_audit_v1.json`: `7c34c1518882e250523d0a69ab61d2e0466273fdbf32489f433da0f816c7b89f`.
- `small_holder_mail_schedule_v1.json`: `08be97b0047b526e41d4a8b04f1c0516c79f8c0eb47b303fb3744fca43122ee3`.

Descriptor remains `af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`; ROM remains `c59c72abe15729e4848ce549b31f1faec63465f16da2c717f0eb233fb1e7cbe4`.
