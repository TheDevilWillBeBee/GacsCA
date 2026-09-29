# Physical contextual commit after cross-colony head damage

2026-09-27. The actual 17-colony state from
[CONTEXTUAL_RECOVERY.md](CONTEXTUAL_RECOVERY.md) now reaches commit and reset.
Only lower colony **9** commits a wrong decoded successor: its complete Info
record is zero, differing in **26 raw F words /12 mutable G words**. Colony 8,
which originally received the noise burst, decodes correctly. This is a noisy
macrostep result in the checked contextual window; upper-layer recovery and a
complete noisy depth-two continuation are not yet established.

The independent audit passes in **302.611631 s**. It verifies all 210578 trace
intervals, covering 5117471 scalar core candidate outputs through 1405940
explicit evaluations of distinct complete neighborhoods. It also checks
1114112 full native clock outputs /171573248 raw words and 470 full scalar G
probes. All six complete checkpoints and the final state agree. Peak sampled
audit RSS is 832028 KiB; both run and audit finish with return code zero.

## What physically happened

The run starts from the exact quiet-recovery endpoint at local time 1232635846.
Colony 8 has five Data defects and its normal evaluator. Colony 9 has its normal
evaluator plus the two incoming heads. The run retains all 17 colonies in one
global physical ring, all Q Data words per colony, every raw controller register,
and the actual copies crossing colony boundaries.

The initial three-head interaction in colony 9 leaves an invalid-PC FETCH head.
The other colonies complete their evaluations at time **2022020768**, matching
the final-phase deadline recorded in
[RETIMED_NOISELESS_MACROSTEP.md](RETIMED_NOISELESS_MACROSTEP.md). This leaves
2979232 ticks before ACTIVE_END=2025000000 in this run. At commit U=2147483648, the only
remaining primary head is at colony-9 address 1699. Its colony commits zero
Hold words into Info. At U+1, every colony again has one head at address 0 and
PC 0. This reset does not itself recover the committed simulated-state error.

The expected upper successor at position **9566** has its active WRITE
controller, PC 7075, operands 9564/9565, destination 9566 and value
18446744073709551614. The actual zero decoded state loses those fields,
its Address=9566 and Age=1232619429, and two neighboring Data copies. All 17
decoded records remain within the fixed field widths. The other 16 decoded
records agree completely with the intended local-rule successors.

The middle colonies' gathered inputs were previously checked against the actual
upper NAND checkpoint. The commit occurs at absolute physical time
2647030067984596992 when combined with the inherited depth-two entry time.
The window's periodic outer boundaries retain the qualification in
CONTEXTUAL_BURST.md; this result is not an executed full-Q lower-ring noise run.

Three Data words survive reset outside the normal bank workspace, at colony-8
addresses 30960–30962. Their values are respectively 648528792106043840,
2418452793257099264 and 72061992092962836. The complete saved procedure arrays
retain them. They cannot be dropped when preparing the next lower period.

## One fixed rule, global physical event execution

`retimed_holder_global_events.py` extends the existing transport scheduler to a
bounded whole colony ring. Physical event outputs use the unchanged native F
evaluator; hard-wiring projection G and every boundary copy use the actual global
neighborhood. Static metadata templates avoid recomputing immutable ROM fields.
These are execution optimizations, not depth-dependent state or rule changes.

Each head's transport stops at instruction, operand, reflection or interaction
events. All controller words move together, while Data stays at its physical
site. Commit and reset evaluate every physical site with full native G and its
actual old radius-seven halo, before installing any output. Complete raw
reconstruction is checked against those outputs. Unsupported flags, geometry,
mail, head locations or controller residues reject instead of being projected
into the executor's domain.

Five distinguishing executor tests pass in **7.473 s**, including second-colony
targets, global boundary copies, reflection, omitted-register rejection, and
every physical output of commit/reset with unused Data. The scheduler records
**210578** physical event/transport intervals for independent audit.

## Independent audit method

The auditor reconstructs the exact initial physical state from the preceding
artifact. It checks transport against instruction, operand and first/last-marker
sites extracted from the actual ROM. Every skipped path must avoid side effects
and head interactions; no clock event may be skipped. Each literal event replays
the scalar core procedures on every possibly changing site in all 17 colonies.

Within one tick, identical complete scalar neighborhoods share a computed
result. The memoization key contains every procedure/controller/mail word and
the canonical address, which fixes metadata; age is fixed within that tick.
No field is omitted because an opcode appears not to use it. Four audit tests
pass in **3.599 s**, including differing high controller bits and rejection of
skipped operands, collisions and first-marker reflections.

Inactive holds and commit/reset are independently constructed from the scalar
clock semantics. At the two clock events, every complete physical output is
also compared with full native G; scalar full-G probes provide an additional
source-transcription check. Every saved checkpoint and final complete procedure
array must match. Canonical geometry, zero flags/Wf, coherent copies, stationary
Signals and zero mail are explicit restrictions. This is an audit of this
trajectory, not a general scheduler theorem or noise threshold.

## Cost and reproduction

The physical run advances **914847803 ticks** in **547.916526 s** on CPU.
It executes 100444 literal-event ticks, 792263710 guarded transport ticks,
122483647 inactive ticks and two whole-ring clock steps: **6231583** complete
native local outputs. Peak sampled RSS is **1585344 KiB**; the process reports
1589720 KiB. No GPU is allocated by this run. It finishes inside its 600 s /
4096 MiB watchdog; this CPU implementation is a correctness reference and
still needs batching or GPU acceleration for practical repeated experiments.

Commands below write corresponding private `.log` files. Choose new artifact
names on rerun; existing datasets are not overwritten.

```sh
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_global_events_tests_v2_watch.json --seconds 120 --rss-mib 1536 -- python -m unittest tests.fixed_rule.test_retimed_holder_global_events -v
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_macrostep_audit_tests_v1_watch.json --seconds 120 --rss-mib 1536 -- python -m unittest tests.fixed_rule.test_retimed_holder_macrostep_audit -v
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_contextual_macrostep_v1_watch.json --seconds 600 --rss-mib 4096 -- python -m experiments.fixed_rule.retimed_holder_contextual_macrostep --output figs/fixed_rule/retimed_holder_contextual_macrostep_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_contextual_macrostep_audit_v1_watch.json --seconds 1500 --rss-mib 3072 -- python -m experiments.fixed_rule.audit_retimed_holder_contextual_macrostep --input figs/fixed_rule/retimed_holder_contextual_macrostep_v1.json --output figs/fixed_rule/retimed_holder_contextual_macrostep_audit_v1.json
```

The NPZ retains every procedure word at all six checkpoints and the complete
event trace. The evidence index is
`figs/fixed_rule/retimed_holder_contextual_macrostep_evidence_v1.json`.
No shared source, historical dataset or other agent's job was modified.

## Next: carry the actual state into receiving-layer repair

The next task is physical continuation from this U/U+1 endpoint. Its malformed
encoded metadata and surviving nonMEM Data do not automatically satisfy the
frozen noiseless endpoint relation. Establish a checked extension or execute
the physical normalization prefix, retaining all remaining state. Then execute
the next lower periods and compare the actual receiving-layer repair.

A prospective nonMEM-Data invariant must account for all clock phases,
communication and Signal capture, not only the current quiet interval. A
prospective Info-normalization claim must check the actual initialization
program's reads and writes. Neither is claimed by this report. Merely inserting
the measured zero symbol into a separate upper fixture would be a conditional
fault-transfer test, not the missing physical nested continuation.

The fixed alphabet, neighborhood, implementation and hard-wired description are
unchanged. Full noisy depth two, general amplification, thresholds, practical
Q/U optimization, robust caps, depth three and the existing Flag2/SimBit
source-fidelity questions remain open. The full goal stays active. STATUS.md
is the handoff; MAIN_AGENT_NOTES.md remains the other agent's reply channel.
