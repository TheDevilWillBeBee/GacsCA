# Audited encoded upper repair and construction costs

2026-09-28. The retained 63-cell experiment passes independent audit. After two
continuous lower work periods its complete decoded upper state rejoins the
healthy trajectory. Broader stochastic noise testing is deferred at the user's
request. The full Gacs/Gray construction remains incomplete.

## Experiment and independent checks

The fixed compact16 candidate is unchanged: Q=16384, U=2^30, radius7,
154 raw words/4090 bits, projected105 words/2704 bits. Descriptor
53f7adbf7c34df6b17897b20a0d0654108f23a9c064defb89bb3c6d1a7fb846b;
own ROM4d055889959a880f189539dc213801780f8e2efa3daa7cb31e72cb3003f48b32.

The upper initial state is a63-cell window from the active NAND2216 fixture
at Age508479315. Two adjacent upper sites have all105 mutable words replaced
by their maximum legal values, with their own ROM metadata correctly lifted.
The lower initial encoding contains these damaged states. One GPU world then
executes two continuous work periods without host re-encoding or upper-rule
substitution. The two damaged upper sites are initial data, not a newly generated
physical-noise history. The represented lower ring has1,032,192 physical sites.

After period1, two upper sites/32 raw words differ from the healthy trajectory.
After period2, all63*154=9702 decoded raw words match it, including controller
replicas. The healthy upper state changes during these steps; this is active
computation, not an initialization or fixed-point test. Experiment37.239422s;
sampled host RSS175836KiB. Explicit device core/flags peak8,978,670bytes plus
at most1,837,080bytes staging, conservative combined10,815,750bytes, excluding
CUDA driver/compiler overhead.

The independent CPU audit checks:

- Source, fixture, descriptor, ROM and artifact hashes.
- All252 scalar upper-cell outputs: healthy/damaged trajectories, two steps,
 63 cells. These use the scalar rule rather than the experiment's native oracle.
- The repair cone against evolution of the original complete Q-cell fixture.
  Thus the63-cell periodic seam does not manufacture the local repair result.
- All217476 initial lower bank words, plus869904 pre/postcommit bank words
  via diagnostic instruction replay. A separate SSA computation verifies434952
  committed bank words, including scratch, histories, votes, Info and Hold.
- Every exported controller/mail/Signal record and its address, field widths,
  uniqueness, zero flags, presence/absence and zero unused padding. There are
 3240 stored active-field comparisons. Cached packed Data/Age are not the owners
  of those values: complete banks and shared clocks supply them, as in rp_read.
- Every physical raw output at both commits, streamed in8192-site chunks with
  radius-seven halos:317915136 words. This checks all five physical Data copies,
  metadata, geometry, flags, controllers and Signals across colony boundaries.
- Exact physical ages and elapsed times at all five saved boundaries.

Audit PASS25.012476s; watchdog25.391996s, sampled RSS183360KiB (~179MiB), exit0.
No GPU job, shared module or shared artifact was modified for this audit.

The in-period execution uses guarded event acceleration, not literal2U replay.
Its new coherent-epoch backend is supported by5 passing tests (65.652s), including
the full forcing interval against literal canonical GPU evolution, resets,
capture, mail rejection, and inactive heads. A123-input-bit BDD proof checks
stationary coherent Signals at every legal Age except the literal capture tick;
it checks90 procedure outputs have no old-Signal dependency. The capture exception
has a concrete mutation witness. These domain checks and earlier instruction/
transport certificates support the accelerated path; this audit is not a general
backend equivalence proof. The upper ring is63 cells, not a complete Q-cell upper
colony or a completed upper work period. No amplification theorem follows.

## Source interpretation and priorities

Gray p.19 Proposition1 gives epsilon<(QU)^(-2) for the hierarchical error-set
decomposition, with the recursive candidate-error bound. That is a sufficient
bound in that argument, not an experimentally measured threshold for this
modified candidate. Here (QU)^(-2)=2^(-88), about3.23e-27. Statistical sweeps
near that scale are not useful construction validation; retain deterministic
adversarial checks and defer additional stochastic sweeps.

Gray p.15 assumes Q>=2^13 and U=128Q. On p.31, the self-simulation argument
requires Q sufficiently large and bounds program length by a+b*log2(QU), with
unspecified constants. It does not furnish a compiled self-simulator certified
to fit exactly Q8192. His illustrative program uses loops and specialized copying
and comparison routines. Our current implementation expands the complete rule
into10452 primitive operations stored individually, then uses a sweeping head
to execute them. This is a concrete engineering cost, not a necessary cost of
Gray's abstract construction. Gray pp.31-32 and Gacs9.2-9.3 support specializing
the fixed evaluator while preserving complete self-reference.

## Measured bottlenecks

The read-only v2 cost profile counts all five controller phases, including the
5522-tick forcing-phase halt. The retained v1 profile omitted that short phase;
its819153631 total is superseded by819159153. No candidate was changed.

| Quantity | Current measured count |
|---|---:|
| Core cells |16354|
| Stored instruction cells |12906 (78.9% of core)|
| Memory cells |3447|
| Histories/votes within memory |2067/689|
| Complete Info/Hold |154/154|
| Optimized descriptor operations |10452|
| NAND operations in descriptor |7864 (75.2%)|
| Three gather paths |77238078 ticks|
| One complete evaluation |370794231 ticks|
| Earlier evaluation plus Signal delivery |371121322 ticks|
| All controller paths per period |819159153 ticks|

The two evaluations account for90.6% of controller-path time. NAND instruction
paths alone cost259460492 ticks per evaluation (70.0%). Own-ROM LOAD/META paths
together are about2.6% of evaluation time. A circuit of the head costs32708 ticks;
repeated fetch/read/write travel dominates arithmetic.

Removing all schedule slack, optimistically ignoring mandatory communication and
flag gaps, could save at most23.7% of U. Reaching U=2^29 requires at least34.5%
less controller-path work, before those other obligations. Shrinking the same
memory layout to Q8192 while retaining today's25-cell gap and5 tail cells leaves
4714 instruction slots:8192 fewer than today. Minor allocator tuning will not
achieve that. Earlier minimal scratch allocation saved space but increased travel;
space and time must be optimized together.

## Concrete optimization directions

1. **Simplify and reschedule the complete expression DAG.** Add Boolean identities
   for majority and conditional selection beyond the existing known-bit, constant
   folding and common-subexpression passes. Schedule independent expressions and
   allocate scratch jointly to reduce read/write wraparounds. This can remove
   instruction cells and travel without changing the physical controller. It is
   the lowest-risk first candidate; no specific percentage gain is established.
   Check every raw output on arbitrary typed neighborhoods, then regenerate and
   recheck its own ROM, packet schedule, barriers and two continuous periods.

2. **Replace repeated primitive expressions with a few specialized operations.**
   Direct word AND/OR/NOT and carefully chosen selection/majority routines could
   replace many of the7864 NAND nodes and their repeated full-core traversals.
   Start with binary operations fitting the existing operand path; multioperand
   majority needs an explicitly accounted fixed workspace and local read sequence.
   This requires a new candidate rule. Its added dispatch/controller logic must
   be included in its own self-description: net savings after recompilation are
   the acceptance criterion. No arbitrary-program platform is required, and
   the chosen hardware and ROM must remain fixed across depths.

3. **Use compact loops/shared routines for repeated holder and gather operations.**
   The current five-holder rule expansion and three691-instruction gather blocks
   are explicit repetition. Fixed counted loops with locally computed addresses
   can share code; the same history locations and all raw outputs remain present.
   Simply sharing the three gather blocks saves at most1382 instruction cells
   before loop overhead, insufficient alone for Q8192. Reusing the much larger
   majority/controller routines is the substantial opportunity. Loop counters,
   indirect addresses and their repair must themselves be self-simulated.
   Fewer instruction cells shorten every sweep, but loop overhead must be timed.

4. **Shorten physical operand travel.** A head that can seek and operate in either
   direction, or a fixed local pipelined data path, avoids waiting for an entire
   sweep between operands. The current controller only performs these operations
   on rightward passes. This chiefly targets U; combined with compact code it
   can reduce both Q and U. It is a larger redesign with new locality, reflection,
   collision, redundant-controller and self-reference obligations. A GPU execution
   optimization alone does not reduce the automaton's physical U.

Prioritize1, then evaluate a small binary-operation extension from2 before a
loop/transport redesign. Preserve fivefold protection, three temporal samples,
complete controller encoding and source-qualified maintenance. A proposed
Q8192/U2^29 pair is a useful acceptance target, not a promised or proved result.

## Reproduction and evidence

```
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_holder_encoded_upper_repair_audit_v1_watch.json --seconds 240 --rss-mib 2048 -- python -m experiments.fixed_rule.audit_compact16_holder_encoded_upper_repair
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_holder_cost_profile_v2_watch.json --seconds 60 --rss-mib 512 -- python -m experiments.fixed_rule.profile_compact16_holder_costs_v2
```

Receipts: compact16_holder_encoded_upper_repair_v1.json/.npz,
compact16_holder_encoded_upper_repair_audit_v1.json,
compact16_holder_cost_profile_v2.json, all in figs/fixed_rule.
The next-period eight-history experiment is separately retained and has not
received the independent audit given to this63-cell experiment.
