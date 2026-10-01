# Complete own-rule DAG: static and local timing pilot

Updated 2026-09-28. This work began after source-only checkpoint `9bfd530`.
It advances the separate `spatial_epoch` evaluator pilot from nine dependency
layers to **all 11,054 operations** of the current integrated
`stream28_holder_*` candidate's compiled complete transition description.
It does **not** integrate that evaluator into the candidate's own physical
rule or establish a self-simulating macrostep. A dependency layer is a
word-DAG layer, not a level of the simulation hierarchy.

## Source and design constraint

Gray's Reader's Guide pp. 28–29 motivates synchronized local mail streams;
pp. 30–32 permits a specialized hard-wired self-simulator after ProgramBit
projection. Its p. 34 fifth-stage window is `8Q=65,536` at `Q=8192`.
Gács §§9.2–9.3 permits identical or suitably modified self-correction.
The integrated candidate's serial late evaluator currently needs
179,678,840 ticks, so matching Gray's window requires a different
physical evaluator. The current fixed pilot has radius one, width 2,334 bits,
three *static* gate-description slots, one *dynamic* operand/result
workspace, 38 static routes/site and one moving packet lane. Its width,
neighborhood and transition never vary with selected DAG prefix.

## Static whole-DAG fit

The full own compiled DAG has 11,054 gates and 21,944 operand occurrences;
2,726 literal occurrences can be preloaded locally. Eight intermediate
values individually exceed 38 routed consumers. The new
`spatial_fanout_compiler.py` processes gates in reverse dependency order,
adds **11 equivalent computations** for those eight values, and assigns
earlier consumers to earlier copies. Their added inputs do not create a
new raw-source or gate-source overflow. An independent checker validates
every source wire, destination, gate slot and route count. The result has
11,065 gate instances and 19,237 routed operands. Every original first-eight
gate site and all 7,680 early operand source/destination sites are preserved.

All instances fit within the fixed 14,196 static gate slots, leaving 3,131
unused; every site has at most three gates and 38 routes. Three random
complete 15-neighborhood raw inputs gave **154/154 matching outputs** for
the transformed DAG, and every duplicate was checked against its logical
original. This is diagnostic transformed-graph evaluation, not evolving
physical computation. Receipt:
`figs/fixed_rule/spatial_fanout_compilation_v4.json`. Maximum process RSS
for that receipt was 431,192 KiB.

## Geometry and healthy event schedule

A route-load-only placement had an optimistic last-output bound of
120,341 ticks, already past 8Q. `explore_spatial_topology.py` reserves ten
sites for unpinned 38-route gate instances, then places remaining gates in
dependency-layer order. It preserves the audited first-eight gate sites,
obeys the fixed spatial alphabet, and its gate-dependency plus per-site
slot-order graph is acyclic with no pinned-slot depth inversion. Ignoring
mail collisions and switch/result lifetimes, its last-output lower bound
is **28,085 ticks**, a 4.28-fold improvement over route-load-only placement.
Receipt: `figs/fixed_rule/spatial_topology_v3.json`. The lower bound itself
is not a schedule.

Adding source-result lifetime and target-slot activation to a shortest-path
packet model exposed a positive timing cycle: one gate needed to release a
source site before its destination gate became active. The local rule now
lets a packet **pass through its target while the wrong gate slot is active**;
it can complete another ring circuit and be accepted when that slot opens.
This changes no state width or neighborhood. A literal local test covers
pass-through and later acceptance. A first source-serialized event candidate
finished at tick 28,122 but had 14,180 overlapping moving-phase conflicts,
so it was rejected (`figs/fixed_rule/spatial_laps_candidate_v1.json`).

`schedule_spatial_phases.py` then reserves each moving phase until packet
acceptance and delays an emission whenever its phase is occupied. It uses
the same physical alphabet and encodes the resulting 19,237 launch ticks
and 6,333 gate-switch ticks in the initial configuration. Its analytical
healthy schedule emits and delivers all 19,237 packets, completes all
11,065 gates, performs 673 target pass-throughs, and finishes the last
gate and all 154 logical outputs at **tick 28,929**. That leaves **36,607
ticks** of Gray's 8Q window. It encountered 500,587 blocked launch
attempts while selecting free moving phases. No two simultaneously live
packets share a phase, and no source emits twice in one tick. Receipt:
`figs/fixed_rule/spatial_phases_candidate_v2.json`. This earlier receipt
predates output commitment and the 4Q period reduction; its source hashes
are historical. These values are healthy-schedule measurements, not noise
or repair bounds.

`audit_spatial_full_dag.py` independently constructs the encoded cells and
an analytical trajectory, then applies the literal `spatial_epoch.local_step`
at **every packet launch and delivery endpoint**, every gate completion,
and every site switch: 55,872 local site transitions in total. It also
compares **311,296 literal site transitions** at 38 sampled complete-ring
ticks, including transport, switches, last deliveries and completion.
All fields agree with the witness and original rule DAG output values.
Mutating an encoded launch tick causes a local-step assertion failure.
Historical receipt: `figs/fixed_rule/spatial_full_dag_audit_v3.json`; its
physical-rule SHA-256 was
`7c1b659dc3189acbe2ce5ea717b6155d86e6e78d13d88dfae9a4a7ebe8ab22f4`.
Tests: `python -m unittest tests.fixed_rule.test_spatial_fanout_compiler
tests.fixed_rule.test_spatial_topology tests.fixed_rule.test_spatial_full_dag
-q` passed seven in 25.381 seconds after final route-provenance checks;
`python -m unittest tests.fixed_rule.test_spatial_epoch -q` passed six in
17.687 seconds after pass-through.
CPU only; no substantial GPU job or shared CUDA rebuild.

## Output commitment and shorter evaluator period

An output-bank inventory gave a concrete layout without widening
the 38-route table. Of the 154 outputs, 49 are raw input wires and can be
decoded directly from their encoded source sites; four of those sites have
no other routed operand use and must still be initialized. The other 105
outputs are gate values. Their 105 physical source sites are distinct and
have at most 21 existing routes each, so one extra route per gate raises
their maximum to 22. There are 2,717 memory sites unused by either routed
raw inputs or those four raw-only outputs, enough for 105 distinct output
sinks. `figs/fixed_rule/spatial_output_capacity_v1.json` records the
candidate sites. `spatial_epoch.local_step` now uses kind `OUTPUT=3` and
stores an arriving packet in its existing `source_value`/`done` registers;
the kind already fits the two-bit field. The 105 gate-output routes are
encoded in the same 38-route/site table. The 49 raw outputs decode directly
from initialized SOURCE sites, including the four with no operand route.
No field or neighborhood was added.

The complete output schedule emits and delivers **19,342 packets**, including
all 105 gate-output commits. The last output arrives at tick **32,100**.
Consequently the *isolated evaluator* work period was reduced from 8Q=65,536
to **4Q=32,768**, with 668 ticks of headroom; reducing the three age/switch
bits and 38 launch-time bits shrinks the physical alphabet from 2,375 to
**2,334 bits/cell**. This is the same fixed rule for all encoded DAG prefixes,
not a depth-dependent kernel. The new schedule has 500,816 blocked phase
attempts and 673 target pass-throughs. Receipt:
`figs/fixed_rule/spatial_phases_output_4q_v1.json`.

The first rollover probe exposed a real bug: a first-slot gate could use its
previous period's `ready` bits after resetting its operands and thereby
compute a stale result. The transition now captures readiness *after*
reset/switch but *before* packet receipt. A targeted regression would fail
without that correction. The two-period audit checks 56,082 first-period
local event endpoints and 303,104 sampled full-ring site steps, decodes all
154 output words, then checks 56,000 second-period endpoints and 24,576
complete-ring site steps, including the wrap and second output commit. The
same encoded sites and unchanged raw inputs are used in both periods. All
fields agree with the literal local rule; the second-period wrap resets all
105 output sinks and has no live mail. Receipt:
`figs/fixed_rule/spatial_output_two_period_audit_v1.json`. Its then-current
physical-rule SHA-256 was
`61e8c662402f3830128add424f7b6c43fa1523d42d46ef66950fceac16e44ed9`.
The focused 17-test run first failed only because one test asserted the old
width; after updating it, all **17 tests passed in 59.531 seconds**. The
output-bank audit itself passed in 27.041 seconds. CPU only; no GPU
scheduling or shared CUDA artifact was touched.

An independent dense NumPy executor now evolves the encoded initial cells
through **65,536 consecutive ticks**, two complete 4Q periods, without
reading the DAG or the analytical schedule inside its transition loop. It
processes 536,870,912 physical site-ticks in 17.988 seconds with peak process
RSS 431,192 KiB, below the shared-memory limit. Each packet-bank period has exactly
19,342 actual packet emissions/deliveries and 11,065 gate computations.
The second wrap returns every dynamic register and mail lane to the first
wrap state. Thirteen complete-ring states match the analytical witness;
49,152 sampled site transitions independently match the literal Python
`local_step`. All output values agree with the own-F oracle at both commit
ticks. The current-source packet-bank receipt is
`figs/fixed_rule/spatial_output_continuous_2period_v4.json`, which checks
308 output words across two periods. This closes the *continuous isolated evaluator*
replay gap, although it is an independent vectorized implementation rather
than literal Python execution of all 536,870,912 local calls.

## In-place output latch: preferred timing candidate

All 105 gate-output primary copies occupy distinct physical sites. Their
`source_value` register was unused at a GATE site, so a marked opcode can
latch the result there before later gates reuse the site's operand/result
workspace. Seven spare four-bit opcode values encode marked variants of the
seven operation kinds in this specialized evaluator. `GateSpec.wire` remains
the original logical wire and the alphabet stays **2,334 bits**. At the
period boundary the rule clears that latch and computes the next period's
first ready gates. This is one fixed transition supporting both encoded
output layouts; no depth-specific kernel is selected.

The latch layout needs **zero output packets or sink sites**. Its 19,237
operand packets and 11,065 gates finish at tick **28,929**, leaving **3,839
ticks** of the 4Q period, versus 668 for the packet bank. The event schedule
is `figs/fixed_rule/spatial_phases_latch_4q_v1.json`; the complete local
event/sampled-ring and two-period rollover audit is
`figs/fixed_rule/spatial_latch_two_period_audit_v1.json`. Removing the
encoded output marker at one gate causes a literal local-step mismatch.

The preferred variant also passed independent continuous replay of two full
periods, each with 19,237 emitted/delivered packets and 11,065 computations;
all **308 decoded output words** match the own-F oracle. It matches 13
analytical full-ring states and 49,152 literal local site transitions, and
returns to the same dynamic state at the second wrap. Its then-current
receipt is `figs/fixed_rule/spatial_latch_continuous_2period_v2.json`:
19.233 seconds, peak431,192 KiB RSS, physical-rule SHA-256
`af7b3513a776efb1efbcd30b394729b50ca3f68a5bfe8123e099f3e0bad87b77`.
`python -m unittest tests.fixed_rule.test_spatial_epoch -q` passed9 tests
in18.144 seconds; `tests.fixed_rule.test_spatial_full_dag` passed6 in
74.811 seconds; `tests.fixed_rule.test_spatial_continuous_replay` passed2
in36.182 seconds. These timings and source hash precede the later
bidirectional Hold integration; its current-source regressions are in the
linked handoff report.

For integration, the 154 results must reach the stream rule's actual Hold
cells. The later [direct Hold handoff](INTEGRATED_SPATIAL_HANDOFF.md) uses
leftward output packets and finishes at tick31,092 with1,676 ticks of 4Q
headroom. The in-place latch above remains the faster isolated-output
comparison, but its values alone do not populate Hold.

## Boundaries and next steps

The schedule is encoded entirely as initial route and switch data; no host
evaluator replaces an evolving transition. Continuous replay now supports
the healthy isolated evaluator trajectory; literal local-step equivalence
was checked on sampled full-ring transitions, not all 536,870,912 site steps.
The two evaluator periods repeat the same raw input and are **not** two
decoded upper transitions. The pilot has no integration with
Info/History/Flag/Signal or colony maintenance, no complete self-description
of its *changed* local rule, and no damaged-state repair or noise evidence.
Known printed Flag2 persistence and computed-SimBit timing fidelity
qualifications remain. The integrated stream candidate still uses Q8192/U2^28
and its serial late evaluator; this 4Q pilot does not establish an integrated
Q8192/U2^20 self-simulator. The isolated latch's 3,839-tick margin, and the
direct Hold route's 1,676-tick margin, may be too narrow once
integration overhead is included.

Next replace the serial late evaluator inside a new fixed complete physical
rule and close the self-description over its gate, route, packet, and output
fields. The direct Hold route's 1,676-tick pilot margin makes integration
timing a key risk.
Only after the new rule's own ROM and decoded complete macrostep pass can
two-level behavior and repair be evaluated.
