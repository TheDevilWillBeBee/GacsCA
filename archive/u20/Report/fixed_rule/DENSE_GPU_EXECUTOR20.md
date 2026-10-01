# Complete-rule dense CUDA performance at Q=8192, U=2^20

2026-09-29. The [U20 candidate](DUAL_PASS_U20.md) still has one fixed
radius-seven, 6,465-bit physical rule and optimized 14,830-operation complete
own-F description, SHA-256
`16bf88a1d4ff5496cd3b61a1200f8a809db1438472a9191fded26de3a0786257`.
The new `stream28_dual_dense_gpu20_tiled.{py,cu}` is an **execution backend for
that same rule**, with no upper-rule callback, event skip or hierarchy-depth
argument. Every `fr_run` tick launches the complete F on every physical site,
retains all 421 raw words in two state buffers and swaps them synchronously.
Its source layout is word-major on the GPU, but host input/output use the exact
existing raw codec. The backend is for validating full physical trajectories;
it is not an additional physical transition rule or a self-reference proof.

## What changed

The previous literal CUDA reference launched four 64-thread blocks, looping
all physical cells through 256 workers. At each site it staged all 6,315
radius-seven input words despite only 1,151 of them being used by the fixed
complete description. It kept site-major state, making adjacent workers'
same-field accesses strided. The new backend fixes 262,144 workers in 1,024
256-thread blocks, stages exactly those 1,151 statically identified input
words, stores the state by field for coalesced reads/writes, and writes each of
the 421 outputs directly to the next state. These changes are compile-time
properties of one backend and do not depend on encoded depth or input contents.
The final build uses `-maxrregcount=128` and unrolls the fixed input gathering.

For 31 colonies (253,952 cells), resident CUDA allocations are 4,751,491,072
bytes; one temporary transpose/read buffer raises the explicit peak to
5,606,801,408 bytes. The active-evaluator 31-colony measurement used at most
4,719,136 KiB host RSS, below the user's 40 GiB shared-RAM allowance.
The 80 GiB A100 had no compute process when the pilots began. No substantial
GPU job or shared CUDA artifact was started or rebuilt.

## Literal parity and timing

`OPENBLAS_NUM_THREADS=1 python -m unittest
tests.fixed_rule.test_stream28_dual_dense_gpu20_tiled -q` passed **4 tests in
35.838 s**, including compilation of the final 262,144-worker variant. It
compared all raw words against the earlier independently
native-checked complete-F CUDA reference for arbitrary typed 17-site states
over two ticks, a complete 8,192-site colony over three ticks, a moving
fivefold packet over 32 ticks, and an initialized active evaluator over 16
ticks. The 31-colony benchmark separately compared **every raw output word
after one full physical tick** with that same reference. The benchmark state
was then evolved for 1,000 consecutive literal ticks with no event skip.

| Ring | Fixture | Dense ticks measured | Seconds/tick | Complete site-ticks/s |
|---|---|---:|---:|---:|
| 15 colonies | canonical Address, otherwise zero | 1,000 | 0.007810327 | 15.73 million |
| 31 colonies | canonical Address, otherwise zero | 1,000 | 0.014005112 | 18.13 million |
| 31 colonies | initialized active evaluator | 1,000 | **0.014036944** | **18.09 million** |

The last receipt is
`figs/fixed_rule/dual_dense_tiled20_bench31_active_workers262144_v1.json`, generated with:

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.bench_dual_dense_tiled20 \
  --colonies 31 --ticks 1000 --fixture active-evaluator --check-reference \
  --output figs/fixed_rule/dual_dense_tiled20_bench31_active_workers262144_v1.json
```

At the measured active-evaluator rate, **four U periods** (4,194,304 physical
ticks) would take **58,875 s = 16.35 h** of uninterrupted GPU evolution.
The prior 1.75 s/tick figure for 31 colonies was itself an extrapolation of
the 256-worker reference pilot; its 85-day projection is about 125 times
larger than the new projection. The new 16-hour figure remains a projection
from 1,000 ticks, not a completed full-period run. Initialization, readbacks,
checkpoints, contention and any data-dependent repair diagnostics add time.
The generated WordCode is straight-line, which explains the nearly identical
zero and active-evaluator tick measurements, but full-period endurance and
decoded macrostep equality must still be measured.

## Tuning record and limits

At 31 colonies, 1,000-tick measurements before the final input unroll were:
32,768 workers 24.798 ms/tick; 65,536 workers 20.887 ms; 131,072 workers
18.766 ms; 262,144 workers 18.435 ms but with 4.75 GB resident allocation.
Under the 128-register cap and unrolled input gather, 131,072 workers took
15.563 ms/tick on the active fixture, while 262,144 took 14.037 ms/tick.
The 1.5 GB additional VRAM was acceptable for this 31-colony experiment, so
the faster 262,144-worker configuration was retained.
Its uncapped compiled kernel used 255 registers and 1,656 stack bytes per
thread. Capping at 128 registers reduced the measured time to 15.643 ms/tick
despite a 2,984-byte stack. A 64-register cap slowed it to 19.666 ms/tick.
Splitting the rule into fixed 1,024-operation functions lowered reported
stack use to 464 bytes but measured 15.841 ms/tick; the extra global-scratch
traffic/overhead did not improve wall time. The final unrolled input gather
and doubled worker count measured 14.005 ms on a zero fixture, then 14.037
ms on the active fixture.
All variant artifacts remain isolated under `figs/fixed_rule/build/`; no
failed variant is selected by the current module.

This backend solves the immediate **31-upper-cell dense-throughput problem**
well enough to make a long experiment conceivable. It does not solve the
larger Q²-cell depth-two GPU state: the current 421-word two-buffer encoding
would require about 421 GiB. Nor does it establish a full U-period physical
self-simulation, correct damaged-ROM evolution, a closed upper ring over
successive macrosteps, or noise amplification. The next step is to prepare a
complete 31-colony physical initializer and short checkpoint parity against
the event-composed audit, then coordinate a substantial full-period A100 run
with the main agent. A distinct packed backend would be needed for Q² cells.
