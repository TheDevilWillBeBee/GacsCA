# Streamed nested initialization and two guarded lower macrosteps

2026-09-26. The complete immediate-parent stream of a real depth-two initializer
has been generated with bounded host memory. Two lower macrosteps also completed
on two guarded windows sampled from that initializer. All 154 decoded fields
match the full rule, and the shrinking interiors match two physical steps of the
actual upper ring. An independent audit passed. This is not a full Q-colony
bottom allocation or a completed upper work period/top macrostep.

## Fixed encoding and streaming

`small_holder_stream_initial.InitialRing` generates bounded chunks of the same
recursive initial configuration as `small_holder_initial.cell_at`. At depth zero
it preserves the supplied complete projected top states. At every higher depth,
all raw parent fields, including procedure/controller backups and the seven
hard-wired metadata records, become Info Data in a new colony. The initializer
lifts that Data into all five physical holders. No evolving transition is computed
by this host initializer. Its recursion is only immutable initial-data generation;
it supplies no evidence of self-reference closure by itself.

A chunk contains at most 128 complete raw rows, or 157696 bytes. Positions and
sizes use arbitrary-precision host integers; physical fields and the local rule
remain fixed. The raw schema is still 154 words/4090 bits, with 105 projected
words/2704 bits. The same descriptor digest applies at every requested depth:
`af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`.
The fixed ROM byte digest remains
`c59c72abe15729e4848ce549b31f1faec63465f16da2c717f0eb233fb1e7cbe4`.

`small_holder_resident_mixed.World.from_raw_chunks` validates row shape, every
field width, all metadata and exact total count before accepting initialization.
It uploads bounded chunks into the actual resident Info banks. Failure frees the
incomplete world. `from_hierarchy` changes only the input stream and colony count;
there is no depth-selected physical rule, alphabet or evaluator. Oversized jobs
are rejected by explicit execution/memory limits before consuming a large stream.

The complete parent stream for one top cell at depth two comprises 32768 rows,
40370176 bytes. It passed in 0.752524 s with 57940 KiB maximum host RSS. The check
compares 512 distributed rows with the independent scalar recursive initializer
and decodes every raw top field. The stream SHA256 is
`20b828059eeb101153877d9ff5d0a6fa48b5249e937d1ebaca6934c8c7591ede`.
This measurement streams and hashes the full parent input; it does not allocate
the full bottom ring on GPU.

## Widened execution domain, unchanged physical rule

Nested windows exposed an unnecessarily strict accelerator restriction: the
resident suffix required right Signals to be uniform across all colonies.
The existing per-colony Flag1 profile in fact supports independently varying
right bits when left Signals are zero. `prove_small_holder_mixed_right.py`
checks this against the unchanged complete physical descriptor using the BDD
engine. It quantifies all Addresses and admissible fronts, plus three independent
neighboring right bits (eight assignments), in each of entry, forced growth,
cutoff and erasure. The four cases passed in 1.260221 s. As before, canonical
geometry, coherent backups and zero suffix mail are required.

The mixed backend compiles a private copy of the frozen resident source with one
exactly checked domain-guard replacement: it removes the comparison with the
first colony's right bit. It retains the left-zero guard, all Signal-copy checks,
mail checks, atomic staging, local expression and physical flag reconstruction.
The independent-event source is included unchanged. Original source files and
binaries remain reference fixtures. This is a broader certified execution domain,
not a new physical transition or a hierarchy-specific kernel.

Flag1 recurrence is colony-local on canonical geometry. Neighboring tail/head
Signal patterns and crossing Wf backup holders are represented explicitly by the
proof, including different bits on the two sides of a boundary. With zero mail
and unchanged Address, Flag1's clearing priorities do not alter controller/Data
computation. Left Signal one, arbitrary flag profiles, broken backup geometry
and arbitrary physical noise remain unsupported by this backend.

The source interpretation stays that of [SMALL_HOLDER.md](SMALL_HOLDER.md):
candidate-B Flag2 and old-Signal D10 timing are explicit modified-rule choices.
The specialized self-description motivation from Gray pp.31–32 and Gacs 9.2–9.3
does not constitute a repair/amplification theorem for this implementation.

## Executed windows and what their guards establish

The top seed includes raw controller value `0x123456789ABCDEF0`. Its actual
first-layer ring has Q=32768 cells and stores that raw word at upper Address
9432. Two contiguous upper windows are sampled: Addresses -14 through 18,
and 9418 through 9446, with indices taken modulo the true upper-ring size.
They contain the controller origin and an encoded top controller word.

These 62 complete upper states initialize 62 lower colonies in a small periodic
bottom world (2031616 physical cells). The joins are artificial; their geometry
produces Flag1 near the window edges. Computed right Signals therefore vary:
12 are one after the first lower period and 24 after the second. Left Signals
remain zero. The run exercises the widened domain through actual computation,
Signal capture, physical waves, commit and recurrence.

At both lower commits, every decoded raw word agrees with the full modified
self-simulated rule on that executed 62-cell periodic upper input. Separately,
full-rule causal cones start from the *true* Q-cell upper initialization and
shrink by radius seven per upper tick. After one step, 34 interior cells agree;
after two steps, six agree: upper Addresses 0–4 and 9432. The upper controller
resets at Address zero, then moves to Address one. The encoded top controller
value stays intact. All raw fields are compared, including controller backups.

These guards establish the stated **decoded upper-rule comparisons**. They do
not establish equality of the complete bottom physical trajectory with an
unexecuted Q-squared-cell ring: two lower work periods have a much larger raw
physical light cone. No such full-bottom trajectory claim is made. Likewise,
two upper physical ticks are far short of a complete upper work period.
Artificial-seam flag activity is not a stochastic noise-correction result.

## Commands and measured evidence

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.prove_small_holder_mixed_right --output figs/fixed_rule/small_holder_mixed_right_proof_v1.json
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_stream_mixed.py -v
# 5 tests, 12.634 s, OK.
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_stream_measure --output figs/fixed_rule/small_holder_stream_measure_v1.json
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_nested_windows --output figs/fixed_rule/small_holder_nested_windows_v1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_nested_windows --input figs/fixed_rule/small_holder_nested_windows_v1 --output figs/fixed_rule/small_holder_nested_windows_audit_v1.json
# Independent audit passed, 1.403208 s, 59728 KiB host RSS.
```

Tests compare the streamed initializer with the existing recursive definition at
depths zero through three, decode every raw controller word at depths one through
three, retain binary/descriptor identity under depth requests, and reject broken
metadata, widths, incomplete streams and oversized chunks. Mixed-wave tests check
full raw native steps around fronts and colony boundaries, plus independent
versus synchronous controller evolution while Flag1 is active.

| Nested-window measurement | Result |
|---|---:|
| Successive lower work periods | 2 |
| Physical ticks | 8589934592 |
| Executed lower colonies / physical sites | 62 / 2031616 |
| GPU advance wall time | 224.434556 s |
| Whole run | 226.296005 s |
| Resident / peak explicit buffers | 12376112 / 17299904 bytes |
| Sampled total GPU process memory | 432 MiB |
| Maximum host RSS | 166240 KiB (162.34 MiB) |

The audit verifies the independent recursive initialization, scalar/native/full
expression agreement, all decoded raw outputs, both true-upper-ring cones,
controller motion, retained top data, actual mixed flags, tick accounting and
source/binary/artifact hashes. The independent kernel still reports 220 registers
and 48 stack bytes/thread. Exact binary SHA256:
`d8b6f3b716eb69bd0a6ec3a14110f9df375a08d814f5b6c2d78e0aa3e4396370`.
Artifact SHA256:
`c3dcba02ab65ee044bca402d917f4fcbb835d476e1c0c00470122b69a9a215b4`.

## Concrete next allocation pilot for coordination

`small_holder_nested_allocation.py` is ready to allocate an entire encoded lower
ring, advance eight physical reset/controller ticks, and verify every uploaded
raw parent word and every lower head. Its depth-one invocation passed in
0.760723 s, with 161552 KiB host RSS and 0.000533 s GPU advance:

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_nested_allocation --depth 1 --output figs/fixed_rule/small_holder_nested_allocation_depth1_v1.json
```

A **proposed, not executed** depth-two pilot needs 5064014048 resident bytes plus
2602303488 staged bytes = 7666317536 explicit bytes (about 7.14 GiB). Request an
8 GiB GPU reservation including context/temporary overhead from the main agent.
The concrete command is:

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_nested_allocation --depth 2 --device-budget 5368709120 --extra-device-budget 2684354560 --output figs/fixed_rule/small_holder_nested_allocation_depth2_v1.json
```

It would verify the whole Q-colony initialization and eight bottom ticks; it
would not establish a lower macrostep, let alone a top macrostep. Its Info hash
should match the complete streamed-input hash above. Large-job scheduling remains
with the main agent; no Q-colony allocation has been launched.

The other next work is communication scaling and a credible way to handle the
U-squared horizon of 2^64 while preserving actual physical state and faults.
Complete nested work periods, finite-depth boundary dynamics, general correction
and measured cross-level noise robustness remain open. The full goal is active.

Owned files: the streaming and mixed-backend modules; test_small_holder_stream_mixed.py;
prove_small_holder_mixed_right.py; stream_measure, nested_windows, its audit and
nested_allocation experiment modules; this report, STATUS.md and named private
build/results under figs/fixed_rule. No shared source, existing report or job was
changed. All runs/audits exited zero; device query empty afterward. The historical
third-link job was not observed, which does not establish its completion.
Replies and scheduling decisions belong in MAIN_AGENT_NOTES.md (still absent).
