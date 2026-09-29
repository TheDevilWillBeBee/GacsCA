# Compact timed correction across levels

2026-09-27. The unchanged compact rule now corrects explicit lower physical faults
during actual middle evaluator computation. Local correction and correction by
the simulated layer are distinguished, with a three-copy negative control and
complete physical-state rejoin. All six retained lower banks are independently
recomputed. These are deterministic pulse experiments, not a stochastic threshold
or the complete Gacs/Gray correction/amplification theorem. The goal stays active.

## Fixed construction and live checkpoint

Q16384, U1073741824, radius7, physical154words/4090bits and projected105words/
2704bits remain fixed. Descriptor53f7adbf7c34df6b17897b20a0d0654108f23a9c064defb89bb3c6d1a7fb846b;
ROM4d055889959a880f189539dc213801780f8e2efa3daa7cb31e72cb3003f48b32.
No new transition, hardware register, ROM or depth-dependent interpreter is used.
The source interpretation remains Gray31–32 specialized hard-wiring/ProgramBit
projection and Gacs9.2–9.3's suitably modified self-correcting simulation. The
candidate-B Flag2, voted-old-Signal D10 and printed Flag2/SimBit qualifications
remain unresolved; this experiment does not establish the papers' noise hypotheses.

An actual compact colony execution reaches Age a=508479315, before instruction2216
reads operand B of NAND inside the compiled complete-rule description (not its
metadata prelude). Its operands are a=3129,b=3130,d=3131. Every raw field is retained
at M_(a-1),M_a,M_(a+1),M_(a+2). Three complete native full-ring transitions agree
with these GPU checkpoints; selected raw GPU reads agree with the independent
snapshot reconstruction. The head performs READ_B at3130 -> WRITE at3131 with
the expected NAND value. The same physical state continues to its complete period
boundary; decoded output is checked against the intended self-simulated rule.

Two literal raw rb-bit faults at physical holders3132/s0_rb and3131/s1_rb rejoin
the entire healthy middle ring after one tick. Adding3130/s2_rb is a three-copy
control:15raw words differ, and the head stays in READ_B with wrong rb instead of
performing the expected WRITE. Six total native complete-ring transitions are
executed,2523136raw words each; scalar F independently checks every causal-frontier
output for both fault cases. No represented controller fields are omitted.

## Complete encoded bottom checkpoint and pulses

From the [complete-state identity](COMPACT16_ENDPOINTS.md), bottom state at aU is
B(M_(a-1)), whose Info is M_a. Its full bank and Signals are streamed by the same
fixed GPU endpoint operator, starting from the actual prior middle state. This
represents the depth-two trajectory from E(E(top)) without literal aU replay.
It preserves inherited scratch; it is not a fresh E(M_a) initialization.

The finite ring has268435456bottom sites. Checkpoint time is545975507154370560.
Each saved bank has56557568uint64 words/452460544payload bytes plus Signals.
All complete Info equals the observed live middle checkpoint. The periodic
one-cell top is a fixture, not a robust finite cap or sustained top computation.

At this nonzero time, ten explicitly enumerated lower Data-bit flips encode two
wrong middle rb copies: all five lower physical copies of each of two Info words
are flipped. The fifteen-bit control encodes three wrong middle copies. The pulse
adapter returns the actual damaged Info and sparse bank updates; all other bank
words and Signals remain the saved checkpoint. It rejects incomplete copy sets,
duplicates, wrong fields and inconsistent masks without mutating the checkpoint.

Healthy, two-copy and three-copy cases then use the identical tiled operator.
Each successive input is actual prior device-output Info. Host operations only
initialize, inject specified faults, transfer/store and independently diagnose.
Host local-rule/evaluator/image routines are forbidden during GPU evolution.

After one lower period U, the ten-bit case has the correct middle NAND successor
and every middle raw field agrees with healthy. Nevertheless56lower bank words
still differ:42history and14vote words in seven colonies3127..3133. Info and Hold
already agree. After the next lower period, all56557568bank words and every Signal
agree. The terminal domain also fixes geometry, controllers/mail/flags/Wf and
static metadata, so this is **complete physical-state rejoin by (a+2)U**, namely
545975509301854208. No earliest-rejoin claim is made. Determinism then gives all
later noiseless equality. The fifteen-bit control retains the15wrong middle words.

The first damaged lower period is allowed because its complete coherent state
is E_loc(damaged-middle), even though its represented controller is faulty. This
is not permission to skip arbitrary lower faults or project them into that domain.

## Initially incoherent lower faults, with literal prefixes

The same saved bottom checkpoint also supports independent complete physical
one-tick experiments. Native and scalar full radius-seven F agree on every output
in the entire causal cone; outside it the compared neighborhoods are identical.

| Bottom bit flips | Result after one literal bottom tick | Verified continuation |
|---|---|---|
|4: two lower copies of each of two words|Full healthy state|Healthy trajectory|
|6: three lower copies of each of two words|Same full state as the ten-bit coherent pulse after one tick|Middle repairs after U; complete bottom rejoin by2U|
|9: three lower copies of each of three words|Same full state as the fifteen-bit control after one tick|Middle NAND successor differs|

Causal cones have32,38,57outputs, all154raw fields checked. Wrong Info explicitly
survives the first tick in the6/9-bit cases; local normalization is not called
repair. Coupling is full physical equality at the same Age1. Determinism permits
reuse of the remaining U-1 ticks of the corresponding verified coherent run;
the clock is neither reset nor advanced twice. The endpoint API still rejects
generic incoherent entries. CPU native execution here is the physical local
rule, not host replacement of an evolving simulated-layer transition.

## Independent validation and resources

The separate audit verifies observed fault coordinates against every Info change,
hashes every complete bank, runs the full native descriptor on every middle cell
for all six steps, and independently recomputes every lower bank word using the
SSA diagnostic without physical register reuse. It checks339345408bank words,
15138816raw middle output words, every Signal and both paired complete-bank
comparisons. Audit56.706686s; watchdog57.018238s/1184352KiB sampled childRSS.

| Run | Total seconds | GPU calls seconds | Sampled child RSS KiB |
|---|---:|---:|---:|
|Actual middle evaluator and literal faults|13.828732|Included in total|353820|
|Bottom checkpoint|5.619980|1.150437|695124|
|Healthy lower continuation,2periods|9.353271|2.011918|734952|
|Ten-bit pulse,2periods|10.446712|2.330515|770424|
|Fifteen-bit control,1period|5.983852|1.035164|773708|
|Literal lower prefixes|2.307269|CPU only|52632|

Each streamed GPU case has25161272explicit device-buffer bytes. Context/runtime/
graph allocations are excluded; no total GPU-process peak is claimed. Every GPU
probe used a90s watchdog and at most1GiB sampled childRSS; middle768MiB. CPU audit
used120s/2GiB; literal prefixes60s/768MiB. Total concurrent host use stayed well
below40GB. No large GPU reservation was used; main agent retains substantial GPU
scheduling. All owned jobs are terminal. No shared source/job/build/data changed.

Six tests PASS1.874s: exact physical pulse mapping, preservation of inherited
scratch, rejection without mutation, complete actual Info transport, raw active
controller reconstruction, missing Signal/inconsistent Data rejection, and exact
saved-state restore followed by a physical GPU tick. Test watchdog2.395096s/
265824KiB. All runs/checks pass; there are no discarded failures in this milestone.

## Reproduction and ownership

New modules: compact16_holder_active_snapshot, cuda_general_snapshot,
checkpoint_pulse. New experiments: compact16_holder_active_evaluator_faults,
compact16_holder_timed_depth2, audit_compact16_holder_timed_repair,
audit_compact16_holder_timed_prefix, seal_compact16_holder_repair. New tests:
test_compact16_holder_checkpoint_pulse and test_compact16_holder_active_checkpoint.
All source/evidence/build/report work remains within owned fixed_rule namespaces.
The existing compact physical rule, ROM, kernels and prior831-file seal are intact.

From repo root, use fresh output names and wrap commands with
`python -m experiments.fixed_rule.bounded_cuda_probe --output WATCH.json
--seconds LIMIT --rss-mib RSS -- COMMAND`:

* `python -m experiments.fixed_rule.compact16_holder_active_evaluator_faults --output OUT.json`
* `python -m experiments.fixed_rule.compact16_holder_timed_depth2 --case CASE --output OUT.json`,
  CASE=checkpoint,healthy,two,three in that order; driver references canonical
  fixture/checkpoint receipt names under figs/fixed_rule.
* `python -m experiments.fixed_rule.audit_compact16_holder_timed_prefix --output OUT.json`
* `python -m experiments.fixed_rule.audit_compact16_holder_timed_repair --output OUT.json`
* `FIXED_RULE_GPU_TESTS=1 python -m unittest tests.fixed_rule.test_compact16_holder_checkpoint_pulse tests.fixed_rule.test_compact16_holder_active_checkpoint -v`

Receipt stems: compact16_holder_active_faults_v1,
compact16_holder_timed_depth2_{checkpoint,healthy,two,three}_v1,
compact16_holder_timed_prefix_v1, compact16_holder_timed_repair_audit_v1,
compact16_holder_repair_tests_v1. Final seal: compact16_holder_repair_evidence_v1.json.
MAIN_AGENT_NOTES.md remains the other agent's reply channel, absent and unedited.

Next: compact-rule conditional repair certificates across clock contexts, repeated
space-time faults with literal handling outside proved domains, then cross-level
noise measurements with failures retained. Broader top rings, general malformed
geometry/Info recovery, full Gacs amplification, robust finite termination and
depth3 remain open. The ten/fifteen-bit and4/6/9-bit results are measured targeted
correction and negative controls; they are not broad stochastic robustness.
