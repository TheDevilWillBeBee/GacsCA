# Early encoded-program repair, with successive dynamics

Gray pp.31–32 describes overwriting the simulated ProgramBit near the beginning
of a work period, using the simulated Address. The preceding clock candidate
only reconstructed the output program after evaluation. This revision adds the
early operation while retaining output reconstruction, which is necessary for
our stronger raw-record relation when the simulated Address changes.

A fixed fourteen-instruction LOAD/META prefix repairs all seven encoded program
words before the first gather. It reads the **current input Address**. After
computing the complete transition, the existing reconstruction reads the **new
output Address**. These are distinct operations: an input Address 143 may be
repaired by the simulated rule to 111, and both raw program records must be
correct at their respective stages.

The complete raw transition F is unchanged: 783 bits, 31 words, radius five,
2,484 operations, including LOAD/META's own controller, clocks and maintenance.
Its hard-wired program P changes once, so projected G changes once for this
construction revision. There is no per-depth selection. The physical alphabet
remains 585 bits / 24 storage words; Q=8,388,608 and U=128Q remain fixed.
The new P has 3,574 instructions, 3,919 memory cells and a 7,494-cell core.

The new local prefix finishes at physical tick **316,152**, before any gathered
record is sent. First-gather final arrival is 47,848,442; third-gather final
arrival is 47,533,697, leaving 19,575,167 ticks before its vote. Evaluation,
Hold reconstruction and halt take **49,842,594 < 8Q=67,108,864** ticks.
`early_program_v1.json` records the exact program and timing certificate.

## Distinguishing tests

All seven raw program fields are corrupted within their finite alphabets.
Strict decoding initially fails. The physical prefix restores them, preserves
every dynamic/controller field, and is bracketed one tick before and at its
predicted completion. Queries cover boot, instruction, final core and padding
addresses. The old clock ROM fails to repair the same corruption.

A separate test compares the entire physical core state with an independently
executed clean initialization after the prefix: they agree exactly, with no
pending mail and identical canonical padding. This is complete convergence for
this **program-only initial corruption class**, not recovery from arbitrary
physical faults. The initializer also follows all 31 raw words through actual
nested Info/Data paths at depths 1–3, including controller values. This improves
on checks restricted to boot or padding sites. It remains initialization evidence,
not deeper dynamics.

## Completed experiment and independent audit

```
python -m experiments.fixed_rule.early_selfsim --output figs/fixed_rule/early_selfsim_v1 --steps 2
python -m experiments.fixed_rule.audit_early --input figs/fixed_rule/early_selfsim_v1 --output figs/fixed_rule/early_audit_v1.json
```

Both passed. The physical initialization has **161 corrupted encoded program
words** (all seven in each of 23 represented cells). Their dynamic records are
unchanged; the saved initial lifted records are explicitly inconsistent with P,
not presented as a valid clean codeword. Early repair restores them before
retrieval. There is no host refill or host upper transition replacement.

Two successive complete 128Q periods pass with zero projected/lifted mismatches.
The simulated state executes temporal voting, commit, Address/Age repair and a
NAND write completing in the second period. Nine output records require program
reconstruction. Printed Flag2 still persists; it is not described as recovery.

| Measurement | Result |
|---|---:|
| Represented physical ticks | 2,147,483,648 |
| Literal core ticks | 41,205,043 |
| Exact quiet skips | 1,879,725,896 |
| Exact guarded physical head-scan skips | 226,552,709 |
| Local evaluations | 2,086,802,374 |
| Wall seconds | 521.0846257265657 |
| Physical sites represented | 192,937,984 |
| Explicit core sites | 172,362 |
| Core-array bytes (not total process memory) | 33,093,504 |

The independent audit checks **107** archived/live source hashes, ROM and binary
identity, early repair snapshots, all saved history and vote words, both Hold
evaluations per period, all complete macro-boundary states and final physical
boundary. Unlike the earlier clock artifact, this experiment saves the raw core
arrays at both ends of all ten rest intervals in `early_selfsim_v1.rests.npz`.
The auditor checks actual Age at each endpoint and compares every other field
independently. These are endpoint checks plus the tested local rest invariant,
not a dense saved trace of every tick. The physical executor still has the
canonical-Address/uniform-Age/**zero-flag** domain restriction described in CLOCK.md.
Concurrent small CPU checks ran during the experiment; its timing is not an
isolated throughput benchmark.

Identities:

- F description: `6bee308cd32c9637d6598034932ed2ee956f60f0e4045ef0a1726f9ed0697ee2`.
- ROM: `67f6d2233a93b4e2636f1c82763a6909a8a628e6e081f45f8ff838f53a8db2a7`.
- Binary: `d8b08d32e7916760bdaca93f281f6e4a0ab6ea49c60e25cf88ad0b2a6329574f`.
- Main artifact: `d2df0a0396fa84b283e83274cc9a6bfd378bf901a4904780a790a3f5cf5aff9e`.
- Rest artifact: `b4b6722b172a71ca7c44b9cfb99f57704c8d7528508466d1a0b39fa780b3489d`.
- Source archive: `38754ad15d630884cc45fb5ac30e03130f71d1041477c82ab5eafac81260cc52`.

## Remaining scope

One clocked self-simulation link with early program repair is verified. No full
Gray hierarchy level, deeper dynamic run or noise-robustness theorem is claimed.
Computed-Address flag signals, Wf initiation/trickle-down, fivefold redundancy of
all simulation state and operations, general physical-fault execution, and deeper
dynamics remain missing. The flagged terminal cap is unchanged and is not an
organized robustness boundary for a future trickle rule. D8 and D10 remain open.
[CANONICAL_FLAGS.md](CANONICAL_FLAGS.md) records new prerequisites for executing
physical flag waves without silently retaining the zero-flag assumption.
