# GAWN4: arbitrary late SF bursts and unconditional two-period repair

This is a proof checkpoint for **unchanged frozen GAWN2**, with
Q4096/U524288, radius8, Word100, native12/19, PC12, lambda24/c104,
the emitted beta_2 and the100Q reset/100Q+1 birth/127Q cutoff.
No rule, ROM, compiler, schedule or constant is changed. The material
word/radius/immutable-code/h1/rest departures from Gray remain.
The result below is a restricted deterministic burst theorem. It does
not cover native-changing bursts or the earlier gather/source window,
and does not establish a positive iid rate.

The physical period and normalization theorem is
[GAWN2](../unregistered_gawn2/GAWN2_HALF_SCALE_NOISELESS_PERIOD.md).
The late factor/inward-head argument is adapted from
[GAW12](../unregistered_gaw12/GAW12_ACTIVE_SF_CONFINEMENT.md), with the
new native widths, total packet guards, schedule and frame checked here.
The larger-alphabet period theorem removes that older argument's
unproved legal-native-padding premise. Old selected fault histories
are not transferred to the new rule.

## Exact statements and restrictions

Write F=F_2, E=E_2, D and pi=pi_2 as in GAWN2. D consists of496
Word100 representation words; pi masks the six native words to their
legal physical widths and preserves all490 SF words. E(d,B) is a legal
lower physical configuration even when d has nonzero native padding.
All13 physical SF components are included: packed Head/registers,
Mem, Out, Info, Scratch, Programme, both couriers, both Mail tracks
and all three History banks.

Start from E(C,B), where C is an arbitrary infinite physical upper
configuration and B arbitrary coherent auxiliary Info. Let Y_t be its
noiseless physical evolution. Fix an integer interval L=[b,b+w),
1<=w<=104. Permit arbitrary legal replacements of **only the SF bits**
at sites in L, on any subset of rows

    100Q+2 <= t <= U-1,

with no other errors. Every replacement retains all six actual native
fields at that site. It can be adaptive, incoherent and have arbitrary
packet metadata. No sixteen- or104-row duration bound is required for
the confinement theorem. Errors are after-row-update overwrites; X_t
is the resulting raw row, and Z_(t+1)=F(X_t).

Choose one fixed adjacent pair of Q-colonies containing
[b-1,b+w+1). Such a pair exists because w+2<=106<Q. Write T for their
union of logical sites and P_T for their two upper indices.

**Theorem A (late SF confinement and first boundary).** Native GF is
x modQ, native Age is t modU, and native Flags/Workspace are0
throughout the fault window and through U. Every pre-overwrite computed
SF row has five coherent copies. Its logical SF differences from Y_t
are confined to T. The physical holder support has a two-site halo
around T; current raw replacements lie in L. There is a D-configuration
dprime and a coherent auxiliary Bprime such that the complete boundary is

    X_U = E(dprime,Bprime),

where dprime[g]=cell_words(F(C)[g]) for g outside P_T. No literal
legal-native-padding assertion is made for dprime inside P_T.

Define the recursively intact H_2 below. Its native fields are
canonical GF, Age0 and zero Flags/Workspace, and all SF copies are
coherent. H_2=E(H_2,0) on the infinite line.

**Theorem B (unconditional two-period repair from H_2).** For the same
fault model, now starting from H_2, with no later errors,

    X_(2U) = F^(2U)(H_2).

This is complete raw equality, not just a decoded bit. Equality persists
at every later tick by determinism. Every native-padding pattern at U
is covered; legal upper native padding is not an extra assumption.
In particular this covers arbitrary SF-only bursts in a fixed
104-site by104-tick box wholly inside the stated late window. It does
not cover a general original-real1 error, since that error can change
native fields or occur in an earlier phase. C in Theorem A need not be
intact; Theorem B's recovery premise does require the stated H_2.

## 1. Actual recursively intact initialization — proved

Let P1800, frame width496, S=(0,-2,-1,1,2), and beta_2 be the frozen
emitted own ROM. Define a Word100 function I_2 on Z. At y=gQ+a,
0<=a<Q, put i=a-P. Outside0..495 set I_2(y)=0. For rows0..5 set
I_2(gQ+P+i)=g modQ if i=0 and0 otherwise. For remaining rows, let
f be FIELD_NAMES[(i-6)//5] and h=(i-6) mod5. Set

    I_2(gQ+P+i) = I_2(g+S[h])                   if f=info,
                   beta_bit(beta_2,(g+S[h]) modQ) if f=program,
                   0                             otherwise.

Only the five Info rows206..210 recurse; their residues are2006..2010.
Every recursive y has |y|>=2006, and
|g+S[h]|<=|y|/4096+3<|y|. Thus this definition terminates for every
integer, including the negative half-line. Terminal values are legal
native addresses or bits; all I_2 values are legal Word100 words.

Define H_2(x) with canonical native GF, Age0, flags0, all work0,
Info[h]=I_2(x+S[h]) and Programme[h]=beta_bit(beta_2,(x+S[h]) modQ).
For every g and frame row i the displayed field cases give exactly

    I_2(gQ+P+i) = cell_words(H_2(g))[i].

Every holder x=y-S[h] stores I_2(y). Unrepresented Info and both
special-source residues3/Q-3 are0. Consequently H_2=E(H_2,0), with
the actual own Programme at every level. This proves infinite recursive
intactness by repeating the same identity; no finite ring is assumed.
The new checker supplements the field argument with both signs and
large coordinates, all496 field rows and actual holder identities.

## 2. Native closure and physical SF factor — proved

The GAWN2 physical-period argument gives canonical GF/common clock for
Y and zero native Flags/Workspace by99Q, before the actual100Q reset.
The100Q+1 birth already occurred before any permitted overwrite.
Under the faults, the six native fields are retained. The adjusted-GF
and Age votes therefore remain canonical/common. The Workspace source
guard96Q..98Q is closed throughout the stated window; arbitrary SF at
special primaries cannot turn it on. The zero flag quorums remain zero.
Thus native fields follow Y everywhere, independently of every SF
replacement. The raw-self GF wipe is always false.

For each logical y and SF component v, all holders compute the same
old vote

    V_v(y)=vote(raw_v(y-S[h])[h], h=0..4).

Their service addresses are (x modQ+S[h]) modQ=y modQ and clocks
are equal. The wipe is false. Hence each computed row is coherent
for all13 components even when the old raw row was incoherent.
This is the literal physical holder equation, not an imposed decoder.

On100Q+2..127Q the Head update is incoming at y followed by the total
step_packet at y, with voted local Mem/Out/Scratch/Programme. Writes
affect only y. All other mutable SF components hold their local voted
values, except Programme which is regenerated from beta_2. There are
no loads, captures, courier movements, source commits, resets or births
in this window. At127Q+1..U-1 Head holds as well; a pending movement
bit does not execute during rest. At U, the normal old-Out commit and
global work reset apply. These chronological statements follow from
the frozen GAWN2 branch guards; they are not external chosen controls.

## 3. One possible escape and inward packet control — proved

An arbitrary old packet can move one logical site before normalization.
Every packet output by an active step thereafter has movement0/1/2,
and has no left move at local Address0 and no right move at Q-1.
This covers arbitrary raw words, not just compiler-generated heads:

* Absent packets give ZERO. Invalid move/mode, invalid PC/decoded
  instruction, branch or IO target gives ERROR with movement0.
  HALT/ERROR and collisions also give movement0.
* RUN arithmetic and ROM operations and valid branches give movement0.
  An IO operation checks target<Q and moves toward that target.
  The computed target is a nonnegative integer; overflow is rejected.
* SEEK checks target<Q; before arrival it moves toward the target,
  and on arrival its local load/store gives movement0. Invalid
  descriptors give ERROR with movement0.

At Address0 an accepted target cannot be left; at Q-1 it cannot be
right. Registers and target words remain nonnegative100-bit values.
This proves the endpoint shield for every raw Packet. The new checker
exhausts all4096 SEEK targets at both endpoints and checks the actual
new immutable RUN instruction cases with boundary/invalid operands.
Those are finite supplements; the total-case inequality above proves
the full100-bit quantifier.

For a coherent computed row, current replacements inside L cannot
alter a vote for a logical y outside L: a five-holder group centred
outside this interval intersects L in at most two sites. Its three
correct operands remain equal. Thus new SF discrepancies occur inside
L and new raw Head movement can expand them only to L+{-1,0,1}.
This interval lies inside the fixed T. Normalized packets already
inside T stay within their own colony until another raw overwrite;
all such overwrites and their possible first escapes are still in T.
Collisions and local writes cannot expand T. Clean legitimate heads
outside T stay on the normal496-word frame, proved by GAWN2's own-ROM
semantics, and never cross into T. Induction on actual rows therefore
confines every computed logical discrepancy to T. The non-Head SF
tracks are local holds in this chronology. Physical holders y-S[h]
give precisely the stated two-site halo; a literal raw two-colony
envelope is not claimed.

## 4. Exact first boundary and unrestricted padding — proved

There is no error at U. The preceding raw row's voted Out is a legal
Word100 value at every logical site, even if the last permitted
overwrite is at U-1. At U the rule consumes those old votes before
resetting work. The resulting Info holders are coherent, native fields
canonical with Age0/flags0, all work is0 and Programme is exact beta_2.
Take dprime[g] to be those496 normal committed words, and Bprime the
actual remaining coherent Info. This gives full X_U=E(dprime,Bprime).
Outside P_T the words equal F(C), by §3 and the noiseless period.
Arbitrary Out faults can set high native representation bits inside
P_T; they are retained rather than silently truncated at the boundary.
This proves Theorem A.

## 5. Unconditional two-period repair from H_2 — proved

Put C_1=F(H_2). It has canonical native GF, common Age1 and zero
Flags/Workspace, and all13 SF tracks coherent by the holder equations.
No upper prepared-frame premise is used here: it is the actual one-tick
physical output from H_2. By Theorem A, pi(dprime) differs from C_1
only at the fixed adjacent upper pair P_T, as complete legal cells.

Any actual five-holder SF vote at the next upper update sees at most
two corrupted sites and restores the correct full coherent word.
Both native GF/Age quorums see at least three correct values and
restore canonical GF/common Age. At most two native mismatch or WF
inputs cannot turn on their three-site sources. An erroneous positive
Flag1 self has at most one erroneous positive right neighbour, so
the keep/on thresholds erase it. ComputedF1 is0. The h1 Flag2 erase
clause likewise clears a positive self with at most one positive left
neighbour; its four-site on and three-site WF sources are false.
Missing-GF source3 is false. Computed Age2 is outside the Workspace
guard. ComputedF1=0 excludes the raw-self SF wipe even if raw GF differs.
Thus every SF operand/control is the clean one and

    F(pi(dprime)) = F(C_1) = F^2(H_2)

as complete raw upper configurations. This is a one-update adjacent-pair
correction identity at a coherent common-clock quiet upper state.
The word and quorum proof covers all replacement values; selected
cofactors do not supply the universal quantifier.

Apply the GAWN2 S2 theorem to the **derived** actual X_U=E(dprime,Bprime).
It allows every native padding pattern in D and arbitrary auxiliary
Bprime. With no subsequent errors it gives

    X_(2U)=E(F(pi(dprime)),0)=E(F^2(H_2),0).

The clean physical shadow is the same E(F^2(H_2),0) by two noiseless
periods from H_2=E(H_2,0). This proves Theorem B, including full raw
recovery and subsequent equality. The older GAW12 legal-native-padding
conditional is unnecessary for this unchanged normalized rule.

## 6. Actual malformed-padding instance — proved finite supplement

The checker derives the intact H_2 banks, runs the actual own-ROM
early entry and complete late entry in colony0, and retains the full
output, final packet, Scratch, addresses/deadline and trace digest.
These are reached from the physical gathers/reset/birth by the GAWN2
holder induction, not independently supplied future banks.

At each of the five sites (P-S[h],U-1), replace only Out[h]0 by2^99,
leaving all other actual bits unchanged. The complete raw pre-error
and replacement cells are retained. The five-point original-c104
classifier gives one real1 and no E0. The actual full local kernel
commits2^99 in the represented upper-cell0 GF word, with coherent
holders and complete reset. No legal physical upper cell has that GF
word, so the narrower literal legal E relation fails at U. The D
encoding contains it exactly. pi(dprime)=C_1 in this instance.

A new actual full early/late evaluation of the derived next-period raw
bank verifies normalized output equality to F^2(H_2)(0), with the raw
high bit included in the input. The universal S2 and global boundary
argument give complete2U recovery; no finite experiment claims an
iid threshold, faithful Gray counterexample or general burst proof.

## Status and remaining obligations

| Step | Status | Scope |
|---|---|---|
| Actual infinite recursively intact H_2 | proved | Terminating field recursion, all integer sites/own Programme |
| Native closure/coherent physical SF factor | proved | SF-only faults after100Q+1, source guard closed |
| Total packet endpoint shield/fixed adjacent-pair logical confinement | proved | Arbitrary100-bit packets and all13 SF replacements in one width<=104 interval |
| First boundary E_2(dprime,Bprime), arbitrary padding retained | proved | No error at U, same frozen normalized rule |
| Quiet-upper one-pair correction/unconditional complete2U from H_2 | proved | No later noise; all legal replacement values after pi_2 |
| Finite source/field/endpoint/quorum/kernel/own-ROM checks and actual padding witness | exact finite supplements | Universal scope comes from displayed inductions and inherited S2 |
| Native-changing real1, earlier SF bursts, continuing mixed clusters | unproved | Not covered by this fault model |
| General higher-error/noisy refinement, positive iid epsilon, memory, minimum sufficient change | unproved | Active goal remains open |

Read-only replay is `python3 Report/proofs/gray_counterexamples/unregistered_gawn4/validate_late_sf_gawn4.py`.
No active or frozen rule/ROM/constants are changed. No commit.
