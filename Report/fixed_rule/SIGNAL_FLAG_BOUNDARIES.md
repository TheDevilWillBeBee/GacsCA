# All-clock Signals, flag clearing and capture schedule

2026-09-26. Canonical geometry now has checked all-clock formulas for primary
flags, Signal and every Wf backup, with arbitrary other raw fields. Directed
ancestry gives a universal flag-clearing bound after forcing. Replaying the
actual packet schedule connects its ten final deliveries to the two five-buffer
Signal groups. This advances the period composition beyond the
[structural invariant](STRUCTURAL_INVARIANT.md); the semantic entry-to-macrostep
induction remains open.

## Full-descriptor boundary formulas

`certify_small_holder_signal_flag_boundaries.py` extracts 15 outputs from the
complete physical descriptor: Address, Age, Flag1, Flag2, Signal and all ten Wf
copies. It checks the independently written canonical formulas at all Q Addresses
and all 2^32 Ages. Only canonical Address and uniform Age are assumed. Other raw
fields, including all Data replicas, metadata, controllers, mail, Signals and
Wf, are arbitrary. No computation-coherence or head-count premise is needed for
these selected outputs.

At a noncapture tick each Signal bit becomes the majority of its five old raw
copies. At capture the relevant bit instead reads the low bit of that physical
holder's **old corrected Data**. Thus the five holders of primary 3 read their
respective buffers at Addresses 1 through 5; the five holders of primary Q-3
read buffers Q-5 through Q-1. Equal low bits give coherent new copies immediately.
Different buffer bits remain visible in the raw capture state. At the next tick,
the ordinary Signal vote makes all five copies equal to their majority.

The Wf outputs use voted **old Signal**, the candidate's existing D10 choice,
and the updated clock window. Wf2 also uses the computed Flag1 at its logical
primary. All these priorities are checked rather than replaced by a coherent
projection. Capture occurs well before the Wf window, so the schedule has no
same-tick capture/forcing dependency.

## Clearing without assuming a front shape

With Wf zero, the canonical Flag1 recurrence has the following implication:
if next Flag1 at Address a is one, some old in-colony Flag1 at a+2 through a+5
was one. A single nearest right neighbor cannot sustain it. Repeatedly tracing
an ancestor moves at least two cells right per tick and cannot cross the colony
boundary. After ceil(Q/2) ticks no ancestry path fits in the colony, so every
Flag1 is zero, regardless of its initial pattern.

Once computed Flag1 is zero, next Flag2 requires an old in-colony Flag2 at a-2
through a-5. Its ancestry moves left, giving the same bound. These implications
are checked by a six-bit BDD over all 64 assignments to the own flag and five
in-colony neighbor flags. Hence both flags clear within at most Q=32768 ticks
for this fixed even Q. Cross-colony Flag2 births while Flag1 is present do not
invalidate the argument: the second bound starts after Flag1 has vanished
everywhere.

At updated Age WF_END, every Wf copy is zero regardless of the old raw Wf or
Signal values. It remains zero through the suffix and clock wrap. The checked
off-window intervals explicitly include the U-1 to 0 transition. Consequently:

| Event | Physical Age |
|---|---:|
| Last forced Wf state ends | 2147549184 |
| Both flags guaranteed zero | 2147581952 |
| Final evaluation entry | 2281701376 |
| Margin before final evaluation | 134119424 ticks |

Starting a period with zero flags and Wf preserves zero flags throughout the
communication/capture prefix, regardless of retained Signals. The suffix
clearing bound restores that premise for the next period. These statements
assume no further injected faults and canonical geometry; they are not a noisy
colony-repair theorem. This generalizes the older suffix argument's Signal
assumptions and does not rely on a contiguous front profile.

## Conditional connection to the actual program

`join_small_holder_signal_schedule.py` replays the preceding
[mail schedule check](MAIL_FACTORIZATION.md), including its instruction-path
dependencies and packet-flight proof. All 6478 SEND occurrences end before
capture and forcing; precommit/final evaluation have no SENDs. Given the checked
trajectory, initially empty mail and zero flags/Wf, physical Flag1 erasure
therefore cannot remove a scheduled packet.

The final ten SENDs have zero colony hops. Five read the same Hold Flag2 word
at Address 9553 and deliver to 1–5. Five read Hold Flag1 at Address 9551 and
deliver to Q-5–Q-1. Each source is unchanged between its five SENDs and is not
a destination. The earlier access/collision checks exclude later controller
access to each delivered buffer. The head halts before capture and no intervening
reset, vote or commit overrides a delivered buffer.

| Signal primary | Last buffer delivery | Capture reads old Data at Age | Margin |
|---|---:|---:|---:|
| 3, from Hold Flag2 | 1906465983 | 1979711487 | 73245504 |
| Q-3, from Hold Flag1 | 1906786889 | 1979711487 | 72924598 |

This establishes the timing and common-source obligations for capture,
conditional on the actual checked instruction/Data trajectory. It does not
prove that trajectory is produced from every encoded entry, or that the Hold
words are the intended self-simulated outputs. Those semantic obligations remain.

## Literal witnesses and checks

The independent scalar/native audit compares all 154 output words at 1353 raw
boundary cases: 41 clock Ages, 11 Addresses and three flag/Wf modes. It also
saves 64 two-tick causal cones, covering all 32 buffer-bit patterns at both
Signal primaries. Another 1536 complete outputs agree. The first tick preserves
the five individual capture bits; the second makes them all the majority.
All initial/intermediate/final raw records are saved in the NPZ artifact.
No state is relifted or replaced between these physical transitions.

These capture fixtures use arbitrary raw metadata/controllers; they are not
fixed-ROM instruction executions or two hierarchy levels. They distinguish
two versus three wrong buffer bits under one Signal vote, not a stochastic
noise threshold or error suppression across levels.

| Check | Seconds | Peak host RSS (KiB) |
|---|---:|---:|
| All-clock formulas, clearing and off-window proof | 0.541882 | 58912 |
| Complete-output audit and capture witnesses | 11.059193 | 61224 |
| Schedule replay and boundary join | 1.509955 | 88948 |

Five focused tests passed in 0.517 s. They reject Signal passthrough, late/wrong
capture packets, cross-colony erasure ancestry and single-neighbor persistence;
they also check clock wrap and the clearing budget. No GPU run or shared edit
was needed; peak host RSS was about 87 MiB.

The first schedule join failed at replay equality because live tuples were
compared with JSON lists. Its log and source snapshot are preserved as
`small_holder_signal_schedule_v1.log` and
`small_holder_signal_schedule_failed_v1_source.py.txt`. JSON normalization fixes
that representation mismatch; the successful join is v2. No physical or timing
condition was changed.

Commands used `OPENBLAS_NUM_THREADS=1`, saving matching `.log` files. Preserve
existing outputs; choose new names for reruns.

```sh
python -m experiments.fixed_rule.certify_small_holder_signal_flag_boundaries --output figs/fixed_rule/small_holder_signal_flag_boundaries_v1.json
python -m experiments.fixed_rule.audit_small_holder_signal_flag_boundaries --certificate figs/fixed_rule/small_holder_signal_flag_boundaries_v1.json --output figs/fixed_rule/small_holder_signal_flag_boundaries_audit_v1
python -m experiments.fixed_rule.join_small_holder_signal_schedule --schedule figs/fixed_rule/small_holder_mail_schedule_v1.json --boundary figs/fixed_rule/small_holder_signal_flag_boundaries_v1.json --output figs/fixed_rule/small_holder_signal_schedule_v2.json
python -m unittest discover -s tests/fixed_rule -p test_small_holder_signal_flag_boundaries.py -v
```

SHA-256 values (prefix `figs/fixed_rule/small_holder_`):

| Suffix | SHA-256 |
|---|---|
| signal_flag_boundaries_v1.json | `9d208dbf236166a36d7b5455fe83b8bdf37bc24a15e8a60643909cdbec1c4253` |
| signal_flag_boundaries_audit_v1.json | `5e832521ebfc367293cb4ad03290785acc008614e266148c02ce5ee5e4348701` |
| signal_flag_boundaries_audit_v1.npz | `2d2f2a7e849f1e4c64a03afd876f1ed6fe5901c297756e151c3d6f630f901f30` |
| signal_schedule_v2.json | `845428172c35f46f1d6e040668b0553345beb531f8066c1cdc3e684603890c07` |

## Remaining work and source scope

Next connect actual encoded entries and controller/Data evolution to the
conditional instruction/packet schedule and prove the full commit/decode
relation over successive periods. In particular, earlier instruction leaves
with zero Signal/flag premises need a justified extension when retained Signals
or flag transients are present. The all-clock boundary results do not silently
remove those premises from old certificates.

Gray pp. 31–32 and Gács §§9.2–9.3 motivate the specialized self-simulator;
these checks concern the current fixed candidate, including its explicit
candidate-B Flag2 and old-Signal D10 choices. The printed Flag2 counterexample,
computed-SimBit source ambiguity, cap Address-defect persistence, full depth-two
periods and general noise suppression remain unresolved. The goal remains
correct self-simulation, practical two-level GPU execution and cross-level
repair, optimizing Q/U without imposing U<=128Q.
