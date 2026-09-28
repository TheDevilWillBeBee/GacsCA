# Arbitrary physical context and quiet clock barriers

2026-09-26. Two new complete-descriptor checks remove the zero-context premise
from procedure reasoning and give explicit quiet reset/vote/commit relations.
They complement [STRUCTURAL_INVARIANT.md](STRUCTURAL_INVARIANT.md) and
[SIGNAL_FLAG_BOUNDARIES.md](SIGNAL_FLAG_BOUNDARIES.md). They do not alone prove a
work-period macrostep.

## Exact context reduction

Let Z clear only physical Flag1, Flag2, Signal and all ten Wf fields, preserving
every other raw field. On canonical Address and uniform Age, compare F(x) with
F(Z(x)) at **every** Address and Age. No coherence, head-count or zero-mail
assumption is imposed; raw metadata, Data, controllers and mail are arbitrary.

The new symbolic certificate proves:

- All 50 next Data/head/controller words agree with the baseline F(Z(x)).
- Each of the 40 next mail words equals its baseline word, except that computed
  holder Flag1 masks it to zero.
- All 49 static fields remain their exact old center inputs.
- Independent canonical geometry/flag/Signal/Wf formulas fill the other outputs.

Together these reconstruct all 154 raw output words. The rule, alphabet, radius,
parameters and ROM did not change. Z is a proof map, never an operation inserted
into an execution. Reusing F(Z(x)) is an exact reduction, not an independent
proof of that baseline's computation.

This lets the **procedure projection** of earlier instruction leaves admit
retained Signals and arbitrary flags/Wf. Their other premises remain: correct
entry/controller geometry, static/Data coherence, prescribed accesses and the
separate treatment of incoming mail. Full raw outputs must still include actual
context evolution. In particular, a Data value delivered by mail can affect
later computation, even though current head/controller outputs do not depend on
old mail. During scheduled SEND trajectories the prior flag-free-prefix result
removes holder masking; during flag transients the intended schedule has no
live mail.

Two distinguishing tests enforce these limits. Erasing context in a two-tick
mail witness changes final Data from 7 to 55, so the reduction cannot be iterated
as a replacement physical rule. A deliberately wrong physical Address causes
Flag1 to clear Data in F(x), while the erased-context baseline retains it:
canonical geometry is essential.

## Quiet reset, vote and commit

The second certificate assumes coherent old static/Data, canonical geometry and
zero old heads, controllers and mail. Physical flags, Signals and Wf are arbitrary.
It checks all Ages in one symbolic relation, covering 90 procedure words, 49
static fields and two geometry words. The separate all-clock boundary lemma
supplies the remaining 13 context outputs.

Every reset clears marked Data and bootstraps the selected ROM entry at the
first cell. The extra first-vote entry uses the final-evaluation PC. Votes read
the three **old** Data operands; at the simultaneous stage-five reset/vote,
the vote overrides reset clearing. At old Age U-1, marked Info copies its old
right-neighbor Hold word. Other quiet Data persists and mail stays zero.

The old-head premise is necessary. A literal test places a WRITE head on an
unmarked Info cell at a reset tick. Its same-tick Data write survives, even
though reset clears the controller. Thus proving the previous phase halted is
required before applying a quiet barrier. The earlier unmarked same-tick mail
delivery example similarly explains the zero-mail premise.

The first barrier attempt used syntactic equality for equivalent head selectors
and failed at `head`. Preserve its v1 log and
`small_holder_quiet_barriers_failed_v1_source.py.txt`. The successful v2 uses the
already-tested conservative Boolean abstraction for nonidentical expressions:
165 bit identities, 28,919 BDD nodes. Neither expected semantics nor the physical
rule changed.

## Validation and resource use

| Check | Result | Seconds | Peak host RSS (KiB) |
|---|---|---:|---:|
| Arbitrary-context reduction | Complete 154-word reconstruction, all Ages/Addresses | 0.573265 | 58424 |
| Quiet barrier relation | 141 words, all Ages/Addresses | 0.608712 | 66208 |
| Independent scalar/native audit | 1804 complete outputs | 7.456331 | 58444 |

The audit includes 615 full inputs and 615 context-erased comparisons, with
55,350 procedure-word comparisons and 584 cases having computed Flag1. It
combines arbitrary raw inputs with deliberately active controller/dense-delivery
patterns in all eight phases. Another 574 complete outputs check quiet barriers
against independent scalar formulas, using both arbitrary coherent metadata and
the actual fixed ROM. The 41 sampled Ages cover clock boundaries and neighbors.

Seven focused tests passed in 0.728 s. Besides the distinguishing cases above,
they reject a context-dependent PC and a dropped entry PC, and check old-Data
vote/reset and commit priorities. Peak host memory was about 65 MiB. No GPU run,
CUDA rebuild, shared-source edit or historical-data modification occurred.

Commands used `OPENBLAS_NUM_THREADS=1` and matching `.log` files. Use fresh output
names when rerunning:

```sh
python -m experiments.fixed_rule.certify_small_holder_procedure_context --output figs/fixed_rule/small_holder_procedure_context_v1.json
python -m experiments.fixed_rule.certify_small_holder_quiet_barriers --output figs/fixed_rule/small_holder_quiet_barriers_v2.json
python -m experiments.fixed_rule.audit_small_holder_procedure_barriers --context figs/fixed_rule/small_holder_procedure_context_v1.json --barriers figs/fixed_rule/small_holder_quiet_barriers_v2.json --output figs/fixed_rule/small_holder_procedure_barriers_audit_v1.json
python -m unittest discover -s tests/fixed_rule -p test_small_holder_procedure_barriers.py -v
```

JSON hashes (prefix `figs/fixed_rule/small_holder_`):

| Suffix | SHA-256 |
|---|---|
| procedure_context_v1.json | `9eb357e415e5c465e057789ce6a6d20aed7ec17794e78f8f66a703565476a031` |
| quiet_barriers_v2.json | `98f1bc72e422d6d29b8ce49a384e59877a5b8b1d2163b67355c5ddc13bed35f9` |
| procedure_barriers_audit_v1.json | `11df93f78caf716cc6ec946987902aab7bab247c318d9cd9cbc308407ddff241` |

## Remaining semantic composition

The existing ROM data-flow certificate checks all-input computation of the
normalized complete rule, including raw controllers, three histories, both
evaluations, metadata regeneration, Signal payloads and commit. It is conditional
on completed-instruction and timing abstractions. New local/context, structural,
schedule and boundary results now supply many of its previously missing leaves;
they must be assembled into an explicit physical induction rather than declaring
the old conditional certificate a macrostep theorem.

Next specify the complete allowed entry relation, including scratch, controller,
mail, flags/Wf and retained Signals, and prove its preservation after commit.
Check the interleaving of actual memory accesses and deliveries against the
batch Data-flow interpretation, prove quiet states at each barrier, and identify
the exact decoded modified rule G=pi F iota. This is still a proof obligation,
not a new accepted encoding or a completed self-simulation claim.

The source rationale remains Gray's specialized hard-wiring/ProgramBit projection
and Gács's identical or suitably modified self-correcting rule. The candidate-B
Flag2 and old-Signal D10 choices, printed-source ambiguities, finite-cap Address
defect, full depth-two periods and general noise suppression remain unresolved.
Correct self-simulation, practical GPU execution at two levels and cross-level
repair remain the goal; U<=128Q remains unnecessary.
