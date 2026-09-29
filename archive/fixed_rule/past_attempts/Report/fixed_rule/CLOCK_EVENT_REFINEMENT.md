# Controller refinement across regular active clocks

2026-09-26. The full-raw local identities now cover the seven regular active
clock intervals, with symbolic physical Address, surrounding coherent metadata
and Data, and all specified stale controller words. General FETCH cases cover
every instruction kind used by the actual fixed ROM, plus LOOP, at ordinary
positions and right endpoints. This extends
[POSITION_EVENT_REFINEMENT.md](POSITION_EVENT_REFINEMENT.md); it is not a full
work-period relation or a nested physical trajectory.

The completed certificate checks 116 event families in seven intervals: 812
cases, each with all 154 raw outputs at nine holders, totaling 1125432 symbolic
output-word identities. The intervals contain 3154116601 possible old Ages.
Those Ages are quantified symbolically; the experiment did not execute billions
of physical transitions. A separate audit checks 21924 concrete full outputs
against independent scalar and native F.

## Clock domain and an informative failed attempt

Ordinary controller evolution is modified at resets, temporal votes, capture and
commit. Reset/vote/commit predicates use the old Age; Signal capture uses the
**updated** maintenance Age. Under canonical geometry, capture therefore acts on
the transition whose old Age is CAPTURE_AGE-1, not CAPTURE_AGE.

The first pilot excluded the wrong capture instant. Four early-clock cases
passed, then the symbolic WRITE case failed at the Signal output in the long
third-stage interval. The failed log and exact source are preserved:

- `figs/fixed_rule/small_holder_clock_events_pilot_v1.log`
- `figs/fixed_rule/small_holder_clock_events_failed_v1.py.txt`

This was a proof-domain error, not a physical-rule change. A new regression test
exhibits the actual counterexample: canonical Address 3, old Age CAPTURE_AGE-1,
zero Signals and primary Data 1 produce Signal 4 and Age CAPTURE_AGE. Scalar and
native F agree. Thus a claim that ordinary quiet dynamics preserve Signal zero
at that instant is false. The corrected pilot passed all 12 selected checks.

The final old-Age intervals, inclusive, are:

| First Age | Last Age |
|---:|---:|
| 1 | 201326591 |
| 268435457 | 469762047 |
| 536870913 | 738197503 |
| 738197505 | 1979711486 |
| 1979711488 | 2013265919 |
| 2147483649 | 2214592511 |
| 2281701377 | 3489660927 |

Their union is exactly the active clock windows minus reset, vote and actual
capture transitions. Commit is excluded by construction and lies outside these
active windows anyway. The full period also contains rest intervals; this
certificate makes no statement about them. Physical Wf outputs remain zero here
because the hypothesized Signals and old Wf fields are zero, including during the
forcing window. This does not establish behavior for arbitrary retained Signals.

## Symbolic method and FETCH coverage

`certify_small_holder_clock_events.py` imports the existing positional/scanner
state formulas into a new term algebra. It replaces only the physical Age field
with a fresh 32-bit symbolic variable restricted to an interval. The frozen
predecessor sources remain unchanged. Scanner word-disequality hypotheses are
carried across explicitly.

The additional reductions use conservative unsigned intervals. Comparisons are
resolved only when all values in the operand intervals give the same answer.
Bounds propagate through complement, addition and low-bit modular addition; when
an interval wraps, the bound broadens to the whole word range. The checker then
evaluates the unchanged complete physical descriptor and requires structural
identity with the independently specified full raw next state. No upper rule or
program interpreter is installed as a physical execution backend.

The new FETCH cases keep metadata operands a/b/d and the instruction index
symbolic. They verify truncation of a into the 32-bit ra field, loading of rb/rd,
retained controller fields, ALU selection, META's zeroed readiness value, HALT,
both clock-dependent IF_THIRD behaviors, and LOOP. Each case is checked with and
without a right-end marker. Conditions such as pc=index, phase=FETCH and the
stated kind remain explicit. These identities can be instantiated at compatible
actual ROM sites; they do not claim that arbitrary instructions can be installed
at any physical site without changing the hard-wired ROM.

The earlier 49 positional and 43 conditional scan families also pass on every
interval. The domain still requires canonical geometry, coherent procedure and
static copies, a single local head (or quiet state), zero flags/Signal/Wf and no
incoming mail. Full raw controller and all replica outputs are retained. Matching
program operations in a simplified controller alone would not pass this check.

## Verification and resources

| Check | Result | Seconds | Peak host KiB |
|---|---:|---:|---:|
| Complete symbolic certificate v2 | 812 cases passed | 172.547991 | 187972 |
| Focused tests v1 | 6 passed | 10.814 | not recorded |
| Independent scalar/native audit v1 | 21924 full outputs passed | 75.710566 | 59868 |

Tests exhaustively validate comparison reductions over small interval domains,
check modular wrap/complement bounds at machine-word edges, check the exact clock
partition and actual capture counterexample, cover every used FETCH kind in both
IF_THIRD clock branches, and reject a mutation that omits a loaded META operand.
The native audit instantiates every interval/event family at both interval
endpoints and a seeded random Age, with zero, width-limited all-ones and random
controller/Data values. It verifies every interval and disequality hypothesis
before comparing all raw outputs. These finite checks corroborate the symbolic
checker; they are not exhaustive concrete enumeration of its domains.

No GPU work was needed or launched. The largest recorded host peak was about
184 MiB, and jobs were bounded single-process CPU checks. Physical Q, U, alphabet,
radius, descriptor and ROM were unchanged.

Exact commands (logs use the corresponding stems):

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.certify_small_holder_clock_events --output figs/fixed_rule/small_holder_clock_events_v2.json
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_clock_events.py -v
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_clock_events --certificate figs/fixed_rule/small_holder_clock_events_v2.json --output figs/fixed_rule/small_holder_clock_events_audit_v1.json
```

## Next composition obligation and scientific limits

For META, the existing physical timing experiment and schedule recipe give
D=4L+d-m+1, where L is core length, m the instruction position and d the write
destination. The new local identities now cover the regular-clock FETCH,
unready/search/returned-value flights, endpoint reflections and WRITE events
needed for a general scan derivation. What remains is an explicit composition
argument showing their hypotheses hold along the entire path, including a query
at either endpoint, a zero-valued result and a miss that invokes fallback.
The actual ROM has 98 META instructions; earlier exhaustive GPU timing used seven
chosen instructions, so that measurement alone is not coverage of all 98 paths.

The same refinement must then cover ordinary instruction durations, incoming
transport and its collision/flag guards, and clock overrides. Only after joining
those results with [ROM_DATAFLOW.md](ROM_DATAFLOW.md), Signal/flag evolution and
[RESET_ENCODING.md](RESET_ENCODING.md) can an all-input period relation be claimed.
The present zero-Signal domain cannot stand in for arbitrary retained upper flags
or noisy physical configurations. No full upper period at depth two or general
cross-level error suppression has been established.

Gray pp.31–32 motivates a specialized hard-wired self-simulator after ProgramBit
projection; Gács §§9.2–9.3 permits a modified self-correcting rule and requires
actual encoded computation/update. Those source requirements remain the target,
not an arbitrary user-program platform. The user priorities remain correct fixed
self-simulation, practical two-level GPU execution and measured cross-level
repair; U<=128Q remains unnecessary. This certificate does not reduce Q or U or
authorize a host replacement of simulated transitions.

## Provenance and handoff

- Certificate SHA256: `e7684d46833a4bc6296280562cca1be0f06b7810f79d3bec6606e262f4ee199c`.
- Audit SHA256: `5f3334596dba809313f790b6926448dbbce7889e4110003ea6611848dbc52432`.
- Checker source SHA256: `e01b973c69c943372f81252af790dd4b81bba9fed5612906c989f6b23ecd33b2`.
- Physical descriptor SHA256: `af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`.

The position/scan audits' five/seven source hashes and this audit's eleven hashes
were rechecked with zero mismatches. Owned additions are the clock certificate,
its test/audit, this report and namespaced evidence; only our STATUS handoff was
updated among existing reports. No frozen/shared source or CUDA artifact changed.
All own handles are terminal. MAIN_AGENT_NOTES.md remains absent; please reply
there. The separate 8 GiB GPU reservation remains pending and was not used. A
read-only process check found no historical third-link process; absence is not a
completion audit. The full research goal remains active and incomplete.
