# SP29: a conditional zero-Address bank induction

This is a reusable interface theorem for the existing isolated SP29
rule and its frozen own programme. It makes no further rule or constant
change. Its pulse premises are explicit: this theorem does **not**
prove that an arbitrary pulse meets them, or prove an eroder, a higher
error map, or a positive iid noise threshold. It also gives an actual
fourth complete-foreign-frame source theorem for the already certified
three-pulse history.

Use Q=1024, U=475136, TF=278401 and S=TF+6144=284545.
Times in the conditional statement are local computed-state times
after a period boundary. The five copies of a logical primary are
its own Info/Hold groups, not five words chosen from a host simulation.
All other Info payloads and disagreements are allowed. There are no
fresh overwrites after that boundary.

## Conditional theorem and premises

For integers L<R define the quiet template T(L,R) by

    a=LQ-512, b=RQ;
    GF(x)=(x+512*1_[a,b)(x)) mod Q;
    Flag1(x)=1_[a-512,a)(x)+1_[b-512,b)(x).

The clock is common; Flag2, Workspace flags and native packet/code/
pressure auxiliaries are zero. The Address bank B(L,R) consists of
the five Info copies of each primary

    jQ+571+bit, j=L-1,...,R-1, bit=0,...,9.

Suppose at a period boundary:

1. The native fields are T(L,R), with common Age0. All non-Info
   simulation private fields are zero, as supplied by the actual807
   commit-reset identities. B(L,R) is zero.
2. During computed times TF through S, every raw/refined/computed
   Address used for the relevant Hold updates has one of the two
   phase labels x mod Q and (x+512) mod Q. The clock stays common and
   legal. Actual keep/wipe masks and all other evolving simulation
   values may be arbitrary. Frozen ROM and actual arrival equations
   are retained; no arbitrary pending-word replacement is allowed.
3. At S the native endpoint is T(L',R'), with zero auxiliaries and
   common AgeS, where

       L'<R', L'<=L, R'<=R-1.

Then at the next period boundary the native template is T(L',R'),
all non-Info private fields reset to zero, and **B(L',R') is zero**.
In the following pre-pulse portion, the actual own programme supplies
MF509=1 at each hQ+509, h=L',...,R'-1, by computed time TF.
These are precisely the claimed complete foreign-frame sources; the
theorem specifies no complete signal track.

The old and new widths need only R-L>=1 and R'-L'>=1 for this lemma.
It is a conditional closure implication, not a theorem that those
widths or displacement inequalities hold in all subsequent periods.

## Quiet geometry and zero old foreign inputs

The four quiet GF/Flag1 boundaries are at a-512,a,b-512,b, each
neighbourhood separated from another by at least512 sites. The native
radius and refinement radius are at most37. The quiet local cofactors
of [SP29_NEXT_GHOST_SIGNAL.md](SP29_NEXT_GHOST_SIGNAL.md) therefore
apply by translating multiples of Q: all relevant boundary residues
and the Address offset512 remain the same. Uniform portions have the
same constant-label cofactors. The checker also checks the shortest
permitted width1.5Q and the actual fourth-source width10.5Q directly.
Refinement returns raw GF and common Age, native GF/Flag1 persist,
and Flag2 stays zero when epoch force is closed.

The closed birth/force/WF1 guard audit covers S through U-1 and0
through TF-1. Without a birth, empty packet/code validities and
pressure cannot manufacture a source. The actual quiet template
therefore persists before TF and after S. This is the same guard and
native induction as the pinned next-source proof, with no new clock
or encoded upper state assumed at a later boundary.

A complete old foreign frame has origin hQ-512, h=L,...,R-1.
Its GF primary of virtual phase59+bit is (h-1)Q+571+bit.
Every requested remote source has the form
(h+d-1)Q+571+bit. If it is inside[a,b), it belongs to B(L,R).
Otherwise its actual speed-eight path crosses a512-site Flag1 strip.
The logical mail recurrence multiplies by the quiet gate on each
step; a strip of length512 cannot be skipped by eight-site steps.
Thus all three captured histories, direct inputs and votes supply
zero GF words, regardless of every outside Info payload. The exact
dependency ranks and capture clocks are those of the accepted
[protected-source proof](SP29_PROTECTED_SCRATCH.md).

All other own-circuit inputs and matched I are free. Its actual GF0
cofactor gives computed GF0 and Flag1=1. Fresh private fields, quiet
relative geometry and the complete-frame front/courier footprint
give the existing physical prefix induction. In particular all ten
GF Hold outputs at phases59..68 materialize zero before TF. This
uses the physical programme, not a substituted full-circuit result
at the end of a damaged execution.

## Closure of the bank through a pulse

Let y=jQ+571+bit be any target in B(L',R'). Its initial phase class
is especially simple. If j<L-1, it starts in the true region left
of a, with Hold0. If j>=L-1, the inequality R'<=R-1 gives
j<=R-2, so it is in the complete old foreign frame h=j+1,
L<=h<=R-1. The previous paragraph gives its GF Hold0 by TF.
No old partial right frame is silently treated as complete.

The all-raw twenty-phase ROM audit in the accepted next-source proof
checks exactly one Hold opcode per phase. At virtual59..68 its input
issue ages are276520..278398, and Hold materializes by278400<TF.
At the opposite true phases571..580 they are352116..360605, with
the first materialization352118>S. Thus initially true targets
have no earlier Hold store, and **neither possible phase has a Hold
issue during the entire pulse**.

This timing conclusion also needs the pending-kind argument; inspecting
only Hold opcodes would be insufficient. For a fixed logical primary
the two possible phase labels differ by512, whereas the five comb
teeth differ by multiples of5 of magnitude at most20. Both phases
cannot arrive on one common clock row. Outside Match, every arriving
holder has the same ROM destination kind k; Match has no store, and
the all-raw arrival theorem allows at most one arrival per holder.
All new pending records consequently have either presence0 or
presence1/k, followed by the actual keep mask. If presence has a
five-vote majority, at least three copies have that same k, so every
voted kind bit is exactly k. The160 presence/k cofactors check this
universal argument. Pval can be arbitrary. A Scratch store cannot
manufacture a Hold destination, and all pre-TF pending stores have
completed. Arbitrary pending seeds or fresh errors are excluded.

Actual votes and wipes preserve zero Hold throughout TF..S. At S,
every target and all of its holders/refinement footprints are in
the new wrong region: its virtual phase is59..68, with at least59
sites of left clearance and444 sites of right clearance. They stay
in that quiet foreign phase thereafter. Their GF Hold issues have
passed; the later true-phase H2 issues cannot address these groups.
Hold0 therefore persists to the inactive commit clock. Phases59..68
are inside the normal commit mask [58,901) union {965}. The actual
commit forwards these Holds to all five Info copies and resets807
private bits, proving the bank and reset conclusions.

## Next source and induction limit

Now apply the same quiet mail-path and own-prefix argument to
T(L',R') and B(L',R'). Each complete foreign frame h=L',...,R'-1
has all zero virtual GF inputs, computes Flag1=1, and its right
courier writes virtual1021 at physical hQ+509 by the next TF.
Five-holder voting and the exact quiet gate permit arbitrary other
Info values and copy disagreements. This proves the claimed source.

The implication can be iterated along **any** sequence of actual
pulses for which premises2-3 have been proved. The source-bank part
then requires no new finite-history argument. The theorem does not
prove those pulse premises, the true/partial-frame signals, retained
H2 data, or shrinkage after any unspecified mask.

## Actual third-pulse instantiation

In the one clock0-error history of the accepted SP29 proofs, at2U
the template is T(116,128), private fields have reset, and B(116,128)
is zero by SP29_PROTECTED_SCRATCH.md. The actual domain proof
[SP29_THIRD_DOMAIN_PULSE.md](SP29_THIRD_DOMAIN_PULSE.md) supplies
binary raw/refined/computed GF, a common clock, and at2U+S the quiet
endpoint T(110,120) for all8192 allowed third masks. The displacement
inequalities110<=116 and120<=127 hold. This theorem therefore gives:

* At3U=1425408, all550 Info copies at jQ+571..580, j109..119,
  are zero, the native endpoint is T(110,120), and807 private bits
  per site have reset. There are60 initially true and50 complete
  old-foreign zero primaries in the target bank.
* At3U+TF=1703809, MF509=1 at each hQ+509, h110..119.

This is a fourth **complete-foreign-frame source** theorem for the
actual history, with arbitrary original upper Info. It does not give
zeros elsewhere, the full MF509/MF1021 mask, a fourth pulse outcome,
or full upper data restoration. No numerical whole-CA trajectory is
used for the new claim.

| Step | Status | Exact limit |
| --- | --- | --- |
| Quiet-template translation, guards and reset | proved | Binary quiet template, at least1.5Q width, common legal clock |
| Zero GF inputs and early zero Holds in complete old foreign frames | proved | Zero bank, fresh private fields, three actual gathers and barriers |
| Bank closure through any pulse meeting premises2-3 | proved conditionally | Frozen ROM, binary phases/common clock, no fresh errors; no pulse closure inferred |
| Induction along a sequence of such certified pulses | proved conditionally | Premises2-3 must be supplied separately at every step |
| Actual550 third-boundary zero copies and ten fourth foreign signals | proved | Accepted original clock0 history and all-mask third endpoint |
| Full fourth mask/pulse, arbitrary defect erosion, noisy higher map/iid epsilon | unproved | This source theorem does not discharge those obligations |

The [checker](check_short_force1024_GF_bank_closure.py) and
[receipt](../../figs/robustness/SP29_GF_bank_closure_certificate.json)
pin the programme, dependencies, twenty-phase ROM audit, shortest-width
cofactors and actual19500 fourth-source routes. The written coordinate,
timing and majority inductions supply the quantified closure theorem;
the finite representative checks are supplementary certificates.
The [initial checker](../../figs/robustness/SP29_GF_bank_closure_initial_checker.py.txt)
and [failure record](../../figs/robustness/SP29_GF_bank_closure_initial_checker_failure.txt)
retain an incorrect dependency-receipt key lookup, corrected before
the mathematical checks ran. This was a checker metadata defect.
