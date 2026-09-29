# Literal physical flags: bounded CPU history and isolated CUDA

These executors accelerate the frozen printed-rule `delivery_*` physical flag
projection on canonical geometry during the unforced interval [98Q,U]. They do
not change G, its complete self-description, alphabet, neighborhood, ROM, or
hierarchy encoding. They do not replace simulated controller transitions. Full
controller evolution must be composed separately using the established
factorization; these results alone are not complete hierarchy macrosteps.

## Preserved CPU results and failures

The native profile distinguished virtual-address baseline from history growth.
An initial 2 GiB limit was below NumPy's default approximately 2.6 GiB virtual
footprint. With OPENBLAS_NUM_THREADS=1 and OMP_NUM_THREADS=1, baseline VmSize was
107,484 KiB, VmRSS 30,832 KiB, one thread. The one-million-tick native query then
actually threw `bad_alloc` after 6.601196786388755 s under 1 GiB, at 11,744,052
nodes / 11,737,744 queries. Both profile records are retained. This identifies the
new probe's exception; it does not retrospectively identify every old catch-all.

`flag_byte_stream` keeps bounded query history, checks every accepted derivation
against independently generated complete-native rule truth tables, checks its
periodic input representation, then collects obsolete history. Budget failures
roll back and shorten the next physical time block. The frozen leaf transition
is unchanged. Five focused tests passed in 1.685 s, including rollback and
rejection of disagreeing truth tables. No depth dispatch is present.

The actual saved cutoff was advanced **1,048,576 ticks** in **871.8716364456341 s**:
12,631 accepted blocks, 14 retries, 2,084,150,597 queries, all checked before
collection, 2,961,734,522 leaf evaluations, peak explicit nodes 262,113 and final
explicit nodes 32,685. Final Age is 823,132,160, F1 count 94,371,840 and F2 count
72,627,515. The fixed 2 GiB virtual bound held; final block length had fallen to
four ticks, making continuation unattractive. Ephemeral derivations are not
retained for an independent offline replay.

Retaining old verified certificates passed five tests in 1.914 s but saved less
than two percent of query checks on this trajectory. That owned run was stopped;
its immutable accepted checkpoint is at 1,015,696 ticks (not the slightly later
progress observation), SHA-256
`f851dc6f4c6bca1130fff3ccd50741c769e9c8c46d4edd30fabd35f13269ad76`.
See `flag_stream_cache_stop_v1.json`. No shared job was affected.

## CUDA temporal blocks

Following the user's explicit suggestion, an isolated CUDA library was built
with CUDA 12.6 / nvcc V12.6.85 for the A100 (sm_80). Build files live only under
`figs/fixed_rule/build/flag_cuda_*`. Shared `gacsca/cuda` artifacts are untouched.
The original `flag_words.c` SHA is pinned, and its exact packed local operation
is mechanically extracted into the build header. Each uint64 word represents
64 consecutive physical sites; the two planes are F1 and F2.

Each CUDA block produces 256 physical words. For T<=512 ticks it loads
H=ceil(5T/64)+1 extra words on each side and evolves the actual rule in shared
memory. Artificial tile-edge inputs cannot reach the output core: their light
cone travels at most five **physical bits** per tick. Whole-ring wrap and actual
colony-boundary masks are applied from physical addresses. The maximum shared
allocation is 10,816 bytes per block. The 23-colony ring has 192,937,984 sites;
two device buffers require 96,468,992 bytes. There is no per-depth hardware.

The initial optimization tests whether the entire actual halo is homogeneous and
contains no colony edge. The homogeneous orbits are 00->00, 10->10, 11->11,
01->00. This shortcut cannot cross a forcing window; the Python entry point
rejects times outside [98Q,U]. It assumes neither a front shape nor a front speed.

Four tests passed in **5.250 s**: full dense CPU parity at T=0,1,17,257,512,515;
different temporal partitions; homogeneous and perturbed tile edges; complete
native local-rule comparisons; changes outside a selected radius-5T cone; and
invalid-domain rejection. A separate random three-colony ring verifies a
non-power-of-two periodic domain.

The actual cutoff pilot compared every bit of the 23-colony ring against the
existing CPU RLE executor. After startup, CUDA took 0.014740181155502796 s for
512 ticks and 0.020240334793925285 s for 4,096 ticks; CPU RLE took
0.029019500128924847 s and 0.09356453362852335 s. The first one-tick GPU call
included context startup and took 0.7333200760185719 s, slower than the CPU.

A second pilot was capped at 60 seconds and completed **1,048,576 physical ticks
in 4.923756510950625 s**. Independent expansion/validation of the saved CPU spatial
DAG and comparison of **all flags** took 0.8771763443946838 s and passed. The final
counts above agree. The approximately 177x wall-time comparison is specifically
against the CPU run that also verified every intermediate query; the GPU run
uses the tested physical kernel and an independent complete endpoint comparison.
This is not a pure hardware comparison with identical audit overhead.

Artifacts: `flag_cuda_tests_v1.log`, `flag_cuda_pilot_v1.*`, and
`flag_cuda_stream_compare_v1.*`. Both pilots archive the relevant source files,
including .cu, along with source, binary, input and output hashes.

## Further exact shortcut and negative continuation probes

A separately named `flag_cuda_fixed` retains the original implementation and
adds a general local fixed-point certificate. It computes the actual one-step
output for every halo word except the outermost word on each side. If all match,
the core stays unchanged for T ticks: the checked region still has at least 5T
bits of halo. Geometry masks are included in the check, so nonuniform stationary
patterns and colony edges are eligible. This matters for printed Flag2's known
persistent isolated defects; it does not turn those defects into repaired data.

Five fixed-point-shortcut tests passed in **4.859 s**. The first test run failed
because its purported stationary fixture included a Flag2 one at Address 0,
where the printed empty in-colony conjunction erases it. The corrected fixture
uses interior isolated defects. The failed log remains preserved.

A final GPU probe was capped at 60 seconds and completed in 52.59678079839796 s,
advancing from the verified million-tick state to **4,194,368 ticks after cutoff**.
The three million-tick blocks took 10.907700465992093, 16.913426966406405 and
22.742335700429976 s, so the first-million timing must not be extrapolated as
constant throughput. F1 was then entirely zero; F2 count was 59,665,313. A
complete-ring CPU one-step check took 0.11005553882569075 s and **rejected
stationarity**. A separate CPU probe checked 64 further full-ring steps in
12.001729661598802 s and found no return to its initial state. This is not proof
of aperiodicity, but neither fixed-point nor short-period skipping is justified.
`flag_cuda_stationary_probe_v1.*` and `flag_cpu_period_probe_v1.*` preserve these
negative results. No claimed quiet interval was added.

The separate `flag_cuda_audit_v1.json` passed in 2.0484075117856264 s: 160 frozen
source files, all flags against the CPU DAG, every F1 bit against the exact
prefix-erosion formula for this fixture, and 358 complete-native local checks.
The extra CUDA continuation after the million-tick comparison has tested-kernel
validation and complete endpoint one-step validation, not an independently
replayed multi-million-tick trajectory.

No substantial GPU suffix experiment is launched here. The main agent retains
GPU scheduling; the owned STATUS requests coordination before such allocation.
A full 251,658,240-tick literal suffix, composition with all controller fields,
and successive literal-rule work periods remain unverified.

## Commands

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m experiments.fixed_rule.flag_stream_execution --input figs/fixed_rule/flag_cutoff_checkpoint_v1.npz --output figs/fixed_rule/flag_stream_execution_v1 --ticks 1048576
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m unittest tests.fixed_rule.test_flag_cuda -v
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m experiments.fixed_rule.flag_cuda_pilot --input figs/fixed_rule/flag_cutoff_checkpoint_v1.npz --output figs/fixed_rule/flag_cuda_pilot_v1
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 timeout --signal=TERM 60s python -m experiments.fixed_rule.flag_cuda_stream_compare --input figs/fixed_rule/flag_stream_execution_v1 --output figs/fixed_rule/flag_cuda_stream_compare_v1
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m unittest tests.fixed_rule.test_flag_cuda_fixed -v
```

The CPU short-period probe used `python -m experiments.fixed_rule.flag_cpu_period_probe --input figs/fixed_rule/flag_cuda_stationary_probe_v1 --output figs/fixed_rule/flag_cpu_period_probe_v1` with one BLAS/OMP thread.
