# GAWN12: the native exterior invariants alone do not force termination

This is for unchanged frozen GAWN2, Q4096/U524288/radius8/Word100/h1/
own beta/lambda24/c104. No rule or constant changes. It is an obstruction
to a proposed proof route, not a counterexample to GAWN10's admitted
104-site burst class, Gray, G17 or iid memory.

## Exact actual history and conclusion

Start from the actual H_2 noiseless history at T_0=100Q+2=409602.
Choose delta in{1,...,8}. At this one row overwrite Address and Flag1
on every site of[-Q,Q), retaining Age, Flag2, Workspace and all SF.
Use the following global native profile, with Age=T_0 modU:

    Address(x)=(x+delta) modQ for -delta<=x<Q,
               x modQ otherwise;
    Flag1(x)=1 for -Q<=x<-delta or Q-max(delta,3)<=x<Q,
             0 otherwise;
    Flag2(x)=Workspace1(x)=Workspace2(x)=0.

There are exactly2Q overwritten sites: the Flag1 interval on the left
and the wrong Address interval together cover[-Q,Q). There are no
subsequent errors. All other raw tracks are retained from the actual
clean history. Thus this specifies a legal finite after-row error
history, without assigning future commands, clocks or SF tapes.
It is **not** a104-site fault; no error-class label is asserted.

**Theorem.** Through the current U boundary, Address/Flag1/Flag2/Workspace
are exactly this profile on every row; Age is the correct common clock.
There are Q+delta wrong Addresses on each row. In particular native
recovery by U is false for this wider fault history.

All eight profiles satisfy GAWN10's common-clock/two-offset/exterior
invariants for b=0: with r=(-3+delta) modQ, ell is -3 for delta1/2,
and -delta for delta3..8. Wrong Address lies in[ell,Q), Flag1 in
[-Q,Q), and Flag2/Workspace are already zero. They also satisfy
GAWN11's triple SF confinement hypotheses that depend only on those
native bounds, though the original small-support fault hypothesis is
absent. Consequently **those native invariants alone**, even with zero
Flag2, cannot imply Address recovery by U. Reachability from the actual
104-site/104-row bursts needs a further argument. No failure of that
still-unproved reachability/termination claim is established here.

## Exact native induction — proved

Every adjusted GF word is canonical or one fixed offset. Both five-word
majorities exist, and all clock voters are the same correct old Age.
The missing-GF source is false. Through U the actual computed clock
is above100Q or0, hence the physical Workspace guard is closed,
independently of every SF value. Both computed Workspace bits are
zero on every update; h1 leaves old zero Flag2 zero. It remains to
check Address and Flag1.

Put l=-delta, h=Q, and m=max(delta,3).

* For x<l-3, the right GF majority is canonical. Within[-Q,l-3),
  three eligible right Flag1 bits turn Flag1 on; farther left every
  eligible right bit is zero because the true colony ends at -Q.
  Both GF voters are canonical, so its selected GF is canonical.
* At x=l-3,l-2,l-1 the right GF majority is foreign and its apparent
  Address is Q-3,Q-2,Q-1. All five old left GF words are canonical
  and disagree inside that apparent colony, forcing Flag1=1.
  Flag2=0 selects the canonical left voter.
* For l<=x<Q-m, the right GF majority is foreign. Its apparent
  colony is[l,Q-delta). Every eligible left GF agrees, including
  the first few sites where canonical left words are excluded by
  the colony mask. At most max(3-delta,0)<=2 right Flag1 bits lie
  inside this apparent colony. Old self Flag1 is zero, so it stays
  zero and the right foreign GF is selected.
* If delta>3, for Q-delta<=x<Q-3 the right GF majority is still
  foreign. Its apparent Address is0,...,delta-4, so the eligible
  right Flag1 count is at least3. Computed Flag1=1; all five left
  GF words are foreign, so the left voter is foreign too.
* At x=Q-3,Q-2,Q-1 the right GF majority is canonical, while five
  old left GF words are foreign and are inside the true colony.
  They force Flag1=1 and the left foreign GF is selected.
* For x>=Q, every in-colony GF is canonical and right Flag1 is0.
  Left foreign words lie outside the true colony. Flag1 stays0
  and the right canonical GF is selected.

These cases partition the line and reproduce the profile. In the first
case's rightmost three canonical targets the three Flag1 witnesses are
exactly l-3,l-2,l-1, all in the true left colony. All counts above use
the actual apparent-colony mask. They also account for the h1 selector;
no Flag1/Flag2 propagation is replaced by a prescribed future value.
Repeating the one-step argument proves the claimed full native history.
The native induction is independent of evolving SF, so retaining the
actual SF at the fault row suffices for a literal full-CA history.

## Status

| Step | Status |
|---|---|
| Actual H_2 late start | GAWN4's proved initializer argument applies |
| Exact finite one-row overwrite/unchanged rule | proved |
| Eight stationary GF/Flag profiles with correct evolving clock | proved |
| Exterior/common-clock/zero-Flag2 invariants imply recovery by U | disproved for the wider invariant class |
| Reachability of these profiles from admitted104-site/104-row faults | unproved |
| Universal native termination for that admitted class | unproved, not disproved here |
| All-time persistence beyond a reopened Workspace pulse | unproved |
| Remembered-bit failure, faithful Gray/G17 or iid refutation | unproved |
