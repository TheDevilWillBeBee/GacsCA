# Timed cross-level repair during actual middle computation

2026-09-27. The same fixed rule and GPU endpoint operator now execute targeted
faults during a middle evaluator's actual computation, with complete lower
scratch retained. Literal physical first-step checks also cover initially
incoherent lower replicas. This is measured deterministic correction across a
simulation link inside a depth-two configuration, not a stochastic threshold or
a general Gacs amplification theorem. The full project goal remains active.

## Actual checkpoint and its encoding

Let M_j be the middle physical trajectory initialized by E(top), using the
one-cell periodic `parents(1)` fixture. The preceding experiment
[ACTIVE_EVALUATOR_REPAIR.md](ACTIVE_EVALUATOR_REPAIR.md) actually executed that
colony to a=1232619428, immediately before NAND instruction 7075 reads operand B.
It retained every raw field at M_(a-1), M_a, M_(a+1) and M_(a+2), and independently
checked their complete adjacent transitions.

The complete-state terminal identity in
[TERMINAL_STATE_IDENTITY.md](TERMINAL_STATE_IDENTITY.md), together with successive
macrostep correctness, gives the bottom checkpoint **B(M_(a-1))** at time
**aU=2647030065837113344**, starting from E(E(top)). Its Info is M_a. The unchanged
GPU operator streams this full checkpoint: **324927488 uint64 bank words**,
2599419904 payload bytes, plus every Signal. Its complete Info is checked against
the actual M_a. The finite ring contains 1073741824 bottom sites.

This is a certified complete endpoint calculation; it does not replay aU literal
bottom ticks. The saved checkpoint includes inherited history, votes, Hold and
scratch. It is not replaced by fresh initialization E(M_a). The source-level
terminal identity applies to the complete canonical entry relation, including
arbitrary inherited scratch; it licenses the subsequent noiseless shortcuts.
The one-cell periodic top remains an aliased fixture, not a robust cap.

## Timed coherent pulses and actual successors

At the saved nonzero-time checkpoint, ten explicit bottom Data-bit flips change
two raw middle `rb` replicas. Each wrong middle word is represented by five
explicit physical lower copies. A fifteen-bit control changes three middle
replicas. `retimed_holder_checkpoint_pulse.py` retains the existing complete bank
and returns the actual Info after the sparse pulse. The damaged physical state
is precisely the saved bank/Signals plus its enumerated physical bit flips.
Nothing else is reinitialized, repaired or silently rounded.

Both healthy and damaged cases execute the same fixed GPU endpoint operator.
Every subsequent input comes from the actual preceding GPU output Info; host
code only transports those words. No host simulated transition is installed.
The middle successor is compared in all **5046272 raw fields**, including its
active controller and all backups, against the independently executed middle
trajectory.

After one lower period U, two wrong middle replicas repair and the running head
performs READ_B->WRITE/NAND. The three-copy control instead leaves READ_B and
changes **15 raw middle words**. After the repaired step, **120 bottom bank words
still differ**: 90 history words and 30 vote words in 16 colonies. Info and Hold
already agree. After the next lower period all **324927488 bank words** and every
Signal agree, establishing complete physical rejoin **by (a+2)U**, namely
2647030070132080640. This is not a claim about the earliest possible rejoin.
Once complete states rejoin, all later noiseless evolution agrees by determinism.

## Initially incoherent pulses: literal physical coupling

An independent physical-prefix experiment starts from the same complete saved
checkpoint and injects smaller, initially inconsistent lower-replica patterns.
It executes the full raw radius-seven rule on every output in the entire causal
cone. Native compiled-descriptor results also match the independent scalar
source transcription at every checked output. Outside that cone, neighborhoods
are identical by locality; no omitted output can distinguish the trajectories.

| Actual bottom bit faults | First literal bottom tick | Subsequent verified trajectory |
|---:|---|---|
| 4: two lower copies for each of two words | Repairs to the full healthy state | Healthy continuation |
| 6: three lower copies for each of two words | Spreads to the same full state as the ten-bit coherent pulse | Middle repairs after U; physical rejoin by 2U after the pulse |
| 9: three lower copies for each of three words | Spreads to the same full state as the fifteen-bit coherent pulse | Three-copy middle control fails the intended NAND step |

The causal cones contain 32, 38 and 57 output sites respectively, each checked
in all 154 raw fields. Wrong encoded values explicitly survive the first tick
in the six- and nine-bit cases. First-tick equality is equality of full physical
states with the coherent reference trajectories, not equality with the healthy
state. Determinism permits their already executed noiseless suffixes to be
reused at the same clock. The clock is neither reset nor advanced twice.
This supplies a literal prefix before any shortcut for initially incoherent
inputs; the endpoint API itself continues to reject unsupported incoherence.

The prefixes use the CPU native/scalar **physical** local rule, not a host
replacement of a simulated middle transition. Subsequent complete endpoints run
on GPU. No additional depth kernel, physical registers or rule-description
language was introduced.

## Validation and resources

The separate audit verifies the exact physical bit lists from observed Info
differences, hashes all six full banks, executes the middle descriptor at every
site for all six macrosteps, checks every output Info and Signal, independently
recomputes **54 complete scratch rows** using the DAG last-writer diagnostic,
and compares all physical bank words at both paired endpoints. In total,
**30277632 raw middle output words** are checked. Scratch recomputation samples
include the actual live head/fault neighborhoods; it does not independently
recompute every bank word. Backend agreement is not a universal proof of source
fidelity.

Three new CPU tests reject incomplete/duplicate/inconsistent pulses, check exact
physical fault sets and inherited-scratch preservation, and retain full Info
under an empty pulse. They pass in **0.241 s**. The physical-prefix coupling
additionally checks all its affected raw outputs with two physical evaluators.
The fixed descriptor and ROM hashes remain unchanged, as does the previously
memchecked private tiled GPU binary. No new CUDA compilation or sanitizer run
was required.

| Run | Wall seconds | GPU calls seconds | Reported host peak KiB |
|---|---:|---:|---:|
| Complete inherited checkpoint | 21.050353 | 3.506679 | 2974216 |
| Healthy, two lower periods | 46.876611 | 7.327523 | 3053548 |
| Two-replica pulse, two lower periods | 46.065193 | 6.837389 | 3055764 |
| Three-replica control, one lower period | 25.325487 | 3.683821 | 3016888 |
| Independent full-bank audit | 31.818229 | CPU | 5617740 |
| Literal incoherent-prefix audit | 4.188438 | CPU | 62004 |

Each GPU run uses **52880184 explicit device bytes**, below 64 MiB. Runs use an
8 GiB sampled host watchdog; the literal-prefix audit uses 1 GiB and small tests
512 MiB. All are below the user's 40 GB host limit. Retained banks use about
15.6 GB of disk payload in total. No shared GPU reservation, source, job or
historical artifact was modified. All jobs are terminal.

## Reproduction and evidence

From the repository root, set `OPENBLAS_NUM_THREADS=1`. The GPU driver is run
with `--case checkpoint`, then `healthy`, `two`, `three`, writing respectively
`figs/fixed_rule/retimed_holder_timed_depth2_<case>_v1.json`. Each invocation uses:

```sh
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_timed_depth2_<case>_v1_watch.json --seconds <limit> --rss-mib 8192 -- python -m experiments.fixed_rule.retimed_holder_timed_depth2 --case <case> --output figs/fixed_rule/retimed_holder_timed_depth2_<case>_v1.json
```

Limits are 90/120/120/90 seconds in that order. The independent commands are:

```sh
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_timed_depth2_audit_v1_watch.json --seconds 120 --rss-mib 8192 -- python -m experiments.fixed_rule.audit_retimed_holder_timed_depth2 --output figs/fixed_rule/retimed_holder_timed_depth2_audit_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_timed_prefix_v1_watch.json --seconds 60 --rss-mib 1024 -- python -m experiments.fixed_rule.audit_retimed_holder_timed_prefix --output figs/fixed_rule/retimed_holder_timed_prefix_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_checkpoint_pulse_tests_v1_watch.json --seconds 30 --rss-mib 512 -- python -m unittest tests.fixed_rule.test_retimed_holder_checkpoint_pulse -v
```

All exit 0. Existing outputs intentionally reject overwriting. The evidence index
is `figs/fixed_rule/retimed_holder_timed_depth2_evidence_v1.json`; it binds the
literal-prefix reference faults to the actual complete GPU cases.

## Remaining scope

The source motivation remains Gray pp. 31–32 specialized hard-wiring and Gacs
9.2–9.3 identical/suitably modified self-correction. No U<=128Q constraint is
introduced. Candidate-B Flag2, voted-old-Signal timing and other recorded source
ambiguities remain explicit. These are deliberately selected deterministic Data
bit pulses at a lower work-period boundary during real middle computation.
They establish neither arbitrary fault-time recovery nor a stochastic threshold.

Next, extend literal physical prefix checking to geometry, Signal and controller
faults near boundaries, recording non-rejoining cases rather than admitting them
to endpoint shortcuts. General full-alphabet noise, amplification bounds,
nonaliasing top colonies, robust finite-depth caps and depth three remain open.
