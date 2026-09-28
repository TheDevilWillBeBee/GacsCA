# Position-independent controller events and conditional scans

2026-09-26. Two new diagnostic certificates extend the physical refinement in
[LOCAL_EVENT_REFINEMENT.md](LOCAL_EVENT_REFINEMENT.md). They retain the same full
raw rule F, projected rule G, ROM, physical alphabet and radius. They are proof
checks, not evolution backends or upper-rule callbacks. No GPU job was launched.

The first certificate covers 49 event families with a symbolic 15-bit physical
base Address and symbolic coherent metadata and Data. The second covers 43 scan
and reflection families with explicit word-disequality hypotheses. Every case
compares all 154 raw outputs at nine holders against the complete 13442-operation
self-description. Together they check 127512 symbolic output words. Independent
finite audits compare 4968 complete output records with scalar and native F.

## Domain and checked behavior

The positional certificate replaces concrete ROM locations with canonical
geometry Address(A+i)=(A+i) mod Q, for arbitrary A in [0,32768). Each logical
metadata record is independently symbolic and consistently replicated into the
seven holders that store it. Data and stale controller words are symbolic within
their declared widths. Event-specific structural conditions still apply: for
example a memory read requires kind=MEM and a normal rightward move requires
last=0. Thus this is an identity for all assignments satisfying those conditions,
not a claim that an arbitrary instruction can execute at every actual ROM site.
Actual hard-wired metadata can be substituted where the conditions hold.

Its cases cover quiet Data preservation, the five READ_B arithmetic operations,
READ_A, WRITE, LOAD, both SEND directions and all eight hop counts, the seven
META selectors, leftward flight, all eight rightward phases and their right-end
reflections. PC overflow, retained ALU/operand fields, five procedure copies,
emitted packets and all geometry/static/flag outputs are included. FETCH at
arbitrary instruction locations is still outside this certificate; the previous
concrete-location FETCH identities remain the available evidence.

The added algebra normalizes low-bit masks and modular addition, including
address wrap and 32-bit PC increment. A bounded word differs from any nonzero
cyclic shift of itself. Exhaustive small-width tests check these identities;
64-bit and boundary-value tests check masking and overflow. The symbolic proof
uses structural term equality after these reductions, not sampled operands.

The original positional flight cases use a particular unequal operand (a cyclic
shift of the site's index). The separate scan certificate removes that
restriction by recording exact conditions such as pc != index, rd != index, or
rd != Address. Its only additional algebraic reduction is EQ(x,y)=0 under a
recorded x != y hypothesis. The certificate lists those hypotheses per case;
concrete audits explicitly check them before comparing outputs.

The 43 scan cases cover rightward flights and right-end reflections for all eight
phases, arbitrary-phase leftward flight, left-end reflections, META becoming
ready, missed-query fallback, metadata hits at the right endpoint, and unready
META flight/reflection. META values may be zero after a hit: WAIT_META preserves
the distinction between a returned zero and a query not yet performed. Selectors
0 through 6 and a representative unsupported selector 7 are checked at relevant
metadata/fallback events. Fallback rd is an arbitrary 64-bit word, including the
gap/tail threshold; this is the actual local rule's fallback, not a host ROM query.

A negative test sets a WRITE operand equal to the current memory index. The real
rule writes 23 over 0 and changes the controller, contradicting an unqualified
flight assertion. Removing necessary hypotheses prevents the symbolic check from
passing. Mutations that lose reflection direction, META phase/value, controller
PC, arithmetic output, geometry or an emitted packet are also rejected.

Both certificates use **one active Age, 738197514**, canonical coherent geometry,
one head or a quiet configuration, zero flags/Signal/Wf, and no incoming mail.
They do not yet quantify over all active clock intervals or cover collisions,
faults, simultaneous heads, the full projected alphabet or an entire scan path.
The nine-holder comparison includes the full raw schema; it does not assert that
metadata can be omitted from decoding or that noncanonical states can be dropped.

## Results and reproduction

| Check | Exact result | Seconds | Peak host KiB |
|---|---:|---:|---:|
| Position certificate v1 | 49 cases; 67914 output words | 8.143864 | 59456 |
| Position tests v1 | 4 passed | 8.614 | not recorded |
| Position independent audit v1 | 2646 full scalar/native outputs | 9.343873 | 58116 |
| Scan certificate v2 | 43 cases; 59598 output words | 8.324450 | 58420 |
| Scan tests v1 | 5 passed | 9.217 | not recorded |
| Scan independent audit v1 | 2322 full scalar/native outputs | 8.177528 | 58472 |

Finite audits use zero, width-limited all-ones and seeded random assignments,
address-wrap boundaries, controller overflow and fallback-threshold queries.
They interpret symbolic syntax independently of the simplifier and compare every
raw output against both scalar and native rules. They corroborate the checker;
they are not exhaustive concrete evaluations of its symbolic domains.

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.certify_small_holder_position_events --output figs/fixed_rule/small_holder_position_events_v1.json
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_position_events.py -v
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_position_events --certificate figs/fixed_rule/small_holder_position_events_v1.json --output figs/fixed_rule/small_holder_position_events_audit_v1.json
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.certify_small_holder_scan_events --output figs/fixed_rule/small_holder_scan_events_v2.json
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_scan_events.py -v
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_scan_events --certificate figs/fixed_rule/small_holder_scan_events_v2.json --output figs/fixed_rule/small_holder_scan_events_audit_v1.json
```

The first scan attempt (`--output .../small_holder_scan_events_v1.json`) failed on
structural normalization of the expected left-end fallback expression. No v1
certificate was written. The log and exact source snapshot
`figs/fixed_rule/small_holder_scan_events_failed_v1.py.txt` are preserved. The v2
checker expresses the same fallback as a boolean mask, compatible with the
existing algebra; the physical descriptor and rule were not changed.

## Source justification and remaining obligations

Gray pp.31–32 hard-wires the description through Address and then removes
ProgramBit by projection. His resulting self-simulator is specialized; no
arbitrary user-program platform is required. Gács §9.2 explicitly permits an
identical or suitably modified self-correcting simulated rule. Section 9.3 and
Definition 9.19 require actual encoded computation and update, not only matching
an opcode list or initializing nested data. Those distinctions motivate these
full-controller physical refinement checks and the earlier
[ROM_DATAFLOW.md](ROM_DATAFLOW.md) and [RESET_ENCODING.md](RESET_ENCODING.md).
The local extracts are `papers_txt/gray_readers_guide.txt` and
`papers_txt/gacs_2001.txt`; no new source-equivalence claim is made here.

Next steps are to cover the relevant clock intervals and arbitrary FETCH sites,
compose these local identities into exact scan durations, and combine incoming
transport under verified noninterference conditions. The resulting instruction
semantics must then join the actual ROM data flow, Signal/flag behavior and reset
encoding into an all-input physical period relation. Existing finite GPU periods
and exhaustive META timing measurements remain useful evidence, not that theorem.
No full upper work period at depth two or general cross-level noise amplification
has been established. The permanent cap Address defect remains an open robustness
obstruction, as documented in [CAP_DEFECT.md](CAP_DEFECT.md).

The user priorities remain correct fixed-rule self-simulation, practical two-level
GPU execution, and measured cross-level repair. Q and U should be optimized under
correctness; U <= 128 Q is not required. Neither Q nor U changed in this work.
The current U squared is still 2^64 physical updates per full second-level period;
these diagnostic identities do not authorize replacing it with a host upper-rule
callback. The final research goal remains active and incomplete.

## Provenance and coordination

SHA256 values:

- Position certificate: `9266990482cb2ccc0237b2272637a767c562e6b610f7b14a13037746ec1b0276`.
- Position audit: `f40f560501d5e21f5dfc99d522c5ef2740d9fd3c4b4e3fb19e74f6644369cb6a`.
- Scan certificate v2: `04f22dfb9305eb3245d26d6bf504a4a73be00c14bd8af580db0f3e8041356745`.
- Scan audit: `3d14a01af838f92da98cc0c03623f84b9b279590d8fbab4be1ec2771378e3cf2`.
- Failed scan source snapshot: `fa3a081848d602a1b301df3c79c71ed76886609d46eb00bab222c5d5aa312819`.

Physical descriptor remains
`af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`.
The previous local-event audit's three source hashes and the new position/scan
audits' five/seven source hashes were rechecked with zero mismatches.

Owned additions are the two certificate modules, their audits and tests, this
report and their namespaced evidence. Only our STATUS handoff was updated among
existing reports. No shared module, CUDA artifact or historical dataset changed.
All own test handles are terminal. Main-agent notes remain absent; please reply
only in `Report/fixed_rule/MAIN_AGENT_NOTES.md`. The separate 8 GiB GPU reservation
request is still pending and was not acted on. A read-only process check found no
`third_link_initialized` process; that absence does not certify its completion.
