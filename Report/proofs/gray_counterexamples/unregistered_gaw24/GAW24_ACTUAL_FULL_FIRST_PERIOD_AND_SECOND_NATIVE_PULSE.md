# GAW24: actual first raw boundary and second Address pulse

This is a selected-history theorem for the **unchanged, explicitly changed
GAW2R rule**, not for Gray's automaton. It uses Q=8192, U=128Q=1,048,576,
lambda=24 and the original separation constant c=104. It neither shortens
U nor supplies an iid reliability or memory theorem. GAW23's actual
intact-start fault is the only error; no subsequent command, bank, head,
Info bit, or upper error is independently supplied.

All old GAW0--GAW23 proofs, receipts, rule sources and the registered Gray
report/checkpoint stay unchanged. The C programs in this directory are
analysis engines; they add no cellular-automaton transition.

## Exact statement and status

Let R be the frozen total radius-eight GAW2R transition, with its exact
immutable own ROM and dictionary. Let H be GAW4's infinite-line recursive
intact initializer, H in E(H,0). Compute row 1 as R(H), then replace GF,
and only GF, at every x in [0,17Q) by (x+Q/2) mod Q. Retain every other
bit of the actual chronological row. Apply R without further errors.

Write P=3848, N=496, S=(0,-2,-1,1,2). Logical SF word f at primary p is
the bitwise majority of its five physical holders p-S[h]. Define ell(p)=1
on [15Q/2,20Q), and zero otherwise, and q(p)=(p+ell(p)Q/2) mod Q.

The following statements are proved for this one physical history.

1. The **complete, unmasked raw row at U** is the formula in section 6:
   GF=q(x), Age=0, F1 on [7Q,15Q/2) union [39Q/2,20Q), F2=WF1=WF2=0;
   Info copies contain the derived old logical Out, Programme copies
   contain the holder-service hardwired beta bits, and every other SF
   field is zero. This formula includes unused Info and partial frames.
   It is not claimed to be a canonical E(C,A) row: GF remains displaced
   and F1 remains nonzero.
2. The second work period's actual three native gathers, 42 early
   executions and guarded flag couriers produce exactly the 24 positive
   right source primaries in section 7. All left sources are zero. The
   native input Age words actually differ; no common upper Age is assumed.
3. The next actual native pulse gives, at absolute row 2U,
   GF(x)=(x+Q/2) mod Q on [29Q/2,23Q), and GF=x mod Q elsewhere;
   Age=0, F1 on [14Q,29Q/2) union [45Q/2,23Q), and F2=WF1=WF2=0.
   This native state is already fixed by U+99Q while source guards remain
   closed. The wrong-GF width is 17Q/2, down from 25Q/2 at U.

The second **full** late pass, Out and Info commit at 2U, a decoded upper
error map, a subsequent orbit and eventual recovery are **unproved here**.
In particular the auxiliary source tracker at its final event is not
claimed to equal physical Info after the 2U commit.

## 1. Rule identity, intactness and error classification

The exact rule is
[gray_three_gather_gaw2r.py](../unregistered_gaw2/gray_three_gather_gaw2r.py),
with [gaw2r_compositional_cost.py](../unregistered_gaw2/gaw2r_compositional_cost.py)
and its frozen builder. The standalone manifest inherits GAW23's 591
hashed assets, ultimately pinning the actual own emission, dictionary,
listing, rule and H. It replays the inherited certificates rather than
substituting another simulator or an assumed upper trajectory.

GAW4's recursion gives every raw Word100 field and all five Info copies
of H. GAW23 retains all 139,264 complete old/replacement 496-word records
of the row-1 fault and proves that every replacement actually changes GF.
The whole location set is one **actual original-c104 real2**, with E0 and
E1 empty. It is not a real1: it cannot fit in a Q by U rectangle, and a
proper nonempty candidate1 subset cannot be isolated by 24Q from its
complement in this connected dense row of diameter 17Q-1<24Q. Two
104-site candidate1 subsets demonstrate the required 24Q linkage for
candidate2. The whole row fits a Q-squared by U-squared rectangle; its
diameter is less than 104Q, so no two nonempty subsets can have separation
104Q. External isolation is vacuous. This uses the printed condition
(iii) on candidate level-n errors, without changing it to level n-1.

There are substantial departures from Gray: h1 Flag2 erasure correction,
radius eight/17 gathered lanes, WORD100/FULLCOL representation, holder
computed-GF service controls, an immutable oversized ROM/dictionary, a
native-only early pass, guarded couriers and a late reset/birth at
102Q/102Q+1. The 3,742-word emission represents 41,162 direct beta bits;
the immutable resources total 270,349 bits (65,536 code bits plus
2,048 dictionary Word100 entries plus 13 metadata bits). The cell has
49,037 bits. Own beta<=Q and a faithful mutable Q-bit Programme protocol
are not proved. These changes cannot be ignored in a Gray attribution.

## 2. Previously proved physical prefix

[GAW23](../unregistered_gaw23/GAW23_ACTUAL_FIRST_ADDRESS_PULSE.md) proves
the actual native and source history through U. Before the first pulse,
the binary GF label is one on [Q/2,17Q), F1 is one on [0,Q/2) union
[33Q/2,17Q), and other flags are zero; this is fixed by row 4099. Common
Age is t mod U. All GF changes in that prefix are in [0,Q/2).

The physical H2/H3 gathers occur after this prefix. Each logical Mail
word loads its actual voted Info, shifts one logical site per tick and
is zeroed where F1 is one. H2 and H3 capture the same words at
S+1 for displacement zero, or S+2+abs(d)Q for d=-8,...,8 otherwise.
Capture is complete by 72Q+2. H1 may differ and is not assumed clean.

The first actual early pass produces the native flags used by the 21
first couriers. GAW23 proves their destinations, five source copies,
reader/computed-primary equations, SF wipe feedback and the first native
pulse. At U its native state is exactly ell/F1 as above, and it is fixed
by 99Q. The missing old result was the full late bank and Out commit.

## 3. Exact retained bank and Info masks

For a held SF Word100 W at logical primary p, suppose its five old copies
are k_h W, with k_h in {0,1}. At a nonreset/noncapture tick, its new holder
copy is maj(k) W unless that holder's actual SF wipe is true, in which
case it is zero. Thus the exact tag recurrence is

    k'_h(p) = majority_5(k(p)) AND NOT wipe(p-S[h]).

Here wipe is newF1(x) AND (newGF(x)!=rawOldGF(x)). It is not a comparison
with refined old GF. This recurrence is bitwise valid for every Word100
value and every history lane. It does not assume copies remain coherent
on intermediate rows. The C mask engine computes it from consecutive
actual old/new native events. Only current wipe groups and groups with
partially restored tags need updating: a zero tag can never resurrect,
and a full tag outside all wipes stays full. The actual finite wipe hull
lies strictly within [-24Q,24Q); the engine processes every affected
holder/group there, and tags outside that hull remain full by induction.
This is an exact finite-support computation on the infinite line.

At row 4099, held Info has coherent zero tags exactly on [0,4095).
Let J(p)=I(p) outside that interval and zero inside it, where I is H's
actual Info scalar. The two initially nonzero Info words in colony 0's
left half, at p=4064 and 4066, are both inside this erased interval.
The other affected native Info words there are already zero; arbitrary
Info is not substituted for them.

Let B=[0,Q/2) union [33Q/2,17Q). After capture, define

    B2(p)[d] = J(p+dQ), if d=0 or [p,p+dQ] misses B;
                0, otherwise.

The path interval is inclusive. H2=H3=B2 at every logical group, with
coherent five copies. This is a consequence of the actual stable native
prefix and the identical second/third LOAD, shift and capture timings.

For the pulse, the same tag recurrence starts with all five tags one at
96Q-1 and acts on both equal histories. Its final coherent zero tags are
exactly [Q/2,15Q/2-2) union [17Q,20Q). Write K(p) for the remaining
zero/one tag. Both histories are exactly L(p)=K(p)B2(p) by 99Q and stay
equal through the late birth. The 96Q and 102Q resets do not clear these
histories: their resets are at the first three gather starts only.

Consequently the actual Mem reload at 102Q+1 is
majority_3(H1,H2,H3)=L, regardless of H1. This identifies **all** 496 rows
and all 17 Word100 lanes of every late input; it is not a preloaded tape.
Held Info before U is K times J, except for the previously derived 21
special source writes at 80Q-1. That Info participates in actual source
reads but is not used in place of the actual late Out.

The mask receipt exhausts 28,675 tag updates. The prefix has 4,096 wipe
holder locations and the first pulse 81,920. These are counts of wipe
locations, not claims that this many nonzero raw fields changed.

## 4. Actual logical SF factor after the pulse

From 99Q to U the native fields are fixed apart from common Age. GF is
the two-label step q(x), old/new GF agree, WF guards are closed and every
SF wipe is false. These conditions follow from the actual native history,
not from arbitrary selected private fields.

For logical primary p, holder h is at x=p-S[h]. Its service Address is
(q(x)+S[h]) mod Q. At either separated GF step, at least three of the
five holders have the centre's GF label. Thus at least three service
Addresses equal q(p). The same is true away from a step. Every holder's
field function reads the same old logical voted words at p (and p-1/p+1
where the specified interpreter or Mail function requires them). The
local native clock is common. The field output depends on the holder
only through this service Address; wipe is false.

It follows, for **every old SF word including arbitrarily incoherent raw
Head, Mem, Scratch and Out copies**, that the next logical five-holder
vote is exactly the scalar operator at q(p). Three outputs equal that
operator's Word100/packet value; the other two cannot change any bit of
its majority. This is a direct dependence proof of the local_R loop,
not a sampled SF coherence assumption. The physical checks pin its raw
holder indices and reset/birth/stationary-ERROR branches. Programme has
logical value beta_bit(q(p)), because its raw holders are hardwired from
their service Address. No source's computed GF is read nonlocally.

At 102Q every logical Head, Out and Scratch resets to zero. At 102Q+1,
Head is born precisely at q(p)=P and Mem loads L(p). Thus actual late
births are true origins gQ for g<=7 or g>=20, and foreign origins
gQ-Q/2 for 8<=g<=20. This is derived from the new GF geometry; the early
head family is not carried through the native pulse.

## 5. Whole late execution, including the two partial pairs

Complete independent true frames are g<=6 and g>=20; complete foreign
frames are 8<=g<=19. Two of these complete heads meet partial neighbours
and must be followed together: true7/foreign8, and foreign20/true20.

The discovery checker runs all full 496x17 banks for 38 independent
heads: true -10..6 and 21..30, and foreign 9..19. Their native words
are all within the declared legal widths, **without projection**. Every
full immutable-ROM run halts by 141,557 ticks, remains in P..P+495,
and its full 496-word Out equals literal local_R on that exact bank.
The selected runtimes are 65,117 or 66,185. The general legal-input
141,557 bound is inherited from GAW2, not asserted for malformed words.

For the infinite exterior true frames g<=-11 or g>=31, all relevant
capture paths miss the finite bad F1/wipe/source hull. Their inputs are
exactly H(g+d), d=-8..8. Their heads therefore run the already proved
own evaluator on those legal raw cells. The same universal deadline and
frame travel bounds apply for every integer g, including all recursive
Info/Programme values of H. Between independent frames there is an
empty gap much larger than the interpreter's one-site incoming radius.
The only crossed GF steps are the following two explicit components.
This establishes exterior independence on the infinite line, without
choosing finite simulation boundary conditions.

The partial true7 entry is 248 sites left of 15Q/2; the partial foreign20
entry is 248 sites left of 20Q. Their Head travel encounters a service
Address jump from 4095 to zero. The next complete head is born in the
same physical component. The checker follows the exact synchronous
incoming collision selection, immutable instruction fetch, operand
travel, actual L(p), Out and Scratch of both heads. Old packets, not
newly written packets, determine every incoming candidate. Out/Scratch
reads and writes are local to the target site, so collecting their
updates simultaneously gives the stated scalar recurrence.

* true7/foreign8 collide at execution tick 10,871 at x=65,600. Their
  head hull is [61,192,65,783].
* foreign20/true20 collide at execution tick 10,869 at x=168,000.
  Their head hull is [163,592,168,183].

The literal collision rule makes the resulting packets stationary ERROR.
Their old-ERROR updates have no Out/Scratch writes, so they stay fixed
through the rest and commit. Each pair has 171 chronological Out store
operations at 158 distinct sites, all within its two represented frames.
The partial head stores at 54 sites with frame indices at most 241;
the complete head stores at 104 sites, with indices up to 491. Native
six outputs have already been written by both heads; Programme output
is incomplete. No sequential prefix of all 496 output words is assumed.
The receipt retains every complete birth bank, store, final Scratch and
Head packet, collision packet and trace digest. The holder checker
compares 2,720 actual full-local_R cofactors from these trajectories.
Raw physical Head coherence at a GF jump is not assumed: section 4's
majority factor is the lift.

## 6. Exact full raw U boundary

Define O(p) as follows. In each independent represented frame it is the
full own-ROM Out just proved, including any zero stores. In the two
coupled components it is the chronological stored Out in the receipt,
and zero at other sites. In the infinite unaffected true exterior it
is the represented raw record R(H)(g). No Out is born or written at any
other site. In particular unused Info after commit need not be zero:
foreign represented frames produce nonzero Out at residues which are
unused by the true encoding.

At the U update the native clock wraps to zero while native GF/F1 stays
fixed, WF remains zero and wipe is false. The local_R assignment takes
**old logical Out** before resetting work. It is independent of holder
service Address at this age. Thus every one of the five new Info copies
at p is exactly O(p), even across a GF step. All Head, Mem, Out, Scratch,
Mail, courier and History fields clear. Programme remains the literal
holder beta bit. The exact raw boundary is

    Cell(x): native = (q(x),0,F1(x),0,0,0);
             Info[h] = O(x+S[h]);
             Programme[h] = beta_bit((q(x)+S[h]) mod Q);
             all other SF words = 0.

The checker pins 1,247 complete unmasked local_R commit cofactors. The
branch dependence above proves it for every site/old work word, not
only those cofactors. The resulting true normal native records are

| true upper record g | GF, Age, F1, F2, WF1, WF2 |
| --- | --- |
| g<=-3 or g>=21 | g mod Q, 1, 0, 0, 0, 0 |
| -2,-1 | g mod Q, 1, 1, 0, 0, 0 |
| 0..7 | 0, 1, 1, 0, 0, 0 |
| 8..19 | 0, 0, 0, 0, 0, 0 |
| 20 | 20, 1, 0, 0, 0, 0 |

Foreign normal records 8..20 have native words (0,1,1,0,0,0).
Their other raw words, including the incomplete Programme words of the
coupled pair, are retained, not replaced with a chosen upper record.
All four possible true/foreign special source residues 3, Q/2-3,
Q/2+3 and Q-3 have Info zero at U. The first and last are outside any
represented Out frame. The middle residues are h1_0/h1_2 primaries;
their old upper Histories were zero and the computed upper Age is one,
which only captures H1 lane 8. The partial heads store no word beyond
frame index 241, below the relevant indices 245 and 251. Their complete
neighbours' actual stores at these indices are zero. This
argument applies in the entire recursive exterior, not just a sampled
range. Arbitrary unused Info elsewhere is retained by O.

## 7. Actual second banks, early heads and couriers

Until the next 96Q window the native equations keep the U GF/F1 fixed:
all native WF guards are closed, and no source-3 command exists. The
full raw U reset gives zero Mail and History before the first LOAD.
For each of the next three gathers, replace J by the just proved O and
the blocking set B by [7Q,15Q/2) union [39Q/2,20Q). The gather formula
in section 3 is therefore exact for all six native input words, for
every receiver, with the actual zero/one Age lanes. The Info special
write is later than every capture. H2=H3 again supplies the temporal
vote; no independently chosen upper history is used.

There are 42 explicitly followed early native-only executions: true
-10..7 and 20..30, plus foreign8..20. They read exactly P..P+5 and no
other bank row, halt within 213 updates, and equal literal native_at on
their complete unmasked six native banks. The exterior native records
are canonical Age1/F1zero, hence give no additional nonzero native flags
beyond the finite listed family. The 213-update bound fits far before
75Q; both partial heads stay within their first six sites before either
GF discontinuity, so their execution is the same actual factor.

The actual early Flag1 outputs are positive at true receivers -2..7,
20,21,22 and foreign receivers8..20. Early Flag2 and both WF outputs
are zero. This is checked on the actual noncommon Age lanes, not
deduced from a hypothetical common upper clock.

The right courier from a seed is forwarded only where
P+2<=q(p)<=Q-3, with an OR hold at q=Q-3. The partial true7 and
foreign20 routes encounter q=0 at the step, leave this interval and
are killed; they are not replaced by invented commands. The other 24
routes each reach their own destination after 4,339 updates. Their
destination holds do not mix adjacent colonies because the guarded
forwarding interval has a zero gap. Exact centre-control majority at
the steps lifts this courier equation to five physical holders.

At absolute U+80Q-1 the positive right source primaries are exactly

    (g+1)Q-3,  g=-2,...,6 or g=20,21,22;
    gQ+Q/2-3,  g=8,...,19.

All 24 have five Info copies equal to one. The left seeds are zero
because they use the actual computed early Flag2 word. Before this
write every potential WF source has its actual first-boundary Info zero.
The courier checker separately pins Mail LOAD/erasure and all four
Boolean incoming/held courier cases at the real holder coordinates.

## 8. Second native pulse and scope of confinement

The binary native/Info factor inherited from GAW23 now starts at this
actual U row, with the actual 24 source positions. It is valid because
common lower Age remains true, binary adjusted GF lists always have a
quorum, and F2/WF2 remain zero under the actual all-zero left sources.
SF can affect native WF only via the actual computed-primary low bits;
the factor carries their five holder bits and the exact SF wipe on
each tick. It does not discard the reader/source wipes or impose a
future Workspace value.

The new driver records 24,579 real updates and three guard-closed jumps
proved fixed by the native equations. Its event partition includes all
old segment boundaries, their native/source-cone shifts and both GF
wrap families. On each event interval the complete adjusted GF/flag
lists and source read are constant modulo the documented Address
arithmetic, so evaluation at interval endpoints gives the infinite-line
update. The independent audit uses literal full GF words and native
quorums, rather than reusing the label selector. It checks 20,488,060
event intervals, 41,027,022 native/WF cofactors and 2,949,480 source-holder
wipe cofactors, including all 24 source lineages and the guard jumps.
Additional frozen full-local_R checks retain actual computed-primary
dependencies with all otherwise unused SF fields free.

This proves the native endpoint in the statement: [29Q/2,23Q), width
17Q/2, with the two half-colony F1 strips and zero other flags. It is
positive selected recovery evidence, not an eroder theorem. No actual
late Out of the second period has been used or claimed. Common lower
Age and the closed WF guard make the native result through 2U valid
even though that unknown Out will determine the next physical Info.

Gray's printed Proposition 5 concerns Address confinement for a real-k
error, in a fixed two-Q-to-the-k spatial interval and time U-to-the-k/16
(p.43; text lines 1946--1951). This selected real2 history through 2U is
far within the much larger level-2 scales and proves no violation of
that claim. Nor does it establish Gray's actual protocol: the stated
GAW2R changes remain material. Raw partial-head collisions and the
mixed upper clocks are not themselves counterexamples to decoded
recovery. P4 all-SF containment, iid unreliability and memory loss are
not asserted here.

## 9. Reproduction and proof statuses

Run, with python3 from the repository root:

    python3 Report/proofs/gray_counterexamples/unregistered_gaw24/validate_gaw24_actual_full_boundary.py

The standalone asset manifest pins all inherited sources/receipts,
actual payload, H, immutable ROM/listing, analysis engines, all full
banks/output records, raw-holder checks and events. It rebuilds the C
engines and compares their exact binary/event bytes, replays the complete
inherited GAW23 certificate and replays every new receipt. The retained
nested-issue wrapper failure attempted no overwrite: an inherited
--issue argument correctly refused to reissue an existing source receipt.
Its exact old source and failure are preserved; the fix only gives the
nested invocation read-only argv. No mathematical/rule change is hidden.

| Step | Status |
| --- | --- |
| Infinite H, full row-1 payload, original-c104 real2 class | proved, inherited GAW4/GAW23 |
| First native/source history through U | proved, inherited GAW23 |
| Full logical retained H2/H3 and 102Q+1 Mem reload | proved here, exact bitwise masks/capture dependence |
| Fixed-geometry logical SF majority factor for arbitrary old SF copies | proved here, local dependence and holder cofactor checks |
| Independent whole-own-ROM execution and deadlines on the actual legal banks | proved here/inherited evaluator contracts |
| Partial paired Head/Out/Scratch trajectories and ERROR closure | proved here, exact finite recurrence plus logical factor |
| Complete unmasked raw U row and infinite exterior | proved here |
| Actual second six-native banks, early commands and couriers | proved here |
| Actual second native pulse and native endpoint at 2U | proved here |
| Full second late Out/Info boundary, decoded upper error map, later orbit | unproved |
| Full literal Gray programme/layout/physical refinement at these constants | unproved |
| Own beta<=Q, shorter U, general real1/real2 repair, higher-error map, iid reliability | unproved |

No step is labeled as Gray's proof applying verbatim to the changed
whole-rule implementation. Primary arguments motivate mechanisms and
the exact proposition being compared; the physical conclusions above
are separately derived from the frozen emitted rule.
