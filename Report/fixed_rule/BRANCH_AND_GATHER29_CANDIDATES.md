# Early-Flag branch and shared-gather fixed-rule candidates

2026-09-28. These are isolated CPU reference candidates in the owned
`gacsca/fixed_rule/` namespace. They preserve a single depth-independent
physical rule per candidate. The original ROM certificates below are
conditional on physical instruction/packet contracts. Subsequently, the
shared-gather candidate completed two accelerated physical lower work periods
on 15 encoded upper cells; see [GATHER29_FULL_PERIOD.md](GATHER29_FULL_PERIOD.md).
The branch-only candidates retain conditional status, and no noise-robustness
result is claimed. The earlier fixed-AND baseline is described in
[AND_OPCODE_CANDIDATE.md](AND_OPCODE_CANDIDATE.md).

## Source and design decision

Gray, *A Reader's Guide*, pp. 30–32 (`papers_txt/gray_readers_guide.txt`),
explicitly contrasts a lookup table with short copying/comparison routines and
loops. His ProgramBit projection hard-wires the self-description; the resulting
specialized simulator need not support arbitrary programs. Gács, §9.2–9.3
(`papers_txt/gacs_2001.txt`), permits simulation of an identical or suitably
modified self-correcting rule and describes a concise rule language. Those
passages justify examining fixed branches and reused routines, **not** the
particular numerical Q/U or a proof of error correction. Gray's `U=128Q` is
his illustrative schedule, not a necessary constant imposed by these passages.

The fixed-AND baseline evaluates its full 154-word local rule twice, though
the early evaluation only needs `f1` and `f2` for signals. Its optimized
description has 8926 operations. Backward slicing finds 445 operations needed
for both flags, all completed by operation 467. The baseline ROM reaches
that point after 600 instructions and 20,348,033 scheduled head ticks, while
the full evaluation takes 9295 instructions and 289,005,289 ticks.

`branch_holder_*` adds fixed instruction kind 15 (`BRANCH_THIRD`), still within
the four-bit kind field. The early age window branches from the flag slice to
the signal sends; the later age window falls through to all raw outputs and
the final commit. The branch itself and both outcomes are described by the
rule's own 154-output description. `branch29_holder_*` then retimes the fixed
clock constants to `U=2^29`, retaining `Q=16384` and radius seven. No
level-dependent kernel, physical register pair or host transition was added.

`gather29_holder_*` is a further isolated candidate. Its three stage-entry PCs
all point to the **same** 691-instruction gather body, at the three fixed reset
ages. The high bit `PHASE_MARK=2^31` in an instruction's destination or packet
target denotes a history-base slot. A fixed local age test maps that base to
offset 0, 2 or 3. The vote slot remains offset 1; all three original histories
remain independent for the later temporal vote. This is routine sharing, **not
yet a general counted-loop evaluator**. The high-bit interpretation changes
the physical rule and is included in its own local self-description. The
diagnostic checker chooses the stage on the host only to evaluate the
conditional ROM dataflow; the physical scalar rule derives the target from
the cell's local `Age`. Directed local-transition tests cover all three ages.

## Measured resources

| Candidate | Q | U | MEM | Instructions | Core | Scheduled controller path |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Fixed AND baseline | 16384 | 1073741824 | 3383 | 11380 | 14764 | 648041233 |
| Early branch at old U | 16384 | 1073741824 | 3383 | 11451 | 14835 | 383563835 |
| Early branch retimed | 16384 | 536870912 | 3383 | 11451 | 14835 | 383563835 |
| Shared gather, retimed | 16384 | 536870912 | 3383 | 10249 | 13633 | 357637146 |

The branch saves elapsed controller work, not colony space: describing its
own new transition costs 71 cells. Retiming enabled a twofold work-period
reduction for the shared-gather rule on the later tested canonical trajectory;
the branch-only retiming remains conditional. Sharing the gather body saves 1202 core cells and
25,926,689 scheduled ticks versus the separately compiled gathers. It leaves
2751 cells between the core plus five tail reservations and Q. The next
power-of-two colony size, 8192, still needs at least 5446 cells removed
(`13633+5-8192`); with MEM fixed, instructions must fall to at most 4803.
Thus neither of these small changes makes Q=8192 viable. `U=2^28` is also
impossible under this schedule because the final evaluation alone needs
274,064,188 ticks, before the other stages.

For the shared candidate, the computed minimum gather deadline margin is
5,423,588 ticks, early-flag capture margin 6,815,617, early-stage stop
margin 9,818,369, and final evaluation margin 109,935,812. The controller
path total is a sum of scheduled head phases, not the measured duration of
its subsequently executed complete period. The fixed rule identity has 154 raw words/4090 bits, 105 projected
words/2704 bits, and radius seven. Its complete physical self-description
SHA-256 is `71152fe782db86266ec4dad8f2dc84adeb71be7b190f13ece48fcf39d117261e`;
compiled-description SHA-256 is
`97504d9153a3f0e911a3a8cbcb704e1e9cbc9ed0aece470d1cd9109d65e168c9`.
The fixed ROM byte SHA-256 is
`dc5cf26b450b29673c1a9e9011df4852f69bada3c612aa10e38c1437585898eb`.
These identifiers are independent of requested hierarchy depth.

## Checks and their limits

`python -m unittest tests.fixed_rule.test_branch_holder -v`: 5 passed.
`python -m unittest tests.fixed_rule.test_branch29_holder -v`: 5 passed.
`python -m unittest tests.fixed_rule.test_gather29_holder -v`: 8 passed in
6.016 s. The tests cover all raw local outputs on random and clock-boundary
neighborhoods; structural arbitrary-typed self-description equality; fixed
alphabet, neighborhood and ROM over depths one through three; actual local
branch movement at both ages; actual local marked ADD/SEND target selection at
all three gather ages and all five holder replicas; complete controller-field
commit; and rejection of ROM mutations in the branch destination or phase
marker. The local-rule tests use only the radius-seven neighborhood.

`python -m experiments.fixed_rule.measure_gather29_holder --output
figs/fixed_rule/gather29_candidate_v2.json`: PASS in 4.354 s, peak process
RSS 376136 KiB. The receipt includes source hashes. Its symbolic dataflow
checks 15 colonies, 62,010 gathered histories, 183,510 instructions, 2205
metadata queries, 26,790 packets, early flag signals, and all 154 raw outputs
per colony at final Hold/Info commit. It checks independent three-time
histories and own-ROM metadata regeneration. Conditional packet delivery and
instruction scheduling are interpreted diagnostically, not evolved for a
complete physical period. Its independent one-step local-event certificate
checks all 154 raw words over nine holder positions for each of eight cases:
branch at early and late ages, one actual marked ADD and one marked SEND ROM
instruction at each of three gather ages (11,088 output words total). The
events assume coherent holder geometry, a regular active clock, arbitrary
surrounding MEM data, and zero flags/mail. They do not compose a head scan.
The report's resource numbers are from this receipt; the separately compiled
gather comparison uses the retimed branch candidate under the same Q/U. The
earlier `gather29_candidate_v1.json` is preserved as a pre-local-event receipt.

**Update:** The shared-gather candidate now has two continuous accelerated
lower periods and independently audited decoded upper macrosteps on a
15-cell canonical ring. Selected changed physical events match literal F at
their actual evolved states. A complete upper work period at depth two,
general physical-event composition, repair of corrupted simulated layers,
and levelwise noise amplification remain open. Existing certificates for the
former rule/ROM cannot establish those claims for this candidate. The printed Flag2 persistence
counterexample and computed-SimBit timing ambiguity also remain source
qualifications. The tested Q/U pair works on the stated canonical two-period
trajectory; that is not proof that all repair and higher-level obligations
work at these constants.

An apparent extra slot saving was rejected: collapsing each four-slot
history/vote block to three slots by overwriting a history with the first
majority would make the second temporal vote depend on that first vote,
instead of independently recomputing from all three original histories.
That would remove a repair mechanism for a very small space gain.

The next validation is broader physical event composition and repaired
upper-state execution while retaining the two-period regression. A substantive Q=8192 route
would require a counted-loop or algorithmic majority/correction evaluator;
sharing the gather body alone cannot remove the remaining 5446 cells.
