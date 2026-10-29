# GAWN25: common-clock native projection for arbitrary Address words

This is a lemma for **unchanged frozen GAWN2**, Q4096/U524288,
Word100/radius8/h1/own beta/lambda24/c104. Every previously declared
departure from Gray remains. G17 is unchanged. This does not describe
a faithful implementation of Gray or a reliable cellular automaton.

## 1. Exact statements

Let a reference clock satisfy a(t+1)=(a(t)+1) modU. On an interval of
ordinary updates, require every computed reference clock a(t+1) to be
outside [96Q,98Q). At the initial row every site's actual Age is a(t).
Permit arbitrary legal Address words0..Q-1, all four flag bits, and all
thirteen SF fields. After-row errors, if any, must retain the correct
reference Age; their other fields may be arbitrary and adaptive.

**Projection theorem — proved.** Throughout this interval actual clocks
remain equal to the reference. On every ordinary update both actual
computed Workspace flags are0, and the other native outputs are the
radius5 projection in section2. No majority, fixed two-offset set, or SF
coherence is required. Every new Address offset is copied from an old
offset. The only new offsets can be introduced by errors. In particular
any fixed set of allowed offsets containing0 is invariant when all
overwrites use that set. Native dependence has radius5, even though the
whole rule has radius8. A quiet canonical native row has a quiet successor
irrespective of SF under this actual guard restriction.

**Conditional native repair lemma — proved.** If at some row R Address is
canonical everywhere, all clocks are correct and common, and there are
no subsequent errors, then all six native fields are correct and quiet
by R+Q+1, provided the guard restriction holds for every intervening
computed clock. This holds for arbitrary initial flags and SF, including
on infinitely many sites. It is conditional on the global Address premise;
this proof does not establish that premise from arbitrary Address faults.

**Finite campaign — measured only.** Start with the actual intact recursive
H2 row at T0=100Q+2=409602. At A=[b,b+104), b=0 orQ-52, declare all sites
on D=1 or104 consecutive after-rows as errors. Retain the true clock.
Overwrite Address with each selected profile in the checker and all four
flags with the selected constant pattern; retain actual SF. Run the exact
native projection, with no later errors, to at most T0+4Q. Section3's causal
argument makes these infinite-line native histories, without periodic
boundary conditions or supplied Workspace commands. The finite sets E
are classified using E itself as the complete error set and original c104.
Measured native recovery does not establish complete SF repair, a uniform
deadline for every Address profile, surrounding E0 tolerance or iid memory.

## 2. Exact projection and proof

Write g(x)=(Address(x)-x) modQ. At target x the adjusted Address of neighbor
x+j is (x+g(x+j)) modQ. Thus a whole-word majority of the adjusted Address
words is precisely a majority of the full offset words. Let rg/e be the
five right offsets' majority/existence, using old g(x) as fallback; let lg
be the five left offsets' majority with the same self fallback. A quorum
is unique when it exists, and a quorum value is one of the old values.
Fallback is also an old value. These observations prove offset-set closure.

Define r=(x+rg) modQ and in(j)=e AND 0<=r+j<Q. The apparent colony is
empty when e=0, even though rg has a fallback value. In the formulas below
counts of flags refer to actual old raw bits, and all sums are integer sums:

    mismatch = sum(in(j) AND g(x+j)!=rg, -5<=j<=-1)
    rightF1  = sum(in(j) AND oldF1(x+j), 1<=j<=5)
    W1,W2    = sum(in(j) AND oldWF1,oldWF2(x+j), -5<=j<=5)
    F1       = NOT e OR mismatch>=3 OR W1>=3 OR rightF1>=3
               OR (oldF1(x) AND rightF1>=2)
    L2       = sum(oldF2(x+j), -5<=j<=-1)
    LI2      = sum(in(j) AND oldF2(x+j), -5<=j<=-1)
    source3  = NOT e AND a(t+1) mod16==0
    source4  = W2>=3
    on       = LI2>=4 OR (F1 AND L2>=4) OR source3 OR source4
    erase    = (NOT F1 AND LI2<=1) OR (F1 AND L2==0)
    F2       = on, if oldF2(x)==0;
               source3 OR source4 OR NOT erase, if oldF2(x)==1
    new_g    = rg, if e AND (NOT F1 OR F2); otherwise lg
    new_Age  = a(t+1)
    new_WF1  = new_WF2 = 0.

These are exactly GAWN2's native equations under the stated hypotheses.
Its **h1 erase clause is an explicitly changed proposal clause**, not an
argument imported from Gray's printed Flag2 predicate. No change is made
here to GAWN2 or that clause. Both five-clock voters always have a quorum
equal to a(t), and both self fallbacks equal it. Thus whichever Address/flag
selector is chosen, the actual Age output is a(t+1). In Flag1 every Age
quorum-existence and Age-mismatch source is consequently false. The only
remaining inconsistency is the masked Address mismatch written above.

The actual Workspace calculation initializes both bits to0. Its nonzero
branch is guarded by computed Age in[96Q,98Q), which is false here before
any SF source is read. The SF wipe, arbitrary SF packets, computed-primary
Info and programmed Head activity cannot invalidate this deduction.
After-row overwrites may replace raw Workspace; the next normal update
again computes0. This proves common clocks and the literal native projection
by induction, including arbitrary adaptive legal overwrites. It does not
prescribe any future source value or Workspace command.

Unlike two-offset arguments, five legal Address words need not have a
majority: five distinct offset words are an immediate example. The
missing-colony Flag2 source can therefore fire every16 ticks while such a
neighborhood exists. Omitting that source or assuming a quorum would make
a claimed generalization of the two-offset proof invalid. This observation
is an obstruction to that proof route, not a counterexample to recovery.

## 3. Exact finite causal restriction — proved

Relative to the quiet common-clock native row, the projected discrepancy
state is the tuple (g,F1,F2,WF1,WF2). Its all-zero neighborhood has an
all-zero successor at every physical Address phase. Formula2 uses only
neighbors within5. Consequently, if all errors lie in A=[b,b+w), the
native support at relative row s lies in [b-5s,b+w+5s). This is the usual
induction on a finite causal cone, not a colony confinement theorem.

The C runner allocates base=b-5M-16 and length10M+w+33 for a maximum
relative row M. This includes that entire cone and extra quiet margins.
At each update it computes the old active hull plus five sites on each
side; all other sites have the proved quiet successor. It clears the
destination buffer's previous write hull before reuse. Re-forcing the
declared after-row support is applied after the computed ordinary row.
No nonzero state can be omitted by active-hull restriction. Explicit
capacity checks and offset-set checks supplement this induction.

SF is allowed to evolve under the actual rule; its row is not simulated by
this runner. The projection theorem proves that whichever legal SF values
that actual trajectory attains, its native rows are exactly these projected
rows. Correct native fields at the measured quiet row persist through the
current U boundary, since the actual clock stays outside the source window
there. No full-SF equality or later source-window assertion follows.

## 4. Conditional R+Q+1 repair — proved

Assume canonical Address everywhere at R and no further errors. Either
five-Address voter remains canonical on every subsequent row regardless
of flags; hence Address stays correct. Clocks stay correct by section2.
By R+1 both raw Workspace bits are0 everywhere.

Consider each true colony independently, starting at row R+1. Address and
Age mismatch and missing-quorum sources are false, and W1=0. New Flag1
has only the right-flag threshold3 and old-self/right-threshold2 predicates.
At the rightmost two sites there are at most zero/one eligible right bits,
so both become0 in the next update. If a zero suffix of length2s exists,
the preceding two sites again have at most zero/one eligible old right
ones, so the suffix extends by two. Existing zero suffix sites stay zero.
After Q/2 updates Flag1 is globally0. This works for every colony at once,
without any finite-support premise.

From that row onward computed Flag1 stays0. Flag2's untruncated five-left
source is disabled, and both Workspace and missing-quorum sources are
false. Only masked LI2 remains. At the first two sites of a colony there
are at most zero/one eligible old left bits. The turn-on test LI2>=4 is
false, and an old1 is erased by the h1 test LI2<=1. Both become0. A zero
prefix of length2s similarly advances two sites, and its old sites stay
zero. After another Q/2 updates Flag2 is globally0. All native fields are
therefore quiet by R+1+Q, as asserted. They remain quiet while the guard
restriction holds. This does not infer that an arbitrary faulty Address
history ever reaches the required global canonical row R.

## 5. Evidence and statuses

The checker compares selected full physical kernels with arbitrary SF,
checks the conditional flag-front formulas, classifies the declared
finite sets E using the original predicates, and reruns selected finite
native histories. It preserves forcing arrays, every-row native counts,
quorum/source3 event counts and full final native arrays in NPZ receipts.
Selected evolving rows are independently compared to the full physical
kernel. The initializer is GAWN4's actual H2 argument; no hypothetical
initial SF source or lower oracle is supplied.

| Step | Status |
|---|---|
| Actual intact H2 late start | GAWN4 initializer argument applies |
| Arbitrary legal Address/common-clock/closed actual Workspace projection | proved |
| Offset-set closure and radius5 finite causal restriction | proved |
| Global canonical Address premise implies R+Q+1 native repair | proved conditionally |
| Error-set classification and selected finite kernel/history receipts | measured/exact finite supplements |
| General arbitrary-Address termination or fixed colony exterior | unproved |
| Complete SF/U/2U recovery for these Address-changing faults | unproved |
| Arbitrary Age/open source guard/multiple or surrounding E0/higher/iid | unproved |
| Faithful Gray/G17 refutation, shorterU or sufficient/minimal global fix | unproved |
| Rule/ROM/constants/CURRENT change or commit | none |
