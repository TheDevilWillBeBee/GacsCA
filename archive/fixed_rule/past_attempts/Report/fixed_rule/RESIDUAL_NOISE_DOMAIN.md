# Residual Data under fresh faults: a stronger domain and its boundary

2026-09-27. The three residual nonMEM Data words from
[FULL_RING_REPAIR.md](FULL_RING_REPAIR.md) are independent of all other outputs
under a stronger condition than previously checked: **canonical Address and its
hard-wired ROM suffice**. Clocks may be arbitrary independent 32-bit values, all
other raw fields may be arbitrary, and the selected Data copies need not agree.
One complete transition sets each group of five selected copies to its bitwise
majority. This is a residual-separation identity, not a theorem that arbitrary
clock/controller faults are repaired.

An explicit scalar/native counterexample shows why Address remains a real
restriction. Six identical full-state replacements in the paired trajectories
can cause a legal one-bit tail residue to change Signal. That residue is not one
of the three even-valued words observed in the earlier burst experiment.

## Complete descriptor check

`certify_retimed_holder_residual_noise_domain.py` examines the unchanged radius-seven
descriptor at all 21 output sites that can see the three selected logical Data
words, addresses 30960, 30961 and 30962. It introduces 15 independent 64-bit input
variables for their five raw copies. Each physical clock is an independent
32-bit variable; every other non-ROM/non-Address field is independently arbitrary.
The previous invariant required a common legal clock and coherent Data copies.

For all 3234 raw outputs, the checker establishes:

- Exactly 15 Data outputs equal the corresponding five-input bitwise majority.
- The other 3219 outputs do not depend on any selected Data input. This includes
  every raw controller, packet, Signal, flag and geometry output.
- Output Address remains canonical. G's projection therefore retains fixed ROM.

The possible influence region is complete: five holders extend each selected
logical word by two sites, and the physical rule reads radius seven. Outside
distance nine, none of the selected inputs occurs in the local neighborhood.

Canonical Address is invariant globally with arbitrary ages and flags: both
left and right adjusted-address votes equal the center's canonical address.
Whichever side the maintenance rule selects gives the same value. This simple
maintenance identity closes the geometric premise between steps; the symbolic
check confirms it at every potentially affected output site. No uniform-clock,
one-head, zero-mail or coherent-procedure premise is used.

Consequently, consider two complete configurations equal except for the selected
15 Data slots, with canonical Address everywhere. Applying identical fresh
full-state replacements with canonical Address preserves that relation, even
when replacements intersect the selected holders and break Data coherence.
Applying G restores the fivefold majority and preserves equality of every other
field. Induction permits any sequence of such Address-preserving replacements.
It does not assert that the common noisy configuration remains a valid colony
simulation or recovers its controller/clock state.

## Literal fresh-fault probes

`audit_retimed_holder_residual_noise.py` starts two complete raw configurations
that differ only by the three **actual observed residual values** versus zero.
All other mutable words are random typed values, including independent 32-bit
clocks. This is deliberately an arbitrary-state separation probe, not a replay
of a valid hierarchical trajectory.

For each of three fixed seeds, both configurations execute 12 literal G steps.
At each step four identical complete projected-state replacements are applied:
one inside the selected holder support and three outside. Address is preserved;
every other physical mutable word is replaced. Finite windows shrink by radius
seven on each edge to remove periodic-boundary influence. The experiment checks
every retained word for leakage and every selected Data output against the
explicit majority formula. The independent scalar transcription checks both
trajectories on the whole seven-site residual support and two exterior fault
sites at every tick.

Totals: **144 replacements**, **3193344 retained native output words**, and
**99792 independently compared scalar raw words**. All three cases retain 15
Data differences after tick 12 and zero differences in every other field.
No simulated transition is substituted on the host; both evolving configurations
use the complete physical transition.

## Address-fault counterexample

The diagnostic witness uses logical address a=30960, with five coherent Data
copies equal to one in the actual configuration and zero in its comparison.
All other mutable words start zero, except canonical Address and uniform old
Age=CAPTURE_AGE-1. This value is chosen to expose the Signal low-bit read; it is
explicitly different from the recorded experiment's three even-valued residues.

At offsets -5,-4,-3,3,4,5 from a, apply the same full projected-state replacement
in both configurations, setting Address to (3+offset) modulo Q and regenerating
its fixed ROM. These sites are outside the residue's five holders, so its five
copies remain intact. The local maintenance step votes the target's new Address
to 3 with Flag1=0 and new Age=CAPTURE_AGE. Signal capture then reads the surviving
Data low bit. The actual target emits Signal=4; its comparison emits Signal=0.
No Flag1/address-change clearing suppresses that output.

Independent scalar and native evaluation agree on all 154 target output words
in both cases. The saved NPZ includes the complete 41-site paired inputs and
complete target outputs. This is a concrete failure of residual separation when
the Address premise is removed. It is not a failure of the conditional previous
repair result, proof of eventual logical corruption, or a measured activation of
the actual even-valued residuals.

## Validation and next obligations

Accepted receipts under `figs/fixed_rule/`:

| Receipt | Runtime | Process peak RSS |
|---|---:|---:|
| `retimed_holder_residual_noise_domain_v1.json` | 2.797297 s | 72520 KiB |
| `retimed_holder_residual_noise_audit_v1.json` | 6.797511 s | 69244 KiB |

Six focused tests pass in **4.453 s**, including rejection of a controller leak,
copying uncorrected Data, and declaring an Info memory word inert. They also run
the scalar/native address witness and a fresh-replacement probe. All watchdogs
are terminal with exit zero and a 1 GiB limit. Exact commands appear in their
receipts. No GPU job or shared source was touched. Final integrity index:
`figs/fixed_rule/retimed_holder_residual_noise_evidence_v1.json`.

The rule, ROM, physical state width, Q/U and neighborhood are unchanged. This
result strengthens a property of the specialized candidate justified by Gray's
ProgramBit projection and Gacs's suitably modified self-rule framework; it does
not resolve printed Flag2 or computed-SimBit ambiguities.

Next, actual fresh geometry faults must be handled in the full noisy entry and
repair relation. One cannot discard tail residue simply because it was inert
after the first burst. A stronger repair domain must either retain its interaction
with later geometry damage, or establish actual physical erasure through a
carefully revalidated fixed rule. Neither is established here. General damage
amplification, stochastic thresholds, robust finite caps, depth three and Q/U
optimization remain open; the full project goal is active.
