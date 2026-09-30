# U20 repair status

Started 2026-09-29. Ownership is limited to the five `u20_repair/` namespaces.

## Approach and identities

The physical baseline is `stream28_dual_pass20.local_step`, SHA-256
`f44caa3e59db8f621de389adb2c6e01f6d9b15f1b315a02ecce10524114cff81`.
The shared optimized description SHA-256 is
`7b044b61d3cd9ee540073b140a917095cf4fc4b11654753978f0a185637e4e39`.
The private successor copies the GPU agent's corrected description chain,
including the `select(selected,abs(offset),0)` hop count in `clock_description.py`.
Its expected WordCode digest is
`232fa6b96f3e2887975337ff52564e54d3a2f7fc59cbf59580e2adf8e1429f88`;
this is a starting point for independent checking, not an equivalence proof.

Additional shared source SHA-256: old clock description
`2a34946c6500c50cd26f51a1a2242941917ba0012f04dc8d59852977303e83da`,
GPU corrected clock `8ebaf6b5a2c3f11318286d0bb050b78e69e879353e22e04c8f86a05192103890`,
Address ROM projector `e10c6eb612bb496c0be647f4eb323f9c9c4fef92a99d2974faf12311b3197a6f`,
shared native backend `5832e57ba7bcc1019c1bb7d47fd63bc0ffaa47f767b4c737f0bc88ac59b3677f`,
corrected CUDA backend Python `c886753a315e8c97c25fa1f279efe8318eca98bc7dce428476d316d194189ece`,
CUDA source `65365a4a302b05c2f66a2dfea3449432dbba3ddf97f0568d11f388aaf1c0c73e`.

## Owned files

- `gacsca/fixed_rule/u20_repair/`: copied corrected description chain, circuit builder wrapper, private native executor.
- `tests/fixed_rule/u20_repair/`, `experiments/fixed_rule/u20_repair/`: harness under construction.

## Derived artifact disposition

Every artifact built from WordCode `16bf88a1…6257` must be regenerated:
Address-projected own-rule circuit ROM and its placement, route/schedule/timing
receipts, shared native C build, shared dense CUDA build, and compiled-F audit
receipts. Literal physical-F-only and independent holder maintenance tests are
unaffected. The GPU corrected description and its private placement are
provisional pending broader parity and physical lookup.

The exact shared-source correction, if ownership permits it later, is:

```diff
--- a/gacsca/fixed_rule/stream28_dual_core_clock_description20.py
+++ b/gacsca/fixed_rule/stream28_dual_core_clock_description20.py
@@
-        hop_counts[lane]=b.bor(hop_counts[lane],b.band(selected,b.const(abs(offset))))
+        hop_counts[lane]=b.bor(hop_counts[lane],b.select(selected,b.const(abs(offset)),zero))
```

`selected` is Boolean; bitwise AND narrows every positive hop count to its
lowest bit. The namespaced copy applies this fix. An extended 433-word codec
and evaluator/layout interface would additionally be needed for the physical
lookup successor; no exact shared patch is proposed because the current
three-slot recipe is already 3,831 slots short and cannot be repaired by an
interface-only edit.
The predecessor `stream28_holder_core_clock_description.py` has the same
line and needs the identical one-line replacement if that separate fixed
candidate is rebuilt. It was not edited here.

## First divergences

From GPU status, old physical age 2392, site 2491, raw field 101
`s2_rp_remaining`: literal F gives 7; old WordCode/CUDA give 1. The copied
successor gives 7 for that case. I will preserve new divergences here.

During construction of the 433-word successor description, a boundary test
at old Age 0 first disagreed at raw field 149 (`address`): literal 2491,
description 0; fields 150–152 also disagreed. This was a **description
wrapper defect in my new code**, not physical F: `word_prune.prune` returns
the older `wordcode.Program`, whose evaluator treats AND opcode 14 as unknown.
Wrapping the pruned DAG back into `wordcode_and.Program` removed the mismatch.
The resulting optimized digest and all later parity receipts use the fix.

## Established versus open

No oracle-free U period or successive macrosteps have been established for
this candidate. `rom_self_fetch/STATUS.md` was absent at this status update;
I will recheck before implementing overlapping work. No substantial GPU job
is requested or scheduled. CPU compilation and short parity jobs only.

## Update 2026-09-29 16:40 UTC

`rom_self_fetch/STATUS.md` remains absent. I read the GPU and design agent
statuses again. The design agent remains CPU-only on its distinct candidates;
its latest status says no GPU request. I used no GPU and requested no window.
All long CPU commands below were pinned to cores 8–11; peak observed host RSS
was 880 MiB for the two-tick full ring and 515 MiB for lookup-only runs.

### Corrected original rule

- Private corrected WordCode remains 14,830 operations, digest
  `232fa6b96f3e2887975337ff52564e54d3a2f7fc59cbf59580e2adf8e1429f88`.
  The original shared `16bf88a1…6257` is invalid for physical F.
- `python -m experiments.fixed_rule.u20_repair.differential --random-cases 96
  --output figs/fixed_rule/u20_repair/parity96.json`: 119 neighborhoods,
  50,099 raw outputs, literal Python = corrected WordCode = private native C,
  2.72 s. Six generated cases per listed opcode, all fourteen nonzero route
  offsets, 96 age values and nine trajectory neighborhood samples. These are
  generated-branch labels, not measured branch coverage; many random states
  do not execute their nominal opcode branch. The native source SHA-256 for
  this local backend is `376a9afb3fe2531c132ddc4905154c7230a041b5df3ba31d36ecad99d8cd84f3`.
- Manual audit of the corrected builder's `band` calls and its imported core
  and spatial builders found no second obvious Boolean-times-multiword
  constant use. This is not a formal all-state equivalence proof. A local
  Z3 executable/module was absent; no bit-blasted certificate was produced.
  A unit test exhausts both Boolean selector values and all fifteen offsets
  for the corrected hop-count expression, but this proves only that isolated
  branch formula.
- `python -m experiments.fixed_rule.u20_repair.certify_rom --output
  figs/fixed_rule/u20_repair/corrected_rom.json`: 7.362 s, 14,851 physical
  gate copies, 26,031 route edges, max 38 routes/site, max 3 gates/site,
  latest event 39,517 < 65,536. Canonical lower spatial ROM SHA-256
  `ba1c776d3bae7c01439a6cd88fec8cf21710e2c10dc752390dd429e853ebdb33`.
  This recertifies the corrected predecessor evaluator circuit, not a closed
  successor circuit.
- `python -m experiments.fixed_rule.u20_repair.inventory --output
  figs/fixed_rule/u20_repair/static_inventory.json`: 390 catalogued upper
  static dependencies, 383 physically wired SOURCE sites, 7 optimizer-pruned
  wires `[2991,2992,2993,2995,3110,3117,3124]`. The 383 SOURCE sites lie
  at physical addresses 2828–3217, all holder `kind=MEM,a=0,b=0`, outside
  history and Info/Hold banks. There is no current packet producer to refill
  their Data from represented Address.
- `python -m unittest -q tests.fixed_rule.u20_repair.test_initial
  tests.fixed_rule.u20_repair.test_differential`: 2 tests, 20.044 s, OK.
  The initializer test patches the upper static projector to raise, asserts
  all represented 119 words are encoded, and asserts every used static
  SOURCE Data starts zero.
- `python -m experiments.fixed_rule.u20_repair.run_short --colonies 15
  --ticks 2 --output figs/fixed_rule/u20_repair/oracle_free_two_ticks.json`:
  two consecutive all-sites native C transitions, no event skips, 27.767 s
  total (15.385 s first tick including native compile, 3.460 s second tick).
  Initial state SHA-256 `8cdaeab2e57310d263d3a3e068f82b83aa0f7319d602dd7e34609678e35daa4d`,
  tick-2 `ad8f6097aa45229562979a181fdb48353976d30eeefe7a4d30d251bde25fe7b6`.
  Six sampled sites per tick matched literal F on all 421 words; Age advanced
  0→1→2. This is a short continuous pilot, not a U period.

### Physical lookup successor prototype

`successor.local_step` is one fixed radius-seven rule over 433 raw words and
6,609 bits, with Q=8192 and U=2^20. It extends physical F with 144 bits:
three immutable lookup metadata fields and nine evolving broadcast/packet
fields. The lower immutable metadata is selected solely by physical site
Address, but it is compiled for the predecessor's 390 static dependencies;
the successor's own 393 static dependencies are not yet laid out or fetched.
At old Ages 0..8191 an Address token visits every lower site; at
Age 8192 each of 390 source sites launches one packet; each packet makes one
complete rightward colony lap, reads the requested static word at the matching
physical ROM row, returns to its unique source, and at old Age 16385 writes
the value to all five Data copies. At each Age 0 it reads the current Info
Address again, so the local protocol is specified to refresh after a work
boundary change; that successive-period case was not executed. The first
evaluator capture is at 393217, leaving 376831 ticks after the fivefold
write. Packet spacing is
fixed by distinct launch sites, so no two lookup packets share a site on a
healthy closed ring. The lookup transition uses local stored Age and Address;
the `lookup_bus.step` vectorized implementation reads radius at most three.

- `run_lookup_bus` on a one-colony closed ring with upper Address 173 and
  again with 4093, each from zero upper-static SOURCE Data. Staged version
  receipts are `lookup_staged_a173.json` (28.683 s, initial/final SHA-256
  `d855d38c…/1aad7bb0…`) and `lookup_staged_a4093.json` (25.268 s,
  `23c139b8…/b19733cd…`). In each, all 390 retrieved values and their
  fivefold copies (1,950 comparisons) matched diagnostic Address projection
  after physical token transitions. The two Addresses require 105 different
  static words. Peak RSS 515 MiB. These runs execute the lookup-only CA
  component, with Age advanced by that component; they do not execute base F
  for 16,386 ticks and cannot prove combined closure.
- Independent literal successor transition, full WordCode and private native
  C all agree on 96 random typed neighborhoods, 41,568 raw output checks,
  including every lookup phase boundary: `python -m
  experiments.fixed_rule.u20_repair.certify_successor --rounds 96 --output
  figs/fixed_rule/u20_repair/successor_parity96.json`, 21.411 s. Optimized
  WordCode 18,314 operations, digest
  `e2b91fce8158e515f2a6973f353f09813bb68040c1aebeaac0dded298594898f`;
  private C source SHA-256
  `aa534f59e58df936418b39af44f34ffd3b5dd087e73f9e626fe13e68e01f9e4c`.
- `python -m experiments.fixed_rule.u20_repair.capacity_successor`:
  fixed 8Q three-gather recipe requires 2,960 memory words and 393 static
  source sites, leaving 4,834 gate sites = 14,502 gate slots; the optimized
  successor needs 18,333 fanout gate copies, a deficit of **3,831 slots**.
  Raw input 3028 has fanout demand 422 versus 38 routes/site, requiring at
  least 12 buffer sources or another routing scheme. This is a counted
  obstruction to using the **unchanged three-slot 8Q evaluator/layout** for
  the successor. It is not a proof that no Q8192/U20 redesign can work.
- `python -m unittest -q tests.fixed_rule.u20_repair.test_protocol
  tests.fixed_rule.u20_repair.test_initial
  tests.fixed_rule.u20_repair.test_differential`: 8 tests, 15.992 s, OK.

### Remaining limits and requests

The 433-word successor is a complete local rule and a locally checked own
WordCode, but its own evaluator ROM has **not** been placed and the current
lookup table still addresses the predecessor's 390 words rather than the
successor's 393. The 119-word
predecessor encoding cannot represent its nine new evolving bus fields, and
the unchanged 8Q three-slot layout is short by 3,831 gate slots before
buffering. The lookup-only vectorized executor is therefore component evidence,
not a continuous full-F successor run. To continue this exact architecture,
one must widen the fixed spatial evaluator to at least five gate slots or
increase Q and U coherently (e.g. Q=16384, U=2^21), then recompile the new
rule, extend the projected upper codec and gather banks, certify routing and
timing, and run consecutive U periods. Neither option has yet been executed.
No GPU window is requested until the self-ROM fits and a same-rule executor
is available. There is no basis yet for damaged-state repair or noise claims.

## Final verification update 2026-09-29 16:45 UTC

After normalizing unused lookup metadata to valid typed zeros, the full owned
suite ran with `OPENBLAS_NUM_THREADS=1 taskset -c 8-11 python -m unittest -q
tests.fixed_rule.u20_repair.test_protocol
tests.fixed_rule.u20_repair.test_initial
tests.fixed_rule.u20_repair.test_differential`: **11 tests OK in 47.132 s**.
The added test compares the literal, WordCode and private C successor at the
fivefold retrieval commit for every copy. Another test compares the vectorized
lookup executor with the independent literal successor at every lookup phase
boundary; this resolves a concrete executor-equivalence risk in the component
receipts. No shared files were edited.
`figs/fixed_rule/u20_repair/source_hashes.json` records SHA-256 values for 28
owned source, test and report files. It was generated by a read-only Python
hash walk of the four owned namespaces; the receipt was newly written and not
overwritten. No processes owned by other agents were stopped or changed.
The final code/test source hashes after the isolated hop-selector regression
are in `figs/fixed_rule/u20_repair/source_hashes_code_v2.json` (26 files).

## Continuation 2026-09-29 18:32 UTC

All commands below used `OPENBLAS_NUM_THREADS=1 taskset -c 8-11`; no GPU
window was requested or used. I re-read the design and GPU agents' statuses;
the separate design agent still reports oracle-free one-level closure for its
own candidates, while the GPU agent's U20 pilot covers only the first gather.
`rom_self_fetch/STATUS.md` is still absent. The active 421-word rule hash is
unchanged at `f44caa3e…14cff81`. The 36-file owned/shared source inventory
is `figs/fixed_rule/u20_repair/source_hashes_code_v3.json`.

### New first divergences and fixes

- **Executor defect:** the vectorized lookup bus cast the full 64-bit Info
  word to `uint16` and broadcast 16 low bits; literal successor F masks to
  13 bits. An Info value `0xDEADBEEF1234A173` distinguishes them. I masked
  before the cast and added a regression comparing the vector bus to literal
  F. This defect affected the lookup-only executor for arbitrary typed upper
  states; previous lookup receipts used 13-bit Info values and were unaffected.
- **Construction defect:** the 433-word successor's packet reader selected
  only predecessor fields 0..420, returning zero for fields 421..432. Thus
  its three own immutable lookup fields could never be retrieved. The literal
  rule and WordCode now select all 433 fields. A test witnesses nonzero reads
  of fields 421, 422 and 423 in literal Python, WordCode and native C.
  The previous successor digest `e2b91fce…898f` and its native/lookup
  receipts describe the earlier incomplete successor and are superseded.

### Executed evidence

- `python -m experiments.fixed_rule.u20_repair.targeted_parity --output
  figs/fixed_rule/u20_repair/targeted_parity_v1.json`: 55 coherent cases,
  23,155 full raw outputs, 4.700 s. A Python line trace witnessed the
  literal `core.advance` branches for eight opcode classes and packed LIT.
  All fourteen nonzero stream offsets actually emitted packets with hop count
  1..7; 32 stage boundary ages were checked. Literal, corrected WordCode and
  private native C agreed throughout. This is measured branch evidence, not
  all-state equivalence.
- `python -m experiments.fixed_rule.u20_repair.differential --random-cases
  2048 --output figs/fixed_rule/u20_repair/parity2048.json`: 2,071 cases,
  871,891 raw output comparisons, 41.305 s, no mismatch. The opcode counts in
  that receipt are generator labels; actual opcode execution is witnessed by
  `targeted_parity_v1.json`.
- `python -m experiments.fixed_rule.u20_repair.certify_successor --rounds
  2048 --output figs/fixed_rule/u20_repair/successor_parity2048_v2.json`:
  2,048 typed cases, 886,784 raw outputs, 48.518 s, no mismatch. Final
  owned successor WordCode digest is
  `b13445f02a14053d06a41dd18065593bbf455efcbc3761afa2a1a2f22596eccc`
  (18,410 operations); private C source digest is
  `4acf6f730bfaa60c97abb38ce43086d8d11660216dc368eb2af2c8c89efd4a60`.
  No CUDA or SAT parity claim follows.
- `python -m experiments.fixed_rule.u20_repair.run_lookup_bus
  --successor-static --upper-address 3218 --output
  figs/fixed_rule/u20_repair/successor_lookup_393_a3218.json`: 16,386
  consecutive **lookup-component** ticks, 28.077 s, one closed colony.
  All 393 own static dependencies, including nonzero successor metadata,
  and 1,965 fivefold stored values matched after-run diagnostic projection.
  Initial/final state SHA-256 `cfcf476c…/bb1641d1…`, peak RSS 514,504 KiB.
  The three new source sites 3218..3220 overlap the predecessor gate bank;
  they are a provisional mapping until a new own-rule ROM is placed.
- `python -m experiments.fixed_rule.u20_repair.run_short_successor
  --colonies 15 --ticks 2 --output
  figs/fixed_rule/u20_repair/successor_two_ticks_v2.json`: two full-ring,
  unskipped native C ticks of the corrected 433-word rule, random upper
  states at 15 distinct Addresses, zero upper-static SOURCE Data, and
  393-site lower lookup metadata chosen by each physical site's Address.
  Eleven sampled sites per tick matched literal F on all 433 fields;
  physical Age advanced 0→1→2. Total 25.724 s, peak RSS 909,552 KiB;
  initial/final state SHA-256 `d4b2cbd5…/20bc6062…`. The retained lower
  evaluator ROM still describes the 421-word predecessor, so this is a
  same-rule local-transition pilot, **not** a self-simulation period.
- `python -m unittest -q tests.fixed_rule.u20_repair.test_protocol
  tests.fixed_rule.u20_repair.test_initial
  tests.fixed_rule.u20_repair.test_differential
  tests.fixed_rule.u20_repair.test_targeted`: 15 tests passed in 19.126 s.

### Remaining construction obstruction

The final successor's unchanged three-slot 8Q recipe has 4,834 gate sites,
14,502 slots, and needs 18,429 fanout gate copies: **3,927 slots short**.
It has raw input fanouts 434, 47 and 41 against a 38-route source limit.
This count uses the final `b13445f0…eccc` description. The provisional
393-source table cannot coexist with the predecessor evaluator gates at
3218..3220, and no final own-rule circuit, placement or schedule exists.
No continuous full-U period, successive decoded macrostep, damaged-state
repair or noise result has been established for U20. The explicit next
construction choice is a widened evaluator/layout or a coherently rescaled
fixed candidate; neither has yet been implemented. No GPU run is justified
before that own-rule circuit is placed.

## Balanced selector optimization 2026-09-29 18:41 UTC

I replaced the 433 separate packet-field comparisons in the successor's
WordCode with a fixed 9-bit binary mux. The literal 433-word rule did not
change. The previous `b13445f0…eccc` WordCode and C backend are superseded
by `8d6dc2b0fc92b5e2bb150c03f4bc21c35423e329f95420caf878dbe372aaab0a`
(16,328 operations) and C source SHA-256
`b0afeb3245dd3a31451382de4f589444fd1399f1373a3c798c65e59371d87980`.

- `python -m experiments.fixed_rule.u20_repair.capacity_successor --output
  figs/fixed_rule/u20_repair/successor_mux_capacity.json`: 16,363 required
  gate copies, 14,319 available three-slot positions, deficit **2,044**;
  raw input overflows are now 47 and 41 against the 38-route limit. The
  largest 434-use packet-field fanout was removed. Scratch demand grew from
  302 to 363, and available gate sites fell from 4,834 to 4,773. This is
  occupancy analysis, not placement or timing certification.
- `python -m experiments.fixed_rule.u20_repair.certify_successor --rounds
  2048 --output figs/fixed_rule/u20_repair/successor_mux_parity2048.json`:
  2,048 typed neighborhoods, 886,784 all-field Python/WordCode/C checks,
  44.767 s, no mismatch.
- `python -m experiments.fixed_rule.u20_repair.certify_packet_mux --output
  figs/fixed_rule/u20_repair/packet_mux_512.json`: all 512 possible typed
  packet-field selectors at a real fetch event, including 79 out-of-range
  values, 221,696 all-field checks, 10.414 s, no mismatch. This exhausts
  the selector for one rich typed center state, not all physical states.
- `python -m experiments.fixed_rule.u20_repair.run_short_successor
  --colonies 15 --ticks 2 --output
  figs/fixed_rule/u20_repair/successor_mux_two_ticks.json`: 32.630 s,
  peak RSS 910,632 KiB. Initial/final state SHA-256 remain
  `d4b2cbd5…/20bc6062…`, exactly matching the previous literal-equivalent
  backend's whole-ring outputs. Eleven sites per tick again matched all 433
  literal fields. The lower ROM is still for the predecessor, so no upper
  macrostep follows from this run.
- `python -m unittest -q tests.fixed_rule.u20_repair.test_protocol
  tests.fixed_rule.u20_repair.test_initial
  tests.fixed_rule.u20_repair.test_differential
  tests.fixed_rule.u20_repair.test_targeted`: 15 tests OK in 19.798 s before
  adding the exhaustive-selector regression to the suite. The selector
  experiment above passed separately. The optimized program still has the
  same 393 own static dependencies and provisional source mapping.

The remaining three-slot deficit requires a genuine layout/rule change.
Four gate slots per site would have 2,729 spare positions **if** the
16,363-copy program stayed unchanged, but adding a fourth slot changes the
physical alphabet and own-rule WordCode, so this is only a sizing hint.
The existing two-bit target slot value 3 marks an OUTPUT; a fourth gate slot
would require widening that field and recompiling the whole rule, codec,
projection, ROM, routes and schedule. I did not claim a four-slot candidate.

Final owned regression command above, repeated after adding the exhaustive
selector test: **16 tests OK in 28.600 s** at 18:42 UTC. No source in a
read-only namespace was edited, and no GPU job was started.
