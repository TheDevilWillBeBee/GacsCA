# SP30: actual third signal, third shrinking pulse and next zero bank

Use the frozen, explicitly changed SP30 own rule of J189, with
Q=1024, U=475136 and TF=278401. Use exactly J191's intact-start
native overwrite at clock0, arbitrary initial upper Info, and no later
errors. J197 supplies the actual second signal, its projected pulse and
the second boundary. There is **no additional rule, programme, layout
or constant change**. This is a theorem about that history on Z;
arbitrary-fault recovery and a positive iid threshold remain unproved.

[Checker](check_signal_reservation1024_third_signal.py),
[receipt](../../figs/robustness/SP30_third_signal_certificate.json),
[second signal and boundary](SP30_SECOND_SIGNAL.md),
[new-ROM conditional bank theorem](SP30_GF_BANK_CLOSURE.md),
[corrected new-rule projected factor](SP30_NATIVE_PULSE.md),
[sound thirteen-bit pulse domain](SP29_THIRD_DOMAIN_PULSE.md).

## Exact statement

Write MF509(j), MF1021(j) for the actual five-holder Info majorities
at physical primaries jQ+509 and jQ+1021. At computed time
2U+TF=1228673 the actual complete third signal is enclosed by

    MF509: 1 exactly at116..127, 0 elsewhere;
    MF1021: 1 at112..114,128..135,141..144;
            unspecified at111,136..140,145..149; 0 elsewhere.

There are eleven unspecified Boolean bits, possibly correlated. Their
individual values and independence are not asserted. In particular the
two partial primaries MF509(115) and MF1021(127) are zero.

At computed time 2U+TF+6144=1234817 the actual native endpoint is
T(110,120): wrong GF on[112128,122880), width10752 instead of12800,
and Flag1 on[111616,112128) and[122368,122880). Native/header/code/
pressure auxiliaries other than that Flag1 are zero. The retained tracks
are MF509one116..119 and MF1021one128..135/141..144, with only
MF1021(136..140/145..149) unspecified; all their other values are zero.
This endpoint holds for every mask allowed by the eleven-bit enclosure.

At3U=1425408 the807 non-Info private bits are reset and all550
Info copies of110 primaries jQ+571..580, j109..119, are zero.
At3U+TF=1703809 the fourth period's complete foreign frames supply
MF509one110..119. The full fourth signal/pulse, all-field upper
restoration, general eroder, higher-error map and iid theorem remain
unproved. No complete encoded upper state is assumed at either boundary.

## The actual second-boundary native source enclosure

J197's two possible second projected histories have the same endpoint
T(116,128), and all-row GF support hull[117312,139264]. The new
private trajectory is not identified with an SP29 trajectory. We use
the exact native hull, actual SP30 programme and actual Hold stores.

Complete true frames j<=113 and j>=136 have their entire physical
working footprint[jQ+1,jQ+1022] outside that hull. Their native GF
and refinement footprints stay correct, with quiet keep1 throughout.
Their gathers were completed before TF. The existing own-programme
induction therefore gives their actual new-ROM outputs and commit.
Flag1's later mail gating does not change already captured inputs.

Frame114 need not keep its entire later working footprint intact.
Its GF59..68 and Flag1 phase88 primaries, five holders and radius37
refinement reserve all lie strictly left of117312. Those early Holds
therefore retain the corresponding actual outputs. The unique-store/
pending argument below excludes a later manufactured Hold issue there.
We require no Age or WF1 output in frame114.

The actual captured inputs for these programmes are J197's first-
boundary native source words and speed-eight crossing gates. The old
Flag1 strips are[121Q,122Q-512) and[136Q-512,136Q). A blocked path
captures zero. Every unblocked left source is at most120, with canonical
GF/F1zero, Age1/WF1zero except for free Age/WF1 at120. Thirty-two
fresh full-circuit cofactors j83..114 give GFj, Age2, F1WF1zero:
992 constant-bit equalities, with every unrelated field and I free.
For j<=82 no requested path can reach an exceptional source, so the
canonical closure supplies the same result on the remaining left half
line. The physical footprint argument supplies all these words for
j<=113 and just the required GF/F1 words at114.

The right sources are zero-GF/F1zero on136..143 with free Age/WF1,
canonical GF on144 and farther, Age1/WF1zero on144 and farther, and
F1one precisely144..146. The same actual capture gates erase every
source at135 or smaller. Forty-eight fresh full-circuit cofactors
j136..183 in the retained right-native probe leave all H2, Info,
unmentioned fields and I free. They give1249 constant-bit equalities:

| Source cell | GF | Age | F1 | WF1 |
| --- | --- | --- | --- | --- |
|136..140|0|free|1|0|
|141..143|free|free|1|0|
|144..146|j modQ|free|1|0|
|147 and farther|j modQ|2|0|0|

The fixed right footprints above connect those cofactors to the actual
new programme, Hold and commit. For j>=184 the maximum37-colony
dependency distance excludes every exceptional source, giving the
canonical right half line. The frozen probe alone did not claim this
physical bridge; this proof supplies it without changing that probe.

Recovered true frames128..135 require a different argument. Every
normal GF59..68 and Flag1 phase88 holder starts in the foreign GF
phase of T(122,136) and ends in the true phase of T(116,128).
Its initial Hold is zero by the807 reset at U. The checker verifies
the new listing and all90112 ROM keys at the22 relevant phases:

| Virtual destination phases | Input Hold issue | Materialization |
| --- | --- | --- |
|59..68|276520..278398|276522..278400, before TF|
|88|259870|259872, before TF|
|571..580|345734..358739|345736..358741, after284545|
|600|357660|357662, after284545|

There is exactly one Hold issue at each phase and none during the
pulse. Normal stores occur while the holders have the foreign phase;
opposite stores occur after they have the true phase. Neither can
address these primaries. This conclusion also uses J195's actual
single-arrival/pending induction: comb teeth differ by multiples of5
of magnitude at most20, never512; simultaneously present pending
records have one destination kind. Their presence majority either
selects that kind or suppresses the store. Arbitrary Pval, votes,
wipes and scratch stores cannot create a new Hold destination.
Thus all440 GF/F1 Info copies at88 recovered primaries commit zero.
No Age or WF1 output is required in these frames.

The source enclosure at2U is consequently:

| Upper source cell | GF | F1 | Age/WF1 |
| --- | --- | --- | --- |
|j<=113|j modQ|0|2/0|
|114|114|0|free|
|128..135|0|0|free|
|136..140|0|1|free/0|
|141..143|free|1|free/0|
|144..146|j modQ|1|free/0|
|j>=147|j modQ|0|2/0|

Only fields read by the third Flag1 cofactor are specified. These are
actual committed words, not a newly imposed upper encoding.

## Reserved aliases and the actual third commands

The literal SP30 commit mask A30 excludes every virtual alias obtained
from physical residues3/509/515/1021 under either binary phase0/512,
for all five holder slots. The conditional forwarded-Hold identities
of J189/J197 therefore reset all their Info copies at2U, independently
of arbitrary old Hold. J197/J195 supply the actual common commit clock
and native GF interface. In the quiet continuation there is no commit
or special write before the new signal row, and keep1 preserves zero.

For T(116,128), virtual Q-3 of physical jQ+509 occurs exactly at
j116..127. These complete foreign-frame commands are already supplied
by J197's zero bank and actual new programme. Physical jQ+1021 is
virtual Q-3 exactly at j<=114 or j>=128. The two partial primaries
115Q+509=a-3 and127Q+1021=b-3, where[a,b)=[118272,131072), have
all holders in virtual phase509. They receive no special write and
remain zero by the actual virtual509 carry identity. Hence there are
no optional MF509 values or optional interior MF1021 values.

The807 private fields are reset at2U. In complete true frames the
native T(116,128) working/front/courier footprint is fixed, quiet and
kept until TF. Actual gathers read the source enclosure just proved,
erasing a bit iff its speed-eight route crosses[115Q,116Q-512) or
[128Q-512,128Q). The native phases59..90 have the same crossing
predicate. The checker rechecks179070 actual routes. Unblocked left
sources are at most114; unblocked right sources are at least128.

Ninety-four fresh full-circuit Flag1 cofactors cover j77..114 and
j128..183 with the indicated GF/Age/F1/WF1 bits and all unrelated
fields/H2/Info/I free. They force one precisely at
112..114/128..135/141..144, and leave only111/136..140/145..149
unspecified. The other listed receivers have Flag1zero. Outside this
range,76+37<114 and184-37>146 exclude all exceptional sources and
give canonical Flag1zero throughout the two farther half lines.

The physical own-programme/courier induction, with actual fresh reset,
fixed working footprint and the proven capture gates, delivers these
commands to all five signal holders before TF. All stores precede
their courier loads. This connects the cofactors to the actual third
history without preloading a bank or assuming a correct upper state.
Together with the alias reset, it proves the complete eleven-bit mask.

## Reuse of the sound domain through the new closed projection

J192 proves the73 new native/header functions and corrected restricted
Info factor identical to the factor used in J180. Its premises allow
arbitrary other private fields and I, binary GF/raw flags, common legal
clock, initially empty headers, and no fresh errors. Here they follow
from the actual starting template. No commit or further special write
occurs during the6144 updates. In particular Info wipe compares new
GF with **refined old GF**, and WF1 reads old Info majority.

The projection observes Info only on the two relevant alias tracks.
An auxiliary representative may set other Info values to zero because
none enters this closed native factor; the actual other Info values
remain arbitrary. We do not identify the whole Info array or the
private trajectory with the old domain representative.

The frozen J180 domain additionally allows MF509(115) and MF1021(127)
to be arbitrary. The actual SP30 mask fixes both to zero, so every
allowed eleven-bit mask belongs to that sound thirteen-bit domain.
There are2048 choices in the smaller enclosure, within8192 in the
larger; no independence of the actual bits is needed.

J180's1062 set-image checks and36 GF-selector cases support a written
domain-inclusion induction. Boolean domains0={0},1={1},2={0,1} enclose
every concrete tuple, including correlated or repeated variables.
Threshold lower/upper sums bound every concrete sum. Exact scalar GF
is retained only when the selector is fixed or its two GF alternatives
coincide; otherwise the run stops. The frozen6144-step run has no such
stop, so its native GF and header/code remain exact by induction.
The corrected wipe and old-majority WF1 update preserve inclusion.
No numerical full-private trajectory is transferred.

Both frozen generated domain sources, log and endpoint arrays are
pinned. The6145 rows check262144 sites each:1610874880 GF checks and
1062876070 exterior/background equalities. Two intermediate rows have
holes in the GF support hull; no always-interval assertion is used.
The final arrays give the stated native singleton endpoint and two
retained-track enclosure. Domain-code sums and unevaluated old-wipe
diagnostics are not used as concrete one-counts or proof evidence.

The initial observed differences fit[111Q,150Q). The proved projected
speed-eight/GF-refinement support bound confines differences at row r to

    [111Q-8(r+1)-37, 150Q+8(r+1)+37).

Every row verifies the actual evolving Q-periodic exterior. At6144
the interval is[64467,202797), strictly inside the256Q quotient.
The seam and every projected read therefore have their infinite-line
background values. The same support induction identifies every
enclosed concrete quotient with its projected history on Z. The new
actual history is one of those histories by the source enclosure and
exact new-rule projection. This proves the third shrinking pulse on Z.

## Third boundary and fourth foreign sources

Apply J195's new-ROM conditional bank theorem to old T(116,128),
its proved zero bank, and endpoint T(110,120). All binary-GF/common-
clock premises are supplied by the exact domain induction. The required
inequalities110<=116 and120<=128-1 hold. At the final template every
target jQ+571..580, j109..119, its five holders and radius37 reserve
lie strictly inside[112128,122880). Sixty of these110 primaries were
initially true and fifty belonged to complete old foreign frames.
The actual store/pending/commit/reset argument gives550 zero copies
and807 reset at3U. The checker repeats19500 actual next-frame source
routes, including300 direct reads. The same fresh-reset, quiet-bank
and actual own-programme induction gives MF509one110..119 at3U+TF.
This does not yet determine any other fourth-period signal values.

| Step | Status | Exact limit |
| --- | --- | --- |
| Actual second-boundary native source enclosure | **proved** | New full-circuit cofactors, physical stores/commit and same specified history |
| Actual eleven-bit complete third signal | **proved** | Actual new-ROM capture/programme bridge; values and independence of optional bits unspecified |
| Sound domain and support lift | **proved previously; applies** | J180 only after J192's actual new-rule projection and present source subset |
| Actual third shrinking pulse on Z | **proved** | This specified original error/no later errors; full private data unobserved |
| Third boundary550 zero copies and ten fourth foreign sources | **proved** | Conditional new bank theorem, with all displacement/interface premises discharged |
| Full fourth signal/pulse, all upper data, arbitrary phase/width/clock faults | **unproved** | No general eroder supplied |
| Continuing E0 beside faults, higher map and positive iid rate | **unproved** | The requested all-level quantifiers are not covered |
| Globally sufficient minimum change or Gray/Gacs argument verbatim | **unproved; not claimed** | SP30 is a separately changed construction |

No active G17/CURRENT change, no numerical whole-CA experiment and no commit.
