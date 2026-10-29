# GAWN9: late mixed bursts, one protected endpoint and complete2U repair

This is a proof for the **unchanged frozen GAWN2** rule,
Q4096/U524288/radius8/Word100/h1/beta_2/lambda24/c104, with all
previous departures from printed Gray. No rule, ROM, schedule or
constant is changed. It combines
[GAWN6's native exterior](../unregistered_gawn6/GAWN6_CANONICAL_ADDRESS_CLOCK_CONFINEMENT.md),
[GAWN8's tagged-suffix repair](../unregistered_gawn8/GAWN8_TAGGED_SUFFIX_AND_UNIVERSAL_LATE_REPAIR.md)
and [GAWN4's total packet and upper-pair correction](../unregistered_gawn4/GAWN4_LATE_SF_BURST_REPAIR.md).
The new arguments cover the simultaneous native/SF damage and repeated
overwrites specified below. They do not prove general noisy reliability.

## 1. Exact theorem and restrictions

Let F=F_2, E=E_2, pi=pi_2 and actual recursively intact H_2 be those
of the preceding proofs. Start with the noiseless physical history
Y_t=F^t(H_2). Put

    T_0=100Q+2=409602,
    I=[0,Q), V=[96Q-1,U-4Q-1]=[393215,507903].

Choose a fixed integer interval A=[b,b+w) contained in I, with
1<=w<=104, and an integer 0<=D<=103. On any subset of physical rows
T_0,...,T_0+D, after the normal row update, replace arbitrary cells
in A. Each replacement retains its Address; its Age is a value in V.
All four native flags and all thirteen SF fields may otherwise be
arbitrary legal values, chosen adaptively. There are no other errors,
including none after t_*=T_0+D. Write X_t for the resulting raw rows.
The support alone does not classify a fault as real1. Original-c104
real1 sets satisfying these restrictions are included.

**Theorem.** For every such history:

1. Address is canonical globally. Wrong Age is confined to I, Flag2
   and Workspace are zero outside I, and Flag1 is zero outside
   I union [-Q,0), through the current U boundary.
2. All native fields are correct globally by t_*+14337, hence by
   T_0+14440<T_0+4Q. They remain correct through U.
3. There is a fixed adjacent pair of true colonies P, containing I,
   such that all voted logical SF differences are confined to P
   throughout the burst and through U. Individual raw copies have
   the ordinary two-site holder halo; raw native Flag1 may lie outside P.
4. The complete U boundary is E(dprime,Bprime), where dprime equals
   cell_words(F(H_2)) outside the two upper indices represented by P.
   Arbitrary native representation padding inside those indices is
   retained. The actual own Programme and complete work reset hold.
5. X_(2U)=F^(2U)(H_2), as complete raw configurations. Equality
   persists at every later tick by determinism.

This covers mixed native/SF 104-site by104-row late bursts while
retaining Address and restricting replacement clocks to V. It does
not cover Address-changing bursts, earlier phases, arbitrary Age
words, surrounding E0 noise, multiple separated bursts or higher
clusters. No positive iid epsilon is established.

## 2. Native exterior and shifted recovery deadline — proved

The GAWN6 one-step exterior induction permits arbitrary native and SF
values inside I. Every overwrite keeps the same canonical Addresses
and changes native fields only in I. It therefore preserves the
exterior premises after each update. Correct outside clocks have
computed values in(100Q,U), and0 at U, so their actual Workspace
guards stay closed even when SF damage has entered a neighboring
colony. GAWN6's induction never assumes that outside SF is clean.
The first assertion follows for all burst rows and afterwards.

Every clock update selects an old clock by a whole-word majority or
self fallback and adds1 modU. Until T_0+4Q, every selected clock can
be labelled by an initial or overwritten value v in V, plus the
number of increments since its originating row. Its maximum is at
most maxV+(t-T_0)<=U-1. There is no wrap on that interval. During the
burst every computed clock is at least minV+1=96Q. Thus no computed
clock hits0 or80Q-1 before native recovery.

At t_* the raw clocks lie in[minV,maxV+D]. With no subsequent error,
at elapsed s after t_* they lie in

    [minV+s,maxV+D+s], 0<=s<=4Q-D.

The actual Workspace guard consequently closes globally by
s=2Q+1=8193 and stays closed through4Q-D. The native exterior has
zero Flag2 to the left of I, so the unchanged h1 zero-front argument
clears a prefix of length min(r,Q) at s=2Q+1+r.

GAWN8's tagged predicate uses only canonical Address, correct clocks
and zero Flag1 to the right of I. It permits arbitrary Flag2/Workspace
and does not require SF outside I to be clean. Starting at t_* with
the exterior just proved, the three rightmost sites are tagged on the
first update and the tagged suffix covers I by s=Q-2=4094. The first
three clocks then become correct when the h1 zero front reaches them.
Correct clocks follow that front one site per update, exactly as in
GAWN8. All clocks and Flag2 are correct by s=3Q+1=12289. The common-
clock Flag1 suffix clears all affected colonies simultaneously within
Q/2=2048 further updates. Therefore

    R=14337, D+R<=14440<4Q=16384,
    4Q-D-R>=1944.

All these component inductions fit in the unwrapped, closed-Workspace
interval. At the quiet row the actual common clock is past100Q, and
its guard remains closed through the current U boundary, including
the wrap to0. Native equality persists. No future command was assigned
or suppressed, and recovery is measured from the last possible fault
row, not from the start of a still-active burst.

## 3. A protected outward Head endpoint — proved

The five physical holders of logical Head at y are

    H(y)={y-2,y-1,y,y+1,y+2}.

The SF voter is bitwise three-of-five. At logical left endpoint0,
the forbidden outward move is2, whose low movement bit1 is1.
At right endpointQ-1, the forbidden outward move is1, whose low
movement bit0 is1. Call the corresponding bit the endpoint's
forbidden bit. A zero forbidden bit excludes that outward move even
if other raw movement bits are malformed. Incoming accepts a neighbor
only for the literal movement value1 or2.

For any canonical service Address at either endpoint, every branch
of the actual Head update preserves a zero voted forbidden bit:

* Reset produces ZERO. Birth is only at the interior HEAD_ADDRESS1800,
  so it also produces ZERO at the endpoints.
* Rest/hold copies the old voted packed Head, preserving that bit.
* Active incoming is followed by the total step_packet. GAWN4's
  arbitrary-word case proof gives no outward movement at either
  endpoint: every accepted target lies in[0,Q), invalid metadata,
  instruction or target produces ERROR with movement0, and HALT,
  collision and local operations also give movement0.
* The raw-self GF wipe is absent because Address is canonical; even
  a wipe would produce ZERO.

The branch argument is applied separately to each holder's actual
computed clock. Holders need not be coherent or have equal clocks.
If at most two holders of an endpoint can be overwritten, the other
three retain forbidden bit0. Their old bitwise vote is0, every
pre-overwrite Head output at that logical endpoint has the bit0, and
the next overwrite can alter at most two holders again. Starting from
the actual clean late history, induction keeps the voted forbidden
bit0 at every row. This uses the actual total packet guard; arbitrary
malformed Head metadata at other sites is not normalized externally.

Since A is contained in I, it can meet H(0) in three sites only by
containing0,1,2. It can meet H(Q-1) in three sites only by containing
Q-3,Q-2,Q-1. An interval of width<=104<Q cannot do both. Hence at
least one endpoint of I is protected. If |A intersect H(0)|>=3,
choose P=[-Q,Q); otherwise choose P=[0,2Q). In the first case the
right endpoint of I is protected. In the second the left endpoint is
protected. The far endpoint of the added neighboring colony has no
overwritten holders and obeys the same zero-bit induction. Thus both
outer boundaries of P block every outward Head arrival. An unprotected
internal boundary may pass many corrupted packets over many rows;
no one-escape assumption is made for it.

## 4. Logical SF confinement with different clocks — proved

From the first fault through t_*+R, all computed clocks are in[96Q,U).
After recovery, their common actual values through U are above100Q,
and0 only at U. In the frozen schedule there are no Mail transports,
gathers/History captures, courier movements or80Q Info commits during
the former interval. The96Q/100Q resets and100Q+1 birth may occur
inside I; they are local operations. Info holds its old vote, except
for the actual old-Out commit at U. Every non-Head SF update before U
therefore uses only the old voted words at the same logical position,
its actual service Address and clock, or the immutable own beta.
Malformed Mail/courier words inside I are allowed and need not be0.

Initially all logical votes outside P equal the clean values, because
every five-holder group for a logical y outside I contains at most
two physical sites in I. At any logical y outside P, at least three
holders are physically outside I. Their clocks are correct by §2,
service Address is canonical, and wipe is false. All voted SF operands
at y are clean by induction. Head's only neighboring operands are
y-1,y,y+1: a packet from P cannot enter through an outer boundary by
§3, so the accepted incoming Head is the clean one.

Native Flag1 may differ in the left adjacent colony, possibly outside
P. Its only relevant SF action with canonical Address is setting Mail
to0. The actual clean late Mail outside P is already0, and there is
no Mail transport, so this leaves the clean output unchanged. Every
other SF control at these three holders is the clean one. They all
produce the clean words, and any other two holders cannot alter the
bitwise vote. A current overwrite also affects at most two holders
of y outside I. This closes the induction on all burst rows and all
later rows through U: logical SF damage stays in P.

This is an induction on the literal raw-holder equations under
different clocks, not a coherent-SF simulator imposed during repair.
Clean legitimate Head packets outside P need not be assumed absent:
their actual update is preserved, and they obey the same endpoint
guard. Raw holder differences near P have a two-site halo, and raw
native Flag1 differences outside P are separately allowed by §2.

## 5. Complete U encoding and complete2U restoration — proved

There are no errors after t_*. At t_*+R all native fields are correct.
On the following SF update all five holders of each logical position
use the same actual clock, canonical service Address and zero Flag1,
and the same old logical votes. All thirteen SF tracks regain
coherence globally. Their values inside P may be arbitrary. Mutable
Programme is regenerated from actual beta every update; it was never
replaced as part of the transition rule.

At U, the actual old voted Out supplies Info before work resets.
Native fields are canonical/Age0/flags0; Head, Mem, Out, Scratch,
Mail, couriers and History banks reset, and Programme is exact beta.
Thus X_U=E(dprime,Bprime), with coherent Bprime admitting arbitrary
auxiliary Info. Outside P, all committed normal frame words are the
clean ones by §4. Only its adjacent upper pair can differ, including
arbitrary high native padding. This is the proved represented-D
encoding, not a new reset or recovery rule.

Let C1=F(H_2), C2=F(C1). The actual C1 has coherent SF, canonical
Address, common Age1 and zero flags. The normalized Cprime=pi(dprime)
differs from C1 only in the adjacent pair corresponding to P.
GAWN4 §5's arbitrary-value adjacent-pair correction applies verbatim:
five-holder SF votes and native quorums have at least three correct
inputs, erroneous positive self flags have at most one positive
eligible neighbor, h1 erases Flag2, and computed Age2 keeps Workspace
closed. Consequently F(Cprime)=C2 as complete raw upper rows.

The universal represented-D period theorem of GAWN2, applied to the
derived actual U boundary, gives

    X_(2U)=F^U(E(dprime,Bprime))=E(F(Cprime),0)=E(C2,0).

The clean2U boundary from H_2=E(H_2,0) is the same E(C2,0). This
proves full raw equality at2U and every later tick by determinism.

## Verification and status

The new checker records finite transcriptions for the endpoint-bit
branches with different computed clocks and arbitrary SF, exact
holder geometry for the allowed intervals, and the shifted deadline
arithmetic. GAWN8's native supplements and GAWN4's total-packet and
pair-quorum proofs are inherited unchanged. No evolving mixed-burst
recovery campaign or complete2U physical simulation is performed.
The universal theorem follows from the displayed inductions and
reused proved statements, not from finite selected histories.

| Step | Status |
|---|---|
| Actual H_2 and native exterior through repeated Address-retaining overwrites | GAWN4/GAWN6's proved arguments apply; overwrite invariance proved here |
| Clock range after final overwrite; tagged/front nativequiet14337 | Proved using GAWN8's unchanged counting inductions |
| At least one protected endpoint; mixed-clock zero-bit induction | Proved for every admitted burst and legal SF word |
| Fixed adjacent-pair logical SF confinement | Proved; raw holder halo and external native Flag1 explicitly allowed |
| Complete actual U represented-D encoding | Proved |
| Complete2U/all-later restoration | GAWN4 pair correction and GAWN2 period arguments apply verbatim |
| New finite geometry/branch/kernel/arithmetic checks | Measured transcription supplements |
| Earlier/GF-changing/arbitrary-Age/E0-surrounded/mixed separated/higher/iid repair | Unproved |
| Faithful printed Gray/G17 refutation, shorterU or global minimum fix | Unproved |
