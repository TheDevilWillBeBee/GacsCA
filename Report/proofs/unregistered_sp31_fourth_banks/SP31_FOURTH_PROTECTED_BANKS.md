# SP31: protected fourth-boundary native banks

This is a restricted physical bank theorem for unchanged isolated F31,
Q1024/U475136/r37. It uses the same actual J225 native-only original-c16
dense16Q real2 fault, arbitrary original upper Info and no later errors.
It asserts neither a complete4U upper state nor fifth-period commands,
eventual repair or iid reliability. G17, CURRENT, all rules and ROMs are
unchanged.

## Exact statement

At the computed boundary4U=1900544 the protected true frames have the
following coherent five-copy normal native Info words. The quantities
a in{0,1}, q134 and q141 are the actual shared third-boundary quantities
of [J242](../SP31_FOURTH_SOURCE_ENCLOSURE.md). Their values are not
prescribed, sampled independently or proved reachable.

| True frame j | GF | Age | F1 | F2 | WF1 | WF2 |
|---|---|---|---|---|---|---|
| <=105 | j modQ | 4 | 0 | 0 | 0 | 0 |
| 106..131 | j | 4 | 1 | 0 | 0 | 0 |
| 132..135 | j | 4 | 1 | free | 0 | 0 |
| 136 | 136 if a=1 or q134=134; otherwise0 | free | 1 | free | 0 | 0 |
| 137 | 137 if a=1 and q134=134; otherwise0 | free | 1 | free | 0 | 0 |
| 138..140 | 0 | free | 1 | free | 0 | 0 |
| 141 | q141 | free | 1 | free | free | 0 |
| >=155 | j modQ | 4 | 0 | 0 | 0 | 0 |

The new foreign GF/F1/F2 bank primaries

    (h-1)Q+571..580, (h-1)Q+600, (h-1)Q+601, h153..155,

are all zero and coherent. There are36 such primaries, or180 physical
Info copies. The interior true banks142..154, old foreign h152,
foreign Age/Workspace banks, all other SF/Info and a complete fifth
source supply remain unrestricted by this theorem.

## 1. Actual protected interpreter work — proved by the existing physical induction

[J248](../unregistered_sp31_fourth_ternary/SP31_FOURTH_NATIVE_ENCLOSURE.md)
encloses the actual wrong-GF support throughout the fourth pulse and
quiet suffix in [142Q+1,155Q). Outside that hull raw GF is canonical,
and the lower Age is the actual common legal clock. On either exterior
side, the two distant blocks farther into the exterior are canonical.
An inward block can have a different valid pair, but the two inward
blocks cannot provide three votes for it. The joint refiner therefore
either retains the canonical raw pair or replaces it with that same
pair. The actual computed GF is canonical by the enclosure. Thus
computed GF equals refined self-GF and the copy keep is1 there.

The unchanged listing's interpreter work phases lie in [58,966).
For j141 the largest work holder plus its native refinement radius is

    141Q+965+2+37 =145388 <142Q+1=145409.

For j155 the smallest is155Q+58-2-37=155Q+19. The same margins protect
every work phase for j<=141 and j>=155 at every pulse/quiet tick.
This is a native-field and no-wipe premise, not an assertion that an
arbitrary SF perturbation has a small causal cone.

J239 supplies the actual fresh3U reset. J242 supplies the complete
fourth captures and the correctly running complete-frame interpreters
up to TF. Reuse J223's physical five-copy, pending, typed-front,
register/scratch, Match and own-ROM induction on these protected work
phases: the position/common clock and keep premises remain valid, the
capture operands are already held, all guarded interpreter references
and scheduled work destinations have the unchanged bounds, and the
total/unique-arrival controls are unchanged. In particular this reuses
the guarded-front induction; the radius inequality alone would not
justify ignoring an incoming SF head. The824 conditional SF/core
identities are used only with the actual supplied native outputs.
Later native Mail erasures cannot replace completed captures.

This establishes execution of the actual full-F31 Boolean function on
J242's held operands in the protected frames through the literal Hold
commit. No interpreter correctness is assumed in the interior frames.
The fresh-frame/typed-front induction is the one already used for
[J241's third protected banks](../SP31_THIRD_BOUNDARY_BANKS.md), with
the newly proved hull and the verified fourth work margins substituted.

## 2. Native output table — proved

Use J242's exact captured left and right tables, including crossing
erasures. Its joint distant-refinement identity retains every raw pair
of these tables. In particular it holds for arbitrary shared q134,
q141 and every free Age or flag; their seven-cell separation prevents
one five-site block from containing both free GF words.

J242 already proves newF1=0 through105, newF1=1 at106..147, and
newF2=0 through131. On the right it proves canonical GF/currentAge3
and all output flags zero from155 onward. These previous conclusions
apply unchanged to the protected receivers here.

Every available native side GF quorum on the left is canonical. A
right quorum always exists through129, is optional at130/131 and
is absent from132 onward. A left quorum always exists through135;
at136 it exists exactly when a=1 or q134=134; at137 it exists exactly
when a=1 and q134=134; it is absent at138..141. These counts follow
by counting the five adjusted GF words in J242's table. A noncanonical
triple cannot occur: among the distinct adjusted zero words a single
free word matches at most one, while every repeated known nonzero word
is canonical. The right five-site neighborhood at136..141 has at most
one free q141 among these distinct adjusted zeroes, so has no quorum
for every q141. The checker exhausts every sole relevant free word on
each side; it does not substitute selected simultaneous q134/q141
pairs for this universal argument.

The literal directional selector is

    vote_right = right_GF_quorum_exists AND (NOT newF1 OR newF2).

Consequently an absent right quorum forces the left choice, independently
of every free Flag2. At132..135 the left choice is canonical. At136/137
it is canonical precisely under the conditions above and otherwise
falls back to raw self-GF0. At138..140 the absent left quorum falls back
to raw0, and at141 to raw q141. Through129 any chosen side is canonical;
at130/131 newF1=1 and newF2=0 force the canonical left choice. This
proves the GF table without choosing the unknown Flag2 bits. The exact
maintenance cofactors additionally leave every old F2, Age and Workspace
symbolic. Their enumeration is exhaustive in the sole free GF word per
dependency window; separate no-right-quorum counting makes q141 irrelevant
to the earlier receivers. Hence every joint pair of shared words is covered.

Current Age is3 through135. Through129 both side Age majorities have
at least three known3 entries. At130/131 the just-proved selector forces
the left choice, and beyond131 no right GF quorum exists. The left GF
quorum is present through135, so the coupled-left-clock fallback cannot
replace the selected left Age. At133/134/135 the five left Ages have
respectively five/four/three known3 entries, and earlier left votes also
have a3 majority. The literal increment therefore gives Age4.
Ages136..141 remain free.

For WF1 the output GF through140 is belowQ-5, closing its right-end
guard. At141 q141 may instead be nearQ-1, and current Age is free;
WF1 must remain free. NewF1=1 suppresses WF2 at106..141. In the
left healthy tail and right protected tail current Age3 closes both
Workspace time guards. This gives all stated Workspace words.

The symbolic checker covers22598 q134 native cofactors and24576 q141
cofactors with all other captured fields free, and30874 side-quorum
cases.324 selected left and36 right full-F31 cofactors supplement
the universal table/refinement/guard proof; these selected full checks
are measured supplements. They are not evidence about reachability of
the free words or a complete upper successor.

The physical composition in section1 and the literal masked Hold
commit put precisely these output bits into their five coherent
normal Info copies. Common legal lower clock is0 at4U; the displayed
Age4 is represented upper data, a different field and level.

## 3. New foreign zero GF/F1/F2 banks — proved

At3U all private Holds are0. Each GF/F1/F2 target has exactly one
own-ROM Hold issue at its native virtual phase59..68/88/89 and one
at the opposite phase571..580/600/601. The former issues, including
their materialization, are before TF; the latter issues are after
TF+6144. The checker scans the raw ROM as well as the actual frozen
listing for these24 target-phase records. No such issue occurs during
the fourth pulse.

Before the pulse the36 new foreign targets have canonical true GF:
all are to the right of the old wrong-GF endpoint152Q. Their virtual
phases are consequently the late opposite phases, so their reset
Hold remains0. Throughout the pulse adjusted GF remains one of the
two phases0/+512, with common legal Age. Reuse J227's one-kind
pending and Match-guard proof: a voted pending store cannot manufacture
a Hold opcode from distinct scratch kinds, and simulated instruction
data cannot replace the physical own-ROM instruction. Thus arbitrary
work or data in these changing frames cannot create a missing Hold
issue. Wipes and votes preserve0.

At native fixed point row3698, J248 proves wrong-GF label1 throughout
[152Q-512,155Q). Every one of these36 primaries, all five holders
and radius37 margins lies strictly inside this definite-one interval.
Its virtual phase is therefore59..68/88/89 thereafter through4U.
The corresponding Hold issue has already passed, and the future
opposite-phase issue cannot address it. Refined and computed GF agree
at the target margins, so keep is1; the voted Hold remains0. The
literal virtual-phase mask at commit includes these normal primaries,
and forwards0 to every Info copy. This reasoning asserts no correct
interpreter execution or characterized Age/Workspace in these frames.
The old foreign h152 is excluded because its pre-pulse phase/history
does not give this reset/no-early-store argument.

## Status and limits

| Step | Status | Scope |
|---|---|---|
| Actual captures, fresh3U work, native exterior hull/fixed core | previously proved arguments apply | J223/J239/J242/J248; same original physical history |
| Protected actual interpreter continuation | proved by the existing physical induction | Explicit keep/clock/work margins and guarded-front hypotheses |
| Protected true native output/Workspace table | proved | Shared-word counting plus exhaustive symbolic native cofactors |
| Selected full-F31 cofactors | measured supplements | No reachability or full-state claim |
|36 newly foreign zero GF/F1/F2 primaries | proved | Own-ROM/no-manufactured-pending issue/fixed-core/commit |
| Interior banks, all foreign Age/Workspace, complete4U Info/SF | unproved | No complete fourth upper successor |
| Fifth command supply, eventual/general higher repair, iid epsilon, minimum change | unproved | No global reliability or Gray/G17 refutation |

Read-only replay:
`python3 Report/proofs/unregistered_sp31_fourth_banks/check_fourth_banks.py`.
