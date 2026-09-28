# Completed clocked macrosteps and audit

The fixed clock-rule candidate completed **two successive 128Q periods** with
all raw output fields correct. The complete stage controller is described and
executed locally. This is one clocked simulation link, **not** the complete Gray
construction: signal/trickle initiation and spatial redundancy remain missing.
See [CLOCK.md](CLOCK.md) for the rule and acceleration domain.

## Reproducible commands

```
python -m experiments.fixed_rule.clock_selfsim --output figs/fixed_rule/clock_selfsim_v1 --steps 2
python -m experiments.fixed_rule.audit_clock --input figs/fixed_rule/clock_selfsim_v1 --output figs/fixed_rule/clock_audit_v1.json
```

Both completed successfully. The audit checks all **95** captured source members
against their archive and live bytes, the compiled binary and immutable ROM,
complete scalar/native/word-description agreement, all saved projected/lifted
macro-boundary records, both saved Hold evaluations per period, final physical
core decode and boundary, and empty padding mail.

The archived runtime checks all three history arrays and vote arrays against
complete expected raw neighborhoods; it also checks hashes of the simulation
state at both ends of each rest and unchanged Info before commit. The audit
verifies these recorded checks and their expected number. Raw history arrays and
intermediate rest arrays were not saved separately, so those parts are runtime
assertions plus source provenance, **not independent replay from saved arrays**.
The complete local-rest rule and bulk-boundary tests separately support the
invariant between the checked endpoints.

## Measurements

| Quantity | Result |
|---|---:|
| Simulated cells | 23 |
| Physical sites represented | 192,937,984 |
| Explicit computation-core sites | 172,040 |
| Core array bytes (not total process memory) | 33,031,680 |
| Total represented physical ticks | 2,147,483,648 |
| Literal core ticks | 41,126,468 |
| Exact quiet/rest/WAIT skips | 1,880,855,724 |
| Exact guarded head-scan skips | 225,501,456 |
| Local transition evaluations | 2,082,885,888 |
| Run wall seconds | 504.2708601048216 |
| Projected/lifted mismatches | 0 / 0 |
| Post-initial projected bits / lifted bits checked | 26,910 / 36,018 |

This is an exact restricted-domain representation, not an all-literal dense
trajectory. Test processes also ran during this CPU experiment; wall time is a
record of this run, not an isolated throughput benchmark. No GPU was used.

Each period has 14 probes: all three gathers, two local votes, two independent
Hold evaluations, five rests and commit. Info remains unchanged until the last
transition into Age 0. All controllers and mail are quiescent at the final
boundary; the next period begins through the same local reset with no host refill.

The represented configuration exercises several non-vacuous branches. A simulated
stage-five vote changes data 99 to 7 using three unequal words 3,5,6. A simulated
period-boundary commit changes data 123 to `0x1122334455667788`. A damaged Address
143 repairs to 111 and Age 321 repairs to 2, then advances to 3. A READ_B controller
moves a pending NAND result and completes its write in the second period, changing
`0xFEDCBA9876543210` to zero. Nine raw output records require program reconstruction
after Address changes. Their new program fields match exactly. Printed Flag2
persists as expected, so the repair result is not full-state recovery.

The upper 23-site ring is deliberately short and is not a whole canonical
Q-site upper colony. Its seam effects and all damaged raw states are included
in the full comparison against G. No deeper hierarchy dynamics were executed.

## Targeted tests

Each command used `python -m unittest discover -s tests/fixed_rule -p PATTERN -v`.
These are separate focused runs, not a whole-repository regression claim.

| PATTERN | Passed | Seconds | Log in `figs/fixed_rule` |
|---|---:|---:|---|
| `test_clock_rule.py` | 6 | 1.209 | `clock_rule_tests_v1.log` |
| `test_clock_world.py` | 6 | 48.197 | `clock_world_tests_v1.log` |
| `test_clock_temporal.py` | 1 | 0.815 | `clock_temporal_tests_v1.log` |
| `test_clock_initial.py` | 4 | 0.382 | `clock_initial_tests_v1.log` |
| `test_clock_closure.py` | 3 | 0.206 | `clock_closure_tests_v1.log` |
| `test_clock_timing.py` | 2 | 3.965 | `clock_timing_tests_v1.log` |

The temporal test physically executes stage five and commit from three initialized
histories. Each single corrupted history yields the clean complete output; two
corrupted histories yield the different expected complete output. This is a
protocol fixture, not an iid or spatially localized noise experiment. The separate
full-period run executes the actual gathers.

The timing test brackets first-gather head halt at tick 5,584,343 and its final
packet arrival at tick 47,523,250 by checks one tick before and at each event.
It similarly brackets evaluation halt at tick 49,749,480, using a represented
Address in padding so all seven META fallbacks are exercised before commit.

Other tests cover all controller phases/directions against literal physical
execution, duplicate-head scan rejection, full-native bulk boundaries, every raw
encoded field, complete descriptor embedding and metadata regeneration, radius-five
exterior locality, and physical stage execution with Python evaluator/transition
callbacks disabled. Fixed alphabet/ROM/rule identity is checked through three
initialization depths. A negative witness disproves the old quiet terminal orbit;
the new flagged same-rule cap is explicitly scoped in CLOCK.md.

The last four test modules and `clock_initial.py` were added after the full run
captured its source list. Their source/log hashes are recorded separately in
`clock_supplemental_sources_v2.json`; no running dependency was changed.

## Identities and preservation

- Complete description: `6bee308cd32c9637d6598034932ed2ee956f60f0e4045ef0a1726f9ed0697ee2`.
- ROM: `7e2f5ef0e1ed995f128defad316f8e4c868d6b2c6812f2ab0cad236a3af3a81a`.
- Binary: `cfed8e2cef9ca6731368aac7dd2d3c74bbf1cb50a13a7681cf0ae9ce18ebe708`.
- Artifact: `07cdf8536e150da40f62de2f1add9ce9c6e4ecf77c2cee0e99615aef04e6c4e8`.
- Source archive: `0b893b3a0ea5a7b6efcf3607714b7df79598f9afe65610b1bb95964f145f3573`.

The older projected/regenerated/window/word manifests still match all 33/46/63/81
live sources respectively; the new clock manifest matches all 95. No shared
module, test, report, experiment, dataset or CUDA dependency was modified.
