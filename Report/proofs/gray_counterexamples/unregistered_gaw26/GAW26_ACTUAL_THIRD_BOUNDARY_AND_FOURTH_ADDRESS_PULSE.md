# GAW26: the same fault's third raw boundary and fourth Address pulse

This checkpoint continues one actual intact-start history of the frozen
GAW2R rule, with Q=8192, U=128Q=1,048,576, lambda=24 and c=104. It proves
the complete raw third boundary and the fourth native pulse. The wrong
Address width falls from 4.5Q to **3.5Q**, rather than the 0.5Q obtained
by extrapolating the preceding 4Q reductions. This is a failure of that
extrapolation, not a Gray, Gács, operational-repair or iid counterexample.

No rule, ROM, constant, frozen GAW0--25 artifact, registered report or
main checkpoint is changed. New C programs analyse the existing rule.

## 1. Exact history and statement

Let H be the frozen recursively intact infinite initializer. Compute
R(H), then at row 1 replace only GF at every x in [0,17Q) with
(x+Q/2) mod Q, retaining every other actual bit. These 139,264 replacements
are genuinely changed, and there are no later errors. GAW23 retains
the full old/replacement records and classifies their single shared
support as one original-c104 real2, with no actual E0/E1 locations.

GAW25 proves the complete raw 2U row and the third native pulse from
that same history. Its accepted proof is
[GAW25_ACTUAL_SECOND_BOUNDARY_AND_THIRD_ADDRESS_PULSE.md](../unregistered_gaw25/GAW25_ACTUAL_SECOND_BOUNDARY_AND_THIRD_ADDRESS_PULSE.md).
At 3U the lower GF is shifted by Q/2 on [43Q/2,26Q); F1 is one on
[21Q,43Q/2) union [51Q/2,26Q); common lower Age is zero and F2=WF1=WF2=0.
Set ell3 to this interval's indicator and
q3(x)=(x+ell3(x)Q/2) mod Q. Let P=3848, N=496 and S=(0,-2,-1,1,2).

For the actual logical late Out O3(p) derived below, the **full raw**
third boundary is

    native(x) = (q3(x),0,F1(x),0,0,0);
    Info[h](x) = O3(x+S[h]);
    Programme[h](x) = beta_bit((q3(x)+S[h]) mod Q);
    every other simulation field = 0.

O3 includes all unmasked Word100 values and nonzero unused true-layout
primaries written by foreign heads. This row is not asserted to be a
canonical E encoding: lower GF/F1 remain displaced/nonzero.

The fourth actual gathers, early immutable executions and couriers give
28 positive right sources and no left sources. Their pulse yields at 4U

    shifted lower GF exactly on [51Q/2,29Q), width 7Q/2;
    F1 exactly on [25Q,51Q/2) union [57Q/2,29Q);
    Age=0, F2=WF1=WF2=0.

This native state first appears at relative fourth-period row 98Q+Q/2
(806,912) and is then fixed until 4U. Its fourth late Out, fourth raw
Info commit, later orbit and eventual repair are not proved here.
The auxiliary tracker after that commit is not physical new Info.

## 2. Rule identity and faithfulness limits

All rule, own-emission, immutable ROM/dictionary and raw local_R sources
are unchanged and pinned transitively by the accepted GAW25 manifest.
GAW2R still has the h1 correction, radius8/17 lanes, WORD100/FULLCOL,
holder computed-GF service Addresses, oversized immutable code and
dictionary, native-only early pass, guarded couriers and 102Q late reset
and birth. Its direct beta has 41,162 bits, exceeding Q; its complete
immutable storage is 270,349 bits. This is not Gray's mutable Q-bit
Programme/layout, and the changed late start enters Gray's rest window.

The inherited own-evaluator identity is used only after checking every
actual gathered native word has its legal 13/20/1/1/1/1-bit width,
without masking. Every other Word100 value is retained. No arbitrary
malformed-native quotient or legal-E theorem is applied to illegal data.

## 3. Actual third bank and expanded analysis domain

Before the third 96Q source window, the lower native state is the fixed
2U geometry. All three gathers therefore load the actual O2(p) proved
in GAW25. Their Flag1 blocking set is
B2=[14Q,29Q/2) union [45Q/2,23Q). For lane d=-8,...,8 the actual capture
is O2(p+dQ) if d=0 or the inclusive source/receiver path misses B2,
and zero otherwise. The literal Mail LOAD, speed-one shift, Flag1
erasure, History reset and capture equations establish this formula.
No upper state or tape is assigned. H2=H3 bitwise after 72Q+2.

The actual third pulse applies the inherited five-holder tag recurrence
to each held history lane:

    newTag[h](p) = majority5(oldTag(p)) AND NOT wipe(p-S[h]);
    wipe(x) = newF1(x) AND (newGF(x) != rawOldGF(x)).

The new tag engine uses **[-32Q,32Q)**, not the old [-24Q,24Q) domain.
This is an analysis-domain expansion, not a CA change. Every current
wipe holder, its five affected logical groups and every pending partial
group lies strictly inside that domain; outside, full tags stay full
and zero tags stay zero by the same induction. Consecutive actual third
native events give no prefix Info wipe and the final coherent H2/H3
zero-tag set

    [29Q/2,43Q/2-2) union [23Q,26Q).

The receipt checks 24,578 tag updates and 81,920 wipe-holder locations.
These are locations where a keep tag is erased, not a count of changed
nonzero physical data. The actual 102Q+1 Mem reload is temporal majority
of H1/H2/H3, hence this retained H2 regardless of H1. Every 496x17 bank
word is thus derived from the one chronological history.

## 4. Actual late births, evaluation and interacting packets

After the third pulse, native GF/F1 is fixed, lower Age is common, source
guards are closed and wipe is false. For each logical p, at least three
holders x=p-S[h] have service Address q3(p). Every SF update at those
holders reads the same old logical voted fields at p and p±1. Its
bitwise five-holder output therefore equals the scalar SF operator at
q3(p), for every old Word100 value, even when the other two raw holders
disagree. This is the inherited dependence proof on the new actual
two-step geometry; it is not an assumption of raw-copy coherence.

The 102Q reset clears Head/Out/Scratch. Actual births at 102Q+1 have
true origins gQ for g<=21 or g>=26 and foreign origins gQ-Q/2 for
22<=g<=26. The two partial/complete interacting pairs are true21 with
foreign22, and foreign26 with true26. The new checker follows them with
literal old incoming packets, actual bank, Out, Scratch, service Address
and immutable instruction fetch.

Seventy independent complete heads are checked: true -26..20 and 27..46,
and foreign23..25. Their full 496-word outputs equal literal local_R on
the exact unmasked banks. Each halts within the inherited legal-input
bound 141,557, with every position in P..P+495. The available late
execution interval has 147,455 updates after the reserved birth tick.
The retained records give every bank, output and chronological trace
hash, not merely six native fields.

For every true g<=-27 or g>=47, the 17-lane bank is exactly
R-squared(H)(g+d): all paths miss B2 and all sources lie outside the
finite second-boundary disturbance. The own identity then yields
R-cubed(H)(g) by the same deadline. R-cubed(H) is computed as literal
R on the exact R-squared(H) neighborhood. The wider finite margin,
independent-frame gaps, and explicit pair hulls give an infinite-line
composition without a finite boundary condition.

| actual pair | collision execution tick/site | complete Head hull |
| --- | --- | --- |
| true21 / foreign22 | 10,871 / 180,288 | [175,880,180,471] |
| foreign26 / true26 | 10,869 / 217,152 | [212,744,217,335] |

Each collision produces stationary ERROR, which writes neither Out nor
Scratch and is held until reset. Each component has 171 chronological
Out writes at 158 distinct sites: 54 partial-frame sites with maximum
index 241 and 104 complete-frame sites up to index 491. The actual stores,
packets and Scratch are retained. These are not sequential output
prefixes. Another 2,720 physical local_R holder cofactors pin these exact
trajectories.

## 5. Full raw 3U commit and actual next source padding

O3 consists of those exact outputs, zero at unwritten pair sites,
R-cubed(H) in the untouched infinite exterior, and zero at every other
site. Foreign-frame outputs at unused normal residues are included.
At wrap, every Info holder copies **old logical Out** before all work
resets, regardless of service Address. This proves section1's raw formula
on the entire line. The new checker pins 2,550 arbitrary-value
reset/control cofactors and 1,240 complete raw commit cofactors.

The actual true native Info records are:

| true normal g | GF, Age, F1, F2, WF1, WF2 |
| --- | --- |
| g<=-1 or g>=26 | g mod Q, 3, 0, 0, 0, 0 |
| 0..6 | g mod Q, 3, 1, 0, 0, 0 |
| 7..9 | 0, 3, 1, 0, 0, 0 |
| 10..13 | 0, 2, 1, 0, 0, 0 |
| 14..21 | 0, 1, 1, 0, 0, 0 |
| 22..25 | 0, 0, 0, 0, 0, 0 |

Foreign22 has (0,3,1,0,0,0); foreign23..26 have (0,1,1,0,0,0).
All raw fields remain in the full output records. Every native width
is checked. In particular the Ages are not assumed common above.

At 3U, Info at all possible true/foreign source residues
3, Q/2-3, Q/2+3, Q-3 is zero globally. The outer residues have no Out
writer. The middle residues correspond to noncentral H1 lanes at output
indices 245/251: their old upper values are zero and upper Ages 1,2,3 do
not capture them. The partial heads' maximum written index is 241;
their complete neighbours' actual values at 245/251 are zero. The
untouched R-cubed(H) exterior has zero noncentral H1 lanes at phase3.
This source-zero conclusion has an infinite exterior proof, not only
the finite native table check.

## 6. Fourth actual banks, flags and courier lineages

The fourth gathers use O3 and actual lower blocking set
B3=[21Q,43Q/2) union [51Q/2,26Q). Their literal path captures give all
native banks. The early program reads exactly six rows P..P+5 and no
other 490 rows, and finishes within 213 updates at these actual entries,
including the partial ones. Seventy-four actual runs cover true
-26..21 and 26..46 and foreign22..26. Their six outputs equal literal
native_at, retaining every 100-bit native lane and noncommon Age.

Positive Flag1 receivers are true0..21 and true26..28, and foreign22..26.
Their computed Flag2 and WF outputs are zero. The untouched upper
R-cubed(H) exterior has canonical GF, Age3 and zero old flags, so adds no
native flags. The checker allows positive Flag2 and derives its absence;
it never imposes future left-command silence.

At 75Q, these actual Flag1 words seed right couriers. The inherited
guard P+2<=q3<=Q-3 with destination hold kills the partial true21 and
foreign26 lineages at their real GF jumps. Other paths finish in 4,339
updates and hold behind a zero gap. Left couriers stay zero because the
actual Flag2 outputs are zero. Additional raw-holder checks cover the
Mail LOAD/erasure and all Boolean courier cases at the real boundary
and source coordinates.

The 28 right Info sources at absolute row 3U+80Q-1 are exactly

    (g+1)Q-3, g=0,...,20 or g=26,27,28;
    gQ+Q/2-3, g=22,...,25.

Each has five actual Info copies one. All other potential sources
retain their proved zero value, so this is the complete command set.

## 7. Fourth pulse and finite allowance

Common lower Age, binary adjusted-GF quorums and the derived zero left
sources give the same closed native/Info factor. The new driver starts
at the actual 3U native state and retains each source-holder bit and
every source/reader wipe. The full-word independent audit checks
22,312,255 event intervals, 44,666,298 native/WF cofactors and 2,867,760
source-holder wipe cofactors. There are 20,484 explicit updates and
three guard-closed fixed-state jumps. A further 2,948 full local_R
checks pin final computed-primary reads with otherwise free private
fields. The existing infinite-line event-partition proof applies;
no new CA equation is used.

The endpoint is [51Q/2,29Q), width7Q/2, with the stated F1 strips.
It is fixed from 3U+98Q+Q/2 through 4U; late private execution cannot
alter native fields there because the WF guards are closed. The
boundary widths are 25Q/2,17Q/2,9Q/2,7Q/2. They therefore do not obey
a universal 4Q decrement, even for this selected history. There is no
proof of a stationary translated orbit, later growth, eventual repair
or any failure of an actual higher-level repair deadline.

Gray's printed Proposition5 (p43, text lines1946--1951) confines Address
for a real-k error to a fixed two-Q-to-the-k box with lifetime
U-to-the-k/16. All 98,334 native event records, plus their fixed-gap
inductions, give Address union hull [0,29Q) and maximum instantaneous
wrong count17Q through4U. For this real2,

    29Q < 2Q^2;
    4U-1 < U^2/16.

Thus the proved trace fits [0,2Q^2) times [1,1+U^2/16). It supplies no
P5 allowance violation. The all-SF P4 property and decoded operational
error map are separate and are not inferred from this calculation.

## 8. What transfers to faithful Gray, and what does not

F2 remains zero throughout this particular lower native trace, so the
h1 erasure correction is not used in its GF recurrence. Conditional on
the same GF/Age/Flag1 equations, the same complete physical command
set, source/reader wipe semantics and schedule, its native algebra is
reproducible. This conditional statement does not establish those
premises for Gray's actual programme and layout.

In particular the bank uses seventeen lanes, the concrete primaries
and immutable evaluator differ, early evaluation is native-only, flag
couriers have explicit guards, computed source reads use radius8, and
late execution starts at102Q. These can change precisely the Out,
captured words and future source commands used here. No proved
refinement eliminates them. Therefore even a future GAW2R operational
failure would not by itself refute corrected Gray/Gács or iid memory.
The present fourth-period contraction is neither such a failure nor
a theorem that faithful Gray would have the same four boundaries.

## 9. Faster-period question

U has not been shortened. Reserving the entire 141,557-update
legal-input bound after the frozen birth at102Q+1 takes more than119Q
of a compatible total period before commit; the current128Q has
sufficient slack. This upper bound is not a lower bound on runtime.
This arithmetic alone is not a U=120Q construction: changing the
modular clock changes own beta, dictionary and instruction layout,
commit/active gate counts and the full cost certificate. Gather,
early flags, special writes, native quieting, reset and physical
period composition must be checked again. Damaged-history quieting
is not made universal by the four selected pulses. No shorter-U or
minimum-U conclusion is asserted.

## 10. Reproduction, retained failures and statuses

Read-only default command from the repository root:

    python3 Report/proofs/gray_counterexamples/unregistered_gaw26/validate_gaw26_actual_third_boundary.py

The validator checks all653 frozen GAW25 asset hashes, its
manifest/proof/validator and both accepted terminal replay logs. It
recomputes every new mask, emitted execution, interacting trajectory,
holder/commit cofactor, early native bank/courier and native event audit.
Optional `--full-inherited` also reruns the unchanged GAW25 mathematical
dependency. Both modes hash all assets again afterwards and generate
new products only in temporary directories. They do not write rules,
main documents or accepted receipts.

Two new source-generation string-map failures and a pre-execution
inherited-filename error are retained, with source/log provenance.
They occurred before their mathematical checks and did not change a
rule or any frozen asset. The corrected actual calculations are the
receipts named above; no failed CA trace is discarded or repaired.

| Step | Status |
| --- | --- |
| Intact H, original shared real2 support, full2U and third native pulse | proved, accepted frozen dependencies |
| Actual third captures, expanded-domain tags and Mem reload | proved here |
| Fixed-geometry SF factor, new late births, full emissions and collisions | proved here with inherited legal evaluator contracts |
| Infinite exterior and complete unmasked raw3U boundary | proved here |
| Fourth actual native banks, flags and complete courier/source set | proved here |
| Fourth native pulse and finite Address allowance | proved here |
| Extrapolated 4Q boundary reduction | false for this selected unchanged-rule history |
| Fourth full Out/Info, later orbit, eventual recovery and decoded map | unproved |
| Faithful Gray programme/layout/source refinement; own beta<=Q | unproved |
| Arbitrary real1/real2/higher repair, iid memory and shorterU | unproved |

No whole-rule reliability argument of Gray or Gács is imported
verbatim for this changed candidate. Their original error-class
definition is used, while the selected physical conclusions follow
from the frozen equations and exact own emission.
