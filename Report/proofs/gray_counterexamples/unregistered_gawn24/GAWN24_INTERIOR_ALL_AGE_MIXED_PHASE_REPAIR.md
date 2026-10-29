# GAWN24: interior address-preserving mixed bursts across the work period

This is a theorem about **unchanged frozen GAWN2**, Q4096/U524288,
radius8/Word100/h1/own beta/lambda24/c104, with all its declared
departures from Gray. It adds no transition, programme or constant.
It is not a positive-rate random-noise theorem. G17 is unchanged.

## Exact statement

Let F and H2 be GAWN2 and its actual recursive initializer from GAWN4,
and Y_t=F^t(H2). Fix I=[0,Q) and an integer interval

    A=[b,b+w) subset [1,Q-1), 1<=w<=104.

Choose 0<=tau<=L<=U-1-R=514049, L-tau<=103, with R=10238.
On any subset of after-update rows tau,...,L replace any cells of A
adaptively. Retain their actual Address; every other native field and
all thirteen SF fields may be arbitrary legal values. In particular
replacement Age is any0..U-1, and internal clocks may wrap. There are
no other errors. At tau=0 an overwrite is applied to the initializer.

For every such history:

1. Address remains canonical everywhere. Outside I, actual Age is the
   physical row modulo U; Flag2 and both Workspace fields are0. Flag1
   may differ only in I and its left adjacent colony.
2. Both true-colony Head endpoints of I stay protected. Outside I,
   the early and late evaluator tapes equal the corresponding seventeen
   H2 records except possibly record0. Completed early native outputs,
   couriers, source Info bits and late Out outside I are correct.
3. Put B=max(L+Q-2,98Q). All native fields are correct/quiet by

       q=B+Q+Q/2=max(L+10238,407552)<=U-1.

   They remain quiet through the actual U commit.
4. X_U=E(dprime,Bprime), with dprime=cell_words(F(H2)) outside upper
   physical cell0; its record0 and auxiliary Info inside I may be arbitrary,
   including represented native padding. Complete raw X_(2U)=Y_(2U),
   and equality holds at every later tick.

This includes the gather, early-computation, courier, source, late-
computation and rest phases up to the stated last-fault bound. The
interior restriction excludes the two physical boundary sites0,Q-1;
it preserves the two endpoint voting quora. It does not assert that
support geometry alone makes a set an original-c104 real1 error.
Address-changing or boundary-touching arbitrary-SF bursts, faults after
514049, multiple supports, surrounding E0, the higher-error induction
and positive epsilon remain open.

## 1. Canonical Address and both packet shields — proved

Every adjusted Address in both native voters is canonical; either
direction returns x modQ. Retaining Address preserves this induction
through overwrites. The computed-vs-raw-self GF wipe is always false.

The holders of logical endpoint0 are[-2,2]; A misses physical0 and
all negative holders, hence can overwrite at most two. The holders
of logical endpointQ-1 are[Q-3,Q+1]; A misses physicalQ-1 and the
two right exterior holders, again leaving at least three.

GAWN22's all-clock endpoint argument applies separately to every
normal holder output: reset gives movement0, birth is interior, hold
preserves the voted forbidden bit, and active total step_packet cannot
give an outward move at service Address0 orQ-1. Its malformed/collision
branches also give movement0. Initially the forbidden bit is0.
After any normal update all five outputs have that bit0; each overwrite
can alter at most two. Induction preserves the voted zero bit on every
row despite different clocks. No packet can leave I across either edge.
No assumption of clean private registers or traces is needed.

## 2. Native exterior before96Q — proved antecedent argument applies

GAWN6's one-step invariant applies whenever the correct exterior
successor clock is below96Q: canonical GF, correct outside Age,
outside F2/Workspace0 and F1 confined to I and its left neighbor.
Its word proof permits arbitrary inside clocks, flags, SF and wrap.
The actual exterior Workspace guard is closed. Its premises hold
before the first fault, and replacements retain Address and stay in I.
Thus the invariant holds through the actual row96Q-1.

For logical y outside I at least three holders lie outside I. These
holders have the same correct computed clock and service Address,
and no wipe. For eleven SF fields other than Mail, their normal
outputs equal the intended common-clock logical equation, independent
of their possibly nonzero Flag1. The other two holder outputs may be
arbitrary. There is no direct overwrite outside A; any overwrite can
alter at most two holders of y. Consequently the outside-I logical
vote follows that actual equation. Incoming Head from I is excluded
by section1. This is a three-actual-holder induction, rather than a
globally coherent raw row or an imposed execution trace.

Until80Q-1 Info receives its old vote on every outside holder; the
successor clock is positive after row0 and has neither Info event.
At row0 the direct overwrite also affects at most two outside-I
holders. Thus every voted Info outside I equals initial I2 through
80Q-2. This includes all three source snapshot rows0,32Q,64Q.

## 3. Two actual gather banks and early preparation — proved

Write W_g=[S_g,S_g+8Q+1], S_g=0,32Q,64Q, for the conservative
old-Mail capture windows. These are the actual windows proved in
GAWN23: reset at S_g, Mail load and centre capture at S_g+1, and
remote lane j capture at S_g+2+abs(j)Q using old Mail one row earlier.
Successive window gaps are24Q-1=98303.

First suppose tau<=72Q+1=294913, the end of W_3. The last possible
fault is at most tau+103. GAWN21's tagged/front proof can be applied
with the same absolute-reference requirement below96Q, rather than
its old below32Q bound: tags use the correct clock or F1=1; the
actual tagged normal-output WF2 gate is closed whenever the correct
clock is below96Q, including arbitrary wrong internal clocks. WF1
can remain arbitrary until all clocks recover. F2's h1 zero front,
the first-three/prefix argument and final F1 sweep give quiet by

    q_early=L+10238<=305254<75Q<96Q.

There is no new early full-U conclusion being imported from GAWN21;
only its native induction is used. After q_early the native fields
stay quiet until96Q because the correct clock guard remains closed.

The entire interval[tau,q_early] has endpoint distance at most10341,
less than98303, so it meets at most one W_g. If q_early<S_g, the
actual subsequent reset/load is performed globally with canonical
common clocks and zero F1; Mail shifts then capture the snapshot
D_g(y+jQ), where D_g is actual voted Info at S_g. D_g equals I2
outside I. If tau>the end of W_g, every old capture operand was
already consumed before the first overwrite; at tau equal to the
last capture's output row, that normal capture also precedes the
overwrite. The resulting History votes outside I are retained by
the three correct-clock holders. Arbitrary inside holder resets,
captures or holds cannot change those votes. A directly overwritten
History copy also affects at most two outside-I holders.

Consequently at least two banks, at every outside-I primary frame
position, contain the displayed snapshot words. Wrong Info inside I
and its two snapshots can be different. The third bank is unrestricted.
This includes F1-induced Mail suppression in the left adjacent colony:
all native disturbance on the capture prefix is inside the same
short time interval, and unaffected later resets/load remove it.

If instead tau>72Q+1, all outside-I banks were already captured in
the actual clean history before the first fault, including a normal
last capture at row72Q+2 if that is tau. Their votes stay fixed under
the same three-holder History equation. All three banks are then good.
No native-recovery deadline is needed for this case's bank argument.

At actual72Q+3 Mem takes the bitwise majority of the three voted
History banks. For each outside-I evaluator every source record
except upper cell0 is restored word for word. Record0 may be arbitrary
and need not agree between evaluators. This supplies a legal seventeen-
record D tape locally, including arbitrary native representation padding.
If the burst starts later, the previously prepared Mem is simply held.

GAWN19's universal one-upper-D-cell identity at actual H2 applies
locally to each tape: F^D gives precisely C1=F(H2). S1's all-D early
contract gives the correct native outputs, here Flag1=Flag2=0, in
at most221 updates. Actual72Q+3 reset and72Q+4 birth derive its
preparation outside I; the three correct-clock Head/Mem/Out/Scratch
holders and both protected edges derive its subsequent execution.
Direct overwrites of I never alter those outside votes. Thus the
early Out is complete before75Q regardless of private work in I.

At75Q outside couriers seed the correct0 flag bits. Their actual
routing clamps at true-colony bounds, and cannot import even an
arbitrary inside-I courier. The same three-holder equation gives
correct outside courier votes through80Q-1. Actual outside Info
writes at Addresses3,Q-3 therefore write0, their initial I2 values.
All other outside Info is held. This proves complete voted Info
outside I equals I2 through96Q-1, without assuming clean inside work.

## 4. Exterior through the source window — proved

Now extend section2's invariant through U-1, including96Q..98Q.
Before each update assume correct outside clocks, outside F2/WF0,
F1 confined to I and its left adjacent colony, and voted Info=I2
outside I. GAWN6's Address/F1/F2/Age word arguments use the old
outside Workspace fields, and give the same correct native successors;
they do not require the new Workspace guard to be closed.

For any outside true colony, its source coordinates at Addresses3
andQ-3 are outside I and have voted Info0. At a successor clock in
96Q..98Q, computed_primary at either coordinate reads that old Info
vote: neither age0 nor80Q-1 applies, and wipe is false. The native
fields at that source are the correct computed fields just proved.
Hence **the actual new Workspace outputs are0 outside I even though
their age guard is open**. This uses the derived early courier/Info
identity; it does not suppress or prescribe a source command.

The new outside Info is an old-vote hold because this clock range
has no Info event. The same induction covers later rows before U,
whose Workspace guard is closed again. Overwrites are only in I.
The native exterior and exact Info therefore persist through U-1.
No circular future-source premise is used: early data/Head/courier
execution was established entirely before96Q, using the closed-guard
exterior, and the source-window induction uses its attained Info row.

## 5. Arbitrary-clock global recovery by q — proved

After the last possible overwrite L, GAWN8's right-suffix tag
argument applies with correct exterior clocks and F1=0 to the right
of I. All of I is tagged by L+Q-2 and remains tagged. Its proof is
independent of absolute phase, internal clock wrap, WF, SF and F2.

Put B=max(L+Q-2,98Q). On that normal output row every inside site
is tagged. If its tag is the correct Age B, its Workspace guard is
closed; if F1=1, the explicit WF2 Flag1 gate is closed. Thus actual
WF2 is globally0 on row B and remains0 thereafter. No global WF1
conclusion is used at B. Every reference row through q is below U.

The actual h1 equation with WF2=0 gives newF2=0 whenever all five
old left F2 bits are0, regardless of F1 or WF1. Starting from the
zero left exterior, a zero prefix covers the first min(s,Q) inside
sites on row B+s. Tags persist. Once that prefix reaches Addresses
0,1,2, each has at least three correct left clock witnesses; tagged
right witnesses either give a correct right quorum or force F1=1
to select the clean left quorum. Their clocks are correct at B+3
and persist. For each subsequent prefix site, its five left clocks
are correct with at least three left-inside witnesses; a missing or
wrong right quorum forces F1=1. This is precisely GAWN21's first-
three and clock-prefix word argument, with its premises derived here.

All clocks and F2 are correct by B+Q. On that actual output row the
correct clock exceeds98Q, so both Workspace fields are0 globally.
The remaining F1 equation is the masked3-on/self2-keep equation;
all true-colony zero suffixes grow by at least two per row. Within
Q/2 further rows every native field is quiet. Hence

    q=max(L+4094,401408)+6144
     =max(L+10238,407552)<=524287=U-1.

Correct common geometry, quiet flags and the closed guard then
persist through U, including the final wrap. This is the actual h1
argument, not Gray's different printed erasure predicate.

## 6. Late execution, actual U and complete2U — proved

Outside-I History votes have no further reset/capture before U.
Section4 gives their three holders the actual reference clock, so
they retain the banks from section3 even while inside clocks perform
arbitrary premature gathers. At actual100Q+1 temporal Mem reload
therefore restores every nonzero upper source record again. Record0
may be arbitrary. Actual100Q reset and100Q+1 birth give the correct
late preparation outside I. Wipe remains false; F1 affects only Mail,
not Head, Mem, Out or Scratch. The same three-holder/read-only/endpoint
induction supplies S1's complete496-word evaluation outside I. Its
104572-update universal bound finishes before127Q, with6019 margin.
Stores are confined to the frame; auxiliary outside Out stays0.
Rest and any permitted inside overwrite retain these completed votes.

At actual U, section5 gives globally correct native inputs. Every
holder has computed clock0 and canonical Address. Old Out commits
before Head/Mem/History/Mail/courier/Out/Scratch resets; Programme is
the actual own beta. Thus the full raw row is exactly E(dprime,Bprime),
with dprime equal to cell_words(C1) outside upper physical cell0.
The bad record may contain arbitrary represented native padding.

GAWN6's universal single-upper-cell correction at C1, or GAWN4's
adjacent-pair identity restricted to one damaged cell, gives
F(pi(dprime))=C2. GAWN2 S2 supplies the complete represented-D period
F^U(E(dprime,Bprime))=E(C2,0), equal to the clean2U row. No later
errors occur, so determinism gives all-later complete raw equality.

## Status and limits

| Step | Status | Scope |
|---|---|---|
| Canonical GF/both actual Head endpoint shields | proved | Address retained; A misses physical0,Q-1 |
| Pre96Q native exterior/three-holder logical equations | proved antecedent argument applies | Arbitrary internal clocks/SF/wrap |
| Two actual gather banks/early tape/Out/courier/source Info | proved | Short native-disturbance interval or already captured banks |
| Native exterior through open Workspace window | proved | Derived actual computed-primary source0, not a closed guard |
| Tagged WF2 deadline B/front/clock/native deadline q | proved | WF1 unrestricted until clocks recover; h1 required |
| Actual late preparation/U encoding/complete2U/all-later | proved antecedent arguments apply | S1/S2 and one-upper-cell correction |
| Literal kernels/phase arithmetic | measured transcription supplements | No evolving physical U/2U trajectory |
| Boundary/GF-changing/later/multiple/E0/higher-iid | unproved | No explicit positive epsilon or memory theorem |
| Faithful Gray/G17 refutation/minimum sufficient global change | unproved | Full goal incomplete |
| Rule/ROM/constants/CURRENT change or commit | none | All earlier frozen assets preserved |
