# Two-sided Signals and arbitrary physical flags

2026-09-26. The retimed CPU reference now retains both coherent Signal sides and
arbitrary Flag1/Flag2 patterns on canonical geometry. Three colonies completed
two whole physical periods without reinitialization in 137.951468 s, using
67544 KiB peak RSS. Every encoded raw output passed an independent
scalar/descriptor audit. Both physical flags were nonzero during forcing and
cleared before each commit. The fixed physical rule, ROM and alphabet are
unchanged.

This removes the left-Signal exclusion of [CPU_PACKET_PERIODS.md](CPU_PACKET_PERIODS.md).
It does not complete practical depth two or cross-level noise amplification.
The three-colony ring aliases represented neighborhood positions; the preceding
15-colony mixed-right experiment remains the nonaliasing full-period evidence.

## Rule identity and justification

Q=32768, U=2147483648, radius seven, raw 154 words/4090 bits, projected 105
words/2704 bits. Descriptor
`6e2f29f61bf281ec5d346cd58e717cf7e5b0afea263d2c17a18a58de295d8d23`;
ROM `4dc026b976c541001421dd214df9c9e33f6f851053d4ba5f53dbbec925ba5645`.
No depth parameter or new physical register was introduced. The host stores
existing physical flag bits compactly; it does not select a transition by level.

The source interpretation remains Gray pp. 31–32's specialized hard-wiring after
ProgramBit projection and Gacs §§9.2–9.3's identical/suitably modified rule.
[RETIMED_NOISELESS_MACROSTEP.md](RETIMED_NOISELESS_MACROSTEP.md) gives the existing
descriptor-semantics composition and its limitations. Candidate-B Flag2 is an
explicit alternative to the printed persistence counterexample, not a claim
that this experiment verifies the printed recurrence unchanged. The prior SimBit,
D10, malformed Info and finite-cap caveats remain.

`prove_retimed_holder_general_flags.py` adapts the preserved general-flag proof
to the actual retimed descriptor. Four forcing-clock regimes pass in 1.808016 s.
Each case has 51 independent Boolean variables: 15 Address bits, 30 raw flags
and six independently chosen neighboring Signal bits. The selected complete F
outputs are geometry, Signal and all ten Wf replicas. Input Wf is derived from
the current flags/Signals; arbitrary inconsistent Wf is outside this domain.
The pre-existing retimed all-clock Signal/flag certificate covers the canonical
formulas, forcing predicates and directed clearing implications, including
prefix/wrap regimes. It is not replaced by the four suffix checks.

## Exact physical representation and acceleration

`retimed_holder_flags_cpu.py/.c` retimes the existing candidate-B packed physical
recurrence. A 64-bit word stores 64 consecutive physical flag bits. Run-length
compression merges only identical neighboring word pairs. Each output bit uses
its old physical radius-five neighborhood. Flag2 can depend on the adjacent
colony when computed Flag1 is on; this dependency is retained.

No Flag2 front shape or propagation speed is assumed. A time skip is allowed
only after one complete recurrence step produces exactly the same run list, and
it stops at the next forcing-clock boundary. The standalone flag component has
fixed coherent Signals during a call. The composed executor never runs it across
a capture boundary without the literal full-F capture step. Host colony capacity
is limited to 64, independently of the physical rule's allowed encoded depth.

`retimed_holder_cpu_general.py/.cpp` combines these actual flag states with the
previous physical packet/controller representation. Literal boundary steps call
complete F at every physical site with actual old flags, both Signal sides, and
derived Wf. They retain the returned Flag1/Flag2 bits and captured Signals.
Unsupported incoherent Signal capture rejects atomically.

Within regular clock intervals, controller and flag evolution compose through
the proved canonical factorization. Controller event calls erase context only
within that identity; reconstructed cells retain full actual context. Flag
updates and controller updates are staged before publication. Packets and new
emission during nonzero-flag/forcing intervals reject, so this backend does not
silently bypass physical Flag1 mail clearing. Faulty geometry, arbitrary raw
procedure exceptions and inconsistent Wf remain unsupported.

## Verification and execution

Six focused tests passed in 7.315 s. They include 768 complete raw-state
comparisons at every bit of selected edge/interior packed words against native
full F, two-sided capture, forcing/cutoff/wrap, an active controller with arbitrary
flags, atomic SEND rejection, arbitrary-flag clearing, and fixed-point skips
compared with literal stepping across clock boundaries. Five saved-state audit
tests passed in 0.624 s, including rejection of an omitted left Signal and an
uncleared physical Flag2 bit.

The first test attempt failed because a test requested a quiet step at
WF_START, which also executes reset 3. The backend correctly rejected that
request. The corrected test executes literal reset and separately compares its
flag outputs to the packed recurrence. The failed log and exact test source are
preserved as `retimed_holder_cpu_general_tests_v1.log` and
`retimed_holder_cpu_general_failed_test_v1.py.txt`. No implementation change was
needed for that failure.

The complete-period fixture adds represented Flag2=1 to the earlier varied-Data,
active-controller initial state. Only initial Info is populated; histories and
physical scratch start empty. Actual gathers, both evaluations, ten Signal SENDs,
capture, forcing/clearing and commit execute twice without host reinitialization.
At each commit all 98304 physical cells pass E validation. The trajectory contains
4246107 full raw F calls, 1035477 colony controller event ticks, and 38868 actual
emitted/delivered packets. The flag component executes 109236 literal recurrence
ticks and 2789604 packed word evaluations; stable intervals use checked skips.
Literal boundary calls account separately for their actual flag updates.

The independent snapshot audit passed in 0.668380 s at 58304 KiB peak RSS. All
462 raw Info words per commit match both scalar F and its word descriptor.
Thirty-five represented controller words change in the first upper tick; none
change in the second. Both retained Signal sides are one in all three colonies.
Each cutoff snapshot has 98304 ones in each flag field; all physical flags and
controllers are zero at the next entry boundary. This is two one-link periods,
not an executed complete upper work period.

The separate trajectory study covers all 16 two-colony Signal patterns, nine
saved ages and 98305 physical ticks per pattern. Every Flag1 frame matches the
independently certified front formula; 2016 selected full-F neighborhood checks
cover flags, Signal and all Wf replicas. Comparing right=(1,1), left=(0,1) with
right=(1,1), left=(0,0) detects Flag2 differences in the first colony, establishing
that independent-colony flag evolution would be wrong. An arbitrary random flag
field on 98304 sites clears Flag1 within Q/2 ticks after forcing stops and both
flags within Q ticks. Total study time was 10.294260 s, 67924 KiB peak RSS.
These are canonical flag-clearing measurements, not stochastic noise-robustness
or faulty-geometry repair measurements.

The evidence index `figs/fixed_rule/retimed_holder_cpu_general_evidence_v1.json`
binds four passing manifests, both snapshots, the 11 passing tests, preserved
failure artifacts and the reused all-clock/local-transfer/period certificates.
All new jobs are terminal; successful implementation sources remain frozen.

## Reproduction and next work

All commands used `ulimit -v 524288` and `OPENBLAS_NUM_THREADS=1`; private native
builds remain under `figs/fixed_rule/build/`. No GPU, shared CUDA artifact, shared
source or historical dataset was changed. The separate GPU reservation remains
pending and unused. Commands below use outputs/logs preserved in that namespace.

```
python -m experiments.fixed_rule.prove_retimed_holder_general_flags --output figs/fixed_rule/retimed_holder_general_flags_v1.json
python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_cpu_general.py -v
python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_cpu_general_audit.py -v
python -m experiments.fixed_rule.run_retimed_holder_cpu_general_periods --colonies 3 --periods 2 --output figs/fixed_rule/retimed_holder_cpu_general_periods_3_v1.json
python -m experiments.fixed_rule.audit_retimed_holder_cpu_general_periods --execution figs/fixed_rule/retimed_holder_cpu_general_periods_3_v1.json --output figs/fixed_rule/retimed_holder_cpu_general_periods_3_audit_v1.json
python -m experiments.fixed_rule.retimed_holder_cpu_flag_trajectories --output figs/fixed_rule/retimed_holder_cpu_flag_trajectories_v1.json
```

Next: validate explicit raw replica defects and encoded-layer repair using actual
local transitions, then compose those trajectories with this general context.
Continue retimed GPU adaptation against saved CPU states when scheduling is
available. Practical full depth two still requires major cost reduction or
justified acceleration; U^2 literal time remains 2^62 ticks. General noisy geometry,
Flag1-masked mail, cross-level amplification and robust finite termination remain
open. U<=128Q is not a requirement.
