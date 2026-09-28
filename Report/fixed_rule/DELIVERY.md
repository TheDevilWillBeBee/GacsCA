# Fixed-ROM computed-flag delivery

This revision connects the previously isolated signal mechanism to actual
encoded-state retrieval and evaluation. The completed, independently audited run
is described separately from
the frozen early-program two-period result: until the physical flag waves and
stage-five commit are executed, it is a **physical prefix, not a complete new-rule
macrostep**. The result/progress JSON records completion; the audit separately passed.

## One described controller and one immutable program

`delivery_rule.py` includes the complete word controller, printed maintenance,
clocked resets/votes/commit, redundant signal capture and Wf generation. Its
alphabet has 788 raw bits in 32 words. Projecting out the seven immutable program
fields gives 590 physical bits in 25 words, at radius five. Q=8,388,608 and U=128Q
are fixed for all requested depths. The program describes this rule, including
its own new stage gate; it is not a depth-specific rule-family test ROM.

`IF_THIRD` uses opcode 13 in the existing four-bit Kind field. At FETCH during
stage three it increments PC; at other ages it removes the head. The same
computation entry can therefore serve stages three and five, with ten additional
SEND instructions executed only during stage three. The gate tests physical Age
inside the transition; no host stage or hierarchy dispatcher implements it.
Metadata lookup still sees the literal gate kind, not a remapped opcode.

The five left buffers are reserved memory cells 1…5. The five right buffers are
at Q−5…Q−1. In the latter range the immutable static fallback is MEM, index=Address,
a=31; all other fallback fields are zero. The full META fallback describes that
same rule, so early/output program reconstruction works for simulated right
buffers too. These buffers reset at stage boundaries; Signal, being reserved
SimBit storage, survives the stage-four workspace reset.

After evaluation and Hold program reconstruction, the gate permits five left
SENDs from Hold.Flag2 and five right SENDs from Hold.Flag1. They travel through
the ordinary local packet channels, enter MEM buffers, and are consumed there.
At computed Age 79Q each holder's Data low bit is captured into the appropriate
Signal copy. No capture payload is installed by the experiment driver.

The choice to use voted old Signal before remote structural clearing remains
explicit, with the D10 locality witness in SIGNAL.md. Fivefold protection applies
to Signal only; raw controller, mail and general workspace redundancy is missing.
The printed Flag2 rule, including D8 persistence, is unchanged.

## Capacity failure, then a semantics-preserving reduction

The direct complete description had 3,050 operations and an 8,717-cell program.
Evaluation cost 71,836,786 ticks, exceeding 8Q by 4,727,922. Final stage-three
delivery missed 79Q capture by 4,893,557. These failed measurements are preserved
in `delivery_unpruned_timing_v1.json`.

`word_prune.py` removes expression wires unreachable from **any** raw output.
Inputs and outputs retain their full width; it neither specializes to initialized
states nor chooses a level-specific rule. All operations are pure finite-word
expressions, so reachability is sufficient. Tests compare the original and pruned
descriptions against scalar and native rules on complete arbitrary raw states.

The resulting complete description has **2,680 operations**, SHA-256
`4391ae3edb105da9e9d4865be2040e3cf80fa7952e554b0f19e537505b238eed`.
The fixed core has **7,977 cells** (4,161 memory, 3,815 instructions, one reflector).
The stage-three vote moves from 72Q to 70Q inside F and its description.

| Procedure | Physical ticks / margin |
|---|---:|
| Early program repair | 336,482 |
| Third gather last arrival from 64Q | 48,085,467 |
| Margin before 70Q vote | 2,246,181 |
| Stage-five evaluation through gate halt | 57,793,354 |
| Margin below 8Q | 9,315,510 |
| Stage-three head halt from 70Q | 57,952,905 |
| Final signal-buffer delivery from 70Q | 66,333,537 |
| Margin before computed 79Q capture | 9,163,935 |

The actual final packet is tested one tick before and exactly at its predicted
arrival; all ten buffers receive the payload, and the head has halted. Separate
world-line tests exclude same-track collisions for the compiled gather sends.
The timing certificate is checked before constructing the prefix executor.

## Physical executor domain and evidence

`delivery_prefix_world.py/.c` stores each complete core plus five tail buffers.
The gap between the core and tail has fixed local background and carries ordinary
ballistic mail. Events account for physical flight distance, colony-boundary hop
counts, pauses in rest periods and clearing at resets. Local transitions execute
against the canonical-geometry specialization of F. Head travel is skipped only
between local events; signal settling prevents a quiet jump until the fivefold
profile is a fixed point. Computed Signal and payload remain actual physical
fields. No host upper transition or expression evaluation runs during dynamics.

This executor requires canonical Address, uniform Age, zero initial physical
flags/signals and no tail heads. It **rejects any run crossing computed Age 96Q**.
It therefore does not silently apply a zero-flag kernel once Wf begins. Its
complete-description ROM contains those later transitions, but physical execution
of them is still pending. Tests compare the conditional kernel against complete F
on arbitrary controller/Data/Signal values within its declared domain.

The long experiment uses 23 represented cells, all 11 distinct neighbors per
cell, and mixed computed upper flags. An active simulated WRITE changes Data to
0x123456789ABCDEF0. Starting from the encoded configuration, it performs early
program overwrite, three real gathers, majority vote, complete evaluation,
program reconstruction, gate execution, ten payload flights, signal capture and
rest until 96Q−1. Saved artifacts include every raw history, vote, Hold, payload
and Signal record, plus the final complete stored core/tail arrays. A separate
auditor checks the arrays, complete scalar/native/description outputs, compiled
identity and archived/live source hashes. The execution and independent audit both passed. It represented
**805,306,367 physical ticks** in **524.7449483852834 s**: 22,684,427 literal core
ticks, 709,777,043 exact quiet ticks and 72,844,897 guarded head-scan ticks;
1,149,204,177 local evaluations. There are 192,937,984 represented physical sites
and 183,586 explicitly stored core/tail sites. No pending packets remain.

The audit verifies 142 archived/live sources plus the binary/ROM identity and all
saved arrays. Main artifact SHA-256:
`bb5287e40e3de42f35e294cdd6e3cbf3a849c1370ee396688f9b5a49af96fe35`.
Source archive SHA-256:
`d37b9f8e39e1866ec9eb2a1690d4650c4700e3ca4412dea5282354ec2271452b`.
These results verify actual computation-to-delivery-to-capture under the fixed
ROM. They do not establish the unexecuted stage-four/five transitions or commit.

## Closure tests, termination and next execution boundary

Tests verify instruction-for-instruction embedding of the complete F description,
all raw output-copy targets, literal opcode metadata, immutable ROM/width across
depths 1–3, and real Info/Data paths for every raw word through those depths.
A native dense-neighborhood test changes every outside-radius site in turn.
Depth initialization remains initial-data recursion; **no deeper transitions have
been executed**.

The former nonzero-payload flagged cap no longer forms the claimed orbit: tail
MEM reset erases its Data. The zero-payload flagged homogeneous cap is checked
across all stage/capture/Wf boundaries and remains an Age-periodic orbit of the
same G. It is not an organized termination boundary or a robustness theorem.

`delivery_factorization.py` records a useful exact domain lemma for the next
executor: canonical Address/uniform Age remain invariant for arbitrary flags;
all controller, Data and Signal outputs are independent of those flags. Mail is
the corresponding zero-flag result followed by computed-Flag1 clearing, and Wf2
is additionally gated by computed Flag1. Receiving a payload can still update
Data on a transition whose outgoing mail is cleared. Complete raw-state tests
cover this distinction. This permits a future composed executor but **does not
supply or omit the actual physical flag evolution**.

Next evolve the signal/flag component through the whole trickle window, preserve
its coupling to mail, and execute stage five plus boundary commit under the same
fixed G. Then validate a second period, complete spatial redundancy/repair and
organized termination, and pursue deeper dynamics and measured noise robustness.


## Flag-profile evidence for the next executor

`flag2_bits.py` gives an exact finite-Q bitplane representation for the restricted
canonical subsystem with no Flag1/right signal and a coherent left signal, from
Age 96Q−1 through U−1. Bit shifts implement only the five left-neighbor reads;
inside-colony birth and vacuous outside-colony erasure differ at the boundary.
The clock generates and removes Wf2 without host per-step selection. Full
coupled flag execution remains missing.

The two tests compare 240 literal steps with the existing scalar physical flag
projection, check Wf timing and reject unsupported ages. The 65,536-tick probe
runs in 0.12675732001662254 s. At powers of two, (support length, count) includes
(31,31) at 64, (57,57) at 256, (109,109) at 1,024, (421,421) at 16,384 and
(837,837) at 65,536. Intermediate profiles have holes, so these samples do not
justify a translating-interval acceleration or an asymptotic speed claim.
This restricted probe should guide exact flag execution, not substitute for the
coupled case produced by the complete delivery run.
