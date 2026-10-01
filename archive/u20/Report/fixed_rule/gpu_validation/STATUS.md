# Dense GPU validation status — 2026-09-29 16:00 UTC

## User-directed change of scope

At approximately 15:58 UTC the user stopped the dense check and prioritized
the missing physical upper-ROM lookup. No further dense or substantial GPU
job is scheduled by this agent. The clean corrected first-gather result below
remains a conditional test with host-prepared upper SOURCE words, not proof of
self-simulation. I wrote a standalone coding-agent handoff at
`Report/fixed_rule/gpu_validation/ROM_SELF_FETCH_AGENT_PROMPT.md`; its new
owner is assigned separate `rom_self_fetch/` namespaces. The design agent's
acknowledged 15:55–16:10 UTC A100 window remains available to it.

## Scope and identity

The physical transition is `stream28_dual_pass20.local_step`, Q=8192,
U=1048576, radius seven, 421 raw words and 6465 bits. Its optimized own-rule
WordCode digest is `16bf88a1d4ff5496cd3b61a1200f8a809db1438472a9191fded26de3a0786257`.
`gacsca/fixed_rule/gpu_validation/dense.{py,cu}` is an isolated copy of the
existing tiled CUDA execution backend. It compiles into
`figs/fixed_rule/gpu_validation/build/`; it evaluates all 421 outputs at every
site and tick. Source hashes are recorded in each run receipt.

## Current approach and GPU schedule

`gpu_validation/initial.py` builds a periodic lower ring from canonical
physical Address and ROM rows. Each colony's Info/Hold banks initially hold
one varied projected upper state; every fivefold Data copy agrees with the
neighboring physical source; 390 used own-rule static inputs are loaded into
SOURCE Data through Address projection. A 31-colony ring provides a central
upper site with two radius-seven macrostep neighborhoods clear of the upper
geometry seam. No 31-cell upper ring can be globally canonical modulo Q;
the seam is tracked explicitly.

`experiments/fixed_rule/gpu_validation/run.py` runs the complete backend
without skips or reinitialization, writes read-only checkpoint hashes and raw
samples, checks Age/Address/static fields and 119 decoded Info words, and
preserves the full raw state if an assertion first fails. It samples literal
Python local-F parity on consecutive checkpoint pairs. Its upper-F oracle is
used only in diagnostics at work boundaries.

At 14:39 UTC `nvidia-smi` reported an idle A100 80 GiB, 5 MiB allocated,
no compute processes. A bounded 15-colony three-tick pilot and a 31-colony
1000-tick pilot have completed. Explicit 31-colony allocation was
4,751,491,072 device bytes and peak host RSS 3,978,144 KiB, below the 40 GiB
limit. Stricter three-tick pilots also passed. The design agent's status
confirmed CPU-only work and no GPU request at 15:05 UTC.

**A100 window released after first divergence:** the corrected 31-colony two-U job started at
15:09 UTC (PID 48819, tool session 70179). Earlier attempts v1 and v2 were
stopped by this agent during the first gather interval to add independent
761-word gather-bank predictions, then to make the expected evaluator
capture depend on each period's represented upper state. Their partial
receipts are preserved and make no full-period claim. A bounded v3 three-tick
pilot passed before restart. The measured initialized
997-tick segment took 14.006 seconds, or 14.048 ms/tick. Two U periods
project to 29,461 seconds (8.18 h), plus initialization/checkpoints, with
expected finish about 23:27 UTC. The job uses approximately 4.75 GB explicit
VRAM (5.336 GiB observed in `nvidia-smi` including runtime allocations),
under 8 GiB host RAM, and saves read-only checkpoint receipts and full raw
snapshots at U boundaries. The design agent should remain CPU-only during
this window unless a GPU window is acknowledged here. It exited at the first
failed gather checkpoint; no U period completed.

At tick 65,515 the central colony's stage-zero history word for represented
upper `Address` (neighbor index 0, projected field 100, physical site 14)
was 14; the independently initialized source upper Address was 8. The
complete raw state is preserved in `dense31_2u_v3_divergence_t65515.npy`,
alongside the tick-zero snapshot and receipt. The preceding 65,511-tick
GPU segment (tick 3 to 65,514) measured 918.2 seconds, 14.016 ms/tick.
Every colony at physical site 14 stored its immediate-left upper Address,
not the required seven-left Address. This is systematic. A focused packet
trace will determine whether physical F, CUDA, or the arrival expectation
caused it.

**Root cause isolated:** at old physical age 2392, site 2491 emits the
neighbor-minus-seven gather packet. `stream28_dual_pass20.local_step`
computes `s2_rp_remaining=7`; the existing 14,830-operation optimized
WordCode and its CUDA backend both compute 1. The first raw divergence is
field 101 at tick 2393, before any boundary crossing. The WordCode builder
in `stream28_dual_core_clock_description20.py` uses
`b.band(selected,b.const(abs(offset)))` while `selected` is a Boolean 0/1.
This masks a seven-hop count to one. The exact shared-source patch would
replace that expression with
`b.select(selected,b.const(abs(offset)),zero)`; all transitive descriptions,
the Address-projected circuit ROM, and the compiled backend must then be
rebuilt and re-certified. No shared source was edited. The isolated successor
under `gacsca/fixed_rule/gpu_validation/` makes this change. Its optimized
description remains 14,830 operations, digest
`232fa6b96f3e2887975337ff52564e54d3a2f7fc59cbf59580e2adf8e1429f88`.
At the first failing emission its Python F, corrected WordCode and corrected
CUDA output match all 421 words; the old WordCode differs only at field 101.
This is a compiled-description/physical-rule parity defect, not an A100
arithmetic or launch defect. The old physical own-rule ROM still describes
the wrong WordCode; corrected ROM placement and schedule need new evidence
before a full self-simulation cycle can be claimed.

The corrected WordCode was re-encoded through the existing placement and
schedule algorithms in an isolated process: 14,851 gate instances, 25,912
operand packets, all complete by evaluator tick 39,517 of 65,536, with
digest `232fa6b96f3e2887975337ff52564e54d3a2f7fc59cbf59580e2adf8e1429f88`.
The 1,151 used raw inputs and 14,849 physical gate copies are unchanged.
`run_corrected.py` prepares this corrected ROM through a process-local
initial-data context and then calls the corrected same-F backend for every
tick. A three-tick 15-colony pilot passed, initial full-state SHA-256
`ea9528306dad99f14cc102392b49637cb5a929f1a45f70e0d63e6ef706320f1e`.
Four corrected regressions passed in 46.845 s, including all fifteen gather
offsets, arbitrary typed full-word parity, packet wrap and active evaluator.
The corrected 15-colony first-gather trajectory **completed** 65,516
uninterrupted physical ticks in 517.246 seconds. The 65,511-tick segment
from tick 3 to 65,514 took 509.44 seconds (7.776 ms/tick). All 761 central
history words matched independently predicted upper inputs at ticks 65,515
and 65,516. Full-state SHA-256 values: tick 65,514
`03a469c64dd8b34afcfdff350ac5b6b243d704bddd0ca23419a2e30d2922d138`,
tick 65,515
`dc18ac7e322a8fc03c0768f07a5448bcc8d703cb27955911dd9829b075b69ee1`,
tick 65,516
`e28041217057f19edb8437960975f8dd7fcc83535b33b6eae65aef5d9b3af223`.
Device allocation was 3,868,590,080 bytes and peak host RSS 2,049,036 KiB.
This is a successful gather pilot, not a U-period result.

**Next bounded A100 window:** a 15-colony trace from age zero to route
arrival 57,260 will run about 8 minutes at the measured 15-colony rate,
with approximately 3.87 GB explicit VRAM and under 5 GiB host RAM. It
reads emission, first-edge, intermediate-target, and intended-arrival
states, with Python F parity around the first edge. No design-agent GPU
request was present at last status check.

## Commands and results

Completed:

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.gpu_validation.run \
  --colonies 15 --periods 1 --stop-tick 3 \
  --output figs/fixed_rule/gpu_validation/receipts/pilot15_t3.json
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.gpu_validation.run \
  --colonies 31 --periods 1 --stop-tick 1000 \
  --output figs/fixed_rule/gpu_validation/receipts/pilot31_t1000.json
OPENBLAS_NUM_THREADS=1 python -m unittest -q \
  tests.fixed_rule.gpu_validation.test_dense
```

The 15-colony pilot completed in 54.449 seconds, initial SHA-256
`669107963c8ac7013f6c3ca27f4e4630bf6e5b99b5ba7b05651486c3f1087525`;
three literal transitions and all checks passed. The 31-colony pilot completed
in 60.699 seconds, initial SHA-256
`ad67a932651da9446e9ccc5089bfd1708ee6b4e141fe2bc15e9e95aeae3ecfeb`;
the initialized 997-tick segment took 14.006 seconds. Its tick-1000 SHA-256
was `e466b539efb253af730d15a46fa69ecb363b6dac3fa2553922ae5a38d875b9f9`.
Five independent regressions passed in 12.174 seconds. A first test attempt
used the Python spatial dataclass on raw typed route-slot value 3, which that
dataclass rejects although the raw word width permits it. This was a test
oracle domain mistake; the arbitrary typed case now uses the separate
WordCode evaluator. The GPU rule did not diverge.

The stricter 31-colony three-tick pilot also completed in 16.605 seconds,
with initial SHA matching the previous 31-colony pilot and runner SHA-256
`27494d8a8bc5d54504ae317f896c09774739f83b937d3f8517fdfa2b34beb287`.
The failed receipt is
`figs/fixed_rule/gpu_validation/receipts/dense31_2u_v3.json`; its log is
adjacent. The job command is:

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.gpu_validation.run \
  --colonies 31 --periods 2 --snapshots \
  --output figs/fixed_rule/gpu_validation/receipts/dense31_2u_v3.json
```

## Design-agent coordination

At 15:05 UTC I read the newly created
`Report/fixed_rule/design_optimization/STATUS.md`: the design agent is
CPU-only and has no GPU request. I agree with its finding that the current
initializer's 390 static SOURCE words use the upper Address on the host.
The dense run tests one chosen Address-projected clean configuration; it
cannot establish a physical self-fetch or damaged-ROM closure. The A100
window is now free after PID 48819 exited. I will publish the bounded trace
window here before using the GPU again.

At 15:43 UTC I read the design agent's GPU request 1(a). **Acknowledged:**
the design agent may use the A100 for its short under-1-GiB parity/benchmark
bursts, at most ten minutes total, from **15:55 to 16:10 UTC**. I will not
run a GPU job in that window and will check `nvidia-smi` afterward. Its later
exclusive 1–3 h request 1(b) needs exact proposed times before scheduling.
My corrected first-gather pilot finished at 15:53 UTC and released the A100.
The design agent's acknowledged 15:55–16:10 UTC window remains in force.

## Next steps and requests

Trace the packet through emission and its first colony edge with complete
421-word Python/CUDA parity at selected sites. Decide whether an executor,
initializer, or construction change is warranted before any new long run.
No design-agent GPU request has been received yet.
