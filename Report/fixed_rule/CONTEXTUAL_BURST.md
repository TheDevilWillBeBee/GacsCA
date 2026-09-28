# Lower-layer noise in an actual receiving-controller context

2026-09-27. A 17-colony physical run now reproduces the stronger noise burst
using inherited lower-layer banks encoding the previously executed upper NAND
checkpoint. Its 34-tick noisy trajectory passes an independent complete causal
window audit. This establishes a contextual starting point for the next repair
experiment; it does **not** yet establish a complete noisy nested macrostep or
receiving-layer recovery. The full project goal remains active.

## State provenance and boundary scope

The source is the complete depth-two checkpoint described in
[TIMED_DEPTH_TWO_REPAIR.md](TIMED_DEPTH_TWO_REPAIR.md). At physical time
2647030065837113344 its lower banks encode the actual upper state at
Age 1232619428, with a READ_B controller at upper position 9565. The new run
copies the complete 9916-word inherited banks for upper positions 9557–9573;
it does not replace scratch state with fresh initialization. The source bank
SHA256 is `606635add054317d1341f8b0c4e7b59cab382eb57d3f9c9a1d0b6a0c65567ccd`.

The existing physical GPU executor advances these 17 colonies to lower Age
1232619428. Every one of the 2310 gathered raw input words in each of lower
colonies 8 and 9 matches its complete radius-seven neighborhood in the actual
upper checkpoint. Full physical readback also matches the new bounded view.
The two controller layers happen to have the same age here; their clocks are
distinct. The burst starts at absolute physical time 2647030067069732772.

The 17-colony ring supplies the required parent neighborhoods for the center
and right neighbor. Its outer boundaries are periodic and are **not** asserted
equivalent to the whole Q-colony lower state. Any later composition must retain
this qualification and check the required boundary independence. In particular,
rogue heads outside the closed ROM interval may enter a neighboring colony;
the earlier single-colony periodic experiment cannot determine that behavior.

## Physical noise and checked result

Only lower colony 8 receives noise. The unchanged sampler uses expected count
8192, seed 2026092713, and 32 physical ticks, producing 8404 independent Poisson
marks. Each mark replaces the complete mutable G state; repeated coordinates
preserve the last sampled replacement. There is no rejection of inconvenient
fault patterns. Every tick executes the existing local physical transition
before its scheduled noise, followed by two quiet ticks. There is no Data or
flag rebasing and no host-installed simulated successor.

At the endpoint, local time 1232619462 / absolute time 2647030067069732806,
118 sites differ from the matching healthy trajectory in 189 raw F words.
There are five wrong primary Data words, two extra primary heads, and 99 Flag1
sites; Flag2 is zero. All exceptions are still in lower colony 8 at this time.
The extra heads occupy addresses 30992 and 30993, outside the ROM interval.
Their subsequent cross-colony behavior has not yet been executed here.

The auditor independently reproduces the exact noise sample and verifies source
hashes, complete inherited banks, the actual upper controller state and both
gathered input neighborhoods. It then evolves both healthy and noisy full raw
causal windows using native G, shrinking each edge by radius seven per tick.
The initial padding covers the entire possible fault support. Every retained
healthy output is compared with the saved GPU background; after each injection,
the entire exception support and all raw exception fields must agree.

This checks **2276300 complete native output states /350550200 raw words**, plus
596 full scalar-source output probes. The audit passes. It checks the actual
34-tick trajectory, not a theorem for arbitrary noisy states or a general
amplification result.

## Representation, cost and reproduction

`gacsca/fixed_rule/retimed_holder_live_window.py` adds a read-only bounded view
of a saved multi-colony state in the checked late, canonical, zero-flag domain.
It retains every raw controller field and all bank words. Procedure copies use
the actual global neighboring colony rather than wrapping within each colony.
It rejects inconsistent active Data and oversized reads. It performs no state
transitions. Four tests pass in 1.536 s, including full raw checkpoint equality
and a distinguishing cross-colony Data-copy test.

| Run | Elapsed computation | Peak sampled host RSS | Explicit GPU bound |
|---|---:|---:|---:|
| Four view tests | 1.536 s | 198992 KiB | None |
| Physical contextual burst | 24.871759 s | 338624 KiB | 57389816 bytes |
| Independent trajectory audit | 31.954896 s | 350880 KiB | None |

Watchdog wall limits are 30 s for tests and 180 s for each experiment/audit;
RSS limits are 512 MiB and 1 GiB respectively. All completed with return code
zero. These allocations remain far below the user's 40 GB host allowance.
The pending substantial GPU reservation was not used. No shared source,
historical data or other agent's running job was changed.

Exact commands, with output redirected to the corresponding private `.log`:

```sh
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_live_window_tests_v1_watch.json --seconds 30 --rss-mib 512 -- python -m unittest tests.fixed_rule.test_retimed_holder_live_window -v
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_contextual_burst_v1_watch.json --seconds 180 --rss-mib 1024 -- python -m experiments.fixed_rule.retimed_holder_contextual_burst --output figs/fixed_rule/retimed_holder_contextual_burst_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_contextual_burst_audit_v1_watch.json --seconds 180 --rss-mib 1024 -- python -m experiments.fixed_rule.audit_retimed_holder_contextual_burst --input figs/fixed_rule/retimed_holder_contextual_burst_v1.json --output figs/fixed_rule/retimed_holder_contextual_burst_audit_v1.json
```

Choose new artifact names for reruns. Complete background snapshots, noise,
and raw exception rows are preserved in the burst NPZ. Evidence index:
`figs/fixed_rule/retimed_holder_contextual_burst_evidence_v1.json`.

## Next distinguishing experiment and remaining gaps

Continue the exact saved state through quiet evolution, retaining flags and
heads that cross colony boundaries. A packed flag representation must first
demonstrate same-time equality of every raw field; it must not silently erase
extra heads or Data outside the usual workspace. Then carry the actual noisy
commit into subsequent lower periods and receiving-layer repair.

The frozen noiseless endpoint relation has explicit entry conditions. Arbitrary
damaged metadata, unused-space Data and rogue reset-time heads do not satisfy
those conditions automatically. They need physical continuation or a checked
extension of the relation. Inserting the earlier all-zero decoded symbol into
an unrelated upper fixture would not establish this nested trajectory.

The fixed rule, alphabet, radius, self-description and ROM are unchanged. Gray's
specialized hard-wiring and Gacs's suitably modified self-rule remain the source
basis; the known Flag2/SimBit fidelity questions remain open. Full noisy depth
two, general amplification, thresholds, practical Q/U optimization, robust caps
and depth three remain unproved. STATUS.md is the coordination handoff; please
use MAIN_AGENT_NOTES.md for replies.
