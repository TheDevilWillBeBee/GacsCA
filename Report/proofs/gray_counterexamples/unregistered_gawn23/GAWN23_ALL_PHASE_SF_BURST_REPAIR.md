# GAWN23: SF-only short bursts at every phase of the unchanged smaller rule

This uses **unchanged frozen GAWN2**, Q4096/U524288/radius8/Word100/h1/
own beta/lambda24/c104 and all its declared departures from Gray.
It supplies an all-phase deterministic burst lemma. It does not supply
general native-changing real1 repair, continuing surrounding E0 errors,
the higher-error induction, a positive iid rate or remembered-bit theorem.
No rule, ROM, constant, CURRENT or earlier frozen asset is changed.

## Exact theorem

Let F be GAWN2 and H2 its actual recursively intact initialization from
GAWN4, with H2=E(cell_words(H2),0). Write Y_t=F^t(H2). Fix
A=[b,b+w) within true colony I=[0,Q), 1<=w<=104. Choose arbitrary
integers 0<=tau<=L<=U-1 with L-tau<=103. On any subset of after-update
rows tau,...,L, overwrite arbitrary cells of A, changing any of the
thirteen SF fields to arbitrary legal values, adaptively. Retain all
six **actual** native fields at each overwrite. There are no other errors.

Then:

1. Actual native Address is canonical and Age=t modU everywhere through U.
   Native flags are0 before96Q and all native fields are quiet by99Q;
   they remain quiet through U. Workspace values during96Q..98Q may differ.
2. A fixed adjacent pair P containing I has protected outer Head endpoints.
   No malformed packet from P can be accepted across either outer boundary.
3. At each early/late Mem load, every outside-pair evaluator frame is a
   seventeen-record D tape equal to the corresponding H2 records except
   possibly upper record0. Different outside evaluators may have different
   erroneous record0 values; no global consistency of these values is needed.
4. Actual early native outputs and completed late Out outside P are correct.
   At U the complete raw row is E(dprime,Bprime), where dprime equals
   cell_words(C1), C1=F(H2), outside P's two adjacent upper indices.
   Inside P arbitrary represented native padding and auxiliary Info are allowed.
5. Complete X_(2U)=Y_(2U), followed by equality at every later tick.

All phases0..U-1 are covered, including bursts crossing a gather/load,
early birth, source window, late birth or final rest boundary. Support
must stay in the fixed A and within one true colony. A longer duration
can affect multiple History banks and is not covered by this theorem.
No original error class is assigned merely from support geometry.

## 1. Exact geometry and actual native quiet — proved antecedent argument applies

Both adjusted Address quorums consist entirely of the canonical value.
Both old Age quorums consist entirely of the correct common clock.
Every native direction selector therefore gives the same correct pair,
independently of flags, Workspace, SF and any old packet value. SF-only
overwrites preserve it. The computed-vs-raw-self GF wipe is always false.
This is GAWN2's geometry argument, now applied through actual overwrites.

Before computed96Q the Workspace guard is closed, and initial zero
flags remain zero: geometry inconsistency, missing-colony and all old
Workspace/flag sources vanish. Overwrites retain those native fields.
During96Q..98Q allow arbitrary Workspace and both native flags.
At actual98Q both Workspace fields are0 globally and remain0 through U.
No SF choice can open their guard with the common correct clock.

GAWN2's exact Flag1 equation with canonical/common geometry and WF0 is

    newF1 = (right-inside count>=3) OR (oldSelfF1 AND right-inside count>=2).

Every true colony's guaranteed zero suffix grows left by at least two
sites per row, starting at its two last sites. All Flag1 is0 afterQ/2.
Now computed Flag1=0 and h1 gives the exact masked Flag2 equation

    newF2 = (left-inside count>=4) OR (oldSelfF2 AND left-inside count>=2).

Each true colony's zero prefix grows right by at least two sites per
row, starting at its two first sites. AnotherQ/2 clears Flag2. Both
sweeps run simultaneously in every true colony; neither needs quiet
flags in adjacent colonies. Thus all native fields are quiet by

    98Q+Q=99Q=405504 <100Q=409600.

This is the actual h1 argument, not Gray's different printed erasure
clause. Common geometry and clock were derived before using the guards.
No native equality during the source window is assumed.

## 2. Coherent normal outputs and protected pair — proved

All five holders of logical y read the same voted operands and have
the same actual clock and canonical service Address y modQ. Wipe is
false. Flag1 affects only the two Mail fields. Consequently every
normal output is coherent for each of the other eleven SF fields,
throughout the period. Before96Q Flag1 is0, so Mail is coherent too.
After-row overwrites may destroy raw coherence. For every logical y
outside A, however, its five holders intersect A in at most two sites;
the vote still equals the preceding coherent normal output. This is
an actual raw-holder identity, not a supplied logical simulation.

Use GAWN22's all-clock endpoint invariant. At logical endpoint0 the
forbidden move bit is bit1, and atQ-1 it is bit0. Reset gives0; birth
is interior; hold preserves the voted zero bit; every active total
step_packet checks targets in[0,Q), and invalid/colliding cases give
movement0. Every normal endpoint output therefore has the forbidden
bit0 if its old vote does. If at most two holders can be overwritten,
the three others preserve that vote through repeated overwrites.
The actual clean H2 history satisfies this invariant before the burst.

Choose P=[-Q,Q) if A contains at least three holders of logical0,
and P=[0,2Q) otherwise. Width<=104 cannot damage three holders at
both endpoints of I. The chosen near endpoint is protected, and the
far endpoint of the added colony has no overwritten holders. No
Head from P can be accepted outside P. Outside evaluators can have
private registers and intermediate Out different from their clean
twins; only their prepared semantics and completed outputs are used.
No all-SF exterior shadow-equality claim is made in the gather window.

## 3. At most one transported History bank is damaged outside the pair — proved

Up to row80Q-2 the actual Info equation is a local old-vote hold.
There is no age0 commit after row0 and no80Q-1 special write yet.
By section2, logical Info outside A, hence outside I, is exactly the
initial I2 word through this prefix. Head, Mail and History cannot
write Info there. Define D_g(y) as the actual voted Info at row

    S_g=0,32Q,64Q, for g=1,2,3.

Each D_g equals I2 outside I. Its values inside I, including auxiliary
positions, may be arbitrary and need not agree between snapshots.

At computed S_g, actual Mail and History_g reset. At S_g+1 both Mail
load D_g, and the central lane captures D_g(y). With Flag1=0 and
canonical common clocks, each subsequent Mail update shifts one logical
site: left Mail reads y+1, right Mail reads y-1. The capture at
S_g+2+abs(j)Q for j!=0 consumes the OLD mail at S_g+1+abs(j)Q.
In a gather unaffected by Mail overwrites, its captured lane is exactly

    History_g(y,j)=D_g(y+jQ), j=-8,...,8.

The source identity follows by induction on the number of shifts;
it includes the centre's distinct S_g+1 capture and both directions.
Flags remain0 through the furthest third capture72Q+2.

A spurious Mail replacement can affect that bank's captures only if
its after-row fault time belongs to the conservative window

    W_g=[S_g,S_g+8Q+1].

Earlier Mail errors are destroyed by the actual S_g reset/load; later
errors occur after every old operand used by that bank's last capture.
Direct History overwrites have logical effect only inside A by section2.
For logical y outside P they cannot change a History vote; captures and
holds regenerate coherent normal History outputs before each overwrite.
Once complete, History_g has no later reset until actual U.

The gap from the end of W_g to the start of W_(g+1) is24Q-1=98303.
Since L-tau<=103, [tau,L] intersects at most one W_g. Thus at least
two banks, for every outside-pair logical frame position, have exactly
the displayed source values. The third bank may be arbitrary. This
is a transported-data argument for the actual history. It does not
assume uncorrupted Mail globally, or that private work stayed in I.

## 4. Actual Mem and executions outside the pair — proved

Fix an outside-pair true colony c, a frame word i, and its logical
primary y=cQ+P1800+i. At both actual72Q+3 and100Q+1 Mem takes the
bitwise majority of the three voted packed History banks. For every
lane j with c+j!=0, the two unaffected banks supply exactly
cell_words(H2(c+j))[i], by section3. Their majority restores this
Word100 regardless of the third bank. For c+j=0 its word is arbitrary.
Hence the complete496-word readonly frame is an actual seventeen-
record D tape with at most record0 corrupted, including native padding.
Each evaluator can use its own such record0: all-records-except0
correctness suffices locally and supplies a legal D tape for S1.

GAWN19's arbitrary single-upper-record correction at H2 applies:
native and SF votes have at least four clean operands, flags/WF
sources cannot turn on, h1 clears a positive self flag, computed age1
closes the Workspace guard and computed Flag1=0 excludes wipe.
Thus F^D of every such tape at centre c is exactly C1(c)=F(H2)(c).
The universal prepared evaluator theorem S1 covers every D record and
both actual entries. Its early outputs are the exact four native words
and zero Workspace; its late outputs are all496 correct words.

Preparation is derived here. At72Q+3 the actual reset gives Head/Out/
Scratch0 and the proved early Mem. At72Q+4 the actual birth gives the
one early-entry packet in every outside-pair colony. Logical Head,
Mem, Out and Scratch votes there follow this prepared execution:
direct SF overwrites cannot change their outside-A votes; Mem is
readonly; a packet from P cannot enter by section2; and the valid
own execution stays inside its496-word frame. The221-update bound
finishes before75Q. No externally prepared early bank is supplied.

At75Q the bounded couriers in every outside-pair colony seed the
correct early native F1/F2 bits, here0. Their routing guards exclude
crossing true-colony boundaries, even for malformed adjacent words;
direct overwrites again cannot alter outside-P votes. They supply
the correct0 sources for the actual80Q-1 Info writes outside P.
This justifies those outside Info values without assuming equality
of the private early execution traces.

At100Q the actual late reset clears Head/Out/Scratch/Mem; at100Q+1
Mem reloads the proved temporal bank and the unique pc0 packet is
born. Section1 gives quiet native flags already at99Q, so every late
native SF dependency is absent. The same holder/endpoint/readonly
argument derives S1's late execution outside P. Its universal104572
bound fits before127Q with the GAWN2 margin6019. All496 completed
Out words there are C1(c). Typed stores affect only that frame;
auxiliary Out outside it stays0 after100Q. Rest and later permitted
overwrites preserve every outside-P logical Out vote until U.

## 5. Actual U encoding and complete2U repair — proved antecedent argument applies

There is no error at U. Every native field is quiet; age wraps to0.
All holders receive the same old Out vote before work resets and the
own Programme bit. Hence the complete raw row is E(dprime,Bprime),
including arbitrary inside-pair upper native padding. Section4 supplies
dprime=cell_words(C1) outside P's two upper indices. No artificial
reset, decoder, new rule or assumed quiet row has been inserted.

GAWN4's universal adjacent-upper-pair identity at actual C1 gives
F(pi(dprime))=C2=F(C1). GAWN2's universal represented-D period theorem
then gives X_(2U)=E(C2,0), which is the actual clean2U row. No later
errors occur, so complete equality holds at every later tick.

## Status and verification scope

Finite supplements cover literal common-geometry kernels with arbitrary
SF/flags, the exact masked flag equations and deadline arithmetic,
all possible short-window start rows, old-mail source/capture identities,
actual temporal Mem loads with incoherent raw holders, and selected
actual early/late own-ROM evaluations on the derived one-record tapes.
The universal proof uses the raw-holder/source/word/packet inductions
above and the proved all-D evaluator, not the selected payload traces.
No full evolving U/2U physical simulation is performed.

| Step | Status | Scope |
|---|---|---|
| Common geometry/native99Q quiet | proved; GAWN2 argument applies | SF-only overwrites; arbitrary actual source flags |
| Eleven normal SF coherence/raw vote protection | proved | Canonical common geometry; Mail separate |
| All-clock protected pair Head endpoints | proved antecedent argument applies | GAWN22; fixed support<=104 |
| At most one transported bad bank/two exact outside-pair banks | proved | Actual reset/load/old-mail captures; duration<=104 |
| Actual Mem has only source record0 arbitrary | proved | Bitwise temporal majority; snapshots may differ in I |
| Actual early/late preparation and completed outside-pair Out | proved | GAWN2 S1 and GAWN19 single-record identity apply |
| Actual U encoding/complete2U/all-later equality | proved antecedent arguments apply | GAWN4 pair identity/GAWN2 S2 |
| Literal kernels/integer identities/selected execution checks | measured transcription supplements | No evolving physical U/2U simulation |
| Native-changing/moving-multiple/longer faults/E0/higher-iid | unproved | No positive noise rate or memory theorem |
| Faithful Gray/G17 refutation/minimum sufficient change | unproved | Existing departures retained |
| Rule/ROM/constants/CURRENT change or commit | none | Frozen assets preserved |
