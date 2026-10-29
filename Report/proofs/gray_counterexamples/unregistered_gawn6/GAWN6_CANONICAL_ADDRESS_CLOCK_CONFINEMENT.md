# GAWN6: universal late clock confinement when Address is retained

This is a proof about the **unchanged frozen GAWN2** transition, not a
new rule. Q4096, U524288, radius8, Word100, h1, beta_2, lambda24 and
integer c104, and all its departures from Gray, remain those of
[GAWN2](../unregistered_gawn2/GAWN2_HALF_SCALE_NOISELESS_PERIOD.md).
The actual recursive initializer H_2 is that of
[GAWN4](../unregistered_gawn4/GAWN4_LATE_SF_BURST_REPAIR.md).

The new result is a universal confinement invariant. It removes one
native-history assumption from
[GAWN5's conditional repair reduction](../unregistered_gawn5/GAWN5_NATIVE_CLOCK_INFO_AND_REPAIR_REDUCTION.md).
It does **not** prove termination of native repair. No native recovery
experiments or complete two-period physical simulations are added here.

## 1. Arbitrary-payload confinement theorem — proved

Write I=[0,Q) for true colony0 and J=[-Q,0) for its left neighbor.
Start with the actual noiseless history of H_2 at physical row
T=100Q+2=409602. At that row replace any subset of cells in I, retaining
their Address fields. Every other field of every replaced cell may be
an arbitrary legal value of the physical alphabet: Age, all four native
flags, all thirteen SF tracks, malformed packets and Info included.
There are no later errors.

For every physical row s with T<=s<=U, the following are exact:

* Address(x)=x modQ at every x.
* Age(x)=s modU for every x outside I.
* Flag2, Workspace1 and Workspace2 are0 outside I.
* Flag1 is0 outside I union J.

Thus wrong clocks stay inside I. Native flag changes outside I can
only be Flag1 changes in J. This holds for arbitrary support inside I,
not just a contiguous104-site fault or the sixteen uniform GAWN5
payloads. It makes no error-class assertion for the whole-colony support.
It applies in particular to those supported faults that actually meet
the original-c104 real1 definition.

### One-step invariant

Let a=s modU be the old reference clock. Suppose the four conclusions
hold at row s. The induction below applies whenever the computed
reference clock a'=(a+1) modU is outside [96Q,98Q). Every update from
T to U has this property: a' runs from100Q+3 through U-1, then0.
Inside I clocks, native flags and all SF fields are unrestricted.

**Address.** Every adjusted candidate Address in either five-site
voter equals x modQ. Both voters have a majority, C(x) exists and is
the true colony, and either selector produces the canonical Address.
The raw-self Address wipe predicate is consequently false everywhere.

**Computed Flag1 on the right.** For x>=Q, the five right clocks all
equal a. Every left neighbor that lies inside C(x) also has clock a;
all adjusted Addresses agree. Every right Flag1 and Workspace1 that
lies inside C(x) is0. Hence the actual inconsistency, Workspace and
Flag1 propagation predicates all vanish, and computed Flag1 is0.

**Computed Flag1 far on the left.** For x<-Q, the right clocks and
the left in-colony clocks equal a. Right Flag1 bits in J are outside
C(x), and do not count. The same predicates vanish. Computed Flag1
is0. No restriction is needed on computed Flag1 in J.

**Computed Flag2.** For x<0, all five left Flag2 bits are0, every
in-colony Workspace2 bit is0, and C(x) exists. The old self Flag2 is0,
so every turn-on predicate is false, even if computed Flag1 is1.
For x>=Q, computed Flag1 is0 by the preceding argument. All left
Flag2 bits inside C(x) and all Workspace2 bits inside C(x) are0.
Bits inside I but lying to the left are outside C(x); the untruncated
left propagation clause is disabled by computed Flag1=0. Again every
turn-on predicate is false. Thus computed Flag2 is0 outside I.
The h1 erasure clause is not used: the relevant old self bits are0.

**Computed Age.** For x>=Q, computed Flag1=0 selects the all-a right
voter. For x<0, the all-a left voter always exists. Let r be the right
Age majority, with self fallback as in the actual rule. If r=a,
either voter produces a. If r!=a, the self fallback cannot have been
used, because old self Age=a. At least three right neighbors therefore
have clocks different from a. They must all lie inside I, so x is one
of -3,-2,-1. At these three positions all five left neighbors lie in
C(x) and have Age=a. All five disagree with r. The actual inconsistency
test forces computed Flag1=1. Computed Flag2=0 then selects the left
voter, again producing a. After the mandatory increment, computed Age
is a' at every outside site. This argument permits arbitrary different
clock values inside I, including0 and values whose increments wrap.

**Computed Workspace.** At every outside site computed Age=a' is
outside the actual [96Q,98Q) pulse. Both Workspace equations return0
before reading any computed Info source. No assumption about the SF
payloads or their later evolution is needed here. This closes the
one-step invariant. All its premises hold immediately after the fault;
induction proves the theorem through U.

In particular, the outside-Workspace conclusion is not inferred from
a quiet tape, assigned future commands, or an Info approximation.
It uses the guard in the full physical transition after proving the
computed outside clocks correct. SF damage may escape I in this broad
theorem; its conclusion concerns the six native fields only.

## 2. A larger late fault class with conditional complete2U repair

For this separate conclusion restrict the replacement fields to Age,
the four native flags, and any Info holder words. Retain every other
SF field and Address. The support is still an arbitrary subset of I.
Let L=4Q=16384 and require each overwritten Age to lie in

    V=[96Q-1,U-L-1]=[393215,507903].

The undamaged clock T also belongs to V. Suppose the actual trajectory
has a row T+r, with1<=r<=L, at which all six native fields equal their
clean values everywhere. This is the **only unproved recovery premise**
for this restricted fault class. Assume no later errors, as above.
Then the actual complete raw configurations satisfy

    X_U=E_2(dprime,Bprime),
    dprime[g]=cell_words(F_2(H_2)[g]) for g!=0,
    X_2U=F_2^(2U)(H_2).

The first record dprime[0] may be any represented496-word record,
including arbitrary native padding. Bprime is arbitrary coherent
auxiliary Info inside I. The last equality is full raw equality;
future histories agree at every tick by determinism.

### Proof of the reduction

Every selected clock is an old whole-word majority or old self fallback
plus1 modU. Through L updates every clock is therefore v+t for some
v in V. No wrap is possible, because maxV+L=U-1. Every computed clock
is at least96Q, and less than U. There are no Info writes at Age0 or
80Q-1, no gathers or Mail transport, and no courier movement. Reset
at96Q or100Q and birth at100Q+1 remain allowed.

Canonical Address is proved in §1. The computed service Address of
each holder is its true logical position; the wipe is absent. Info
therefore receives its old five-holder vote at every update. Define
D(y) to be the logical Info vote immediately after the fault. At most
two holders of each logical position outside I are inside I, so
D(y) there equals the actual clean Info word. All five copies of
D(y), even those with different clocks, are produced on the first
update. They remain coherent and fixed until native recovery. Both
actual special source bits inside I may be arbitrary; no future
Workspace command is assigned or suppressed in this argument.

Mail and couriers start0 everywhere because they were retained from
the actual late clean row. Mail transport and courier movement are
closed at every admitted clock; resets and Flag1 erasure preserve0.
Thus Mail and couriers stay0 even when native flags vary.

The endpoint protection proved in GAWN4/GAWN5 applies separately to
each holder with its own computed clock. No Head word was overwritten.
The clean initial Head copies have no forbidden outward movement bit
at logical endpoints0 andQ-1. Reset and birth give that bit0; holding
votes preserve0; every active total step_packet update, invalid
instruction or collision gives the endpoint bit0 because its target
must lie in[0,Q). Consequently no Head crosses a true colony edge.

At any logical position outside I, at least three holders are
physically outside I. Their clocks are correct by §1, Address is
canonical, Mail is0 and wipe is false. Native Flag1 is irrelevant to
the other SF equations. On the initial row all SF logical votes
outside I equal their clean values, including Info by the three
retained holders. Inductively all non-head SF operations at these
logical positions are local, and incoming Head across the only bad
colony edge is blocked by endpoint protection. These three holders
produce the clean value on every update. The other two cannot alter
the logical vote. All SF logical votes outside I stay clean, even
though individual backup copies close to the boundary may disagree.

Once all native fields equal their clean values at T+r, the common
clock is past100Q. Workspace supply is closed, and native fields stay
clean until U. On the next full SF update, all five holders use the
same clock and correct service Address, no wipe and zero Mail. All
thirteen SF fields consequently regain coherence everywhere. Their
values inside I need not be correct. No correct interpreter execution
inside I has been presumed.

At U the actual old-Out commit and all global resets give the claimed
E_2(dprime,Bprime). Every logical Out outside I is clean; only upper
physical cell0 can differ. Arbitrary Out outside the ordinary frame
inside I is admitted by Bprime. Programme is the actual own beta,
and all native boundary fields are canonical/zero. This is precisely
the represented-D encoding of GAWN2, not a new repair or reset rule.

Let C1=F_2(H_2), C2=F_2(C1), and Cprime=pi_2(dprime). C1 has coherent
SF, canonical Address, common Age1 and zero flags. Only physical
cell0 of Cprime may differ from C1. The arbitrary-value one-cell
quorum argument of GAWN4 §5 gives F_2(Cprime)=C2: at least four of
every native quorum and SF vote are correct, computed Flag1 is0,
and computed Age2 keeps Workspace closed. No legal-padding premise
on dprime[0] is required. The universal represented-D period theorem
of GAWN2 now gives

    F_2^U(E_2(dprime,Bprime))=E_2(F_2(Cprime),0)=E_2(C2,0).

The clean2U row is the same E_2(C2,0). This proves the conditional
reduction. All16 GAWN5 native histories lie in this broader class,
but their recovery premise remains measured there. This result proves
no new native quiet-row instance or universal deadline.

## Verification and status

The [checker](check_gawn6_clock_confinement.py) exhausts the equality
partitions of the at most five internal Age operands seen by an outside
voter, and the eligible external Flag1 masks, at the distinct boundary
classes. It also retains selected inside-flag transcriptions and full
physical-kernel comparisons with arbitrary SF data. The finite checks
supplement the written algebraic induction; they are not a universal
execution search. No evolving repair campaign is performed.

| Step | Status |
|---|---|
| Existing GAWN2 rule/own beta/actual H_2 and clean rowT | Proved previously; unchanged |
| Canonical Address under Address-retaining faults | Proved |
| Outside Age/F2/Workspace and far-left/right F1 invariant through U | Proved for arbitrary internal native and SF payloads |
| Clock range, Info coherence, Mail/courier and endpoint shield for §2 | Proved |
| Exterior logical SF, coherent U encoding and complete2U reduction | Proved conditional on actual full native recovery by4Q |
| Finite cofactor/kernel transcriptions | Finite measured supplements, not a repair-time proof |
| Full native recovery by4Q for every §2 payload | Unproved |
| Earlier/GF-changing faults, surrounding E0, mixed/higher errors or iid ε>0 | Unproved |
| Faithful Gray/G17 refutation, smaller U or globally sufficient minimum change | Unproved |
