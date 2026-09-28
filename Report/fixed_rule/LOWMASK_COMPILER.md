# Less controller travel with a complete self-referential ROM

2026-09-27. The experimental `lowmask_holder` compiler reduces scheduled
controller travel by **324718766 ticks per period (16.2268%)**, while preserving
the complete conditional self-ROM computation. New physical path and packet
schedule checks pass. This is a candidate for further optimization, not a
replacement for the frozen retimed execution baseline or a measured GPU speedup.

## Change and physical reason

The existing evaluator implements bitwise NOT as NAND(x,x). A head reads the
same MEM address twice, requiring a full computation-core circuit between
reads. The compiler changes 2930 instructions to NAND(MASK,x), reading a shared
all-ones word at reserved MEM Address 6 first. A single extra LIT initializes
that word at each of the two evaluation entries. Fivefold protection already
applies to this Data word; no additional physical field, opcode or controller
register is introduced.

The literal must precede every changed read. In particular, input metadata
regeneration occurs before the evaluation entry and retains its original NANDs.
An early exploratory rewrite of all 2936 equal-operand NANDs would have read
the uninitialized constant during that regeneration. It was not installed or
used as successful evidence. The accepted compiler changes only the evaluation
and subsequent output-regeneration instructions.

The other rejected placement puts MASK after the existing MEM bank. It merely
moves a circuit from operand reading to result writing, and slightly increases
total travel to 2001384332 ticks. The diagnostic retains a reproducible cost
calculation for that initialized alternative; no full correctness result is
claimed for it.

| Quantity | Retimed baseline | Low-mask candidate |
|---|---:|---:|
| Controller-path ticks per period | 2001129064 | 1676410298 |
| Stored instructions | 17809 | 17810 |
| Computation-core cells | 27721 | 27722 |
| Q | 32768 | 32768 |
| U | 2147483648 | 2147483648 |
| Projected state bits | 2704 | 2704 |

The paths still exceed 2^30 ticks and the core still exceeds 16384 cells.
Consequently neither power-of-two parameter can be halved by this change alone.
Outside-controller time includes communication and flag dynamics; it cannot
all be discarded as idle time. Fewer travel ticks also need not reduce the
current event backend's runtime, since that backend already skips quiet flight.

## Fixed rule and complete self-reference

The full physical transition F, alphabet and radius seven are unchanged:
`6e2f29f61bf281ec5d346cd58e717cf7e5b0afea263d2c17a18a58de295d8d23`.
The **projected rule G does change**, because its hard-wired ROM changes to
`08579e057a390c9e99d5eb993525591989929419b37dfc5c52533f7a179c1fc8`.
This one candidate ROM is fixed independently of initialization depth. Tests
check identical rule identity and state width at depths 1, 2 and 3, and complete
raw controller encoding. Those depth checks are initialization evidence only.

The symbolic checker uses the candidate ROM for both input and output metadata
regeneration and compares all 154 computed raw fields with F on arbitrary typed
complete input neighborhoods. It includes active controllers, all three gathered
histories, votes, both evaluations, Signal delivery payloads, commit and reset.
This is complete conditional own-ROM computation, not an opcode inventory or a
payload-only computation. It does not substitute an upper transition into a
physical trajectory.

The construction remains consistent with Gray's specialized hard-wiring and
ProgramBit projection (pp. 31–32), and the self-description/block-simulation
approach in Gacs sections 9.2–9.3. See the source discussion in
[RETIMED_HOLDER.md](RETIMED_HOLDER.md). Candidate-B Flag2 and the SimBit/Signal
timing qualifications remain. No general amplification theorem is claimed.

## Physical checks and limits

The candidate rechecks 17713 ordinary paths, 392 metadata-query cases and 17811
dispatch paths. It reuses the unchanged local descriptor lemmas through their
existing clock-transfer identity, while binding fresh diagnostic constructors
to the new ROM without mutating module globals. The six-phase schedule checks
28544 instruction occurrences and all 6478 SEND sites, including collisions,
delivery/read order and clock barriers. All phase margins are positive.

Six focused tests pass. They include full conditional self-reference, literal
physical READ_A/READ_B events compared between scalar and complete descriptor
implementations across all five controller copies, depth-independent identity,
exact-neighborhood rejection, and rejection of a wrong MASK or omitted raw PC
output. A separate test confirms no other instruction writes Address 6 and
the initialization precedes every rewritten instruction.

Still missing for this candidate: a composed whole-period theorem and complete
physical period execution, successive decoded physical macrosteps, backend
validation against the changed ROM, and noisy validation of the shared constant.
The existing baseline's GPU runs and broader repair evidence do not transfer
automatically. All new symbolic/path claims retain their stated canonical,
typed-input and local-refinement premises.

## Reproduction and resource use

All runs used the existing watchdog, OPENBLAS_NUM_THREADS=1 and a 512-MiB child
RSS threshold. No GPU was used or rebuilt; the largest combined sampled child
peaks during concurrent path/tests were below 213 MiB. All processes exited 0.

```sh
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/lowmask_holder_rom_v1_watch.json --seconds 60 --rss-mib 512 -- python -m experiments.fixed_rule.certify_lowmask_holder_rom --output figs/fixed_rule/lowmask_holder_rom_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/lowmask_holder_paths_v1_watch.json --seconds 120 --rss-mib 512 -- python -m experiments.fixed_rule.certify_lowmask_holder_paths --output figs/fixed_rule/lowmask_holder_paths_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/lowmask_holder_tests_v1_watch.json --seconds 90 --rss-mib 512 -- python -m unittest discover -s tests/fixed_rule -p test_lowmask_holder.py -v
```

| Check | Internal time | Process peak RSS | Watch time / sampled peak |
|---|---:|---:|---:|
| Complete ROM and cost | 5.743797 s | 91692 KiB | 6.106992 s / 89988 KiB |
| All paths and packets | 39.003035 s | 102928 KiB | 39.741337 s / 120500 KiB |
| Six tests | 11.248 s | Not separately recorded | 11.641063 s / 96736 KiB |

Watchdog sampling is not an instantaneous memory cap. Shared files, jobs and
historical datasets are untouched. The main-agent reply file remains absent.

## Next material reduction

A direct dependency inventory of the current compiled complete descriptor finds
only **738 of 2310 input words** used by its operations or outputs. By offset
-7 through 7 the counts are 5, 6, 20, 38, 56, 75, 93, 146, 93, 76, 57, 39, 21,
7, 6. All 49 used metadata words are from the center cell. The current compiler
nevertheless retrieves and reserves histories for all 2310 words.

Next implement retrieval and history storage for actual descriptor dependencies,
while retaining complete encoded Info/Hold and all raw controller outputs.
Unused *neighbor input operands* are distinct from omitted represented state.
Recheck all own-ROM, timing, communication and repair interfaces for that
layout; this inventory alone proves no smaller working construction. Combining
that reduction with the present travel improvement is more promising than
simply shrinking current clock margins. The full project goal remains active.
