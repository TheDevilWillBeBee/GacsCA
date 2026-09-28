# Bounded host memory and isolated CUDA execution

The user clarified on 2026-09-26 that CPU RAM is shared. Host-wide free RAM is
not an allocation budget. The current effective cgroup limit is 48 GiB. The
3,601-colony CPU attempt would require an 82,588,214,800-byte pair of dense
logical-state buffers, before other arrays. It must not be restarted as designed.

The attempted process and its unified-exec handle are absent. Its only output is
an initialization log and source archive, with no completed data/result manifest.
The exit cause is not established. This is recorded in
`figs/fixed_rule/holder_depth2_causal_v1.stop.json`; no depth-two causal-prefix
execution result follows from that attempt. Earlier audited one-link runs and
the explicitly nonembedded fifteen-colony benchmark remain unchanged.

## Implemented CUDA building block

`holder_packed.py` losslessly packs all 25 coherent-representation fields into
604 bits / ten uint64 words. This representation retains every controller,
Data, mail, geometry, flag and Signal word. It does not change the physical
105-word / 2,724-bit holder alphabet, the 154-word raw self-description, the ROM,
the neighborhood or the rule with depth.

`holder_cuda_local.{py,cu}` compiles the same exact zero-flag canonical physical
prefix expression used by the CPU. Metadata comes from the same immutable ROM.
Its GPU batch ABI has no depth parameter or upper-rule callback. It accepts at
most 4,096 logical radius-five neighborhoods; their coherent reconstruction has
the fixed physical radius seven. It rejects noncanonical geometry, nonuniform or
out-of-prefix clocks, flags/Wf and oversized batches. Build products stay under
`figs/fixed_rule/build/holder_cuda_local_*`; no shared CUDA source/artifact changes.

Three tests passed in **1.415 s**:

```
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p 'test_holder_cuda_local.py' -v
```

The tests cover random packing round trips for every raw logical field, padding
and width rejection, 160 GPU-versus-CPU local transitions, 32 complete physical
holder reconstructions versus the full native rule, and explicit domain/batch
rejection. They include reset, rest, evaluation entry, capture and boundary sites.
The physical descriptor hash remains
`314843221ed0692fbb560ba13d503f6daa557b3c9e54340769d308f49f66db25`.

Measured small execution:

```
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.holder_cuda_resources --output figs/fixed_rule/holder_cuda_resources_v2.json
```

This passed in 1.0308318622410297 s, with maximum host RSS **179,684 KiB** and
**3,364,192 bytes** of explicit device allocations and host transfers for 160
neighborhoods. CUDA context memory is additional to explicit device allocations.
The v1 diagnostic log preserves a parser-name collision; the measurement driver
was corrected before v2. No scientific transition or existing result changed.

## Remaining GPU executor work

The large GPU colony/event executor is **not implemented yet**. The validated
local kernel is one required component, not a replacement for a complete run.
The two packed state buffers for 3,601 colonies would require 33,035,285,920 bytes
rather than 82,588,214,800 bytes. Active-site indexes, event queues, ROM, temporary
storage and context still need an explicit budget and enforcement. A provisional
40 GiB total device allocation budget appears feasible but is not a measured
large-run result.

Keep host staging below 1 GiB, initialize encoded records directly into device
storage from bounded chunks, and retain evolving Data/controller/mail on the GPU.
Port the tested local/event semantics and compare entire traces with the frozen
CPU executor, including metadata queries, packet crossings, all clock boundaries
and consecutive periods. Do not replace evolution with host upper transitions.
A full physical light-cone guard remains required for the planned depth-two
controller-prefix claim; its target is still not a complete top macrostep.

The GPU was idle before/after these small checks. Main-agent GPU coordination
remains through STATUS.md / MAIN_AGENT_NOTES.md before a substantial allocation.
No large GPU job is running; no shared job was stopped or modified.
