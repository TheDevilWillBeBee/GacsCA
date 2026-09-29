# Exact general-Signal flags integrated with resident computation

2026-09-26. The executor now supports arbitrary coherent left/right Signal bits
in its canonical, mail-free suffix. It retains exact Flag1/Flag2 transients on
GPU instead of imposing the former left-zero profile. Two successive physical
work periods with both computed Signals equal to one pass all raw evaluation,
metadata regeneration and decoded commit checks. The physical rule, ROM,
154-word raw/105-word projected alphabet and radius seven remain unchanged.

## Source and mathematical scope

This is still the explicit candidate-B construction, with healthy Flag2 erasure
when at most one in-colony left Flag2 is one. It is not a claim that Gray's printed
formula says this. The printed persistence counterexample and old-Signal D10
choice remain documented in REPAIR_B.md and the shared fidelity audits. Gray's
correction argument motivates studying the flag dynamics; it does not authorize
silently changing them or establish a general amplification theorem here.

On canonical geometry, both directional votes recover the same Address and Age,
regardless of flags. The physical inconsistency term and D3 are false. Wf1/Wf2
are derived from the current forcing window, coherent boundary Signals, and
current Flag1. Thus two primary flag bits per physical site suffice for an exact
projection; all five backup Wf fields are reconstructed from their actual logical
positions and computed Flag1 values. No front shape or propagation speed is
assumed in execution.

The recurrence retains in-colony masks, the computed new Flag1 in Flag2's
birth/erasure terms, old Wf forcing, and cross-colony left Flag2 reads. In
particular, Flag2 cannot generally be advanced independently per colony. The
saved experiment contains a witness: changing the preceding colony's left
Signal changes the current colony's Flag2 despite its own Signals being fixed.

## Symbolic certificate

`prove_small_holder_general_flags.py` selects geometry, primary flags, Signal
and every backup Wf output from the complete physical descriptor. It compares
those outputs to the canonical recurrence using 51 independent Boolean inputs:
15 Address bits, 30 arbitrary neighboring Flag1/Flag2 bits, and six neighboring
left/right Signal bits. Input primary Wf is coherently derived; arbitrary raw
Wf faults are outside this certificate.

Four clock regimes cover entry, forcing, cutoff and erasure. On canonical
geometry, the flag recurrence has no other Age dependence in this suffix;
clock increments are compared explicitly. All Address/flag/Signal assignments
pass. The largest BDD has 63030 nodes. This proves the selected full-rule
recurrence, not a theorem about arbitrary geometry or arbitrary computation
histories. Bit-packed CUDA implementation equivalence has separate local tests.

## GPU implementation and controller integration

New `small_holder_flags_gpu.{py,cu}` packs 64 physical Flag1 bits and 64 Flag2 bits
per word pair. Neighbor shifts and Boolean threshold expressions evaluate every
physical output bit from its old radius-five flag neighborhood. Double buffering
preserves synchrony. CUDA graphs repeat 128 literal ticks; execution splits at
forcing-clock boundaries. Odd remainders copy buffers without changing captured
pointers. Every transient tick is executed; there is no unverified wave shortcut.

Explicit flag buffers use `32 * colonies * (Q/64) + 2 * colonies` bytes. Graphs,
CUDA runtime/context overhead are additional. The initial experimental API caps
allocations at 128 colonies; this is a resource guard, not a physical state field
or hierarchy-depth branch. It will need scaling for a whole-Q parent ring.

`small_holder_resident_general.py` composes this flag engine with the existing
resident computation. A private generated build removes the old left-zero/
uniform-right accelerator guard, while retaining canonical geometry, coherent
Signal shape, mail exclusion and controller-event guards. Frozen backends are
untouched. The physical descriptor and program are unchanged.

The factorization is justified directly by the full rule: corrected procedure
operands and virtual controller neighborhoods do not depend on flags; canonical
geometry makes computed Address unchanged, disabling geometry-repair clearing;
and old/new mail is zero in the admitted suffix, making flag-based mail erasure
irrelevant. Conversely, flags do not read controller/Data fields in this suffix.
The previously verified full physical controller path and exact flag projection
can therefore advance independently to the same physical time. Tests also compare
complete local transitions with arbitrary flags and live computation.

At the suffix entry, the wrapper copies the already computed boundary Signal bits
from the resident state into flag storage and starts from its known zero flags.
This is representation transfer, not a simulated transition or an upper-rule
callback. Those Signals remain stationary over the forcing/clearing interval.
Diagnostics reconstruct actual flags/Wf from GPU state. The public wrapper is
intentionally not a `period.World`: the older physical-exception backend assumes
the restricted implicit flag profile and must reject this new representation.
Combining those two backends remains work; silently dropping Flag2 is prevented.

After forcing ends, Flag1 clears from the right by at least two cells per tick:
the next two positions outside a zero suffix have too few right ones to be born
or retained. Once Flag1 is zero, Flag2 clears from the left by at least two cells
per tick, with cross-colony birth disabled. Hence all flags are zero within Q/2
plus Q/2 ticks. The wrapper executes all 3Q+1 entry/forcing/clearing ticks,
asserts the final GPU state is zero, then drops the now-redundant flag buffers.
No state is replaced with zero merely because the bound predicts it.

## Verification and measured costs

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.prove_small_holder_general_flags --output figs/fixed_rule/small_holder_general_flags_proof_v1.json
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_general_flag_trajectories --output figs/fixed_rule/small_holder_general_flag_trajectories_v1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_general_two_periods --output figs/fixed_rule/small_holder_general_two_periods_v1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_general_flags --macrosteps figs/fixed_rule/small_holder_general_two_periods_v1 --trajectories figs/fixed_rule/small_holder_general_flag_trajectories_v1 --proof figs/fixed_rule/small_holder_general_flags_proof_v1.json --output figs/fixed_rule/small_holder_general_flags_audit_v1.json
```

All exited zero. Tests used Python unittest discovery/TextTestRunner with
`OPENBLAS_NUM_THREADS=1` and these exact patterns:

| Pattern | Result | Test time | Host RSS |
|---|---|---:|---:|
| `test_small_holder_flags_gpu.py` | 4 passed | 1.820 s | 168176 KiB |
| `test_small_holder_resident_general.py` | 2 passed | 6.556 s including private build | 168832 KiB |

The packed tests compare arbitrary flag words at colony/word boundaries with the
complete radius-seven native physical rule, including all backup Wf and geometry
outputs. They compare CUDA graph batches with repeated literal steps across
clock boundaries, check repeated odd-length calls, test mail-free procedure
independence from flags, and reject invalid initial data/durations. Integrated
tests compare full physical steps with both Signals and active controllers,
carry flags across short calls, preserve the old right-only reference, and reject
the incompatible old exception wrapper.

The symbolic certificate passed in 1.836706 s. Complete forcing/clearing runs
covered all 16 two-colony Signal patterns, 98305 physical ticks each, plus
32768 ticks from arbitrary random flags on three colonies. GPU advance took
2.774712 s, total 3.569017 s, host RSS 146568 KiB, with at most 49158 bytes of
explicit flag buffers. Every case met the clearing bound; left-one cases had
nonzero Flag2 transients.

The integrated run executes two successive one-link macrosteps on 491520 sites,
8589934592 physical ticks, without reinitializing between periods. At each forcing
cutoff all 491520 sites have Flag1=Flag2=1. They subsequently clear through actual
local flag evolution before the final evaluation. Every raw pre-regeneration
output, regenerated Hold and decoded commit matches the intended complete rule.
Upper Address 30000 repairs to 107; cleared controller Data recovers on the second
step. This extends the prior explicit closure fixture to nonzero computed Flag2.

GPU advance took 37.980548 s, of which literal flag evolution took 0.367051 s for
196610 ticks. Total was 39.505978 s; host RSS 176352 KiB. Resident buffers are
5116680 bytes; during flags, 245790 flag-buffer bytes and existing controller
staging are additional. No GPU process peak was sampled during this short run.

Independent audit passed in 0.856253 s, 64444 KiB RSS. It checks complete saved
upper transitions using scalar/native/descriptor evaluation; compares all saved
Flag1 frames with the independently certified old front formula; checks observed
clearing, the cross-colony Flag2 witness, proof provenance, and source/binary/
artifact hashes. Flag2's full trajectory is supported by runtime checks, local
full-rule tests and the symbolic recurrence; the audit does not reconstruct the
entire trajectory from scratch.

Full descriptor SHA256 remains
`af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`.
Two-period artifact SHA256:
`c903913c1cd17ef81d0ebdd67589dae6b2073df542a1c0402b9f4b71f32b5948`.
Flag-trajectory artifact SHA256:
`95e4f5dd4aeaadefc40968f6a797b71dbde473a28039f39241497910a025103b`.
Manifests record exact binary/source hashes. All handles exited; final GPU query
was empty. Main-agent notes/reservation reply remain absent; no large allocation
or shared/frozen source change was made.

## Remaining goal

The left-zero restriction is removed for the admitted canonical, coherent,
mail-free suffix. The new engine does not repair arbitrary geometry, represent
noncoherent physical faults alongside general flags, or prove a noisy one-link
boundary relation. Those are separate integration/proof obligations.

Full nested upper work periods, robust finite-depth termination and stochastic
amplification remain unverified. The 8 GiB whole-Q allocation/reset pilot remains
pending scheduling coordination; even that pilot would not execute a top
macrostep. The practical-time problem U²=2^64 remains. Next work should integrate
general flags with physical exceptions and reduce or certify compression of the
actual evaluator's nested trajectory costs. The goal remains active, with Q and
U optimized for correctness/practicality rather than a fixed ratio of 128.
