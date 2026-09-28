# GPU complete-state endpoint operator

2026-09-27. The complete terminal identity now has a GPU implementation. It
matches all four precommit/commit endpoints of the fresh two-period physical
trace, including every scratch/controller/Signal/flag field. It also retains the
120 different terminal scratch words of the equal-decoded-output repair witness.
The fixed physical rule, ROM, alphabet and prior execution backends are unchanged.

This is acceleration on the proved noiseless canonical entry domain, not an
alternative physical transition. It uses C and B from
[TERMINAL_STATE_IDENTITY.md](TERMINAL_STATE_IDENTITY.md): C advances U-1 ticks
from E_loc; B additionally performs the actual adjacent-Hold commit. Complete
depth-two composition remains unimplemented. General noisy intervals cannot be
advanced with this operator.

## Implementation and contract

`gacsca/fixed_rule/retimed_holder_endpoint_gpu.py` and `.cu` are new owned files.
Their private build embeds the exact final 10733-instruction stream and all Q
metadata records from the single existing ROM. Header generation replays the
finite layout certificate, checks every instruction's memory addresses, and
requires the frozen full-descriptor and ROM hashes. No user program, depth
argument, depth-specific instruction set or physical register is introduced.

A canonical state is stored as all 9916 Data words per colony plus the two
localized Signal bits. Its fixed reconstruction includes all procedure replicas,
canonical Address/Age, zero controller/mail/flags/Wf, and normalized metadata.
This representation is valid only at the entry and endpoint times in the proof.
It is not a claim that arbitrary physical controller states can be omitted.
Those states are retained, in full, as the raw encoded Info/history/Hold data.

Before an endpoint operation, the device extracts all 154 Info words per colony,
checks every narrow field width, and checks all 49 metadata words against the
actual encoded Address and the one ROM. Invalid input returns without changing
any current bank, Signal or clock. A separate output bank is then filled with
complete neighbor histories, votes and unchanged old Info. One GPU thread per
colony executes the fixed final stream, retaining every result scratch write,
LOAD/META query and Hold output. Output widths and query bounds are checked.
Only after all colonies pass does the backend install the complete precommit
bank and captured Signals. Commit copies each old adjacent Hold into Info.
The two bank buffers are software staging storage, not additional physical
state fields or a hierarchy-dependent pair of registers.

The same compiled binary handles all colony counts. All evolving transition
calculations occur on GPU. Python schedules calls, maintains the common clock,
and performs initialization/readback/diagnostic checks. During validation,
host scalar rules, descriptor evaluation and both terminal formulas are patched
to fail if called while the GPU operator advances. No diagnostic answer is
installed into the world. Successive periods use the preceding actual bank.

`World.from_snapshot` checks the full canonical entry shape before importing a
resident snapshot; nonzero live controller/mail/flags/Wf or missing Signal
replicas reject. The basic bank/Signal constructor defines that canonical
physical representation directly. Malformed encoded Info can be represented as
input but is rejected atomically before advancement. No reset or repair of
invalid Info is silently substituted. Device allocation has an explicit budget;
readback also has a budget. These software limits do not constrain the physical
alphabet or define a maximum hierarchy depth.

The kernel's represented input dependence is exactly offsets -7..7. This is an
endpoint dependency test in colony units. It does not replace the existing
radius-seven physical local-rule proofs or assert that U-1 physical ticks are
one physical tick. The endpoint shortcut is justified by the separate complete
state induction, not by the opcode loop alone.

## Evidence

The validation initializes the GPU bank from the exact saved random-scratch
initial state in `retimed_holder_cuda_terminal_v2.npz`, then retains one state
through two periods. At each precommit/commit checkpoint, its complete bank,
Signal replicas, controller/mail/Wf state, flags and clocks match the actual
physical trajectory. Each bank has 148740 words; its canonical coherent
reconstruction covers 491520 physical cells. Comparison permits harmless
internal sparse-record ordering while checking every actual physical field.

The healthy and damaged witness cases are separate noiseless executions from
their respective typed encoded upper states. Both complete terminal banks match
the earlier physical repair experiment, including 120 differing scratch words
with identical Info. This does not mean the new operator can evolve faults:
the prior repair proof explains why those particular fault histories have these
endpoints. No in-period fault handler or stochastic correction is implemented.

| Check | Result | Seconds | Host peak KiB |
|---|---|---:|---:|
| Four endpoint calls, retained two periods | All fields match physical trace | 0.017185 total | Included below |
| Healthy witness period call | All terminal bank words match | 0.006056 | Included below |
| Damaged witness period call | All terminal bank words match | 0.006093 | Included below |
| Complete validation experiment | Six cases pass | 3.221947 | 185604 reported /188156 sampled |
| Independent artifact audit | Four complete endpoints and both witness banks | 0.549088 | 53000 |
| GPU contract tests | Six pass | 2.929 | 173468 sampled |
| Width/locality tests | Two pass | 2.956 | 173236 sampled |
| CUDA memcheck of the six contract tests | Zero errors | 3.965239 watchdog time | 216488 family aggregate |

The endpoint calls include Python guard/context overhead and synchronous device
validation, but exclude allocation, readback and diagnostic comparison. The
physical trajectory backend's 43.350940-second result covers the same retained
two periods; it is a comparison on this fixture, not a depth-two timing result.
The new operator's explicit device allocation for 15 colonies is **4577324 bytes**.
No large GPU allocation or reservation was used. Ordinary runtime probes retained
a 60-second/512 MiB sampled-RSS watchdog; memcheck used 60 seconds/1 GiB family
RSS, within the new 40 GB user allowance. The private build used a 4 GiB virtual
memory cap; runtime CUDA probes did not use a virtual-memory cap.

Tests cover random complete typed states, successive periods, one-colony aliasing,
all-max field values, phase/readback/budget guards, complete snapshot import, and
rejection of live physical controllers, flags or incomplete Signal copies. Each
of the **110 raw fields narrower than 64 bits** is individually made overwide:
all reject with unchanged state/time. A stale metadata word also rejects.
A change at represented offset 15 leaves colony zero's entire endpoint unchanged;
a change at wrapped offset -1 changes its bank. Complete output data from the
modified distant colony does change, preventing a vacuous constant-output pass.
Two different colony counts share the same library binary.

Exact reproducible commands, from the repo root, with fresh output names:

```
ulimit -v 4194304
OPENBLAS_NUM_THREADS=1 python -c 'from gacsca.fixed_rule import retimed_holder_endpoint_gpu as m; print(m.library()._name)'
# Use a separate shell without the VM limit for the CUDA runtime:
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_endpoint_tests_watch_v1.json --seconds 60 --rss-mib 512 -- python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_endpoint_gpu.py -v
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_endpoint_validation_watch_v1.json --seconds 60 --rss-mib 512 -- python -m experiments.fixed_rule.validate_retimed_holder_endpoint_gpu --output figs/fixed_rule/retimed_holder_endpoint_validation_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_endpoint_locality_watch_v1.json --seconds 60 --rss-mib 512 -- python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_endpoint_locality.py -v
python -m experiments.fixed_rule.bounded_cuda_process_tree --output figs/fixed_rule/retimed_holder_endpoint_memcheck_watch_v1.json --seconds 60 --rss-mib 1024 -- /usr/local/cuda/bin/compute-sanitizer --tool memcheck --error-exitcode 99 python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_endpoint_gpu.py -v
# CPU artifact audit used ulimit -v 524288 and OPENBLAS_NUM_THREADS=1:
python -m experiments.fixed_rule.audit_retimed_holder_endpoint_gpu --reference figs/fixed_rule/retimed_holder_endpoint_validation_v1.json --output figs/fixed_rule/retimed_holder_endpoint_audit_v1.json
```

Private binary: `figs/fixed_rule/build/retimed_holder_endpoint_6e3be7d1ed27ff8d6ce0/endpoint.so`.
Manifest: `figs/fixed_rule/retimed_holder_endpoint_evidence_v1.json`.
All current jobs are terminal. All additions are in owned namespaces. No shared
source, old CUDA artifact, physical rule, historical dataset or other agent's
status file changed. MAIN_AGENT_NOTES.md remains the reply channel.

## Next concrete depth-two work

The proved endpoint at depth two is B(C(y)), retaining complete physical state.
The next backend must reconstruct C(y)'s full raw physical cells **on GPU**,
including adjacent procedure copies and metadata, and feed those cells to the
same fixed endpoint operator. It must compare reconstruction with literal local
commit and existing physical states, and decode the resulting complete banks
across both levels. Successive top periods must use encoded data extracted from
the actual retained result, with no host replacement of a represented step.

A streaming implementation can keep the GPU working set small: generate a tile
plus seven-neighbor halos from the device image, evaluate the fixed operator,
and store all output bank words. One top cell's complete depth-two terminal bank
is 2599419904 bytes. Keeping two such banks requires about 5.20 GB, within the
40 GB host allowance. These are proposed storage costs; the streaming operator,
full depth-two execution and its measured time are not yet implemented. The
prior substantial 8 GiB GPU reservation remains pending/unused; substantial
GPU scheduling stays coordinated with the main agent.

The goal remains active. Correct full depth-two dynamics, general correction
across levels, malformed Info repair and reliable finite caps remain incomplete.
Candidate-B Flag2 and the source-fidelity qualifications remain unchanged. A
noiseless endpoint accelerator does not by itself establish noise robustness.
