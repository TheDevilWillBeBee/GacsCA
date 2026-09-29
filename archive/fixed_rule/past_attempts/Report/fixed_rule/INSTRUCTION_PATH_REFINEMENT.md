# Ordinary fixed-ROM instruction paths

2026-09-26. Complete conditional paths now cover every non-META instruction in
the actual fixed ROM: 20703 sites, with both branches of IF_THIRD giving 20704
catalog paths. They check the complete controller, Data effects, SEND packet
birth and exact duration starting at a matching FETCH. Together with
[META_PATH_REFINEMENT.md](META_PATH_REFINEMENT.md), this advances physical
instruction refinement of [ROM_DATAFLOW.md](ROM_DATAFLOW.md). It does not yet
justify composition of an entire program with mail and clock overrides.

## Scan relation and full-state contracts

For a rightward head at h, use scan coordinate h; for a leftward head use
2L-1-h, where L=30724 is the core length. Each flight or endpoint reflection
takes one physical tick. To reach a rightward memory target a from a rightward
head at h, the checked path takes (a-h) mod 2L ticks before processing that site.
Processing the memory event takes one additional tick. Equal successive operand
addresses require a full circuit because the head has already moved right after
the previous event.

`certify_small_holder_instruction_paths.py` derives that count by instantiating
the complete-raw event templates and checking every segment. Flights must
preserve all controller fields and Data. The checker verifies actual ROM records,
endpoint conditions and every non-hit condition. Memory is keyed by Address, so
aliased operands share the same old word; treating repeated addresses as fresh
independent inputs would give a false arithmetic contract.

An important distinction needed new leaves: in READ_A, READ_B, WRITE, TRANSMIT
and READ_LOAD, a matching index on a non-MEM site has no memory effect. The earlier
flight lemma unnecessarily required unequal indices everywhere. Ten new
non-memory flight/reflection families replace that condition with kind != MEM.
They are proved against all 154 raw outputs at nine holders in each of seven
regular clock intervals: 70 full-descriptor cases. Actual ROM inspection verifies
the non-MEM condition when these leaves are instantiated. A concrete scalar/native
test checks matching index 19 on a non-memory site and retained value 77, rather
than an erroneous read of Data 23.

Completed contracts cover all five arithmetic operations, LIT, LOAD, SEND, HALT
and IF_THIRD. They retain stale fields where the physical rule retains them and
clear the controller when the head halts. LOAD's arbitrary 64-bit result is
preserved in rd. SEND includes the emitted packet's direction, target, remaining
hop count, validity and full payload; it does not write memory. The full result
is derived from the leaf output and compared with a separately stated instruction
contract. Packet transport after birth remains outside this isolated contract.

For a matching FETCH at m followed by memory events at the instruction's operand
addresses, the certificate agrees with the cyclic schedule recipe used by the
older data-flow checker. Durations range from 1 through 163318 ticks across the
actual catalog. The certificate records every site's duration and representative
traces, plus the digest of all checked traces. Each complete path must fit inside
one regular active clock interval. IF_THIRD's legal intervals depend on its
clock branch.

The hypotheses remain canonical geometry, coherent procedure/static copies,
zero flags/Signal/Wf, one isolated head and no incoming mail. The prior descriptor
support certificate supplies the quiet exterior outside the checked event window.
These proof interpreters are diagnostics. No instruction-level interpreter was
installed as a physical evolution backend, and no physical rule or ROM changed.

## Tests and physical checks

Six tests passed. They cover the new full-raw leaves, the concrete non-MEM
matching-index example, aliasing in EQ, every SEND direction/hop tag, both
IF_THIRD branches, and rejection of dropped packet output, lost stale ALU state
or a missing tick. The full symbolic run checks all actual instruction sites;
the physical run is a representative sample, not concrete enumeration of every
site and input.

The GPU sample selects the first and last instruction in each actual arithmetic
alias/order class and each SEND direction/hop class, with other used kinds also
represented. This gives 65 sites. Six Data patterns include zero, all-ones,
random words and shift counts 63 and 64; aliases preserve one physical value per
Address. Runs start at Age 1 or 738197505, exercising both IF_THIRD branches.

Each physical run checks complete logical records and selected complete raw
physical records before/after FETCH, reads, writes and packet birth. Each
one-tick event uses the existing literal physical GPU step; longer flights use
the unchanged physical event backend. Host full-rule, evaluator and primary
controller calls are disabled during GPU evolution. Scalar expected-state
calculations are diagnostics only. SEND stops immediately after emission, so no
claim about subsequent packet transport is hidden in this experiment.

| Check | Result | Seconds | Peak host KiB |
|---|---:|---:|---:|
| Full symbolic catalog | 20704 paths passed | 59.562966 | 76616 |
| Focused tests | 6 passed | 2.506 | not recorded |
| Physical pilot | 120 completions, 10 sites | 2.224181 | 171972 |
| Physical selected-site run | 780 completions, 65 sites | 10.077379 | 186720 |
| Independent final audit | passed | 16.258178 | 79416 |

The selected-site run checked and saved 22686 complete logical records and checked
22686 full raw physical probes. GPU advance time was 0.724007 s, with 39168 local
evaluations; explicit device allocation was 3726576 bytes and recorded process
GPU memory was 422 MiB. No substantial GPU reservation or CUDA rebuild was used.

The independent audit checks all catalog sites and durations, 1890 complete
scalar/native outputs for the new leaves, 1456 complete scalar/native event-boundary
outputs, all saved logical records and the expected raw-probe digest. The native
checks validate the checkpoint model; actual GPU raw-probe assertions are in the
hashed driver. The audit does not replay every physical microstep. The pilot
also passed its independent audit in 8.383742 s (71372 KiB host).

## Reproduction

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.certify_small_holder_instruction_paths --clock-certificate figs/fixed_rule/small_holder_clock_events_v2.json --clock-audit figs/fixed_rule/small_holder_clock_events_audit_v1.json --output figs/fixed_rule/small_holder_instruction_paths_v1.json
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_instruction_paths.py -v
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_instruction_path_execution --pilot --output figs/fixed_rule/small_holder_instruction_path_execution_pilot_v1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_instruction_path_execution --output figs/fixed_rule/small_holder_instruction_path_execution_all_v1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_instruction_paths --certificate figs/fixed_rule/small_holder_instruction_paths_v1.json --execution figs/fixed_rule/small_holder_instruction_path_execution_all_v1 --output figs/fixed_rule/small_holder_instruction_paths_audit_v1.json
```

The pilot audit uses the same final command with execution stem
`small_holder_instruction_path_execution_pilot_v1` and output
`small_holder_instruction_paths_pilot_audit_v1.json`. All runs finished; no failed
ordinary-instruction attempt was superseded or omitted.

## Remaining composition and final-goal limits

These paths **start at a matching FETCH**. Reaching that FETCH from a reset or
previous completed instruction is still a distinct obligation. In particular,
FETCH on a MEM site must ignore an index match; the current generic non-hit FETCH
leaf is unnecessarily restrictive there. A suitable MEM/FETCH identity and
actual instruction-index guards can close this dispatch step. The ordinary
memory-target scan proof above does not silently establish it.

SEND creates nonzero mail, so its next instruction cannot simply reuse a
mail-free contract. Incoming packet motion, crossings, delivery, Data priority
and flag clearing must be refined and composed with the actual program's
noninterference conditions. Reset/vote/capture/commit, rest intervals and
arbitrary retained Signals also remain. Only after those joins can the full ROM
data flow and reset encoding yield an all-input work-period relation.

Gray's pp.31–32 specialized hard-wiring/projection and Gács §§9.2–9.3 modified
self-correcting simulation remain the source target. The self-description still
includes the evaluator's complete state and rule. This work adds no physical
field, register pair, depth case or alternative transition kernel. Q and U did
not change; the measured instruction costs can inform later optimization.
Correct full two-level execution and general cross-level noise suppression remain
unfinished. U<=128Q remains unnecessary, and the complete goal remains active.

## Provenance and coordination

- Catalog: `8c5d2bd82750e1ab4b528dd0fb5a651b8e258e7c30c19ae9401125bda0583be0`.
- Physical run manifest: `5a0b82076d4699128251860dce440953c3d6bca3e80ffad3945cc475dfc55904`.
- Physical archive: `5958ddf54aac49a139540a1e74aa251c82c4e1fed6eab4e840f2c70f7b79144c`.
- Final audit: `0c7ecb04c8efd02c42c83904cd053df5e6b0464397a16ba322a9bd4ba88bb224`.

Descriptor remains `af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`;
GPU binary remains `4419e5fdd8caeb81c884db3ede3d709d677693aee1943482040e171bc54f1c7e`.
Prior clock/META and new run/audit source hashes all match. Owned additions are the
ordinary-path certificate, test, physical driver and audit, this report and
namespaced evidence. Only our STATUS handoff was edited among existing reports.
No frozen/shared module or CUDA artifact changed. All own handles are terminal.
MAIN_AGENT_NOTES.md remains absent; please reply there. The separate 8 GiB request
is still pending and unused. The historical third-link process was not observed;
absence is not a completion audit.
