# Parallel local gather prototype

The subsequent integrated fixed-rule candidate is documented in
[STREAM28_INTEGRATION.md](STREAM28_INTEGRATION.md). The limitations below
describe the isolated prototype at the time it was measured.

2026-09-28. This work follows the source-only Git checkpoint `1ea6239`.
The new `gacsca/fixed_rule/stream_gather.py` is an isolated fixed-width,
radius-one local CA component for the current Q8192 rule's 689 required
gathered words. It is **not yet part of** `packed28_holder_*`, and therefore
does not establish a faster self-simulator. Its purpose is to test whether
Gray's stream-based communication can replace the current serial head's
12-million-tick gather within the 16Q=131072 active-stage budget.

Gray, pp. 28–29 in `papers_txt/gray_readers_guide.txt`, moves simultaneous
SimBit streams in a local Mailbox and copies them into designated Workspace
sites. This prototype applies the same locality principle to the 154-word
raw state of the current fixed rule, while preserving the actual sparse set
of 689 required inputs rather than gathering all 2310 neighbor/field pairs.
The schedule is specialized to the current rule family, consistent with
Gray's hard-wired ProgramBit projection on pp. 31–32 and Gács's similar or
modified self-simulation in §9.2. It has no arbitrary user-program support.

## Fixed physical mechanism and collision argument

Each physical site stores a fixed 363-bit state: Address13, Age19, an
Info-field index8 and 15-bit emission mask, a 12-bit acceptance wire and
two-bit acceptance stage, source and received 64-bit words, one validity
bit, two 82-bit moving packets, and a collision bit. A packet contains
validity, 12-bit wire id, three-bit remaining colony hops, two-bit stage,
and a 64-bit payload. Those widths, the radius-one neighborhood, and the
`local_step` implementation do not vary with depth. Initial data put the
source values at the existing Info addresses, an emission mask at each
source, and `(wire,stage)` acceptance tags at three distinct history sites
per required input. The local transition alone launches, moves, receives
and stores packet values; no host transition inserts packets afterward.

For a required input with neighbor offset `j` and field `k`, the immutable
wire id is `w=(j+7)*154+k`, so `0<=w<2310<Q`. A source at Address `a` sends
right when `j<0`, otherwise left (local `j=0` targets lie left of Info).
Its new-state launch tick is

```
right: 1 + ((a-w) mod Q)
left:  1 + ((w-a) mod Q)
```

For a right-moving packet, `position-time mod Q` equals `w-1`; for a
left-moving packet, `position+time mod Q` equals `w+1`. Distinct wire ids
therefore occupy distinct trajectories in each directed lane, even across
colonies. Packets in opposite directions have separate lanes. At a colony
boundary a packet decrements its three-bit hop count. Once it reaches the
destination colony, the static acceptance tag at its history site consumes
it. Each destination site accepts one `(wire,stage)`; the three histories
remain independent. The local rule defines a collision bit for malformed
or overlapping states, so the rule remains total outside the certified
healthy trajectory, but this bit is not an error-correction scheme.

The exact schedule covers 97 local and 592 nonlocal input words per colony,
with at most 15 emissions from any Info site over a stage. The two directed
lanes have 293 and 396 distinct trajectory phases. All 689 stage words
arrive by tick **65096**, which is just below 8Q=65536 and well within
Gray's active gather budget 16Q=131072. The three stages together route
2067 words per colony; on a 15-colony ring they produce 31005 received
history words. This is a communication schedule only: it does not include
vote, computation, signal, repair, or the new rule's own description cost.

## Executed checks

`python -m experiments.fixed_rule.measure_stream_gather --output
figs/fixed_rule/stream_gather_schedule_v1.json` passed in 31.77 seconds.
It checked all 2067 `(stage,wire)` schedules, uniqueness of directed
trajectories, acceptance locations, and deadlines. It also advanced 30
representative packet paths, covering local transport and both directions
at every hop count 1–7 in stages 0 and 2, one physical radius-one local
step per travelled site. Every packet was emitted from encoded static data
and delivered with its original 64-bit value.

`experiments/fixed_rule/audit_stream_gather_concurrent.py` reconstructs the
entire concurrent packet state as an analytical witness. At selected ticks
it applies `local_step` literally to *every site* of a 15-colony ring and
checks the complete next state, including packets, history, age, static
fields, and collision status. The final receipt is under
`figs/fixed_rule/stream_gather_concurrent_v3.json`. It covers launch,
crowded flight, last delivery, and all three stage boundaries. It also
checks each of the 31005 final raw history words against the corresponding
source colony's complete raw field. The 17 sampled full-ring steps covered
2088960 literal physical site transitions in 59.12 seconds, with no
collision or mismatch. `python -m unittest -q
tests.fixed_rule.test_stream_gather` passed seven tests in 18.112 seconds,
including local radius/width rejection, boundary-hop semantics, encoded
launches, representative paths, concurrent stage-boundary steps, and
static-ROM metadata encoding.

The analytical witness is not a literal replay of every quiet and moving
tick. The collision-phase argument covers all packets on canonical
geometry; sampled whole-ring local steps test the implementation against
that argument. This establishes a strong feasibility slice, not repair
under faulty geometry or arbitrary packet faults.

## Integration experiment needed next

The source and acceptance metadata are presently encoded data in the
prototype. To make this a faster fixed-rule self-simulator, a successor to
`packed28_holder_*` must use the existing MEM Info/History banks and
left/right mail fields for streams, replace its 691-virtual-instruction
head gather, and describe the new emission/acceptance logic in its own
complete physical F. Candidate static storage is the unused static ROM
fields at Info and History MEM sites: a 15-bit emission mask at an Info site
and a `(wire,stage)` acceptance tag at a History site. The executable
initializer-only `stream_gather_overlay.py` verifies that 154 source masks
and 2067 acceptance tags fit existing `b` and `d` static fields; the ROM
still has 7597 rows and the physical field widths are unchanged. It also
round-trips a moving packet through each existing target/data/remaining/valid
mail register, inferring its stage from Age and rejecting moving mail outside
a gather stage. The separate prototype's collision bit would need a
deterministic priority or fault representation in the integrated rule. The
overlay is **not** a valid own-ROM for the unmodified packed rule, because
the new stream transition has not been described or compiled into that rule.
The projected upper
state must include any genuinely dynamic new fields; Address-determined
static data can be regenerated. The changed F may require different raw
neighbor inputs, so the set of 689 and the 65096-tick schedule must be
recompiled and retested to a fixed point. Physical flag clearing, Signal
capture, voted histories, and two consecutive decoded upper periods remain
acceptance tests. No claim of U=2^20 follows until those checks pass.
