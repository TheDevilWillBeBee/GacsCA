# Dependency-directed retrieval with complete self-reference

2026-09-27. The new fixed `sparse_holder` ROM reduces the computation core from
27721 to **16346 cells** and scheduled controller travel from 2001129064 to
**818235377 ticks per period**. Complete conditional own-ROM computation and
new physical path/packet checks pass. All154 raw Info/Hold fields remain encoded.
The execution baseline is unchanged; this candidate still uses Q32768/U2^31.

## What was removed, and what is still represented

The complete compiled descriptor uses738 of its2310 neighborhood input words.
689 are mutable words; the other49 are the center cell's ROM metadata. Only
the689 mutable operands receive three temporal histories and one vote slot.
Unused incoming operands have no address in the new history layout. No mutable
raw output or encoded controller field is removed.

At each evaluation entry the fixed program regenerates all49 own metadata words
from the **voted simulated Address** using its own ROM. This supplies the same
normalized input that G=pi F iota requires. It avoids retrieving static words
or maintaining temporal histories for them. Neighbors' metadata does not occur
in the complete descriptor's dependencies. The input Info metadata can remain
untouched: it is not read by retrieval, and both evaluations regenerate the
metadata they actually use. The output still includes all49 metadata fields,
regenerated into Hold from the newly computed Address before commit.

The compiler also retains the low-address MASK optimization, copies only the105
mutable descriptor outputs before output metadata regeneration, and fixes the
scratch allocation capacity at320. These are compile-time choices, with no
depth-dependent case or evolving host interpretation. Both initial encodings
and diagnostic decoders retain all154 raw fields. The physical local rule still
has105 mutable words/2704 bits and radius seven.

| Quantity | Retimed baseline | Sparse candidate |
|---|---:|---:|
| Gathered operands | 2310 | 689 |
| Temporal-history cells | 6930 | 2067 |
| Vote cells | 2310 | 689 |
| Core MEM cells | 9911 | 3447 |
| Stored instructions | 17809 | 12898 |
| SEND instructions | 6478 | 1786 |
| Core cells | 27721 | 16346 |
| Controller-path ticks | 2001129064 | 818235377 |
| Complete encoded Info/Hold fields | 154 /154 | 154 /154 |

The full physical F descriptor is unchanged:
`6e2f29f61bf281ec5d346cd58e717cf7e5b0afea263d2c17a18a58de295d8d23`.
The new hard-wired ROM is
`92e01ae6445c1bf7e125080bc2929b36fdc86ea089705f80650a2a3e9d7fa77a`.
Thus the candidate's projected G changes once, while remaining fixed across
depths. It is separate from both earlier ROMs; no frozen baseline was modified.

## Evidence

The symbolic check uses15 independent complete typed raw input cells. It checks
62010 retained-history instances, all738 supplied operands after regeneration,
both evaluations against the full physical descriptor with the candidate's own
ROM, all154 Hold outputs per cell, Signal payloads, commit and complete scratch
reset. It permits arbitrary stale input metadata rather than assuming the new
normalizer's result in advance. Its355665 instruction instances,2940 metadata
queries and26790 packet instances are **symbolic checks**, not physical evolution.

Separate new-ROM physical path checks pass for12801 ordinary paths,392 metadata
cases and12899 dispatch paths, through the unchanged local descriptor lemmas and
their existing clock-transfer relation. The six-phase packet schedule checks
23711 instruction occurrences and all1786 SEND sites. It checks actual new
operand positions, travel, same-track collisions, delivery/read ordering and
clock barriers. All phase margins are positive.

Six tests pass. They verify complete conditional self-reference, depth1–3
identity and full raw controller round trips, used-input coverage, disjoint
histories/votes and typed metadata. Mutations with a wrong controller retrieval,
wrong own-ROM lookup or omitted raw PC output fail. Literal active READ_B
transitions compare independent scalar and complete-descriptor outputs across
all five controller copies, including the computed result and next phase.
Those literal events do not constitute a full new-ROM physical work period.

Remaining candidate obligations are a whole-period composition, full physical
execution with successive decoded macrosteps, backend validation for the changed
layout, and noisy validation. Baseline repair experiments do not automatically
transfer to this different retrieval/metadata schedule. The conditional proof
still has typed-input, coherent-domain and local-refinement premises.

## Parameter reduction is now testable, not yet installed

Core plus five tail cells occupies16351 cells, fitting below16384 with33 unused
cells between the core and tail. Controller paths fit below2^30 with255506447
ticks to spare. These facts support investigating Q=16384/U=2^30; they do not
prove that the modified self-referential rule will retain these costs or fit a
new complete schedule. Packet flight, forcing, clearing and phase margins must
also be accommodated.

Simply changing Q is unsafe. The current complete description uses the physical
Address field width to implement modular Address arithmetic in two helpers,
and metadata regeneration leaves its zero-offset Address unmasked. Those are
consistent with today's Q=2^15. A Q=2^14 candidate must either fix a matching
Address alphabet once for all depths, or preserve the current width and correctly
handle its excess raw states in scalar/descriptor/projection/query semantics.
Regenerate and check its own description, ROM, space and timing after making
that fixed construction choice. Do not substitute a level-selected rule.

The minimal scratch allocator was also measured: it gives16263 core cells but
1102390861 controller ticks, slightly exceeding2^30. A fixed320 capacity gives
the accepted16346-cell/818235377-tick tradeoff. Larger349-used-slot layouts fit
more tightly but leave only four hypothetical core-to-tail cells atQ16384;
the selected layout retains more spatial margin. These are compiler design
measurements, not depth-dependent runtime choices.

This follows Gray's specialized ProgramBit projection and Gacs's self-description
approach discussed in [LOWMASK_COMPILER.md](LOWMASK_COMPILER.md). The changes
do not settle candidate-B Flag2, computed-SimBit timing or the papers' general
noise-amplification hypotheses.

## Reproduction and ownership

All commands used the existing watchdog with a512-MiB RSS threshold and
OPENBLAS_NUM_THREADS=1. No GPU allocation/build occurred. All jobs exited0;
combined sampled path/test child peaks were below155MiB, well below40GB.

```sh
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/sparse_holder_rom_v1_watch.json --seconds 60 --rss-mib 512 -- python -m experiments.fixed_rule.certify_sparse_holder_rom --output figs/fixed_rule/sparse_holder_rom_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/sparse_holder_paths_v1_watch.json --seconds 120 --rss-mib 512 -- python -m experiments.fixed_rule.certify_sparse_holder_paths --output figs/fixed_rule/sparse_holder_paths_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/sparse_holder_tests_v1_watch.json --seconds 90 --rss-mib 512 -- python -m unittest discover -s tests/fixed_rule -p test_sparse_holder.py -v
```

| Check | Internal seconds | Process peak KiB | Watch seconds / sampled KiB |
|---|---:|---:|---:|
| Complete ROM | 4.565152 | 66488 | 4.848755 /66116 |
| Paths and packets | 27.343333 | 81304 | 27.985636 /88988 |
| Six tests | 8.453 | Not separately recorded | 8.776203 /69168 |

Watchdog sampling is not an instantaneous OS cap. All new source, reports and
evidence are in the owned namespaces. Main-agent replies remain absent; its
status/reply file and all shared sources, jobs and historical data are untouched.
The full project goal remains active. Next implement and audit the smaller
fixed-parameter candidate, then close its physical execution and noisy behavior.
