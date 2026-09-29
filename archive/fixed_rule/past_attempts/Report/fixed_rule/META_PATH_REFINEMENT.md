# Complete conditional META paths

2026-09-26. The local identities in
[CLOCK_EVENT_REFINEMENT.md](CLOCK_EVENT_REFINEMENT.md) now compose into complete
isolated META instructions at all 98 actual fixed-ROM sites. The composition
checks the full controller, exactly one Data write and exact duration for every
valid query Address, under the stated clean physical hypotheses. A separate GPU
experiment executed 3822 instructions with intermediate checkpoints. This closes
a META refinement obligation; it is not the whole-period or depth-two theorem.

## Composition and locality

`certify_small_holder_meta_paths.py` reads and validates the actual fixed ROM:
unique first/last markers, memory-prefix kinds and indices, and every instruction
record. It checks the hashes and complete coverage of the prior clock certificate
and its audit. For each actual META it partitions queries into core except the
last site, last core site, gap and tail. The 392 paths cover all 32768 valid query
Addresses at all 98 instruction sites.

Each path instantiates the certified leaf's actual old controller and structural
metadata, checking both against the current symbolic state and the hard-wired
ROM. It obtains the next controller from that leaf's complete-raw expected state.
It checks every disequality hypothesis, not only whether an opcode is supported.
Flights have affine counts and positions in the query. The checker proves their
counts nonnegative, establishes conditions on the nonempty iteration domain, and
requires unchanged controller/Data for the repeated step. This supplies the loop
induction; zero-length flights are included. The final comparison retains all
eight controller fields, including stale ALU state, and requires exactly one
write at the intended destination.

Composition exposed a missing leaf: the first leftward move after right-end
reflection starts at a site with last=1. The previous left-flight template fixed
last=0. A new variant is proved against all 154 raw outputs at nine holders for
each of the seven clock intervals. A regression test replacing it with the old
leaf fails its ROM precondition. Tests also reject a skipped reflection, lost ALU
state, incorrect memory index and missing/misplaced endpoint markers.

`certify_small_holder_event_support.py` walks the complete descriptor backward
from its outputs. Of its 738 used raw input words, procedure inputs represent
logical offsets -3 through +4. Consequently, outside the checked nine-holder
window, a coherent one-head configuration agrees on every used input with an
instance of the quiet lemma. Unused raw slots may still contain head replicas;
the support argument accounts for that distinction. The other inputs agree
because geometry is canonical, Age uniform, metadata fixed, and flags/Signal/Wf
zero. A mutation that reads procedure Data beyond the event window is rejected.
This justifies composing the event with its quiet exterior in this domain.

## Exact path and result

Let L=30724 be core length, m the physical instruction location, d its memory
destination, q the query Address and s the metadata selector. From old FETCH:

- At 2L-m ticks, the first right/left sweep pair has returned to Address zero,
  reflected rightward and set META's readiness value to 1.
- The search/return pair takes another 2L ticks. At 4L-m, the head is at zero,
  moving right in WRITE, with rd=d and the metadata result in value.
- Reaching d and completing its WRITE takes d+1 ticks.

Thus D=4L+d-m+1. Core hits, endpoint hits and misses have equal duration. A core
hit switches to WAIT_META even when its returned value is zero; the return
reflection converts that phase to WRITE. A miss uses the actual gap/tail fallback
at the left reflection. The certificate compares the final value with the same
hard-wired record function. The final head is at d+1 in FETCH with pc advanced,
ra=rd=d, rb=s, the returned value retained and the original ALU state preserved.
Only Data[d] changes; procedure copies remain coherent.

The 98 sites have 12 durations, from 101532 through 122217 ticks. Each path lists
legal starting-Age intervals so that every old Age used by its D transitions lies
inside one certified regular active interval. The theorem does not silently cross
resets, votes, capture, rest or commit. Its other hypotheses are canonical coherent
state, zero flags/Signal/Wf, no incoming mail, a valid 15-bit query and an isolated
head. Multiple sufficiently separated copies were used in the physical tests.

## Physical execution and independent audit

The unchanged GPU physical event backend executed all 98 META sites with 13
query Addresses covering first/last core sites, memory/instruction boundaries,
gap and tail. It used three initial Ages: 1, 738197505 and 2281701377. Queries and
stale ra/rb/value/alu fields were supplied only in initial data; host transition
and evaluator callbacks were disabled during evolution.

Six checkpoints per run observe the instants before/after the ready reflection,
before/after the result/fallback reflection, and before/after the final write.
All complete logical head records match. Five selected physical holders per query
and checkpoint—including shifted holders carrying replica slots, the old
instruction and the destination—match all 154 raw fields. This is selected raw
coverage, not a complete-colony scan at every checkpoint.

| Measurement | Result |
|---|---:|
| Symbolic paths | 392; all 98 sites and valid queries |
| Composition certificate | 3.115732 s; 62376 KiB host |
| Added last-marked left-flight cases | 7 full-descriptor cases |
| Tests | 6 passed / 3.129 s; support 2 passed / 0.061 s |
| Actual META executions | 3822 |
| Saved full logical head records | 22932 |
| Checked complete raw probe records | 114660 |
| GPU advance wall time | 1.418373 s |
| Complete physical experiment | 94.407349 s |
| Peak host memory | 259980 KiB (about 254 MiB) |
| Explicit device allocation | 4807768 bytes |
| Recorded GPU process memory | 424 MiB |
| Independent final audit | 37.782466 s; 73792 KiB host |

The audit checks all 229376 metadata lookup values, 189 complete scalar/native
outputs for the added leaf, 3528 complete scalar/native reflection/write-boundary
outputs, every saved head record and the digest of all expected physical probes.
The native boundary comparisons validate the checkpoint model. Actual GPU probe
assertions are in the hashed driver; the audit does not replay every microstep.

The early pilot (26 executions) passed in 1.131434 s. An expanded attempt then
completed 26 executions before the existing prefix-only initializer rejected the
late Age. Its log and terminal failed progress record are preserved. No physical
transition failed in that attempt. A separate extended driver uses the existing
public, validated `from_stored` initialization for late Ages. Its late pilot
passed 26 executions in 2.446091 s, followed by the complete run above. This is
host-side initialization, not replacement of evolving state. No kernel or guard
was changed. The initial composition v1 also preserves a pre-execution Python
class-name collision and its exact source snapshot; v2 fixes that naming error.

## Reproduction

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.certify_small_holder_meta_paths --certificate figs/fixed_rule/small_holder_clock_events_v2.json --audit figs/fixed_rule/small_holder_clock_events_audit_v1.json --output figs/fixed_rule/small_holder_meta_paths_v2.json
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_meta_paths.py -v
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.certify_small_holder_event_support --output figs/fixed_rule/small_holder_event_support_v1.json
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_event_support.py -v
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_meta_path_execution --pilot --output figs/fixed_rule/small_holder_meta_path_execution_pilot_v1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_meta_path_execution_extended --late-pilot --output figs/fixed_rule/small_holder_meta_path_execution_late_pilot_v1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_meta_path_execution_extended --output figs/fixed_rule/small_holder_meta_path_execution_all_v2
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_meta_paths --certificate figs/fixed_rule/small_holder_meta_paths_v2.json --execution figs/fixed_rule/small_holder_meta_path_execution_all_v2 --output figs/fixed_rule/small_holder_meta_paths_audit_v1.json
```

The same audit command with the early/late pilot execution stems passed and is
saved as `small_holder_meta_paths_pilot_audit_v1.json` and
`small_holder_meta_paths_late_pilot_audit_v1.json`. The failed expanded command used
`small_holder_meta_path_execution --output .../small_holder_meta_path_execution_all_v1`.
No failed artifact was overwritten by a successful run.

## Remaining target and source relevance

Next is the ordinary-instruction scan relation. A useful coordinate is h for a
rightward head and 2L-1-h for a leftward head: every ordinary flight/reflection
advances one step around a cycle of length 2L. That relation must be derived from
these physical leaves before validating the full program's scheduling formula.
Incoming mail, its collision/flag guards, clock overrides, arbitrary retained
Signals and repair must still be composed with the ROM data flow and reset
encoding. Isolated META correctness does not establish the whole period.

This supports the Address-based hard-wiring/projection construction described by
Gray pp.31–32 and the modified self-correcting self-simulation allowed by Gács
§§9.2–9.3. It does not substitute general-purpose programming for the specialized
self-simulator. All proof interpreters here are diagnostics; physical evolution
uses the same fixed alphabet, neighborhood, description and implementation.
No depth dispatch, additional hardware register or new physical kernel was added.
Q and U did not change. Practical full depth-two execution and general cross-level
noise suppression remain unfinished; U<=128Q remains unnecessary.

## Provenance and coordination

- Path certificate: `9c10516111e40533a9b48c7d32d0cc7007822255c4338d2a14bd6e705843a44f`.
- Support certificate: `b0a4f13a1e83ae18c4c9478baaeea25c43596022a86f7a8dd346f52379a13d50`.
- Physical run manifest: `b22caf1abd2558a59bc8c589b9358fab6ecfb101c524990c48c90313b19c9b99`.
- Physical archive: `8663f691e086cf9fd6fd4e4f81991093c5986daae35442a9fdbfe9d5a5db67a6`.
- Final audit: `86e7c33bb004f20c6c6f000693fa08e3121bfb3684f6d3dff1369eb10fe17796`.

Descriptor remains `af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`;
GPU binary remains `4419e5fdd8caeb81c884db3ede3d709d677693aee1943482040e171bc54f1c7e`.
Clock-audit and new execution/audit source hashes all match. Owned additions are
META path/support certificate and test files, two physical drivers, the audit,
this report and namespaced evidence. Only our STATUS handoff was updated among
existing reports. No frozen/shared source or CUDA artifact was edited. All own
handles are terminal. MAIN_AGENT_NOTES.md remains absent; please reply there.
The separate 8 GiB reservation is still pending and was not used. The historical
third-link process was not observed; absence is not a completion audit. The full
research goal remains active.
