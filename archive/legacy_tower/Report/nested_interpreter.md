# Nested interpreter: incremental third-link implementation

## Scope

The existing two-link tower interprets a middle rule with no interpreter of its
own. A third link needs the outer colony to execute the middle interpreter's
instructions too. **The unprojected third link now passes one complete reduced
middle work period; a full top work period is not verified.** Nested
`IINIT`, `BUSLATCH_INT`, `IBC`, `ICHAIN`, `ILATCH` and `IEVAL` have tested NumPy
and CUDA implementations; the latter four require inner-context metadata and
the new physical control pair. Both nested evaluation and the separate
23-instruction dispatch barrier were implemented on 2026-09-23. Legacy `IWF` is unsupported,
but the current compiler does not emit it. Nontrivial nested `REGWIN` remains
unfinished, although the exact three-link target audited below queries an
empty deeper window and therefore correctly returns zero.

This is an implementation of the project's explicit colony-computer instruction
semantics, not a claim that Gray specifies these opcodes. Source-level timing,
redundancy, and unresolved D8/D10 conventions remain as documented elsewhere.

## IINIT derivation

Let the represented middle cell have raw Address a. Its own encoded-track region
starts at b, with N tracks, R copies and h=(R−1)/2. An initialization instruction
selects copy offset o. The write guard is

\[
lo\le a<hi,\quad 0\le a-b<NR,\quad (a-b)\bmod R=o+h.
\]

It writes repaired source bit V_src(y−d) into its destination, where d=o for
an ordinary instruction and d=0 for an already-routed instruction. Outside the
guard, the repaired destination remains unchanged. Fivefold outer copies o=±2
are pre-routed by the middle program, because direct offset-two operations
would exceed its D=1 reach.

An outer writer for middle copy c uses the holder's inferred address
(a+c) mod Q_middle, and latches from middle offset **c−d**, into one existing
value slot. The ordinary repaired-track transport already supplies that offset:
|c−d|≤h+D. Evaluation applies the middle layout's guard, not the outer layout's
track base. No deeper integer control is consulted, so this instruction needs
**no additional register pair or state track**. Configuration words 78–79 carry
the middle track-region bounds. Constructors reject unmatched registries,
invalid slots, and unrouted sources beyond D.

## Evidence

Before implementation, four component tests failed with the explicit unsupported
`IINIT` exception. The first end-to-end fixture then exposed an error in its
program projection: an injected +1 clock fault reached the following `MOV`,
which the fixture had omitted. The projection now includes every instruction
reachable at the test's raw clock values, checked against the real middle
program. Random source/destination agreement also made one case vacuous;
each slot now has an explicit changed-output witness, retaining arbitrary raw
copies elsewhere. These were fixture failures, not evidence of a repaired
source-level rule defect.

Validation covers:

- R=3 and R=5 **complete 65,536-step outer periods**, decoding all fields/raw
  copies after actual middle `IINIT` transitions. Clock, Address and Flag faults,
  inconsistent raw backups, and full 16-bit own registers are included.
- NumPy/CUDA direct middle-transition parity and outer `IEVAL` parity.
- Gray Q=8192, U=1,048,576, R=5: actual fifth-stage execution from three prepared
  gather banks, fresh input-register loading, and comparison of all **512 encoded
  bits** per represented cell, including the full 20-bit own-register alphabet.
  All five copy slots are covered. This uses a 16-cell arbitrary middle ring
  (no radius-five aliasing), **not a whole 8192-cell middle colony**, and does
  not execute a complete Gray outer period.
- Explicit rejection of the remaining nested instructions and a nonlocal
  unrouted fivefold initialization.

[Tests](../tests/test_nested_iinit.py),
[initial unsupported baseline](../../../figs/legacy_tower/nested_iinit_before_20260921.xml),
[seven-test final run](../../../figs/legacy_tower/nested_iinit_final_20260921.xml): **7 passed in
55.34 s**, including the constructor-rejection witness. The source and binary
snapshot is [archived](../../../figs/legacy_tower/nested_iinit_sources_20260921.tar.gz), with
[fingerprints](../../../figs/legacy_tower/nested_iinit_identity_20260921.json). Broad default
regressions on that archived build completed: **170 passed**, one slow test
deselected, in 1353.26 s ([record](../../../figs/legacy_tower/full_regressions_nested_iinit_20260921.xml)).
That process had loaded the pre-register-load backend; its result must not be
attributed to the subsequent `BUSLATCH_INT` change.

## Nested register loading (2026-09-22)

The previous interpreter nominally accepted `BUSLATCH_INT`, but its source
bus was permanently disabled. Two end-to-end witnesses failed: 29/64 and
19/64 simulated Age registers disagreed at R=3/5 because timed writes used
zero instead of the middle instruction's source bit.
[Failing record](../../../figs/legacy_tower/nested_buslatch_before_20260921.xml).

For a represented field bit at middle colony address X, middle Address a,
pass direction s∈{−1,+1}, speed D and elapsed pass time τ, set

\[
d=s(a-X),\qquad j=d\bmod D.
\]

The bit is written iff the instruction's Address guard holds, d≥0, and
floor(d/D)=τ. Its new value is the repaired **instruction source track** at
middle offset −sj. The outer transport latches that bit into the existing
`BLB` temporary; evaluation uses the same guard/timing and writes only that
encoded register bit. Other bits, including high alphabet bits beyond the
loaded field, are preserved from the independently computed local transition.
The source is `op.src`, not a global bus override. Invalid source/direction
descriptors are rejected. No additional integer registers or tracks are needed.

**Eleven tests pass** in 145.35 s ([record](../../../figs/legacy_tower/nested_buslatch_all_fields_20260922.xml)):
complete 65,536-step outer periods at R=3/5; both directions and zero/nonzero
pass times; arbitrary raw copies and register values; Address/clock faults;
high-bit preservation; non-vacuous NumPy/CUDA latch and evaluation witnesses;
and an excluded-Address guard that prevents an otherwise timed write.
The full-Q Gray fifth-stage case uses four load phases, 64 arbitrary middle
cells, all 512 encoded bits, and arbitrary 20-bit registers. The wider Address
span includes the lowest Address-field and highest Age-field bit positions.
It reloads outer input controls from prepared three-way gathers and compares
every final HOLD field/raw copy. This is **not a full Gray outer period or a
whole middle colony**. The later test refactor briefly introduced an undefined
fixture variable (two errors); that test-only defect was corrected before the
final run. **53 existing hierarchy/register/execution tests also pass** on the
new backend, in 250.56 s ([record](../../../figs/legacy_tower/nested_register_regressions_20260922.xml)).
Together with the 11 register-load cases, these cover 64 distinct tests, not a
new full-suite run. [Tests](../tests/test_nested_buslatch.py),
[source/binary archive](../../../figs/legacy_tower/nested_buslatch_sources_20260922.tar.gz),
[verified fingerprints](../../../figs/legacy_tower/nested_buslatch_identity_20260922.json).

## Actual remaining three-link opcode dependencies

A direct inventory of current middle programs gives:

| Middle program | ILATCH | ICHAIN | IBC | IEVAL | IWF |
|---|---:|---:|---:|---:|---:|
| compressed R=3 | 18 | 9 | 9 | 4 | 0 |
| compressed R=5 | 14 | 7 | 7 | 4 | 0 |
| full Gray R=5 | 14 | 7 | 7 | 4 | 0 |

Counts are static instructions, not durations. `IBC`, `ICHAIN`, `ILATCH` and
`IEVAL` are now supported with an explicit inner context.
All three middle contexts query `(0,0)` in their
own `REGWIN` instruction, because the represented top program has no register
load of its own. Their **own** register windows are nonempty, and are already
passed to the outer local-transition compiler. Thus a general nested `REGWIN`
implementation would extend the system, but is not a prerequisite for this
particular three-link tower. Additional middle control values are still needed
for the four table-dependent instructions above.

## Optional second physical control pair (2026-09-22)

Outer cells now optionally contain `simage2/simaddr2`, loaded locally from voted
**input ARGA+0.SIMAGE/SIMADDR**, alongside the existing pair loaded from input
AGE/ADDR. They represent the middle holder's **raw input** controls: middle
operations read S, while its local transition repairs registers into N. Loading
repaired outputs or future HOLD controls would change the faulty-state rule.
Each physical holder retains its own copies. The archived initial pair did not
yet drive nested instructions; the subsequent `IBC` implementation below is
its first table-dependent consumer.

`Program.nested_register_bits` is zero by default, or 16–31 when enabled.
`compile_register_load(..., nested=True)` uses two consecutive bit-serial local
loads, selecting the second pair with `BUSLATCH_INT.param=1`; the common repair
inhibition window spans both loads. Gray's optional `nested_controls=True`
reloads voted raw input after reset. Reset, colony-local register repair,
full-cell replacement noise, NumPy/CUDA packing and checkpoint restart all
include the optional pair. New noise draws follow the legacy track draws, so
projection onto the old state alphabet preserves its exact counter stream.
Default states and packed layouts are unchanged. Encoding a represented upper
state which itself has a second pair is explicitly rejected, not silently
truncated; a general fourth link is outside this schema's current scope.

**21 tests pass in 24.80 s** ([tests](../tests/test_nested_controls.py),
[record](../../../figs/legacy_tower/nested_controls_final_20260922.xml)). They cover R=3/5 complete
local loads, pair widths 16/17/20/31, isolated repair at colony boundaries,
load-window boundaries, joint field/track damage, full-replacement counter
oracles, stochastic checkpoint restart at time 2^40, invalid schema rejection,
and quiescent-certificate rejection followed by exact skipping after repair.
The full-Q Gray stage-five witness includes arbitrary 512-bit represented
states: one raw middle cache contains 98765/88888 while its direct repaired
output is 233/111. The second physical pair retains the former values while
every decoded HOLD field/raw track matches the latter transition. This is
16 represented cells with prepared gathers, **not a full middle colony or
complete outer period**.

For that Q=8192, U=1,048,576 case, the two-pair load window is
[917518,950294), interpretation is [960965,972255), and the stage-five active
deadline is 983040: **10,785 steps remain**. The full default regression run on
this backend completed: **202 passed**, one slow test deselected, in 1492.57 s
([record](../../../figs/legacy_tower/full_regressions_nested_controls_20260922.xml)).
The exact [source/backend snapshot](../../../figs/legacy_tower/nested_controls_sources_20260922.tar.gz)
has 28 independently hash-verified members
([identity](../../../figs/legacy_tower/nested_controls_identity_20260922.json)); its archived report
predates completion of this full run. The earlier 170-test result belongs to
the separate archived IINIT backend.

## Nested broadcast accumulation (IBC)

An explicit `inner_ctx` now supplies the middle interpreter's immutable program,
layout and scratch-track registry. No host-side simulated transition executes
inside the CA. The GPU carries versioned inner metadata plus separate table
slices in the existing device table buffers. Legacy configurations retain 96
configuration words; nested configurations use 128. This is a bounded inner
context, not recursive device execution or a universal encoded interpreter.

For a middle target with inferred Address a₁, derive its deeper track t₂ and
copy offset c₂ from the middle layout. Let o be the middle IBC pass offset,
and a₂=(raw SimAddr+c₂) mod Q₂. An inner BCAST instruction selected by **raw
SimAge** is eligible when t₂ is its destination or SIG, o−c₂ is the requested
signed neighbour displacement s·k (1≤k≤D₂), and a₂+s·k is inside its range.
The middle instruction's own Address guard must also hold.

The outer mail passes latch the middle target's repaired SIGk, CARRYk and
BFOUND into three existing temporary slots. No new scratch tracks or nonlocal
reads are introduced. Evaluation takes the candidate iff SIGk=1 and either
BFOUND=0 or the broadcast direction is positive. It then writes BFOUND=1 or
BVAL=CARRYk, as appropriate. Positive-direction passes may overwrite a farther
candidate with a nearer one; negative-direction passes keep the first found.
Other bits retain their independently computed local-transition output.

Compressed nested schedules now explicitly reset and load both pairs from
voted input before computation, rather than using the old speculative HOLD
cache. This change is opt-in; ordinary compressed schedules are unchanged.
Gray already has the tested stage-five reset/input-load path.

**20 new tests pass** across two runs: 11 in 125.78 s
([periods, branch table, fault containment and Gray](../../../figs/legacy_tower/nested_ibc_extended_20260922.xml)),
and nine in 3.61 s ([timed latches and rejection guards](../../../figs/legacy_tower/nested_ibc_latch_20260922.xml)).
[Tests](../tests/test_nested_ibc.py) cover:

- Complete 65,536-step outer periods at R=3/5, actual middle IBC and inner
  BCAST programs, both directions and every feasible pass offset. No host
  cache initialization is used; deliberately wrong caches must be reset and
  locally reloaded. Every field and raw backup copy matches the direct middle
  rule, including inconsistent raw input copies and an isolated inner-clock
  fault repaired in the output but still used raw for instruction selection.
- An independent Boolean branch table for candidate/found/value bits, both
  directions, excluded Address and out-of-table raw Age; NumPy/CUDA timed-latch
  and evaluation parity, including damaged full-alphabet controls.
- Isolated faults in either physical second register affect **only that
  holder's output copies** at both R=3/5; the next full transition repairs the
  discrepancy. These are targeted witnesses, not a noise threshold claim.
- Full-Q Gray stage five on 16 represented cells, all 512 encoded bits and
  20-bit registers, from prepared gather banks through locally loaded raw
  controls. Every decoded HOLD field/raw copy matches. This is **not a whole
  middle colony, a complete Gray outer period, or a completed third link**.

The preceding 202-test full-suite result belongs to the archived control-pair
snapshot, **not to this newer nested-IBC backend**. A broad regression process
was started on the [IBC source/backend archive](../../../figs/legacy_tower/nested_ibc_sources_20260922.tar.gz)
([identity](../../../figs/legacy_tower/nested_ibc_identity_20260922.json)) before the carry changes
below. It completed with **222 passed**, one slow test deselected, in 1864.10 s
([record](../../../figs/legacy_tower/full_regressions_nested_ibc_20260922.xml)), using its imported
Python modules and mapped old binary. Tests do not reload core modules or
spawn fresh interpreters. This result is not attributed to subsequent builds.

## Nested intermediate carry propagation (ICHAIN)

For carry hypothesis k, 2≤k≤D₂, set u=o−c₂ using the same inferred middle
geometry as above. An inner SWEEP selected by raw SimAge contributes iff
the middle instruction's Address guard holds, t₂ belongs to the SWEEP's
write set, and **−k<u<0**. This strict interval excludes both the originating
token and final target. There is deliberately no additional inner field-range
guard: the direct middle instruction advances scratch hypotheses, whose
validity is checked later during evaluation.

Let j be the inner instruction's value-resource slot, a₂=(raw SimAddr+c₂)
mod Q₂, and b the bit of its constant at index a₂+u−lo (zero outside the
constant's alphabet). Three locally transported old repaired bits suffice:
x=S[j,0], y=S[j,1], c=CARRY[k]. The new carry is:

| Operation | Carry output |
|---|---|
| EQC | c AND [x=b] |
| EQF | c AND [x=y] |
| ORF | c OR x |
| ANDF | c AND x |
| LTC | [x<b] OR ([x=b] AND c) |
| ADDC | [c+x+b≥2] |

Multiple active SWEEPs may target the same carry. Because they all read the
old repaired state, the **last eligible instruction** wins. The implementation
selects that instruction before transporting its operands, preventing mail
arrival order from changing program semantics. Over-capacity resource slots
are rejected explicitly. Inner metadata version two adds the scratch-slot
indices without changing the physical state alphabet or 128-word config size.
At D₂=1, there are no intermediate cells and ICHAIN is exactly a no-op, even
for damaged controls and arbitrary raw copies. Gray's actual D=1 program
uses this case; the R=3 reduced program exercises real carry computation.

**23 distinct tests pass** across targeted runs
([tests](../tests/test_nested_ichain.py)):

- All six Boolean carry functions against an independently written scalar
  truth table; 36 actual-program cases covering the four emitted SWEEP kinds,
  all eligible middle copy/pass combinations and both k=2/3. Complete
  65,536-step outer periods reproduce every middle field/raw copy after local
  input-cache loading. The test includes inconsistent input backups and an
  isolated raw inner-clock fault. [Seven-test record](../../../figs/legacy_tower/nested_ichain_after_20260922.xml).
- Two concurrent SWEEPs with distinguishable operands, including a later
  instruction that is ineligible for one target: complete outer-period output
  matches the direct last-eligible write. Isolated faults in each physical
  inner control alter only that holder's copies and are repaired by the next
  full transition. [Three-test record](../../../figs/legacy_tower/nested_ichain_order_faults_20260922.xml).
- Every D=1 middle ICHAIN phase as an exact no-op, through a reduced complete
  outer period and full-Q Gray stage five (16 represented cells, all 512 bits,
  20-bit registers). Unsupported scratch-slot concurrency is rejected.
  [Record](../../../figs/legacy_tower/nested_ichain_order_gray_20260922.xml), which also contains an
  earlier version of the concurrent-write witness subsequently strengthened.
- Ten strict-boundary/control-guard cases, including an out-of-table Age,
  excluded middle Address, invalid encoded geometry and full-alphabet raw
  SimAddr. [Record](../../../figs/legacy_tower/nested_ichain_guards_20260922.xml).

The [initial seven-test baseline](../../../figs/legacy_tower/nested_ichain_before_20260922.xml)
failed at the unsupported-opcode check. A misplaced CUDA block caused one
intermediate compile failure; correcting its location produced the tested
backend. Neither is a scientific counterexample to the rule. A combined
82-test nested-component regression run completed on the archived carry build:
**82 passed in 599.35 s** ([record](../../../figs/legacy_tower/nested_interpreter_closure_20260922.xml),
[source/backend archive](../../../figs/legacy_tower/nested_ichain_sources_20260922.tar.gz),
[identity](../../../figs/legacy_tower/nested_ichain_identity_20260922.json)).
**Neither a complete third link nor noisy hierarchy scaling is established.**

## Nested mail latching (ILATCH)

The outer interpreter now reproduces the middle latch's operand requests,
including ordinary value operands, shifts, sweep intermediates/tokens, both
broadcast directions, routed IINIT operands, register-bit requests and
Workspace requests. For a middle writer Address a₁ requesting encoded source
position X during direction d and pass time τ₁, define

\[
\delta=d(a_1-X),\qquad j=\delta\bmod D_1.
\]

A timed request needs δ≥0 and floor(δ/D₁)=τ₁, in addition to its opcode,
copy-offset and writer guards. It reads repaired middle BUS at displacement
−dj. The outer holder for middle copy c transports that bit from offset c−dj
into one existing value slot. Evaluation writes only the selected middle
scratch bit; other bits retain the local-transition result. All selection uses
raw holder controls, including when their output is repaired in the same step.

Workspace requests run **even when inner Age has no active instruction**.
Register-bit requests use their own inner direction/time/Address guard before
the middle pass timing. Ordinary operand prefetches do not impose the later
evaluation's inner Address guard. Version-three metadata adds the needed
scratch indices and field bounds, staying within 128 config words; there are
no additional state tracks or nonlocal state reads.

The source positions have form X=b+h+R·t. They are spaced by R, and every
legal transport speed satisfies D₁≤R. Hence a timing interval of D₁ consecutive
positions contains **at most one distinct source position**. Simultaneous
successful requests therefore read the same middle BUS displacement. The code
also retains request order explicitly, matching the direct instruction.

**46 tests pass in 153.80 s** ([tests](../tests/test_nested_ilatch.py),
[record](../../../figs/legacy_tower/nested_ilatch_verified_20260922.xml)):

- Complete 65,536-step outer periods at (R,D)=(3,3),(3,2),(5,1), both mail
  directions and every copy slot. Spatially distinct BUS bits make incorrect
  source offsets observable. Actual concurrent RSHIFT remains active. Every
  field/raw copy matches the direct middle transition after local cache loading,
  with inconsistent backups and an isolated raw inner-clock fault.
- NumPy/CUDA local latch/evaluation witnesses for all seven emitted operand
  classes, all three value slots, both broadcast directions, empty-clock
  Workspace requests, both register fields/directions/edge bits, and routed
  IINIT operands. Timing, middle Address, inner clock and pass guards each
  prevent an otherwise visible write.
- Isolated faults in either physical inner control change only the holder's
  output copies; the next full transition repairs the difference at R=3/5.
- Full-Q Gray stage five on 16 represented cells, all 512 encoded bits and
  20-bit controls, matches every decoded HOLD field/raw copy. The final extra
  caches also equal the raw input controls, not the repaired output. This uses
  prepared gather banks, **not a whole middle colony or complete Gray period**.

The [initial baseline](../../../figs/legacy_tower/nested_ilatch_before_20260922.xml) failed at the
unsupported-opcode check. Earlier component records are retained; the 46-test
record above reruns the final strengthened fixtures together. The archived
latch build subsequently completed **148 component/backend tests in 1146.07 s**
([record](../../../figs/legacy_tower/nested_latch_regressions_20260922.xml),
[source/backend archive](../../../figs/legacy_tower/nested_ilatch_sources_20260922.tar.gz),
[identity](../../../figs/legacy_tower/nested_ilatch_identity_20260922.json)). The process handle was
lost during an environment reset, but its complete saved XML reports zero
failures/errors. The run was not restarted or attributed to a later backend.

## Full-program closure requires more than the last opcode

The [reproducible inventory](../experiments/nested_inventory.py)
([result](../../../figs/legacy_tower/nested_inventory_20260922.json)) finds a distinct barrier:

| Middle program | Largest batch | Age | Former interpreter cap |
|---|---:|---:|---:|
| R=3 compressed | 23 CONST | 8728 | 4 |
| R=5 compressed | 23 CONST | 18046 | 4 |
| Gray R=5 | 23 CONST | 943502 | 4 |

These are simultaneous scratch clears at interpreter initialization, not 23
operand computations. The largest nonconstant resource slot is still index 2,
within the three-slot alphabet. Earlier wording that opcode closure alone
enabled full compilation was incomplete: dispatch also had to handle this
batch faithfully, without changing the represented middle transition.

### Dispatch closure (2026-09-23)

CUDA now uses a view into the immutable instruction/index tables instead of
a fixed four-entry per-thread array. NumPy's matching cap is removed; the
compiler emits an outer evaluation step for every possible batch index.
The middle instructions remain simultaneous and unchanged. Operand transport
reads their old input state before evaluation, while guarded writes are applied
in program order. The physical state alphabet and scratch-track count do not
change. Existing resource numbering is preserved: a data operation must still
have a class-slot index below three (preceding constants count in that index).
Incompatible batches are rejected, not assigned nonexistent scratch tracks.
Work-period budgets still bound the compiled computation.

**13 tests pass in 40.72 s** ([tests](../tests/test_instruction_batches.py),
[record](../../../figs/legacy_tower/instruction_batches_verified_20260923.xml)):

- Actual 23-clear initialization at R=3/5 through complete 65,536-step outer
  periods, plus full-Q Gray stage five on 16 represented cells. All 23 writes
  are non-vacuous; every decoded field/raw copy matches the direct transition
  with arbitrary backup/register state and clock/Address/Flag faults.
- A 67-instruction synthetic batch at R=3/5 proves old-state reads even after
  an earlier clear, and the last eligible guarded write after index 64. Every
  field/raw copy matches after an actual outer period. This is not just an
  increased constant or an untested absence of truncation.
- NumPy/CUDA evaluation at index 22, inactive high-index preservation, and
  explicit rejection of unavailable operand slots.
- All middle instructions **except IEVAL** compile together without retiming
  or serializing the middle rule. The full program still explicitly rejects
  IEVAL. These projection tests are compilation/budget diagnostics, not
  third-link execution.

The [baseline](../../../figs/legacy_tower/instruction_batches_before_20260923.xml) failed on the
four-instruction assertion in all three real-clear cases. The updated
[inventory](../../../figs/legacy_tower/nested_inventory_20260923.json) records no fixed dispatch
cap (`null`), while retaining three operand slots:

| All-but-IEVAL diagnostic | Encoded bits | Compute end | Deadline | Slack |
|---|---:|---:|---:|---:|
| R=3, Q₀=1024, U₀=65536 | 241 | 31507 | 65535 | 34028 |
| R=5, Q₀=1024, U₀=65536 | 365 | 44992 | 65535 | 20543 |
| Gray, Q₀=8192, U₀=1048576 | 512 | 972274 | 983040 | 10766 |

These are stage-computation margins, not total-runtime bounds or proof of a
completed hierarchy. Broader regressions on the archived dispatch build completed:
**304 passed**, one slow test deselected, in 2436.13 s
([record](../../../figs/legacy_tower/full_regressions_dispatch_20260923.xml)). They must not be
attributed to the subsequent nested-evaluation build.

## Nested evaluation and full opcode closure (2026-09-23)

`nested_eval.py` maps middle interpreter scratch bits to existing outer scratch
tracks and evaluates the selected instruction without calling a host simulated
transition. The represented middle `IEVAL` occupies a dedicated instruction age
(enforced at construction); its operand passes can therefore reuse the outer
token and broadcast temporaries. For an outer copy offset c, the transported
bits come from middle offset c. No new state track or integer register is added.
The immutable metadata schema advances to version 4 (160 words) to carry the
inner computed-Address track identifiers and encoded-track bounds.

Given raw middle controls (g₂,a₂), select the instruction at its specified index
in the inner table at g₂. Derive inner encoded track/copy from the middle holder's
Address, then use (a₂+c₂) mod Q₂ for ordinary range guards. Computed-Address MOV
instead uses the transported middle match bit. All sources are repaired old-state
bits. SWEEP selects the nearest valid token, retains a terminal token, and writes
SIG, ACC, then destination in the original order. BCAST requires no local token
and a found source. Register writes retain their field-bit timing and raw range
guard. Nonempty deeper REGWIN, concurrent represented IEVAL, negative indices,
and an encoded upper state with a second control pair are explicitly rejected.

**30 component tests pass** across [19 extended tests](../../../figs/legacy_tower/nested_ieval_extended_20260923.xml)
(281.17 s) and [11 register/fault tests](../../../figs/legacy_tower/nested_ieval_fault_register_20260923.xml)
(4.14 s). [Test source](../tests/test_nested_ieval.py). Coverage includes:

- Actual value and emitted token/broadcast transitions through complete 65,536-step
  outer periods at R=3/5, every decoded field and raw track copy checked against
  the direct NumPy middle transition; direct middle CUDA parity also checked.
- Independent Boolean tables for all six carry kinds, nearest-token priority,
  missing-token/boundary behavior, broadcast guards, shift padding, reset/register
  fields, zero REGWIN, computed-Address MOV disagreement and routed IINIT guards.
- Explicit timed local transport of every emitted operand class and every outer
  copy; isolated faults in each of the four control registers affect only the
  damaged holder and heal on the next step in these witnesses.
- Full-Q Gray fifth-stage token evaluation, 16 represented cells and all 512
  encoded bits, including 20-bit controls and an out-of-table raw inner-clock
  fault. This is not a full Gray outer period or a whole middle colony.

The initial two tests failed with unsupported IEVAL, as expected. Subsequent
fixture failures assumed a computed-Address MOV in the compressed schedule and
all six carry kinds in the actual top program. Corrected tests use Gray for that
MOV and separate synthetic truth tables from emitted-program witnesses. These
were test assumptions, not transition-rule counterexamples.

**Full-program integration:** [five tests pass](../../../figs/legacy_tower/third_link_initial_20260923.xml)
in 190.36 s: three full-program compilation checks (R=3, R=5, Gray), plus two
unprojected R=3/5 execution checks through complete outer periods. Execution
batches cover every emitted middle instruction family, inner value families,
rollover, inconsistent backups and control faults on 16-cell middle rings.
These integration checks are supplemented by the non-vacuous component witnesses;
they do not establish every possible faulty state or long-time behavior.
**Two consecutive-transition tests also pass** in 678.50 s
([record](../../../figs/legacy_tower/third_link_consecutive_20260923.xml)): whole 256-cell (R=3)
and 512-cell (R=5) middle colonies, each followed through four physical outer
periods without state reinitialization. Two independent initial conditions cross
the evaluation boundary and middle rollover. All decoded fields/raw copies match
the direct middle evolution after every period. Physical rings contain 262,144
and 524,288 cells respectively. Each ring represents only one top cell, so
next-level neighborhood aliasing is explicit; this is not a complete middle or
top work-period result. Two [factory tests](../../../figs/legacy_tower/third_link_factory_20260923.xml)
verify `make_simulation_layer` preserves the entire middle program, whole-colony
geometry, full register alphabet and explicit rejection of unsupported further nesting.

The [full inventory](../../../figs/legacy_tower/nested_inventory_closed_20260923.json) now has **no
unsupported emitted opcode** and the same budgets as the historical partial table
above, including 10,766 active-stage steps spare in Gray. The middle instructions
are neither dropped nor retimed. This is finite, level-specific instruction-table
closure—not Gray's encoded universal interpreter/ProgramBit fixed point
(Gray §5.3, pp.30–32), and not a proof of noise robustness.

The exact source, backend and passing records are [archived](../../../figs/legacy_tower/nested_ieval_sources_20260923.tar.gz)
with [verified fingerprints](../../../figs/legacy_tower/nested_ieval_identity_20260923.json): 43 members,
39 passing component/integration/factory cases, archive SHA-256
`22c3d822842cead80fa159be540c0f3694c6a92f2fd3bfd4de56f9c1913a6895`.
Broader default regressions on this build completed: **340 passed**, one slow test
deselected, in 4007.00 s ([record](../../../figs/legacy_tower/full_regressions_nested_ieval_20260923.xml)).
The earlier 304-test result belongs to the separate pre-evaluation archive.
Later [physical execution](third_link_execution.md) completed a full reduced
middle period, with independent replay and a single-top-cell endpoint check.

## Next concrete steps

1. Extend validation beyond the now-tested middle period and aliased top ring.
   Compact outer geometries now pass execution checks (R=3: Q=256,U=16384;
   R=5: Q=512,U=32768). A transient credit rejection delayed the initial launch;
   later permitted validation completed. Full-alphabet inner configurations and
   checkpoint parity are now tested; see [physical execution](third_link_execution.md).
2. Validate non-aliased top neighborhoods and whole top colonies; distinguish
   physical execution from direct reference endpoint checks.
3. Extend nontrivial nested `REGWIN` when a target requires it; the current
   three-link target has an empty deeper load window.
4. Test localized physical faults before persistent-noise/depth scaling. Resolve
   source gaps and encoded-program uniformity separately from opcode closure.
