# Conditional prefix embedding and a finite noisy light cone

2026-09-27. The fixed descriptor, ROM, alphabet, Q and U are unchanged. This
CPU-only work addresses the missing initial-context obligation identified in
[the wider repair report](WIDE_CONTEXTUAL_REPAIR.md). The full goal stays active.

The new argument establishes conditional complete-state agreement between the
73-colony window and the corresponding full lower ring at burst time. Ordinary
radius-seven locality then extends that agreement through the saved checkpoint
116418 physical ticks later, in seven complete central colonies. The light cone
is empty before commit. Final noisy commit and subsequent repair still do not
have a complete lower-ring embedding proof.

## Dependence argument

`certify_retimed_holder_prefix_dependence.py` loads and verifies the existing
noiseless composition's source hashes, actual packet schedule and instruction
refinements. It interprets timed reads, writes and packet deliveries as sets of
integer source-colony offsets. It never supplies states to an evolving world.

Every initial MEM word, including arbitrary scratch, starts with owner zero.
NonMEM Data starts zero. Reset clears exactly the marked cells, vote takes the
union of its three operands, and every ALU operation conservatively takes the
union of its inputs. META depends on its entire query into the fixed ROM.
Delivery translates source-relative owners into destination-relative owners;
there is no finite-ring aliasing in this calculation. All 6478 packet deliveries
and every timed event in all six phases are checked. At every write and read,
the source set stays in -7 through 7. Info remains locally sourced until commit.

This bounds intermediate controller state as well as completed instruction
results. Its registers and data-dependent META path depend only on operands
already read in the same colony; PC/phase progression, routing metadata and
completed instruction times have the existing physical refinement. No controller
is omitted because it happens to be between instruction boundaries.

The physical join uses the existing canonical-context identity: flags cannot
alter coherent Data/controllers on canonical geometry, and no mail is live
during forcing. Capture uses the checked local five-buffer deliveries. **Initial
Signals must be zero** for this bank-only statement. They remain zero except
for those captured buffer primaries. Flags/Wf have cleared by Age 1230098304.
Thus every logical procedure and Signal in the late precommit interval depends
within seven initial colonies. A whole raw colony includes replicas belonging
to its immediate neighbors, giving the conservative bound of eight colonies.
All 154 raw fields are explicitly partitioned into these cases.

This is an inspectable conditional proof composition with executable finite
checks, not a proof-assistant result or an independent replay of the GPU prefix.
The physical instruction, mail, context and clearing premises remain those of
[the noiseless induction](RETIMED_NOISELESS_MACROSTEP.md). Gray's specialized
hard-wiring/ProgramBit projection and Gacs 9.2–9.3 remain the construction basis;
this dependence bound is a property checked for our fixed candidate.

## Matching the actual inherited entry

`audit_retimed_holder_prefix_embedding.py` checks all 723868 inherited bank words
against the complete 32768-colony bank source. It checks the complete zero initial
controller arrays, counts, flags, Signals and clock. Across the full source,
5046272 upper raw words are typed, normalized to the fixed ROM, and equal the
encoded Info. The full initial Signal array is zero.

The 73 selected upper positions are contiguous. Therefore complete raw colonies
8 through 64 (57 colonies) have the required eight-colony initial context at
burst Age 1232619428. In particular, the candidate enclosing cuts at 35Q and 39Q
have matching noiseless initial collars under the descriptor-semantics argument.
This is stronger than checking only gathered votes, but still conditional on the
physical executor/refinement connection for the saved GPU prefix.

## What ordinary locality then guarantees

Both executions receive the same translated 8404 replacement marks, with no
other faults. If their complete states initially agree on [L,R), radius-seven
locality gives agreement on [L+7t,R-7t) after t ticks, including when faults corrupt
geometry or controllers. Here [L,R)=[8Q,65Q).

| Saved stage | Ticks since burst start | Complete matching window colonies |
|---|---:|---|
| Burst end | 34 | 9–63 |
| Quiet recovery end | 16418 | 12–60 |
| First macro checkpoint | 20514 | 13–59 |
| Second macro checkpoint | 116418 | 33–39 |
| Later evaluator stop and commit | 792380572 and later | None certified by this cone |

At the second checkpoint the exact interval is [1077070,1314994). The complete
stored state has 73 heads, all controller words outside ROM zero and all mail
zero. Signals are zero around both proposed cuts, whose required input collars
fit inside that matching interval. Signals are **not globally zero**: 30 raw
Signal words remain in edge colonies 0,1,2,70,71,72. Those are retained explicitly.
The cut's local hypotheses are checked at this time only, not proved invariant.

## Evidence, failures and resource costs

Accepted receipts under `figs/fixed_rule/`:

- `retimed_holder_prefix_dependence_v2.json`: 4.311976 s, 123352 KiB process RSS.
- `retimed_holder_prefix_embedding_v3.json`: 4.590282 s, 2466208 KiB process RSS;
  4 GiB watchdog, terminal zero. Large input hashing is streamed.
- `retimed_holder_embedding_cones_v2.json`: 2.554205 s, 438948 KiB process RSS;
  2 GiB watchdog, terminal zero.
- `retimed_holder_prefix_embedding_tests_v3_watch.json`: eight focused tests pass in 1.491 s;
  watch 2.090091 s, 74976 KiB sampled RSS. Exact commands are in the watches.

The first dependence receipt reports a passing abstract calculation but omitted
the zero-initial-Signal restriction from its prose claim. It is **superseded and
not accepted as that theorem**. Its exact source is archived. A complete scalar
rule test exhibits a retained Signal at a noncapture primary with identical
procedure words, demonstrating why bank equality alone is insufficient under
unrestricted Signals.

The entry witness twice hit its conservative 2 GiB watchdog: first while using
whole-file hashing, then while accessing the full mapped bank after switching to
streaming hashing. Both processes were authoritatively killed before the next
attempt. The same corrected source passed with a 4 GiB cap, well below 40 GB.
The first cone/collar check rejected the false global-zero-Signal hypothesis.
Its source, log and terminal nonzero watch are preserved; the accepted version
checks only the justified local collars and reports the nonzero edge Signals.

The tests check complete controller accounting, owner translations that would
expose forwarded radius-14 data, rejected omitted controller/Signal entry state,
the retained-Signal witness, raw replica halos and wraparound, and exhaustive
small-line light-cone erosion. They also reject using this finite cone to claim
the billion-tick commit.

Final index: `figs/fixed_rule/retimed_holder_prefix_embedding_evidence_v1.json`.
No GPU allocation, shared source change, other-agent job change or overwrite of
prior evidence occurred.

## Remaining boundary work

Prove persistence of suitable local collars from the embedded checkpoint through
commit, including their full-ring exterior inputs. Establish confinement of the
actual fault influence through the preceding interval; the saved local agreement
does not imply that the full-ring exterior remained noiseless. The one-step cut
certificate and a zero-mail check at one time do not by themselves supply this
induction. Then join the committed relation to subsequent physical periods.
General amplification, thresholds, robust caps, Q/U optimization, depth three and
the existing Flag2/SimBit source-fidelity issues remain open.
