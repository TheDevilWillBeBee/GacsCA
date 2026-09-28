# All eight retained noisy macrosteps resolved

2026-09-28. The fixed-rule goal remains active. All eight high-rate histories
from the unfiltered local-noise pilot now reach an actual commit. **Case1 gives
the correct complete upper transition; the other seven fail.** This improves the
earlier classification: none had completely rejoined the healthy raw state, but
one nevertheless computes the correct decoded macrostep. No fault history was
discarded or repaired by replacing its state.

## Execution changes, with the same physical rule

The existing sparse resident executor stores every Data word in its MEM bank
and every active raw controller/Signal/mail word in sorted records. Its late
Signal guard admitted only patterns near colony ends. The new
`compact16_holder_late_events.py` admits arbitrary **coherent, stationary** Signal
patterns after the last reset/vote/capture/Wf event. A same-time adapter checks
all154raw words, canonical Address/uniform legal Age, zero flags/Wf, complete
procedure/Signal coherence, zero non-MEM Data and the64record capacity. It
restores and re-renders the entire state exactly before any transition.

The local transition, controller-event computations, physical alphabet, ROM and
Q/U are unchanged. The sole CUDA source change in this first extension is the
Signal acceptance guard. It checks both stored and absent records, including
cross-colony and periodic seams. No new opcode, depth parameter or controller
hardware is introduced. Host code initializes/reads state and schedules physical
time; it does not execute a simulated upper transition.

A BDD certificate proves the late coherent-Signal identity for every old Age
502000001..1073741823, every canonical Address, arbitrary underlying Signal bits
and arbitrary Data:123independent bits,5458nodes,0.274874s. A structural traversal
of the complete F descriptor finds **zero old-Signal dependencies in all90raw
procedure outputs**. The late interval excludes future capture/Wf forcing.
The generated resident source is checked to differ only in its acceptance guard.
These facts justify admitting the broader stationary patterns without changing
controller dynamics. Five testsPASS9.206s: all8saved states, full raw parity,
inactive/commit boundaries, seam Signals, two-head reflection and domain rejection.

The first all-case attempt hit its240s wall cap in case4 because the old
transport shortcut rejects multiple heads. Its source/log/watchdog are retained;
the process was confirmed terminal before another run started. No complete
artifact was published for that attempt.

`compact16_holder_late_multi_events.py` retains all individual instruction,
waiting and reflection distance bounds and adds pairwise interaction bounds.
For heads at a<b with constant velocities va,vb in{-1,0,1}, only va>vb can close
the gap. The safe transport length is bounded by max(0,floor((b-a-2)/(va-vb))).
At every skipped input tick a closing pair remains outside the radius-one
interaction zone. Equal-velocity transport preserves distinct locations;
diverging heads separate. Full local ticks handle reflection, instruction events
and collisions. Existing non-head residue and individual event guards remain.
This is a conservative scheduling bound, not a changed transition.

Three testsPASS33.700s: two/three heads, adjacent parallel motion, odd/even gaps,
reflections, and the actual damaged two-head state over16384ticks against the
complete factored literal kernel. A deliberately unsafe build omitting the pair
bound leaves two heads where the literal rule leaves one; the mutation is
detected. That build is used only as a negative test. The pair bound is also
applied conservatively in inactive intervals; some frozen opposing-head states
can therefore lose acceleration, although correctness is preserved. This did
not obstruct these retained outcomes.

The second run completed seven cases and saved case4 atAge514889820 when the
mail-free domain correctly rejected the next transition. Its `passed:false`
receipt means incomplete coverage, despite exit0. The exact saved state has a
head at2862, phaseTRANSMIT, PC98, ra2862, rb1568, rd3, and another damaged head
at2880. One full local tick emits an lp packet at2862 with target1568,
Data15386914758072594124 and remaining1; the first head advances to2863/PC99.

`compact16_holder_late_mail_events.py` removes only the two late mail-rejection
guards. Existing complete packet transitions and edge/delivery transport bounds
remain. Single-controller independent batches still reject packets; synchronous
sparse execution handles them. The adapter checks every raw mail width/copy and
uploads all mail before verifying exact raw equality. A temporary zero-mail
array is used solely to reuse the remaining-domain validator and allocate storage;
it is never evolved or returned as the actual state. Three testsPASS43.805s:
the real emission followed by32768ticks against full literal G; cross-colony
delivery, opposing packets and controller-write priority; invalid packet residue
evolution; and rejection of bad packet widths or replicas.

The saved case4 then resumes at the same clock and reaches commit with all
packets retained. All variants remain restricted to the current late period,
coherent procedures/Signals, zero flags/Wf, finite sparse capacity and zero
non-MEM Data. They are not arbitrary noisy-state executors. The earlier complete
literal/canonical executors supply the transition references outside these
event domains. No universal compiler/event-equivalence proof is claimed.

## Actual decoded results

The target is the complete scalar G transition of the original active top state;
the independently executed healthy terminal fixture agrees with it. Each case
executes its actual commit before decoding all154Info words. All five physical
Info replicas agree on each decoded word.

|Case|Correct complete macrostep?|Raw differing words|Projected differing words|Projected width validity|
|---|---|---:|---:|---|
|0|No|49|33|Valid|
|1|Yes|0|0|Valid|
|2|No|49|33|Valid|
|3|No|49|33|Valid|
|4|No|49|33|Valid|
|5|No|49|33|Valid|
|6|No|19|19|Invalid Signal word|
|7|No|49|33|Valid|

Cases0/2/3/4/5/7 remain wrong after discarding metadata. Their raw metadata also
fails the fixed-projection consistency check. Case6 commits Signal32212254792
into a5bit simulated field; the decoder rejects it. This value is preserved
unmasked in the evidence. Its other errors include controller PC/value/Data,
Age502131225 instead of502000101, and wrong Flag1/Flag2. Counting19projected
word differences is a diagnostic comparison, not accepting an invalid G state.
The six width-valid failures have33incorrect mutable fields, including Age0
instead of502000101. Case1 is a genuine complete decoded success even though
its lower raw scratch state had not fully rejoined at the prior deadline.

This is the resolution of the eight previously selected high-rate failures
(p=.1 for16ticks on65sites). It is not a new random sample, a whole-lattice
noise experiment, a threshold estimate or a full-period independent-noise rate.
The p=.005/.02 pilot recoveries and conditional sparse repair lemma remain
separate evidence. No claim is made that the construction should tolerate this
particular dense burst.

## Measurements and independent audit

The revised all-case run took38.079468s/watch38.532642s, peak sampled RSS961284KiB.
Seven cases completed; case4 was retained at its verified mail boundary. Each
case has its own compressed complete-state checkpoint and journal entry, so a
later interruption cannot erase earlier completed outcomes. Case4 continuation
took24.277152s/watch24.694809s,388340KiB RSS. Explicit event buffers are2097776
bytes per one-colony world, with at most27616additional bytes for staged Data.
GPU context/compiler overhead is excluded. The40GB host allowance was respected;
no shared source/job/build/dataset was modified.

The independent audit checks the active/inactive boundary, precommit boundary
and actual commit of all8cases against full native G, plus the case4 emission.
It checks every physical Info output with the independent scalar rule
(1232complete outputs), all five replicas, and the unmasked projected widths.
Cases3/7agree word-for-word with the earlier separately guarded headless suffix.
68,124,672raw words checked. Audit12.383913s/watch12.675508s,182824KiB RSS, PASS.
Long event intervals are not wholly replayed tick-by-tick with another backend;
the documented domain/factorization arguments and finite parity checks support
their acceleration.

Eleven tests passed overall. The Signal certificate and final audit pass.
The timeout and incomplete seven-case receipt are retained as such, not relabeled
as successful all-case runs. Final combined coverage comes from the seven commits
plus the exact saved case4 continuation and the all-eight audit.

```sh
FIXED_RULE_GPU_TESTS=1 python -m unittest tests.fixed_rule.test_compact16_holder_late_events -v
python -m experiments.fixed_rule.prove_compact16_holder_stationary_signals
FIXED_RULE_GPU_TESTS=1 python -m unittest tests.fixed_rule.test_compact16_holder_late_multi_events -v
python -m experiments.fixed_rule.compact16_holder_all_noise_macrosteps_v2
FIXED_RULE_GPU_TESTS=1 python -m unittest tests.fixed_rule.test_compact16_holder_late_mail_events -v
python -m experiments.fixed_rule.compact16_holder_mail_macrostep
python -m experiments.fixed_rule.audit_compact16_holder_all_noise_macrosteps
```

All listed commands exit0; the fourth intentionally records `passed:false` for
its retained case4 domain boundary. The older `compact16_holder_all_noise_macrosteps`
attempt has watchdog returncode-9, wall-time exceeded. Evidence manifest:
`figs/fixed_rule/compact16_holder_all_macrosteps_evidence_v1.json`, preserving
all984previous files and nine external banks alongside the new artifacts.

## Next work

Follow the committed states into the next work period, explicitly preserving or
rejecting malformed simulated encodings. Use multiple simulated colonies to test
repair by healthy simulated neighbors; the one-periodic-top fixture cannot
establish cross-level repair of these failures. Broaden noise support/time only
with failures and decoder-domain violations retained. An efficient inactive
interval rule can remove the conservative frozen-head transport limitation.

The physical construction remains Q16384/U2^30/radius7,154words4090bits,
descriptor53f7adbf...fb846b and ROM4d055889...f48b32. Gray31–32 specialized
hard-wiring and Gács9.2–9.3 modified self-correcting simulation remain source
basis. General amplification, arbitrary malformed-code/geometry repair, reliable
finite caps, sustained depth-two top arithmetic and depth3 remain open. Known
Flag2/SimBit qualifications remain. This milestone improves actual execution and
measurement; it does not complete the full self-simulation goal.
