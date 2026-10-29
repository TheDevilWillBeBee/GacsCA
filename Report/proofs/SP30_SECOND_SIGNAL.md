# SP30: actual second signal, second shrinking pulse and next zero bank

This concerns the already changed own SP30 rule of J189, with its frozen
ROM and Q=1024, U=475136, TF=278401. There is **no additional rule,
programme, layout or constant change**. Use exactly J191's original
intact-start native overwrite, arbitrary initial upper Info payloads,
and no subsequent errors. No correct upper encoding is assumed after
the error. The conclusions are on the infinite line.

[Checker](check_signal_reservation1024_second_signal.py),
[receipt](../../figs/robustness/SP30_second_signal_certificate.json),
[own rule and commit mask](SP30_OWN_RULE.md),
[actual first signal](SP30_FIRST_SIGNAL.md),
[corrected native/Info factor and first pulse](SP30_NATIVE_PULSE.md),
[conditional zero-GF bank theorem](SP30_GF_BANK_CLOSURE.md).

## Exact statement

Write MF509(j), MF1021(j) for the retained logical Info majorities at
physical primaries jQ+509, jQ+1021. At computed time U+TF=753537,
native state is T(122,136), with common legal clock TF, and

    MF509(j) = 1 exactly for122<=j<=135;
    MF1021(j) = 1 forj=118,119,120 or136<=j<=146,
                q atj117, and0 elsewhere,

where q is the actual Boolean MF1021(117). Its value or independence
is not asserted. In particular MF509(121)=MF1021(135)=0. Thus the
actual second signal has **one free bit**, rather than SP29's three.

At computed time U+TF+6144=759681 the actual native/Info projection
is the same for both possible q values. Native state is T(116,128),
with wrong GF interval[118272,131072), width12800 instead of14848:
another decrease of2048=2Q. Flag1 occupies the two512-site strips
immediately preceding its edges. The other native/header/code/pressure
fields are zero. The two retained Info tracks are the receipt's common
final arrays. This does not specify all unobserved private fields.

At2U=950272, all807 non-Info private bits are reset and all650 Info copies
of primaries jQ+571..580, j115..127, are zero. In the third period,
at2U+TF=1228673, complete foreign frames supply MF509=1 for
h116..127. The full third signal, third pulse, entire upper data and
general eroder remain unproved.

## Reservation removes the two partial signals

The actual SP30 commit set is

    A30=([58,901) minus{509,515}) union{901,902,965}.

For every physical alias residue p in{3,509,515,1021}, every holder
slot s in{-2,-1,0,1,2} and either GF phase sigma in{0,512}, its
virtual primary residue is(p-s+sigma+s) modQ=(p+sigma) modQ,
which is outside A30. J189's literal forwarded-Hold commit identity
therefore gives all five Info copies zero at every such primary,
independently of old Hold or arbitrary other private values. This
conditional alias-reset lemma also allows different binary phases at
different holders. It needs the correct commit clock/native GF
interface. J195 supplies that interface at the actual first boundary.

Between that boundary and the next special write, the native template
is stationary, raw/refined/computed GF agree, and actual keep is1.
The actual Info equation carries these zeros: there is no intervening
commit or special write. This uses no SP29 late-suffix/data calculation;
ordinary Hold data can no longer be committed at these aliases.

At the special write's input Age TF-1, a primary changes only if its
virtual residue is3 or Q-3. For T(122,136), the five holders of each
relevant509/1021 primary have the same GF phase. Hence:

* jQ+509 is virtual Q-3 exactly forj122..135, supplied by the
  complete foreign frame with origin jQ-512; otherwise it is509.
* jQ+1021 is virtual Q-3 exactly forj<=120 orj>=136, supplied by
  a complete true frame; otherwise it is509.

The left partial primary121Q+509 is a-3, with a=124416. All its
holders are below a and its virtual residue is509. The right partial
primary135Q+1021 is b-3, with b=139264. All its holders are below b
in the foreign phase, again with virtual residue509. Neither receives
a special flag write; both retain zero. Five actual conditional-GF
Boolean identities, leaving clock/private/Info/flags/I inputs free,
check that a virtual509 primary carries its majority except for zero
at commit. Translation applies this same identity to both partials.

J195 already supplies Flag1one from every complete foreign frame
h122..135. This establishes the entire MF509 track. Determining the
true-frame Flag1 commands requires the actual source words below.

## Actual first-boundary native source words

The source argument of SP29_SECOND_SIGNAL_ENCLOSURE.md uses geometry,
the corrected projected first pulse and specific Hold stores. Those
parts are rechecked against **SP30's own** listing, ROM and full circuit;
the old full private history and late h2:77 suffix are not transferred.

The first-pulse all-row GF support has minimum left123456 and maximum
right147456, by J192's exact new projection. Normal GF holders59..68
and Flag1 holders88 in true frame120, including their radius32
refinement footprints, lie strictly left of that hull. Actual keep
is1 there throughout. Full working footprints of true framesj<=119
andj>=144 also lie outside the hull. Their gathers completed before
the pulse. The actual own-programme proof therefore continues in
those full frames; in frame120 it preserves the early GF/Flag1 Holds.
Arbitrary later private values in frame120 cannot manufacture another
Hold issue at those already finished destinations, by the one-kind
pending/unique-store argument. Flag1's post-gather mail gates cannot
alter the already captured programme inputs.

Seventy-five **new full-circuit** first-input cofactors, forj90..181
outside127..143, give GF=j modQ, Age1, WF1zero and Flag1one only
at124..126/144..146. Their captured GF is canonical unless the actual
speed-eight path crosses an original Flag1 strip, where mail is zero.
Input Age/flags/validities/pressure are the original upper zeros;
all unrelated fields and I are free. Outside this finite range no
requested path reaches a strip, so the canonical closure applies.

For recovered true framesj136..143, normal GF and F1 primaries start
foreign-phase and finish true-phase. All relevant initial Holds are
zero. The new listing and all90112 raw ROM keys at phases59..68/88
and their512-shift partners571..580/600 have exactly one Hold issue:

| Phase | Input issue | Materialization |
| --- | --- | --- |
| 59..68 | 276520..278398 | 276522..278400, before TF |
| 88 | 259870 | 259872, before TF |
| 571..580 | 345734..358739 | 345736..358741, after284545 |
| 600 | 357660 | 357662, after284545 |

Normal stores occur while those primaries have the foreign phase and
cannot address them. Opposite stores occur after they have recovered
the true phase and cannot address them. Neither phase has a Hold
issue during the pulse. J195's single-arrival, comb differences and
pending-kind induction exclude a spurious Hold issue from bitwise
voting or wipes. Zero Holds therefore survive to actual commit.

The source words at U are consequently:

| Upper source cells | GF | F1 | Age/WF1 |
| --- | --- | --- | --- |
| j<=119 | j modQ | 0 | 1/0 |
| 120 | 120 | 0 | free |
| 136..143 | 0 | 0 | free |
| j>=144 | j modQ | one exactly at144..146 | 1/0 |

These are only the fields used by the next Flag1 proof. No all-field
encoding or correct Age in the nine exceptional cells is assumed.

## Actual second true-frame commands

At U all807 private bits are freshly reset. Native T(122,136) stays
quiet until TF, with Flag1 strips[121Q,122Q-512) and[136Q-512,136Q).
The actual voted-mail majority/gate recurrence from J191 applies.
A direct read or capture returns the held source bit unless its
speed-eight route intersects a strip; then it returns zero. All
native phases59..90 needed here have the same strip-crossing predicate.
The three gathers precede the special write. Captured normal Info
values remain held during those gathers.

In a complete left true framej<=120, every source121 or larger is
erased; unblocked GF is canonical, F1zero, Age1/WF1zero except for
free Age/WF1 at120. New full-circuit cofactors forj83..120 give
Flag1one at118..120, zero atj<=116, with onlyj117 unspecified.
In a complete right true framej>=136, every source135 or smaller is
erased; unblocked GF/F1/Age/WF1 are exactly the source table above.
New cofactors forj136..183 give Flag1one precisely at136..146.
Every unrelated circuit field and I remains free. Forj<=82 orj>=184,
the maximum37-colony dependency distance excludes every exceptional
source, giving canonical Flag1zero for all farther integer cells.

Complete frames have fixed native phase and quiet keep1 throughout
the working/front/courier footprint. The own new ROM/operand/gather
and physical programme/courier inductions therefore apply to these
actual source bits, and deliver the cofactor commands. The early flags
are stored before their courier loads, and delivered by TF. This is
the physical bridge from the symbolic cofactors, with no preloaded
bank or freely chosen new upper encoding. Combined with the reserved
alias argument, it proves the one-bit second-signal enclosure.

## Two exhaustive projected pulses and infinite-line lift

J192 proves the new restricted native/header/Info factor identical to
the corrected SP29 factor, for arbitrary binary GF/raw flags and
unobserved private/Info/I inputs, common legal clock, initially empty
headers and no new errors. Info wipe compares to the **refined old
GF**; WF1 reads the old majority. There is no commit or special write
during these6144 updates. All its premises are supplied by the actual
second starting template above.

The frozen SP29 eight-case calculation orders its optional bits as
MF509(121), MF1021(117), MF1021(135). The actual SP30 enclosure fixes
the first and third to zero and selects only masks0 or2. Those two
complete integer-recurrence certificates each check all262144 sites
at6145 rows, including the initial row:1610874880 GF-support checks
and1113215910 evolving-background equalities per case. The retained
logs and common final arrays give endpoint T(116,128). Intermediate
GF support has two holes at two rows; no always-interval assertion
is used. This reuses a proved **closed projection**, not the old
private-state trajectory, and involves no sampled noisy experiment.

The initial projected defect and signal support lie in[117Q,148Q).
The binary-GF hull/flag-header propagation and no-new-one Info formula
confine every projected difference at row r to

    [117Q-8(r+1)-37, 148Q+8(r+1)+37).

The quotient's verified exterior equals the actual evolving Q-periodic
background at every row. At r6144 this interval is[70611,200749),
strictly inside the256Q quotient, with each projected read covered
by the margin. Induction identifies each quotient row with the
infinite-line projected recurrence inside that interval, and with
the background outside it. Exact factor induction identifies this
with the new actual SP30 history. Both q cases give the same endpoint.

## Second bank and third complete foreign sources

Apply J195's **new-ROM** conditional bank theorem with oldT(122,136),
its proved zero bank, and endpointT(116,128). The actual second pulse
meets its binary/raw-refined-computed GF and common-clock premises;
116<=122 and128<=136-1. The new bank has130 primaries and650 copies:
sixty targets were initially true and seventy were in complete old
foreign frames. Every target and refinement footprint lies inside
the final wrong-GF interval. The frozen new Hold/commit/reset argument
therefore gives the claimed bank at2U, followed by twelve complete
foreign Flag1 sources. The checker also rechecks their23400 GF source
routes, including360 direct reads. This still supplies only a subset
of the third signal and no arbitrary-error induction.

| Step | Status | Exact limit |
| --- | --- | --- |
| Two-phase alias reset and virtual509 carry | **proved conditional identities** | Correct native GF/commit clock; arbitrary old private/Info inputs |
| Actual partial signals zero and complete one-bit second enclosure | **proved** | Specified original error; actual new-ROM source/programme bridge |
| Second shrinking native/Info pulse on Z | **proved** | Two exhaustive finite cases, corrected factor and support lift |
| Second boundary650 zero copies and twelve third foreign sources | **proved** | New conditional bank theorem with all premises discharged |
| Full third mask/pulse, all upper data, arbitrary phase/width/clock errors | **unproved** | No general eroder supplied |
| Continuing E0 beside faults, higher error map, positive iid threshold | **unproved** | Restricted history is insufficient for the requested theorem |
| Globally sufficient minimum change or Gray/Gács argument verbatim | **unproved; not claimed** | SP30 is a separately changed construction |

No active G17/CURRENT change, no new numerical whole-CA trajectory and no commit.

The initial checker asked its limited syntactic normalizer to equate
`NOT(commit) AND MUX(commit, Hold, oldInfo)` directly with
`NOT(commit) AND oldInfo`; that assertion failed. The corrected check
pins the actual first expression and checks its eight Boolean cofactors
to obtain the second. The exact initial checker and failure are retained
in the receipt. This is a checker normalization limitation; no claim or
rule equation was changed.
