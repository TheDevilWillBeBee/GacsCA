# Completed word-rule macrostep experiment

This is a verified continuous-evaluator self-simulation link with printed Gray
maintenance. It is **not** a completed Gray hierarchy level: the source stage
schedule, redundancy and amplification are absent. [Architecture](WORD.md),
[next clocked construction and rejected voting composition](WORD_CLOCK_PLAN.md).

## Execution and audit

Commands:

```
python -m experiments.fixed_rule.word_selfsim --output figs/fixed_rule/word_selfsim_v1 --steps 2 --chunk-ticks 1000000
python -m experiments.fixed_rule.audit_word --input figs/fixed_rule/word_selfsim_v1 --output figs/fixed_rule/word_audit_v1.json
```

The CPU experiment and independent audit completed successfully. Sources were
captured as exact bytes before execution; all **81** archived and live source
hashes agree. ROM and compiled-binary identities agree. The audit compares scalar
F, compiled native F, word-description F and the intended projection/regeneration
relation at both macrosteps. It checks the final physical-core decode and boundary
and absence of pending padding packets.

| Measurement | Result |
|---|---:|
| Simulated cells (nonaliased radius-five ring) | 23 |
| Successive macrosteps | 2 |
| Physical cells represented | 192,937,984 |
| Explicit computation-core cells | 101,913 |
| Core array bytes (not total memory) | 19,567,296 |
| Total represented physical ticks | 134,736,236 |
| Literal core ticks | 57,662,096 |
| Exact WAIT/quiet skips | 77,074,140 |
| Local transition evaluations | 2,841,529,618 |
| Experiment wall seconds | 519.7794570475817 |
| Projected/lifted mismatches | 0 / 0 |
| Post-initial projected raw words / represented bits | 1,104 / 26,910 |
| Post-initial lifted raw words / represented bits | 1,426 / 36,018 |

These are physical ticks of an exact restricted-domain representation, not an
all-literal dense trajectory. Padding packets are represented by speed-one
world-lines. Uniform actual Age is materialized from a proved increment invariant.
No host upper transition or descriptor evaluator installs simulated outputs.

## Distinguishing dynamic results

The central simulated cell begins at wrong Address 143 and Age 123 amid locally
canonical neighbors. Its first simulated transition repairs Address to 111 and
Age to 0, then Age becomes 1. All raw controller fields match throughout. Its
READ_B phase computes NAND of two all-one words, moves the WRITE controller to
the adjacent cell, and the next simulated transition changes that cell's data
from `0xFEDCBA9876543210` to zero. No reinitialization occurs between macrosteps.

Seven raw output records differ from F's untouched program fields because their
computed Address changed. Local META reconstructs each from the new Address;
strict decoding and lifted-state comparison would fail if regeneration were
omitted or used the old Address. The central printed Flag2 stays one across both
steps. This is a retained source counterexample, not complete-state recovery.

The short upper ring is not a globally canonical Q-cell colony; its seam has
structural effects. The entire ring is compared against G, and the central repair
and write lie outside the seam's two-step radius-five causal influence. The
physical lower colonies themselves satisfy the accelerator's healthy-structure
invariant. Arbitrary physical damage remains outside this accelerator's domain.

## Tests and supplemental evidence

Separate targeted unittest runs (no new whole-repository suite claim):

| Pattern under `tests/fixed_rule` | Tests passed | Seconds | Log in `figs/fixed_rule` |
|---|---:|---:|---|
| `test_word_rule.py` | 5 | 1.296 | `word_rule_tests_v1.log` |
| `test_word_world.py` | 6 | 0.311 | `word_world_tests_v1.log` |
| `test_word_initial.py` | 3 | 0.186 | `word_initial_tests_v1.log` |
| `test_word_contract.py` | 3 | 0.102 | `word_contract_tests_v1.log` |
| `test_word_temporal_capacity.py` | 2 | 0.024 | `word_temporal_capacity_tests_v1.log` |

Each used `python -m unittest discover -s tests/fixed_rule -p PATTERN -v`.
The contract test was added after the macrostep source capture; its separate
source/log provenance is `word_contract_provenance_v1.json`. The capacity model
was also added later and has its own manifests; it is not a running dependency.
Its v1 source archive preserves an incorrect explanatory gate-count comment;
v2 fixes only that comment. Both executed six NANDs and report 93,977,870 ticks,
which exceeds the 8Q update window. The counterexample is for the specified
serial-voting composition, not an impossibility result for local voting.

Exact description and ROM/program data are exported in
`word_description_v1.json` and `word_program_v1.json`. Lazy depths 1–3 retain the
same alphabet and identities, but **no depth-two/three dynamics were run**.
At depth two, one top cell requires Q^2=70,368,744,177,664 physical cells and
T^2=4,538,463,322,861,924 ticks per top transition under this construction.
Even explicit lowest-level cores would contain 37,169,922,048 cells.

## Identities and preservation

- Full descriptor SHA-256: `43aa649dcea0e6b8c1fc2c5065b854e92c950d4c935549d5062b8f131ac62ffb`.
- ROM SHA-256: `7e179505523acec223aac9dba89703ea05c80a927c9f72afcab0fd6dfcf1fb8b`.
- Binary SHA-256: `7c89fdb40846633d9e101e20aa768062f7db6fc643c5f65b6e5679b5fe813c94`.
- Artifact SHA-256: `ece271bf6638af3ce1cf37c2058be0fd7ee4636aeaf102f58d2fb78897c8c2aa`.
- Source archive SHA-256: `bda63f6cff405541a3b4c7c5f3869559215e01c0f43e4c208e7d4339dd5671a0`.

The older projected, regenerated and window experiment manifests still match
all 33, 46 and 63 corresponding live source files respectively. No existing
shared module, test, report, experiment or dataset was modified. No GPU work.
