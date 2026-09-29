# Wider physical repair: the complete audit chain now passes

2026-09-27. The remaining independent quiet-recovery audit has passed. The
73-colony experiment now has checked evidence from the actual lower physical
burst, through cross-colony head transport and a faulty decoded commit, to
subsequent repair of the decoded upper controller and refresh of lower histories.

The central 17 decoded cells agree in every raw field with the complete upper
colony's corresponding trajectory. This resolves the earlier narrow-window
contamination of that comparison. It does **not** prove that the full lower-Q
physical ring has the same noisy evolution; that boundary relation remains open.
Three inert nonMEM words persist. No physical-erasure, amplification or stochastic
threshold claim follows. The full project goal remains active.

## What the final audit adds

`retimed_holder_wide_recovery_audit_v2.json` independently replays **all 16384
quiet physical ticks** in all 73 colonies. It checks 7241728 scalar procedure
candidates and all complete saved observations and the final state. In this
trajectory the complete-input memoization finds no duplicate scalar neighborhoods;
the unique-evaluation count is also 7241728.

The first two ticks execute complete native outputs everywhere in both actual
and healthy rings. Further complete native windows cover the actual boundary
crossing. Altogether these checks cover **9569792 native output states /
1473747968 raw words**. The audit confirms:

- The first extra primary head enters receiving colony 37 at quiet tick **1775**.
- Flag1 first becomes globally zero at quiet tick **15453**; Flag2 stays zero.
- Every saved complete raw observation and final state agrees with the physical run.
- All replayed mail outputs remain zero.

The audit takes **1168.662948 s**, with 6786380 KiB process peak RSS and 6788500
KiB sampled RSS. Its watchdog terminates normally with return code zero, under
1800 s /12 GiB limits. The earlier 900-second timeout remains preserved as an
incomplete run; it is not relabeled a pass. No observation timeout triggered a
restart: the version-1 watchdog had authoritatively killed that process first.

## Combined result

The completed trajectory uses one unchanged physical rule, alphabet, ROM and
neighborhood. The actual wider state is retained between every stage.

| Stage | Result | Execution or audit time |
|---|---|---:|
| Physical quiet recovery | Flags clear; controller/Data defects remain in colonies 36/37 | 176.831657 s |
| Noisy commit/reset | Only colony 37 commits an all-zero record; 12 mutable upper fields wrong | 252.522558 s |
| Independent commit audit | Every event interval, six complete states, complete clock outputs pass | 874.295199 s |
| Three subsequent physical lower periods | Upper error gone after two; histories refreshed after three | 106.504515 s |
| Independent subsequent endpoint audit | 1473511424 complete raw words checked | 144.734491 s |
| Literal reset-entry check | 368377856 raw words match the valid-entry reset image | 39.510738 s |
| Full-upper alignment/history comparison | Central 17 raw states agree; bank differences 660 then zero | 3.453203 s |

The third-period complete bank and Signals equal the matching unfaulted terminal
reference. The three retained Data words in lower colony 36 at addresses
30960–30962 remain explicitly stored. Their quiet inertness uses the existing
descriptor certificate and its geometry/ROM hypotheses; fresh faults that break
those hypotheses cannot be silently skipped.

The final phase uses conditional endpoint identities rather than literal replay
of billions of ticks. Physical normalization is independently replayed, its
comparison state has a literal valid reset preimage, and every complete endpoint
is compared against the identity. No formula-generated reference is installed
into the actual evolving world. The detailed domains, storage fix, failed test
fixture and exact per-stage commands remain preserved in
[the interim report](WIDE_REPAIR_PENDING_RECOVERY_AUDIT.md).

All owned runs are now terminal. GPU working sets remain below 64 MiB; system
RAM remained below the user ceiling. No shared source, CUDA artifact, historical
dataset or other agent's job was modified. The substantial GPU reservation
remains unused.

## Next boundary obligation

[COLONY_CUT.md](COLONY_CUT.md) supplies a new conditional one-step separation
certificate for the complete physical descriptor. It accounts for replica
ownership and all controller fields. It is not yet an all-time boundary proof.

To connect this experiment to the complete lower-Q ring, establish matching
initial physical collars around an enclosing region, verify the cut hypotheses
through the affected interval, and justify the noiseless prefix outside it.
The initial correct upper input halo alone does not prove those facts. Do not
replace that work with injecting the measured decoded error into a fresh full
upper fixture; that comparison is already available and is a different claim.

Final evidence index:
`figs/fixed_rule/retimed_holder_wide_repair_evidence_v1.json`.
The interim report/index stay frozen to preserve the actual verification history.
General amplification, thresholds, robust finite caps, Q/U optimization, depth
three and the existing Flag2/SimBit source-fidelity questions remain open.
