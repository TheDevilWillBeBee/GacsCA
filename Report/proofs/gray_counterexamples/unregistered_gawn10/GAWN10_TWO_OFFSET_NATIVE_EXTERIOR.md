# GAWN10: an exact native projection for late two-offset Address faults

This concerns the **unchanged frozen GAWN2** rule, Q4096/U524288/radius8/
Word100/h1/own beta/lambda24/c104. All its stated departures from Gray
remain. No rule, ROM, clock schedule or constant is changed. This removes
the retained-Address hypothesis for a different restricted native theorem;
it does not extend GAWN9's complete2U theorem or prove iid reliability.

## 1. Exact hypotheses and conclusions

Start with the actual intact H_2 history, at T_0=100Q+2=409602. Let
I=[0,Q), A=[b,b+w) subset I, 1<=w<=104, and fix delta in{1,...,Q-1}.
For D in{0,...,103}, permit arbitrary adaptive after-row overwrites
on any subset of A and rows T_0,...,T_0+D. Each replacement Address
must be either x modQ or (x+delta) modQ. It retains the correct
reference Age of that row. All four flags and all thirteen SF fields
may otherwise be arbitrary legal values. There are no other errors,
including none after t_*=T_0+D. The set's geometry alone is not declared
real1; original-c104 real1 sets meeting these restrictions are included.

Put r=(b-3+delta) modQ and define

    ell = b-3-r if r<=5, and ell=b-3 otherwise.

**Theorem.** Through the current U boundary:

1. Every Address is one of the two prescribed offsets, and every Age
   equals the clean reference clock. Both adjusted-Address five-voters
   always have a whole-word majority. The missing-colony Flag2 source
   therefore never fires.
2. Both computed Workspace fields are0 on every ordinary update.
   Raw Workspace can be nonzero only on A immediately after an overwrite.
   Native evolution is independent of all SF payloads, including raw
   malformed packets and arbitrary Info: an exact closed projection.
3. Wrong Address stays in[ell,Q), with ell>=b-8>=-8. Flag2 is0
   outside[b-3,Q), and Flag1 is0 outside[-Q,Q). All clocks stay correct.
4. After the final overwrite Workspace is0 by t_*+1, and Flag2 is0
   globally by t_*+Q-b+4, at most t_*+4100. Flag2 stays0 through U.

If Address is additionally correct globally at some row t_*+a, it
stays correct through U. Provided the following deadline is at most U,
all native fields recover by

    t_* + max(a,Q-b+4) + Q/2.

This last sentence is a **conditional** native recovery theorem. Address
termination, SF confinement, complete U/2U recovery, general arbitrary
Address/clock faults and an iid threshold are not established here.

## 2. Exact common-clock/two-offset projection — proved

Induct on raw rows, including overwrites. Write a site's Address as
(x+delta*z_x) modQ with z_x in{0,1}. At a target x, every adjusted
neighbor Address is either x modQ or (x+delta) modQ. Five binary
choices always have a majority, and delta!=0 makes the two values
distinct. Either selected Address majority therefore remains one of
these same two values. Overwrites obey the same restriction. Both
right and left voters exist on every row.

Every old clock is the same reference a. Either whole-word clock voter
and its fallback equal a. The actual selector, irrespective of Flag1,
Flag2 or Address, consequently gives(a+1) modU. The overwrite retains
that value. This closes the common-clock induction.

From T_0 through U the computed common clocks are above100Q, or0
at U. They never lie in[96Q,98Q). In the actual physical transition,
Workspace1/2 are initialized0 and the only nonzero branch has that
clock guard. Thus both computed Workspace fields are0 before any SF
source is read. Raw overwrites can replace them only on A. No future
command is supplied, suppressed or approximated. The native update
uses only old native fields; its only missing-GF source is false by
the majority just proved. This is the literal full-rule projection,
not a simulator whose Workspace fields have been chosen independently.

## 3. Native exterior and the eight-site left bound — proved

Prove simultaneously that Address is canonical for x<ell and x>=Q,
Flag2 is0 for x<b-3 and x>=Q, Flag1 is0 outside[-Q,Q), and raw
Workspace is0 outside A. Initially these hold. Current overwrites
cannot disturb any exterior because A starts at b and ends before Q.

**Flag2 left of b-3.** Every old left Flag2 there is0 by induction.
The old self bit is0. The four-site propagation predicates are false,
as is the missing-GF source. At x<=b-4, at most two of the eleven
neighbors can lie in A, so the three-Workspace2 source is false even
before applying the apparent-colony mask. Computed Flag2 is0.

**The right exterior.** For x>=Q, the five right adjusted Addresses
are canonical; C(x) is the true colony. In-colony left Addresses and
all clocks agree, every in-colony Workspace bit is0, and right Flag1
is0. Thus computed Flag1 is0. Old self Flag2 and in-colony left
Flag2 are0. Its untruncated left source is disabled by computed
Flag1=0. Computed Flag2 is0, and the selected right Address is canonical.

**The left Address barrier.** Left of ell, all old left adjusted
Addresses are canonical. A right canonical majority therefore gives
the canonical result under either selector. Consider a foreign right
majority. At least three of its five sites must lie at or to the right
of ell, so x is one of ell-3,ell-2,ell-1. If r>=6, ell=b-3 and
the foreign apparent Address is r-3,r-2 or r-1, each at least3.
If r<=5, ell+delta is0 modQ, and these apparent Addresses are
Q-3,Q-2,Q-1, also at least3. At least three canonical left neighbors
are therefore inside C(x), and each disagrees with the foreign
right majority. This forces computed Flag1=1. Computed Flag2=0
because x<ell<=b-3, so the rule selects the canonical left voter.
This prevents every new foreign Address to the left of ell. The
bound ell>=b-8 follows directly from r<=5 in its only extended case.

**Far-left Flag1.** For x<-Q all native geometry voters see canonical
Addresses: ell>=-8 and Q4096. C(x) is the true colony, clocks agree,
and Workspace is0. Any right Flag1 in[-Q,Q) lies outside C(x), while
every eligible right bit is0. All turn-on/keep predicates are false.
This closes the simultaneous exterior induction, on every burst row
and afterwards. The SF wipe may act inside the native envelope, but
it cannot change the proved native projection.

## 4. Actual Flag2 zero front and conditional native recovery — proved

There are no errors after t_*. At t_*+1 all raw Workspace is0.
Flag2 is already0 for x<b-3 and x>=Q. Suppose its zero prefix ends
just before c>=b-3. At target c all five left bits are0. Both its
propagation predicates are false, as are Workspace and missing-GF
sources. If the old self bit is1, h1's erasure predicate is true:
computed Flag1=0 implies left-inside count0<=1; computed Flag1=1
implies all five left bits0. If the old self is0, it stays0. The same
argument keeps the old prefix zero. Its front advances one site per
update independently of all Address labels and Flag1.

There are Q-b+3 possible Flag2 sites in[b-3,Q). Starting after the
Workspace-zero row proves the deadline Q-b+4<=4100. This is less
than the remaining late interval, even for D103. Both sources remain
closed afterwards, so zero Flag2 persists through U. The h1 erasure
clause is an explicit proposal departure; this argument is not
imported verbatim from Gray's printed clause.

If Address is correct at t_*+a, either Address voter keeps it correct
through U, independently of flags. Suppose the stated recovery deadline
falls within that current period. At max(a,Q-b+4), geometry and
clocks are correct and Workspace/Flag2 are0. No Flag1 inconsistency
or Workspace source remains. In each affected true colony the two
rightmost sites become0, and the zero suffix advances at least two
sites per update: the previous one/two sites see at most zero/one
eligible right ones, respectively, below both on/keep thresholds.
Both affected colonies clear simultaneously in Q/2=2048 updates.
This proves the stated conditional full-native deadline. It does not
prove the additional Address premise.

## 5. Finite verification and remaining obligations

The checker independently transcribes the exact binary native projection
in C, compares selected full physical-kernel outputs with arbitrary SF,
enumerates the ell formula for every legal b/delta, and runs a selected
finite burst family. Histories are native projections justified by §2;
they are not full-SF trajectories or complete2U physical simulations.
Measured recovery in that finite family does not prove universal
Address termination. Receipts retain row counts, full final native
arrays and selected native snapshots.

| Step | Status |
|---|---|
| Actual H_2 late start | GAWN4's proved initializer argument applies |
| Common clocks/two-offset labels/majorities/closed native projection | proved |
| Fixed native exterior/eight-site left Address allowance | proved |
| Workspace1/Flag2 deadline Q-b+4 and persistence through U | proved |
| Address-correct row implies full-native recovery | proved conditionally |
| New geometry/kernel/selected evolving-native checks | measured transcription supplements |
| Universal Address termination for this burst class | unproved |
| Complete SF/U/2U repair for these Address-changing faults | unproved |
| Earlier/arbitrary clocks/multiple Address offsets/surrounding E0/higher/iid repair | unproved |
| Faithful Gray/G17 refutation, shorterU or a globally sufficient/minimal fix | unproved |
