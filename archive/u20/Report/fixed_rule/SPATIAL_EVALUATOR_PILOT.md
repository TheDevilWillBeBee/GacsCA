# Spatial evaluator pilot for the fixed-rule candidate

Updated 2026-09-28. The later full-DAG result is documented in
[FULL_SPATIAL_DAG_SCHEDULE.md](FULL_SPATIAL_DAG_SCHEDULE.md). This is an isolated physical-rule experiment, **not** a
replacement for the integrated `stream28_holder_*` simulator. Its measured
advance is a local route and gate-reuse schedule for the first nine dependency
layers of that candidate's own compiled transition description. Here *dependency
layer* means a layer of the Boolean/word DAG; it is not a level of the
Gács/Gray simulation hierarchy.

## Why this experiment

Gray's Reader's Guide, pp. 28–32, describes concurrent mailbox movement,
short copying/comparison procedures, hard-wiring of ProgramBit, and the
specialized self-simulator obtained after projection. On p. 34 its fifth
stage has `8Q` time units; at `Q=8192` that is 65,536 ticks. Gács §§9.2–9.3
permits simulating the same or a suitably modified self-correcting rule.
The current integrated fixed candidate instead uses 179,678,840 ticks for
its serial late evaluator. Its complete own compiled description has 11,054
operations, 21,944 operand edges and critical dependency depth 73. These
facts motivate a placed parallel evaluator, but do not imply one exists.

## Executable local slice

`gacsca/fixed_rule/spatial_layer1.py` defines one finite-state radius-one
local transition `local_step`. Its cell width is **1,630 bits**, independent
of the selected DAG prefix; `Q=8192`, `Age` period 65,536, 38 immutable
encoded output-route slots per cell, one moving 64-bit packet lane, and a
word ALU gate are fixed. A host compiler places a prefix of the *actual*
`stream28_holder_program.compiled_description()` as initial gate, opcode,
literal and route data. The compiler and the diagnostic expected-value
evaluator do not perform any evolving transition. Each physical tick reads
only the left, center and right cells. Gate results can themselves become
packet sources, so successive dependency layers execute by the same rule.
Literal-operand gates are initialized with their constant value locally.

For a packet emitted at site `s` at tick `l`, its site at tick `t` is
`s+t-l (mod Q)`. Thus its phase `s-l (mod Q)` remains invariant. Assigning
each simultaneously possible trajectory a unique phase guarantees that
moving packets cannot share a site and tick. The old `ordinal` policy
reserved phases in edge order. The new `earliest` policy picks the first
unused phase after the source gate becomes ready. **Only encoded route
launch times change; the transition function and alphabet stay identical.**

`experiments/fixed_rule/measure_spatial_layer1.py` builds an analytical
packet/gate trajectory as an independent witness. At selected ticks it
applies the literal local transition to **all 8,192 cells**, comparing every
cell field with the next witness state. It also checks the final value of
every placed gate against the compiled DAG oracle. This is a sampled
full-ring step audit, not a continuous physical replay of every tick.

| DAG prefix | Gates | Packet edges | Earliest completion | Ordinal completion |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 1,020 | 1,876 | 4,414 | 11,610 |
| 2 | 1,794 | 3,088 | 5,504 | 19,767 |
| 3 | 2,493 | 4,178 | 7,011 | 27,944 |
| 4 | 3,124 | 5,209 | 8,673 | 36,051 |
| 5 | 3,522 | 5,869 | 9,731 | 44,370 |
| 6 | 3,831 | 6,377 | 10,548 | 52,557 |
| 7 | 4,294 | 7,031 | 11,664 | 60,745 |
| 8 | 4,653 | 7,680 | **12,672** | misses 65,536 |

The eighth prefix uses 1,462 locally preloaded constant operands, 4,394
source sites, and at most 30 of the 38 encoded routes at any source. It
finishes 52,864 ticks before Gray's fifth-stage deadline, *for this prefix
alone*. The final source-hashed receipt is
`figs/fixed_rule/spatial_layer8_earliest_v2.json`; it checks all 4,653
placed gate outputs and 212,992 literal site transitions across 26 sampled
whole-ring steps. The source description digest is
`ee57d794f4d97875dd7740915079dc70c3e40a3fd88e212c0f4dd225d5257fbc`.
`python -m unittest tests.fixed_rule.test_spatial_layer1 -v` passed all
five tests in 26.255 seconds. Tests require actual encoded emission,
transport, reception and gate evaluation, fixed radius/width/rule identity
for different prefixes, all eight-prefix outputs, and the failure of the
ordinal eight-prefix schedule.

## Capacity boundary and next design

The ninth prefix has 5,024 gates and 8,205 packet edges. With the existing
3,455-site memory bank and five tail sites, only 4,732 distinct gate sites
are available. The current one-gate-per-site, one-use-per-phase layout
therefore needs **at least 292 gate-site reuses and 13 packet-phase reuses**
before it can even place prefix nine. Across all 73 dependency layers,
11,054 gates and 21,944 operand edges make reuse unavoidable. The immediate
next experiment should implement encoded sequential gate instructions on
selected sites, with a local reset after the first result has launched to
all consumers. Packet phases may be reused after the preceding packet has
arrived. Later waves must reuse the same finite hardware.

`experiments/fixed_rule/explore_spatial_reuse.py` gives an *analytical*
two-epoch certificate for layer nine. The 79 still-free sites receive one
gate each, and 292 earlier sites receive a second gate. All first-epoch
packets finish by tick 12,672. At tick 16,384, the second gate could replace
the first at reused sites: all 525 new operands launch between ticks 12,673
and 15,990 while the old result still exists, and all operands addressed to
reused sites arrive at or after the reset. The 525 second-epoch packet
phases are pairwise distinct; first-epoch phases can be reused because their
packets have already arrived. The maximum source has 30 routes, below the
fixed 38-slot limit. The last ninth-layer result would be ready at tick
**20,137**, inside 8Q. Receipt:
`figs/fixed_rule/spatial_reuse_ninth_v2.json`.

`gacsca/fixed_rule/spatial_epoch.py` implements that reset in **one new,
fixed** radius-one physical rule. Its width is 2,375 bits for both the
eight- and nine-layer initial configurations. Each site has three *static*
encoded gate descriptions and two encoded switch times, but only **one
dynamic operand pair and one result register**; the local transition resets
those dynamic fields when advancing a gate slot. Packet and route fields
identify the destination gate slot, and routes identify which active source
slot supplies their value. The ninth layer exercises one switch; the third
static slot is present in the same finite alphabet but is not yet used by
the tested schedule. At the end of its fixed 65,536-tick evaluator window,
the same local rule resets to the first gate description. No host transition
selects the gate or alters state after initialization.

`experiments/fixed_rule/measure_spatial_epoch.py` verifies both prefixes
with this *same* rule. The eight-layer configuration checks all 4,653 first
epoch outputs and 131,072 literal local site transitions at sampled
whole-ring steps. The nine-layer configuration checks those first outputs
before reset, then all 371 ninth-layer outputs at the end, plus **245,760**
literal site transitions across 30 sampled whole-ring steps. Both agree
field-for-field with the independent trajectory witness; the latter checks
packet launches, flights, arrivals and the reset boundary. Final receipts
are `figs/fixed_rule/spatial_epoch_eight_v3.json` and
`figs/fixed_rule/spatial_epoch_ninth_v5.json` after the later packet
pass-through refinement.
`python -m unittest tests.fixed_rule.test_spatial_epoch -v` passed five
tests in 18.751 seconds. The tests cover the same rule identity/width across
encoded prefixes, actual switching and second-result emission with one
operand workspace, receipt on the switch tick, window wrap reset, and
nine-layer dynamics.

This physical audit still samples complete-ring ticks rather than evolving
every tick consecutively. The switch rule is an isolated optimization pilot;
it has not been included in a new description of the integrated complete
transition or in its self-evaluated ROM.

The full DAG has a second, independent capacity obstruction. Across all
11,054 gates, it has 19,218 routed operand uses and 2,726 operands that can
be preloaded from local literal descriptions. Eight intermediate gate values
each have more than 38 nonliteral consumers; their fanouts are 92, 90, 85,
61, 47, 45, 45 and 40. Thus the current fixed 38-route table cannot encode
the complete DAG by merely reassigning gate sites. A **lower bound** is 11
additional copies of those computations, splitting each value's consumers
across copies; this is tiny against the 3,142 unused static gate slots, but
duplicating a gate adds operand demand to its own sources and may trigger
further duplication. `python -m experiments.fixed_rule.measure_spatial_full_fanout
--output figs/fixed_rule/spatial_full_fanout_v1.json` records this inventory.
No complete placement or routing certificate follows from the count.

The later [complete-DAG report](FULL_SPATIAL_DAG_SCHEDULE.md) records the
resolved fanout, placement and phase scheduling, physical output commitment,
and a 2,334-bit, 4Q successor pilot. The older 2,375-bit measurements above
are historical. The successor is still separate from the integrated
`stream28_holder_*` rule; no complete self-description, integrated macrostep,
or repair/noise result follows from this prefix experiment.
