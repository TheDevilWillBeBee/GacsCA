# Retained complete depth-two endpoints on GPU

2026-09-27. Two successive noiseless depth-two endpoint steps now execute with
one fixed tiled GPU endpoint operator. The full initial bottom Info array and
both complete bottom Data banks are retained. Every intermediate decoded raw
field and every top raw field matches; an independent CPU audit passes. The
full experiment, including storage and hashing, took 52.659860 seconds, with
53042568 explicit GPU bytes and 2741968 KiB peak sampled host RSS.

This uses the exact endpoint composition proved in
[TERMINAL_STATE_IDENTITY.md](TERMINAL_STATE_IDENTITY.md), not literal replay of
U^2 local ticks. It supplies the previously missing practical depth-two endpoint
execution. It does not supply arbitrary intermediate-time evolution, noisy
interval acceleration, general correction/amplification, or a robust finite cap.
The overall goal remains active.

## What was executed

Q=32768 and U=2^31 remain unchanged. The experiment has one periodic top cell,
32768 middle physical cells and **1073741824 bottom physical cells**. The top
is an arbitrary typed state with every raw controller field initialized. The
middle ring has distinct positions throughout each radius-seven neighborhood;
the top ring itself aliases its neighbors. This is not a 15-top-cell experiment.

Let E_loc be the canonical entry relation with complete encoded state, arbitrary
MEM scratch and localized coherent Signals. C(y) is the complete endpoint at
U-1; B(y)=G(C(y)) is the complete endpoint at U. The proved identities give

    G^(U^2)(E_loc(E_loc(y))) = {B(C(y))}.

The GPU computes C(y), reconstructs its complete physical cells on-device, and
feeds those cells through the **same** endpoint evaluator to obtain B(C(y)).
A second call of the first-stage evaluator also supplies B(y) for the complete
intermediate-field check G(C(y))=B(y). No CPU transition computes or installs the
next represented state. Every next top input is decoded on GPU from the actual
Info words of the completed bottom result. The restored nested entry relation
justifies the next endpoint despite retained scratch; no physical cleanup or
fresh initialization is inserted into the evolving state.

The two represented physical times are 4611686018427387904 and
9223372036854775808. These are exact endpoint times under the proved shortcut,
not counts of literal GPU tick calls. The top changes 77 raw words at the first
step and one at the second. This random top fixture is broad typed-state
coverage; it does not itself establish sustained healthy top-controller activity.
A non-vacuous active-controller correction fixture is prepared separately below.

## Fixed kernel, full state and encoded depth

New `retimed_holder_endpoint_tiles.py/.cu` uses the complete fixed final
instruction stream already validated in [GPU_ENDPOINT_OPERATOR.md](GPU_ENDPOINT_OPERATOR.md).
The evaluator body is mechanically taken from that implementation with only
its input indexing changed to a tile plus seven-cell halos. The generated
header, 154-field schema, 10733 instructions, ROM, U/Q and full-descriptor hashes
are independent of colony count and hierarchy depth.

There is one evaluator kernel. A fixed device accessor reads either raw cells
or a compressed canonical image. These are storage representations, not level
identifiers or different physical rules. The accessor reconstructs all metadata,
all five adjacent procedure Data copies, geometry and all distributed Signal
bits; canonical image controllers/mail/flags/Wf are zero by the endpoint proof.
Their encoded counterparts remain unrestricted complete raw data in Info,
histories, Hold and scratch. Raw-source width/metadata checks run before each
tile. Incomplete decoded streams, missing tiles and partial-image freezing reject.
The same kernel has been tested with raw and image inputs, aliasing and distinct
neighbors, precommit/commit states, and successive actual output data.

Initial depth is actual configuration data. The GPU constructs E_loc(y) and
serializes every complete raw cell of it into the bottom Info array. Together
with zero remaining lower scratch and controller/mail/flag/Signal fields and
canonical geometry/coherent replicas, this specifies E_loc(E_loc(y)). The file
contains 32768*154=5046272 words; no raw controller field is omitted. GPU decoding
of this actual initial encoded image supplies the first top input. The CPU
independent audit reconstructs and compares this entire array, not just its top
decode. Finite depth has a periodic top evolving by G, with no special top kernel;
this is not a proof of a noise-stable cap.

The physical alphabet remains projected G's 105 words/2704 bits (154 lifted
words/4090 bits); radius seven and the hard-wired ROM are unchanged. More depth
adds encoded sites and storage, not physical hardware fields. The software
backend's image handles and staging buffers are not new physical registers.
The fixed operator has no depth argument or maximum-depth transition case.
Higher-depth materialization still faces severe resource growth; depth three is
not claimed here.

## Retained state and independent validation

Every bottom endpoint bank has 32768 rows and 9916 words per row:
324927488 words /2599419904 payload bytes. The bank retains every MEM and tail
Data word, including actual history/vote/result/query scratch. The small artifact
retains all localized Signal bits; canonical endpoint geometry, zero live
controllers/mail/flags/Wf and coherent replicas reconstruct the complete physical
state. This compressed representation is restricted to its proved domain; it is
not a general physical-state serializer that silently omits live controllers.

Per period, the device collects the actual raw Info from every output tile,
then decodes the full collected middle state to the next top. No next-top oracle
is installed. The driver compares every one of the 5046272 middle raw words with
B(y), including encoded controller fields and geometry, then compares all 154
top fields against the independent scalar G. Host scalar/descriptor/formula and
physical-image reconstruction functions are patched to fail during GPU execution.

The independent CPU audit verifies:

- Source, binary and artifact hashes, including both full retained banks.
- All 5046272 initial raw Info words against a separately vectorized initial image.
- Every middle raw word and all 154 top fields at both endpoints, reading the
  actual bottom banks. Both upper C/B banks also match the independent DAG formula.
- Complete bank integrity by 256 tile hashes per period.
- Fourteen full 9916-word scratch rows per period, independently recomputed from
  their complete fifteen-cell middle neighborhoods. Samples cover Info/Hold,
  memory/core boundaries, tail buffers and periodic wrap.

This independently recomputes 277648 complete scratch words across 28 rows;
it does not independently recompute all 649854976 saved bank words. Kernel and
representation correctness also rely on the fixed-stream/indexing argument and
focused tests. Neither this audit nor the earlier proof is a universal CUDA
backend equivalence proof or a proof-assistant development.

## Measurements and reproducibility

| Quantity | Result |
|---|---:|
| GPU operator/transfer/decode call time, both periods | 7.570928 s |
| First period including host storage/checking | 18.226222 s |
| Second period including host storage/checking | 19.176212 s |
| Entire experiment including hashing | 52.659860 s |
| Explicit GPU peak | 53042568 bytes (about 50.59 MiB) |
| Reported /sampled peak host RSS | 2732488 /2741968 KiB |
| Independent CPU audit | 14.891052 s; 2693372 KiB reported RSS |
| Six tiled GPU tests | 3.926 s; pass |
| CUDA memcheck of those tests | Zero errors; 225372 KiB aggregate RSS |
| Two independent image-array tests | 1.987 s; pass |

The complete run used a 60-second watchdog and an 8 GiB sampled host-RSS
threshold; the audit used 90 seconds/4 GiB. All are below the user's 40 GB RAM ceiling. The GPU working set stayed
under 64 MiB; no substantial GPU reservation was consumed. The GPU was idle
before launch, and no other job, old CUDA artifact or shared source changed.
All owned jobs are now terminal.

Preserved failed diagnostic: the first vector-image test attempted NumPy uint64
addition with a negative Python offset and raised OverflowError. The source/log
are retained. Grouping Q+offset before adding it to the unsigned array fixes the
index expression; both tests then pass. No GPU implementation or recorded
trajectory was changed in response.

Artifacts under `figs/fixed_rule/retimed_holder_streamed_depth2_v1`:

- `.json/.log`: execution receipt and exact results.
- `_initial_info.npy`: complete raw initial bottom Info.
- `_period1_bank.npy`, `_period2_bank.npy`: full endpoint banks.
- `_small.npz`: actual decoded top states, upper C/B banks, complete lower Signals,
  sample banks and all tile hashes.

Commands from the repo root, with OPENBLAS_NUM_THREADS=1 and fresh output names:

```
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_endpoint_tiles_tests_watch_v1.json --seconds 60 --rss-mib 512 -- python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_endpoint_tiles.py -v
python -m experiments.fixed_rule.bounded_cuda_process_tree --output figs/fixed_rule/retimed_holder_endpoint_tiles_memcheck_watch_v1.json --seconds 60 --rss-mib 1024 -- /usr/local/cuda/bin/compute-sanitizer --tool memcheck --error-exitcode 99 python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_endpoint_tiles.py -v
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_streamed_depth2_watch_v1.json --seconds 60 --rss-mib 8192 -- python -m experiments.fixed_rule.run_retimed_holder_streamed_depth2 --output figs/fixed_rule/retimed_holder_streamed_depth2_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_streamed_depth2_audit_watch_v1.json --seconds 90 --rss-mib 4096 -- python -m experiments.fixed_rule.audit_retimed_holder_streamed_depth2 --reference figs/fixed_rule/retimed_holder_streamed_depth2_v1.json --output figs/fixed_rule/retimed_holder_streamed_depth2_audit_v1.json
# The following CPU tests used ulimit -v 524288:
python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_endpoint_image_array.py -v
python -m experiments.fixed_rule.prepare_retimed_holder_depth2_repair --output figs/fixed_rule/retimed_holder_depth2_repair_fixture_v1.json
```

The private tiled binary is
`figs/fixed_rule/build/retimed_holder_endpoint_tiles_c2ff88d01ee4376e69a1/tiles.so`.
The owned evidence index is `retimed_holder_streamed_depth2_evidence_v1.json`.
Previous successful files and evidence remain frozen.

## Next correction experiment, prepared but not executed

`prepare_retimed_holder_depth2_repair.py` gives a non-vacuous active controller:
Address 100, Age RESET_AGES[4]+100, five head copies, READ_B, rb=99, NAND and
explicit nonzero operands. Flipping two rb copies from 99 to 98 leaves the entire
next raw state equal to healthy, including READ_B->WRITE and the NAND result.
Flipping three changes the transition; the central phase stays READ_B.

The exact E_loc(E_loc(healthy))->E_loc(E_loc(damaged)) initial physical fault
sets are constructed, not inferred from a label. Two wrong top copies correspond
to 10 changed middle raw Data words and **50 bottom bit flips**; three correspond
to 15 and **75 flips**. Every affected full physical cell, after applying the
listed XORs, equals direct depth-two initialization of the damaged top. The
preparation passes in 1.714780 seconds /147216 KiB RSS and saves all raw states
and physical fault positions/fields.

These are deliberately correlated initial errors at encoded controller locations,
not independent random noise or arbitrary in-period defects. No faulty depth-two
GPU trajectory has yet run. Next: apply these exact faults to the retained initial
encoded state, decode that state on GPU, execute paired full endpoints, retain
all scratch differences and check a later complete rejoin. Run the three-copy
control through the same path. General noise thresholds and fault-time evolution
still require additional machinery; the noiseless shortcut must never silently
skip faults outside its domain.

Gray pp. 31–32's specialized hard-wiring and Gacs sections 9.2–9.3 remain the
source basis. Candidate-B Flag2, voted-old-Signal D10, printed Flag2 persistence
and SimBit ambiguity are unchanged. No U<=128Q constraint was reinstated. General
source-faithful correction/amplification, malformed Info repair, robust finite
termination, depth-three execution and wider top configurations remain open.
