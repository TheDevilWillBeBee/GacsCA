# SP28 short-window pulses: an exact Info/native factor

This concerns the already explicit force durations Q and2Q of
[the short-window family](proposed_sparse_short_epoch_duration.py), at
Q1024/U475136/TF278401. No additional equation change is proposed here.
Matching own programmes and the reliability theorem remain unproved.
The [C factor](native_address_info_factor.c) and
[checker](check_info_native_factor.py) retain the actual Info signal instead
of replacing Workspace.Flag1 by an independent zero/maximum control.

## Exact factor theorem (proved)

At clock TF, let every raw GF be x modQ or(x+512) modQ, with arbitrary
binary labels L(x). All raw clocks are the common legal TF clock.
Flag1/2 may be arbitrary. Raw Workspace flags, packet/code validities
and backward pressure are initially0; invalid headers may be arbitrary.
Every private field, raw Info copy and instruction input may be arbitrary.
There are no later errors. Consider the6144 updates with input clocks
TF,...,TF+6143. The theorem is on Z; it does not assume spatial periodicity.

For logical position y, let M(y,t) be the majority of its five raw Info
holders. Retain M only at residues509 and1021 modQ. The entire native
GF/Age/Flag1/Flag2/WorkspaceFlag1 history and the packet/code/backward
history during this interval are determined by the initial native data,
these two M tracks and the following exact recurrence. All omitted
private data and instruction inputs have no further influence.

1. The native/header updates are the literal one-step substitutions in
   [the earlier prefix proof](SP28_SHORT_EPOCH_ENCLOSURE_GAP.md), items1–6.
   Use the actual raw WF1 values and actual native flags, not their
   independent monotone bounds. The selector is evaluated exactly;
   the first enclosing ambiguity at2064/2368 is not a stopping condition
   for this factor.
2. Put

       K(x,t) = NOT(F1_new(x,t) AND (L_new(x,t) != L(x,t))).

   Then, for each retained logical primary,

       M(y,t+1) = M(y,t) AND [sum_{s=-2}^2 K(y-s,t) >= 3].

3. Write G(x,t+1)=(x+512 L_new(x,t)) modQ and
   y=x+(Q−3)−G(x,t+1). The actual Workspace.Flag1 output is

       [G(x,t+1) >= Q−5] AND [t−TF < 2Q] AND M(y,t).

   Whenever the first guard holds, y−x lies−2..2, and y has residue
   1021 if L_new=0 or509 if L_new=1. The source is the **old** Info
   majority. It is not multiplied by the reader's new wipe factor.

In particular each retained M is nonincreasing during this pulse, even
when its five initial raw copies disagree. Two initial full states with
the same native/header premises and these same initial majority tracks
have identical projected histories throughout the pulse.

## Proof

The two-GF-phase/common-clock closure proved for full SP28 applies to
arbitrary labels, not only a sharp island. Every five-word adjusted-GF
block has a binary majority. Its Age components agree. Joint refinement
and either directional selector preserve the two GF words, and both
native clock choices are the common clock. This proves closure on every
row, independently of the Info signal. The packed-clock increment is
legal on the stated interval.

All live packet/code records descend from the single TF birth, so their
counters agree. Their adjusted tags/positions, eligibility, first-lane
ties, packet priority, unchecked expired cohort and backward force are
exactly those in the earlier projection. Their derivation does not
require sharp GF boundaries or any private field. Native Flag1 uses the
actual WF1 vote. Hence items1–6 of that projection remain valid after the
earlier enclosure stops: uncertainty there concerned an unspecified
WF1 signal, not an absent native equation.

The actual generated SF source sets every Info copy to its old logical
five-copy vote times K, except at commit or the special Info update.
Their input clocks are U−1=475135 and T_sig=278400. Neither lies in
[TF,TF+6144). Thus, for any logical y and physical holder y−s,

    new_Info_s(y−s) = K(y−s,t) * M(y,t).

Taking the majority of these five outputs gives recurrence2. This is an
exact Boolean identity for all32 old-copy assignments and32 keep masks;
it does not require coherent old copies or infer an arbitrary-duration
claim from sampled trajectories. Equal low GF bits make the wipe Address
comparison precisely L_new!=L_old.

The literal WF1 equation in the same source uses the old `lv(info)`
vote at offset(Q−3)−computed_GF, with the last-five-GF and two-Q-clock
guards. It has no reader keep multiplier. Substituting the two GF words
gives recurrence3 and the two stated source residues. No other Info
primary, Hold, history, scratch, pending value or instruction input
enters this equation. Together the recurrences prove closed projection
and equality of projected histories by induction on all6144 updates.

## What this factor establishes and leaves open

It replaces the earlier independently imposed WF1 signal with its actual
vote/wipe data dependence. Prepared initial majority tracks are legitimate
full-state premises and can be realized by setting their five copies
coherently. They are not automatically the tracks delivered by an intact
recursive history at TF: the preceding special Info write can supply
different data, especially in a shifted colony.

The checker runs the exact factor for the earlier native island seed and
three explicit initial majority patterns: both tracks0; both tracks1;
or509=1 only inside the initial wrong-GF island with1021=0. These finite
runs are recorded as **measured** checks. A full pulse is evidence only
when its process terminates successfully and its complete snapshots are
retained. The earlier interrupted run has only snapshots through2368;
its receipt asserts no full-pulse result.

No all-period orbit, finite eroder, matching own programme or upper data
map is inferred here. In particular the missing history-to-initial-M
argument remains explicit. The factor supplies a concrete subsystem in
which that data argument can be tested and then proved; it is not an iid
threshold or a faithful Gray counterexample.

| Step | Status | Limit |
| --- | --- | --- |
| Two-Info-track/native/header factor during the6144-row pulse | proved | Two GF phases/common legal clock/sole simultaneous birth/no later errors |
| Info majority monotonicity and exact per-holder wipe rule | proved | No commit/special write during the interval; arbitrary initial copies |
| MF source routing and absence of reader wipe multiplier | proved from actual source | Old majority at509/1021, computed-GF/two-Q guards |
| Retained finite coupled trajectories | measured only | Prepared majority patterns; completion and snapshots required |
| Intact history supplies a particular M pattern; all-period repair/own programme/iid | unproved | Higher data-map and changed-duration compilation remain open |
