# Retimed fixed candidate: U = 2^31

Subsequent result: [RETIMED_NOISELESS_MACROSTEP.md](RETIMED_NOISELESS_MACROSTEP.md)
closes the whole-period descriptor-semantics induction left pending in this
initial milestone. Its execution and noise limitations remain separate.

2026-09-26. The retimed_holder candidate implements a globally fixed period
U=2147483648, half the reference candidate's 4294967296. Its scalar transition,
complete word description and native CPU transition use that same wrap. The
physical alphabet remains 154 words /4090 bits, including a 32-bit Age field;
projection remains 105 words /2704 bits, radius seven and Q=32768. No parameter,
ROM, field count or transition selection depends on initializer depth.

This is a separate candidate. The original small_holder rule, ROM, proof,
executors and datasets remain unchanged. The intermediate identity_holder
candidate also remains available. The retimed candidate's full period theorem
has **not yet been composed**, and no complete new-ROM physical period or
complete depth-two upper period has been executed. The results below establish
specific local identities, physical paths and conditional timed Data flow.

## Source basis and self-reference

The construction follows Gray pp. 31–32: eliminate ProgramBit by hard-wiring a
specialized self-simulator. Gacs sections 9.2–9.3 allow simulation of an identical
or suitably modified self-correcting rule. See the supplied
[Gray extract](../../papers_txt/gray_readers_guide.txt),
[Gacs extract](../../papers_txt/gacs_2001.txt) and the reference proof in
[NOISELESS_MACROSTEP.md](NOISELESS_MACROSTEP.md). This does not establish every
correction/amplification hypothesis in either paper.

The colonies execute the complete retimed physical descriptor, including its
own controller and the new clock wrap, then regenerate metadata using their own
new ROM. Symbolic comparison checks every one of the 154 raw outputs. This is
not closure by an opcode inventory, initializer or simulated payload alone.
The optimized program is equivalent on typed raw inputs, including active
controllers and damaged geometry. Oversized 64-bit Info contents outside a
represented field's width still need a legalization/repair argument.

## Actual parameters and costs

| Quantity | Reference | Retimed candidate |
|---|---:|---:|
| Q | 32768 | 32768 |
| U | 4294967296 | 2147483648 |
| Stored instructions | 20801 | 17809 |
| Core cells | 30724 | 27721 |
| Controller-path ticks | 2802642834 | 2001129064 |

The changed wrap adds one instruction compared with the intermediate optimized
ROM. The new core still requires Q=32768 in the present power-of-two layout.
No padding was introduced to enforce U<=128Q; that inequality is not a project
requirement. U^2 remains 2^62 physical ticks for a literal depth-two macrostep.
Halving U is useful but does not make that execution practical by itself.

```
RESET_AGES = (0, 150000000, 290000000, 1230000000, 1232000000)
ACTIVE_ENDS = (149000000, 288000000, 1228000000, 1231000000, 2025000000)
VOTE_AGES = (430000000, 1232000000)
CAPTURE_AGE = 1224000000
WF_START = 1230000000
WF_END = 1230065536
```

Age retains all 32 raw bits. Canonical legal trajectories wrap modulo 2^31;
high-Age physical states are still described. Native/scalar tests cover Age
U-2, U-1, U and 2U-1. Commit is triggered by old Age U-1, not every high-bit alias.

## Completed checks and their limits

* Complete optimized-expression equality and symbolic ROM execution include
  all raw controller outputs, three histories, both evaluations, own-ROM
  regeneration, Signal buffers and commit. All fixed metadata values fit their
  declared widths.
* The canonical clock comparison covers all 2^31 legal ages in 22 intervals.
  For each interval, all 153 non-Age raw outputs equal the reference rule at a
  matching clock signature, with every other raw field arbitrary. The new Age
  output is checked separately modulo 2^31. This transfers local rule identities;
  it does not transfer old numerical ROM paths or prove a whole period alone.
* Actual new-ROM guards, controller effects and durations pass for 17712
  ordinary paths, 392 metadata cases and 17810 dispatch paths. Proof constructors
  are explicitly bound to the new ROM and clock without modifying old module
  globals. These are diagnostics, not an evolving interpreter or depth dispatch.
* The six-phase schedule checks 28542 instruction occurrences and all 6478 SEND
  sites. It excludes packet overwrites and controller accesses at/after delivery.
* Timed symbolic execution checks 748575 reads, 328650 writes and 97170 packet
  deliveries against batch interpretation, including all 154 committed raw
  outputs. All 5880 metadata lookup checks remain within 15-bit query bounds.
* The open-lattice check uses independent integer source offsets -7..7, with
  45 source-access disjointness checks. It does not use wrapped destinations to
  establish central histories or the complete output identity.
* The new-clock Signal/flag formulas and clearing bound pass directly. The
  packet/Signal join checks equal five-buffer sources and capture timing.
  Last packet delivery is at Age 1220580247, before capture's old Age 1223999999.
  Both flags clear by Age 1230098304, before final evaluation at 1232000000.

All six phase margins are positive:

| Phase | Head stopped at Age | Last packet arrival | Checked margin |
|---|---:|---:|---:|
| Gather 0 | 147155420 | 147373066 | 1626934 |
| Gather 1 | 286679194 | 286894530 | 1105470 |
| Gather 2 | 426681506 | 426894531 | 3105469 |
| Third evaluation | 1220575199 | 1220580247 | 3419752 |
| Precommit halt | 1230016977 | none | 983023 |
| Final evaluation | 2022020768 | none | 2979232 |

Ten literal/compiler tests pass in 9.763 s, including native compilation. They
compare scalar/descriptor/native outputs during active FETCH, ALU, SEND and all
META selectors; reject the old wrap and an omitted raw controller output; check
fixed identity and controller encoding at depths 1–3; and execute literal
commit/wrap/reset causal cones. Depth checks are initialization checks, not
complete nested trajectories.

Seven additional tests pass in 2.644 s. They reject an old path catalog, changed
instruction duration, aliased MEM index, same-track packet collision, late
controller access, changed dispatch target and oversized metadata query. They
also check that new proof bindings leave the reference modules unchanged.

The first metadata-query diagnostic failed on the new symbolic vocabulary
(`variable` versus the older `input` node). Its log and exact failed source are
preserved. The corrected diagnostic uses the existing independent structural
width bound; it neither masks queries nor changes any transition. Version 2
reproduces the timed result and passes all query bounds.

## Reproduction and evidence

All commands ran from the repository root, preceded by `ulimit -v 524288`, with
`OPENBLAS_NUM_THREADS=1` in the environment. No GPU run or CUDA rebuild occurred.
The largest reported certificate RSS was 195808 KiB (about 191 MiB).

```
python -m experiments.fixed_rule.certify_retimed_holder_rom --output figs/fixed_rule/retimed_holder_rom_v1.json
python -m experiments.fixed_rule.certify_retimed_holder_clock_transfer --output figs/fixed_rule/retimed_holder_clock_transfer_v1.json
python -m experiments.fixed_rule.certify_retimed_holder_paths --clock-transfer figs/fixed_rule/retimed_holder_clock_transfer_v1.json --output figs/fixed_rule/retimed_holder_paths_v1.json
python -m experiments.fixed_rule.certify_retimed_holder_mail_schedule --output figs/fixed_rule/retimed_holder_mail_schedule_v1.json
python -m experiments.fixed_rule.certify_retimed_holder_timed_dataflow --schedule figs/fixed_rule/retimed_holder_mail_schedule_v1.json --output figs/fixed_rule/retimed_holder_timed_dataflow_v1.json
python -m experiments.fixed_rule.certify_retimed_holder_open_dataflow --schedule figs/fixed_rule/retimed_holder_mail_schedule_v1.json --output figs/fixed_rule/retimed_holder_open_dataflow_v1.json
python -m experiments.fixed_rule.certify_retimed_holder_meta_query_bounds --schedule figs/fixed_rule/retimed_holder_mail_schedule_v1.json --timed figs/fixed_rule/retimed_holder_timed_dataflow_v1.json --output figs/fixed_rule/retimed_holder_meta_query_bounds_v2.json
python -m experiments.fixed_rule.certify_retimed_holder_signal_flag_boundaries --output figs/fixed_rule/retimed_holder_signal_flag_boundaries_v1.json
python -m experiments.fixed_rule.join_retimed_holder_signal_schedule --schedule figs/fixed_rule/retimed_holder_mail_schedule_v1.json --boundary figs/fixed_rule/retimed_holder_signal_flag_boundaries_v1.json --output figs/fixed_rule/retimed_holder_signal_schedule_v1.json
python -m unittest discover -s tests/fixed_rule -p test_retimed_holder.py -v
python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_composition.py -v
```

Each command's stdout/stderr is saved in the correspondingly named log. The
query v1 failed command used the same arguments with a v1 output name. Successful
output files refuse overwrite. Use new versioned filenames for any reruns.

| Certificate | Seconds | Peak RSS, KiB |
|---|---:|---:|
| Complete ROM | 4.928047 | 89768 |
| All-clock transfer | 2.230900 | 59700 |
| Physical paths | 43.948842 | 92200 |
| Packet schedule | 1.968997 | 100600 |
| Timed Data flow | 8.107246 | 195808 |
| Open lattice | 2.649508 | 102352 |
| Query bounds v2 | 6.603346 | 179664 |
| Signal/flag boundaries | 0.552006 | 56996 |
| Signal schedule join | 2.012729 | 102712 |

[Evidence index](../../figs/fixed_rule/retimed_holder_evidence_index_v1.json)
records all nine passing manifests and two passing test logs with SHA-256 hashes;
all recorded source/input hashes were checked after the runs. Rule identities:

```
physical descriptor 6e2f29f61bf281ec5d346cd58e717cf7e5b0afea263d2c17a18a58de295d8d23
compiled descriptor 0870fc731d82bfb307275ad08b53068ae3e9a2141528e0727cb51a90ea66cda4
ROM                 4dc026b976c541001421dd214df9c9e33f6f851053d4ba5f53dbbec925ba5645
```

## Remaining work

Compose the retimed whole-period induction explicitly: transfer the canonical
structure, arbitrary-context, raw-mail and quiet-barrier lemmas through the
all-clock identity; recheck their new layout/phase interfaces and output typing;
then close the new Age-zero encoding relation across successive periods. A green
path/Data-flow catalog is not a substitute for that composition.

The reference period theorem is retained, but neither its complete executions
nor its backend certificates automatically cover the new ROM/wrap. Retimed
physical execution and backend equivalence need their own validation. Practical
complete depth-two execution still needs further evaluator/layout improvement
or justified acceleration. General cross-level correction, noisy amplification,
malformed-encoding repair and a reliably repaired finite cap remain open.
Candidate-B Flag2 and voted-old-Signal D10 remain explicit source choices; the
printed Flag2/SimBit issues have not been resolved by this optimization.
