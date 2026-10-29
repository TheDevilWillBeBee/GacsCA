# GAWN17: an upper triple need not correct in one tick

This is a counterexample to an **arbitrary upper-triple one-tick
correction identity** for unchanged frozen GAWN2, Q4096/U524288/
radius8/Word100/h1/own beta/lambda24/c104. All departures from Gray
remain. No rule, ROM, constant, CURRENT or earlier frozen asset changes.
It is not a faithful Gray refutation, an iid memory theorem or an
actual J279 lower-burst counterexample.

## Exact prepared fault and conclusion

Let H_2 be the actual intact recursive initializer of GAWN4, and
C_1=F(H_2). Its native fields are canonical Address, common Age1 and
zero four flags. Form Z_0 by replacing **only Age** at upper physical
sites {-1,0,1} by2, retaining all actual SF and other native fields.
Let Z_k=F^k(Z_0), Y_k=F^(k+1)(H_2). There are no later overwrites.
Put K=96Q-3=393213. For every integer 0<=k<=K,

    I_k=[-1-3k, 2-3k),
    Z_k.Address(x)=Y_k.Address(x)=x modQ,
    Z_k.Age(x)=k+2 on I_k, and k+1 elsewhere,
    Y_k.Age(x)=k+1 everywhere,
    all four native flags in both histories are zero.

The SF is the actual evolving SF; it is not held fixed, reset or
externally prescribed. No claim about its agreement is needed. At
k=1 the bad Ages are3 at{-4,-3,-2}, while clean Ages are2.
Consequently F(Z_0)!=F(C_1) as complete raw upper configurations.
The arbitrary triple analogue of GAWN4's adjacent-pair correction
identity is **false**, not merely unproved. At the proved window's
last row, the native defect is still present and has moved1179639
cells left. Its later behavior is unproved here.

## Proof

Whenever all Address fields are canonical, every adjusted Address
voter consists of five identical words x modQ. Both voters exist and
are canonical. Zero old Flag1/Workspace makes every Flag1 inconsistency,
Workspace, right quorum and old-self retention source false. Thus
computed Flag1 is0. Zero old Flag2, an existing right GF voter and
zero old Workspace make every h1 Flag2 source false, so computed
Flag2 is0. The selector uses the right GF and **right five-clock
majority**, with one added modulo U. None of these conclusions depends
on SF.

For an old bad clock interval [a,a+3), the right witnesses x+1..x+5
contain at least three bad values precisely when they contain all
three: a-3<=x<=a-1. At those three targets the unique right majority
is the bad clock; everywhere else at least three right values have
the common clean clock. Thus the clock interval becomes [a-3,a)
and both clock values increment by1. No fallback is invoked.

For an output row k+1<=K, the largest computed Age is k+3<=K+2
=96Q-1. There is no modulo wrap since 96Q-1<U. The actual physical
Workspace guard, which requires 96Q<=computed Age<98Q, is closed at
every site regardless of SF. Computed Workspace stays zero. Address
and the other flags therefore retain the induction hypotheses on
the entire infinite line. The actual H_2/C_1 native facts initialize
the induction. This proves every stated row, including k=1.

## Relation to the actual-U reduction and limits

GAWN16 proves native recovery for J279's lower faults that **retain
the correct Age**. Its nonpositive-ell case gives an actual upper
triple dprime, but proves neither that this prepared Z_0 is one such
reachable pi(dprime), nor complete correction of all those reachable
triples. GAWN17 proves the unrestricted one-tick triple shortcut
cannot be used to discharge that gap. Restricted reachable-triple
correction and eventual general triple correction remain separate
unproved obligations.

For the separately prepared boundary E(cell_words(Z_0),B), GAWN2's
normalized period theorem applies and gives E(cell_words(F(Z_0)),0)
after U. This differs in represented native Age from
E(cell_words(F(C_1)),0). This is a conditional prepared-encoding
consequence, not an encoding asserted to have been produced by
an admitted lower burst. No error class is assigned from support
geometry alone. No noise rate or all-time memory failure is inferred.

The same right-five clock formula needs examination against Gray's
literal rule and his recovery hypotheses before transferring even
this native obstruction. Matching Q/U/c does not supply that step.

## Verification and status

The checker compares the actual full-kernel clean/faulty C_1 outputs
on17 target sites, retaining complete raw inputs/output digests. It
also checks all4096 Address residues times13 relative positions in
the native equation, and256 full physical-kernel cofactors with
arbitrary legal SF, varied early clocks and interval positions.
These are measured transcription supplements. No full393213-step
SF simulation or encoded full-U physical simulation is performed;
the infinite-line history conclusion follows from the induction.

| Step | Status |
|---|---|
| Actual H_2/C_1 native facts | GAWN4's proved argument applies |
| Canonical GF/zero flags/right-clock selector independent of SF | proved |
| Exact three-clock majority shift/closed guard/0..393213 induction | proved |
| Arbitrary upper triple one-tick correction | false; explicit counterexample proved |
| Prepared normalized encoding consequence | GAWN2's proved period argument applies under its premises |
| Native/kernel/actual-start finite checks | measured transcription supplements |
| Reachability from GAWN16 lower faults/restricted triple repair | unproved |
| Later correction/general faults/higher/iid/faithful Gray or G17 failure | unproved |
| Positive noise rate/minimum sufficient global change | unproved |
| Rule/ROM/constants/CURRENT change or commit | none |
