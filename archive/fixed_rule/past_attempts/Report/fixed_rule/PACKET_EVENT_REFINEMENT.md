# Packet events and continuous SEND successors

2026-09-26. Full-raw local identities now cover 134 packet-event families in all
seven regular active clock intervals: 938 symbolic cases, 1,300,068 raw output
word identities. Actual GPU execution also passed 384 SEND-to-next-FETCH
trajectories with emitted packets retained. These extend the previously
mail-free [dispatch contracts](DISPATCH_PATH_REFINEMENT.md); they do not yet
establish general head/mail composition or a whole work-period relation.

## Independent local relation

The new packet-event checker independently specifies old and next complete
physical records, then compares their 154 raw fields through the fixed physical
self-description at nine holders. Both incoming tracks are present together;
payloads and allowed target/controller/Data words are symbolic. Each direction
has invalid, positive-hop transport, zero-hop target-miss and delivery cases.
Boundary cases separately cover exhaustion/drop, decrement-to-zero with delivery
or miss, and counts 2..7 continuing across the edge. Invalid packets may retain
arbitrary stale input fields, but those fields are cleared on output.

At an interior destination neither channel crosses a colony edge. At Address 0
the right-moving channel crosses an edge; at Address Q-1 the left-moving channel
does. The proof bounds Address accordingly, covering every canonical position.
The quiet MEM cases check target equality or an explicit disequality. A separate
non-MEM extension permits all fifteen nonzero kind values and arbitrary targets:
matching index alone never delivers on a program or fallback cell. Together
these cases cover quiet reception on the actual ROM's memory/program/gap/tail
metadata, under the stated coherent geometry and clock assumptions.

The checked priorities are:

- Simultaneous right-moving delivery wins over left-moving delivery.
- A local WRITE wins over both deliveries.
- A read and SEND use old Data, before that tick's deliveries.
- SEND overwrites a continuing packet on its emitted track; the other track is
  retained. This is a local priority identity, not permission to ignore unwanted
  packet loss in a composed program.

Controller interactions include READ_A, all five READ_B arithmetic operations,
LOAD, WRITE, and all sixteen SEND direction/hop tags. Complete stale controller
fields, both tracks, Data and physical geometry are checked, not just payloads.
The additional non-MEM certificate extends the frozen MEM/event source without
altering it. The existing descriptor-support result supplies the quiet exterior
under the same coherent-state conditions.

The scope remains canonical/coherent states, zero flags/Signal/Wf, regular active
clocks and either no head or the stated one-head interaction. Reset, vote,
capture and commit overrides remain outside these leaves. No arbitrary head
placement relative to packets, packet trains, faulty geometry or flag-clearing
claim follows automatically. The prior ballistic receive induction in
`prove_small_holder_packet_flight.py` is a separate algebraic ingredient; it has
not yet been joined to these full-raw identities and a global occupancy invariant.

## Validation and measured cost

| Check | Result | Seconds | Peak host KiB |
|---|---:|---:|---:|
| Packet event certificate | 707 cases | 148.461296 | 148,852 |
| Non-MEM extension | 231 cases | 45.507037 | 84,324 |
| Packet native/scalar audit | 19,089 complete outputs | 71.628010 | 59,916 |
| Non-MEM native/scalar audit | 6,237 complete outputs | 22.308157 | 58,468 |
| GPU SEND pilot | 48 trajectories | 1.870177 | 170,500 |
| GPU selected-site run | 384 trajectories | 8.271291 | 182,668 |
| Saved GPU checkpoint audit | passed | 9.754163 | 71,376 |

Ten tests passed across three focused suites: six packet-event tests (3.679 s),
two metadata tests (0.613 s) and two SEND-trajectory tests (0.527 s). They reject
wrong delivery priority, missing boundary decrement and admission of MEM into the
non-MEM lemma. Concrete checks force matching indices on all fifteen non-MEM
kinds and check old-Data read/SEND behavior. The pilot certificate also passed
101 families in 21.804472 s; its audit checked 2727 outputs in 9.987981 s.

The GPU run uses first/last actual SEND sites for each direction/hop tag: 32 sites,
six Data patterns and two initial Ages (1 and 738197505). A single initialized
world evolves through the instruction, packet birth, selected edge/delivery
boundaries, dispatch and next FETCH. It never installs an intermediate state.
Host evaluator, full-rule and primary controller calls are disabled during GPU
advance; host calculations are diagnostic expectations only.

After packet birth the driver uses the existing device-guarded transport/literal
`World.run` API. This handles live packets outside the independent/gather batch
accelerator's guards. The fixed physical kernel and all guards are unchanged.
Total GPU advance was 0.375047 s, process GPU memory 422 MiB, explicit allocation
3,726,576 B, and 21,000 local evaluations. No CUDA rebuild or large GPU reservation
was used.

The run saved and checked 19,536 complete logical records plus selected full raw
physical probes. Its independent audit rechecks every saved record and expected
raw digest, and checks 1598 complete scalar/native one-tick boundary outputs.
At the final checkpoint 24 packets have delivered and 360 remain in flight;
they are explicitly represented, not discarded. This run therefore establishes
sampled SEND continuation, not delivery completion for every hop count. Actual
raw GPU assertions reside in the hashed driver; the audit does not recover
unsaved records or replay every microstep.

## Preserved failed attempts

The first symbolic pilot stopped because bounded u64 subtraction and its masked
three-bit form had different symbolic DAGs. Given the positive count bounds both
expressions agree. The corrected expected formula uses ordinary bounded
subtraction; no physical rule changed. The original log and source snapshot are
`small_holder_packet_events_pilot_v1.log` and
`small_holder_packet_events_failed_v1_source.py.txt`.

The first real-SEND GPU pilot stopped with batch rejection -4 when a live packet
fell outside the accelerator's protected-target/mail-free domain. The failed log
and source snapshot are `small_holder_send_dispatch_pilot_v1.log` and
`small_holder_send_dispatch_failed_v1_source.py.txt`. It produced no successful
manifest. The corrected driver retains those packets and uses the existing
physical transport/literal API after birth. This is a guard-respecting execution
change, not removal of a guard or replacement of a simulated transition.

## Reproduction

All commands below completed. Existing output names are protected; use new names
for reproduction. Logs have corresponding stems in `figs/fixed_rule/`.

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.certify_small_holder_packet_events --pilot --output figs/fixed_rule/small_holder_packet_events_pilot_v2.json
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.certify_small_holder_packet_events --output figs/fixed_rule/small_holder_packet_events_v2.json
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.certify_small_holder_packet_metadata --output figs/fixed_rule/small_holder_packet_metadata_v1.json
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_packet_events.py -v
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_packet_metadata.py -v
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_send_dispatch.py -v
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_packet_events --certificate figs/fixed_rule/small_holder_packet_events_pilot_v2.json --output figs/fixed_rule/small_holder_packet_events_pilot_audit_v1.json
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_packet_events --certificate figs/fixed_rule/small_holder_packet_events_v2.json --output figs/fixed_rule/small_holder_packet_events_audit_v1.json
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_packet_metadata --certificate figs/fixed_rule/small_holder_packet_metadata_v1.json --output figs/fixed_rule/small_holder_packet_metadata_audit_v1.json
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_send_dispatch_execution --pilot --output figs/fixed_rule/small_holder_send_dispatch_pilot_v2
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_send_dispatch_execution --output figs/fixed_rule/small_holder_send_dispatch_all_v2
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_send_dispatch --execution figs/fixed_rule/small_holder_send_dispatch_all_v2 --output figs/fixed_rule/small_holder_send_dispatch_audit_v1.json
```

## Next obligations and scientific scope

Compose packet-flight leaves with the ballistic induction, actual MEM target
metadata and occupancy/collision conditions. Prove the controller/mail
noninterference relation for arbitrary relative positions used by the fixed
program. Existing ROM data-flow checks exclude overlapping same-track lifetimes
and accesses to protected foreign histories, but those checks alone do not prove
physical composition. Flag clearing and clock/Signal/reset/rest joins remain
necessary before an all-input whole-period relation follows.

Gray pp.31–32 specialized hard-wiring/projection and Gacs sections9.2–9.3 modified
self-correcting simulation remain the source target. The descriptor still includes
the evaluator's complete state and transition. No physical alphabet, neighborhood,
ROM, Q, U, depth case or kernel changed. U<=128Q is not required. Practical full
two-level execution, reliable finite termination and general cross-level noise
suppression remain unestablished; the original goal remains active.

Owned additions are the two packet certificates, two native audits, SEND driver
and checkpoint audit, three focused test files, this report and evidence. Only
our STATUS handoff was edited among existing reports. No shared source or job was
changed. All own processes were checked terminal. MAIN_AGENT_NOTES.md was absent;
please reply there. The separate 8 GiB scheduling request remains pending/unused.
The historical third-link process was not observed; absence is not completion
evidence. The earlier expanded mail-free dispatch run remains unverified; the new
SEND run is a distinct experiment with its own successful manifest.

## Evidence SHA256

- `small_holder_packet_events_v2.json`: `7249d8a606b67000913e8d3235b526a429ee4fdc1a0795e4f91e879780f5959b`.
- `small_holder_packet_metadata_v1.json`: `6ef1446dac24b8a8b61afcd6e7294b89cc34ead7b5c5e1ed453444f675e53b91`.
- `small_holder_packet_events_audit_v1.json`: `524bcdf43ab66b4e15ca7cd4351a2bbff4873db15f550f83cab3b08408a7eb35`.
- `small_holder_packet_metadata_audit_v1.json`: `793719cb50bd1909c808023f5fe4c4dcc471b7d07dddb565868ac8bcb7f5e9e8`.
- `small_holder_send_dispatch_all_v2.json`: `3740d2afca316a86523d29546d708e048a452d35735f27c1ebd278e78fc7ec6b`.
- `small_holder_send_dispatch_audit_v1.json`: `1a525cd5063a69694cf0a2e0dde3cf0b4580a93d7c7d56169d603803e1cab1f5`.

Physical archive: `52b49e4c40732137ce8f8ce04462d2ce4308b57156e6172e18491e079745793e`.
Descriptor: `af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`.
GPU binary: `4419e5fdd8caeb81c884db3ede3d709d677693aee1943482040e171bc54f1c7e`.
