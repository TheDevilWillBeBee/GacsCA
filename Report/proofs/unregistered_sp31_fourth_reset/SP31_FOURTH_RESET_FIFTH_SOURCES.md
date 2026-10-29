# SP31: universal commit reset and the actual fifth command enclosure

This concerns unchanged isolated F31, Q1024/U475136/r37, TF278401.
The physical-history conclusions use exactly J225's native-only,
original-c16 dense16Q real2 fault from an intact encoding, arbitrary
original upper Info, and no later errors. No rule, ROM, constant, CURRENT
or G17 changes. The universal reset lemma has its separately stated
common-clock hypothesis; the other conclusions concern that one family
of histories. This proves neither a fifth pulse nor general repair.

## Exact statements

1. Whenever all raw Ages in an F31 local input have the common legal
   value U-1, all 807 output bits outside GF, Age, F1 and Info are zero,
   and all 19 output Age bits are zero. GF, flags, SF and instruction
   inputs may be arbitrary. This includes resetting native F2 and both
   Workspace flags as well as the private simulation fields.
2. In the actual history above, at 4U=1900544 these resets apply globally.
   Every copy of each physical Info primary of phase3/509/515/1021 is
   also zero. Other committed Info is not claimed to be zero.
3. From 4U through 4U+TF=2178945, the actual common lower clock advances
   from0 toTF. GF and F1 remain in J248's fixed enclosure:

   | Field | Free binary domain | Definite-one domain |
   |---|---|---|
   | wrong GF label b | [142Q+1,152Q-512) | [152Q-512,155Q) |
   | F1 | [142Q-2,152Q-512) | [155Q-512,155Q) |

   These fields are zero elsewhere. Actual native F2/WF1/WF2 are zero
   throughout this prefix. The free bits need not be independently
   reachable. The alias Info copies remain zero through state
   4U+TF-1; the scheduled commands may be written on the next update.
4. At state 4U+TF, the actual five-copy voted commands have this enclosure:

   | Physical track | Fixed-one colonies | Free colonies | All others |
   |---|---|---|---|
   | MF509 | 152..154 | 142..151 | 0 |
   | MF1021 | 100..139 and155..157 | 140..150 | 0 |
   | MF3 | none | 133..151 | 0 |
   | MF515 | none | 142..154 | 0 |

   There are46 fixed ones and53 free votes. The 2^53 Cartesian set is
   an enclosure, not a reachability assertion or a distribution.

The proof gives only these native and source statements. It does not
characterize the complete4U upper state, all SF/Info, the exact interior
command correlations, the fifth pulse, eventual erosion, an arbitrary
higher-error map or a positive iid noise threshold.

## 1. Universal common-clock reset — proved

Use the actual full F31 builder and its joint GF/Age refinement. A valid
distant joint block has Age U-1 because every raw member has that Age.
If no joint replacement exists the raw Age is also U-1. Thus every
refined Age used by native maintenance is U-1. Its chosen current Age
is U-1 and its literal successor is0, regardless of every GF quorum,
flag or private input. No agreement of raw, refined and computed GF is
needed.

The common-clock cofactor in
[probe_fourth_reset.py](probe_fourth_reset.py) leaves all other raw
bits and all instruction ports free. The actual compiled expressions
give zero for every Age output and every field other than GF/F1/Info.
The latter count is842-10-19-1-5=807. This is an exact circuit identity
under the common-Age substitution, not sampling of flag combinations.

A second, conditional interface cofactor keeps computed GF and refined
self-GF independent, computed F1/F2 free, and current/successor Ages
U-1/0. For each holder slot s=-2..2 the actual commit expression is

    keep AND allowed((computedGF+s) modQ) AND forwardedHold(s),
    keep = NOT(computedF1 AND (computedGF != refinedSelfGF)).

The checker compares these expressions by the existing sound Boolean
normalization rules. It also certifies the same807 reset bits. This
conditional identity explains what is committed without assuming a
well-running interpreter or keep1 at interior sites.

J248 supplies the actual common legal clock and binary adjusted GF at
the fourth boundary. If y has physical phase3/509/515/1021 and x=y-s
is any of its five holders, computedGF(x)=(x+512b) modQ with b in{0,1}.
Its virtual primary is (y+512b) modQ. For either label this is another
member of {3,509,515,1021}, all excluded from the normal commit mask.
The conditional expression is therefore0 for all40 phase/slot/label
cases, even if holders choose different labels. Hence all20 physical
alias copies per colony are zero at4U. Normal Info outside these aliases
may contain arbitrary voted Hold data.

## 2. Actual quiet prefix — proved using J248's fixed point

[J248](../unregistered_sp31_fourth_ternary/SP31_FOURTH_NATIVE_ENCLOSURE.md)
proves a sound powerset native fixed point after the fourth pulse, with
the displayed GF/F1 domains, native F2 possibly free on
[142Q,152Q-512), and both Workspace domains zero. Section1 resets the
actual F2 to0 at4U; zero belongs to that F2 domain. The boundary GF/F1
are already enclosed by J248. The commit reset introduces no new GF
or F1 equation.

For lower current Ages0..TF-1 the literal Workspace time guards are
closed. F31's native maintenance has private service force0 and reads
no SF or instruction field. Binary adjusted GF and common legal Age
remain closed under refinement and the directional selectors. Every
five-site right GF vote has a label majority, so the no-right-quorum
Flag2 source is false. With all old F2/WF2 zero, every other native F2
source and retention clause is also zero. The closed guards make new
WF1/WF2 zero. Induction preserves actual F2/WF1/WF2 zero and encloses
GF/F1 by the same native fixed point throughout the quiet prefix.
This uses the fixed point only while its source guards are closed;
it makes no assertion about the next active Workspace interval.

The actual alias Info starts0 by section1. Between commits Info is
old Info with possible holder erasures, except for the literal special
command write. No ordinary Out/Hold store writes Info in this prefix.
J223/J225's unchanged courier guard permits its first special write at
current Age TF-1, into the resulting state AgeTF. An arbitrary interior
interpreter cannot move that clock guard. Therefore every alias copy
remains0 through state4U+TF-1. On the next update the current Age still
lies outside the Workspace window, so native Workspace stays0 in state
4U+TF even though its new commands may be nonzero.

## 3. Actual fresh work and captures — proved by the existing physical induction

[J250](../unregistered_sp31_fourth_banks/SP31_FOURTH_PROTECTED_BANKS.md)
supplies the actual protected normal native Info banks at4U for true
frames<=141 and>=155, with the same shared a/q134/q141 values, and the
new foreign zero GF/F1/F2 banks at h153..155. Section1 gives fresh work
globally at4U, independently of unknown private work before that time.
Section2 gives the native premises through the fifth source deadline.

For true frames<=141/>=155, the complete work phases58..965, all five
holders and the native radius37 margin lie on the known canonical-GF
exterior sides, just as in J250. Two outward joint blocks retain the
canonical self pair; the actual computed GF is also canonical. Thus
keep1 protects these work fields even where an endpoint's F1 is free.
The guarded-front/typed-pending/Match/own-ROM induction of J223,
J239 and J242 applies from the actual fresh reset. Captures may include
unrestricted interior data, but every such capture is an actual binary
word. The interpreter computes the full native output on their temporal
vote; no correctness premise is imposed on an interior frame.

The complete foreign frames h152..154 have origin o=(h-1)Q+512. For
each of them

    152Q-512 <= o+58-39,
    o+965+39 < 155Q-512,
    [o+1,o+1023] is contained in [152Q-512,155Q-512).

These are their complete work/native margins and courier holders.
All have actual wrong-GF label1, common clock and F1=0, so no wipe.
The same guarded-front induction proves complete foreign execution
and actual courier delivery. At h154 the last courier holder is
155Q-513, one cell before the fixed right F1 strip. This argument does
not extend to partial foreign h155.

Known normal native Info sources remain their J250 values: their
holders/margins are on the protected exterior sides and keep1. The
foreign GF zero holders have stable label1/native margins and no wipe.
No Info commit or special write touches these ordinary primaries before
the deadline. The three gathers therefore agree on each known source;
unknown source captures may be enlarged to independent free words only
as an enclosure. No three independently reachable upper histories are
postulated.

The speed-eight Mail paths are the unchanged actual capture paths.
The fixed right F1 strip is [155Q-512,155Q). Checking the literal
arithmetic-progression crossing predicate for every native field bit,
listed source offset and gather gives:

- True right receivers j>=155 erase every source s<=154 and retain
  the known right sources s>=155.
- True left receivers j<=141 retain every known source s<=141;
  every required source s>=155 crosses the fixed right strip and is0.
  Sources142..154 are left free, whether erased or retained.
- Complete foreign receivers h152..154 erase every native source
  s>=155. Their GF sources153/154 are already0 by J250, so all captured
  GF sources>=153 are0. Remaining native fields are left free.

The two probes
[probe_fifth_sources.py](probe_fifth_sources.py) and
[probe_fifth_routes.py](probe_fifth_routes.py) check these path predicates
and the stated margins, including the left-to-right erasure separately.
The healthy infinite tails follow the same route inequalities; the
finite near-defect checks cover every nonuniform native dependency.

## 4. Joint refinement and complete native flags — proved

For the left captures the raw native table through141 is exactly
J250's table. Sources142..154 are unrestricted and sources>=155 are
zero after routing. For any reader t<=141, the two negative distant
blocks are entirely within sources<=133, hence have canonical GF and
Age4. For t<=135 the raw self is itself canonical/4; replacement by a
different pair cannot have three valid block votes because two votes
are already canonical/4. Retention or replacement therefore gives
canonical/4.

For t136..141 the far positive block has only erased GF0 members.
Their five adjusted GF words are distinct moduloQ, so it has no valid
joint triple. The remaining positive block is unrestricted. The only
possible three-valid-block replacement is consequently canonical/4.
Otherwise the raw pair is retained. The post-refinement GF enclosure
is canonical through135, in{0,t} at136..140, and arbitrary at141 and
beyond. This preserves the actual shared J250 values; allowing those
optional choices independently only enlarges the set. Ages after135
remain free. Joint refinement changes GF/Age only, leaving the raw
flag/Workspace bits as captured.

At true left j<=99 every new F1 is0. Near this endpoint the right old
F1 population contains at most two ones, self F1 and WF1 are0, geometry
is canonical and at least three quiet-right positions exist. At
j100..105 the right GF quorum is canonical and at least three inside
right old F1 bits from106..108 are1, so newF1=1.

For j106..139, if no right GF quorum exists, the literal absence clause
forces newF1=1. Otherwise quantify its word v over all1024 values.
The known old right F1 bits at j+d<=141, d1..8, are1 when v+d<Q.
Three suffice; two suffice with the known old selfF1=1. If neither
population suffices, at least three inside left GF words disagree
with v: their post-refinement possibilities are t if t<=135, or
{0,t} for t136..140. The exact34816 receiver/v cases verify this last
alternative. Thus newF1=1 for every possible GF quorum, without any
Age, F2 or Workspace assumption. New F1 at140/141 remains free.

NewF2 is0 through132. The right GF quorum is canonical through132,
since even j132 has the three known right GF words133..135. Thus its
no-quorum source is off. All local old WF2 bits are0, and all left
old F2 bits are0 through132. At132 any possibly free old selfF2 is
erased because newF1=1 and the left population is zero. The far-left
healthy tail has the same zero conclusion. NewF2 after132 is free.

For true right captures, sources<=154 are erased0 and sources>=155
are canonical GF/Age4 with all flags/Workspace0. Every valid distant
joint triple is canonical/4; erased receivers have at most two valid
positive blocks, hence retain raw0. Canonical receivers retain or
select canonical/4. The right native GF quorum is therefore canonical.
The five left mismatches number5/4/3 at155/156/157, giving newF1=1,
and at most two from158 onward, where all other Flag1 sources are0.
All newF2 on the right are0.

For complete foreign h152..154, each right native reader t=h+1..h+5
has captured raw GF0. Its two positive distant blocks consist of GF0
sources, with five distinct adjusted GF words. Both blocks are invalid,
so a three-valid-block replacement is impossible; the reader retains
GF0 regardless of every Age and other captured word. The five right
adjusted GF words are then distinct and have no quorum. The literal
absence clause forces newF1=1 in each complete foreign frame. Their
newF2 is left free; no foreign clock theorem is assumed.

The exact symbolic checks include41 near-left maintenance cofactors,
170 selected right-quorum maintenance cofactors, three full-F31
foreign cofactors and41 full-F31 right cofactors. The latter selected
checks are supplements to the counting/refinement/native proof above,
not a sampled substitute for all free inputs. The actual interpreter
and bounded courier induction in section3 delivers these proved flags
to their corresponding special physical primaries by the deadline.

## 5. Physical aliases and the complete command enclosure — proved

For any physical alias y=jQ+k and holder x=y-s, its possible virtual
primary is (k+512b(x)) modQ. Section2 fixes b=0 outside
[142Q+1,155Q), b=1 on [152Q-512,155Q), and allows both labels on the
remaining interval. A virtual3/1021 can receive the actual Flag2/Flag1
courier; virtual509/515 is ordinary and stays0 from the actual reset.
Each of the five holders starts0; erasures preserve ordinary0.

Consequently MF1021 is the true Flag1 track through141 and from155
onward. Its proved ones are100..139 and155..157. The unknown true
outputs at140/141 and uncertain-phase colonies142..150 give exactly
its11 free votes. At151, y=152Q-3 and all its holders are already in
the definite label1 core; it has virtual509 and is0, as are152..154.

MF509 has only ordinary virtual509 outside142..154. Complete foreign
h152..154 deliver its three ones, while142..151 have ten free voted
outputs. MF3 has true newF2=0 through132 and from155 onward; its true
free outputs133..141 and unknown-phase142..151 give19 free votes.
At152..154 it is ordinary virtual515 and zero. MF515 is ordinary
outside142..154; its13 remaining votes, including the complete foreign
Flag2 outputs, are left free.

The probe checks2080 phase/colony/slot roles over the finite affected
range. The ordinary-alias/reset identity and healthy native tails
extend the zero assertion to every other integer colony. Fixed outputs
are coherent by the proved courier copies and keep1; all partial or
unknown outputs are represented only by their actual binary majority5
vote. Summing gives46 fixed ones and53 free votes, exactly the statement.
Nothing in this count asserts independence or attainability of all
2^53 choices. QED for the restricted reset/prefix/source theorem.

## Evidence, statuses and remaining gaps

The original discovery receipts retain their false physical-lift flags;
they certify cofactors/counts only. The separate final certificate pins
this written physical proof and its parent assets. The default checker
replays without modifying any receipt:

`python3 Report/proofs/unregistered_sp31_fourth_reset/check_fourth_reset_fifth_sources.py`

| Step | Status | Exact scope |
|---|---|---|
| J223/J225/J239/J242/J248/J250 history, native factor, work/courier contracts and banks | previous proved arguments apply | Same actual original fault, arbitrary original upper Info, no later errors |
| Universal common-clock Age/807-bit reset and40 masked alias cases | proved | All other input bits free; no keep/equal-GF premise |
| Actual fourth reset and native quiet-prefix enclosure | proved | Through state4U+TF, Workspace source guard closed on every contributing update |
| Fresh complete work, exact Mail routes and post-refinement captures | proved | True<=141/>=155 and foreign152..154; interior operands enlarged conservatively |
| Complete native flag populations and53-bit physical source enclosure | proved | Actual deadline votes; no free-word reachability or independence claim |
| Selected maintenance/full-F31 cofactor checks | measured supplements | Universal scope supplied by the written counts and physical induction |
| Fifth pulse, complete data state, eventual/general higher repair, Gray/G17/iid/minimum | unproved | No positive noise rate or globally sufficient new construction |
