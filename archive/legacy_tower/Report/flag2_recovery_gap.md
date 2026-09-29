# Flag2 recovery: a printed-rule counterexample (D8)

The full-Q transient experiment prompted a stronger check of D8. Gray's
supplied PDF was visually checked at p.21 (not only extracted text); Masumori
p.3 repeats the same condition. In a healthy colony, Flag2=1 turns off only
if **all** left neighbors in the colony have Flag2=1. Gray's p.22 prose says
isolated local/flag errors are immediately corrected; p.23 promises flags
return to zero, and Proposition 2 (p.26) bounds their residual lifetime.
The printed condition does not support those assertions on its own.

## Minimal invariant

Take perfect Address/Age, Flag1=Workspace.Flag1=Workspace.Flag2=0, and one
Flag2=1 at interior address a≥5. Its five left neighbors have Flag2=0.
The printed erasure condition is false; the unhealthy-colony condition is
inapplicable. No other cell gets four left 1's. Thus the singleton remains
unchanged, while Age advances and every other field stays healthy. The
same argument holds for blocks of two or three 1's. It is independent of
Age, so this is an invariant, not merely a long finite simulation.

More generally, in the healthy interior, let n be the number of left 1's:

\[
F'_2(x)=\begin{cases}[n\ge4],&F_2(x)=0,\\[n<5],&F_2(x)=1.\end{cases}
\]

For example, 0101… across a complete Q=8192 colony is also stationary in
Flag2: **4096 residual flag bits with perfect local structure**. Consequently,
Address/Age recovery alone cannot certify flag recovery.

Scalar, NumPy and CUDA agree on singleton/two-/three-cell witnesses at three
phases, including the trickle window and clock rollover. The alternating
pattern is separately checked. **9 tests pass**:
[tests](../tests/test_flag2_recovery_gap.py), [record](../../../figs/legacy_tower/flag2_recovery_gap_20260920.xml).
These passing tests establish a **fidelity discrepancy**, not noise robustness.

## Explicit candidate variants, not source-authorized corrections

In a restricted healthy-colony Boolean model (F1=WF2=0), compare:

| Healthy erasure condition | One isolated 1 | Two adjacent 1's after one step | Tested finite islands |
|---|---|---|---|
| Printed: no left 0 | Persists | Both persist | Leftmost interior 1 persists |
| Candidate A: no left 1 | Clears | One remains | Eventually clear |
| Candidate B: at most one left 1 | Clears | Both clear | Eventually clear |

Candidates A/B both clear tested widths 1,2,3,5,20 within 256 steps in a
128-cell colony. Candidate A changes one printed digit; candidate B additionally
fits immediate repair of two adjacent faulty flag bits, like Gray's Flag1
threshold. Neither is identified as Gray's intended rule without further
evidence. Both are now explicit opt-ins through
`Variant(flag2_healthy_erase="no_ones")` or `"at_most_one"`; Gray and Masumori
defaults remain `"printed"`. Scalar, NumPy, CUDA, compiled local computation,
and the finite-tower interpreter implement the same choice. Full
trickle-down interactions and error-separated wave bounds still need testing.
Gács uses a different Kind/Purge/Heal construction, not this literal Flag2 rule,
so his paper does not select a replacement threshold directly.

Backend agreement covers all 64 self/left flag patterns at six boundary/interior
positions, random damaged states, full colony computations and two successive
damaged upper transitions with all raw track copies. Together with the literal
witnesses and exact RNG tests, **29 tests pass**
([record](../../../figs/legacy_tower/flag2_variants_20260920.xml)). A further **33 tests pass**,
including the full-Q six-phase Gray interpreter under candidate B
([record](../../../figs/legacy_tower/flag2_gray_regressions_20260920.xml)). Candidate B adds 11
microsteps to local computation; it still fits the prescribed active intervals.

Three further [recovery-contract tests](../tests/test_flag2_repair_contracts.py)
pass at Q=8192 ([record](../../../figs/legacy_tower/flag2_repair_contracts_20260920.xml)):
256 adjacent two-site local-field faults (all eight flag-input bits exhausted,
Address/Age sampled at boundary/interior locations and three phases); a healthy
200-bit Flag2 wave whose leading and trailing fronts move two sites per step
and cannot cross a colony boundary; and a three-site Workspace.Flag2 pulse
near that boundary. The pulse is supplied externally: this is not a proof of
hierarchy-generated trickle-down recovery or separated-error bounds.

The two-site local-field contract also has a short deterministic argument for
candidate B. Starting from a healthy colony background, replace all local and
Workspace-flag inputs at at most two sites by arbitrary legal values. Each
five-site vote still contains at least three correct voters, so the apparent
colony and right Age majority are correct. Every inconsistency/Workspace
threshold of three fails. A pre-existing erroneous Flag1 has at most one other
flagged right neighbor, so computed Flag1 is zero everywhere. Flag2 cannot
turn on (its thresholds need four local or three Workspace flags); an existing
erroneous Flag2 has at most one other left 1, so candidate B erases it. The
right votes then restore Address/Age. This proves **one-step restoration of
Address/Age/Flag1/Flag2**, conditional on a healthy background; it does not
restore externally supplied Workspace inputs or prove simulation-track repair.
Candidate A fails precisely the two-adjacent-Flag2 part of this contract.

## Physical faults and paired noise audit

The printed-rule [physical experiment](gray_schedule.md#physical-transient-fault-experiment)
completed **2,097,152 steps**. At the final boundary, singleton/early-burst/late-burst
Flag2 counts are **1 / 4079 / 4228**, despite zero physical Address/Age errors.
The late burst corrupts one simulated cell's Address and Age at period 1;
period 2 matches every ground and conditional-transition field in all scenarios.
Decoded recovery therefore does not imply physical flag recovery.

A paired candidate-B run completed **2,097,152 steps in 1408.82 s**, using
identical fault-box coordinates, times, seed and counter version. The singleton clears on the first clean step;
both flags from the early 200×200 burst have cleared by step 8257, i.e. 7993
steps after the burst ends. At step 4360 they were still nonzero. Address/Age
recovery is unchanged at the sampled (16,57]-step bracket. The late burst clears
both flags within the sampled (4096,8192]-step bracket after its end.
All final physical flags are zero. Decoded outcomes are identical to the printed
run: one bad Address/Age cell at period 1, none at period 2. This is a paired
single-seed case study, not evidence of improved logical error probability.
[Checkpoint](../../../figs/legacy_tower/gray_physical_faults_erase1_20260920.npz),
[source/binary archive](../../../figs/legacy_tower/gray_physical_faults_erase1_sources_20260920.tar.gz).

Residual-state analysis separates encoded data, scratch, unused Info, and
inactive packed-word padding. At the second boundary the early/late bursts
leave 6/4 unused primary Info bits (30/20 raw copies) under **both** rules.
The late burst also leaves 1320 raw gathered-history bits. An exact-fingerprint
one-step reset probe of candidate B clears all those history differences,
but not unused Info or inactive padding (160/150 differing padding bits).
All encoded payload bits and reserved flag-signal bits are already correct.
Thus neither burst has exact full-state recovery; address/flag, simulated-state,
and full-state recovery must remain distinct metrics.
[Candidate analysis and reset probe](../../../figs/legacy_tower/gray_faults_erase1_residuals_20260921.json),
[printed static analysis](../../../figs/legacy_tower/gray_faults_printed_residuals_20260921.json).

![Completed candidate-B fault trajectories](../../../figs/legacy_tower/gray_physical_faults_erase1_20260920.png)

The separate [paired local-noise audit](../../../figs/legacy_tower/flag2_noise_audit_20260920.json)
completed 36 points: Gray/Masumori × valid/bit-width replacements ×
ε=0.4,0.5,0.6 × three erasers, with 128 independent rings per point,
Q=271, four colonies, 500 noisy + 500 clean steps, Workspace noise disabled,
seed 920 and explicit RNG v2. **Every paired original-address-phase recovery
outcome is identical across the three erasers.** At ε=0.5 the original/any-phase
counts are Gray-valid 1/26, Gray-bits 0/22, Masumori-valid 1/27,
Masumori-bits 0/22. This does not resolve the published 0.55–0.6 discrepancy.
Residual flags can differ even when the address outcome does not.

Zero observed paired disagreements does not establish equality of true recovery
probabilities. The degenerate bootstrap interval [0,0] in the raw file is not
an informative uncertainty bound here: the one-sided 95% upper bound on a
paired ring disagreement is `1 − 0.05^(1/128) = 0.02313` per comparison
(not simultaneous across all comparisons). The older local-noise audit lacks
RNG-version/source metadata and should not be pooled with this v2 run.

Next: extend independent physical-fault trials and test hierarchy-generated
trickle-down coexistence beyond the explicit local Workspace pulse.
The source does not uniquely establish this amendment; its justification must
remain the executable recovery contracts, not an attribution to Gray.
