# Testing Gray's printed construction at Q = 8192

2026-10-09. This is the requested independent counterexample-search
checkpoint. G17, CURRENT, the active compiler and manifest are unchanged.
All new rule/compiler adaptations are isolated under
[`proofs/gray_counterexamples/`](proofs/gray_counterexamples/), and receipts
are under [`figs/gray_counterexamples/`](../figs/gray_counterexamples/).
There are no commits.

**Finding: Gray's printed Flag2 erasure clause contradicts the Flags part
of his printed Proposition 2.** A single legal level-0 overwrite suffices;
the contradiction is proved, rather than inferred from a noisy simulation.
It does not show that the intended corrected Gray rule, Gács's 2001 rule,
or the Address-memory theorem is wrong. A separate Gray-scale experimental
completion, GR0, now has a universally verified own abstract programme,
but its simulation protocol has explicit departures from Gray's.

A separate [conditional stage theorem](proofs/gray_counterexamples/GRAY_LITERAL_STAGE_ENVELOPE.md)
finds that faithful raw-state gathering and retained Workspace records
are incompatible with Proposition4's literal pointwise two-colony
envelope. This theorem uses Gray's stated native/majority equations and
no GR1 implementation. The actual Gray gathering, retention and
programme/layout refinement remain unverified; it is not a fully
specified Gray-rule or decoded-memory counterexample.

The new [GT0 component proof](proofs/gray_counterexamples/GT0_RAW_GATHER.md)
implements the raw gathering and record retention used by that conditional
argument. Its emitted transitions and exact first-56Q coupling supply
those semantics for this concrete component under the printed-native
control premise. It has explicit unimplemented programme/control ports;
it is not a complete faithful Gray automaton. Its late SimBit equation
also exposes a [radius integration obstruction](proofs/gray_counterexamples/GT0_RADIUS_INTEGRATION.md)
when combined literally with Gray's computed-SimBit Workspace read.

The original PDF actually prints the disputed predicate. It is visible in
the retained [page 21 image](../figs/gray_counterexamples/Gray_page21.png),
and appears in the [extracted text, lines 948–952](../papers_txt/gray_readers_guide.txt#L948).
The relevant short quotation is: “no site in L(x) ∩ C(x) has Flag2 equal
to 0”. This is not an OCR substitution.

Gray assumes Q ≥ 2¹³ and U = 128Q on page 15, at
[lines 650 and 653](../papers_txt/gray_readers_guide.txt#L650).
Thus 8192 is his minimum stated colony scale for the local-structure
discussion. It is not an explicit sufficient-size certificate for the
entire programme. Pages 31–32 also require Q to be sufficiently large
for a description of length a + b log₂(QU), with unspecified a,b
([lines 1401–1410](../papers_txt/gray_readers_guide.txt#L1401)). Page 34 gives
an update-stage time bound 3Q + a log₂ Q + b, again with unspecified
constants, to fit into 8Q. Q = 8192 does not by itself verify those bounds.
The error-class constants used here are the original λ = 24 and c = 104,
as defined on pages 16–17, not the repository's smaller c = 16.

The exact proposition under test is the **Flags assertion of Proposition 2**,
page 26, [lines 1174–1181](../papers_txt/gray_readers_guide.txt#L1174).
It allows disagreement outside E0 only inside boxes associated with real
level-1 errors; for Flags those boxes last U ticks. In particular, if E
consists of one isolated level-0 error and no real level-1 error, all Flags
must agree with the deterministic reference at every point outside E0.
The immediate-correction discussion on page 22 makes the same prediction.

**Proved two-tick counterexample from the stated initialization.**
Take the lattice Z, Q = 8192, U = 1,048,576, and any of Gray's intact
initial hierarchical configurations: Address(x) = x mod Q, Age(x) = 0,
Flag1 = Flag2 = 0, and Workspace.Flag1 = Workspace.Flag2 = 0. The initial
SimBits may be whatever that hierarchy requires. There are no boundaries
or driven halos. At the first transition, overwrite only Flag2 at
x₀ = 4096 to 1, retaining the computed values of every other bit. In the
usual convention where error times label the resulting state, the entire
error set is E = {(4096,1)}. There are no further errors.

This singleton is a real level-0 error: its isolation condition is vacuous.
Consequently E0 = E. No candidate or real level-1 error remains in E minus
E0. The value c = 104 is retained and is irrelevant to this singleton's
classification. The exact classifier result is retained in the
[native certificate](../figs/gray_counterexamples/printed_flag2_certificate.json).

At time 1, every Address is still canonical and every Age is 1. All Flag1
bits are 0. The Workspace flags are 0: their initial values were 0 and
Gray's page 41 rules only permit a 1 during the computed-Age interval
[3U/4, 3U/4 + 2Q). Computed Age 1 is outside it, independently of every
SimBit, Mailbox, Workspace and programme detail. Only Flag2(x₀) differs
from the reference.

For the next transition C(x) is the true colony at every site. Both
directional Address and Age votes are correct. There is no inconsistency,
no Flag1 wave and no Workspace source, so computed Flag1 stays 0. At x₀
the five sites in L(x₀) ∩ C(x₀) all have Flag2 = 0. Thus printed Flag2
erasure condition (a) is **false**. Condition (b) is false because computed
Flag1 is 0. Conditions (iii) and (iv) provide no source: C(x₀) exists and
Workspace.Flag2 is zero. Flag2(x₀) therefore remains 1. At every other
site no birth condition holds, since one Flag2 = 1 supplies fewer than
four required left supporters. All Address/Age values remain correct.

The noiseless reference has Flag2(x₀,2) = 0, whereas the perturbed trajectory
has Flag2(x₀,2) = 1. The point (4096,2) is outside E0, and there are no
real level-1 boxes. This contradicts the printed Flags assertion. The
argument needs the Workspace-zero fact only at time 1, which follows
from Gray's stated initialization and his published Workspace rule. It
does not assume an unexplained all-time Workspace-zero trajectory.

Existence of an intact initial hierarchy is a premise of Gray's construction,
not an extra hostile seed. For the isolated GR0 alphabet, the corresponding
static initialization is also available: the ordinary encoding fixes
physical structure, sets work fields to zero and stores arbitrary upper
bits in five copies at the layout's distinct primary cells. Its iterated
images are nested, nonempty compact subsets of the configuration space;
their intersection supplies an infinite initial hierarchy. This static
compactness argument does not certify GR0's continuing simulation dynamics.
The two-tick native argument holds for every configuration in that
intersection, regardless of its recursively specified SimBits.

There is a stronger **conditional native invariant**: if Workspace flags
remain zero at all later times, the single Flag2 = 1 persists forever and
all Address/Age values remain correct. The same local calculation proves
it by induction. That stronger invariant has an explicit all-time
Workspace-zero premise; it is not used to strengthen the two-tick
counterexample or to infer iid unreliability.

[`check_printed_flag2.py`](proofs/gray_counterexamples/check_printed_flag2.py)
checks 22 singleton cofactors, leaving the 20-bit common clock symbolic.
The certificate therefore covers every one of the 2²⁰ common clocks.
It also checks 36 adjacent-pair cofactors and retains 1000 randomly chosen
scalar-versus-circuit comparisons. Those 1000 comparisons are **measured
only**, with seed and actual inputs/outputs in
[the NPZ receipt](../figs/gray_counterexamples/printed_flag2_scalar_inputs.npz);
they are not the proof. The symbolic cofactors and the preceding induction
are the proof. The isolated literal maintenance circuit has 2919 gates.

The repository's candidate-B clause already differs from the printed one:
with computed Flag1 = 0 it erases when there are at most one left in-colony
Flag2 = 1. It corrects the singleton in one update. It must be labeled as
a changed predicate, not silently treated as the literal quotation.
The apparent single-token repair, replacing the printed final 0 with 1,
would erase only when there are **zero** left ones. It corrects the
singleton but fails for an adjacent E0 pair at sites 4096 and 4097: the
right member has one left supporter and remains 1 at time 2. Within the
specified healthy erasure family “left in-colony ones ≤ h,” **h = 1 is
the minimum threshold** for one-tick correction of arbitrary adjacent
pairs. The [same certificate](../figs/gray_counterexamples/printed_flag2_certificate.json)
proves these three pair restrictions. This is a local minimum within that
predicate family, not a globally sufficient reliability repair, nor a
claim about Gray's intended correction.

GR0 is the separately constructed experimental rule in
[`gray_scale_rule.py`](proofs/gray_counterexamples/gray_scale_rule.py).
It uses the literal printed native predicate, Q = 8192, U = 128Q, radius
5 and 266 bits per cell. Its complete Boolean net has 17,881 gates.
Its own instruction table is retained in
[GR0_program.npz](../figs/gray_counterexamples/GR0_program.npz), with candidate
SHA256 `21476b814d910bbfd1744da49bf102110441117a891521047a34ed3c053e2446`.

The [build receipt](../figs/gray_counterexamples/GR0_program_build.json)
and [universal schedule certificate](../figs/gray_counterexamples/GR0_symbolic_schedule.json)
record 24,014 instructions, 23 exact fetch-key identities, two early-flag
identities and all 266 final-output identities. They also verify 2,048,000
front-visit coordinates, 30 gather coordinates, exact ROM packing and a
minimum scratch read delay of five ticks. Programme usage is NPe = 11,
MP = 85 and NP = 97 within the chosen 20/85/100 limits. The abstract
programme is **proved for every input**, assuming correct physical gathers,
register transport, scratch retention and instruction fetching. The 64
random replay vectors are supplementary measurements.

The compiler has two explicitly isolated adaptations: the already audited
repeated-XOR workaround, and permission for deliberate idle pages before
a late fixed match pass. The latter changes only the compiler's stall
diagnostic, not emitted instruction semantics. Two preliminary diagnostic
failures, with partial listings and exact builder sources, remain in
[GR0_initial_stall_program_build.json](../figs/gray_counterexamples/GR0_initial_stall_program_build.json)
and [GR0_wait_boundary_stall_program_build.json](../figs/gray_counterexamples/GR0_wait_boundary_stall_program_build.json).
The successful listing is universally checked independently. Power-of-two
Q and the fully padded ROM make every raw Address/selector lookup in GR0
in range; this does not repair G17's separate executable defect.

GR0's simulation protocol is **not Gray verbatim**. It has the repository's
five-front evaluator, streaming gathers at 0/32Q/64Q, two retained
histories with the third stream voted into one, early evaluation from 70Q,
special flag copies at 80Q and a pulse at 96Q. Its packed sweep has length
4096, with working cells 2058–6133. Register transport and mail movement
continue through Gray's published rest intervals, and its stage wipes
are the repository's equations. Those differences prevent importing
Gray's Proposition 4 or 5 solely from the matching constants.
The Workspace equations also test the selected current Age and corrected
current Info, whereas Gray's page 41 text specifies computed Age and
computed SimBit. The special copy at selected Age 80Q is likewise a
boundary timing adaptation. These distinctions are irrelevant to the
two-tick witness, whose Workspace interval is inactive, but are material
to later faithfulness and recovery tests.
Reducing U has not been attempted: an own-ROM fit would also need new
timing, recovery and schedule arguments. No GPU campaign was needed for
the preceding printed-clause checkpoint. The following separate campaign
tests the explicitly corrected native subsystem.

The full GR0 local restriction is separately **proved** by
[`check_gray_scale_flag2_cofactor.py`](proofs/gray_counterexamples/check_gray_scale_flag2_cofactor.py):
under canonical/common geometry and zero input Flag1/Workspace flags,
the singleton mutation changes only its own Flag2 output. All simulation
inputs and the external instruction are shared free variables. The
[receipt](../figs/gray_counterexamples/GR0_flag2_cofactor_certificate.json)
records 3189 exact full-output and lookup equalities. It does not certify
an all-time noisy hierarchy or replace the published two-tick proof.

**Corrected-native follow-up: no substantive counterexample obtained.**
The next target was the Address/Age assertion of Proposition 2, rather
than the printed Flag2 contradiction: from the same intact initialization,
level-1 noise must leave all geometry damage outside E0 within two adjacent
true colonies and a time interval of length U/32 = 32768. The preceding
discussion on pages 24–26 places recovery within that interval after the
first error in the burst. The relevant error-value family, initialization,
clock restriction and finite-boundary justification were fixed before
running the campaigns.

[`corrected_native_rule.py`](proofs/gray_counterexamples/corrected_native_rule.py)
contains only the 37 native bits: Address, Age, Flag1, Flag2 and the two
Workspace flags. Its maintenance equations use the repository's candidate-B
healthy Flag2 erasure threshold h = 1. This is the explicit local rule
change already discussed; it is not attributed to Gray's literal printed
rule or claimed to be his unique intended repair. All other native equations
are the transcription of pages 20–22. Q = 8192, U = 1048576, radius 5,
λ = 24 and c = 104 are retained. The test object has no own programme or
simulated alphabet: the padded dummy ROM exists only to execute the native
operator through the available backends. GR0 was not used for these tests.

The native restriction has a **proved bounded-clock coupling**, not an
assumption that the Workspace flags happen to stay zero. Let
M = 5U/8 = 655360, permit each error to write any native values with
Age ≤ M, and put H = 1 + U/32 = 32769. Initially every Age is zero.
A directional whole-word majority either selects one of its five input
words or falls back to the current cell's word. The vote direction then
selects one whole Age word, and the rule increments it by one modulo U.
Consequently, by induction, every raw Age at time t ≤ H is at most M+t;
every intermediate selected/computed Age satisfies the same bound. There
is no wrap in this interval, and

```
M + H = 688129 < 3U/4 = 786432       (slack 98303).
```

Gray's page 41 Workspace equations therefore output zero throughout this
interval, irrespective of Address, SimBit, Mailbox, programme results or
other simulation fields. Errors may directly overwrite Workspace flags;
those input values are retained and processed, and their next computed
outputs are zero. Thus the native test trajectory is exactly the native
restriction of **any full completion with these corrected maintenance
equations, Gray's published computed-Age Workspace gating, and the stated
initial native fields**, for this error family and horizon. This does not
certify that GR0 has that full completion or that Gray's physical programme
has been compiled. It identifies a family in which a native counterexample
could refute the full corrected maintenance claim without needing a
programme-faithfulness premise.

There is also a **proved noiseless geometry invariant**, checked in
[`check_native_geometry_invariant.py`](proofs/gray_counterexamples/check_native_geometry_invariant.py)
and the [8192-phase certificate](../figs/gray_counterexamples/native_geometry_invariant_certificate.json).
For canonical Address and a common arbitrary 20-bit Age, both directional
votes give the same correct geometry. The next Address is canonical and
the next Age is the common Age plus one modulo U, for all 44 independent
Flag1/Flag2/Workspace flag input bits in the eleven-cell neighbourhood.
Exact netlist cofactors verify every Address phase. No Workspace-zero
premise is needed. Once a campaign has no remaining geometry disagreement
and ceases errors, this invariant allows its geometry test to stop; flags
and later Workspace pulses cannot reintroduce geometry damage by themselves.
It does not prove recovery from arbitrary error patterns.

The [backend receipt](../figs/gray_counterexamples/corrected_native_operator_certificate.json)
records 16 complete NumPy/C/CUDA updates, with actual input and output
states retained in [an NPZ asset](../figs/gray_counterexamples/corrected_native_operator_inputs.npz).
Two random rings, an all-zero ring and an all-one ring are checked for four
updates. This is finite backend validation, **measured only**. An initial
driver mistake passed packed words to a C API that expects Boolean cells;
its exact checker, inputs and explanation remain in
[the failure receipt](../figs/gray_counterexamples/corrected_native_initial_C_api_failure.json).
It was corrected in the driver and was not a backend or Gray counterexample.

The first recovery campaign used **32 legal single real1 bursts**: eight
value patterns at four placements relative to colony boundaries. The
patterns include coherent ±1 and half-colony Address shifts, a false colony
origin, incompatible colours, checkerboard geometry, flat Addresses with
ramping clocks, and random native words. All error Ages obey M. Each error
set consists of the 104×104 dense core

```
[b,b+104) × [24,128), plus (b−23,1) and (b+126,150).
```

Its extent is 150×150 and it has 10818 points. None is E0: every core
point has several other linked core points outside any one adjacent-site,
same-tick pair, and neither satellite can form such a pair with its linked
core neighbour, which is at a different tick. Every minimal level-1
candidate meets the core, because the two satellites are not (24,24)-linked.
Any two such candidates are (104,104)-linked through their core points.
Conditions (i)–(iii) hold, and (iv) is vacuous. The exact classifier receipts
agree. In particular these are not arbitrary 200×200 dense boxes, which
would fail Gray's condition (iii).

All rings start with pristine native fields, not a pre-damaged island.
The four b placements are −52, 1, 4044 and 8088 relative to the midpoint
colony. A periodic ring has 48Q = 393216 sites. The initial error set's
minimum edge margin is 188393, greater than the radius-5 dependency bound
5H = 163845. Q divides the ring length. Thus no error-dependent cone
reaches a periodic boundary during the full recovery horizon; the native
trajectory in the affected region represents the infinite pristine
initialization. Simulation fields outside the ring are immaterial to the
bounded-clock restriction.

[`check_corrected_native_real1.py`](proofs/gray_counterexamples/check_corrected_native_real1.py),
[its receipt](../figs/gray_counterexamples/corrected_native_real1_certificate.json),
[exact replacement inputs](../figs/gray_counterexamples/corrected_native_real1_inputs.npz)
and [per-tick observations](../figs/gray_counterexamples/corrected_native_real1_tracking.npz)
record **no counterexample**. All 32 geometries are correct at the measured
stop time 3072; the latest observed computed geometry disagreement is at
2908. For each case, the union of all observed geometry disagreements,
including raw real1 overwrites, fits one fixed pair of adjacent true
colonies; the pair does not change with the tick. A moving narrow island can visit much
of a colony before disappearing: the union of visited sites is not an
instantaneous island width. The campaign took about 26 seconds on the
RTX 4090. These trajectories are **measured only**, not a universal
deterministic recovery proof or a noisy hierarchy experiment.

The second campaign replayed twenty of those bursts and added **110 E0
pair events per case**, at resulting-state times 175,200,…,2900. Each
event overwrites two spatially adjacent sites at one tick. Pairs are
placed adaptively just outside left/right geometry fronts or at the
Flag1 fronts, with arbitrary retained native replacements designed to
extend damage or delay Flag1. Pair times differ by 25, and the first
event is 25 ticks after the last burst point. Hence all pair events are
(24,24)-separated from each other and from the burst. Exact classification
of the full error set gives precisely those 220 E0 points; the burst remains
real1 under c = 104 because E0 is subtracted before condition (iv).
The checker also verifies that every newly introduced error's dependency
cone remains away from the ring boundary through H.

The numerical observer excludes the fresh E0 sites at their exact ticks.
It first uses a deterministic GPU zero overwrite and that same mask, then
replaces those same two sites with the retained custom values on the host;
the resulting state has one arbitrary replacement on the stated location
set. The intermediate zero value is never used in another transition.
The [observer validation](../figs/gray_counterexamples/native_observer_mask_certificate.json),
implemented in [`check_native_observer_masks.py`](proofs/gray_counterexamples/check_native_observer_masks.py),
compares 28 complete NumPy/CUDA updates at six pair positions, including
packed-word boundaries. Requested error masks, cumulative geometry
footprints and first/last differing ticks all agree with independent NumPy
calculations; its [actual states and replacements](../figs/gray_counterexamples/native_observer_mask_inputs.npz)
are retained. This is finite numerical validation, not universal backend
equivalence.

[`check_corrected_native_mixed.py`](proofs/gray_counterexamples/check_corrected_native_mixed.py),
[its receipt](../figs/gray_counterexamples/corrected_native_mixed_certificate.json),
[exact errors and values](../figs/gray_counterexamples/corrected_native_mixed_inputs.npz),
[adaptive decisions](../figs/gray_counterexamples/corrected_native_mixed_choices.json)
and [per-tick observations](../figs/gray_counterexamples/corrected_native_mixed_tracking.npz)
again record **no counterexample**. Every geometry is correct at the clean
stop time 2924; the latest observed geometry disagreement outside E0 is
2908, and for each case the union of all observed geometry damage outside
E0 fits one fixed pair of adjacent true colonies. The receipt's `colonies`
indices describe that complete spatial union, not per-tick pairs.
Errors then cease. The campaign took about 22 seconds. A first receipt
serialization failure, after transitions had completed, is preserved with
all completed assets in
[its failure receipt](../figs/gray_counterexamples/corrected_native_mixed_initial_serialization_failure.json);
the identical campaign was rerun after converting classifier coordinates
to Python integers. This was a receipt-driver failure, not a native-rule
failure.

Neither campaign proves Gray's proposed transient-speed bounds or the
universal U/32 recovery lemma. They cover bounded error clocks and these
finite value/location patterns. Reaching the Workspace pulse, allowing
unrestricted error clocks, or attacking simulation recovery and higher
levels needs a faithful physical completion and new hypotheses. GR0's
listed departures remain; no such full-rule refinement is claimed here.

**Physical-refinement checkpoint: a conditional computed-SimBit radius
obstruction.** The primary text requires more than matching constants.
[`gray_protocol_spec.py`](proofs/gray_counterexamples/gray_protocol_spec.py)
records sixteen separate obligations, with the exact stage arithmetic in
[its checklist receipt](../figs/gray_counterexamples/gray_protocol_refinement_checklist.json).
The active intervals are [0,16Q), [32Q,48Q), [64Q,80Q), [96Q,104Q) and
[112Q,120Q); the intervening intervals are rest. The first three gathers
must occupy separate Workspace storage. Full temporal majority, computation
and output distribution belong to the fifth active interval. Stage-start
resets preserve only necessary earlier gathered data. Early upper Flags
must reach the unrepresented SimBits at 3 and Q−3 before 80Q. The two
native wipe rules and the [96Q,98Q) Workspace pulse also apply.

| Checklist obligation | Primary pages | Current refinement status |
|---|---|---|
| G01 Native equations, full binary alphabet and radius | 14, 20–22 | Native restrictions certified; full-rule radius unresolved. |
| G02 Represented-state layout and reserved flag cells | 33, 35 | GR0 and GR1 layouts checked; GR1 has K=386 and Q≥2K. |
| G03 Fivefold storage, transport and procedure copies | 33–34 | GR1 pure-E0 copy/wake induction proved; real1 and literal-Gray refinement open. |
| G04 Computed-clock convention and active/rest timing | 22, 34, 41 | Stage arithmetic and GR1 tracked-field operator partition proved; damaged-clock refinement open. |
| G05 Three snapshots and mail routing | 28–29, 34 | GR1 primitive routing and all 33 gather coordinates proved conditionally; whole physical lift open. |
| G06 Separate histories and fifth-stage temporal vote | 34 | GR1 stores all three banks and votes at 112Q+1; primitive identities proved. |
| G07 Noiseless rest stuttering | 34 | GR1 tracked fields stutter conditionally and its encoded clean trajectory rests; arbitrary damaged-state rest refinement open. |
| G08 Selective stage-start resets | 33–35 | GR1 tracked-field resets proved; interpreter/reset dependency refinement open. |
| G09 Mailbox/native-address simulation wipes | 33 | Holder-local implementation present; full damaged-clock semantics open. |
| G10 Early Flags and redundant couriers | 34–35, 41 | GR1 abstract prefix and courier coordinates/deadlines proved; physical early execution remains a premise. |
| G11 Computed-SimBit Workspace pulse | 41 | Literal composition has the conditional radius witness below. |
| G12 Interpreter, hardwired fetch, execute, find/match and write | 30–32, 34 | GR1 abstract programme, Match/frame/forwarding and pure-E0 composition proved; real1/literal refinement open. |
| G13 Fifth-stage results, rest preservation and period commit | 34 | GR1 clean and pure-E0 encoded-period Hold/commit closure proved; real1 recovery open. |
| G14 Programme size and runtime | 31, 34 | GR1 actual ROM/runtime checked; Address/selector ROM has not been compiled into Gray's Q ProgramBit positions. |
| G15 Initial encoding and continuing physical self-simulation | 15, 33 | GR1 broad encoding family has continuing boundary decoding under pure E0; faithful Gray/higher noisy closure open. |
| G16 Physical E0 lift, real1 recovery and residue localization | 34–36, 41 | GR1 pure-E0 lift proved with arbitrary replacement clocks; real1/localization/iid claims open. |

Fetch/Execute/Find/Match/Write describes the proposed implementation's
micro-operations; Gray describes an interpreter but does not print that
microcode. A faster compiler would need its own universal certificate,
and would still need to satisfy the physical obligations above. No smaller
U is proposed in this checkpoint.

The original PDF explicitly declares radius 5 on
[page 14](../figs/gray_counterexamples/Gray_page14.png), requires all simulation
bits to be wiped under the computed-Flag1/changed-Address condition on
[page 33](../figs/gray_counterexamples/Gray_page33.png), gives the stage protocol
on [page 34](../figs/gray_counterexamples/Gray_page34.png), and makes a Workspace
flag read a **computed** SimBit at another site on
[page 41](../figs/gray_counterexamples/Gray_page41.png). The computed value of
that SimBit can itself depend on the native vote at that other site.
Reading a corrected current SimBit, as GR0 does, does not implement that
composition on every raw configuration.

[`check_computed_simbit_radius.py`](proofs/gray_counterexamples/check_computed_simbit_radius.py)
and [its certificate](../figs/gray_counterexamples/computed_simbit_radius_certificate.json)
give an exact local obstruction with one explicit completion premise:
at computed Age 96Q+1, the primary SimBit at site 3 is its coherent fivefold
majority unless the mandatory native wipe applies; no other SimBit write
occurs on that tick. This is the natural stuttering interpretation of the
fourth stage. Gray's unspecified simulation microcode has not been proved
to implement it on arbitrary damaged raw states, so it is retained as a
premise. The witness is one tick after the stage-start reset, avoiding a
simultaneous reset-priority question.

Take x = 0. In both configurations all raw Ages are 96Q, all native and
Workspace Flags are 0, and the five coherent copies of logical SimBit 3
are 1. Raw Addresses are canonical except that sites −2,−1,0 are shifted
by +1, and sites 4,5 are shifted by +2. One configuration has Address(8)=8;
the other has Address(8)=10. Every full input bit in [−5,5] is identical;
the configurations differ only at site 8. At x = 0 both native updates
produce Address 0, Age 96Q+1, Flag1 = Flag2 = 0. The Workspace.Flag2
read therefore selects computed SimBit at site 3 in both cases.

At site 3, the left directional Address vote is 4 in both configurations.
With Address(8)=8, its right vote is 3 and only one in-colony left site
mismatches; computed Flag1 is 0, and the new Address is the unchanged 3.
With Address(8)=10, its right vote is 5 and all five in-colony left sites
mismatch; computed Flag1 is 1, and the selected left vote makes the new
Address 4. Thus the mandatory simulation wipe applies only in the second
configuration. Under the stated SimBit-write premise, computed SimBit(3)
is respectively 1 and 0, so computed Workspace.Flag2(0) is respectively
1 and 0.

Eight exact native netlist cofactors verify those constants, using both
the literal printed and corrected h = 1 native rules. This witness is
independent of the healthy Flag2 erasure change, since every input Flag2
is 0. Identical radius-5 input neighbourhoods cannot give different outputs
in a radius-5 CA. Consequently the literal composition, **with the stated
SimBit-write premise**, requires radius at least 8. This is a proved
conditional refinement obstruction, not an unconditional claim that no
completion of Gray's informal description exists.

The fourteen same-tick overwrite locations [−5,8] at raw time 96Q form a
valid real1 set under λ = 24 and c = 104, as the receipt checks. They can
specify the finite input neighbourhood from a pre-existing history by
arbitrary legal replacements. This location-set fact does not certify a
full encoded history or a physical next-state counterexample: those still
depend on a defined faithful completion and the explicit SimBit-write
premise. There is no iid memory-failure inference.

Possible implementations must resolve this obligation explicitly. Expanding
the full rule's radius and gathered neighbourhood, replacing computed SimBit
with corrected current SimBit, or adding a delay/protocol invariant are
changes or additional proof obligations. None is silently chosen here,
and none is claimed to make the reliability proof go through. Stage-gated
transport/reset primitives can be developed independently while this full
rule interpretation remains open.

**Stage-gated completion checkpoint: GR1.**
[`gray_staged_transport.py`](proofs/gray_counterexamples/gray_staged_transport.py)
implements an isolated transport/reset primitive with 52 logical simulation
bits and five physical copies each: Info, Hold, two mail tracks, three
11-lane histories including the local input, an 11-lane temporal-vote bank,
and four scratch bits. Its computed native Address, Age, Flag1 and wipe
are explicit control inputs. It is not a complete cellular-automaton rule.

[`check_gray_staged_transport.py`](proofs/gray_counterexamples/check_gray_staged_transport.py)
and [its certificate](../figs/gray_counterexamples/gray_staged_transport_certificate.json)
prove 330,720 output route identities over all 53 clock classes and 24
Address classes. These classes partition every possible 20-bit clock and
13-bit Address; each branch is constant within its class. There are 780
free logical data bits per class. The checker also proves 31,200 rest
identities, 80 exhaustive two-fault majority cofactors, all 33 gather
coordinates, the fifth-stage temporal vote and the selective tracked-field
resets. Each gather snapshots at computed Age S+1, after its stage-start
reset at S; nonlocal captures occur at S+2+distance. These are exact finite
Boolean/coordinate proofs, not sampled simulator results.

The copy-transparency implication requires five coherent copies before
at most two arbitrary physical-site replacements and unchanged correct
computed controls. The rest implication excludes native wipe and Flag1
mail clearing. The early programme must populate coherent Hold at LO=3850
and HI−1=4341 before the courier loads, and the final programme must populate
coherent Hold before 120Q. Those writes and the interpreter fields are not
proved by the primitive certificate.

[`gray_staged_rule.py`](proofs/gray_counterexamples/gray_staged_rule.py)
combines the primitive with the native h=1 rule and an isolated five-front
interpreter. This is a new diagnostic proposal **GR1**, not a change to G17
and not Gray verbatim. It retains Q=8192, U=1,048,576, λ=24 and c=104.
It has 386 state bits, 20,275 Boolean gates and 386 distinct represented
layout cells; Q≥2K holds. The early prefix runs at physical computed Ages
70Q through 72Q, after all third-stage captures. The two courier loads
occur at 651,511 and 651,510 and deliver the flags at 80Q−1=655,359.
At 112Q+1 the primitive stores the temporal vote. A fresh full replay
starts at 112Q+2 and its declared 124×512-tick window ends at 980,994,
before 120Q=983,040.

The isolated [builder](proofs/gray_counterexamples/build_gray_staged.py)
uses the already flagged XOR-multiplicity scheduler repair and a deliberate
Match-page wait adaptation; active compiler sources remain unchanged.
[Its build receipt](../figs/gray_counterexamples/GR1_program_build.json),
[exact ROM asset](../figs/gray_counterexamples/GR1_program.npz) and
[instruction listing](../figs/gray_counterexamples/GR1_program_listing.json)
retain all 27,571 instructions and the successful first attempt. The
actual usage is NPe=11, MP=65 and NP=82. Its 64 replay vectors have zero
observed mismatches; that comparison is measured only.

[`check_gray_staged_schedule.py`](proofs/gray_counterexamples/check_gray_staged_schedule.py)
and [its universal certificate](../figs/gray_counterexamples/GR1_symbolic_schedule.json)
prove all 23 lookup-key bits, both early Flag outputs and all 386 final
outputs for every abstract input. The final replay starts with undefined
registers and scratch, so the proof does not rely on early evaluator
residue. During the early prefix, the majority of the three retained
histories must supply each compiler input; during the final replay, the
stored vote bank must supply those same inputs. Correct physical front
execution, write forwarding and gathered values remain hypotheses.

One suspected fetch failure was checked and rejected. The confined Match
front traverses only [3830,4341], whereas an arbitrary lookup Address can
be anywhere in [0,8191]. All ROM rows outside [3850,4342) are zero. More
decisively, the actual multiplexed front gates every instruction write
and match write by the selected Address being inside [3850,4342). If no
slot arrives, its outputs are independent of I. If a slot arrives outside
the work rows, registers merely carry and pending outputs are zero,
independently of I. Every other GR1 output is I-independent. Thus failing
to fetch an outside-row zero instruction cannot alter the upper output;
the initial missing-key suspicion alone was not a counterexample.

[`check_gray_staged_fetch.py`](proofs/gray_counterexamples/check_gray_staged_fetch.py)
and [its certificate](../figs/gray_counterexamples/GR1_fetch_certificate.json)
prove 1,446,400 output/lookup identities in 12,800 symbolic front cases:
all 512 Match ticks, five comb fronts and five coherent copy holders,
with 64 free register bits and 24 free instruction bits. With canonical
holder geometry and common correct computed clock, front0 visits each
of the 492 work keys exactly once. Before that hit the selector remains
unchanged; the complete instruction is loaded at the hit. Its Address
key is not overwritten or revisited, so the selector/I-buffer overlap
causes no later hit. The next forward page starts at the same final
center and carries the loaded instruction. All 7,700 outside work keys
have zero ROM rows and are covered by the independence argument above.
This is a conditional noiseless Match-courier sublemma, not a complete
physical Fetch/Execute/Write or noisy refinement theorem. An initial
checker assertion used two Boolean-equivalent equality encodings with
different node trees; [the first checker and failure](../figs/gray_counterexamples/GR1_fetch_initial_checker_failure.json)
are retained, and the rerun uses the same equality encoding as the netlist.

GR1 explicitly replaces Gray's computed-SimBit Workspace read with a
corrected **current** SimBit read; its pulse does use computed Age. The
conditional radius obstruction above remains unresolved for the literal
printed read. It also uses a multi-front interpreter, selected resets
and stage boundaries defined by this explicit microcode. In particular,
the tracked-field rest lemma excludes register/pending fields, which
GR1 clears when its evaluator window closes. Rest stuttering on arbitrary
damaged raw states and its literal Gray refinement remain open. A failure
of this proposal would not by itself refute Gray's construction.

**GR1 clean-period closure.**
[`check_gray_staged_frame.py`](proofs/gray_counterexamples/check_gray_staged_frame.py)
and [its certificate](../figs/gray_counterexamples/GR1_frame_certificate.json)
classify all 314,880 nonmatch visits into 175 control classes and prove
19,775 output/lookup identities with 64 free register and 24 free instruction
bits per class. The route implication covers starts, turns, movement,
operand selection and coherent pending targets/values using the fixed
interpreter's decoder/ALU definition. Separately, the actual full GR1
netlist gives 6,240 tracked-field coupling identities over all 24 Address
route classes, with the entire common 20-bit clock and all 44 native and
Workspace flag inputs free. Hold and scratch reads forward the coherent
current pending store before the selective stage resets. These are local
implications with coherent input data; they do not establish such input
conditions after arbitrary errors.

[`check_gray_staged_flag_quiet.py`](proofs/gray_counterexamples/check_gray_staged_flag_quiet.py)
and [its certificate](../figs/gray_counterexamples/GR1_flag_quiet_certificate.json)
prove 22 exact boundary cofactors under canonical geometry and common Age.
After Workspace.Flag1 is zero, a zero Flag1 suffix grows from the right
colony boundary by at least two cells per clean tick. Once Flag1 is zero
everywhere and Workspace.Flag2 is zero, a zero Flag2 prefix grows from
the left boundary by at least two cells per tick under h=1. Every colony
therefore clears both flags within Q clean ticks. For GR1's pulse, this
puts every native flag at zero by Age 99Q=811,008. This is a healthy-geometry
noiseless clearing lemma, not damaged-geometry or continuing-E0 recovery.

The [written composition proof](proofs/gray_counterexamples/GR1_NOISELESS_PERIOD.md)
defines a broad encoding family E(s): native Address is canonical, Age
and all native/Workspace flags are 0, every private simulation field is 0,
and five coherent Info copies encode the upper configuration s at the
386 layout cells. Coherent unrepresented Info values are unrestricted;
no auxiliary/represented flag alias is assumed from arbitrary work. For
every bi-infinite s and every c∈E(s), the fixed GR1 local rule satisfies

    F^U(c) ∈ E(F(s)).

Thus decoding at each noiseless period boundary gives F^n(s) for every
n≥0. The proof composes the exact gather, native-geometry, front, pending,
Match and own-programme identities, and proves that all required coherent
copy/control premises hold along this clean encoded trajectory. Before
the Workspace pulse Flag1 is 0; at its start both mail tracks reset to 0,
so subsequent nonuniform Flag1 masks cannot spoil mail coherence. Native
Address never changes, so the simulation wipe never fires. At the final
commit, Info consumes coherent old Hold while every private field resets
to 0. [Its constituent validator/receipt](../figs/gray_counterexamples/GR1_noiseless_period_certificate.json)
pins the written proof and scheduling bounds: last gather 565,245, last
early pending-store application 578,540, last final pending-store
application 959,464. The proof uses no sampled physical trajectory and
does not permit any errors.

There is an additional programme representation departure. Gray's
pages 31–32 describe a single ProgramBit at each Address, containing a
Q-bit programme string, and its projection out of the state. GR1 instead
hardwires a table indexed by Address **and selector**. Its 8192×1024
24-bit entries contain 201,326,592 logical table bits; the 27,571 nonzero
words have 661,704 payload bits. The instruction listing has not been
compressed into Gray's 8192 ProgramBit positions. These sizes do not prove
that a compressed faithful programme cannot fit; they show that our
present own-ROM certificate does not establish that obligation. This
departure, the current-SimBit substitution and the interpreter's behavior
on damaged rest states prevent attributing GR1's clean theorem to Gray
verbatim. No real1 simulation recovery, higher reliability bound or positive
iid noise rate is established here.

**GR1 pure-E0 lift and the wipe wake.** A correct computed clock/Address
alone does not imply unconditional one-step raw-copy transparency. At
site y=Q−3=8189 and raw time 96Q+1=786,433, let the legitimate right
Workspace.Flag1 pulse be1. A singleton overwrite changing stored Address
from Q−3 to Q−2 is a genuine original E0 error. The native vote restores
the correct Address, but computed Flag1=1 and the restored Address differs
from the erroneous stored one. The mandatory simulation wipe therefore
sets the Info bits at y to0 on the following **clean** tick; the baseline
primary Info is1 from the early Flag1 courier.

[`check_gray_staged_wipe_wake.py`](proofs/gray_counterexamples/check_gray_staged_wipe_wake.py)
and [its receipt](../figs/gray_counterexamples/GR1_wipe_wake_certificate.json)
prove this with 64 actual compiled-net cofactors and coherent free history
bits. The wake has 171 potentially changed outputs at y, including all
five Info copies stored there and Workspace.Flag1. Native Address, Age,
Flag1 and Flag2 already match. All 410 local outputs at eleven readers
match again one tick later, with 4,510 exact equalities. These are finite
Boolean proofs, not sampled measurements.

This context is reachable from the GR1 broad E family: choose upper raw
Workspace.Flag1=1, canonical upper Address/common Age0, the other upper
flags0 and all other upper fields0. Choose initial unrepresented Info1.
The universally verified early prefix produces upper new Flags(1,0),
so the specified pulse follows. This proves reachability for GR1's broad
encoding theorem. It does **not** prove reachability from Gray's intact
recursive all-level initialization, whose upper Workspace flags start0.
The witness is not a Gray Proposition2/4 refutation, a boundary-decoding
failure or an iid memory counterexample. It exposes the necessity of the
earlier primitive lemma's unchanged-wipe-control premise.

The [pure-E0 period proof](proofs/gray_counterexamples/GR1_E0_PERIOD.md)
handles the wake without changing the rule or reclassifying its point as
an error. A spatial interval of diameter10 across two adjacent time rows
cannot meet two distinct original E0 groups: that would violate their
(24,24) isolation. The union of current overwrites and previous-tick
wipe wakes therefore contains at most two holders in any needed vote.
Whole-word majority likewise restores canonical Address/common clock
from three correct words, regardless of the two replacement words.
The current-GF comparison can wipe only a current input error site;
an older wake has already-correct geometry and heals rather than creating
a further wipe chain.

The remaining native obstruction is quieting Flags before the final
interpreter. [`check_gray_staged_E0_flag_recovery.py`](proofs/gray_counterexamples/check_gray_staged_E0_flag_recovery.py)
and [its receipt](../figs/gray_counterexamples/GR1_E0_flag_recovery_certificate.json)
prove 616 exact native boundary/growth cofactors. After 98Q, a guaranteed
zero Flag1 suffix never retreats and advances two cells unless the current
E0 group meets its five-site charge strip. Its guaranteed boundary moves
at most two sites per row. Two charges less than ten ticks apart would
have error points within 2Δ+4<24 sites and Δ<24 ticks, contradicting original
E0 isolation. Thus at most ceil(n/10) of n rows are charged. Exactly 4,552
rows suffice to cover Q. The same argument clears a Flag2 prefix once
Flag1 is quiet. All computed native Flags are therefore quiet by
98Q+9104=811,920, before 100Q and the final 112Q interpreter start.
The bound covers arbitrary replacement clocks and bits under pure E0;
it is not a noisy real1 recovery estimate.

Both interpreter windows are consequently wipe-free. Captures, the early
prefix and the couriers precede the first legitimate Flag1 source; the
final prefix follows proven quieting. The actual front and pending-write
lemmas apply to selected five-holder register cohorts after majority
correction. Inactive/nonarriving lookups are I-irrelevant. Mail is unblocked
before96Q and is reset to0 during and after the pulse. All data outputs
remain correct except current overwrites and one-tick wipe wakes; at a
period boundary quiet Flags remove even the wakes.

The resulting theorem, pinned by
[`check_gray_staged_E0_period.py`](proofs/gray_counterexamples/check_gray_staged_E0_period.py)
and [its constituent receipt](../figs/gray_counterexamples/GR1_E0_period_certificate.json),
is: for every original **pure E0** error set and arbitrary full-state
replacement values, starting from E(s), the state at nU agrees outside
current E0 with an E(F^n(s)) member, and the five-copy boundary decoder
returns exactly F^n(s), for every n≥0. This is a written universal
induction, not a sampled noisy campaign or proof-assistant formalization.
All errors must belong to E0. The theorem provides no ε>0 for iid noise,
which includes non-E0 clusters, and no real1/higher localization. All
listed GR1-to-Gray representation and semantic departures remain.

**Real1 legal-clock wrap and pointwise transport footprint.** The next
full-clock audit uses Age=U−1, outside the former bounded-clock quotient.
From a stated GR1 broad-E initialization, five adjacent errors at time1
change only Age and Hold, leaving Info and Address untouched. The next
clean tick computes Age0 and commits Info1 at3868/3869. Exact local
Boolean evaluation and a620-cofactor two-clock-label induction prove
that the five-cell clock island moves right3 cells/tick, stops at the true
colony boundary and disappears at1444<U/32. Native Flags are quiet by9636.
This provides no counterexample to native recovery.

The Info difference persists until the usual commit. The exact second
gather routes it in both directions. At time266470, Info3868,
Mailbox.L(−457) and Mailbox.R(8193) differ simultaneously: three colonies
cannot fit in a single fixed adjacent pair. The
[written proof](proofs/gray_counterexamples/GR1_REAL1_CLOCK_COMMIT.md),
[checker](proofs/gray_counterexamples/check_gray_staged_real1_clock_commit.py)
and [receipt](../figs/gray_counterexamples/GR1_real1_clock_commit_certificate.json)
prove this GR1 failure of the literal pointwise all-simulation-fields
two-colony envelope. They do not refute the accepted pure-E0 theorem:
the five-point error group is real1. No decoded boundary error is claimed.

Gray's printed Proposition4 on page36 uses pointwise simulation-field
equality, while its page35 argument permits wrong incoming Mailbox
information in undamaged colonies and instead argues about correct
simulated transitions. The written audit isolates that distinction.
A counterexample to a faithful Gray completion remains unproved because
GR1's physical departures persist. The original checker used a broad
upper state; the new intact initialization certificate below strengthens
this premise without changing that retained checker or rule. The
[initial checker and failure receipt](../figs/gray_counterexamples/GR1_real1_clock_commit_initial_checker_failure.json)
retain the premature24-tick recovery assertion; the proof uses actual
clock advection, without changing the rule.

**The clock/mail witness from an intact GR1 hierarchy.** The
[explicit initializer](proofs/gray_counterexamples/gray_recursive_initialization.py)
defines a logical Info word D on the whole integer line by recursion:
Address primaries encode the parent Address, Info primaries recursively
read the parent's five Info slots, and all other primaries are0. Each
recursive Info call strictly decreases the argument's absolute value.
The [all-level proof](proofs/gray_counterexamples/GR1_INTACT_CLOCK_COMMIT.md)
proves the resulting raw configuration H satisfies H∈E(H), including
every represented field and all five backup copies. Every hierarchy
level can start in this same H. Cell H_0 is all zero, and lower colony0
has exactly the all-zero Info context of the retained clock cone.

The [new checker](proofs/gray_counterexamples/check_gray_staged_intact_clock_commit.py)
and [receipt](../figs/gray_counterexamples/GR1_intact_clock_commit_certificate.json)
certify the old cone's197632 input equalities, all8192 native flag
cofactors with free common Age, and22 complete upper-net cofactors/4510
output identities. Geometry heals by1444 and native flags clear by9636,
before the second gather. Both later banks encode the same q, which
differs from H only at raw upper Reg bit2 of holder0. Their native
inputs are correct at every receiver and all11 offsets; arbitrary
History1 is outvoted. The early flag outputs and special pulse sources
are0. Thus the same simultaneous Info/Mail footprint in colonies−1,0,1
is reached from a genuinely intact GR1 hierarchy by the sole physical
real1 core, without an independently supplied upper fault.

This particular error has a correct first decoded boundary: every
register read votes five copies, so F(q)=F(H), and the full physical
composition gives X_U∈E(F(H)). With no later errors, accepted noiseless
self-simulation gives correct continuing decoded boundaries. The
counterexample is to GR1's literal pointwise temporary-field envelope,
not to decoded recovery or iid memory. Gray's ProgramBit/interpreter,
computed-SimBit and damaged-rest refinement gaps persist.

**Literal stage assumptions versus Proposition4.** The
[new theorem and exact assumptions](proofs/gray_counterexamples/GRAY_LITERAL_STAGE_ENVELOPE.md)
use a simpler real1 core: at one tick overwrite three holders' copies of
one ordinary represented SimBit, preserving every native, Workspace and
ProgramBit value. An upper Workspace bit initially0 provides such a
primary independently of the programme string. The explicit five-copy
vote makes the erroneous value1 coherent next tick; canonical native
geometry and zero Flags persist before the96Q Workspace pulse. This
avoids the unprovided literal Hold buffer and damaged-Age0 commit rule.

Under faithful full raw-state gathering, the second stage stores that
wrong source bit in Workspace records in both neighboring receiving
colonies. Under the stated rest retention, at T=56Q=458752 these records
and the source SimBit give pointwise differences in colonies−1,0,1.
Proposition4 supplies only one fixed adjacent-pair box for this sole
real1 error, so no spatial or temporal choice covers them all. The proof
does not require simultaneous Mailbox motion or GR1's stream geometry.

The [constituent checker](proofs/gray_counterexamples/check_gray_literal_stage_envelope.py)
and [receipt](../figs/gray_counterexamples/Gray_literal_stage_envelope_certificate.json)
verify all8192 literal-native phase cofactors with free common Age,
three-copy majority, original c104 classification and stage arithmetic.
The recursive initialization formula accommodates arbitrary correct
ProgramBits beta and fixed unused marker bits; an explicitly illustrative
symbolic frame is not claimed to be Gray's actual fields or programme.
Raw-state gathering, local receiving-colony storage, independence of
older histories and record retention on this post-error trajectory are
the exact unverified physical premises G,R. A rule that repairs upper
raw copies or omits irrelevant bits before storage would not satisfy G;
its refinement of the printed description needs a separate argument.

The original [page35](../figs/gray_counterexamples/Gray_page35.png) and
[page36](../figs/gray_counterexamples/Gray_page36.png) images confirm the
distinction between admitted incorrect incoming mail and the literal
all-SF equality conclusion. [Page31](../figs/gray_counterexamples/Gray_page31.png)
and [page32](../figs/gray_counterexamples/Gray_page32.png) retain the
ProgramBit construction: its earlier example's Address primaries1..log2Q
cannot be retained unchanged together with the later reserved primary3.
Compatible final layout, own-programme fit/runtime at8192 and actual
gathering/refinement remain open. The new result is a conditional
incompatibility of the published stage semantics and the pointwise
statement, not a proof of iid memory failure. A small tuple/list assertion
error in the initial checker is retained in its
[failure receipt](../figs/gray_counterexamples/Gray_literal_stage_envelope_initial_checker_failure.json);
no mathematical witness or rule changed.

**Real1 split snapshot at an arbitrary upper boundary.** A stronger GR1
boundary counterexample uses upper z with canonical native fields, Flags0
and four deliberately incoherent Info backup bits. Lower E(z) is valid,
but this z is outside an intact recursive initialization. At the second
gather snapshot262145, errors at3988…3990 and4091…4093 change only the
logical Info, right-mail and History2-own copies of upper holder0's Info
slots1/2. These six points are one original c104 real1 error despite
their total width106; the exact classifier checks condition(iii).

The [literal lower/upper checker](proofs/gray_counterexamples/check_gray_staged_real1_split_input.py)
proves64 lower cofactors/13120 identities and six upper cofactors.
The [written boundary composition](proofs/gray_counterexamples/GR1_REAL1_SPLIT_BOUNDARY.md)
uses the retained histories and exact route/front/ROM certificates:
History1 sees the old0, History2 sees0 on the left and1 at self/right,
History3 sees1 everywhere. The final output Y has logical upper Info0
copies(0,0,1,1,1) and Info−1 copies(0,0,0,1,1).
Any adjacent upper input replacement pair still gives a coherent common
Info vote at the next tick. The first output pattern forces output
exceptions at{−2,−1}, while the second excludes that pair. Therefore no
single adjacent input pair and output pair explain this actual boundary
as Y=F(v) outside the output pair, with v=z outside the input pair.
The [receipt](../figs/gray_counterexamples/GR1_real1_split_input_certificate.json)
pins X_U∈E(Y) and this counterexample for arbitrary upper raw states.
It refutes that stronger arbitrary-upper-state real1 map for GR1; it
does not refute a theorem whose initialization requires intact recursive
Info backups, the accepted pure-E0 theorem, Gray, or iid reliability.

**Width99 variant and hierarchy isolation.** The
[simpler proof and isolation audit](proofs/gray_counterexamples/GR1_REAL1_SPLIT_E0_CONTEXT.md)
uses lower Info2/Info3 primaries4092/4188. Its six-point real1 core changes
only Info and right-mail; History2-own and left-mail retain0. The initial
upper defects are all at holders1/2, a single adjacent pair of a coherent-zero
Info state. The pair is E0 when classified alone. The
[new checker](proofs/gray_counterexamples/check_gray_staged_real1_split_e0_context.py)
and [receipt](../figs/gray_counterexamples/GR1_real1_split_e0_context_certificate.json)
prove64 lower cofactors/13120 identities, plus22 upper/reference cofactors
each at upper Ages0 and1. Info0 outputs(0,0,0,1,1), forcing output exceptions
at{1,2}; Info1 outputs(0,0,1,1,1), forcing{−1,0}. The actual boundary
therefore has no adjacent input/output-pair explanation even in that
smaller initial-state family. An independent upper F tick followed by
one E0 overwrite pair reaches the Age1 starting context.

That independent upper noise is not an extra noise source in the physical
hierarchy. Pure lower E0 histories cannot produce its decoded boundary
pair, by the accepted E0 theorem. A proposed nearby earlier non-E0 lower
source makes the later core fail Gray's condition(iv): the receipt's
specific earlier/later sets combine into real2, with no real1 groups.
It does not claim the proposed earlier points generate the upper pair.
Likewise, the manually supplied pair and later bad upper holders are not
E0 when classified in their combined upper location set. Reachability
from a complete admissible physical error history and an intact recursive
initialization remains unproved. No universal exclusion of distant/old
histories is claimed. A real1 lifting theorem needs an operational copy
invariant coupled to physical error separation; permitting an arbitrary
current upper E0 pair independently of the lower core is insufficient.

**GT0: concrete raw gathering and retained records.** The
[isolated component](proofs/gray_counterexamples/gray_raw_gather.py)
keeps Q8192, U128Q and lambda24/c104. It emits an explicit radius-five
data transition with primary-first five-holder copies. Both Mailboxes
snapshot the corrected primary word and shift in opposite directions;
three independent eleven-lane History banks capture the same within-colony
position in all eleven source colonies. The last capture takes5Q+2 ticks,
inside each16Q active gathering interval. Earlier History content cannot
control later gathering, and coherent tracked records stutter during rest
when the native wipe and Flag1 are clear. The
[written proof](proofs/gray_counterexamples/GT0_RAW_GATHER.md),
[checker](proofs/gray_counterexamples/check_gray_raw_gather.py) and
[receipt](../figs/gray_counterexamples/GT0_raw_gather_certificate.json)
contain144000 exact route equalities,14400 rest equalities and80 two-fault
majority cofactors. This supplies G/R for GT0 under correct native controls
and coherent source/record premises. It leaves Gray's actual unspecified
programme's refinement to this component unproved.

The [JSON graph](../figs/gray_counterexamples/GT0_transitions.json) and
[C source](../figs/gray_counterexamples/GT0_transitions.c) give the emitted
Boolean transitions, with2687 input bits,5035 gates and240 data output bits.
The preliminary277-bit frame includes native and Workspace flags but
excludes the future interpreter. Its
[layout](../figs/gray_counterexamples/GT0_preliminary_frame_layout.json)
has a proved terminating recursive data initialization H in E(H), allowing
arbitrary symbolic correct ProgramBits at unrepresented primary0. No
actual compact self-programme beta has been compiled. Native computed
controls, early Flag results and final interpreter stores are explicit
integration ports. The latter two port families are unused through56Q.
The independent C-source mapping is structurally checked;600 compiled C
comparisons are **measured only**, with their complete
[inputs/outputs](../figs/gray_counterexamples/GT0_C_comparison_inputs_outputs.npz)
retained. The universal route proof does not rely on those comparisons.

From this recursive data initialization, overwrite only the three
SimBit copies of logical primary4010 at holders4009,4010,4011, time1.
This is one original real1 and no E0; it does not overwrite Age, Address,
Workspace or Mailbox. Thirty compiled local cofactors prove7200 output
identities: at time2 exactly the five copies of that logical primary
become coherently wrong. With the printed native equations and Workspace
pulse restriction supplied, native geometry and Flags remain correct
before96Q. GT0's proved gather/retention equations then give simultaneous
wrong History2 records at sites−4182 and12202 plus the persistent wrong
SimBit4010 at time56Q. They lie in colonies−1,0,1. This closes the
first56Q data-prefix footprint for every completion retaining these
component equations and that native condition. The full-rule existence,
actual Gray programme/layout, last-stage runtime and period composition
remain open. No decoded-memory conclusion follows. An initial checker
bound on unused emitted inputs was enlarged from y±10 to y±14; the
[failure receipt](../figs/gray_counterexamples/GT0_initial_injection_bound_failure.json)
pins the first checker/proof. No transition, schedule, layout or error
changed to fix that check.

The [late integration checker](proofs/gray_counterexamples/check_gray_raw_gather_radius.py)
and [receipt](../figs/gray_counterexamples/GT0_radius_integration_certificate.json)
add a precise obstacle to whole-rule composition. At computed Age96Q+1,
GT0's primary SimBit equation is exactly its current five-holder vote
masked by native wipe, for arbitrary future programme ports. Two raw
states differing only in Address8 give the same computed native controls
at0 but a different wipe and computed SimBit at3. Gray's literal p41
Workspace.Flag2 read then gives different outputs at0. Thus this particular
component set requires radius at least8; it has no radius-five or
radius-seven full raw-state completion preserving all three equations.
This removes the older witness's no-other-SimBit-write premise **for
GT0 only**. It neither excludes every possible Gray completion nor
proves intact-hierarchy reachability or iid failure. Enlarging the radius
or changing either literal interface must be flagged as a rule change.

**Locality and evaluation order.** The
[follow-up source audit](proofs/gray_counterexamples/GRAY_COMPUTED_SIMBIT_ORDER.md)
separates final computed SimBit, scheduled pre-wipe SimBit, raw current
primary and voted current SimBit. Native “computed” values are explicitly
defined as transition outputs; the mandatory wipe includes final SimBit.
Interpreting the p41 SimBit read as a pre-wipe intermediate is an explicit
interpretation change, since Gray does not name that intermediate.
His full raw-state SimBit rule is also implicit, so this audit does not
claim a unique interpretation or nonexistence of every Gray completion.

Deleting only the source wipe does not fix GT0's locality. A second exact
witness changes only Age8: source3 commits old NextBit0 at computed Age0
in one state, and keeps current voted SimBit1 in the other. Reader0's
native controls remain fixed at the pulse. Thus the scheduled pre-wipe
read also requires radius at least8. The
[checker](proofs/gray_counterexamples/check_gray_computed_simbit_order.py)
and [receipt](../figs/gray_counterexamples/Gray_computed_simbit_order_certificate.json)
pin17 native cofactors, with every future GT0 programme port free.
Neither local witness establishes encoded-history reachability.

Raw current-primary reading fits radius5 but a singleton E0 corruption
of primary3 can falsely turn on all five left-edge WF2 outputs on the
next tick while its SimBit vote corrects0. This is a local source-copy
transparency failure under canonical pulse controls and coherent source0;
the actual self-programme's complete snapshot still needs certification.
The explicitly changed
[GV0 interface](proofs/gray_counterexamples/gray_workspace_voted_current.py)
instead reads the majority of **current** five-holder source copies,
excluding both the source wipe and every source-site scheduled write.
Its [emitted Boolean graph](../figs/gray_counterexamples/GV0_voted_current_workspace_transitions.json)
has radius5 for all raw states. Sixty-six symbolic route identities and102
complete at-most-two-fault vote cofactors certify this per-cell interface.
It preserves the printed native rule and therefore also leaves its known
Flag2 issue. GV0 is a source-expression rule change, not an unchanged
Gray compilation or a full noisy-period theorem.

Alternatively, if a completed source SimBit transition has radius5,
the literal Workspace composition needs the neighbourhood[-7,8], inside
radius8. The accepted lower bound and this dependency upper bound then
match for that component family. A radius8 self-simulation needs17
upper neighbours; the asymmetric[-7,8] option needs16. The17-lane raw
gather fits in16Q but grows GT0's preliminary frame277 to397 bits.
Programme fit, last-stage runtime, compatible layout and period composition
are unproved. Error-location classification and its purely geometric
estimates do not depend on the radius. Deterministic control/wipe,
E0-copy induction, transient speeds and higher-level lifting must still
be checked; a retained geometry example has two distinct original E0
groups inside a two-tick radius8 cone. It demonstrates possible cone
overlap, not survival of actual corrected errors. No enlarged-radius
Gray reliability proof is obtained by borrowing those steps unchanged.

**Programme bottleneck: one concrete evaluator is too large.** The
[programme/hardwirer audit](proofs/gray_counterexamples/GPN0_PROGRAMME_OBSTRUCTION.md)
checks Gray pp30-32 and the corresponding material in the supplied Gács
paper. Despite its filename, [gacs_2001.txt](../papers_txt/gacs_2001.txt) identifies itself as a corrected
and strengthened printing dated24January2024. Its relevant rule-language
and block-evaluator statements are now §§9.1-9.3, Theorem9.2,
Algorithm9.7 and Condition9.20, rather than Gray's contemporary7.3-7.4
references. This version difference does not refute Gray's citation.
The available interpreter bounds retain an unspecified coefficient and
do not emit a beta or a finite Q8192/runtime certificate.

The new [GPN0 encoder/evaluator](proofs/gray_counterexamples/gray_native_bitpacked_program.py)
uses a bit-packed straight-line Boolean programme with implicit gate
destinations; it has no GR1 page ROM. The actual
[native programme](../figs/gray_counterexamples/GPN0_literal_native_beta.bin)
and [decoded graph](../figs/gray_counterexamples/GPN0_literal_native_programme.json)
encode the unchanged literal native module alone. Its2919 gates need26
bits each, and its35 outputs need420 map bits. With a75-bit header,
the programme has76389bits, exceeding the Q8192 one-ProgramBit-per-cell
capacity. This is a proved obstruction for this explicit separate-module
encoder, before adding any SF/interpreter/hardwirer code. A fresh serial
one-programme-bit/tick fetch starting in the fifth active interval also
needs at least76389 ticks, exceeding8Q65536. Prefetching or parallel
delivery can avoid that runtime model; neither lengthening U nor changing
delivery alone repairs the stated programme-storage failure.

The [checker](proofs/gray_counterexamples/check_gray_native_bitpacked_program.py)
and [receipt](../figs/gray_counterexamples/GPN0_native_programme_certificate.json)
prove all-input native-code equivalence by exact topological decoding:
2919 gate and35 output-map equalities. The abstract parser/evaluator has
a total invalid-input response, with eight malformed cases retained.
Its128 [random replays](../figs/gray_counterexamples/GPN0_native_programme_replays.npz)
are measured evidence, separate from that structural proof. A labelled
h1 native programme still fails both constraints. For this encoder the
first tested power-of-two Q whose native prefix fits is131072; that is
neither a complete-rule fit nor a smallest reliability repair. Compact
word/loop programmes remain open. GPN0 has no physical interpreter/service
equations or final layout, and its emitted bitstring is a native programme,
not the whole self-beta. The exact failed fit precedes those construction
obligations; it provides no Gray or iid-memory counterexample.

GMW0 now implements a different, compact representation: an actual finite
moving-head word interpreter and its emitted native programme at the original
Q=8192, U=128Q, lambda24/c104. The
[kernel](proofs/gray_counterexamples/gray_moving_word_kernel.py),
[physical-prefix proof](proofs/gray_counterexamples/GMW0_PHYSICAL_NATIVE_PROGRAMME.md),
[checker](proofs/gray_counterexamples/check_gray_moving_word_kernel.py) and
[receipt](../figs/gray_counterexamples/GMW0_native_programme_certificate.json)
define all raw-state component equations, opcode decoding, collisions and
invalid behavior. The programme has107 instructions and2346 bits in an
actual [beta](../figs/gray_counterexamples/GMW0_native_beta.bin) and
[listing](../figs/gray_counterexamples/GMW0_native_listing.json). Its
2272-bit tentative physical frame fits Q>=2K. One head fetches immutable
programme bits and physically walks to mutable input/output columns; no
instruction intrinsically evaluates the native or whole rule. The input-
independent execution takes34396 ticks within the fifth active65536 ticks.
Register invariants prove the literal native35 output bits for every raw
native input. A five-copy/head induction proves noiseless physical execution,
unique head initialization, radius5, rest and old-Out-to-Info-before-reset
order. Every physical head tick and98 native inputs were also
[replayed](../figs/gray_counterexamples/GMW0_native_physical_replays.npz),
as measured checks. A [listing-format failure](../figs/gray_counterexamples/GMW0_initial_listing_failure.json)
and its exact source snapshots are retained.

GMW0 is an explicitly changed **quiet native-prefix primitive**: native
Workspace flags are forced0 and the input tape is preloaded. Its beta
computes35 outputs of a2272-bit rule; it does not describe its interpreter
fields. The own full beta, actual gather/hardwirer/programme transfer,
full fifth-stage output and computed-SimBit/Workspace order remain unproved.
Neither the earlier radius/order gap nor noisy execution is repaired by
assuming this quiet interface. Full-loop space/time fit and faithful Gray
whole-rule completion remain open.

GMW1 attempted an actual complete word-programme emission. Its
[Q-code overflow receipt](../figs/gray_counterexamples/GMW1_full_own_overflow.json)
retains42850 bits,1829 instructions and268 out-of-range references for
Q8192/13-bit-PC storage, together with the failed listing, masked invalid
bits and source snapshots. This is an obstruction for that specified
implementation; it is not a lower bound for all word/loop programmes.

GMW2 now defines an entire2007-bit finite local component rule and emits
a proposed programme for every field. The
[full audit](proofs/gray_counterexamples/GMW2_FULL_PROGRAMME_AUDIT.md),
[kernel](proofs/gray_counterexamples/gray_moving_word_v2.py),
[builder](proofs/gray_counterexamples/build_gray_moving_word_v2.py),
[actual beta](../figs/gray_counterexamples/GMW2_full_own_beta.bin) and
[listing](../figs/gray_counterexamples/GMW2_full_own_listing.json)
retain Q8192/U128Q/lambda24/c104. This is an **explicitly changed64K
immutable-ROM/16-bit-PC candidate**:44730bits/1863instructions fit that
separate ROM, exceeding Gray's Q-sized ProgrammeBits storage. Mutable
ProgramBits are defined and can be read as input data; instruction fetch
uses immutable code. CODE is a specified finite ROM-word lookup, not a
native/head/whole-transition syscall. The same emitted/padded beta supplies
physical instruction decode, virtual code reads and output ProgramBits.
Universal full-beta equivalence remains **unproved**.

GMW2 also explicitly uses h1, holder-computed GF plus copy offset for
service/birth controls, and Workspace outputs0. Its all-raw transition
and radius5, quiet five-copy closure and pure-E0 component transparency
are proved from the local equations. Under a canonical/common-clock/
zero-native-flags reference, at most two current E0 holders affect any
vote. Both geometry votes repair, h1 clears erroneous native flags,
no wipe fires, and all copy-voted head/tape data and service controls
match the reference. This fixes GMW0's raw-GF birth hole **in the changed
GMW2 interface**; GMW0 remains untouched. It does not establish a
whole-period map, real1/higher recovery or an iid rate.

The [final execution receipt](../figs/gray_counterexamples/GMW2_full_own_certificate.json)
and [retained replays](../figs/gray_counterexamples/GMW2_full_own_replays.npz)
contain70 successful full-field finite comparisons, measured only, and
65535 actual active local-rule updates from a specified preloaded no-error
input. Birth consumes the first stage tick, leaving8Q-1=65535 execution
updates. The programme needs102026 uninterrupted head updates on that
input. At the actual end120Q, Out primary5099 is0 while the actual intended
upper ProgramBit copy4 is beta[2]=1. The physical rest equation freezes
the unfinished head/Out, and all five Info copies commit0 at Age0. The
[audit checker](proofs/gray_counterexamples/check_gray_moving_word_v2_audit.py)
and [audit receipt](../figs/gray_counterexamples/GMW2_full_programme_audit_certificate.json)
pin every finite prefix recurrence plus the physical copy/rest/commit
argument. This proves the **specified prepared fifth-stage failure**,
without an intact recursive initial hierarchy or a Gray/iid attribution.

A coherent upper raw state with stationary RUN/HLT heads at every logical
site also needs132803 uninterrupted evaluator updates. It still has a
wrong head-mode output bit after16Q-1 updates; an actual schedule before
Age0 allows at most16Q-2. Thus simply extending this evaluator's end to
125Q, or using all remaining16Q, does not provide an all-raw own map.
This input is not an intact one-head-per-colony hierarchy. No new schedule
or faster U is asserted; recompilation and all physical deadlines remain
required for any schedule change.

Three [retained semantic implementation failures](../figs/gray_counterexamples/GMW2_semantic_failure_01.json)
and their exact sources/inputs identify full-word Address truncation,
cross-word argument-temporary aliasing, and invalid-IO PC handling.
These were our bugs and are separate from Gray. The
[first56 receipt](../figs/gray_counterexamples/GMW2_first56_full_own_certificate.json)
and source/assets remain immutable; its older “physical preloaded” replay
label is superseded by the final distinction between uninterrupted runner
and physically gated execution. Actual Gray ProgrammeBits/hardwirer,
gather/pulse/order refinement and a complete self-simulating rule remain
unproved. GMW2 is a defined component and a concrete evaluator attempt;
its current schedule already fails before those obligations are filled.
The pinned [full cost traces](../figs/gray_counterexamples/GMW2_uninterrupted_cost_traces.npz)
split102026 into21951 instruction,12425 mutable-column and67650 travel
updates, and132803 into26539 instruction,14105 column and92159 travel
updates. Entire instructions and CODE are already fetched in one update;
the44730-bit programme length is not a44730-tick serial-fetch cost.

The new [GMW3 transport audit](proofs/gray_counterexamples/GMW3_FAST_TRANSPORT.md)
changes only the inherited evaluator's movement convention: odd computed-Age
rows may move an IO head up to three sites, while even rows move at most one
site and restore all five copies. Q = 8192, U = 128Q, λ = 24 and c = 104
remain fixed. This is an explicit variant with the inherited h1 correction,
zero Workspace, holder-computed service Address, immutable 64K ROM and
preloaded-input premises. It does not instantiate Gray's original programme.

Unpaused three-site movement fails under an exact original-E0 history.
An adjacent pair at physical holders 3092/3093 on tick 917505 removes two
copies of a prepared SEEK head; those missing copies persist through its
next three-site jumps. A singleton at holder 3117 on tick 917513 then
removes a third copy, and the next update loses the head entirely. The
two groups have minimum spatial separation 24, so this is one shared legal
E0 history, with no real1 points. The [transport receipt](../figs/gray_counterexamples/GMW3_fast_transport_certificate.json)
and [full-field witness](../figs/gray_counterexamples/GMW3_unpaused_E0_transport_witness.npz)
retain actual holder coordinates, absolute/relative clocks and replacement
words. This rules out the unpaused optimization from its prepared context;
it does not refute Gray's velocity-one transport or iid memory reliability.

The alternating variant has a proved component repair: under any two
arbitrary physical overwrites, at least three destination slots have every
prospective head vote exact. The 67 possible local fault supports exhaust
the geometry, including arbitrary packet values and collisions. A one-site
row then restores all five copies. A two-update cone has spatial diameter
20, below λ = 24, and can meet at most one E0 group. This proves continuing
pure-E0 component coupling for canonical/common-clock/zero-flag reference
geometry and arbitrary coherent SF words. It does not prove a real1 lift,
an encoded physical period, or a positive iid noise threshold.

The [recompiled proposed beta](../figs/gray_counterexamples/GMW3_full_proposed_beta.bin)
has 58,129 bits and 2,410 instructions, fitting the explicitly separate
64K ROM while exceeding Gray's Q-bit storage. The [emission receipt](../figs/gray_counterexamples/GMW3_full_proposed_certificate.json)
retains 86 successful finite whole-field comparisons, measured only; an
earlier [missing-no-head-branch failure](../figs/gray_counterexamples/GMW3_emission_failure_01.json)
is retained as our implementation bug. Universal beta identity is still
unproved. The [deadline receipt](../figs/gray_counterexamples/GMW3_deadline_certificate.json)
and [prepared traces](../figs/gray_counterexamples/GMW3_prepared_deadline_traces.npz)
separate halt time from decoded output completion: all canonical outputs
are correct at 65,535 updates despite a 71,354-update halt. A normalized
dense-HLT input instead has output bit 66 wrong at that deadline; all five
physical holders are checked on all 65,535 active updates, and its wrong
Out primary 3159 commits five wrong Info copies at the boundary. That is
a proved prepared-input deadline failure of this variant, without an
intact recursive starting hierarchy or Gray attribution. No faster U or
revised stage endpoint is asserted.

**GH0/GH1: programme hardwiring before the first raw gather.**

The next concrete refinement is an
[interior hardwirer and delayed gather](proofs/gray_counterexamples/GH0_HARDWIRER_GATHER.md),
with [total emitted courier equations](proofs/gray_counterexamples/gray_layout_hardwirer.py)
and [GH1 data equations](proofs/gray_counterexamples/gray_hardwired_gather.py).
It keeps Q8192/U128Q/lambda24/c104 and replaces neither the programme with
a64K instruction ROM nor its raw-holder reads with a head-centre lookup.
An arbitrary correct beta of at most Q bits remains a **premise**; the
test beta is random data. No own beta or final alphabet is certified.

The projected ProgrammeBit in physical holder j, copy t, is
beta[(rawGF(j)+t) modQ]. Fetch votes the five actual holders, including
their raw GF if corrupted. The18-bit courier has five stored copies and
one-site movement. It collects thirteen simulated Address bits at the
actual interior primaries3958..3970, returns to0, visits Address A to fetch
its programme bit, then returns to0 to write it. Its service Address
uses the receiving holder's computed native GF plus its copy offset,
an explicit raw-state control convention. The total component equations
have radius5, with native controls and later interpreter/flag ports
still explicit integration obligations.

The universal quiet execution finishes at3984+2A, at most20366 ticks.
GT0's original snapshot at1 precedes this hardwire. GH1 therefore makes
an **explicit schedule change**: first load20367, remote capture
20368+|off|Q. The furthest capture61328 still precedes16Q. Loads and
captures in stages2/3, all active/rest endpoints, U and special flag/write
deadlines remain unchanged. No shorter U follows. The preliminary frame
now has367 bits, retaining the original GT0 coordinates and appending
ninety courier bits. Actual final K and full programme/runtime fit remain
unproved.

The [component certificate](../figs/gray_counterexamples/GH0_hardwirer_gather_certificate.json)
pins both complete [GH0](../figs/gray_counterexamples/GH0_transitions.json)
and [GH1](../figs/gray_counterexamples/GH1_transitions.json) graphs and their
[GH0](../figs/gray_counterexamples/GH0_transitions.c)/[GH1](../figs/gray_counterexamples/GH1_transitions.c)
C equations. It records184320 exact symbolic data routes,17280 rest
identities,102 arbitrary replacement vote cofactors and thirty actual
first-clean-update cofactors/9900 output assertions. The quiet source
identity covers every A and all five actual holders. The121730 retained
physical courier checks,10050 arbitrary whole-cell/native replacement
checks, and192 compiled/scalar/backend comparisons for each component
are measured corroboration, separately scoped from the universal proofs.
Their [courier traces](../figs/gray_counterexamples/GH0_physical_courier_traces.npz)
and [GH0](../figs/gray_counterexamples/GH0_backend_inputs.npz)/[GH1](../figs/gray_counterexamples/GH1_backend_inputs.npz)
backend inputs are retained. An
[initial validator tuple/list normalization failure](../figs/gray_counterexamples/GH0_initial_validator_serialization_failure.json)
is retained; it did not change classification or component equations.

Under canonical geometry/common clock, h1 supplies correct computed
GF/Age/flags despite two arbitrary complete-cell replacements. That
native word/flag argument and3-of5 source votes prove conditional E0
local transparency. The h1 correction is explicit. The
[raw-holder source example](../figs/gray_counterexamples/GH0_raw_holder_programme_witness.json)
with its [exact beta](../figs/gray_counterexamples/GH0_raw_holder_witness_beta.bin)
shows why the actual lookup matters: one prepared E0 at(0,3983) changes
GF0 to1; beta0=1,beta1=0 gives five reads(0,1,1,1,1) and five correct
auxiliary writes1. A head-centre lookup would give0. This positive repair
example is prepared, with no claim of intact own-hierarchy reachability.

For arbitrary correct beta the terminating367-bit recursion gives an
intact preliminary H in E(H) at every level. The sole shared original
real1 history remains three SimBit overwrites at(4009,1),(4010,1),(4011,1).
No native/control bit is changed; the courier reads SimBit only in the
disjoint Address-collection strip, so this error cannot change its
packets, programme fetch or auxiliary write. Under the printed-native
and pre96Q Workspace-pulse contract, the literal Flag2 defect and h1
change do not enter this trajectory: both native flags remain0.

The delayed first snapshot now sees the persistent wrong primary4010.
First-stage History1 at−4182/lane+1 and12202/lane−1 captures1 at28560,
then retains it throughout[16Q,32Q); SimBit4010 remains1. At24Q these
three discrepancies are therefore simultaneous in colonies−1,0,1,
outside any fixed box[jQ,(j+2)Q). The documented second-stage56Q footprint
also survives. This closes the hardwire/read/snapshot/retention dependency
for **this component**, conditional on its native/pulse interface. It
does not produce a faithful complete Gray rule, refute the corrected
Gray theorem, or show decoded memory or iid failure. Own beta<=Q,
final K, evaluator runtime and late computed-SimBit/wipe/order refinement
remain open. The accepted GT0/order radius obstructions retain their
original scopes. The [standalone validator](proofs/gray_counterexamples/validate_gray_layout_hardwirer.py)
replays the new checkpoint without rewriting older certificates.

**GMW4: generic affine physical IO still fails Q storage and the active deadline.**

The new [affine evaluator audit](proofs/gray_counterexamples/GMW4_AFFINE_COMPILER_ATTEMPT.md)
replaces repeated field-address helper calls with two generic finite
instructions. They compute base+s1*R[i1]+s2*R[i2] without truncating
overflow and perform actual one-site head travel/bit IO. The total
changed rule retains Q8192/U128Q/lambda24/c104, h1, holder-computed
service Address, zero Workspace outputs, and immutable instruction/CODE
lookup; the full emitted programme includes the new virtual instruction
cases and generic saturating multiplication. The original GMW2/GMW3/GH
sources and receipts are unchanged.

The [Q-target emission](../figs/gray_counterexamples/GMW4_Q_full_attempt_listing.json)
uses a13-bitPC and Q-bit table:39544bits/1413instructions, with165invalid
instruction references and120out-of-range code labels. Its masked
attempted bitstream is retained and explicitly invalid. This exceeds
Q by31352bits; it is a failure of this specified emitter, with no
lower-bound conclusion for another compact evaluator. The separate
[64K emission](../figs/gray_counterexamples/GMW4_64K_full_attempt_listing.json)
uses16-bitPC:40188bits/1410instructions and no invalid references.
Exact decoding/reassembly proves static ROM/listing identity; universal
own-beta semantic equivalence remains unproved. Both machines have
total radius-five transitions; their respective represented frames
have1992/2007bits. Immutable64K lookup is an explicit storage departure
from Gray, not a silently supplied self-programme.

The [receipt](../figs/gray_counterexamples/GMW4_affine_full_attempt_certificate.json)
and [retained inputs/outputs](../figs/gray_counterexamples/GMW4_64K_full_attempt_replays.npz)
keep51prepared full-field comparisons, all matching. They provide
measured evidence only for universal equivalence. Runtime is76614..115920
updates; canonical101902, native birth76614, native commit115920.
Canonical execution saves only124updates relative to GMW2's102026,
despite a substantial static instruction-count reduction. This fetch
already reads a whole instruction per update, so programme-bit savings
cannot be counted as saved serial-fetch ticks.

The [exact prepared deadline trace](../figs/gray_counterexamples/GMW4_64K_prepared_deadline.npz)
retains all65535execution updates from a canonical upper neighbourhood
with preloaded lower eleven-lane Mem, zero Out/Scratch, quiet canonical
native controls and a single born head. Quiet five-copy coupling proves
this recurrence describes the physical evaluator. At Age120Q it is
still RUN atPC38105/Address5079. Output framebit2006 is0 versusexpected1
(mutable ProgramBitcopy4 atprimary5099, beta[2]=1); this is the only
different output bit. Rest retains it and all five actual Age0 Info
commits store0. This proves a no-error **prepared-context** decoded-field
deadline failure for the explicitly changed64K evaluator. It does not
certify intact hierarchy initialization, faithful gathering, or a flaw
in Gray's evaluator. A late HALT alone is not used as evidence.

The [standalone validator](proofs/gray_counterexamples/validate_gray_affine_word_machine.py)
reassembles both attempts, replays all retained comparisons and the
entire deadline recurrence, and checks actual rest/commit transitions.
An [initial provenance-check race](../figs/gray_counterexamples/GMW4_initial_validator_receipt_race.json)
is retained: validation was launched before the refreshed certificate
finished and rejected its older checker hash. Sequential validation
uses the completed certificate; there was no transition disagreement.
An actual own beta<=Q, universal runtime, physical gather/early flag/
special-write integration and complete encoded period remain unproved.
No shortenedU, corrected-Gray counterexample or iid conclusion follows.

**GMW5: full word-tape attempt and an actual prepared deadline failure.**

The [word-tape audit](proofs/gray_counterexamples/GMW5_WORD_TAPE_ATTEMPT.md)
keeps Q8192/U128Q/lambda24/c104 but explicitly changes SF data to100-bit
words, Mem to eleven words, and head metadata to six words plus sixteen
registers. It retains h1, holder-computed service Address, immutable code
fetch and fixed-zero Workspace outputs. Its alphabet is18537bits and
its represented191-word frame uses primaries4001..4191. Total raw-state
radius5 and real one-site operand travel are proved component properties.

The specified Q-code emission has26137bits/891instructions,105invalid
references and70out-of-range labels. The separate64K diagnostic uses
26542bits with no invalid references; neither is a Gray-faithful Q-bit
evaluator. The [receipt](../figs/gray_counterexamples/GMW5_word_tape_execution_certificate.json)
keeps128 native and62 full finite comparisons, all matching after
uninterrupted execution; the full measured range is23358..68254updates.
These finite comparisons do not prove universal own-beta equivalence.

The dense-mask [exact trace](../figs/gray_counterexamples/GMW5_64K_dense_mask_deadline.npz)
starts from coherent preloaded inputs and quiet lower controls with no
physical errors. At65535updates two represented words are wrong:
mode copy4 at4021 is1 versus0, and register7 copy4 at4076 is
0xb657f818b715a6e0aa8ce3b47 versus0x3f9. The pending head is SEEK at4113,
PC23773. Rest retains the wrong Out words and the actual Age0 transition
commits them to all five Info holders. The
[read-only validator](proofs/gray_counterexamples/validate_gray_word_tape_v5.py)
replays every tick/write, all retained comparisons and physical commits.
This is a proved **prepared-context decoded deadline failure for GMW5**,
not an intact hierarchy or Gray counterexample. Initial overflow,
generator and three changed-emitter failures retain their exact snapshots.

**GMW6: a complete prepared self-evaluator with extra immutable storage.**

The [token-word evaluator proof](proofs/gray_counterexamples/GMW6_TOKEN_WORD_EVALUATOR.md)
and [receipt](../figs/gray_counterexamples/GMW6_token_word_certificate.json)
give a new changed component at the same Q/U/lambda/c. The full emitted
programme has884 instruction words and15 data words, represented by899
nine-bit tokens:8091 beta bits, padded to8192. A separate immutable
dictionary has512100-bit words,406used. **Total immutable capacity is
59392bits**, not8192; even the used stores contain48691bits. The token
fit is not a Gray-faithful Q-bit programme. Word-addressed PC, dictionary
CODE, BITCODE, SIGNEXT/RSHIFT and changed scratch coordinates are explicit
new equations. Both finite lookup primitives have total raw-state behavior
and neither calls the whole transition/native/head interpreter.

Register/field contracts cover every represented native/SF word, actual
raw five-holder accesses, all14opcodes, all four SEEK kinds, invalid raw
metadata/targets/PCs, data/padding PCs and the old-Programme/fresh-printed
Programme distinction. Under coherent preloaded lower input tape and quiet
canonical native controls, these prove that the **actual emitted programme
evaluates the complete GMW6 local rule for every legal raw upper
neighbourhood**. The physical one-site-head/copy induction lifts this to
the lower evaluator and its five actual Info commits. No physical errors
occur in this theorem.

The [universal execution bound](../figs/gray_counterexamples/GMW6_execution_bound.json)
uses a conservative interval/finite-set control-flow calculation, with
every unknown branch followed and real operand travel charged. Its five
copy blocks are bounded by9759,9638,9517,9396,9334updates;269overhead gives
47913. Birth is112Q+1, leaving65535execution updates through120Q, so the
bound has17622updates of slack at unchanged U128Q. The separate wipe path
is bounded by1364. A comparison-fact hardening retained the old checker
and re-established the same bound; it changed neither kernel nor beta.
The [91 retained comparisons](../figs/gray_counterexamples/GMW6_full_replays.json)
all match and finish in1103..46188updates (canonical22044; upper wipe1103).
An initial validator/report minimum error is retained with its source
snapshots; it changed neither execution nor the universal bound. They are measured additional
checks; the universal theorem uses the written contracts and bound.
The [read-only validator](proofs/gray_counterexamples/validate_gray_token_word_v6.py)
re-emits both stores, independently decodes them, replays all inputs and
recomputes the universal bound.

GMW6 has a **proved noiseless prepared physical self-evaluation theorem**.
Its earlier input gathers, flag couriers, hardwirer and complete encoded
period remain unproved. Its Workspace.Flag1/2 outputs are fixed0, omitting
Gray's mechanism driven by simulated Flag1/Flag2; adding gathers alone
would not transplant his higher-error repair proof. The dictionary, word
layout and immutable execution remain departures. No continuing-E0,
real1/higher, intact-history, Gray-proof, iid or shorter-U conclusion is
claimed by that no-error checkpoint. G17 and all accepted earlier candidates
are unchanged.

**GMW6: separate continuing-E0 prepared execution extension.**

The subsequent [E0 coupling proof](proofs/gray_counterexamples/GMW6_E0_COMPONENT_COUPLING.md)
preserves the frozen evaluator kernel, emitter, programme, bound and
receipts. It proves a one-step identity for a quiet reference configuration:
canonical GF, common legal Age, all four native flags0, and five coherent
holders of every logical SF word. Logical heads/metadata/data may be
arbitrary legal words. If a current row replaces whole cells on any set D
with at most two sites in every eleven consecutive sites, then F6(Z)=F6(X).
Replacement values may change every control, native and SF bit adversarially.
The immutable ROMs remain constants of the rule.

Both geometry votes have three correct inputs; inconsistency and flag
front/source triggers cannot fire. The h1 healthy predicate clears a
corrupted self Flag2; new native flags remain0, and the raw-GF wipe is0.
Every actual incoming/destination holder group lies in the radius5 cone
and has at least three correct copies. All2200head bits,1100Mem bits,
100-bit SF words and computed service/phase controls are reconstructed
before interpretation. The quiet coherent family is closed under F6.
Induction therefore leaves raw discrepancies only on each **current** error
row, with no previous-row wake.

Original pure-E0 histories satisfy this row bound: an adjacent spatial
pair or singleton is(24,24)-separated from other groups, so an eleven-site
row cannot meet two groups. At the prepared evaluator's Age0 boundary,
each Info majority consequently decodes exactly the correct upper rule
output despite continuing arbitrary pure-E0 whole-cell replacements.
This is a **proved conditional prepared fifth-stage extension**, not a
whole encoded-period or higher-error theorem. Constant-zero Workspace is
essential to this quiet-family statement and remains a material departure.

The [receipt](../figs/gray_counterexamples/GMW6_E0_component_certificate.json)
and [read-only validator](proofs/gray_counterexamples/validate_gray_token_word_v6_E0.py)
pin156827 reduced native Boolean cofactors and3402 vote identities.
GF/Age payload independence is algebraic rather than sampled.8576 retained
full-cell comparisons and368 finite temporal holder updates are additional
measured checks. The temporal support is the original-E0 spatial pair
(0,1),(1,1), plus singleton(30,3), with all whole-cell values retained.
No earlier gather, nonquiet native front, real1/higher, intact hierarchy,
faithful-Gray, iid or shortened-U conclusion follows.

**GMW7: an explicitly changed complete encoded period.**

The [single-gather period proof](proofs/gray_counterexamples/GMW7_SINGLE_GATHER_PERIOD.md)
closes physical input preparation for a new isolated rule at unchanged
Q8192/U128Q/lambda24/c104. Its total local rule loads one Info snapshot at
computed Age32Q, moves lane j at speed one for |j-5|Q updates and freezes
it. All eleven lanes at all191 represented primaries therefore contain
the actual upper neighbours' words by37Q, well before the112Q reset and
112Q+1 head birth. This is a changed single-middle-gather schedule, not
Gray's three snapshots, history majority or early flag evaluation.

A new generic MADD5 arithmetic primitive reduces addressing overhead.
The full own programme has878 tokens/7902 bits and425 used dictionary
words; the total immutable capacity remains **59392 bits**, including
the separate51200-bit dictionary. Word100 IO, h1 erasure, holder-computed
Address controls, immutable instruction access and fixed-zero simulated
Workspace outputs remain explicit departures. In particular this does
not implement Gray's simulated-Flag1/2 repair pulses.

The proof gives all-raw own-programme equivalence and a universal49068
physical-update bound within65535 active updates. Under canonical lower
native geometry/common Age0/flags0 and five-copy coherent Info representing
arbitrary legal raw upper cells C, its actual U-tick period belongs to the
broad encoding family E7(F7(C)). Initial private fields and unrepresented
Info are arbitrary coherent values; no input-tape preload or alias equality
is assumed. Reset, gathering, instruction fetch/operand travel and old-Out
boundary commit are all actual equations of the new rule.

The same period/majority-decoder result holds for continuing pure-E0
whole-cell replacements under the original lambda24 group convention.
Every eleven-site current row contains at most two errors. Computed native
controls and all five-holder votes, including moving Mem sources, repair
that row before it can leave a wake. This is a **proved changed-rule
noiseless and pure-E0 period theorem**. Real1/higher repair and iid reliability
are unproved; pure E0 alone does not cover iid noise for all time.

The [period receipt](../figs/gray_counterexamples/GMW7_single_gather_period_certificate.json)
and [read-only validator](proofs/gray_counterexamples/validate_gray_token_gather_v7.py)
retain450571 tick/lane route identities and2101 source/primary captures.
The97 finite prepared comparisons (maximum47085 updates) and14807
full-cell fault comparisons are supplementary measured checks. All replay
and fresh bound checks pass. No shortened U, faithful-Gray counterexample
or memory-failure theorem follows from this milestone.

**GMW7: a permanent native-clock island from its intact hierarchy.**

The [stationary clock-island proof](proofs/gray_counterexamples/GMW7_WF0_CLOCK_ISLAND.md)
uses the [root-certified intact recursive initializer](proofs/GMW7_INTACT_HIERARCHY.md).
At physical tick0 overwrite only Age with1 on[0,17Q), leaving every
other native/SF field intact; there are no later errors. The shared
139264-site error row is one actual real2 under original lambda24/c104.
It is outside the preceding pure-E0 theorem's hypotheses.

In the actual full GMW7 rule, GF remains canonical, F2 and Workspace
remain0, and Age is(t+1)modU inside this same interval and tmodU outside,
forever. F1 at rowt is exactly[-h_t,0) union[17Q-h_t,17Q), with
h_t=min(3t,Q). It saturates to the two preceding colonies by tick2731.
The native orbit is then periodic with periodU and zero translation.
It has a bounded17Q spatial clock hull and **infinite temporal lifetime**.
No finite space-time native-clock erasure envelope can contain it.

This is a **proved obstruction to the explicitly changed fixed-WF0
variant**, not a contradiction to Gray: his simulated-flag repair is
omitted here. Address stays correct, and no decoded memory or iid
failure is inferred. Changing only private programme/dictionary/SF
equations cannot remove this orbit while the native equations and
constant-zero Workspace interface stay unchanged. A native/interface
change is necessary; no sufficient or smallest reliable repair is proved.

The [receipt](../figs/gray_counterexamples/GMW7_WF0_clock_island_certificate.json)
and [read-only validator](proofs/gray_counterexamples/validate_gray_token_gather_v7_clock_island.py)
pin232496 actual-scalar cofactors,8192 phase identities and633714 exact
transient event segments. The binary-clock factor and event compression
are proved, not assumed from a finite simulation. Whole20-bit clock
translation and arbitrary evolving SF independence are algebraic.

**Authentic simulated-flag commands: conditional contract and a GMW7 timing gap.**

The [command contract](proofs/gray_counterexamples/GRAY_FLAG_COMMAND_CONTRACT.md)
separates Gray's native upper trigger from its physical source preparation.
Four null right raw Address words imply that the adjusted right vote has
no majority. With correct left Address inputs, common left Age A, no old
Flag2 ones and no Workspace2 source, both the printed and h1 native rules
compute Flag1=1 and Flag2=[(A+1)mod16=0]. A clock mismatch alone does
not force this Flag2 trigger. The actual null bank and the upper Age
progression remain premises, not consequences of a presumed clean snapshot.

Gray's p41 predicates then force a five-site Workspace2 seed when the
**final computed** left-end SimBit is1, computed Age is in96Q..98Q and
the readers' computed Flag1 is0. That seed forces native Flag2 on the
next update, even with arbitrary whole-cell replacements satisfying the
stated one-row two-fault density bound. This is a conditional seed lemma,
not a continuing-noise erosion theorem. The finite nonadjacent supports
test the stronger algebraic bound; not every such support is classified E0.

On GMW7's accepted intact clock-island history, Info stays fixed through
the first pulse window, so both unused end-source words remain0. Its
head is born at computed Age112Q+1; there is no third-stage evaluator or
special flag courier. Adding only the pulse predicates to those unchanged
source values would therefore produce no first-window command. This is
a proved **changed-interface gap**, not a Gray counterexample or an emitted
candidate. The hypothetical early38Q pass remains a conditional engineering
route requiring new equations, output preservation and an own-programme proof.

The [receipt](../figs/gray_counterexamples/Gray_flag_command_contract_certificate.json)
and [read-only replay](proofs/gray_counterexamples/validate_gray_flag_command_contract.py)
retain40960 adjusted-vote cases,16170 printed/h1 native-input cofactors,
135605 shared-support seed cases and216 actual F7 source neighbourhoods.
Gray's actual damaged input bank, progressing upper Ages, early temporal
vote/evaluator, source retention/wipe, composite locality and eventual
wave recovery remain **unproved**. Q8192/U128Q/lambda24/c104, all previous
rules and the59392-bit GMW7 immutable-storage accounting are unchanged.

**GMW7: the required null Address bank occurs in its actual first gather.**

The [clock-gather bank proof](proofs/gray_counterexamples/GMW7_CLOCK_GATHER_BANK.md)
uses the same intact X and shared clock-only real2 row, with no preloaded
bank or independent upper history. At each logical Mem group at least
three holders share the centre's clock label, so their identical phase
updates determine its bitwise vote. This gives an exact voted-Mem factor
without assuming raw-copy coherence at the clock boundaries.

For normal residue p and lane d its actual capture source is
(g+d)Q+p+sign(d)(e_source-e_receiver), where e=1 on[0,17Q) and0 outside.
Right-crossing sources shift by one word to p-1. Thus the complete,
native-Flag1-set colony16 really has five null right Address inputs;
quiet colony15 has four. Their left Age inputs are0, so both banks
compute upper Age1, Flag1 one and Flag2 zero at this first evaluation.
The initial missing-colony bank premise is closed for **changed GMW7**;
the later-map result below closes sixteen actual periods, while an
authentic early command remains open.

The [receipt](../figs/gray_counterexamples/GMW7_clock_gather_bank_certificate.json)
and [read-only replay](proofs/gray_counterexamples/validate_gray_clock_gather_bank.py)
retain60929 exact compressed capture paths and480 complete1100-bit group
checks against2400 actual holder transitions. Capture-source and retention
claims follow from the coordinate/majority proof; finite cofactors supplement
it. Gray's different Mailbox-on-Flag1 erasure and three-gather protocol
are not verified by this bank result. No candidate or schedule changed.

**GMW7: sixteen actual distorted-bank evaluations from the same history.**

The [stroboscopic proof](proofs/gray_counterexamples/GMW7_CLOCK_STROBOSCOPIC_NATIVE.md)
extends the identical-candidate centre-clock factor to every SF field,
including head execution and commit. Actual input capture, zero padding
at4000/4192, per-colony head bounds and asynchronous commits close the
repeated physical map. The emitted programme reads displaced native flag
words only through low-bit masks, so its legal-input equivalence also
applies to these real captured tapes. The zero upper Head/Mem/Out/Scratch
family closes; Info remains legal without an upper-copy-coherence premise.

An exact full-F7 finite coupling, with clean infinite-line exterior and
explicit dependency margins, certifies the first sixteen actual represented
upper rows. The first failure of a common upper Age occurs at evaluation5,
colony2: three crossed left inputs provide old Flag1=1 as their Age word,
and the right Flag1 wave makes the rule choose that left majority. Its
represented Age becomes2 instead of5. Right-edge Ages at13..16 are common
through evaluation9, then(6,6,10,10), then(6,6,7,7) through evaluation16.
Flag2 remains0 inside colonies0..16 in all sixteen rows. The proposed
sixteen-common-Age continuation premise therefore fails on this **actual
changed-GMW7 trajectory**. It is not a counterexample to Gray's different
gathering or early flag protocol.

The [receipt](../figs/gray_counterexamples/GMW7_clock_stroboscopic_native_certificate.json)
and [read-only replay](proofs/gray_counterexamples/validate_gray_clock_stroboscopic_native.py)
pin256 all-SF group checks against1280 actual holders,4208 exact full-rule
cofactors and six paired raw/normalized emitted-programme executions.
The finite identities and physical-contract proof establish the scoped
sixteen-period conclusion; the programme comparisons are supplementary.
The initial instrumentation incorrectly treated an Out store as a raw
input read; its source/log remain pinned. No rule or schedule changed.
Gray refinement, general later recovery and iid memory remain **unproved**;
the extra51200-bit dictionary and fixed-zero Workspace departure remain.

**GT0: printed Mailbox erasure supplies actual second/third native banks.**

The [erasure-bank proof](proofs/gray_counterexamples/GT0_CLOCK_ERASURE_BANK.md)
uses the frozen bit transducer's actual Mailbox-on-Flag1 erasure and three
separate gathers. It is a conditional prefix for any completion retaining
those equations, the printed native rule/published Workspace window, and
an intact compatible interior native-bit layout. It does not assume a
preloaded bank or an independent upper error. The one Age-only clock row
has the original real2 location set; a GT0 completion's alphabet and intact
state are not silently identified with GMW7's different ones.

Before the third captures, the published Workspace window forces0 and
native Flag1 saturates the two predecessor colonies-1/16 by2731 ticks.
The actual five-copy Mailbox votes are zero inside these barriers. Outside
them at least three holders are both unflagged and share the logical
centre's clock, so the unmasked centre operation determines the vote.
History banks follow the centre clock without a Mailbox mask. These
factors cover raw boundary-copy incoherence.

At physical row70Q, History2 and History3 agree on all represented native
bits. Receiver15 has correct self/five-left native words and five null
right words. Receiver16 has correct self and all ten nonself words null.
Both banks compute GF equal to the receiver, Age1, Flag1 one and Flag2 zero.
Their temporal majority with **any** first bank is the same input, so the
damaged first gather does not alter this available native-bank result.
An actual early evaluator and its delivery of flags are still missing;
the GT0 Voted field itself is scheduled later and is not claimed to have
already executed this early majority.

The [receipt](../figs/gray_counterexamples/GT0_clock_erasure_bank_certificate.json)
and [read-only replay](proofs/gray_counterexamples/validate_gray_clock_erasure_bank.py)
certify1148 clock/boundary groups,182696 free-bit actual output identities,
and360052 interior-primary route/erasure identities. This closes the
intended blocked-mail native bank for the specified component/prefix;
it contradicts no Gray claim. Final layout/K, own beta, early execution,
retention through later repair commands and the whole faithful Gray rule
remain **unproved**. No existing component, schedule or U changed.

**GE0: actual early native evaluation and flag delivery for that prefix.**

The [early component proof](proofs/gray_counterexamples/GE0_EARLY_NATIVE_FLAGS.md)
and [total ported equations](proofs/gray_counterexamples/gray_early_native_flags.py)
connect actual GT0 History1/2/3 votes to a physical moving head. LOAD forms
their temporal majority at the actual raw holders, rather than reading a
preloaded bank. The emitted [native beta](../figs/gray_counterexamples/GE0_native_prefix_beta.bin)
and [listing](../figs/gray_counterexamples/GE0_native_prefix_listing.json)
have2346 bits/107 instructions and preserve the literal printed native
clauses. This is a native-prefix programme, **not a whole own beta**.

GE0 declares a2462-bit component frame at residues2865..5326 and native
columns2865..2901. It adds an early reset at69Q+3, birth at69Q+4 and run
before75Q; the34396-tick register/operand-travel bound gives halt at
Age599648. Two speed-one flag couriers seeded at75Q reach3/Q-3 by
617296/619691, before the existing GT0 delivery at655359=80Q-1. This is
an explicit early schedule/interface addition; all five original stage
endpoints, total U, lambda24 and c104 are unchanged.

On the same conditional intact-layout/shared clock-real2 prefix, the two
derived banks in receivers15/16 produce GF equal to the receiver, Age1,
Flag1=1 and Flag2=0. The actual Head/EarlyOut/courier equations and all
five source holders deliver those flag bits. The
[receipt](../figs/gray_counterexamples/GE0_early_native_flags_certificate.json)
pins34544 actual local head calls for each derived bank,8205 courier calls
per retained case, and all five reset/birth/target checks. The
[read-only replay](proofs/gray_counterexamples/validate_gray_early_native_flags.py)
also checks444 retained-History outputs. A separately labelled prepared
common-Age15 bank produces Flag2=1; its reachability from the clock fault
is **unproved**. Finite replays supplement the register/copy/route proofs.

The reviewed initial GE0 port gate mistakenly included Age98Q. Gray p41
uses[96Q,98Q); the corrected gate is half-open. The exact
[old kernel](../figs/gray_counterexamples/GE0_workspace_endpoint_initial_kernel.py.txt),
[old receipt](../figs/gray_counterexamples/GE0_workspace_endpoint_initial_certificate.json)
and other initial sources/logs linked from the proof are retained. A
canonical endpoint cofactor gives old Workspace(1,1), corrected(0,0).
This is our component transcription defect, not Gray's; the early theorem
ends before80Q and is unchanged.

Late Workspace and fifth stores remain finite integration ports. The
immutable raw-Address beta access, own full beta<=Q/final self-layout,
Gray ProgrammeBits/hardwirer refinement, final computed-SimBit/wipe order,
late pass/commit, later native-bank progression and all higher-error/iid
claims remain **unproved**. General E0 raw-GF birth transparency is not
claimed. No registered component or active G17 is changed, and no shorter
U, faithful Gray refutation or global reliability theorem follows.

**GE0: actual first native banks and delivered flags at every receiver.**

The [all-receiver extension](proofs/gray_counterexamples/GE0_GLOBAL_FIRST_FLAGS.md)
uses the same shared clock-only row0 fault and conditional intact
completion premises. Its actual second/third History word at offset d
is the original canonical native word of g+d when d=0, or when the
inclusive integer-colony interval from g to g+d avoids both barrier
colonies−1 and16. Every other nonself record is the all-zero word,
supplied by the physical Mailbox erasure. Surviving routes have the same
clock phase and exact source residue; no independently chosen upper
history, preloaded bank or ±1 word displacement is used.

The emitted early native programme produces GF=g modQ and Age1
everywhere, Flag2=0 everywhere, and Flag1=1 exactly in
{−3,−2,−1,13,14,15,16,17,18,19}. The accepted physical GE0 induction
then delivers all five corresponding special SimBits by physical80Q−1.
The [receipt](../figs/gray_counterexamples/GE0_global_first_flags_certificate.json)
retains the finite noncanonical native-bank table,28 actual emitted
programme executions and affine route endpoint checks for every
interior native residue. Its
[read-only replay](proofs/gray_counterexamples/validate_gray_global_first_flags.py)
passed. Outside the finite affected receiver intervals, canonical native
closure gives the result for every integer receiver.

At g=−4, two good right GF records and one adjusted null record coincide
and form a correct majority; Flag1 remains0. This rules out a simple
null-count heuristic. The extension establishes the first actual flag
source bits, while late Workspace composition, later reachable native
banks, full own beta/layout, Gray refinement and all-time/noisy claims
remain **unproved**. No candidate, schedule or earlier receipt changes.

**GE0: first literal Workspace/native pulse, conditional on late refinement.**

The [first-Workspace proof](proofs/gray_counterexamples/GE0_FIRST_WORKSPACE_NATIVE.md)
adds the explicit premise that a completion implements Gray p41's late
Workspace equations using the final computed SimBit. GE0's own kernel
still has late ports; their physical whole-rule implementation and
all-raw order/locality are not supplied. On this prefix, canonical GF
makes SF wipe false, and all five special SimBit copies hold the actual
early delivered commands. Their computed final values are the same held
bits, so no clean global snapshot or independently selected command is
assumed.

The native fields close on clock label0/1, Flag1 and Workspace1; Flag2
and Workspace2 stay0. The
[interval kernel](proofs/gray_counterexamples/ge0_first_workspace_native.c)
updates the infinite line, deriving its exterior from the old support
and finite source strips on every row. It retains computed-Age timing:
the offset colonies can enable Workspace one physical row earlier, and
new Workspace enters the native Flag1 rule only on the next update.
The source window is[96Q,98Q).

The [receipt](../figs/gray_counterexamples/GE0_first_workspace_native_certificate.json)
certifies32770 updates from row786430=96Q-2 through819200=100Q, using
9962211 exact event intervals, at most27 state segments/391 event cuts.
The independent literal-scalar checker tests81672 retained event endpoints;
the [read-only replay](proofs/gray_counterexamples/validate_ge0_first_workspace_native.py)
and parent replay passed. The clock interval first becomes exactly[0,20Q)
at797352. At806912, and still at100Q, Flag1 is exactly in predecessor
colonies−1/19, GF is canonical and Flag2/Workspace flags are0.

This first command grows the offset-clock interval17Q to20Q and does
not yet recover a common clock. It is **not a counterexample** to Gray's
recovery argument; later Flag2 repair remains possible. Exact finite
computation is backed by the native quotient/event-partition proof.
Final own beta/layout, continuing native writeback, reachable later banks,
all-raw late refinement and any whole Gray/iid result remain **unproved**.
No earlier component, schedule endpoint, U or active rule changes.

**GE1: changed native-only fifth writeback and the next actual bank.**

The [GE1 proof](proofs/gray_counterexamples/GE1_NATIVE_WRITEBACK_SECOND_BANK.md)
closes one specified store interface. Its
[local equations](proofs/gray_counterexamples/gray_native_writeback_ge1.py)
replace the fifth-store ports at the37 native primaries[2865,2902) by
the actual old five-holder EarlyOut vote. Service lookup uses the
holder's computed native GF plus its copy offset. The existing112Q
reset,112Q+1..120Q-1 write window and Age0 old-Nextbit commit are
retained. This **explicit native-only mirror changes the fifth writer**;
it does not implement Gray's full fifth own programme. Non-native
fifth stores and both late Workspace outputs remain finite ports.
Own beta<=Q, final intact layout and the literal final-computed-SimBit
Workspace completion remain explicit premises. No stage endpoint,
U, accepted earlier component or active rule changes.

On the same shared row0 Age-only real2 fault[0,17Q), without later
errors, the accepted actual first gathers and early programme supply
Z1(g)=(GF=g modQ,Age1,Flag1=1[g in D],Flag2=Workspace1=Workspace2=0),
D={−3,−2,−1,13,14,15,16,17,18,19}. The native EarlyOut copies survive
the first Workspace prefix. GE1 commits all37 normal native SimBits
and their five holders at physical U-e20(g), e20(g)=1[0<=g<20].
The native quiet form continues through the next gathers. Their actual
History2/3 native records are Z1(g+d) on self or barrier-free paths,
and zero on nonself paths meeting colony−1 or19. Surviving routes have
one clock phase and the exact same primary residue. No upper bank is
preloaded and no separate upper history is chosen.

The [receipt](../figs/gray_counterexamples/GE1_native_writeback_second_bank_certificate.json)
retains8880 actual local copy/gate/commit checks,160 five-holder payload
cases,3960 actual History captures,540 reset/hold checks,1364 affine
route endpoints and33 emitted native-prefix replays on the derived
banks. The [read-only validator](proofs/gray_counterexamples/validate_gray_native_writeback_ge1.py)
and [parent replay](../figs/gray_counterexamples/GE1_native_writeback_root_replay.log)
passed. The actual native function on those next banks gives Ages
2,1,1,1,1,2 at receivers18..23. Thus a global common-Age progression
has not been established; later Flag2 repair remains open. This is a
**conditional changed-component bridge**, not a faithful Gray rule,
full-period/noisy theorem, shorter-U result or counterexample to Gray.

The first checker-only packed-beta comparison mistake and an unexecuted
automatic-approval timeout are retained and pinned separately in the
new receipt. They make no claim about a mathematical rule failure.

**GE2: second actual early delivery and conditional Workspace/native pulse.**

The [GE2 proof](proofs/gray_counterexamples/GE2_SECOND_NATIVE_PREFIX.md)
extends unchanged GE1 on the same shared row0 clock-only real2 history.
Its stage0 capture and the previously derived later History banks supply
the actual B1 native input to the second early interpreter. No upper
state, tape or command is independently selected. The native-only fifth
mirror, non-native ports, own beta<=Q/final intact layout and literal
final-computed-SimBit completion premises remain explicit. No candidate,
schedule endpoint, U, earlier component or active rule changes.

The actual34396-tick head evaluation and speed-one couriers deliver all
five source copies by physical U+80Q-1. Flag1 is1 exactly on
D2={-4,-3,-2,-1,10,11,12,13,14,15,16,17,18,19,20,21,22}; Flag2 is0
everywhere. The derived upper Age is1 at-1 and19..22, and2 elsewhere.
Thus this calculation uses the actual noncommon upper Ages and does not
assume the progression needed for a later positive Flag2 source.

Under the retained literal late Workspace completion, the native fields
close on clock label0/1, Flag1 and Workspace1. The new event instance
uses the derived D2 sources and exact old-Workspace latency. It certifies
32770 infinite-line updates and12502342 event intervals, at most48 state
segments/547 cuts, supplemented by102420 independent literal-scalar
retained endpoints. The clock support first becomes exactly[0,23Q) at
physical1845928. At1855488 and through U+100Q, GF is canonical, the clock
offset is1 on[0,23Q), Flag1 is exactly in predecessor colonies-1/22,
and Flag2/Workspace flags are0. The second actual pulse grows20Q to23Q;
temporary growth is **not a counterexample** to eventual Gray repair.

The [receipt](../figs/gray_counterexamples/GE2_second_native_prefix_certificate.json)
pins the new sources, accepted dependencies and actual receiver18/19/20
head/carrier/reset/birth checks. The
[read-only validator](proofs/gray_counterexamples/validate_ge2_second_native_prefix.py)
passed147.799s and the
[parent replay](../figs/gray_counterexamples/GE2_second_native_prefix_root_replay.log)
passed149.256s. The original
[proof and receipt](../figs/gray_counterexamples/GE2_second_prefix_initial_certificate.json)
are retained with a proof-only clarification: boundary fixtures are
vote-equivalent representatives for observed fields, rather than a claim
that unused fields or minority raw ghosts vanish globally. The checker,
component and computed results stayed unchanged and were fully replayed.
Full own beta/layout, all-raw late order, later reachable banks/Flag2
repair, whole Gray/iid and shorter-U conclusions remain **unproved**.

| Step or target | Status | Scope |
|---|---|---|
| Q ≥ 8192, U = 128Q, λ = 24 and c = 104 are printed choices | **proved from primary text** | Full programme size remains “sufficiently large.” |
| Disputed Flag2 clause is present in the original PDF | **proved from primary text** | Page image and source hashes retained. |
| Singleton is E0, with no real1 errors | **proved** | Exact location set and classifier retained. |
| Printed Proposition 2's Flags assertion fails at time 2 | **proved counterexample** | Stated intact initialization; no boundaries, later errors or all-time Workspace premise. |
| Singleton persists forever | **proved conditionally** | Native invariant with all-time Workspace flags zero. |
| Adjacent-pair failure of the single-token repair; h = 1 local minimum | **proved** | Restricted healthy erasure predicate; no global sufficiency. |
| GR0 own abstract programme | **proved** | Physical input/transport/fetch hypotheses remain explicit. |
| GR0 singleton full-rule local restriction | **proved** | Shared arbitrary simulation inputs; zero input Workspace flags. |
| Scalar/circuit comparisons and random programme replay | **measured only** | Actual inputs or reproducible replay retained. |
| Bounded-clock restriction to the corrected native operator | **proved** | All error Ages ≤ 5U/8, horizon 1+U/32; published computed-Age Workspace gating. |
| Noiseless canonical Address/common Age invariant | **proved** | All 8192 phases, symbolic common Age and all 44 native flag inputs; no Workspace-zero premise. |
| Native backends and E0 observation masks | **measured only** | 16 three-backend and 28 independent NumPy/CUDA full updates. |
| 32 real1-only and 20 mixed corrected-native recovery cases | **measured only; no counterexample** | Original λ24/c104; exact errors and values retained. |
| Universal corrected-native Proposition 2 recovery and speed estimates | **unproved** | Finite negative searches do not establish these claims. |
| Published stage arithmetic and sixteen physical obligations | **proved from primary text / explicit checklist** | Detailed interpreter and damaged-clock refinement remain open. |
| Computed-SimBit radius ≥ 8 witness | **proved conditionally** | Explicit no-other-SimBit-write premise at computed Age 96Q+1; exact native cofactors. |
| Unconditional radius-5 completion obstruction or noisy memory failure | **unproved** | No full physical completion or encoded-history reachability certificate. |
| GR0 physical continuing self-simulation and Gray-protocol faithfulness | **unproved** | Matching constants do not establish these. |
| GR1 tracked transport/reset and copy transparency | **proved conditionally** | All control classes; coherent-copy/correct-control and programme-write premises explicit. |
| GR1 concrete ROM fit and own abstract programme | **proved** | Fresh fifth-stage replay; physical input/frame/write hypotheses remain. |
| GR1 64 random abstract replay vectors | **measured only** | Zero observed mismatches; universal certificate is separate. |
| GR1 Match courier and outside-key instruction irrelevance | **proved conditionally / proved** | Match routing needs coherent copies and correct native controls; outside-key irrelevance is an all-raw gate argument. |
| GR1 nonmatch frame and actual tracked-field pending coupling | **proved conditionally** | 175 route classes and free common clock/all native flags; coherent data premises explicit. |
| GR1 healthy-geometry clean Flag clearing | **proved** | 22 cofactors plus two-cell prefix/suffix induction; no later errors. |
| GR1 noiseless encoded period and continuing boundary decoding | **proved** | Written universal composition for the broad E family; no errors. |
| GR1 one-tick raw-GF wipe wake and next-tick healing | **proved** | Actual broad-E context and original singleton E0; Gray intact recursive reachability unproved. |
| GR1 flag quieting with continuing pure E0 | **proved** | 616 exact cofactors, ten-tick charge spacing and 98Q+9104 bound. |
| GR1 pure-E0 period lift and continuing boundary decoding | **proved** | Written majority/wake/controller/front induction; arbitrary replacements, original λ24. |
| GR1 real1 Age=U−1 early commit, clock advection and recovery | **proved** | Exact finite Boolean cone and620 native cofactors/count argument; broad E initialization. |
| GR1 literal pointwise all-SF two-colony envelope | **refuted** | Simultaneous three-colony Info/Mail footprint under one real1; no boundary memory claim. |
| GR1 explicit stationary intact recursive initialization H∈E(H) | **proved** | Terminating integer recursion covers every represented field, all five Info slots and unused/special0 primaries. |
| GR1 clock/commit and three-colony footprint from that intact hierarchy | **proved counterexample to the pointwise envelope** | Only the original five-site real1 error; two later history banks and all-receiver early flags certified. |
| GR1 first boundary and later decoded hierarchy for this particular error | **proved correct** | Both later banks encode q; full upper counterfactual gives F(q)=F(H), then X_U∈E(F(H)). No arbitrary-real1 theorem. |
| Faithful Gray Proposition4 pointwise-field counterexample | **unproved** | Printed statement/transport argument distinction identified; GR1's intact-context result does not settle its Gray refinement gaps. |
| Literal-native closure for the three-copy SimBit-only real1 core | **proved under the published pulse premise** | All8192 literal phases and free common Age; preserves printed Flag2 predicate and all native fields. |
| Literal raw-gather/record-retention stage axioms versus Proposition4 | **proved conditional incompatibility** | Three-copy real1; second-stage Workspace records in both receiving colonies contradict a fixed adjacent pair. Exact G,R realization remains unproved. |
| Arbitrary-programme recursive initialization data compatibility | **proved conditionally on an admissible final layout** | Symbolic beta/marker choices; no all-zero-programme premise or actual compiler/field-size certificate. |
| GT0 emitted raw gather/local record/retention and tracked rest equations | **proved** | Exact component transitions; coherent data and correct native controls; no actual Gray programme refinement. |
| GT0 preliminary recursive data frame and first56Q three-colony footprint | **proved conditionally** | Symbolic correct programme bits and supplied printed-native/pulse controls; one shared SimBit-only real1 history. |
| GT0 C-source gate mapping / compiled backend comparisons | **proved / measured only** | Structural source correspondence;600 retained compiled input/output comparisons. |
| GT0 plus literal native/p41 requires radius at least8 | **proved** | Full raw-state local component-set obstruction; no encoded-history reachability or universal Gray nonexistence claim. |
| GT0 self-programme, final layout, flag results and whole-period completion | **unproved** | Explicit ports and preliminary frame; no faster-U or iid result. |
| Meaning/order of computed SimBit as final versus pre-wipe value | **source audit / explicit interpretation choice** | Native final-value analogy supports an inference; full damaged-state SimBit table is implicit. |
| Deleting only source wipe still leaves radius at least8 | **proved** | Second GT0 all-raw Age8/commit witness, future ports free; no reachability claim. |
| Raw current-primary read's local E0 source-copy transparency | **refuted** | Singleton primary corruption produces five false WF2 outputs under canonical pulse controls; full encoded snapshot unproved. |
| GV0 voted-current Workspace interface and local source-copy correction | **proved changed component** | All raw states radius5;66 routing identities and102 vote cofactors; no full-rule or noisy-period lift. |
| Radius8 literal-source composition support /17-lane gather arithmetic | **proved conditionally / proved** | Complete source SimBit must itself be radius5; programme/runtime and final frame remain open. |
| Larger-radius native/SF confinement, E0 period and higher noisy lift | **unproved** | Location-set geometry is unchanged, but deterministic interface obligations cannot be borrowed unchanged. |
| Supplied Gács programme-source version and finite-constant applicability | **source audit / unproved fit** |2024 corrected printing uses §§9.1-9.3; unknown coefficients and no emitted self-beta; no citation refutation. |
| GPN0 native bitstream semantic equivalence and total abstract evaluation | **proved** |2919 gate/35 output-map identities for every raw native input;128 retained random replays measured only. |
| GPN0 Q8192 native-prefix space and fresh serial-fetch runtime | **proved obstruction** | Separate-module bit-SSA encoding;76389bits, fresh one-bit/tick fetch; no lower bound for word/loop or parallel evaluators. |
| GMW0 compact emitted native word programme | **proved** |2346bits/107instructions; literal native35 outputs by register invariants;98 retained replays measured only. |
| GMW0 all-raw local interpreter and noiseless physical native execution | **proved** |2272-bit tentative frame, radius5;34396 physical ticks, unique head, operand travel, rest and old-Out commit; input tape preloaded and native WF outputs forced0. |
| GMW0 continuing-noise computation and faithful gather/flag integration | **unproved** | Quiet native-prefix theorem does not establish E0 recovery or a whole-period map. |
| GMW1 full Q-code emission fit/reference obstruction | **proved** |42850bits/1829instructions/268 invalid references; this specified emission only. |
| GMW2 all-raw component, final component alphabet/layout and radius5 | **proved changed component** |2007bits; h1, zero Workspace, holder-computed service and immutable64K ROM explicit. |
| GMW2 emitted proposed full beta and finite ROM identity | **proved fit/identity; semantic equivalence unproved** |44730bits/1863instructions/16-bitPC fit separate64K ROM; exceeds Gray Q storage. |
| GMW2 quiet-copy closure and pure-E0 component transparency | **proved** | Arbitrary coherent SF data under canonical/common-clock/native-flags0 reference; no real1/higher theorem. |
| GMW2 full-field programme comparisons | **measured only** |70 retained finite inputs; no universal equivalence/runtime proof. |
| GMW2 prepared no-error fifth-stage decoded-field failure | **proved** |65535 exact update recurrence/rest/commit; ProgramBitcopy4 at5099 wrong; preloaded non-intact upper context. |
| GMW2 dense upper raw-head remaining16Q output obstruction | **proved** |132803 uninterrupted updates; output wrong after16Q-1; not an intact hierarchy or evaluator lower bound. |
| GMW3 raw-state three-site transport and radius-five locality | **proved changed component** | Zero-padded five-nominal-value votes; inherited service/ROM/zero-Workspace departures explicit. |
| GMW3 unpaused transport under an original-E0 history | **refuted** | Exact pair/singleton holder history, prepared SEEK head, loss after nine updates; no intact hierarchy or Gray attribution. |
| GMW3 paired restoration and continuing pure-E0 component coupling | **proved** | 67 arbitrary-support cases and two-tick diameter-20 isolation; arbitrary coherent SF data, canonical/common native reference. |
| GMW3 proposed own emission and finite comparisons | **proved fit/identity; measured semantic checks only** | 58,129 bits / 2,410 instructions / 86 comparisons; separate 64K ROM, universal beta identity open. |
| GMW3 canonical decoded outputs at the active deadline | **proved for this finite input** | Correct at 65,535 despite an unfinished head; halt delay alone is not a decoded-field failure. |
| GMW3 prepared dense-HLT wrong represented boundary commit | **proved** | 327,675 actual holder transitions and five Info commits; preloaded non-intact context, unchanged 128Q schedule. |
| GMW3 faithful full-period self-simulation and faster schedule | **unproved** | Universal beta/runtime and physical gather/early-flag/special-write integration remain open. |
| GH0 total five-copy hardwirer, actual raw-holder programme source and radius5 | **proved component** | Arbitrary beta<=Q premise; native controls are integration ports, no own beta. |
| GH0 quiet source identity and completion before GH1 load | **proved conditionally** | All A; stable represented Address/canonical quiet native controls; worst20366<load20367. |
| GH0/GH1 local complete-cell E0 copy transparency | **proved conditionally** | Explicit h1 native correction; arbitrary two-holder payloads;10050 finite checks measured separately. |
| GH1 changed first load/capture, raw gathering and rest retention | **proved component** |184320 exact routes/17280 rest identities; U and stage endpoints unchanged. |
| GH1 preliminary recursive H and single-real1 three-colony footprint | **proved conditionally** | Arbitrary correct beta/native-pulse contract; first-rest24Q corollary and second-rest56Q witness. |
| GH0/GH1 own beta<=Q, final K and faithful complete Gray composition | **unproved** | No shorter U, decoded-boundary or iid conclusion. |
| GMW4 total affine physical IO and radius5 | **proved changed component** | Integer overflow rejection, one-site operand travel, inherited explicit service/ROM/zero-Workspace departures. |
| GMW4 Q-bit full emission/reference failure | **proved** |39544bits/1413instructions/165invalid references/120out-of-range labels; this emitter only. |
| GMW4 separate64K full emission and finite comparisons | **proved static identity; measured semantic checks only** |40188bits/1410instructions/51prepared inputs; universal own-beta identity open. |
| GMW4 canonical prepared fifth-stage decoded-field failure | **proved** |65535 exact updates/rest/five actual Info commits; wrong ProgramBitcopy4 at5099, non-intact preloaded context. |
| GMW4 own beta<=Q, universal deadline and full-period/Gray refinement | **unproved** | No sufficient schedule or hierarchy/noise theorem. |
| GMW5 total word-tape component and Q-code fit/reference obstruction | **proved changed component / specified emitter obstruction** |18537-bit alphabet;26137beta bits/105invalid references, no general evaluator lower bound. |
| GMW5 separate64K semantics and prepared two-word deadline failure | **measured finite comparisons / proved finite failure** |62inputs; all65535updates/rest/ten actual Info commits checked; non-intact preloaded context. |
| GMW6 total radius5 token/dictionary rule and static emission | **proved changed component** |8091token bits plus51200dictionary bits;59392total capacity, not Gray Q storage. |
| GMW6 full own-beta raw-field/opcode equivalence and prepared runtime | **proved under stated input/control premises** |Universal register/field contracts and47913conservative execution bound; no errors. |
| GMW6 prepared physical fifth-stage and five-copy boundary commit | **proved conditional theorem** |Preloaded coherent tape, quiet canonical controls; all legal upper raw neighbourhoods. |
| GMW6 quiet coherent whole-cell/current-row E0 coupling | **proved conditional theorem** |All raw native/metadata payloads; every eleven-site row has at most two faults; no previous-row wake. |
| GMW6 prepared continuing pure-E0 boundary decoder | **proved conditional extension** |Original lambda24; unchanged frozen evaluator, dictionary and fixed-zero Workspace scope. |
| GMW6 earlier preparation, simulated-flag repair and whole encoded period | **unproved** |Fixed-zero Workspace and immutable-code/word departures remain. |
| GMW7 total radius5 rule, full own-programme and universal execution deadline | **proved changed rule** |7902token bits plus51200dictionary bits;49068active updates. |
| GMW7 actual single-gather input preparation and broad encoded period | **proved changed rule** |32Q snapshot, all191×11 captures by37Q; arbitrary coherent initial private fields. |
| GMW7 continuing pure-E0 period and majority boundary decoder | **proved changed rule** |Original lambda24, arbitrary whole-cell payloads; fixed-zero Workspace essential. |
| GMW7 finite prepared/gather implementation comparisons | **measured only** |97 execution cases and14807 actual full-cell comparisons supplement the proof. |
| GMW7 Gray three-gather/early-flag/pulse refinement, real1/higher and iid memory | **unproved** |Dictionary, word IO and control/schedule departures remain. |
| GMW7 intact-context single-real2 native-clock stationary island | **proved changed-WF0 obstruction** |139264 clock-only physical overwrites; no later errors; all transient/saturated rows. |
| GMW7 finite native-clock erasure and private-only correction | **refuted / ruled out under unchanged native/WF0** |Fixed17Q spatial hull, infinite lifetime; Address stays correct. |
| Null right Address bank to computed upper Flag2 | **proved conditional native lemma** |Four null words, correct left GF/common Age, zero old Flag2 and Workspace2; actual damaged gather reachability open. |
| Authentic final source to Workspace2 seed and next native Flag2 | **Gray predicates apply / proved conditional seed lemma** |Correct reader controls and final computed source1; arbitrary one-row local two-fault replacements, no erosion claim. |
| Intact GMW7 first-window end-source zeros and late-only timing gap | **proved changed-interface gap** |Actual held Info on the accepted shared real2 clock history; no rule or schedule emitted. |
| Authentic early evaluator, source retention, Age progression and higher repair | **unproved** |Early38Q route is conditional; full Gray programme/gather/order and noisy closure remain open. |
| GMW7 actual first-gather four/five-null right Address banks | **proved changed-rule bank lemma** |Intact shared real2 history, actual raw-holder factor and sources; col15 quiet/col16 fully Flag1-set. |
| GMW7 all-SF centre-clock factor and sixteen actual distorted-bank periods | **proved changed-rule finite-history theorem** |Same intact clock real2; actual gather, padding, beta normalization and asynchronous commit lift. |
| GMW7 sixteen common upper Age increments on that history | **refuted** |First Age mismatch at evaluation5/col2, Age2; no inside Flag2 through evaluation16. |
| GMW7 general later-map recovery and authentic early Flag2 command | **unproved** |No full Gray erasure/three-gather/repair refinement or all-time native-map conclusion. |
| GT0 printed Mailbox erasure and raw-boundary centre-clock factors | **proved conditional component prefix** |Actual retained transitions; native printed/h1 prefix and published Workspace window. |
| GT0 second/third native banks and early temporal-majority availability | **proved conditional physical prefix** |Same original real2 location set, compatible intact layout premise; no preloaded bank or chosen upper fault. |
| GT0 actual early evaluator, own beta/final layout and later repair | **unproved** |Available banks alone do not implement early computation or the full Gray rule. |
| GE0 actual three-History LOAD, finite native beta and all-raw radius5 ported equations | **proved conditional component** |Declared2462-bit frame;2346-bit native prefix, immutable raw-source beta; no whole own programme. |
| GE0 early native run, unique five-copy head and flag couriers | **proved conditional physical prefix** |34396 updates; delivered before80Q-1; actual banks give F1one/F2zero. |
| GE0 prepared Age15 positive Flag2 command | **finite replay; reachability unproved** |Not an independently selected upper history in the actual-bank theorem. |
| GE0 initial Workspace endpoint transcription | **refuted and explicitly corrected** |Exact old sources/receipt retained; corrected[96Q,98Q), early theorem unaffected. |
| GE0 all-receiver actual first native banks and emitted/delivered flags | **proved conditional physical prefix** |Same shared clock real2; GFcorrect/Age1 everywhere, F1 on ten explicit colonies, F2zero; no preloaded upper bank. |
| GE0 first literal Workspace/native command window | **proved conditional prefix** |Final computed-source/literal late-equation premises; exact17Q to20Q clock growth and quiet native form by806912. |
| GE0 native writeback and reachable later common-Age/Flag2 banks | **unproved** |First pulse does not establish the continuing simulated native map or eventual repair. |
| GE0 own beta/final layout, late Workspace/commit and full Gray or noisy completion | **unproved** |Early schedule/interface added; no general E0 birth, higher-error, iid or faster-U theorem. |
| GE1 actual old-holder native mirror stores and radius5 | **proved changed component** |37 native ports replaced; reset/gate/old-Nextbit semantics explicit, non-native and Workspace ports remain. |
| GE1 first native commit and next actual History2/3 bank | **proved conditional physical composition** |Same shared real2 and actual early outputs; native quiet phase20Q, barriers−1/19, no preloaded upper state. |
| GE1 next-bank global common upper Age | **absent on this history** |Literal/emitted native Ages18..23 are2,1,1,1,1,2; eventual Flag2 is not inferred. |
| GE1 literal own fifth evaluator, own beta/final layout and noisy/full-period/Gray theorem | **unproved** |Native-only writer change is explicit; no iid or shorter-U conclusion. |
| GE2 actual second native History preparation, head and courier delivery | **proved conditional physical prefix** |Same GE1 error history and completion premises; actual B1, no independently selected upper input. |
| GE2 derived D2, zero Flag2 and noncommon upper Ages | **proved conditional native calculation** |All receiver classes and canonical exterior; actual delivery before U+80Q-1. |
| GE2 second literal Workspace/native pulse20Q to23Q | **proved conditional prefix** |Final computed-source premise, exact infinite-line event partition and old/new Workspace latency. |
| GE2 later Flag2 repair, own beta/layout, whole Gray/noisy/iid or shorter U | **unproved** |Temporary growth and finite native prefix do not refute eventual repair. |
| Gray-faithful Q-bit self-evaluator, universal noisy execution and encoded period | **unproved** |GMW6's extra dictionary prepared theorem does not close Gray's programme/gather/pulse obligations. |
| GR1 arbitrary-upper-state real1-to-adjacent-pair boundary map | **refuted** | Six-site real1 split snapshot; exact lower/upper cofactors and physical boundary composition; initial upper Info backups deliberately incoherent. |
| GR1 independent-current-upper-E0 plus real1 boundary map | **refuted** | Width99 core without History overwrite; one initial upper pair and a separately certified upper operational tick. |
| Nearby earlier physical-source isolation obstruction | **proved** | Combined nine-point example is real2; the later core fails(iv). Example does not certify generation of its initial upper fault. |
| Intact-hierarchy reachability or universal exclusion of the split context | **unproved** | Global physical-history/operational-copy invariant remains open; independently admissible upper E0 does not settle it. |
| GR1 faithful Gray programme/rest refinement or real1/higher noisy lift | **unproved** | Address/selector ROM, current-SimBit and damaged-rest departures remain. |
| Counterexample to corrected Gray, Gács 2001, or all-time Address memory | **unproved; none obtained** | Flag persistence alone does not prove memory failure. |

To reproduce the completed certificates from the repository root:

```sh
python3 Report/proofs/gray_counterexamples/check_printed_flag2.py
python3 Report/proofs/gray_counterexamples/check_gray_scale_schedule.py
python3 Report/proofs/gray_counterexamples/check_gray_scale_flag2_cofactor.py
python3 Report/proofs/gray_counterexamples/check_native_geometry_invariant.py
python3 Report/proofs/gray_counterexamples/check_corrected_native_operator.py
python3 Report/proofs/gray_counterexamples/check_native_observer_masks.py
python3 Report/proofs/gray_counterexamples/check_corrected_native_real1.py
python3 Report/proofs/gray_counterexamples/check_corrected_native_mixed.py
python3 Report/proofs/gray_counterexamples/check_computed_simbit_radius.py
python3 Report/proofs/gray_counterexamples/check_gray_staged_transport.py
python3 Report/proofs/gray_counterexamples/check_gray_staged_schedule.py
python3 Report/proofs/gray_counterexamples/check_gray_staged_fetch.py
python3 Report/proofs/gray_counterexamples/check_gray_staged_frame.py
python3 Report/proofs/gray_counterexamples/check_gray_staged_flag_quiet.py
python3 Report/proofs/gray_counterexamples/check_gray_staged_noiseless_period.py
python3 Report/proofs/gray_counterexamples/check_gray_staged_wipe_wake.py
python3 Report/proofs/gray_counterexamples/check_gray_staged_E0_flag_recovery.py
python3 Report/proofs/gray_counterexamples/check_gray_staged_E0_period.py
python3 Report/proofs/gray_counterexamples/check_gray_staged_real1_clock_commit.py
python3 Report/proofs/gray_counterexamples/check_gray_staged_intact_clock_commit.py
python3 Report/proofs/gray_counterexamples/check_gray_literal_stage_envelope.py
python3 Report/proofs/gray_counterexamples/check_gray_raw_gather.py
python3 Report/proofs/gray_counterexamples/check_gray_raw_gather_radius.py
python3 Report/proofs/gray_counterexamples/check_gray_computed_simbit_order.py
python3 Report/proofs/gray_counterexamples/check_gray_native_bitpacked_program.py
python3 Report/proofs/gray_counterexamples/check_gray_moving_word_kernel.py
python3 Report/proofs/gray_counterexamples/check_gray_moving_word_v2.py
python3 Report/proofs/gray_counterexamples/check_gray_moving_word_v2_audit.py
python3 Report/proofs/gray_counterexamples/check_gray_moving_word_v3_transport.py
python3 Report/proofs/gray_counterexamples/check_gray_moving_word_v3.py
python3 Report/proofs/gray_counterexamples/check_gray_moving_word_v3_deadline.py
python3 Report/proofs/gray_counterexamples/check_gray_layout_hardwirer.py
python3 Report/proofs/gray_counterexamples/validate_gray_layout_hardwirer.py
python3 Report/proofs/gray_counterexamples/check_gray_affine_word_machine.py
python3 Report/proofs/gray_counterexamples/validate_gray_affine_word_machine.py
python3 Report/proofs/gray_counterexamples/check_gray_word_tape_v5.py
python3 Report/proofs/gray_counterexamples/validate_gray_word_tape_v5.py
python3 Report/proofs/gray_counterexamples/check_gray_token_word_v6.py
python3 Report/proofs/gray_counterexamples/validate_gray_token_word_v6.py
python3 Report/proofs/gray_counterexamples/check_gray_token_word_v6_E0.py
python3 Report/proofs/gray_counterexamples/validate_gray_token_word_v6_E0.py
python3 Report/proofs/gray_counterexamples/check_gray_token_gather_v7.py
python3 Report/proofs/gray_counterexamples/check_gray_token_gather_v7_period.py
python3 Report/proofs/gray_counterexamples/validate_gray_token_gather_v7.py
python3 Report/proofs/gray_counterexamples/check_gray_token_gather_v7_clock_island.py
python3 Report/proofs/gray_counterexamples/validate_gray_token_gather_v7_clock_island.py
python3 Report/proofs/gray_counterexamples/check_gray_flag_command_contract.py
python3 Report/proofs/gray_counterexamples/validate_gray_flag_command_contract.py
python3 Report/proofs/gray_counterexamples/check_gray_clock_gather_bank.py
python3 Report/proofs/gray_counterexamples/validate_gray_clock_gather_bank.py
python3 Report/proofs/gray_counterexamples/check_gray_clock_stroboscopic_native.py
python3 Report/proofs/gray_counterexamples/validate_gray_clock_stroboscopic_native.py
python3 Report/proofs/gray_counterexamples/check_gray_clock_erasure_bank.py
python3 Report/proofs/gray_counterexamples/validate_gray_clock_erasure_bank.py
python3 Report/proofs/gray_counterexamples/check_gray_early_native_flags.py
python3 Report/proofs/gray_counterexamples/validate_gray_early_native_flags.py
python3 Report/proofs/gray_counterexamples/check_gray_global_first_flags.py
python3 Report/proofs/gray_counterexamples/validate_gray_global_first_flags.py
python3 Report/proofs/gray_counterexamples/check_ge0_first_workspace_native.py
python3 Report/proofs/gray_counterexamples/validate_ge0_first_workspace_native.py
python3 Report/proofs/gray_counterexamples/validate_gray_native_writeback_ge1.py
python3 Report/proofs/gray_counterexamples/validate_ge2_second_native_prefix.py
python3 Report/proofs/gray_counterexamples/check_gray_staged_real1_split_input.py
python3 Report/proofs/gray_counterexamples/check_gray_staged_real1_split_e0_context.py
python3 Report/proofs/gray_counterexamples/validate_gray_counterexamples.py
```

The [checkpoint validator](proofs/gray_counterexamples/validate_gray_counterexamples.py)
checks links, paper/proof source hashes, retained failures, ROM/listing
identity, receipt dependencies and unchanged tracked active-rule files.
Its final [validation receipt](../figs/gray_counterexamples/checkpoint_validation.json)
keeps the printed-counterexample result separate from the unproved global
reliability and faithful-protocol targets.

The remaining counterexample-search task is to broaden the corrected-native
recovery attack and certify a faithful physical completion before testing
simulation recovery and higher levels. The literal printed contradiction
is separate from those targets. No iid unreliability or reliability theorem
has been established by this search.
