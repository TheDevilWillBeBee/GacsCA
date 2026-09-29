# Memory observables and the remaining payload construction

## Source distinction

Gray pp.15–16 identifies the remembered information with the initial **Address
phase**: translating the periodic address ground state gives Q distinct phases,
corresponding to log2(Q) stored bits. He explicitly distinguishes this from
Gács's stronger arbitrary one-bit-per-site memory. Thus measuring phase memory
is faithful to Gray, but must not be described as arbitrary payload storage.
[Supplied Gray text](../../../papers_txt/gray_readers_guide.txt).

The current simulator implements local structure and finite encoded simulation
states. Correct decoded transitions are not by themselves a persistent-memory
test: a simulated state can follow its intended rule while losing the original
phase, and a transient simulated error can later repair. Likewise, a shifted
ordered ring is a structure success but an original-phase memory failure.

## Operational measurements to add

For an Address array at level k, record the histogram

\[
h_k(a,t)=L_k^{-1}\sum_x [\,(A_k(x,t)-x)\bmod Q_k=a\,].
\]

Report separately: original-phase mass h_k(a0,t), modal phase (with explicit
ties), modal mass, exact original-phase recovery, and exact ordering at any
phase. Exact ordering while iid noise remains on is too stringent as a memory
observable; retain it as a structural diagnostic, not the sole memory criterion.
An observer for two selected initial phases should return the winning phase
only above a predeclared confidence/mass threshold, otherwise an erasure.
Count wrong-bit outputs and erasures separately, not as interchangeable events.

Lifetime studies need independent rings, right-censoring at the observation
horizon, and an explicit first-passage criterion. If sampling only every Δt,
first failures are interval-censored, not known to occur at the sample instant.
Hierarchy comparisons must report both physical time and work periods and
hold physical size/noise or logical size/noise fixed explicitly. Avoid the
one-terminal-cell aliasing geometry when interpreting phase diversity.

## Persistent-noise measurements (2026-09-21)

`experiments/phase_memory.py` implements the observer and stores every sampled
ring outcome, phase mass, final phase histogram, and first-observed failure
interval. CPU/CUDA observer and censoring tests pass (**3 tests**,
[record](../../../figs/phase_observer_20260921.xml)). Configuration: Q=271, four
colonies, 64 independent rings (32 per initial bit), phases 0/135, strict-majority
threshold, sample interval 10, persistent valid-field replacement noise v2,
Workspace flags forced zero as in the local-only protocol, seed 922.
Draws are paired across printed/candidate-B erasers. **No hierarchy is present.**

| Physical ε | Horizon | Rings with any sampled erasure, printed / B | Erased at horizon, printed / B |
|---|---:|---:|---:|
| 0.20 | 1000 | 0 / 0 | 0 / 0 |
| 0.30 | 10000 | 6 / 7 | 2 / 4 |
| 0.32 | 10000 | 24 / 24 | 10 / 11 |
| 0.34 | 10000 | 58 / 58 | 25 / 25 |
| 0.40 | 1000 | 64 / 64 | 64 / 64 |

No sampled wrong-bit output occurs. At ε=0.4 all first erasures are observed
at t=10, so the first observed failure excursion starts in (0,10]. At ε=0.2
all rings are right-censored at 1000; mean final original-phase mass is 0.798.
For each initial-bit stratum, zero observed failures in 32 independent rings
still allows a one-sided 95% failure-risk upper bound of **0.0894** over that
sampled horizon. These are pointwise bounds, not simultaneous across the sweep.

“Ever erased” versus “erased at the horizon” shows recovery from some observer
excursions. Do not label the first erasure irreversible memory loss, infer a
critical threshold from this short run, or treat time samples/cells as independent
trials. The small printed/B differences do not establish a candidate improvement.
[1000-step pilot](../../../figs/phase_memory_pilot_20260921.json),
[10000-step near-transition run](../../../figs/phase_memory_transition_20260921.json).

![Persistent phase retention and sampled first-failure survival](../../../figs/phase_memory_transition_20260921.png)

## Finite-size observer control (2026-09-21)

`experiments/phase_size.py` compares the whole-ring observer with a **fixed
absolute window [0,Q)** on each same trajectory. It does not relocate the
window to follow a damaged colony. Q=271, 10,000 persistent-noise steps,
sampling every 10, literal printed rules and local-only Workspace treatment
as above. Sizes have separate seeds; observers are paired, not independent
trials. A 64-ring pilot was repeated with **256 rings (128 per initial bit)**
and independent base seed 924. Both completed; all 24 source/archive members
of each run have been hash-verified. Eight observer tests and one uncertainty
formula test pass; these tests do not validate additional hierarchy machinery.

| ε | Colonies | Ever noncorrect: whole ring / fixed window | Final erasures: whole ring / window |
|---|---:|---:|---:|
| .30 | 1 | 34 / 34 | 7 / 7 |
| .30 | 4 | 25 / 73 | 8 / 10 |
| .30 | 16 | 4 / 131 | 0 / 14 |
| .34 | 1 | 256 / 256 | 52 / 52 |
| .34 | 4 | 212 / 256 | 93 / 69 |
| .34 | 16 | 191 / 256 | 126 / 77 |

Counts are out of 256 and describe the larger replication. The two observers
agree identically for a one-colony ring, as required. Increasing global
averaging suppresses some observed local excursions: at .30 and 16 colonies,
127 rings fail the window criterion while never failing the whole-ring one.
This does **not** isolate all physical size effects or prove local repair
worsens with size; boundary geometry and correlations also change.

One window emits the opposite bit: .30, 16 colonies, trial 105, initially
phase 135 (bit 1), first seen at t=6900 (previous sample 6890), with 37 wrong
samples through 7270. It returns the correct bit at the horizon. No whole-ring
wrong-bit output occurs. Thus erasures and reversible wrong-bit excursions
must remain separate from irreversible-memory-loss claims. Initial-bit strata
and paired contingency tables are retained for uncertainty analysis; cells,
samples and the two observers are not extra independent trials.

[Pilot](../../../figs/phase_size_20260921.json),
[independent replication](../../../figs/phase_size_replication_20260921.json),
[nine combined observer/uncertainty tests](../../../figs/phase_size_complete_tests_20260921.xml).
Plotting via `experiments/plot_phase_size.py` uses pointwise 95% Wilson
intervals **separately for each initial bit**, not a pooled iid assumption
across different phase encodings.

![Size dependence changes with the observer](../../../figs/phase_size_replication_20260921.png)

An exact replay of the .30/16-colony point matches **512,512 observer outputs
and all corresponding original-phase masses**, across every sampled time,
all 256 rings and both observers. The saved space-time data show a phase-0
region moving left through the fixed window and wrapping around the ring.
The window returns to the original phase, but the opposite phase is **not
eliminated**: at t=10,000 it still occupies 11.12% of the ring, versus 53.02%
for the original phase. Thus window recovery can reflect domain motion,
not actual removal of the error region. This is one exploratory trajectory,
not a population-level domain-speed or lifetime estimate.
[Replay and all phase histograms](../../../figs/phase_excursion_20260921.npz),
[replay driver](../experiments/phase_excursion.py).

![Wrong-phase region crosses the observation window](../../../figs/phase_excursion_20260921.png)

Every-step first-passage/recovery tracking is next; its proposed implementation
has not yet been applied. Future recovery analyses must distinguish observer
recovery from elimination, shrinkage, or transport of wrong-phase regions.

## Gács payload machinery still required

Gács Algorithms 19.5–19.8 (supplied PDF pp.188–190) do more than Gray's three
gathers: Compute legalizes retrieved/self codes, repeatedly decodes and
evaluates the rule three times, encodes each result, then votes the outputs.
Locally maintained command fields cause a separate payload processor to act.
Refresh-payload handles each packet by three decode/re-encode attempts followed
by a vote and copy-back. These are not supplied by merely adding a passive
bit to the present state layout or by taking a majority of three gathered
inputs once. Update-payload, germ/colony creation and the payload code family
remain additional components.
[Supplied Gács text, Algorithms 19.5–19.8](../../../papers_txt/gacs_2001.txt).

Next implementation order: extend these observables to size and hierarchy
comparisons on verified finite systems; an independently tested explicit
payload codec/refresh specification; then local executable packet processing
and its hierarchical interpretation. A host-side refresh oracle is useful for
tests but must not be counted as a cellular-automaton implementation.
