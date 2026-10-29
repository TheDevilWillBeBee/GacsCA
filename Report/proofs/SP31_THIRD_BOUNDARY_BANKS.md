# SP31: protected third-boundary banks and the fourth-pulse obstruction

This is a restricted bank theorem for unchanged isolated F31,
Q1024/U475136/r37, the actual J225 native-only original-c16 dense16Q
real2 fault, arbitrary initial upper Info and no later errors. It does
not prove a fourth command enclosure, a fourth actual pulse, arbitrary
repair or iid reliability. G17 and all frozen rule/ROM sources stay
unchanged.

## Exact statement

[J239](SP31_THIRD_PULSE.md) gives the actual third endpoint T(149,152)
and quiet native/reset boundary at3U=1425408. At that same boundary,
the complete protected true frames have these coherent normal native
Info words. Write a in{0,1} and q for the shared quantities in
[J238](SP31_THIRD_SOURCE_ENCLOSURE.md); they are not prescribed anew.

| True frame j | GF | Age | F1 | F2 | WF1 | WF2 |
|---|---|---|---|---|---|---|
| <=111 | j modQ | 3 | 0 | 0 | 0 | 0 |
| 112..130 | j | 3 | 1 | 0 | 0 | 0 |
| 131..132 | j | 3 | 1 | free | 0 | 0 |
| 133 | 133a | free | 1 | free | 0 | 0 |
| 134 | q | free | 1 | free | free | 0 |
| 135..140 | 0 | free | 1 | free | 0 | 0 |
| >=152 | j modQ | 3 | 0 | 0 | 0 | 0 |

The old partial true frame141 remains unrestricted. At normal GF/F1/F2
primaries of recovered true frames142..148 the Info words are zero;
their Age/Workspace words remain unrestricted. In the surviving foreign
GF bank, at physical primaries (h-1)Q+571..580, h149..152, every word
is zero except one unrestricted ten-bit word at h149. The corresponding
foreign F2 bank at (h-1)Q+601 is zero except possibly h149. These
statements include the current partial frames and assert no correct
interpreter execution there. Every described bank has coherent five
copies. No complete foreign Age/Workspace bank is characterized.

## 1. Actual protected work — previous proved argument applies

All4096 executions of J239 have all-row GF hull[144896,155648), that is
[142Q-512,152Q). Outside it raw GF is canonical and Age is the actual
common legal clock. For an exterior cell two distant blocks lie farther
in the canonical exterior, so a three-of-four replacement can only give
the canonical pair; otherwise its canonical raw pair is retained.
Computed GF equals refined self-GF there, so the actual copy keep is1.
This is J238's exterior argument with the checked third hull.

The true work of j<=140 and j>=152 is protected throughout the pulse.
Actual third captures already precede TF. J223's unchanged fresh-frame,
824 conditional SF/core identities and own-ROM execution therefore
carry their actual held operands and interpreter through the pulse and
quiet suffix. Later Mail erasure does not replace those operands. The
statement concerns the actual original physical history, not a future
upper-state tape or newly initialized registers.

## 2. The actual protected true output table — proved

Use exactly J238's captured third true table, with all crossing sources
s>=141 erased on the left and s<=148 erased on the right. J238 proves
joint distant refinement retains every raw native pair of this table.
That universal identity is reused, not inferred from sampled clocks.

For left receivers through132 the selected GF is canonical. Receivers
through130 have new F2=0 by J238. Their selected left Age is2, including
124, whose old free self Age is not the selected left word. At131/132,
the left side has respectively four/three known canonical Age2 entries,
so its selected Age is2 even though new F2 may be free; an available
right choice also has that clock. Increment gives3. At133 a left GF
triple exists precisely when a=1, giving133; otherwise GF falls back
to its raw0. No right GF triple exists there. At134 neither side has a
GF triple, and GF is its raw q. At135..140 neither side has a GF triple
and raw GF is0. Unknown Ages and F2 remain unknown in these rows.

J238 already proves F1 is1 exactly112..140 on this left side. The
right captures have canonical GF/Age2 and zero flags/Workspace at
every surviving source152 and above, giving canonical GF/Age3 and
zero flags there. The literal masked Hold commit supplies the coherent
physical Info bank words.

Workspace zeroes use the actual output guards. Every left output GF
except q at134 is belowQ-5. At every left receiver112..140 F1=1,
which suppresses WF2. For the quiet remaining rows the selected current
Age2 is outside the source interval. At134 GF may instead be nearQ-1
and Age is unrestricted; WF1 is therefore left free. It is not set to0
by the proof. The checker exhausts both a and every q at all receivers
whose native dependency contains q, leaving every free Age/flag
symbolic; selected full-rule cofactors supplement these guard facts.

## 3. Recovered true and surviving foreign GF/F1/F2 banks — proved

All private Holds reset at2U. True native GF phases59..68/F1phase88/
F2phase89 have their sole own-ROM Hold issues before TF. Their opposite
phases571..580/600/601 have sole issues after S=TF+6144. The frozen
listing and raw ROM are checked for both phases. No such issue occurs
during the third pulse. J227's one-kind pending/Match guard argument
excludes a manufactured Hold issue for arbitrary actual work/data.

The true bank targets j142..148 change from foreign to true during the
pulse. Their old opposite-phase issue is late, their new native issue
is already past, and both phases have no pulse issue. Thus their Hold
is still0 at S. Their five-copy/radius37 target margins are then inside
the quiet true region, so later stores cannot reach these targets.
Voted Hold and masked commit give the stated recovered zero banks.
No correctly completed old foreign interpreter is assumed.

The foreign targets h150..152 analogously change from true to foreign.
Their old true virtual phases571..580/601 have late issues, and their
new foreign virtual phases59..68/89 have passed. The same exclusion
and quiet foreign target margins give GF/F2 zero there. The old partial
foreign h149 remains unrestricted; its ten GF bits form one shared
word, and its F2 bit one shared bit. Hold votes/commit make all stated
banks coherent. There are84 recovered true zero primaries,40 foreign
GF primaries (30zero/10free), and4 foreign F2 primaries (3zero/1free).

Age and Workspace stores do not have this early/late separation:
native Age/Workspace issues themselves occur after the pulse. This
argument cannot supply their values. In particular, the previous
four-protected-foreign-clock premise has disappeared.

## 4. Prepared fourth enclosure: shrinking is not universal

Separate exploratory drivers retain a proposed fourth signal superset:
MF509149..151=1, MF1021106..147/152..154=1, MF3132..148 free and
MF515148..151 free, everything else0. Its21 bits are **not yet proved
to enclose the actual physical fourth commands**. The protected-bank
theorem above alone neither derives all its captures/partial aliases
nor shows which assignments are reachable.

Four exact executions of the unchanged native/voted-Info factor start
at T(149,152), with the actual erasure equations retained. Masks0,
131071 (all true free commands1), and1966080 (all foreign free
commands1) end T(152,155), still width3584. Mask2097151 (all free
commands1) ends T(146,155), width9728, an increase6144=6Q. These are
**finite quotient measurements**, replayed without a rule change.
They are not actual fourth physical histories or noise counterexamples.
They do refute the proposed assertion that *every* assignment in this
prepared superset shrinks the native defect.

The accompanying sound-domain diagnostic stops at row171/x152066
when right GF1 and left GF0 have an undetermined F2 selector. That is
loss of precision, not a trajectory failure. Its partial state and
all rows are retained. The result calls for actual Age/partial-source
information or a different repair argument; repeating all-mask
shrinkage is not justified. Even the all-zero optional command case
only translates the defect in this finite pulse, so eliminating free
Flag2 alone does not prove fourth-pulse shrinkage.

| Step | Status | Scope |
|---|---|---|
| Actual third pulse/quiet3U and raw refinement identity | previous proved argument applies | J238/J239, same original error/all upper Info |
| Proper true native/Workspace banks at3U | proved | Physical interpreter/actual captures/native guards |
| Recovered true zero and one-exception foreign GF/F2 banks | proved | Own-ROM/pending/quiet Hold/commit identities |
| Selected full-rule cofactor checks | measured supplements | Universal table/refinement/guard argument covers unknowns |
| Four prepared fourth native/Info pulses | measured only | Exact finite quotient, masks not proved reachable |
| Universal shrinkage in that prepared21-bit superset | disproved by the finite quotient instances | No physical or iid conclusion |
| Actual fourth commands/pulse/full successor/general higher/iid/minimum | unproved | No global reliability theorem |
