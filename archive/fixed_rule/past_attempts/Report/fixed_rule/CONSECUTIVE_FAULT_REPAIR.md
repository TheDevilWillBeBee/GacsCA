# Consecutive physical faults: conditional repair invariant

2026-09-27. The unchanged fixed G rule now has a checked conditional repair
argument allowing faults on consecutive ticks. Literal active-controller
experiments exercise surviving discrepancies when the next faults arrive.
An interacting negative control shows why spatial sparsity at each time alone
is insufficient. This advances continuing-noise analysis; it does not establish
the full Gacs correction/amplification theorem. The project goal remains active.

## One-step statement and induction

Use the healthy-context premises of [TWO_TICK_REPAIR_THEOREM.md](TWO_TICK_REPAIR_THEOREM.md):
canonical Address, uniform legal Age, zero healthy Flag1/Flag2 and all Wf copies,
coherent fivefold procedure copies, and coherent fivefold Signals. Logical
Data/head/controller/mail words are unrestricted. The domain is the infinite
line or a periodic ring whose size is divisible by Q.

Let x be the healthy input. Before the current faults, let z differ from x only
in procedure fields at sites P. Apply arbitrary full projected-state replacements
at sites D to obtain y. Assume:

1. Every eleven-site interval contains at most two sites of D.
2. Every five-site interval contains at most two sites of P union D.

Then **G(y) differs from G(x) only in procedure fields at sites D**. All geometry,
Signal, Wf and regenerated metadata fields agree everywhere. The healthy output
procedure copies are coherent. There is no global bound on the number of faults,
no one-head restriction, and no requirement for a fault-free tick between pulses.

For consecutive steps, write x_(t+1)=G(x_t), y_t=N_(D_t)(z_t), and
z_(t+1)=G(y_t). Start with z_0=x_0. Set P=D_(t-1), or use a verified smaller
residual-support set, at each step. If the healthy-context premises and the two
spatial bounds hold at each input time, induction confines each new residual
to procedure fields at D_t. A step with D_t empty restores complete equality.
This convention places a fault just before its following transition; it is
equivalent to the Poisson pilot's faults just after the preceding transition.

The `eligible` diagnostic checks only the two spatial bounds. It neither proves
healthy-context premises nor verifies an actual residual-support claim. Once
an earlier step violates the invariant, later empty fault sets alone do not
justify declaring the damaged state repaired.

## Complete-descriptor justification

The new certificate validates the existing 55 exact BDD geometry cases and
replays the complete structural and majority cuts, rather than accepting only
a prior success flag. It checks the full partition: 90 procedure, 15 other
mutable, and 49 hard-wired metadata words.

Previous residuals in P cannot affect geometry: its entire checked support uses
only geometry and primary Wf. Current faults satisfy the eleven-site bound, so
geometry repairs exactly. Signal votes see only current corruption and also
repair. Procedure votes may see both old residuals and new corruption, but
the union's five-site bound leaves at least three identical healthy copies.

After substituting these exactly matched corrected inputs, the complete DAG
cuts establish equality of every nonprocedure output, regardless of the damaged
center's old state. At a center outside D, old Address/Age/metadata also agree;
the remaining procedure outputs therefore agree. Any prior procedure residual
at that center is already behind a corrected vote. At centers in D, procedure
outputs may differ, which is exactly the stated invariant. G's fixed projection
restores all metadata from the repaired Address. The replayed output-copy
comparison establishes healthy procedure coherence for arbitrary logical words.

The certificate passes in **1.808048 s**, peak **64096 KiB**. Its trusted basis is
the inspectable Python BDD/DAG/algebra checkers and this dependency composition,
not a proof-assistant derivation or an independent compiler proof. Healthy
Signal/flag/Wf premises are **not** asserted invariant across capture/forcing.
The physical rule, ROM, alphabet and radius seven are unchanged.

## Literal experiments and distinguishing control

Two positive streams begin at the saved actual active NAND checkpoint from
[ACTIVE_EVALUATOR_REPAIR.md](ACTIVE_EVALUATOR_REPAIR.md), Age 1232619428, head at
9565. Complete projected-state replacements have randomized typed words and
deliberately wrong Age=0, so they leave real controller discrepancies after
one step. This is targeted deterministic testing, not an independent-noise sample.

| Stream | Faults | Observed behavior |
|---|---:|---|
| One holder moving right on each of eight consecutive ticks | 8 | 7–11 raw procedure words differ after each noisy step, confined to its latest holder. |
| Same adjacent pair on eight consecutive ticks | 16 | 7–21 raw procedure words differ, confined to that pair. |

In both streams, seven noise times overlap surviving discrepancies from the
preceding tick. One fault-free step after the eighth pulse restores **every raw
field**; the next step stays equal. Healthy and damaged states both execute the
literal full local G transition. No state is repaired by host replacement, no
simulated successor is installed, and no event or endpoint shortcut is used.

The negative control starts with coherent arbitrary Data at Age 17. Wrong clocks
and ROM addresses at sites 199 and 200 make two copies of logical Data_200 take
the neighboring Data value after one transition. A fault at site 201 on the next
tick supplies the same wrong value to a third copy. Each external pulse separately
satisfies the eleven-site condition; their union violates the five-site bound.
The wrong majority becomes coherent across holders 198–202 and survives the
next two fault-free steps: five wrong raw Data words remain. This demonstrates
failure of the per-time-only hypothesis, not a counterexample to the new lemma.

Native execution uses small shrinking causal windows: both trajectories retain
all 154 raw fields, initial padding is twice radius times the duration, and each
step discards one radius at each end. The retained region contains the entire
possible fault cone; artificial ring boundaries cannot affect it. All healthy
input contexts are checked explicitly. The driver passes in **1.839228 s**,
peak **128020 KiB**. No GPU job or CUDA rebuild is needed.

The independent scalar auditor replays **8960 complete physical output states**
(1379840 raw words), covering every retained output in both trajectories. It
checks injection records, input inheritance, spatial conditions by independent
window counting, residual supports, every saved output and final equality or
failure. Audit passes in **19.859934 s**, peak **104188 KiB**. Four domain tests
pass in **0.546 s**, including 10000 independent cyclic-window comparisons,
wrapping/moving/repeated supports and the overlapping-pulse rejection.

## Reproduction and handoff

From the repository root, all commands exited 0. Watchdog logs retain the exact
commands, limits and measured RSS; they were capped at 512 MiB, below the user's
40 GB allowance. Use new artifact names for reruns to preserve accepted evidence.

```sh
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_spacetime_certificate_v1_watch.json --seconds 60 --rss-mib 512 -- python -m experiments.fixed_rule.certify_retimed_holder_spacetime_repair --output figs/fixed_rule/retimed_holder_spacetime_certificate_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_spacetime_domain_tests_v1_watch.json --seconds 30 --rss-mib 512 -- python -m unittest tests.fixed_rule.test_retimed_holder_spacetime_domain -v
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_consecutive_faults_v1_watch.json --seconds 60 --rss-mib 512 -- python -m experiments.fixed_rule.retimed_holder_consecutive_faults --output figs/fixed_rule/retimed_holder_consecutive_faults_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_consecutive_faults_audit_v1_watch.json --seconds 180 --rss-mib 512 -- python -m experiments.fixed_rule.audit_retimed_holder_consecutive_faults --input figs/fixed_rule/retimed_holder_consecutive_faults_v1.json --output figs/fixed_rule/retimed_holder_consecutive_faults_audit_v1.json
```

New owned code: `retimed_holder_spacetime_domain.py`, certificate, literal driver,
independent auditor and domain tests. Evidence index:
`figs/fixed_rule/retimed_holder_spacetime_repair_evidence_v1.json`.
No shared module, existing physical executor, ROM, job or dataset was modified.

The next execution task is to use the invariant to organize independent fault
cones at higher rates, while evaluating interacting clusters and forcing contexts
explicitly. No new execution shortcut has been installed. General cluster repair,
stochastic rates/thresholds, noisy depth-two work periods, robust caps, Q/U
optimization and depth three remain open. Existing Flag2/SimBit source ambiguities
and cap limitations are unchanged.
