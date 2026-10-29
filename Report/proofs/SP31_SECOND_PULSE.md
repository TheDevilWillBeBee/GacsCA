# SP31: the actual second pulse shrinks the same fault by another4Q

This uses unchanged isolated F31, Q1024/U475136/TF278401, its actual own
ROM and the same original-c16 real2 history as [J225](SP31_FIRST_PULSE.md).
There is no rule, constant or G17 change. The result is a second native
pulse and boundary theorem for that history, **not general repair or
a positive iid threshold**.

## Exact statement

Start from J225's intact E31(z), arbitrary upper Info and one native-only
dense16Q row error, with no later errors. At t=U+TF J229/J232 give the
quiet native template T(135,146), the exact complete Flag1 source pattern
and an actual seven-bit Flag2 source enclosure. Then, at

    t=U+TF+6144=759681,

the actual native fields are exactly

    GF=(x+512) modQ on[142Q-512,149Q), x modQ elsewhere;
    Flag1=1 on[141Q,142Q-512) and[149Q-512,149Q), 0 elsewhere;
    Age=the common legal clock TF+6144;
    native Flag2/Workspace1/Workspace2=0 everywhere.

Thus the second pulse ends at T(142,149). Wrong GF has width7680=7.5Q,
down from11776=11.5Q, another decrease4096=4Q. Its left edge advances7Q
and its right edge3Q. These native fields persist with the correct clock
to the computed boundary2U, where807 other private bits and all four
physical Info signal/alias tracks reset to0. Other Info and the full
upper successor at2U are uncharacterized. There is no third-pulse or
eventual-repair assertion.

## 1. Actual start and all source assignments — previously proved

[J229](SP31_SECOND_SOURCE_ENCLOSURE.md) derives the full second Flag1
pattern from the actual first-boundary banks and actual next gathers:
MF509=1 precisely135..145; MF1021=1 precisely118..133 and146..148;
every other Flag1 source is0. [J232](SP31_PROTECTED_FOREIGN_AGE_BANK.md)
derives eight actual protected Age1 banks and all eleven complete
foreign F2=0 outputs. Only these seven Flag2 sources remain free:

    MF3 at124,130,131,132,133,134; MF515 at145.

Every other Flag2 source is0. All four command-track Info votes are
coherent at the actual source time. No independent upper tape, future
Workspace value or later physical error is selected. The unknown votes
may be correlated, but each is binary, so the actual state belongs to
one of the128 assignments. Exhausting this superset does not require
proving individual masks reachable.

The first-boundary reset and quiet native lemma establish the same
T(135,146) until that source time. Its input TF-1 is outside the Workspace
guard, so the native Workspace/Flag2 values in the initial quotient row
are0. Physical time is U+TF; the common clock is TF, not U+TF as a raw
packed clock word.

## 2. Exact infinite-line quotient and128 executions — proved

J225's closed binary-adjusted-GF/common-clock native/voted-Info quotient
applies verbatim. All odd votes and fallback choices retain the two GF
labels and common legal clock. Native source3 is false. Both native
Flag2 and Workspace flags evolve by their literal full equations;
the18-to-seven source reduction does not suppress subsequent Flag2
activity. Each Info source undergoes the actual five-holder keep-vote
erasure. There are no intervening special Info writes or commits in the
6144-update window, and private execution fields cannot force native
maintenance in F31. Normal other Info is irrelevant to this projection.

The unchanged [J231 wrapper](unregistered_sp31_second_pulse/sp31_second_enclosure_cases.c)
and frozen included `sp31_two_flag2_sources.c` supply the exact second
native template and full Flag1 pattern. The128-mask driver uses

    diagnostic18_mask=(seven_mask &63) | ((seven_mask >>6)<<17).

Bits0..5 encode MF3 in the listed order; bit6 encodes MF515(145).
All other eleven diagnostic Flag2 bits are0. It runs the existing
byte-pinned diagnostic binary, changing no equation or event engine.

The exact infinite-line event proof in J225 section3 applies: cuts at
every native endpoint shifted-37..37 and both GF phases' guard boundaries
shifted-8..8 make the entire native stencil and every inside/end predicate
constant on each interval. A guarded Info read has a single fixed source
primary there. Endpoint tuples/guards/outputs are explicitly checked,
capacity overruns abort, and the zero exterior is closed. This is a
finite exact evaluation on Z, not a finite ring with forced boundaries,
or endpoint sampling of varying intervals.

Every one of the128 complete6145-row traces has final native segments

    [144384,144896,2], [144896,152064,1], [152064,152576,3],

with bit0 wrong GF and bit1 Flag1. There are no other nonzero native
segments; F2/WF1/WF2 are0. The checker verifies all trace hashes, rows,
initial and final summaries, full endpoint segments and Info lists,
stderr/exit receipts and exact mask mapping. It independently rebuilds
the identical binary and replays all rows for the two extreme seven-bit
masks0 and127. Intermediate GF holes and Flag2 activity are retained,
not replaced by a solid-interval or Flag2-zero assumption. The retained
receipt reports each case's exact event count and maximum segment count.

The actual second-source state is one of those128 quotient states. The
closed-factor induction therefore transfers their common endpoint to
the **same actual physical error history**, for every allowed original
upper Info payload and its resulting unknown/correlated votes. This is
the second native pulse theorem, not a measured claim extrapolated to
unlisted source assignments.

## 3. Actual second native boundary — proved by composition

The endpoint is again the sharp quiet template of J225/J229, with widely
separated edges,512-site Flag1 strips, a common legal clock and native
F2/Workspace flags0. The source window is closed after6144 updates.
The literal quiet native lemma advances it to2U, unaffected by arbitrary
private evolution because native service_force=0 and all native/workspace
dependencies retain this quiet projection. At input2U-1 computed GF
equals refined self-GF. The all-raw807 reset and five-copy masked-Hold
Info identities of J223 consequently apply globally. The actual mask
excludes3/509/515/1021 for either GF phase; those tracks are0 at2U.
This proves the stated boundary result. QED.

## Limits

The boundary is not proved to be an encoding of a complete upper
configuration; normal Info and the late Age/H2/other banks are not derived
here. The single-exception GF bank of J227 was specific to the first
boundary. No assertion that it persists to2U follows from the native
endpoint, nor that the third sources reproduce either earlier enclosure.
An originally partial interpreter and retained old bank words require
actual next-period tracking. A third shrinking pulse, an arbitrary-island
eroder, repair with surrounding E0, the upper error map, all-time iid
memory and a smallest sufficient rule/constant change remain unproved.

The separate abstract late-suffix probe with arbitrary earlier registers/
scratch does not prove constant recovered-frame Age outputs, even under
its stronger read-only-zero hypotheses. Its unresolved symbolic normal
forms are not concrete physical counterexamples. No source value or
repair conclusion is borrowed from that probe.

| Step | Status | Scope |
| --- | --- | --- |
| Actual second native state/full F1/seven-bit F2 enclosure | previously proved arguments apply | J225/J229/J232, same history/all initial Info |
| Closed native/Info quotient and event partition | previously proved argument applies verbatim | J225 equations with different initial assignment |
| All128 exact6144-update endpoints | proved finite certificate | Complete source enclosure, literal Info erasures and native F2/WF retained |
| Actual second native pulse/another4Q shrink | proved by composition | Same specified original-real2 history |
| Quiet continuation/2U native fields and807/alias reset | proved | No full normal-Info upper reconstruction |
| Abstract suffix/recovered Age conclusions from it | unproved | Free seed reachability unproved; nonconstant terms are not failures |
| Third banks/pulse/general higher repair/iid/minimum | unproved | No reliability or Gray/G17 refutation |
