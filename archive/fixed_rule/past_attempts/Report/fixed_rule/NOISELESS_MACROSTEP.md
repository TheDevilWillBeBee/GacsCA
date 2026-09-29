# Noiseless macrostep: composition at descriptor semantics

2026-09-26. The complete period now has a certificate-assisted mathematical
induction, stated below. Its finite interfaces, alphabet closure and open-lattice
Data identity have executable checks. This is a noiseless self-simulation result
for the current fixed candidate, **not completion of the Gács/Gray project**.
It is not a proof-assistant development or a new literal U-tick trace. Backend
agreement still has the scope of its existing differential execution audits.

## Precise statement and rule

Here F means the complete executable word descriptor returned by
`small_holder_rule.self_description()`, using unsigned 64-bit word operations.
Its digest is `af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`.
The scalar Python rule is a separately audited reference for that descriptor;
this proof does not silently assert universal equivalence of every backend.

Let pi remove the 49 static metadata words, and iota regenerate them from the
cell's Address and the single fixed ROM. Define G = pi F iota, applying iota
pointwise to the radius-seven neighborhood. G has 105 words / 2704 bits, with
Q=32768 and U=4294967296. Nothing here depends on hierarchy depth. The ROM digest
is `c59c72abe15729e4848ce549b31f1faec63465f16da2c717f0eb233fb1e7cbe4`.

Let E(y) be the raw physical block relation defined in
[PERIOD_ENTRY_AND_TIMED_DATAFLOW.md](PERIOD_ENTRY_AND_TIMED_DATAFLOW.md) and
`small_holder_period_relation.py`: canonical Address, uniform Age zero, actual
metadata, coherent Data, Info equal to all 154 words of iota(y), zero physical
heads/controllers/mail/flags/Wf, zero non-MEM Data, arbitrary other MEM scratch
and arbitrary retained Signals. Upper y is any typed projected configuration;
its controllers may be active and its geometry need not be canonical.

For an infinite lattice, or any ring of N upper cells with N>=1, the statement is

```
F^U(E(y)) is contained in E(G(y)).
```

All 154 descriptor outputs fit their declared widths on all typed raw inputs.
The ten hop-counter outputs need a guarded-decrement bound: when the decrement
branch is selected, its unsigned operand is nonzero, so subtracting one cannot
wrap. The new abstraction recognizes the exact Boolean selector lowering and
that nonzero factor before tightening a bound. It never truncates an output or
changes the descriptor. All 229376 fixed-ROM/fallback values were separately
checked against their seven declared widths. Thus normalization also returns a
typed cell for every Address, not just those in the sampled executions.

## Physical induction

The induction concerns the literal synchronous F trajectory. Symbolic memory
and packet records below are proof interpretations of that trajectory, never
host replacements for a transition.

1. **Entry and persistent structure.** E(y) satisfies the canonical structural
   domain in [STRUCTURAL_INVARIANT.md](STRUCTURAL_INVARIANT.md). Its all-clock
   preservation keeps static metadata and canonical geometry, coherent
   Data/head/controllers, zero inactive controllers, and at most one head in
   each fixed core. Core separation makes every local head case covered.
   At old Age zero the quiet-reset lemma applies: all scratch is cleared, Info
   is retained, and the unique first record bootstraps the actual first entry.
   The ROM layout check includes tail MEM and excludes non-MEM writes.

2. **Instruction and transport induction.** Suppose a scheduled instruction
   entry has the interpreted Data and controller. Dispatch and ordinary/META
   path certificates give the complete controller path, Data accesses and
   successor entry. All actual paths fit their checked clock intervals; all
   META queries are 15-bit, including descriptor-computed output Addresses.
   The arbitrary-context lemma preserves the procedure projection of those
   formerly zero-context leaves. The all-clock raw-mail factorization adds
   exact delivery, overwrite and send behavior; it does not assume away mail.
   Every flight may have arbitrary Data at sites it does not read.
   The timed Data checker supplies the values at each separate physical read,
   write and SEND birth. Its equality with the batch calculation covers
   aliased operands and intervening deliveries. Packet-flight induction keeps
   each payload and decrements hops at actual colony boundaries. The schedule
   excludes same-track collisions and controller accesses at/after delivery.
   All live packets finish before flag forcing, when holder masks are zero.
   This establishes the next instruction entry and the next packet event,
   completing mutual induction over their actual physical times. Durations
   are independent of payload, including the padded META paths, so colonies
   retain the common schedule used by the collision check.

3. **Three gathers and quiet barriers.** Each gather leaves its head halted
   and every packet consumed. Inactive-controller closure then makes all
   controllers zero. Consumed packets leave all mail words zero, not merely
   invalid valid-bits. The quiet-barrier lemma bridges the remaining ticks and
   the next reset. No other reset/vote/commit lies in those gaps. Each gather
   normalizes its source Info and fills all 15 raw neighbor histories. The
   earlier histories survive subsequent resets. The open-lattice identity
   below establishes these histories independently of periodic input aliasing.
   At the first vote the three copies of each word agree, so old-Data voting
   returns that word and bootstraps the actual evaluation entry.

4. **Complete evaluation and capture.** The instruction induction applies to
   the entire F descriptor, including controller and transport transitions,
   followed by executed META regeneration of output metadata. Hold is therefore
   iota(G(y)). Ten final zero-hop SENDs place its Flag2 and Flag1 values in the
   respective five-buffer groups. Their common sources remain unchanged, all
   deliveries finish before the capture's old Age 1979711487, and no later
   access or intervening clock override changes those buffers. The exact
   capture rule reads their old corrected Data; the following Signal votes
   retain the common bits. Arbitrary unrelated retained Signals are permitted.

5. **Forcing, clearing and the final computation.** No live packet or SEND
   occurs in or after the Wf forcing interval. Canonical geometry prevents
   flag-driven Data/controller clearing; the context lemma therefore also
   covers the precommit HALT while flags may be nonzero. Wf becomes zero at
   Age 2147549184. Directed flag ancestry clears both flags by 2147581952,
   strictly before the final reset/vote at 2281701376. The simultaneous vote
   uses old Data and overrides reset clearing. Checked history reset marks
   preserve its operands, so the final evaluation again returns iota(G(y)).
   It halts at 3449674225, with no packets. Quiet evolution preserves Hold
   until commit at old Age U-1.

6. **Commit restores the entire relation.** Every marked Info cell copies its
   old adjacent Hold; the checked Info and Hold sets are disjoint and inside
   the colony. The resulting Info is exactly iota(G(y)), on all 154 fields.
   Age wraps to zero. Metadata/canonical Address and Data coherence persist;
   heads, every controller word, every mail word, flags and Wf are zero.
   Non-MEM Data stays zero: reset/commit/vote marks, executed writes and packet
   targets act only on actual MEM records, including the first record.
   Remaining MEM scratch and Signals are allowed by E. No extra reset or host
   cleanup is counted in these U transitions. This proves the stated inclusion.

The local results used in steps 2–5 are linked from
[MAIL_FACTORIZATION.md](MAIL_FACTORIZATION.md), [ALL_CLOCK_MAIL.md](ALL_CLOCK_MAIL.md),
[PROCEDURE_CONTEXT_AND_BARRIERS.md](PROCEDURE_CONTEXT_AND_BARRIERS.md),
[SIGNAL_FLAG_BOUNDARIES.md](SIGNAL_FLAG_BOUNDARIES.md), and the entry/timed report.
Their old stand-alone limitations remain accurate; the induction above supplies
composition rather than retroactively changing those historical certificates.
In particular, context erasure is not iterated as a different physical rule.

## Open lattice and arbitrary ring size

`certify_small_holder_open_dataflow.py` uses independent source labels -7 through
7 and integer destinations. During gathers none of those source programs
accesses any foreign incoming delivery target. Omitted incoming deliveries
therefore cannot affect its reads or output. Only deliveries to the central
colony need be installed. All central histories match the independent inputs;
all later packets have zero colony hops. Both central complete evaluations and
commit then match the normalized full descriptor. The checker ignores the old
batch interpreter's wrapped destination field; a mutation test scrambles every
such field and still obtains the same identity. Reversing real direction fails.

Translate this all-input central identity to colony k. On an N-colony ring,
substitute input j by y[(k+j) mod N]. Aliased inputs are valid substitutions,
including N<15. The independent modulo-Q collision check is conservative over
all colony translations. Equal-PC packets from distinct colonies remain
Q-spaced, hence distinct modulo NQ; different-PC overlaps are already excluded.
Hop counts record each boundary crossing, including repeated ring laps.
Thus neither timing nor the Data identity requires a 15-colony ring.

## Self-reference, repeated periods and finite depth

Along E trajectories physical metadata remains normalized, so iota pi is the
identity there. Projecting the inclusion gives the same block simulation for
G by G. Reapply it after each period: retained scratch and Signals require no
external reset. Composing the relation d times gives a noiseless decoded G step
after U^d physical ticks, on blocks of Q^d cells, for every fixed finite d.
Depth changes the initial encoded configuration, never the physical state or
transition. This is a mathematical consequence, not an executed depth-two run.

The program computes the entire F descriptor, including its own evaluator's
controller transition, and regenerates its own static program records through
physical META reads. It is neither a test ROM nor an opcode-inventory argument.
Gray pp. 31–32 describes Address-based hard-wiring and ProgramBit projection,
then explicitly specializes away general-purpose simulation. Gacs sections
9.2–9.3 permits an identical or modified self-correcting rule. These are the
source rationale for G. They do not transfer the papers' noise theorems to this
candidate automatically.

A finite nested encoding stops at a chosen top configuration, which continues
under the same G. This needs no distinct top transition. It does not establish
a noise-stable quiescent cap; the previously observed cap Address defect is
still unresolved. Candidate-B Flag2 and voted-old-Signal D10 are still explicit
choices, not resolutions of the printed Flag2/SimBit ambiguities.

## Executable evidence and costs

All runs used a 512 MiB virtual-memory ceiling and one OpenBLAS thread. No GPU
job, CUDA artifact, shared source or historical dataset changed.

| New check | Result | Seconds | Peak host RSS (KiB) |
|---|---|---:|---:|
| Open-lattice Data flow | 45 access-disjointness checks; 154 central outputs | 2.107540 | 89704 |
| Period interfaces and descriptor typing, v2 | Six phases; all 154 widths; ten guarded decrements | 1.777067 | 94228 |
| Fixed-ROM typing | 229376 values; seven invalid-width mutations rejected | 1.307523 | 58436 |
| Focused tests | Seven passed | 2.704 | Not separately measured |

The failed v1 composition log and source snapshot remain preserved. Its plain
possible-bit abstraction lost the nonzero/decrement correlation and reported
possible 64-bit underflow for a three-bit counter. V2 proves that correlation;
it does not mask the result or alter the rule. Tests also reject missing/wrong
guards, overwide output, missing phase coverage, late halt, overwide META query,
late SEND allowance and reversed packet direction.

Commands below used `ulimit -v 524288` and `OPENBLAS_NUM_THREADS=1`, with matching
log files. Choose fresh output names for reruns.

```sh
python -m experiments.fixed_rule.certify_small_holder_open_dataflow --schedule figs/fixed_rule/small_holder_mail_schedule_v1.json --output figs/fixed_rule/small_holder_open_dataflow_v1.json
python -m experiments.fixed_rule.compose_small_holder_noiseless_period --output figs/fixed_rule/small_holder_noiseless_period_v2.json
python -m experiments.fixed_rule.certify_small_holder_rom_types --output figs/fixed_rule/small_holder_rom_types_v1.json
python -m unittest discover -s tests/fixed_rule -p test_small_holder_noiseless_period.py -v
```

## Practical execution and remaining objective

This proof makes no performance claim. One dense packed projected buffer for
Q^2 physical cells would occupy 338 GiB, before a second time buffer; one such
macrostep represents U^2=2^64 literal ticks. This is plainly outside a direct
80 GB A100 run. Reachable-state compression and rigorously refined event
execution may reduce the cost; Q/U optimization is still necessary. U<=128Q
is not imposed, and no artificial colony padding is justified by that ratio.

Next audit the current physical event backend against this complete period
relation, then choose and measure a practical depth-two execution strategy.
A closed noiseless relation alone does not validate skipped transitions in a
backend. Full upper work periods at depth two, repair after faults at multiple
levels, noise suppression, source-faithful amplification and robust cap behavior
remain required. The goal remains active and incomplete.

New manifest SHA-256 values:

- `small_holder_open_dataflow_v1.json`: `36c62c5951a67ba4cea2d4dad1d47d0c88936af706ed117d8c66a93bcd96ad59`
- `small_holder_noiseless_period_v2.json`: `8348e8c7ddeddbb0982757ed981b74b701f8c90b3f9527619a054c2a6c36c8d2`
- `small_holder_rom_types_v1.json`: `51c4a3f9d573dafe2c208fdb7c4b60c8351553d72e8c3f555f0332742682154b`
