# Routes toward Gray's U=128Q timing

2026-09-28. This is a research roadmap, not a claim that Q=8192,
U=1048576 has been constructed. It uses the measured `packed28_holder_*`
candidate in [PACKED_ROM_Q8192_U28.md](PACKED_ROM_Q8192_U28.md) and the
supplied Gray/Gács texts. The current candidate has a fixed physical rule
and two physically executed lower periods, but its clock is U=2^28.

## What Gray's number means

At Q=8192, Gray's `U=128Q` equals 2^20=1048576. Gray, pp. 28–31 in
`papers_txt/gray_readers_guide.txt`, moves whole SimBit streams through
Mailbox fields and implements copying/comparison in nested loops. On p. 34
he divides the period into three gathering stages with 16Q=131072 active
ticks each and a fifth-stage update window with 8Q=65536 active ticks.
He cites a `3Q+a log2 Q+b` bound for that final procedure, with constants
not specified in the guide; he says it fits for **sufficiently large** Q.
The separate assumption `Q>=2^13` on p. 15 does not certify that the
unspecified computation constants fit at the lower endpoint Q=8192.
Gács §9.3, Condition 9.20, likewise gives space/time inequalities with
an unspecified interpreter coefficient, not an executable 8192-site ROM.

| Physical task | Current measured path | Gray-style active budget | Ratio |
| --- | ---: | ---: | ---: |
| One information gather, including last packet | 12018404 ticks | 16Q=131072 | 91.7× |
| Early Flag-only evaluation | 10688979 ticks | Within third 16Q window | 81.5× |
| Complete late evaluation | 159058378 ticks | 8Q=65536 | 2427× |

The fifth stage is decisive. It executes 9903 virtual instructions, averaging
16062 physical head ticks each, because one head visits widely separated
ROM and MEM sites for fetch, operands, and writeback. Of the 159.1m ticks,
NAND alone accounts for 78.6m, AND 26.0m, ADD 23.6m, and EQ 14.8m.
The gather stage serially launches 592 nonlocal word packets per colony;
three gathers plus ten Flag sends yield 1786 packets per lower period.
This per-word serial launch is why a communication task that should cost
O(Q) takes 12m ticks.

The complete optimized own-rule Boolean program has 9531 word operations
but only 72 dependency layers (the Flag outputs have depths 42 and 50).
Its first layer has 1240 independent operations. These measurements show
substantial *potential* parallelism, though they do not prove the required
local spatial routing fits in Q cells and 8Q ticks. A head retaining the
present fetch/read/read/write execution model would have less than seven
ticks per virtual late instruction under the 8Q budget, versus 16062 now.
Another ROM packing or clock retiming cannot bridge that gap.

## Ranked architecture experiments

1. **Stream the gathered words through local mail tracks.** Keep three
   independent temporal histories and fivefold copy repair. Put the
   represented raw fields at fixed addresses; at a stage boundary, each
   site emits its assigned word as a scheduled stream, so many words move
   simultaneously. Use the existing two directions, static rank/target
   positions and either collision-free time slots or a fixed small number
   of constant-width lanes. The acceptance target is all 689 gathered
   words per upper cell delivered and voted within 16Q ticks, including
   seven-colony hops. A first prototype can stream one neighbor/direction,
   then all fourteen, before changing the evaluator. Gray pp. 28–29 gives
   the source pattern; our packet-guard and raw-history checks provide a
   precise regression oracle. The challenge is preserving error isolation
   with moving replicated data and no collision or host routing.

2. **Replace the serial ALU head with a spatial specialized evaluator.**
   A physical site should process a fixed field/routine or a small set of
   gates in parallel with other sites, using local streams to bring its
   inputs. Hard-wire the Gács/Gray rule family rather than interpreting
   arbitrary user programs. Start with one output family (Address/Age,
   then Flags, then controller/mail) and measure exact routed makespan,
   live storage, and communication volume. The target is complete 154-word
   raw F, including active controller state, in at most 8Q ticks after
   retrieval. The 72-layer word-DAG is a profiling fixture, not a ready
   spatial layout: a naive full-colony sweep per layer would cost 72Q and
   miss the budget. Streaming, short wires, and 64-bit field primitives
   such as compare/majority/shift must avoid those repeated sweeps.

3. **Close self-reference around the new parallel hardware.** Every new
   mail lane, gate controller, clock and repair field changes physical F.
   Its projected upper state and complete evaluator must include that
   state; the physical rule and evaluator must stay fixed across depth.
   Use Gray's Address-determined hard-wiring or Gács's `My-rules` pattern
   to encode a compact, parameterized rule family. Compile the actual
   resulting F, check all raw outputs, run the new physical event states,
   and retain the two-consecutive-period upper-transition test. This is
   the main construction risk. Merely displaying a short program or
   calling host F from a diagnostic does not close it.

4. **Reduce live storage and circuit routing once timing is credible.**
   The current MEM region uses 3383 of 8192 sites; the packed ROM/core
   uses 7597. A spatial evaluator must time-share scratch or pack several
   fixed-width lanes per site without exceeding the fixed projected state
   budget. This is necessary for Q8192, but isolated storage compression
   will not solve the U target. Four-instruction ROM packing on the current
   virtual program has an optimistic 6800-site core and 142.4m-tick late
   traversal *before* adding its own decoder, still far above 8Q.

An intermediate target such as U=2^24 can be useful for validating each
subsystem, but the acceptance criterion should remain the stage-wise
16Q/8Q schedule, not just a smaller power-of-two period. GPU execution
can shorten experiment wall time; it does not reduce the CA work period.
The existing guarded CPU backend handled 15 upper cells in about 50 MiB
peak process RAM. Whole Q-colony upper experiments will need compressed
GPU state even after the clock is shortened; a dense raw two-level snapshot
alone is about 82.7 GB before buffers.

**Assessment:** There is a plausible architectural path to Gray-scale
timing through parallel communication and specialized spatial computation.
There is no credible incremental path from the current one-head ROM via
packing, retiming or CUDA alone, and the supplied papers do not establish
that their hidden constants fit the concrete pair Q=8192, U=2^20.
