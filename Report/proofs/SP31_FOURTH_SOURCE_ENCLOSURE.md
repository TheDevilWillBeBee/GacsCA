# SP31: actual fourth command enclosure and the limit of uniform shrinkage

This concerns unchanged isolated F31, Q1024/U475136/r37, the same
J225 native-only original-c16 dense16Q real2 fault, arbitrary original
upper Info and no later errors. It proves an enclosure of the actual
fourth commands. It does not prove their independence or reachability,
an actual fourth endpoint, arbitrary repair or iid reliability. No
rule, ROM, constant, frozen source or active G17 is changed.

## Exact statement

At the actual physical time 3U+TF=1703809 the complete five-copy
native command votes have the following enclosure.

| Physical track | Command1 colonies | Otherwise |
|---|---|---|
| MF509 | 149..151 | 0 |
| MF1021 | 106..147 and152..154 | 0 |

| Physical Flag2 track | Free binary commands | Otherwise |
|---|---|---|
| MF3 | 132..148 | 0 |
| MF515 | 148..151 | 0 |

There are21 free votes and2^21 allowed assignments in the enclosure.
They are a superset of the actual possibilities, not new errors,
independent choices or a prescribed future tape. All subsequent native
flags and Info erasures must still be computed by F31.

The prepared signal pattern studied in J241 is therefore an enclosure
of this actual history. Its translating/growing finite quotient cases
show why this enclosure alone cannot prove a shrinking fourth pulse.
The operational reachability of any of those cases is still unproved.

## 1. Actual quiet prefix and fourth captures — previous proved argument applies

[J239](SP31_THIRD_PULSE.md) proves T(149,152), the common legal native
clock, zero native F2/Workspace and the actual3U fresh private/alias
reset. [J241](SP31_THIRD_BOUNDARY_BANKS.md) proves the required coherent
Info banks of that same physical history. J223/J225's unchanged quiet
template, Workspace guards, earliest actual courier issue and fresh
work/own-ROM induction apply up to the fourth signal deadline. The
physical interpreters start from that reset; no new seed is supplied.

The Flag1 strips are [148Q,149Q-512) and[152Q-512,152Q). Apply the
literal speed-eight arithmetic-progression crossing predicate separately
to every native field bit, offset and one of the three gathers. For
complete left true frames j<=147 it erases sources s>=148, and for
complete right true frames j>=152 it erases sources s<=151. In complete
foreign frames h149..151, whose origin is(h-1)Q+512, it erases sources
s<=148 or s>=152. Every nonzero-distance source reaches its capture
before E0. Direct reads and repeated gathers retain the same physical
bank bit. Thus their temporal vote has the stated single captured
table, without three independent upper histories.

The left table is exactly J241's proper true table through140, its old
partial true141 and its recovered true142..147. Set a in{0,1}, let
q134 be the shared GF word at134, and q141 the shared GF word at141.
After crossing erasure it is

| Source s | GF | Age | F1 | F2 | WF1 | WF2 |
|---|---|---|---|---|---|---|
| <=111 | s modQ | 3 | 0 | 0 | 0 | 0 |
| 112..130 | s | 3 | 1 | 0 | 0 | 0 |
| 131..132 | s | 3 | 1 | free | 0 | 0 |
| 133 | 133a | free | 1 | free | 0 | 0 |
| 134 | q134 | free | 1 | free | free | 0 |
| 135..140 | 0 | free | 1 | free | 0 | 0 |
| 141 | q141 | free | free | free | free | free |
| 142..147 | 0 | free | 0 | 0 | free | free |
| >=148 | 0 | 0 | 0 | 0 | 0 | 0 |

The free entries can be allowed independently as an enclosure, but a
particular physical bank word remains the same on every read. The
right table is canonical GF/Age3/allflags0 at s>=152 and erased0
below. The foreign table has GF0 except one shared word q149 at149;
F2 is0 except its possibly free149 bit. All its Ages, F1 and Workspace
inside149..151 are unrestricted; crossing erasure is0 elsewhere.

## 2. Joint distant refinement retains these raw native pairs — proved

For the left table, a five-site block cannot include both free GF
words134 and141, since their distance is7. Its adjusted zero GF words
are distinct. At most one free word can match one of them, so a
noncanonical word has multiplicity at most2. The optional GF133,
when nonzero, is canonical. Every GF triple is consequently canonical.
Any such triple contains a known Age3 member: the only possible
canonical sources with free Age in one block are133 and134, or141,
at most two. A joint GF/Age triple therefore has canonical GF/Age3.

For a receiver t<=132 its raw pair is canonical/3, so either retention
or replacement gives exactly that pair. For t>=133 both positive
distant blocks have at most two matching GF words: each contains at
most one free word among adjusted zeroes. At most two of the four
blocks can be valid, and a three-of-four replacement is impossible.
The raw pair is again retained, including arbitrary Ages at133 and
beyond. This is a universal shared-word argument. The checker exhausts
all1024 values of the sole free word in every affected block, both a,
and every relevant receiver/center; it never treats a sample of a pair
of GF words as exhaustive.

For the right table a valid joint triple in the canonical part has
Age3 and canonical GF. An erased receiver has at most two valid
positive blocks and keeps its raw0 pair. For the foreign table every
distant block has at most one free GF word among distinct adjusted
zeroes; no GF triple exists at all. Its joint refinement retains every
raw GF/Age pair, with no foreign clock assumption.

## 3. Complete true Flag1/Flag2 outputs — proved

On the left every available native right GF quorum is canonical.
Such a quorum always exists through j129, can exist at130/131 and
cannot exist at any j132..147. Through105, local Ages are3, the eight
right F1 inputs contain at most two ones and at least three quiet
positions, Workspace is0 and selfF1=0; hence newF1=0. At106..129
at least three of those right flag inputs are1, with inside masks1,
so newF1=1. At130/131 either absence of the right quorum forces1 or
the right flag population does. At132..147 absence forces1 directly.
Thus newF1 is1 exactly106..147 in complete left frames.

Through129 source3 is disabled by the right GF quorum. At130/131,
if that quorum is absent, the five left Ages are all3, so source3
is still false. The actual source3 predicate is absence of the right
GF quorum AND the selected left Age's low four bits all1; Age3
does not satisfy it. All11 local WF2 inputs are0 through131, so
source4 is off. Every left F2 input through131 is0. A possibly free
selfF2 at131 is erased by newF1=1 and the zero left population.
Therefore complete left newF2 is0 through131. No value is asserted
for newF2 at132..147.

For complete right frames the right GF/Age quorum is canonical/3.
At152/153/154 the erased left GF words give5/4/3 mismatches and
newF1=1. At155 there are only two mismatches, all right flags and
Workspace are0 and the quiet test gives0. Farther right the healthy
native branch gives0. Source3 is disabled and all old F2/Workspace2
inputs are0, so every complete right newF2=0. Distant refinement's
identity covers the near-boundary cases; the healthy uniform-region
argument covers both infinite tails.

Native five-word GF side-quorum counts are checked separately for
every value of the single relevant free word. Selected maintenance
and full-F31 cofactors keep other Ages/flags/private/instructions free
and supplement the universal count/population proof. They are not a
reachability test.

## 4. Foreign, partial and ordinary-alias commands — proved

For every complete foreign h149..151 the five native right adjusted
GF words are distinct zero-source adjustments. No right quorum can
exist, and newF1=1 independently of every other native or private
field. Its actual held operands, fresh work, unchanged own programme
and bounded courier deliver that1 to physical MF509(h). No foreign
Age is characterized. In particular, the modal Age fallback may
select a free word with its low four bits all1; the old source3-off
argument cannot be reused. NewF2 is left free in all three frames,
giving MF515 in physical colonies148..150.

The partial true frame148 contributes the single free MF3(148) vote.
The partial foreign frame152 contributes free MF515(151). No interpreter
correctness is assumed for either. As in J225/J238, the actual deadline
five-copy equation gives each a single binary voted command; no later
command is supplied by hand.

For each phase3/509/515/1021 primary and its five holders the pre-pulse
GF labels agree, with wrong GF on[149Q-512,152Q). Their virtual phases
give the following special-write roles:

| Physical phase | Special-write colonies | Ordinary elsewhere |
|---|---|---|
| 3 | j<=148 or j>=152 | virtual515 |
| 509 | 149..151 | virtual509 |
| 515 | 148..151 | virtual515 |
| 1021 | j<=147 or j>=152 | virtual509 |

The ordinary aliases start0 at the actual3U reset and retain0. The
partial right Flag1 aliases therefore introduce no free Flag1 bit.
All complete special outputs are the values proved above, transported
by the actual unchanged programme/couriers. Combining these roles
with the two partial Flag2 votes proves exactly the statement. QED
for the source enclosure.

## 5. What this enclosure cannot prove

J241's unchanged finite native/actual-Info factor starts at T(149,152)
with precisely this enclosure. Its already retained four corner
measurements run6144 updates and retain every subsequent actual Info
erasure. Masks0,131071 and1966080 end T(152,155), width3584 unchanged,
translated3Q. Mask2097151 ends T(146,155), width9728, growing6144=6Q.
No fourth mask is shown reachable in the original physical history.
These measurements do not prove an operational defect or noise failure.
They do show that a shrink assertion allowing every enclosure member
cannot be obtained from these bounds alone.

The missing repair step is more precise now: source/capture/alias
derivation is proved, whereas actual clock constraints, command
correlations or a different multi-period repair invariant must still
exclude or handle the nonshrinking cases. Setting all optional Flag2
commands0 is insufficient to prove shrinkage in this fourth pulse.
No smallest sufficient global rule or constant change follows from
this local obstruction.

| Step | Status | Scope |
|---|---|---|
| Quiet3U/reset, actual banks and frozen interpreter/courier induction | previous proved arguments apply | J223/J225/J238/J239/J241, same history |
| Fourth native captures and shared-word joint-refinement identity | proved | Literal crossing predicate and quorum counts |
| True/foreign Flag1, proved-zero Flag2, partial and alias roles | proved | Native clauses and actual programme/deadline coupling |
| Actual full fourth21-bit command enclosure | proved | All original upper Info/no later errors |
| Four finite fourth quotient corners | measured only | Retained J241 exact executions; reachability unproved |
| Uniform shrink inferred from this enclosure | unavailable | Enclosure contains the translating/growing cases |
| Reachable command masks, actual fourth endpoint, general higher repair/iid/minimum | unproved | No global reliability theorem |
