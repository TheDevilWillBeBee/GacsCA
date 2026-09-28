# Address repair and hard-wired self-reference closure

2026-09-26. Two successive physical work periods now have explicit checkpoints
before and after metadata regeneration, with an upper Address fault repaired
from 30000 to 107. Separately, the actual fixed-ROM regeneration subroutine passed
for every one of the 32768 possible encoded Addresses, all seven offsets and all
seven selectors. No rule, alphabet, ROM, clock or existing backend was changed.
These results strengthen one-link closure; they do not execute a nested upper
work period or establish the full noisy simulation relation.

## Source interpretation and the actual mechanism

Gray pp.31–32 (supplied extract lines 1413–1450) reconstructs a represented
ProgramBit by reading the colony's own program at the represented Address,
then projects ProgramBit out of physical state. He explicitly specializes the
resulting self-simulator. Gács §9.2 (extract lines 3866–3878) permits simulation
of an identical or suitably modified self-correcting rule. The construction need
not implement an arbitrary user-programming platform. These source statements
motivate the mechanism; they do not prove the executable implementation.

The current `small_holder_program.layout()` already has both required operations:
`regenerate(info)` at the start of retrieval and `regenerate(hold)` after the
complete raw descriptor evaluation/output copies. Each obtains the represented
Address from encoded Data, forms its seven wrapped offsets using actual word
instructions, and uses LOAD/META heads to read the same local physical ROM. A
query outside the computation core follows the fixed fallback. The complete raw
rule F describes those LOAD/META/controller transitions as well as maintenance,
mail and computation. P is the one fixed program containing F's description and
these regeneration operations; it is independent of depth.

Let iota restore the 49 metadata words from P at a cell's Address, and let pi drop
those words. The physical projected rule is G = pi F iota on radius seven. It is
incorrect to assert `F iota = iota G` for this Address-changing rule: F preserves
old raw metadata when maintenance changes Address. The correct block construction
uses the *executed* regeneration phase:

1. Input metadata is normalized locally, so the retrieved raw neighborhood is
   iota(x), including all raw controller fields.
2. The physical program evaluates the full F description into Hold, producing
   y = F(iota(x)). This output can have stale metadata after Address repair.
3. Actual LOAD/META computation replaces only Hold metadata, producing iota(pi(y)).
4. Commit transfers all 154 words into Info. The projected decoder returns
   pi(y) = G(x), with a consistent complete lifted representation for the next
   work period.

This explains the self-reference construction without placing a literal copy of
the entire hard-wired ROM lookup into F's word description. The evaluator itself
is described, and its program reads its own physical ROM. It also explains why
an opcode inventory, initialization alone, or projecting away inconsistent
metadata at diagnostic decode would not establish closure.

The four steps are a conditional construction argument. They still require the
physical retrieval, computation, timing, suffix and next-boundary obligations.
Experiments below provide stronger finite evidence for steps 2–4 and exhaustive
clean-subroutine coverage of the finite query domain. They do not prove all
admissible macrosteps or all noisy histories. Candidate-B Flag2 and the old-Signal
D10 interpretation remain explicit modifications.

## Address-fault physical trajectory

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_geometry_closure --output figs/fixed_rule/small_holder_geometry_closure_v1
```

The 15-cell active-WRITE fixture has projected upper holder 7's Address changed
from 107 to 30000. Its initial metadata is the correct fixed ROM metadata for
that faulty Address; no inconsistent raw metadata is hidden at initialization.
The same lower resident world then runs for 2U=8589934592 physical ticks on
491520 sites, without reinjection or reinitialization.

Each period records Hold just after all descriptor outputs have been copied,
before the first metadata query can write, then again after regeneration, and
finally records the complete decoded commit. The first checkpoint is at period
offset 1894535625, based on the actual fixed instruction schedule; the regeneration
entry is instruction 20661. All 154 fields match the independently computed raw F
output at that checkpoint. After regeneration and commit they match iota(G(x)).

| Period | Metadata words actually changed | Center Address | Center primary Data |
|---|---:|---:|---:|
| 1 | 77 | 107 | 0 after maintenance clearing |
| 2 | 42 | 107 | 0x123456789ABCDEF0 restored from surviving copies |

The changes also include the fixture's upper ring-boundary Address adjustments.
Earlier clean fixtures already exercised some of those adjustments (42 metadata
changes); regeneration was present, not a newly added missing mechanism. The
new experiment explicitly separates raw evaluation from regeneration and adds
an interior geometry fault. Omitting regeneration would fail the observed raw
metadata comparisons and strict decoder consistency check.

GPU advance 36.445883 s; total 37.987277 s; host max RSS 176324 KiB; resident
buffers 5116680 bytes plus existing bounded staging. Both periods completed with
all checkpoints matching. Host `Program.evaluate` and raw/projected/native local
rule calls are forbidden during physical advance. Diagnostic expected values are
never installed into the evolving world.

## Exhaustive clean regeneration domain

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_regeneration_domain --output figs/fixed_rule/small_holder_regeneration_domain_v1
```

For each possible Hold.Address, a canonical lower colony starts at the actual
regeneration entry of the unchanged physical ROM. Its 49 Hold metadata words are
poisoned with `0xD3AD123456789ABC`. Its head, phase, pc and encoded Address are
ordinary initial-state fields. The same physical local controller executes the
complete regeneration sequence and halts through its real IF_THIRD instruction.
No host metadata write occurs during evolution.

All 32768 Addresses are processed in 256 batches of 128 colonies. Each batch
executes 11644385 physical ticks. Every Hold word is checked, including unchanged
dynamic fields; the completed head/controller state is also checked at the exit.
The query coverage includes all seven signed/wrapped offsets, all selectors,
MEM/instruction/end records, the gap fallback and the five tail records.

| Measurement | Result |
|---|---:|
| Checked metadata words | 1605632 |
| Checked complete Hold words | 5046272 |
| Actual colony literal events | 23492755 |
| Local logical evaluations | 58091912 |
| GPU advance time | 20.187524 s |
| Total including initialization/readback | 111.298448 s |
| Maximum explicit device buffers | 32735456 bytes |
| Sampled GPU process memory | 442 MiB |
| Host max RSS | 197200 KiB |

A nine-address boundary/fallback pilot also passed before the exhaustive run;
it used 6298 literal events, 15464 local evaluations and 0.133078 s GPU advance.
This is an exhaustive finite-domain test of the *clean regeneration subroutine*.
It does not enumerate all lower-controller faults or arbitrary macrostep inputs.
The physical rule, descriptor, ROM and state width remain fixed in every batch.

## Independent audit and provenance

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_geometry_closure --geometry figs/fixed_rule/small_holder_geometry_closure_v1 --domain figs/fixed_rule/small_holder_regeneration_domain_v1 --output figs/fixed_rule/small_holder_geometry_closure_audit_v1.json
```

Passed in 0.919370 s, 80632 KiB host RSS. The audit compares both complete upper
transitions using independent scalar, native and descriptor evaluation; verifies
saved pre/post-regeneration Hold and commit arrays; requires an actual discrepancy
if regeneration is omitted; and independently totalizes the ROM to check every
saved query offset/selector. It also verifies source, binary and artifact hashes.
The full physical trajectory and host-call prohibition are runtime assertions in
the hashed drivers, not reconstructed from the small checkpoint archives.

Unchanged full descriptor SHA256:
`af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`.
Geometry artifact SHA256:
`9ddbc5d7c45542cab9163e66c4ff7073fac85dc8643bb379eae02afa51ac87dd`.
Exhaustive-domain artifact SHA256:
`312b5523b7177fbe94d479e2d6586b96988b5123e77af4fd2de0fb2ac2fd7694`.
Exact binary hashes and measured resources are in the manifests; all run and
audit handles exited zero. No shared or frozen sources were modified.

## Remaining end-state obligations

Metadata lookup is no longer merely sampled at a few Addresses, and explicit
upper geometry repair preserves projected closure in two consecutive physical
work periods. A general noisy one-link relation still needs broader flag/Signal
suffix coverage and recovery of the lower geometry/controller/communication
invariants. Current accelerators retain their supported reference domains and
capacity guards. Exact metadata regeneration does not establish these other
requirements.

Actual full nested work periods remain missing. With current Q and U, a top step
at depth two requires Q² sites and U²=2^64 physical ticks. The clean-subroutine
batch timings are not a nested runtime estimate. The next engineering priorities
are broader flag-domain certification and physical evaluator/schedule cost
reduction or rigorously justified trajectory compression. A special upper-rule
callback would not satisfy the execution requirement. Robust finite-depth
termination and stochastic error amplification across levels remain open.
