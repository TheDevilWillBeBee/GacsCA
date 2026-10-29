# GAWN22: arbitrary clocks in late, repeated address-preserving bursts

This uses **unchanged frozen GAWN2**, Q4096/U524288/radius8/Word100/h1/
own beta/lambda24/c104, with all its declared departures from Gray.
No rule, ROM, constant, CURRENT or prior frozen asset is changed.
This is a deterministic restricted recovery theorem. It does not prove
positive-rate iid reliability, general hierarchy maintenance or memory.

## Exact statement

Use actual noiseless Y_t=F^t(H_2), with the recursively intact H_2 of
GAWN4. Set I=[0,Q), T0=100Q+2=409602, and

    r0=Q-2=4094,
    r_clock=2Q-2=8190,
    R=r_clock+Q/2=10238,
    Lmax=U-1-R=514049.

Fix an interval A=[b,b+w) within I, 1<=w<=104, and any last possible
overwrite row L in[T0,Lmax]. On any subset of after-update physical
rows T0,...,L, replace arbitrary cells in A, retaining their Address.
Every other native or SF field may be an arbitrary legal value, chosen
adaptively. Age may be **any integer0..U-1**: backward, forward, wrapping
and event-triggering clocks are all permitted. All four native flags
and all thirteen SF fields may change. There are no other errors.

Then, for every such history:

1. Address is canonical globally; outside I Age is correct and Flag2/
   both Workspace fields are0; Flag1 is0 outside I and its left
   adjacent colony, through U.
2. All clocks and Flag2 are correct by L+8190, and all native fields
   by q=L+10238<=U-1. Native equality persists through U.
3. A fixed adjacent pair P of true colonies containing I confines every
   voted logical SF difference through U. Raw holder differences have
   the usual two-site halo, and native Flag1 is allowed outside P.
4. X_U=E(dprime,Bprime) as complete raw configurations; dprime equals
   cell_words(F(H_2)) outside P's two represented upper indices.
   Inside that pair arbitrary represented native padding is admitted.
5. X_(2U)=F^(2U)(H_2) as complete raw configurations, and equality
   holds at every later tick.

The longest permitted overwrite interval has104448 rows, with fixed
spatial support width<=104. In particular this includes GAWN9's late
104-site/104-row class with its Age restriction removed. No original
error class is assigned from geometry alone; independently qualifying
original-c104 real1 histories meeting these restrictions are included.
Address-changing faults, varying/multiple supports, other phases,
continuing surrounding E0/higher errors and iid closure remain unproved.

## 1. Actual native exterior — proved antecedent argument applies

GAWN6's one-step exterior proof permits arbitrary inside clocks,
all flags, every SF value and clock wrap. It requires only that the
correct outside successor clock is outside[96Q,98Q). Here it runs
from T0+1 through U-1 and then0 at U. Both adjusted GF votes are
canonical, hence the actual wipe is false everywhere. Outside I all
clock/Flag2/Workspace conclusions hold; Flag1 can differ only in I
and the left adjacent colony. Every after-row overwrite preserves
these premises, because it stays in I and retains GF. Induction gives
item1, with no inside clock-band or global Workspace-closure premise.

## 2. Actual tag-to-Workspace2 gate and native deadline — proved

After the last possible overwrite let r=t-L. Tag means correct Age
or raw Flag1=1. GAWN8's suffix disjunction needs only canonical GF,
the correct right exterior and its zero Flag1. It allows arbitrary
old Workspace, wrong clock values and wrap. Three correct right
clocks give a correct new clock when computed Flag1=0; computed
Flag1=1 supplies the tag. Otherwise three wrong tagged right clocks
have Flag1=1 inside the true colony and force the tag by propagation.
The last three sites are tagged at r=1, and the suffix persists and
grows left one site per row. All of I is tagged by r0=Q-2=4094.

GAWN21's actual-output gate applies with this **late** reference phase:
Workspace2 can be nonzero only when computed Age lies in[96Q,98Q),
Address<=4 and computed Flag1=0. Correct late clocks exceed100Q,
closing the guard; a Flag1-supplied tag closes the explicit Flag1
gate. Thus a tagged unoverwritten normal output has raw Workspace2=0,
independently of SF and Workspace1. Outside Workspace2 is already0.
Global Workspace2 is therefore0 from r0 to q. Inside Workspace1 may
still be1, and inside clocks may trigger every SF event, including0.

Canonical GF eliminates the missing-colony Flag2 source. Its other
source reads only old Workspace2, now0. GAWN7's h1 zero-front clause
then forces new Flag2=0 whenever all five old left Flag2 bits are0,
for either old self bit and either computed Flag1. This requires no
Workspace1-zero premise. A zero prefix has length min(s,Q) at row
r0+s. The first three clocks are correct at r0+3=Q+1=4097: their
left quorum has three correct exterior words and the tagged right
neighbors supply either a correct right quorum or Flag1 forcing the
clean left selector. They persist. For s>=3, all five old left clocks
at centers3..s are correct and at least three are in-colony. A missing
or wrong right Age majority forces computed Flag1=1 by inconsistency;
computed Flag2=0 chooses the clean left quorum. A correct right quorum
works with either voter. Additional Workspace1 forcing cannot hurt.
The correct prefix advances one site per row behind the Flag2 front.

All clocks and Flag2 are correct by r0+Q=8190. On that actual output
row both Workspace fields are0 because every clock is the correct
late reference. Common clocks and zero Workspace/Flag2 persist. The
remaining Flag1 equation is the exact masked3/right-keep2 equation.
Its zero suffix advances at least two sites per true colony per row,
simultaneously in every affected colony. It clears in Q/2=2048 ticks.
This proves native quiet by R=8190+2048=10238 after the last possible
overwrite, at q<=U-1. The late reference guard remains closed through
the final successor0 at U, so native equality persists through U.

These are GAWN21's word/front/gate arguments with their correct
reference clocks replaced by the late ones. No correspondence of SF
schedules, inside clock trajectories or global age ranges is assumed.

## 3. Protected pair endpoints for every clock — proved

GAWN9's endpoint proof did not require its Age interval. For logical
Head at endpoint e, its five holders are H(e)={e-2,...,e+2}. Let the
forbidden outward movement bit be bit1 at a left endpoint and bit0
at a right endpoint. A zero voted forbidden bit excludes that literal
outward arrival. At canonical service Address e modQ, every actual
Head-update branch preserves this zero bit separately for each holder:

* Reset gives ZERO. Birth is only at interior P1800, so also gives0
  at either endpoint. This includes arbitrary age0/early resets.
* Hold copies the old voted packet and preserves that bit.
* Every active incoming is followed by the total step_packet. Its
  targets are guarded to[0,Q); invalid metadata/instruction/target,
  HALT, collision or local operations have movement0. A legitimate
  target cannot move outward at the true endpoint.

The GF wipe is false; even a wipe would give0. Therefore the invariant
holds for arbitrary SF/malformed packets, different holder clocks,
repeated resets/gathers and any other actual inside branch. If at most
two holders of an endpoint can be overwritten, the other three give
old vote0, every normal output gives0, and the next overwrite cannot
change the vote. This uses the actual clean late initial endpoints.

An interval A of width<=104<Q cannot contain both0,1,2 andQ-3,Q-2,Q-1.
At least one endpoint of I is protected. Choose

    P=[-Q,Q) if |A intersect H(0)|>=3,
    P=[0,2Q) otherwise.

In the first case I's right endpoint is protected; in the second its
left endpoint is protected. The far endpoint of the added neighbor has
no overwritten holders and has the same invariant. Both outer pair
boundaries consequently block outward Head arrival for the entire
overwrite interval and through U. Many malformed packets may cross
the internal pair boundary; no one-escape premise is made.

## 4. SF confinement needs only the actual exterior holders — proved

GAWN9's old proof established a global clock band excluding transport,
gathers, courier movement and special Info writes inside I. **That
global assertion is not reused.** Inside I every one of those branches,
including the age0 old-Out commit, is allowed here.

Induct on all logical SF votes outside P. Initially they equal the
actual clean votes: every logical y outside I has at most two holders
inside I, and overwrites stay there. At any logical y outside P, at
least three physical holders are outside I. Their actual computed
clock is the correct physical row in(T0,U) before the final commit,
by section1. It is above100Q, so **at those three holders** Mail
transport, gathers/captures, courier movement,80Q-1 Info writes and
all earlier reset/birth events are closed. There is no old-Out commit
until the correct physical row U. Native service Address is canonical
and wipe is false.

For these holders every non-Head SF operand is the old voted word at
the same logical y or the actual immutable beta. Those operands are
clean by the induction. Head additionally reads y-1,y,y+1. If one
lies inside P, the protected outer endpoint prevents any accepted
outward packet from it, just as in the clean history. All other Head
operands are clean. The resulting accepted incoming and total CPU
step therefore give exactly the clean Head/Out/Scratch outputs.

Possible native Flag1 outside P only sets Mail to0 with canonical GF.
The actual clean late Mail there is already0 and stays0; transport
and new loads are closed at the correct outside clocks. This action
also gives the clean output. All other SF controls at these holders
match the clean one. The three actual outside holders therefore give
each clean voted SF word on the next row. At most two other holders,
with arbitrary inside clocks and work, cannot change that bitwise
majority; an after-row overwrite cannot either.

This closes the induction through every overwrite row and every later
row before U. It permits arbitrary inside Mail/courier transport and
captures: they cannot defeat the three correctly clocked actual
outside holders. The clean accepted Head operands at the pair edge
are justified by the endpoint-bit invariant, not by assuming that
the malformed work stayed in I. No coherent-SF simulator or clean
outside private-work tape is imposed.

At U all native clocks are already correct. Every holder now has the
correct clock0, no wipe and the same logical old Out vote. The actual
commit produces exactly the clean Info outside P; resets give the
clean remaining SF there. SF confinement therefore extends through U.
Individual raw copies can differ within the ordinary two-site holder
halo before that common reset; the assertion concerns logical votes.

## 5. The actual U boundary and complete2U correction — proved

At q all native fields are quiet. If q<U-1, the following normal SF
update uses the same clock/service Address and same logical operands
at all five holders, so SF regains coherence globally. No inside work
correctness is inferred. For the limiting **q=U-1** case, a separate
intermediate coherence row is unnecessary: the actual U update itself
has common age0 and gives coherent Info from old voted Out, all work
resets and the own Programme. This handles the exact deadline endpoint.

At U native fields are canonical/Age0/flags0. Head, Mem, Out, Scratch,
both Mail/couriers and all History banks reset; Programme is own beta.
The old voted Out supplies Info **before** the reset. Thus the complete
actual row is E(dprime,Bprime), with arbitrary coherent auxiliary Info
Bprime. By section4 all represented frame words outside P equal
cell_words(C1), C1=F(H_2). Only P's adjacent upper pair may differ,
including arbitrary represented native padding. No reset or new rule
has been supplied externally.

Normalize Cprime=pi(dprime). GAWN4's universal adjacent-pair correction
at actual C1 applies unchanged: each native/SF voter has at least three
clean witnesses; erroneous positive self flags have at most one eligible
positive neighbor; h1 erases Flag2; the successor clock2 closes Workspace.
Complete raw F(Cprime)=C2=F(C1) follows, including padding projection.
GAWN2's universal represented-D period theorem now gives

    X_(2U)=F^U(E(dprime,Bprime))=E(F(Cprime),0)=E(C2,0).

The clean2U boundary is the same E(C2,0). There are no later errors,
so complete raw agreement holds at every later tick by determinism.

## Checks, statuses and remaining gaps

Finite supplements compare native gate cofactors at late reference
clocks with arbitrary SF and selected wrapping inside clocks; endpoint
branches at every distinct scheduled control event and mixed clocks;
three actual exterior-holder outputs for all13 SF tracks, with arbitrary
inside clocks/SF and protected outward bits; and the actual age0 reset
using incoherent raw work. Deadline arithmetic covers every permitted
last-fault row, including q=U-1. The universal claim rests on the literal
gate, word counts and inductions above. No evolving10238-step full-SF
trajectory or physical2U simulation is performed.

| Step | Status | Scope |
|---|---|---|
| Native exterior/repeated-overwrite invariance | proved antecedent argument applies | GAWN6; arbitrary inside Age/SF |
| Tagged suffix/actual Workspace2 gate/native10238 | proved antecedent component arguments apply | GAWN21; late correct-clock guard supplied |
| Protected endpoints/fixed adjacent pair | proved antecedent argument applies | GAWN9/4; every actual clock branch |
| All-SF exterior confinement with active inside schedules | proved | Three correctly clocked outside physical holders |
| Native q<=U-1 and actual coherent U encoding | proved | Includes q=U-1 directly at actual commit/reset |
| Adjacent upper-pair correction/complete2U/all-later equality | proved antecedent arguments apply | GAWN4/2; actual encoding derived |
| Kernel/gate/endpoint/holder/deadline checks | measured transcription supplements | No complete evolving repair simulation |
| GF changes/multiple or moving supports/other phases/E0/higher/iid | unproved | No positive-rate or memory theorem |
| Faithful Gray/G17 refutation/minimum sufficient global fix | unproved | GAWN2 departures remain |
| Rule/ROM/constants/CURRENT change or commit | none | Frozen prior assets preserved |
