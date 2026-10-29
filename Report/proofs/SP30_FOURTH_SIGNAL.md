# SP30: actual fourth signal, fourth shrinking pulse and next zero bank

This uses the frozen, explicitly changed SP30 own rule of J189:
Q=1024, U=475136, TF=278401, radius37 and force duration2048.
Use exactly J191's intact-start native overwrite at clock0, arbitrary
original upper Info, and no subsequent errors. J199 supplies the actual
third signal, its pulse and third boundary. There is no further rule,
programme, layout or constant change. This theorem concerns that one
history on Z. General repair and a positive iid noise rate are unproved.

[Checker](check_signal_reservation1024_fourth_signal.py),
[certificate](../../figs/robustness/SP30_fourth_signal_certificate.json),
[preceding actual history](SP30_THIRD_SIGNAL.md),
[new-ROM bank theorem](SP30_GF_BANK_CLOSURE.md),
[corrected closed projection](SP30_NATIVE_PULSE.md),
[sound domain induction](SP29_THIRD_DOMAIN_PULSE.md).
The [cofactor probe](probe_signal_reservation1024_fourth_signal.py) and
[separate domain driver](probe_signal_reservation1024_fourth_pulse_domains.py)
retain their conditional scopes. This proof supplies their physical and
infinite-line bridges; neither probe alone asserted those bridges.

## Exact statement

Let MF509(j), MF1021(j) be the actual five-holder Info majorities at
physical primaries jQ+509, jQ+1021. At computed time
3U+TF=1703809 the complete fourth signal belongs to this enclosure:

    MF509: 1 exactly at110..119, 0 elsewhere;
    MF1021: 1 at106..108 and120..130;
            unspecified at105 and131..152; 0 elsewhere.

The23 unspecified Boolean bits may correlate. No individual value or
independence is asserted. Both partial primaries MF509(109) and
MF1021(119) are zero.

At computed time3U+TF+6144=1709953 the native endpoint is T(104,112):
wrong GF on[105984,114688), width8704 instead of10752, and Flag1 on
[105472,105984) and[114176,114688). All other native/header/code/
pressure auxiliaries are zero. The retained observed Info tracks are

    MF509: 1 at110..111, 0 elsewhere;
    MF1021: 1 at120..130, unspecified at131..152, 0 elsewhere.

Every one of the8388608 masks in the enclosure has the same native
endpoint. The actual history is included without choosing its mask or
assuming a completely correct encoded upper state at a later boundary.

At4U=1900544,807 non-Info private bits per site are reset and all450
Info copies of90 primaries jQ+571..580, j103..111, are zero. At
4U+TF=2178945 the next complete foreign frames give MF509one104..111.
The complete fifth signal/pulse, all-field upper restoration, arbitrary
phase/width/clock faults, continuing E0 beside faults, higher-error map,
positive iid threshold and a globally sufficient minimum change remain
unproved. Four shrinking pulses do not establish a general eroder.

## Actual third-boundary native sources

J199 gives endpoint T(110,120) and the all-row third-pulse GF support
hull[111168,131072]. Use that hull rather than assuming a sharp
interval at intermediate times: two intermediate rows have holes.
Every full true frame j<=107 or j>=128 has its working footprint
[jQ+1,jQ+1022] outside the hull, with correct native/refinement
geometry and keep1. Its gathers finish before TF. The existing actual
own-programme induction preserves its new-ROM outputs through Hold
and commit, even though Flag1 subsequently changes already-finished
mail routes. No old SP29 private trajectory is substituted.

Frame108 may lose part of its late working footprint. Its early GF
phases59..68 and Flag1 phase88, all five holders and radius37 reserve,
are strictly left of111168: their rightmost endpoint is110719.
Those Holds remain valid; Age and WF1 are allowed to be arbitrary.
The unique-store/pending argument below excludes a manufactured later
GF/F1 Hold issue at these primaries.

The actual third gathers use J199's second-boundary source enclosure
and the strips[115Q,116Q-512),[128Q-512,128Q). Every blocked route
captures zero. Every unblocked left source is at most114, with GF
canonical and F1zero, Age2/WF1zero except free Age/WF1 at114.
Thirty-two fresh full-circuit cofactors j77..108 give992 constant-bit
equalities: GFj, Age3, F1WF1zero. Since76+37<114, the canonical
closure gives the same words on the farther left half line. The
physical footprint argument supplies all these words through107 and
the required GF/F1 words at108.

Every unblocked right source is at least128. J199 gives GF0 through140,
free GF141..143, canonical GF144 and beyond, F1one136..146, free Age
through146 and Age2 beyond, free WF1 through135 and WF1zero beyond.
Sixty fresh full-circuit cofactors j128..187 give1311 constant-bit
equalities, with all H2, Info, unrelated fields and I free. The checker
retains each individual bit equality, including constant bits of words
that are not completely constant. Whole-word summaries are:

| Source cell | GF | Age | F1 | WF1 |
| --- | --- | --- | --- | --- |
|128..135|0|free|1|0|
|136..140|free|free|free|free|
|141..144|free|free|1|free|
|145..146|free|free|free|free|
|147..149|j modQ|free|free|0|
|150 and beyond|j modQ|3|0|0|

The actual correct footprints connect all sixty cofactors to their
physical new-ROM programme, Hold and commit. Since188-37>146, the
canonical closure supplies the farther right half line. In the later
Flag1 calculation every nonconstant output bit is free. In particular
no shared selector identity GF in{0,j} is assumed: the attempted
syntactic identity test found none, and its result tightens nothing.

Recovered true frames120..127 need a store argument. Their normal
GF59..68 and Flag1 phase88 holders start inside T(116,128)'s foreign
GF region and end in the true phase of T(110,120). Their Hold starts
zero at2U by the807 reset. The checker rechecks22 actual destination
phases and all90112 corresponding ROM keys:

| Virtual phases | Unique input Hold issue | Materialization |
| --- | --- | --- |
|59..68|276520..278398|276522..278400, before TF|
|88|259870|259872, before TF|
|571..580|345734..358739|345736..358741, after284545|
|600|357660|357662, after284545|

No Hold issue exists during the pulse. The normal stores run while
these holders have foreign phase; the opposite stores run after they
have true phase. Neither can address them. J195's actual single-
arrival/pending induction is essential here: comb differences are
multiples of5 with magnitude at most20, never512, and simultaneously
present pending records have one destination kind. Their presence
vote either keeps that kind or suppresses the store. Arbitrary Pval,
scratch writes, votes and wipes cannot create a new Hold destination.
All440 GF/F1 Info copies at88 recovered primaries therefore commit
zero. Their Age/WF1 remain free. This completes the actual third-
boundary source enclosure, with2303 constant-bit equalities in its92
fresh full-circuit cofactors. It does not restore all upper fields.

## Actual fourth commands and reserved aliases

At3U the actual SP30 commit mask A30 excludes every virtual alias of
physical residues3/509/515/1021 under binary GF phase0/512, for each
of the five holder slots. J189's conditional forwarded-Hold identities
therefore zero these Info copies independently of old Hold. J199/J195
supply the actual common clock and raw/refined native interface. The
quiet template carries those zeros until the new special write, and
the807 private reset starts the new own programme from fresh state.

For T(110,120), virtual Q-3 occurs at physical jQ+509 exactly for
110<=j<=119; J199 already supplies these complete foreign-frame
commands. It occurs at physical jQ+1021 exactly for j<=108 or j>=120.
The partial primaries109Q+509=a-3 and119Q+1021=b-3, with
[a,b)=[112128,122880), have all five holders in virtual phase509.
They receive no special write and remain zero by its actual carry
identity. No optional MF509 or interior MF1021 value is introduced.

The true-frame working/front/courier footprint remains quiet and
fixed before TF. Its actual gathers use strips[109Q,110Q-512),
[120Q-512,120Q). Native phases59..90 have the same crossing predicate.
The checker repeats201930 actual capture gates; unblocked left sources
are at most108, and unblocked right sources are at least120. Every
left route reading109 or farther is erased, so no output assumption
for frame109 is needed. Use the actual source enclosure just proved,
with Age/WF1 free at108 and all four fields except GF/F1 free on
recovered120..127. On128..187 use precisely the fixed individual bits
of the fresh source cofactors, leaving every other bit free.

One hundred six fresh full-circuit Flag1 cofactors j71..108/j120..187
force ones at106..108/120..130 and leave only105/131..152 unspecified.
Every other listed receiver has Flag1zero. The bounds70+37<108 and
188-37>149 exclude the exceptional source data on the farther half
lines, so their canonical closure gives Flag1zero everywhere else.
The actual fresh-reset own-programme and early-courier induction,
with stores preceding courier loads and delivery before TF, turns
those cofactors into all five physical signal holders. Together with
the alias argument and foreign commands this proves the23-bit mask.

## The new domain instance and its infinite-line lift

J192's73 native/header identities and corrected restricted Info
factor apply to this actual start: binary GF, common legal clock,
empty headers, arbitrary other private fields and I, no further
errors, and no commit or extra special write in these6144 updates.
Info wipe compares computed GF with refined old GF; WF1 reads old
Info majority. Only MF509/MF1021 enters the closed projection.
Unobserved Info and all unobserved private data need not equal the
domain representative.

The frozen J180 domain factor is included unchanged in a separately
named wrapper. Only its initial template/mask, protection interval,
diagnostic instance number and output filename differ. J180's1062
set-image checks and36 GF-selector cases prove one-step inclusion
for the same domain equations, regardless of the number of uncertain
input bits. Domains0={0},1={1},2={0,1} and lower/upper threshold sums
cover every concrete tuple, even correlated or repeated inputs. GF
stays scalar only when its selector is fixed or both alternatives
coincide; otherwise the run stops. The new6144-update certificate
never stops. Induction therefore preserves inclusion and exact GF/
header/code for every one of the2^23 masks. No independence or
monotonicity of the full CA is used.

The wrapper, frozen factor, log and final arrays are pinned. At all
6145 rows it checks262144 sites,1610874880 GF-site checks and
999951270 exterior/background equalities. Two intermediate rows have
holes in the GF hull; its all-row hull is[105024,122880]. All final
native/header/code domains are singletons and the arrays give the
stated T(104,112) and retained-track enclosure. The optional bit105
has become known0. Domain-code sums and unevaluated old-wipe
diagnostics are not concrete one-counts or proof evidence.

All initial observed differences fit I=[105Q,154Q). The previously
proved projected speed-eight bound with radius37 refinement reserve
confines differences at row r to

    [105Q-8(r+1)-37,154Q+8(r+1)+37).

Each row checks equality to the evolving Q-periodic background
outside this interval. At6144 it is[58323,206893), strictly inside
the256Q quotient. The16Q reference period and quotient seam remain
outside the protected region and every projected seam read has its
infinite-line background value. The same support induction lifts
every enclosed concrete quotient history to Z. The actual new-rule
history belongs to the enclosure by the physical signal bridge and
closed projection. This proves the fourth shrinking pulse on Z.

## Fourth boundary and eight fifth foreign sources

Apply J195 to old T(110,120), its proved zero bank and the new
endpoint T(104,112). The exact domain induction supplies its binary-
GF/common-clock premises. Its inequalities104<=110,112<=119 and
104<112 hold. Every target jQ+571..580, j103..111, its five holders
and radius37 reserve is strictly inside[105984,114688). Sixty of90
primaries were initially true; thirty came from complete old foreign
frames h110..112. The actual store/pending/commit/reset argument
gives all450 zero copies and807 reset at4U. The checker repeats15600
next-frame source routes including240 direct checks. The actual new
programme with this fresh quiet bank then gives MF509one104..111
at4U+TF. It does not determine the rest of the fifth signal.

| Step | Status | Exact limit |
| --- | --- | --- |
| Actual third-boundary native bit enclosure | **proved** |92 new full-circuit cofactors plus actual programme/stores/commit; only requested native fields |
| Actual23-bit complete fourth signal | **proved** | Fixed-bit boxes, actual mail gates/own programme/couriers, alias zeros; unspecified bits may correlate |
| Sound one-step domain induction | **proved previously; applies** | Same frozen J180 factor after J192's new-rule projection; new initial enclosure |
| Actual fourth shrinking pulse on Z | **proved** | All6145 rows and support lift for the one specified error/no later errors |
| Fourth boundary450 zero copies/eight fifth foreign sources | **proved** | All premises of the conditional new-ROM bank theorem discharged |
| Complete fifth signal/pulse/full upper data/general faults/continuing E0 eroder | **unproved** | No all-width/all-phase or arbitrary raw-fault theorem |
| Higher-error map/positive iid epsilon/minimum globally sufficient change | **unproved** | Finite specified-history progress does not give the required all-level quantifiers |
| Gray/Gacs argument applies verbatim to the changed rule | **unproved; not claimed** | This is a separately changed construction |

The initial cofactor probe failed on a missing logQ attribute before
any cofactor conclusion; its source and failure log are retained.
The corrected probe reads the actual addr schema width. No equation,
programme or rule changed. There is no active G17/CURRENT change,
numerical whole-CA trajectory or commit.
