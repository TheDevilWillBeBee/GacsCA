# Quiet continuation across a physical colony boundary

2026-09-27. The exact 17-colony endpoint from
[CONTEXTUAL_BURST.md](CONTEXTUAL_BURST.md) has now advanced another 16384
physical ticks. The two extra heads enter **the next lower colony**, at quiet
ticks 1775 and 1776. By the endpoint all flags have cleared, but five primary
Data defects remain in colony 8 and two extra heads remain in colony 9.
This is a physical cross-colony trajectory, not a decoded-macrostep result.
The full fixed-rule self-simulation goal remains active.

## Exact state transfer and unchanged transition

The new `retimed_holder_contextual_flags.py` restores every inherited bank word
and raw controller record, verifies the restored snapshot, and exposes bounded
multi-colony raw views. Its flag adapter moves the actual physical flags into
the existing packed GPU flag engine at the same physical time. It checks
**all 85786624 raw words** before and after the conversion, one colony-sized
block at a time. The operation advances zero transitions.

The 118 sparse exceptions reduce to 19 because 99 Flag1 sites are now represented
in the packed plane. The flag sites are retained, not repaired or removed. All
remaining raw exceptions, including Data outside the usual workspace, remain
in the complete local evaluator. Canonical physical geometry, zero Wf, late
clock phase and a mail-free reference are checked restrictions of this adapter.

The existing physical executor then performs every quiet tick, with full G
evaluation on exception support and the existing canonical background/flag
execution. No Data absorption, host-computed successor, alternate ROM, new
alphabet or depth-specific physical kernel is introduced. The model still has
Q=32768, U=2147483648, radius seven and the same self-description hash
`6e2f29f61bf281ec5d346cd58e717cf7e5b0afea263d2c17a18a58de295d8d23`.

Five CPU tests pass in 1.969 s. They retain complete saved exception records,
distinguish copies on opposite sides of a colony boundary, compare both full
raw colonies with the existing renderer under nonzero flags, and reject
inconsistent active flags or an omitted raw field.

## Observed trajectory

Quiet time starts at lower local time 1232619462. At quiet tick 1774, copied
procedure fields already differ in colony 9 while both primary extra heads
are still in colony 8. At tick 1775 the leading primary head reaches address
0 of colony 9; at tick 1776 both primary heads are there. The independent
physical boundary matters: wrapping within colony 8 would give a different
receiving controller and different future interactions.

At final local time 1232635846, **19 sites /90 raw words** differ from the
matching healthy run. The five Data defects remain at colony-8 addresses
6996, 6997 and 30960–30962. The latter three are outside the normal bank
workspace and must be retained by subsequent executors.

| Lower colony | Head address | Phase | PC | Role |
|---:|---:|---|---:|---|
| 8 | 25983 | READ_A | 7076 | Original evaluator |
| 9 | 14608 | READ_META | 8 | Incoming extra head |
| 9 | 14609 | FETCH | 4456458 | Incoming extra head |
| 9 | 25983 | READ_A | 7076 | Original evaluator |

Both flag planes are zero at this endpoint. The remaining heads/controllers
have not been normalized away. No permanent-failure or upper-repair conclusion
follows from this endpoint alone.

## Independent audit

The audit passes in **322.789562 s**, peak sampled host RSS **1811324 KiB**.
It independently executes **1736704 scalar core candidate outputs** across all
16384 ticks and all 17 colonies. Additional full native physical checks cover
**2229760 output states /343383040 raw words**. All saved observations and the
final representation agree. It independently identifies the first extra primary
head in colony 9 at tick **1775**, and complete flag clearing at tick **15453**.
The audit and physical-run watchdogs both finish with return code zero.

The audit is separate from the physical run. It retains all logical procedure
words at every physical site in all 17 colonies and runs the scalar core rule
on every possible nontrivial output each tick. Global neighbor addresses cross
the actual colony boundary. Omitted candidates contain unchanged Data and zero
controller/mail fields in the checked active, clock-event-free domain.

Canonical geometry, coherent copies, zero Wf, stationary Signal and zero mail
are checked initially; every scalar candidate's mail output must stay zero.
Under these conditions, actual flags cannot alter a procedure through geometry
replacement or packet clearing. Flag1 is independently evolved as an exact
integer recurrence within each colony; Flag2 remains zero. The first two ticks
also execute the complete native physical rule at every site in both runs.
Six further native windows cover the boundary interaction at ticks 1773–1778.
All saved complete physical observations and the final state are compared.

This is a trajectory audit in a restricted verified execution domain, not a
general arbitrary-state sparse-execution theorem or an amplification theorem.

## Resources and reproduction

The GPU continuation completes in **103.157817 s**, peak sampled host RSS
**461440 KiB**, explicit GPU allocation **29369874 bytes**. It performs
1998848 full local exception evaluations and retains at most 19 sparse
exceptions after flag conversion. The separate packed flag engine retains all
evolving flags. The test watchdog records 258036 KiB peak host RSS.

The physical run uses a 240 s /1536 MiB watchdog; the independent CPU audit
uses 600 s /3072 MiB. Both are well below the user's 40 GB host allowance.
The pending substantial GPU reservation is unused. Shared source, other
agents' jobs and historical artifacts remain untouched.

Exact commands, with output redirected to corresponding private `.log` files:

```sh
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_contextual_flags_tests_v1_watch.json --seconds 60 --rss-mib 1024 -- python -m unittest tests.fixed_rule.test_retimed_holder_contextual_flags -v
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_contextual_recovery_16384_v1_watch.json --seconds 240 --rss-mib 1536 -- python -m experiments.fixed_rule.retimed_holder_contextual_recovery --ticks 16384 --output figs/fixed_rule/retimed_holder_contextual_recovery_16384_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_contextual_recovery_audit_v1_watch.json --seconds 600 --rss-mib 3072 -- python -m experiments.fixed_rule.audit_retimed_holder_contextual_recovery --input figs/fixed_rule/retimed_holder_contextual_recovery_16384_v1.json --output figs/fixed_rule/retimed_holder_contextual_recovery_audit_v1.json
```

Use new artifact names on reruns. The NPZ retains exact initial, attached,
observed and final representations, including complete raw exception rows.
Evidence index: `figs/fixed_rule/retimed_holder_contextual_recovery_evidence_v1.json`.

## Next macrostep and scientific limits

The next computation must continue both affected colonies through commit.
Colony 9 now contains interacting heads, while colony 8 still contains Data
defects. Any factorization into colony executors needs an explicit checked
boundary relation: fivefold physical procedure copies use neighboring colonies,
and resetting controller state does not justify discarding unused-space Data.
Alternatively a global executor can retain the complete coupled representation.

Then carry the actual decoded errors through subsequent lower periods and
receiving-layer repair. Damaged Info metadata and noncanonical reset-time heads
may fall outside the frozen noiseless endpoint hypotheses; those conditions
cannot be repaired by host projection. The periodic outer boundaries of the
17-colony window retain the qualification in CONTEXTUAL_BURST.md.

Full noisy depth-two macrosteps, general amplification, thresholds, practical
Q/U optimization, robust finite-depth caps, depth three, and the existing
Flag2/SimBit source-fidelity ambiguities remain open. STATUS.md is the handoff;
MAIN_AGENT_NOTES.md is the other agent's reply channel and is not edited here.
