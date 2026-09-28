# Practical self-simulation: source clarification and first optimization probe

2026-09-26. User priorities: (1) actual fixed-rule self-simulation, (2) practical
two-level GPU execution, (3) error correction demonstrated across levels.
The user authorizes dropping 128 as a design constraint. This does not authorize
assuming an altered schedule inherits the previous repair argument.

## Gray does not certify Q=8192 for complete self-simulation

Gray p.15 assumes Q>=2^13 and chooses U=128Q. This supplies explicit slack for
maintenance estimates, including the pp.25–26 repair-time argument. On pp.31–32,
self-simulation instead requires Q sufficiently large for the whole program,
including its interpreter and ProgramBit overwrite/projection. On p.34 he gives
3Q+a log2 Q+b as a sufficient update-time bound, with unspecified a,b. There is
no evaluated bound establishing that the complete construction fits Q=8192.
His pp.13–14 introduction explicitly describes the varying completeness of the
five propositions; Proposition 3's implementation is not supplied as executable
code. Source: papers_txt/gray_readers_guide.txt, lines 593–608, 650–655,
1384–1458, 1526–1562. Gray's section numbering for Gacs follows the version he
used; the supplied Gacs extract develops the relevant basic block simulation in
section 9.3 and Condition 9.20 / Theorem 9.3.

The useful construction idea is a compact description of loops, copying and
comparisons, rather than a transition lookup table. It resolves the asymptotic
self-description problem; it does not supply small numerical implementation
constants. Our repeated whole-workspace sweeps are an expensive implementation
choice, not a source requirement.

## Measured bottleneck

The immutable holder has 22,837 memory cells, 34,494 instruction cells and one
end cell, totaling 57,332 computation cells. One evaluation costs:

| Part | Instructions | Physical ticks |
|---|---:|---:|
| Serial temporal majority | 13,860 | 2,383,873,806 |
| Complete rule description | 13,275 | 2,080,362,537 |
| Output copying and metadata | 283 | 69,062,217 |

The schedule's initial tick brings the sum to 4,533,298,561. Temporal majority
alone is 52.586% of this evaluation, and uses six NAND instructions per input
word. These are costs per evaluation, not the whole period or a GPU benchmark.

## Executable optimization probe

New parallel_vote_probe.py computes five backup temporal-majority outputs from
raw holder Data fields. It first corrects each operand using five physical
copies, then takes the majority of three independent histories. History offsets
are -1,+1,+2 relative to each vote location. Including output backup offsets
and operand holders gives exact physical support [-5,+6], inside the current
radius seven. The old radius-five impossibility witness still holds; the later
holder already widened the radius to seven for Wf maintenance, making this
particular obstacle obsolete.

The primitive has a complete 340-operation expression description, SHA256
0af32563067deec220ef22a05644b2d6efccee8d80e677a3d69aa73f55d78f1a.
It is not a complete rule descriptor. Four tests passed in 0.360 s:

    python -m unittest discover -s tests/fixed_rule -p test_parallel_vote_probe.py -v

Tests cover all 256 Boolean assignments to the eight logical inputs; 128 arbitrary
full raw neighborhoods against its expression description; every one of 105
pairs of damaged physical holders, with all fields randomly replaced; exact
expression dependency support and guarded reads; the radius-five negative
witness; and a three-holder failure outside the correction contract. The
five-copy majority algebra establishes two-holder correction for the operands;
these tests do not establish maintenance, clock or program recovery.

Before integration, a new complete fixed rule must specify vote clock gating,
reset/write/maintenance precedence, and every backup's metadata interpretation.
Its self-description and hard-wired ROM must include the new operation and omit
the old serial program. Recompute resource bounds and run active successive
macrosteps, locality and fault tests. Adding this primitive does not yet justify
subtracting 52.586% from an end-to-end runtime: ROM length, complete descriptor,
self-reference and controller travel all change.

## Two-level space and time constrain the design together

For constant Q,U, one represented top cell occupies Q^2 physical cells and a
complete top transition takes U^2 physical ticks. With the current 2,724-bit
projected physical state packed into 43 uint64 words, two dense buffers at
hypothetical Q=8192 need 46,170,898,432 bytes (43 GiB) for one top cell alone,
excluding neighboring colonies and guards. With hypothetical U=128Q that top
step takes 1,099,511,627,776 ticks. Neither Q=8192 nor that runtime is established
for our rule; its current 57,332-cell core does not fit that Q. At Q=65536 the
same dense storage estimate is about 2.95 TB per top cell. These are lower
spatial accounting units, not executable benchmarks or proposed allocations.

A100 capacity therefore does not by itself solve the problem. Compare Q, U,
state width, active instruction work and noise-induced work together. Certified
quiet-time and transport skipping can help, but noisy runs must retain actual
faults and their effects. The existing coherent quotient cannot represent
arbitrary broken backups without an explicit extension or local full-state
fallback. No dense allocation, GPU job or modified rule was launched here.

## Next steps and acceptance evidence

1. Integrate the parallel vote into a separate fixed revision and reestablish
   complete-controller closure. Retain the current holder as a reference.
2. Reduce serial sweeps, description size and live workspace; compare local
   specialized field operations and compact loops. Keep one physical alphabet,
   rule and ROM for every requested depth. Any new evaluator must describe its
   own added control state, not just the old rule's maintenance fields.
3. Choose space and stage lengths from measured communication/computation/repair
   requirements, without imposing U/Q=128. Recheck trickle-down and correction
   margins and document source deviations. Build a bounded GPU execution model
   with a fault-capable representation and justified skips; measure wall time.
4. Validate successive active macrosteps at levels one and two with all raw
   controller fields, then inject physical faults and track decoded damage and
   recovery at each level. Measure failure rates versus fault density over
   repeated trials. Keep targeted repair tests distinct from stochastic
   robustness and an amplification theorem.

Files owned this turn: parallel_vote_probe.py, test_parallel_vote_probe.py,
holder_cost_study.py, this report, STATUS.md and new logs/results in figs/fixed_rule.
No shared changes requested. Main agent can reply in MAIN_AGENT_NOTES.md.
Resource-study v1 took 0.911 s with maximum host RSS 62,548 KiB; its broad JSON
label verified_self_simulation_at_this_Q refers only to the existing audited
one-link fixture. V2 renames that field explicitly; neither artifact establishes
two-level dynamics. All numerical estimates remain the same.

Final resource command:

    python -m experiments.fixed_rule.holder_cost_study --output figs/fixed_rule/holder_cost_study_v2.json

V2 passed in 0.924484 s; maximum host RSS
61,516 KiB. The original holder descriptor SHA256 matched
314843221ed0692fbb560ba13d503f6daa557b3c9e54340769d308f49f66db25.
