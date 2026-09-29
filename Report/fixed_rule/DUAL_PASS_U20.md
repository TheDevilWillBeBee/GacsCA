# Retimed dual-pass fixed-rule candidate at Q=8192, U=2^20

2026-09-29. This is the current optimized *candidate*, not a completed
hierarchical self-simulation. It supersedes the U=2^28 timing proposal in
[COMPACT8_VERTICAL_SLICE.md](COMPACT8_VERTICAL_SLICE.md). The mathematical
motivation is Gray pp. 31–32: the rule may hard-wire its own description and
project ProgramBit from Address. Gács §9.2 permits an identical or suitably
modified self-correcting simulated rule. Neither source makes an arbitrary
user-program interpreter necessary. The printed Flag2 and computed-SimBit
source-fidelity questions in the baseline report are still open.

## Fixed rule and encoded description

`stream28_dual_pass20.local_step` is one radius-seven transition on a fixed
6,465-bit cell alphabet, with Q=8,192 and U=1,048,576. The evaluator is the
same fixed 8Q=65,536-tick radius-one spatial circuit on both invocations:
once after the first compact three-history vote to produce Flag1/Flag2 Hold,
then again after the final vote to produce all 119 projected Hold words. A
first-site ROM marker starts the holder head after the early pass. The new
short holder ROM has ten SEND instructions and HALT; it addresses the compact
Info/Hold banks. Rule selection, physical width, radius, route slots, gate
slots, and dynamic operand/result registers do not depend on hierarchy depth.
The U=2^28 modules are an earlier *different fixed candidate*, not a level
kernel selected by this U=2^20 rule.

The full local F has 421 typed outputs and 6,315 typed inputs. Its optimized
WordCode has 14,830 operations, digest
`16bf88a1d4ff5496cd3b61a1200f8a809db1438472a9191fded26de3a0786257`.
The 108-case literal certificate includes both invocations, earlier compact
vote behavior, nonflag rejection and the first-site head trigger. The exact
1,151 used raw input words have the same wire indices as the predecessor:
761 evolving gathered words and 390 immutable address-derived words. Of
those, 341 are spatial ROM fields from the *same encoded circuit* and 49 are
holder static fields from the compact SEND/metadata table. `project_all_dual_static`
derives them from canonical upper addresses; the physical evaluator reads
their locally stored SOURCE values. This gives an executable own-rule
description and address projection, but it does not by itself prove that
healthy holder dynamics reload and maintain all SOURCE values for a full U
period or that damaged ROM values are corrected.

## Measured space, routes, and clock

The compiled evaluator uses 14,849 gate copies and two raw-source buffers,
packed into 4,969 three-slot gate sites after the three-history, Info/Hold,
scratch and 390 static-source reservations. Fifty-six slots remain but no
additional gate-capable sites. All source route tables fit the fixed 38-entry
limit. The encoded healthy schedule emits/delivers 25,982 operands, completes
all 14,851 gates by evaluator tick 39,517, and delivers all 119 Hold outputs
by tick 45,125, inside the fixed 65,536-tick window. The explicit physical
endpoint audit checks 119 launches, 119 receivers, 595 early and 595 final
fivefold Hold steps. These numbers are in the `stream28_dual_pass20_*_v1.json`
receipts under `figs/fixed_rule/`.

The clock keeps three unchanged disjoint 16Q gather frames. Their last
audited arrivals are absolute ages 65,515, 196,586 and 327,657, before
their deadlines 131,072, 262,144 and 393,216. The early evaluator starts
at 393,218, last Hold arrives at 438,343, and the invocation stops at
458,754. The single-head SEND witness halts at 630,680 and its last boundary
Data packet arrives at 630,685, **16,483 ticks** before stage-three stop at
647,168. Signal capture is 655,360; Wf runs 688,128–704,512. The final
evaluator starts at 720,898, last Hold arrives at 766,023, and its invocation
stops at 786,434, before the 1,048,576 work boundary. The composed receipt
is `stream28_dual_clock20_v3.json`. The direct U=2^20 gather evidence checks
all 2,283 packet paths, all literal core launch/receive endpoints, and 24
sampled complete combined-rule endpoints, while the SEND witness follows a
single symbolic head with literal fetch/emit/receive steps. This composition
is a healthy-path timing witness, **not continuous whole-colony dynamics**.

The NumPy physical executor continuously evolved the encoded 8Q evaluator
for two consecutive periods, 131,072 ticks or 1,073,741,824 spatial site
updates. All 390 static words came from the two own address tables. It
observed 26,101 packet deliveries (25,982 operands plus 119 outputs) and
14,851 gate completions per period, 238 correct Hold output words,
139,264 literal local comparisons, and equal
states at successive wraps, in about 44 seconds with 351,604 KiB process
peak RSS. `stream28_dual_pass20_full_rom_continuous_2period_v1.json` is the
receipt. Forty coherent 15-cell local neighborhoods at five distinct U ages
also decoded all 119 evolving words, including controller fields, spatial
operand/result workspace and mail, against literal F and the address-projected
own-rule WordCode. One such coherent input passed a complete physical
evaluator period (`stream28_dual_projection20_physical_v1.json`). These are
two **isolated evaluator periods**, not successive decoded upper macrosteps.

`stream28_dual_native20.py` compiles the same 14,830-operation complete F
to a native CPU function and a radius-seven ring step, with build artifacts
isolated under `figs/fixed_rule/build/`. Forty literal local transitions
across ten clock ages and four addresses, plus every site of a 17-cell ring,
matched the Python fixed local rule. This is a local engine for future
full-period event boundaries; it is not an accelerated U-period runner yet.
No GPU artifact or shared backend was rebuilt.
A single complete 8,192-cell native ring transition at early capture took
0.134 seconds for the C kernel (six sampled sites matched literal F), with
153,788 KiB process peak RSS. At that unaccelerated dense rate, one
1,048,576-tick work period would take roughly 39 hours for **one** colony;
this is an extrapolation, not a measured work-period run. Full-period
validation needs a sound event-skip engine or coordinated GPU execution.

For a prospective two-level state, Q²=67,108,864 physical cells. Bit-packing the entire
6,465-bit alphabet needs 50.51 GiB for one state and 101.02 GiB for a
two-buffer update, above the 80 GiB A100. The projected evolving state is
3,063 bits/cell, so two packed evolving buffers would need 47.86 GiB; the
3,402 static bits/cell can be represented by one 8,192-address ROM table
(3.32 MiB) on a healthy uniform configuration. This is an implementation
compression, not a smaller physical alphabet. Independent ROM damage in a
noise experiment would need additional per-cell fault data. Neither a packed
GPU kernel nor a two-level physical run has been implemented.

An earlier patch-style dual-pass description took 14,926 operations and
missed the fixed gate capacity by 38 slots. Sharing capture/run logic in the
description reduced it to 14,830 for U=2^20; the failed approach is retained
in the earlier receipts and reports. A separate real bug was found in the
compact metadata: Info sites had `a=31|INFO`, so reset would clear Info Data.
They now use `a=INFO`; literal reset-age tests cover all three gathers.
The U=2^20 regression also checks a literal complete-rule Info copy from
Hold at U−1.

## What prevents a final construction claim

No test has yet evolved the **combined 8,192-cell local rule for a complete
U=2^20 work period**, including three gathers, both evaluator invocations,
holder SEND traffic, Flag/Signal maintenance, and final Info/Hold reload in
one retained world. Consequently there are no successive decoded upper
macrosteps for this candidate. The address-derived circuit and holder ROM
solve the static-input preparation relation, but a complete dynamic ROM
fixed point with correction under faults is unproved. Finite-depth boundary
data for two or three self-simulating levels, simulated-layer repair, and
noise amplification are also missing. The one-head SEND audit does not rule
out interference among all fivefold heads or packets in a full colony.

The next decisive experiment is a continuous full-U combined-rule execution
on a small ring of initialized colonies, retaining state across at least two
work boundaries and decoding all 119 fields against upper F at each boundary.
It must use one physical transition throughout, with host code only for
initialization and diagnostics. A CPU event engine may be sufficient at this
U; any substantial GPU run needs coordination with the main agent's GPU
schedule. A failure there should be repaired before claiming two-level
self-simulation or testing noise.
