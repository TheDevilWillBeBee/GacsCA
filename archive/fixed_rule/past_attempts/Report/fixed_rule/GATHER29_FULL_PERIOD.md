# Full encoded-upper macrosteps for the optimized fixed rule

2026-09-28. **The shared-gather `gather29_holder_*` candidate completed two
continuous lower work periods on 15 encoded upper cells.** At each period
boundary, all 15 decoded upper cells agree with one application of this
candidate's own projected rule. The second period starts from the actual
physical state produced by the first; there is no host re-encoding between
them. This establishes exercised self-simulation on the stated canonical
trajectory, not a universal or noisy self-simulation theorem.

## Execution and independent check

The candidate remains one fixed radius-seven rule with Q=16384, U=536870912,
154 raw words/4090 bits, and a fixed own-ROM SHA-256
`dc5cf26b450b29673c1a9e9011df4852f69bada3c612aa10e38c1437585898eb`.
The complete physical description SHA-256 is
`71152fe782db86266ec4dad8f2dc84adeb71be7b190f13ece48fcf39d117261e`.
The initial physical ring has 245760 sites (15 colonies), with complete upper
raw states only in Info. Upper Data vary by site; one upper controller is
actively in `READ_B`, and raw upper Flag2 is set. The 15-site upper ring gives
15 distinct positions across the radius-seven neighborhood.

`run_gather29_holder_cpu_general_periods.py` evolves one retained physical
world for 2U=1073741824 elapsed lower ticks. Its new native local function is
compiled from the candidate's complete physical description, including AND,
the early branch, and phase-marked gather targets. Literal full-rule physical
steps are used at reset/vote/capture/commit boundaries. Between them, guarded
CPU head events, packet flights and packed physical flags accelerate regular
intervals. These are changes in the diagnostic executor, not in the physical
rule. Host upper-rule transitions are computed only as expected values;
`f.local_step` and `r.local_step` are patched to raise during the physical
`step`/`advance` calls. No upper transition is substituted into the Data
bank. The independently constructed audit applies scalar upper F and the
complete word description to every represented upper neighborhood.

| Check | Period 1 | Period 2 |
| --- | ---: | ---: |
| Actual lower ticks elapsed | 536870912 | 536870912 |
| Decoded complete upper raw words checked | 2310 | 2310 |
| Physical sites checked against the full entry relation | 245760 | 245760 |
| Gathered history words checked | 62010 | 62010 |
| Changed projected upper words | 108 | 97 |
| Changed represented controller words | 70 | 47 |
| Nonzero physical Flag1/Flag2 bits at forcing cutoff | 49152 / 212992 | 98304 / 180224 |
| Elapsed CPU time | 171.98 s | 168.63 s |

Across both periods, 53580 packets were emitted and delivered, with zero
recorded drops and none live at either commit. Actual left and right Signals
were nonuniform across colonies. Both final full Hold values and complete
Info commitments match the normalized raw upper outputs; controllers and mail
are empty at the age-zero boundaries. The independent audit verifies scalar
F equals the full descriptor on all 30 upper output computations and checks
all committed Info words, raw flags, non-MEM Data, and source/artifact hashes.
The run took 341.03 s on CPU with sampled peak RSS 376136 KiB; no GPU job or
shared CUDA artifact was touched.

The new event accelerator was checked separately against literal full-ring F
on *actual evolved states*: marked ADD and SEND FETCH steps at each of the
three gather ages, plus both early and late branch outcomes. Eight comparisons
cover 8×16384=131072 physical site steps and agree in complete Data, controller,
location, Signals and flags. The native C descriptor compiler also agrees with
scalar `f.local_step` on random typed and clock-boundary neighborhoods.
`python -m unittest tests.fixed_rule.test_gather29_holder
tests.fixed_rule.test_gather29_holder_physical_events -q`: 10 passed in
10.143 s. The prior branch/retimed-branch/gather candidate tests also passed
18/18 before these two new physical tests were added.

Reproduction from the repository root:

```
python -m experiments.fixed_rule.run_gather29_holder_cpu_general_periods --colonies 15 --periods 2 --output figs/fixed_rule/gather29_holder_cpu_periods_15_v1.json
python -m experiments.fixed_rule.audit_gather29_holder_cpu_general_periods --execution figs/fixed_rule/gather29_holder_cpu_periods_15_v1.json --output figs/fixed_rule/gather29_holder_cpu_periods_15_audit_v1.json
python -m experiments.fixed_rule.seal_gather29_holder_periods --execution figs/fixed_rule/gather29_holder_cpu_periods_15_v1.json --audit figs/fixed_rule/gather29_holder_cpu_periods_15_audit_v1.json --output figs/fixed_rule/gather29_holder_cpu_periods_15_seal_v1.json
```

These commands have completed successfully. The seal records source and
compiled-binary hashes, the two decoded state hashes, artifact hashes, packet
counts and the selected literal event check. Output files are data under
`figs/fixed_rule/` and remain uncommitted. A one-cell pilot and separate audit
are retained as earlier checks.

## Exact scope

One **lower** work period represents one upper-cell transition. Thus this run
checks two upper transitions on 15 upper cells; it does **not** execute an
entire upper work period of U upper transitions, which would require roughly
U² bottom ticks at depth two. It also does not test a full Q-cell upper colony
or 63-cell repair fixture. The evolved states have canonical coherent geometry
and coherent two-sided Signals. The event accelerator has guarded domains and
selected literal comparisons, but the whole 2U trajectory was not replayed
literally one tick at a time. Broader physical-event composition, damaged
upper states, simulated-layer repair, and noise amplification remain open.

Within that scope, the previous blocker is resolved: the optimized fixed
branch/shared-gather rule actually computes, communicates, commits, decodes,
and continues its own upper dynamics over complete lower periods. Further
Q/U optimization should retain this two-period regression and independent
audit as acceptance tests.
