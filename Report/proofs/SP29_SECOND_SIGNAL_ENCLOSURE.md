# SP29: a three-bit enclosure of the complete second signal

This concerns the unchanged SP29 rule, own ROM and original first-error
history in SP29_FIRST_SIGNAL.md. It uses the corrected first pulse,
SP29_NEXT_GHOST_SIGNAL.md and SP29_FIRST_BOUNDARY_SIGNAL_DATA.md.
There are no errors after the original clock0 overwrite. The initial
upper Info payload remains arbitrary. No correct upper encoding is
assumed at the first boundary.

Write MF509(j) and MF1021(j) for the two retained logical Info-majority
tracks at computed time U+TF. The native GF template there has wrong
phase on [122Q-512,136Q); native age is the common legal TF clock,
Flag1 is the quiet two-strip template and other native/header fields
are0. Define three unspecified Boolean values

    p=MF509(121), q=MF1021(117), r=MF1021(135).

**Theorem.** The actual complete second signal belongs to this enclosure:

    MF509(j)=1 on122..135, p at121, and0 elsewhere;
    MF1021(j)=1 on118..120 and136..146, q at117, r at135,
               and0 elsewhere.

Thus the three values give at most eight possible starting patterns.
Their correlations or actual values are not asserted. The enclosure
does not by itself prove another shrinking pulse or an error-map induction.

## First-boundary source words used by the second true frames

The corrected first-pulse all-row log has GF support left minimum123456
and right maximum147456. Every physical holder of the normal upper
GF bits59..68 and Flag1 bit88 at true cell120 lies at least484 sites
below that minimum. Its radius32 joint refinement therefore stays
canonical, its computed native GF stays canonical and actual keep is1.
The early normal GF/Flag1 Hold issues precede TF; the opposite phases'
h2 Hold issues follow the settled pulse. The one-kind pending lemma
excludes a spurious Hold destination. Consequently these original
correct early outputs survive through commit, irrespective of the
damaged later programme in the right half of true frame120.

For every true frame j<=119 or j>=144, all working-front footprints
remain strictly outside the first GF support throughout the pulse.
Its native geometry and keep1 remain correct. All gathers finish
before TF, and no later normal Info write changes the programme inputs.
The ordinary physical own-programme proof therefore continues through
commit in those frames, even if native Flag1 temporarily gates mail
after the completed gathers. The original true-frame input has upper
native Age0, native flags/validities/backward pressure0, canonical GF
except for the explicitly cleared capture paths, and arbitrary other
circuit inputs. The75 actual first-circuit cofactors certify:

    GF(j)=j modQ, Age(j)=1, WF1(j)=0;
    Flag1(j)=1 only at124..126 and144..146 in their checked true frames.

Outside the checked finite range, no requested path reaches the old
strips, and the canonical native argument supplies the same words.
Hence at the first U, sources j<=119 have canonical GF/Age1/F1=WF1=0;
sources j>=144 have canonical GF/Age1/WF1=0, with F1=1 at144..146 only.
Cell120 has canonical GF and F1=0, while its Age and WF1 are left free.

For j136..143 the normal GF and Flag1 primaries start wrong-phase and
end true-phase. Initially their Holds are0. Their normal-phase Hold
issues (GF59..68 and F1 at88) precede TF and are never addressed while
the primary is initially wrong-phase. The opposite phases571..580 and
600 have their only Hold issues after the settled pulse, when the
primary has become true-phase. No Hold issue at either possible phase
occurs during the pulse. The pending-kind lemma and carry/wipe updates
therefore keep all these Holds0 through commit. At U these cells have
GF0 and F1=0; Age/WF1 at all eight cells remain arbitrary.

The corresponding physical Info copies and logical words are the
actual commit outputs. No all-field restoration is inferred.

## Exact second gather words and true-frame cofactors

The new native Flag1 strips are[121Q,121Q+512) and[135Q+512,136Q).
J167's exact majority/gate mail recurrence applies to this stationary
template, starting with fresh private0 at U. A direct input or an
eight-step capture path returns its original source word unless the
path hits a strip, in which case it returns0. The native field phases
59..90 used here all have the same crossing predicate at the relevant
colony indices. Captures precede the second special signal, and the
normal Info logical values are constant during the three gathers.

For a complete left true frame j<=120, every source at upper index
121 or larger is cleared. All other GF sources are canonical. Upper
Age is1 before120 and arbitrary at120; upper F1 is0 at every unblocked
source, and WF1 is0 except for its arbitrary bit at120. Other fields
and I can be free. The complete-circuit cofactors for j83..120 prove
new Flag1=1 at118/119/120,0 for j<=116, and leave only j117 unspecified.
For farther left j<=82 no requested path reaches either the strips
or cell120; the canonical source-free Flag1 conclusion is0. These
claims also cover negative indices by GF periodicity and the same
finite-path exclusion, not by a finite ring assumption.

For a complete right true frame j>=136, every source at135 or smaller
is cleared. Unblocked GF is0 on136..143 and canonical from144 onward.
Upper F1 is1 at144/145/146 only. Age and WF1 are arbitrary on136..143;
all other unblocked Ages are1 and WF1 bits0. Full-circuit cofactors
for j136..183 prove new Flag1=1 exactly on136..146 and0 otherwise,
leaving every unrelated field and I free. For j>=184 no requested
path meets the exceptional sources, so Flag1=0 canonically.

The second period starts with the actual807 private resets at U.
Every complete true frame has fixed native geometry, keep1, quiet
Flag1 throughout its full front/courier footprint, and constant
gathered inputs. The complete physical programme and courier argument
therefore writes precisely these cofactor Flag1 values to its true
MF1021 signal primary. It needs no correct upper configuration or
assumed Age value in the nine exceptional source cells.

## Assemble the tracks and their limits

The retained-data theorem gives MF5090 on j<=120 or j>=136 and
MF1021=0 on121..134 until the second special signal. Those primaries
have virtual phase509 and are not overwritten by that signal.
J169 gives MF5091 on122..135 from all complete foreign frames. The
left partial MF509(121) and right partial MF1021(135) are arbitrary
bits. The true-frame cofactors supply all other MF1021 values except
the optional j117 value. This proves the complete three-bit enclosure.

The separate eight-case corrected-factor driver retains every6145-row
certificate and final array. It labels its runs conditional until
combined with this physical enclosure and a new infinite-line lift.
Its result must be read rather than assuming all eight cases shrink.
No general arbitrary-width/phase/noise induction follows from this
one specific second signal.

| Step | Status | Exact limit |
| --- | --- | --- |
| First-boundary GF/F1 words, protected and recovered cases | proved | Same specified original error; actual Hold issue and hull audits |
| Complete true-frame second Flag1 cofactors | proved | One left Age/WF1 word and eight right words free; unrelated inputs free |
| Actual full second MF tracks belong to the three-bit enclosure | proved | Fresh private reset and complete-frame programme/courier proof; two partial bits free |
| Actual second shrinking pulse | requires separate completed eight-case certificate and Z lift | No endpoint is assumed by this enclosure |
| General eroder/higher map/positive iid rate | unproved | Two particular periods do not establish the required induction |

Reproduce with check_short_force1024_second_signal_enclosure.py;
receipts in figs/robustness preserve the conditional probes and their
actual-source bridge. No active rule, ROM or constant is changed.
