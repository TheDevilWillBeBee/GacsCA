# Delivery-rule suffix: actual flags, controller commit, and resource limits

The fixed delivery rule has not changed. It has radius five, a 590-bit projected
physical state (25 words), a 788-bit complete raw description (32 words), and a
2,680-operation self-description with SHA-256
`4391ae3edb105da9e9d4865be2040e3cf80fa7952e554b0f19e537505b238eed`.
Q=8,388,608 and U=128Q. Depth is still initial encoded data. No additional register
pair, level branch, description language, or depth-selected kernel was added.

The complete-state physical trajectory now reaches **Age 98Q**. The controller
component separately reaches the first commit at U and passes a raw-field audit.
These are different claims: the remaining **30Q physical flag ticks** have not
been completed. This revision therefore still has no verified complete macrostep,
second work period, or depth-two dynamics. The earlier two-period early-rule
fixture has fewer mechanisms and remains a separate result.

## Source scope and exact composition domain

Gray pp. 27–34, especially the hard-wiring/ProgramBit projection on pp. 31–32,
and Gács §§9.2–9.3 motivate a specialized self-simulator of the same or suitably
modified rule. They do not require an arbitrary-program platform. The existing
complete description includes this evaluator's own state, clocks, metadata,
communications and signal transition. See [DELIVERY.md](DELIVERY.md) for the
construction, source qualifications, and measured program budget.

The new representation uses a property of the implemented rule on **canonical
Address and uniform Age**, established in `delivery_factorization.py`:

1. This geometry is invariant for arbitrary old physical flags.
2. Controller, Data and Signal outputs do not depend on those flags.
3. Mail is the zero-flag result followed by clearing when computed Flag1 is one.
4. Wf2 is the signal-derived value gated by computed Flag1.

After the actual delivery/capture prefix, every mail word is zero. The remaining
controller schedule produces no packet: the stage-five IF_THIRD gate halts before
the ten SENDs. `delivery_control_world` rejects nonzero initial mail, checks all
output mail words, and requires the exact coherent five-copy boundary Signal
pattern. It only admits the suffix through U. Noncanonical geometry, unexpected
Signal support and a generated packet invalidate this representation.

Under these guards, the controller quotient and the independently evolved four
physical flags compose to **every field of the same physical local transition**.
`delivery_composed_world` exposes actual flags in both individual cells and all
stored arrays; it does not report its zero-flag controller quotient as physical
state. On a component failure it invalidates the wrapper, since the two advances
are not transactional. Padding has canonical geometry and a defined controller
state; complete flag runs cover every padding site as well as stored sites.

This is a domain-specific physical execution optimization. Recursive light-cone
memoization below also concerns only physical spacetime blocks. Neither method
interprets an encoded upper controller in the host language or takes hierarchy
depth as an execution argument. Host `Program.evaluate` and scalar upper-rule
callbacks are disabled during the main physical executions.

The literal printed Flag2 rule and the explicit voted-old-Signal D10 choice
remain unchanged. [The shared D8 audit](../flag2_recovery_gap.md) describes
persistent isolated Flag2 errors and candidate alternatives. No easier Flag2
variant was silently selected for these performance experiments. This work does
not establish faithful repair of arbitrary damaged geometry or noise robustness.

## Completed execution and independent checks

Commands use the project root and CPU only. Output stems refuse overwrites.

```sh
python -m experiments.fixed_rule.delivery_control_execution --input figs/fixed_rule/delivery_execution_v1 --output figs/fixed_rule/delivery_control_execution_v1
python -m experiments.fixed_rule.audit_delivery_control --input figs/fixed_rule/delivery_control_execution_v1 --output figs/fixed_rule/delivery_control_audit_v1.json
python -m experiments.fixed_rule.delivery_forcing_execution --input figs/fixed_rule/delivery_execution_v1 --checkpoint figs/fixed_rule/flag_cutoff_checkpoint_v1.npz --output figs/fixed_rule/delivery_forcing_execution_v1
python -m experiments.fixed_rule.audit_delivery_forcing --input figs/fixed_rule/delivery_forcing_execution_v1 --output figs/fixed_rule/delivery_forcing_audit_v1.json
python -m experiments.fixed_rule.flag_byte_bounded_execution --input figs/fixed_rule/flag_cutoff_checkpoint_v1.npz --output figs/fixed_rule/flag_byte_bounded_v1 --ticks 65536
python -m experiments.fixed_rule.audit_flag_byte --input figs/fixed_rule/flag_byte_bounded_v1 --output figs/fixed_rule/flag_byte_bounded_audit_v1.json
```

All six commands passed.

| Evidence | Exact outcome |
|---|---|
| Controller suffix | 268,435,457 physical controller ticks; 2.4161268267780542 s; 18,202 literal, 210,636,863 quiet, 57,780,392 guarded scan ticks; 1,304,606 local evaluations |
| Controller audit | 147 archived/live sources; all five saved arrays replayed; every raw vote and Hold word checked; scalar/native/description agreement; active simulated WRITE `0x123456789ABCDEF0`; 690 native neighborhood pairs; 5.1315116779878736 s |
| Entire forcing window | 16,777,217 additional physical ticks, 96Q−1→98Q; 90.09758451394737 s; 3,920,139,548 packed-word evaluations; 1,721 complete-native neighborhood comparisons across six frames |
| Complete state at 98Q | 192,937,984 physical sites, 183,586 stored core/tail sites; 11 flag runs; Flag1 count 125,829,120, Flag2 count 78,320,307; Wf1=Wf2=0 |
| Forcing artifact audit | 151 archived/live sources; every stored flag bit independently checked; controller replay exact; raw Info preserved; old cutoff reproduced; 0.9483850188553333 s |
| Bounded post-cutoff flags | 65,536 ticks; 0.24369460251182318 s including proof output; 2,893 memoized queries, 414 physical leaf evaluations; final flag counts 123,863,040 / 77,936,861 |
| Bounded derivation audit | All 2,893 queries verified from 1,152 complete-native local truth-table checks; 180 distinct leaf neighborhoods; 1,971 periodic initial subblocks |

The first forcing run was saved before a later compression attempt was stopped.
The completed forcing experiment replays it from the actual prefix Signal values
and checks its immutable cutoff SHA-256:
`d5ad2339193c4f15f60aa108a8f3dd7ff24c9bfd2209137cd96090a83526a8b9`.
The new complete-state artifact SHA-256 is
`5fa8eeba681f0851a0807e0422e5a062035abc5bc8bfffe9cb81dbb03381c039`.

The forcing audit independently checks provenance, representation, each stored
flag bit, raw Info and controller replay. Its long flag replay uses the same
packed engine; the sampled native comparisons are not an independent second
long-trajectory algorithm. In contrast, the bounded light-cone audit verifies
**every saved temporal query** from smaller queries and native leaf truth tables,
then checks the entire periodic initial DAG and the final whole-ring counts.
A mutation test changes a local query result and recomputes the artifact checksum;
the derivation verifier still rejects it.

## Preserved failures and resource measurements

The packed flag implementation evaluates each output bit using only old sites
within radius five. It groups equal 64-site word triples and separates colony
edges. It skips time only after exact whole-state equality, without crossing a
forcing-clock change. This was efficient throughout the forcing window but not
through the subsequent printed-rule dynamics.

| Attempt | Measured limitation and evidence |
|---|---|
| 64-site repeated-word RLE | At 250,000 ticks after cutoff: 78,162 runs, 13,712,142,527 cumulative word evaluations, 293.9713149201125 s. Deliberately stopped; `flag_words_execution_v1_stop.json` preserves the last batch. |
| Nine-word (576-site) block RLE | Handles a nine-word periodic homogeneous test, but the actual mixed case reaches 3,300 runs and 11,760,623,700 post-conversion word evaluations at 1,500,000 ticks; 329.8699563750997 s including forcing prefix. Deliberately stopped after saving cutoff; `flag_blocks_execution_v1_stop.json`. |
| Initial block conversion bug | Mixing signed ends and unsigned bit words promoted to float64 and destroyed all-ones words. Fixed before the recorded run; exact full-plane round-trip checks added. Initial apparent speed result discarded in `flag_blocks_conversion_failure_v1.json`. |
| Python 64-site light cones | Resource probe failed while handling MemoryError after a 4 GiB virtual-memory limit was applied. No trajectory; `flag_pair_hash_full_failure_v1.json`. |
| Python 8-site light cones | Full 251,658,240-tick request raised MemoryError under 6 GiB virtual-memory bound; `flag_byte_execution_v1_failure.json`. |
| Compact native 8-site light cones | Full 251,658,240-tick request and bounded 1,048,576-tick request both failed under 6 GiB. The native catch-all does not distinguish allocation from other exceptions. No final state/proof; `flag_byte_native_execution_v1_failure.json` and `flag_byte_bounded_v2_failure.json`. |

The native implementation uses an 18-bit leaf label (eight Flag1 bits, eight
Flag2 bits, first/last boundary metadata), compact node IDs and hash tables.
Its 265,218-node successful proof includes 262,144 implicit possible leaves;
only 3,074 nodes are additional tree nodes. These are **host representation**
resources, not new physical state bits or a depth ceiling. Its uint32 query-time
and tree-size guards are also host execution limits. The full physical rule is
still defined on its original fixed alphabet for arbitrarily large initial data.

The larger failure used the same command as the successful bounded experiment,
with `--output figs/fixed_rule/flag_byte_bounded_v2 --ticks 1048576`. Original
sources, logs and archives are retained. No shared or GPU process was stopped.

## Focused tests

Each row used:
`python -m unittest discover -s tests/fixed_rule -p NAME -v`.
There are **24 passing focused tests** in these nine files; this is not a claim
that every historical fixed_rule test was rerun.

| NAME | Passed | Seconds | Log stem under figs/fixed_rule |
|---|---:|---:|---|
| test_delivery_control.py | 3 | 0.599 | delivery_control_tests_v1 |
| test_flag_words.py | 4 | 2.904 | flag_words_tests_v2 |
| test_flag_blocks.py | 4 | 0.730 | flag_blocks_tests_v1 |
| test_flag_hash.py | 3 | 0.185 | flag_hash_tests_v1 |
| test_flag_pair_hash.py | 3 | 0.182 | flag_pair_hash_tests_v1 |
| test_flag_byte_hash.py | 2 | 0.340 | flag_byte_hash_tests_v1 |
| test_flag_byte_native.py | 2 | 170.221 | flag_byte_native_tests_v1 |
| test_delivery_composed.py | 2 | 0.710 | delivery_composed_tests_v1 |
| test_flag_derivation_audit.py | 1 | 1.761 | flag_derivation_audit_tests_v2 |

The native tests compare 10,000 leaf triples and actual periodic causal results
at 0, 1, 17, 1,000 and 65,536 ticks. Earlier tests cover rule identity/width across
depths, every raw controller field in the encoding, self-description closure,
locality, and active dynamics; they remain frozen reference evidence. New tests
add actual physical nonzero flags, complete-field composition, rejected mail and
Signal domains, work-period boundaries, exact block conversion, and rejection of
forged local derivations.

## Remaining construction work

First finish the physical flag suffix using a measured, bounded-resource method,
then compose it with the audited controller commit. Preserve actual residues
into a second period; current suffix implementations deliberately reject that
extension. A source-grounded alternative Flag2 rule would be a separate fixed
construction revision with its own complete description and distinguishing tests,
not a runtime performance switch.

Full spatial redundancy of workspace/mail/controllers, damaged-geometry repair,
organized finite-depth termination, deeper dynamics, and measured noise remain
missing. The existing zero-payload flagged cap is a tested orbit, not a robustness
boundary. Depth-three raw initialization still does not certify depth-three
execution. No final self-correcting construction or full Gács/Gray fidelity claim
is made. The full research goal remains active.

## Preservation audit

`suffix_source_preservation_v1.json` scans 25 source manifests and 175 distinct
live files. It found four mismatches confined to older v1 records: the initial
`vertical_slice_v1.json` points to earlier versions of `vertical_slice.py`,
`tape.py` and `test_machine.py`; `word_temporal_capacity_v1.json` points to an
earlier explanatory-comment version of `word_temporal_capacity.py` (already
noted in WORD_VALIDATION.md). This continuation did not edit those files or
rewrite the old records. The capacity v1 source archive remains available;
the vertical-slice v1 record has no corresponding source archive. Do not claim
that every historical v1 manifest matches current code.

The projected/regenerated/window/word/clock/early/delivery execution manifests
and the new 147-/151-source suffix manifests match live files. New source,
reports, exact test logs, audit records and preserved failure metadata are
captured by `figs/fixed_rule/suffix_sources_v1.{json,tar.gz}`. Build products stay
in the owned namespace. Shared modules, reports, datasets and GPU dependencies
were not edited. No `third_link_initialized` process was visible in the latest
read-only process check; that observation does not establish experiment completion.
