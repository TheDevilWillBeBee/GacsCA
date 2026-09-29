# Period entry relation and timed symbolic Data flow

2026-09-26. The work-period boundary now has an executable encoding/validation
relation that includes complete raw controller state, retained Signals and
uncleared scratch. A new symbolic checker interleaves every instruction memory
event and packet delivery and compares every read/write with the batch ROM
calculation. A separate known-bit check discharges the 15-bit META-query premise
along that entire trajectory. These close semantic composition obligations;
the complete physical macrostep induction is still to be assembled explicitly.

## The Age-zero relation

`gacsca/fixed_rule/small_holder_period_relation.py` defines initialization,
streaming validation and decoding only. It never evolves a simulated cell.
For a projected upper configuration y, the allowed lower boundary states E(y)
have:

- Address `i mod Q`, Age zero, and actual fixed-ROM metadata;
- coherent Data replicas, with all 154 words of `iota(y[colony])` stored in Info,
  including all controller and mail fields;
- zero physical heads, every controller field, every mail field, flags and Wf;
- zero Data at non-MEM sites, arbitrary Data at other MEM scratch sites;
- arbitrary physical Signal words.

The projected upper alphabet has 105 dynamic words; its 49 raw metadata words
are regenerated from Address by the fixed hard-wiring. Decoding reads every
Info word, validates its field width and metadata normalization, then projects
to the upper cell. It does not discard controller fields or substitute a
transition result.

Scratch freedom matters at the macrostep boundary. Commit changes Info while
the final computation's scratch remains. The actual next reset clears all 9773
MEM scratch words and retains all 154 Info words. This is checked against the
entire fixed ROM, including tail memory. Clearing scratch is therefore a real
next-period transition, not a host reinitializer. The timed checker also verifies
that reset after commit, but does not count it inside the preceding U ticks.
Retained Signals likewise remain physical state rather than being erased at a
boundary.

The constructor accepts a lazy parent accessor and produces one full raw cell
at a time. The full-ring validator uses a 64-cell cache and streams decoded
parents rather than accumulating a hierarchy in host memory. No depth argument,
depth-selected rule or additional hardware state is introduced.

The intended next theorem is

```
F^U(E(y)) is contained in E(G(y)), where G = pi F iota.
```

Along canonical lower states, physical metadata remains normalized, so this can
be transferred to the single fixed projected rule G. This equation is the
remaining composition target, not a claim that the new validator proves it.

## Actual-time symbolic memory events

`certify_small_holder_timed_dataflow.py` uses the existing fixed-ROM schedule and
symbolic input words. It starts from the same 15 independently represented raw
upper cells as the old ROM certificate. It splits arithmetic instructions into
their separate READ_A, READ_B and WRITE events, retains LOAD query values, places
META writes at their certified completion times, samples SEND payloads at birth,
and writes deliveries at their actual arrival times.

Events at one clock tick read old memory before deliveries; controller writes
have their physical priority after deliveries. The actual schedule's stricter
noninterference checks exclude conflicting accesses in any case. Pending packet
payloads are retained until delivery and removed only then. Every phase must
finish with no pending packets.

Each instruction read and write is compared symbolically with the original
batch calculation. Whole Data memory is compared after each phase. This checks
the batch interpretation's delayed-delivery abstraction rather than assuming
that it is harmless. All-input equality follows from interned symbolic word
expressions, not from selected concrete payloads.

| Phase | Instruction reads | Instruction writes | Deliveries | Last memory event Age |
|---|---:|---:|---:|---:|
| Gather 0 | 38235 | 3510 | 32340 | 163312990 |
| Gather 1 | 36960 | 2325 | 32340 | 420134776 |
| Gather 2 | 36960 | 2325 | 32340 | 688570233 |
| Third evaluation | 408075 | 205125 | 150 | 1906786889 |
| Precommit halt | 0 | 0 | 0 | 2147500636 (head halt) |
| Final evaluation | 407925 | 205125 | 0 | 3449652859 |

Totals: 928155 reads, 418410 writes and 97170 deliveries. Each phase checks
491520 Data words. All three histories, both complete evaluator results, both
five-buffer Signal groups, the commit result and next-reset scratch clearing
agree with the normalized complete descriptor. All 154 decoded raw output words
are included. The physical interpretation of these timed events still depends
on the separately checked instruction, dispatch, transport and barrier lemmas;
this diagnostic is not an execution backend or recursive interpreter.

## META query-domain closure

The existing complete META paths quantify valid 15-bit query Addresses. Merely
checking their durations would not prove that the program's LOAD values satisfy
this premise, particularly when output Address was computed by the descriptor.

`certify_small_holder_meta_query_bounds.py` instruments every lookup in the timed
and batch diagnostic. Conservative possible-one/possible-zero masks propagate
through typed inputs, constants, NAND, arithmetic, comparisons, shifts and ROM
values. All 5880 lookups, covering all seven selectors and both input/output
regeneration, have possible-one masks at most 32767. The instrumented Data-flow
result is exactly the saved timed result. No query is truncated by the checker.
Tests reject an unbounded input word and separately bound the complete
descriptor's Address output on all typed inputs.

## Executable checks and costs

The entry experiment validates every one of 32768 sites in a full colony with
nonzero scratch, arbitrary retained Signals and a complete random upper state.
It then compares 317 complete scalar/native first-reset outputs, covering every
Info/Hold location and representative core/tail boundaries. This is actual
single-tick physical execution; it is not a full-period run.

Seven period-semantics tests passed in 1.062 s. They round-trip active raw upper
controllers, reject omitted controller content and stale physical fields, admit
scratch/Signals, and check the same relation and rule identity at initializer
depths one through three without materializing those hierarchies. They also
reject an altered packet arrival and an omitted real operand read. The depth
checks are initialization/decoding checks, not multi-level dynamics. Three
additional known-bit tests passed in 0.399 s; their unittest log is retained.

| Check | Seconds | Peak host RSS (KiB) |
|---|---:|---:|
| Timed symbolic Data-flow proof | 6.171405 | 198116 |
| Full entry validation and first-reset probes | 12.154382 | 58452 |
| Instrumented META-query proof | 5.219202 | 213904 |

Every main run used a 512 MiB virtual-memory ceiling; measured peak RSS was about
209 MiB. No GPU job, shared CUDA artifact or historical dataset was changed.
No failed run was superseded in this milestone.

Reproduction used `ulimit -v 524288` and `OPENBLAS_NUM_THREADS=1`, saving matching
`.log` files. Preserve existing evidence by choosing new output names.

```sh
python -m experiments.fixed_rule.certify_small_holder_timed_dataflow --schedule figs/fixed_rule/small_holder_mail_schedule_v1.json --output figs/fixed_rule/small_holder_timed_dataflow_v1.json
python -m experiments.fixed_rule.validate_small_holder_period_relation --output figs/fixed_rule/small_holder_period_relation_v1.json
python -m experiments.fixed_rule.certify_small_holder_meta_query_bounds --schedule figs/fixed_rule/small_holder_mail_schedule_v1.json --timed figs/fixed_rule/small_holder_timed_dataflow_v1.json --output figs/fixed_rule/small_holder_meta_query_bounds_v1.json
python -m unittest discover -s tests/fixed_rule -p test_small_holder_period_semantics.py -v
python -m unittest discover -s tests/fixed_rule -p test_small_holder_meta_query_bounds.py -v
```

Each JSON records source hashes; the query proof also binds the schedule and
timed-result hashes. The descriptor remains
`af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`.
Q=32768, U=4294967296 and the fixed ROM remain unchanged.

## Remaining proof and project scope

Next assemble the physical induction over the complete period: first reset
establishes the timed program entry; instruction/dispatch and packet lemmas
justify each timed event and intervening flight; context/noninterference lemmas
preserve the read values; quiet phases justify the clock barriers; Signal/flag
lemmas restore the flags/Wf boundary premise; commit restores E(G(y)). The
translation/aliasing argument extending the 15-symbolic-colony calculation to
arbitrary ring lengths must also be explicit. No certificate should be called
a macrostep theorem merely because its dependencies are listed.

Source rationale and limitations remain those in
[PROCEDURE_CONTEXT_AND_BARRIERS.md](PROCEDURE_CONTEXT_AND_BARRIERS.md): the
specialized Gray/Gács construction and its explicit candidate-B/old-Signal
choices, rather than a general-purpose programming requirement. Full depth-two
periods at practical GPU cost, cross-level error correction, cap stability and
the printed-source ambiguities remain open. Q/U optimization is still required;
U<=128Q is not an acceptance constraint.
