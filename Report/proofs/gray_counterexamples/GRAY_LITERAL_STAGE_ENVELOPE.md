Gray's literal Proposition4 is incompatible with faithful raw-state
gathering and retention as stated below. This is a conditional theorem
about the published stage specifications, not a counterexample run of a
fully specified Gray automaton. It uses none of GR1's ROM, front, rest or
transport equations. It does not refute a decoded-state recovery or iid
memory theorem.

The relevant original PDF pages are14–15,31–36 and41. Proposition4 on
page36 compares the entire simulation structure, whose three fields are
SimBit, Workspace and Mailbox (page14). Its boxes are
[jQ,(j+2)Q)×(kU,(k+2)U), with one box for each real1 error, plus the stated
E0 boxes. The claim is pointwise equality outside the boxes; it is not
restricted to decoded states or period boundaries. Page35 explicitly
allows incorrect information arriving through Mailbox in otherwise
undamaged colonies. These are different types of claims.

**Precise conditional statement.** Let Q>=8192, U=128Q, with the original
lambda24/c104 classes. Suppose a finite-state rule and its initialization
satisfy I,N,S,G,R below. Then there is one three-site, one-tick original
real1 error whose simulation-structure differences from the noiseless
trajectory occupy colonies−1,0,1 during the second-stage rest period.
No box of Proposition4's printed spatial form covers these differences.
Therefore such a rule cannot satisfy the literal pointwise Proposition4.
The same statement at Q=8192 gives U=1048576, conditional on the rule,
programme and gathering assumptions being realized at this Q.

The assumptions and their status are deliberately explicit:

| Axiom | Exact meaning used here | Primary support and proof status |
|---|---|---|
| I: initialized encoded data | Address=x modQ, Age0, native Flags0, all Workspace/Mailbox bits0. Five SimBit holders agree. There is an interior represented primary y in colony0 encoding a nonflag upper Workspace bit, whose value is0; y is not0,3,Q−3. All levels are recursively encoded; actual ProgramBits are correct for the chosen fixed programme. | Pages15,31–33 prescribe these types of initial values. Recursive data compatibility for arbitrary correct programme is proved below. An actual Gray programme, field sizes and final layout at Q8192 are unprovided/unproved. |
| N: native rule and pulse | Native Address/Age/Flags obey the printed pp20–22 rules. Workspace.Flag1/2 are0 outside the initial2Q ticks of stage4, in particular before96Q. | Printed equations and p34/p41 pulse. All8192 phase cofactors certify canonical Address/common Age and zero Flags when input Workspace flags are0. |
| S: selected SimBit evolution | Each clean update replaces the five copies of logical SimBit y by their majority. Ordinary primary y is otherwise unchanged before the next period boundary. The extra ProgramBit operation at primary0 and the flag-source operations at3,Q−3 do not write y. | Majority is explicit p33; boundary update p34; special writes p35 and31–32. Exact combination/order on damaged states is not a fully supplied rule. This trajectory never damages local controls, so it does not require a spurious-Age0 commit equation. |
| G: full, raw-state gathering | During stage2, with correct native controls and coherent current SimBits, every colony collects the full currently represented raw states of its ten neighboring colonies. Its stage2 record is an injective fixed encoding of those raw input bits in Workspace locations inside that receiving colony. The gathering completes by48Q and works for the changed coherent source state here, independently of data retained from stage1. | Pages32/34 specify state gathering and Workspace storage; p35 assumes the described operation despite E0. Full raw-state collection, local storage and independence of older bank values are the precise semantic interpretation needed. They are not verified transition equations for Gray's unspecified implementation. A gather that first repairs upper raw copies or omits currently irrelevant state bits does not satisfy G. |
| R: retained records | Stage2 records remain available and unchanged throughout its rest period [48Q,64Q). | Page34 gives separate Workspace locations and no simulation-structure changes in noiseless rest periods. Preservation of these records under the particular earlier real1 history is part of the stated conditional stage semantics, not independently checked machine code. |

The selected Workspace bit excludes Workspace.Flag1/2. The proof can use
any ordinary Workspace storage bit; the interpreter necessarily has such
bits. Its upper initial value0 follows from the initial Workspace rule,
regardless of ProgramBit values. No all-zero raw upper cell or all-zero
lower colony is assumed. A represented native zero bit could be used
instead, but choosing Workspace separates this error from native controls.

**Initialization with ProgramBits: proved as data compatibility, not a
programme compiler.** Let beta(a) be any correct programme string padded
to Q bits. The lifted ProgramBit at physical x is beta(x modQ); in the
projected system it is a fixed function of Address. Let ell(f,b) be any
given injective represented-state layout consistent with I. Assume the
five represented upper SimBit slots have primaries at residues4,...,Q−4,
as can be arranged under the stipulated interior layout and Q>=2K. Write
their logical offsets as s in {−2,−1,0,1,2}. Define D on integers, with
i=floor(x/Q), a=x modQ, by these cases:

    Address primary: D(iQ+ell(Address,b)) = bit_b(i modQ).
    SimBit slot-s primary: D(iQ+ell(SimBit,s)) = D(i+s).
    Age, Flags, Workspace or Mailbox primary: D(iQ+ell(f,b)) = 0.
    Optional lifted ProgramBit primary: D(iQ+ell(ProgramBit,0)) = beta(i modQ).
    Every remaining unused primary: a chosen fixed marker value gamma(a).

For the projected final system, ProgramBit need not be a represented
state field. The auxiliary primary0 used by the p31–32 hardwiring step
can instead be assigned beta(i modQ), giving the same lifted ProgrammeBit
relation there; choose it only when0 is not a represented primary. Choose
the unused special pulse primaries3,Q−3 to be0. Other marker values may
be arbitrary; zero marker values are not needed for the witness.

An Info-recursion argument has |x|>=4. Its next argument i+s has smaller
absolute value: for x>=4, |floor(x/Q)+s|<=floor(x/Q)+2<x; for x<=−4,
|floor(x/Q)+s|<=ceil(|x|/Q)+2<|x|, since Q>=8192. Thus D is defined by a
terminating recursion, for any beta and marker choices. Define H with
canonical Address, zero Age/Flags/Workspace/Mailbox, SimBit slot-s equal
to D(x+s), and the correct ProgramBit beta(x modQ) if that field is present.
Every represented primary encodes the corresponding raw H_i bit by the
case definitions. All five holders of logical D(x) agree. The optional
ProgramBit case or auxiliary primary0 also encodes beta(i modQ), so the
same initial data work at every level. In particular D(y)=0 when y is a
represented Workspace bit of H_0, without imposing beta(0)=0.

This establishes compatibility of the initialization constraints used in
the theorem. It does not supply the actual beta, the actual field widths,
interpreter or final physical representation map. The simple hardwiring
example on p31 uses Address primaries1,...,log2Q, whereas the later p33/p35
description moves represented state away from the boundary and reserves
3 for the flag source. Their literal position choices cannot all be used
unchanged together. Adapting the hardwirer to the final layout is an
explicit remaining refinement obligation; it is not silently done here.
At Q8192, beta fitting and the p34 last-stage runtime condition are also
unproved: the sufficient-size constants a,b are not specified.

**One valid real1 error: proved.** In colony0 choose the ordinary primary
y from I. At physical time1 replace only these three raw bits:

    holder y−1: its secondary copy of logical primary y -> 1;
    holder y:   its primary SimBit y -> 1;
    holder y+1: its secondary copy of logical primary y -> 1.

Leave every other bit, including Address, Age, native Flags, both
Workspace flags, ProgramBits and all other SimBits, at its noiseless value.
The entire physical location set is E={(y−1,1),(y,1),(y+1,1)}. No point
belongs to E0: every permitted candidate0 singleton or adjacent pair has
linked exterior error points. E is candidate1 because it fits a Q×U box
and contains two disjoint linked candidate0 subsets. Condition(iii)
holds with c104 (all three points fit a width3,time1 box), and(iv) is
vacuous. Thus the complete location set is one real1 error. There is no
independently imposed upper noise or earlier lower error. The classifier
checks the representative y=4096; the classification is translation
invariant and independent of the unspecified representation layout.

**Native closure and SimBit persistence: proved under N,S.** Before96Q,
the output Workspace flags are0 irrespective of SimBit data. Both native
Flags start0 and are never overwritten. Canonical Address makes C(x)
exist everywhere, common Age gives consistency, and all native/Workspace
flag forcing terms are0. The printed native equations therefore preserve
canonical Address, increment common Age, and keep Flag1=Flag2=0. This
holds at every colony phase. The literal erroneous Flag2 erasure predicate
does not enter because Flag2 is always0. Computed-versus-current SimBit
in the Workspace equation is also irrelevant before96Q. Both p33 special
Mailbox/SF wipe predicates are false throughout this interval.

At time1 the five holders of y have values0,1,1,1,0. Their majority is1.
At time2 every holder therefore has1, including primary y. The majority
of five1s remains1. Before the next work-period boundary no permitted
exception in S writes y. The coherent wrong primary thus persists at
least through T=56Q. The noiseless reference has0 there, under the same
logic. No Age error, Hold buffer, rest continuation under a damaged clock,
or GR1 transport equation is used.

**Workspace differences and the fixed box: proved under G,R.** Stage2
starts at32Q after the three copies have become a coherent wrong logical
bit. Colony−1 must gather the raw represented state of colony0 as its
right-neighbor input. Colony1 must gather it as its left-neighbor input.
Both receive a state with the selected raw upper Workspace bit1; the
noiseless reference receives0. By G's fixed injective record, at least
one stage2 Workspace bit differs at a site in each of colonies−1 and1.
Both records are complete by48Q and persist through T=56Q by R. Primary
y still differs in colony0. Hence at T there are simulation-structure
differences in all three colonies−1,0,1. At Q8192, T=458752<96Q=786432.
Using any time in the interior of the second rest period avoids the
unprovided current/computed-Age convention at its boundaries.

There is one real1 error and no E0, so Proposition4 provides only one
two-colony spatial interval. Such an interval contains exactly colonies
j,j+1. It cannot contain both−1 and1, let alone all three. If its temporal
interval excludes T, the claimed pointwise equality already fails there;
if it includes T, its spatial interval omits a differing point. This is
a contradiction for every integer j,k. The proof does not depend on
same-time bidirectional Mailbox shifts. Even incorrect deliveries at
different times on opposite sides would defeat a fixed spatial pair.

**What is established and what remains open.** The conditional theorem
proves that the literal pointwise statement cannot follow from the
faithful raw-gather-and-retain stage specification. It is stronger than
merely observing the p35 allowance for incorrect incoming mail, and it
does not import a GR1 mechanism. The native and SimBit-core calculations
use actual printed equations or explicit majority axioms. The ProgrammeBit
argument proves that choosing an initial zero workspace bit need not
depend on an all-zero programme, while leaving its actual compilation open.

A fully specified faithful Gray counterexample would still require a
correct self programme and compatible final layout, plus verification of
G and R on this post-error state. Conversely a concrete implementation
that repairs upper raw copies before gathering, omits irrelevant bits,
stores records outside the receiver or sanitizes old data would require
an explanation of how its behavior refines the stated stage description;
this conditional theorem does not prohibit such implementations. The
older Age/Hold route has an additional gap: Gray names no Hold field and
gives no damaged-clock commit equation. It is unnecessary for this proof
and remains unproved for a literal completion.

A possible corrected deterministic lemma should constrain decoded
period-boundary states, or explicitly permit temporary data footprints
in receiving colonies. This proof establishes neither the smallest rule
change nor a complete corrected reliability theorem. All-time decoded
memory failure, iid failure, Gacs's construction and any positive noise
threshold remain unproved here.

Reproduce the local and provenance constituent checks with
check_gray_literal_stage_envelope.py. Its receipt labels G,R and the
actual programme/layout realization as assumptions, retains primary PDF
page images, and sets faithful_Gray_full_rule_counterexample_proved=false.
