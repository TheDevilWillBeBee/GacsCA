# Executed depth-two encoded-controller correction

2026-09-27. Exact correlated initial physical faults have now been run through
the complete depth-two GPU endpoint pipeline. Fifty bottom bit flips become
two wrong top controller replicas; the actual top transition repairs them and
performs the intended NAND read. The independently evolved healthy/damaged
states still differ in 39740 stored Data words after that top step. They match
in every retained bank word and Signal at the second endpoint. A 75-bit,
three-copy control changes the actual top transition as intended.

This is a targeted correction experiment across two simulation links, using the
fixed G and the proved endpoint shortcut. It is not independent random noise,
arbitrary fault-time execution, a uniform recovery bound, or a robustness
threshold. The full project goal remains active.

## Actual faults and initial state

The fixture in `prepare_retimed_holder_depth2_repair.py` uses an active top
controller at Address 100 and Age RESET_AGES[4]+100, with READ_B, rb=99, rd=107,
NAND, Data=0x13579bdf and Value=0x123456789abcdef0. Two rb replicas are changed
from 99 to 98; the three-copy control changes one more. The complete scalar
reference distinguishes READ_B->WRITE with the NAND result from the negative
control's central READ_B outcome. This is not a controller-clearing example.

All three GPU cases begin with the same unperturbed nested physical encoding.
The 50/75 listed **bottom physical bit flips** are applied before device decoding.
One encoded top bit occupies five middle procedure Data copies, each encoded
again into five bottom copies: 25 physical bits per altered top replica. The
faults therefore change 10/15 complete middle raw words. Their exact physical
positions, raw field indices and XORs are saved; all indices designate mutable
Data fields, not hard-wired metadata.

`retimed_holder_initial_info_faults.apply` groups the actual physical changes by
their logical Info word. It verifies that all five replicas were explicitly
flipped consistently before changing any initial Data. Incomplete, inconsistent,
duplicate, non-Data or outside-Info patterns reject. This restriction is essential:
the helper is an initializer/representation check, not a recovery procedure. It
never repairs a partial group, drops an error or installs a desired decoded state.
The pattern happens to leave the canonical bottom encoding coherent.

The resulting complete initial Info is uploaded to GPU, and GPU decoding supplies
the actual next input. The entire middle initial state is checked against its
nested entry relation, including every raw controller field. The diagnostic
expected damaged top is compared with the device decode; it is not installed.
Thus the existing C/B endpoint identity applies to each resulting nested initial
state. All subsequent intervals are noiseless. No fault outside the shortcut's
proved domain is skipped.

"Healthy" here denotes the unperturbed comparison state. The periodic top has
one cell and aliases its neighbors; it is not a canonical full Q-cell top colony
or a noise-stable cap. The bottom and middle initial encodings satisfy the checked
canonical entry relation. The experiment tests actual controller protection in G
without asserting healthy top-colony geometry.

## Same dynamics in all cases

No physical rule, ROM, alphabet, CUDA implementation or old evidence was changed.
Every case uses the same frozen tiled binary and all raw state fields. The only
case-dependent input is the initial physical fault list. The two-step cases retain
one evolving result; the next top input is decoded on GPU from its actual Info.
No healthy state is copied into the damaged trajectory. During evolution, host
scalar/descriptor/formula/image-reconstruction calls are patched to fail.

As in [STREAMED_DEPTH_TWO.md](STREAMED_DEPTH_TWO.md), Q=32768, U=2^31, radius seven,
105 mutable words/2704 bits, and 154 lifted words/4090 bits are fixed. Each endpoint
retains all 324927488 Data-bank words for 1073741824 bottom physical cells. The
canonical endpoint representation additionally determines geometry, zero live
controller/mail/flags/Wf, all procedure replicas, metadata and the explicitly
retained Signals. This is complete physical state on that domain, not a general
serializer for arbitrary active/faulty configurations.

## Results

| Initial case | Bottom bit flips | Top result after one step | Full trajectories |
|---|---:|---|---|
| Unperturbed reference | 0 | READ_B->WRITE; correct NAND | Two endpoints |
| Two bad rb copies | 50 | Entire raw top output equals reference | Two endpoints |
| Three bad rb copies | 75 | Central phase remains READ_B; nine raw top fields differ | One endpoint |

After the first corrected top step, equal top outputs do **not** imply physical
recovery. The complete paired bank comparison finds:

| Stored category | Different words after first endpoint | After second |
|---|---:|---:|
| Histories | 27450 | 0 |
| Votes | 9150 | 0 |
| Info | 600 | 0 |
| Hold | 600 | 0 |
| Other scratch | 1940 | 0 |
| **Total** | **39740** | **0** |

The 600 Info differences encode residual middle-layer scratch, despite the
matching top decode. At the second endpoint all Data words and all physical
Signals match; the known canonical reconstruction then establishes complete
physical rejoin. This is observed **by** represented time 2*U^2=9223372036854775808,
not a claim that this is the earliest rejoin time. No ongoing faults are injected.

## Independent evidence

The CPU audit checks all five saved banks, every decoded intermediate raw word,
and all top raw fields, against the independent scalar/DAG construction. It
re-derives the physical fault lists from the observed initial-array differences
and compares them with the exact 50/75-bit fixture. This inverse check does not
call the fault applicator. It checks full file/tile integrity and independently
recomputes 70 complete scratch rows at layout interfaces.

A second audit specifically selects eight colonies from actual healthy/damaged
differences, rather than fixed interface samples. There are 27 differing tiles.
Selected colonies are 225, 913, 2687, 3921, 4609, 6385, 7617 and 9354. All 9916
scratch words are independently recomputed for both cases at each selected colony:
16 additional full rows pass. This validates examples with real residual state,
not merely rows unaffected by the controller errors.

The audit checks every stored word for paired rejoin, but does not independently
recompute every scratch word of every trajectory. Correctness also relies on the
fixed instruction stream, local image/indexing argument and previous tests.
There is no proof-assistant result or universal CUDA parity theorem here.

| Run/check | Wall time | GPU call time | Reported host peak KiB |
|---|---:|---:|---:|
| Healthy, two endpoints | 50.311789 s | 7.547577 s | 2744880 |
| Two-copy faults, two endpoints | 52.548445 s | 7.771113 s | 2743588 |
| Three-copy control, one endpoint | 27.350120 s | 3.844533 s | 2745060 |
| Full independent audit/rejoin comparison | 35.259436 s | None | 5149520 |
| Changed-row audit | 4.802760 s | None | 266536 |

Each GPU case used 53042568 explicit device bytes (about 50.59 MiB). Runtime
watchdogs allowed 8 GiB sampled host RSS: 90 seconds for two-endpoint cases,
60 seconds for the control. The CPU full audit used 120 seconds/8 GiB; its peak
was about 4.91 GiB, below the user's 40 GB ceiling. These limits bound owned
processes only. All jobs are terminal, and no other job or shared CUDA artifact
was touched. The substantial GPU reservation remains unused.

Four initial-fault tests pass in 2.104 seconds; four audit-distinction tests pass
in 0.298 seconds. They reject partial/inconsistent replica groups without mutation,
geometry/outside-Info faults, multi-bit differences in the single-bit audit, and
attempts to ignore history, encoded controller, query or tail state. No new CUDA
code was built; the previously memory-checked tiled binary is unchanged.

## Reproduce and locate evidence

New owned sources are `retimed_holder_initial_info_faults.py`, the streamed repair
driver, two auditors and two test files. Frozen prior sources are reused. Each
case prefix `figs/fixed_rule/retimed_holder_streamed_repair_{healthy,two,three}_v1`
contains a receipt/log, complete initial Info, one/two full `.npy` banks and a small
archive with actual decoded states, exact faults, Signals and tile/sample data.
The five complete bank payloads total 12997099520 bytes. Source and artifact
hashes are recorded in `retimed_holder_streamed_repair_evidence_v1.json`.

Commands from the repo root, with OPENBLAS_NUM_THREADS=1 and fresh output names:

```
# CPU unit tests used ulimit -v 524288:
python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_initial_info_faults.py -v
python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_streamed_repair_audit.py -v
# CUDA/runtime and mapped-file audits must not inherit that VM limit:
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_streamed_repair_healthy_watch_v1.json --seconds 90 --rss-mib 8192 -- python -m experiments.fixed_rule.run_retimed_holder_streamed_repair --case healthy --periods 2 --output figs/fixed_rule/retimed_holder_streamed_repair_healthy_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_streamed_repair_two_watch_v1.json --seconds 90 --rss-mib 8192 -- python -m experiments.fixed_rule.run_retimed_holder_streamed_repair --case two --periods 2 --output figs/fixed_rule/retimed_holder_streamed_repair_two_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_streamed_repair_three_watch_v1.json --seconds 60 --rss-mib 8192 -- python -m experiments.fixed_rule.run_retimed_holder_streamed_repair --case three --periods 1 --output figs/fixed_rule/retimed_holder_streamed_repair_three_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_streamed_repair_audit_watch_v1.json --seconds 120 --rss-mib 8192 -- python -m experiments.fixed_rule.audit_retimed_holder_streamed_repair --output figs/fixed_rule/retimed_holder_streamed_repair_audit_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_repair_changed_rows_watch_v1.json --seconds 60 --rss-mib 1024 -- python -m experiments.fixed_rule.audit_retimed_holder_repair_changed_rows --output figs/fixed_rule/retimed_holder_repair_changed_rows_v1.json
```

## Remaining work

Move beyond correlated errors that preserve the nested entry domain. A concrete
next step is a checkpoint of the middle colony's **actual running evaluator**,
followed by literal local physical faults and explicit correction/rejoin, before
using any endpoint shortcut again. The current initializer must keep rejecting
out-of-domain patterns. A one-tick replica-correction certificate can justify a
shortcut only after the actual local outputs establish the required equality;
it must not be used to assume or install recovery.

General stochastic full-alphabet noise, faults during work periods, geometry
and Signal repair, malformed encodings, broader top rings, depth-three execution
and robust finite caps remain open. Existing scalar/full-rule local-fault backends
and replica lemmas are useful starting points, with their recorded domains.
The one-cell top experiment is not a substitute for those requirements.

Gray pp. 31–32 and Gacs sections 9.2–9.3 remain the self-simulation source basis.
Candidate-B Flag2, voted-old-Signal D10, printed Flag2 persistence/SimBit ambiguity
and source amplification qualifications are unchanged. U<=128Q remains unnecessary.
No full noise-robustness theorem or threshold is claimed.
